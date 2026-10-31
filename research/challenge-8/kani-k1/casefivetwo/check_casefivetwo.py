"""Static gate for the CASE5-2 request (read-only git/source; no cargo/rustc/Kani). From the repo root:
python3 research/challenge-8/kani-k1/casefivetwo/check_casefivetwo.py BASE LIBCOMMIT REQUEST.json
BASE = CASE5-2 task commit (0b63fbdaac); LIBCOMMIT = the CASE5-2 library commit."""
import json, re, subprocess, sys

base, lib, reqp = sys.argv[1], sys.argv[2], sys.argv[3]
S = "library/core/src/slice/sort/shared/smallsort/verify/"
C = S + "merge/casefive.rs"
P = "slice::sort::shared::smallsort::verify::merge::casefive::"
NEW = ["casefive_a1_plain_profile_bytes17", "casefive_a2_raw_call_bytes17",
       "casefive_p17_checked_contract_bytes17", "casefive_p16_checked_contract_bytes16",
       "casefive_s4_checked_contract_bytes16", "casefive_c1_bad_body_contract_bytes17",
       "casefive_d1_select_read_bytes1", "casefive_d2_select_read_u8"]
ENS = "swap_transfer::<P>(old(pair_models::<P>(v, a, b)), v, a, b)"
git = lambda *a: subprocess.run(["git", *a], check=True, capture_output=True, text=True).stdout
ok = True
def check(cond, msg):
    global ok
    ok &= bool(cond)
    print(("ok   " if cond else "FAIL ") + msg)

files = [f for f in git("diff", "--name-status", base, lib).split("\n") if f]
check(files == [f"M\t{C}"], f"diff {base[:10]}..{lib[:10]} = casefive.rs only: {files}")
old, new = git("show", f"{base}:{C}"), git("show", f"{lib}:{C}")
# Old rows unchanged: new = old with a doc insertion, the import block replaced, and a tail appended.
u0, u1 = old.index("use crate::mem::ManuallyDrop;"), old.index("use crate::{hint, kani, ptr};\n")
old_doc, old_body = old[:u0], old[u1 + len("use crate::{hint, kani, ptr};\n"):]
n0, n1 = new.index("use super::super::network"), new.index("use crate::{hint, kani, ptr};\n")
new_doc, new_rest = new[:n0], new[n1 + len("use crate::{hint, kani, ptr};\n"):]
check(new_doc.startswith(old_doc.rstrip("\n").rsplit("\n", 1)[0]) and len(new_doc) > len(old_doc)
      and new_doc.count("\n") == old_doc.count("\n") + 3, "module doc: 3 lines appended, old lines kept")
check(new_rest.startswith(old_body), "G1/G2 rows (everything after the imports) byte-identical, tail appended")
tail = new_rest[len(old_body):]
check("#[cfg(" not in new and "cfg!(" not in new, "no inner cfg (module gated by its declaration in merge.rs)")
check(git("show", f"{lib}:{S}merge.rs") == git("show", f"{base}:{S}merge.rs"), "merge.rs unchanged")
heads = re.findall(r"#\[kani::(proof|proof_for_contract\((\w+)\))\]\n#\[kani::unwind\((\d+)\)\]\nfn (casefive_\w+)\(\)", tail)
check([h[3] for h in heads] == NEW, f"8 new harnesses in order: {[h[3] for h in heads]}")
check(all(h[2] == "180" for h in heads), "unwind 180 on every new row")
tgt = {h[3]: h[1] for h in heads}
check(tgt["casefive_p17_checked_contract_bytes17"] == tgt["casefive_p16_checked_contract_bytes16"]
      == "swap_profile_checked" and tgt["casefive_s4_checked_contract_bytes16"] == "sort4_profile_checked"
      and tgt["casefive_c1_bad_body_contract_bytes17"] == "bad_swap_profile"
      and all(tgt[n] == "" for n in NEW if "_a" in n[8:11] or "_d" in n[8:11]), f"targets {tgt}")
# Twins carry exactly the contract attributes of the originals.
spec = git("show", f"{lib}:{S}merge/specfix.rs")
def attrs(src, fn):
    m = re.search(r"((?:#\[kani::[^\n]*\]\n)+)(?:pub\(crate\) )?unsafe fn " + fn + r"<P: Profile>\(", src)
    return m.group(1) if m else None
sw, s4 = attrs(spec, "swap_profile"), attrs(spec, "sort4_profile")
check(sw and attrs(tail, "swap_profile_checked") == sw, "swap_profile_checked contract == swap_profile contract")
check(sw and attrs(tail, "bad_swap_profile") == sw, "bad_swap_profile contract == swap_profile contract")
check(s4 and attrs(tail, "sort4_profile_checked") == s4, "sort4_profile_checked contract == sort4_profile contract")
check("swap_if_less(v, a, b, &mut is_less);" in tail and "sort4_stable(src, dst, &mut is_less);" in tail,
      "twins call the real swap_if_less / sort4_stable as the profiles do")
bad = re.search(r"unsafe fn bad_swap_profile<P: Profile>\(.*?\n\}\n", tail, re.S).group(0)
check("select_unpredictable" not in bad and "swap_if_less" not in bad, "C1 body: no selected pointer, no swap_if_less")
msgs = [m for m in re.findall(r'"(casefive [^"]*)"', new) if m != "casefive "]  # R0/R4 concat! prefix
check(len(msgs) == len(set(msgs)), f"{len(msgs)} literal casefive messages (R0/R4 concat! prefix excluded), all unique")
check(tail.count(ENS) == 2, "transfer ensures text occurs in the tail only on the two swap-contract targets")
req = json.load(open(reqp))
names = [h["name"].removeprefix(P) for h in req["harnesses"]]
check(names == NEW and all(h["name"].startswith(P) for h in req["harnesses"]), "request = the 8 new rows")
exp = {h["name"].removeprefix(P): (h["expect"], h.get("expect_check")) for h in req["harnesses"]}
check(exp["casefive_c1_bad_body_contract_bytes17"] == ("FAILED", ENS), "C1 expects FAILED on the transfer ensures")
d1 = exp["casefive_d1_select_read_bytes1"]
check(d1[0] == "FAILED" and [m for m in msgs if d1[1] in m] == ["casefive D1: read through the selection"],
      "D1 expect_check matches only D1's assert")
check(all(e == ("SUCCESS", None) for n, e in exp.items() if n not in
          ("casefive_c1_bad_body_contract_bytes17", "casefive_d1_select_read_bytes1")), "other rows expect SUCCESS")
check(req["kind"] == "diagnostic" and req["harness_timeout_minutes"] == 3 and req["controls"] is True
      and req["kani_jobs"] == 1 and req["uninit_checks"] is False, "kind diagnostic, 3 min, controls, jobs 1, uninit off")
print("GATE", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
