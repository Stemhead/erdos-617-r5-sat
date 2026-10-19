"""K_21, a=(4,5,5,5,5), HIGH regime: e_1 := min(e_1..e_4) >= Emin (default 40). Then e_0 <= 210 - 4*Emin and
colour 0 (alpha<=4, complement K_5-free, Turán-min 45) is Füredi-structured with t_0 = e_0 - 45 <= 165 - 4 Emin:
cube = (colour-0 part sizes as consecutive blocks, e_0).  Lex within colour-0 blocks.
Colour 1 = minority among 1..4 (cardinality), e_1 >= Emin."""
import itertools, sys, time, json
from math import comb
from multiprocessing import Pool
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.pb import PBEnc
from pysat.solvers import Solver
from final import lex_rows
N, k, T0 = 21, 5, 45
edges = list(itertools.combinations(range(N), 2))
eid = {e: i for i, e in enumerate(edges)}
var = lambda e, c: eid[e] * k + c + 1

def cubes(Emin):
    out = []
    e0max = 210 - 4 * Emin
    for e0 in range(T0, e0max + 1):
        t0 = e0 - T0
        for p in itertools.combinations_with_replacement(range(0, N + 1), 4):
            if sum(p) == N and sum(comb(x, 2) for x in p) <= T0 + 2 * t0:
                out.append((tuple(sorted(p, reverse=True)), e0))
    return sorted(set(out), key=lambda c: (-c[1], c[0]))

def build(sizes, e0, Emin, lex=True):
    pool = IDPool(start_from=len(edges) * k + 1)
    cnf = CNF()
    for e in edges:
        cnf.append([var(e, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                cnf.append([-var(e, c1), -var(e, c2)])
    for S in itertools.combinations(range(N), 5):
        cnf.append([var(e, 0) for e in itertools.combinations(S, 2)])
        for c in range(1, k):
            cnf.append([-var(e, c) for e in itertools.combinations(S, 2)])
    for S in itertools.combinations(range(N), 6):
        for c in range(1, k):
            cnf.append([var(e, c) for e in itertools.combinations(S, 2)])
        cnf.append([-var(e, 0) for e in itertools.combinations(S, 2)])
    part = {}; v = 0
    for i, s in enumerate(sizes):
        for _ in range(s): part[v] = i; v += 1
    within = [e for e in edges if part[e[0]] == part[e[1]]]
    t0 = e0 - T0
    cnf.extend(CardEnc.equals([var(e, 0) for e in edges], bound=e0, vpool=pool, encoding=EncType.seqcounter).clauses)
    if within:
        cnf.extend(CardEnc.atmost([-var(e, 0) for e in within], bound=t0, vpool=pool, encoding=EncType.seqcounter).clauses)
    # colour 1 minority among 1..4 and >= Emin
    n = len(edges)
    for c in range(2, k):
        pb = PBEnc.leq(lits=[var(e, 1) for e in edges] + [-var(e, c) for e in edges], weights=[1] * (2 * n), bound=n, vpool=pool)
        cnf.extend(pb.clauses)
    cnf.extend(CardEnc.atleast([var(e, 1) for e in edges], bound=Emin, vpool=pool, encoding=EncType.seqcounter).clauses)
    if lex:
        v = 0
        for sz in sizes:
            for u in range(v, v + sz - 1):
                lex_rows(cnf, pool, var, u, u + 1, N)
            v += sz
    return cnf

def work(args):
    sizes, e0, Emin = args
    cnf = build(sizes, e0, Emin)
    t = time.time()
    with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
        r = s.solve(); m = s.get_model() if r else None
    col = None
    if r:
        mm = set(l for l in m if l > 0)
        col = {f"{e[0]}-{e[1]}": next(c for c in range(k) if var(e, c) in mm) for e in edges}
    return sizes, e0, r, time.time() - t, col, cnf.nv, len(cnf.clauses)

if __name__ == "__main__":
    nproc = int(sys.argv[1]); Emin = int(sys.argv[2])
    cs = cubes(Emin)
    if len(sys.argv) > 3 and sys.argv[3] == "probe": cs = cs[:int(sys.argv[4])]
    print(f"Emin={Emin}: {len(cs)} cubes: {cs}", flush=True)
    t0 = time.time()
    with Pool(nproc) as p:
        for sizes, e0, r, dt, col, nv, nc in p.imap_unordered(work, [(sz, e0, Emin) for sz, e0 in cs]):
            print(f"{time.time()-t0:8.1f}s sizes0={sizes} e0={e0} nv={nv} nc={nc} -> {'SAT' if r else 'UNSAT'} {dt:.1f}s", flush=True)
            if r: json.dump({"N": N, "sizes0": sizes, "e0": e0, "colouring": col}, open(f"K21c_SAT_{'-'.join(map(str,sizes))}_e0{e0}.json", "w"))
    print("DONE", flush=True)
