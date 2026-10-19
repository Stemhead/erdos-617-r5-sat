"""Exact bottom-up computation of N(a), v2: each SAT question (n, a) is split into cubes over the colour-degree
vector of vertex 0, solved in parallel. Extra valid symmetry: vertex 0 has minimum colour-0 degree."""
import itertools, sys, json, time, os
from math import comb, ceil
from multiprocessing import Pool
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver
import bounds

k = 5
CACHE = "exact.json"
N = {}
key = lambda a: ",".join(map(str, sorted(a)))

def base(a):
    a = tuple(sorted(a))
    if a[0] == 0: return 0
    if a[0] == 1: return min(a[1:]) if a.count(1) == 1 else 1
    return None

def killed(n, a, subs):
    mins = [n - 1 - subs[c] for c in range(k)]
    if sum(mins) > n - 1: return "count"
    if sum(mins) == n - 1:
        for c in range(k):
            D = mins[c]
            if (n * D) % 2 == 1: return f"parity c={c} D={D}"
            clique_ok = all(D + 1 <= a[cc] for cc in range(k) if cc != c)
            if D >= 3 and not clique_ok:
                if ceil(n / D) > a[c]: return f"brooks c={c} D={D}"
            else:
                if ceil(n / (D + 1)) > a[c]: return f"greedy c={c} D={D}"
    return None

def trivial_bound(a):
    return next((s - 1 for s in range(2, 60) if sum(1 for x in a if x < s) > comb(s, 2)), 10**9)

def cubes(n, a, subs):
    lbs = [n - 1 - subs[c] for c in range(k)]
    out = []
    def rec(c, rem, cur):
        if c == k:
            if rem == 0: out.append(tuple(cur))
            return
        lo = max(lbs[c], 0)
        hi = rem
        if c > 0 and a[c] == a[c - 1] and c > 0 and c - 1 > 0:   # colours 1.. with equal a interchangeable (colour 0 is special: min-degree vertex)
            hi = min(hi, cur[-1])
        for d in range(hi, lo - 1, -1):
            rec(c + 1, rem - d, cur + [d])
    rec(0, n - 1, [])
    return out

def solve_cube(args):
    n, a, subs, dv, solver = args
    edges = list(itertools.combinations(range(n), 2))
    eid = {e: i for i, e in enumerate(edges)}
    var = lambda e, c: eid[e] * k + c + 1
    pool = IDPool(start_from=len(edges) * k + 1)
    cnf = CNF()
    for e in edges:
        cnf.append([var(e, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                cnf.append([-var(e, c1), -var(e, c2)])
    for c in range(k):
        for S in itertools.combinations(range(n), a[c] + 1):
            cnf.append([var(e, c) for e in itertools.combinations(S, 2)])
    # vertex 0 star fixed by cube
    j = 1
    for c, d in enumerate(dv):
        for _ in range(d):
            cnf.append([var((0, j), c)]); j += 1
    # degree lower bounds for all vertices; colour 0 degree >= dv[0] (vertex 0 minimal in colour 0)
    for v in range(1, n):
        for c in range(k):
            lb = n - 1 - subs[c]
            if c == 0: lb = max(lb, dv[0])
            if lb > 0:
                lits = [var(tuple(sorted((v, u))), c) for u in range(n) if u != v]
                cnf.extend(CardEnc.atleast(lits, bound=lb, vpool=pool, encoding=EncType.seqcounter).clauses)
    t = time.time()
    with Solver(name=solver, bootstrap_with=cnf.clauses) as s:
        res = s.solve()
        col = None
        if res:
            m = set(l for l in s.get_model() if l > 0)
            col = {f"{e[0]}-{e[1]}": next(c for c in range(k) if var(e, c) in m) for e in edges}
    return dv, res, time.time() - t, col

def sat_question(n, a, subs, nproc):
    """Returns (res, seconds, colouring or None)."""
    cs = cubes(n, a, subs)
    t0 = time.time()
    found = None
    with Pool(nproc) as p:
        for dv, res, dt, col in p.imap_unordered(solve_cube, [(n, a, subs, dv, "cadical195") for dv in cs]):
            if res:
                found = col
                p.terminate(); break
    return (found is not None), time.time() - t0, found, len(cs)

if __name__ == "__main__":
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    if os.path.exists(CACHE): N.update(json.load(open(CACHE)))
    os.makedirs("certs", exist_ok=True)
    vecs = sorted({tuple(sorted(v)) for v in itertools.product(range(0, 6), repeat=k)}, key=lambda v: (sum(v), v))
    t0 = time.time()
    for a in vecs:
        if key(a) in N: continue
        b = base(a)
        if b is not None:
            N[key(a)] = b; json.dump(N, open(CACHE, "w"), indent=0); continue
        lower = bounds.L(a)
        subs = [N[key(tuple(a[j] - (1 if j == c else 0) for j in range(k)))] for c in range(k)]
        n_max = min(1 + sum(subs) // 4, trivial_bound(a))
        val = lower; log = []
        for n in range(lower + 1, n_max + 1):
            kl = killed(n, a, subs)
            if kl: log.append((n, "killed:" + kl)); break
            res, dt, col, nc = sat_question(n, a, subs, nproc)
            log.append((n, "SAT" if res else "UNSAT", round(dt, 1), nc))
            if res:
                val = n
                json.dump({"n": n, "a": a, "colouring": col}, open(f"certs/colouring_n{n}_a{'-'.join(map(str,a))}.json", "w"))
            else: break
        N[key(a)] = val
        json.dump(N, open(CACHE, "w"), indent=0)
        print(f"{time.time()-t0:8.1f}s N{a} = {val}   [L={lower} nmax={n_max} subs={subs}] {log}", flush=True)
    print("DONE", flush=True)
