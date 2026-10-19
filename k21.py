"""Rbar(5,6,6,6,6) <= 21 ?  i.e. no 5-colouring of K_21 with alpha_0 <= 4 and alpha_c <= 5 (c=1..4).
If true, Erdős #617 (r=5) follows by the degree argument (see NOTES.md).
Structure: colour 1 := minority among colours 1..4: e_1 <= (210 - e_0)/4 <= 41, Turán-min for alpha<=5 on 21
vertices is T=34 (parts 5,4,4,4,4), t_1 = e_1 - 34 <= 7; Füredi: 5 parts as consecutive blocks, M_1 <= t_1,
W_1 <= 2 e_1 - 34. Redundant facts: omega_c <= 4 for c>=1 (a K_5 of colour c is colour-0-independent),
omega_0 <= 5. Lex symmetry breaking within colour-1 parts."""
import itertools, sys, time, json, os
from math import comb
from multiprocessing import Pool
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver
from final import lex_rows
N, k, T = 21, 5, 34
edges = list(itertools.combinations(range(N), 2))
eid = {e: i for i, e in enumerate(edges)}
var = lambda e, c: eid[e] * k + c + 1

def size_vectors():
    out = set()
    for p in itertools.combinations_with_replacement(range(0, N + 1), 5):
        if sum(p) == N and sum(comb(x, 2) for x in p) <= 2 * 41 - T:
            out.add(tuple(sorted(p, reverse=True)))
    return sorted(out)

def cubes():
    return [(sz, E) for sz in size_vectors() for E in range(T, 42) if sum(comb(x, 2) for x in sz) <= 2 * E - T]

def build(sizes, E, lex=True):
    pool = IDPool(start_from=len(edges) * k + 1)
    cnf = CNF()
    for e in edges:
        cnf.append([var(e, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                cnf.append([-var(e, c1), -var(e, c2)])
    for S in itertools.combinations(range(N), 5):
        cnf.append([var(e, 0) for e in itertools.combinations(S, 2)])          # alpha_0 <= 4
        for c in range(1, k):
            cnf.append([-var(e, c) for e in itertools.combinations(S, 2)])     # omega_c <= 4 (redundant)
    for S in itertools.combinations(range(N), 6):
        for c in range(1, k):
            cnf.append([var(e, c) for e in itertools.combinations(S, 2)])      # alpha_c <= 5
        cnf.append([-var(e, 0) for e in itertools.combinations(S, 2)])         # omega_0 <= 5 (redundant)
    part = {}; v = 0
    for i, s in enumerate(sizes):
        for _ in range(s): part[v] = i; v += 1
    within = [e for e in edges if part[e[0]] == part[e[1]]]
    t = E - T
    cnf.extend(CardEnc.equals([var(e, 1) for e in edges], bound=E, vpool=pool, encoding=EncType.seqcounter).clauses)
    if within:
        cnf.extend(CardEnc.atmost([-var(e, 1) for e in within], bound=t, vpool=pool, encoding=EncType.seqcounter).clauses)
    for c in range(2, k):
        cnf.extend(CardEnc.atleast([var(e, c) for e in edges], bound=E, vpool=pool, encoding=EncType.seqcounter).clauses)
    # e_0 <= 210 - 4E
    cnf.extend(CardEnc.atmost([var(e, 0) for e in edges], bound=210 - 4 * E, vpool=pool, encoding=EncType.seqcounter).clauses)
    if lex:
        v = 0
        for sz in sizes:
            for u in range(v, v + sz - 1):
                lex_rows(cnf, pool, var, u, u + 1, N)
            v += sz
    return cnf

def solve(args):
    sizes, E = args
    cnf = build(sizes, E)
    t0 = time.time()
    with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
        r = s.solve(); m = s.get_model() if r else None
    col = None
    if r:
        mm = set(l for l in m if l > 0)
        col = {f"{e[0]}-{e[1]}": next(c for c in range(k) if var(e, c) in mm) for e in edges}
    return sizes, E, r, time.time() - t0, col, cnf.nv, len(cnf.clauses)

if __name__ == "__main__":
    nproc = int(sys.argv[1])
    cs = cubes()
    if len(sys.argv) > 2 and sys.argv[2] == "probe":
        cs = [c for c in cs if c[0] == (5,4,4,4,4) and c[1] in (34, 37, 41)]
    if len(sys.argv) > 2 and sys.argv[2] == "emax":
        Emax = int(sys.argv[3]); import re, os
        done = set()
        for logf in sys.argv[4:]:
            for line in open(logf):
                m = re.search(r"sizes=\((.*?)\) E=(\d+) .*-> UNSAT", line)
                if m: done.add((tuple(int(x) for x in m.group(1).split(",")), int(m.group(2))))
        cs = [c for c in cs if c[1] <= Emax and c not in done]
        cs.sort(key=lambda c: -c[1])
    print(f"{len(cs)} cubes; size vectors {size_vectors()}", flush=True)
    t0 = time.time()
    with Pool(nproc) as p:
        for sizes, E, r, dt, col, nv, nc in p.imap_unordered(solve, cs):
            print(f"{time.time()-t0:8.1f}s sizes={sizes} E={E} nv={nv} nc={nc} -> {'SAT' if r else 'UNSAT'} {dt:.1f}s", flush=True)
            if r: json.dump({"N": N, "a": [4,5,5,5,5], "sizes": sizes, "E": E, "colouring": col}, open(f"K21_SAT_{'-'.join(map(str,sizes))}_E{E}.json", "w"))
    print("DONE", flush=True)
