#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted admission controls for exact actual projection ghost coordinates.

Only a single exported ghost-coordinate field changes in each case. The
verified/original Rust sources and runtime typed MIR graph stay identical.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil


PROFILE = "experimental-source-linked-select-pointer-drop-v2"
MUTATIONS = ("regular_hi", "explicit_end")
EXPECTED = {
    "regular_hi": "actual projection ghost source span",
    "explicit_end": "actual projection ghost explicit coordinates",
}
FIRST_RAW = (
    '//@ std::mem::open_MaybeUninit::<*Element>'
    '(true_ptr as *std::mem::MaybeUninit<*Element>);'
)
PREFIX = 'SORT4-SELECT-INTRINSIC: certificate mismatch: '


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def mutate_actual_ghost_mir(decoded: str, mutation: str, constructor) -> str:
    require(mutation in MUTATIONS, "unknown actual ghost coordinate mutant")
    marker = 'defPath = "select_unpredictable"'
    require(decoded.count(marker) == 1, "actual MIR body not unique")
    at = decoded.index(marker)
    lead = decoded.rfind("    ( defKind =", 0, at)
    require(lead >= 0, "actual MIR body opening missing")
    opening = decoded.index("(", lead)
    body = constructor.mir_balanced_item(decoded, opening)
    head = 'ghostStmts = ['
    require(body.count(head) == 1, "actual ghost list not unique")
    first = body.index(head) + len(head)
    annotation_start = body.index("(", first)
    annotation = constructor.mir_balanced_item(body, annotation_start)
    require(annotation.count('raw = "' + FIRST_RAW + '"') == 1 and
            'startLine = 40,' in annotation and
            'startCol = 5,' in annotation and
            'endLine = 40,' in annotation and
            'endCol = 94' in annotation,
            "first exact projection ghost identity/coordinates changed")
    hi = annotation.index('hi = (')
    high = re.search(r'col = \(pos = (\d+)\)', annotation[hi:])
    require(high is not None and high.group(1) == '92',
            "first regular ghost hi changed")
    if mutation == "regular_hi":
        start = hi + high.start(1)
        end = hi + high.end(1)
        changed = annotation[:start] + "93" + annotation[end:]
    else:
        end_marker = 'endCol = 94'
        require(annotation.count(end_marker) == 1,
                "first explicit ghost end changed")
        changed = annotation.replace(end_marker, 'endCol = 93', 1)
    require(changed != annotation, "actual ghost mutant had no effect")
    body = body[:annotation_start] + changed + body[annotation_start + len(annotation):]
    return decoded[:opening] + body + decoded[opening + len(constructor.mir_balanced_item(decoded, opening)):]


