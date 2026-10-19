"""Count 4-colourings of the 5x5 grid (K5 x K5 cross edges between two colour-0 cliques) such that every
3x3, 2x4, 4x2, 1x5, 5x1 subgrid contains all 4 colours. Raw count via SAT enumeration (cap), then orbits
under row perms x col perms x colour perms (and transpose) via canonical form."""
import itertools, sys
from pysat.formula import CNF
from pysat.solvers import Solver
R = C = 5; K = 4
var = lambda i, j, c: (i * C + j) * K + c + 1
cnf = CNF()
for i in range(R):
    for j in range(C):
        cnf.append([var(i, j, c) for c in range(K)])
        for c1 in range(K):
            for c2 in range(c1 + 1, K): cnf.append([-var(i, j, c1), -var(i, j, c2)])
def need(rows, cols):
    for c in range(K):
        cnf.append([var(i, j, c) for i in rows for j in cols])
for a, b in [(3, 3), (2, 4), (4, 2), (1, 5), (5, 1)]:
    for rows in itertools.combinations(range(R), a):
        for cols in itertools.combinations(range(C), b):
            need(rows, cols)
sols = []
with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
    while s.solve() and len(sols) < 2000000:
        m = s.get_model()
        g = tuple(tuple(next(c for c in range(K) if m[var(i, j, c) - 1] > 0) for j in range(C)) for i in range(R))
        sols.append(g)
        s.add_clause([-var(i, j, g[i][j]) for i in range(R) for j in range(C)])
print("raw solutions:", len(sols))
def canon(g):
    best = None
    for rp in itertools.permutations(range(R)):
        for cp in itertools.permutations(range(C)):
            for tr in (False, True):
                h = [[g[rp[i]][cp[j]] for j in range(C)] for i in range(R)]
                if tr: h = [list(x) for x in zip(*h)]
                # colour canonical: relabel by first occurrence
                mp = {}; out = []
                for row in h:
                    for x in row:
                        if x not in mp: mp[x] = len(mp)
                        out.append(mp[x])
                t = tuple(out)
                if best is None or t < best: best = t
    return best
if len(sols) <= 20000:
    classes = {canon(g) for g in sols}
    print("isomorphism classes:", len(classes))
    for cl in sorted(classes)[:10]:
        for i in range(R): print("  ", cl[i*C:(i+1)*C])
        print()
