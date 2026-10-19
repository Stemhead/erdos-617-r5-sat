"""Erdős #617 encoder: r-colour E(K_N) so that every (r+1)-set sees all r colours
(equivalently each colour class has independence number <= r)."""
import itertools, sys, time
from pysat.formula import CNF
from pysat.solvers import Solver

def build(N, r, symbreak=True):
    edges = list(itertools.combinations(range(N), 2))
    eid = {e: i for i, e in enumerate(edges)}
    var = lambda e, c: eid[e] * r + c + 1
    cnf = CNF()
    for e in edges:
        cnf.append([var(e, c) for c in range(r)])              # at least one colour
        for c1 in range(r):
            for c2 in range(c1 + 1, r):
                cnf.append([-var(e, c1), -var(e, c2)])        # at most one
    for S in itertools.combinations(range(N), r + 1):
        es = list(itertools.combinations(S, 2))
        for c in range(r):
            cnf.append([var(e, c) for e in es])               # colour c appears in S
    if symbreak:
        # colours are interchangeable: fix the colours of the star at vertex 0 in
        # "first occurrence" order -- edge (0,j) may only use a colour index <= max used so far + 1.
        # Simple version: colour of (0,1) is 0; (0,2) in {0,1}; (0,3) in {0,1,2}; ...
        for j in range(1, N):
            for c in range(min(j, r), r):
                cnf.append([-var((0, j), c)])
    return cnf, var, edges

if __name__ == "__main__":
    N, r = int(sys.argv[1]), int(sys.argv[2])
    solver = sys.argv[3] if len(sys.argv) > 3 else "cadical195"
    cnf, var, edges = build(N, r)
    print(f"N={N} r={r}: vars={cnf.nv} clauses={len(cnf.clauses)}", flush=True)
    t = time.time()
    with Solver(name=solver, bootstrap_with=cnf.clauses) as s:
        res = s.solve()
        print("SAT" if res else "UNSAT", f"{time.time()-t:.1f}s", flush=True)
        if res:
            m = set(l for l in s.get_model() if l > 0)
            col = {e: next(c for c in range(r) if var(e, c) in m) for e in edges}
            print(col)
