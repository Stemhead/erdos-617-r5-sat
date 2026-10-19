import sys, time
from pysat.solvers import Solver
import k21
sizes = tuple(int(x) for x in sys.argv[1].split(",")); E = int(sys.argv[2])
cnf = k21.build(sizes, E)
t = time.time()
with Solver(name="kissat404", bootstrap_with=cnf.clauses) as s:
    r = s.solve()
print(f"kissat sizes={sizes} E={E} -> {'SAT' if r else 'UNSAT'} {time.time()-t:.1f}s", flush=True)
