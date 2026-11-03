"""
Un sistem minimal de diferențiere automată, pentru numere (scalari).

Fiecare obiect Value ține un număr (data), gradientul pierderii în raport cu acel număr (grad) și legăturile spre
valorile din care a fost calculat. Metoda backward parcurge aceste legături invers și aplică regula lanțului.

Ideea și structura urmează micrograd, scris de Andrej Karpathy (https://github.com/karpathy/micrograd, licență MIT).
"""

import math


class Value:
    def __init__(self, data, _children=(), _op="", label=""):
        self.data = float(data)
        self.grad = 0.0  # derivata pierderii în raport cu această valoare, calculată de backward()
        self.label = label  # un nume opțional, afișat în diagrame
        # Valorile din care a fost calculată aceasta și operația care le-a combinat.
        self._prev = tuple(_children)
        self._op = _op
        # Trimite gradientul acestei valori spre valorile din care a fost calculată. Fiecare operație își scrie
        # propria funcție, iar o valoare introdusă direct (o intrare sau o pondere) nu are ce trimite mai departe.
        self._backward = lambda: None

    def __repr__(self):
        return f"Value(data={self.data:.4f}, grad={self.grad:.4f})"

    # Operațiile de bază: fiecare calculează rezultatul și își scrie derivata locală.

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), "+")

        def _backward():
            # La adunare, gradientul trece neschimbat spre ambii termeni.
            self.grad += out.grad
            other.grad += out.grad

        out._backward = _backward
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), "*")

        def _backward():
            # La înmulțire, fiecare factor primește gradientul înmulțit cu celălalt factor.
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad

        out._backward = _backward
        return out

    def __pow__(self, exponent):
        assert isinstance(exponent, (int, float)), "exponentul trebuie să fie un număr obișnuit"
        out = Value(self.data**exponent, (self,), f"**{exponent}")

        def _backward():
            self.grad += exponent * self.data ** (exponent - 1) * out.grad

        out._backward = _backward
        return out

    def exp(self):
        out = Value(math.exp(self.data), (self,), "exp")

        def _backward():
            # Derivata lui e^x este tot e^x, adică exact rezultatul.
            self.grad += out.data * out.grad

        out._backward = _backward
        return out

    def tanh(self):
        t = math.tanh(self.data)
        out = Value(t, (self,), "tanh")

        def _backward():
            self.grad += (1 - t**2) * out.grad

        out._backward = _backward
        return out

    def relu(self):
        out = Value(max(0.0, self.data), (self,), "relu")

        def _backward():
            # Gradientul trece doar dacă neuronul a fost activ (rezultat pozitiv).
            self.grad += (out.data > 0) * out.grad

        out._backward = _backward
        return out

    # Celelalte operații se scriu cu cele de mai sus, deci nu au nevoie de derivate proprii.

    def __neg__(self):
        return self * -1

    def __sub__(self, other):
        return self + (-other)

    def __truediv__(self, other):
        return self * other**-1

    # Variantele în care numărul obișnuit este primul termen, de exemplu 2 * x sau 1 - x.

    def __radd__(self, other):
        return self + other

    def __rmul__(self, other):
        return self * other

    def __rsub__(self, other):
        return other + (-self)

    def __rtruediv__(self, other):
        return other * self**-1

    def backward(self):
        # Ordinea topologică: fiecare valoare apare după toate valorile din care a fost calculată.
        topo = []
        visited = set()

        def build(v):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build(child)
                topo.append(v)

        build(self)

        # Derivata unei valori în raport cu ea însăși este 1. De aici, gradientul merge înapoi, nod cu nod.
        self.grad = 1.0
        for v in reversed(topo):
            v._backward()
