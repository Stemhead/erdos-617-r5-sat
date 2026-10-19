"""Independent check of a saved colouring: every colour class must have independence number <= 5
(equivalently every 6-set sees all 5 colours). Uses networkx clique search on complements, plus a direct
brute-force 6-set scan."""
import sys, json, itertools, networkx as nx
d = json.load(open(sys.argv[1]))
N = d["N"]; col = {tuple(map(int, e.split("-"))): c for e, c in d["colouring"].items()}
assert len(col) == N * (N - 1) // 2
for c in range(5):
    G = nx.Graph(); G.add_nodes_from(range(N)); G.add_edges_from(e for e, cc in col.items() if cc == c)
    alpha = max(len(q) for q in nx.find_cliques(nx.complement(G)))
    omega = max(len(q) for q in nx.find_cliques(G))
    print(f"colour {c}: edges={G.number_of_edges()} alpha={alpha} omega={omega}")
    assert alpha <= 5
bad = 0
for S in itertools.combinations(range(N), 6):
    if len({col[e] for e in itertools.combinations(S, 2)}) < 5: bad += 1
print("6-sets missing a colour:", bad)
print("VALID" if bad == 0 else "INVALID")
