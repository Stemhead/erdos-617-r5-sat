"""Finer split of the remaining cubes: k21b encoding (colour-1 blocks + colour-0 partition variables) with e_0 fixed."""
import sys, time, json
from multiprocessing import Pool
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver
import k21b
def work(args):
    sizes, E, e0 = args
    cnf, var, edges = k21b.build(21, sizes, E)
    pool = IDPool(start_from=cnf.nv + 1)
    cnf.extend(CardEnc.equals([var(e, 0) for e in edges], bound=e0, vpool=pool, encoding=EncType.seqcounter).clauses)
    t = time.time()
    with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
        r = s.solve()
    return sizes, E, e0, r, time.time() - t
if __name__ == "__main__":
    jobs = []
    for line in open("remaining.txt"):
        sz, E = line.split(); sz = tuple(int(x) for x in sz.split(",")); E = int(E)
        for e0 in range(45, 210 - 4 * E + 1): jobs.append((sz, E, e0))
    print(len(jobs), "sub-cubes", flush=True)
    t0 = time.time()
    with Pool(int(sys.argv[1])) as p:
        for sizes, E, e0, r, dt in p.imap_unordered(work, jobs):
            print(f"{time.time()-t0:8.1f}s split sizes={sizes} E={E} e0={e0} -> {'SAT' if r else 'UNSAT'} {dt:.1f}s", flush=True)
    print("SPLIT DONE", flush=True)
