import final, time, sys
from multiprocessing import Pool
def run(args):
    N, sizes, E, second, lex = args
    cnf, var, edges = final.build(N, sizes, E, second=second, lex=lex)
    from pysat.solvers import Solver
    t = time.time()
    with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
        r = s.solve()
    return (N, sizes, E, second, lex, r, time.time() - t, cnf.nv, len(cnf.clauses))
if __name__ == "__main__":
    jobs = [(26, (6,5,5,5,5), 65, True, True), (26, (6,5,5,5,5), 60, True, True), (26, (7,5,5,5,4), 65, True, True),
            (26, (6,5,5,5,5), 65, False, True)]
    t0 = time.time()
    with Pool(4) as p:
        for N, sizes, E, second, lex, r, dt, nv, nc in p.imap_unordered(run, jobs):
            print(f"{time.time()-t0:8.1f}s N={N} sizes={sizes} E={E} second={second} lex={lex}: {'SAT' if r else 'UNSAT'} {dt:.1f}s nv={nv} nc={nc}", flush=True)
    print("DONE", flush=True)
