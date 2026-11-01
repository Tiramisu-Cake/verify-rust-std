#!/usr/bin/env python3
"""Run the standalone Kani repro and preserve outcomes without claiming proofs."""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("GITHUB_WORKSPACE", Path(__file__).resolve().parents[1]))
OUT, CRATE = ROOT / "out", ROOT / "array-select-standalone"
NAMES = [
    "casefive_d1_select_read_bytes1", "casefive_d2_select_read_u8",
    "arrayfactor_f2_if_bytes1", "arrayfactor_f5_symbolic_indices_bytes1",
    "arrayfactor_f7_witness_bytes1", "arrayrepro_w_observed_bytes1",
    "arrayrepro_cover_other_element_bytes1", "arrayrepro_cover_neither_element_bytes1",
]
EXPECTED_COVERS = [2, 2, 2, 4, 2, 2, 1, 1]
TIMEOUT = ["timeout", "--verbose", "--kill-after=10s", "300s"]


def execute(tag: str, args: list[str], cwd: Path = CRATE) -> tuple[int | None, str]:
    command = TIMEOUT + args
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{tag}.command.txt").write_text(f"cwd: {cwd}\ncommand: {shlex.join(command)}\n")
    try:
        result = subprocess.run(command, cwd=cwd, env=os.environ.copy(), text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        rc, output = result.returncode, result.stdout
    except OSError as exc:
        rc, output = None, f"EXECUTION_ERROR: {exc}\n"
    (OUT / f"{tag}.txt").write_text(output, encoding="utf-8", errors="replace")
    (OUT / f"{tag}.rc").write_text(f"{rc if rc is not None else 'EXEC_ERROR'}\n")
    return rc, output


def outcome(rc: int | None, output: str) -> str:
    actual_timeout = re.search(
        r"\b(?:timed out|time limit exceeded)\b|VERIFICATION:- TIMEOUT|^timeout: sending signal",
        output, re.I | re.M,
    )
    if rc == 124 or actual_timeout:
        return "TIMEOUT"
    if rc == 137:
        return "KILLED_OR_TIMEOUT"
    if rc is None:
        return "ERROR"
    if re.search(r"\bpanicked\b|thread .*panicked", output, re.I):
        return "ERROR"
    if re.search(r"unsupported|not supported|does not support|unexpected argument|unrecognized (?:argument|option)", output, re.I):
        return "UNSUPPORTED"
    if re.search(r"(?:^|\n)(?:error|fatal error|ERROR):|driver error|backend error|VERIFICATION:- ERROR", output, re.I):
        return "ERROR"
    if "VERIFICATION:- SUCCESSFUL" in output:
        return "SUCCESSFUL" if rc == 0 else "ERROR"
    if "VERIFICATION:- FAILED" in output:
        return "FAILED" if rc == 1 else "ERROR"
    return "ERROR" if rc != 0 else "MISSING_OUTCOME"


def parse_result(output: str) -> tuple[str, dict[str, int] | None, list[str]]:
    fails = re.findall(r"\*\*\s*(\d+)\s+of\s+(\d+)\s+failed", output, re.I)
    failed_summary = ", ".join(f"{a}/{b}" for a, b in fails) if fails else "MISSING_OUTCOME"
    labels = re.findall(r"Failed Checks?:\s*([^\n]+)", output, re.I)
    covers_match = re.search(r"\*\*\s*(\d+)\s+of\s+(\d+)\s+cover properties satisfied", output, re.I)
    covers = {"satisfied": int(covers_match.group(1)), "total": int(covers_match.group(2))} if covers_match else None
    return failed_summary, covers, labels


def version_summary(name: str) -> tuple[str, str]:
    """Return first version line and its recorded rc, preserving empty output."""
    path, rc_path = OUT / f"{name}-version.txt", OUT / f"{name}-version.rc"
    if not path.exists():
        return "MISSING_OUTCOME", "MISSING_OUTCOME"
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    version = lines[0].strip() if lines and lines[0].strip() else "MISSING_OUTCOME"
    rc = rc_path.read_text(encoding="utf-8", errors="replace").strip() if rc_path.exists() else "MISSING_OUTCOME"
    return version, rc or "MISSING_OUTCOME"


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def tri_state(value: bool | None) -> str:
    if value is None:
        return "UNKNOWN"
    return "ESTABLISHED" if value else "NOT_ESTABLISHED"


def run() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    build = os.environ.get("BUILD_OUTCOME", "unknown")
    (OUT / "build-status.txt").write_text(build + "\n")
    metadata = {}
    if (OUT / "build-metadata.txt").exists():
        metadata = dict(line.split("=", 1) for line in (OUT / "build-metadata.txt").read_text().splitlines() if "=" in line)
    report: dict[str, object] = {
        "build_outcome": build,
        "expected_kani_sha": os.environ.get("KANI_EXPECTED_SHA"),
        "actual_kani_sha": metadata.get("sha"),
        "kani_toolchain": metadata.get("toolchain"),
        "runs": {},
    }
    summary = [
        f"## Array-select repro — {os.environ.get('KANI_LABEL', 'unknown')}", "",
        f"Build: **{build}**; Kani expected SHA `{report['expected_kani_sha']}`, actual SHA `{report['actual_kani_sha']}`; "
        f"toolchain `{report['kani_toolchain']}`. A green report job means collection completed, not proof success.", "",
    ]
    kani = Path(os.environ.get("KANI_ROOT", "")) / "scripts/cargo-kani"
    toolchain = metadata.get("toolchain") or os.environ.get("KANI_TOOLCHAIN", "")
    tags = [f"harness-{name}" for name in NAMES] + ["d1-minisat", "playback-d1", "playback-w"]
    if build == "success" and kani.is_file() and toolchain:
        os.environ["RUSTUP_TOOLCHAIN"] = toolchain
        execute("kani-version", [str(kani), "--version"])
        execute("rustc-version", ["rustc", "--version", "--verbose"])
        execute("kani-help", [str(kani), "--help"])
        help_rc, help_out = execute("playback-help", [str(kani), "-Z", "concrete-playback", "--help"])
        if help_rc is None or help_rc != 0:
            support_state = outcome(help_rc, help_out)
        elif "--concrete-playback" in help_out:
            support_state = "SUPPORTED"
        else:
            support_state = "MISSING_OUTCOME"
        report["playback_cli_support"] = {"rc": help_rc, "status": support_state}
        summary.append(f"Concrete playback CLI support probe: **{support_state}** (rc={help_rc}; details in `playback-help.txt`).")
        # Kani invokes the dependency-installed CBMC through PATH. Resolve the
        # exact same executable under the same environment used by harness runs.
        cbmc = shutil.which("cbmc")
        if cbmc:
            execute("cbmc-version", [cbmc, "--version"])
            (OUT / "cbmc-path.txt").write_text(cbmc + "\n")
        else:
            (OUT / "cbmc-version.txt").write_text("CBMC binary not found in this Kani build\n")
            (OUT / "cbmc-version.rc").write_text("MISSING\n")
        for name in NAMES:
            execute(f"harness-{name}", [str(kani), "--output-format=terse", "--solver", "cadical",
                    "--harness-timeout", "3m", "--jobs=1", "--harness", f"check::{name}", "--exact"])
        execute("d1-minisat", [str(kani), "--output-format=terse", "--solver", "minisat",
                "--harness-timeout", "3m", "--jobs=1", "--harness", f"check::{NAMES[0]}", "--exact"])
        for tag, name in [("playback-d1", NAMES[0]), ("playback-w", NAMES[5])]:
            execute(tag, [str(kani), "-Z", "concrete-playback", "--concrete-playback=print", "--harness",
                    f"check::{name}", "--exact", "--output-format=terse", "--solver", "cadical",
                    "--harness-timeout", "3m", "--jobs=1"])
    else:
        summary.append("Kani was not run: build failed or cargo-kani/toolchain is missing.")

    summary += ["", "| experiment | rc | outcome | failed checks | covers (observed / expected) |",
                "|---|---:|---|---|---:|"]
    for i, tag in enumerate(tags):
        txt, rcfile = OUT / f"{tag}.txt", OUT / f"{tag}.rc"
        if not txt.exists():
            report["runs"][tag] = {"rc": None, "outcome": "MISSING_OUTCOME", "failed_checks": "MISSING_OUTCOME", "covers": None}
            summary.append(f"| {tag} | MISSING | MISSING_OUTCOME | MISSING_OUTCOME | MISSING_OUTCOME |")
            continue
        text = txt.read_text(encoding="utf-8", errors="replace")
        rc_text = rcfile.read_text().strip() if rcfile.exists() else "MISSING"
        rc = int(rc_text) if rc_text.lstrip("-").isdigit() else None
        verdict = outcome(rc, text)
        failed, covers, labels = parse_result(text)
        expected = EXPECTED_COVERS[i] if i < 8 else (2 if i == 8 else "n/a")
        report["runs"][tag] = {"rc": rc_text, "outcome": verdict, "failed_checks": failed,
                               "failed_check_labels": labels,
                               "covers": covers, "expected_covers": expected}
        observed = f"{covers['satisfied']}/{covers['total']}" if covers else "MISSING_OUTCOME"
        failed_display = "; ".join([failed] + [escape_cell(label) for label in labels])
        summary.append(f"| {tag} | {rc_text} | {verdict} | {failed_display} | {observed} / {expected} |")

    summary += ["", "### D1 versus W value assertion", ""]
    states: list[bool | None] = []
    for tag, label in [(f"harness-{NAMES[0]}", "casefive D1: read through the selection"),
                       (f"harness-{NAMES[5]}", "arrayrepro W: read through the selection")]:
        text = (OUT / f"{tag}.txt").read_text(encoding="utf-8", errors="replace") if (OUT / f"{tag}.txt").exists() else ""
        _, _, failed_labels = parse_result(text)
        present = any(label in item for item in failed_labels)
        run_rc = report["runs"].get(tag, {}).get("rc")
        if isinstance(run_rc, str) and run_rc.lstrip("-").isdigit():
            run_rc = int(run_rc)
        verdict = outcome(run_rc, text)
        failed = True if present and verdict == "FAILED" else False if verdict == "SUCCESSFUL" else None
        states.append(failed)
        summary.append(f"- `{tag}` value assertion: **{tri_state(failed)}** (exact failed-check label present: {present}).")
    both_failed = (True if all(x is True for x in states) else
                   False if all(x is not None for x in states) else None)
    report["d1_w_value_failure_comparison"] = {"d1_failed": states[0], "w_failed": states[1],
                                                 "both_failed": both_failed}
    summary.append(f"- W preserves D1 value-assert failure: **{tri_state(both_failed)}**.")
    versions = {}
    for key in ["kani", "rustc", "cbmc"]:
        version, rc = version_summary(key)
        versions[key] = {"version": version, "rc": rc}
        summary.append(f"- {key}: `{escape_cell(version)}` (rc={rc})")
    report["versions"] = versions
    (OUT / "summary.md").write_text("\n".join(summary) + "\n")
    (OUT / "outcomes.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if path := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(path, "a", encoding="utf-8") as stream:
            stream.write("\n".join(summary) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(run())
