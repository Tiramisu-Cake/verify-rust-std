#!/usr/bin/env python3
"""Static packet checks only. Does not invoke Rust, Kani, CBMC or a build."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PACKET = Path(__file__).resolve().parent
BASE = "708b3a6661"
TOOLING_BASE = "59893bff1fbb2af1a0c08862afd7e3bb87c19cdd"
VERIFY = "library/core/src/slice/sort/shared/smallsort/verify.rs"
MODULE = "library/core/src/slice/sort/shared/smallsort/verify/looppin.rs"
RUNTIME = "library/core/src/slice/sort/shared/smallsort.rs"
LANES = [
    ".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
    "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh", "tool_config/kani-version.toml",
    "rust-toolchain.toml", ".gitmodules", ".cargo", "library/.cargo", "library/Cargo.toml",
    "library/Cargo.lock",
]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    sys.path.insert(0, str(ROOT / "research/challenge-8/kani-k1/tools"))
    import kani_k1

    request_bytes = (PACKET / "request.json").read_bytes()
    assert request_bytes == (PACKET.parent / "RUN-REQUEST.json").read_bytes()
    request = kani_k1.validate_request(json.loads(request_bytes))
    assert request["agent"] == "k1-network"
    assert request["request_id"].startswith("looppin-")
    assert request["kind"] == "diagnostic" and request["controls"] is True
    assert request["runner"] == "gcb-e2-standard-4" and request["kani_jobs"] == 1
    assert request["harness_timeout_minutes"] == 3

    registration = b"#[cfg(kani_smallsort_controls)] mod looppin;\n"
    verify = (ROOT / VERIFY).read_bytes()
    assert verify.count(registration) == 1
    assert verify.replace(registration, b"") == git("show", f"{BASE}:{VERIFY}")
    source = (ROOT / MODULE).read_text()
    roots = [name for attrs, name in re.findall(
        r"(?m)^((?:#\[[^\n]+\]\n)+)fn (\w+)\(", source
    ) if "#[kani::proof]" in attrs or "#[kani::proof_for_contract(" in attrs]
    prefix = "slice::sort::shared::smallsort::verify::looppin::"
    assert len(roots) == 4
    assert {prefix + name for name in roots} == {h["name"] for h in request["harnesses"]}
    reference = json.loads((PACKET / "pinned-doc-reference.json").read_text())
    negative = [h for h in request["harnesses"] if h["expect"] == "FAILED"]
    assert len(negative) == 1
    assert negative[0]["expect_check"] == reference["invariant_step_description_prefix"]
    assert (ROOT / RUNTIME).read_bytes() == git("show", f"{BASE}:{RUNTIME}")
    assert git("diff", "--name-only", TOOLING_BASE, "--", *LANES) == b""
    tracked_library_changes = set(git("diff", "--name-only", BASE, "--", "library").decode().splitlines())
    assert tracked_library_changes <= {VERIFY, MODULE}
    untracked_library = set(git("ls-files", "--others", "--exclude-standard", "library").decode().splitlines())
    assert untracked_library <= {MODULE}
    ledger = json.loads((PACKET / "RUN-LEDGER.json").read_text())
    assert ledger["request_sha256"] == sha256(request_bytes)
    minutes = len(roots) * request["harness_timeout_minutes"] + 30
    reserve = round(minutes * 0.0135, 4)
    assert minutes == ledger["build_timeout_minutes"] == 42
    assert reserve == ledger["maximum_reservation_usd"] == 0.567
    assert reserve * 2 <= ledger["own_cap_usd"]
    report = {
        "status": "PASS_STATIC_ONLY",
        "task_base": git("rev-parse", BASE).decode().strip(),
        "tooling_base": TOOLING_BASE,
        "request_sha256": sha256(request_bytes),
        "library_sha256": {p: sha256((ROOT / p).read_bytes()) for p in (VERIFY, MODULE, RUNTIME)},
        "roots": roots,
        "controls_registration": "single added line; existing verify.rs bytes otherwise identical",
        "runtime_and_lane_files": "unchanged",
        "build_timeout_minutes": minutes,
        "maximum_reservation_usd": reserve,
        "limitations": "No compilation, cfg inventory, actual check text, covers or proof result established.",
    }
    (PACKET / "check-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
