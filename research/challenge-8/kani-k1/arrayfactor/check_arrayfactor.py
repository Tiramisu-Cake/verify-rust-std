"""Read-only static gate for the arrayfactor request. From the repo root:
python3 research/challenge-8/kani-k1/arrayfactor/check_arrayfactor.py BASE LIBCOMMIT REQUEST.json
BASE = arrayfactor task commit (db9583a0b9). No cargo/rustc/Kani is run.
"""
import json, re, subprocess, sys

base, lib, reqp = sys.argv[1], sys.argv[2], sys.argv[3]
C = "library/core/src/slice/sort/shared/smallsort/verify/merge/casefive.rs"
P = "slice::sort::shared::smallsort::verify::merge::casefive::"
OLD = ["casefive_d1_select_read_bytes1", "casefive_d2_select_read_u8"]
NEW = ["arrayfactor_f2_if_bytes1", "arrayfactor_f3_deref_bytes1",
       "arrayfactor_f4_from_fn_bytes1", "arrayfactor_f5_symbolic_indices_bytes1",
       "arrayfactor_f6_address_bytes1", "arrayfactor_f7_witness_bytes1"]
MESSAGES = {
    "arrayfactor_f2_if_bytes1": ["arrayfactor F2: read through if selection"],
    "arrayfactor_f3_deref_bytes1": ["arrayfactor F3: copy through dereference"],
    "arrayfactor_f4_from_fn_bytes1": ["arrayfactor F4: read from from_fn selection"],
    "arrayfactor_f5_symbolic_indices_bytes1": ["arrayfactor F5: read through symbolic indices"],
    "arrayfactor_f6_address_bytes1": ["arrayfactor F6: selected address",
                                      "arrayfactor F6: read through the selection"],
    "arrayfactor_f7_witness_bytes1": ["arrayfactor F7: first selected value",
                                      "arrayfactor F7: second selected value"],
}
git = lambda *a: subprocess.run(["git", *a], check=True, capture_output=True, text=True).stdout
ok = True
def check(cond, msg):
    global ok
    ok &= bool(cond)
    print(("ok   " if cond else "FAIL ") + msg)

def norm(s):
    return re.sub(r"\s+", "", s)

files = [f for f in git("diff", "--name-status", base, lib).splitlines() if f]
check(files == [f"M\t{C}"], f"diff {base[:10]}..{lib[:10]} = casefive.rs only: {files}")
old, new = git("show", f"{base}:{C}"), git("show", f"{lib}:{C}")
check(new.startswith(old), "entire old casefive.rs is a byte-identical prefix")
tail = new[len(old):]
check("#[cfg(" not in tail and "cfg!(" not in tail, "no inner cfg in appended harnesses")
heads = re.findall(r"#\[kani::proof\]\s*#\[kani::unwind\((\d+)\)\]\s*fn (\w+)\(\)", tail)
check([name for _, name in heads] == NEW, f"six new proof harnesses appended in order: {[n for _, n in heads]}")
check(all(unwind == "180" for unwind, _ in heads), "unwind 180 on every appended harness")

# Isolate each new function to inspect statement order and its literal assertions.
blocks = {}
for i, name in enumerate(NEW):
    start = tail.find(f"fn {name}()")
    end = tail.find("#[kani::proof]", start + 1) if i + 1 < len(NEW) else len(tail)
    blocks[name] = tail[start:end]
    check(start >= 0 and (i + 1 == len(NEW) or end > start), f"found function body {name}")

for name, block in blocks.items():
    covers = [m.start() for m in re.finditer(r"kani::cover!\s*\(|kani::cover\s*\(", block)]
    asserts = [m.start() for m in re.finditer(r"kani::assert!\s*\(|kani::assert\s*\(", block)]
    check(bool(covers) and bool(asserts) and max(covers) < min(asserts),
          f"{name}: all covers precede every assert")
    actual = []
    for call in re.finditer(r"kani::assert!?\s*\(", block):
        end = block.find(";", call.start())
        args = block[call.end():end if end >= 0 else len(block)]
        literals = re.findall(r'"([^"]+)"', args)
        if literals:
            actual.append(literals[-1])
    check(actual == MESSAGES[name], f"{name}: expected assertion message(s): {actual}")
    boolean_positions = [m.start() for m in re.finditer(r"let\s+\w+_ok\s*=", block)]
    check(bool(boolean_positions) and max(boolean_positions) < min(asserts),
          f"{name}: every oracle boolean is computed before the first assert")
    compact = norm(block)
    check("kani::cover(c&&x[0]!=y[0]" in compact and "kani::cover(!c&&x[0]!=y[0]" in compact,
          f"{name}: c/!c covers require differing values")

