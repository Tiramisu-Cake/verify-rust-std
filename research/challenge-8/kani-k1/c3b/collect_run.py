"""Collect only the authorized bounded k1g interfaces; never read cached/raw Kani output."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
HELPER = BASE.parent / "tools/k1g.sh"
ENV = dict(os.environ, TMPDIR=str(BASE.parent / ".c3b-tmp"),
           K1_CACHE=str(BASE.parent / ".c3b-cache"),
           K1_GCLOUD_CONFIG=str(BASE.parent / ".c3b-cache/gcloud"))


def query(*args):
    result = subprocess.run([str(HELPER), *args], cwd=ROOT, env=ENV,
                            text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-1800:] or result.stdout[-1800:])
    return result.stdout


def page_fields(text):
    return dict(line.split("=", 1) for line in text.splitlines()
                if "=" in line and "\t" not in line)


def collect(label, inventory=False):
    if not re.fullmatch(r"[a-z0-9-]+", label):
        raise ValueError("invalid label")
    entries = json.loads((BASE / "builds.json").read_text())
    matching = [entry for entry in entries if entry["label"] == label]
    if len(matching) != 1:
        raise ValueError("build label is missing or ambiguous")
    entry = matching[0]
    build = entry["build_id"]
    summary = query("summary", build)
    (BASE / f"{label}.summary.md").write_text(summary)
    rows = query("summary", build, "0", "80")
    fields = page_fields(rows)
    if fields["head_sha"] != entry["sha"] or fields["build_id"] != build:
        raise ValueError("summary identities do not match build register")
    if fields["next_offset"] != "done" or int(fields["count"]) != entry["harnesses"]:
        raise ValueError("expected the whole <=80 harness request in one page")
    (BASE / f"{label}.rows.tsv").write_text(rows)
    (BASE / f"{label}.peaks.txt").write_text(query("peaks", build))
    if inventory:
        offset = 0
        names = []
        identity = None
        while True:
            page = query("inventory", build, str(offset), "80")
            fields = page_fields(page)
            binding = tuple(fields[key] for key in
                            ("inventory_sha256", "names_sha256", "total", "head_sha", "build_id"))
            if identity is not None and binding != identity:
                raise ValueError("inventory identities changed between pages")
            identity = binding
            if fields["head_sha"] != entry["sha"] or fields["build_id"] != build:
                raise ValueError("inventory identities do not match build register")
            found = [line for line in page.splitlines()
                     if line.startswith("slice::sort::shared::smallsort::verify::")]
            if int(fields["offset"]) != offset or len(found) != int(fields["count"]):
                raise ValueError("incomplete inventory page")
            (BASE / f"{label}.inventory-{offset}.page").write_text(page)
            names.extend(found)
            next_offset = fields["next_offset"]
            if next_offset == "done":
                break
            offset = int(next_offset)
        canonical = "\n".join(names) + "\n"
        if len(names) != int(fields["total"]) or len(set(names)) != len(names):
            raise ValueError("inventory count or uniqueness failure")
        if hashlib.sha256(canonical.encode()).hexdigest() != fields["names_sha256"]:
            raise ValueError("assembled inventory SHA mismatch")
        (BASE / f"{label}.ordinary.txt").write_text(canonical)
        predicted = set((BASE / "predicted-ordinary.txt").read_text().splitlines())
        print(json.dumps({"label": label, "inventory_count": len(names),
                          "missing_from_prediction": sorted(set(names) - predicted),
                          "absent_in_remote": sorted(predicted - set(names))}))
    print(f"collected {label} build={build} harnesses={entry['harnesses']}")


if __name__ == "__main__":
    try:
        collect(sys.argv[1], "--inventory" in sys.argv[2:])
    except (ValueError, KeyError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(2)
