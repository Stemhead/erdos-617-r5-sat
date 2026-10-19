"""Conquer phase: solve each cube (icnf 'a ... 0' lines) of a base CNF with CaDiCaL under assumptions, in parallel."""
import sys, time
from multiprocessing import Pool
from pysat.formula import CNF
from pysat.solvers import Solver
BASE = None
def init(path):
    global BASE
    BASE = CNF(from_file=path)
def work(cube):
    t = time.time()
    with Solver(name="cadical195", bootstrap_with=BASE.clauses) as s:
        r = s.solve(assumptions=cube)
        m = s.get_model() if r else None
    return cube, r, time.time() - t, m
if __name__ == "__main__":
    cnf_path, icnf_path, nproc = sys.argv[1], sys.argv[2], int(sys.argv[3])
    cubes = []
    for line in open(icnf_path):
        if line.startswith("a "):
            cubes.append([int(x) for x in line.split()[1:-1]])
    print(f"{len(cubes)} cubes", flush=True)
    t0 = time.time(); done = 0; nsat = 0; maxt = 0
    with Pool(nproc, initializer=init, initargs=(cnf_path,)) as p:
        for cube, r, dt, m in p.imap_unordered(work, cubes, chunksize=1):
            done += 1; maxt = max(maxt, dt)
            if r:
                nsat += 1
                print(f"SAT cube {cube}", flush=True)
                open("SAT_MODEL.txt", "w").write(" ".join(map(str, m)))
            if done % 50 == 0 or dt > 60:
                print(f"{time.time()-t0:8.1f}s done {done}/{len(cubes)} sat={nsat} last={dt:.1f}s max={maxt:.1f}s", flush=True)
    print(f"DONE {done} cubes, SAT={nsat}, {time.time()-t0:.0f}s, max cube {maxt:.1f}s", flush=True)
