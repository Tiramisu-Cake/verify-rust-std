"""COVERCOST source/packet checks only. Does not run a compiler or verifier."""
import difflib
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
K1 = HERE.parent
ROOT = HERE.parents[3]
BASE = "5737fa738bac360f19dd0113b2b8640f16bea5f5"  # terminal U64-TEN-CALLER (task base)
TOOL_BASE = "30f77e859903df14b442ff9294d4fbbd44827f20"
SMALLSORT = "library/core/src/slice/sort/shared/smallsort"
VERIFY = SMALLSORT + "/verify"
CHILD = VERIFY + "/network/u64nine/tenleaves/caller.rs"
LANE = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
        "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh", "tool_config/kani-version.toml",
        "rust-toolchain.toml", ".gitmodules", ".cargo", "library/.cargo", "library/Cargo.toml",
        "library/Cargo.lock"]
ORIG = "u64tencall_positive_u64_n10"
CLONE = "u64tencall_positive_nocover_u64_n10"
FULL = "slice::sort::shared::smallsort::verify::network::u64nine::tenleaves::caller::"
ANNOTATION = [
    "#[kani::proof]",
    "#[kani::stub(crate::slice::sort::shared::smallsort::swap_if_less, swap_adapter_u64ten)]",
    "#[kani::stub_verified(super::super::swap_u64_net9)]",
    "#[kani::stub(crate::slice::sort::shared::smallsort::insert_tail, insert_adapter_u64ten)]",
    "#[kani::stub_verified(super::super::super::super::merge::specfix::insert_tail_profile)]",
    "#[kani::unwind(25)]",
]
HEADER = ("\n// COVERCOST diagnostic (memory only, no proof credit): byte clone of u64tencall_positive_u64_n10\n"
          "// with every kani::cover of the root body removed; nothing else differs. Helpers and adapters\n"
          "// above are shared unchanged and contain no kani::cover.\n")
ROOT_COVERS = {"u64tencall_positive_u64_n10": 9, "u64tencall_swap_binding_negative_u64_n10": 1,
               "u64tencall_insert_binding_negative_u64_n10": 1, "u64tencall_count_negative_u64_n10": 2,
               CLONE: 0}
# Files whose functions the clone can reach (name-level over-approximation below).
DEP_FILES = [CHILD, VERIFY + "/network/u64nine/tenleaves.rs", VERIFY + "/network/u64nine.rs",
             VERIFY + "/network.rs", VERIFY + "/merge.rs", VERIFY + "/merge/specfix.rs"]
NO_COVER_FILES = [SMALLSORT + ".rs", "library/core/src/ub_checks.rs"]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


predict = load("predict", K1 / "c3b/predict_inventory.py")
inv = load("inventory", K1 / "cleanup/source_inventory.py")


def root_block(text, name):
    """Attributes + fn item of a root, from its first #[kani::proof] to the closing brace line."""
    pos = text.index("\nfn " + name + "()")
    start = text.rindex("#[kani::proof]", 0, pos)
    end = text.index("\n}\n", pos) + 3
    return text[start:end]


def strip_covers(block):
    out, lines, i = [], block.split("\n"), 0
    while i < len(lines):
        if lines[i].lstrip().startswith("kani::cover("):
            while not lines[i].rstrip().endswith(");"):
                i += 1
            i += 1
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


# 1. Library: only the child changes, and only by appending header + clone root.
base_child = git("show", f"{BASE}:{CHILD}")
child = (ROOT / CHILD).read_text()
assert git("diff", "--name-only", BASE, "--", "library").splitlines() == [CHILD]
assert child.startswith(base_child), "existing bytes of caller.rs changed"
appended = child[len(base_child):]
orig = root_block(base_child, ORIG)
assert orig == root_block(child, ORIG)
ALLOW = "#[allow(unused_variables, unused_assignments)]"  # review dce6fab10d: the only extra line
expected_clone = strip_covers(orig).replace(f"fn {ORIG}()", f"{ALLOW}\nfn {CLONE}()", 1)
assert appended == HEADER + expected_clone, "appended text is not header + cover-free clone"
clone = root_block(child, CLONE)
assert clone == expected_clone
assert not git("diff", TOOL_BASE, "--", *LANE)
assert max(map(len, child.splitlines())) <= 100

# 2. Byte diff of the original root against the clone: only cover lines and the fn name.
diff = list(difflib.unified_diff(orig.splitlines(), clone.splitlines(), "original-root", "clone-root",
                                 n=0, lineterm=""))
(HERE / "root-clone.diff").write_text("\n".join(diff) + "\n")
removed = [l[1:] for l in diff if l.startswith("-") and not l.startswith("---")]
added = [l[1:] for l in diff if l.startswith("+") and not l.startswith("+++")]
assert added == [ALLOW, f"fn {CLONE}() {{"], added
assert child.count("#[allow(") == 1 and ALLOW in clone and ALLOW not in orig
assert removed[0] == f"fn {ORIG}() {{"
removed_cover_text = "\n".join(removed[1:])
assert removed_cover_text.count("kani::cover(") == 9
assert all(l.lstrip().startswith(("kani::cover(", "probe ", "\"u64tencall positive", ");"))
           for l in removed[1:]), removed[1:]

