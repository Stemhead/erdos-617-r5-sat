"""Full run of the K21 cubes with the k21b encoding (colour-1 blocks + colour-0 4-partite structure + lex)."""
import sys, time, json, os
from multiprocessing import Pool
from pysat.solvers import Solver
import k21, k21b
N = 21
def work(args):
    sizes, E = args
    cnf, var, edges = k21b.build(N, sizes, E)
    t0 = time.time()
    with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
        r = s.solve(); m = s.get_model() if r else None
    col = None
    if r:
        mm = set(l for l in m if l > 0)
        col = {f"{e[0]}-{e[1]}": next(c for c in range(5) if var(e, c) in mm) for e in edges}
    return sizes, E, r, time.time() - t0, col
if __name__ == "__main__":
    nproc = int(sys.argv[1]); Emin = int(sys.argv[2]) if len(sys.argv) > 2 else 34
    done = set()
    if os.path.exists("k21b_results.json"): done = set(json.load(open("k21b_results.json")).keys())
    cs = [c for c in k21.cubes() if c[1] >= Emin and f"{c[0]}|{c[1]}" not in done]
    cs.sort(key=lambda c: -c[1])   # hardest first
    print(f"{len(cs)} cubes", flush=True)
    results = json.load(open("k21b_results.json")) if os.path.exists("k21b_results.json") else {}
    t0 = time.time()
    with Pool(nproc) as p:
        for sizes, E, r, dt, col in p.imap_unordered(work, cs):
            results[f"{sizes}|{E}"] = ("SAT" if r else "UNSAT", round(dt, 1))
            json.dump(results, open("k21b_results.json", "w"), indent=1)
            print(f"{time.time()-t0:8.1f}s sizes={sizes} E={E} -> {'SAT' if r else 'UNSAT'} {dt:.1f}s", flush=True)
            if r: json.dump({"N": N, "a": [4,5,5,5,5], "sizes": sizes, "E": E, "colouring": col}, open(f"K21b_SAT_{'-'.join(map(str,sizes))}_E{E}.json", "w"))
    print("DONE", flush=True)