# Factor-specific source checks, normalized so whitespace and comments do not matter.
f2, f3, f4, f5, f6, f7 = (norm(blocks[n]) for n in NEW)
d1 = norm(old[old.find("fn casefive_d1_select_read_bytes1()"):old.find("fn casefive_d2_select_read_u8()")])
check("lets=ifc{base}else{unsafe{base.add(1)}};" in f2 and "ptr::read(s)" in f2,
      "F2: if-selected pointer then ptr::read")
check("hint::select_unpredictable(c,base,unsafe{base.add(1)})" in f3 and "letgot=unsafe{*s};" in f3,
      "F3: D1 selector with copy by dereference")
check("crate::array::from_fn(|k|ifk==0{x}else{y})" in f4
      and "hint::select_unpredictable(c,base,unsafe{base.add(1)})" in f4,
      "F4: from_fn array construction with D1 selection")
check("letr:bool=kani::any();" in f5 and "let(i,j)=ifr{(1,0)}else{(0,1)};" in f5
      and "base.add(i)" in blocks[NEW[3]] and "base.add(j)" in blocks[NEW[3]],
      "F5: symbolic r-controlled index order")
check(all(x in f5 for x in ["kani::cover(c&&x[0]!=y[0]", "kani::cover(!c&&x[0]!=y[0]",
                              "kani::cover(r&&x[0]!=y[0]", "kani::cover(!r&&x[0]!=y[0]"]),
      "F5: c/!c and r/!r covers require differing values")
check("letaddr_ok=s==ifc{base}else{unsafe{base.add(1)}};" in f6
      and "kani::cover(addr_ok&&!value_ok" in f6 and "kani::cover(!addr_ok" in f6
      and "kani::cover(addr_ok&&value_ok" in f6,
      "F6: address/value booleans and all three outcome covers")
check("letx:[u8;1]=[1];" in f7 and "lety:[u8;1]=[2];" in f7
      and "ifc{kani::assert(first_ok" in f7 and "else{kani::assert(second_ok" in f7,
      "F7: concrete distinct witness values and path-specific assertions")
# Each experiment keeps D1's base, selector, and selected read, except the named factor.
check(all(x in d1 for x in ["letbase=v.as_mut_ptr();", "letgot=unsafe{ptr::read(s)};"])
      and "letbase=v.as_mut_ptr();" in f2 and "letbase=v.as_mut_ptr();" in f3
      and "letbase=v.as_mut_ptr();" in f4 and "letbase=v.as_mut_ptr();" in f5
      and "letbase=v.as_mut_ptr();" in f6 and "letbase=v.as_mut_ptr();" in f7,
      "F2-F7 retain D1's shared array base setup")

req = json.load(open(reqp))
rows = req["harnesses"]
names = [h["name"].removeprefix(P) for h in rows]
EXPECTED = ["casefive_d1_select_read_bytes1", "casefive_d2_select_read_u8"] + NEW
check(names == EXPECTED and all(h["name"].startswith(P) for h in rows),
      f"request has exactly F0-F7 rows in order: {names}")
expected_results = ["FAILED", "SUCCESS", "FAILED", "FAILED", "FAILED", "SUCCESS", "FAILED", "FAILED"]
check([h.get("expect") for h in rows] == expected_results,
      f"request predictions F0/F2/F3/F4/F6/F7 fail, F1/F5 succeed: {[h.get('expect') for h in rows]}")
checks = {h["name"].removeprefix(P): h.get("expect_check") for h in rows}
check(all(h.get("expect_check") for h in rows if h.get("expect") == "FAILED"),
      "every FAILED request row names its own expected assertion")
check(checks.get(OLD[0]) == "casefive D1: read through the selection"
      and checks.get("arrayfactor_f6_address_bytes1") == "arrayfactor F6: read through the selection"
      and checks.get("arrayfactor_f7_witness_bytes1") == "arrayfactor F7: first selected value",
      f"expect_check literals identify F0, F6 value, and F7 first-value assertions: {checks}")
# Every declared expect_check must identify exactly one assert literal in its harness.
by_name = {n: old[old.find(f"fn {n}()"):old.find("\n///", old.find(f"fn {n}()") + 1)] for n in OLD}
by_name.update(blocks)
for h in rows:
    check_literal = h.get("expect_check")
    if check_literal:
        source = by_name.get(h["name"].removeprefix(P), "")
        found = re.findall(r'kani::assert(?:!|)\s*\([^;]*?"([^"]+)"', source, re.S)
        check(found.count(check_literal) == 1, f"expect_check appears on exactly one assert: {h['name']}")
check(req.get("schema") == "kani-k1-run-request-v1" and req.get("runner") == "gcb-e2-standard-4"
      and req.get("kind") == "diagnostic" and req.get("request_id", "").startswith("arrayfactor-")
      and req.get("harness_timeout_minutes") == 3 and req.get("controls") is True
      and req.get("kani_jobs") == 1 and req.get("uninit_checks") is False,
      "request is diagnostic on standard4, arrayfactor ID, timeout 3, controls/jobs/uninit settings correct")
print("GATE", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
