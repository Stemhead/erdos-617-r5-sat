"""Upper-bound recursion for N(a) = max n such that K_n has a 5-colouring with alpha_c <= a_c.
Recursion (vertex-degree count): for any vertex v, colour c: n-1-d_c(v) <= N(a - e_c).
Sum over c: 4(n-1) <= sum_c N(a-e_c)  =>  n <= 1 + floor(sum/4).
Parity: if equality would force all colour classes regular of degree n-1-N(a-e_c) and n*deg odd, n is impossible.
Base: a_c = 0 => n = 0 (no vertices allowed? alpha<=0 means empty) ; a_c = 1 => all edges colour c => n <= min other a."""
from functools import lru_cache
from math import comb
import itertools, sys

k = 5
@lru_cache(None)
def U(a):
    a = tuple(sorted(a))
    if a[0] == 0: return 0
    if a[0] == 1:
        return min(a[1:]) if a.count(1) == 1 else 1
    # trivial size bound: an s-set has C(s,2) edges; colours with a_c < s must all appear
    bound = 10**9
    for s in range(2, 60):
        if sum(1 for x in a if x < s) > comb(s, 2):
            bound = min(bound, s - 1); break
    # recursion
    subs = [U(tuple(a[j] - (1 if j == c else 0) for j in range(k))) for c in range(k)]
    tot = sum(subs)
    n = 1 + tot // 4
    # parity refinement at n: if 4(n-1) == tot then every class c is regular of degree n-1-subs[c]
    if 4 * (n - 1) == tot:
        if any((n * (n - 1 - subs[c])) % 2 == 1 for c in range(k)):
            n -= 1
    return min(n, bound)

if __name__ == "__main__":
    for a in [(3,3,3), (4,4,4,4)]:
        pass
    print("U(5,5,5,5,5) =", U((5,5,5,5,5)))
    for a in [(4,5,5,5,5),(3,5,5,5,5),(4,4,5,5,5),(3,4,5,5,5),(2,5,5,5,5),(4,4,4,5,5),(3,3,5,5,5),(2,4,5,5,5)]:
        print(a, U(a))
