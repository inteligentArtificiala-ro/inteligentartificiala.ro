"""Atenția cauzală scrisă de mână, pe o propoziție de șase tokenuri."""

import math

import torch
from torch.nn import functional as F

from model import CausalSelfAttention, GPTConfig


def attention(q, k, v):
    T, d = q.shape
    scores = q @ k.T / math.sqrt(d)
    future = torch.triu(torch.ones(T, T, dtype=torch.bool), diagonal=1)
    scores = scores.masked_fill(future, float("-inf"))
    weights = F.softmax(scores, dim=-1)
    return weights @ v, weights


def show(tokens, weights):
    print(" " * 6 + "".join(f"{t:>7}" for t in tokens))
    for token, row in zip(tokens, weights.tolist()):
        print(f"{token:>6}" + "".join(f"{w:7.2f}" if w > 0 else f"{'·':>7}" for w in row))


if __name__ == "__main__":
    torch.manual_seed(0)
    tokens = ["Lily", "has", "a", "red", "ball", "."]
    d_model, d_head = 16, 8
    x = torch.randn(len(tokens), d_model)
    W_q, W_k, W_v = (torch.randn(d_model, d_head) / math.sqrt(d_model) for _ in range(3))
    q, k, v = x @ W_q, x @ W_k, x @ W_v
    out, weights = attention(q, k, v)
    print(f"x {tuple(x.shape)} | q, k, v {tuple(q.shape)} | ieșire {tuple(out.shape)}")
    show(tokens, weights)
    reference = F.scaled_dot_product_attention(q[None], k[None], v[None], is_causal=True)[0]
    print(f"diferența maximă față de PyTorch: {(out - reference).abs().max().item():.1e}")

    config = GPTConfig()
    layer = CausalSelfAttention(config).eval()
    x = torch.randn(2, 10, config.n_embd)
    params = sum(p.numel() for p in layer.parameters())
    print(f"{config.n_head} capete de câte {config.n_embd // config.n_head}: {tuple(x.shape)} -> {tuple(layer(x).shape)}, "
          f"{params:,} parametri")
