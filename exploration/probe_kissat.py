import final, time, sys
from pysat.solvers import Solver
N, sizes, E = 26, (6,5,5,5,5), int(sys.argv[1])
solver = sys.argv[2]
cnf, var, edges = final.build(N, sizes, E, second=False, lex=True)
cnf.to_file(f"cube_{E}_lex.cnf")
t = time.time()
with Solver(name=solver, bootstrap_with=cnf.clauses) as s:
    r = s.solve()
print(f"{solver} sizes={sizes} E={E} lex-only: {'SAT' if r else 'UNSAT'} {time.time()-t:.1f}s", flush=True)
