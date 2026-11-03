"""
Același MLP 784 → 128 → 10 pentru MNIST, în PyTorch. Librăria face singură retropropagarea (autograd).

Rulare: python mnist_torch.py (are nevoie de PyTorch: pip install torch).
"""

import time

import numpy as np
import torch
import torch.nn as nn

from mnist_data import load_mnist
from mnist_numpy import backward, forward, init_params, softmax


def make_model():
    return nn.Sequential(nn.Linear(784, 128), nn.ReLU(), nn.Linear(128, 10))


def compare_gradients(x, y):
    # Aceleași ponderi în NumPy și în PyTorch, apoi gradienții calculați de mână și de autograd, pe același lot.
    params = init_params()
    logits, cache = forward(params, x)
    ours = backward(params, cache, softmax(logits), y)

    model = make_model()
    with torch.no_grad():
        # nn.Linear ține ponderile transpuse: forma (ieșiri, intrări).
        model[0].weight.copy_(torch.from_numpy(params["W1"].T))
        model[0].bias.copy_(torch.from_numpy(params["b1"]))
        model[2].weight.copy_(torch.from_numpy(params["W2"].T))
        model[2].bias.copy_(torch.from_numpy(params["b2"]))
    loss = nn.functional.cross_entropy(model(torch.from_numpy(x)), torch.from_numpy(y))
    loss.backward()

    theirs = {
        "W1": model[0].weight.grad.T,
        "b1": model[0].bias.grad,
        "W2": model[2].weight.grad.T,
        "b2": model[2].bias.grad,
    }
    for name in ours:
        diff = np.abs(ours[name] - theirs[name].numpy()).max()
        print(f"  {name}: diferența maximă {diff:.1e}")


def train(x_train, y_train, x_test, y_test, epochs=10, batch_size=64, lr=0.1, seed=0):
    torch.manual_seed(seed)
    model = make_model()
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)

    for epoch in range(1, epochs + 1):
        start = time.time()
        order = torch.randperm(len(x_train))
        total_loss = 0.0
        for i in range(0, len(order), batch_size):
            idx = order[i : i + batch_size]
            loss = nn.functional.cross_entropy(model(x_train[idx]), y_train[idx])  # softmax inclus
            optimizer.zero_grad()  # gradienții pasului anterior se șterg
            loss.backward()  # retropropagarea, făcută de autograd
            optimizer.step()  # p -= lr * p.grad, pentru fiecare parametru
            total_loss += loss.item() * len(idx)
        with torch.no_grad():
            test_acc = (model(x_test).argmax(dim=1) == y_test).float().mean().item()
        print(
            f"epoca {epoch:2d}   pierdere {total_loss / len(x_train):.4f}   "
            f"acuratețe la testare {test_acc:.2%}   {time.time() - start:.1f} s"
        )
    return model


if __name__ == "__main__":
    data = load_mnist()
    print("Gradienții NumPy față de autograd, pe un lot de 64 de imagini:")
    compare_gradients(data[0][:64], data[1][:64])
    print()
    start = time.time()
    train(*(torch.from_numpy(a) for a in data))
    print(f"Durata antrenării: {time.time() - start:.1f} s")
