# Text for the erdosproblems.com proof-claim entry (problem 617, fixed r = 5)

**Summary (short field):**
Independent computer-assisted proof of the fixed r = 5 case: every 5-colouring of E(K₂₆) has a 6-set missing a
colour (R̄(6,6,6,6,6) = 26). Not a first proof: it confirms the July 2026 claims (Sneiderman, Silverstein, Kara,
Rose, Winter) by a different route. Hand reduction to K₂₁ (Lemma A, Brooks), Füredi stability instead of
Kang–Pikhurko, 117 SAT cases, all UNSAT; 116 with drat-trim-checked DRAT certificates, 1 (the hardest) by solver
verdict only. AI-authored (Claude Fable 5.1, operated by Glen Howell); not refereed. Says nothing about general r.

**Link:** https://github.com/Stemhead/erdos-617-r5-sat (REPORT.md; CNF instances in release v1.0)

**Notes field:** The one uncertified case is colour-1 block sizes (5,4,4,4,4) with 39 edges; `k21.build((5,4,4,4,4), 39)`
produces the CNF, CaDiCaL refutes it in ≈25 CPU-hours, and a checked DRAT proof is expected to be 60 GB or more.
