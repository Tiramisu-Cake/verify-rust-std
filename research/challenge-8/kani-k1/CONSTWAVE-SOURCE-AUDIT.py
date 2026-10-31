"""Source-only audit; run from the CONSTWAVE worktree root with Python 3."""

import difflib
import hashlib
import re
import subprocess
from pathlib import Path

BASE = "0d0e585912cb1295c22d4f9e610386d00a88dc9f"
PATH = "library/core/src/slice/sort/shared/smallsort/verify/merge.rs"


def git(*args):
    return subprocess.check_output(["git", *args])


def item(source, name):
    start = source.index("fn " + name)
    return source[start:source.index("\n}\n", start) + 3]


old_bytes = git("show", BASE + ":" + PATH)
new_bytes = Path(PATH).read_bytes()
old, new = old_bytes.decode(), new_bytes.decode()
ops = difflib.SequenceMatcher(None, old.splitlines(True), new.splitlines(True),
                             autojunk=False).get_opcodes()
assert all(op in ("equal", "insert") for op, *_ in ops), "existing source changed"
added = "".join("".join(new.splitlines(True)[j:k])
                for op, _, _, j, k in ops if op == "insert")
assert len(added.splitlines()) == 112
assert git("diff", "--name-only", BASE, "--", "library").decode().splitlines() == [PATH]
assert max(map(len, new.splitlines())) <= 100

pairs = [
    ("stable_general_u64_safety_body", "stable_general_const_u64_safety_body"),
    ("general_route_properties", "general_route_const_properties"),
    ("merge_scratch48_length_body", "merge_scratch48_const_length_body"),
]
for original, copy in pairs:
    expected = item(old, original).replace(original, copy)
    expected = re.sub(r"\[MaybeUninit::<(T|u64)>::uninit\(\);",
                      r"[const { MaybeUninit::<\1>::uninit() };", expected)
    assert item(new, copy) == expected, copy

original, copy = "all_upper_routes_safety_body", "all_upper_routes_const_safety_body"
expected = item(old, original).replace(original, copy).replace(
    "=> stable_general_u64_safety_body", "=> stable_general_const_u64_safety_body")
assert item(new, copy) == expected

original, copy = "stable_direct_u64_properties", "stable_direct_const_u64_properties"
expected = item(old, original).replace(original, copy).replace(
    "    let mut holder = MaybeUninit::<[u64; SMALL_SORT_GENERAL_SCRATCH_LEN]>::uninit();\n"
    "    let scratch = scratch_view(&mut holder);\n",
    "    let mut scratch = [const { MaybeUninit::<u64>::uninit() }; "
    "SMALL_SORT_GENERAL_SCRATCH_LEN];\n").replace(
        "small_sort(&mut v, scratch,", "small_sort(&mut v, &mut scratch,")
assert item(new, copy) == expected
donor = git("show", "7fd3d250a1:" + PATH).decode()
assert item(new, copy) == item(donor, copy).replace(
    "N >= 6 && N <= 9", "N == 6 || N == 7 || N == 8")

# Check complete old items too: diff alignment can split identical braces between copies.
for name in re.findall(r"^fn (\w+)", old, re.M):
    assert item(new, name) == item(old, name), name
for name in re.findall(r"^macro_rules! (\w+)", old, re.M):
    start = old.index("macro_rules! " + name)
    end = old.index("\n}\n", start) + 3
    assert old[start:end] in new, name

# No added imports, macros, types or nested definitions; each new item is opt-in.
assert not re.search(r"\b(?:use|macro_rules|struct|enum|impl|mod|static)\b", added)
names = re.findall(r"^fn (\w+)", added, re.M)
names += re.findall(r"^define_\w+!\(\s*(\w+)", added, re.M)
assert len(names) == len(set(names)) == 11
assert all(not re.search(r"\b" + name + r"\b", old) for name in names)
assert len(re.findall(r"#\[cfg\(kani_smallsort_controls\)\]", added)) == 11
for name in names:
    pattern = (r"#\[cfg\(kani_smallsort_controls\)\]\n(?:#\[[^\n]*\]\n)*"
               r"(?:fn " + name + r"\b|define_\w+!\(\s*" + name + r"\b)")
    assert re.search(pattern, new), name

# Wrapper attributes match the existing macros, whose source bytes remain unchanged.
assert "#[kani::proof]\n#[kani::unwind(34)]\n" + item(
    new, "general_stable_direct_const_u64_n5") in added
assert "#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]\n" \
       "#[kani::unwind(34)]\n" + item(new, "merge_scratch48_contract_const_u8_n9") in added
assert "general_route_const_properties::<u64, _, 5>(lt_u64);" in added
assert "merge_scratch48_const_length_body::<u8, _, 9>(lt_u8);" in added
assert "route_safety_all_routes_const_n16,\n    all_upper_routes_const_safety_body,\n    16" in added
for n in (6, 7, 8):
    assert f"stable_direct_const_u64_n{n}, stable_direct_const_u64_properties, {n}" in added

print("PASS: 112 insertion-only lines; 5 helpers and 6 opt-in harnesses; no shadowing")
print("PASS: old items/macros/imports intact; other library files and dependencies unchanged")
print("PASS: four scratch sites differ only by specified storage/initializer and helper routing")
print("PASS: donor helper exact except baseline guard; wrapper attributes and function items match")
print("base merge.rs sha256:", hashlib.sha256(old_bytes).hexdigest())
print("candidate merge.rs sha256:", hashlib.sha256(new_bytes).hexdigest())
