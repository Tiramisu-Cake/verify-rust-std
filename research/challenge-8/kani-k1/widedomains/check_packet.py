#!/usr/bin/env python3
"""Source-only WIDEDOMAINS packet checks. Never invokes a Rust compiler/prover."""
import hashlib
import importlib.util
import json
import subprocess
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = "34f69f034b"
G1 = "90fadd7ccf8b5bb32d04401d274a6f492b612897"
G2 = "4fbe77cf46cd416fb6140a54bf6c9ffb78479d3c"
spec = importlib.util.spec_from_file_location(
    "static_source", HERE.parent / "codefix/trimpart_static.py")
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def main():
    old, new = s.Source(BASE), s.Source(None)
    g1 = s.Source(G1)
    g2 = s.Source(G2)
    old_off, old_on = old.roots(False), old.roots(True)
    off, on = new.roots(False), new.roots(True)
    added = set(on) - set(old_on)
    g3_added = set(on) - set(g2.roots(True))
    module = s.VERIFY_DIR + "widedomains.rs"
    g1_functions = {it.name: it.text() for f, it in g1.all_items()
                    if f == module and it.kind == "fn"}
    current_functions = {it.name: it.text() for f, it in new.all_items()
                         if f == module and it.kind == "fn"}
    changed_g1_functions = [name for name, text in g1_functions.items()
                            if current_functions.get(name) != text]
    g2_functions = {it.name: it.text() for f, it in g2.all_items()
                    if f == module and it.kind == "fn"}
    changed_g2_functions = [name for name, text in g2_functions.items()
                            if current_functions.get(name) != text]
    changed_old = [f for f, text in old.files.items()
                   if f != s.VERIFY_ROOT and new.files.get(f) != text]
    expected_registration = old.files[s.VERIFY_ROOT].replace(
        "mod wrap;", "#[cfg(kani_smallsort_controls)]\nmod widedomains;\nmod wrap;")
    changed_library = set(git("diff", "--name-only", BASE, "--", "library").splitlines())
    changed_library.update(git("ls-files", "--others", "--exclude-standard",
                               "--", "library").splitlines())
    lanes = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
             "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh",
             "tool_config/kani-version.toml", "rust-toolchain.toml", ".gitmodules",
             ".cargo", "library/.cargo", "library/Cargo.toml", "library/Cargo.lock"]
    lane_diff = git("diff", "--name-only", "59893bff1f", "--", *lanes)
    request_bytes = (HERE.parent / "RUN-REQUEST.json").read_bytes()
    request = json.loads(request_bytes)
    covers = json.loads((HERE / "expected-covers.json").read_text())
    ledger = json.loads((HERE / "RUN-LEDGER.json").read_text())
    names = {entry["name"] for entry in request["harnesses"]}
    orphans = {str(cfg): s.orphans(new, cfg) for cfg in (False, True)}
    runtime = s.REPO / s.SMALLSORT
    runtime_before = subprocess.check_output(["git", "show", BASE + ":" + s.SMALLSORT])
    long_lines = [i for i, line in enumerate(new.files[module].splitlines(), 1)
                  if len(line) > 100]
    checks = {
        "ordinary_219_unchanged": len(off) == len(old_off) == 219 and set(off) == set(old_off),
        "cfg_on_253_plus_30": len(old_on) == 253 and len(on) == 283 and len(added) == 30,
        "all_g1_functions_unchanged": not changed_g1_functions,
        "g2_273_plus_10_roots_and_all_g2_functions_unchanged":
            len(g2.roots(True)) == 273 and len(g3_added) == 10 and not changed_g2_functions,
        "all_added_roots_in_gated_module": all(
            name.startswith("widedomains::") and on[name][0] == module for name in added)
            and new.file_gate[module],
        "existing_verify_files_byte_identical": not changed_old,
        "only_one_gated_module_registration": new.files[s.VERIFY_ROOT] == expected_registration,
        "runtime_contracts_byte_identical": runtime.read_bytes() == runtime_before,
        "library_scope_exact": changed_library == {s.VERIFY_ROOT, module},
        "tooling_equals_59893bff1f": not lane_diff,
        "no_static_orphans_both_cfgs": not any(any(parts) for parts in orphans.values()),
        "request_exactly_g3_roots": names == {s.PREFIX + n for n in g3_added},
        "diagnostic_controls_jobs1_standard4_4minutes": (
            request["kind"] == "diagnostic" and request["controls"] is True
            and request["kani_jobs"] == 1 and request["runner"] == "gcb-e2-standard-4"
            and request["agent"] == "k1-merge" and request["harness_timeout_minutes"] == 4
            and request["inventory"] is False),
        "ten_success_expectations": len(request["harnesses"]) == 10
            and all(entry["expect"] == "SUCCESS" for entry in request["harnesses"]),
        "covers_exact_77": set(covers) == names and sum(covers.values()) == 77,
        "request_hash_matches_ledger": hashlib.sha256(request_bytes).hexdigest()
            == ledger["request_sha256"],
        "reservation_70min_0945usd": ledger["build_timeout_minutes"] == 70
            and Decimal(str(ledger["maximum_reservation_usd"]))
            == (10 * 4 + 30) * Decimal("0.0135")
            and ledger["spent_usd"] + ledger["maximum_reservation_usd"] <= 4.0,
        "line_width_100": not long_lines,
        "git_diff_check": subprocess.run(["git", "diff", "--check"],
                                         capture_output=True).returncode == 0,
    }
    report = dict(status="PASS" if all(checks.values()) else "FAIL", checks=checks,
                  base=git("rev-parse", BASE), tooling_base=git("rev-parse", "59893bff1f"),
                  ordinary_count=len(off), cfg_on_count=len(on), new_roots=sorted(added),
                  g3_roots=sorted(g3_added), changed_g1_functions=changed_g1_functions,
                  changed_g2_functions=changed_g2_functions,
                  source_sha256=hashlib.sha256(new.files[module].encode()).hexdigest(),
                  request_sha256=hashlib.sha256(request_bytes).hexdigest(),
                  changed_old_files=changed_old, tooling_diff=lane_diff,
                  static_orphans=orphans, long_lines=long_lines,
                  limitations="Source parsing only; no compiler inventory is requested. "
                              "G3 proof, cover reachability, timing and memory require GCB. "
                              "G1/G2 evidence is preserved separately under g1/ and g2/.")
    (HERE / "check-report.json").write_text(json.dumps(report, indent=2) + "\n")
    for filename, roots in (("ordinary-expected.txt", off), ("cfg-on-expected.txt", on)):
        (HERE / filename).write_text("".join(s.PREFIX + n + "\n" for n in sorted(roots)))
    print(json.dumps(dict(status=report["status"], checks=checks), indent=2))
    return int(report["status"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())
