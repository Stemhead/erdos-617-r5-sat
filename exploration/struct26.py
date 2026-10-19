"""Erdős #617, r=5: K_26, 5 colours, every colour class alpha<=5 (and omega<=5).
Structure (Füredi 2015 stability): minority colour G_1 has 55 <= e <= 65 edges; its complement H is K_6-free with
e(H) = 270 - t, t = e(G_1) - 55 <= 10; so H can be made 5-partite by deleting <= t edges. WLOG (relabelling) the
parts are consecutive blocks of sizes n_1>=...>=n_5. Then colour 1 misses <= t within-part pairs and has exactly
E = 55 + t edges in total.  Cube = (size vector, E)."""
import itertools, sys, time, json
from math import comb
from multiprocessing import Pool
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

N, k = 26, 5
edges = list(itertools.combinations(range(N), 2))
eid = {e: i for i, e in enumerate(edges)}
var = lambda e, c: eid[e] * k + c + 1

def size_vectors():
    out = []
    for p in itertools.combinations_with_replacement(range(0, 27), 5):
        if sum(p) != 26: continue
        v = tuple(sorted(p, reverse=True))
        if sum(comb(x, 2) for x in v) <= 75: out.append(v)
    return sorted(set(out))

def lex_rows(cnf, pool, u, w, order_vertices):
    """row(u) <=_lex row(w) over positions order_vertices (excluding u, w), colours ordered 0<1<...<k-1.
    Sound symmetry breaking for the transposition (u w) (Codish et al.)."""
    pos = [x for x in order_vertices if x not in (u, w)]
    ev = lambda a, b: var(tuple(sorted((a, b))), 0)  # placeholder
    prev = None  # literal "all previous positions equal" (None = true)
    for x in pos:
        A = [var(tuple(sorted((u, x))), c) for c in range(k)]
        B = [var(tuple(sorted((w, x))), c) for c in range(k)]
        pre = [] if prev is None else [-prev]
        # prev -> A <= B : forbid A=c, B=c' with c > c'
        for c in range(k):
            for c2 in range(c):
                cnf.append(pre + [-A[c], -B[c2]])
        e = pool.id()
        # e -> prev ; e -> (A=c -> B=c)
        if prev is not None: cnf.append([-e, prev])
        for c in range(k):
            cnf.append([-e, -A[c], B[c]])
            # prev & A=c & B=c -> e
            cnf.append(pre + [-A[c], -B[c], e])
        prev = e

def build(sizes, E, extra=True, lex=True):
    pool = IDPool(start_from=len(edges) * k + 1)
    cnf = CNF()
    for e in edges:
        cnf.append([var(e, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                cnf.append([-var(e, c1), -var(e, c2)])
    for c in range(k):
        for S in itertools.combinations(range(N), 6):
            cnf.append([var(e, c) for e in itertools.combinations(S, 2)])            # alpha_c <= 5
            cnf.append([-var(e, c) for e in itertools.combinations(S, 2)])           # omega_c <= 5 (implied, redundant)
    # parts
    part = {}
    v = 0
    for i, s in enumerate(sizes):
        for _ in range(s): part[v] = i; v += 1
    within = [e for e in edges if part[e[0]] == part[e[1]]]
    t = E - 55
    # colour 1 (index 0) has exactly E edges
    lits = [var(e, 0) for e in edges]
    cnf.extend(CardEnc.equals(lits, bound=E, vpool=pool, encoding=EncType.seqcounter).clauses)
    # at most t within-part pairs are NOT colour 1
    if within:
        cnf.extend(CardEnc.atmost([-var(e, 0) for e in within], bound=t, vpool=pool, encoding=EncType.seqcounter).clauses)
    if lex:
        v = 0
        for sz in sizes:
            for u in range(v, v + sz - 1):
                lex_rows(cnf, pool, u, u + 1, range(N))
            v += sz
    if extra:
        # colour 1 is the minority: every other colour has >= E edges (and total 325 handled implicitly)
        for c in range(1, k):
            cnf.extend(CardEnc.atleast([var(e, c) for e in edges], bound=E, vpool=pool, encoding=EncType.seqcounter).clauses)
    return cnf

def solve(args):
    sizes, E, solver = args
    cnf = build(sizes, E)
    t0 = time.time()
    with Solver(name=solver, bootstrap_with=cnf.clauses) as s:
        res = s.solve()
        model = s.get_model() if res else None
    return sizes, E, res, time.time() - t0, model

if __name__ == "__main__":
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    only = sys.argv[2] if len(sys.argv) > 2 else None
    cubes = [(sz, E, "cadical195") for sz in size_vectors() for E in range(55, 66)
             if sum(comb(x, 2) for x in sz) - (E - 55) <= E]   # within pairs minus missing must fit in E
    if only == "probe":
        cubes = [c for c in cubes if c[0] in [(6,5,5,5,5), (7,5,5,5,4)] and c[1] in (55, 60, 65)]
    if only == "probe2":
        cubes = [c for c in cubes if (c[0], c[1]) in [((6,5,5,5,5), 60), ((6,5,5,5,5), 65), ((7,5,5,5,4), 65), ((6,5,5,5,5), 59)]]
    print(f"{len(cubes)} cubes", flush=True)
    t0 = time.time()
    with Pool(nproc) as p:
        for sizes, E, res, dt, model in p.imap_unordered(solve, cubes):
            print(f"{time.time()-t0:8.1f}s sizes={sizes} E={E} -> {'SAT' if res else 'UNSAT'} {dt:.1f}s", flush=True)
            if res:
                m = set(l for l in model if l > 0)
                col = {f"{e[0]}-{e[1]}": next(c for c in range(k) if var(e, c) in m) for e in edges}
                json.dump({"sizes": sizes, "E": E, "colouring": col}, open(f"K26_SAT_{'-'.join(map(str,sizes))}_{E}.json", "w"))
    print("DONE", flush=True)
