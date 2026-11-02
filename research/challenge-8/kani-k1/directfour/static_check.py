"""DIRECTFOUR source/packet checks only. Does not run a compiler or verifier."""
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = "8505b3b2882cf2e18f0b7771b54f4239135ccfd5"  # TASK-DIRECTFOUR staging commit on MERGESTEP.
BASE_LIBRARY_TREE = "dc7c79bb9b2a779a6db2977f6142adfea835441b"
BASE_LIBRARY_COMMIT = "91d4d9f77a5a6e7f27b151839e6ac42114523a89"
VERIFY = "library/core/src/slice/sort/shared/smallsort/verify/"
PARENT = VERIFY + "network/netcomp/mergestep.rs"
MODULE = VERIFY + "network/netcomp/mergestep/directfour.rs"
TOOL_BASE = "30f77e859903df14b442ff9294d4fbbd44827f20"
LANE = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
        "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh", "tool_config/kani-version.toml",
        "rust-toolchain.toml", ".gitmodules", ".cargo", "library/.cargo", "library/Cargo.toml",
        "library/Cargo.lock"]
REGISTRATION = ("\n// DIRECTFOUR direct merge4 baseline without step substitutions: child module after"
                " all above.\nmod directfour;\n")
PREFIX_MOD = "network::netcomp::mergestep::directfour::"
NAME = "directfour_merge4_u8"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def sha(data):
    return hashlib.sha256(data.encode()).hexdigest()


assert git("rev-parse", f"{BASE}:library").strip() == BASE_LIBRARY_TREE
assert git("rev-parse", f"{BASE_LIBRARY_COMMIT}:library").strip() == BASE_LIBRARY_TREE
# Library change: exactly the new child file plus the trailing registration in mergestep.rs.
assert sorted(git("diff", "--name-only", BASE, "--", "library").splitlines()) == [PARENT, MODULE]
parent_old = git("show", f"{BASE}:{PARENT}")
assert (ROOT / PARENT).read_text() == parent_old + REGISTRATION
assert not git("diff", TOOL_BASE, "--", *LANE)
for unchanged in ["library/core/src/slice/sort/shared/smallsort.rs", VERIFY + "network.rs",
                  VERIFY + "network/netcomp.rs", VERIFY + "merge/specfix.rs",
                  VERIFY + "network/netcomp/neteighteen.rs"]:
    assert (ROOT / unchanged).read_text() == git("show", f"{BASE}:{unchanged}"), unchanged

source = (ROOT / MODULE).read_text()
code = "\n".join(l.split("//")[0] for l in source.splitlines())  # comments/doc removed
for banned in ["kani::stub", "stub_verified", "kani::assume", "#[cfg(", "pub ", "pub(", "static ",
               "STEP_CONTEXT", "adapter", "up_step_u8", "down_step_u8", "merge_up", "merge_down",
               "bidirectional_merge(", "inline", "unsafe fn", "impl "]:
    assert banned not in code, banned
assert max(map(len, source.splitlines())) <= 100
assert re.findall(r"^\s*fn (\w+)", source, re.M) == [NAME]
assert source.count("#[kani::") == 2
want = ["#[kani::proof_for_contract(super::super::super::super::merge::specfix::merge_profile)]",
        "#[kani::unwind(34)]"]
pos = source.index("fn " + NAME + "()")
annotations = re.findall(r"#\[kani::[^\n]+", source[:pos])
assert annotations == want, annotations
body = source[pos:source.index("\n}\n", pos)]

# Fixture lines, call and post-oracle: byte-identical statements to the MERGESTEP composed root.
old_root = parent_old[parent_old.index("fn mergestep_composed_merge4_u8()"):]
old_root = old_root[:old_root.index("\n}\n")]
stmts = lambda b: [l.strip() for l in b.splitlines()[1:]
                   if l.strip() and not l.strip().startswith("//")]
