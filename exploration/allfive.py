"""final.build + Füredi partition structure for ALL colours 1..4 (colour 0 fixed by the cube),
with e_1 <= e_2 <= e_3 <= e_4 as colour symmetry breaking."""
import itertools, sys, time, json
from math import comb
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.pb import PBEnc
from pysat.solvers import Solver
import final
k = 5

def build(N, sizes, E, lex=True):
    T = final.turan_min(N); P2 = comb(N, 2)
    cnf, var, edges = final.build(N, sizes, E, second=False, lex=lex)
    pool = IDPool(start_from=cnf.nv + 1)
    n = len(edges)
    for c in range(1, k):
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
            x = var(e, c)
            cnf.append([-m[e], s[e]]); cnf.append([-m[e], -x]); cnf.append([m[e], -s[e], x])
            cnf.append([-cr[e], -s[e]]); cnf.append([-cr[e], x]); cnf.append([cr[e], s[e], -x])
        pb = PBEnc.leq(lits=[m[e] for e in edges] + [-s[e] for e in edges] + [-cr[e] for e in edges],
                       weights=[2] * n + [1] * n + [1] * n, bound=2 * n - T, vpool=pool)
        cnf.extend(pb.clauses)
        pb = PBEnc.leq(lits=[s[e] for e in edges] + [-var(e, c) for e in edges],
                       weights=[1] * n + [2] * n, bound=2 * n - T, vpool=pool)
        cnf.extend(pb.clauses)
    for c in range(1, k - 1):   # e_c <= e_{c+1}
        pb = PBEnc.leq(lits=[var(e, c) for e in edges] + [-var(e, c + 1) for e in edges],
                       weights=[1] * (2 * n), bound=n, vpool=pool)
        cnf.extend(pb.clauses)
    cnf.extend(CardEnc.atmost([var(e, 1) for e in edges], bound=(P2 - E) // 4, vpool=pool, encoding=EncType.seqcounter).clauses)
    return cnf, var, edges

if __name__ == "__main__":
    N = int(sys.argv[1]); sizes = tuple(int(x) for x in sys.argv[2].split(",")); E = int(sys.argv[3])
    cnf, var, edges = build(N, sizes, E)
    t = time.time()
    with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
        r = s.solve()
        if r:
            m = set(l for l in s.get_model() if l > 0)
            col = {f"{e[0]}-{e[1]}": next(c for c in range(k) if var(e, c) in m) for e in edges}
            json.dump({"N": N, "sizes": sizes, "E": E, "colouring": col}, open(f"allfive_SAT_N{N}_E{E}.json", "w"))
    print(f"allfive N={N} sizes={sizes} E={E}: {'SAT' if r else 'UNSAT'} {time.time()-t:.1f}s nv={cnf.nv} nc={len(cnf.clauses)}", flush=True)
