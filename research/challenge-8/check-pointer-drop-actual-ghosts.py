#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Independent hosted NORMAL-MIR admissions for the exact S6 projection.

The readonly exporter output used for refinement passes through unchanged.
Each case mutates one field of the second, normal exporter invocation before
VeriFast translates the actual helper. No case is a proof of that helper.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil


PROFILE = "experimental-source-linked-select-pointer-drop-v4"
EXPORTER_SHA = "2b8ebb5373d0bdd82cc163f5a298a4291b89dcdb8630a01bf74149987f2d5e0c"
READONLY_BIN_SHA = "1f374757a362d0c8ef8bab6ebc9d870b56ce3ae5a4df5b4ac50deba1d949459c"
READONLY_TEXT_SHA = "b70408ccb36582cda9ebeadf9e13ac70eea4aee7633e893b9466ee24b151baad"
NORMAL_BIN_SHA = "1594bc4e9e5209d1cde39a5f10d8c3e2b08dbb332c895d90ee15179b7d8679f1"
NORMAL_TEXT_SHA = "0d9c5fee619879da01fe988f9ed72c19f704cdd490b7b4daa1f91947b9f1a0a8"
FIRST_RAW = ('//@ std::mem::open_MaybeUninit::<*Element>'
             '(true_ptr as *std::mem::MaybeUninit<*Element>);')
PREFIX = "SORT4-SELECT-INTRINSIC: certificate mismatch: "
EXPECTED = {
    "regular_hi": "actual projection ghost source span",
    "explicit_end": "actual projection ghost explicit coordinates",
    "ghost_callee": "actual typed callee identity",
    "ghost_args": "actual call arity",
    "ghost_substs": "actual typed callee identity",
    "ghost_unit_type": "actual projected local identity/type: _12",
    "ghost_destination": "actual terminator place: _12",
    "ghost_normal_target": "actual normal target: 5",
    "ghost_unwind": "actual unwind action/target",
    "ghost_call_span": "actual projected ghost call span",
    "ghost_missing": "actual full basic-block count",
    "ghost_extra": "actual full basic-block count",
    "drop_operand": "actual terminator place: _26",
    "drop_old_receiver": "actual terminator place: _26",
    "drop_callee": "actual typed callee identity",
    "drop_cleanup": "actual unwind action/target",
    "final_return": "actual projected return terminator",
    "cleanup_successor": "actual projected cleanup drop successor",
    "cleanup_switch": "actual projected drop-flag switch values/targets",
}
MUTATIONS = tuple(EXPECTED)


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def one_replace(text: str, old: str, new: str, where: str) -> str:
    require(text.count(old) == 1, f"{where}: expected one exact field")
    return text.replace(old, new, 1)


def bracketed(text: str, at: int) -> str:
    require(text[at] == "[", "bracketed MIR list missing")
    depth = 0
    quoted = False
    escaped = False
    for i in range(at, len(text)):
        ch = text[i]
        if quoted:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                quoted = False
        elif ch == '"':
            quoted = True
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return text[at:i + 1]
    raise ValueError("unterminated MIR list")


def actual_body(decoded: str, constructor) -> tuple[int, str]:
    marker = 'defPath = "select_unpredictable"'
    require(decoded.count(marker) == 1, "actual normal MIR body not unique")
    at = decoded.index(marker)
    lead = decoded.rfind("    ( defKind =", 0, at)
    require(lead >= 0, "actual normal MIR body opening missing")
    opening = decoded.index("(", lead)
    body = constructor.mir_balanced_item(decoded, opening)
    require(body.count("localDecls = [") == 1 and
            body.count("basicBlocks = [") == 1 and
            body.count("ghostStmts = [") == 1,
            "actual normal MIR graph sections differ")
    return opening, body


def block_item(body: str, number: int, constructor) -> tuple[int, str]:
    start = body.index("basicBlocks = [")
    end = body.index("ghostStmts = [", start)
    span = body[start:end]
    matches = list(re.finditer(r'^        \( id = \(index = (\d+)\)', span, re.M))
    ids = [int(match.group(1)) for match in matches]
    require(ids == list(range(19)), "canonical normal block indices differ")
    match = matches[number]
    opening = start + match.start() + match.group(0).index("(")
    return opening, constructor.mir_balanced_item(body, opening)


