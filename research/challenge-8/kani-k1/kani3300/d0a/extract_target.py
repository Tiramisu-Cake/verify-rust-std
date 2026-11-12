#!/usr/bin/env python3
"""Read only D0 property fragments; never promote a capped capture to complete.

No verifier/compiler invocation. Coordinates are zero-based byte/trace indices.
The CBMC result header indentation is deliberate: nested failure steps cannot
be mistaken for property results. Raw data and full traces are never emitted.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

PROPERTY = "<u8 as std::array::equality::SpecArrayEq<u8, 4>>::spec_eq.safety_check."
RESULT = re.compile(rb'^      \{\n        "description": [^\n]+\n        "property": "([^"\n]+)"', re.M)
FIELDS = {"tracked_object_id", "tracked_offset", "value"}
SOURCES = {"candidate": "5eec235e3d0eeb99d7e432fcaef3a3135747b789",
           "baseline": "a0a2386001a15fecfe2facc2f6cd87f3dee13b60"}
SPEC_EQ = PROPERTY.rsplit(".safety_check.", 1)[0]


def read_bounded(path, limit):
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"input exceeds explicit read limit: {path}")
    return data


def check_location(loc):
    if not isinstance(loc, dict) or not str(loc.get("file", "")).endswith("/core/src/array/equality.rs"):
        raise ValueError("wrong/missing source file")
    if loc.get("function") != SPEC_EQ or str(loc.get("line")) != "157":
        raise ValueError("source function/line mismatch")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def compact(value):
    """Keep decoded values, omitting redundant bit strings and packing bool masks."""
    if value.get("name") == "array":
        elements = value.get("elements", [])
        if all(e.get("index") == i and e.get("value", {}).get("data") in {"TRUE", "FALSE"}
               for i, e in enumerate(elements)):
            return {"name": "array", "length": len(elements),
                    "mask": "".join("1" if e["value"]["data"] == "TRUE" else "0" for e in elements)}
    return {k: v for k, v in value.items() if k != "binary"}


def fragment(data, suffix):
    wanted = PROPERTY + suffix
    matches = [m for m in RESULT.finditer(data) if m[1].decode() == wanted]
    if len(matches) != 1:
        return {"state": "UNAVAILABLE", "matching_result_headers": len(matches)}
    start = matches[0].start() + 6
    suffix_bytes = data[start:]
    try:
        text = suffix_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        if exc.reason != "unexpected end of data" or exc.end != len(suffix_bytes):
            return {"state": "INVALID_UTF8", "start_byte": start}
        # A capped suffix can end inside a codepoint after the selected object.
        text = suffix_bytes[:exc.start].decode("utf-8")
    try:
        obj, end = json.JSONDecoder().raw_decode(text)
    except json.JSONDecodeError as exc:
        return {"state": "PARTIAL", "start_byte": start, "error": exc.msg}
    assert isinstance(obj, dict) and obj.get("property") == wanted
    check_location(obj.get("sourceLocation"))
    end = start + len(text[:end].encode("utf-8"))
    return {"state": "COMPLETE_RESULT_FRAGMENT", "start_byte": start,
            "end_byte_exclusive": end, "sha256": sha(data[start:end]), "object": obj}


def summarize(prop):
    if prop.get("property") != PROPERTY + "2" or prop.get("status") != "FAILURE":
        raise ValueError("wrong property/status")
    trace = prop.get("trace")
    if not isinstance(trace, list) or not trace:
        raise ValueError("missing/wrong-type/empty trace")
    if not all(isinstance(t, dict) for t in trace):
        raise ValueError("non-object trace entry")
    if trace[-1].get("stepType") != "failure" or trace[-1].get("property") != prop["property"]:
        raise ValueError("partial or wrong-target trace endpoint")
    check_location(prop.get("sourceLocation"))
    check_location(trace[-1].get("sourceLocation"))
    if len(trace) < 2 or trace[0].get("stepType") != "location-only" or trace[1].get("function", {}).get("displayName") != "__CPROVER_initialize":
        raise ValueError("missing trace initialization prefix")
    frames, calls, writes, checks = [], [], [], []
    for i, t in enumerate(trace):
        typ = t.get("stepType")
        fn = t.get("function", {}).get("displayName")
        if typ == "function-call":
            if not isinstance(fn, str):
                raise ValueError("call missing function identity")
            frames.append({"function": fn, "call_index": i, "assignments": []})
        elif typ == "function-return":
            if not frames or frames[-1]["function"] != fn:
                raise ValueError("unbalanced trace call stack")
            frame = frames.pop()
            if "MemoryInitializationState::" in fn:
                last = {}
                for j, assignment in frame["assignments"]:
                    lhs = assignment.get("lhs")
                    if lhs in {"ptr", "obj", "offset", "from_obj", "from_offset", "to_obj",
                               "to_offset", "num_elts", "value", "layout", "var_0"}:
                        last[lhs] = {"index": j, "value": compact(assignment["value"])}
                calls.append({"function": fn, "call_index": frame["call_index"],
                              "return_index": i, "final_assignments": last})
        elif typ == "assignment":
            lhs, value = t.get("lhs"), t.get("value")
            if not isinstance(lhs, str) or not isinstance(value, dict):
                raise ValueError("assignment missing/wrong-type lhs/value")
            if frames:
                frames[-1]["assignments"].append((i, t))
            if "MEM_INIT_STATE" in lhs and (lhs.rsplit(".", 1)[-1] in FIELDS or "." not in lhs):
                if "." not in lhs:
                    raise ValueError("whole-state assignment: field-last identity unavailable")
                writes.append({"index": i, "lhs": lhs, "value": compact(value),
                               "sourceLocation": t.get("sourceLocation"),
                               "frame": frames[-1]["function"] if frames else None})
            if t.get("sourceLocation", {}).get("function", "").endswith("::spec_eq"):
                if lhs in {"var_4", "var_11"}:
                    checks.append({"index": i, "lhs": lhs, "value": compact(value)})
    root = frames[0]["function"] if frames else None
    if root not in {"array_value_as_used_by_merge_output", "partial_copy_preserves_written_byte"}:
        raise ValueError("wrong/missing trace root")
    if len(frames) != 3 or frames[-1]["function"] != SPEC_EQ or frames[1]["function"] != "std::array::equality::<impl std::cmp::PartialEq for [u8; 4]>::eq":
        raise ValueError("unexpected open call stack at failure")
    selected = {k: next((w for w in reversed(writes) if w["lhs"].endswith("." + k)), None)
                for k in FIELDS}
    gets = [c for c in calls if "::get::<4>" in c["function"]][-2:]
    if len(gets) != 2:
        raise ValueError("missing equality get calls")
    return {"trace_count": len(trace), "root": root, "failure_index": len(trace)-1,
            "failure": trace[-1], "end_stack": [f["function"] for f in frames],
            "state_writes": writes, "last_state_writes": selected,
            "shadow_calls": calls, "equality_gets": gets, "spec_eq_results": checks,
            "coverage": {"trace_entries_examined": len(trace), "call_stack_checked": True,
                         "all_MEM_INIT_STATE_field_and_whole_assignments_examined": True,
                         "other_assignments_emitted": False},
            "pointer_rendering_warning": "unknown ptr text is preserved; numeric obj/offset are executed assignments"}


def collect(base):
    rows = []
    for f in sorted(base.glob("*/cases/*/cbmc-private/*.meta.json")):
        meta_bytes = read_bounded(f, 64 * 1024)
        meta = json.loads(meta_bytes)
        if meta.get("child_exit") != 10:
            continue  # Excludes --version probes, not failed verification captures.
        raw = f.with_name(f.name.replace(".meta.json", ".json"))
        data = read_bounded(raw, 64 * 1024 * 1024)
        case = f.parents[1]
        lane = case.parents[1].name
        results = json.loads(read_bounded(case / "results.json", 1024 * 1024))
        if lane not in SOURCES or results.get("kani_commit") != SOURCES[lane] or results.get("kani_commit_dirty") is not False:
            raise ValueError("source identity/dirty mismatch")
        roots_bytes = read_bounded(case / "roots.json", 64 * 1024)
        roots = json.loads(roots_bytes)
        matches = [r for r in roots if r["solver_input"] in meta["argv"]]
        if len(matches) != 1:
            raise ValueError(f"ambiguous/missing exact argv input: {f}")
        root = matches[0]
        model = case / "model" / Path(root["solver_input"]).name
        model_sha = sha(read_bounded(model, 128 * 1024 * 1024))
        if model_sha != root["solver_input_sha256"]:
            raise ValueError(f"solver input SHA mismatch: {model}")
        row = {"capture": str(raw.relative_to(base)), "source": SOURCES[lane], "meta_sha256": sha(meta_bytes),
               "retained_prefix_sha256": sha(data), "full_stdout_sha256_declared": meta["original_stdout_sha256"],
               "retained_bytes": len(data), "dropped_bytes": meta["dropped_bytes"],
               "captured_complete": meta["captured_complete"], "capture_state": meta["capture_state"],
               "original_solver_exit": meta["child_exit"], "solver_input_sha256": model_sha,
               "roots_sha256": sha(roots_bytes), "root": root["pretty_name"],
               "input_binding": "exact captured argv = roots path; local model SHA verified",
               "full_stdout_integrity": "UNKNOWN: only retained prefix available",
               "properties": {}}
        for suffix in ["1", "2"]:
            frag = fragment(data, suffix)
            obj = frag.pop("object", None)
            if obj:
                frag["status"] = obj.get("status")
                frag["sourceLocation"] = obj.get("sourceLocation")
                if suffix == "2":
                    frag["witness"] = summarize(obj)
                    if frag["witness"]["root"] != row["root"]:
                        raise ValueError("trace root/argv root mismatch")
            row["properties"][suffix] = frag
        rows.append(row)
    return {"schema": "kani3300-d0a-target-fragments-v1", "run": "43209338134",
            "scope": "selected complete result fragments inside INCOMPLETE captures; no global solver success claim",
            "coordinate_convention": "zero-based bytes; half-open fragments; zero-based /trace indices",
            "captures": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("private", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = collect(args.private)
    encoded = (json.dumps(result, indent=2) + "\n").encode()
    if len(encoded) > 1024 * 1024:
        raise ValueError("curated output exceeds 1 MiB")
    args.output.write_bytes(encoded)
    print(json.dumps({"captures": len(result["captures"]), "output_bytes": len(encoded),
                      "complete_target_fragments": sum(r["properties"]["2"]["state"] == "COMPLETE_RESULT_FRAGMENT" for r in result["captures"])}))
