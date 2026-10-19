"""General encoder: k colours on K_N, colour c must have independence number <= a[c]
(i.e. every (a[c]+1)-set contains an edge of colour c).
Symmetry breaking: star at vertex 0 sorted by colour index; optional fixed degree vector."""
import itertools, sys, time
from pysat.formula import CNF
from pysat.solvers import Solver

def build(N, a, degvec=None):
    k = len(a)
    edges = list(itertools.combinations(range(N), 2))
    eid = {e: i for i, e in enumerate(edges)}
    var = lambda e, c: eid[e] * k + c + 1
    cnf = CNF()
    for e in edges:
        cnf.append([var(e, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                cnf.append([-var(e, c1), -var(e, c2)])
    for c in range(k):
        for S in itertools.combinations(range(N), a[c] + 1):
            cnf.append([var(e, c) for e in itertools.combinations(S, 2)])
    if degvec is None:
        # sorted star at vertex 0: colour(0,j) <= colour(0,j+1)
        for j in range(1, N - 1):
            for c in range(k):
                cnf.append([-var((0, j), c)] + [var((0, j + 1), c2) for c2 in range(c, k)])
    else:
        assert sum(degvec) == N - 1
        j = 1
        for c, d in enumerate(degvec):
            for _ in range(d):
                cnf.append([var((0, j), c)]); j += 1
    return cnf, var, edges

def solve(N, a, degvec=None, solver="cadical195", verbose=True):
    cnf, var, edges = build(N, a, degvec)
    t = time.time()
    with Solver(name=solver, bootstrap_with=cnf.clauses) as s:
        res = s.solve()
        dt = time.time() - t
        col = None
        if res:
            m = set(l for l in s.get_model() if l > 0)
            col = {e: next(c for c in range(len(a)) if var(e, c) in m) for e in edges}
    if verbose:
        print(f"N={N} a={a} deg={degvec}: vars={cnf.nv} clauses={len(cnf.clauses)} -> {'SAT' if res else 'UNSAT'} {dt:.1f}s", flush=True)
    return res, col, dt

if __name__ == "__main__":
    N = int(sys.argv[1]); a = [int(x) for x in sys.argv[2].split(",")]
    degvec = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 and sys.argv[3] != "-" else None
    solver = sys.argv[4] if len(sys.argv) > 4 else "cadical195"
    res, col, dt = solve(N, a, degvec, solver)
    if res: print(col)
