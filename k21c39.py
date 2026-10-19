"""Alternative decomposition of the e_1 = 39 slice: cube over colour-0 Füredi blocks (sizes0, e_0) with
e_0 in [45, 54] (since e_1 = 39 = min(e_1..e_4) gives e_0 <= 210 - 156 = 54, t_0 <= 9), e_1 = 39 exactly.
Covers every colour-1 shape with e_1 = 39, in particular the still-open (5,4,4,4,4) cube."""
import sys, time, json, itertools
from math import comb
from multiprocessing import Pool
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver
import k21c
def cubes():
    out = []
    for e0 in range(45, 55):
        for p in itertools.combinations_with_replacement(range(0, 22), 4):
            if sum(p) == 21 and sum(comb(x, 2) for x in p) <= 45 + 2 * (e0 - 45):
                out.append((tuple(sorted(p, reverse=True)), e0))
    return sorted(set(out), key=lambda c: (c[1], c[0]))
def work(args):
    sizes, e0 = args
    cnf = k21c.build(sizes, e0, 39)
    pool = IDPool(start_from=cnf.nv + 1)
    cnf.extend(CardEnc.atmost([k21c.var(e, 1) for e in k21c.edges], bound=39, vpool=pool, encoding=EncType.seqcounter).clauses)
    t = time.time()
    with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
        r = s.solve(); m = s.get_model() if r else None
    col = None
    if r:
        mm = set(l for l in m if l > 0)
        col = {f"{e[0]}-{e[1]}": next(c for c in range(5) if k21c.var(e, c) in mm) for e in k21c.edges}
    return sizes, e0, r, time.time() - t, col
if __name__ == "__main__":
    cs = cubes(); print(len(cs), "cubes", flush=True)
    t0 = time.time(); n = 0
    with Pool(int(sys.argv[1])) as p:
        for sizes, e0, r, dt, col in p.imap_unordered(work, cs):
            n += 1
            print(f"{time.time()-t0:8.1f}s [{n}/{len(cs)}] sizes0={sizes} e0={e0} -> {'SAT' if r else 'UNSAT'} {dt:.1f}s", flush=True)
            if r: json.dump({"N": 21, "sizes0": sizes, "e0": e0, "colouring": col}, open(f"K21c39_SAT_{'-'.join(map(str,sizes))}_e0{e0}.json", "w"))
    print("C39 DONE", flush=True)
