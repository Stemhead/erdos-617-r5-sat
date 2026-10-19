"""Exact bottom-up computation of N(a) for 5-colourings with alpha_c <= a_c.
Uses exact lower-level values for degree constraints d_c(v) >= n-1-N(a-e_c)."""
import itertools, sys, json, time, os
from math import comb, ceil
from multiprocessing import Pool
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver
import bounds  # L (affine lower bounds)

k = 5
CACHE = "exact.json"
N = {}   # tuple -> exact value

def key(a): return ",".join(map(str, sorted(a)))

def base(a):
    a = tuple(sorted(a))
    if a[0] == 0: return 0
    if a[0] == 1: return min(a[1:]) if a.count(1) == 1 else 1
    return None

def count_bound(a, lower):
    """Upper bound at level a from exact lower values: smallest n > lower that is NOT killed by counting/parity/Brooks; returns (ubound, killed_list)"""
    a = tuple(sorted(a))
    subs = [N[key(tuple(a[j] - (1 if j == c else 0) for j in range(k)))] for c in range(k)]
    tb = 10**9
    for s in range(2, 60):
        if sum(1 for x in a if x < s) > comb(s, 2): tb = s - 1; break
    n_max = min(1 + sum(subs) // 4, tb)
    def killed(n):
        mins = [n - 1 - subs[c] for c in range(k)]
        if sum(mins) > n - 1: return True
        if sum(mins) == n - 1:
            for c in range(k):
                D = mins[c]
                if (n * D) % 2 == 1: return True
                clique_ok = all(D + 1 <= a[cc] for cc in range(k) if cc != c)
                if D >= 3 and not clique_ok:
                    if ceil(n / D) > a[c]: return True
                else:
                    if ceil(n / (D + 1)) > a[c]: return True
        return False
    # candidates n in (lower, n_max]; N(a) = largest n not killed, but killing is monotone? not necessarily; be safe:
    # we need to SAT-check every n in (lower, n_max] that is not killed, in increasing order, stopping at first UNSAT
    cands = [n for n in range(lower + 1, n_max + 1) if not killed(n)]
    return n_max, subs, cands

def sat_instance(n, a, subs, solver="cadical195"):
    a = tuple(sorted(a))
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
    # degree lower bounds
    for v in range(n):
        for c in range(k):
            lb = n - 1 - subs[c]
            if lb > 0:
                lits = [var(tuple(sorted((v, u))), c) for u in range(n) if u != v]
                if lb > len(lits): return False, 0.0
                cnf.extend(CardEnc.atleast(lits, bound=lb, vpool=pool, encoding=EncType.seqcounter).clauses)
    # symmetry: sorted star at vertex 0
    for j in range(1, n - 1):
        for c in range(k):
            cnf.append([-var((0, j), c)] + [var((0, j + 1), c2) for c2 in range(c, k)])
    t = time.time()
    with Solver(name=solver, bootstrap_with=cnf.clauses) as s:
        res = s.solve()
    return res, time.time() - t

def compute(args):
    a, lower, n_max, subs, cands = args
    log = []
    val = lower
    for n in cands:
        res, dt = sat_instance(n, a, subs)
        log.append((n, "SAT" if res else "UNSAT", round(dt, 1)))
        if res: val = n
        else: break
    else:
        pass
    # if we exhausted candidates with all SAT, val = last SAT (and n_max bounds it)
    return a, val, f"L={lower} nmax={n_max} subs={subs}", log

if __name__ == "__main__":
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    if os.path.exists(CACHE): N.update(json.load(open(CACHE)))
    vecs = sorted({tuple(sorted(v)) for v in itertools.product(range(0, 6), repeat=k)}, key=lambda v: (sum(v), v))
    levels = {}
    for v in vecs: levels.setdefault(sum(v), []).append(v)
    t0 = time.time()
    for s in sorted(levels):
        todo = [v for v in levels[s] if key(v) not in N]
        if not todo: continue
        jobs = []
        for v in todo:
            b = base(v)
            if b is not None:
                N[key(v)] = b; print(f"N{v} = {b} [base]", flush=True); continue
            lower = bounds.L(v)
            n_max, subs, cands = count_bound(v, lower)
            jobs.append((v, lower, n_max, subs, cands))
        json.dump(N, open(CACHE, "w"), indent=0)
        if not jobs: continue
        with Pool(min(nproc, len(jobs))) as p:
            for a, val, info, log in p.imap_unordered(compute, jobs):
                N[key(a)] = val
                print(f"{time.time()-t0:8.1f}s N{a} = {val}   [{info}] {log}", flush=True)
                json.dump(N, open(CACHE, "w"), indent=0)
    print("DONE", flush=True)
