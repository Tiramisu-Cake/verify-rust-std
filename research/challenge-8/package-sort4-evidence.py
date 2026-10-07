#!/usr/bin/env python3
"""Create a compact, hash-indexed copy of one immutable Actions artifact.

This is intended to run only on a GitHub-hosted runner. It reads the exact
artifact selected by run and artifact ID, streams its ZIP members through the
curation rules, and never extracts archive paths onto disk.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import pathlib
import re
import stat
import sys
import urllib.error
import urllib.request
import zipfile
import zlib
from datetime import datetime, timezone


REPO = "Tiramisu-Cake/verify-rust-std"
SOURCE_RUN_ID = 37601511894
SOURCE_ARTIFACT_ID = 11473086721
SOURCE_HEAD_SHA = "182ddf29dc73961723bf32be6b65643c524ca927"
SOURCE_ARTIFACT_NAME = "smallsort-research-37601511894-1"
EVIDENCE_ROOT = "maybeuninit-new-pointer/"
MAX_COMPACT_BYTES = 25 * 1024 * 1024
RANGE_CACHE_BYTES = 1024 * 1024
CURRENT_SUFFIXES = {
    ".bin", ".csv", ".diff", ".json", ".log", ".md", ".patch", ".rs",
    ".py", ".sh", ".stderr", ".stdout", ".toml", ".txt", ".yaml", ".yml",
}
CURRENT_EXCLUDED_SUFFIXES = {
    ".a", ".deb", ".dll", ".dylib", ".exe", ".gz", ".o", ".pyc",
    ".rlib", ".rmeta", ".rpm", ".so", ".tar", ".whl", ".xz", ".zip",
}
CURRENT_EXCLUDED_DIRS = {
    ".cargo", "bin", "build", "compact-evidence", "lib", "lib64",
    "mutation-profile", "node_modules", "rustlib", "site-packages", "target",
    "tool", "tools", "vendor",
}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def api_json(url: str, token: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + token,
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def artifact_download_url(artifact_id: int, token: str) -> str:
    url = f"https://api.github.com/repos/{REPO}/actions/artifacts/{artifact_id}/zip"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + token,
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        urllib.request.build_opener(NoRedirect).open(request, timeout=60)
    except urllib.error.HTTPError as error:
        if error.code != 302:
            raise RuntimeError(f"artifact download API returned HTTP {error.code}") from None
        location = error.headers.get("Location")
        if not location:
            raise RuntimeError("artifact download API omitted its signed URL")
        return location
    raise RuntimeError("artifact download API unexpectedly returned a body without redirect")


class RangeReader(io.RawIOBase):
    """Seekable HTTP range reader; refuses servers that would send the full ZIP."""

    def __init__(self, url: str, expected_size: int):
        self.url = url
        self.expected_size = expected_size
        self.position = 0
        self.cache_start = -1
        self.cache = b""
        request = urllib.request.Request(url, headers={"Range": "bytes=0-0"})
        with urllib.request.urlopen(request, timeout=60) as response:
            if response.status != 206:
                raise RuntimeError("artifact host does not support bounded range reads")
            content_range = response.headers.get("Content-Range", "")
            match = re.fullmatch(r"bytes 0-0/(\d+)", content_range)
            if not match or int(match.group(1)) != expected_size:
                raise RuntimeError("artifact range size differs from GitHub metadata")
            first_byte = response.read()
            if len(first_byte) != 1:
                raise RuntimeError("artifact range probe returned an invalid byte count")
            self.cache_start, self.cache = 0, first_byte

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=os.SEEK_SET):
        if whence == os.SEEK_SET:
            position = offset
        elif whence == os.SEEK_CUR:
            position = self.position + offset
        elif whence == os.SEEK_END:
            position = self.expected_size + offset
        else:
            raise ValueError("invalid seek origin")
        if position < 0:
            raise ValueError("negative seek")
        self.position = position
        return position

    def read(self, size=-1):
        if size is None or size < 0:
            size = self.expected_size - self.position
        size = min(size, self.expected_size - self.position)
        if size <= 0:
            return b""
        end_position = self.position + size
        if not (self.cache_start <= self.position and
                end_position <= self.cache_start + len(self.cache)):
            end = min(self.expected_size, self.position + max(size, RANGE_CACHE_BYTES)) - 1
            request = urllib.request.Request(
                self.url,
                headers={"Range": f"bytes={self.position}-{end}"},
            )
            with urllib.request.urlopen(request, timeout=120) as response:
                expected_range = f"bytes {self.position}-{end}/{self.expected_size}"
                if response.status != 206 or response.headers.get("Content-Range") != expected_range:
                    raise RuntimeError("artifact host returned an invalid bounded range")
                self.cache = response.read()
                self.cache_start = self.position
                if len(self.cache) != end - self.position + 1:
                    raise RuntimeError("artifact host returned a truncated range")
        start = self.position - self.cache_start
        result = self.cache[start:start + size]
        self.position += len(result)
        return result


def safe_member_name(name: str) -> pathlib.PurePosixPath:
    if "\x00" in name or "\\" in name or name.startswith("/") or re.match(r"^[A-Za-z]:", name):
        raise RuntimeError(f"unsafe archive member path: {name!r}")
    path = pathlib.PurePosixPath(name)
    if ".." in path.parts or not path.parts:
        raise RuntimeError(f"unsafe archive member path: {name!r}")
    return path


def classify(info: zipfile.ZipInfo, path: pathlib.PurePosixPath) -> tuple[bool, str]:
    if info.is_dir():
        return False, "directory entry; child entries are classified separately"
    if not info.filename.startswith(EVIDENCE_ROOT):
        raise RuntimeError(f"unexpected source artifact entry outside evidence root: {info.filename}")
    if "mutation-profile" in path.parts:
        return False, "disposable shadow tool profile; contains tool/library links or copies"
    mode = (info.external_attr >> 16) & 0xFFFF
    if mode and (mode & 0o170000) == 0o120000:
        return False, "symbolic link entry; never followed or copied"
    return True, "curated evidence under maybeuninit-new-pointer"


def hash_member(source: zipfile.ZipFile, info: zipfile.ZipInfo,
                target: zipfile.ZipFile | None, target_name: str | None) -> str:
    digest = hashlib.sha256()
    crc = 0
    count = 0
    input_stream = source.open(info, "r")
    if target is None:
        with input_stream as stream:
            while True:
                chunk = stream.read(256 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
                crc = zlib.crc32(chunk, crc)
                count += len(chunk)
    else:
        assert target_name is not None
        with input_stream as stream, target.open(target_name, "w", force_zip64=True) as output:
            while True:
                chunk = stream.read(256 * 1024)
                if not chunk:
                    break
                output.write(chunk)
                digest.update(chunk)
                crc = zlib.crc32(chunk, crc)
                count += len(chunk)
    if count != info.file_size or (crc & 0xFFFFFFFF) != info.CRC:
        raise RuntimeError(f"source ZIP member failed size/CRC validation: {info.filename}")
    return digest.hexdigest()


def current_file_decision(relative: pathlib.PurePosixPath, is_dir: bool,
                          is_symlink: bool, is_executable: bool = False) -> tuple[bool, str]:
    if is_symlink:
        return False, "symbolic link; never followed or copied"
    if is_dir:
        if relative.name in CURRENT_EXCLUDED_DIRS:
            return False, "tool/build/shadow/compact-output directory excluded recursively"
        return False, "directory entry; child entries are classified separately"
    if any(part in CURRENT_EXCLUDED_DIRS for part in relative.parts[:-1]):
        return False, "tool/build/shadow/compact-output subtree excluded"
    suffix = relative.suffix.lower()
    if suffix in CURRENT_EXCLUDED_SUFFIXES:
        return False, "binary, library, or packaged dependency excluded"
    if is_executable and suffix not in CURRENT_SUFFIXES:
        return False, "executable tool payload excluded"
    if suffix not in CURRENT_SUFFIXES:
        raise RuntimeError(f"unclassified current evidence file suffix: {relative.as_posix()}")
    return True, "curated current run evidence file"


def checked_size(path: pathlib.Path, limit: int = MAX_COMPACT_BYTES) -> int:
    size = path.stat().st_size
    if size > limit:
        raise RuntimeError(f"compact archive is {size} bytes; limit is {limit} bytes")
    return size


def validate_manifest_entries(entries: list[dict]) -> None:
    seen = set()
    for entry in entries:
        identity = (entry.get("source_set"), entry.get("source_entry"))
        if not identity[0] or not identity[1] or identity in seen:
            raise RuntimeError("manifest has a missing or duplicate source entry identity")
        source_path = safe_member_name(identity[1].rstrip("/"))
        if identity[0] == "o4" and not source_path.as_posix().startswith(EVIDENCE_ROOT):
            raise RuntimeError("O4 manifest entry is outside the selected evidence root")
        if identity[0] == "current" and source_path.parts[0] != "research-results":
            raise RuntimeError("current manifest entry is outside research-results")
        if identity[0] not in {"o4", "current"}:
            raise RuntimeError("manifest entry has an unknown source set")
        seen.add(identity)
        if entry.get("included"):
            if not re.fullmatch(r"[0-9a-f]{64}", entry.get("sha256") or ""):
                raise RuntimeError("included manifest entry has no valid SHA256")
            compact_entry = entry.get("compact_entry") or ""
            if not compact_entry:
                raise RuntimeError("included manifest entry has no compact archive path")
            compact_path = safe_member_name(compact_entry)
            if compact_path.parts[0] not in {"o4", "current"}:
                raise RuntimeError("included manifest entry has an invalid compact archive root")
            if not isinstance(entry.get("file_size"), int) or entry["file_size"] < 0:
                raise RuntimeError("included manifest entry has no valid file size")
            if not re.fullmatch(r"[0-9a-f]{8}", entry.get("crc32") or ""):
                raise RuntimeError("included manifest entry has no valid CRC32")
        elif not entry.get("reason"):
            raise RuntimeError("excluded manifest entry has no explicit reason")


def add_current_evidence(compact: zipfile.ZipFile, results_dir: pathlib.Path) -> list[dict]:
    records = []
    if not results_dir.exists():
        raise RuntimeError("current research-results directory is missing")
    root = results_dir.resolve()
    for directory, dirs, files in os.walk(results_dir, topdown=True, followlinks=False):
        directory_path = pathlib.Path(directory)
        retained_dirs = []
        for name in sorted(dirs):
            path = directory_path / name
            relative = pathlib.PurePosixPath(path.relative_to(results_dir).as_posix())
            is_link = path.is_symlink()
            include, reason = current_file_decision(relative, True, is_link)
            records.append({
                "source_entry": "research-results/" + relative.as_posix() + "/",
                "compact_entry": None,
                "included": include,
                "reason": reason,
                "file_size": path.lstat().st_size,
                "compressed_size": None,
                "crc32": None,
                "sha256": None,
            })
            if not is_link and not any(part in CURRENT_EXCLUDED_DIRS for part in relative.parts):
                retained_dirs.append(name)
        dirs[:] = retained_dirs
        for name in sorted(files):
            path = directory_path / name
            relative = pathlib.PurePosixPath(path.relative_to(results_dir).as_posix())
            is_link = path.is_symlink()
            executable = not is_link and bool(path.lstat().st_mode & 0o111)
            include, reason = current_file_decision(relative, False, is_link, executable)
            record = {
                "source_entry": "research-results/" + relative.as_posix(),
                "compact_entry": None,
                "included": include,
                "reason": reason,
                "file_size": path.lstat().st_size,
                "compressed_size": None,
                "crc32": None,
                "sha256": None,
            }
            if include:
                resolved = path.resolve(strict=True)
                if not resolved.is_relative_to(root):
                    raise RuntimeError(f"current evidence path escapes research-results: {relative}")
                digest = hashlib.sha256()
                crc = 0
                size = 0
                compact_name = "current/" + relative.as_posix()
                descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
                with os.fdopen(descriptor, "rb") as source, compact.open(
                    compact_name, "w", force_zip64=True
                ) as target:
                    if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
                        raise RuntimeError(f"current evidence entry is not a regular file: {relative}")
                    while True:
                        chunk = source.read(256 * 1024)
                        if not chunk:
                            break
                        target.write(chunk)
                        digest.update(chunk)
                        crc = zlib.crc32(chunk, crc)
                        size += len(chunk)
                record.update({
                    "compact_entry": compact_name,
                    "file_size": size,
                    "crc32": f"{crc & 0xffffffff:08x}",
                    "sha256": digest.hexdigest(),
                })
            records.append(record)
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN")
    if not token:
        raise RuntimeError("GH_TOKEN is required")
    run = api_json(f"https://api.github.com/repos/{REPO}/actions/runs/{SOURCE_RUN_ID}", token)
    artifact = api_json(
        f"https://api.github.com/repos/{REPO}/actions/artifacts/{SOURCE_ARTIFACT_ID}", token
    )
    run_artifacts = api_json(
        f"https://api.github.com/repos/{REPO}/actions/runs/{SOURCE_RUN_ID}/artifacts?per_page=100",
        token,
    )
    matching_artifacts = [
        entry for entry in run_artifacts.get("artifacts", [])
        if entry.get("id") == SOURCE_ARTIFACT_ID
    ]

    checks = {
        "run_id": run.get("id") == SOURCE_RUN_ID,
        "run_head_sha": run.get("head_sha") == SOURCE_HEAD_SHA,
        "run_repository": (run.get("repository") or {}).get("full_name") == REPO,
        "artifact_id": artifact.get("id") == SOURCE_ARTIFACT_ID,
        "artifact_name": artifact.get("name") == SOURCE_ARTIFACT_NAME,
        "artifact_attached_to_selected_run": len(matching_artifacts) == 1,
        "artifact_not_expired": artifact.get("expired") is False,
    }
    failed = [key for key, valid in checks.items() if not valid]
    if failed:
        raise RuntimeError("selected source identity failed: " + ", ".join(failed))

    download_url = artifact_download_url(SOURCE_ARTIFACT_ID, token)
    del token

    size = artifact.get("size_in_bytes")
    if not isinstance(size, int) or size <= 0:
        raise RuntimeError("GitHub artifact metadata omitted a valid archive size")
    output_dir = pathlib.Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    compact_path = output_dir / "sort4-select-compact-evidence.zip"
    working_path = output_dir / "sort4-select-compact-evidence.zip.partial"
    compact_path.unlink(missing_ok=True)
    working_path.unlink(missing_ok=True)
    manifest_entries = []
    included_count = 0
    with RangeReader(download_url, size) as remote, zipfile.ZipFile(remote, "r") as source:
        infos = source.infolist()
        seen = set()
        with zipfile.ZipFile(working_path, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=6, allowZip64=True) as compact:
            for info in infos:
                path = safe_member_name(info.filename)
                if info.filename in seen:
                    raise RuntimeError(f"duplicate source ZIP member: {info.filename}")
                seen.add(info.filename)
                include, reason = classify(info, path)
                target_name = "o4/" + info.filename if include else None
                sha256 = hash_member(source, info, compact, target_name) if include else None
                manifest_entries.append({
                    "source_set": "o4",
                    "source_entry": info.filename,
                    "compact_entry": target_name,
                    "included": include,
                    "reason": reason,
                    "file_size": info.file_size,
                    "compressed_size": info.compress_size,
                    "crc32": f"{info.CRC:08x}",
                    "sha256": sha256,
                    "compression": info.compress_type,
                    "external_mode": f"{(info.external_attr >> 16) & 0xffff:06o}",
                })
                included_count += int(include)
            if not included_count:
                raise RuntimeError("no evidence files matched the curation rules")
            current_records = add_current_evidence(compact, pathlib.Path("research-results"))
            current_included = sum(record["included"] for record in current_records)
            if not current_included:
                raise RuntimeError("no current research-results evidence files matched the curation rules")
            for record in current_records:
                record["source_set"] = "current"
            manifest_entries.extend(current_records)
            validate_manifest_entries(manifest_entries)

            manifest = {
                "format": "challenge-8-compact-evidence-v2",
                "created_utc": datetime.now(timezone.utc).isoformat(),
                "source": {
                    "repository": REPO,
                    "run_id": SOURCE_RUN_ID,
                    "run_url": run.get("html_url"),
                    "head_sha": run.get("head_sha"),
                    "ref": run.get("head_branch"),
                    "workflow_path": run.get("path"),
                    "artifact_id": SOURCE_ARTIFACT_ID,
                    "artifact_name": artifact.get("name"),
                    "artifact_size_in_bytes": size,
                    "artifact_digest": artifact.get("digest"),
                    "artifact_created_at": artifact.get("created_at"),
                    "artifact_expires_at": artifact.get("expires_at"),
                    "artifact_url": artifact.get("url"),
                    "artifact_archive_download_url": artifact.get("archive_download_url"),
                },
                "selection": {
                    "historical_evidence_root": EVIDENCE_ROOT,
                    "current_evidence_root": "research-results/",
                    "included_file_count": included_count + current_included,
                    "excluded_entry_count": len(manifest_entries) - included_count - current_included,
                    "excluded_policy": [
                        "directory entries are listed; known excluded directories represent their entire skipped subtree",
                        "mutation-profile shadow directories are omitted because they contain disposable tool/library links or copies",
                        "symbolic links are recorded and omitted without following them",
                        "excluded entries retain source ZIP CRC/size metadata where available; SHA256 is computed for included files",
                    ],
                    "source_accounting": {
                        "o4_archive_entries_all_listed": True,
                        "current_entries_outside_excluded_subtrees_all_listed": True,
                        "excluded_current_subtrees_listed_at_root_and_not_traversed": True,
                    },
                },
                "current_source": {
                    "repository": os.environ.get("GITHUB_REPOSITORY"),
                    "run_id": os.environ.get("GITHUB_RUN_ID"),
                    "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
                    "run_url": (
                        "https://github.com/" + os.environ["GITHUB_REPOSITORY"] +
                        "/actions/runs/" + os.environ["GITHUB_RUN_ID"]
                        if os.environ.get("GITHUB_REPOSITORY") and os.environ.get("GITHUB_RUN_ID")
                        else None
                    ),
                    "head_sha": os.environ.get("GITHUB_SHA"),
                    "ref": os.environ.get("GITHUB_REF"),
                    "proof_selection": os.environ.get("PROOF_SELECTION"),
                    "compact_artifact_name": (
                        "smallsort-select-compact-evidence-" +
                        os.environ["GITHUB_RUN_ID"] + "-" + os.environ["GITHUB_RUN_ATTEMPT"]
                        if os.environ.get("GITHUB_RUN_ID") and os.environ.get("GITHUB_RUN_ATTEMPT")
                        else None
                    ),
                    "compact_artifact_id": None,
                },
                "entries": manifest_entries,
            }
            compact.writestr(
                "COMPACT-EVIDENCE-MANIFEST.json",
                json.dumps(manifest, sort_keys=True, indent=2).encode("utf-8") + b"\n",
            )

    try:
        compact_size = checked_size(working_path)
    except RuntimeError:
        working_path.unlink(missing_ok=True)
        raise
    working_path.replace(compact_path)
    print(json.dumps({
        "compact_archive": str(compact_path),
        "compact_size_bytes": compact_size,
        "limit_bytes": MAX_COMPACT_BYTES,
        "source_run_id": SOURCE_RUN_ID,
        "source_artifact_id": SOURCE_ARTIFACT_ID,
        "included_historical_files": included_count,
        "included_current_files": current_included,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"compact evidence packaging failed: {error}", file=sys.stderr)
        raise SystemExit(1)
