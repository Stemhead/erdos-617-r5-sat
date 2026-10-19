"""Independent verification pass for the exact N(a) table.
For every non-base vector a (bottom-up): recompute the counting kill-set from the exact lower values,
re-solve each candidate n; SAT -> check the colouring with networkx (independence numbers, degrees) and save it;
UNSAT -> write DIMACS + DRAT proof and check with drat-trim."""
import itertools, json, os, subprocess, sys, time
from math import comb, ceil
import networkx as nx
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

k = 5
N = json.load(open("exact.json"))
key = lambda a: ",".join(map(str, sorted(a)))
os.makedirs("certs", exist_ok=True)
DRAT = "../dl/drat-trim/drat-trim"

def base(a):
    a = tuple(sorted(a))
    if a[0] == 0: return 0
    if a[0] == 1: return min(a[1:]) if a.count(1) == 1 else 1
    return None

def killed(n, a, subs):
    mins = [n - 1 - subs[c] for c in range(k)]
    if sum(mins) > n - 1: return "count"
    if sum(mins) == n - 1:
        for c in range(k):
            D = mins[c]
            if (n * D) % 2 == 1: return f"parity(c={c},D={D})"
            clique_ok = all(D + 1 <= a[cc] for cc in range(k) if cc != c)
            if D >= 3 and not clique_ok:
                if ceil(n / D) > a[c]: return f"brooks(c={c},D={D})"
            else:
                if ceil(n / (D + 1)) > a[c]: return f"greedy(c={c},D={D})"
    return None

def instance(n, a, subs):
    edges = list(itertools.combinations(range(n), 2))
    eid = {e: i for i, e in enumerate(edges)}
    var = lambda e, c: eid[e] * k + c + 1
    pool = IDPool(start_from=len(edges) * k + 1)
    cnf = CNF()
    for e in edges:
        cnf.append([var(e, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                cnf.append([-var(e, c1), -var(e, c2)])
    for c in range(k):
        for S in itertools.combinations(range(n), a[c] + 1):
            cnf.append([var(e, c) for e in itertools.combinations(S, 2)])
    for v in range(n):
        for c in range(k):
            lb = n - 1 - subs[c]
            if lb > 0:
                lits = [var(tuple(sorted((v, u))), c) for u in range(n) if u != v]
                cnf.extend(CardEnc.atleast(lits, bound=lb, vpool=pool, encoding=EncType.seqcounter).clauses)
    for j in range(1, n - 1):
        for c in range(k):
            cnf.append([-var((0, j), c)] + [var((0, j + 1), c2) for c2 in range(c, k)])
    return cnf, var, edges

def check_colouring(n, a, col):
    for c in range(k):
        G = nx.Graph(); G.add_nodes_from(range(n))
        G.add_edges_from(e for e, cc in col.items() if cc == c)
        alpha = max(len(q) for q in nx.find_cliques(nx.complement(G)))
        if alpha > a[c]: return False, f"colour {c} alpha={alpha} > {a[c]}"
    return True, "ok"

vecs = sorted({tuple(sorted(v)) for v in itertools.product(range(0, 6), repeat=k)}, key=lambda v: (sum(v), v))
only = sys.argv[1:]  # optional: restrict to listed vectors like 3,5,5,5,5
report = []
for a in vecs:
    if base(a) is not None:
        assert N[key(a)] == base(a); continue
    if only and key(a) not in only: continue
    val = N[key(a)]
    subs = [N[key(tuple(a[j] - (1 if j == c else 0) for j in range(k)))] for c in range(k)]
    # must verify: (i) a colouring exists at n=val, (ii) n=val+1 impossible (killed or UNSAT)
    t0 = time.time()
    lines = [f"a={a} N={val} subs={subs}"]
    # (ii)
    kl = killed(val + 1, a, subs)
    tb = next((s - 1 for s in range(2, 60) if sum(1 for x in a if x < s) > comb(s, 2)), 10**9)
    if val + 1 > tb:
        lines.append(f"  n={val+1}: impossible by trivial size bound ({tb})")
    elif kl:
        lines.append(f"  n={val+1}: killed by {kl}")
    else:
        cnf, var, edges = instance(val + 1, a, subs)
        with Solver(name="cadical195", bootstrap_with=cnf.clauses, with_proof=True) as s:
            res = s.solve()
            assert not res, f"n={val+1} unexpectedly SAT for {a}"
            proof = s.get_proof()
        tag = f"n{val+1}_a{'-'.join(map(str,a))}"
        cnf.to_file(f"certs/{tag}.cnf")
        with open(f"certs/{tag}.drat", "w") as f: f.write("\n".join(proof) + "\n")
        out = subprocess.run([DRAT, f"certs/{tag}.cnf", f"certs/{tag}.drat"], capture_output=True, text=True).stdout
        ok = "s VERIFIED" in out
        lines.append(f"  n={val+1}: UNSAT, drat-trim {'VERIFIED' if ok else 'FAILED'} ({len(proof)} proof lines)")
        if not ok: lines.append(out[-500:])
    # (i)
    cnf, var, edges = instance(val, a, subs)
    with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
        res = s.solve()
        assert res, f"n={val} unexpectedly UNSAT for {a}"
        m = set(l for l in s.get_model() if l > 0)
    col = {e: next(c for c in range(k) if var(e, c) in m) for e in edges}
    ok, msg = check_colouring(val, a, col)
    lines.append(f"  n={val}: colouring found, independent check: {msg}")
    assert ok
    json.dump({"n": val, "a": a, "colouring": {f"{e[0]}-{e[1]}": c for e, c in col.items()}}, open(f"certs/colouring_n{val}_a{'-'.join(map(str,a))}.json", "w"))
    lines.append(f"  ({time.time()-t0:.1f}s)")
    print("\n".join(lines), flush=True)
print("VERIFY DONE")
