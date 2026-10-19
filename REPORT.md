# Erdős Problem #617, the case r = 5: every 5-colouring of the edges of K_26 has six vertices missing a colour

*Computer-assisted proof, 2026-10-17 to 2026-10-19. Status: all 117 cases refuted; 116 with drat-trim-verified certificates, the last case solved without a checked certificate (§5, §6). See §5 for the final state of the computation and §8 for its relation to prior claims. This is an independent confirmation by a different method, not a first proof: five AI-assisted proofs of the same statement were posted in July 2026 (§8), none yet refereed.*

## 1. Statement

**Conjecture (Erdős–Gyárfás 1999, Conj. 1; erdosproblems.com #617).** For r ≥ 3, if the edges of K_{r²+1} are
coloured with r colours then some r+1 vertices span a K_{r+1} with at least one colour missing.
Erdős and Gyárfás proved r = 3, 4 (r = 3 is also Chung–Liu 1978). The case r = 5 (K_26, 5 colours, 6-sets) was
described as open in a forum comment of 15 July 2026; proof claims for it appeared from 18 July 2026 onward (§8).
The work here was started on 17 October 2026 without knowledge of those claims. The affine plane AG(2,5) gives a 5-colouring of K_25 in which every 6-set
sees all five colours (four parallel classes + the union of the other two; verified by computer), so 26 is sharp.

**Theorem.** Every 5-colouring of E(K_26) contains a 6-set on which at most four colours appear.
Equivalently, in the notation of Chung–Liu / Munemasa–Shinohara, R̄(6,6,6,6,6) = 26.

Reformulation used throughout: a colouring is *good* iff every 6-set sees all five colours iff every colour class
G_c has independence number α(G_c) ≤ 5 (a 6-set with no c-edge is a c-independent 6-set). A good colouring also has
ω(G_c) ≤ 5 for every c (a monochromatic K_6 misses the other four colours).

## 2. Reduction to K_21 (Lemma A)

**Lemma A.** Suppose no 5-colouring of E(K_21) satisfies α(G_1) ≤ 4 and α(G_c) ≤ 5 for c = 2,…,5. Then the Theorem holds.

*Proof.* Let K_26 be good. Fix a vertex v and a colour c and let W = V ∖ N_c[v] (the vertices not joined to v in
colour c). Any c-independent set inside W extends by v, so the induced colouring on W has α_c ≤ 4 and α_{c'} ≤ 5
for c' ≠ c. By hypothesis |W| ≤ 20, i.e. d_c(v) ≥ 5. As Σ_c d_c(v) = 25, every d_c(v) = 5: each colour class is
5-regular. By Brooks' theorem each component of G_c has chromatic number ≤ 5 unless it is K_6; a K_6 component is a
monochromatic K_6 (impossible in a good colouring), and χ(G_c) ≤ 5 gives a c-independent set of size ⌈26/5⌉ = 6,
contradicting α(G_c) ≤ 5. ∎

So everything rests on the K_21 statement, which is settled by computer (§4–5).

## 3. Structure used in the K_21 computation

Notation: colour 0 is the colour with α ≤ 4; colours 1–4 have α ≤ 5; e_c = |E(G_c)|, Σ e_c = 210.
Every 6-set sees all five colours (α_0 ≤ 4 forces a colour-0 edge in every 5-set, hence in every 6-set).

(a) *Turán.* A graph on 21 vertices with α ≤ 4 has ≥ 45 edges (complement of the Turán graph T(21,4), parts
6,5,5,5); with α ≤ 5 it has ≥ 34 edges (T(21,5), parts 5,4,4,4,4). So e_0 ≥ 45, e_c ≥ 34.

(b) *Redundant clique bounds.* A K_5 in colour c ≥ 1 is a colour-0-independent 5-set, so ω(G_c) ≤ 4 for c ≥ 1;
a K_6 in colour 0 is colour-1-independent, so ω(G_0) ≤ 5.

(c) *Füredi's stability theorem* (Z. Füredi, "A proof of the stability of extremal graphs, Simonovits' stability
from Szemerédi's regularity", JCTB 115 (2015) 66–71, Theorem 2): if G is K_{p+1}-free on n vertices with
e(G) = e(T(n,p)) − t edges, then G has a p-partite subgraph with ≥ e(G) − t edges, i.e. G becomes p-partite after
deleting ≤ t edges.
  * Colour 1 (α ≤ 5): its complement is K_6-free with 176 − t_1 edges, t_1 := e_1 − 34. Hence there is a
    5-partition (parts n_1 ≥ … ≥ n_5) such that at most t_1 within-part pairs are *not* of colour 1 (M_1 ≤ t_1),
    and Σ C(n_i,2) ≤ e_1 + t_1 = 2e_1 − 34.
  * Colour 0 (α ≤ 4): its complement is K_5-free with 165 − t_0 edges, t_0 := e_0 − 45. Hence a 4-partition
    with M_0 ≤ t_0 and Σ C(n_i,2) ≤ 2e_0 − 45.

(d) *Choice of the minority colour.* Let e_1 = min(e_1,…,e_4) (relabel colours 1–4). Then e_1 ≤ (210 − e_0)/4 ≤ 41.
  * **Low regime** e_1 ≤ 39: t_1 ≤ 5. Relabel vertices so the colour-1 parts are consecutive blocks.
    Cube = (part sizes, e_1); 70 cubes.
  * **High regime** e_1 ≥ 40: e_0 ≤ 210 − 4·40 = 50, so t_0 ≤ 5. Relabel so the colour-0 parts are consecutive
    blocks. Cube = (part sizes, e_0); 47 cubes.
  (A separate script, coverage.py, re-derives both cube lists from these inequalities and checks they coincide
  with the lists actually solved.)

(e) *Symmetry breaking.* Within each block, consecutive vertices u, u+1 satisfy row(u) ≤_lex row(u+1), where
rows are the colour vectors to the other vertices in increasing order (entries at columns u, u+1 removed),
colours ordered 0 < 1 < 2 < 3 < 4. Soundness: among all relabellings by block-preserving permutations, take the
one whose colour matrix (read row by row) is lexicographically least; if some adjacent pair violated the
constraint, the transposition (u u+1) would produce a smaller matrix (a direct check of the three cases
first-difference-column < u, = u+1 side, > u+1). All other constraints in a cube are invariant under
block-preserving permutations. (This is the "adjacent-rows" lex-leader of Codish, Miller, Prosser, Stuckey.)
Empirical check: the affine K_20 sub-colouring, after the swap normalisation from the proof, is admitted by the
encoding with lex on (lexcheck.py), and without lex by the full encoding (k21b.py validate).

(f) *Hand-checkable corner.* For e_1 = 41 one gets e_0 = 46 and the colour-0 shape must be (6,5,5,5) with exactly
one missing pair in the 6-part, i.e. colour 0 contains K_6 − e. **Lemma B:** in a good colouring (n ≥ 7) no colour
class contains K_6 − e. (Let A be the 6-set, xy its non-c pair of colour c*. For w ∉ A and each a ∈ A the 6-set
(A∖{a}) ∪ {w} must see all colours; inside A∖{a} only c and — iff a ∉ {x,y} — c* occur. So each colour other than
c, c* occurs on w's edges to A at ≥ 2 vertices, and c* at ≥ 1 vertex of A∖{x}: ≥ 7 occurrences on 6 edges.)
The solver refutes all four e_1 = 41 cubes in < 1 s, consistent with this.

## 4. Encoding (k21.py low regime, k21c.py high regime)

Variables x_{e,c} (pair e, colour c), exactly one colour per pair. Clauses: every 5-set has a colour-0 pair;
every 6-set has a pair of each colour 1–4; the clique bounds (b); cardinalities (sequential counters): e_1 = E or
e_0 = e_0 as the cube says, e_c ≥ e_1 (c = 2,3,4), e_0 ≤ 210 − 4e_1 (low) / e_1 ≥ 40 (high, with e_1 ≤ e_c via
pseudo-Boolean constraints), at most t within-block pairs not of the block colour; lex constraints (e).
Solver: CaDiCaL 1.9.5 through python-sat 1.9; cubes run in parallel on an Apple M5 (10 cores).

## 5. Results

| regime | cubes | result | max time per cube |
|---|---|---|---|
| high (e_1 ≥ 40), colour-0 blocks | 47 | all UNSAT, all 47 DRAT-verified | 143 s |
| low (e_1 ≤ 39), colour-1 blocks, e_1 ≤ 38 | 44 | all UNSAT, all DRAT-verified | 58 min ((5,4,4,4,4), e_1=38) |
| low, e_1 = 39, 24 cubes other than the two below | 24 | all UNSAT, all DRAT-verified | 29 min |
| low, (5,5,4,4,3), e_1 = 39 | 1 | UNSAT (CaDiCaL 1.9: 4 h 27 min; CaDiCaL 3.0.1: ~2.5 h); 11.6 GB binary DRAT proof, drat-trim VERIFIED in 4 h 04 min (76.5 M lemmas, 27.7 M in core) | |
| low, (5,4,4,4,4), e_1 = 39 | 1 | UNSAT (CaDiCaL 1.9.5, finished 2026-10-19 02:14 CDT: ≈25 h CPU, ≈28 h wall excluding an 8.7 h suspension); DRAT certificate: see §6 | |

### 5a. State of the two auxiliary runs when the session was stopped (2026-10-19 04:15 CDT)

* CaDiCaL 3.0.1 with proof streaming on (5,4,4,4,4) e_1 = 39: still running after 22 h 10 min CPU; the partial
  binary DRAT file had reached 65.7 GB. Stopped and the partial proof deleted, since an unfinished proof certifies
  nothing. (For scale: the same solver refuted the sibling cube (5,5,4,4,3) in ≈2.5 h with an 11.6 GB proof,
  so this cube is at least an order of magnitude harder, consistent with the 25 h CaDiCaL 1.9 run.)
* Alternative decomposition of the e_1 = 39 slice (k21c39.py, 150 cubes): 147 UNSAT; the three unfinished cubes
  are colour-0 block sizes (6,5,5,5) with e_0 = 53 and e_0 = 54, and (6,6,5,4) with e_0 = 54, each stopped after
  ≈10 h CPU. This run is not part of the proof; it was a second, differently-structured attack on the same slice.

Totals: 117/117 cubes UNSAT; 116 certificates checked by drat-trim; wall time of the whole project from first
encoding to last verdict ≈ 33 h (2026-10-17 17:00 to 2026-10-19 02:14), of which the single cube (5,4,4,4,4)
e_1 = 39 accounts for 25 h of solver CPU.

## 6. Certification

Every cube is re-solved with DRAT proof logging; the DIMACS file and the proof are checked with drat-trim
(Heule). Results in certs21/results.json (k21_cert_all.py; 115 cubes) and certs21b/results_b.json ((5,5,4,4,3)
e_1=39, standalone CaDiCaL 3.0.1 with a streamed binary proof, 11.6 GB, verified).

Status of the 117th cube, (5,4,4,4,4) e_1 = 39: refuted by CaDiCaL 1.9.5 (no proof logging). A second run with
CaDiCaL 3.0.1 and proof streaming was started in parallel; its state at the end of the session is recorded in
§5a below. Checking a proof of that size with drat-trim takes on the order of a day (the 11.6 GB proof took 4 h),
which did not fit in the session. So the theorem rests on 116 machine-checked certificates plus one solver
verdict, and that one cube is the natural target for anyone who wants to complete the certification: re-run
`k21.py` on sizes (5,4,4,4,4), E = 39 with proof logging and check the result with drat-trim.

An independent second refutation of the whole e_1 = 39 slice (`k21c39.py`: colour-0 blocks with e_1 ≤ 39,
150 cubes) was also run; its state at the end of the session is in §5a. The remaining trust base: Füredi's theorem, Brooks'
theorem, Turán's theorem, the lex-leader soundness argument, the Python encoder (k21.py / k21c.py / final.lex_rows)
and drat-trim.

## 7. Files
See README.md for the repository layout. Core: k21.py, k21c.py, final.py (lex_rows), coverage.py, k21_cert_all.py,
lexcheck.py, k21b.py, affine.py (AG(2,5) construction and check), k21c39.py; logs in logs/ (k21_full.log,
k21_low.log, k21c_40.log, k21c_41.log, k21_cert.log, k21c39.log); verification results and CNF hashes in certs/;
the 117 CNF files in the release asset erdos617-r5-cnf.tar.xz.

## 8. Relation to prior claims (added 2026-10-18)

The erdosproblems.com proof-claims thread for #617 (https://www.erdosproblems.com/forum/thread/617/proof-claims)
lists five claims for exactly this r = 5 statement, all from July 2026, all AI-assisted, and all self-described as
not refereed by an independent human expert:

| date | claimant | route |
|---|---|---|
| 2026-07-18 | R. Sneiderman (GPT-5.6) | hand proof: Kang–Pikhurko extremal theorem on complements, minimum-degree peeling, Brooks; github.com/Robby955/erdos-617-fixed-cases |
| 2026-07-21 | C. Silverstein (Claude, ChatGPT) | computer-assisted; github.com/sprite143/erdos617-r5-computer-proof |
| 2026-07-24 | R. Kara (Codex) | Lean 4 formalisation of Sneiderman's argument, finite step via 89 LRAT certificates replayed in the Lean kernel; doi:10.5281/zenodo.21535385 |
| 2026-07-25 | A. Rose (Codex, Claude) | independent proof; github.com/arose-logos/erdos-gyarfas-r5 |
| 2026-07-31 | N. Winter (Claude, GPT-5.6) | Lean 4, Brouwer/Kang–Pikhurko + four LRAT certificates; github.com/nwinter/erdos-617-r5 |

A further written proof by J. J. Gebendorfer (Sept 2026) backs the r = 5 statement in google-deepmind/formal-conjectures
PR #7223 (one approving review as of 2026-10-15, unmerged). Sneiderman also claims r = 6..9; the all-r conjecture
is open and this report says nothing about it.

The present proof shares only Brooks' theorem with those routes. It uses Füredi's stability theorem instead of
Kang–Pikhurko, a different reduction (Lemma A: K_26 → K_21 with one colour of independence number ≤ 4), and a
different case split with lex-leader symmetry breaking, each case refuted by a SAT solver and certified with
drat-trim-checked DRAT proofs. Agreement with the earlier claims is therefore evidence for the statement that
does not reuse their reasoning. No priority is claimed.
