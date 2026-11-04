#!/usr/bin/env python3
"""TRIMPART static checks: Part 1 v6 (d6b8caf7fe) against the trimmed v7 tree.

Source-level only: a small Rust lexer, item splitter and `macro_rules!` expander for the
declarative macro shapes used by the SmallSort verify modules. It does not run rustc, cargo,
Kani or CBMC, does not resolve names like the compiler and is not a compiler inventory.

Usage (repository root): python3 -I research/challenge-8/kani-k1/trimpart/check_trimpart.py
    [--head REV] [--rustfmt WRAPPER --rustfmt-config TOML]
Without --head the working tree is checked. Writes check-report.json next to this script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V6 = "d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097"
V6_BASE = "c0bd09c354a50bf9fe4dcc7cc5f9c34503658479"
BASE = "233f96f66ab3785881cead133817ed5db4c76b09"
SMALLSORT = "library/core/src/slice/sort/shared/smallsort.rs"
CARGO = "library/core/Cargo.toml"
VERIFY_ROOT = "library/core/src/slice/sort/shared/smallsort/verify.rs"
VERIFY_DIR = "library/core/src/slice/sort/shared/smallsort/verify/"
PREFIX = "slice::sort::shared::smallsort::verify::"
CFG = "kani_smallsort_controls"
CONTROLS = [
    "assembly::reject_mutant_swap_u8_n2",
    "merge::specfix::specfix_full_value_checker_rejects_payload_change_u8",
    "wrap::rejects_payload_corruption",
    "wrap::rejects_always_true",
    "merge::specfix::specfix_wrong_f_swap_rejected_u8",
    "merge::specfix::specfix_wrong_f_sort4_rejected_u64",
    "merge::specfix::specfix_wrong_f_insert_rejected_u8",
    "merge::specfix::specfix_wrong_f_merge_rejected_u8",
]
# Items whose v7 replacement is intentional; every other v6/v7 item difference fails check 1/3.
EXPECTED_REPLACED_MACROS = {
    "library/core/src/slice/sort/shared/smallsort/verify/assembly.rs": (
        {"paired_case"}, {"original_case"}),
    "library/core/src/slice/sort/shared/smallsort/verify/network.rs": (
        {"insertion_offset_group_cases"},
        {"insertion_offset_group_u64_case", "insertion_offset_group_cell_case"}),
}
# v7 removes the second `trait_cases` arm: after the opt-in n7_to9 roots moved to Part 2 it has
# no caller. The kept first arm must equal v6's first arm token-for-token.
EXPECTED_CHANGED = {
    "library/core/src/slice/sort/shared/smallsort/verify/types.rs:macro_rules:trait_cases",
}
# Conservatively reached by name from the ordinary roots in v6, removed in v7 because only the
# opt-in ZST dispatch roots instantiated it; check 3 also requires that no kept network root
# instantiates a generic helper with the unit type.
EXPECTED_REMOVED_REACHED = {
    "removed:library/core/src/slice/sort/shared/smallsort/verify/network.rs:impl:"
    "impl ArbitraryValue for (  )",
}
KEYWORDS = set("""as async await break const continue crate dyn else enum extern false fn for if impl in
let loop match mod move mut pub ref return self Self static struct super trait true type unsafe use
where while macro_rules union u8 u16 u32 u64 u128 usize i8 i16 i32 i64 i128 isize bool char str f32
f64""".split())


# ----------------------------------------------------------------------------- lexer
class Tok:
    __slots__ = ("kind", "text", "line", "children", "end_line")

    def __init__(self, kind, text, line, children=None, end_line=None):
        self.kind, self.text, self.line = kind, text, line
        self.children, self.end_line = children, end_line if end_line is not None else line

    def __repr__(self):
        return f"Tok({self.kind},{self.text!r})"


CLOSE = {"(": ")", "[": "]", "{": "}"}


def lex(src: str):
    toks, i, n, line = [], 0, len(src), 1
    ident = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    while i < n:
        c = src[i]
        if c == "\n":
            line += 1
            i += 1
            continue
        if c.isspace():
            i += 1
            continue
        if src.startswith("//", i):
            end = src.find("\n", i)
            end = n if end < 0 else end
            text = src[i:end]
            doc = (text.startswith("///") and not text.startswith("////")) or text.startswith("//!")
            if doc:
                toks.append(Tok("doc", text.rstrip(), line))
            i = end
            continue
        if src.startswith("/*", i):
            depth, j = 1, i + 2
            while j < n and depth:
                if src.startswith("/*", j):
                    depth, j = depth + 1, j + 2
                elif src.startswith("*/", j):
                    depth, j = depth - 1, j + 2
                else:
                    j += 1
            line += src.count("\n", i, j)
            i = j
            continue
        raw = re.match(r"(?:b|c)?r(#*)\"", src[i:])
        if raw:
            close = '"' + raw.group(1)
            end = src.find(close, i + raw.end())
            end = n if end < 0 else end + len(close)
            toks.append(Tok("lit", src[i:end], line))
            line += src.count("\n", i, end)
            i = end
            continue
        q = i + 1 if src.startswith(('b"', 'c"', "b'"), i) else i
        if src[q] == '"':
            j = q + 1
            while j < n and src[j] != '"':
                j += 2 if src[j] == "\\" else 1
            toks.append(Tok("lit", src[i:j + 1], line))
            line += src.count("\n", i, j + 1)
            i = j + 1
            continue
        if src[q] == "'":
            m = re.match(r"'(?:\\(?:x[0-9a-fA-F]{2}|u\{[0-9a-fA-F]+\}|.)|[^\\'])'", src[q:])
            if m:
                toks.append(Tok("lit", src[i:q + m.end()], line))
                i = q + m.end()
                continue
            m = ident.match(src, i + 1)
            toks.append(Tok("lifetime", "'" + m.group(0), line))
            i = m.end()
            continue
        if c.isdigit():
            m = re.match(r"[0-9][0-9a-zA-Z_]*(?:\.[0-9][0-9a-zA-Z_]*)?", src[i:])
            toks.append(Tok("lit", m.group(0), line))
            i += m.end()
            continue
        m = ident.match(src, i)
        if m:
            toks.append(Tok("ident", m.group(0), line))
            i = m.end()
            continue
        toks.append(Tok("punct", c, line))
        i += 1
    return toks


def tree(toks):
    stack, out = [], []
    cur = out
    for t in toks:
        if t.kind == "punct" and t.text in CLOSE:
            g = Tok("group", t.text, t.line, [])
            cur.append(g)
            stack.append((cur, g))
            cur = g.children
        elif t.kind == "punct" and t.text in ")]}":
            parent, g = stack.pop()
            if CLOSE[g.text] != t.text:
                raise ValueError(f"mismatched {g.text}{t.text} at line {t.line}")
            g.end_line = t.line
            cur = parent
        else:
            cur.append(t)
    if stack:
        raise ValueError("unclosed delimiter")
    return out


def ser(tts, docs=False) -> str:
    out = []
    for t in tts:
        if t.kind == "group":
            out.append(t.text + " " + ser(t.children, docs) + " " + CLOSE[t.text])
        elif t.kind == "doc":
            if docs:
                out.append(t.text)
        else:
            out.append(t.text)
    return " ".join(x for x in out if x)


def idents(tts, acc=None):
    acc = set() if acc is None else acc
    for t in tts:
        if t.kind == "group":
            idents(t.children, acc)
        elif t.kind == "ident":
            acc.add(t.text)
    return acc


def is_p(t, s):
    return t is not None and t.kind == "punct" and t.text == s


def is_i(t, s=None):
    return t is not None and t.kind == "ident" and (s is None or t.text == s)


def is_g(t, d):
    return t is not None and t.kind == "group" and t.text == d


def last_line(t):
    return t.end_line if t.kind == "group" else t.line


# ----------------------------------------------------------------------------- items
class Item:
    def __init__(self, kind, name, attrs, body, first_line, last, outer=()):
        self.kind, self.name, self.attrs, self.body = kind, name, attrs, body
        self.first_line, self.last_line = first_line, last
        self.outer = list(outer)  # attributes inherited from a macro invocation
        self.file = None
        self.macro_origin = None

    @property
    def all_attrs(self):
        return self.outer + self.attrs

    def tokens(self):
        return self.all_attrs + self.body

    def text(self, docs=False):
        return ser(self.tokens(), docs)

    def key(self):
        return (self.kind, self.name)


def split_items(tts):
    items, i, n = [], 0, len(tts)
    while i < n:
        start = i
        if tts[i].kind == "doc" and tts[i].text.startswith("//!"):
            j = i
            while j < n and tts[j].kind == "doc" and tts[j].text.startswith("//!"):
                j += 1
            items.append(Item("inner_doc", "module_doc", [], tts[i:j], tts[i].line,
                              tts[j - 1].line))
            i = j
            continue
        if is_p(tts[i], "#") and i + 1 < n and is_p(tts[i + 1], "!"):
            items.append(Item("inner_attr", ser(tts[i:i + 3]), [], tts[i:i + 3], tts[i].line,
                              last_line(tts[i + 2])))
            i += 3
            continue
        attrs = []
        while i < n and (tts[i].kind == "doc" or (is_p(tts[i], "#") and is_g(tts[i + 1], "["))):
            if tts[i].kind == "doc":
                attrs.append(tts[i])
                i += 1
            else:
                attrs.extend(tts[i:i + 2])
                i += 2
        if i >= n:
            raise ValueError("dangling attributes")
        j = i
        if is_i(tts[j], "pub"):
            j += 1
            if is_g(tts[j], "("):
                j += 1
        kw = tts[j].text if tts[j].kind == "ident" else None
        if kw == "unsafe" and is_i(tts[j + 1]):
            kw = tts[j + 1].text
            j += 1
        if kw == "macro_rules" and is_p(tts[j + 1], "!"):
            end = j + 4
            if end < n and is_p(tts[end], ";"):
                end += 1
            items.append(Item("macro_rules", tts[j + 2].text, attrs, tts[i:end], tts[start].line,
                              last_line(tts[end - 1])))
            i = end
            continue
        if kw and is_p(tts[j + 1], "!") and tts[j + 2].kind == "group":
            end = j + 3
            if end < n and is_p(tts[end], ";"):
                end += 1
            items.append(Item("macro_call", kw, attrs, tts[i:end], tts[start].line,
                              last_line(tts[end - 1])))
            i = end
            continue
        k = j
        semicolon_only = kw in ("use", "static", "const", "type", "mod")
        if kw == "mod" and is_g(tts[j + 2], "{"):
            semicolon_only = False
        while k < n:
            t = tts[k]
            if is_p(t, ";"):
                break
            if is_g(t, "{") and not semicolon_only:
                break
            k += 1
        end = k + 1
        body = tts[i:end]
        if kw == "impl":
            head = ser([t for t in body[1:-1] if not is_g(t, "{")])
            name = "impl " + head
        elif kw == "use":
            name = ser(body)
        elif kw in ("fn", "struct", "trait", "static", "type", "mod", "const", "enum"):
            p = j + 1
            if is_i(tts[p], "mut"):
                p += 1
            name = tts[p].text
        else:
            raise ValueError(f"unknown item at line {tts[i].line}: {ser(body)[:80]}")
        items.append(Item(kw, name, attrs, body, tts[start].line, last_line(tts[end - 1])))
        i = end
    return items


def cfg_values(attr_tokens):
    vals = []
    for a, b in zip(attr_tokens, attr_tokens[1:]):
        if is_p(a, "#") and is_g(b, "[") and b.children and is_i(b.children[0], "cfg"):
            vals.append(ser(b.children[1:]))
        if is_p(a, "#") and is_g(b, "[") and b.children and is_i(b.children[0], "cfg_attr"):
            raise ValueError("cfg_attr is not supported")
    return vals


def gated(attr_tokens) -> bool:
    vals = cfg_values(attr_tokens)
    unknown = [v for v in vals if v != f"( {CFG} )"]
    if unknown:
        raise ValueError(f"unknown cfg: {unknown}")
    return bool(vals)


def proof_kind(attr_tokens):
    for a, b in zip(attr_tokens, attr_tokens[1:]):
        if is_p(a, "#") and is_g(b, "["):
            c = b.children
            if len(c) >= 4 and is_i(c[0], "kani") and is_p(c[1], ":") and is_p(c[2], ":"):
                if is_i(c[3], "proof") or is_i(c[3], "proof_for_contract"):
                    return c[3].text
    return None


# ----------------------------------------------------------------------------- macros
class MacroError(Exception):
    pass


def parse_pattern(tts):
    out, i = [], 0
    while i < len(tts):
        t = tts[i]
        if is_p(t, "$") and i + 1 < len(tts):
            nxt = tts[i + 1]
            if nxt.kind == "ident" and i + 3 < len(tts) + 1 and is_p(tts[i + 2] if i + 2 < len(tts)
                                                                     else None, ":"):
                out.append(("var", nxt.text, tts[i + 3].text))
                i += 4
                continue
            if is_g(nxt, "("):
                sub = parse_pattern(nxt.children)
                j = i + 2
                sep = None
                if not (j < len(tts) and tts[j].kind == "punct" and tts[j].text in "*+?"):
                    sep = tts[j]
                    j += 1
                op = tts[j].text
                out.append(("rep", sub, sep, op))
                i = j + 1
                continue
        if t.kind == "group":
            out.append(("group", t.text, parse_pattern(t.children)))
        elif t.kind != "doc":
            out.append(("tok", t))
        i += 1
    return out


def same_tok(a, b):
    return a.kind == b.kind and a.text == b.text and a.kind != "group"


def take_fragment(frag, tts, i):
    n = len(tts)
    if i >= n:
        return None
    if frag == "ident":
        return i + 1 if tts[i].kind == "ident" else None
    if frag == "literal":
        if is_p(tts[i], "-") and i + 1 < n and tts[i + 1].kind == "lit":
            return i + 2
        if tts[i].kind == "lit" or is_i(tts[i], "true") or is_i(tts[i], "false"):
            return i + 1
        return None
    if frag == "tt":
        return i + 1
    if frag == "block":
        return i + 1 if is_g(tts[i], "{") else None
    if frag in ("expr", "ty", "meta", "path", "pat"):
        j, angle = i, 0
        if frag == "expr" and is_p(tts[j], "|"):
            j += 1
            while j < n and not is_p(tts[j], "|"):
                j += 1
            j += 1
        while j < n:
            t = tts[j]
            if angle == 0 and (is_p(t, ",") or is_p(t, ";") or
                               (is_p(t, "=") and j + 1 < n and is_p(tts[j + 1], ">"))):
                break
            if frag in ("ty", "path"):
                if is_p(t, "<"):
                    angle += 1
                elif is_p(t, ">") and angle:
                    angle -= 1
            j += 1
        return j if j > i else None
    raise MacroError(f"unsupported fragment {frag}")


def match(pat, tts, i, binds):
    """Match pattern list `pat` starting at tts[i]; return end index or None."""
    for k, el in enumerate(pat):
        kind = el[0]
        if kind == "tok":
            while i < len(tts) and tts[i].kind == "doc":
                i += 1
            if i >= len(tts) or not same_tok(el[1], tts[i]):
                return None
            i += 1
        elif kind == "group":
            if i >= len(tts) or not is_g(tts[i], el[1]):
                return None
            sub = {}
            end = match(el[2], tts[i].children, 0, sub)
            if end is None or end != len(tts[i].children):
                return None
            binds.update(sub)
            i += 1
        elif kind == "var":
            end = take_fragment(el[2], tts, i)
            if end is None:
                return None
            binds[el[1]] = ("one", tts[i:end])
            i = end
        elif kind == "rep":
            _, sub, sep, op = el
            seqs = []
            while True:
                j = i
                if seqs and sep is not None:
                    if j < len(tts) and same_tok(sep, tts[j]):
                        j += 1
                    else:
                        break
                b = {}
                end = match(sub, tts, j, b)
                if end is None or end == j:
                    break
                seqs.append(b)
                i = end
                if op == "?":
                    break
            if op == "+" and not seqs:
                return None
            names = rep_names(sub)
            for name in names:
                binds[name] = ("seq", [s.get(name) for s in seqs])
    return i


def rep_names(pat):
    out = set()
    for el in pat:
        if el[0] == "var":
            out.add(el[1])
        elif el[0] == "rep":
            out |= rep_names(el[1])
        elif el[0] == "group":
            out |= rep_names(el[2])
    return out


def clone(t):
    if t.kind == "group":
        return Tok("group", t.text, t.line, [clone(c) for c in t.children], t.end_line)
    return Tok(t.kind, t.text, t.line)


def transcribe(tts, binds):
    out, i = [], 0
    while i < len(tts):
        t = tts[i]
        if is_p(t, "$") and i + 1 < len(tts):
            nxt = tts[i + 1]
            if is_i(nxt, "crate"):
                out.append(Tok("ident", "$crate", nxt.line))
                i += 2
                continue
            if nxt.kind == "ident":
                if nxt.text not in binds or binds[nxt.text][0] != "one":
                    raise MacroError(f"unbound ${nxt.text}")
                out.extend(clone(x) for x in binds[nxt.text][1])
                i += 2
                continue
            if is_g(nxt, "("):
                j = i + 2
                sep = None
                if not (tts[j].kind == "punct" and tts[j].text in "*+?"):
                    sep = tts[j]
                    j += 1
                used = [v for v in used_vars(nxt.children) if v in binds and binds[v][0] == "seq"]
                if not used:
                    raise MacroError("repetition without repeated variable")
                counts = {len(binds[v][1]) for v in used}
                if len(counts) != 1:
                    raise MacroError("inconsistent repetition counts")
                for r in range(counts.pop()):
                    if r and sep is not None:
                        out.append(clone(sep))
                    b = dict(binds)
                    for v in used:
                        b[v] = binds[v][1][r]
                    out.extend(transcribe(nxt.children, b))
                i = j + 1
                continue
        if t.kind == "group":
            out.append(Tok("group", t.text, t.line, transcribe(t.children, binds), t.end_line))
        else:
            out.append(clone(t))
        i += 1
    return out


def used_vars(tts):
    out = []
    for a, b in zip(tts, tts[1:]):
        if is_p(a, "$") and b.kind == "ident":
            out.append(b.text)
    for t in tts:
        if t.kind == "group":
            out.extend(used_vars(t.children))
    return out


def desugar_docs(tts):
    """Doc comments in macro input become `#[doc = "..."]` attributes, as in rustc."""
    out = []
    for t in tts:
        if t.kind == "doc":
            out.append(Tok("punct", "#", t.line))
            out.append(Tok("group", "[", t.line, [Tok("ident", "doc", t.line),
                                                   Tok("punct", "=", t.line),
                                                   Tok("lit", json.dumps(t.text), t.line)]))
        elif t.kind == "group":
            out.append(Tok("group", t.text, t.line, desugar_docs(t.children), t.end_line))
        else:
            out.append(t)
    return out


class Macro:
    def __init__(self, item):
        self.name = item.name
        self.item = item
        g = item.body[3] if is_i(item.body[0], "macro_rules") else None
        if g is None:
            # pub(crate) or attributes are not used on macro_rules items here.
            raise MacroError("unexpected macro_rules shape")
        self.arms = []
        c, i = g.children, 0
        while i < len(c):
            matcher, arrow1, arrow2, trans = c[i], c[i + 1], c[i + 2], c[i + 3]
            assert matcher.kind == "group" and is_p(arrow1, "=") and is_p(arrow2, ">")
            self.arms.append((parse_pattern(matcher.children), trans.children))
            i += 4
            if i < len(c) and is_p(c[i], ";"):
                i += 1
        self.used_arms = set()

    def expand(self, args):
        args = desugar_docs(args)
        for index, (pat, trans) in enumerate(self.arms):
            binds = {}
            end = match(pat, args, 0, binds)
            if end is not None and end == len(args):
                self.used_arms.add(index)
                return transcribe(trans, binds)
        raise MacroError(f"no arm of {self.name} matches {ser(args)[:120]}")


# ----------------------------------------------------------------------------- source tree
class Source:
    """One revision (git rev or None = working tree) of the verify module tree."""

    def __init__(self, rev):
        self.rev = rev
        self.files = {}
        self.file_gate = {}
        self.items = {}       # file -> list of top-level items (macro calls unexpanded)
        self.expanded = {}    # file -> list of items after item-level macro expansion
        self.macros = {}      # name -> Macro (first definition wins per file, then global)
        self.file_macros = {}
        self.walk(VERIFY_ROOT, False)
        for f in self.files:
            self.file_macros[f] = {}
            for it in self.items[f]:
                if it.kind == "macro_rules":
                    m = Macro(it)
                    self.file_macros[f][m.name] = m
                    self.macros.setdefault(m.name, m)
        for f in self.files:
            self.expanded[f] = self.expand_list(f, self.items[f], [])

    def read(self, path):
        if self.rev is None:
            p = REPO / path
            return p.read_text() if p.is_file() else None
        r = subprocess.run(["git", "-C", str(REPO), "show", f"{self.rev}:{path}"],
                           capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else None

    def walk(self, path, gate):
        text = self.read(path)
        if text is None:
            raise ValueError(f"missing module source {path}")
        self.files[path] = text
        self.file_gate[path] = gate
        items = split_items(tree(lex(text)))
        for it in items:
            it.file = path
        self.items[path] = items
        base = path[:-3] + "/"
        for it in items:
            if it.kind == "mod" and is_p(it.body[-1], ";"):
                self.walk(base + it.name + ".rs", gate or gated(it.attrs))

    def module_path(self, f):
        rel = f[len(VERIFY_DIR):-3] if f.startswith(VERIFY_DIR) else ""
        return rel.replace("/", "::")

    def lookup_macro(self, f, name):
        return self.file_macros[f].get(name) or self.macros.get(name)

    def expand_list(self, f, items, outer, depth=0):
        out = []
        for it in items:
            if it.kind == "macro_call":
                m = self.lookup_macro(f, it.name)
                if m is None:
                    out.append(it)  # e.g. a std macro at item level (none expected)
                    continue
                if depth > 8:
                    raise MacroError("expansion too deep")
                produced = split_items(m.expand(it.body[2].children))
                for p in produced:
                    p.file = f
                    p.first_line, p.last_line = it.first_line, it.last_line
                    p.macro_origin = it.name
                inherit = outer + it.attrs
                for p in self.expand_list(f, produced, inherit, depth + 1):
                    if p.macro_origin is None:
                        p.macro_origin = it.name
                    out.append(p)
                continue
            if outer:
                it.outer = list(outer) + it.outer
            out.append(it)
        return out

    def all_items(self):
        for f in self.files:
            for it in self.expanded[f]:
                yield f, it

    def active(self, f, it, controls):
        g = self.file_gate[f] or gated(it.all_attrs)
        return controls or not g

    def roots(self, controls):
        res = {}
        for f, it in self.all_items():
            if it.kind == "fn" and proof_kind(it.all_attrs) and self.active(f, it, controls):
                mp = self.module_path(f)
                name = (mp + "::" if mp else "") + it.name
                if name in res:
                    raise ValueError(f"duplicate root {name}")
                res[name] = (f, it)
        return res


# ----------------------------------------------------------------------------- dependency closure
def def_index(src: Source, controls):
    idx = {}
    for f, it in src.all_items():
        if not src.active(f, it, controls) or it.kind in ("use", "inner_attr", "inner_doc", "mod"):
            continue
        if it.kind == "fn" and proof_kind(it.all_attrs):
            continue
        for name in item_def_names(it):
            idx.setdefault(name, []).append((f, it))
    return idx


def item_def_names(it):
    if it.kind != "impl":
        return {it.name}
    names = set()
    head = [t for t in it.body if not is_g(t, "{")]
    trait_name = None
    hs = ser(head)
    m = re.match(r"impl (?:< [^>]* > )?(.+?) for (.+)$", hs)
    toks = re.findall(r"[A-Za-z_]\w*", hs)
    if m:
        trait_name = re.findall(r"[A-Za-z_]\w*", m.group(1))[0]
        self_names = [x for x in re.findall(r"[A-Za-z_]\w*", m.group(2)) if x not in KEYWORDS]
        # A trait impl is reachable through its trait together with its self type; a self type
        # without a nominal identifier (here `()`, arrays of u8) is reachable through the trait.
        names.add(("trait-impl", trait_name, tuple(self_names)))
    else:
        names |= {x for x in toks if x not in KEYWORDS and x != "impl"}
    body = it.body[-1]
    for a, b in zip(body.children, body.children[1:]):
        if is_i(a, "fn") and is_i(b):
            names.add(b.text)
    return names


def closure(src: Source, start_items, controls):
    idx = def_index(src, controls)
    trait_impls = [(k, v) for k, v in idx.items() if isinstance(k, tuple)]
    seen, names, work = {}, set(), list(start_items)
    while work:
        f, it = work.pop()
        key = (f, it.kind, it.name)
        if key in seen:
            continue
        seen[key] = it
        new = idents(it.tokens()) - names
        names |= new
        for name in new:
            for dep in idx.get(name, []):
                work.append(dep)
        for (tag, trait_name, self_names), deps in trait_impls:
            if trait_name in names and (not self_names or all(s in names for s in self_names)):
                for dep in deps:
                    if (dep[0], dep[1].kind, dep[1].name) not in seen:
                        work.append(dep)
    return seen


# ----------------------------------------------------------------------------- checks
def item_map(src: Source):
    res = {}
    for f, it in src.all_items():
        if it.kind == "fn" and proof_kind(it.all_attrs):
            continue
        res.setdefault((f, it.kind, it.name), []).append(it)
    return res


def check_names(v6, v7):
    o6, o7 = set(v6.roots(False)), set(v7.roots(False))
    c6, c7 = set(v6.roots(True)), set(v7.roots(True))
    controls_v6_missing = sorted(set(CONTROLS) - c6)
    controls_v6_ordinary = sorted(set(CONTROLS) & o6)
    res = dict(
        v6_ordinary=len(o6), v6_cfg_on=len(c6), v7_ordinary=len(o7), v7_cfg_on=len(c7),
        ordinary_equal=o6 == o7, ordinary_missing=sorted(o6 - o7), ordinary_unexpected=sorted(o7 - o6),
        cfg_on_minus_ordinary=sorted(c7 - o7),
        controls_found_in_v6=not controls_v6_missing and not controls_v6_ordinary,
        controls_v6_missing=controls_v6_missing,
        removed_opt_in_roots=len(c6 - o6 - set(CONTROLS)),
    )
    res["pass_check1_names"] = res["ordinary_equal"] and len(o7) == 202
    res["pass_check2"] = (set(CONTROLS) == c7 - o7 and len(c7) == 210 and o7 <= c7
                          and res["controls_found_in_v6"])
    return res, sorted(o7), sorted(c7 - o7), sorted(c6 - o6 - set(CONTROLS))


def check_bodies(v6, v7):
    r6, r7 = v6.roots(True), v7.roots(True)
    o7 = v7.roots(False)
    compared, strict_diff, token_diff = 0, [], []
    for name in sorted(set(o7) | set(CONTROLS)):
        if name not in r7 or name not in r6:
            token_diff.append(name)
            continue
        a, b = r6[name][1], r7[name][1]
        compared += 1
        if a.text() != b.text():
            token_diff.append(name)
        elif a.text(True) != b.text(True):
            strict_diff.append(name)
    # Transitive dependencies of the ordinary roots (cfg-off) and of the 8 controls (cfg-on).
    deps_diff, deps_missing, deps_docs = [], [], []
    m6, m7 = item_map(v6), item_map(v7)
    total = 0
    for controls, roots in ((False, [o7[n] for n in o7]), (True, [r7[n] for n in CONTROLS])):
        seen = closure(v7, roots, controls)
        seen6 = closure(v6, [r6[n] for n in (o7 if not controls else CONTROLS)], controls)
        for key, it in seen.items():
            if it.kind == "fn" and proof_kind(it.all_attrs):
                continue
            total += 1
            olds = m6.get(key)
            if not olds:
                deps_missing.append(":".join(key))
                continue
            texts6 = sorted(o.text() for o in olds)
            texts7 = sorted(o.text() for o in m7[key])
            if texts6 != texts7:
                deps_diff.append(":".join(key))
            elif sorted(o.text(True) for o in olds) != sorted(o.text(True) for o in m7[key]):
                deps_docs.append(":".join(key))
        # Everything v6 reached from the same roots must still exist in v7.
        for key in seen6:
            it = seen6[key]
            if it.kind == "fn" and proof_kind(it.all_attrs):
                continue
            if key not in m7:
                deps_missing.append("removed:" + ":".join(key))
    deps_missing = sorted(set(deps_missing))
    explained = sorted(set(deps_missing) & EXPECTED_REMOVED_REACHED)
    deps_missing = sorted(set(deps_missing) - EXPECTED_REMOVED_REACHED)
    return dict(
        dependency_removed_explained=explained,
        roots_compared=compared, root_token_differences=token_diff,
        root_doc_only_differences=strict_diff,
        dependency_items_checked=total, dependency_token_differences=sorted(set(deps_diff)),
        dependency_doc_only_differences=sorted(set(deps_docs)),
        dependency_missing_or_removed=deps_missing,
        pass_check1_bodies=not token_diff and not deps_diff and not deps_missing,
    )


def use_leaves(it):
    """Imported names of a `use` item (last path segment or alias of each leaf)."""
    out = []

    def walk(tts):
        last, i = None, 0
        while i < len(tts):
            t = tts[i]
            if t.kind == "group" and t.text == "{":
                for part in split_commas(t.children):
                    walk(part)
                last = None
            elif is_i(t, "as"):
                last = tts[i + 1].text
                i += 1
            elif t.kind == "ident" and t.text not in ("use", "pub", "crate", "super", "self"):
                last = t.text
            i += 1
        if last:
            out.append(last)

    body = [t for t in it.body if not (is_g(t, "(") or is_p(t, ";"))]
    walk(body)
    return out


def split_commas(tts):
    parts, cur = [], []
    for t in tts:
        if is_p(t, ","):
            parts.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        parts.append(cur)
    return parts


def orphans(src: Source, controls):
    roots = src.roots(controls)
    seen = closure(src, list(roots.values()), controls)
    orphan_items, orphan_imports = [], []
    invoked = set()
    for f in src.files:
        for it in src.items[f]:
            if it.kind == "macro_call" and src.active(f, it, controls):
                invoked.add(it.name)
    for f, it in src.all_items():
        if not src.active(f, it, controls):
            continue
        if it.kind in ("use", "inner_attr", "inner_doc", "mod") or (it.kind == "fn" and proof_kind(it.all_attrs)):
            continue
        if it.kind == "macro_rules":
            used = it.name in invoked or any(
                it.name in idents(x.tokens()) for x in seen.values())
            if not used:
                orphan_items.append(f"{f}:{it.kind}:{it.name}")
            continue
        if (f, it.kind, it.name) not in seen:
            orphan_items.append(f"{f}:{it.kind}:{it.name}")
    for f in src.files:
        used_names = set()
        for it in src.items[f]:
            if it.kind != "use" and src.active(f, it, controls):
                used_names |= idents(it.tokens())
        for it in src.expanded[f]:
            if it.kind != "use" and src.active(f, it, controls):
                used_names |= idents(it.tokens())
        for it in src.items[f]:
            if it.kind == "use" and src.active(f, it, controls):
                for leaf in use_leaves(it):
                    if leaf not in used_names and not (is_i(it.body[0], "pub")):
                        orphan_imports.append(f"{f}:{leaf}")
    arms = []
    for f in src.files:
        for name, m in src.file_macros[f].items():
            unused = sorted(set(range(len(m.arms))) - m.used_arms)
            if unused and m.used_arms and (controls or not (src.file_gate[f] or gated(m.item.attrs))):
                arms.append(f"{f}:{name}:arms{unused}")
    return sorted(orphan_items), sorted(orphan_imports), arms


def check_references(v6, v7):
    names6 = {it.name for _, it in v6.all_items() if it.kind not in ("use", "inner_attr", "inner_doc", "impl")}
    names7 = {it.name for _, it in v7.all_items() if it.kind not in ("use", "inner_attr", "inner_doc", "impl")}
    removed = names6 - names7
    hits = []
    for f, text in v7.files.items():
        all_idents = idents(tree(lex(text)))
        for name in sorted(removed & all_idents):
            hits.append(f"{f}:{name}")
    # Module declarations must resolve and every verify source file must be declared.
    declared = set(v7.files)
    on_disk = set()
    if v7.rev is None:
        on_disk = {str(p.relative_to(REPO)) for p in (REPO / VERIFY_DIR).rglob("*.rs")}
        on_disk.add(VERIFY_ROOT)
    else:
        out = subprocess.run(["git", "-C", str(REPO), "ls-tree", "-r", "--name-only", v7.rev,
                              VERIFY_DIR], capture_output=True, text=True, check=True).stdout
        on_disk = set(out.split()) | {VERIFY_ROOT}
    mut_refs = set()
    for f, text in v7.files.items():
        mut_refs |= set(re.findall(r"mutations::(\w+)", text))
    mut_defs = {it.name for it in v7.items.get(VERIFY_DIR + "mutations.rs", [])}
    return dict(
        removed_item_names=len(removed), references_to_removed_names=hits,
        undeclared_source_files=sorted(on_disk - declared),
        mutations_references=sorted(mut_refs), unresolved_mutations=sorted(mut_refs - mut_defs),
        specdiag_mentions=[f for f, t in v7.files.items() if "specdiag" in t],
        pass_check3_refs=not hits and not (on_disk - declared) and not (mut_refs - mut_defs)
        and not [f for f, t in v7.files.items() if "specdiag" in t],
    )


def item_diff(v6, v7):
    m6, m7 = item_map(v6), item_map(v7)
    removed, added, changed, doc_only = [], [], [], []
    for key in sorted(set(m6) | set(m7)):
        if key not in m7:
            g = [v6.file_gate[key[0]] or gated(i.all_attrs) for i in m6[key]]
            removed.append(dict(item=":".join(key), gated=all(g)))
        elif key not in m6:
            added.append(":".join(key))
        else:
            if sorted(i.text() for i in m6[key]) != sorted(i.text() for i in m7[key]):
                changed.append(":".join(key))
            elif sorted(i.text(True) for i in m6[key]) != sorted(i.text(True) for i in m7[key]):
                doc_only.append(":".join(key))
    arm_check = {}
    for key in EXPECTED_CHANGED:
        f, _, name = key.split(":")
        m6, m7_ = v6.file_macros[f][name], v7.file_macros[f][name]
        arm_check[key] = dict(
            v6_arms=len(m6.arms), v7_arms=len(m7_.arms),
            kept_arm_identical=len(m7_.arms) == 1 and ser(m6.item.body[3].children[:4])
            == ser(m7_.item.body[3].children[:4]))
    expected_added = {f"{f}:macro_rules:{n}" for f, (_, new) in EXPECTED_REPLACED_MACROS.items()
                      for n in new}
    expected_removed_macros = {f"{f}:macro_rules:{n}"
                               for f, (old, _) in EXPECTED_REPLACED_MACROS.items() for n in old}
    return dict(
        removed=removed, added=added, changed=changed, doc_only=doc_only,
        expected_changed=arm_check,
        unexpected_added=sorted(set(added) - expected_added),
        ungated_removed=[r["item"] for r in removed if not r["gated"]],
        pass_items=set(changed) <= EXPECTED_CHANGED
        and all(v["kept_arm_identical"] for v in arm_check.values())
        and set(added) == expected_added
        and expected_removed_macros <= {r["item"] for r in removed},
    )


def macro_expansion_equivalence(v6, v7):
    """The split macros must reproduce v6 positive (and kept negative) items token-for-token."""
    r6, r7 = v6.roots(True), v7.roots(True)
    rows = []
    for f, (old, new) in EXPECTED_REPLACED_MACROS.items():
        for name, (ff, it) in sorted(r7.items()):
            if ff == f and (it.macro_origin in new or name == "assembly::reject_mutant_swap_u8_n2"):
                same = name in r6 and r6[name][1].text(True) == it.text(True)
                rows.append(dict(root=name, v6_macro=r6[name][1].macro_origin if name in r6
                                 else None, v7_macro=it.macro_origin, identical=same))
    return dict(rows=len(rows), all_identical=all(r["identical"] for r in rows),
                not_identical=[r for r in rows if not r["identical"]])


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)


def check_format(head, wrapper, config, files):
    res = {}
    files = sorted(files)
    long_lines = []
    for f in files:
        text = Source.read(type("R", (), {"rev": head})(), f) or ""
        for n, line in enumerate(text.splitlines(), 1):
            if len(line) > 100:
                long_lines.append(f"{f}:{n}:{len(line)}")
    for f in (SMALLSORT, CARGO):
        d = git("diff", "-U0", BASE, *([] if head is None else [head]), "--", f).stdout
        for line in d.splitlines():
            if line.startswith("+") and not line.startswith("+++") and len(line) - 1 > 100:
                long_lines.append(f"{f}:added:{len(line) - 1}")
    res["files"] = files
    res["long_lines"] = long_lines
    # Working tree: `git diff --check` only sees tracked paths, so stage intent-to-add first
    # (`git add -N`) or pass --head after committing.
    d = git("diff", "--check", BASE, *([] if head is None else [head]), "--", "library")
    res["git_diff_check_rc"] = d.returncode
    res["git_diff_check_output"] = d.stdout[:2000]
    if wrapper:
        if head is not None:
            res["rustfmt"] = "skipped: --rustfmt checks the working tree only"
        else:
            assert files, "no files to format-check"
            r = subprocess.run([wrapper, "--check", "--edition", "2024", "--config-path", config,
                                *[str(REPO / f) for f in files]], capture_output=True, text=True)
            res["rustfmt_rc"] = r.returncode
            res["rustfmt_output"] = (r.stdout + r.stderr)[:2000]
    else:
        res["rustfmt"] = "not run (no --rustfmt wrapper given)"
    res["pass_check4"] = (not long_lines and res["git_diff_check_rc"] == 0
                          and res.get("rustfmt_rc", 0 if not wrapper else 1) == 0)
    return res


def check_diff_scope(head):
    rng = [BASE] if head is None else [BASE, head]
    names = git("diff", "--name-only", *rng).stdout.split()
    if head is None:
        names += git("ls-files", "--others", "--exclude-standard").stdout.split()
    allowed_lib = lambda p: p.startswith(VERIFY_DIR) or p in (VERIFY_ROOT, SMALLSORT, CARGO)
    outside = [p for p in names if not allowed_lib(p)
               and not p.startswith("research/challenge-8/kani-k1/")]
    ss = git("diff", "-U0", *rng, "--", SMALLSORT).stdout
    ss6 = git("diff", "-U0", V6_BASE, V6, "--", SMALLSORT).stdout
    cg = git("diff", "-U0", *rng, "--", CARGO).stdout
    cg6 = git("diff", "-U0", V6_BASE, V6, "--", CARGO).stdout
    body = lambda d: [l for l in d.splitlines() if l[:1] in "+-" and not l.startswith(("+++",
                                                                                      "---"))]
    runtime_same = git("diff", "--quiet", V6_BASE, BASE, "--", SMALLSORT).returncode == 0
    res = dict(
        changed_files=sorted(set(names)), outside_allowed=outside,
        smallsort_rs_lines=body(ss), smallsort_rs_same_as_v6=body(ss) == body(ss6),
        smallsort_rs_only_additions=all(l.startswith("+") for l in body(ss)),
        cargo_toml_lines=body(cg), cargo_toml_same_as_v6=body(cg) == body(cg6),
        runtime_smallsort_unchanged_c0bd09c354_to_233f96f66a=runtime_same,
    )
    res["pass_check5"] = (not outside and res["smallsort_rs_same_as_v6"] and
                          res["smallsort_rs_only_additions"] and res["cargo_toml_same_as_v6"]
                          and runtime_same)
    return res


def line_counts(src: Source, base, head_rev):
    """total / ordinary code / opt-in code / comments / blank, per file and summed.

    A code line is opt-in when it lies in a top-level item gated by the controls cfg (or in a
    gated module file); macro definitions or calls that emit both kinds count as ordinary and are
    listed as `mixed`. Cargo.toml: the check-cfg entry is opt-in code. smallsort.rs: the added
    registration lines.
    """
    per_file, mixed = {}, []
    for f, text in src.files.items():
        lines = text.splitlines()
        optin = set()
        for it in src.items[f]:
            g = src.file_gate[f] or gated(it.attrs)
            if g:
                optin |= set(range(it.first_line, it.last_line + 1))
            elif it.kind in ("macro_rules", "macro_call") and CFG in ser(it.body):
                mixed.append(f"{f}:{it.kind}:{it.name}:{it.first_line}")
        c = Counter()
        for n, line in enumerate(lines, 1):
            s = line.strip()
            if not s:
                c["blank"] += 1
            elif s.startswith("//"):
                c["comment"] += 1
            elif src.file_gate[f] or n in optin:
                c["opt_in_code"] += 1
            else:
                c["ordinary_code"] += 1
        c["total"] = len(lines)
        per_file[f] = dict(c)
    rng = [base] if head_rev is None else [base, head_rev]
    for f in (SMALLSORT, CARGO):
        d = git("diff", "-U0", *rng, "--", f).stdout
        c = Counter()
        for l in d.splitlines():
            if l.startswith("+") and not l.startswith("+++"):
                s = l[1:].strip()
                if not s:
                    c["blank"] += 1
                elif s.startswith(("//", "#")) and not s.startswith(("#[", "#!")):
                    c["comment"] += 1
                elif f == CARGO and CFG in s:
                    c["opt_in_code"] += 1
                else:
                    c["ordinary_code"] += 1
                c["total"] += 1
        per_file[f] = dict(c)
    total = Counter()
    for v in per_file.values():
        total.update(v)
    return dict(per_file=per_file, total=dict(total), mixed_items=mixed)


def sha256_text(t):
    return hashlib.sha256(t.encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--head", default=None, help="git revision for v7 (default: working tree)")
    ap.add_argument("--rustfmt", default=None)
    ap.add_argument("--rustfmt-config", default=None)
    ap.add_argument("--report", default=str(HERE / "check-report.json"))
    args = ap.parse_args()

    v6 = Source(V6)
    v7 = Source(args.head)
    names, ordinary, controls, removed_roots = check_names(v6, v7)
    bodies = check_bodies(v6, v7)
    equivalence = macro_expansion_equivalence(v6, v7)
    o6_items, o6_imports, o6_arms = orphans(v6, False)
    c6_items, c6_imports, c6_arms = orphans(v6, True)
    o7_items, o7_imports, o7_arms = orphans(v7, False)
    c7_items, c7_imports, c7_arms = orphans(v7, True)
    refs = check_references(v6, v7)
    items = item_diff(v6, v7)
    fmt = check_format(args.head, args.rustfmt, args.rustfmt_config, list(v7.files))
    scope = check_diff_scope(args.head)
    lines6 = line_counts(v6, V6_BASE, V6)
    lines7 = line_counts(v7, BASE, args.head)
    # The only ordinary trait impl removed is `impl ArbitraryValue for ()`; no remaining root in
    # network.rs instantiates an ArbitraryValue user with the unit type.
    unit_users = [n for n, (f, it) in v7.roots(True).items()
                  if f.endswith("network.rs") and "< ( ) ," in it.text()]
    check3 = dict(
        v6_cfg_off=dict(orphan_items=o6_items, orphan_imports=o6_imports, unused_arms=o6_arms),
        v6_cfg_on=dict(orphan_items=c6_items, orphan_imports=c6_imports, unused_arms=c6_arms),
        v7_cfg_off=dict(orphan_items=o7_items, orphan_imports=o7_imports, unused_arms=o7_arms),
        v7_cfg_on=dict(orphan_items=c7_items, orphan_imports=c7_imports, unused_arms=c7_arms),
        references=refs, network_roots_with_unit_element_type=unit_users,
    )
    check3["pass_check3"] = (refs["pass_check3_refs"] and not o7_items and not o7_imports
                             and not c7_items and not c7_imports and not o7_arms and not c7_arms
                             and not unit_users)
    checks = {
        "1_ordinary_same_as_v6": names["pass_check1_names"] and bodies["pass_check1_bodies"]
        and items["pass_items"] and equivalence["all_identical"],
        "2_cfg_on_is_ordinary_plus_8": names["pass_check2"],
        "3_no_dangling_refs_or_orphans": check3["pass_check3"],
        "4_format": fmt["pass_check4"],
        "5_diff_scope": scope["pass_check5"],
        "6_line_counts": True,
    }
    report = dict(
        status="PASS" if all(checks.values()) else "FAIL",
        checks=checks,
        v6=V6, base=BASE, head=args.head or "working tree",
        v6_files={f: sha256_text(t) for f, t in v6.files.items()},
        v7_files={f: sha256_text(t) for f, t in v7.files.items()},
        names=names, bodies=bodies, macro_split_equivalence=equivalence, items=items,
        check3=check3, format=fmt, diff_scope=scope,
        line_counts=dict(v6=lines6, v7=lines7),
        removed_opt_in_roots=removed_roots,
        method=("Source-level lexer, item splitter and macro_rules expander; token comparison "
                "ignores whitespace and plain comments, doc comments are compared separately; "
                "name-based conservative dependency closure (every verify item whose name occurs "
                "in a reached item). Not a compiler or Kani inventory."),
    )
    Path(args.report).write_text(json.dumps(report, indent=2) + "\n")
    (HERE / "ordinary-expected.txt").write_text("".join(PREFIX + n + "\n" for n in ordinary))
    (HERE / "controls-expected.txt").write_text("".join(PREFIX + n + "\n" for n in controls))
    (HERE / "moved-to-part2.txt").write_text("".join(PREFIX + n + "\n" for n in removed_roots))
    summary = dict(status=report["status"], checks=checks,
                   counts={k: names[k] for k in ("v6_ordinary", "v6_cfg_on", "v7_ordinary",
                                                 "v7_cfg_on", "removed_opt_in_roots")},
                   lines_v6=lines6["total"], lines_v7=lines7["total"])
    print(json.dumps(summary, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
