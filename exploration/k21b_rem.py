import sys, time, json
from multiprocessing import Pool
from pysat.solvers import Solver
import k21b
def work(args):
    sizes, E = args
    cnf, var, edges = k21b.build(21, sizes, E)
    t = time.time()
    with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
        r = s.solve()
    return sizes, E, r, time.time() - t
if __name__ == "__main__":
    jobs = []
    for line in open("remaining.txt"):
        sz, E = line.split(); jobs.append((tuple(int(x) for x in sz.split(",")), int(E)))
    t0 = time.time()
    with Pool(len(jobs)) as p:
        for sizes, E, r, dt in p.imap_unordered(work, jobs):
            print(f"{time.time()-t0:8.1f}s k21b sizes={sizes} E={E} -> {'SAT' if r else 'UNSAT'} {dt:.1f}s", flush=True)
    print("DONE", flush=True)
