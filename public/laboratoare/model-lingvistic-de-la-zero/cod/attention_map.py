"""Ce privește atenția modelului antrenat: unde se uită fiecare cap, de la ultimul token al unei propoziții."""

import argparse
import math

import torch
from torch.nn import functional as F

from checkpoint import load_checkpoint
from model import pick_device


@torch.no_grad()
def attention_maps(model, ids):
    inputs = []
    hooks = [block.attn.register_forward_hook(lambda module, args, out: inputs.append(args[0]))
             for block in model.blocks]
    logits, _ = model(ids)
    for hook in hooks:
        hook.remove()
    maps = []
    for block, x in zip(model.blocks, inputs):
        attn = block.attn
        B, T, C = x.shape
        q = attn.q_proj(x).view(B, T, attn.n_head, C // attn.n_head).transpose(1, 2)
        k = attn.k_proj(x).view(B, T, attn.n_head, C // attn.n_head).transpose(1, 2)
        scores = q @ k.transpose(-2, -1) / math.sqrt(C // attn.n_head)
        future = torch.triu(torch.ones(T, T, dtype=torch.bool, device=x.device), diagonal=1)
        maps.append(F.softmax(scores.masked_fill(future, float("-inf")), dim=-1)[0])
    return torch.stack(maps), logits[0, -1]


def main():
    parser = argparse.ArgumentParser(description="Atenția unui model antrenat.")
    parser.add_argument("checkpoint")
    parser.add_argument("prompt", nargs="?", default="Tom and Lily went to the park. Tom gave the ball to")
    args = parser.parse_args()

    device = pick_device()
    model, tokenizer, _ = load_checkpoint(args.checkpoint, device)
    model.eval()
    ids = tokenizer.encode(args.prompt)
    tokens = [tokenizer.id_to_token[i] for i in ids]
    maps, logits = attention_maps(model, torch.tensor([ids], device=device))
    top = torch.topk(F.softmax(logits, dim=-1), 3)
    print(" ".join(tokens))
    print("următorul token: " + ", ".join(f"{tokenizer.id_to_token[i]} {p:.0%}"
                                          for p, i in zip(top.values.tolist(), top.indices.tolist())))
    last = maps[:, :, -1, :]
    for layer in range(last.size(0)):
        cells = []
        for head in range(last.size(1)):
            j = last[layer, head].argmax().item()
            cells.append(f"{tokens[j]:>5} {last[layer, head, j].item():.2f}")
        print(f"stratul {layer + 1} | " + " | ".join(cells))


if __name__ == "__main__":
    main()
