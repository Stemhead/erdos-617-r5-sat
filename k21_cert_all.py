"""Certification pass for Lemma A: every cube of both regimes re-solved with DRAT proof logging, DIMACS written,
proof checked by drat-trim.  LOW regime (k21.cubes() with E<=39) and HIGH regime (k21c.cubes(40))."""
import sys, time, os, subprocess, json
from multiprocessing import Pool
from pysat.solvers import Solver
import k21, k21c
DRAT = os.path.abspath("../dl/drat-trim/drat-trim")
os.makedirs("certs21", exist_ok=True)
def work(job):
    regime, a, b = job
    if regime == "low":
        tag = f"certs21/low_{'-'.join(map(str,a))}_E{b}"; cnf = k21.build(a, b)
    else:
        tag = f"certs21/high_{'-'.join(map(str,a))}_e0{b}"; cnf = k21c.build(a, b, 40)
    cnf.to_file(tag + ".cnf")
    t0 = time.time()
    with Solver(name="cadical195", bootstrap_with=cnf.clauses, with_proof=True) as s:
        r = s.solve()
        proof = None if r else s.get_proof()
    if r: return job, "SAT", time.time() - t0, ""
    with open(tag + ".drat", "w") as f: f.write("\n".join(proof) + "\n")
    out = subprocess.run([DRAT, tag + ".cnf", tag + ".drat"], capture_output=True, text=True).stdout
    ok = "s VERIFIED" in out
    if ok: os.remove(tag + ".drat")
    return job, "UNSAT " + ("VERIFIED" if ok else "CHECK-FAILED"), time.time() - t0, out[-300:] if not ok else ""
if __name__ == "__main__":
    nproc = int(sys.argv[1])
    jobs = [("low", sz, E) for sz, E in k21.cubes() if E <= 39] + [("high", sz, e0) for sz, e0 in k21c.cubes(40)]
    jobs.sort(key=lambda j: -j[2])
    results = json.load(open("certs21/results.json")) if os.path.exists("certs21/results.json") else {}
    jobs = [j for j in jobs if str(j) not in results]
    print(f"{len(jobs)} jobs", flush=True)
    t0 = time.time()
    with Pool(nproc) as p:
        for job, status, dt, msg in p.imap_unordered(work, jobs):
            results[str(job)] = (status, round(dt, 1))
            json.dump(results, open("certs21/results.json", "w"), indent=1)
            print(f"{time.time()-t0:8.1f}s {job}: {status} ({dt:.1f}s) {msg}", flush=True)
    print("CERT DONE", flush=True)
