"""Solve N, a over all degree vectors of vertex 0 (with colour symmetry among equal a-values), in parallel."""
import sys, itertools, json, time
from multiprocessing import Pool
from enc2 import solve

def degvecs(N, a):
    k = len(a); tot = N - 1
    # group colours by a-value; within a group require non-increasing degrees (colour symmetry)
    out = []
    def rec(i, rem, cur):
        if i == k:
            if rem == 0: out.append(tuple(cur))
            return
        lo, hi = 0, rem
        if i > 0 and a[i] == a[i-1]: hi = min(hi, cur[-1])
        for d in range(hi, lo - 1, -1):
            rec(i + 1, rem - d, cur + [d])
    rec(0, tot, [])
    return out

def work(args):
    N, a, dv, solver = args
    res, col, dt = solve(N, a, list(dv), solver, verbose=False)
    return dv, res, dt, col

if __name__ == "__main__":
    N = int(sys.argv[1]); a = [int(x) for x in sys.argv[2].split(",")]
    nproc = int(sys.argv[3]); solver = sys.argv[4] if len(sys.argv) > 4 else "cadical195"
    dvs = degvecs(N, a)
    print(f"{len(dvs)} degree vectors", flush=True)
    t0 = time.time()
    with Pool(nproc) as p:
        for dv, res, dt, col in p.imap_unordered(work, [(N, a, dv, solver) for dv in dvs]):
            print(f"{time.time()-t0:8.1f}s dv={dv} {'SAT' if res else 'UNSAT'} {dt:.1f}s", flush=True)
            if res:
                with open(f"sat_{N}_{'-'.join(map(str,a))}_{'-'.join(map(str,dv))}.json", "w") as f:
                    json.dump({str(k): v for k, v in col.items()}, f)
    print("done", time.time() - t0, flush=True)
