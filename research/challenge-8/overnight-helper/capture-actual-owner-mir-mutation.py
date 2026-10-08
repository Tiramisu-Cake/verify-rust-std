#!/usr/bin/env python3
"""Hosted-only direct typed-MIR negatives for O21 actual-owner admission.

The real exporter, source, readonly export and refinement remain unchanged.
Only a disposable shadow console sees a one-field Cap'n Proto mutation.
No result from this test-tool profile can count as a positive proof.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
from types import SimpleNamespace


HERE = Path(__file__).resolve().parent


def load():
    import importlib.util
    import sys
    path = HERE / "prepare-actual-owner-linked.py"
    spec = importlib.util.spec_from_file_location("actual_owner_mir_preparer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing linked owner source preparer: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PREP = load()
REPO = PREP.REPO
MUTATIONS = ("forget_move_to_copy", "forget_cleanup_to_bb22",
             "nested_ghost_span_line")
SOURCE_SHA256 = "595e93c5c08ebd61a6ab4b7f7b98ed2f2d6765dbb8d903509a53391ea9a2b5b3"
EXPECTED_FATAL = (
    'Fatal error: exception Failure("SORT4-SELECT-INTRINSIC: '
    'certificate mismatch: owner complete decoded unit SHA256")')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(ok: bool, why: str) -> None:
    PREP.OWNER.require(ok, why)


def replace_once(source: str, before: str, after: str, label: str) -> str:
    require(source.count(before) == 1,
            f"{label}: expected exactly one targeted MIR field, found {source.count(before)}")
    return source.replace(before, after, 1)


def selected_body(decoded: str, def_path: str) -> tuple[int, int, str]:
    marker = f'defPath = "{def_path}"'
    require(decoded.count(marker) == 1,
            f"selected exact MIR body not unique: {def_path}")
    at = decoded.index(marker)
    lead = decoded.rfind("    ( defKind =", 0, at)
    require(lead >= 0, "selected MIR body opening missing")
    opening = decoded.index("(", lead)
    body = PREP.LINK.CONSTRUCTOR.mir_balanced_item(decoded, opening)
    return opening, opening + len(body), body


def mutate_actual_mir(decoded: str, mutation: str) -> str:
    require(mutation in MUTATIONS, "unknown direct actual-owner MIR mutation")
    if mutation == "nested_ghost_span_line":
        opening, tail, body = selected_body(
            decoded,
            "<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop")
        lo = body.index("      basicBlocks = [")
        hi = body.index("\n      span = (", lo)
        blocks = body[lo:hi]
        marker = "( id = (index = 0),"
        require(blocks.count(marker) == 1,
                "qualified nested ghost bb0 not unique")
        start = blocks.index(marker)
        old_block = PREP.LINK.CONSTRUCTOR.mir_balanced_item(
            blocks, blocks.index("(", start))
        require(old_block.count('name = "VeriFast_ghost_command"') == 1,
                "qualified nested first typed ghost call absent")
        term_at = old_block.index("terminator = (") + len("terminator = ")
        old_term = PREP.LINK.CONSTRUCTOR.mir_balanced_item(old_block, term_at)
        source_lo = old_term.index("sourceInfo = (")
        source_hi = old_term.index("kind = (", source_lo)
        source_info = old_term[source_lo:source_hi]
        line_lo = source_info.index("lo = (")
        line_hi = source_info.index("hi = (", line_lo)
        lo_record = source_info[line_lo:line_hi]
        lo_record = replace_once(lo_record, "line = 95,", "line = 94,",
                                 mutation)
        source_info = (source_info[:line_lo] + lo_record +
                       source_info[line_hi:])
        term = old_term[:source_lo] + source_info + old_term[source_hi:]
        block = old_block[:term_at] + term + old_block[term_at + len(old_term):]
        blocks = blocks[:start] + block + blocks[start + len(old_block):]
        body = body[:lo] + blocks + body[hi:]
        require(body != decoded[opening:tail],
                "nested ghost span mutation had no effect")
        return decoded[:opening] + body + decoded[tail:]
    opening, tail, body = selected_body(decoded, "select_unpredictable")
    lo = body.index("      basicBlocks = [")
    hi = body.index("\n      span = (", lo)
    blocks = body[lo:hi]
    marker = "( id = (index = 16),"
    require(blocks.count(marker) == 1, "actual forget bb16 not unique")
    start = blocks.index(marker)
    block = PREP.LINK.CONSTRUCTOR.mir_balanced_item(
        blocks, blocks.index("(", start))
    require(block.count('name = "std::mem::forget"') == 1,
            "bb16 exact forget callee absent")
    call_start = block.index("call = (") + len("call = ")
    call = PREP.LINK.CONSTRUCTOR.mir_balanced_item(block, call_start)
    if mutation == "forget_move_to_copy":
        arg_lo = call.index("args = [")
        arg_hi = call.index("destination = (", arg_lo)
        args = call[arg_lo:arg_hi]
        require(args.count('local = (name = "_34")') == 1 and
                'projection = []' in args and
                'localIsMutable = true' in args,
                "forget operand is not exact plain Move(_34)")
        args = replace_once(args, "args = [\n                  ( move = (",
                            "args = [\n                  ( copy = (", mutation)
        call = call[:arg_lo] + args + call[arg_hi:]
    else:
        call = replace_once(
            call, "unwindAction = (cleanup = (index = 23))",
            "unwindAction = (cleanup = (index = 22))", mutation)
        require("target = (something = (index = 17))" in call,
                "forget normal successor changed")
    original_call = PREP.LINK.CONSTRUCTOR.mir_balanced_item(block, call_start)
    block = block[:call_start] + call + block[call_start + len(original_call):]
    blocks = blocks[:start] + block + blocks[start + len(
        PREP.LINK.CONSTRUCTOR.mir_balanced_item(blocks, blocks.index("(", start))):]
    body = body[:lo] + blocks + body[hi:]
    require(body != decoded[opening:tail], "direct MIR mutation had no effect")
    return decoded[:opening] + body + decoded[tail:]


def make_shadow(tool_home: Path, schema: Path, case: Path,
                mutation: str, source_sha: str) -> Path:
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
spec = importlib.util.spec_from_file_location("actual_owner_mir_mutant", @PREPARER@)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
real, schema = @REAL@, @SCHEMA@
mutation, source_sha = @MUTATION@, @SOURCE_SHA@
record = Path(@RECORD@)
argv = sys.argv[1:]
proc = subprocess.run([real, *argv], stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE, check=False)
sys.stderr.buffer.write(proc.stderr)
if proc.returncode:
    sys.stdout.buffer.write(proc.stdout)
    raise SystemExit(proc.returncode)
selected = any(Path(arg).suffix == ".rs" and Path(arg).is_file() and
               hashlib.sha256(Path(arg).read_bytes()).hexdigest() == source_sha
               for arg in argv)
if not selected:
    sys.stdout.buffer.write(proc.stdout)
    raise SystemExit(0)
decoded = subprocess.run(["capnp", "decode", schema, "VfMir"], input=proc.stdout,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
if decoded.returncode:
    sys.stderr.buffer.write(decoded.stderr)
    raise SystemExit(decoded.returncode)
try:
    canonical = decoded.stdout.decode()
    changed = module.mutate_actual_mir(canonical, mutation)
except Exception as exc:
    record.write_text(json.dumps({"mutation": mutation, "error": str(exc)}) + "\\n")
    sys.stderr.write("ACTUAL OWNER MIR mutant setup failed: " + str(exc) + "\\n")
    raise SystemExit(98)
encoded = subprocess.run(["capnp", "encode", schema, "VfMir"],
                         input=changed.encode(), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, check=False)
if encoded.returncode:
    sys.stderr.buffer.write(encoded.stderr)
    raise SystemExit(encoded.returncode)
record.parent.mkdir(parents=True, exist_ok=True)
(record.parent / "canonical-mir.txt").write_text(canonical)
(record.parent / "mutated-mir.txt").write_text(changed)
(record.parent / "canonical-mir.bin").write_bytes(proc.stdout)
(record.parent / "mutated-mir.bin").write_bytes(encoded.stdout)
record.write_text(json.dumps({"mutation": mutation, "matched": True,
    "exporter_exit": proc.returncode, "decode_exit": decoded.returncode,
    "encode_exit": encoded.returncode, "selected_source_sha256": source_sha,
    "canonical_sha256": hashlib.sha256(proc.stdout).hexdigest(),
    "mutated_sha256": hashlib.sha256(encoded.stdout).hexdigest(),
    "real_exporter_sha256": hashlib.sha256(Path(real).read_bytes()).hexdigest()},
    sort_keys=True, indent=2) + "\\n")
sys.stdout.buffer.write(encoded.stdout)
'''.replace("@PREPARER@", repr(str(HERE / "capture-actual-owner-mir-mutation.py")))
   .replace("@REAL@", repr(str(source_bin / "vf-rust-mir-exporter")))
   .replace("@SCHEMA@", repr(str(schema.resolve())))
   .replace("@MUTATION@", repr(mutation))
   .replace("@SOURCE_SHA@", repr(source_sha))
   .replace("@RECORD@", repr(str(case / "mutation-record.json"))))
    wrapper.chmod(0o755)
    shutil.copy2(wrapper, case / "mir-exporter-wrapper.py")
    PREP.LINK.LINK.write_json(case / "mutation-profile.json", {
        "mutation": mutation,
        "base_console_sha256": sha((source_bin / "verifast").read_bytes()),
        "shadow_console_sha256": sha((binary / "verifast").read_bytes()),
        "real_exporter_sha256": sha((source_bin / "vf-rust-mir-exporter").read_bytes()),
        "wrapper_sha256": sha(wrapper.read_bytes()),
    })
    return shadow


def run_case(case: Path, args, shadow: Path) -> dict:
    exporter = str(args.tool_home / "bin/vf-rust-mir-exporter")
    stages = {}
    stages["normal-export"] = PREP.LINK.stage(case, "normal-export", [
        exporter, "verified/lib.rs", f"--sysroot={args.compiler_sysroot}",
        "--edition", "2021"], args, output_name="normal-mir.bin")
    stages["readonly-export"] = PREP.LINK.stage(case, "readonly-export", [
        exporter, "verified/lib.rs", f"--sysroot={args.compiler_sysroot}",
        "--edition", "2021", "--crate-type", "lib",
        "--vf-rust-mir-exporter:preprocess-readonly"], args,
        output_name="readonly-mir.bin")
    for mode in ("normal", "readonly"):
        if stages[f"{mode}-export"]["exit"] == 0:
            stages[f"{mode}-decode"] = PREP.LINK.stage(case, f"{mode}-decode", [
                "capnp", "decode", str(args.schema), "VfMir"], args,
                input_name=f"{mode}-mir.bin", output_name=f"{mode}-mir.txt",
                cap_seconds=40)
    if all(stages.get(k, {}).get("exit") == 0 for k in (
            "normal-export", "normal-decode", "readonly-export", "readonly-decode")):
        stages["refinement"] = PREP.LINK.stage(case, "refinement", [
            str(args.tool_home / "bin/refinement-checker"), "--rustc-args",
            "--edition 2021", "original/lib.rs", "verified/lib.rs"], args,
            cap_seconds=70)
        shadow_args = SimpleNamespace(**vars(args))
        shadow_args.tool_home = shadow
        stages["full-verification"] = PREP.LINK.stage(case, "full-verification", [
            str(shadow / "bin/verifast"), "-rustc_args", "--edition 2021",
            "-verbose", "1", "verified/lib.rs"], shadow_args,
            gates=True, pointer_drop=True, cap_seconds=100)
    return stages


def classify(case: Path, mutation: str, stages: dict) -> dict:
    complete = all(stages.get(k, {}).get("exit") == 0 for k in (
        "normal-export", "normal-decode", "readonly-export",
        "readonly-decode", "refinement"))
    intact = all(s.get("source_unchanged") is True
                 for s in stages.values() if s.get("status") == "RAN")
    log_path = case / "full-verification.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    fatal = [line for line in log.splitlines() if line.startswith("Fatal error:")]
    errors = PREP.LINK.LINK.ERR.findall(log)
    record_path = case / "mutation-record.json"
    profile_path = case / "mutation-profile.json"
    files = [case / name for name in (
        "canonical-mir.txt", "mutated-mir.txt", "canonical-mir.bin",
        "mutated-mir.bin", "mir-exporter-wrapper.py")]
    exact = False
    record = None
    if record_path.is_file() and profile_path.is_file() and all(p.is_file() for p in files):
        record = json.loads(record_path.read_text())
        profile = json.loads(profile_path.read_text())
        try:
            exact = mutate_actual_mir(files[0].read_text(), mutation) == files[1].read_text()
        except (ValueError, IndexError):
            exact = False
        exact = exact and all((
            record.get("matched") is True,
            record.get("mutation") == mutation,
            record.get("exporter_exit") == 0,
            record.get("decode_exit") == 0,
            record.get("encode_exit") == 0,
            record.get("selected_source_sha256") == SOURCE_SHA256,
            sha((case / "verified/lib.rs").read_bytes()) == SOURCE_SHA256,
            record.get("canonical_sha256") == sha(files[2].read_bytes()),
            record.get("mutated_sha256") == sha(files[3].read_bytes()),
            files[2].read_bytes() != files[3].read_bytes(),
            record.get("real_exporter_sha256") == profile.get("real_exporter_sha256"),
            profile.get("base_console_sha256") == profile.get("shadow_console_sha256"),
            profile.get("wrapper_sha256") == sha(files[4].read_bytes()),
        ))
    refused = (complete and intact and exact and
               stages.get("full-verification", {}).get("exit") == 2 and
               len(fatal) == 1 and fatal[0] == EXPECTED_FATAL and not errors and
               "SORT4-ACTUAL-OWNER: exact source and complete decoded MIR admission only"
               not in log and
               "Verifying function 'select_unpredictable'" not in log)
    paired_export_byte_equal = (
        record is not None and (case / "normal-mir.bin").is_file() and
        record.get("canonical_sha256") ==
          sha((case / "normal-mir.bin").read_bytes()))
    result = {
        "mutation": mutation,
        "classification": "EXACT_TYPED_MIR_ADMISSION_REJECTED" if refused else "INCONCLUSIVE",
        "actual_helper_proved": False,
        "test_tool_mutation_profile": True,
        "source_integrity": intact,
        "independent_frontend_refinement": complete,
        "mutant_exact": exact,
        "paired_export_byte_equal": paired_export_byte_equal,
        "expected_reason": "owner complete decoded unit SHA256",
        "full_verifier_exit": stages.get("full-verification", {}).get("exit"),
        "fatal": fatal,
        "first_error": errors[0] if errors else None,
        "mutation_record": record,
        "stages": stages,
    }
    PREP.LINK.LINK.write_json(case / "classification.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--mutations", nargs="+", choices=MUTATIONS,
                        default=list(MUTATIONS))
    args = parser.parse_args()
    require((os.environ.get("GITHUB_ACTIONS"),
             os.environ.get("RUNNER_ENVIRONMENT"),
             os.environ.get("RUNNER_OS")) ==
            ("true", "github-hosted", "Linux"),
            "direct MIR controls require GitHub-hosted Linux")
    evidence = args.evidence.resolve()
    require(not evidence.exists(), f"refusing overwrite: {evidence}")
    evidence.mkdir(parents=True)
    os.environ["SORT4_ACTUAL_OWNER_REPO_ROOT"] = str(REPO)
    os.environ["SORT4_ACTUAL_OWNER_ADMISSION"] = "1"
    results = []
    for mutation in args.mutations:
        out = evidence / mutation
        PREP.write_case(REPO, out)
        case = out / "linked-owner"
        verified = (case / "verified/lib.rs").read_bytes()
        require(sha(verified) == SOURCE_SHA256 and
                PREP.OWNER.strip_ghost(verified) ==
                    (case / "original/lib.rs").read_bytes(),
                "direct MIR control source certificate changed")
        shadow = make_shadow(args.tool_home, args.schema, case,
                             mutation, SOURCE_SHA256)
        results.append(classify(case, mutation, run_case(case, args, shadow)))
    PREP.LINK.LINK.write_json(evidence / "summary.json", {
        "classification": "ACTUAL_OWNER_TYPED_MIR_TEST_MUTATIONS_ONLY",
        "actual_helper_proved": False,
        "mutations": results,
    })
    print(json.dumps({"mutations": [
        {"mutation": row["mutation"], "classification": row["classification"],
         "fatal": row["fatal"]} for row in results]}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
