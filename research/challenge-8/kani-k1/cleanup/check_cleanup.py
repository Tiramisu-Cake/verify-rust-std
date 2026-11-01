#!/usr/bin/env python3
"""Check the cleanup against its frozen base, without compiling Rust.

The lexer hides comments and literals before balancing delimiters, but normalization
preserves literal bytes. This is a bounded source checker, not a Rust parser.
"""
import argparse
import difflib
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = "e2c5ac879b8f18bcc5684f79f24d5e5195c30e54"
S = "library/core/src/slice/sort/shared/smallsort"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args]).decode()


def lex(src):
    """Return (text, start, end, kind); reject unterminated lexical constructs."""
    out, i = [], 0
    while i < len(src):
        a = i
        if src[i].isspace():
            i += 1
            continue
        if src.startswith("//", i):
            i = src.find("\n", i)
            if i < 0:
                i = len(src)
            kind = "comment"
        elif src.startswith("/*", i):
            depth, i = 1, i + 2
            while depth and i < len(src):
                if src.startswith("/*", i):
                    depth, i = depth + 1, i + 2
                elif src.startswith("*/", i):
                    depth, i = depth - 1, i + 2
                else:
                    i += 1
            assert depth == 0, "unterminated block comment"
            kind = "comment"
        elif m := re.match(r'(?:br|cr|r)(#+)?"', src[i:]):
            close = '"' + (m[1] or "")
            end = src.find(close, i + m.end())
            assert end >= 0, "unterminated raw string"
            i, kind = end + len(close), "literal"
        elif (m := re.match(r'(?:b|c)?"', src[i:])):
            i += m.end()
            while i < len(src):
                if src[i] == "\\":
                    i += 2
                elif src[i] == '"':
                    i += 1
                    break
                else:
                    i += 1
            else:
                raise AssertionError("unterminated string")
            kind = "literal"
        elif m := re.match(r"b?'(?:\\(?:u\{[0-9a-fA-F_]+\}|x[0-9a-fA-F]{2}|.)|[^'\\\n])'", src[i:]):
            i, kind = i + m.end(), "literal"
        elif m := re.match(r"[A-Za-z_][A-Za-z_0-9]*", src[i:]):
            i, kind = i + m.end(), "code"
        else:
            i, kind = i + 1, "code"
        out.append((src[a:i], a, i, kind))
    return out


def balanced_end(tokens, start):
    pairs, stack = {"(": ")", "[": "]", "{": "}"}, []
    for j in range(start, len(tokens)):
        value = tokens[j][0]
        if tokens[j][3] == "literal":
            continue
        if value in pairs:
            stack.append(pairs[value])
        elif value in pairs.values():
            assert stack and stack.pop() == value, ("unbalanced", tokens[j])
            if not stack:
                return j + 1
    raise AssertionError("unclosed delimiter")


def retired_spans(src):
    tokens = [t for t in lex(src) if t[3] != "comment"]
    spans, i = [], 0
    while i < len(tokens):
        if [t[0] for t in tokens[i:i + 9]] != ["#", "[", "cfg", "(", "any", "(", ")", ")", "]"]:
            i += 1
            continue
        start, j = tokens[i][1], i + 9
        # Include any preceding attached outer attributes and doc comments.
        k = i
        while k and tokens[k - 1][0] == "]":
            matches = [n for n in range(k) if tokens[n][0] == "#" and n + 1 < k
                       and tokens[n + 1][0] == "[" and balanced_end(tokens, n + 1) == k]
            if not matches:
                break
            k = matches[-1]
            start = tokens[k][1]
        line_start = src.rfind("\n", 0, start) + 1
        assert not src[line_start:start].strip(), "attribute shares a code line"
        start = line_start
        while start:
            prev = src.rfind("\n", 0, start - 1) + 1
            if src[prev:start].lstrip().startswith(("///", "/**")):
                start = prev
            else:
                break
        while tokens[j][0] == "#":
            assert tokens[j + 1][0] == "["
            j = balanced_end(tokens, j + 1)
        first = tokens[j][0]
        while j < len(tokens):
            value = tokens[j][0]
            if value == ";":
                end, j = tokens[j][2], j + 1
                break
            if value in ("(", "[", "{"):
                after = balanced_end(tokens, j)
                if value == "{" and first not in ("use", "const", "static", "type"):
                    end, j = tokens[after - 1][2], after
                    if j < len(tokens) and tokens[j][0] == ";":
                        end, j = tokens[j][2], j + 1
                    break
                j = after
            else:
                j += 1
        else:
            raise AssertionError("retired item lacks terminator")
        line_end = src.find("\n", end)
        line_end = len(src) if line_end < 0 else line_end + 1
        assert not src[end:line_end].strip(), "item shares a trailing code line"
        spans.append((start, line_end))
        i = j
    return spans


