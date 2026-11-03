"""Învățare prin consolidare cu GRPO: modelul scrie un grup de povești pentru fiecare instrucțiune, iar fiecare
poveste este comparată cu restul grupului ei."""

import copy
import os
import sys
import textwrap
import time

import numpy as np
import torch
from torch.nn import functional as F

from checkpoint import CHECKPOINTS, load_checkpoint, save_checkpoint
from data import DATA_DIR
from dpo import DEMO
from model import pick_device
from preferences import cut, load_asks
from reward import MAX_TOKENS, words_used
from sample import write

RUN_DIR = os.path.join(CHECKPOINTS, "grpo")
PROMPTS = 16
GROUP = 8
LR = 2e-5
KL = 0.05
CHUNK = 16
EVAL_EVERY = 4


@torch.no_grad()
def rollout(policy, tokenizer, asks, rng):
    device = next(policy.parameters()).device
    stories = []
    for i in rng.choice(len(asks), PROMPTS, replace=False):
        ids, words = asks[i]
        out = policy.generate(torch.tensor([ids] * GROUP, device=device), MAX_TOKENS, temperature=1.0)
        for story in out[:, len(ids) :].tolist():
            story = cut(story, tokenizer.eot_id)
            stories.append((ids, story, words_used(tokenizer.decode(story), words) / len(words)))
    return stories


def advantages(reward):
    groups = reward.view(-1, GROUP)
    adv = (groups - groups.mean(dim=1, keepdim=True)) / (groups.std(dim=1, keepdim=True) + 1e-4)
    return adv.view(-1)


def pack(stories, pad_id, device):
    longest = max(len(ids) + len(story) for ids, story, _ in stories)
    seq = torch.full((len(stories), longest), pad_id, dtype=torch.long)
    mask = torch.zeros(len(stories), longest - 1)
    for row, (ids, story, _) in enumerate(stories):
        seq[row, : len(ids) + len(story)] = torch.tensor(ids + story)
        mask[row, len(ids) - 1 : len(ids) + len(story) - 1] = 1
    return seq.to(device), mask.to(device)


def token_log_probs(model, seq):
    logits, _ = model(seq[:, :-1])
    return F.log_softmax(logits, dim=-1).gather(-1, seq[:, 1:].unsqueeze(-1)).squeeze(-1)


def main(minutes):
    torch.manual_seed(1337)
    rng = np.random.default_rng(1337)
    device = pick_device()
    policy, tokenizer, _ = load_checkpoint(os.path.join(CHECKPOINTS, "sft", "model.pt"), device)
    reference = copy.deepcopy(policy).eval().requires_grad_(False)
    policy.eval()
    optimizer = torch.optim.AdamW(policy.parameters(), lr=LR, weight_decay=0.0)
    by_length = load_asks(os.path.join(DATA_DIR, "instruct_train.txt"), tokenizer, policy.config.block_size - MAX_TOKENS)
    asks = [ask for group in by_length.values() for ask in group]
    print(f"{len(asks):,} instrucțiuni cu cuvinte cerute | {PROMPTS} pe rundă, câte {GROUP} povești", flush=True)

    def evaluate(step):
        story = write(policy, tokenizer, DEMO, max_new_tokens=120, with_prompt=False)
        print(textwrap.indent(textwrap.fill(story, width=86), "  "), flush=True)

    budget = minutes * 60
    start = time.time()
    step = 0
    evaluate(step)
    while time.time() - start < budget:
        stories = rollout(policy, tokenizer, asks, rng)
        reward = torch.tensor([r for _, _, r in stories], device=device)
        adv = advantages(reward)
        seq, mask = pack(stories, tokenizer.pad_id, device)

        drift = 0.0
        for rows in torch.randperm(len(stories), device=device).split(CHUNK):
            logp = token_log_probs(policy, seq[rows])
            with torch.no_grad():
                ref = token_log_probs(reference, seq[rows])
            r = ref - logp
            kl = torch.exp(r) - r - 1
            per_token = (adv[rows, None] * logp - KL * kl) * mask[rows]
            loss = -(per_token.sum(dim=1) / mask[rows].sum(dim=1)).mean()
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.0)
            optimizer.step()
            drift += (kl.detach() * mask[rows]).sum().item() / len(stories)
        step += 1

        print(f"runda {step:>3} | recompensa {reward.mean().item():.3f} | KL {drift:5.2f} | "
              f"{(time.time() - start) / 60:.1f} min", flush=True)
        if step % EVAL_EVERY == 0:
            evaluate(step)

    if step % EVAL_EVERY != 0:
        evaluate(step)
    save_checkpoint(os.path.join(RUN_DIR, "model.pt"), policy, tokenizer, step=step)
    print(f"gata: {step} runde, {(time.time() - start) / 60:.1f} minute")


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 10)
