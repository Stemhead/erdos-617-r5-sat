"""Verify: affine plane AG(2,5) gives a 5-colouring of K_25 with every colour class alpha<=5,
and removing a vertex x and its colour-c neighbours gives K_20 with alpha_c<=4, others <=5."""
import itertools, networkx as nx
q = 5
pts = [(x, y) for x in range(q) for y in range(q)]
# parallel classes: slopes 0..q-1 (y = m x + b) and vertical
def cls(m):
    if m == 'v': return lambda p: p[0]
    return lambda p: (p[1] - m * p[0]) % q
classes = [cls(m) for m in list(range(q)) + ['v']]
# colours: 4 single classes + merged pair (classes 4 and 'v')
def colour(p, r):
    for c in range(4):
        if classes[c](p) == classes[c](r): return c
    return 4
def alpha(G):
    # brute force max independent set via complement clique
    return max(len(c) for c in nx.find_cliques(nx.complement(G)))
col = {}
for p, r in itertools.combinations(pts, 2):
    col[(p, r)] = colour(p, r)
for c in range(5):
    G = nx.Graph(); G.add_nodes_from(pts)
    G.add_edges_from(e for e, cc in col.items() if cc == c)
    degs = set(dict(G.degree()).values())
    print("colour", c, "edges", G.number_of_edges(), "degrees", degs, "alpha", alpha(G))
# sub-colouring: remove x=(0,0) and its colour-0 neighbours
x = (0, 0)
W = [p for p in pts if p != x and colour(p, x) != 0]
print("W size", len(W))
for c in range(5):
    G = nx.Graph(); G.add_nodes_from(W)
    G.add_edges_from((p, r) for p, r in itertools.combinations(W, 2) if colour(p, r) == c)
    print("  colour", c, "alpha on W", alpha(G))
