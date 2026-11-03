"""Perechi de preferințe: modelul ajustat scrie patru povești pentru o instrucțiune, iar povestea care folosește cele
mai multe cuvinte cerute este preferată celei care folosește cele mai puține."""

import json
import os
import sys
import time

import numpy as np
import torch

from checkpoint import CHECKPOINTS, load_checkpoint
from data import DATA_DIR
from model import pick_device
from reward import MAX_TOKENS, words_used
from sft import instruction, parse
from tokenizer import EOT

SAMPLES = 4
GROUP = 8
PAIRS_PATH = os.path.join(CHECKPOINTS, "dpo", "preferences.json")


def load_asks(path, tokenizer, max_prompt, skip=0):
    with open(path, encoding="utf-8") as f:
        docs = [parse(doc) for doc in f.read().split(EOT)][skip:]
    by_length = {}
    for fields in docs:
        if "Words" in fields and "Story" in fields:
            ids = tokenizer.encode(instruction(fields))
            if len(ids) <= max_prompt:
                by_length.setdefault(len(ids), []).append((ids, fields["Words"].split(", ")))
    return by_length


def cut(story, eot_id):
    return story[: story.index(eot_id) + 1] if eot_id in story else story


@torch.no_grad()
def make_pairs(model, tokenizer, by_length, n, rng):
    device = next(model.parameters()).device
    lengths = [length for length, asks in by_length.items() if len(asks) >= GROUP]
    pairs, ties = [], 0
    while len(pairs) < n:
        length = lengths[rng.integers(len(lengths))]
        group = [by_length[length][i] for i in rng.choice(len(by_length[length]), GROUP, replace=False)]
        prompts = torch.tensor([ids for ids, _ in group], device=device)
        out = model.generate(prompts.repeat_interleave(SAMPLES, dim=0), MAX_TOKENS, temperature=1.0, top_k=50)
        for i, (ids, words) in enumerate(group):
            scored = []
            for story in out[i * SAMPLES : (i + 1) * SAMPLES, length:].tolist():
                story = cut(story, tokenizer.eot_id)
                scored.append((words_used(tokenizer.decode(story), words) / len(words), story))
            scored.sort(key=lambda s: s[0])
            (low, rejected), (high, chosen) = scored[0], scored[-1]
            if high == low:
                ties += 1
                continue
            pairs.append({"prompt": ids, "chosen": chosen, "rejected": rejected, "scores": [high, low]})
    return pairs[:n], ties


def load_pairs():
    with open(PAIRS_PATH) as f:
        return json.load(f)


def main(n_train, n_valid):
    torch.manual_seed(1337)
    rng = np.random.default_rng(1337)
    model, tokenizer, _ = load_checkpoint(os.path.join(CHECKPOINTS, "sft", "model.pt"), pick_device())
    model.eval()
    max_prompt = model.config.block_size - MAX_TOKENS
    start = time.time()
    splits = {}
    for split, path, n, skip in [("train", "instruct_train.txt", n_train, 0), ("valid", "instruct_valid.txt", n_valid, 2000)]:
        by_length = load_asks(os.path.join(DATA_DIR, path), tokenizer, max_prompt, skip)
        pairs, ties = make_pairs(model, tokenizer, by_length, n, rng)
        chosen = np.mean([p["scores"][0] for p in pairs])
        rejected = np.mean([p["scores"][1] for p in pairs])
        print(f"{split}: {len(pairs)} perechi, {ties} egalități sărite | cuvinte folosite: {chosen:.0%} în cele preferate, "
              f"{rejected:.0%} în cele respinse | {(time.time() - start) / 60:.1f} min", flush=True)
        splits[split] = pairs
    os.makedirs(os.path.dirname(PAIRS_PATH), exist_ok=True)
    with open(PAIRS_PATH, "w") as f:
        json.dump(splits, f)
    print(f"salvate în {os.path.relpath(PAIRS_PATH)}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 500, int(sys.argv[2]) if len(sys.argv) > 2 else 50)