# 3. Annotations, inputs, calls and covers of every root.
for name in [ORIG, CLONE]:
    block = root_block(child, name)
    assert re.findall(r"#\[kani::[^\n]+", block) == ANNOTATION, name
    assert block.count("kani::any()") == 2 and block.count("kani::assume") == 0
calls = ["let mut v: [u64; 10] = kani::any();", "let pre = v;", "let probe: u64 = kani::any();",
         "let mut cmp: U64Cmp = StrictU64::CMP;", "run_u64ten(&mut v, probe, &mut cmp);",
         "check_final_u64ten(&v, &pre, probe);"]
for name in [ORIG, CLONE]:
    block = root_block(child, name)
    assert [block.index(c) for c in calls] == sorted(block.index(c) for c in calls), name
covers_per_root = {}
for name, want in ROOT_COVERS.items():
    covers_per_root[name] = root_block(child, name).count("kani::cover(")
    assert covers_per_root[name] == want, (name, covers_per_root[name])
assert child.count("kani::cover(") == sum(ROOT_COVERS.values()) == 13  # none outside root bodies
assert re.findall(r"^fn (u64tencall_\w+)\(\)", child, re.M)[-1] == CLONE


# 4. Covers reachable from the clone: name-level closure over the dependency files.
def functions(path):
    text = (ROOT / path).read_text()
    masked = predict.mask_comments_strings(text)
    found = []
    for m in re.finditer(r"\bfn\s+([A-Za-z_]\w*)\s*(?:<|\()", masked):
        # First `{` or `;` outside (...) and [...] after the name: body or bodiless declaration.
        depth, k = 0, m.end() - 1
        while not (depth == 0 and masked[k] in "{;"):
            depth += masked[k] in "([" and 1 or -(masked[k] in ")]")
            k += 1
        if masked[k] == ";":
            continue  # trait method declaration without body
        brace = k
        close = predict.matching(masked, brace, "{", "}")
        item = m.start()  # back over `pub(crate)`, `unsafe`, `const` so contract attributes are seen
        while q := re.search(r"(?:pub\s*\([^)]*\)|pub|unsafe|const)\s*$", masked[max(0, item - 40):item]):
            item -= len(q.group(0))
        attrs = inv.attr_block(masked, item)
        proof = bool(re.search(r"kani\s*::\s*proof(?:_for_contract)?\b", attrs))
        found.append(dict(file=path, name=m.group(1), proof=proof,
                          line=text.count("\n", 0, m.start()) + 1,
                          code=attrs + masked[m.start():close + 1],
                          covers=text[m.start():close + 1].count("kani::cover(")))
    return found


fns = [f for p in DEP_FILES for f in functions(p)]
for p in NO_COVER_FILES:
    assert (ROOT / p).read_text().count("kani::cover") == 0, p
macro_body = predict.mask_comments_strings((ROOT / (VERIFY + "/merge/specfix.rs")).read_text())
ident_start = macro_body.index("macro_rules! identity_profile")
ident_body = macro_body[ident_start:predict.matching(macro_body, macro_body.index("{", ident_start),
                                                     "{", "}") + 1]
assert "kani::cover" not in ident_body
caller_names = {f["name"] for f in fns if f["file"] == CHILD}
seen, todo = set(), [f for f in fns if f["file"] == CHILD and f["name"] == CLONE]
idents = lambda code: set(re.findall(r"\b([A-Za-z_]\w*)\b", code))
while todo:
    f = todo.pop()
    key = (f["file"], f["line"])
    if key in seen:
        continue
    seen.add(key)
    for ident in idents(f["code"]):
        for g in fns:
            if g["name"] != ident or g["proof"]:
                continue
            # Trait methods named like the caller's closed impls resolve to caller.rs (T: *BridgeU64Ten).
            if ident in caller_names and g["file"] != CHILD:
                continue
            todo.append(g)
reach = sorted({(f["file"], f["name"], f["line"]) for f in fns if (f["file"], f["line"]) in seen})
reach_covers = [(f["file"], f["name"], f["covers"]) for f in fns
                if (f["file"], f["line"]) in seen and f["covers"] and f["name"] != CLONE]
