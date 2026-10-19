"""Exhaustive sub-split of a low-regime cube by the colour-degree vector (d_0..d_4) of vertex 0 (sum 20).
Not a symmetry claim: plain case split, every vector is solved."""
import sys, time, itertools
from multiprocessing import Pool
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver
import k21
k = 5; N = 21
def work(args):
    sizes, E, dv = args
    cnf = k21.build(sizes, E)
    pool = IDPool(start_from=cnf.nv + 1)
    for c, d in enumerate(dv):
        lits = [k21.var((0, u), c) for u in range(1, N)]
        cnf.extend(CardEnc.equals(lits, bound=d, vpool=pool, encoding=EncType.seqcounter).clauses)
    t = time.time()
    with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
        r = s.solve()
    return sizes, E, dv, r, time.time() - t
if __name__ == "__main__":
    sizes = tuple(int(x) for x in sys.argv[1].split(",")); E = int(sys.argv[2]); nproc = int(sys.argv[3])
    dvs = [dv for dv in itertools.product(range(21), repeat=5) if sum(dv) == 20]
    print(len(dvs), "degree vectors", flush=True)
    t0 = time.time(); n = 0; mx = 0
    with Pool(nproc) as p:
        for sz, E_, dv, r, dt in p.imap_unordered(work, [(sizes, E, dv) for dv in dvs], chunksize=4):
            n += 1; mx = max(mx, dt)
            if r: print(f"SAT dv={dv}", flush=True)
            if n % 100 == 0 or dt > 30: print(f"{time.time()-t0:8.1f}s {n}/{len(dvs)} last dv={dv} {dt:.1f}s max={mx:.1f}s", flush=True)
    print(f"DVSPLIT DONE sizes={sizes} E={E}: {n} sub-cubes, max {mx:.1f}s", flush=True)
