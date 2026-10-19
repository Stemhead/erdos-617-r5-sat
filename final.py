"""Erdős #617, r = 5.  Decide whether K_N (N=26) has a 5-edge-colouring in which every 6-set sees all 5 colours.
Equivalently every colour class G_c has alpha(G_c) <= 5 (and then also omega(G_c) <= 5).

Structure used (all provable, see NOTES.md):
 * T := min #edges of a graph on N vertices with alpha <= 5 = sum C(n_i,2) over 5 near-equal parts (Turán).
   Every colour class has >= T edges; the minority colour 0 has E := e(G_0) in [T, C(N,2)/5].
 * Füredi (2015): complement of G_0 is K_6-free with ex(N,K_6) - t edges, t = E - T, hence can be made
   5-partite by deleting <= t edges. Relabel so the parts are consecutive blocks of sizes n_1>=...>=n_5.
   Then: #within-part pairs not of colour 0 (M) <= t, and sum C(n_i,2) =: W <= 2E - T.
 * Colour 1 := the minority among colours 1..4 (so e(G_1) <= e(G_c), c=2,3,4 and e(G_1) <= (C(N,2)-E)/4);
   it has its own (free) 5-partition P with first-occurrence part labels, and Füredi gives
   2*M_1 + T <= W_1 + X_1   and   W_1 <= 2 e(G_1) - T.
 * Within each colour-0 part, consecutive vertices u,u+1 satisfy row(u) <=_lex row(u+1) (Codish-style).
Cube = (size vector, E)."""
import itertools, sys, time, json, os
from math import comb
from multiprocessing import Pool
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.pb import PBEnc
from pysat.solvers import Solver

k = 5

def turan_min(N):
    q, r = divmod(N, 5)
    return r * comb(q + 1, 2) + (5 - r) * comb(q, 2)

def setup(N):
    edges = list(itertools.combinations(range(N), 2))
    eid = {e: i for i, e in enumerate(edges)}
    return edges, (lambda e, c: eid[e] * k + c + 1)

