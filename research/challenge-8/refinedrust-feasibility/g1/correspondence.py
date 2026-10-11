"""Read-only, fail-closed G1 source/MIR/Radium admission auditor.

This is a classifier of *saved* frontend output, never a proof or a frontend
driver.  The stock RR revision emits rustc ``.mir`` dumps under log/mir and
``generated_code_<crate>.v`` under output/<crate>/generated.  It emits no
machine-readable source-to-Radium map.  Consequently the caller supplies a
reviewed, file-hash-bound ``correspondence`` receipt; absence or disagreement
is INCONCLUSIVE, never guessed from a name appearing somewhere in a file.

``inspect_outputs(out_dir, source_receipt)`` accepts a dictionary with:

* ``reviewed_map_schema``: ``g1-reviewed-correspondence-v1`` when an external
  mapping is supplied.  The collector must separately check the map's
  independently reviewed SHA-256 before merging its fields.
* ``source_base_dir``: base for relative source archive paths.  The injector
  certificate puts ``sources/*.rs`` beside the certificate.
* ``sources``: mapping of source labels to {original_path, original_sha256,
  annotated_path, annotated_sha256, stripped_path}.  The stripped file must
  byte-equal an independently reconstructed strip of the annotated bytes.
* ``insertions``: mapping from source label to the injector certificate's
  ordered insertion records (offset, hex bytes, SHA-256).  Only the fixed RR
  ghost attributes are removed.  All four pinned source archives are required.
* ``body_map``: seven keys in ``BODY_SOURCES``.  Each gives source_line,
  mir_file/mir_sha256/mir_header and radium_file/radium_sha256/
  radium_definition.  The seventh is compiler CopyOnDrop DropGlue.
* ``correspondence``: mapping of event labels to {function, source_line,
  mir_file, mir_sha256, mir_bb, mir_callee, radium_file, radium_sha256,
  radium_definition, radium_bb, radium_callee_binding}.  File paths for MIR and
  Radium are relative to ``out_dir``.  The callee and binding are exact names
  found in the respective *selected block*, not search needles for full files.
* ``locals``: {gap_guard, tmp} MIR local names from the selected dump.  Debug
  declarations must substantiate each name.  No local name is inferred.
* ``callee_inventory``: each emitted ``CallS`` binding of each selected body,
  with {caller, binding, resolution, resolved_file, resolved_sha256,
  resolved_definition}; resolution is translated_body/compiler_glue/rr_shim/
  trait_contract/intrinsic.  The target definition must exist in hash-bound
  generated output under ``out_dir``.
* ``resource_inventory``: six named generated spec definitions with
  {file, sha256, definition}.  Presence only inventories syntax; no resource
  post or proof obligation is discharged.

The external reviewed-map JSON shape is::

    {"schema":"g1-reviewed-correspondence-v1",
     "correspondence":{}, "body_map":{}, "locals":{},
     "callee_inventory":[], "resource_inventory":{}}

Empty collections are a schema illustration and always fail closed.  Fill
exact observed file hashes, DefId/callee identities, source lines and block
numbers only after inspecting the saved Cloud output; do not generate guessed
mapping entries in the Cloud runner.

Required events are ``first_fnmut``, ``tail_read``, ``gap_copy``,
``late_fnmut``, ``normal_guard_drop``, ``late_guard_drop``.  The two Drop
events bind real MIR Drop terminators to generated Radium DropGlue calls;
they use the source line that creates ``gap_guard``.  Calls and graph
edges are inspected in the chosen MIR dump and translated Radium definition.
The final return value contains individual check statuses and an admission
correspondence verdict.  It never upgrades resource or proof obligations.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any


PINNED_SMALLSORT_SHA256 = "32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959"
PINNED_SOURCE_COMMIT = "c7ca8c467aecf10a4b53039372ee97714f854ee3"
PINNED_RR_COMMIT = "332d945fafa14bf55c0c8390cb35ec4b0c012cff"
# No verified bytes of the pinned Radium writer are available in this package.
# A reviewed-map claim or synthetic fixture cannot qualify the output contract.
RADIUM_OUTPUT_CONTRACT = "UNKNOWN"
REVIEWED_MAP_SCHEMA = "g1-reviewed-correspondence-v1"
PINNED_SOURCES = {
    "smallsort": PINNED_SMALLSORT_SHA256,
    "manually_drop": "17e8e41866d3eadcfdc6f1a516e4ed9dd5555e10ad725aac3b04aec7c759731b",
    "maybe_dangling": "1cf24b2ec36fff143f329f2ef6db5b4d47cfa798da7f30d88b554b712c8f4b53",
    "core_lib": "ec773985e10a944e1d4b0fc35ac22e163f59ef3af4ba5324df20129db18c7860",
}
BODY_SOURCES = {
    "insert_tail": ("smallsort", "unsafe fn insert_tail<", "insert_tail"),
    "CopyOnDrop_drop": ("smallsort", "fn drop(&mut self)", "CopyOnDrop"),
    "ManuallyDrop_new": ("manually_drop", "pub const fn new(value: T)", "ManuallyDrop"),
    "ManuallyDrop_deref": ("manually_drop", "fn deref(&self) -> &T", "ManuallyDrop"),
    "MaybeDangling_new": ("maybe_dangling", "pub const fn new(x: P) -> Self", "MaybeDangling"),
    "MaybeDangling_as_ref": ("maybe_dangling", "pub const fn as_ref(&self) -> &P", "MaybeDangling"),
    "CopyOnDrop_glue": ("smallsort", "impl<T> Drop for CopyOnDrop<T>", "CopyOnDrop"),
}
ALLOWED_GHOST_ATTRIBUTES = {
    '#![feature(register_tool)]', '#![register_tool(rr)]',
    '#[rr::verify]', '#[rr::may_unwind_if("True")]',
    '#[rr::refined_by("()" : "unit")]',
}
RESOURCE_FORM_TOKENS = {
    "fnmut": ("PostMut", "UnwindCondition", "unwind post"),
    "ptr_read": ("Copyable", "precondition", "postcondition"),
    "ptr_copy": ("ArraySynType", "precondition", "postcondition"),
    "guard_drop": ("precondition", "postcondition", "unwind post"),
    "manually_drop": ("precondition", "postcondition"),
    "maybe_dangling": ("precondition", "postcondition"),
}
REQUIRED_EVENTS = (
    "first_fnmut", "tail_read", "gap_copy", "late_fnmut",
    "normal_guard_drop", "late_guard_drop",
)
UNPROVED = (
    "generic T/F ownership and CURRENT state on normal/unwind",
    "borrow and lender recovery after FnMut panic",
    "scalar versus ArraySynType(T,1), layout, alignment and provenance",
    "ptr read/copy owner transfer and shim-to-actual-source correspondence",
    "generic guard invariant, payload Drop suppression semantics and full resource closure",
    "Rocq proof, transitive assumption closure and actual caller safety",
)


def _check(checks: list[dict[str, Any]], name: str, status: str, detail: str, **evidence: Any) -> None:
    checks.append({"id": name, "status": status, "detail": detail, "evidence": evidence})


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_file(path: Path, expected: str | None = None) -> tuple[str | None, str]:
    if not path.is_file():
        return None, f"missing file: {path}"
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return None, f"unreadable file: {path}: {exc}"
    digest = _sha(raw)
    if expected is None or not re.fullmatch(r"[0-9a-f]{64}", expected):
        return None, f"missing/invalid expected SHA-256 for {path}"
    if digest != expected:
        return None, f"SHA-256 mismatch for {path}: actual {digest}, receipt {expected}"
    try:
        return raw.decode("utf-8"), ""
    except UnicodeDecodeError:
        return None, f"non-UTF-8 text file: {path}"


def _inside(root: Path, relative: Any) -> Path | None:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
        return None
    candidate = root / relative
    if any(parent.is_symlink() for parent in (candidate, *candidate.parents) if parent != root.parent):
        return None
    path = candidate.resolve()
    return path if path.is_relative_to(root.resolve()) else None


def _mir_blocks(text: str) -> dict[int, str]:
    # rustc -Zdump-mir=all plain text, not Graphviz.  A malformed or unfamiliar
    # block shape simply yields no block and cannot grant admission.
    starts = list(re.finditer(r"(?m)^\s*bb(\d+)(?:\s*\([^\n]*\))?:\s*\{\s*$", text))
    blocks: dict[int, str] = {}
    for i, match in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        number = int(match.group(1))
        if number in blocks:
            return {}
        blocks[number] = text[match.end() : end]
    return blocks


def _radium_definition(text: str, name: str) -> str | None:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", name):
        return None
    pattern = re.compile(r"(?m)^Program Definition " + re.escape(name) + r"\b[^\n]*: function :=")
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        return None
    start = matches[0].start()
    end = text.find("Final Obligation.", start)
    if end < 0:
        return None
    body = text[start:end]
    if "f_code :=" not in body or "f_init :=" not in body:
        return None
    return body


def _radium_blocks(definition: str) -> dict[int, str]:
    # Stock writer emits <[ "_bbN" := ... ]>%E $ fragments.
    starts = list(re.finditer(r'"_bb(\d+)"\s*:=', definition))
    blocks: dict[int, str] = {}
    for i, match in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(definition)
        number = int(match.group(1))
        if number in blocks:
            return {}
        blocks[number] = definition[match.end() : end]
    return blocks


def _coq_tokens(text: str) -> list[str]:
    """Lex saved text, excluding nested Coq comments and keeping strings opaque.

    This is not a Coq parser. Unbalanced comments/strings/delimiters are errors;
    no search for call names in comments or quoted strings earns admission.
    """
    tokens: list[str] = []
    pos = 0
    while pos < len(text):
        if text[pos].isspace():
            pos += 1
        elif text.startswith('(*', pos):
            depth = 1
            pos += 2
            while depth and pos < len(text):
                if text.startswith('(*', pos):
                    depth += 1
                    pos += 2
                elif text.startswith('*)', pos):
                    depth -= 1
                    pos += 2
                else:
                    pos += 1
            if depth:
                raise ValueError('unterminated Coq comment')
        elif text[pos] == '"':
            start = pos
            pos += 1
            while pos < len(text):
                if text[pos] == '"':
                    if text.startswith('""', pos):
                        pos += 2
                    else:
                        pos += 1
                        break
                else:
                    pos += 1
            else:
                raise ValueError('unterminated Coq string')
            tokens.append(text[start:pos])
        else:
            match = re.match(r'[A-Za-z_][A-Za-z_0-9\']*|[0-9]+|:=|=>', text[pos:])
            token = match.group(0) if match else text[pos]
            tokens.append(token)
            pos += len(token)
    return tokens


def _coq_term(tokens: list[str], pos: int) -> tuple[list[str], int]:
    if pos >= len(tokens):
        raise ValueError('missing call argument')
    pairs = {'(': ')', '[': ']', '{': '}'}
    token = tokens[pos]
    if token in pairs:
        start = pos
        stack = [pairs[token]]
        pos += 1
        while stack and pos < len(tokens):
            token = tokens[pos]
            if token in pairs:
                stack.append(pairs[token])
            elif token in pairs.values():
                if stack.pop() != token:
                    raise ValueError('mismatched call argument delimiter')
            pos += 1
        if stack:
            raise ValueError('unterminated call argument')
        return tokens[start:pos], pos
    if token in pairs.values() or token in {';', '$', '%', ':='}:
        raise ValueError('invalid call argument')
    return [token], pos + 1


def _radium_calls(block: str) -> tuple[list[dict[str, Any]], str]:
    """Syntactic CallS inventory; deliberately does not assign argument roles.

    The old fixture has a bare location parameter and balanced argument terms.
    Counting those terms is useful service evidence, not qualification of the
    pinned generator. Qualified/complex callees and unknown CallS spellings
    fail closed until the exact pinned grammar is confirmed. The
    identical inventory is used for event detection and selected-body closure.
    """
    try:
        tokens = _coq_tokens(block)
        # Remove the legacy fixture's map fragment trailer, if present. Do not
        # treat f_init or the next map fragment as arguments of the final call.
        for pos in range(len(tokens) - 3):
            if tokens[pos:pos + 4] == [']', '>', '%', 'E']:
                tokens = tokens[:pos]
                break
        calls: list[dict[str, Any]] = []
        for pos, token in enumerate(tokens):
            if token.startswith('CallS') and token != 'CallS':
                raise ValueError('unknown CallS constructor')
            if token != 'CallS':
                continue
            if pos + 1 >= len(tokens) or not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', tokens[pos + 1]):
                raise ValueError('unknown CallS callee form')
            end = pos + 2
            # The lexer splits Coq qualified identifiers at dots. Reject before
            # parsing arguments so Module.FnMut_loc cannot become binding Module
            # with the rest of its name silently consumed as argument terms.
            if end < len(tokens) and tokens[end] == '.':
                raise ValueError('unsupported qualified CallS callee syntax')
            arguments: list[list[str]] = []
            while end < len(tokens):
                term, end = _coq_term(tokens, end)
                if 'CallS' in term:
                    raise ValueError('nested CallS requires a verified statement grammar')
                arguments.append(term)
            if not arguments:
                raise ValueError('CallS has no argument terms')
            calls.append({'binding': tokens[pos + 1], 'arguments': arguments})
        if len(calls) > 1:
            raise ValueError('multiple CallS in one block require a verified statement grammar')
        return calls, ''
    except ValueError as exc:
        return [], str(exc)


def _radium_inventory(definition: str) -> tuple[list[dict[str, Any]], str]:
    blocks = _radium_blocks(definition)
    if not blocks:
        return [], 'selected Radium blocks absent'
    calls: list[dict[str, Any]] = []
    for bb, block in blocks.items():
        found, error = _radium_calls(block)
        if error:
            return [], f'bb{bb}: {error}'
        calls.extend(dict(call, bb=bb) for call in found)
    try:
        # Calls outside recognized blocks cannot silently vanish from inventory.
        count = _coq_tokens(definition).count('CallS')
    except ValueError as exc:
        return [], str(exc)
    if count != len(calls):
        return [], 'CallS occurs outside the recognized block inventory'
    return calls, ''


def _successors(block: str, kind: str = "any") -> set[int]:
    # rustc terminators print e.g. [return: bb3, unwind: bb9],
    # [return: bb3, unwind: cleanup bb9], goto -> bb3, switchInt -> [...].
    block = re.sub(r'//[^\n]*', '', block)
    if kind == "unwind":
        patterns = (r"\bunwind:\s*(?:cleanup\s*)?bb(\d+)",)
    elif kind == "normal":
        patterns = (
            r"\breturn:\s*bb(\d+)",
            r"\bgoto\s*->\s*bb(\d+)",
            r"(?:\b\d+|otherwise):\s*bb(\d+)",
        )
    else:
        patterns = (r"\bbb(\d+)\b",)
    return {int(x) for pat in patterns for x in re.findall(pat, block, re.I)}


def _reachable(blocks: dict[int, str], start: int, target: int, kind: str = "normal") -> bool:
    pending = [start]
    seen: set[int] = set()
    while pending:
        current = pending.pop()
        if current == target:
            return True
        if current in seen or current not in blocks:
            continue
        seen.add(current)
        pending.extend(_successors(blocks[current], kind) - seen)
    return False


def _cleanup_outcomes(blocks: dict[int, str], first: int, guard_local: str) -> set[bool | None]:
    # None is an unestablished exit (missing block, cycle, unfamiliar terminal).
    # Never silently discard such a branch while accepting another good path.
    pending = [(first, False, frozenset())]
    outcomes: set[bool | None] = set()
    steps = 0
    while pending:
        current, dropped, path = pending.pop()
        steps += 1
        if steps > 10000:
            outcomes.add(None)
            break
        state = (current, dropped)
        if state in path or current not in blocks:
            outcomes.add(None)
            continue
        body = re.sub(r'//[^\n]*', '', blocks[current])
        dropped |= bool(re.search(r"(?m)^\s*drop\s*\(\s*" + re.escape(guard_local) + r"\s*\)\s*->", body))
        if re.search(r"(?m)^\s*(?:resume|UnwindResume)\s*;", body):
            outcomes.add(dropped)
            continue
        successors = _successors(body)
        terminal = bool(re.search(r'\bunwind\s+terminate\b|\bUnwindTerminate\b', body, re.I))
        if terminal:
            outcomes.add(dropped)
        if not successors and not terminal:
            outcomes.add(None)
        pending.extend((x, dropped, path | {state}) for x in successors)
    return outcomes


def _event_call(block: str, callee: str) -> bool:
    if not isinstance(callee, str) or not callee or "\n" in callee:
        return False
    # Exact callee expression in a terminator, not an arbitrary comment or
    # independent occurrence elsewhere in the dump.
    return bool(re.search(r"(?m)^\s*_[0-9]+\s*=\s*" + re.escape(callee) + r"\s*\(", block))


def _radium_call(block: str, binding: str) -> bool:
    """Match only an error-free shared inventory; never use a partial callee."""
    if not isinstance(binding, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", binding):
        return False
    calls, error = _radium_calls(block)
    return not error and len(calls) == 1 and calls[0]['binding'] == binding


def _source_path(base: Path, value: Any) -> Path:
    path = Path(str(value or ""))
    if ".." in path.parts:
        return base.resolve() / ".invalid-source-evidence-path"
    candidate = path if path.is_absolute() else base / path
    resolved_base = base.resolve()
    if any(parent.is_symlink() for parent in (candidate, *candidate.parents) if parent != resolved_base.parent):
        return resolved_base / ".invalid-source-evidence-path"
    resolved = candidate.resolve()
    return resolved if resolved.is_relative_to(resolved_base) else resolved_base / ".invalid-source-evidence-path"


def _strip_certified(annotated: bytes, records: Any) -> bytes | None:
    if not isinstance(records, list) or not records:
        return None
    stripped = annotated
    try:
        offsets = [record["annotated_offset"] for record in records]
        if any(not isinstance(x, int) or x < 0 for x in offsets) or offsets != sorted(set(offsets)):
            return None
        growth = 0
        for record in records:
            original_offset = record["original_offset"]
            if not isinstance(original_offset, int) or original_offset < 0 or record["annotated_offset"] != original_offset + growth:
                return None
            growth += len(bytes.fromhex(record["inserted_hex"]))
        for record in reversed(records):
            added = bytes.fromhex(record["inserted_hex"])
            offset = record["annotated_offset"]
            if not added or _sha(added) != record["inserted_sha256"] or stripped[offset : offset + len(added)] != added:
                return None
            lines = added.decode("utf-8").splitlines()
            if not lines or any(line.strip() not in ALLOWED_GHOST_ATTRIBUTES for line in lines):
                return None
            stripped = stripped[:offset] + stripped[offset + len(added) :]
        for record in records:
            offset = record["original_offset"]
            if offset > len(stripped) or (offset > 0 and stripped[offset - 1] != 10):
                return None
    except (KeyError, TypeError, ValueError, UnicodeDecodeError):
        return None
    return stripped


def inspect_outputs(out_dir: str | Path, source_receipt: dict[str, Any]) -> dict[str, Any]:
    """Classify saved G1 P1 output; never invoke a compiler or proof tool.

    OBSERVED means syntactic evidence in hash-bound files.  STOP is reserved for
    a *positively observed* contradictory MIR/translation fact; absent files,
    mappings, unsupported syntax, or unfinished runs are INCONCLUSIVE.  This
    verdict is only a correspondence gate, not G1 admission or proof acceptance.
    """
    root = Path(out_dir).resolve()
    checks: list[dict[str, Any]] = []
    _check(checks, 'radium_output_contract', RADIUM_OUTPUT_CONTRACT,
           'pinned generator/config/annotation semantics have not been independently inspected; no real-output PASS')
    if not isinstance(source_receipt, dict):
        source_receipt = {}
    schema = source_receipt.get("reviewed_map_schema")
    _check(checks, "reviewed_map_schema", "OBSERVED" if schema == REVIEWED_MAP_SCHEMA else "NOT_RUN" if schema is None else "INCONCLUSIVE", "external reviewed mapping schema present" if schema == REVIEWED_MAP_SCHEMA else "external reviewed mapping unavailable or wrong schema")
    for key, pinned in (("source_commit", PINNED_SOURCE_COMMIT), ("refinedrust_commit", PINNED_RR_COMMIT)):
        actual = source_receipt.get(key)
        _check(checks, key, "OBSERVED" if actual == pinned else "NOT_RUN" if actual is None else "STOP", "pinned input identity present" if actual == pinned else "pinned input identity missing or mismatched", expected=pinned, actual=actual)
    source_base = Path(str(source_receipt.get("source_base_dir") or root))
    sources = source_receipt.get("sources")
    insertions = source_receipt.get("insertions")
    insertions = insertions if isinstance(insertions, dict) else {}
    smallsort = sources.get("smallsort") if isinstance(sources, dict) else None
    source_text: str | None = None
    if not isinstance(smallsort, dict):
        _check(checks, "source_identity", "INCONCLUSIVE", "no smallsort source receipt")
    else:
        original = _source_path(source_base, smallsort.get("original_path"))
        annotated = _source_path(source_base, smallsort.get("annotated_path"))
        stripped = _source_path(source_base, smallsort.get("stripped_path"))
        expected = smallsort.get("original_sha256")
        source_text, error = _read_file(original, expected)
        ann_text, ann_error = _read_file(annotated, smallsort.get("annotated_sha256"))
        if expected != PINNED_SMALLSORT_SHA256:
            error = "source receipt is not pinned actual SmallSort SHA-256"
        if source_text is None or ann_text is None or not stripped.is_file() or error or ann_error:
            _check(checks, "source_identity", "INCONCLUSIVE", error or ann_error or "missing stripped source", original=str(original))
            source_text = None
        elif "smallsort" not in insertions:
            _check(checks, "source_identity", "INCONCLUSIVE", "missing independent ghost insertion records")
        elif _strip_certified(annotated.read_bytes(), insertions["smallsort"]) != original.read_bytes() or stripped.read_bytes() != original.read_bytes():
            _check(checks, "source_identity", "STOP", "ghost-stripped source differs byte-for-byte from pinned source", original=str(original))
            source_text = None
        else:
            _check(checks, "source_identity", "OBSERVED", "pinned source, annotated bytes and stripped equality observed", sha256=expected)

    source_texts: dict[str, str | None] = {"smallsort": source_text}
    for key, pin in PINNED_SOURCES.items():
        if key == "smallsort":
            continue
        entry = sources.get(key) if isinstance(sources, dict) else None
        if not isinstance(entry, dict) or entry.get("original_sha256") != pin:
            _check(checks, f"source:{key}", "INCONCLUSIVE", "missing pinned source archive receipt")
            source_texts[key] = None
            continue
        original = _source_path(source_base, entry.get("original_path"))
        annotated = _source_path(source_base, entry.get("annotated_path"))
        stripped = _source_path(source_base, entry.get("stripped_path"))
        original_text, error = _read_file(original, pin)
        annotated_text, ann_error = _read_file(annotated, entry.get("annotated_sha256"))
        if original_text is None or annotated_text is None or error or ann_error or not stripped.is_file():
            _check(checks, f"source:{key}", "INCONCLUSIVE", error or ann_error or "missing stripped source")
            source_texts[key] = None
        elif key not in insertions:
            _check(checks, f"source:{key}", "INCONCLUSIVE", "missing independent ghost insertion records")
            source_texts[key] = original_text
        elif _strip_certified(annotated.read_bytes(), insertions[key]) != original.read_bytes() or stripped.read_bytes() != original.read_bytes():
            _check(checks, f"source:{key}", "STOP", "ghost-stripped source differs byte-for-byte from pinned source")
            source_texts[key] = None
        else:
            _check(checks, f"source:{key}", "OBSERVED", "pinned source and ghost-strip byte equality observed", sha256=pin)
            source_texts[key] = original_text

    events = source_receipt.get("correspondence")
    if not isinstance(events, dict):
        events = {}
    mir_cache: dict[tuple[str, str], tuple[str, dict[int, str]]] = {}
    rad_cache: dict[tuple[str, str, str, str], tuple[str, dict[int, str]]] = {}
    observed: dict[str, dict[str, Any]] = {}
    for label in REQUIRED_EVENTS:
        entry = events.get(label)
        if not isinstance(entry, dict):
            _check(checks, f"event:{label}", "INCONCLUSIVE", "missing reviewed correspondence entry")
            continue
        mpath = _inside(root, entry.get("mir_file"))
        rpath = _inside(root, entry.get("radium_file"))
        if mpath is None or rpath is None:
            _check(checks, f"event:{label}", "INCONCLUSIVE", "output path absent, absolute or escapes output root")
            continue
        mk = (str(mpath), str(entry.get("mir_sha256", "")))
        rk = (str(rpath), str(entry.get("radium_sha256", "")), str(entry.get("radium_definition", "")), str(entry.get("radium_callee_binding", "")))
        if mk not in mir_cache:
            mtext, merr = _read_file(mpath, entry.get("mir_sha256"))
            mir_cache[mk] = (merr, _mir_blocks(mtext) if mtext else {})
        if rk not in rad_cache:
            rtext, rerr = _read_file(rpath, entry.get("radium_sha256"))
            definition = _radium_definition(rtext, str(entry.get("radium_definition", ""))) if rtext else None
            binding = entry.get("radium_callee_binding")
            if definition is not None and (not isinstance(binding, str) or not re.search(r"\(\s*" + re.escape(binding) + r"\s*:\s*loc\s*\)", definition.split(": function :=", 1)[0])):
                rerr = "Radium callee binding is not a function location parameter"
            rad_cache[rk] = (rerr or ("Radium definition missing or malformed" if definition is None else ""), _radium_blocks(definition) if definition else {})
        merr, mblocks = mir_cache[mk]
        rerr, rblocks = rad_cache[rk]
        if merr or rerr:
            _check(checks, f"event:{label}", "INCONCLUSIVE", merr or rerr, mir_file=str(mpath), radium_file=str(rpath))
            continue
        mbb, rbb = entry.get("mir_bb"), entry.get("radium_bb")
        if not isinstance(mbb, int) or not isinstance(rbb, int) or mbb not in mblocks or rbb not in rblocks:
            _check(checks, f"event:{label}", "INCONCLUSIVE", "mapped MIR/Radium basic block absent")
            continue
        line = entry.get("source_line")
        if source_text is None or not isinstance(line, int) or line < 1 or line > len(source_text.splitlines()):
            _check(checks, f"event:{label}", "INCONCLUSIVE", "source line not bound to checked source bytes")
            continue
        source_line = source_text.splitlines()[line - 1]
        if entry.get("function") != "insert_tail" or not re.search(r"(?m)^fn\s+(?:[^\n]*::)?insert_tail(?:\b|<)", mpath.read_text(encoding="utf-8", errors="replace")):
            _check(checks, f"event:{label}", "INCONCLUSIVE", "selected MIR function is not actual insert_tail")
            continue
        expected_source = {
            "first_fnmut": "is_less(", "tail_read": "tail.read()",
            "gap_copy": "copy_nonoverlapping(", "late_fnmut": "is_less(",
            "normal_guard_drop": "let mut gap_guard = CopyOnDrop",
            "late_guard_drop": "let mut gap_guard = CopyOnDrop",
        }[label]
        if expected_source not in source_line:
            _check(checks, f"event:{label}", "NOT_OBSERVED", "selected source line does not contain required operation", line=line)
            continue
        callee, binding = entry.get("mir_callee"), entry.get("radium_callee_binding")
        _, call_error = _radium_calls(rblocks[rbb])
        if call_error:
            _check(checks, f"event:{label}", "INCONCLUSIVE", f"bb{rbb}: {call_error}", mir_bb=mbb, radium_bb=rbb)
            continue
        if label.endswith("guard_drop"):
            local = source_receipt.get("locals", {}).get("gap_guard") if isinstance(source_receipt.get("locals"), dict) else None
            mir_match = isinstance(local, str) and bool(re.search(r"(?m)^\s*drop\s*\(\s*" + re.escape(local) + r"\s*\)\s*->", mblocks[mbb]))
            if not mir_match or not isinstance(binding, str) or "DropGlue" not in binding or not _radium_call(rblocks[rbb], binding):
                _check(checks, f"event:{label}", "NOT_OBSERVED", "mapped MIR guard Drop/Radium DropGlue call absent at selected blocks", mir_bb=mbb, radium_bb=rbb)
                continue
        elif not _event_call(mblocks[mbb], callee) or not _radium_call(rblocks[rbb], binding):
            _check(checks, f"event:{label}", "NOT_OBSERVED", "mapped callee absent at selected MIR/Radium terminator", mir_bb=mbb, radium_bb=rbb)
            continue
        if label.endswith("fnmut") and "FnMut" not in callee:
            _check(checks, f"event:{label}", "INCONCLUSIVE", "MIR callee is not an FnMut call")
            continue
        if label == "gap_copy" and "copy_nonoverlapping" not in callee:
            _check(checks, f"event:{label}", "INCONCLUSIVE", "MIR callee is not copy_nonoverlapping")
            continue
        if label == "tail_read" and "read" not in callee:
            _check(checks, f"event:{label}", "INCONCLUSIVE", "MIR callee is not read")
            continue
        observed[label] = {"entry": entry, "mblocks": mblocks, "rblocks": rblocks, "mir_bb": mbb, "radium_bb": rbb}
        _check(checks, f"event:{label}", "OBSERVED", "exact source line and selected MIR/Radium calls match receipt", line=line, mir_bb=mbb, radium_bb=rbb, callee=callee, binding=binding)

    if all(label in observed for label in REQUIRED_EVENTS[:4]):
        first, read, copy, late = (observed[x] for x in REQUIRED_EVENTS[:4])
        same_mir = all(x["mblocks"] is first["mblocks"] for x in (read, copy, late))
        if same_mir and _reachable(first["mblocks"], first["mir_bb"], read["mir_bb"]) and _reachable(first["mblocks"], read["mir_bb"], copy["mir_bb"]) and _reachable(first["mblocks"], copy["mir_bb"], late["mir_bb"]):
            _check(checks, "normal_order", "OBSERVED", "first call -> read -> copy -> late call on MIR normal graph")
        else:
            _check(checks, "normal_order", "INCONCLUSIVE", "selected calls are not connected in required MIR normal order")
        normal_drop, late_drop = observed.get("normal_guard_drop"), observed.get("late_guard_drop")
        if normal_drop and late_drop:
            normal_path = normal_drop["mblocks"] is first["mblocks"] and _reachable(first["mblocks"], late["mir_bb"], normal_drop["mir_bb"])
            late_path = late_drop["mblocks"] is first["mblocks"] and any(_reachable(first["mblocks"], x, late_drop["mir_bb"], "any") for x in _successors(first["mblocks"][late["mir_bb"]], "unwind"))
            _check(checks, "guard_drop_mir_paths", "OBSERVED" if normal_path and late_path else "INCONCLUSIVE", "normal and late-unwind paths reach mapped MIR guard Drop" if normal_path and late_path else "mapped MIR guard Drop paths not established")
        else:
            _check(checks, "guard_drop_mir_paths", "INCONCLUSIVE", "normal/late guard Drop correspondence entries absent")
        same_radium = normal_drop is not None and late_drop is not None and all(x["rblocks"] == first["rblocks"] and x["entry"].get("radium_file") == first["entry"].get("radium_file") and x["entry"].get("radium_definition") == first["entry"].get("radium_definition") for x in (read, copy, late, normal_drop, late_drop))
        if same_radium and late_drop is not None:
            panic_free = any("UnwindFreeAnnot" in x["rblocks"][x["radium_bb"]] for x in (first, late))
            _check(checks, "fnmut_unwind_policy", "STOP" if panic_free else "UNKNOWN", "FnMut block contains forbidden UnwindFreeAnnot" if panic_free else "absence of a panic-free marker does not establish the unwind continuation")
            # Do not infer roles from a Goto occurring anywhere in a call. The
            # actual pinned writer is unavailable; in particular a supplied
            # radium_unwind_bb or the fixture's argument order is not authority.
            _check(checks, "radium_normal_paths", "UNKNOWN", "normal continuation roles require the exact pinned Radium writer")
            _check(checks, "radium_unwind_paths", "UNKNOWN", "early/late cleanup roles and all exits require the exact pinned Radium writer; map cannot qualify them")
        else:
            _check(checks, "fnmut_unwind_policy", "INCONCLUSIVE", "selected Radium FnMut blocks are not in one generated definition")
            _check(checks, "radium_unwind_paths", "INCONCLUSIVE", "selected Radium events are not in one generated definition")

        locals_receipt = source_receipt.get("locals")
        locals_receipt = locals_receipt if isinstance(locals_receipt, dict) else {}
        guard, tmp = locals_receipt.get("gap_guard"), locals_receipt.get("tmp")
        mtext_path = _inside(root, first["entry"].get("mir_file"))
        mtext = mtext_path.read_text() if mtext_path else ""
        valid_locals = all(isinstance(x, str) and re.fullmatch(r"_\d+", x) for x in (guard, tmp))
        if valid_locals and all(re.search(r"\bdebug\s+" + name + r"\s*=>\s*" + re.escape(local) + r"\s*;", mtext) for name, local in (("gap_guard", guard), ("tmp", tmp))):
            _check(checks, "local_identity", "OBSERVED", "MIR debug declarations bind guard and ManuallyDrop temporary", guard=guard, tmp=tmp)
            first_unwind = _successors(first["mblocks"][first["mir_bb"]], "unwind")
            late_unwind = _successors(late["mblocks"][late["mir_bb"]], "unwind")
            no_payload_drop = not any(re.search(r"\bdrop\s*\(\s*(?:\(\s*)?" + re.escape(tmp) + r"\b", b) for b in first["mblocks"].values())
            if no_payload_drop:
                _check(checks, "payload_drop", "OBSERVED", "no MIR Drop terminator targets the ManuallyDrop temporary")
            else:
                _check(checks, "payload_drop", "STOP", "MIR Drop terminator targets the ManuallyDrop temporary")
            first_outcomes = _cleanup_outcomes(first["mblocks"], next(iter(first_unwind)), guard) if len(first_unwind) == 1 else set()
            late_outcomes = _cleanup_outcomes(late["mblocks"], next(iter(late_unwind)), guard) if len(late_unwind) == 1 else set()
            early = first_outcomes == {False}
            late_ok = late_outcomes == {True}
            first_wrong = True in first_outcomes
            late_wrong = False in late_outcomes
            _check(checks, "first_unwind", "OBSERVED" if early else "STOP" if first_wrong else "INCONCLUSIVE", "first comparator unwind reaches resume without guard Drop" if early else "first comparator cleanup drops nonexistent guard" if first_wrong else "first comparator cleanup path unestablished")
            _check(checks, "late_unwind", "OBSERVED" if late_ok else "STOP" if late_wrong else "INCONCLUSIVE", "late comparator unwind reaches guard Drop then resume" if late_ok else "late comparator resumes without guard Drop" if late_wrong else "late comparator guard Drop/resume path unestablished")
            normal_guard = normal_drop is not None and bool(re.search(r"\bdrop\s*\(\s*" + re.escape(guard) + r"\s*\)\s*->\s*\[return:\s*bb", first["mblocks"][normal_drop["mir_bb"]]))
            _check(checks, "normal_guard_drop", "OBSERVED" if normal_guard else "INCONCLUSIVE", "MIR normal guard Drop terminator observed" if normal_guard else "normal guard Drop terminator unestablished")
        else:
            _check(checks, "local_identity", "INCONCLUSIVE", "guard/tmp MIR locals lack exact debug declarations")

    body_map = source_receipt.get("body_map")
    body_map = body_map if isinstance(body_map, dict) else {}
    body_definitions: dict[str, tuple[str, str]] = {}
    for label, (source_key, source_token, mir_token) in BODY_SOURCES.items():
        entry = body_map.get(label)
        if not isinstance(entry, dict):
            _check(checks, f"body:{label}", "NOT_RUN", "no reviewed selected-body MIR/Radium mapping receipt")
            continue
        original_text = source_texts.get(source_key)
        line = entry.get("source_line")
        if original_text is None or not isinstance(line, int) or line < 1 or line > len(original_text.splitlines()) or source_token not in original_text.splitlines()[line - 1]:
            _check(checks, f"body:{label}", "INCONCLUSIVE", "body source span does not match pinned source")
            continue
        mir_path = _inside(root, entry.get("mir_file"))
        radium_path = _inside(root, entry.get("radium_file"))
        if mir_path is None or radium_path is None:
            _check(checks, f"body:{label}", "INCONCLUSIVE", "selected-body path escapes output root")
            continue
        mtext, merr = _read_file(mir_path, entry.get("mir_sha256"))
        rtext, rerr = _read_file(radium_path, entry.get("radium_sha256"))
        if merr or rerr or mtext is None or rtext is None:
            _check(checks, f"body:{label}", "INCONCLUSIVE", merr or rerr)
            continue
        header = entry.get("mir_header")
        definition_name = entry.get("radium_definition")
        if not isinstance(header, str) or not header.startswith("fn ") or header not in mtext.splitlines() or mir_token not in header:
            _check(checks, f"body:{label}", "NOT_OBSERVED", "exact MIR function header absent or wrong selected body")
            continue
        definition = _radium_definition(rtext, str(definition_name))
        if definition is None or mir_token not in str(definition_name) or not _radium_blocks(definition):
            _check(checks, f"body:{label}", "NOT_OBSERVED", "selected Radium body definition absent, malformed or wrong identity")
            continue
        body_definitions[label] = (definition, str(definition_name))
        _check(checks, f"body:{label}", "OBSERVED", "pinned source span, exact MIR header and generated Radium function body observed", source_line=line, mir_header=header, radium_definition=definition_name)

    # Stock generated code lists each call as CallS <location parameter>.  A
    # complete closure must account for every such binding in every selected
    # body, including compiler glue.  A caller-provided category alone has no
    # force: it needs a hash-bound generated definition as the resolution.
    callee_inventory = source_receipt.get("callee_inventory")
    callee_inventory = callee_inventory if isinstance(callee_inventory, list) else []
    for label in BODY_SOURCES:
        if label not in body_definitions:
            _check(checks, f"callees:{label}", "NOT_RUN", "selected body unavailable; callee closure unobserved")
            continue
        definition, _ = body_definitions[label]
        calls, parse_error = _radium_inventory(definition)
        if parse_error:
            _check(checks, f"callees:{label}", "INCONCLUSIVE", parse_error)
            continue
        bindings = {call['binding'] for call in calls}
        supplied = [x for x in callee_inventory if isinstance(x, dict) and x.get("caller") == label]
        by_binding = {str(x.get("binding")): x for x in supplied}
        if len(by_binding) != len(supplied) or set(by_binding) != bindings:
            _check(checks, f"callees:{label}", "INCONCLUSIVE", "CallS binding closure differs from reviewed callee inventory", emitted=sorted(bindings), call_count=len(calls), inventoried=sorted(by_binding))
            continue
        unresolved: list[str] = []
        for binding, edge in by_binding.items():
            if not re.search(r'\(\s*' + re.escape(binding) + r'\s*:\s*loc\s*\)', definition.split(': function :=', 1)[0]):
                unresolved.append(binding)
                continue
            resolution = edge.get("resolution")
            target_path = _inside(root, edge.get("resolved_file"))
            if resolution not in {"translated_body", "compiler_glue", "rr_shim", "trait_contract", "intrinsic"} or target_path is None:
                unresolved.append(binding)
                continue
            target_text, error = _read_file(target_path, edge.get("resolved_sha256"))
            symbol = edge.get("resolved_definition")
            if error or target_text is None or not isinstance(symbol, str) or not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', symbol) or len(re.findall(r"(?m)^(?:Program )?Definition\s+" + re.escape(symbol) + r"\b", target_text)) != 1:
                unresolved.append(binding)
        # Existence of arbitrary definitions does not substantiate linkage to
        # a location parameter, DefId or type substitution. Until the exact
        # generator/linking contract is inspected there is no positive resolver.
        _check(checks, f"callees:{label}", "INCONCLUSIVE" if unresolved else "UNKNOWN" if bindings else "OBSERVED", "candidate definitions missing or ambiguous" if unresolved else "candidate definitions do not establish callee linkage; pinned linking contract UNKNOWN" if bindings else "no CallS in selected body", unresolved=unresolved, bindings=sorted(bindings), call_count=len(calls))

    # Resource forms are syntactic inventory, never a discharge of their proof
    # obligations.  The reviewed receipt must identify exact generated spec
    # definitions; a free-form assertion about ownership is not accepted.
    resources = source_receipt.get("resource_inventory")
    required_resource_keys = ("fnmut", "ptr_read", "ptr_copy", "guard_drop", "manually_drop", "maybe_dangling")
    resources = resources if isinstance(resources, dict) else {}
    for label in required_resource_keys:
        entry = resources.get(label)
        if not isinstance(entry, dict):
            _check(checks, f"resources:{label}", "NOT_RUN", "no hash-bound generated spec inventory")
            continue
        path = _inside(root, entry.get("file"))
        if path is None:
            _check(checks, f"resources:{label}", "INCONCLUSIVE", "spec path escapes output root")
            continue
        spec, error = _read_file(path, entry.get("sha256"))
        name = entry.get("definition")
        if error or spec is None or not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", name):
            _check(checks, f"resources:{label}", "INCONCLUSIVE", error or "invalid spec definition identity")
            continue
        matches = list(re.finditer(r"(?m)^(?:Program )?Definition\s+" + re.escape(name) + r"\b", spec))
        if len(matches) != 1:
            _check(checks, f"resources:{label}", "NOT_OBSERVED", "selected generated spec definition missing or ambiguous")
            continue
        next_definition = re.search(r"(?m)^(?:Program )?Definition\s+", spec[matches[0].end():])
        end = matches[0].end() + next_definition.start() if next_definition else len(spec)
        region = spec[matches[0].start():end]
        missing_forms = [token for token in RESOURCE_FORM_TOKENS[label] if token not in region]
        if missing_forms:
            _check(checks, f"resources:{label}", "NOT_OBSERVED", "selected spec lacks required syntactic resource/unwind forms", definition=name, missing=missing_forms)
            continue
        _check(checks, f"resources:{label}", "OBSERVED", "hash-bound generated resource/spec forms present; applicability and proof remain unproved", definition=name, forms=list(RESOURCE_FORM_TOKENS[label]))

    status_set = {x["status"] for x in checks}
    admission_complete = bool(checks and status_set == {"OBSERVED"})
    verdict = "STOP" if "STOP" in status_set else "PASS" if admission_complete else "INCONCLUSIVE"
    return {"verdict": verdict, "admission_complete": admission_complete, "scope": "saved frontend correspondence only", "checks": checks, "unproved": list(UNPROVED)}
