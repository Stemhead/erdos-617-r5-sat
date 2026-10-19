"""Certification pass for the K21 cubes: re-solve each cube with DRAT proof logging, write DIMACS + proof,
check with drat-trim. Run after k21_full.log shows all cubes UNSAT."""
import sys, time, os, subprocess, json
from multiprocessing import Pool
from pysat.solvers import Solver
import k21
DRAT = os.path.abspath("../dl/drat-trim/drat-trim")
os.makedirs("certs21", exist_ok=True)
def work(args):
    sizes, E = args
    tag = f"certs21/K21_{'-'.join(map(str,sizes))}_E{E}"
    cnf = k21.build(sizes, E)
    cnf.to_file(tag + ".cnf")
    t0 = time.time()
    with Solver(name="cadical195", bootstrap_with=cnf.clauses, with_proof=True) as s:
        r = s.solve()
        proof = None if r else s.get_proof()
    if r: return sizes, E, "SAT", time.time() - t0, ""
    with open(tag + ".drat", "w") as f: f.write("\n".join(proof) + "\n")
    out = subprocess.run([DRAT, tag + ".cnf", tag + ".drat"], capture_output=True, text=True).stdout
    ok = "s VERIFIED" in out
    if ok: os.remove(tag + ".drat")   # keep disk small; cnf kept for the record
    return sizes, E, "UNSAT " + ("VERIFIED" if ok else "CHECK-FAILED"), time.time() - t0, out[-300:] if not ok else ""
if __name__ == "__main__":
    nproc = int(sys.argv[1])
    cs = k21.cubes()
    t0 = time.time(); results = {}
    with Pool(nproc) as p:
        for sizes, E, status, dt, msg in p.imap_unordered(work, cs):
            results[f"{sizes}|{E}"] = status
            print(f"{time.time()-t0:8.1f}s sizes={sizes} E={E}: {status} ({dt:.1f}s) {msg}", flush=True)
            json.dump(results, open("certs21/results.json", "w"), indent=1)
    print("CERT DONE", flush=True)