def make_mutation_tool_home(tool_home: Path, schema: Path, repo: Path,
                            case: Path, mutation: str) -> Path:
    require(mutation in MUTATIONS, "unknown actual ghost mutation")
    shadow = case / "mutation-profile"
    binary = shadow / "bin"
    binary.mkdir(parents=True)
    source_bin = tool_home / "bin"
    for entry in source_bin.iterdir():
        if entry.name == "vf-rust-mir-exporter":
            continue
        target = binary / entry.name
        if entry.name == "verifast" and entry.is_file():
            shutil.copy2(entry, target)
        else:
            target.symlink_to(entry, target_is_directory=entry.is_dir())
    wrapper = binary / "vf-rust-mir-exporter"
    wrapper.write_text('''#!/usr/bin/env python3
import hashlib, importlib.util, json, subprocess, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("sort4_actual_ghost_mutant", @MUTATOR@)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ctor_spec = importlib.util.spec_from_file_location("sort4_actual_ghost_ctor", @CONSTRUCTOR@)
constructor = importlib.util.module_from_spec(ctor_spec)
ctor_spec.loader.exec_module(constructor)
real = @REAL@
schema = @SCHEMA@
mutation = @MUTATION@
record = Path(@RECORD@)
argv = sys.argv[1:]
proc = subprocess.run([real, *argv], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
sys.stderr.buffer.write(proc.stderr)
if proc.returncode:
    sys.stdout.buffer.write(proc.stdout)
    raise SystemExit(proc.returncode)
decoded = subprocess.run(["capnp", "decode", schema, "VfMir"], input=proc.stdout,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
if decoded.returncode:
    sys.stderr.buffer.write(decoded.stderr)
    raise SystemExit(decoded.returncode)
try:
    canonical = decoded.stdout.decode()
    changed = module.mutate_actual_ghost_mir(canonical, mutation, constructor)
except Exception as exc:
    record.write_text(json.dumps({"mutation": mutation, "error": str(exc)}) + "\\n")
    sys.stderr.write("SORT4-ACTUAL-GHOST MIR mutant failed: " + str(exc) + "\\n")
    raise SystemExit(98)
encoded = subprocess.run(["capnp", "encode", schema, "VfMir"], input=changed.encode(),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
if encoded.returncode:
    sys.stderr.buffer.write(encoded.stderr)
    raise SystemExit(encoded.returncode)
record.parent.mkdir(parents=True, exist_ok=True)
(record.parent / "canonical-mir.txt").write_text(canonical)
(record.parent / "mutated-mir.txt").write_text(changed)
(record.parent / "canonical-mir.bin").write_bytes(proc.stdout)
(record.parent / "mutated-mir.bin").write_bytes(encoded.stdout)
selected = next((Path(arg) for arg in argv if Path(arg).suffix == ".rs" and Path(arg).is_file()), None)
record.write_text(json.dumps({"mutation": mutation, "matched": True,
    "exporter_exit": proc.returncode, "decode_exit": decoded.returncode,
    "encode_exit": encoded.returncode,
    "canonical_sha256": hashlib.sha256(proc.stdout).hexdigest(),
    "mutated_sha256": hashlib.sha256(encoded.stdout).hexdigest(),
    "selected_source_sha256": hashlib.sha256(selected.read_bytes()).hexdigest() if selected else None,
    "real_exporter_sha256": hashlib.sha256(Path(real).read_bytes()).hexdigest()},
    indent=2, sort_keys=True) + "\\n")
sys.stdout.buffer.write(encoded.stdout)
'''.replace("@MUTATOR@", repr(str(repo / "research/challenge-8/check-pointer-drop-actual-ghosts.py")))
   .replace("@CONSTRUCTOR@", repr(str(repo / "research/challenge-8/check-maybeuninit-new-pointer.py")))
   .replace("@REAL@", repr(str(source_bin / "vf-rust-mir-exporter")))
   .replace("@SCHEMA@", repr(str(schema)))
   .replace("@MUTATION@", repr(mutation))
   .replace("@RECORD@", repr(str(case / "mutation-record.json"))))
    wrapper.chmod(0o755)
    shutil.copy2(wrapper, case / "mir-exporter-wrapper.py")
    (case / "mutation-profile.json").write_text(json.dumps({
        "mutation": mutation,
        "base_console_sha256": sha((source_bin / "verifast").read_bytes()),
        "shadow_console_sha256": sha((binary / "verifast").read_bytes()),
        "real_exporter_sha256": sha((source_bin / "vf-rust-mir-exporter").read_bytes()),
        "wrapper_sha256": sha(wrapper.read_bytes()),
    }, indent=2, sort_keys=True) + "\n")
    return shadow


