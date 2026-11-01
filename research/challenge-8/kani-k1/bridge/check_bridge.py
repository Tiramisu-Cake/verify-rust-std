#!/usr/bin/env python3
"""Read-only source/request gate; no compiler, proof, or native inventory claim."""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
K1 = HERE.parent
ROOT = K1.parents[2]
BASE = "2dde801cf4"
S = "library/core/src/slice/sort/shared/smallsort"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True)


ss = load("source_sets", K1 / "poneclean/source_sets.py")
ss.MODULES += [("wrap", "wrap.rs", "ordinary")]
old = ss.sets(BASE)
ss.MODULES += [("bridge", "bridge.rs", "controls")]
now = ss.sets()
src = (ROOT / S / "verify/bridge.rs").read_text()
registration = (ROOT / S / "verify.rs").read_text()
base_registration = git("show", f"{BASE}:{S}/verify.rs")
req = json.loads((K1 / "RUN-REQUEST.json").read_text())
lane = load("kani_k1", K1 / "tools/kani_k1.py")
lane.validate_request(req)
rows = [r for r in now["records"] if r["name"].startswith(ss.PREFIX + "bridge::")]
expected = (K1 / "integwrapfix/ordinary-expected.txt").read_text().splitlines()
changed = set(git("diff", "--name-only", BASE, "--", "library").splitlines())
changed |= set(git("ls-files", "--others", "--exclude-standard", "--", "library").splitlines())
allowed = {f"{S}/verify.rs", f"{S}/verify/bridge.rs"}
checks = {
    "library_scope": changed == allowed,
    "registration_only": registration == base_registration + "\nmod bridge;\n",
    "bridge_opt_in": "#![cfg(kani_smallsort_controls)]" in src,
    "target_module_before_pfc_module": registration.index("mod merge;")
    < registration.index("mod bridge;"),
    "a3_target_before_pfcs": src.index("unsafe fn frame_target(")
    < src.index("#[kani::proof_for_contract(frame_target)]"),
    "ordinary_exact_base_and_frozen_200": now["ordinary"] == old["ordinary"] == sorted(expected)
    and len(expected) == 200,
    "cfg_on_delta_exact_six": set(now["cfg_on"]) - set(old["cfg_on"])
    == {r["name"] for r in rows} and set(old["cfg_on"]) <= set(now["cfg_on"])
    and len(rows) == 6,
    "request_exact_six": {r["name"] for r in req["harnesses"]}
    == {r["name"] for r in rows},
    "request_copy": req == json.loads((HERE / "g1.request.json").read_text()),
    "request_envelope": req["kind"] == "diagnostic" and req["controls"] is True
    and req["kani_jobs"] == 1 and req["uninit_checks"] is False
    and req["harness_timeout_minutes"] == 3 and len(req["harnesses"]) == 6,
    "sole_closed_impl": src.count("impl MergeBridge<") == 1
    and "impl MergeBridge<fn(&u8, &u8) -> bool> for u8" in src,
    "forward_received_fn_value": "merge_profile::<LtU8>(v, dst, *is_less)" in src,
    "no_transmute_or_specialization": "transmute" not in src
    and "specialization" not in src,
    "caller_stubs_only": src.count("#[kani::stub(bidirectional_merge, adapter)]") == 3
    and src.count("#[kani::stub_verified(merge_profile)]") == 3
    and all(not r["stub_verified"] for r in rows if r["pfc"]),
    "line_width": all(len(line) <= 100 for line in src.splitlines()),
}
names_text = "\n".join(now["ordinary"]) + "\n"
out = dict(ok=all(checks.values()), base=git("rev-parse", BASE).strip(), checks=checks,
           ordinary_count=len(now["ordinary"]),
           ordinary_names_sha256=hashlib.sha256(names_text.encode()).hexdigest(),
           cfg_on_before=len(old["cfg_on"]), cfg_on_after=len(now["cfg_on"]),
           new_rows=rows, request_sha256=hashlib.sha256((K1 / "RUN-REQUEST.json").read_bytes()).hexdigest(),
           reserve_usd=(6 * 3 + 30) * 0.0135,
           limitation="Static source forecast only; compile/proofs/native inventory NOT_RUN")
print(json.dumps(out, indent=2))
sys.exit(0 if out["ok"] else 1)
