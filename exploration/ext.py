"""Extension experiments from the affine-plane colouring.
(1) Can the affine K_25 balanced colouring be extended to K_26?  (expect UNSAT)
(2) Take W = K_20 sub-colouring (alpha_0<=4 on W). Can it be extended by t new vertices keeping
    alpha_0<=4 and alpha_c<=5 (c=1..4)?  t=1 => a K_21 witness for Rbar(5,6,6,6,6)>=22."""
import itertools, sys, time
from pysat.formula import CNF
from pysat.solvers import Solver
q = 5
pts = [(x, y) for x in range(q) for y in range(q)]
def cls(m):
    if m == 'v': return lambda p: p[0]
    return lambda p: (p[1] - m * p[0]) % q
classes = [cls(m) for m in list(range(q)) + ['v']]
def colour(p, r):
    for c in range(4):
        if classes[c](p) == classes[c](r): return c
    return 4

def extend(base_pts, base_col, a, t, solver="cadical195"):
    """base_col: dict over pairs of base vertices (indices) -> colour. Add t new vertices."""
    n0 = len(base_pts); N = n0 + t; k = len(a)
    edges = list(itertools.combinations(range(N), 2))
    eid = {e: i for i, e in enumerate(edges)}
    var = lambda e, c: eid[e] * k + c + 1
    cnf = CNF()
    for e in edges:
        if e[1] < n0:
            for c in range(k):
                cnf.append([var(e, c)] if c == base_col[e] else [-var(e, c)])
        else:
            cnf.append([var(e, c) for c in range(k)])
            for c1 in range(k):
                for c2 in range(c1 + 1, k):
                    cnf.append([-var(e, c1), -var(e, c2)])
    for c in range(k):
        for S in itertools.combinations(range(N), a[c] + 1):
            if S[-1] < n0: continue   # already satisfied by base
            cnf.append([var(e, c) for e in itertools.combinations(S, 2)])
    t0 = time.time()
    with Solver(name=solver, bootstrap_with=cnf.clauses) as s:
        res = s.solve()
    print(f"base n={n0} +{t} new, a={a}: vars={cnf.nv} clauses={len(cnf.clauses)} -> {'SAT' if res else 'UNSAT'} {time.time()-t0:.1f}s", flush=True)
    return res

# (1) full affine K_25 -> K_26
idx = {p: i for i, p in enumerate(pts)}
col25 = {(idx[p], idx[r]): colour(p, r) for p, r in itertools.combinations(pts, 2)}
extend(pts, col25, [5]*5, 1)
# (2) W = K_20: remove x=(0,0) and its colour-0 neighbours
x = (0, 0)
W = [p for p in pts if p != x and colour(p, x) != 0]
widx = {p: i for i, p in enumerate(W)}
col20 = {(widx[p], widx[r]): colour(p, r) for p, r in itertools.combinations(W, 2)}
for t in (1, 2):
    extend(W, col20, [4, 5, 5, 5, 5], t)
