# Whitespace-normalized diff of the PERMANY shared body against the PERMSOLVER arbitrary-probe bodies
# (read from git at RESULT a13389358a). Usage: python3 -I body_diff.py (from the repo root).
import re, subprocess, difflib
N = "library/core/src/slice/sort/shared/smallsort/verify/network/"
REF = "a13389358a"
def git_text(path): return subprocess.run(["git", "show", f"{REF}:{path}"], check=True, capture_output=True, text=True).stdout
def item(t, name):
    i = re.search(r"fn " + name + r"\b", t).start(); s = t.rfind("\n\n", 0, i) + 2
    d = 0; j = t.index("{", i)
    for k in range(j, len(t)):
        d += t[k] == "{"; d -= t[k] == "}"
        if d == 0: return t[s:k + 1]
def norm(s, subs):
    for a, b in subs: s = s.replace(a, b)
    s = re.sub(r"(?m)^\s*///.*\n", "", s)  # doc comments are not statements
    s = re.sub(r"\s+", " ", s); s = re.sub(r"\(\s", "(", s); s = re.sub(r",\s\)", ")", s)
    s = s.replace("; ", ";\n").replace("{ ", "{\n").replace("} ", "}\n")
    return re.sub(r"\)\] (?=[#f])|\] (?=[#f])", lambda m: m.group(0)[:-1] + "\n", s)
def show(tag, a, b):
    print("==", tag); d = list(difflib.unified_diff(a.splitlines(), b.splitlines(), "orig", "new", n=0, lineterm=""))
    print("\n".join(d[2:]) if d else "(identical)")
new = open(N + "permany.rs").read()
body = norm(item(new, "permany_count_u64_n8"), [])
show(f"permany_count_u64_n8 vs posts::partposts_count_u64_n8 @{REF} (same parent paths super::)",
     norm(item(git_text(N + "posts.rs"), "partposts_count_u64_n8"), []), body)
show(f"permany_count_u64_n8 vs posts::perm::solver::perm_arbitrary_kissat_u64_n8 @{REF} (super::super::super:: -> super::)",
     norm(item(git_text(N + "posts/perm/solver.rs"), "perm_arbitrary_kissat_u64_n8"), [("super::super::super::", "super::")]), body)
show("permany_u64_n8_kissat vs permany_u64_n8_default", norm(item(new, "permany_u64_n8_default"), []),
     norm(item(new, "permany_u64_n8_kissat"), []))
show("permany_u64_n8_value_loss_control vs permany_u64_n8_kissat", norm(item(new, "permany_u64_n8_kissat"), []),
     norm(item(new, "permany_u64_n8_value_loss_control"), []))
