"""Structured encoder for Erdős #617 (r colours on K_N, every colour class alpha<=r), following
Erdős–Gyárfás: colour 0 = a minority colour (<= floor(C(N,2)/r) edges), vertex 0 = a vertex of
minimum colour-0 degree d (cube over d), other vertices have colour-0 degree >= d, star at vertex 0
sorted by colour, and degrees of colours 1..r-1 at vertex 0 non-increasing (colour symmetry)."""
import itertools, sys, time
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

def build(N, r, degvec, enc=EncType.seqcounter):
    """degvec = (d0, d1, ..., d_{r-1}) colour degrees of vertex 0, d0 = min colour-0 degree."""
    assert sum(degvec) == N - 1
    d0 = degvec[0]
    edges = list(itertools.combinations(range(N), 2))
    eid = {e: i for i, e in enumerate(edges)}
    pool = IDPool(start_from=len(edges) * r + 1)
    var = lambda e, c: eid[e] * r + c + 1
    cnf = CNF()
    for e in edges:
        cnf.append([var(e, c) for c in range(r)])
        for c1 in range(r):
            for c2 in range(c1 + 1, r):
                cnf.append([-var(e, c1), -var(e, c2)])
    for c in range(r):
        for S in itertools.combinations(range(N), r + 1):
            cnf.append([var(e, c) for e in itertools.combinations(S, 2)])
    # vertex 0 star fixed by degvec (sorted by colour)
    j = 1
    for c, d in enumerate(degvec):
        for _ in range(d):
            cnf.append([var((0, j), c)]); j += 1
    # minority colour 0: at most floor(C(N,2)/r) edges
    lits = [var(e, 0) for e in edges]
    cnf.extend(CardEnc.atmost(lits, bound=len(edges) // r, vpool=pool, encoding=enc).clauses)
    # every other vertex has colour-0 degree >= d0
    if d0 > 0:
        for v in range(1, N):
            lits = [var(tuple(sorted((v, u))), 0) for u in range(N) if u != v]
            cnf.extend(CardEnc.atleast(lits, bound=d0, vpool=pool, encoding=enc).clauses)
    return cnf, var, edges

def degvecs(N, r, dmax):
    out = []
    for d0 in range(0, dmax + 1):
        rem = N - 1 - d0
        def rec(i, rem, cur):
            if i == r:
                if rem == 0: out.append((d0,) + tuple(cur))
                return
            hi = rem if i == 1 else min(rem, cur[-1])
            for d in range(hi, -1, -1):
                rec(i + 1, rem - d, cur + [d])
        rec(1, rem, [])
    return out

def solve(N, r, degvec, solver="cadical195"):
    cnf, var, edges = build(N, r, degvec)
    t = time.time()
    with Solver(name=solver, bootstrap_with=cnf.clauses) as s:
        res = s.solve(); dt = time.time() - t
        col = None
        if res:
            m = set(l for l in s.get_model() if l > 0)
            col = {e: next(c for c in range(r) if var(e, c) in m) for e in edges}
    return res, col, dt, cnf.nv, len(cnf.clauses)

if __name__ == "__main__":
    N, r = int(sys.argv[1]), int(sys.argv[2])
    dmax = int(sys.argv[3])   # max min-degree of colour 0 to consider (floor(2E/(rN)))
    solver = sys.argv[4] if len(sys.argv) > 4 else "cadical195"
    dvs = degvecs(N, r, dmax)
    print(f"{len(dvs)} degree vectors", flush=True)
    t0 = time.time()
    for dv in dvs:
        res, col, dt, nv, nc = solve(N, r, dv, solver)
        print(f"{time.time()-t0:8.1f}s dv={dv} vars={nv} clauses={nc} -> {'SAT' if res else 'UNSAT'} {dt:.1f}s", flush=True)
        if res: print(col)
