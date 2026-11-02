"""
Antrenarea unui MLP mic, construit din obiecte Value, pe două semilune de puncte (două clase).

Rulare: python moons.py (salvează imaginea frontierei de decizie în imagini/frontiera.svg).
"""

import math
import os
import random
import time

from engine import Value
from nn import MLP


def make_moons(n, noise=0.1, seed=0):
    # Două semilune întrepătrunse: punctele de pe semiluna de sus au eticheta +1, cele de jos, -1.
    rng = random.Random(seed)
    points, labels = [], []
    for i in range(n):
        t = math.pi * rng.random()
        if i % 2 == 0:
            x, y, label = math.cos(t), math.sin(t), 1.0
        else:
            x, y, label = 1 - math.cos(t), 0.5 - math.sin(t), -1.0
        points.append([x + rng.gauss(0, noise), y + rng.gauss(0, noise)])
        labels.append(label)
    return points, labels


def loss_and_accuracy(model, points, labels):
    scores = [model(p) for p in points]
    # Eroarea pătratică medie: scorul rețelei ar trebui să fie +1 pentru o clasă și -1 pentru cealaltă.
    loss = sum((s - y) ** 2 for s, y in zip(scores, labels)) / len(labels)
    # Clasa prezisă este semnul scorului.
    correct = sum((s.data > 0) == (y > 0) for s, y in zip(scores, labels))
    return loss, correct / len(labels)


def train(model, points, labels, steps=100, lr=0.1, log_every=10):
    for step in range(steps):
        # 1. Propagarea directă și pierderea, pe toate punctele odată.
        loss, accuracy = loss_and_accuracy(model, points, labels)
        # 2. Gradienții vechi se șterg, apoi retropropagarea calculează gradienții noi.
        model.zero_grad()
        loss.backward()
        # 3. Coborârea pe gradient: fiecare parametru face un pas mic în sensul în care pierderea scade.
        for p in model.parameters():
            p.data -= lr * p.grad
        if step % log_every == 0 or step == steps - 1:
            print(f"pasul {step:3d}   pierdere {loss.data:.4f}   acuratețe {accuracy:.0%}")


def save_boundary(model, points, labels, path, resolution=80):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Scorul rețelei pe o grilă de puncte, fără gradienți: ne interesează doar valorile.
    xs = [-1.5 + 4.0 * i / (resolution - 1) for i in range(resolution)]
    ys = [-1.2 + 2.9 * j / (resolution - 1) for j in range(resolution)]
    grid = [[model([x, y]).data for x in xs] for y in ys]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.contourf(xs, ys, grid, levels=[-100, 0, 100], colors=["#e8833a", "#3d6fd9"], alpha=0.25)
    ax.contour(xs, ys, grid, levels=[0], colors=["#888888"], linewidths=1)
    for label, color in [(1.0, "#3d6fd9"), (-1.0, "#e8833a")]:
        sel = [p for p, y in zip(points, labels) if y == label]
        ax.scatter([p[0] for p in sel], [p[1] for p in sel], s=16, color=color, edgecolors="none")
    ax.set_axis_off()
    fig.savefig(path, bbox_inches="tight", transparent=True)
    plt.close(fig)


if __name__ == "__main__":
    random.seed(1)
    points, labels = make_moons(100)
    model = MLP(2, [8, 8, 1])
    print(f"Puncte: {len(points)}, parametri: {len(model.parameters())}")

    start = time.time()
    train(model, points, labels, steps=200, lr=0.1, log_every=20)
    print(f"Durata antrenării: {time.time() - start:.1f} s")

    os.makedirs("imagini", exist_ok=True)
    save_boundary(model, points, labels, "imagini/frontiera.svg")
    print("Frontiera de decizie a fost salvată în imagini/frontiera.svg")