def mask(src, spans):
    chars = list(src)
    for a, b in spans:
        for i in range(a, b):
            if chars[i] != "\n":
                chars[i] = " "
    return "".join(chars)


def normalize(src, path, retire):
    spans = retired_spans(src) if retire else []
    spans += [(a, b) for _, a, b, kind in lex(src) if kind == "comment"]
    if path == S + "/verify.rs":
        spans += [(m.start(), m.end()) for m in re.finditer(r"(?m)^mod correct;\n", src)]
    clean = mask(src, spans)
    return "\n".join(line.rstrip() for line in clean.splitlines() if line.strip()), clean


def line_ranges(numbers):
    ranges = []
    for n in numbers:
        if ranges and ranges[-1][1] + 1 == n:
            ranges[-1][1] = n
        else:
            ranges.append([n, n])
    return ranges


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=BASE)
    args = parser.parse_args()
    base = git("rev-parse", args.base).strip()
    files = git("ls-tree", "-r", "--name-only", base, "--", S + "/verify.rs", S + "/verify/").splitlines()
    current = sorted(str(p.relative_to(ROOT)) for p in (ROOT / S / "verify").rglob("*.rs"))
    current += [S + "/verify.rs"]
    report = {"base": base, "files": {}, "ok": True,
              "deletion_provenance": "All nonblank code lines outside retired items must survive "
              "in order with identical bytes after comment masking; all other nonblank base "
              "lines belong to retired items, comments or the correct module registration."}
    for path in sorted(set(files) | set(current)):
        old = git("show", f"{base}:{path}") if path in files else ""
        new = (ROOT / path).read_text() if (ROOT / path).exists() else ""
        before, allowed = normalize(old, path, True)
        after, _ = normalize(new, path, False)
        lost = 0
        old_lines, new_lines = old.splitlines(), new.splitlines()
        for op, a, b, _, _ in difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False).get_opcodes():
            if op in ("delete", "replace"):
                lost += b - a
        # Match surviving code lines in order. A textual diff may align a retired `}`
        # with an identical live `}`, incorrectly attributing the deletion to live code.
        # The normalized line bijection provides unambiguous survivor provenance instead.
        live_lines = [i + 1 for i, line in enumerate(allowed.splitlines()) if line.strip()]
        provenance_ok = before.splitlines() == after.splitlines()
        bad_words = re.findall(r"cfg\(any\(\)\)|DEACTIVATED|P1-CLEAN|poneclean|Known limitations", new)
        item = {"retired_items": len(retired_spans(old)), "deleted_lines": lost,
                "normalized_equal": before == after,
                "all_live_lines_preserved_in_order": provenance_ok,
                "live_base_line_ranges": line_ranges(live_lines),
                "eligible_deletion_nonempty_lines": sum(bool(line.strip()) for line in old_lines) - len(live_lines),
                "forbidden_markers": bad_words,
                "candidate_sha256": hashlib.sha256(new.encode()).hexdigest() if new else None,
                "normalized_sha256": hashlib.sha256(before.encode()).hexdigest()}
        report["files"][path] = item
        report["ok"] &= before == after and provenance_ok and not bad_words
    delta = git("diff", "--name-only", base, "--", "library").splitlines()
    report["library_delta_in_verify_only"] = all(p in files for p in delta)
    report["ok"] &= report["library_delta_in_verify_only"]
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
