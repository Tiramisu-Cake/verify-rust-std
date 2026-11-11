"""Bounded, summary-only reader for the opt-in KANI3300 compile-time JSONL sidecars."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

SCHEMA = "kani3300-trace-v1"
STAGE = "kani3300-t1b"
MAX_RECORD_BYTES = 2048
MAX_RUN_BYTES = 1024 * 1024
MAX_RUN_RECORDS = 4096
MAX_SIDECARS = 128
MAX_ERRORS = 16
MAX_PAGE_RECORDS = 20
MAX_PAGE_BYTES = 12000


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def collect_trace(directory: Path, *, build_id: str | None, head_sha: str | None,
                  request_sha256: str | None, request: dict[str, Any], kani_commit: str | None,
                  kani_build: dict[str, Any] | None, tooling: dict[str, str],
                  build_outcome: str | None, effective_argv: list[str], effective_env: dict[str, str],
                  actual_library_tree: str | None) -> dict[str, Any]:
    """Read only compiler-produced JSONL files. Every failure is retained as diagnostic state."""
    expected_id = request_sha256
    request_trace = request["diagnostic_trace"]
    filters = request_trace["filters"]
    trace: dict[str, Any] = {
        "schema": "kani3300-diagnostic-trace-v1", "diagnostic_only": True,
        "state": "INCOMPLETE", "complete": False, "records": [], "seen": 0, "emitted": 0,
        "omitted": 0, "omitted_bytes": 0, "errors": [], "coverage": [],
        "source_identity": {"trace_id": expected_id, "stage": STAGE},
        "identity": {
            "build_id": build_id, "head_sha": head_sha, "request_sha256": request_sha256,
            "library_tree": request_trace["library_tree"], "actual_library_tree": actual_library_tree,
            "base_pin": request_trace["base_pin"],
            "kani_commit": kani_commit,
            "patch_sha256": (request.get("kani_patch") or {}).get("sha256"),
            "applied_tree": (kani_build or {}).get("tree"),
            "expected_applied_tree": request_trace["expected_applied_tree"],
            "tooling_sha256": tooling, "effective_argv": effective_argv,
            "effective_env": effective_env,
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
            trace["errors"].append("sidecar is a symlink")
            states.append("INVALID")
            continue
        try:
            size = path.stat().st_size
            if size > MAX_RUN_BYTES or total_bytes + size > MAX_RUN_BYTES:
                trace["errors"].append("aggregate sidecar bytes exceed 1 MiB")
                states.append("OVERSIZED")
                break
            with path.open("rb") as stream:
                raw = stream.read(MAX_RUN_BYTES - total_bytes + 1)
            if len(raw) > MAX_RUN_BYTES - total_bytes:
                trace["errors"].append("aggregate sidecar bytes exceed 1 MiB")
                states.append("OVERSIZED")
                break
        except OSError as exc:
            trace["errors"].append(f"sidecar read failed: {type(exc).__name__}")
            states.append("INVALID")
            continue
        total_bytes += len(raw)
        if total_bytes > MAX_RUN_BYTES:
            trace["errors"].append("aggregate sidecar bytes exceed 1 MiB")
            states.append("OVERSIZED")
            break
        try:
            lines = raw.splitlines()
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
                        or overflow.get("stage") != STAGE or overflow.get("state") != "OVERSIZED"
                        or overflow.get("omitted_invocations") != "one-or-more"):
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
            if not isinstance(hdata, dict) or hdata.get("filters") != filters:
                raise ValueError("source literal filter identity mismatch")
            if any(row.get("schema") != SCHEMA or row.get("trace_id") != expected_id
                   or row.get("stage") != STAGE or row.get("invocation") != invocation
                   or type(row.get("seq")) is not int or not isinstance(row.get("kind"), str)
                   or not isinstance(row.get("data"), dict) for row in rows):
                raise ValueError("record identity/schema/type mismatch")
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
            total_seen += seen
            total_emitted += emitted
            total_omitted += omitted
            if type(fdata.get("omitted_bytes")) is int and fdata["omitted_bytes"] >= 0:
                total_omitted_bytes += fdata["omitted_bytes"]
            else:
                omitted_bytes_known = False
            if type(fdata.get("bytes_before_footer")) is not int or fdata["bytes_before_footer"] < 0:
                raise ValueError("footer byte counter missing")
            states.append(fdata["state"])
            trace["coverage"].append({"invocation": invocation, "state": fdata["state"],
                                      "seen": seen, "emitted": emitted, "omitted": omitted,
                                      "coverage": fdata.get("coverage")})
            all_records.extend({"invocation": invocation, "seq": row["seq"], "kind": row["kind"], "data": row["data"]}
                               for row in records)
        except (ValueError, TypeError, AttributeError, UnicodeError, json.JSONDecodeError) as exc:
            if len(trace["errors"]) < MAX_ERRORS:
                trace["errors"].append(f"{path.name}: {str(exc)[:180]}")
            states.append("INVALID")
    if excess_files:
        trace["errors"].append("more than 128 sidecars; enumeration bounded")
        states.append("OVERSIZED")
    if len(all_records) > MAX_RUN_RECORDS:
        extra = len(all_records) - MAX_RUN_RECORDS
        total_omitted += extra
        all_records = all_records[:MAX_RUN_RECORDS]
        states.append("OVERSIZED")
        trace["errors"].append(f"summary reader retained at most {MAX_RUN_RECORDS} records")
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
    if type(start) is not int or start < 0 or type(count) is not int or not 1 <= count <= MAX_PAGE_RECORDS:
        raise ValueError("start must be nonnegative and count must be 1..20")
    value: Any = summary["diagnostic_trace"]
    for part in path.split("."):
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
