"""
Un MLP 784 → 128 → 10 pentru MNIST, scris doar cu NumPy: propagarea directă, softmax, entropia încrucișată,
retropropagarea scrisă de mână și coborârea pe gradient cu loturi mici (SGD).

Rulare: python mnist_numpy.py (salvează exemple de predicții în imagini/).
"""

import os
import time

import numpy as np

from mnist_data import load_mnist


def init_params(n_in=784, n_hidden=128, n_out=10, seed=0):
    rng = np.random.default_rng(seed)
    # Inițializarea He: ponderi normale cu varianța 2 / numărul de intrări, potrivită pentru ReLU.
    return {
        "W1": (rng.standard_normal((n_in, n_hidden)) * np.sqrt(2 / n_in)).astype(np.float32),
        "b1": np.zeros(n_hidden, dtype=np.float32),
        "W2": (rng.standard_normal((n_hidden, n_out)) * np.sqrt(2 / n_hidden)).astype(np.float32),
        "b2": np.zeros(n_out, dtype=np.float32),
    }


def forward(params, x):
    # x are câte un rând pentru fiecare imagine din lot: forma (lot, 784).
    z1 = x @ params["W1"] + params["b1"]  # sumele ponderate ale celor 128 de neuroni ascunși
    h = np.maximum(z1, 0)  # ReLU
    logits = h @ params["W2"] + params["b2"]  # 10 scoruri nenormalizate, câte unul pentru fiecare cifră
    # Valorile intermediare sunt păstrate pentru retropropagare.
    return logits, (x, z1, h)


def softmax(logits):
    # Scădem maximul fiecărui rând: rezultatul este același, dar exp nu mai poate depăși valorile reprezentabile.
    e = np.exp(logits - logits.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


def cross_entropy(probs, y):
    # Media logaritmului negativ al probabilității date cifrei corecte.
    return -np.log(probs[np.arange(len(y)), y] + 1e-12).mean()


def backward(params, cache, probs, y):
    x, z1, h = cache
    n = len(y)
    # Gradientul pierderii în raport cu scorurile: probabilitățile, minus 1 la cifra corectă, împărțite la lot.
    dlogits = probs.copy()
    dlogits[np.arange(n), y] -= 1
    dlogits /= n
    # Stratul de ieșire: logits = h @ W2 + b2.
    dW2 = h.T @ dlogits
    db2 = dlogits.sum(axis=0)
    dh = dlogits @ params["W2"].T
    # ReLU lasă gradientul să treacă doar unde neuronul a fost activ.
    dz1 = dh * (z1 > 0)
    # Stratul ascuns: z1 = x @ W1 + b1.
    dW1 = x.T @ dz1
    db1 = dz1.sum(axis=0)
    return {"W1": dW1, "b1": db1, "W2": dW2, "b2": db2}


def predict(params, x):
    logits, _ = forward(params, x)
    return logits.argmax(axis=1)


def train(params, x_train, y_train, x_test, y_test, epochs=10, batch_size=64, lr=0.1, seed=0):
    rng = np.random.default_rng(seed)
    for epoch in range(1, epochs + 1):
        start = time.time()
        # La fiecare epocă, imaginile sunt amestecate și împărțite în loturi de câte 64.
        order = rng.permutation(len(x_train))
        total_loss = 0.0
        for i in range(0, len(order), batch_size):
            idx = order[i : i + batch_size]
            x, y = x_train[idx], y_train[idx]
            logits, cache = forward(params, x)
            probs = softmax(logits)
            total_loss += cross_entropy(probs, y) * len(y)
            grads = backward(params, cache, probs, y)
            for name in params:
                params[name] -= lr * grads[name]
        test_acc = (predict(params, x_test) == y_test).mean()
        print(
            f"epoca {epoch:2d}   pierdere {total_loss / len(x_train):.4f}   "
            f"acuratețe la testare {test_acc:.2%}   {time.time() - start:.1f} s"
        )
    return params


def save_examples(x_test, y_test, pred, path, count=12, mistakes=False):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Primele imagini din setul de testare sau primele imagini clasificate greșit.
    idx = np.flatnonzero(pred != y_test)[:count] if mistakes else np.arange(count)
    fig, axes = plt.subplots(1, count, figsize=(count * 0.9, 1.35))
    for ax, i in zip(axes, idx):
        ax.imshow(x_test[i].reshape(28, 28), cmap="gray")
        ok = pred[i] == y_test[i]
        title = f"{pred[i]}" if ok else f"{pred[i]} ({y_test[i]})"
        ax.set_title(title, color="#888888" if ok else "#e8833a", fontsize=11)
        ax.set_axis_off()
    fig.savefig(path, bbox_inches="tight", transparent=True, dpi=120)
    plt.close(fig)


if __name__ == "__main__":
    x_train, y_train, x_test, y_test = load_mnist()
    params = init_params()
    n_params = sum(p.size for p in params.values())
    print(f"Imagini de antrenare: {len(x_train)}, de testare: {len(x_test)}, parametri: {n_params:,}")

    start = time.time()
    params = train(params, x_train, y_train, x_test, y_test)
    print(f"Durata antrenării: {time.time() - start:.1f} s")

    pred = predict(params, x_test)
    print(f"Imagini de testare clasificate greșit: {(pred != y_test).sum()} din {len(y_test)}")
    # Perechile (cifra corectă, cifra prezisă) care apar cel mai des printre greșeli.
    pairs, counts = np.unique(np.stack([y_test, pred])[:, pred != y_test], axis=1, return_counts=True)
    for k in np.argsort(-counts, kind="stable")[:5]:
        print(f"  {pairs[0, k]} citit ca {pairs[1, k]}: de {counts[k]} ori")

    os.makedirs("imagini", exist_ok=True)
    save_examples(x_test, y_test, pred, "imagini/predictii.png")
    save_examples(x_test, y_test, pred, "imagini/greseli.png", mistakes=True)
    print("Exemplele au fost salvate în imagini/predictii.png și imagini/greseli.png")
