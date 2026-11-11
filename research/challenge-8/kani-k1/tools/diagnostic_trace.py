"""Bounded, summary-only reader for the opt-in KANI3300 compile-time JSONL sidecars."""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import re
from pathlib import Path
from typing import Any

SCHEMA = "kani3300-trace-v1"
STAGE = "kani3300-t1b"
MAX_RECORD_BYTES = 2048
MAX_RUN_BYTES = 1024 * 1024
MAX_INVOCATION_BYTES = 256 * 1024
MAX_PRODUCER_INVOCATION_BYTES = 250 * 1024
MAX_INVOCATION_RECORDS = 512
MAX_RUN_RECORDS = 4096
MAX_SIDECARS = 128
MAX_ERRORS = 16
MAX_PAGE_RECORDS = 20
MAX_PAGE_BYTES = 12000
INVOCATION_SCOPE = "scripts/run-kani.sh argv at lane executor boundary; internal Kani/rustc/CBMC argv unknown"
CONTROL_CFG = "kani_smallsort_controls"
FILTER_MODE = "semicolon-literal-substring"


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha_json(value: Any) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def _retain_footer(raw: bytes) -> dict[str, Any]:
    """Retain only bounded footer counters, independently of sidecar acceptance.

    This is an unvalidated source observation, never coverage/proof credit. The caller
    binds it to the sidecar hash; malformed fields are named without retaining payload.
    """
    line = raw.rstrip(b"\n").rsplit(b"\n", 1)[-1]
    result: dict[str, Any] = {"status": "UNAVAILABLE", "data": None}
    if not line or len(line) > MAX_RECORD_BYTES:
        result["error"] = "last row missing or exceeds 2048 bytes"
        return result
    result["line_sha256"] = hashlib.sha256(line).hexdigest()
    try:
        row = json.loads(line)
    except (ValueError, UnicodeError, RecursionError):
        result["error"] = "last row is not valid bounded JSON"
        return result
    if not isinstance(row, dict) or row.get("kind") != "footer" or not isinstance(row.get("data"), dict):
        result["error"] = "last row is not a footer object"
        return result
    data = row["data"]
    retained: dict[str, Any] = {}
    malformed = []
    for key in ("state", "seen_records", "emitted_records", "omitted_records",
                "omitted_bytes", "bytes_before_footer", "coverage", "omission_counts"):
        if key == "omitted_bytes" and key not in data:
            continue
        value = data.get(key)
        if key == "state":
            valid = isinstance(value, str) and re.fullmatch(r"[A-Z_]{1,64}", value) is not None
        elif key in ("coverage", "omission_counts"):
            valid = isinstance(value, dict) and all(re.fullmatch(r"[A-Za-z0-9_]{1,128}", k)
                                                   and type(v) is int for k, v in value.items())
        else:
            valid = type(value) is int
        retained[key] = value if valid else None
        if not valid:
            malformed.append(key)
    result.update(status="UNVALIDATED", data=retained, malformed_fields=malformed)
    return result


