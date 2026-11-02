"""
Diagramele grafurilor computaționale din laborator: o expresie înainte și după backward(), un neuron și o rețea mică.

Rulare: python diagrams.py (imaginile SVG se salvează în directorul imagini/).
"""

import os

from engine import Value
from graph import draw_graph
from nn import MLP

OUT = "imagini"


def expression():
    # L = (a * b + c) * f, cu fiecare valoare intermediară numită, ca să se vadă în diagramă.
    a = Value(2.0, label="a")
    b = Value(-3.0, label="b")
    c = Value(7.0, label="c")
    f = Value(-2.0, label="f")
    e = a * b
    e.label = "e"
    d = e + c
    d.label = "d"
    L = d * f
    L.label = "L"
    return L


def neuron():
    # Un neuron cu două intrări și activare tanh: o = tanh(x1 * w1 + x2 * w2 + b).
    x1 = Value(1.0, label="x1")
    x2 = Value(-2.0, label="x2")
    w1 = Value(0.5, label="w1")
    w2 = Value(0.25, label="w2")
    b = Value(0.8, label="b")
    x1w1 = x1 * w1
    x1w1.label = "x1*w1"
    x2w2 = x2 * w2
    x2w2.label = "x2*w2"
    s = x1w1 + x2w2
    s.label = "s"
    n = s + b
    n.label = "n"
    o = n.tanh()
    o.label = "o"
    return o


def tiny_mlp():
    # O rețea cu 2 intrări, un strat ascuns de 2 neuroni cu ReLU și o ieșire, plus pierderea pe un exemplu.
    model = MLP(2, [2, 1], activation="relu")
    # Ponderi alese de mână, cu nume, ca diagrama să fie ușor de citit. Primul neuron ascuns va fi activ,
    # al doilea nu (suma lui ponderată este negativă).
    hidden, output = model.layers[0].neurons, model.layers[1].neurons[0]
    values = {"w11": 0.5, "w12": -0.25, "b1": 0.1, "w21": -0.4, "w22": 0.3, "b2": 0.2}
    for j, n in enumerate(hidden, start=1):
        for i, w in enumerate(n.w, start=1):
            w.label, w.data = f"w{j}{i}", values[f"w{j}{i}"]
        n.b.label, n.b.data = f"b{j}", values[f"b{j}"]
    for j, (w, value) in enumerate(zip(output.w, [1.2, 0.6]), start=1):
        w.label, w.data = f"v{j}", value
    output.b.label, output.b.data = "c", 0.3

    x = [Value(1.0, label="x1"), Value(-1.0, label="x2")]
    y = model(x)
    y.label = "y"
    loss = (y - 1.0) ** 2  # eroarea pătratică față de ținta 1
    loss.label = "pierdere"
    return loss


def draw_before_and_after():
    # Același graf, desenat de două ori: imediat după calcul și după retropropagare.
    L = expression()
    draw_graph(L, f"{OUT}/expresie-inainte.svg")
    L.backward()
    draw_graph(L, f"{OUT}/expresie-dupa.svg")
    return L


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)

    L = draw_before_and_after()
    print("Expresia L = (a * b + c) * f")
    print(f"  L = {L.data}")

    o = neuron()
    o.backward()
    draw_graph(o, f"{OUT}/neuron.svg")
    print(f"Neuronul: o = {o.data:.4f}")

    loss = tiny_mlp()
    loss.backward()
    draw_graph(loss, f"{OUT}/retea-mica.svg")
    print(f"Rețeaua mică: pierderea = {loss.data:.4f}")

    print("Diagramele au fost salvate în", OUT)
