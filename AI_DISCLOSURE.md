# AI disclosure

All of the mathematics, code, and text in this repository were produced by Claude (Anthropic, model
Claude Fable 5.1) running in Claude Code on Glen Howell's laptop between 17 and 19 October 2026, in a single
session. Glen Howell chose to let the model pick an open problem, supplied the machine and the time, paused
and resumed the computation, and decided to publish; he did not contribute mathematical content or review the
mathematics. No human mathematician has reviewed any of it.

What was verified by machine and what was not:

* The 117 SAT instances: 116 refuted with DRAT proofs checked by `drat-trim` (Heule), one refuted by the
  solver's verdict only.
* The case split: re-derived by a second script (`coverage.py`) written from the inequalities rather than
  copied from the encoder.
* The encodings: checked against the known affine colouring of K₂₅ / K₂₀ (`lexcheck.py`, `k21b.py`), which
  the encoders must and do admit.
* Lemma A, Lemma B, the use of Füredi's theorem and the soundness of the symmetry breaking are hand arguments
  written by the model (NOTES.md, REPORT.md) and have **not** been checked by a proof assistant or a person.

Honest account of the process: the model began this work on 17 October 2026 believing the r = 5 case to be
open, on the strength of a 15 July 2026 forum comment saying so, and did not check the site's proof-claims tab
or GitHub. The five July 2026 claims were found on 18 October, after 116 of the 117 cases were already
certified. Two earlier bugs during development (a variable collision in pseudo-Boolean constraints that
produced bogus two-second "UNSAT" results, and a missing at-most-one constraint that produced a bogus "SAT")
were caught by the affine-colouring checks and fixed before any result reported here was produced; the
scripts from that period are in `exploration/` and are not used in the proof.
