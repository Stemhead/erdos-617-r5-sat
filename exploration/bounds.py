"""N(a) = max n such that K_n has a 5-colouring with alpha_c <= a_c for all c (a sorted, entries 0..5).
Lower bounds L(a): largest induced sub-colouring of the affine-plane K_25 colouring (via SAT, maximise |W|).
Upper bounds U(a): degree-count recursion with parity and Brooks refinements, using U at lower levels.
Prints the table and the gaps."""
import itertools, sys, json
from functools import lru_cache
from math import comb, ceil
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

k = 5
q = 5
pts = [(x, y) for x in range(q) for y in range(q)]
def cls(m):
    if m == 'v': return lambda p: p[0]
    return lambda p: (p[1] - m * p[0]) % q
classes = [cls(m) for m in list(range(q)) + ['v']]
def colour(p, r):
    for c in range(4):
        if classes[c](p) == classes[c](r): return c
    return 4
P = len(pts)
col = {}
for i, j in itertools.combinations(range(P), 2):
    col[(i, j)] = colour(pts[i], pts[j])
# independent sets per colour of each size up to 6 (as frozensets), computed by brute force
indep = {c: {s: [] for s in range(1, 7)} for c in range(k)}
for s in range(1, 7):
    for S in itertools.combinations(range(P), s):
        for c in range(k):
            if all(col[(i, j)] != c for i, j in itertools.combinations(S, 2)):
                indep[c][s].append(S)

def L_affine(a, perm_colours=True):
    """max |W| subset of affine points with alpha_c(W) <= a[c]; try all assignments of the 5 affine
    colours to the vector positions (since the affine classes are not symmetric: one is the double class)."""
    best = 0
    perms = set(itertools.permutations(range(k))) if perm_colours else [tuple(range(k))]
    seen = set()
    for perm in perms:
        key = tuple(a[perm[c]] for c in range(k))  # a-value assigned to affine colour c
        if key in seen: continue
        seen.add(key)
        if 0 in key: continue
        cnf = CNF(); pool = IDPool(start_from=P + 1)
        for c in range(k):
            s = key[c] + 1
            if s > 6: continue
            for S in indep[c][s]:
                cnf.append([-(i + 1) for i in S])
        lo = best
        # maximise via increasing cardinality
        while True:
            cnf2 = CNF(from_clauses=cnf.clauses)
            if lo + 1 > P: break
            cnf2.extend(CardEnc.atleast([i + 1 for i in range(P)], bound=lo + 1, vpool=pool, encoding=EncType.seqcounter).clauses)
            with Solver(name="cadical195", bootstrap_with=cnf2.clauses) as s:
                if s.solve(): lo += 1
                else: break
        best = max(best, lo)
    return best

@lru_cache(None)
def L(a):
    a = tuple(sorted(a))
    if a[0] == 0: return 0
    return L_affine(a)

@lru_cache(None)
def U(a):
    a = tuple(sorted(a))
    if a[0] == 0: return 0
    if a[0] == 1:
        return min(a[1:]) if a.count(1) == 1 else 1
    bound = 10**9
    for s in range(2, 60):
        if sum(1 for x in a if x < s) > comb(s, 2):
            bound = min(bound, s - 1); break
    subs = [U(tuple(a[j] - (1 if j == c else 0) for j in range(k))) for c in range(k)]
    tot = sum(subs)
    n = min(1 + tot // 4, bound)
    # refine: at candidate n, every vertex has d_c >= n-1-subs[c]; if forced equality, each class regular
    while n > 0:
        mins = [n - 1 - subs[c] for c in range(k)]
        if sum(mins) > n - 1: n -= 1; continue
        if sum(mins) == n - 1:
            # all classes regular with degree Delta_c = mins[c]
            bad = False
            for c in range(k):
                D = mins[c]
                if (n * D) % 2 == 1: bad = True; break
                # clique component K_{D+1} in colour c allowed only if D+1 <= a_{c'} for all c' != c
                clique_ok = all(D + 1 <= a[cc] for cc in range(k) if cc != c)
                if D >= 3 and not clique_ok:
                    if ceil(n / D) > a[c]: bad = True; break       # Brooks: chi <= D
                else:
                    if ceil(n / (D + 1)) > a[c]: bad = True; break  # greedy: chi <= D+1
            if bad: n -= 1; continue
        break
    return n

if __name__ == "__main__":
    vecs = sorted({tuple(sorted(v)) for v in itertools.product(range(1, 6), repeat=k)}, key=lambda v: (sum(v), v))
    rows = []
    for a in vecs:
        if a[0] <= 1: continue
        l, u = L(a), U(a)
        rows.append((a, l, u))
        print(a, "L=", l, "U=", u, "GAP" if u > l else "", flush=True)
    json.dump([(list(a), l, u) for a, l, u in rows], open("bounds.json", "w"))
