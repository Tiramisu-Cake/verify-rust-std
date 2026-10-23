#!/usr/bin/env python3
"""Project only fields consumed by the inactive R21 fingerprint pin checker.

This is local Evidence Brief client tooling. It does not read raw evidence,
invoke proof tooling, or establish any claim beyond exact returned values.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

BRIEF = "/usr/local/bin/smallsort-brief"
VARIANTS = (
    "positive", "omit-selected-own", "omit-unselected-own", "no-retained-half",
    "callee-false-normal", "callee-owner-duplicate", "callee-owner-loss",
    "callee-thread-duplicate",
)
SNAPSHOTS = ("unit", *(f"body-{i}" for i in range(9)))
SOURCES = {"original/lib.rs", "verified/lib.rs"}


class ProjectionError(RuntimeError):
    pass


@dataclass(frozen=True)
class Object:
    fields: dict[str, Any]
    exact_keys: bool = False


@dataclass(frozen=True)
class Array:
    item: Any


BOOL, INT, STR, SHA = "bool", "int", "str", "sha256"


def _snapshot_row() -> Object:
    return Object({"file": STR, "bytes": INT, "sha256": SHA}, exact_keys=True)


def _fingerprint() -> Object:
    return Object({
        "classification": STR,
        "expected_refusal_seen": BOOL,
        "all_ten_snapshots": BOOL,
        "body_proof_run": BOOL,
        "stage": Object({
            "status": STR, "exit": INT, "source_unchanged": BOOL,
            "source_before": Object({key: SHA for key in SOURCES}, exact_keys=True),
            "source_after": Object({key: SHA for key in SOURCES}, exact_keys=True),
            "intrinsic_gate_active": BOOL, "pointer_drop_gate_active": BOOL,
            "stdout": STR, "stderr": STR,
        }),
        "snapshots": Object({name: _snapshot_row() for name in SNAPSHOTS}, exact_keys=True),
    })


RECORD_SPEC = Object({
    "schema": STR, "complete": BOOL, "accepted": BOOL,
    "proof_credit": BOOL, "body_proof_run": BOOL,
    "base_source": Object({"original_sha256": SHA, "verified_sha256": SHA}),
    "variant_order": Array(STR),
    "snapshot_pins": Object({name: SHA for name in SNAPSHOTS}, exact_keys=True),
    "location_control": Object({
        "reproduces_pinned": BOOL, "source_intact_after_stages": BOOL,
        "fingerprint_check": Object({"complete": BOOL,
                                      "snapshots_match_default_pins": BOOL}),
        "fingerprint": _fingerprint(),
    }),
    "variants": Object({name: Object({
        "status": STR, "source_intact_after_stages": BOOL,
        "original_preserved": BOOL, "original_sha256": SHA,
        "verified_sha256": SHA,
        "fingerprint": Object({"body_proof_run": BOOL, "stage": _fingerprint().fields["stage"],
                                "snapshots": _fingerprint().fields["snapshots"]}),
        "fingerprint_check": Object({"complete": BOOL,
                                      "snapshots_match_default_pins": BOOL}),
        "normal_mir_check": Object({"complete": BOOL}),
    }) for name in VARIANTS}, exact_keys=True),
})

IDENTITY_FIELDS = ("build_id", "file_id", "file_path", "file_sha256", "index_sha256",
                   "archive_sha256")


def cli_call(build_id: str, file_id: str, expected_sha256: str,
             runner: Callable[..., Any] = subprocess.run):
    def call(pointer: str, offset: int | None = None,
             value_start: int | None = None) -> dict[str, Any]:
        argv = [BRIEF, build_id, "--refresh", "--file", file_id,
                "--expect-sha256", expected_sha256, "--pointer", pointer]
        if offset is not None:
            argv += ["--offset", str(offset)]
        if value_start is not None:
            argv += ["--value-start", str(value_start)]
        result = runner(argv, capture_output=True, text=True, check=False)
        try:
            response = json.loads(result.stdout)
        except (TypeError, ValueError) as exc:
            raise ProjectionError("Brief did not return JSON") from exc
        if result.returncode not in (0, 3):
            raise ProjectionError(f"Brief command failed with exit {result.returncode}")
        return response
    return call


class Projector:
    def __init__(self, call: Callable[[str, int | None, int | None], dict[str, Any]],
                 *, build_id: str, file_id: str, expected_sha256: str):
        self.call = call
        self.expected = {"build_id": build_id, "file_id": file_id,
                         "file_sha256": expected_sha256}
        self.identity: dict[str, Any] | None = None
        self.requests: list[dict[str, Any]] = []
        self.coverage: dict[str, Any] = {}

    @staticmethod
    def _fail(message: str) -> None:
        raise ProjectionError(message)

    def _response(self, pointer: str, offset: int | None,
                  value_start: int | None) -> dict[str, Any]:
        d = self.call(pointer, offset, value_start)
        if not isinstance(d, dict) or d.get("status") != "OK":
            self._fail(f"Brief error or malformed response at {pointer!r}")
        if d.get("schema") != "smallsort-targeted-observation-v2":
            self._fail("unrecognized Brief response schema")
        if d.get("exact") is not True or type(d.get("complete")) is not bool:
            self._fail(f"inexact/malformed response at {pointer!r}")
        req_id = d.get("request_id")
        req = d.get("request")
        if not isinstance(req_id, str) or not req_id or not isinstance(req, dict):
            self._fail("Brief request identity missing")
        if req.get("pointer") != pointer or req.get("file_id") != self.expected["file_id"] or \
                req.get("expected_sha256") != self.expected["file_sha256"]:
            self._fail("Brief selector/file/SHA request binding differs")
        if offset is not None and req.get("offset") != offset:
            self._fail("Brief request does not echo the server-issued offset")
        if value_start is not None and req.get("value_start") != value_start:
            self._fail("Brief request does not echo the server-issued value start")
        ident = {key: d.get(key) for key in IDENTITY_FIELDS}
        if any(not isinstance(ident[key], str) or not ident[key] for key in IDENTITY_FIELDS):
            self._fail("Brief build/file/index/archive identity missing")
        if any(ident[key] != value for key, value in self.expected.items()):
            self._fail("Brief build or file identity differs from requested identity")
        if self.identity is None:
            self.identity = ident
        elif ident != self.identity:
            self._fail("Brief identity changed between projection requests")
        for key in ("coverage", "projection_coverage"):
            if key in d:
                if key in self.coverage and self.coverage[key] != d[key]:
                    self._fail(f"Brief {key} changed between pages")
                self.coverage[key] = d[key]
        self.requests.append({"request_id": req_id, "pointer": pointer,
                              "offset": offset, "value_start": value_start,
                              "complete": d["complete"]})
        return d

    @staticmethod
    def _unescape(token: str) -> str:
        # RFC 6901 decoding order matters; reject malformed escapes.
        if re.search(r"~(?![01])", token):
            raise ProjectionError("malformed JSON pointer escape")
        return token.replace("~1", "/").replace("~0", "~")

    def _collect(self, pointer: str) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
        offset: int | None = None
        all_results: list[dict[str, Any]] = []
        last: dict[str, Any] | None = None
        seen_offsets: set[int] = set()
        while True:
            d = self._response(pointer, offset, None)
            last = d
            if d.get("offset", 0) != (0 if offset is None else offset):
                self._fail("Brief returned offset differs from requested page")
            results = d.get("results")
            if not isinstance(results, list):
                self._fail("Brief results is not an array")
            all_results.extend(results)
            next_offset = d.get("next_offset")
            if next_offset is None:
                if d.get("complete") is not True:
                    self._fail(f"Brief projection incomplete at {pointer!r}")
                break
            if (type(next_offset) is not int or next_offset < 0 or
                    next_offset <= (offset if offset is not None else -1) or
                    next_offset in seen_offsets):
                self._fail("invalid or repeated server next_offset")
            seen_offsets.add(next_offset)
            offset = next_offset
        assert last is not None
        kind = last.get("selected_kind")
        if not isinstance(kind, str):
            self._fail("selected JSON kind missing")
        child_count = last.get("child_count")
        if kind in ("object", "array"):
            if type(child_count) is not int or child_count != len(all_results):
                self._fail(f"child inventory incomplete at {pointer!r}")
        return kind, all_results, last

    def _scalar(self, pointer: str, first: dict[str, Any], spec: Any) -> Any:
        if first.get("exact") is not True:
            self._fail(f"inexact scalar at {pointer!r}")
        value = first.get("value")
        next_start = first.get("next_value_start")
        if next_start is not None:
            # A partial string is re-read only by the server-issued continuation.
            pieces: list[str] = []
            if not isinstance(value, str):
                self._fail("partial JSON value is not a string")
            pieces.append(value)
            start = next_start
            visited: set[int] = set()
            while start is not None:
                if type(start) is not int or start < 0 or start in visited:
                    self._fail("invalid or repeated server next_value_start")
                visited.add(start)
                d = self._response(pointer, None, start)
                if d.get("complete") is not True or d.get("next_offset") is not None:
                    self._fail("continued JSON string response is incomplete")
                rows = d.get("results")
                if not isinstance(rows, list) or len(rows) != 1:
                    self._fail("continued JSON string must have one exact result")
                row = rows[0]
                if row.get("pointer") != pointer or row.get("exact") is not True or \
                        not isinstance(row.get("value"), str):
                    self._fail("continued JSON string result malformed")
                pieces.append(row["value"])
                start = row.get("next_value_start")
            value = "".join(pieces)
        elif not first.get("complete", True):
            self._fail("scalar is marked incomplete without continuation")
        self._check_type(value, spec, pointer)
        return value

    def _check_type(self, value: Any, spec: Any, pointer: str) -> None:
        valid = {
            BOOL: type(value) is bool,
            INT: type(value) is int,
            STR: isinstance(value, str),
            SHA: isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
        }.get(spec, False)
        if not valid:
            self._fail(f"required scalar has wrong type/value at {pointer!r}")

    def project(self, pointer: str, spec: Any) -> Any:
        kind, results, descriptor = self._collect(pointer)
        if isinstance(spec, Object):
            if kind != "object":
                self._fail(f"required object has kind {kind!r} at {pointer!r}")
            children: dict[str, dict[str, Any]] = {}
            for row in results:
                if not isinstance(row, dict) or row.get("exact") is not True or \
                        not isinstance(row.get("pointer"), str):
                    self._fail(f"malformed/inexact child at {pointer!r}")
                prefix = pointer + "/" if pointer else "/"
                child_pointer = row["pointer"]
                if not child_pointer.startswith(prefix) or "/" in child_pointer[len(prefix):]:
                    self._fail(f"non-child pointer returned at {pointer!r}")
                key = self._unescape(child_pointer[len(prefix):])
                if key in children:
                    self._fail(f"duplicate child key at {pointer!r}")
                children[key] = row
            if spec.exact_keys and set(children) != set(spec.fields):
                self._fail(f"required object inventory differs at {pointer!r}")
            output: dict[str, Any] = {}
            for key, child_spec in spec.fields.items():
                row = children.get(key)
                if row is None:
                    self._fail(f"required field missing: {pointer}/{key}")
                child_pointer = (pointer + "/" if pointer else "/") + key.replace("~", "~0").replace("/", "~1")
                if isinstance(child_spec, Object):
                    if "value" in row or row.get("kind") != "object":
                        self._fail(f"required nested object malformed: {child_pointer}")
                    output[key] = self.project(child_pointer, child_spec)
                elif isinstance(child_spec, Array):
                    if "value" in row or row.get("kind") != "array":
                        self._fail(f"required nested array malformed: {child_pointer}")
                    output[key] = self.project(child_pointer, child_spec)
                else:
                    if "value" not in row:
                        self._fail(f"required scalar child has no value: {child_pointer}")
                    output[key] = self._scalar(child_pointer, row, child_spec)
            return output
        if isinstance(spec, Array):
            if kind != "array":
                self._fail(f"required array has kind {kind!r} at {pointer!r}")
            indexed: dict[int, dict[str, Any]] = {}
            prefix = pointer + "/"
            for row in results:
                if not isinstance(row, dict) or row.get("exact") is not True:
                    self._fail(f"malformed array item at {pointer!r}")
                p = row.get("pointer")
                token = p[len(prefix):] if isinstance(p, str) and p.startswith(prefix) else ""
                if not token.isdecimal() or "/" in token:
                    self._fail(f"invalid array index at {pointer!r}")
                i = int(token)
                if i in indexed:
                    self._fail(f"duplicate array index at {pointer!r}")
                indexed[i] = row
            if sorted(indexed) != list(range(len(indexed))):
                self._fail(f"array indices are not contiguous at {pointer!r}")
            out = []
            for i in range(len(indexed)):
                row = indexed[i]
                item_pointer = f"{pointer}/{i}"
                if "value" not in row:
                    self._fail(f"required array scalar has no value: {item_pointer}")
                out.append(self._scalar(item_pointer, row, spec.item))
            return out
        # Scalar selector (normally used only if a root schema is ever scalar).
        if len(results) != 1 or results[0].get("pointer") != pointer:
            self._fail(f"scalar selector returned unexpected results at {pointer!r}")
        return self._scalar(pointer, results[0], spec)

    def run(self) -> dict[str, Any]:
        record = self.project("", RECORD_SPEC)
        if record["variant_order"] != list(VARIANTS):
            self._fail("fingerprint variant order differs from pinned R21 order")
        return {"projected_record": record,
                "receipt": {
                    "schema": "r21-fingerprint-brief-projection-receipt-v1",
                    "identity": self.identity,
                    "requests": self.requests,
                    "coverage": self.coverage,
                    "omitted_fields": [
                        "root fields not consumed by fingerprint_to_pins (including mode and classification)",
                        "base_source fields other than original_sha256 and verified_sha256",
                        "variant metadata other than the fields in the projected record",
                        "fingerprint stage argv and any stage fields not read by fingerprint_to_pins",
                        "normal_mir_check fields other than complete",
                        "all unrelated fingerprint/check fields and all unselected record branches",
                    ],
                    "claims": "Exact returned values only; projection is not a complete source record, source/MIR binding, proof result, or proof credit.",
                }}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build_id")
    parser.add_argument("file_id")
    parser.add_argument("expected_sha256")
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[0-9a-f]{64}", args.expected_sha256):
        parser.error("expected_sha256 must be lowercase SHA-256")
    projector = Projector(cli_call(args.build_id, args.file_id, args.expected_sha256),
                          build_id=args.build_id, file_id=args.file_id,
                          expected_sha256=args.expected_sha256)
    bundle = projector.run()
    args.output.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n")
    print(f"projected {len(bundle['receipt']['requests'])} Brief requests; "
          "record is a consumed-field projection only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