old_stmts = [s for s in stmts(old_root) if not s.startswith("kani::cover(")]
new_stmts = [s for s in stmts(body) if not s.startswith("kani::cover(")]
assert old_stmts == new_stmts, (old_stmts, new_stmts)
cover_re = r'kani::cover\(([^"]*), "([^"]+)"\);'
old_cov = re.findall(cover_re, old_root)
new_cov = re.findall(cover_re, body)
assert [p for p, _ in old_cov] == [p for p, _ in new_cov] and len(new_cov) == 6
assert [l.replace("mergestep ", "directfour ", 1) for _, l in old_cov] == [l for _, l in new_cov]
# Cover positions relative to the oracle are unchanged (returned before check_merge4, rest after).
order = lambda b: [("C" if s.startswith("kani::cover(") else s) for s in stmts(b)]
assert order(old_root) == order(body)
assert body.index("StrictU8::set_probe(kani::any())") < body.index("let src: [u8; 18] = kani::any();")
assert body.index("register(") < body.index("merge_profile::<StrictU8>(&src[..ACTIVE4], dst, cmp)")
assert body.index("merge_profile::<StrictU8>(") < body.index("check_merge4(")

# Existing ordinary set and cfg-on composition.
spec = importlib.util.spec_from_file_location("inventory", HERE.parent / "cleanup/source_inventory.py")
inv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inv)
ordinary, _ = inv.inventory(False)
controls, _ = inv.inventory(True)
expected = (HERE.parent / "integwrapfix/ordinary-expected.txt").read_text().splitlines()
assert [r["name"] for r in ordinary] == sorted(expected) and len(ordinary) == 200
prefix = inv.PREFIX + PREFIX_MOD
new = sorted(r["name"] for r in controls if r["name"].startswith(prefix))
assert new == [prefix + NAME], new
assert len(controls) == 405, len(controls)
old_mergestep = sorted(r["name"] for r in controls
                       if r["name"].startswith(inv.PREFIX + "network::netcomp::mergestep::")
                       and not r["name"].startswith(prefix))
assert len(old_mergestep) == 6, old_mergestep

request = json.loads((HERE / "g1.request.json").read_text())
assert (HERE / "g1.request.json").read_bytes() == (HERE.parent / "RUN-REQUEST.json").read_bytes()
assert request["harnesses"] == [{"name": prefix + NAME, "expect": "SUCCESS"}]
assert request["request_id"].startswith("directfour-") and request["agent"] == "k1-network"
assert request["kind"] == "measurement" and request["controls"] is True
assert request["kani_jobs"] == 1 and request["uninit_checks"] is False
assert request["harness_timeout_minutes"] == 10
assert request["runner"] == "gcb-e2-standard-4"

dependencies = ["library/core/src/slice/sort/shared/smallsort.rs", VERIFY + "network.rs",
                VERIFY + "network/netcomp.rs", PARENT, MODULE, VERIFY + "merge/specfix.rs",
                "library/core/src/ub_checks.rs"] + LANE[4:7]
report = dict(status="PASS", base=BASE, base_library_tree=BASE_LIBRARY_TREE,
              library_tree=git("rev-parse", "HEAD:library").strip(),
              ordinary_exact=200, controls_exact=405, added=1, annotations={NAME: annotations},
              covers=[l for _, l in new_cov], oracle_statements_equal_mergestep_composed=True,
              mergestep_rs_change="trailing child-module registration only",
              runtime_specfix_network_netcomp_neteighteen_tooling_unchanged=True,
              source_sha256=sha(source), request_sha256=sha((HERE / "g1.request.json").read_text()),
              dependency_sha256={p: sha((ROOT / p).read_text()) for p in dependencies},
              scope="Static source/packet checks only; compile, proof and covers NOT_RUN before GO.")
(HERE / "static-check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k not in ["annotations", "dependency_sha256"]},
                 indent=2))
