"""
Graful computațional al unei valori, desenat cu Graphviz.

to_dot scrie graful ca text, în limbajul DOT al programului Graphviz, deci funcționează și fără Graphviz instalat.
draw_graph transformă textul într-o imagine, cu pachetul Python graphviz și programul dot
(https://graphviz.org/download/). În Jupyter și în Google Colab, imaginea apare direct sub celulă.
"""


def trace(root):
    # Toate valorile din care a fost calculată rădăcina și legăturile dintre ele, pornind de la rădăcină.
    nodes, edges = [], []
    seen = set()

    def build(v):
        if v in seen:
            return
        seen.add(v)
        nodes.append(v)
        for child in v._prev:
            edges.append((child, v))
            build(child)

    build(root)
    return nodes, edges


def to_dot(root, rankdir="LR"):
    nodes, edges = trace(root)
    ids = {v: f"v{i}" for i, v in enumerate(nodes)}
    lines = [
        "digraph {",
        f"  rankdir={rankdir}; nodesep=0.15; ranksep=0.3;",  # LR: de la stânga la dreapta, în ordinea calculului
        '  node [fontname="Helvetica", fontsize=11];',
    ]
    for v in nodes:
        # O valoare este un dreptunghi cu numele ei (dacă are unul) și, unul sub altul, valoarea și gradientul.
        name = f"{v.label} | " if v.label else ""
        fields = f"{{ data {v.data:.4f} | grad {v.grad:.4f} }}"
        lines.append(f'  {ids[v]} [shape=record, label="{{ {name}{fields} }}"];')
        if v._op:
            # Operația care a produs valoarea este un nod separat, de formă ovală, legat de rezultat.
            lines.append(f'  {ids[v]}_op [label="{v._op}", width=0.4, height=0.3];')
            lines.append(f"  {ids[v]}_op -> {ids[v]};")
    for child, parent in edges:
        lines.append(f"  {ids[child]} -> {ids[parent]}_op;")
    lines.append("}")
    return "\n".join(lines)


def draw_graph(root, path=None, rankdir="LR"):
    import graphviz

    graph = graphviz.Source(to_dot(root, rankdir))
    if path:
        # Formatul imaginii (svg, png, pdf) vine din extensia fișierului.
        graph.render(outfile=path, cleanup=True)
    return graph
