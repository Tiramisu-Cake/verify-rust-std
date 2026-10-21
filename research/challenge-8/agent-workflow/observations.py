#!/usr/bin/env python3
"""Compact, immutable Evidence Brief observations.

Records preserve source claims and explicit uncertainty. They are navigation
facts, not proof admission or acceptance. The CLI uses only the standard
library and never executes values stored in a record.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any


SCHEMA = "smallsort-observation-v1"
MAX_SPEC_BYTES = 16 * 1024
MAX_RECORD_BYTES = 8 * 1024
MAX_OUTPUT_BYTES = 12_000
MAX_RECORDS = 10_000
MAX_PAGE_RECORDS = 20
MAX_SELECTOR_BYTES = 2048
MAX_COVERAGE_BYTES = 1024
MAX_TEXT = 500
MAX_PATH = 500
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
BUILD_UUID = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
RECORD_NAME = re.compile(r"^([0-9a-f]{64})\.json$")
REFERENCE_NOTICE = "AUTHOR_ASSERTED_REFERENCES_NOT_VALIDATED"


class ObservationError(ValueError):
    """Invalid, unsafe, or oversized observation input/store."""


def _fail(message: str) -> None:
    raise ObservationError(message)


def _canonical(value: Any) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        _fail(f"value is not canonical JSON data: {exc}")


def _string(value: Any, name: str, cap: int = MAX_TEXT) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{name}: expected non-empty string")
    if len(value) > cap or "\x00" in value:
        _fail(f"{name}: exceeds {cap} characters or contains NUL")
    return value


def _sha(value: Any, name: str, *, required: bool = False, git: bool = False) -> None:
    if value is None and not required:
        return
    pattern = SHA40 if git else SHA256
    if not isinstance(value, str) or not pattern.fullmatch(value):
        _fail(f"{name}: expected {'40-character Git SHA' if git else 'lowercase SHA-256'}" + (" or null" if not required else ""))


def _reference(value: Any, name: str, *, required: bool) -> None:
    if value is None and not required:
        return
    if not isinstance(value, dict) or set(value) != {"path", "sha256"}:
        _fail(f"{name}: expected path and sha256" + (" or null" if not required else ""))
    path = _string(value["path"], f"{name}.path", MAX_PATH)
    if path.startswith("/") or "\\" in path or any(part in {"", ".", ".."} for part in path.split("/")):
        _fail(f"{name}.path: expected descriptive relative artifact path")
    _sha(value["sha256"], f"{name}.sha256", required=True)


def _utc(value: Any) -> None:
    _string(value, "observed_utc", 40)
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _fail("observed_utc: invalid ISO-8601 timestamp")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail("observed_utc: timezone is required")


def _safe_json_data(value: Any, name: str, limit: int) -> None:
    encoded = _canonical(value)
    if len(encoded) > limit:
        _fail(f"{name}: exceeds {limit} canonical JSON bytes")
    # Bound nesting to keep validation/rendering predictable.
    def depth(item: Any, level: int = 0) -> None:
        if level > 8:
            _fail(f"{name}: nesting exceeds 8 levels")
        if isinstance(item, dict):
            for k, v in item.items():
                if not isinstance(k, str):
                    _fail(f"{name}: object keys must be strings")
                depth(v, level + 1)
        elif isinstance(item, list):
            for child in item:
                depth(child, level + 1)
        elif item is not None and type(item) not in (str, int, float, bool):
            _fail(f"{name}: unsupported JSON value")
    depth(value)


def validate(value: Any) -> dict[str, Any]:
    fields = {
        "schema", "build_uuid", "identities", "archive_sha256", "index_sha256",
        "file_sha256", "request_sha256", "file_id", "selector", "observed_utc",
        "exact", "complete", "coverage", "stage", "target", "status", "exit_code",
        "observation", "assurance",
        "evidence_ref", "independence_receipt_ref",
    }
    if not isinstance(value, dict) or set(value) != fields:
        _fail("record must contain exactly the documented observation fields")
    if value["schema"] != SCHEMA:
        _fail(f"schema must be {SCHEMA}")
    if not isinstance(value["build_uuid"], str) or not BUILD_UUID.fullmatch(value["build_uuid"]):
        _fail("build_uuid: invalid Build UUID")
    ids = value["identities"]
    if not isinstance(ids, dict) or set(ids) != {"source_sha", "tool_sha", "profile_sha256"}:
        _fail("identities: expected source_sha, tool_sha, profile_sha256")
    _sha(ids["source_sha"], "identities.source_sha", git=True)
    _sha(ids["tool_sha"], "identities.tool_sha", git=True)
    _sha(ids["profile_sha256"], "identities.profile_sha256")
    for key in ("archive_sha256", "index_sha256", "file_sha256", "request_sha256"):
        _sha(value[key], key)
    _string(value["file_id"], "file_id", 200)
    _safe_json_data(value["selector"], "selector", MAX_SELECTOR_BYTES)
    _utc(value["observed_utc"])
    for key in ("exact", "complete"):
        if value[key] not in (True, False, "UNKNOWN") or type(value[key]) not in (bool, str):
            _fail(f"{key}: expected true, false, or UNKNOWN")
    _safe_json_data(value["coverage"], "coverage", MAX_COVERAGE_BYTES)
    if not isinstance(value["coverage"], (dict, list, str)):
        _fail("coverage: expected object, array, string, or UNKNOWN data")
    if isinstance(value["coverage"], str) and len(value["coverage"]) > MAX_TEXT:
        _fail("coverage: string too long")
    for key in ("stage", "target", "status"):
        if value[key] is not None:
            _string(value[key], key, 160)
    if value["exit_code"] is not None and (type(value["exit_code"]) is not int or abs(value["exit_code"]) > 1_000_000):
        _fail("exit_code: expected bounded integer or null")
    _string(value["observation"], "observation", MAX_TEXT)
    if value["assurance"] not in {"SOURCE_REPORTED", "INDEPENDENTLY_ESTABLISHED"}:
        _fail("assurance: expected SOURCE_REPORTED or INDEPENDENTLY_ESTABLISHED")
    _reference(value["evidence_ref"], "evidence_ref", required=True)
    _reference(value["independence_receipt_ref"], "independence_receipt_ref", required=value["assurance"] == "INDEPENDENTLY_ESTABLISHED")
    if value["independence_receipt_ref"] is not None and value["independence_receipt_ref"] == value["evidence_ref"]:
        _fail("independence_receipt_ref must be a distinct receipt reference")
    encoded = _canonical(value)
    if len(encoded) > MAX_RECORD_BYTES:
        _fail(f"record exceeds {MAX_RECORD_BYTES} bytes")
    return value


def _check_components(path: Path, *, allow_missing: bool) -> None:
    absolute = path.absolute()
    parts = [absolute, *absolute.parents]
    for item in reversed(parts):
        try:
            mode = item.lstat().st_mode
        except FileNotFoundError:
            if allow_missing:
                continue
            _fail(f"path component does not exist: {item}")
        except OSError as exc:
            _fail(f"cannot inspect path {item}: {exc}")
        if stat.S_ISLNK(mode):
            _fail(f"symlink path component refused: {item}")


def _store_dir(path: Path, *, create: bool = False) -> Path:
    path = path.absolute()
    _check_components(path, allow_missing=create)
    if create:
        path.mkdir(parents=True, exist_ok=True)
        _check_components(path, allow_missing=False)
    try:
        if not stat.S_ISDIR(path.lstat().st_mode):
            _fail("store must be a directory")
    except OSError as exc:
        _fail(f"cannot inspect store: {exc}")
    return path


def _read_regular(path: Path, cap: int) -> bytes:
    _check_components(path, allow_missing=False)
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_size > cap:
                _fail(f"refusing non-regular or oversized file: {path}")
            chunks = bytearray()
            while len(chunks) <= cap:
                chunk = os.read(fd, min(8192, cap + 1 - len(chunks)))
                if not chunk:
                    break
                chunks.extend(chunk)
            if len(chunks) > cap:
                _fail(f"file exceeds {cap} bytes: {path}")
            return bytes(chunks)
        finally:
            os.close(fd)
    except ObservationError:
        raise
    except OSError as exc:
        _fail(f"cannot read {path}: {exc}")


def record(spec_path: Path, store_path: Path) -> str:
    raw = _read_regular(spec_path, MAX_SPEC_BYTES)
    try:
        data = validate(json.loads(raw.decode("utf-8")))
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        _fail(f"invalid spec JSON: {exc}")
    payload = _canonical(data) + b"\n"
    store = _store_dir(store_path, create=True)
    digest = hashlib.sha256(payload).hexdigest()
    target = store / f"{digest}.json"
    try:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    except FileExistsError:
        existing = _read_regular(target, MAX_RECORD_BYTES + 1)
        if existing != payload:
            _fail(f"content-address collision or modified record: {target.name}")
        return digest
    except OSError as exc:
        _fail(f"cannot create immutable record: {exc}")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        try:
            target.unlink()
        except OSError:
            pass
        _fail(f"cannot write record: {exc}")
    return digest


def _load_records(store: Path) -> list[tuple[str, dict[str, Any]]]:
    store = _store_dir(store)
    found: list[tuple[str, dict[str, Any]]] = []
    try:
        for path in store.iterdir():
            if len(found) >= MAX_RECORDS:
                _fail(f"store exceeds {MAX_RECORDS} records")
            if path.name.startswith("."):
                _fail(f"unexpected hidden entry in store: {path.name}")
            match = RECORD_NAME.fullmatch(path.name)
            if not match:
                _fail(f"unexpected store entry: {path.name}")
            raw = _read_regular(path, MAX_RECORD_BYTES + 1)
            try:
                data = validate(json.loads(raw.decode("utf-8")))
            except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
                _fail(f"invalid record {path.name}: {exc}")
            if raw != _canonical(data) + b"\n":
                _fail(f"record is not canonical JSON with one trailing newline: {path.name}")
            digest = hashlib.sha256(raw).hexdigest()
            if digest != match.group(1):
                _fail(f"record digest mismatch: {path.name}")
            found.append((digest, data))
    except OSError as exc:
        _fail(f"cannot list store: {exc}")
    found.sort(key=lambda pair: (pair[1]["observed_utc"], pair[0]))
    return found


def check(store: Path) -> dict[str, Any]:
    records = _load_records(store)
    return {"store": str(store.absolute()), "checked": len(records), "valid": True}


def _render_page(page: dict[str, Any], index_sha256: str | None, offset: int) -> str:
    lines = [f"# Evidence Brief observations for Build {_code(page['build_uuid'])}", "",
             "Records are navigation facts; they do not imply proof acceptance or freshness.",
             f"Reference validation: `{REFERENCE_NOTICE}`. Assurance labels and reference digests are caller asserted; this tool does not read referenced bytes.",
             f"Index filter: {_code(index_sha256 or 'all recorded indexes')}; snapshot SHA-256 {_code(page['records_snapshot_sha256'])}; offset {offset}; next offset {_code(page['next_offset'])}.", ""]
    if not page["records"]:
        lines.append("No matching observations recorded. This does not mean NOT_RUN.")
    for item in page["records"]:
        row = item["record"]
        lines.extend([f"## {_code(item['digest'])}", "",
                      f"- Caller asserted assurance label: {_code(row['assurance'])}",
                      f"- Observation: {_code(row['observation'])}",
                      f"- Observed: {_code(row['observed_utc'])}; exact: {_code(row['exact'])}; complete: {_code(row['complete'])}",
                      f"- Coverage: {_code(row['coverage'])}",
                      f"- File: {_code(row['file_id'])}; file SHA: {_code(row['file_sha256'] or 'UNKNOWN')}; index SHA: {_code(row['index_sha256'] or 'UNKNOWN')}",
                      f"- Caller supplied evidence reference (not validated): {_code(row['evidence_ref']['path'])} SHA-256 {_code(row['evidence_ref']['sha256'])}"])
        if row["assurance"] == "INDEPENDENTLY_ESTABLISHED":
            ref = row["independence_receipt_ref"]
            lines.append(f"- Caller supplied separate independence receipt reference (not validated): {_code(ref['path'])} SHA-256 {_code(ref['sha256'])}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _code(value: Any) -> str:
    """JSON-quote untrusted values inside a code span that cannot be closed."""
    body = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    longest = max((len(run) for run in re.findall(r"`+", body)), default=0)
    fence = "`" * (longest + 1)
    return f"{fence}{body}{fence}"


def _page(store: Path, build_uuid: str, index_sha256: str | None, limit: int, offset: int,
          expect_snapshot_sha256: str | None) -> dict[str, Any]:
    if not BUILD_UUID.fullmatch(build_uuid):
        _fail("build_uuid: invalid Build UUID")
    if index_sha256 is not None:
        _sha(index_sha256, "index_sha256", required=True)
    if type(limit) is not int or not (1 <= limit <= MAX_PAGE_RECORDS):
        _fail(f"limit must be between 1 and {MAX_PAGE_RECORDS}")
    if type(offset) is not int or offset < 0:
        _fail("offset must be a non-negative integer")
    if offset > 0 and expect_snapshot_sha256 is None:
        _fail("continuation requires --expect-snapshot-sha256 from the first page")
    if expect_snapshot_sha256 is not None:
        _sha(expect_snapshot_sha256, "expect_snapshot_sha256", required=True)
    rows = [(digest, row) for digest, row in _load_records(store)
            if row["build_uuid"].lower() == build_uuid.lower()
            and (index_sha256 is None or row["index_sha256"] == index_sha256)]
    snapshot = hashlib.sha256(_canonical([digest for digest, _ in rows])).hexdigest()
    if expect_snapshot_sha256 is not None and expect_snapshot_sha256 != snapshot:
        _fail("record snapshot changed; restart pagination at offset 0")
    result = {"build_uuid": build_uuid, "index_sha256": index_sha256,
              "records_snapshot_sha256": snapshot, "reference_validation": REFERENCE_NOTICE,
              "assurance_labels": "AUTHOR_ASSERTED", "total_matching": len(rows), "offset": offset,
              "next_offset": None, "records": []}
    for digest, row in rows[offset:offset + limit]:
        candidate = dict(result)
        candidate["records"] = [*result["records"], {"digest": digest, "record": row}]
        next_offset = offset + len(candidate["records"])
        candidate["next_offset"] = next_offset if next_offset < len(rows) else None
        if len(_canonical(candidate)) + 1 > MAX_OUTPUT_BYTES or len(_render_page(candidate, index_sha256, offset).encode("utf-8")) > MAX_OUTPUT_BYTES:
            if not result["records"]:
                _fail("one observation exceeds page output limit; reduce its field sizes")
            break
        result = candidate
    next_offset = offset + len(result["records"])
    result["next_offset"] = next_offset if next_offset < len(rows) else None
    return result


def list_records(store: Path, build_uuid: str, index_sha256: str | None = None,
                 limit: int = 20, offset: int = 0,
                 expect_snapshot_sha256: str | None = None) -> dict[str, Any]:
    return _page(store, build_uuid, index_sha256, limit, offset, expect_snapshot_sha256)


def render(store: Path, build_uuid: str, index_sha256: str | None = None,
           limit: int = 20, offset: int = 0,
           expect_snapshot_sha256: str | None = None) -> str:
    page = _page(store, build_uuid, index_sha256, limit, offset, expect_snapshot_sha256)
    return _render_page(page, index_sha256, offset)


def _emit(value: Any) -> None:
    out = _canonical(value) + b"\n"
    if len(out) > MAX_OUTPUT_BYTES:
        _fail(f"output exceeds {MAX_OUTPUT_BYTES} bytes")
    sys.stdout.buffer.write(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="smallsort-session observations")
    sub = parser.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("record")
    rec.add_argument("--spec", required=True, type=Path)
    rec.add_argument("--store", required=True, type=Path)
    for name in ("list", "render"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--store", required=True, type=Path)
        cmd.add_argument("--build", required=True)
        cmd.add_argument("--index-sha256")
        cmd.add_argument("--limit", type=int, default=20)
        cmd.add_argument("--offset", type=int, default=0)
        cmd.add_argument("--expect-snapshot-sha256")
    chk = sub.add_parser("check")
    chk.add_argument("--store", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "record":
            _emit({"digest": record(args.spec, args.store)})
        elif args.command == "check":
            _emit(check(args.store))
        elif args.command == "list":
            _emit(list_records(args.store, args.build, args.index_sha256, args.limit, args.offset, args.expect_snapshot_sha256))
        else:
            sys.stdout.write(render(args.store, args.build, args.index_sha256, args.limit, args.offset, args.expect_snapshot_sha256))
        return 0
    except ObservationError as exc:
        print(f"observations: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