def local_item(body: str, number: int, constructor) -> tuple[int, str]:
    start = body.index("localDecls = [")
    end = body.index("basicBlocks = [", start)
    span = body[start:end]
    matches = list(re.finditer(
        r'^        \( mutability = \([^\n]+\),\n          id = \(name = "_(\d+)"\)',
        span, re.M))
    require([int(match.group(1)) for match in matches] == list(range(36)),
            "canonical normal local indices differ")
    match = matches[number]
    opening = start + match.start() + match.group(0).index("(")
    return opening, constructor.mir_balanced_item(body, opening)


def replace_item(body: str, opening: int, original: str, changed: str) -> str:
    require(changed != original, "normal MIR mutation had no effect")
    return body[:opening] + changed + body[opening + len(original):]


def replace_block(body: str, number: int, old: str, new: str,
                  constructor) -> str:
    opening, item = block_item(body, number, constructor)
    return replace_item(body, opening, item,
                        one_replace(item, old, new, f"block {number}"))


def replace_call_part(body: str, number: int, field: str, old: str,
                      new: str, constructor) -> str:
    opening, item = block_item(body, number, constructor)
    term = item.split("terminator = (", 1)[1]
    marker = field + " = "
    require(term.count(marker) == 1, f"block {number}: {field} not unique")
    field_at = item.index(marker, item.index("terminator = (")) + len(marker)
    require(item[field_at] == "(", f"block {number}: {field} not a record")
    record = constructor.mir_balanced_item(item, field_at)
    changed_record = one_replace(record, old, new, f"block {number} {field}")
    changed = item[:field_at] + changed_record + item[field_at + len(record):]
    return replace_item(body, opening, item, changed)


