#!/usr/bin/env python3
"""Fail-closed focused evidence audit for the ManuallyDrop::new CFG repair.

This checks observations in a Cloud evidence bundle; it never runs VeriFast.  A
verifier exit, successful refinement, or equal exported MIR alone earns no credit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

FIXTURES = {
    "forget": ("2a6f0d16bd29cc9ea6c10e3b63e6b94000249d72e94d64f99d45cefb277ce1f7", "forget"),
    "shared_cleanup": ("c3c77c383b54e19a35233b14764fb1be23e9244ee3a13d997c157dfe0d31ba2f", "shared_cleanup"),
    "false_normal_post": ("23a1360b673fe6ece1f8903e69aae104f9e8dadfc34061d09062a993f6071f0d", "forget_false_normal_post"),
    "shared_false_unwind": ("886b12a0cd0f5f6edc22080577f241df63588251ec02cb495074e742639cf15e", "shared_cleanup_false_unwind_post"),
    "dead_code_pre": ("b1317808274abeca09fc9b5b4e9079c7426822347205970217123993e0af70c2", "forget_from_dead_precondition"),
}
BASE = "f76012fb518703b1d98e243ac4f487f16877cfcb"
CANDIDATE = "1435539475fdaa7810bc2bc780fba0514f765f48"
TREE = "be55d8d934fb10617309a289e0d546ca1aed6ea0"
REF = "refs/heads/challenge8/manuallydrop-new-cfg-upstream-candidate"
BUNDLE = "a87775fabeec73187f6da91d4944281232b74bc70aeeb5642d6043056cb000d0"
STOCK_ARCHIVE = "5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd"
DEPS_ARCHIVE = "8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580"
RUSTC = "f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f"
ERROR = re.compile(r"(?m)^([^\n]*\.(?:rs|rsspec)\(\d+,[^\n]*?: error: [^\n]+|Fatal error:[^\n]+)")
DEAD = re.compile(r"(?m)^([^\n]*?\(\d+,[^\n]*?\): dead code)\s*$")
SUCCESS = re.compile(r"(?m)^0 errors found \(\d+ statements verified\)")


class AuditIssue(Exception):
    def __init__(self, message: str, classification: str = "INCONCLUSIVE"):
        super().__init__(message)
        self.classification = classification


def require(ok: bool, reason: str, classification: str = "INCONCLUSIVE") -> None:
    if not ok:
        raise AuditIssue(reason, classification)


def read(path: Path) -> str:
    require(path.is_file(), f"missing evidence: {path}")
    return path.read_text(errors="replace")


def digest(path: Path) -> str:
    require(path.is_file(), f"missing evidence: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def obj(path: Path) -> dict:
    try:
        value = json.loads(read(path))
    except json.JSONDecodeError as ex:
        raise AuditIssue(f"invalid JSON: {path}: {ex}") from ex
    require(isinstance(value, dict), f"expected JSON object: {path}")
    return value


def sha64(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def verify_provenance(root: Path) -> dict:
    all_logs = root.parent
    evidence = all_logs.parent
    manifest_path = all_logs / "tool-input" / "manifest"
    bundle_path = manifest_path.with_name("bundle")
    manifest = obj(manifest_path)
    receipt = obj(all_logs / "restore-receipt.json")
    identities = obj(all_logs / "identities.json")
    runtime = obj(all_logs / "runtime-components.json")
    certificate = obj(evidence / "source-input-certificate.json")
    require(manifest.get("schema") == "verifast-input-bundle-v1" and
            manifest.get("purpose") == "mdnew-cfg-cloud-delivery" and
            manifest.get("base_commit") == BASE and
            manifest.get("candidate_commit") == CANDIDATE and
            manifest.get("candidate_ref") == REF and
            manifest.get("candidate_tree") == TREE and
            manifest.get("bundle_sha256") == BUNDLE and digest(bundle_path) == BUNDLE,
            "committed tool bundle/manifest differs from pinned delivery")
    require(receipt.get("classification") == "RESTORED_GIT_INPUT" and
            receipt.get("base_commit") == BASE and
            receipt.get("candidate_commit") == CANDIDATE and
            receipt.get("candidate_ref") == REF and
            receipt.get("candidate_tree") == TREE and
            receipt.get("bundle_sha256") == BUNDLE and
            receipt.get("manifest_sha256") == digest(manifest_path) and
            receipt.get("git_identity_preserved") is True,
            "restore receipt does not bind original candidate Git identities")
    proof = identities.get("proof_sha")
    infra = identities.get("infra_sha")
    require(isinstance(proof, str) and re.fullmatch(r"[0-9a-f]{40}", proof) is not None and
            proof == infra == receipt.get("proof_sha") == receipt.get("infra_sha") and
            identities.get("source_input_archive_sha256") == certificate.get("archive_sha256") and
            certificate.get("lane") == "verifast-mdnew-cfg" and
            certificate.get("proof", {}).get("commit") == proof == certificate.get("proof", {}).get("head") and
            certificate.get("infra", {}).get("commit") == infra == certificate.get("infra", {}).get("head") and
            certificate.get("proof", {}).get("root_tree") == identities.get("proof_tree") and
            certificate.get("infra", {}).get("root_tree") == identities.get("infra_tree"),
            "infra/proof identity or source transport certificate differs")
    input_prefix = "research/challenge-8/verifast-input/" + CANDIDATE + "/"
    for rel, expected in ((input_prefix + "bundle", BUNDLE),
                          (input_prefix + "manifest", digest(manifest_path))):
        rows = [row for row in certificate.get("proof", {}).get("restored_paths", [])
                if row.get("path") == rel]
        require(len(rows) == 1 and rows[0].get("sha256") == expected,
                f"source transport did not restore pinned {rel}")
    auditor_rel = "research/challenge-8/cloud-build/mdnew-audit.py"
    auditor_rows = [row for row in certificate.get("infra", {}).get("restored_paths", [])
                    if row.get("path") == auditor_rel]
    require(len(auditor_rows) == 1 and
            auditor_rows[0].get("sha256") == digest(Path(__file__)),
            "auditor bytes are not bound to restored infrastructure commit")
    require(runtime.get("baseline_source_sha") == BASE and
            runtime.get("candidate_source_sha") == CANDIDATE and
            runtime.get("candidate_tree") == TREE and
            runtime.get("stock_distribution_sha256") == STOCK_ARCHIVE and
            runtime.get("vfdeps_archive_sha256") == DEPS_ARCHIVE and
            f"commit-hash: {RUSTC}" in runtime.get("rustc_verbose", ""),
            "tool runtime profile differs from pinned source/archive/compiler")
    consoles = runtime.get("console_binary_sha256", {})
    require(sha64(consoles.get("baseline")) and sha64(consoles.get("candidate")) and
            consoles["baseline"] != consoles["candidate"],
            "source-built baseline/candidate console identities absent or equal")
    for name in ("vf-rust-mir-exporter", "refinement-checker", "vf-cxx-ast-exporter",
                 "libz3.so", "rust/std/lib.rsspec"):
        record = runtime.get("pinned_stock_binaries", {}).get(name, {})
        require(sha64(record.get("sha256")) and record.get("baseline_equal") is True and
                record.get("candidate_equal") is True,
                f"unchanged runtime component {name} lacks profile equality")
    for name in ("src/rust_frontend/vf_mir_exporter",
                 "src/rust_frontend/vf_mir_decoder", "src/refinement_checker"):
        record = runtime.get("components", {}).get(name, {})
        require(isinstance(record.get("source_file_count"), int) and
                record["source_file_count"] > 0 and
                sha64(record.get("source_files_sha256")),
                f"unchanged source component {name} lacks inventory")
    for case, (expected, _) in FIXTURES.items():
        rel = "tests/rust/purely_unsafe/manuallydrop_new_cfg/" + case + ".rs"
        manifest_row = manifest.get("fixtures", {}).get(rel, {})
        require(manifest_row.get("sha256") == expected and
                receipt.get("fixture_hashes", {}).get(rel) == expected and
                receipt.get("selected_files", {}).get(rel) == expected,
                f"{case} fixture delivery receipt differs")
        for side in ("baseline", "candidate"):
            row = obj(root / side / case / "fixture.json")
            require(row.get("source_sha256") == expected and
                    row.get("candidate_commit") == CANDIDATE and
                    row.get("git_blob") == manifest_row.get("git_blob"),
                    f"{side}/{case} fixture copy is not bound to original Git blob")
    return {"infra_sha": infra, "proof_sha": proof,
            "bundle_sha256": BUNDLE, "manifest_sha256": digest(manifest_path),
            "console_binary_sha256": consoles}


def verify_capture_status(root: Path, case: str, side: str, provenance: dict) -> None:
    folder = root / "captures" / case
    prefix = "baseline-" if side == "baseline" else ""
    status_file = folder / ("baseline-capture-status.json" if side == "baseline"
                            else "capture-status.json")
    record = obj(status_file)
    require(record.get("schema") == "verifast-mdnew-capture-v1" and
            record.get("case") == case and record.get("side") == side and
            record.get("tool_source_sha") == (BASE if side == "baseline" else CANDIDATE) and
            record.get("source_sha256") == FIXTURES[case][0] and
            record.get("infra_sha") == provenance["infra_sha"] and
            record.get("proof_sha") == provenance["proof_sha"],
            f"{side}/{case} capture status has wrong source/profile identities")
    stages = record.get("stages", {})
    paths = {"normal-export": folder / f"{prefix}normal-mir.bin",
             "normal-decode": folder / f"{prefix}normal-mir.txt",
             "readonly-export": folder / f"{prefix}readonly-mir.bin",
             "readonly-decode": folder / f"{prefix}readonly-mir.txt",
             "refinement": folder / f"{prefix}refinement.log"}
    for name, path in paths.items():
        stage = stages.get(name, {})
        require(stage.get("exit_status") == 0 and
                stage.get("output_sha256") == digest(path),
                f"{side}/{case} {name} failed or captured output digest differs")
    require(record.get("verified_ast_sha256") == digest(folder / f"{prefix}verified-ast.txt"),
            f"{side}/{case} captured verifier AST digest differs")


def status(path: Path) -> int:
    value = read(path).strip()
    require(re.fullmatch(r"\d+", value) is not None, f"invalid exit status: {path}")
    return int(value)


def source_line(source: str, prefix: str) -> int:
    rows = [i for i, s in enumerate(source.splitlines(), 1) if s.strip().startswith(prefix)]
    require(len(rows) == 1, f"annotation {prefix!r} is not unique")
    return rows[0]


def target_log(log: str, name: str) -> str:
    starts = []
    position = 0
    for line in log.splitlines(keepends=True):
        if ": Verifying function '" in line and ": note:" not in line:
            starts.append((position, line))
        position += len(line)
    matches = [i for i, (_, line) in enumerate(starts)
               if f"Verifying function '{name}'" in line]
    require(len(matches) == 1, f"target function {name} was not reached exactly once")
    i = matches[0]
    return log[starts[i][0]:starts[i + 1][0] if i + 1 < len(starts) else len(log)]


def first_diagnostic(log: str) -> tuple[str, str] | None:
    rows = [(m.start(), "error", m.group(1)) for m in ERROR.finditer(log)]
    rows += [(m.start(), "dead code", m.group(1)) for m in DEAD.finditer(log)]
    if not rows:
        return None
    _, kind, message = min(rows)
    return kind, message


def target_location(message: str, case: str, line: int | None = None) -> bool:
    # The verifier can report the original fixture or the generated verified file.
    m = re.search(r"([^\s():]+\.(?:rs|rsspec))\((\d+),", message)
    if not m:
        return False
    path, actual = m.group(1), int(m.group(2))
    if not (path.endswith("/" + case + ".rs") or path == case + ".rs"):
        return False
    return line is None or actual == line


def verify_source(root: Path, side: str, case: str) -> str:
    data = (root / side / case / "source.rs").read_bytes() if (root / side / case / "source.rs").is_file() else None
    require(data is not None, f"missing {side}/{case}/source.rs")
    require(hashlib.sha256(data).hexdigest() == FIXTURES[case][0],
            f"{side}/{case} differs from candidate 1435539475fdaa7810bc2bc780fba0514f765f48")
    return data.decode("utf-8")


def verify_diagnostic_derivative(root: Path, side: str, case: str) -> None:
    folder = root / side / case
    original = (folder / "source.rs").read_bytes()
    marker = b" //~should_fail"
    require(original.count(marker) == 1,
            f"{side}/{case} exact fixture lacks one expected should_fail marker")
    derived = original.replace(marker, b"", 1)
    require((folder / "diagnostic-source.rs").read_bytes() == derived and
            derived.count(b"\n") == original.count(b"\n"),
            f"{side}/{case} diagnostic source changed more than marker")
    expected = hashlib.sha256(derived).hexdigest()
    require(read(folder / "diagnostic-source-sha256.txt").strip() == expected,
            f"{side}/{case} diagnostic source digest receipt differs")
    fixture = obj(folder / "fixture.json")
    require(fixture.get("diagnostic_source_sha256") == expected and
            fixture.get("diagnostic_source_path") == "diagnostic-source.rs" and
            fixture.get("diagnostic_line_count_preserved") is True and
            fixture.get("should_fail_marker_count_removed") == 1,
            f"{side}/{case} fixture derivative receipt differs")
    sidecar = obj(folder / "diagnostic-source.json")
    require(sidecar.get("original_sha256") == FIXTURES[case][0] and
            sidecar.get("diagnostic_sha256") == expected and
            sidecar.get("marker_count_removed") == 1 and
            sidecar.get("line_count_preserved") is True,
            f"{side}/{case} diagnostic derivative sidecar differs")


def verify_positive(root: Path, side: str, case: str) -> str:
    base = root / side / case
    log = read(base / "full-verification.log")
    require(status(base / "exit-status.txt") == 0, f"{side}/{case} did not exit 0")
    require(first_diagnostic(log) is None and SUCCESS.search(log) is not None,
            f"{side}/{case} has a verifier diagnostic or no complete success summary")
    body = target_log(log, FIXTURES[case][1])
    require("Executing return statement" in body and "Leak check." in body,
            f"{side}/{case} lacks target return/leak evidence")
    return body


def require_completed_control(log: str, body: str, label: str) -> None:
    # A false unwind post intentionally stops the function before normal return
    # and leak closure. The control must still reach its target and finish the
    # verifier run, which consumes the original should_fail marker.
    require(bool(body.strip()) and SUCCESS.search(log) is not None,
            f"{label} lacks target entry or complete verifier success summary")


def verify_baseline_forget(root: Path) -> None:
    base = root / "baseline/forget"
    log = read(base / "full-verification.log")
    require(status(base / "exit-status.txt") == 1, "baseline forget did not exit 1")
    body = target_log(log, "forget")
    diagnostic = first_diagnostic(log)
    require(diagnostic is not None and diagnostic[0] == "dead code" and
            target_location(diagnostic[1], "forget", 1),
            "baseline forget first diagnostic is not whole-function orphan dead code")
    require(body.find("Executing return statement") >= 0 and
            body.find("Leak check.") > body.find("Executing return statement") and
            body.find(diagnostic[1]) > body.find("Leak check."),
            "baseline forget did not reach normal return/leak before orphan dead code")
    require(not ERROR.search(log), "baseline forget has a separate verifier error")
    # The dead-code location is the whole function, never the statement in its body.
    require(len(DEAD.findall(log)) == 1, "baseline forget has extra dead-code diagnostics")


def verify_shared_log_paths(root: Path, side: str) -> None:
    log = read(root / side / "shared_cleanup/full-verification.log")
    for name in ("new", "ordinary_caller", "shared_cleanup"):
        body = target_log(log, name)
        require(body.count("Executing return statement") >= 2 and
                body.count("Leak check.") >= 2,
                f"{side}/shared_cleanup lacks both real outcomes and token/leak closure in {name}")


def verify_negative(root: Path, side: str, case: str, annotation: str) -> None:
    verify_diagnostic_derivative(root, side, case)
    source = verify_source(root, side, case)
    line = source_line(source, annotation)
    base = root / side / case
    log = read(base / "full-verification.log")
    require(status(base / "exit-status.txt") == 1, f"{side}/{case} diagnostic copy did not exit 1")
    body = target_log(log, FIXTURES[case][1])
    diagnostic = first_diagnostic(log)
    require(diagnostic is not None and diagnostic[0] == "error" and
            "Cannot prove false" in diagnostic[1] and
            target_location(diagnostic[1], case, line),
            f"{side}/{case} first diagnostic is not Cannot prove false at marked post")
    require(diagnostic[1] in body, f"{side}/{case} diagnostic predates target entry")
    require(len(ERROR.findall(log)) == 1 and not DEAD.search(log),
            f"{side}/{case} has additional errors or dead code")
    allow = read(base / "allow-full-verification.log")
    require(status(base / "allow-exit-status.txt") == 0,
            f"{side}/{case} allow_should_fail did not complete successfully")
    allow_body = target_log(allow, FIXTURES[case][1])
    require(first_diagnostic(allow) is None,
            f"{side}/{case} allow_should_fail has a verifier diagnostic")
    require(not DEAD.search(allow) and len(ERROR.findall(allow)) <= 1,
            f"{side}/{case} allow_should_fail has extra diagnostics")
    require_completed_control(allow, allow_body, f"{side}/{case} allow_should_fail")


def verify_dead_pre(root: Path, side: str) -> None:
    case = "dead_code_pre"
    base = root / side / case
    log = read(base / "full-verification.log")
    require(status(base / "exit-status.txt") == 1, f"{side} contradictory pre did not exit 1")
    body = target_log(log, FIXTURES[case][1])
    diagnostic = first_diagnostic(log)
    require(diagnostic is not None and diagnostic[0] == "dead code" and
            target_location(diagnostic[1], case, 1) and diagnostic[1] in body,
            f"{side} contradictory pre first diagnostic is not whole-function dead code")
    require(len(DEAD.findall(log)) >= 2,
            f"{side} contradictory pre lacks target-body dead-code diagnostics")
    require("Executing statement" not in body and "Executing return statement" not in body,
            f"{side} contradictory pre executed target body")
    require(not ERROR.search(log), f"{side} contradictory pre has another verifier error")


def mir_body(mir: str, name: str) -> str:
    found = list(re.finditer(r'(?m)^\s+defPath = "([^\"]+)"', mir))
    matches = [i for i, m in enumerate(found) if m.group(1) == name]
    require(len(matches) == 1, f"MIR target {name} absent or ambiguous")
    i = matches[0]
    return mir[found[i].start(): found[i + 1].start() if i + 1 < len(found) else len(mir)]


def mir_blocks(body: str) -> dict[int, str]:
    found = list(re.finditer(r"(?m)^\s{8}\( id = \(index = (\d+)\),", body))
    require(bool(found), "MIR basic blocks absent")
    result: dict[int, str] = {}
    for i, m in enumerate(found):
        key = int(m.group(1))
        require(key not in result, "duplicate MIR block id")
        result[key] = body[m.start(): found[i + 1].start() if i + 1 < len(found) else len(body)]
    return result


def call_record(body: str, callee: str) -> tuple[int | None, int, str]:
    # Bind the fnDef, type substitution, argument, unwind and target in one
    # terminator; matches in another statement or function cannot contribute.
    edges = []
    for block in mir_blocks(body).values():
        if "terminator = (" not in block:
            continue
        term = block.split("terminator = (", 1)[1].split("isCleanup =", 1)[0]
        if "kind = (" not in term or "call = (" not in term:
            continue
        for m in re.finditer(r'fnDef = \(\s*id = \(\s*name = "([^\"]+)"', term):
            if m.group(1) != callee:
                continue
            tail = term[m.end():]
            action = re.search(r"unwindAction = \((cleanup = \(index = (\d+)\)|continue = void)\).*?target = \(something = \(index = (\d+)\)\)", tail, re.S)
            require(action is not None, f"MIR {callee} lacks explicit unwind action/normal target")
            edges.append((int(action.group(2)) if action.group(2) else None,
                          int(action.group(3)), term))
    require(len(edges) == 1, f"MIR {callee} call absent or ambiguous")
    return edges[0]


def call_edge(body: str, callee: str) -> tuple[int | None, int]:
    cleanup, target, _ = call_record(body, callee)
    return cleanup, target


def ast_function(ast: str, name: str) -> str:
    found = list(re.finditer(r"(?m)^\s{4}Func \(loc [^\n]+", ast))
    matches = [i for i, m in enumerate(found) if re.search(r'"' + re.escape(name) + r'"', m.group())]
    require(len(matches) == 1, f"AST function {name} absent or ambiguous")
    i = matches[0]
    return ast[found[i].start():found[i + 1].start() if i + 1 < len(found) else len(ast)]


def ast_body(ast: str, name: str) -> str:
    fn = ast_function(ast, name)
    marker = "false, Some ((["
    require(marker in fn, f"AST function {name} has no body")
    return fn.split(marker, 1)[1]


def verify_mir_ast(root: Path) -> dict:
    cap = root / "captures"
    findings = {}
    for case in ("forget", "shared_cleanup"):
        folder = cap / case
        normal = read(folder / "normal-mir.txt")
        readonly = read(folder / "readonly-mir.txt")
        require(normal == readonly, f"{case} NORMAL/readonly decoded MIR differ")
        if case == "forget":
            require(normal == read(folder / "baseline-normal-mir.txt"),
                    "forget baseline/candidate MIR changed; normal assignment/target is not preserved")
        ast = read(folder / "verified-ast.txt")
        body = mir_body(normal, case)
        md_cleanup, md_target, md_term = call_record(body, "std::mem::ManuallyDrop::<T>::new")
        md_edge = (md_cleanup, md_target)
        require(re.search(r'substs = \[.*?param = "T"', md_term, re.S) is not None and
                re.search(r'args = \[\s*\( move = \(', md_term) is not None,
                f"{case} lacks typed MDnew Move<T> argument")
        blocks = mir_blocks(body)
        require(md_edge[1] in blocks, f"{case} MDnew normal target absent")
        if case == "forget":
            require(md_edge[0] is not None and md_edge[0] in blocks and
                    "isCleanup = true" in blocks[md_edge[0]] and
                    "unwindResume = void" in blocks[md_edge[0]],
                    "forget MIR cleanup shape differs")
            candidate = ast_body(ast, "forget")
            require('"returning"' in candidate and
                    not re.search(r'ReturnStmt .*?"unwinding"', candidate) and
                    not re.search(r'LabelStmt \([^\n]*"' + str(md_edge[0]) + r'"', candidate),
                    "forget caller AST has missing normal path or orphan unwind return")
            baseline_ast = root / "captures/forget/baseline-verified-ast.txt"
            old = ast_body(read(baseline_ast), "forget")
            require(re.search(r'GotoStmt \([^\n]*"' + str(md_edge[1]) + r'"', old) is not None and
                    re.search(r'LabelStmt \([^\n]*"' + str(md_edge[0]) +
                              r'"\);\s*ReturnStmt \([^\n]*"unwinding"', old) is not None and
                    re.search(r'GotoStmt \([^\n]*"' + str(md_edge[0]) + r'"', old) is None,
                    "baseline AST lacks concrete orphan cleanup beside preserved normal goto")
            assignments = lambda text: re.findall(r"(?m)^\s*ExprStmt \(AssignExpr [^\n]+", text)
            require(assignments(old) and assignments(old) == assignments(candidate),
                    "forget caller's normal assignments changed between baseline and candidate AST")
            findings[case] = {"mdnew_cleanup": md_edge[0], "normal_target": md_edge[1],
                              "baseline_ast_checked": True}
        else:
            ordinary = call_edge(body, "new")
            require(md_edge[0] is not None and md_edge[0] == ordinary[0] and
                    ordinary[1] in blocks and md_edge[0] in blocks and
                    "isCleanup = true" in blocks[md_edge[0]] and
                    "unwindResume = void" in blocks[md_edge[0]],
                    "shared caller calls do not retain one real cleanup/UnwindResume")
            caller = ast_body(ast, "shared_cleanup")
            label = str(md_edge[0])
            new_switch = re.search(r'SwitchStmt \(loc "([^"]+)", CallExpr \(loc "[^"]+", "new"', caller)
            switch_loc = re.escape(new_switch.group(1)) if new_switch else "<missing>"
            unwind_arm = re.search(r'SwitchStmtClause \(loc "' + switch_loc +
                                   r'"[^\n]*"unwinding"[^\n]*GotoStmt \([^\n]*"' +
                                   re.escape(label) + r'"', caller)
            returning_arm = re.search(r'SwitchStmtClause \(loc "' + switch_loc +
                                      r'"[^\n]*"returning"', caller)
            cleanup_return = re.search(r'LabelStmt \([^\n]*"' + re.escape(label) + r'"\);\s*ReturnStmt \([^\n]*"unwinding"', caller)
            require(new_switch is not None and returning_arm is not None and
                    unwind_arm is not None and cleanup_return is not None,
                    "shared caller AST lacks ordinary new unwind arm to retained cleanup return")
            # Ordinary caller must have its own Continue action, independently of shared caller.
            ordinary_mir = mir_body(normal, "ordinary_caller")
            cont, _ = call_edge(ordinary_mir, "new")
            ordinary_ast = ast_body(ast, "ordinary_caller")
            ordinary_switch = re.search(r'SwitchStmt \(loc "([^"]+)", CallExpr \(loc "[^"]+", "new"', ordinary_ast)
            ordinary_loc = re.escape(ordinary_switch.group(1)) if ordinary_switch else "<missing>"
            require(cont is None and ordinary_switch is not None and
                    re.search(r'SwitchStmtClause \(loc "' + ordinary_loc +
                              r'"[^\n]*"returning"', ordinary_ast) is not None and
                    re.search(r'SwitchStmtClause \(loc "' + ordinary_loc +
                              r'"[^\n]*"unwinding"[^\n]*ReturnStmt \([^\n]*"unwinding"',
                              ordinary_ast) is not None,
                    "ordinary caller lacks direct Continue unwind switch/return")
            findings[case] = {"shared_cleanup": md_edge[0], "mdnew_target": md_edge[1],
                              "ordinary_target": ordinary[1], "ordinary_caller_continue": True}
    return findings


def audit(root: Path) -> dict:
    root = root.resolve()
    provenance = verify_provenance(root)
    for case in FIXTURES:
        for side in ("baseline", "candidate"):
            verify_source(root, side, case)
    for case in FIXTURES:
        for side in ("baseline", "candidate"):
            verify_capture_status(root, case, side, provenance)
        folder = root / "captures" / case
        normal = read(folder / "normal-mir.txt")
        require(normal == read(folder / "readonly-mir.txt") and
                normal == read(folder / "baseline-normal-mir.txt") and
                normal == read(folder / "baseline-readonly-mir.txt"),
                f"{case} decoded NORMAL/readonly or baseline/candidate MIR differs")
    verify_baseline_forget(root)
    verify_positive(root, "candidate", "forget")
    verify_positive(root, "baseline", "shared_cleanup")
    verify_positive(root, "candidate", "shared_cleanup")
    verify_shared_log_paths(root, "baseline")
    verify_shared_log_paths(root, "candidate")
    verify_negative(root, "candidate", "false_normal_post", "//@ ens false;")
    verify_negative(root, "candidate", "shared_false_unwind", "//@ on_unwind_ens false;")
    # Baseline may stop at the old CFG defect for false_normal_post.
    verify_negative(root, "baseline", "shared_false_unwind", "//@ on_unwind_ens false;")
    verify_dead_pre(root, "baseline")
    verify_dead_pre(root, "candidate")
    structure = verify_mir_ast(root)
    return {"classification": "FOCUSED_GATE_PASS", "accepted": True,
            "fixture_commit": "1435539475fdaa7810bc2bc780fba0514f765f48",
            "structure": structure, "provenance": provenance,
            "scope": "five focused fixtures only; no consumer or upstream acceptance"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--output", type=Path, help="write JSON result here")
    args = parser.parse_args()
    try:
        result = audit(args.evidence)
        code = 0
    except AuditIssue as ex:
        result = {"classification": ex.classification, "accepted": False, "reason": str(ex)}
        code = 2 if ex.classification == "INCONCLUSIVE" else 1
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError) as ex:
        result = {"classification": "INCONCLUSIVE", "accepted": False, "reason": str(ex)}
        code = 2
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    sys.stdout.write(rendered)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
