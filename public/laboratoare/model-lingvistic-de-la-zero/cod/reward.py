"""Recompensa: câte dintre cuvintele cerute de o instrucțiune apar în poveste. Și măsurarea unui model."""

import os
import re
import sys

import torch

from checkpoint import load_checkpoint
from data import DATA_DIR
from model import pick_device
from sft import instruction, parse
from tokenizer import EOT

INSTRUCTIONS = 50
MAX_TOKENS = 200


def words_used(story, words):
    return sum(bool(re.search(rf"\b{re.escape(w)}(s|es|d|ed|ing)?\b", story, re.I)) for w in words)


def load_instructions(path, n):
    with open(path, encoding="utf-8") as f:
        docs = [parse(doc) for doc in f.read().split(EOT)]
    asks = [fields for fields in docs if "Words" in fields and "Story" in fields][:n]
    return [(instruction(fields), fields["Words"].split(", ")) for fields in asks]


@torch.no_grad()
def measure(model, tokenizer, instructions):
    model.eval()
    device = next(model.parameters()).device
    used, ended = 0, 0
    for prompt, words in instructions:
        ids = torch.tensor([tokenizer.encode(prompt)], device=device)
        out = model.generate(ids, MAX_TOKENS, temperature=0.8, top_k=50, eos_id=tokenizer.eot_id)
        story = out[0, ids.size(1) :].tolist()
        used += words_used(tokenizer.decode(story), words)
        ended += story[-1] == tokenizer.eot_id
    return used / sum(len(words) for _, words in instructions), ended / len(instructions)


def main(paths):
    instructions = load_instructions(os.path.join(DATA_DIR, "instruct_valid.txt"), INSTRUCTIONS)
    asked = sum(len(words) for _, words in instructions)
    print(f"{len(instructions)} instrucțiuni de validare, {asked} de cuvinte cerute")
    for path in paths:
        torch.manual_seed(0)
        model, tokenizer, _ = load_checkpoint(path, pick_device())
        used, ended = measure(model, tokenizer, instructions)
        name = os.path.basename(os.path.dirname(path))
        print(f"{name:<10} cuvinte folosite {used:6.1%} | povești terminate {ended:5.0%}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