def mutate_actual_ghost_mir(decoded: str, mutation: str, constructor) -> str:
    require(mutation in MUTATIONS, "unknown S6 normal admission mutation")
    require(sha(decoded.encode()) == NORMAL_TEXT_SHA,
            "canonical stock NORMAL MIR differs from pinned diagnostic")
    opening, body = actual_body(decoded, constructor)
    if mutation in ("regular_hi", "explicit_end"):
        first = body.index("ghostStmts = [") + len("ghostStmts = [")
        start = body.index("(", first)
        item = constructor.mir_balanced_item(body, start)
        require(item.count('raw = "' + FIRST_RAW + '"') == 1 and
                "startLine = 40," in item and "startCol = 5," in item and
                "endLine = 40," in item and "endCol = 94" in item,
                "canonical first ghost source identity differs")
        if mutation == "regular_hi":
            hi = item.index("hi = (")
            match = re.search(r'col = \(pos = (\d+)\)', item[hi:])
            require(match is not None and match.group(1) == "124",
                    "canonical NORMAL regular ghost hi differs")
            start_hi = hi + match.start(1)
            end_hi = hi + match.end(1)
            changed = item[:start_hi] + "125" + item[end_hi:]
        else:
            changed = one_replace(item, "endCol = 94", "endCol = 93",
                                  "first explicit ghost end")
        body = replace_item(body, start, item, changed)
    elif mutation == "ghost_unit_type":
        start, item = local_item(body, 12, constructor)
        changed = one_replace(item, "ty = (kind = (tuple = []))",
                              "ty = (kind = (bool = void))", "ghost unit type")
        body = replace_item(body, start, item, changed)
    elif mutation == "ghost_missing":
        start, item = block_item(body, 4, constructor)
        next_start, _ = block_item(body, 5, constructor)
        require(body[start + len(item):next_start].strip() == ",",
                "ghost block separator differs")
        body = body[:start] + body[next_start:]
    elif mutation == "ghost_extra":
        start, item = block_item(body, 4, constructor)
        extra = one_replace(item, "id = (index = 4)", "id = (index = 19)",
                            "extra ghost block index")
        last_start, last = block_item(body, 18, constructor)
        at = last_start + len(last)
        body = body[:at] + ",\n" + extra + body[at:]
    elif mutation == "ghost_callee":
        body = replace_block(body, 4, 'name = "VeriFast_ghost_command"',
                             'name = "VeriFast_ghost_command_wrong"', constructor)
    elif mutation == "ghost_substs":
        _, first = block_item(body, 0, constructor)
        term = first.split("terminator = (", 1)[1]
        at = term.index("substs = [") + len("substs = ")
        real_substs = bracketed(term, at)
        require(real_substs != "[]", "constructor type substitution absent")
        body = replace_block(body, 4, "substs = []",
                             "substs = " + real_substs, constructor)
    elif mutation == "ghost_args":
        _, drop = block_item(body, 9, constructor)
        term = drop.split("terminator = (", 1)[1]
        at = term.index("args = [") + len("args = [")
        operand_at = term.index("(", at)
        operand = constructor.mir_balanced_item(term, operand_at)
        body = replace_block(body, 4, "args = []", "args = [" + operand + "]",
                             constructor)
    elif mutation == "ghost_destination":
        body = replace_call_part(body, 4, "destination", 'name = "_12"',
                                 'name = "_13"', constructor)
    elif mutation == "ghost_normal_target":
        body = replace_block(body, 4, "target = (something = (index = 5))",
                             "target = (something = (index = 6))", constructor)
    elif mutation == "ghost_unwind":
        body = replace_block(body, 8, "unwindAction = (cleanup = (index = 18))",
                             "unwindAction = (continue = void)", constructor)
    elif mutation == "ghost_call_span":
        body = replace_call_part(body, 4, "callSpan", "col = (pos = 35)",
                                 "col = (pos = 36)", constructor)
    elif mutation == "drop_operand":
        _, item = block_item(body, 9, constructor)
        term = item.split("terminator = (", 1)[1]
        at = term.index("args = [") + len("args = [")
        operand_at = term.index("(", at)
        operand = constructor.mir_balanced_item(term, operand_at)
        require(operand.count('name = "_26"') == 1,
                "canonical drop operand differs")
        body = replace_block(body, 9, operand,
                             operand.replace('name = "_26"', 'name = "_18"', 1),
                             constructor)
    elif mutation == "drop_old_receiver":
        _, item = block_item(body, 9, constructor)
        term = item.split("terminator = (", 1)[1]
        at = term.index("args = [") + len("args = [")
        operand_at = term.index("(", at)
        operand = constructor.mir_balanced_item(term, operand_at)
        require(operand.count('name = "_26"') == 1,
                "canonical drop receiver differs")
        body = replace_block(body, 9, operand,
                             operand.replace('name = "_26"', 'name = "_23"', 1),
                             constructor)
    elif mutation == "drop_callee":
        body = replace_block(body, 9,
            'name = "std::ptr::mut_ptr::<impl *mut T>::drop_in_place"',
            'name = "std::mem::forget"', constructor)
    elif mutation == "drop_cleanup":
        body = replace_block(body, 9, "unwindAction = (cleanup = (index = 18))",
                             "unwindAction = (continue = void)", constructor)
    elif mutation == "final_return":
        body = replace_block(body, 15, "kind = (return = void)",
                             "kind = (unwindResume = void)", constructor)
    elif mutation == "cleanup_successor":
        body = replace_block(body, 17, "target = (index = 16)",
                             "target = (index = 15)", constructor)
    elif mutation == "cleanup_switch":
        body = replace_block(body, 18,
            "targets = [(index = 16), (index = 17)]",
            "targets = [(index = 16), (index = 16)]", constructor)
    return decoded[:opening] + body + decoded[opening + len(constructor.mir_balanced_item(decoded, opening)):]


def make_mutation_tool_home(tool_home: Path, schema: Path, repo: Path,
                            case: Path, mutation: str) -> Path:
    require(mutation in MUTATIONS, "unknown normal admission mutation")
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
selected = next((Path(arg) for arg in argv if Path(arg).suffix == ".rs" and Path(arg).is_file()), None)
source_sha = hashlib.sha256(selected.read_bytes()).hexdigest() if selected else None
if "--vf-rust-mir-exporter:preprocess-readonly" in argv:
    (record.parent / "readonly-mode.json").write_text(json.dumps({
        "mode": "preprocess-readonly", "argv": argv,
        "canonical_sha256": hashlib.sha256(proc.stdout).hexdigest(),
        "selected_source_sha256": source_sha,
        "real_exporter_sha256": hashlib.sha256(Path(real).read_bytes()).hexdigest()},
        indent=2, sort_keys=True) + "\\n")
    sys.stdout.buffer.write(proc.stdout)
    raise SystemExit(0)
