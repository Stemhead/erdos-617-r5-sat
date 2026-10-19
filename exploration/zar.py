"""z(m,n;3,3): max cells in an m x n 0/1 matrix with no all-ones 3x3 submatrix (K_{3,3}-free bipartite)."""
import itertools, sys
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver
def z(m, n, s, t):
    cell = lambda i, j: i * n + j + 1
    cnf = CNF()
    for R in itertools.combinations(range(m), s):
        for C in itertools.combinations(range(n), t):
            cnf.append([-cell(i, j) for i in R for j in C])
    best = 0
    for b in range(1, m * n + 1):
        pool = IDPool(start_from=m * n + 1)
        c2 = CNF(from_clauses=cnf.clauses)
        c2.extend(CardEnc.atleast(list(range(1, m * n + 1)), bound=b, vpool=pool, encoding=EncType.seqcounter).clauses)
        with Solver(name="cadical195", bootstrap_with=c2.clauses) as S:
            if S.solve(): best = b
            else: break
    return best
print("z(5,5;3,3) =", z(5, 5, 3, 3))
print("z(4,4;3,3) =", z(4, 4, 3, 3))
print("z(5,5;2,4) =", z(5, 5, 2, 4), " z(5,5;4,2) =", z(5, 5, 4, 2))
print("z(6,6;3,3) =", z(6, 6, 3, 3))
