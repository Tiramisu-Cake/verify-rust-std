"""Static gate for CASE5 requests (read-only git/source; no cargo/rustc/Kani). From the repo root:
python3 research/challenge-8/kani-k1/casefive/check_casefive.py BASE LIBCOMMIT REQUEST.json"""
import json, re, subprocess, sys

base, lib, reqp = sys.argv[1], sys.argv[2], sys.argv[3]
S = "library/core/src/slice/sort/shared/smallsort/verify/"
git = lambda *a: subprocess.run(["git", *a], check=True, capture_output=True, text=True).stdout
ok = True
def check(cond, msg):
    global ok
    ok &= bool(cond)
    print(("ok   " if cond else "FAIL ") + msg)

files = [f for f in git("diff", "--name-status", base, lib, "--", "library").split("\n") if f]
check(files == [f"M\t{S}merge.rs", f"A\t{S}merge/casefive.rs"], f"library diff = merge.rs + new casefive.rs: {files}")
d = [l for l in git("diff", "-U0", base, lib, "--", S + "merge.rs").split("\n")
     if l and l[0] in "+-" and not l.startswith(("+++", "---"))]
check(d == ["+#[cfg(kani_smallsort_controls)]", "+mod casefive;"], f"merge.rs: only cfg-gated registration {d}")
check(git("diff", "--name-only", base, lib, "--", "library", f":!{S}").strip() == "",
      "no change outside smallsort/verify (runtime library untouched)")
src = git("show", f"{lib}:{S}merge/casefive.rs")
check("#[cfg(" not in src and "cfg!(" not in src, "casefive.rs has no inner cfg (module gated by its declaration)")
msgs = {n: re.findall(r'"(casefive [^"]*)"', body)
        for n, body in re.findall(r"\n#\[kani::unwind\(140\)\]\nfn (casefive_\w+)\(\) \{(.*?)\n\}\n", src, re.S)}
mac = re.search(r"macro_rules! casefive_closure_swap \{(.*?)\n\}\n", src, re.S).group(1)
tails = re.findall(r'concat!\("casefive ", \$row, "([^"]*)"\)', mac)
for n, row in re.findall(r'^casefive_closure_swap!\((casefive_\w+), "(R\d)", \d+\);', src, re.M):
    msgs[n] = [f"casefive {row}{t}" for t in tails]
nproof = src.count("#[kani::proof]") - 1 + len(re.findall(r"^casefive_closure_swap!\(", src, re.M))
check(len(msgs) == nproof, f"{nproof} harnesses in source, messages parsed for {len(msgs)}")
allm = [m for v in msgs.values() for m in v]
check(len(allm) == len(set(allm)), f"{len(allm)} messages, all unique")
req = json.load(open(reqp))
P = "slice::sort::shared::smallsort::verify::merge::casefive::"
for h in req["harnesses"]:
    n = h["name"].removeprefix(P)
    check(h["name"].startswith(P) and n in msgs, f"{n} exists in source")
    if "expect_check" in h:
        hit = [m for m in allm if h["expect_check"] in m]
        check(hit and all(m in msgs.get(n, []) for m in hit), f"{n} expect_check {h['expect_check']!r} -> {hit}")
check(req["kind"] == "diagnostic" and req["harness_timeout_minutes"] == 3 and req["controls"] is True
      and req["kani_jobs"] == 1 and req["uninit_checks"] is False, "kind diagnostic, 3 min, controls, jobs 1, uninit off")
print("GATE", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