decoded = subprocess.run(["capnp", "decode", schema, "VfMir"], input=proc.stdout,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
if decoded.returncode:
    sys.stderr.buffer.write(decoded.stderr)
    raise SystemExit(decoded.returncode)
canonical = decoded.stdout.decode()
(record.parent / "canonical-normal-mir.txt").write_text(canonical)
(record.parent / "canonical-normal-mir.bin").write_bytes(proc.stdout)
try:
    changed = module.mutate_actual_ghost_mir(canonical, mutation, constructor)
except Exception as exc:
    record.write_text(json.dumps({"mode": "normal", "mutation": mutation,
        "error": str(exc), "canonical_sha256": hashlib.sha256(proc.stdout).hexdigest()}) + "\\n")
    sys.stderr.write("SORT4-ACTUAL-NORMAL MIR mutant failed: " + str(exc) + "\\n")
    raise SystemExit(98)
encoded = subprocess.run(["capnp", "encode", schema, "VfMir"], input=changed.encode(),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
if encoded.returncode:
    sys.stderr.buffer.write(encoded.stderr)
    raise SystemExit(encoded.returncode)
(record.parent / "mutated-normal-mir.txt").write_text(changed)
(record.parent / "mutated-normal-mir.bin").write_bytes(encoded.stdout)
record.write_text(json.dumps({"mode": "normal", "mutation": mutation,
    "argv": argv, "matched": True,
    "exporter_exit": proc.returncode, "decode_exit": decoded.returncode,
    "encode_exit": encoded.returncode,
    "canonical_bin_sha256": hashlib.sha256(proc.stdout).hexdigest(),
    "canonical_text_sha256": hashlib.sha256(decoded.stdout).hexdigest(),
    "mutated_bin_sha256": hashlib.sha256(encoded.stdout).hexdigest(),
    "mutated_text_sha256": hashlib.sha256(changed.encode()).hexdigest(),
    "selected_source_sha256": source_sha,
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
    verified = (case / "verified/lib.rs").read_bytes()
    original = (case / "original/lib.rs").read_bytes()
    fixture = json.loads((case / "fixture.json").read_text())
    log = (case / "verifast.log").read_text(errors="replace")
    fatal = [line for line in log.splitlines() if line.startswith("Fatal error:")]
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
    readonly_path = case / "readonly-mode.json"
    profile_path = case / "mutation-profile.json"
    names = ("canonical-normal-mir.txt", "mutated-normal-mir.txt",
             "canonical-normal-mir.bin", "mutated-normal-mir.bin")
    files = tuple(case / name for name in names)
    record = json.loads(record_path.read_text()) if record_path.exists() else None
    readonly = json.loads(readonly_path.read_text()) if readonly_path.exists() else None
    profile = json.loads(profile_path.read_text()) if profile_path.exists() else None
    readonly_bin = (case / "compiler-mir.bin").read_bytes()
    readonly_text = (case / "compiler-mir.txt").read_bytes()
    readonly_exact = bool(readonly and profile and
        readonly.get("mode") == "preprocess-readonly" and
        "--vf-rust-mir-exporter:preprocess-readonly" in readonly.get("argv", []) and
        readonly.get("canonical_sha256") == READONLY_BIN_SHA and
        sha(readonly_bin) == READONLY_BIN_SHA and
        sha(readonly_text) == READONLY_TEXT_SHA and
        readonly.get("selected_source_sha256") == sha(verified) and
        readonly.get("real_exporter_sha256") == EXPORTER_SHA ==
            profile.get("real_exporter_sha256"))
    normal_exact = False
    if record and profile and all(path.exists() for path in files):
        canonical_text, changed_text = files[0].read_text(), files[1].read_text()
        canonical_bin, changed_bin = files[2].read_bytes(), files[3].read_bytes()
        try:
            exact_text = mutate_actual_ghost_mir(canonical_text, mutation,
                                                  constructor) == changed_text
        except ValueError:
            exact_text = False
        normal_exact = bool(exact_text and record.get("mode") == "normal" and
            record.get("mutation") == mutation and record.get("matched") is True and
            record.get("exporter_exit") == 0 and record.get("decode_exit") == 0 and
            record.get("encode_exit") == 0 and
            record.get("canonical_bin_sha256") == NORMAL_BIN_SHA and
            record.get("canonical_text_sha256") == NORMAL_TEXT_SHA and
            sha(canonical_bin) == NORMAL_BIN_SHA and
            sha(canonical_text.encode()) == NORMAL_TEXT_SHA and
            record.get("mutated_bin_sha256") == sha(changed_bin) and
            record.get("mutated_text_sha256") == sha(changed_text.encode()) and
            canonical_bin != changed_bin and canonical_text != changed_text and
            record.get("selected_source_sha256") == sha(verified) and
            "--vf-rust-mir-exporter:preprocess-readonly" not in record.get("argv", []) and
            profile.get("base_console_sha256") == profile.get("shadow_console_sha256") and
            record.get("real_exporter_sha256") == profile.get("real_exporter_sha256") and
            record.get("real_exporter_sha256") == EXPORTER_SHA and
            profile.get("wrapper_sha256") == sha(
                (case / "mutation-profile/bin/vf-rust-mir-exporter").read_bytes()))
    before_proof = "Verifying function 'select_unpredictable'" not in log and \
        "SORT4-SELECT-INTRINSIC: full typed actual MIR graph accepted" not in log
    evidence = {
        "source_exact": bool(source_exact),
        "stage_integrity": bool(integrity),
        "readonly_export_refinement": bool(frontend and readonly_exact),
        "normal_only_mutant_exact": bool(normal_exact),
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
        "readonly_record": readonly,
        "normal_mutation_record": record,
        "runner_result": runner,
    }
    (case / "admission-classification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def run_controls(projected: Path, args, repo: Path, constructor,
                 evidence: Path, imported_coordinates: list[dict] | None = None) -> dict:
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux" and
            os.environ.get("SORT4_SELECT_PROFILE") == PROFILE,
            "actual NORMAL controls require exact hosted v3 profile")
    evidence.mkdir(parents=True, exist_ok=False)
    imported_coordinates = imported_coordinates or []
    if imported_coordinates:
        require(len(imported_coordinates) == 2 and
                [item.get("mutation") for item in imported_coordinates] ==
                    ["regular_hi", "explicit_end"] and
                all(item.get("classification") == "INTENDED_ADMISSION_REJECTION" and
                    item.get("expected_obligation") == PREFIX + EXPECTED[item["mutation"]] and
                    set(item.get("admission_evidence", {})) == {
                        "source_exact", "stage_integrity", "readonly_export_refinement",
                        "normal_only_mutant_exact", "exact_fatal", "before_proof",
                        "verifier_exit_two"} and
                    all(value is True for value in item["admission_evidence"].values())
                    for item in imported_coordinates),
                "pinned v3 coordinate control evidence differs")
    results = list(imported_coordinates)
    for mutation in MUTATIONS[len(imported_coordinates):]:
        case = evidence / f"normal_{mutation}"
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
    readonly_preserved = len(results) == len(MUTATIONS) and all(
        result.get("admission_evidence", {}).get("readonly_export_refinement") is True
        for result in results)
    summary = {"classification": "ADMISSION_CONTROLS_ACCEPTED" if accepted else
               "INCONCLUSIVE", "accepted_controls": accepted,
               "tool_profile": PROFILE, "source_variant": projected.name,
               "normal_only": True, "readonly_preserved": readonly_preserved,
               "imported_coordinate_controls_source_run":
                   37651717720 if imported_coordinates else None,
               "new_hosted_control_count": len(results) - len(imported_coordinates),
               "cases": results, "full_select_proved": False}
    (evidence / "summary.json").write_text(json.dumps(summary, indent=2,
        sort_keys=True) + "\n")
    return summary
