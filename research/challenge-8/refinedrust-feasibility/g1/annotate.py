#!/usr/bin/env python3
"""G1-only insertion of RefinedRust ghost attributes into a disposable core tree.

The module is inert on import. Invoke only in the authorized Cloud Build lane.
No compiler, extractor, or verifier is launched here.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


SCHEMA = "g1-ghost-annotations-v1"
ALLOWED_ATTRS = {
    '#![feature(register_tool)]',
    '#![register_tool(rr)]',
    '#[rr::verify]',
    '#[rr::may_unwind_if("True")]',
    '#[rr::refined_by("()" : "unit")]',
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_head(repo: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def prepare_file(repo: Path, entry: dict) -> tuple[Path, bytes, bytes, list[dict]]:
    relative = Path(entry["path"])
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ValueError(f"unsafe manifest path: {relative}")
    source = repo / relative
    if source.is_symlink() or not source.is_file() or not source.resolve().is_relative_to(repo.resolve()):
        raise ValueError(f"missing, linked, or external source: {relative}")
    original = source.read_bytes()
    if sha256(original) != entry["sha256"]:
        raise ValueError(f"exact-source SHA256 mismatch: {relative}")

    insertions = []
    used_offsets = set()
    for spec in entry["insertions"]:
        anchor = spec["anchor"].encode("utf-8")
        if not anchor.endswith(b"\n") or original.count(anchor) != 1:
            raise ValueError(f"anchor missing or ambiguous: {relative}: {spec['symbol']}")
        offset = original.index(anchor)
        if offset in used_offsets or (offset > 0 and original[offset - 1] != 10):
            raise ValueError(f"overlapping or non-line anchor: {relative}: {spec['symbol']}")
        used_offsets.add(offset)
        attrs = spec["attributes"]
        if not attrs or any(attr.strip() not in ALLOWED_ATTRS for attr in attrs):
            raise ValueError(f"invalid ghost attribute: {relative}: {spec['symbol']}")
        added = ("\n".join(attrs) + "\n").encode("utf-8")
        insertions.append((offset, added, spec["symbol"]))

    insertions.sort(key=lambda item: item[0])
    chunks = []
    records = []
    cursor = 0
    growth = 0
    for offset, added, symbol in insertions:
        chunks.extend((original[cursor:offset], added))
        records.append({
            "symbol": symbol,
            "original_offset": offset,
            "annotated_offset": offset + growth,
            "inserted_hex": added.hex(),
            "inserted_sha256": sha256(added),
        })
        growth += len(added)
        cursor = offset
    chunks.append(original[cursor:])
    annotated = b"".join(chunks)
    if strip_insertions(annotated, records) != original:
        raise ValueError(f"ghost-strip byte equality failed: {relative}")
    return source, original, annotated, records


def strip_insertions(annotated: bytes, records: list[dict]) -> bytes:
    stripped = annotated
    for record in reversed(records):
        added = bytes.fromhex(record["inserted_hex"])
        offset = record["annotated_offset"]
        if stripped[offset:offset + len(added)] != added:
            raise ValueError(f"insertion bookkeeping mismatch: {record['symbol']}")
        stripped = stripped[:offset] + stripped[offset + len(added):]
    return stripped


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".g1-annotation-", delete=False) as tmp:
        temp_path = Path(tmp.name)
        try:
            tmp.write(data)
            tmp.flush()
            os.fsync(tmp.fileno())
            os.chmod(temp_path, path.stat().st_mode & 0o777)
        except BaseException:
            temp_path.unlink(missing_ok=True)
            raise
    os.replace(temp_path, path)


def prepare(repo: Path, out: Path, manifest_path: Path | None = None) -> dict:
    """Inject into a disposable Cloud checkout and return a byte-equality receipt."""
    build_id = os.environ.get("BUILD_ID")
    if not build_id:
        raise ValueError("BUILD_ID missing; G1 injector is Cloud-only")
    repo = repo.resolve(strict=True)
    out = out.absolute()
    if out.parent.resolve().is_relative_to(repo):
        raise ValueError("certificate and source archive must be outside checkout")
    manifest_path = manifest_path or Path(__file__).with_name("annotations.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA:
        raise ValueError("unknown annotation manifest schema")
    head = git_head(repo)
    if head != manifest["source_commit"]:
        raise ValueError(f"source commit mismatch: {head}")
    if out.exists():
        raise ValueError("certificate path already exists")

    prepared = [prepare_file(repo, entry) for entry in manifest["files"]]
    source_archive = out.parent / "sources"
    if source_archive.exists():
        raise ValueError("source archive directory already exists")
    certificate = {
        "schema": SCHEMA,
        "build_id": build_id,
        "source_commit": head,
        "refinedrust_commit": manifest["refinedrust_commit"],
        "manifest_sha256": sha256(manifest_path.read_bytes()),
        "files": [],
        "source_receipt": {"sources": {}},
    }
    archive_payloads = []
    for entry, (source, original, annotated, records) in zip(manifest["files"], prepared, strict=True):
        key = entry["source_key"]
        if not key.isidentifier() or key in certificate["source_receipt"]["sources"]:
            raise ValueError(f"invalid or duplicate source key: {key}")
        certificate["files"].append({
            "path": source.relative_to(repo).as_posix(),
            "original_sha256": sha256(original),
            "annotated_sha256": sha256(annotated),
            "strip_equals_original": True,
            "insertions": records,
        })
        paths = {
            "original_path": f"sources/{key}.original.rs",
            "annotated_path": f"sources/{key}.annotated.rs",
            "stripped_path": f"sources/{key}.stripped.rs",
        }
        certificate["source_receipt"]["sources"][key] = {
            **paths,
            "original_sha256": sha256(original),
            "annotated_sha256": sha256(annotated),
            "stripped_sha256": sha256(original),
            "strip_equals_original": True,
        }
        archive_payloads.extend((
            (out.parent / paths["original_path"], original),
            (out.parent / paths["annotated_path"], annotated),
            (out.parent / paths["stripped_path"], strip_insertions(annotated, records)),
        ))

    # All source hashes, anchors, and strip certificates were checked before the first write.
    for source, _, annotated, _ in prepared:
        atomic_write(source, annotated)
    for source, original, annotated, records in prepared:
        actual = source.read_bytes()
        if actual != annotated or strip_insertions(actual, records) != original:
            raise ValueError(f"post-write ghost-strip byte equality failed: {source}")
    out.parent.mkdir(parents=True, exist_ok=True)
    source_archive.mkdir()
    for path, data in archive_payloads:
        with path.open("xb") as payload:
            payload.write(data)
    with out.open("x", encoding="utf-8") as output:
        json.dump(certificate, output, indent=2, sort_keys=True)
        output.write("\n")
    return certificate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True, help="disposable pinned Rust checkout")
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("annotations.json"))
    parser.add_argument("--certificate", type=Path, required=True, help="new output path outside tracked source")
    args = parser.parse_args()
    prepare(args.repo, args.certificate, args.manifest)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"G1 annotation injection refused: {error}", file=sys.stderr)
        sys.exit(1)
