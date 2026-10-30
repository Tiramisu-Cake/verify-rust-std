"""Static domain/scope checks only; does not invoke Rust or proof tools."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

BASE = "e5a0d8dd511730f374e2f757c8ac37f733062842"
G2 = "c81c10e3061e07bb83c732d81413632ada757d2c"
ROOT = Path(__file__).parent
VERIFY = Path("library/core/src/slice/sort/shared/smallsort/verify")


def blob(sha, path):
    return subprocess.check_output(["git", "show", f"{sha}:{path}"])


def body(text, name):
    start = text.index("fn " + name + "<")
    begin = text.index(" {", start) + 1
    depth, end = 1, begin + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[begin:end]


checks = {}
for name in ("merge.rs", "network.rs"):
    path = VERIFY / name
    old, now = blob(BASE, path), path.read_bytes()
    assert now.startswith(old)
    delta = now[len(old):].decode()
    assert delta.count("mod backing {") == 1
    assert "#[cfg(kani_smallsort_controls)]\nmod backing {" in delta
    assert "assume_init" not in delta and "opt_split::" not in delta
    assert max(map(len, delta.splitlines())) <= 100
    checks[name] = {"original_prefix_preserved": True, "appended_lines": len(delta.splitlines())}

old = blob(BASE, VERIFY / "merge.rs").decode()
new = (VERIFY / "merge.rs").read_text().split("mod backing {", 1)[1]
before, after = body(old, "stable_direct_body"), body(new, "stable_direct_body")
before = before.replace(
    "let mut scratch = [MaybeUninit::<u64>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN];",
    "let mut holder = MaybeUninit::<[u64; SMALL_SORT_GENERAL_SCRATCH_LEN]>::uninit();\n"
    "        let scratch = scratch_view(&mut holder);",
).replace("&mut v, &mut scratch,", "&mut v, scratch,")
assert before == after
checks["B_body_except_backing_and_adapter"] = True

old = blob(BASE, VERIFY / "network.rs").decode()
new = (VERIFY / "network.rs").read_text().split("mod backing {", 1)[1]
oldbody = body(old, "dispatch_safety_fixed")[1:-1]
init, branches = oldbody.split("    if STABLE {\n", 1)
init = "\n".join(line for line in init.splitlines() if "use super::super::" not in line)
before = init + branches.split("    } else {", 1)[0]
before = before.replace(
    "let mut scratch = [const { crate::mem::MaybeUninit::<T>::uninit() }; 48];",
    "let mut holder = MaybeUninit::<[T; SMALL_SORT_GENERAL_SCRATCH_LEN]>::uninit();"
    "let scratch = scratch_view(&mut holder);",
).replace("&mut scratch,", "scratch,")
after = body(new, "dispatch_safety_aggregate")[1:-1]
assert re.sub(r"\s", "", before) == re.sub(r"\s", "", after)
checks["dispatch_true_branch_except_backing_and_adapter"] = True

paths = [
    "library/core/src/slice/sort/shared/smallsort.rs",
    "library/core/src/slice/sort/shared/smallsort/verify.rs",
    str(VERIFY / "merge.rs"), str(VERIFY / "network.rs"),
    "library/core/src/slice/sort/shared/mod.rs",
    "scripts/run-kani.sh", "tool_config/kani-version.toml", "rust-toolchain.toml",
    "research/challenge-8/kani-k1/tools/kani_k1.py",
    "research/challenge-8/kani-k1/tools/gcb-k1.sh",
    "research/challenge-8/kani-k1/gcb/cloudbuild.yaml", ".github/workflows/kani.yml",
]
checks["G2_to_base_identical_dependencies"] = {}
for path in paths:
    a, b = blob(G2, path), blob(BASE, path)
    assert a == b, path
    checks["G2_to_base_identical_dependencies"][path] = hashlib.sha256(a).hexdigest()

request = json.loads((ROOT.parent / "RUN-REQUEST.json").read_text())
assert len(request["harnesses"]) == 7 and request["kani_jobs"] == 1 and request["controls"]
assert request["kind"] == "measurement" and request["harness_timeout_minutes"] == 10
assert request["runner"] == "gcb-e2-standard-4"
assert (ROOT / "matched.request.json").read_bytes() == (
    ROOT.parent / "RUN-REQUEST.json"
).read_bytes()
for entry in request["harnesses"]:
    if "::backing::" in entry["name"]:
        module = entry["name"].split("::verify::")[1].split("::")[0]
        text = (VERIFY / f"{module}.rs").read_text()
        assert f'fn {entry["name"].rsplit("::", 1)[1]}()' in text
checks["request_names_and_envelope"] = True
subprocess.run(["git", "diff", "--exit-code", G2, BASE, "--", "library"], check=True)
checks["G2_to_base_whole_library_identical"] = True
result = dict(base_sha=BASE, reuse_a_source_sha=G2, checks=checks, local_proof_tools_run=False)
lines = []
for line in json.dumps(result, indent=2).splitlines():
    if len(line) > 100 and ": " in line:
        key, value = line.split(": ", 1)
        lines.extend([key + ":", "      " + value])
    else:
        lines.append(line)
(ROOT / "static-audit.json").write_text("\n".join(lines) + "\n")
print("PASS: original prefixes, matched bodies, G2 dependencies, request names and envelope")
