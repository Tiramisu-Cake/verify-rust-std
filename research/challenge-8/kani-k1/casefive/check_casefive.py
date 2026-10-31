"""Static gate for CASE5 G1 (read-only git/source; no cargo/rustc/Kani). Usage: from the repo root,
python3 research/challenge-8/kani-k1/casefive/check_casefive.py BASE LIBCOMMIT"""
import json, re, subprocess, sys

base, lib = sys.argv[1], sys.argv[2]
S = "library/core/src/slice/sort/shared/smallsort/verify/"
git = lambda *a: subprocess.run(["git", *a], check=True, capture_output=True, text=True).stdout
ok = True
def check(cond, msg):
    global ok
    ok &= bool(cond)
    print(("ok   " if cond else "FAIL ") + msg)

files = git("diff", "--name-status", base, lib, "--", "library").split("\n")
files = [f for f in files if f]
check(files == [f"M\t{S}merge.rs", f"A\t{S}merge/casefive.rs"], f"library diff = merge.rs + new casefive.rs: {files}")
d = [l for l in git("diff", "-U0", base, lib, "--", S + "merge.rs").split("\n")
     if l and l[0] in "+-" and not l.startswith(("+++", "---"))]
check(d == ["+#[cfg(kani_smallsort_controls)]", "+mod casefive;"], f"merge.rs: only cfg-gated registration {d}")
src = git("show", f"{lib}:{S}merge/casefive.rs")
check("#[cfg(" not in src and "cfg!(" not in src, "casefive.rs has no inner cfg (module gated by its declaration)")
names = re.findall(r"^fn (casefive_\w+)\(", src, re.M)
names += re.findall(r"^casefive_closure_swap!\((casefive_\w+),", src, re.M)
req = json.load(open("research/challenge-8/kani-k1/RUN-REQUEST.json"))
P = "slice::sort::shared::smallsort::verify::merge::casefive::"
rnames = [h["name"].removeprefix(P) for h in req["harnesses"]]
check(sorted(rnames) == sorted(names) and len(names) == 8, f"request names = 8 source harnesses")
check(src.count("#[kani::proof]") == 7 and src.count("casefive_closure_swap!(casefive_") == 2,
      "7 proof attributes, macro instantiated twice -> 8 harnesses")
# messages per row: literal strings, and the macro's concat! expanded per instantiation
msgs = {}
for row, body in re.findall(r"\n/// (R\d):.*?\nfn casefive_\w+\(\) \{(.*?)\n\}\n", src, re.S):
    msgs[row] = re.findall(r'"(casefive [^"]*)"', body)
mac = re.search(r"macro_rules! casefive_closure_swap \{(.*?)\n\}\n", src, re.S).group(1)
tails = re.findall(r'concat!\("casefive ", \$row, "([^"]*)"\)', mac)
for row in ("R0", "R4"):
    msgs[row] = [f"casefive {row}{t}" for t in tails]
check(sorted(msgs) == [f"R{i}" for i in range(8)], f"messages found for rows {sorted(msgs)}")
allm = [m for v in msgs.values() for m in v]
check(len(allm) == len(set(allm)), f"{len(allm)} messages, all unique")
for h in req["harnesses"]:
    row = "R" + re.search(r"casefive_r(\d)_", h["name"]).group(1)
    if "expect_check" in h:
        hit = [m for m in allm if h["expect_check"] in m]
        own = all(m in msgs[row] for m in hit)
        check(hit and own, f"{row} expect_check {h['expect_check']!r} -> {hit}")
check(req["kind"] == "diagnostic" and req["harness_timeout_minutes"] == 3 and req["controls"] is True
      and req["kani_jobs"] == 1 and req["uninit_checks"] is False, "kind diagnostic, 3 min, controls, jobs 1, uninit off")
rt = git("diff", "--name-only", base, lib, "--", "library", f":!{S}")
check(rt.strip() == "", "no change outside smallsort/verify (runtime library untouched)")
print("GATE", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
