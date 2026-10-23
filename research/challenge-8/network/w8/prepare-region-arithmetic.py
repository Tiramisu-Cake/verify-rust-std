#!/usr/bin/env python3
"""Prepare unverified W8 arithmetic input units after provider admission.

Importing this module is inert. Its pure byte helpers do not read repository
files or invoke a compiler, parser, assembler, or verifier.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any
import uuid


EXPECTED_POSITIVE_BODIES = [
    "w8_prefix_in_bounds",
    "w8_split_and_prefix_facts",
    "w8_prefix_choice_facts",
]
REQUIRED_NEGATIVE_IDS = [
    "len25-both-prefixes-9",
    "region8-prefix-9",
    "len33-fits32",
]
SOURCE_COMMIT = "cd371e035c7e573760c43bf934d53e8118ee3e7d"
SOURCE_BLOB = "40939f922bcb6fdc7ee0d30427fa861827043827"
SOURCE_PATH = "library/core/src/slice/sort/shared/smallsort.rs"
SOURCE_SHA256 = "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"
INPUT_SCHEMA = "smallsort-w8-arithmetic-inputs-v1"
OUTPUT_SCHEMA = "smallsort-w8-prepared-arithmetic-v1"
MANIFEST_SHA256 = "4af99419c8219101ee0c45bc6d817e0189c914c89e4884948de9ee260cf6b72e"
INPUT_PINS = {
    "header": (
        "research/challenge-8/network/w8/region-arithmetic.gh",
        "e87f023764910c636df32d2422b4265c6c5fffbf4274894f05de0fa20c523ea0",
    ),
    "positive": (
        "research/challenge-8/network/w8/region-arithmetic-lemmas.c",
        "a67df90bd3723d6332e72f1851ab7c454363a94bc4cd9ed65c818a3fccebe129",
    ),
    "len25-both-prefixes-9": (
        "research/challenge-8/network/w8/len25-both-prefixes-9.negative.inc",
        "481a94ec78205cd85cb8b3bb5b830cf3ff1194976622a4c7940ab702aa6292fa",
    ),
    "region8-prefix-9": (
        "research/challenge-8/network/w8/region8-prefix-9.negative.inc",
        "781597cb80a68328c78aaca0641427ad0b5e0c72d7683d8e3a3b67103e249679",
    ),
    "len33-fits32": (
        "research/challenge-8/network/w8/len33-fits32.negative.inc",
        "7fb9989ad850a8986392d9e3ae40f2e6a8c0a7b8397ff4e2ee23111601a07398",
    ),
}
HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
LEMMA_NAME = re.compile(r"\blemma\s+void\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")


class PreparationError(ValueError):
    """Fail-closed validation error for preparation metadata or bytes."""


def sha256(data: bytes) -> str:
    if not isinstance(data, bytes):
        raise PreparationError("input data must be bytes")
    return hashlib.sha256(data).hexdigest()


def _require_mapping(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PreparationError(f"{where} must be an object")
    return value


def _require_text(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value:
        raise PreparationError(f"{where} must be a nonempty string")
    return value


def _require_sha(value: Any, where: str) -> str:
    if not isinstance(value, str) or not HEX_SHA256.fullmatch(value):
        raise PreparationError(f"{where} must be a lowercase SHA-256 hex digest")
    return value


def _safe_relative_path(value: Any, where: str) -> str:
    path_text = _require_text(value, where)
    path = Path(path_text)
    if path.is_absolute() or ".." in path.parts or "\\" in path_text:
        raise PreparationError(f"{where} must be a safe repository-relative path")
    return path_text


def validate_manifest(manifest: Any) -> dict[str, Any]:
    """Validate the small input manifest without touching the filesystem."""
    manifest = _require_mapping(manifest, "manifest")
    if manifest.get("schema") != INPUT_SCHEMA:
        raise PreparationError("input schema is missing or unsupported")
    if manifest.get("state") != "UNVERIFIED_STATIC_PREPARATION":
        raise PreparationError("manifest state is missing or unsupported")
    if manifest.get("proof_credit") is not False:
        raise PreparationError("proof_credit must be false")
    if manifest.get("parser_input_binding") != "NOT_ESTABLISHED":
        raise PreparationError("parser_input_binding must be NOT_ESTABLISHED")

    source = _require_mapping(manifest.get("source"), "source")
    if source.get("commit") != SOURCE_COMMIT:
        raise PreparationError("source commit mismatch")
    if source.get("blob") != SOURCE_BLOB:
        raise PreparationError("source blob mismatch")
    source["path"] = _safe_relative_path(source.get("path"), "source.path")
    if source["path"] != SOURCE_PATH:
        raise PreparationError("source path mismatch")
    source["sha256"] = _require_sha(source.get("sha256"), "source.sha256")
    if source["sha256"] != SOURCE_SHA256:
        raise PreparationError("source SHA-256 pin mismatch")

    inputs = _require_mapping(manifest.get("inputs"), "inputs")
    required_input_names = {"header", "positive", *REQUIRED_NEGATIVE_IDS}
    if set(inputs) != required_input_names:
        raise PreparationError("input inventory is incomplete or has unexpected entries")
    for name, entry_value in inputs.items():
        entry = _require_mapping(entry_value, f"inputs.{name}")
        entry["path"] = _safe_relative_path(entry.get("path"), f"inputs.{name}.path")
        entry["sha256"] = _require_sha(entry.get("sha256"), f"inputs.{name}.sha256")
        if (entry["path"], entry["sha256"]) != INPUT_PINS[name]:
            raise PreparationError(f"input {name} path/SHA-256 pin mismatch")

    bodies = manifest.get("positive_body_inventory")
    if not isinstance(bodies, list) or any(not isinstance(x, str) for x in bodies):
        raise PreparationError("positive_body_inventory must be a string array")
    if bodies != EXPECTED_POSITIVE_BODIES:
        raise PreparationError("positive body inventory is incomplete or out of order")
    negatives = manifest.get("negative_controls")
    if not isinstance(negatives, list) or any(not isinstance(x, dict) for x in negatives):
        raise PreparationError("negative_controls must be an object array")
    ids = [item.get("id") for item in negatives]
    if ids != REQUIRED_NEGATIVE_IDS:
        raise PreparationError("negative control inventory is incomplete or out of order")
    for item in negatives:
        if ("expected_diagnostic_predicate" not in item or
                item["expected_diagnostic_predicate"] is not None):
            raise PreparationError("expected diagnostic predicate must remain unpinned/null")
        if item.get("target_marker") != "TARGET_ASSERTION":
            raise PreparationError("negative target marker is missing or unsupported")
    return manifest


def _ghost_code(source: bytes) -> str:
    """Extract VeriFast ghost blocks/directives, excluding ordinary prose."""
    text = source.decode("utf-8")
    pieces = [match.group(1) for match in re.finditer(r"/\*@([\s\S]*?)@\*/", text)]
    pieces.extend(match.group(1) for match in re.finditer(r"(?m)^\s*//@(.*)$", text))
    code = "\n".join(pieces)
    code = re.sub(r"/\*[\s\S]*?\*/", " ", code)
    code = re.sub(r"//[^\n]*", " ", code)
    return code


def _body_inventory(source: bytes) -> list[str]:
    return LEMMA_NAME.findall(_ghost_code(source))


def _validate_checked_bodies(source: bytes, names: list[str]) -> None:
    text = _ghost_code(source)
    if re.search(r"\b(?:assume|assume_correct|lemma_auto|axiom)\b", text):
        raise PreparationError("unchecked assume/assume_correct/lemma_auto/axiom construct is forbidden")
    starts = list(LEMMA_NAME.finditer(text))
    if [match.group(1) for match in starts] != names:
        raise PreparationError("positive body inventory mismatch")
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        if end < match.end():
            raise PreparationError("positive body boundary is ambiguous")
        body_region = text[match.end():end]
        body_start = body_region.find("{")
        if body_start < 0:
            raise PreparationError(f"lemma {names[index]} has no explicit body")
        depth = 0
        body_closed = False
        for char in body_region[body_start:]:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    body_closed = True
                    break
        if not body_closed:
            raise PreparationError(f"lemma {names[index]} has an unterminated body")


def _validate_header(header: bytes) -> None:
    code = header.decode("utf-8")
    code = re.sub(r"/\*@([\s\S]*?)@\*/", r"\1", code)
    code = re.sub(r"/\*[\s\S]*?\*/", " ", code)
    code = re.sub(r"//[^\n]*", " ", code)
    if re.search(r"\b(?:assume|assume_correct|lemma_auto|axiom)\b", code):
        raise PreparationError("unchecked assume/assume_correct/lemma_auto/axiom construct is forbidden in header")
    if LEMMA_NAME.search(code):
        raise PreparationError("header definitions closure must not contain lemma bodies")


def _target_lines(fragment: bytes, marker: str) -> tuple[int, int, str]:
    if b"\r" in fragment:
        raise PreparationError("negative fragment must use LF line endings for target coordinates")
    raw_text = fragment.decode("utf-8")
    text = _ghost_code(fragment)
    original_lines = raw_text.splitlines()
    marker_lines = [i for i, line in enumerate(original_lines, 1) if marker in line]
    if len(marker_lines) != 1:
        raise PreparationError("negative fragment must contain exactly one target marker")
    names = LEMMA_NAME.findall(text)
    if len(names) != 1 or len(set(names)) != 1:
        raise PreparationError("negative fragment must contain exactly one lemma")
    _validate_checked_bodies(fragment, names)
    marker_line = marker_lines[0]
    ghost_ranges = [
        (match.start(), match.end())
        for match in re.finditer(r"/\*@([\s\S]*?)@\*/", raw_text)
    ]
    marker_offset = sum(len(line) + 1 for line in original_lines[:marker_line - 1])
    if not any(start <= marker_offset < end for start, end in ghost_ranges):
        raise PreparationError("negative target marker must be inside a ghost block")
    line_offsets = []
    offset = 0
    for line in original_lines:
        line_offsets.append(offset)
        offset += len(line) + 1
    assertion_lines = [
        i for i, line in enumerate(original_lines, 1)
        if i > marker_line
        and any(start <= line_offsets[i - 1] < end for start, end in ghost_ranges)
        and re.search(r"\bassert\b", re.sub(r"//.*", " ", re.sub(r"/\*.*?\*/", " ", line)))
    ]
    if len(assertion_lines) != 1:
        raise PreparationError("negative marker must have exactly one following assertion")
    return marker_line, assertion_lines[0], names[0]


def _read_repo_file(repo_root: Path, relative_path: str) -> bytes:
    root = Path(repo_root).resolve(strict=True)
    candidate = root / relative_path
    current = root
    for part in Path(relative_path).parts:
        current = current / part
        if current.is_symlink():
            raise PreparationError("source/input path must not traverse a symlink")
    resolved = candidate.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise PreparationError("source/input path escapes repository root") from error
    return resolved.read_bytes()


def assemble_units(
    manifest_value: Any,
    source: bytes,
    input_bytes: dict[str, bytes],
) -> tuple[dict[str, bytes], dict[str, Any]]:
    """Purely validate bytes and create in-memory candidate unit byte strings."""
    manifest = validate_manifest(manifest_value)
    if not isinstance(source, bytes) or sha256(source) != manifest["source"]["sha256"]:
        raise PreparationError("source bytes are missing or do not match the pinned SHA-256")
    if not isinstance(input_bytes, dict):
        raise PreparationError("input_bytes must be an object")
    if set(input_bytes) != set(manifest["inputs"]):
        raise PreparationError("input byte inventory is incomplete or unexpected")
    for name, data in input_bytes.items():
        if not isinstance(data, bytes):
            raise PreparationError(f"input {name} must be bytes")
        if sha256(data) != manifest["inputs"][name]["sha256"]:
            raise PreparationError(f"input {name} SHA-256 mismatch")

    positive = input_bytes["positive"]
    _validate_header(input_bytes["header"])
    expected_bodies = manifest["positive_body_inventory"]
    if _body_inventory(positive) != expected_bodies:
        raise PreparationError("positive body inventory mismatch")
    _validate_checked_bodies(positive, expected_bodies)

    # The positive C unit is never treated as a header. Its own include line
    # resolves only the separately inventoried ghost definitions closure.
    units: dict[str, bytes] = {"positive.c": positive}
    metadata_negatives: list[dict[str, Any]] = []
    for item in manifest["negative_controls"]:
        control_id = item["id"]
        fragment = input_bytes[control_id]
        marker_line, fragment_assert_line, negative_name = _target_lines(
            fragment, item["target_marker"])
        assembled = positive + b"\n" + fragment
        full_inventory = _body_inventory(assembled)
        expected_inventory = expected_bodies + [negative_name]
        if len(set(full_inventory)) != len(full_inventory) or full_inventory != expected_inventory:
            raise PreparationError("assembled positive-plus-negative body inventory mismatch")
        _validate_checked_bodies(assembled, full_inventory)
        unit_name = f"negative-{control_id}.c"
        units[unit_name] = assembled
        prefix_line_count = (positive + b"\n").count(b"\n")
        metadata_negatives.append({
            "id": control_id,
            "unit": unit_name,
            "unit_sha256": sha256(assembled),
            "body_inventory": full_inventory,
            "target_marker": item["target_marker"],
            "target_marker_line_in_fragment": marker_line,
            "target_assertion_line_in_fragment": fragment_assert_line,
            "target_assertion_line_in_assembled_unit": prefix_line_count + fragment_assert_line,
            "expected_diagnostic_predicate": None,
        })

    # Include the header definitions closure as a distinct byte artifact.
    units["region-arithmetic.gh"] = input_bytes["header"]
    metadata = {
        "schema": OUTPUT_SCHEMA,
        "state": "UNVERIFIED_STATIC_PREPARATION",
        "proof_credit": False,
        "parser_input_binding": "NOT_ESTABLISHED",
        "source": {
            **manifest["source"],
            "bytes_sha256": sha256(source),
        },
        "inputs": {
            name: {"path": manifest["inputs"][name]["path"], "sha256": sha256(data)}
            for name, data in input_bytes.items()
        },
        "positive_body_inventory": list(expected_bodies),
        "positive_unit": {"path": "positive.c", "sha256": sha256(positive)},
        "negative_controls": metadata_negatives,
        "header_definitions_closure": "region-arithmetic.gh",
    }
    return units, metadata


def write_new_output_directory(output_dir: Path, artifacts: dict[str, bytes]) -> None:
    """Write files into a previously nonexistent directory; clean partial writes."""
    output_dir = Path(output_dir)
    if output_dir.exists():
        raise PreparationError("output directory already exists")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir()  # exclusive creation; never replace an existing path
    try:
        for name, data in artifacts.items():
            if Path(name).name != name or not isinstance(data, bytes):
                raise PreparationError("artifact name or bytes are invalid")
            with open(output_dir / name, "xb") as handle:
                handle.write(data)
    except BaseException:
        shutil.rmtree(output_dir, ignore_errors=True)
        raise


def require_supported_provider() -> dict[str, str]:
    """Load the existing provider gate lazily, so CLI can call it first."""
    provider_path = Path(__file__).resolve().parents[2] / "cloud-build" / "provider.py"
    module_name = f"_smallsort_w8_provider_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, provider_path)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load the existing provider guard")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
        return module.require_supported_provider()
    finally:
        sys.modules.pop(module_name, None)


def main(argv: list[str] | None = None) -> int:
    # This gate runs before parsing paths or reading any source/input bytes.
    provider = require_supported_provider()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("ARITHMETIC-INPUTS-N4.json"))
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)

    manifest_bytes = args.manifest.read_bytes()
    if sha256(manifest_bytes) != MANIFEST_SHA256:
        raise PreparationError("raw input manifest SHA-256 pin mismatch")
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    manifest = validate_manifest(manifest)
    repo_root = args.repo_root
    source = _read_repo_file(repo_root, manifest["source"]["path"])
    inputs = {
        name: _read_repo_file(repo_root, entry["path"])
        for name, entry in manifest["inputs"].items()
    }
    units, metadata = assemble_units(manifest, source, inputs)
    metadata["provider"] = provider
    artifacts = dict(units)
    artifacts["prepared-metadata.json"] = (json.dumps(metadata, indent=2, sort_keys=True) + "\n").encode()
    write_new_output_directory(args.output_dir, artifacts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
