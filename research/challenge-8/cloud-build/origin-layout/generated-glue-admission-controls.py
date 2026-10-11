#!/usr/bin/env python3
"""Cloud-only official-refiner admission controls for captured generated glue.

Importing this module is inert. ``run`` is called by the existing hosted
runner after both compiler exports and decodes have succeeded. The tests replay
those exact exports through a copied, SHA-checked official refiner; they do not
invoke a compiler, exporter, verifier, or source preparation step.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _one(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"{label}: expected exactly one decoded-text anchor, found {count}")
    return text.replace(old, new, 1)


def _generated_descriptor(text: str, old: str, new: str, label: str) -> str:
    start = text.find('      generatedGlue = (')
    end = text.find('\n      capturedMirHash =', start)
    if start < 0 or end < 0:
        raise ValueError(f"{label}: generated descriptor block is absent")
    block = _one(text[start:end], old, new, label)
    return text[:start] + block + text[end:]


def _generated_body(text: str, old: str, new: str, label: str) -> str:
    start = text.find('      defPath = "__vf_generated_drop_glue",')
    end = text.find('\n      visibility =', start)
    if start < 0 or end < 0:
        raise ValueError(f"{label}: generated function body is absent")
    block = _one(text[start:end], old, new, label)
    return text[:start] + block + text[end:]


def _mutations(original: str, verified: str) -> dict[str, tuple[str, str]]:
    """Return (side,text) cases, each based on the untouched decoded exports."""
    cases: dict[str, tuple[str, str]] = {}
    cases["missing_generated_enabled"] = (
        "verified", _one(verified, "        enabled = true,\n", "        enabled = false,\n",
                         "generated enabled tag"))
    cases["wrong_generated_body_key"] = (
        "verified", _one(verified, '        bodyKey = "__vf_generated_drop_glue",\n',
                         '        bodyKey = "__vf_wrong_generated_glue",\n',
                         "generated body identity"))
    cases["wrong_generated_function_identity"] = (
        "verified", _one(verified, 'defPath = "__vf_generated_drop_glue",',
                         'defPath = "__vf_wrong_generated_drop_glue",',
                         "generated function identity"))
    cases["wrong_selected_destructor"] = (
        "verified", _generated_descriptor(verified,
            '        selectedDropPath = "<CopyOnDrop as core::ops::Drop>::drop",\n',
            '        selectedDropPath = "<CopyOnDrop as core::ops::Clone>::clone",\n',
            "selected destructor"))
    cases["wrong_actual_call_target"] = (
        "verified", _one(verified, 'name = "core::ops::Drop::drop"',
                         'name = "core::ops::Drop::clone"', "generated call target"))
    cases["wrong_unwind_edge"] = (
        "verified", _generated_descriptor(verified, '        unwindKind = "Continue",\n',
                         '        unwindKind = "Terminate",\n', "generated unwind edge"))
    cases["wrong_actual_call_unwind"] = (
        "verified", _generated_body(verified,
            '                unwindAction = (continue = void),\n',
            '                unwindAction = (terminate = void),\n',
            "generated call unwind edge"))
    cases["wrong_actual_call_normal_target"] = (
        "verified", _generated_body(verified,
            '                target = (something = (index = 1)) ) ) ),\n',
            '                target = (something = (index = 0)) ) ) ),\n',
            "generated call normal target"))
    cases["missing_caller_generated_reference"] = (
        "original", _one(original, '                generatedBodyKey = "__vf_generated_drop_glue" ) ) ),\n',
                         '                 ) ) ),\n', "caller generated-body reference"))
    return cases


def _write_wrapper(bin_dir: Path, raw_original: Path, raw_verified: Path) -> tuple[Path, str]:
    """Install an argv-checked exporter shim that emits only captured messages."""
    wrapper = bin_dir / "vf-rust-mir-exporter"
    wrapper.write_text(
        "#!/usr/bin/env python3\n"
        "import pathlib, sys\n"
        f"messages = {{'original/lib.rs': pathlib.Path({str(raw_original)!r}), "
        f"'verified/lib.rs': pathlib.Path({str(raw_verified)!r})}}\n"
        "if len(sys.argv) < 2 or sys.argv[1] not in messages:\n"
        "    raise SystemExit('admission control wrapper refused unknown source argument')\n"
        "sys.stdout.buffer.write(messages[sys.argv[1]].read_bytes())\n",
        encoding="utf-8")
    wrapper.chmod(0o755)
    return wrapper, _sha(wrapper)


def capture_refiner_exports(evidence: Path, args, env: dict[str, str], base,
                            positive_case: Path) -> tuple[dict[str, Path], dict]:
    """Capture the two exact exporter invocations made by the official refiner.

    The ordinary case exporter has different rustc arguments from the refiner
    frontend. Reusing its MIR makes a false negative at unrelated constants.
    This wrapper forwards argv byte-for-byte to the pinned real exporter and
    saves its stdout before the refiner consumes it. It runs only in Cloud.
    """
    capture = evidence / 'refiner-export-capture'
    capture.mkdir()
    bin_dir = capture / 'bin'
    bin_dir.mkdir()
    sources = capture / 'sources'
    (sources / 'original').mkdir(parents=True)
    (sources / 'verified').mkdir()
    source_before = {}
    for side in ('original', 'verified'):
        src = positive_case / side / 'lib.rs'
        dst = sources / side / 'lib.rs'
        shutil.copy2(src, dst)
        source_before[side] = _sha(dst)
    refiner_source = Path(args.tool_home) / 'bin/refinement-checker'
    exporter_source = Path(args.tool_home) / 'bin/vf-rust-mir-exporter'
    refiner = bin_dir / 'refinement-checker'
    shutil.copy2(refiner_source, refiner)
    refiner.chmod(refiner.stat().st_mode | 0o111)
    if _sha(refiner) != _sha(refiner_source):
        raise RuntimeError('capture refiner copy differs from pinned executable')
    wrapper = bin_dir / 'vf-rust-mir-exporter'
    wrapper.write_text(
        '#!/usr/bin/env python3\n'
        'import json, os, pathlib, subprocess, sys\n'
        f'real = {str(exporter_source)!r}\n'
        f'root = pathlib.Path({str(capture)!r})\n'
        'allowed = {"original/lib.rs": "original", "verified/lib.rs": "verified"}\n'
        'if len(sys.argv) < 2 or sys.argv[1] not in allowed:\n'
        '    raise SystemExit("refiner exporter capture refused unknown source")\n'
        'side = allowed[sys.argv[1]]\n'
        'result = subprocess.run([real, *sys.argv[1:]], stdout=subprocess.PIPE,\n'
        '                        stderr=subprocess.PIPE, check=False)\n'
        'if result.returncode == 0:\n'
        '    target = root / (side + "-refiner-export.bin")\n'
        '    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)\n'
        '    with os.fdopen(fd, "wb") as output: output.write(result.stdout)\n'
        '    (root / (side + "-argv.json")).write_text(json.dumps(sys.argv[1:]))\n'
        'sys.stdout.buffer.write(result.stdout)\n'
        'sys.stderr.buffer.write(result.stderr)\n'
        'raise SystemExit(result.returncode)\n', encoding='utf-8')
    wrapper.chmod(0o755)
    child_env = dict(env)
    child_env['PATH'] = str(bin_dir) + os.pathsep + child_env.get('PATH', '')
    status = base.run_stage(sources, 'official-refinement-capture', [
        str(refiner), '--rustc-args', '--edition 2021',
        'original/lib.rs', 'verified/lib.rs'], child_env,
        timeout_seconds=args.stage_seconds)
    log = ''.join((sources / name).read_text(errors='replace') for name in (
        'official-refinement-capture.log', 'official-refinement-capture.out')
        if (sources / name).exists())
    raw = {side: capture / (side + '-refiner-export.bin')
           for side in ('original', 'verified')}
    after = {side: _sha(sources / side / 'lib.rs') for side in source_before}
    row = {'exit_code': status, 'success_marker': 'No refinement errors found',
           'success_marker_present': 'No refinement errors found' in log,
           'source_sha256_before': source_before, 'source_sha256_after': after,
           'refiner_sha256': _sha(refiner), 'real_exporter_sha256': _sha(exporter_source),
           'wrapper_sha256': _sha(wrapper),
           'raw_sha256': {side: _sha(path) for side, path in raw.items() if path.is_file()},
           'argv': {side: json.loads((capture / (side + '-argv.json')).read_text())
                    for side in raw if (capture / (side + '-argv.json')).is_file()}}
    row['matched'] = (status == 0 and row['success_marker_present'] and
                      source_before == after and all(path.is_file() and
                      path.stat().st_size > 0 for path in raw.values()) and
                      len(row['argv']) == 2)
    if not row['matched']:
        raise RuntimeError(f'official refiner exporter capture failed: {row}')
    return raw, row


def run(evidence: Path, args, env: dict[str, str], base, positive_case: Path) -> dict:
    """Run baseline replays and bounded official-refiner admission mutants."""
    evidence = Path(evidence)
    positive_case = Path(positive_case)
    if evidence.exists():
        raise FileExistsError(f"refusing to reuse generated-glue admission evidence: {evidence}")
    evidence.mkdir(parents=True)
    captured_raw, capture_receipt = capture_refiner_exports(evidence, args, env, base,
                                                             positive_case)
    capture_sources = evidence / 'refiner-export-capture/sources'
    include_dirs = list(dict.fromkeys([Path(args.schema).parent, *getattr(args, "capnp_include", ())]))
    decode_args = ['capnp', 'decode']
    for directory in include_dirs:
        decode_args.extend(['-I', str(directory)])
    decode_args.extend([str(args.schema), 'VfMir'])
    captured_decoded = {}
    for side in ('original', 'verified'):
        name = f'{side}-refiner-decode.out'
        status = base.run_stage(capture_sources, f'{side}-refiner-decode',
                                decode_args, env, timeout_seconds=args.stage_seconds,
                                stdin=captured_raw[side], stdout_name=name)
        path = capture_sources / name
        if status != 0 or not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f'{side}: captured official-refiner MIR decode failed')
        captured_decoded[side] = path
    source_files = {
        "original_source": positive_case / "original/lib.rs",
        "verified_source": positive_case / "verified/lib.rs",
        "original_raw_export": captured_raw['original'],
        "verified_raw_export": captured_raw['verified'],
        "original_decoded": captured_decoded['original'],
        "verified_decoded": captured_decoded['verified'],
    }
    for label, path in source_files.items():
        if not path.is_file():
            raise FileNotFoundError(f"admission control input {label} missing: {path}")
    preserved = evidence / "preserved-inputs"
    preserved.mkdir(parents=True)
    for label, path in source_files.items():
        shutil.copy2(path, preserved / f"{label}-{path.name}")
    capnp_path = shutil.which("capnp")
    if capnp_path is None:
        raise FileNotFoundError("capnp encoder is required in the Cloud build image")
    receipt = {
        "schema": "generated-glue-official-refiner-admission-controls-v1",
        "classification": "ADMISSION_CONTROLS_ONLY_NO_PROOF_CREDIT",
        "source_sha256": {name: _sha(path) for name, path in source_files.items()},
        "preserved_input_sha256": {name: _sha(preserved / f"{name}-{path.name}")
                                   for name, path in source_files.items()},
        "refiner_sha256": _sha(Path(args.tool_home) / "bin/refinement-checker"),
        "schema_sha256": _sha(Path(args.schema)),
        "capnp_path": capnp_path,
        "capnp_sha256": _sha(Path(capnp_path)),
        "cases": {},
        "official_refiner_export_capture": capture_receipt,
    }
    original_text = source_files["original_decoded"].read_text()
    verified_text = source_files["verified_decoded"].read_text()
    temp = evidence / "replay-inputs"
    temp.mkdir()
    try:
        refiner_source = Path(args.tool_home) / "bin/refinement-checker"
        receipt["raw_export_sha256"] = {
            "original": _sha(source_files["original_raw_export"]),
            "verified": _sha(source_files["verified_raw_export"])}

        def invoke(label: str, orig_raw: Path, ver_raw: Path,
                   orig_file: Path, ver_file: Path) -> dict:
            case_dir = evidence / label
            case_dir.mkdir()
            # Each case gets an isolated executable directory and wrapper bound
            # to these exact binary streams; no shell lookup can reach tools.
            local_bin = case_dir / "bin"
            local_bin.mkdir()
            local_refiner = local_bin / "refinement-checker"
            shutil.copy2(refiner_source, local_refiner)
            local_refiner.chmod(local_refiner.stat().st_mode | 0o111)
            if _sha(local_refiner) != receipt["refiner_sha256"]:
                raise RuntimeError("copied official refiner hash differs from the build receipt")
            _, wrapper_sha = _write_wrapper(local_bin, orig_raw, ver_raw)
            case_src = case_dir / "sources"
            (case_src / "original").mkdir(parents=True)
            (case_src / "verified").mkdir()
            shutil.copy2(orig_file, case_src / "original/lib.rs")
            shutil.copy2(ver_file, case_src / "verified/lib.rs")
            source_before = {"original": _sha(case_src / "original/lib.rs"),
                             "verified": _sha(case_src / "verified/lib.rs")}
            child_env = dict(env)
            child_env["PATH"] = str(local_bin) + os.pathsep + child_env.get("PATH", "")
            status = base.run_stage(case_src, "official-refinement", [
                str(local_refiner), "--rustc-args", "--edition 2021",
                "original/lib.rs", "verified/lib.rs"], child_env,
                timeout_seconds=args.stage_seconds)
            log_path = case_src / "official-refinement.log"
            log = log_path.read_text(errors="replace") if log_path.exists() else ""
            stdout_path = case_src / "official-refinement.out"
            out = stdout_path.read_text(errors="replace") if stdout_path.exists() else ""
            (case_dir / "log.txt").write_text(log + out)
            return {"exit_code": status, "log_sha256": _sha(case_dir / "log.txt"),
                    "wrapper_sha256": wrapper_sha,
                    "refiner_sha256": _sha(local_refiner),
                    "source_sha256_before": source_before,
                    "source_sha256_after": {
                        "original": _sha(case_src / "original/lib.rs"),
                        "verified": _sha(case_src / "verified/lib.rs")},
                    "log": log + out}

        # First prove that captured and capnp re-encoded pristine messages both
        # reach the same successful official-refiner route.
        pristine = {
            "original": source_files["original_decoded"].read_text(),
            "verified": source_files["verified_decoded"].read_text(),
        }
        encoded = {}
        for side, text in pristine.items():
            path = temp / f"encoded-{side}.bin"
            with path.open("wb") as output:
                result = subprocess.run(["capnp", "encode", "-I", str(Path(args.schema).parent),
                                         str(args.schema), "VfMir"], input=text, text=True,
                                        stdout=output, stderr=subprocess.PIPE,
                                        cwd=positive_case, env=env, check=False)
            if result.returncode != 0 or not path.is_file() or path.stat().st_size == 0:
                raise RuntimeError(f"capnp encode pristine {side} failed: {result.stderr!r}")
            encoded[side] = path
        baselines = {}
        for label, raw in (("raw_baseline", (source_files["original_raw_export"],
                                                 source_files["verified_raw_export"])),
                           ("encoded_baseline", (encoded["original"], encoded["verified"]))):
            outcome = invoke(label, raw[0], raw[1], source_files["original_source"],
                             source_files["verified_source"])
            marker = "No refinement errors found"
            matched = outcome["exit_code"] == 0 and marker in outcome["log"]
            baselines[label] = {"matched": matched, "exit_code": outcome["exit_code"],
                                "success_marker": marker,
                                "log_sha256": outcome["log_sha256"],
                                "wrapper_sha256": outcome["wrapper_sha256"],
                                "copied_refiner_sha256": outcome["refiner_sha256"],
                                "source_sha256_before": outcome["source_sha256_before"],
                                "source_sha256_after": outcome["source_sha256_after"],
                                "original_message_sha256": _sha(raw[0]),
                                "verified_message_sha256": _sha(raw[1])}
            if not matched:
                receipt["baseline_controls"] = baselines
                receipt["status"] = "BASELINE_REPLAY_FAILED_CONTROLS_NOT_QUALIFIED"
                (evidence / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
                raise RuntimeError(f"official-refiner {label} control did not pass its success marker")
        receipt["baseline_controls"] = baselines

        expected_messages = {
            "missing_generated_enabled": "Generated DropGlue: body missing from one exported unit",
            "wrong_generated_body_key": "Generated DropGlue: verified has an unexpected generated body key",
            "wrong_generated_function_identity": "Generated DropGlue: verified has an unexpected generated body key",
            "wrong_selected_destructor": "Generated DropGlue: verified must contain one checked selected Drop::drop body",
            "wrong_actual_call_target": "Generated DropGlue: verified call is not the recorded raw trait FnDef",
            "wrong_unwind_edge": "Generated DropGlue: verified has an unexpected MIR phase or control-flow edge",
            "wrong_actual_call_unwind": "Generated DropGlue: verified call operands, destination, target, or unwind differ",
            "wrong_actual_call_normal_target": "Generated DropGlue: verified call operands, destination, target, or unwind differ",
            "missing_caller_generated_reference": "Generated DropGlue: original caller Drop does not bind the generated body",
        }
        outcomes = {}
        for name, (side, mutated_text) in _mutations(original_text, verified_text).items():
            mutated_path = temp / f"{name}.bin"
            with mutated_path.open("wb") as output:
                result = subprocess.run(["capnp", "encode", "-I", str(Path(args.schema).parent),
                                         str(args.schema), "VfMir"], input=mutated_text, text=True,
                                        stdout=output, stderr=subprocess.PIPE,
                                        cwd=positive_case, env=env, check=False)
            if result.returncode != 0 or not mutated_path.is_file() or mutated_path.stat().st_size == 0:
                outcomes[name] = {"matched": False, "stage": "ENCODE_SETUP_FAILURE",
                                  "stderr": (result.stderr.decode(errors="replace")
                                             if isinstance(result.stderr, bytes) else result.stderr)}
                continue
            raw = ((mutated_path, encoded["verified"]) if side == "original" else
                   (encoded["original"], mutated_path))
            outcome = invoke(name, raw[0], raw[1], source_files["original_source"],
                             source_files["verified_source"])
            log = outcome.pop("log")
            expected = expected_messages[name]
            matched = outcome["exit_code"] != 0 and expected in log
            (evidence / name / "official-log.txt").write_text(log)
            outcomes[name] = {"matched": matched,
                              "stage": "INTENDED_ADMISSION_REFUSAL" if matched else
                                      ("WRONG_REFUSAL_OR_ACCEPTED" if outcome["exit_code"] else
                                       "UNEXPECTED_SUCCESS"),
                              "expected_message": expected,
                              "expected_message_present": expected in log,
                              "wrapper_sha256": outcome["wrapper_sha256"],
                              "copied_refiner_sha256": outcome["refiner_sha256"],
                              "source_sha256_before": outcome["source_sha256_before"],
                              "source_sha256_after": outcome["source_sha256_after"],
                              "original_message_sha256": _sha(raw[0]),
                              "verified_message_sha256": _sha(raw[1]),
                              "log_sha256": outcome["log_sha256"],
                              "exit_code": outcome["exit_code"]}
        receipt["mutations"] = outcomes
        receipt["all_matched"] = (bool(expected_messages) and
                                   len(outcomes) == len(expected_messages) and
                                   all(row.get("matched") is True for row in outcomes.values()))
        receipt["status"] = ("ALL_INTENDED_ADMISSION_REFUSALS" if receipt["all_matched"] else
                             "ADMISSION_CONTROL_FAILURES_RECORDED")
        receipt["not_run"] = [name for name, row in outcomes.items()
                              if row.get("stage") == "ENCODE_SETUP_FAILURE"]
        (evidence / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
        return receipt
    finally:
        # The isolated executable copies and replay messages are retained with
        # the machine-readable receipt for independent review.
        pass
