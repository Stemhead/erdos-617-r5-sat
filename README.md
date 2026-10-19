# Erdős Problem #617, the case r = 5: a SAT-based proof with checked certificates

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23485982.svg)](https://doi.org/10.5281/zenodo.23485982)

Archived on Zenodo: https://doi.org/10.5281/zenodo.23485982 (concept DOI, always resolves to the latest version).

**Statement proved.** Every colouring of the edges of the complete graph K₂₆ with five colours contains six
vertices among whose fifteen edges at least one colour is missing. Equivalently, in the notation of
complementary / weakened Ramsey numbers, R̄(6,6,6,6,6) = 26 (the affine plane AG(2,5) gives the matching
colouring of K₂₅, so 26 is sharp). This is the r = 5 instance of the Erdős–Gyárfás conjecture,
[erdosproblems.com/617](https://www.erdosproblems.com/617). The conjecture for all r remains open; nothing here
bears on it.

**Status, honestly stated.**

* The computation is complete: the statement reduces (Lemma A, a hand argument) to the non-existence of a
  5-colouring of K₂₁ with one colour of independence number ≤ 4 and the others ≤ 5; that is split into 117
  SAT instances, and all 117 are unsatisfiable.
* 116 of the 117 instances have DRAT proofs checked by `drat-trim`. The 117th, the hardest instance
  (colour-1 block sizes (5,4,4,4,4), 39 edges), was refuted by CaDiCaL 1.9.5 after about 25 CPU-hours
  **without** a checked certificate; a proof-logging run was stopped at 66 GB of partial proof when the
  session's time ran out. That instance is the obvious target for anyone wanting to finish the certification.
* **This is not the first proof of the statement.** Five AI-assisted proofs were posted on the
  erdosproblems.com proof-claims page in July 2026 (Sneiderman; Silverstein; Kara, Lean-verified; Rose; Winter,
  Lean-verified), plus a written proof by Gebendorfer in September. All of them, like this one, lack review by
  an independent human expert. This proof shares only Brooks' theorem with those routes (it uses Füredi's
  stability theorem instead of Kang–Pikhurko, a different reduction, and a different case split), so its
  agreement with them is independent evidence. No priority is claimed. Details in [REPORT.md §8](REPORT.md).
* Nothing here has been refereed. The work was done by an AI (see [AI_DISCLOSURE.md](AI_DISCLOSURE.md)).

**Read first:** [REPORT.md](REPORT.md) (statement, Lemma A, structure, encoding, results, certification,
prior claims). [NOTES.md](NOTES.md) has the working derivations, including the proofs of Lemma A, Lemma B and
the soundness of the symmetry breaking.

## Proof outline

1. **Lemma A (hand proof).** If no 5-colouring of K₂₁ has one colour class with independence number ≤ 4 and
   the other four with independence number ≤ 5, then every 5-colouring of K₂₆ has a 6-set missing a colour.
   (Vertex deletion forces every colour degree to be exactly 5 at every vertex, so every colour class is
   5-regular; Brooks' theorem then gives a 5-colouring of a colour class, hence an independent 6-set.)
2. **Structure (Füredi 2015, stability for Turán's theorem).** In a hypothetical K₂₁ colouring, every colour
   class is close to a Turán graph, so its complement is close to a union of cliques ("blocks"). The minority
   colour's block sizes and edge count give a finite list of cases: 70 cases where colour 1 is sparse
   (`k21.py`), 47 where it is dense and colour 0's blocks are used instead (`k21c.py`). `coverage.py`
   re-derives both lists independently from the inequalities.
3. **SAT.** Each case is a CNF (≈43 000 variables, ≈465 000 clauses) with clique/independence constraints,
   cardinality constraints, block structure and lex-leader symmetry breaking inside blocks (soundness argued in
   NOTES.md, and tested on the known affine colouring by `lexcheck.py`). All 117 are UNSAT.
4. **Certification.** `k21_cert_all.py` re-solves every case with proof logging and checks the DRAT proof with
   `drat-trim`; results in `certs/results_certs21.json` (115 cases) and `certs/results_b.json` (the 11.6 GB
   proof of case (5,5,4,4,3), E = 39). The 117 CNF files are in the release asset `erdos617-r5-cnf.tar.xz`;
   their hashes are in `certs/SHA256SUMS_cnf.txt`.

## Reproducing

```
python3 -m venv venv && . venv/bin/activate
pip install python-sat          # tested with python-sat 1.9.dev16 (bundles CaDiCaL 1.9.5)
# drat-trim: https://github.com/marijnheule/drat-trim  (expected at ../dl/drat-trim/drat-trim)
python coverage.py              # prints "coverage OK": the 70 + 47 cases match the independent derivation
python lexcheck.py              # the affine K_20 colouring survives the symmetry breaking (SAT expected)
python k21.py 8                 # low regime: solves all cases with E <= 41 on 8 processes (E = 39 cases take hours to a day)
python k21c.py 8 40             # high regime: 47 cases, minutes
python k21_cert_all.py 6        # re-solve with proof logging and check with drat-trim
```

The 117th case alone: `k21.build((5,4,4,4,4), 39)` gives the CNF; expect roughly a CPU-day with CaDiCaL and a
proof in the tens of gigabytes.

## Files

| file | role |
|---|---|
| `REPORT.md`, `NOTES.md` | the write-up and the working notes |
| `k21.py`, `k21c.py` | encoders and parallel drivers for the two regimes |
| `final.py` | `lex_rows`, the symmetry-breaking clauses |
| `coverage.py` | independent re-derivation of the case lists |
| `k21_cert_all.py` | DRAT certification pass |
| `lexcheck.py`, `affine.py`, `k21b.py` | validation against the known AG(2,5) colouring |
| `k21c39.py` | a second, differently structured attack on the E = 39 slice (147/150 cases done, not part of the proof) |
| `logs/` | solver logs for every run cited in the report |
| `certs/` | verification results, the drat-trim transcript for the 11.6 GB proof, CNF hashes |
| `exploration/` | earlier scripts and probes, kept for the record; not vetted, not used in the proof |

Hardware: one Apple M5 laptop, 10 cores, 16 GB. Total wall time from first encoding to last verdict ≈ 33 h.

## License

MIT (code) and CC BY 4.0 (text). See LICENSE.
