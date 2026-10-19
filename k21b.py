"""K_N, a = (4,5,5,5,5): colour 0 alpha<=4, colours 1..4 alpha<=5.  Parametrised in N.
Structure: colour 1 = minority among 1..4 with Füredi 5-partition as consecutive blocks (cube = sizes, E=e_1);
PLUS colour 0's Füredi 4-partition (complement K_5-free) as free partition variables with
   2 M_0 + T4 <= W_0 + X_0    and    W_0 <= 2 e_0 - T4,   e_0 <= P2 - 4E.
Lex symmetry breaking within colour-1 parts (optional)."""
import itertools, sys, time, json
from math import comb
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.pb import PBEnc
from pysat.solvers import Solver
from final import lex_rows
k = 5
def T5(N):
    q, r = divmod(N, 5); return r * comb(q + 1, 2) + (5 - r) * comb(q, 2)
def T4(N):
    q, r = divmod(N, 4); return r * comb(q + 1, 2) + (4 - r) * comb(q, 2)

def build(N, sizes, E, lex=True, colour0=True):
    P2 = comb(N, 2); T = T5(N); T0 = T4(N)
    edges = list(itertools.combinations(range(N), 2))
    eid = {e: i for i, e in enumerate(edges)}
    var = lambda e, c: eid[e] * k + c + 1
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
    t = E - T
    cnf.extend(CardEnc.equals([var(e, 1) for e in edges], bound=E, vpool=pool, encoding=EncType.seqcounter).clauses)
    if within:
        cnf.extend(CardEnc.atmost([-var(e, 1) for e in within], bound=t, vpool=pool, encoding=EncType.seqcounter).clauses)
    for c in range(2, k):
        cnf.extend(CardEnc.atleast([var(e, c) for e in edges], bound=E, vpool=pool, encoding=EncType.seqcounter).clauses)
    cnf.extend(CardEnc.atmost([var(e, 0) for e in edges], bound=P2 - 4 * E, vpool=pool, encoding=EncType.seqcounter).clauses)
    if lex:
        v = 0
        for sz in sizes:
            for u in range(v, v + sz - 1):
                lex_rows(cnf, pool, var, u, u + 1, N)
            v += sz
    if colour0:
        n = len(edges)
        p = [[pool.id() for i in range(4)] for v in range(N)]
        for v in range(N):
            cnf.append(p[v])
            for i in range(4):
                for j in range(i + 1, 4): cnf.append([-p[v][i], -p[v][j]])
        cnf.append([p[0][0]])
        for v in range(1, N):
            for i in range(1, 4):
                cnf.append([-p[v][i]] + [p[u][i - 1] for u in range(v)])
        s = {}; m = {}; cr = {}
        for e in edges:
            u, w = e
            s[e] = pool.id(); m[e] = pool.id(); cr[e] = pool.id()
            same = [pool.id() for i in range(4)]
            for i in range(4):
                cnf.append([-same[i], p[u][i]]); cnf.append([-same[i], p[w][i]]); cnf.append([same[i], -p[u][i], -p[w][i]])
            cnf.append([-s[e]] + same)
            for i in range(4): cnf.append([s[e], -same[i]])
            x = var(e, 0)
            cnf.append([-m[e], s[e]]); cnf.append([-m[e], -x]); cnf.append([m[e], -s[e], x])
            cnf.append([-cr[e], -s[e]]); cnf.append([-cr[e], x]); cnf.append([cr[e], s[e], -x])
        pb = PBEnc.leq(lits=[m[e] for e in edges] + [-s[e] for e in edges] + [-cr[e] for e in edges],
                       weights=[2] * n + [1] * n + [1] * n, bound=2 * n - T0, vpool=pool)
        cnf.extend(pb.clauses)
        pb = PBEnc.leq(lits=[s[e] for e in edges] + [-var(e, 0) for e in edges],
                       weights=[1] * n + [2] * n, bound=2 * n - T0, vpool=pool)
        cnf.extend(pb.clauses)
    return cnf, var, edges

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "validate":
        # affine K_20 sub-colouring with alpha_0 <= 4; relabel so colour-1 parts are consecutive blocks
        q = 5
        pts = [(x, y) for x in range(q) for y in range(q)]
        def cls(mm):
            if mm == 'v': return lambda p: p[0]
            return lambda p: (p[1] - mm * p[0]) % q
        classes = [cls(mm) for mm in list(range(q)) + ['v']]
        def colour(p, r):
            for c in range(4):
                if classes[c](p) == classes[c](r): return c
            return 4
        x0 = (0, 0)
        W = [p for p in pts if p != x0 and colour(p, x0) != 0]
        # colour 1's parts = lines of class 1 restricted to W; order W by class-1 line
        W.sort(key=lambda p: classes[1](p))
        sizes = tuple(sorted([sum(1 for p in W if classes[1](p) == l) for l in range(q)], reverse=True))
        idx = {p: i for i, p in enumerate(W)}
        N = len(W)
        col = {(idx[p], idx[r]): colour(p, r) for p, r in itertools.combinations(W, 2)}
        col = {tuple(sorted(e)): c for e, c in col.items()}
        E = sum(1 for c in col.values() if c == 1)
        print("validate: N", N, "sizes", sizes, "E", E, "e_0", sum(1 for c in col.values() if c == 0))
        for lex in (False, True):
            cnf, var, edges = build(N, sizes, E, lex=lex, colour0=True)
            assum = [var(e, col[e]) for e in edges]
            with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
                r = s.solve(assumptions=assum)
            print(f"  lex={lex}: affine K_{N} colouring admitted: {'SAT' if r else 'UNSAT'}", flush=True)
    else:
        N = int(sys.argv[2]); sizes = tuple(int(x) for x in sys.argv[3].split(",")); E = int(sys.argv[4])
        cnf, var, edges = build(N, sizes, E)
        t0 = time.time()
        with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
            r = s.solve()
        print(f"k21b N={N} sizes={sizes} E={E}: {'SAT' if r else 'UNSAT'} {time.time()-t0:.1f}s nv={cnf.nv} nc={len(cnf.clauses)}", flush=True)
