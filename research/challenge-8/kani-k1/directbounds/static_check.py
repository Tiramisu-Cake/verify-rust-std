"""DIRECTBOUNDS source/packet checks only. Does not run a compiler or verifier."""
import difflib
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = "f23d7f2354cff734880cd1b930e6ee8e56289815"
TOOL_BASE = "e8e238db9d87323fa4da011a1a8b37fb76ec91c0"
NET = "library/core/src/slice/sort/shared/smallsort/verify/network/"
PARENT = NET + "netcomp.rs"
MODULE = NET + "netcomp/directbounds.rs"
LANE = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
        "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh", "tool_config/kani-version.toml",
        "rust-toolchain.toml", ".gitmodules", ".cargo", "library/.cargo", "library/Cargo.toml",
        "library/Cargo.lock"]
REGISTRATION = "\n#[cfg(kani_smallsort_controls)]\nmod directbounds;\n"
ROOTS = ["direct_u8_n10", "direct_u8_n13", "count_negative_u8_n10", "count_negative_u8_n13"]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def sha(data):
    return hashlib.sha256(data.encode()).hexdigest()


def item(src, header):
    """Text of one top-level item from its attributes to its closing brace."""
    start = src.index(header)
    attrs = src.rfind("\n\n", 0, start) + 2
    return src[attrs:src.index("\n}\n", start) + 3]


source = (ROOT / MODULE).read_text()
parent = (ROOT / PARENT).read_text()
old_parent = git("show", f"{BASE}:{PARENT}")

# Library delta: one new file plus the exact appended registration line.
assert git("diff", "--name-only", BASE, "--", "library").splitlines() == [PARENT, MODULE]
assert parent == old_parent + REGISTRATION
assert not git("diff", TOOL_BASE, "--", *LANE)
assert git("rev-parse", f"{BASE}:library").strip() == "3b6d2a51dae08e52464f4b2b82f5168d8ba9977b"

code = "\n".join(line.split("//")[0] for line in source.splitlines())
# Roots: exactly four, each only proof + unwind(25); no stubs/contracts/adapters/assumes/solver.
names = re.findall(r"^fn (\w+)\(\)", source, re.M)
assert names == ROOTS, names
annotations = {}
for name in names:
    block = item(source, f"fn {name}()")
    annotations[name] = re.findall(r"#\[kani::[^\n]+", block)
    assert annotations[name] == ["#[kani::proof]", "#[kani::unwind(25)]"], (name, annotations[name])
for banned in ["kani::stub", "stub_verified", "proof_for_contract", "kani::requires",
               "kani::ensures", "kani::modifies", "kani::assume", "any_where", "kani::solver",
               "adapter", "SwapBridge", "register", "CONTEXT", "static mut", "pub "]:
    assert banned not in code, banned
assert source.count("#[kani::") == 8
assert source.count("<u8 as UnstableSmallSortTypeImpl>::small_sort(v, cmp);") == 2
assert source.count("let mut cmp: U8Cmp = StrictU8::CMP;") == 4
assert max(map(len, source.splitlines())) <= 100

