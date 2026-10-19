# Erdős problem #617, case r = 5 — working notes (2026-10-17)

## Problem
Erdős–Gyárfás (1999), Conjecture 1: if the edges of K_{r^2+1} are r-coloured (r ≥ 3) then some r+1 vertices
miss at least one colour. Proved by them for r = 3, 4; r = 5 (K_26, 5 colours, every 6-set must see all 5
colours) is open per the erdosproblems.com forum (July 2026). Affine plane AG(2,5) gives a 5-colouring of K_25 in
which every 6-set sees all colours (4 parallel classes + the union of the remaining two), so 26 is the boundary.

Equivalent form: a colouring is "good" iff every colour class G_c has independence number α(G_c) ≤ 5
(a 6-set with no c-edge is exactly an independent 6-set of G_c).

## Generalised quantity
For a = (a_1,…,a_5) let N(a) = max n such that K_n has a 5-edge-colouring with α(G_c) ≤ a_c for all c.
(Complementary Ramsey number of Chung–Liu / Munemasa–Shinohara: N(a) = R̄(a+1) − 1.)  Target: N(5,5,5,5,5) = 25.

## Reduction (vertex deletion)
Fix a good colouring on n vertices, a vertex v and a colour c. Let W = V ∖ N_c[v] (non-c-neighbours of v).
Any c-independent set inside W extends by v, so α_c(W) ≤ a_c − 1 while the other bounds persist. Hence
    n − 1 − d_c(v) ≤ N(a − e_c)   for every v, c.                                      (1)