def classify(case: Path, runner: dict, canonical: Path, mutation: str,
             constructor) -> dict:
    require(mutation in MUTATIONS, "unknown actual ghost mutation")
    verified = (case / "verified/lib.rs").read_bytes()
    original = (case / "original/lib.rs").read_bytes()
    fixture = json.loads((case / "fixture.json").read_text())
    log = (case / "verifast.log").read_text(errors="replace")
    fatal = [line for line in log.splitlines() if "Fatal error:" in line]
    expected = PREFIX + EXPECTED[mutation]
    stage = runner.get("stage_integrity", {})
    integrity = set(stage) == {"exporter", "decode", "verifast", "refinement"} and \
        all(item.get("unchanged") is True for item in stage.values())
    frontend = runner.get("exporter_exit") == 0 and \
        runner.get("decode_exit") == 0 and runner.get("refinement_exit") == 0
    source_exact = (verified == (canonical / "verified/lib.rs").read_bytes() and
        original == (canonical / "original/lib.rs").read_bytes() and
        constructor.strip_ghost_annotations(verified) == original and
        fixture.get("final_original_sha256") == sha(original) and
        fixture.get("final_verified_sha256") == sha(verified) and
        fixture.get("projection_ghosts_exact") is True and
        fixture.get("tool_profile") == PROFILE)
    record_path = case / "mutation-record.json"
    profile_path = case / "mutation-profile.json"
    files = tuple(case / name for name in (
        "canonical-mir.txt", "mutated-mir.txt", "canonical-mir.bin", "mutated-mir.bin"))
    record = json.loads(record_path.read_text()) if record_path.exists() else None
    profile = json.loads(profile_path.read_text()) if profile_path.exists() else None
    mutant_exact = False
    if record is not None and profile is not None and all(path.exists() for path in files):
        canonical_text, mutated_text = files[0].read_text(), files[1].read_text()
        canonical_bin, mutated_bin = files[2].read_bytes(), files[3].read_bytes()
        try:
            exact_text = mutate_actual_ghost_mir(canonical_text, mutation,
                                                  constructor) == mutated_text
        except ValueError:
            exact_text = False
        mutant_exact = (exact_text and record.get("mutation") == mutation and
            record.get("matched") is True and
            record.get("exporter_exit") == 0 and
            record.get("decode_exit") == 0 and record.get("encode_exit") == 0 and
            record.get("canonical_sha256") == sha(canonical_bin) and
            record.get("mutated_sha256") == sha(mutated_bin) and
            canonical_bin != mutated_bin and
            record.get("selected_source_sha256") == sha(verified) and
            record.get("real_exporter_sha256") == profile.get("real_exporter_sha256") and
            profile.get("base_console_sha256") == profile.get("shadow_console_sha256") and
            profile.get("wrapper_sha256") == sha(
                (case / "mutation-profile/bin/vf-rust-mir-exporter").read_bytes()))
    before_proof = "Verifying function 'select_unpredictable'" not in log and \
        "SORT4-SELECT-INTRINSIC: full typed actual MIR graph accepted" not in log
    evidence = {
        "source_exact": bool(source_exact),
        "stage_integrity": bool(integrity),
        "frontend_refinement": bool(frontend),
        "mutant_exact": bool(mutant_exact),
        "exact_fatal": (len(fatal) == 1 and
            fatal[0] == f'Fatal error: exception Failure("{expected}")' and
            not any(": error:" in line for line in log.splitlines())),
        "before_proof": bool(before_proof),
        "verifier_exit_two": runner.get("verifast_exit") == 2,
    }
    accepted = all(value is True for value in evidence.values())
    result = {
        "mutation": mutation,
        "classification": "INTENDED_ADMISSION_REJECTION" if accepted else "INCONCLUSIVE",
        "accepted_component": False,
        "expected_obligation": expected,
        "admission_evidence": evidence,
        "fatal": fatal,
        "mutation_record": record,
        "runner_result": runner,
    }
    (case / "admission-classification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def run_controls(projected: Path, args, repo: Path, constructor,
                 evidence: Path) -> dict:
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux" and
            os.environ.get("SORT4_SELECT_PROFILE") == PROFILE,
            "actual ghost controls require exact hosted v2 profile")
    evidence.mkdir(parents=True, exist_ok=False)
    results = []
    for mutation in MUTATIONS:
        case = evidence / f"ghost_{mutation}"
        try:
            shutil.copytree(projected, case)
            home = make_mutation_tool_home(args.tool_home, args.schema, repo,
                                           case, mutation)
            runner = constructor.run_case(
                case, args.schema, home, args.compiler_sysroot,
                repo, case.name, "diagnostic", certificate_mode=True)
            result = classify(case, runner, projected, mutation, constructor)
        except Exception as exc:
            case.mkdir(parents=True, exist_ok=True)
            result = {"mutation": mutation, "classification": "INCONCLUSIVE",
                      "accepted_component": False,
                      "harness_exception": f"{type(exc).__name__}: {exc}"}
            (case / "admission-classification.json").write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n")
        results.append(result)
    accepted = len(results) == len(MUTATIONS) and all(
        result["classification"] == "INTENDED_ADMISSION_REJECTION"
        for result in results)
    summary = {"classification": "ADMISSION_CONTROLS_ACCEPTED" if accepted else
               "INCONCLUSIVE", "accepted_controls": accepted,
               "tool_profile": PROFILE, "source_variant": projected.name,
               "cases": results, "full_select_proved": False}
    (evidence / "summary.json").write_text(json.dumps(summary, indent=2,
        sort_keys=True) + "\n")
    return summary
