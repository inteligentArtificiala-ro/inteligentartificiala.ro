"""
Neuroni, straturi și o rețea neuronală cu mai multe straturi (MLP), construite din obiecte Value.
"""

import random

from engine import Value


class Module:
    def parameters(self):
        return []

    def zero_grad(self):
        # Gradienții se adună la fiecare backward(), așa că îi readucem la zero înaintea fiecărui pas.
        for p in self.parameters():
            p.grad = 0.0


class Neuron(Module):
    def __init__(self, nin, activation="tanh"):
        # Ponderi aleatoare mici, câte una pentru fiecare intrare, și un bias care pornește de la zero.
        self.w = [Value(random.uniform(-1, 1)) for _ in range(nin)]
        self.b = Value(0.0)
        self.activation = activation

    def __call__(self, x):
        # Suma ponderată a intrărilor plus bias, apoi funcția de activare.
        z = sum((wi * xi for wi, xi in zip(self.w, x)), self.b)
        if self.activation == "tanh":
            return z.tanh()
        if self.activation == "relu":
            return z.relu()
        return z  # fără activare, pentru stratul de ieșire

    def parameters(self):
        return self.w + [self.b]


class Layer(Module):
    def __init__(self, nin, nout, activation="tanh"):
        self.neurons = [Neuron(nin, activation) for _ in range(nout)]

    def __call__(self, x):
        # Toți neuronii stratului primesc aceleași intrări.
        out = [n(x) for n in self.neurons]
        return out[0] if len(out) == 1 else out

    def parameters(self):
        return [p for n in self.neurons for p in n.parameters()]


class MLP(Module):
    def __init__(self, nin, nouts, activation="tanh"):
        # De exemplu, MLP(2, [16, 16, 1]): 2 intrări, două straturi ascunse de câte 16 neuroni și o ieșire.
        sizes = [nin] + nouts
        self.layers = [
            Layer(sizes[i], sizes[i + 1], activation if i < len(nouts) - 1 else "linear")
            for i in range(len(nouts))
        ]

    def __call__(self, x):
        # Propagarea directă: ieșirile fiecărui strat devin intrările stratului următor.
        for layer in self.layers:
            x = layer(x)
        return x

    def parameters(self):
        return [p for layer in self.layers for p in layer.parameters()]
