"""Empirical check of the lex symmetry-breaking encoding: take the affine K_20 colouring, repeatedly swap
adjacent vertices within a colour-1 part whenever row(u) > row(u+1) (as in the soundness proof), then confirm the
resulting labelling is admitted by the k21b encoding WITH lex on."""
import itertools
from pysat.solvers import Solver
import k21b
q = 5
pts = [(x, y) for x in range(q) for y in range(q)]
def cls(mm):
    if mm == 'v': return lambda p: p[0]
    return lambda p: (p[1] - mm * p[0]) % q
classes = [cls(mm) for mm in list(range(q)) + ['v']]
def colour(p, r):
    for c in range(4):
        if classes[c](p) == classes[c](r): return c
    return 4
x0 = (0, 0)
W = [p for p in pts if p != x0 and colour(p, x0) != 0]
W.sort(key=lambda p: classes[1](p))
N = len(W); sizes = (4, 4, 4, 4, 4)
M = [[None] * N for _ in range(N)]
for i, j in itertools.combinations(range(N), 2):
    M[i][j] = M[j][i] = colour(W[i], W[j])
def row(u, w):  # row u excluding columns u, w
    return [M[u][x] for x in range(N) if x not in (u, w)]
part = {}; v = 0
for i, s in enumerate(sizes):
    for _ in range(s): part[v] = i; v += 1
changed = True; swaps = 0
while changed:
    changed = False
    for u in range(N - 1):
        if part[u] != part[u + 1]: continue
        if row(u, u + 1) > row(u + 1, u):
            # swap labels u, u+1
            M[u], M[u + 1] = M[u + 1], M[u]
            for x in range(N): M[x][u], M[x][u + 1] = M[x][u + 1], M[x][u]
            changed = True; swaps += 1
print("swaps performed:", swaps)
cnf, var, edges = k21b.build(N, sizes, 30, lex=True, colour0=True)
assum = [var(e, M[e[0]][e[1]]) for e in edges]
with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
    print("lex-normalised affine K_20 admitted with lex ON:", "SAT" if s.solve(assumptions=assum) else "UNSAT")
