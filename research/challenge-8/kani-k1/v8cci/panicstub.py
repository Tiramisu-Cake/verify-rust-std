"""panicstub.py VERIFY_DIR NAMES_TSV: classify each ordinary harness as panic-stubbed or not.

Static, name-based: finds the fn or macro invocation that defines each harness and checks whether
the generating attribute block stubs panic_on_ord_violation. Recursive macros are followed.
"""
import re
import sys
from pathlib import Path

vdir, names_tsv = Path(sys.argv[1]), sys.argv[2]
STUB = re.compile(r"kani::stub\(\s*[\w:]*panic_on_ord_violation")


def strip_comments(s):
    return re.sub(r"//[^\n]*", "", s)


def matching(s, i, o, c):
    d = 0
    for j in range(i, len(s)):
        if s[j] == o:
            d += 1
        elif s[j] == c:
            d -= 1
            if d == 0:
                return j
    raise ValueError("unbalanced")


files = {}
for p in vdir.rglob("*.rs"):
    rel = p.relative_to(vdir).with_suffix("")
    mod = "::".join(rel.parts)
    files[mod] = strip_comments(p.read_text())

# macro name -> list of rule bodies (all files share the namespace for simplicity, keyed per file)
macros = {}
for mod, s in files.items():
    for m in re.finditer(r"macro_rules!\s*(\w+)\s*\{", s):
        end = matching(s, m.end() - 1, "{", "}")
        body = s[m.end():end]
        rules = []
        i = 0
        while True:
            a = body.find("=>", i)
            if a < 0:
                break
            k = a + 2
            while body[k].isspace():
                k += 1
            o = body[k]
            c = {"{": "}", "(": ")", "[": "]"}[o]
            e = matching(body, k, o, c)
            rules.append(body[k + 1:e])
            i = e + 1
        macros.setdefault(m.group(1), []).append(rules)


def macro_status(name, seen=()):
    """Return set of stub statuses (True/False) of proofs the macro can generate."""
    out = set()
    if name in seen or name not in macros:
        return out
    for rules in macros[name]:
        for r in rules:
            for pm in re.finditer(r"#\[kani::proof(_for_contract)?", r):
                fn = r.find("fn ", pm.end())
                out.add(bool(STUB.search(r[pm.start():fn])))
            for im in re.finditer(r"(\w+)!\s*[\(\{\[]", r):
                if im.group(1) in macros:
                    out |= macro_status(im.group(1), seen + (name,))
    return out


res, unknown = {}, []
for line in open(names_tsv):
    h = line.split("\t")[0]
    if h == "harness":
        continue
    mod, _, leaf = h.rpartition("::")
    s = files.get(mod)
    if s is None:
        unknown.append((h, "no file"))
        continue
    m = re.search(r"\bfn\s+" + re.escape(leaf) + r"\s*[<(]", s)
    if m:
        # attribute block above the fn
        start = s.rfind("\n\n", 0, m.start())
        prev_item = max(s.rfind("}\n", 0, m.start()), s.rfind(";\n", 0, m.start()))
        block = s[max(start, prev_item) + 1:m.start()]
        res[h] = bool(STUB.search(block))
        continue
    m = re.search(r"(\w+)!\s*\(\s*" + re.escape(leaf) + r"\b", s)
    if m:
        st = macro_status(m.group(1))
        if len(st) == 1:
            res[h] = st.pop()
        else:
            unknown.append((h, f"macro {m.group(1)} statuses {st}"))
        continue
    unknown.append((h, "not found"))

stubbed = sorted(h for h, v in res.items() if v)
by_mod = {}
for h in stubbed:
    by_mod[h.split("::")[0]] = by_mod.get(h.split("::")[0], 0) + 1
print(f"classified={len(res)} stubbed={len(stubbed)} by_module={by_mod}")
for u in unknown:
    print("UNKNOWN", *u)
if len(sys.argv) > 3:
    Path(sys.argv[3]).write_text("\n".join(stubbed) + "\n")