def size_vectors(N, T):
    out = set()
    for p in itertools.combinations_with_replacement(range(0, N + 1), 5):
        if sum(p) == N and sum(comb(x, 2) for x in p) <= 2 * (comb(N, 2) // 5) - T:
            out.add(tuple(sorted(p, reverse=True)))
    return sorted(out)

def cubes_for(N):
    T = turan_min(N); Emax = comb(N, 2) // 5
    return [(sz, E) for sz in size_vectors(N, T) for E in range(T, Emax + 1)
            if sum(comb(x, 2) for x in sz) <= 2 * E - T]

def lex_rows(cnf, pool, var, u, w, N):
    pos = [x for x in range(N) if x not in (u, w)]
    prev = None
    for x in pos:
        A = [var(tuple(sorted((u, x))), c) for c in range(k)]
        B = [var(tuple(sorted((w, x))), c) for c in range(k)]
        pre = [] if prev is None else [-prev]
        for c in range(k):
            for c2 in range(c):
                cnf.append(pre + [-A[c], -B[c2]])
        e = pool.id()
        if prev is not None: cnf.append([-e, prev])
        for c in range(k):
            cnf.append([-e, -A[c], B[c]])
            cnf.append(pre + [-A[c], -B[c], e])
        prev = e

def build(N, sizes, E, second=True, lex=True):
    T = turan_min(N); P2 = comb(N, 2)
    edges, var = setup(N)
    pool = IDPool(start_from=len(edges) * k + 1)
    cnf = CNF()
    for e in edges:
        cnf.append([var(e, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                cnf.append([-var(e, c1), -var(e, c2)])
    for c in range(k):
        for S in itertools.combinations(range(N), 6):
            cnf.append([var(e, c) for e in itertools.combinations(S, 2)])      # alpha_c <= 5
            cnf.append([-var(e, c) for e in itertools.combinations(S, 2)])     # omega_c <= 5 (implied)
    part = {}; v = 0
    for i, s in enumerate(sizes):
        for _ in range(s): part[v] = i; v += 1
    within = [e for e in edges if part[e[0]] == part[e[1]]]
    t = E - T
    cnf.extend(CardEnc.equals([var(e, 0) for e in edges], bound=E, vpool=pool, encoding=EncType.seqcounter).clauses)
    if within:
        cnf.extend(CardEnc.atmost([-var(e, 0) for e in within], bound=t, vpool=pool, encoding=EncType.seqcounter).clauses)
    for c in range(1, k):   # colour 0 is the minority
        cnf.extend(CardEnc.atleast([var(e, c) for e in edges], bound=E, vpool=pool, encoding=EncType.seqcounter).clauses)
    if lex:
        v = 0
        for sz in sizes:
            for u in range(v, v + sz - 1):
                lex_rows(cnf, pool, var, u, u + 1, N)
            v += sz
    if second:
        p = [[pool.id() for i in range(5)] for v in range(N)]
        for v in range(N):
            cnf.append(p[v])
            for i in range(5):
                for j in range(i + 1, 5): cnf.append([-p[v][i], -p[v][j]])
        cnf.append([p[0][0]])
        for v in range(1, N):
            for i in range(1, 5):
                cnf.append([-p[v][i]] + [p[u][i - 1] for u in range(v)])
        s = {}; m = {}; cr = {}
        for e in edges:
            u, w = e
            s[e] = pool.id(); m[e] = pool.id(); cr[e] = pool.id()
            same = [pool.id() for i in range(5)]
            for i in range(5):
                cnf.append([-same[i], p[u][i]]); cnf.append([-same[i], p[w][i]]); cnf.append([same[i], -p[u][i], -p[w][i]])
            cnf.append([-s[e]] + same)
            for i in range(5): cnf.append([s[e], -same[i]])
            x = var(e, 1)
            cnf.append([-m[e], s[e]]); cnf.append([-m[e], -x]); cnf.append([m[e], -s[e], x])
            cnf.append([-cr[e], -s[e]]); cnf.append([-cr[e], x]); cnf.append([cr[e], s[e], -x])
        n = len(edges)
        # 2 M_1 + T <= W_1 + X_1   <=>  2*sum m + sum(not s) + sum(not c) <= 2n - T
        pb = PBEnc.leq(lits=[m[e] for e in edges] + [-s[e] for e in edges] + [-cr[e] for e in edges],
                       weights=[2] * n + [1] * n + [1] * n, bound=2 * n - T, vpool=pool)
        cnf.extend(pb.clauses)
        # W_1 <= 2 e(G_1) - T   <=>  sum s + 2*sum(not x1) <= 2n - T
        pb = PBEnc.leq(lits=[s[e] for e in edges] + [-var(e, 1) for e in edges],
                       weights=[1] * n + [2] * n, bound=2 * n - T, vpool=pool)
        cnf.extend(pb.clauses)
        for c in range(2, k):   # e(G_1) <= e(G_c)  <=> sum x1 + sum(not xc) <= n
            pb = PBEnc.leq(lits=[var(e, 1) for e in edges] + [-var(e, c) for e in edges],
                           weights=[1] * (2 * n), bound=n, vpool=pool)
            cnf.extend(pb.clauses)
        cnf.extend(CardEnc.atmost([var(e, 1) for e in edges], bound=(P2 - E) // 4, vpool=pool, encoding=EncType.seqcounter).clauses)
    return cnf, var, edges

def solve(args):
    N, sizes, E, proof = args
    cnf, var, edges = build(N, sizes, E)
    t0 = time.time()
    with Solver(name="cadical195", bootstrap_with=cnf.clauses, with_proof=proof) as sv:
        res = sv.solve()
        model = sv.get_model() if res else None
        pf = sv.get_proof() if (proof and not res) else None
    col = None
    if res:
        mm = set(l for l in model if l > 0)
        col = {f"{e[0]}-{e[1]}": next(c for c in range(k) if var(e, c) in mm) for e in edges}
    if pf is not None:
        tag = f"certs26/N{N}_{'-'.join(map(str,sizes))}_E{E}"
        cnf.to_file(tag + ".cnf")
        with open(tag + ".drat", "w") as f: f.write("\n".join(pf) + "\n")
    return N, sizes, E, res, time.time() - t0, col, cnf.nv, len(cnf.clauses)

if __name__ == "__main__":
    N = int(sys.argv[1]); nproc = int(sys.argv[2]); proof = len(sys.argv) > 3 and sys.argv[3] == "proof"
    os.makedirs("certs26", exist_ok=True)
    cubes = cubes_for(N)
    print(f"N={N} T={turan_min(N)} Emax={comb(N,2)//5}: {len(cubes)} cubes", flush=True)
    t0 = time.time(); nsat = 0
    with Pool(nproc) as P:
        for N_, sizes, E, res, dt, col, nv, nc in P.imap_unordered(solve, [(N, sz, E, proof) for sz, E in cubes]):
            print(f"{time.time()-t0:8.1f}s N={N_} sizes={sizes} E={E} vars={nv} clauses={nc} -> {'SAT' if res else 'UNSAT'} {dt:.1f}s", flush=True)
            if res:
                nsat += 1
                json.dump({"N": N_, "sizes": sizes, "E": E, "colouring": col}, open(f"certs26/SAT_N{N_}_{'-'.join(map(str,sizes))}_E{E}.json", "w"))
    print(f"DONE N={N} SAT cubes: {nsat} / {len(cubes)}  total {time.time()-t0:.0f}s", flush=True)