assert reach_covers == [], reach_covers
# StrictU64::CMP / model_less come from identity_profile!(StrictU64, u64, ..., strict_less::<u64>, ...).
net_text = predict.mask_comments_strings((ROOT / (VERIFY + "/network.rs")).read_text())
strict_call = net_text[net_text.index("StrictU64,", net_text.index("identity_profile!(")):]
assert strict_call[:strict_call.index(");")].count("strict_less::<u64>") == 2
macro_arg_helpers = [f for f in fns if f["file"] == VERIFY + "/network.rs" and f["name"] == "strict_less"]
assert len(macro_arg_helpers) == 1 and macro_arg_helpers[0]["covers"] == 0
helper_cover_fns = sorted({(f["file"].split("/verify/")[1], f["name"]) for f in fns
                           if f["covers"] and not f["proof"]})
excluded_same_name = sorted({f["file"].split("/verify/")[1] + ":" + f["name"] for f in fns
                             if f["name"] in caller_names and f["file"] != CHILD and not f["proof"]})
assert "network/u64nine.rs:exchange" in excluded_same_name
assert not any(name == "adapter_u64nine" for _, name, _ in reach)

# 5. Static inventory: ordinary unchanged, cfg-on +1 exact name, PFC sites unchanged.
ordinary, _ = inv.inventory(False)
controls, _ = inv.inventory(True)
expected_ordinary = (K1 / "integwrapfix/ordinary-expected.txt").read_text().splitlines()
assert [r["name"] for r in ordinary] == sorted(expected_ordinary) and len(ordinary) == 200
base_controls = json.loads((K1 / "u64tencall/static-check.json").read_text())
assert base_controls["controls_exact"] == 405
controls_names = [r["name"] for r in controls]
assert len(controls_names) == 406 and FULL + CLONE in controls_names
old_controls = sorted(n for n in controls_names if n != FULL + CLONE)
assert len(old_controls) == 405 and set(base_controls["added"]) <= set(old_controls)
pfc = subprocess.check_output(["python3", "-I", str(K1 / "integwrapfix/pfc_order.py"),
                               str(ROOT / SMALLSORT)], text=True).strip()
assert pfc == "ordinary pfc sites 21 bad 0", pfc
pfc_attr = {rev: sum(git("show", f"{rev}:{p}").count("proof_for_contract")
                     for p in git("ls-tree", "-r", "--name-only", rev, "--", SMALLSORT).split())
            for rev in [BASE, "HEAD"]}
assert pfc_attr[BASE] == pfc_attr["HEAD"], pfc_attr
assert "proof_for_contract" not in appended and "kani::requires" not in appended

# 6. Request package.
request_path = K1 / "RUN-REQUEST.json"
g1 = HERE / "g1.request.json"
assert request_path.read_bytes() == g1.read_bytes()
request = json.loads(g1.read_text())
assert request == {
    "schema": "kani-k1-run-request-v1", "agent": "k1-merge", "runner": "gcb-e2-standard-4",
    "request_id": request["request_id"], "kind": "diagnostic", "purpose": request["purpose"],
    "harness_timeout_minutes": 10, "kani_jobs": 1, "uninit_checks": False, "controls": True,
    "harnesses": [{"name": FULL + CLONE, "expect": "SUCCESS"}]}
assert request["request_id"].startswith("covercost-")

dependencies = [SMALLSORT + ".rs", "library/core/src/ub_checks.rs"] + DEP_FILES + LANE[4:7]
report = dict(
    status="PASS", base=BASE, base_library_tree=git("rev-parse", f"{BASE}:library").strip(),
    library_commit=git("log", "-1", "--format=%H", "--", "library").strip(),
    library_tree=git("rev-parse", "HEAD:library").strip(),
    changed_library_files=[CHILD], child_change="append-only (header comment + clone root)",
    base_child_sha256=sha(base_child), child_sha256=sha(child),
    original_root_sha256=sha(orig), clone_root_sha256=sha(clone),
    clone_diff_removed_cover_calls=9, clone_diff_other_change="fn name + one #[allow(unused_variables, unused_assignments)] line",
    covers_per_root=covers_per_root, child_covers_outside_roots=0,
    reachable_helpers=[f"{f.split('/verify/')[1]}:{n}" for f, n, _ in reach if n != CLONE],
    macro_arg_helpers=["network.rs:strict_less (0 covers)"],
    reachable_helper_covers=0, helper_cover_fns_not_reachable=[f"{a}:{b}" for a, b in helper_cover_fns],
    same_name_excluded=excluded_same_name, no_cover_files=NO_COVER_FILES,
    ordinary_exact=200, controls_before=405, controls_exact=406, added=[FULL + CLONE],
    pfc_order=pfc, proof_for_contract_occurrences=pfc_attr["HEAD"],
    protected_tooling_unchanged=True, annotations=ANNOTATION,
    request_sha256=sha(g1.read_bytes()), run_request_sha256=sha(request_path.read_bytes()),
    dependency_sha256={p: sha((ROOT / p).read_text()) for p in dependencies},
)
(HERE / "static-check.json").write_text(json.dumps(report, indent=1) + "\n")
print("PASS", report["library_commit"], report["library_tree"], len(report["reachable_helpers"]),
      "reachable helpers, 0 covers;", pfc)
