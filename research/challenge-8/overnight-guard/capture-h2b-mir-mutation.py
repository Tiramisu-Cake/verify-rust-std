#!/usr/bin/env python3
"""Hosted-only direct typed-MIR admission negatives for local H2b.

This creates a disposable exporter wrapper; it never alters the real exporter,
source fixture, production verifier profile, or the independent refinement run.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
from types import SimpleNamespace
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load():
    import importlib.util
    import sys
    path = HERE / "capture-guard-linkage.py"
    spec = importlib.util.spec_from_file_location("h2b_mir_linkage", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing H2b linkage runner: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


LINKAGE = load()
H2A = LINKAGE.H2A
H2B = LINKAGE.H2B
LINK = LINKAGE.LINK
REPO = LINKAGE.REPO
GUARD = "<DropOnPanic<T> as std::ops::Drop>::drop"
MUTATIONS = (
    "receiver", "callee", "callee_type", "move", "operand_local",
    "projection", "destination", "normal_edge", "unwind_edge",
    "cleanup", "extra_operation", "ghost_inventory",
)
REASONS = {
    "receiver": "SAFE local guard Drop identity/interface",
    "callee": "guard Drop typed FnDef/substitution",
    "callee_type": "guard Drop typed FnDef/substitution",
    "move": "guard Drop move argument",
    "operand_local": "guard Drop place: _4",
    "projection": "guard Drop place: _4",
    "destination": "guard Drop place: _0",
    "normal_edge": "guard Drop normal edge",
    "unwind_edge": "guard Drop unwind edge",
    "cleanup": "guard Drop block identity/cleanup",
    "extra_operation": "guard Drop block2 statements",
    "ghost_inventory": "local guard exact source/ghost owner",
}


def require(ok: bool, why: str) -> None:
    LINKAGE.require(ok, why)


def replace_once(data: str, old: str, new: str, mutation: str) -> str:
    require(data.count(old) == 1,
            f"{mutation}: expected exactly one selected MIR field, found {data.count(old)}")
    return data.replace(old, new, 1)


def guard_body(decoded: str) -> tuple[int, int, str]:
    marker = f'defPath = "{GUARD}"'
    require(decoded.count(marker) == 1, "local guard complete MIR body not unique")
    at = decoded.index(marker)
    lead = decoded.rfind("    ( defKind =", 0, at)
    require(lead >= 0, "local guard MIR body opening missing")
    opening = decoded.index("(", lead)
    body = H2A.CONSTRUCTOR.mir_balanced_item(decoded, opening)
    return opening, opening + len(body), body


def section(body: str, before: str, after: str) -> tuple[int, int, str]:
    lo = body.index(before)
    hi = body.index(after, lo + len(before))
    return lo, hi, body[lo:hi]


def mutate_guard_mir(decoded: str, mutation: str) -> str:
    """Change exactly one typed field in O17's full local guard graph."""
    require(mutation in MUTATIONS, "unknown H2b direct MIR mutation")
    opening, tail, body = guard_body(decoded)
    if mutation == "receiver":
        lo, hi, inputs = section(body, "      inputs = [", "      localDecls = [")
        inputs = replace_once(inputs, "mutability = (mut = void)",
                              "mutability = (not = void)", mutation)
        body = body[:lo] + inputs + body[hi:]
    elif mutation == "ghost_inventory":
        lo, hi, ghosts = section(body, "      ghostStmts = [", "\n      unsafety = (")
        ghosts = replace_once(
            ghosts,
            'raw = "//@ open <DropOnPanic<T>>.own(_t, ?g);"',
            'raw = "//@ assert true;"', mutation)
        body = body[:lo] + ghosts + body[hi:]
    elif mutation == "cleanup":
        lo, hi, blocks = section(body, "      basicBlocks = [", "\n      span = (")
        require(blocks.count("isCleanup = false") == 4,
                "cleanup mutant expected exactly four plain guard blocks")
        at = blocks.rfind("isCleanup = false")
        blocks = blocks[:at] + "isCleanup = true" + blocks[at + len("isCleanup = false"):]
        body = body[:lo] + blocks + body[hi:]
    elif mutation == "extra_operation":
        lo, hi, blocks = section(body, "      basicBlocks = [", "\n      span = (")
        marker = "( id = (index = 2),"
        require(blocks.count(marker) == 1, "guard block2 not unique")
        start = blocks.index(marker)
        block = H2A.CONSTRUCTOR.mir_balanced_item(blocks, blocks.index("(", start))
        stmt_at = block.index("statements = [") + len("statements = [")
        first_at = block.index("( sourceInfo = (", stmt_at)
        first = H2A.CONSTRUCTOR.mir_balanced_item(block, first_at)
        changed = block[:first_at] + first + ",\n            " + block[first_at:]
        blocks = blocks[:start] + changed + blocks[start + len(block):]
        body = body[:lo] + blocks + body[hi:]
    else:
        lo, hi, blocks = section(body, "      basicBlocks = [", "\n      span = (")
        marker = "( id = (index = 2),"
        require(blocks.count(marker) == 1, "guard block2 not unique")
        start = blocks.index(marker)
        block = H2A.CONSTRUCTOR.mir_balanced_item(blocks, blocks.index("(", start))
        call_start = block.index("call = (") + len("call = ")
        call = H2A.CONSTRUCTOR.mir_balanced_item(block, call_start)
        if mutation == "callee":
            call = replace_once(call,
                'name = "std::ptr::mut_ptr::<impl *mut T>::drop_in_place"',
                'name = "std::ptr::read"', mutation)
        elif mutation == "callee_type":
            call = replace_once(call, 'type = (kind = (param = "T"))',
                                'type = (kind = (uInt = (u8 = void)))', mutation)
        elif mutation == "move":
            call = replace_once(call, "args = [\n                  ( move = (",
                                "args = [\n                  ( copy = (", mutation)
        elif mutation in ("operand_local", "projection"):
            arg_lo, arg_hi, arg = section(call, "args = [", "destination = (")
            if mutation == "operand_local":
                arg = replace_once(arg, 'local = (name = "_4")',
                                   'local = (name = "_3")', mutation)
            else:
                arg = replace_once(arg, "projection = []",
                                   "projection = [(deref = void)]", mutation)
            call = call[:arg_lo] + arg + call[arg_hi:]
        elif mutation == "destination":
            dst_lo, dst_hi, dst = section(call, "destination = (", "callSpan = (")
            dst = replace_once(dst, 'local = (name = "_0")',
                               'local = (name = "_3")', mutation)
            call = call[:dst_lo] + dst + call[dst_hi:]
        elif mutation == "normal_edge":
            call = replace_once(call, "target = (something = (index = 3))",
                                "target = (something = (index = 2))", mutation)
        elif mutation == "unwind_edge":
            call = replace_once(call, "unwindAction = (continue = void)",
                                "unwindAction = (unreachable = void)", mutation)
        changed = block[:call_start] + call + block[call_start + len(
            H2A.CONSTRUCTOR.mir_balanced_item(block, call_start)):]
        blocks = blocks[:start] + changed + blocks[start + len(block):]
        body = body[:lo] + blocks + body[hi:]
    require(body != decoded[opening:tail], "H2b MIR mutation had no effect")
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
spec = importlib.util.spec_from_file_location("h2b_mir_mutant", @PREPARER@)
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
    changed = module.mutate_guard_mir(canonical, mutation)
