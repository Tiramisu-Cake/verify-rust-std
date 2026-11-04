#!/usr/bin/env python3
"""Source-only v7/v8 comparison. No compiler, Kani or CBMC is invoked.

Reuses the lexer, item splitter, macro expander and conservative closure from
120e443536's check_trimpart.py (copied verbatim as trimpart_static.py).
Run from this worktree: python3 -B research/challenge-8/kani-k1/codefix/check_codefix.py
"""
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("trimpart_static", HERE / "trimpart_static.py")
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
V7 = "e470652790"
TOOLING_BASE = "59893bff1f"
NEW = {"network::swap_same_position_u8", "network::unstable_freeze_noncopy_bytes86_fallback_n2"}
LANES = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
         "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh", "tool_config/kani-version.toml",
         "rust-toolchain.toml", ".gitmodules", ".cargo", "library/.cargo", "library/Cargo.toml",
         "library/Cargo.lock"]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=s.REPO, text=True).strip()


def main():
    old, new = s.Source(V7), s.Source(None)
    o, n = old.roots(False), new.roots(False)
    c, d = old.roots(True), new.roots(True)
    changes = [name for name, (_, it) in c.items()
               if name not in d or it.text() != d[name][1].text()]
    retained_changes, removed = [], []
    old_items, new_items = s.item_map(old), s.item_map(new)
    for key, items in old_items.items():
        if key[1] in ("inner_attr", "inner_doc"):
            continue
        if key not in new_items:
            removed.append(":".join(key))
        elif sorted(it.text() for it in items) != sorted(it.text() for it in new_items[key]):
            retained_changes.append(":".join(key))
    orphan_checks = {str(cfg): s.orphans(new, cfg) for cfg in (False, True)}
    changed_library = git("diff", "--name-only", V7, "--", "library").splitlines()
    outside = [f for f in changed_library
               if f != s.VERIFY_ROOT and not f.startswith(s.VERIFY_DIR)]
    long_lines = [f"{f}:{i}:{len(line)}" for f, text in new.files.items()
                  for i, line in enumerate(text.splitlines(), 1) if len(line) > 100]
    lane_diff = git("diff", "--name-only", TOOLING_BASE, "--", *LANES)
    diff_check = subprocess.run(["git", "diff", "--check"], cwd=s.REPO, capture_output=True)
    checks = {
        "ordinary_202_plus_2": len(o) == 202 and len(n) == 204 and set(n) == set(o) | NEW,
        "controls_unchanged_8": set(d) - set(n) == set(c) - set(o) == set(s.CONTROLS),
        "old_210_roots_token_identical": not changes,
        "all_retained_helpers_token_identical": not retained_changes and not removed,
        "cfg_off_and_on_no_static_orphans": not any(any(parts) for parts in orphan_checks.values()),
        "library_diff_only_verify": not outside,
        "tooling_equals_59893bff1f": not lane_diff,
        "line_width_100": not long_lines,
        "git_diff_check": diff_check.returncode == 0,
    }
    report = {
        "status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
        "v7": git("rev-parse", V7), "tooling_base": git("rev-parse", TOOLING_BASE),
        "ordinary_before": len(o), "ordinary_after": len(n), "new_roots": sorted(NEW),
        "controls": sorted(set(d) - set(n)), "root_changes": changes,
        "retained_helper_changes": retained_changes, "removed_helpers": removed,
        "static_orphans": orphan_checks, "outside_verify": outside,
        "lane_diff": lane_diff, "long_lines": long_lines,
        "verify_lines_before": sum(len(t.splitlines()) for t in old.files.values()),
        "verify_lines_after": sum(len(t.splitlines()) for t in new.files.values()),
        "verify_sha256": {f: hashlib.sha256(t.encode()).hexdigest() for f, t in new.files.items()},
        "limitations": "Source macro expansion and conservative name closure, not compiler inventory. "
                        "ArbitraryValue impls also audited against concrete generic instantiations. "
                        "Compile/warning checks for cfg-off and cfg-on await the authorized GCB build.",
    }
    (HERE / "check-report.json").write_text(json.dumps(report, indent=2) + "\n")
    (HERE / "ordinary-expected.txt").write_text("".join(s.PREFIX + name + "\n" for name in sorted(n)))
    (HERE / "controls-expected.txt").write_text("".join(s.PREFIX + name + "\n" for name in sorted(set(d) - set(n))))
    print(json.dumps({"status": report["status"], "checks": checks,
                      "lines_before": report["verify_lines_before"],
                      "lines_after": report["verify_lines_after"]}, indent=2))
    return int(report["status"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())
