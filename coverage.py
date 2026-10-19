"""Independent re-derivation of the case split for Lemma A (K_21, alpha_0<=4, alpha_c<=5), and check that the
cube lists used by k21.py (low regime) and k21c.py (high regime) are exactly the derived ones."""
from math import comb
import itertools, k21, k21c
P2 = comb(21, 2)                                   # 210 pairs
# Turán minima: min #edges of a graph on 21 vertices with alpha <= 4 (4 near-equal parts) and alpha <= 5 (5 parts)
def tmin(n, r):
    q, s = divmod(n, r); return s * comb(q + 1, 2) + (r - s) * comb(q, 2)
T0, T1 = tmin(21, 4), tmin(21, 5)
assert (T0, T1) == (45, 34)
# e_1 := min(e_1..e_4) ranges over [T1, floor((P2 - T0)/4)] = [34, 41]
E_range = range(T1, (P2 - T0) // 4 + 1)
assert list(E_range) == list(range(34, 42))
# LOW regime (e_1 <= 39): Füredi on colour 1: parts n_1..n_5 (sum 21) with sum C(n_i,2) <= 2E - T1
low = set()
for E in E_range:
    if E > 39: continue
    for p in itertools.combinations_with_replacement(range(22), 5):
        if sum(p) == 21 and sum(comb(x, 2) for x in p) <= 2 * E - T1:
            low.add((tuple(sorted(p, reverse=True)), E))
used_low = {c for c in k21.cubes() if c[1] <= 39}
assert used_low == low, (len(used_low), len(low))
# HIGH regime (e_1 >= 40): e_0 <= P2 - 4*40 = 50; Füredi on colour 0: 4 parts with sum C(n_i,2) <= T0 + 2(e_0 - T0)
high = set()
for e0 in range(T0, P2 - 4 * 40 + 1):
    for p in itertools.combinations_with_replacement(range(22), 4):
        if sum(p) == 21 and sum(comb(x, 2) for x in p) <= T0 + 2 * (e0 - T0):
            high.add((tuple(sorted(p, reverse=True)), e0))
used_high = set(k21c.cubes(40))
assert used_high == high, (len(used_high), len(high))
print(f"coverage OK: low regime {len(low)} cubes (e_1 in 34..39), high regime {len(high)} cubes (e_1 >= 40, e_0 in 45..50)")
