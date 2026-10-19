"""As struct26 (Füredi structure for colour 0 = minority, lex within parts) PLUS a free 5-part partition for
colour 1 (:= the minority among colours 1..4) with its own Füredi constraints via pseudo-Boolean encoding:
  2*M_2 + 55 <= W_2 + X_2  (i.e. M_2 <= t_2 = e(G_2) - 55)   and   W_2 <= 2*e(G_2) - 55,
with e(G_2) <= e(G_c) for c=2,3,4 and e(G_2) <= (325-E)/4."""
import itertools, sys, time, json
from math import comb
from multiprocessing import Pool
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.pb import PBEnc
from pysat.solvers import Solver
import struct26 as S
N, k, edges, var = S.N, S.k, S.edges, S.var

def build(sizes, E):
    cnf = S.build(sizes, E, extra=True, lex=True)
    pool = IDPool(start_from=max(abs(l) for cl in cnf.clauses for l in cl) + 1)
    # partition variables for colour 1: p[v][i]
    p = [[pool.id() for i in range(5)] for v in range(N)]
    for v in range(N):
        cnf.append(p[v]); 
        for i in range(5):
            for j in range(i + 1, 5): cnf.append([-p[v][i], -p[v][j]])
    # symmetry: part labels by first occurrence
    cnf.append([p[0][0]])
    for v in range(1, N):
        for i in range(1, 5):
            cnf.append([-p[v][i]] + [p[u][i - 1] for u in range(v)])
    # s_uv <-> same part ; m_uv = s_uv & not x1 ; c_uv = not s_uv & x1
    s = {}; m = {}; cr = {}
    for e in edges:
        u, v = e
        s[e] = pool.id(); m[e] = pool.id(); cr[e] = pool.id()
        same = [pool.id() for i in range(5)]
        for i in range(5):
            cnf.append([-same[i], p[u][i]]); cnf.append([-same[i], p[v][i]]); cnf.append([same[i], -p[u][i], -p[v][i]])
        cnf.append([-s[e]] + same)
        for i in range(5): cnf.append([s[e], -same[i]])
        x = var(e, 1)
        cnf.append([-m[e], s[e]]); cnf.append([-m[e], -x]); cnf.append([m[e], -s[e], x])
        cnf.append([-cr[e], -s[e]]); cnf.append([-cr[e], x]); cnf.append([cr[e], s[e], -x])
    # 2*M + 55 <= W + X  <=>  2*sum m - sum s - sum c <= -55
    lits = [m[e] for e in edges] + [-s[e] for e in edges] + [-cr[e] for e in edges]
    wts = [2] * len(edges) + [1] * len(edges) + [1] * len(edges)
    pb = PBEnc.leq(lits=lits, weights=wts, bound=-55 + 2 * len(edges), top_id=pool.top)
    cnf.extend(pb.clauses); pool.occupy(pool.top + 1, pb.nv)
    # W <= 2 e(G_2) - 55  <=>  sum s - 2 sum x1 <= -55
    lits = [s[e] for e in edges] + [-var(e, 1) for e in edges]
    wts = [1] * len(edges) + [2] * len(edges)
    pb = PBEnc.leq(lits=lits, weights=wts, bound=-55 + 2 * len(edges), top_id=pool.top)
    cnf.extend(pb.clauses); pool.occupy(pool.top + 1, pb.nv)
    # e(G_2) <= e(G_c), c=2,3,4 ; e(G_2) <= (325-E)//4
    for c in range(2, k):
        lits = [var(e, 1) for e in edges] + [-var(e, c) for e in edges]
        pb = PBEnc.leq(lits=lits, weights=[1] * len(edges) + [1] * len(edges), bound=len(edges), top_id=pool.top)
        cnf.extend(pb.clauses); pool.occupy(pool.top + 1, pb.nv)
    cnf.extend(CardEnc.atmost([var(e, 1) for e in edges], bound=(325 - E) // 4, vpool=pool, encoding=EncType.seqcounter).clauses)
    return cnf

def solve(args):
    sizes, E = args
    cnf = build(sizes, E)
    t0 = time.time()
    with Solver(name="cadical195", bootstrap_with=cnf.clauses) as sv:
        res = sv.solve(); model = sv.get_model() if res else None
    return sizes, E, res, time.time() - t0, model, cnf.nv, len(cnf.clauses)

if __name__ == "__main__":
    nproc = int(sys.argv[1]); 
    cubes = [((6,5,5,5,5), 59), ((6,5,5,5,5), 65), ((6,5,5,5,5), 60)]
    t0 = time.time()
    with Pool(nproc) as P:
        for sizes, E, res, dt, model, nv, nc in P.imap_unordered(solve, cubes):
            print(f"{time.time()-t0:8.1f}s sizes={sizes} E={E} vars={nv} clauses={nc} -> {'SAT' if res else 'UNSAT'} {dt:.1f}s", flush=True)
            if res:
                mm = set(l for l in model if l > 0)
                col = {f"{e[0]}-{e[1]}": next(c for c in range(k) if var(e, c) in mm) for e in edges}
                json.dump({"sizes": sizes, "E": E, "colouring": col}, open(f"K26b_SAT_{E}.json", "w"))
    print("DONE", flush=True)