except Exception as exc:
    record.write_text(json.dumps({"mutation": mutation, "error": str(exc)}) + "\\n")
    sys.stderr.write("H2B MIR mutant setup failed: " + str(exc) + "\\n")
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
'''.replace("@PREPARER@", repr(str(HERE / "capture-h2b-mir-mutation.py")))
   .replace("@REAL@", repr(str(source_bin / "vf-rust-mir-exporter")))
   .replace("@SCHEMA@", repr(str(schema.resolve())))
   .replace("@MUTATION@", repr(mutation))
   .replace("@SOURCE_SHA@", repr(source_sha))
   .replace("@RECORD@", repr(str(case / "mutation-record.json"))))
    wrapper.chmod(0o755)
    shutil.copy2(wrapper, case / "mir-exporter-wrapper.py")
    LINK.write_json(case / "mutation-profile.json", {
        "mutation": mutation,
        "base_console_sha256": LINK.sha((source_bin / "verifast").read_bytes()),
        "shadow_console_sha256": LINK.sha((binary / "verifast").read_bytes()),
        "real_exporter_sha256": LINK.sha((source_bin / "vf-rust-mir-exporter").read_bytes()),
        "wrapper_sha256": LINK.sha(wrapper.read_bytes()),
    })
    return shadow


def run_case(case: Path, args, shadow: Path) -> dict:
    exporter = str(args.tool_home / "bin/vf-rust-mir-exporter")
    stages = {}
    stages["normal-export"] = LINK.stage(case, "normal-export", [
        exporter, "verified/lib.rs", f"--sysroot={args.compiler_sysroot}",
        "--edition", "2021"], args, output_name="normal-mir.bin")
    stages["readonly-export"] = LINK.stage(case, "readonly-export", [
        exporter, "verified/lib.rs", f"--sysroot={args.compiler_sysroot}",
        "--edition", "2021", "--crate-type", "lib",
        "--vf-rust-mir-exporter:preprocess-readonly"], args,
        output_name="readonly-mir.bin")
    for mode in ("normal", "readonly"):
        if stages[f"{mode}-export"]["exit"] == 0:
            stages[f"{mode}-decode"] = LINK.stage(case, f"{mode}-decode", [
                "capnp", "decode", str(args.schema), "VfMir"], args,
                input_name=f"{mode}-mir.bin", output_name=f"{mode}-mir.txt",
                cap_seconds=40)
    if all(stages.get(k, {}).get("exit") == 0 for k in (
            "normal-export", "normal-decode", "readonly-export", "readonly-decode")):
        stages["refinement"] = LINK.stage(case, "refinement", [
            str(args.tool_home / "bin/refinement-checker"), "--rustc-args",
            "--edition 2021", "original/lib.rs", "verified/lib.rs"], args,
            cap_seconds=70)
        shadow_args = SimpleNamespace(**vars(args))
        shadow_args.tool_home = shadow
        stages["full-verification"] = LINK.stage(case, "full-verification", [
            str(shadow / "bin/verifast"), "-rustc_args", "--edition 2021",
            "-verbose", "1", "verified/lib.rs"], shadow_args, cap_seconds=100)
    return stages


def classify(case: Path, mutation: str, stages: dict) -> dict:
    complete = all(stages.get(k, {}).get("exit") == 0 for k in (
        "normal-export", "normal-decode", "readonly-export", "readonly-decode",
        "refinement"))
    intact = all(s.get("source_unchanged") is True for s in stages.values())
    log_file = case / "full-verification.log"
    log = log_file.read_text(errors="replace") if log_file.exists() else ""
    fatal = [line for line in log.splitlines() if line.startswith("Fatal error:")]
    errors = LINK.ERR.findall(log)
    record_path = case / "mutation-record.json"
    profile_path = case / "mutation-profile.json"
    files = [case / name for name in (
        "canonical-mir.txt", "mutated-mir.txt", "canonical-mir.bin",
        "mutated-mir.bin", "mir-exporter-wrapper.py")]
    exact = False
    record = None
    if record_path.exists() and profile_path.exists() and all(p.exists() for p in files):
        record = json.loads(record_path.read_text())
        profile = json.loads(profile_path.read_text())
        try:
            exact = (mutate_guard_mir(files[0].read_text(), mutation) ==
                     files[1].read_text())
        except (ValueError, IndexError):
            exact = False
        exact = exact and all((
            record.get("matched") is True,
            record.get("mutation") == mutation,
            record.get("exporter_exit") == 0,
            record.get("decode_exit") == 0,
            record.get("encode_exit") == 0,
            record.get("selected_source_sha256") ==
                LINK.sha((case / "verified/lib.rs").read_bytes()),
            record.get("canonical_sha256") == LINK.sha(files[2].read_bytes()),
            record.get("mutated_sha256") == LINK.sha(files[3].read_bytes()),
            files[2].read_bytes() != files[3].read_bytes(),
            record.get("real_exporter_sha256") == profile.get("real_exporter_sha256"),
            profile.get("base_console_sha256") == profile.get("shadow_console_sha256"),
            profile.get("wrapper_sha256") == LINK.sha(files[4].read_bytes()),
        ))
    expected = ('Fatal error: exception Failure("SORT4-GENERIC-GUARD: '
                'certificate mismatch: ' + REASONS[mutation] + '")')
    rejection = (complete and intact and exact and
                 stages.get("full-verification", {}).get("exit") == 2 and
                 len(fatal) == 1 and fatal[0] == expected and not errors and
                 "source/MIR local link accepted" not in log and
                 "Verifying function 'sort4_checked_generic_drop'" not in log and
                 "Verifying function '<DropOnPanic<T> as std::ops::Drop>::drop'" not in log)
    result = {
        "mutation": mutation,
        "classification": "EXACT_TYPED_MIR_ADMISSION_REJECTED" if rejection else "INCONCLUSIVE",
        "component_accepted": False, "actual_nested_drop_proved": False,
        "test_tool_mutation_profile": True,
        "source_integrity": intact, "independent_frontend_refinement": complete,
        "mutant_exact": exact, "expected_reason": REASONS[mutation],
        "full_verifier_exit": stages.get("full-verification", {}).get("exit"),
        "fatal": fatal, "first_error": errors[0] if errors else None,
        "mutation_record": record, "stages": stages,
    }
    LINK.write_json(case / "classification.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--guard-root", type=Path, required=True)
    parser.add_argument("--template-root", type=Path, required=True)
    parser.add_argument("--mutations", nargs="+", choices=MUTATIONS,
                        default=list(MUTATIONS))
    args = parser.parse_args()
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux", "GitHub-hosted Linux required")
    require(args.guard_root.resolve() == REPO and
            args.template_root.resolve() == REPO,
            "H2a/H2b MIR controls require the same exact root")
    evidence = args.evidence.resolve()
    require(not evidence.exists(), f"refusing overwrite: {evidence}")
    evidence.mkdir(parents=True)
    os.environ["SORT4_GUARD_REPO_ROOT"] = str(REPO)
    os.environ["SORT4_GUARD_TEMPLATE_REPO_ROOT"] = str(REPO)
    method_body, method_cert = H2A.source_certificate()
    struct_body, drop_body, guard_cert = H2B.source_certificate()
    method = LINKAGE.checked_method(method_body)
    original, verified = LINKAGE.source_pair(method, struct_body, drop_body,
                                             "positive", template_active=True)
    cert = {"generic_method": method_cert, "guard": guard_cert,
            "actual_nested_drop_proved": False}
    LINK.write_json(evidence / "source-certificate.json", cert)
    positive = evidence / "positive-unwrapped"
    positive.mkdir()
    (positive / "original").mkdir()
    (positive / "verified").mkdir()
    (positive / "original/lib.rs").write_bytes(original)
    (positive / "verified/lib.rs").write_bytes(verified)
    LINK.write_json(positive / "fixture.json", {
        "variant": "positive", "source_certificate": cert,
        "original_sha256": LINK.sha(original),
        "verified_sha256": LINK.sha(verified),
        "test_tool_mutation_profile": False})
    positive_result = LINKAGE.classify(positive, "positive",
                                       H2A.run_case(positive, args), True)
    results = []
    if positive_result["classification"] == "H2B_LOCAL_NOMINAL_DROP_CANDIDATE_PROVED":
        for mutation in args.mutations:
            case = evidence / mutation
            case.mkdir()
            (case / "original").mkdir()
            (case / "verified").mkdir()
            (case / "original/lib.rs").write_bytes(original)
            (case / "verified/lib.rs").write_bytes(verified)
            LINK.write_json(case / "fixture.json", {
                "mutation": mutation, "source_certificate": cert,
                "original_sha256": LINK.sha(original),
                "verified_sha256": LINK.sha(verified),
                "test_tool_mutation_profile": True,
                "actual_nested_drop_proved": False})
            shadow = make_shadow(args.tool_home, args.schema, case,
                                 mutation, LINK.sha(verified))
            results.append(classify(case, mutation, run_case(case, args, shadow)))
    LINK.write_json(evidence / "summary.json", {
        "classification": "H2B_TYPED_MIR_TEST_MUTATIONS_DIAGNOSTIC_ONLY",
        "component_accepted": False, "actual_nested_drop_proved": False,
        "positive_unwrapped": positive_result, "results": results,
        "source_certificate": cert,
    })


if __name__ == "__main__":
    main()