def _coverage_incomplete(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            name = str(key).lower()
            if name.startswith("omitted") and type(child) is int and child > 0:
                return True
            if name in ("complete", "is_complete") and child is False:
                return True
            if name in ("partial", "incomplete") and child is True:
                return True
            if name == "state" and isinstance(child, str) and child.upper() not in ("COMPLETE", "OK"):
                return True
            if _coverage_incomplete(child):
                return True
    elif isinstance(value, list):
        return any(_coverage_incomplete(child) for child in value)
    return False


def _validate_context(value: Any) -> None:
    if not isinstance(value, dict) or set(value) != {"root", "stage", "unit"}:
        raise ValueError("trace context must contain exactly root, stage, unit")
    if (not isinstance(value["root"], str) or len(value["root"].encode("utf-8")) > 320
            or not isinstance(value["stage"], str) or len(value["stage"].encode("utf-8")) > 64):
        raise ValueError("trace context root/stage type or byte limit invalid")
    unit = value["unit"]
    if unit is not None and (type(unit) is not int or unit < 0):
        raise ValueError("trace context unit must be null or a non-negative integer")


def _validate_trace_identity_envelope(summary: dict[str, Any]) -> dict[str, Any]:
    """Validate source, request, and target identities before exposing any trace page."""
    trace = summary.get("diagnostic_trace")
    if not isinstance(trace, dict):
        raise ValueError("summary has no diagnostic_trace object")
    identity = trace.get("identity")
    source = trace.get("source_identity")
    request_sha = summary.get("request_sha256")
    head = summary.get("head_sha")
    run_id = (summary.get("run") or {}).get("id")
    kani_commit = summary.get("kani_commit")
    kani_build = summary.get("kani_build")
    if (trace.get("schema") != "kani3300-diagnostic-trace-v1" or not isinstance(identity, dict)
            or not isinstance(source, dict)):
        raise ValueError("diagnostic trace schema or identity envelope missing")
    required = ("build_id", "head_sha", "request_sha256", "library_tree", "actual_library_tree",
                "base_pin", "kani_commit", "patch_sha256", "applied_tree", "expected_applied_tree",
                "tooling_sha256", "effective_argv", "effective_env", "argv_sha256", "env_sha256",
                "filters", "filter_sha256", "trace_schema", "trace_stage", "argv_scope", "cwd")
    if any(key not in identity for key in required):
        raise ValueError("diagnostic trace identity fields missing")
    if (not isinstance(run_id, str) or identity["build_id"] != run_id
            or identity["head_sha"] != head or identity["request_sha256"] != request_sha):
        raise ValueError("diagnostic trace build/head/request identity mismatch")
    if (source.get("trace_id") != request_sha or source.get("stage") != STAGE
            or source.get("schema") != SCHEMA or source.get("filter_sha256") != identity.get("filter_sha256")
            or source.get("filter_mode") != FILTER_MODE
            or identity.get("trace_stage") != STAGE or identity.get("trace_schema") != SCHEMA):
        raise ValueError("diagnostic trace source/stage/schema identity mismatch")
    if (not isinstance(request_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", request_sha)
            or not isinstance(head, str) or not re.fullmatch(r"[0-9a-f]{40}", head)):
        raise ValueError("outer request/head identity is malformed")
    if (not isinstance(kani_commit, str) or identity.get("base_pin") != kani_commit
            or identity.get("kani_commit") != kani_commit):
        raise ValueError("diagnostic trace Kani pin identity mismatch")
    if not isinstance(kani_build, dict):
        raise ValueError("outer Kani build identity missing")
    patch = kani_build.get("patch")
    patch_sha = patch.get("sha256") if isinstance(patch, dict) else None
    applied_tree = kani_build.get("tree")
    if (identity.get("patch_sha256") != patch_sha or identity.get("applied_tree") != applied_tree
            or identity.get("expected_applied_tree") != applied_tree):
        raise ValueError("diagnostic trace patch/applied-tree identity mismatch")
    if identity.get("actual_library_tree") != identity.get("library_tree"):
        raise ValueError("diagnostic trace library-tree identity mismatch")
    if (not isinstance(identity.get("tooling_sha256"), dict)
            or identity.get("tooling_sha256") != summary.get("tooling_sha256")
            or not isinstance(identity.get("effective_argv"), list)
            or any(not isinstance(arg, str) for arg in identity["effective_argv"])
            or not isinstance(identity.get("effective_env"), dict)):
        raise ValueError("diagnostic trace tooling/argv/env identity malformed")
    if identity.get("argv_sha256") != _sha_json(identity["effective_argv"]):
        raise ValueError("diagnostic trace argv digest mismatch")
    if identity.get("env_sha256") != _sha_json(identity["effective_env"]):
        raise ValueError("diagnostic trace env digest mismatch")
    filters = identity.get("filters")
    if (not isinstance(filters, list) or not filters or any(not isinstance(item, str) for item in filters)
            or any(not re.fullmatch(r"[A-Za-z0-9_:.$<>-]{1,300}", item) for item in filters)
            or sum(len(item.encode()) for item in filters) + len(filters) - 1 > 900
            or identity.get("filter_sha256") != hashlib.sha256(";".join(filters).encode()).hexdigest()
            or identity["effective_env"].get("KANI3300_TRACE_FILTER") != ";".join(filters)
            or identity["effective_env"].get("KANI3300_TRACE_ID") != request_sha
            or identity["effective_env"].get("KANI3300_TRACE_STAGE") != STAGE
            or not identity["effective_env"].get("KANI3300_TRACE_DIR")):
        raise ValueError("diagnostic trace filter/environment identity malformed")
    argv = identity["effective_argv"]
    env = identity["effective_env"]
    if (identity.get("argv_scope") != INVOCATION_SCOPE or not isinstance(identity.get("cwd"), str)
            or not os.path.isabs(identity["cwd"]) or len(argv) < 5
            or argv[:4] != ["scripts/run-kani.sh", "--path", identity["cwd"], "--kani-args"]
            or not isinstance(env.get("RUSTFLAGS"), (str, type(None)))
            or (isinstance(env.get("RUSTFLAGS"), str) and len(env["RUSTFLAGS"].encode()) > 4096)):
        raise ValueError("diagnostic trace invocation scope/cwd missing")
    state = trace.get("state")
    complete = trace.get("complete")
    if state == "COMPLETE":
        if complete is not True or trace.get("omitted") != 0:
            raise ValueError("diagnostic trace COMPLETE state has omissions or incomplete flag")
    elif complete is not False:
        raise ValueError("incomplete diagnostic trace must explicitly set complete=false")
    records = trace.get("records")
    seen, emitted, omitted = (trace.get(key) for key in ("seen", "emitted", "omitted"))
    if (not isinstance(records, list) or any(type(n) is not int or n < 0 for n in (seen, emitted, omitted))
            or emitted != len(records) or seen != emitted + omitted):
        raise ValueError("diagnostic trace record counters inconsistent")
    sidecars = trace.get("sidecars")
    if not isinstance(sidecars, list) or len(sidecars) > MAX_SIDECARS:
        raise ValueError("diagnostic trace sidecar identity list missing/oversized")
    for sidecar in sidecars:
        if (not isinstance(sidecar, dict) or not isinstance(sidecar.get("file"), str)
                or not sidecar["file"].startswith("kani3300-trace-")
                or not sidecar["file"].endswith(".jsonl") or not isinstance(sidecar.get("status"), str)):
            raise ValueError("diagnostic trace sidecar identity malformed")
        if sidecar["status"] == "READ":
            if (type(sidecar.get("bytes")) is not int or sidecar["bytes"] < 0
                    or not isinstance(sidecar.get("sha256"), str)
                    or not re.fullmatch(r"[0-9a-f]{64}", sidecar["sha256"])):
                raise ValueError("diagnostic trace sidecar content hash malformed")
        elif sidecar.get("sha256") is not None:
            raise ValueError("unread sidecar cannot claim a complete content hash")
    coverage = trace.get("coverage")
    if not isinstance(coverage, list):
        raise ValueError("diagnostic trace coverage summary missing")
    if state == "COMPLETE":
        if (not coverage or any(not isinstance(item, dict) or item.get("state") != "COMPLETE"
                                or item.get("omitted") != 0 or item.get("seen") != item.get("emitted")
                                or not isinstance(item.get("coverage"), dict)
                                or any(type(v) is not int or v < 0 for v in item["coverage"].values())
                                or sum(v for v in item["coverage"].values() if type(v) is int) != item.get("emitted")
                                or not isinstance(item.get("omission_counts"), dict)
                                or any(type(v) is not int or v != 0 for v in item["omission_counts"].values())
                                for item in coverage)):
            raise ValueError("diagnostic trace coverage summary incomplete")
    return identity


def validate_trace_page_identity(summary: dict[str, Any]) -> dict[str, Any]:
    identity = _validate_trace_identity_envelope(summary)
    if summary["diagnostic_trace"].get("state") == "INVALID":
        raise ValueError("diagnostic trace state INVALID; pages withheld")
    return identity


def invocation_manifest_errors(manifest: Any, *, build_id: str | None, head_sha: str | None,
                               request_sha256: str | None, request: dict[str, Any],
                               trace_dir: Path, expected_argv: list[str]) -> list[str]:
    errors: list[str] = []
    if not isinstance(manifest, dict) or manifest.get("schema") != "kani3300-invocation-v1":
        return ["invocation manifest missing or schema mismatch"]
    if manifest.get("valid") is not True or not isinstance(manifest.get("errors"), list):
        errors.append("invocation manifest is marked invalid")
    if manifest.get("errors"):
        errors.extend(str(error)[:180] for error in manifest["errors"][:4])
    if (manifest.get("build_id") != build_id or manifest.get("head_sha") != head_sha
            or manifest.get("request_sha256") != request_sha256):
        errors.append("invocation manifest build/head/request identity mismatch")
    argv_for_cwd = manifest.get("argv")
    argv_cwd = argv_for_cwd[2] if isinstance(argv_for_cwd, list) and len(argv_for_cwd) >= 3 else None
    if manifest.get("argv_scope") != INVOCATION_SCOPE or manifest.get("cwd") != argv_cwd:
        errors.append("invocation manifest scope/cwd mismatch")
    if not isinstance(manifest.get("cwd"), str) or not os.path.isabs(manifest["cwd"]):
        errors.append("invocation manifest cwd is not absolute")
    argv = manifest.get("argv")
    if not isinstance(argv, list) or argv != expected_argv:
        errors.append("invocation manifest argv differs from validated runner argv")
    if not isinstance(manifest.get("kani_args"), list) or manifest.get("kani_args") != expected_argv[4:]:
        errors.append("invocation manifest Kani argument vector differs from runner argv")
    if manifest.get("argv_sha256") != _sha_json(argv):
        errors.append("invocation manifest argv digest mismatch")
    env = manifest.get("effective_env")
    required_env = {"RUSTFLAGS", "KANI3300_TRACE_DIR", "KANI3300_TRACE_FILTER", "KANI3300_TRACE_ID", "KANI3300_TRACE_STAGE"}
    if not isinstance(env, dict) or set(env) != required_env:
        errors.append("invocation manifest effective environment fields missing/extra")
        env = env if isinstance(env, dict) else {}
    rustflags = env.get("RUSTFLAGS")
    if rustflags is not None and (not isinstance(rustflags, str) or len(rustflags.encode()) > 4096):
        errors.append("invocation manifest RUSTFLAGS malformed or oversized")
    if request.get("controls") and rustflags != f"--cfg {CONTROL_CFG}":
        errors.append("invocation manifest RUSTFLAGS differs from controls request")
    trace = request["diagnostic_trace"]
    expected_env = {"KANI3300_TRACE_DIR": str(trace_dir.resolve()),
                    "KANI3300_TRACE_FILTER": ";".join(trace["filters"]),
                    "KANI3300_TRACE_ID": request_sha256, "KANI3300_TRACE_STAGE": STAGE}
    if any(env.get(key) != value for key, value in expected_env.items()):
        errors.append("invocation manifest trace environment differs from request")
    if manifest.get("env_sha256") != _sha_json(env):
        errors.append("invocation manifest env digest mismatch")
    return errors


def collect_trace(directory: Path, *, build_id: str | None, head_sha: str | None,
                  request_sha256: str | None, request: dict[str, Any], kani_commit: str | None,
                  kani_build: dict[str, Any] | None, tooling: dict[str, str],
                  build_outcome: str | None, actual_library_tree: str | None,
                  invocation: dict[str, Any] | None = None,
                  invocation_errors: list[str] | None = None) -> dict[str, Any]:
    """Read only compiler-produced JSONL files. Every failure is retained as diagnostic state."""
    expected_id = request_sha256
    request_trace = request["diagnostic_trace"]
    filters = request_trace["filters"]
    trace: dict[str, Any] = {
        "schema": "kani3300-diagnostic-trace-v1", "diagnostic_only": True,
        "state": "INCOMPLETE", "complete": False, "records": [], "seen": 0, "emitted": 0,
        "omitted": 0, "omitted_bytes": 0, "errors": [], "coverage": [], "sidecars": [], "footers": [],
        "source_identity": {"trace_id": expected_id, "stage": STAGE, "schema": SCHEMA,
                            "filter_mode": FILTER_MODE,
                            "filter_sha256": hashlib.sha256(";".join(filters).encode()).hexdigest()},
        "identity": {
            "build_id": build_id, "head_sha": head_sha, "request_sha256": request_sha256,
            "library_tree": request_trace["library_tree"], "actual_library_tree": actual_library_tree,
            "base_pin": request_trace["base_pin"],
            "kani_commit": kani_commit,
            "patch_sha256": (request.get("kani_patch") or {}).get("sha256"),
            "applied_tree": (kani_build or {}).get("tree"),
            "expected_applied_tree": request_trace["expected_applied_tree"],
            "tooling_sha256": tooling,
            "effective_argv": (invocation or {}).get("argv", []),
            "effective_env": (invocation or {}).get("effective_env", {}),
            "argv_sha256": (invocation or {}).get("argv_sha256"),
            "env_sha256": (invocation or {}).get("env_sha256"),
            "argv_scope": (invocation or {}).get("argv_scope"),
            "cwd": (invocation or {}).get("cwd"),
            "filters": filters,
            "filter_sha256": hashlib.sha256(";".join(filters).encode()).hexdigest(),
            "trace_schema": SCHEMA, "trace_stage": STAGE,
        },
    }
    identity_errors = []
    if actual_library_tree != request_trace["library_tree"]:
        identity_errors.append("actual library tree differs from request")
    if kani_commit != request_trace["base_pin"]:
        identity_errors.append("actual Kani base pin differs from request")
    if (kani_build or {}).get("tree") != request_trace["expected_applied_tree"]:
        identity_errors.append("actual applied Kani tree differs from request")
    identity_errors.extend(invocation_errors or [])
    if invocation is None:
        identity_errors.append("actual invocation manifest missing")
    trace["errors"].extend(identity_errors)
    files = sorted(itertools.islice(directory.glob("kani3300-trace-*.jsonl"), MAX_SIDECARS + 1)) if directory.is_dir() else []
    excess_files = len(files) > MAX_SIDECARS
    files = files[:MAX_SIDECARS]
    if not files:
        trace["state"] = "INVALID" if identity_errors else ("TIMEOUT" if build_outcome == "timeout" else "MISSING")
        trace["errors"].append("no compiler trace sidecars found")
        return trace

    all_records: list[dict[str, Any]] = []
    total_bytes = 0
    total_seen = total_emitted = total_omitted = total_omitted_bytes = 0
    omitted_bytes_known = True
    states: list[str] = []
    invocations: list[str] = []
    for path in files:
        if path.is_symlink():
            trace["sidecars"].append({"file": path.name, "bytes": None, "sha256": None, "status": "SYMLINK"})
            trace["errors"].append("sidecar is a symlink")
            states.append("INVALID")
            continue
        try:
            size = path.stat().st_size
            if size > MAX_INVOCATION_BYTES:
                trace["sidecars"].append({"file": path.name, "bytes": size, "sha256": None,
                                          "status": "NOT_READ_INVOCATION_CAP"})
                trace["errors"].append(f"{path.name}: sidecar exceeds 256 KiB invocation cap")
                states.append("OVERSIZED")
                continue
            if total_bytes + size > MAX_RUN_BYTES:
                trace["sidecars"].append({"file": path.name, "bytes": size, "sha256": None,
                                          "status": "NOT_READ_RUN_CAP"})
                trace["errors"].append("aggregate sidecar bytes exceed 1 MiB")
                states.append("OVERSIZED")
                break
            with path.open("rb") as stream:
                raw = stream.read(MAX_RUN_BYTES - total_bytes + 1)
            if len(raw) > MAX_RUN_BYTES - total_bytes:
                trace["sidecars"].append({"file": path.name, "bytes": size, "sha256": None,
                                          "prefix_bytes": len(raw),
                                          "prefix_sha256": hashlib.sha256(raw).hexdigest(),
                                          "status": "PARTIAL_READ_RUN_CAP"})
                trace["errors"].append("aggregate sidecar bytes exceed 1 MiB")
                states.append("OVERSIZED")
                break
        except OSError as exc:
            if not any(item.get("file") == path.name for item in trace["sidecars"]):
                trace["sidecars"].append({"file": path.name, "bytes": None, "sha256": None,
                                          "status": f"READ_ERROR:{type(exc).__name__}"})
            trace["errors"].append(f"sidecar read failed: {type(exc).__name__}")
            states.append("INVALID")
            continue
        trace["sidecars"].append({"file": path.name, "bytes": len(raw),
                                  "sha256": hashlib.sha256(raw).hexdigest(), "status": "READ"})
        # Persist in summary.json (already uploaded by the recipe) BEFORE validation can
        # reject any row. Do not promote source footer counts into accepted coverage.
        trace["footers"].append({"file": path.name, "sidecar_sha256": hashlib.sha256(raw).hexdigest(),
                                 **_retain_footer(raw)})
        total_bytes += len(raw)
        if total_bytes > MAX_RUN_BYTES:
            trace["errors"].append("aggregate sidecar bytes exceed 1 MiB")
            states.append("OVERSIZED")
            break
        try:
            line_count = raw.count(b"\n") + (not raw.endswith(b"\n"))
            if line_count > MAX_INVOCATION_RECORDS:
                trace["errors"].append(f"{path.name}: JSONL rows exceed per-invocation cap 512 including header/footer")
                states.append("OVERSIZED")
                continue
            if not raw.endswith(b"\n"):
                raise ValueError("sidecar must end with newline-delimited footer")
            lines = raw.split(b"\n")[:-1]
            if not lines:
                raise ValueError("empty sidecar")
            rows = []
            for line in lines:
                if len(line) > MAX_RECORD_BYTES:
                    raise ValueError("record exceeds 2048 bytes")
                item = json.loads(line)
                if not isinstance(item, dict):
                    raise ValueError("record is not an object")
                rows.append(item)
            if len(rows) == 1 and rows[0].get("kind") == "overflow":
                overflow = rows[0]
                if (overflow.get("schema") != SCHEMA or overflow.get("trace_id") != expected_id
                        or overflow.get("stage") != STAGE or type(overflow.get("seq")) is not int
                        or not isinstance(overflow.get("invocation"), str)
                        or overflow.get("data", {}).get("state") != "OVERSIZED"
                        or overflow.get("data", {}).get("omitted_invocations") != "one-or-more"):
                    raise ValueError("overflow sentinel identity/state mismatch")
                states.append("OVERSIZED")
                trace["coverage"].append({"state": "OVERSIZED", "omitted_invocations": "one-or-more"})
                if len(trace["errors"]) < MAX_ERRORS:
                    trace["errors"].append("producer run cap emitted an overflow sentinel")
                continue
            if len(rows) < 2:
                raise ValueError("sidecar missing header/footer")
            header, footer = rows[0], rows[-1]
            if (header.get("schema") != SCHEMA or header.get("kind") != "header"
                    or header.get("trace_id") != expected_id or header.get("stage") != STAGE):
                raise ValueError("header schema/trace identity/stage mismatch")
            invocation = header.get("invocation")
            if not isinstance(invocation, str) or not invocation or invocation in invocations:
                raise ValueError("missing or duplicate invocation identity")
            invocations.append(invocation)
            if (footer.get("schema") != SCHEMA or footer.get("kind") != "footer"
                    or footer.get("trace_id") != expected_id or footer.get("stage") != STAGE
                    or footer.get("invocation") != invocation):
                raise ValueError("footer schema/trace identity/stage mismatch")
            hdata = header.get("data")
            if (not isinstance(hdata, dict) or hdata.get("filters") != filters
                    or hdata.get("filter_mode") != FILTER_MODE
                    or not isinstance(hdata.get("limits"), dict)
                    or hdata["limits"].get("records") != MAX_INVOCATION_RECORDS
                    or hdata["limits"].get("record_bytes") != MAX_RECORD_BYTES
                    or hdata["limits"].get("invocation_bytes") != MAX_PRODUCER_INVOCATION_BYTES):
                raise ValueError("source literal filter identity mismatch")
            if any(row.get("schema") != SCHEMA or row.get("trace_id") != expected_id
                   or row.get("stage") != STAGE or row.get("invocation") != invocation
                   or type(row.get("seq")) is not int or not isinstance(row.get("kind"), str)
                   or not isinstance(row.get("data"), dict) for row in rows):
                raise ValueError("record identity/schema/type mismatch")
            context_presence = ["context" in row for row in rows]
            if any(context_presence) and not all(context_presence):
                raise ValueError("trace context missing from some invocation rows")
            for row in rows:
                if "context" in row:
                    _validate_context(row["context"])
            records = rows[1:-1]
            if any(row.get("kind") in ("header", "footer") for row in records):
                raise ValueError("unexpected internal header/footer record")
            if ([row["seq"] for row in rows] != list(range(len(rows)))
                    or [row["seq"] for row in records] != list(range(1, len(records) + 1))):
                raise ValueError("record sequence is partial or reordered")
            fdata = footer.get("data")
            if not isinstance(fdata, dict) or fdata.get("state") not in ("COMPLETE", "PARTIAL", "OVERSIZED", "IO_ERROR"):
                raise ValueError("footer state/counters missing")
            seen, emitted, omitted = (fdata.get(k) for k in ("seen_records", "emitted_records", "omitted_records"))
            if any(type(n) is not int or n < 0 for n in (seen, emitted, omitted)) or emitted != len(records) or seen != emitted + omitted:
                raise ValueError("footer record counts inconsistent")
            if emitted > MAX_INVOCATION_RECORDS - 2:
                trace["errors"].append(f"{path.name}: footer payload exceeds 510 records after header/footer")
                states.append("OVERSIZED")
                continue
            total_seen += seen
            total_emitted += emitted
            total_omitted += omitted
            if type(fdata.get("omitted_bytes")) is int and fdata["omitted_bytes"] >= 0:
                total_omitted_bytes += fdata["omitted_bytes"]
            else:
                omitted_bytes_known = False
            bytes_before_footer = sum(len(line) + 1 for line in lines[:-1])
            if fdata.get("bytes_before_footer") != bytes_before_footer:
                raise ValueError("footer bytes_before_footer does not match raw JSONL prefix")
            coverage = fdata.get("coverage")
            omission_counts = fdata.get("omission_counts")
            if (not isinstance(coverage, dict) or any(type(v) is not int or v < 0 for v in coverage.values())
                    or sum(coverage.values()) != emitted or not isinstance(omission_counts, dict)
                    or any(type(v) is not int or v < 0 for v in omission_counts.values())
                    # The producer also counts clipped bytes, lines and witness payloads here.
                    # Only these two categories count serialized records omitted by write_record.
                    or sum(omission_counts.get(k, 0) for k in ("record_cap", "oversized_records")) != omitted):
                raise ValueError("footer coverage does not bind emitted event count")
            if (fdata["state"] == "COMPLETE" and
                    (omitted != 0 or seen != emitted or bool(omission_counts) or _coverage_incomplete(coverage))):
                raise ValueError("footer claims COMPLETE with omitted/incomplete coverage")
            states.append(fdata["state"])
            trace["coverage"].append({"invocation": invocation, "state": fdata["state"],
                                      "seen": seen, "emitted": emitted, "omitted": omitted,
                                      "coverage": coverage, "omission_counts": omission_counts})
            room = max(0, MAX_RUN_RECORDS - len(all_records))
            retained = records[:room]
            dropped = len(records) - len(retained)
            all_records.extend({"invocation": invocation, "seq": row["seq"], "kind": row["kind"],
                                **({"context": row["context"]} if "context" in row else {}),
                                "data": row["data"]} for row in retained)
            if dropped:
                total_omitted += dropped
                states.append("OVERSIZED")
                if len(trace["errors"]) < MAX_ERRORS:
                    trace["errors"].append(f"summary reader retained at most {MAX_RUN_RECORDS} aggregate records")
        except (ValueError, TypeError, AttributeError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
            if len(trace["errors"]) < MAX_ERRORS:
                trace["errors"].append(f"{path.name}: {str(exc)[:180]}")
            states.append("INVALID")
    if excess_files:
        trace["errors"].append("more than 128 sidecars; enumeration bounded")
        states.append("OVERSIZED")
    trace["records"] = all_records
    trace["seen"], trace["emitted"] = total_seen, len(all_records)
    trace["omitted"] = max(total_omitted, total_seen - len(all_records))
    trace["omitted_bytes"] = total_omitted_bytes if omitted_bytes_known else None
    trace["sidecar_bytes"] = total_bytes
    trace["invocations"] = invocations
    if "INVALID" in states or identity_errors:
        state = "INVALID"
    elif build_outcome == "timeout":
        state = "TIMEOUT"
    elif "OVERSIZED" in states:
        state = "OVERSIZED"
    elif not states or any(s != "COMPLETE" for s in states) or total_omitted:
        state = "PARTIAL"
    else:
        state = "COMPLETE"
    trace["state"] = state
    trace["complete"] = state == "COMPLETE"
    return trace


def trace_field_page(summary: dict[str, Any], path: str, start: int, count: int,
                     expected_build_id: str | None = None) -> str:
    """Render one bounded field page; callers must continue only with returned next_start."""
    if not isinstance(summary, dict) or not isinstance(summary.get("diagnostic_trace"), dict):
        raise ValueError("summary has no diagnostic_trace")
    actual_build_id = (summary.get("run") or {}).get("id")
    if expected_build_id is not None and actual_build_id != expected_build_id:
        raise ValueError("summary/build identity mismatch")
    if not path or any(not part for part in path.split(".")):
        raise ValueError("path must be a nonempty dotted diagnostic_trace field")
    # Validation metadata can explain a rejected sidecar, but never expose its payload.
    # Retain every source/request/invocation identity check and the existing payload guard.
    validation_fields = {"state", "complete", "errors", "seen", "emitted", "omitted",
                         "omitted_bytes", "sidecar_bytes", "sidecars", "coverage", "invocations",
                         "identity", "source_identity", "footers"}
    if path.startswith("validation."):
        parts = path.split(".")
        if len(parts) != 2 or parts[1] not in validation_fields:
            raise ValueError("unknown trace validation metadata field")
        _validate_trace_identity_envelope(summary)
        field_path = parts[1]
    else:
        validate_trace_page_identity(summary)
        field_path = path
    if type(start) is not int or start < 0 or type(count) is not int or not 1 <= count <= MAX_PAGE_RECORDS:
        raise ValueError("start must be nonnegative and count must be 1..20")
    value: Any = summary["diagnostic_trace"]
    for part in field_path.split("."):
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            raise ValueError(f"unknown trace field path: {path}")
    result: dict[str, Any] = {"path": path, "build_id": actual_build_id,
                              "state": summary["diagnostic_trace"].get("state"),
                              "trace_complete": summary["diagnostic_trace"].get("complete"),
                              "identity": summary["diagnostic_trace"].get("identity"),
                              "diagnostic_only": True}
    if isinstance(value, list):
        if start > len(value):
            raise ValueError(f"start {start} exceeds {len(value)} items")
        page: list[Any] = []
        idx = start
        while idx < len(value) and len(page) < count:
            candidate = page + [value[idx]]
            trial = dict(result, records=candidate, start=start, next_start=idx + 1 if idx + 1 < len(value) else None,
                         omitted=max(0, len(value) - (idx + 1)), complete=idx + 1 == len(value))
            if len(_json_bytes(trial)) > MAX_PAGE_BYTES:
                if not page:
                    raise ValueError("one trace item exceeds 12000-byte page limit")
                break
            page.append(value[idx]); idx += 1
        result.update(records=page, start=start, next_start=idx if idx < len(value) else None,
                      omitted=max(0, len(value) - idx), complete=idx == len(value))
    else:
        result.update(value=value, start=start, next_start=None, omitted=0, complete=True)
        if len(_json_bytes(result)) > MAX_PAGE_BYTES:
            raise ValueError("trace field exceeds 12000-byte page limit")
    return json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