Summing (1) over c (Σ_c d_c(v) = n − 1):  4(n − 1) ≤ Σ_c N(a − e_c).                   (2)
Refinements when (2) is tight (every d_c(v) forced to D_c := n − 1 − N(a − e_c), so every class is D_c-regular):
  * parity: n·D_c must be even;
  * Brooks: if D_c ≥ 3 and a K_{D_c+1} component is impossible (it would be a monochromatic clique, i.e. an
    independent (D_c+1)-set in every other colour, so impossible when D_c+1 > a_{c'} for some c' ≠ c), then
    χ(G_c) ≤ D_c and α(G_c) ≥ ⌈n/D_c⌉, which must be ≤ a_c; otherwise the greedy bound α ≥ ⌈n/(D_c+1)⌉.
Trivial bound: an s-set has C(s,2) edges, and every colour c with a_c < s must appear in it, so
    #{c : a_c < s} > C(s,2)  ⇒  n ≤ s − 1.
Base: a_c = 0 ⇒ n = 0;  a_c = 1 ⇒ every edge has colour c ⇒ n ≤ min_{c'≠c} a_{c'} (and n ≤ 1 if two a's equal 1).
Monotonicity: a good colouring of K_n induces one on K_{n-1}, so impossibility propagates upward.

## Computation (bottom-up, exact)
For each a in increasing order of Σa: lower bound from the largest induced sub-colouring of the affine K_25
(SAT, maximising |W|), then SAT at n = L+1, L+2, … with (1) as explicit degree constraints
d_c(v) ≥ n − 1 − N(a − e_c) (exact lower-level values), plus the star at vertex 0 sorted by colour
(valid by relabelling). First UNSAT (or a counting/parity/Brooks kill) fixes N(a).
Verification pass (verify.py): colourings rechecked with networkx; UNSAT instances re-solved with DRAT proof
logging and checked by drat-trim.

## The reduction actually used (2026-10-17, afternoon)
Direct SAT on K_26 (even with Füredi structure on the two smallest colour classes and lex symmetry breaking)
stalls on cubes with slack t >= 5.  The decisive route is the vertex-deletion lemma at the top level only:

**Lemma A.**  If no 5-colouring of K_21 has alpha_1 <= 4 and alpha_c <= 5 for c = 2..5 (i.e. R̄(5,6,6,6,6) <= 21),
then every 5-colouring of K_26 has a 6-set missing a colour.
Proof. Suppose K_26 is coloured with every colour class of independence number <= 5. For a vertex v and colour c,
W = V \ N_c[v] induces a colouring with alpha_c(W) <= 4 (any c-independent set in W extends by v), so
|W| = 25 - d_c(v) <= 20, i.e. d_c(v) >= 5 for all v, c. Since sum_c d_c(v) = 25, every d_c(v) = 5: each colour
class is 5-regular. A 5-regular graph has, by Brooks' theorem applied to each component, chi <= 5 unless some
component is K_6; a monochromatic K_6 is a 6-set missing four colours, and chi <= 5 gives an independent set of
size >= ceil(26/5) = 6 in that colour. Contradiction either way.  □

**Computation for Lemma A** (k21.py): colouring of K_21, colour 0 with alpha <= 4, colours 1..4 with alpha <= 5.
* Redundant facts: a K_5 in colour c >= 1 is a colour-0-independent 5-set, so omega_c <= 4 (c >= 1); omega_0 <= 5.
* Colour 1 := the minority among colours 1..4, so e_1 <= e_c (c = 2,3,4) and e_1 <= (210 - e_0)/4;
  since e_0 >= 45 (Turán: alpha_0 <= 4 on 21 vertices), e_1 <= 41.  T = 34 = min edges with alpha <= 5 on 21
  vertices (parts 5,4,4,4,4).  t_1 = e_1 - 34 in [0, 7].
* Füredi (JCTB 2015, Thm 2): the complement of G_1 is K_6-free with ex(21,K_6) - t_1 = 176 - t_1 edges, so it
  has a 5-partite subgraph missing at most t_1 of its edges.  Relabel vertices so the parts are consecutive
  blocks with sizes n_1 >= ... >= n_5 (sum 21).  Then M_1 (within-part pairs not of colour 1) <= t_1 and
  W_1 = sum C(n_i,2) <= 2 e_1 - 34.  Cube = (size vector, e_1): 145 cubes.
* Within each part, consecutive vertices u,u+1 satisfy row(u) <=_lex row(u+1) (entries at columns u,u+1 removed,
  colours ordered 0<1<2<3<4).  Sound: take the lex-least colouring matrix in the orbit under part-preserving
  permutations; a violated pair would be fixed by the transposition (u u+1), giving a smaller matrix.
Each cube is a CaDiCaL run; UNSAT cubes get DRAT proofs checked by drat-trim (k21_cert.py).

### Two regimes for Lemma A (K_21), by e_1 := min(e_1,...,e_4)
Let e_0 = #colour-0 edges (alpha_0 <= 4 ⇒ e_0 >= 45, Turán), e_c for c>=1 (alpha_c <= 5 ⇒ e_c >= 34), sum = 210.
* LOW regime e_1 <= 39: colour-1 Füredi blocks (t_1 = e_1 - 34 <= 5), cubes (sizes, e_1) — k21.py.
* HIGH regime e_1 >= 40: then e_0 <= 210 - 4·40 = 50, t_0 = e_0 - 45 <= 5, so colour 0 is Füredi-structured:
  complement K_5-free with ex(21,K_5) - t_0 = 165 - t_0 edges ⇒ a 4-partite subgraph missing <= t_0 edges;
  cube = (4 part sizes as consecutive blocks, e_0), M_0 <= t_0, W_0 <= 45 + 2 t_0 — k21c.py (47 cubes).
  The same cubes with e_1 >= 41 (e_0 <= 46, t_0 <= 1) are refuted in < 1 s each, matching the hand argument:

**Lemma B (no K_6 minus an edge).** In any edge-colouring of K_n (n >= 7) with 5 colours in which every 6-set sees
all 5 colours, no colour class contains K_6 − e.  Proof: let A be a 6-set all of whose pairs have colour c except
xy of colour c*. For w ∉ A and a ∈ A consider the 6-set (A∖{a}) ∪ {w}. Its pairs inside A∖{a} have colour c, plus
c* iff a ∉ {x,y}. So for each colour c' ∉ {c, c*}, c' must occur on w's edges to A∖{a} for every a, hence at >= 2
vertices of A; and c* must occur on w's edges to A∖{x}, hence >= 1 time. That is >= 2+2+2+1 = 7 occurrences on
w's 6 edges to A — impossible.  □   (In the K_21 problem every 6-set sees all colours too, since alpha_0 <= 4.)
Consequence for e_1 >= 41: e_0 <= 46, t_0 <= 1, the only admissible colour-0 shape is (6,5,5,5) with exactly one
missing pair in the 6-part, i.e. a K_6 − e in colour 0 — contradiction with Lemma B.