# Positives: same body as A9 positive9 with N, run and literal prefix renamed.
a9 = item(old_parent, "fn positive9(composed: bool)")
run9 = item(old_parent, "fn run9(")
assert "<u8 as UnstableSmallSortTypeImpl>::small_sort(v, cmp);" in run9
assert 'kani::assert(canonical(*cmp), "netcomp N9: canonical comparator unchanged");' in run9
assert "fn netcomp_direct_u8_n9() {\n    positive9(false);\n}" in old_parent
byte_diff = {}
for n in (10, 13):
    new = item(source, f"fn direct_u8_n{n}()")
    want = (a9.replace("fn positive9(composed: bool)", f"#[kani::proof]\n#[kani::unwind(25)]\nfn direct_u8_n{n}()")
              .replace("[u8; 9]", f"[u8; {n}]")
              .replace("run9(&mut v, probe, &mut cmp, composed);", f"run{n}(&mut v, &mut cmp);")
              .replace('"netcomp N9: ', f'"directbounds N{n}: ')
              .replace("while i < 9 {", f"while i < {n} {{"))
    assert new == want, n
    byte_diff[f"direct_u8_n{n}"] = list(difflib.unified_diff(
        a9.splitlines(), new.splitlines(), "A9 positive9 @f23d7f2354", f"direct_u8_n{n}", n=0, lineterm=""))
    run = item(source, f"fn run{n}(")
    want_run = (f"fn run{n}(v: &mut [u8; {n}], cmp: &mut U8Cmp) {{\n"
                "    <u8 as UnstableSmallSortTypeImpl>::small_sort(v, cmp);\n"
                f'    kani::assert(canonical(*cmp), "directbounds N{n}: canonical comparator unchanged");\n'
                "}\n")
    assert run.endswith(want_run), n
    byte_diff[f"run{n}"] = list(difflib.unified_diff(
        run9.splitlines(), want_run.splitlines(), "A9 run9 @f23d7f2354", f"run{n}", n=0, lineterm=""))

    neg = item(source, f"fn count_negative_u8_n{n}()")
    order = [f"let mut v = [0u8; {n}];", "let probe = 0u8;", f"run{n}(&mut v, &mut cmp);",
             f'"directbounds N{n} negative: sorted before corruption"',
             f'"directbounds N{n} negative: count before corruption"',
             f'kani::cover(true, "directbounds N{n} negative: sort returned before corruption");',
             f"v[{n - 1}] = 1;",
             f'"directbounds N{n} negative: sorted after corruption"',
             f'kani::cover(true, "directbounds N{n} negative: corrupted count check reached");',
             f'"directbounds negative: count n{n}"']
    pos = [neg.index(s) for s in order]
    assert pos == sorted(pos), (n, pos)
    assert neg.rstrip().endswith(f'"directbounds negative: count n{n}",\n    );\n}}')

# Literal uniqueness: each expect_check occurs exactly once and is no substring of another literal.
literals = re.findall(r'"([^"\n]*)"', source)
for n in (10, 13):
    needle = f"directbounds negative: count n{n}"
    assert [s for s in literals if needle in s] == [needle]
covers = re.findall(r'kani::cover\([^"]*"([^"]+)"\)', source)
assert len(covers) == 12

spec = importlib.util.spec_from_file_location("inventory", HERE.parent / "cleanup/source_inventory.py")
inv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inv)
ordinary, files = inv.inventory(False)
controls, _ = inv.inventory(True)
expected = (HERE.parent / "integwrapfix/ordinary-expected.txt").read_text().splitlines()
assert [r["name"] for r in ordinary] == sorted(expected) and len(ordinary) == 200
prefix = inv.PREFIX + "network::netcomp::directbounds::"
base_controls = json.loads((HERE / "cfg-on-base.json").read_text())
assert len(base_controls) == 395
assert sorted(r["name"] for r in controls) == sorted(base_controls + [prefix + n for n in ROOTS])
assert len(controls) == 399

request_text = (HERE / "g1.request.json").read_text()
assert (HERE / "g1.request.json").read_bytes() == (HERE.parent / "RUN-REQUEST.json").read_bytes()
request = json.loads(request_text)
assert [r["name"] for r in request["harnesses"]] == [prefix + n for n in ROOTS]
assert [r["expect"] for r in request["harnesses"]] == ["SUCCESS", "SUCCESS", "FAILED", "FAILED"]
assert [r.get("expect_check") for r in request["harnesses"]][2:] == [
    "directbounds negative: count n10", "directbounds negative: count n13"]
assert request["request_id"].startswith("directbounds-") and request["agent"] == "k1-network"
assert request["runner"] == "gcb-e2-standard-4" and request["kind"] == "measurement"
assert request["controls"] is True and request["kani_jobs"] == 1 and request["uninit_checks"] is False
assert request["harness_timeout_minutes"] == 10

dependencies = ["library/core/src/slice/sort/shared/smallsort.rs",
                "library/core/src/slice/sort/shared/smallsort/verify/network.rs",
                "library/core/src/slice/sort/shared/smallsort/verify/merge/specfix.rs"] + LANE[4:7]
report = dict(status="PASS", base=BASE, tooling_base=TOOL_BASE, ordinary_exact=200,
              controls_exact=399, controls_base=395, added=[prefix + n for n in ROOTS],
              parent_change="exact appended cfg-gated registration only",
              annotations=annotations, a9_byte_diff=byte_diff,
              source_sha256=sha(source), parent_sha256=sha(parent),
              request_sha256=sha(request_text),
              dependency_sha256={p: sha((ROOT / p).read_text()) for p in dependencies},
              scope="Static source/packet checks only; compile, proof and covers NOT_RUN before GO.")
(HERE / "static-check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items()
                  if k not in ["annotations", "dependency_sha256", "a9_byte_diff", "added"]}, indent=2))
