"""DPO (Direct Preference Optimization): modelul învață din perechi de povești, față de o copie înghețată a lui."""

import copy
import os
import sys
import textwrap
import time

import torch
from torch.nn import functional as F

from checkpoint import CHECKPOINTS, load_checkpoint, save_checkpoint
from model import pick_device
from preferences import load_pairs
from sample import write
from sft import make_batch

RUN_DIR = os.path.join(CHECKPOINTS, "dpo")
BATCH_SIZE = 16
LR = 1e-5
BETA = 0.1
EVAL_EVERY = 100
DEMO = "Words: rain, cake, jump\nStory:"


def log_probs(model, x, y):
    logits, _ = model(x)
    picked = F.log_softmax(logits, dim=-1).gather(-1, y.clamp(min=0).unsqueeze(-1)).squeeze(-1)
    return (picked * (y != -1)).sum(dim=-1)


def dpo_loss(policy, reference, pairs, pad_id, device):
    examples = [(p["prompt"] + p["chosen"], len(p["prompt"])) for p in pairs]
    examples += [(p["prompt"] + p["rejected"], len(p["prompt"])) for p in pairs]
    x, y = make_batch(examples, pad_id, device)
    with torch.no_grad():
        ref = log_probs(reference, x, y)
    gain = log_probs(policy, x, y) - ref
    margin = BETA * (gain[: len(pairs)] - gain[len(pairs) :])
    return -F.logsigmoid(margin).mean(), margin


@torch.no_grad()
def held_out(policy, reference, pairs, pad_id, device):
    margins = torch.cat([dpo_loss(policy, reference, pairs[i : i + 32], pad_id, device)[1]
                         for i in range(0, len(pairs), 32)])
    return (margins > 0).float().mean().item(), margins.mean().item()


def main(minutes):
    torch.manual_seed(1337)
    device = pick_device()
    policy, tokenizer, _ = load_checkpoint(os.path.join(CHECKPOINTS, "sft", "model.pt"), device)
    reference = copy.deepcopy(policy).eval().requires_grad_(False)
    policy.eval()
    pairs = load_pairs()
    train, valid = pairs["train"], pairs["valid"]
    optimizer = torch.optim.AdamW(policy.parameters(), lr=LR, betas=(0.9, 0.95), weight_decay=0.0)
    print(f"{len(train):,} perechi de antrenare, {len(valid)} păstrate pentru validare", flush=True)

    def evaluate(step):
        accuracy, margin = held_out(policy, reference, valid, tokenizer.pad_id, device)
        story = write(policy, tokenizer, DEMO, max_new_tokens=120, with_prompt=False)
        print(f"pasul {step:>5} | validare: ordonate corect {accuracy:.0%}, marja {margin:+.2f}", flush=True)
        print(textwrap.indent(textwrap.fill(story, width=86), "  "), flush=True)

    budget = minutes * 60
    start = time.time()
    step = 0
    evaluate(step)
    while time.time() - start < budget:
        batch = [train[i] for i in torch.randint(len(train), (BATCH_SIZE,)).tolist()]
        loss, margin = dpo_loss(policy, reference, batch, tokenizer.pad_id, device)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.0)
        optimizer.step()
        step += 1

        if step % 20 == 0:
            accuracy = (margin > 0).float().mean().item()
            print(f"pasul {step:>5} | pierdere {loss.item():.3f} | ordonate corect {accuracy:.0%} | "
                  f"{(time.time() - start) / 60:.1f} min", flush=True)
        if step % EVAL_EVERY == 0:
            evaluate(step)

    if step % EVAL_EVERY != 0:
        evaluate(step)
    save_checkpoint(os.path.join(RUN_DIR, "model.pt"), policy, tokenizer, step=step)
    print(f"gata: {step:,} pași, {(time.time() - start) / 60:.1f} minute")


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 2)
