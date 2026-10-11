#!/usr/bin/env python3
"""Cloud-only native C1–C4 source and original-AST capture. Inert on import."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil

HERE = Path("research/challenge-8/cloud-build/sort4-native-c1-bound")
TR = Path("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")
BASE_TR = "381e80ebe9a789877ee9d0e860da386f7692f54879b39775e01267f0db6f53d6"
KERNEL = "37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c"


def require(ok, message):
    if not ok:
        raise RuntimeError("NATIVE-C4-CAPTURE: " + message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one_replace(source, old, new, label):
    require(source.count(old) == 1, "nonunique " + label)
    return source.replace(old, new, 1)


def current_post(index, *, leak=False):
    suffix = str(index)
    prior = "source_current" if index == 2 else f"source_current{index-1}"
    body = (f"assert v_base[..4] |-> ?first_current{suffix};\n"
            "array_join::<T>(v_base);\n"
            f"foreach_append(first_current{suffix}, drop(4, {prior}));\n"
            f"assert v_base[..len] |-> ?source_current{suffix};\n"
            f"assert foreach(source_current{suffix}, own::<T>(t));\n"
            "assert mu_base[..scratch_len] |-> mu_all;\n"
            "assert foreach(mu_all, own::<std::mem::MaybeUninit<T>>(t));\n"
            f"assert *is_less |-> ?less_current{suffix};\n"
            f"assert <F>.own(t, less_current{suffix});")
    if leak:
        body += "\nleak type_interp::<T>();\nleak type_interp::<F>();"
    return body


def annotated_step(proof_root, index):
    paths = {
        2: "research/challenge-8/cloud-build/sort4-native-entry-c1/C2-ANNOTATION-DRAFT.rs",
        3: "research/challenge-8/cloud-build/sort4-c3-bound-prefix/C3-ANNOTATION.rs",
        4: "research/challenge-8/cloud-build/sort4-c4-bound-prefix/C4-ANNOTATION.rs",
    }
    source = (proof_root / paths[index]).read_text()
    start = f"        //@ let cmp{index}_k = begin_lifetime();"
    require(source.count(start) == 1, f"C{index} source start")
    source = source[source.index(start):].rstrip() + "\n"
    marker = f"__vf_sort4_{ {2: 'second', 3: 'third', 4: 'fourth'}[index] }_unwind();"
    require(source.count(marker) == 1, f"C{index} marker")
    source = one_replace(source, "        } @*/\n",
                         "            { " + current_post(index, leak=True).replace("\n", "\n              ") + " }\n        } @*/\n",
                         f"C{index} full direct-unwind cleanup")
    return source


def make_source(a, driver, fixture):
    """Create one isolated source pair in Cloud; no verifier is invoked here."""
    source_file = a.proof_root / HERE / "followup-cases.rs"
    source = source_file.read_text()
    matched = re.search(r"(?ms)^// CASE_BEGIN native-c1-bound-positive\n(.*?)^// CASE_END native-c1-bound-positive$", source)
    require(matched is not None, "pinned C1 positive case absent")
    first = matched.group(1)
    provenance = json.loads((a.proof_root / HERE / "TRAIT-SOURCE-PROVENANCE.json").read_text())
    require(provenance["mode"] == "DOCUMENTARY_EXCERPT_NOT_CALLER_PROOF" and
            provenance["sources"]["library/core/src/marker.rs"]["exact_declaration"] ==
            "pub unsafe auto trait Freeze {}" and
            provenance["sources"]["library/core/src/slice/sort/shared/mod.rs"]["exact_declaration"] ==
            "pub(crate) trait FreezeMarker {}\n\nimpl<T: Freeze> FreezeMarker for T {}",
            "trait provenance declarations")

    require(first.count("let c1 = is_less") == 1 and first.count("let c2 = is_less") == 0,
            "C1 case runtime shape")
    selected_file = (a.proof_root /
        "research/challenge-8/cloud-build/sort4-c3-bound-prefix/selected-four.rs")
    selected = selected_file.read_text()
    require(selected.startswith("/*@") and selected.rstrip().endswith("@*/") and
            selected.count("lem split_selected_four<T>") == 1 and
            selected.count("lem join_selected_four<T>") == 1,
            "selected-four same-version helper shape")
    first = one_replace(first, "// This function keeps the automatic safe-reference contract.",
                        selected + "\n\n// This function keeps the automatic safe-reference contract.",
                        "helper insertion")
    # The C1 normal path retains type interpretations while another callback
    # follows. Direct unwind still leaks them only after all current resources
    # have been restored; final normal return leaks them after C4.
    ending = ("        //@ assert <F>.own(t, less_current);\n"
              "        //@ leak type_interp::<T>();\n"
              "        //@ leak type_interp::<F>();\n"
              "    }\n}\n")
    require(first.endswith(ending), "C1 normal ending")
    first = first[:-len(ending)] + "        //@ assert <F>.own(t, less_current);\n"
    # Extend the original unsafe block through C4 so the source-derived c1
    # result remains in scope for the exact a/b pointer selections.
    first = one_replace(first,
                        "            //@ end_lft_binding::<'cmp>();\n        }\n",
                        "            //@ end_lft_binding::<'cmp>();\n",
                        "C1 unsafe scope extension")
    steps = []
    for index in (2, 3, 4):
        preceding = "source_current" if index == 2 else f"source_current{index-1}"
        steps.extend((
            "        //@ array_split::<T>(v_base, 4);\n",
            f"        //@ foreach_split({preceding}, own::<T>(t), 4);\n",
        ))
        if index == 3:
            steps.append("        //@ selected_four_limits::<T>(v_base, c1, c2);\n")
            steps.append("        let a = v_base.add(c1 as usize);\n"
                         "        let b = v_base.add(!c1 as usize);\n"
                         "        let c = v_base.add(2 + c2 as usize);\n"
                         "        let d = v_base.add(2 + (!c2 as usize));\n")
        steps.append(annotated_step(a.proof_root, index))
        normal = current_post(index, leak=index == 4)
        steps.append("".join("        //@ " + line + "\n" for line in normal.splitlines()))
    verified_text = first + "".join(steps) + "        }\n    }\n}\n"
    require(verified_text.count("let c1 = is_less") == 1 and
            all(verified_text.count(f"let c{i} = is_less") == 1 for i in (2, 3, 4)) and
            all(verified_text.count(f"__vf_sort4_{name}_unwind();") == 1
                for name in ("first", "second", "third", "fourth")),
            "four actual calls and four direct-unwind markers")
    std = (a.proof_root / "library/core/src/slice/sort/shared/smallsort.rs").read_text()
    expressions = (
        "let c1 = is_less(&*v_base.add(1), &*v_base);",
        "let c2 = is_less(&*v_base.add(3), &*v_base.add(2));",
        "let a = v_base.add(c1 as usize);",
        "let b = v_base.add(!c1 as usize);",
        "let c = v_base.add(2 + c2 as usize);",
        "let d = v_base.add(2 + (!c2 as usize));",
        "let c3 = is_less(&*c, &*a);",
        "let c4 = is_less(&*d, &*b);",
    )
    for expression in expressions:
        require(std.count(expression) == 1, "actual std expression " + expression)
    ghost = driver.load(a.cloud_dir / "sort4-native-entry-c1/c2_discovery.py", "native_c4_ghost")
    verified = verified_text.encode()
    original = ghost.strip_ghost(verified)
    for expression in expressions:
        require(original.count(expression.encode()) == 1,
                "ghost-stripped actual expression " + expression)
    require([original.index(expression.encode()) for expression in expressions] ==
            sorted(original.index(expression.encode()) for expression in expressions),
            "ghost-stripped comparator/pointer source order")
    require(original.count(b"is_less(") == 4 and
            b"copy_nonoverlapping" not in original and
            b"select_unpredictable" not in original,
            "four-call prefix boundary")
    fixture.mkdir(parents=True)
    (fixture / "verified").mkdir()
    (fixture / "original").mkdir()
    (fixture / "verified/lib.rs").write_bytes(verified)
    (fixture / "original/lib.rs").write_bytes(original)
    certificate = {"verified_sha256": sha(fixture / "verified/lib.rs"),
                   "original_sha256": sha(fixture / "original/lib.rs"),
                   "std_source_sha256": sha(a.proof_root / "library/core/src/slice/sort/shared/smallsort.rs"),
                   "c1_case_sha256": sha(source_file), "selected_helper_sha256": sha(selected_file),
                   "runtime_ghost_strip_identical": True, "proof_credit": False,
                   "external_caller": "NOT_PROVED", "native_c1_to_c4": "NOT_RUN"}
    driver.save(a.evidence / "native-c4-source-certificate.json", certificate)
    return certificate


def run(a, c1_tool, env, driver):
    require(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
            os.environ.get("LANE") == "o26-sort4-c1-current-recovery",
            "Cloud-only authorized lane")
    manifest_path = a.proof_root / HERE / "NATIVE-C4-CAPTURE-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    patch = a.proof_root / HERE / "native-c4-capture.patch"
    require(manifest.get("mode") == "NATIVE_C4_CAPTURE_ONLY_ALWAYS_REFUSE" and
            manifest.get("profile_accepted") is False and
            manifest.get("tool_head") == "f76012fb518703b1d98e243ac4f487f16877cfcb" and
            manifest.get("base_translator_sha256") == BASE_TR and
            manifest.get("kernel_sha256") == KERNEL and
            sha(patch) == manifest.get("patch_sha256") and
            [line for line in patch.read_text().splitlines()
             if line.startswith(("--- ", "+++ "))] ==
            [f"--- a/{TR}", f"+++ b/{TR}"], "manifest/patch admission")
    source_inputs = manifest.get("source_inputs")
    require(isinstance(source_inputs, dict) and len(source_inputs) == 6 and
            all(sha(a.proof_root / path) == expected
                for path, expected in source_inputs.items()),
            "exact source/helper input hashes")
    require(sha(c1_tool / TR) == BASE_TR and
            sha(c1_tool / "src/verifast.ml") == KERNEL,
            "fresh C1 base tool identity")
    historical = driver.load(a.cloud_dir / "sort4-c1-current-recovery.py", "native_c4_snapshot")
    before = historical.snapshot(a, c1_tool)
    verifast1_before = sha(c1_tool / "src/verifast1.ml")
    require(verifast1_before == manifest.get("verifast1_sha256"),
            "fresh reviewed ZST repair model identity")
    tool = a.work_root / "sort4-native-c4-capture-isolated-source"
    require(not tool.exists(), "isolated capture tool preexists")
    shutil.copytree(c1_tool, tool, symlinks=True)
    require(historical.snapshot(a, tool) == before, "isolated tool copy")
    root = a.evidence / "native-c4-capture"
    for operation in ("check", "apply"):
        row = driver.stage(a, root, "patch-" + operation,
                           ["git", "-C", str(tool), "apply", *( ["--check"] if operation == "check" else []), str(patch)],
                           env, 60, cwd=tool)
        require(row.get("exit") == 0, "incremental patch " + operation)
    require(sha(tool / TR) == manifest.get("translator_sha256"), "patched translator hash")
    active = driver.clean_env(a, tool)
    row = driver.stage(a, root, "console-build",
                       ["make", "-C", str(tool / "src"), "../bin/verifast",
                        "WITHOUT_LABLGTK=yes", "VERBOSE=yes"], active, 600, cwd=tool)
    require(row.get("exit") == 0, "capture console build")
    after = historical.snapshot(a, tool)
    require(after["head"] == before["head"] and
            after["head"] == manifest["tool_head"] and
            sha(tool / "src/verifast1.ml") == verifast1_before and
            after["critical"][str(TR)] == manifest["translator_sha256"] and
            all(after["critical"][key] == value for key, value in before["critical"].items()
                if key != str(TR)) and
            all(after["modified_hashes"][key] == value
                for key, value in before["modified_hashes"].items()
                if key != str(TR)) and
            all(after[key] == before[key] for key in ("effective_rsspec", "proof_std", "modified_names")) and
            all(after["binaries"][key] == value for key, value in before["binaries"].items()
                if key != "bin/verifast"), "non-translator tool identity")
    driver.save(root / "effective-profile.json", {
        "manifest": manifest, "manifest_sha256": sha(manifest_path),
        "before": before, "after": after,
        "verifast1_sha256_before": verifast1_before,
        "verifast1_sha256_after": sha(tool / "src/verifast1.ml"),
        "proof_credit": False, "accepted": False})
    fixture = root / "fixture"
    certificate = make_source(a, driver, fixture)
    active.update({"SORT4_ACTUAL_AST_SCOPE_TEST": "0", "SORT4_STRICT_LFT_CUT": "1",
                   "SORT4_NATIVE_C4_CAPTURE": "0", "SORT4_NATIVE_C4_CAPTURE_SOURCE_SHA256": ""})
    stages, support = driver.source_support(a, tool, fixture, root, active,
                                             target="small_sort_general_with_scratch")
    require(support.get("paired_support_passed") is True,
            "normal/readonly MIR and refinement support")
    active.update({"SORT4_NATIVE_C4_CAPTURE": "1",
                   "SORT4_NATIVE_C4_CAPTURE_SOURCE_SHA256": certificate["verified_sha256"]})
    row = driver.stage(a, root, "capture-refusal",
                       [str(tool / "bin/verifast"), "-rustc_args", "--edition 2021",
                        "-verbose", "2", "verified/lib.rs"], active, 180, cwd=fixture)
    ast = fixture / "native-c4-capture-pre-ast.ml"
    raw = (root / "capture-refusal.log").read_text(errors="replace")
    classification = "NATIVE_C4_CAPTURE_INCONCLUSIVE_NOT_PROOF"
    if (row.get("exit") in (1, 2) and ast.is_file() and
            "NATIVE-C4-CAPTURE: FULL_ORIGINAL_AST_CAPTURED_NOT_PROOF" in raw and
            "Verifying function 'small_sort_general_with_scratch'" not in raw):
        classification = "NATIVE_C4_SOURCE_MIR_PREAST_CAPTURED_REFUSED_NOT_PROOF"
    if ast.is_file():
        shutil.copy2(ast, root / ast.name)
    result = {"classification": classification, "source": certificate,
              "support": support, "capture_exit": row.get("exit"),
              "pre_ast_sha256": sha(ast) if ast.is_file() else None,
              "tool": {"translator": sha(tool / TR),
                       "kernel": sha(tool / "src/verifast.ml"),
                       "verifast1": sha(tool / "src/verifast1.ml"),
                       "console": sha(tool / "bin/verifast"),
                       "head": after["head"]},
              "target_proof": "NOT_RUN", "profile_accepted": False,
              "actual_caller_proved": False}
    driver.save(root / "result.json", result)
    return result


def run_bound(a, c1_tool, env, driver):
    """Fresh, default-off exact-source candidate and its refusal controls."""
    require(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
            os.environ.get("LANE") == "o26-sort4-c1-current-recovery",
            "bound Cloud-only authorized lane")
    manifest_path = a.proof_root / HERE / "NATIVE-C4-BOUND-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    capture_manifest = json.loads((a.proof_root / HERE /
                                   "NATIVE-C4-CAPTURE-MANIFEST.json").read_text())
    capture_patch = a.proof_root / HERE / "native-c4-capture.patch"
    bound_patch = a.proof_root / HERE / "native-c4-bound.patch"
    require(manifest.get("mode") == "NATIVE_C4_BOUND_SOURCE_SPECIFIC_CANDIDATE" and
            manifest.get("profile_accepted") is False and
            manifest.get("tool_head") == capture_manifest.get("tool_head") and
            manifest.get("kernel_sha256") == KERNEL and
            manifest.get("verifast1_sha256") == capture_manifest.get("verifast1_sha256") and
            manifest.get("capture_translator_sha256") == capture_manifest.get("translator_sha256") and
            sha(capture_patch) == capture_manifest.get("patch_sha256") and
            sha(bound_patch) == manifest.get("bound_patch_sha256") and
            [line for line in bound_patch.read_text().splitlines()
             if line.startswith(("--- ", "+++ "))] ==
            [f"--- a/{TR}", f"+++ b/{TR}"],
            "bound manifest/patch admission")
    require(sha(c1_tool / TR) == BASE_TR and
            sha(c1_tool / "src/verifast.ml") == KERNEL and
            sha(c1_tool / "src/verifast1.ml") == manifest["verifast1_sha256"],
            "fresh C1 base tool")
    historical = driver.load(a.cloud_dir / "sort4-c1-current-recovery.py",
                             "native_c4_bound_snapshot")
    before = historical.snapshot(a, c1_tool)
    tool = a.work_root / "sort4-native-c4-bound-isolated-source"
    require(not tool.exists(), "bound isolated tool preexists")
    shutil.copytree(c1_tool, tool, symlinks=True)
    require(historical.snapshot(a, tool) == before, "bound tool copy")
    root = a.evidence / "native-c4-bound"
    for name, patch, expected in (
            ("capture", capture_patch, manifest["capture_translator_sha256"]),
            ("bound", bound_patch, manifest["bound_translator_sha256"])):
        for operation in ("check", "apply"):
            row = driver.stage(a, root, f"{name}-patch-{operation}",
                               ["git", "-C", str(tool), "apply",
                                *(["--check"] if operation == "check" else []),
                                str(patch)], env, 60, cwd=tool)
            require(row.get("exit") == 0, f"{name} patch {operation}")
        require(sha(tool / TR) == expected, f"{name} translator identity")
    active = driver.clean_env(a, tool)
    row = driver.stage(a, root, "console-build",
                       ["make", "-C", str(tool / "src"), "../bin/verifast",
                        "WITHOUT_LABLGTK=yes", "VERBOSE=yes"],
                       active, 600, cwd=tool)
    require(row.get("exit") == 0, "bound console build")
    after = historical.snapshot(a, tool)
    require(after["head"] == before["head"] == manifest["tool_head"] and
            after["critical"][str(TR)] == manifest["bound_translator_sha256"] and
            all(after["critical"][key] == value
                for key, value in before["critical"].items() if key != str(TR)) and
            all(after["modified_hashes"][key] == value
                for key, value in before["modified_hashes"].items()
                if key != str(TR)) and
            all(after[key] == before[key] for key in
                ("effective_rsspec", "proof_std", "modified_names")) and
            all(after["binaries"][key] == value
                for key, value in before["binaries"].items()
                if key != "bin/verifast") and
            sha(tool / "src/verifast.ml") == KERNEL and
            sha(tool / "src/verifast1.ml") == manifest["verifast1_sha256"],
            "bound tool non-translator profile identity")
    driver.save(root / "effective-profile.json", {
        "manifest": manifest, "manifest_sha256": sha(manifest_path),
        "before": before, "after": after, "proof_credit": False,
        "profile_accepted": False})
    fixture = root / "positive-fixture"
    certificate = make_source(a, driver, fixture)
    require(certificate["verified_sha256"] == manifest["verified_source_sha256"] and
            certificate["original_sha256"] == manifest["original_source_sha256"],
            "bound exact source pair")
    active.update({"SORT4_ACTUAL_AST_SCOPE_TEST": "0",
                   "SORT4_STRICT_LFT_CUT": "1", "SORT4_NATIVE_C4_CAPTURE": "0",
                   "SORT4_NATIVE_C4_CAPTURE_SOURCE_SHA256": "",
                   "SORT4_NATIVE_C4_BOUND": "0",
                   "SORT4_NATIVE_C4_BOUND_CONTROL": "none"})
    _, support = driver.source_support(a, tool, fixture, root, active,
                                       target="small_sort_general_with_scratch")
    require(support.get("paired_support_passed") is True and
            support["source_pair_sha256"] == {
                "verified/lib.rs": certificate["verified_sha256"],
                "original/lib.rs": certificate["original_sha256"]} and
            sha(fixture / "verified/lib.rs") == certificate["verified_sha256"] and
            sha(fixture / "original/lib.rs") == certificate["original_sha256"] and
            support["full_mir"]["normal"]["sha256"] ==
                manifest["normal_full_mir_sha256"] and
            support["full_mir"]["readonly"]["sha256"] ==
                manifest["readonly_full_mir_sha256"],
            "bound exact paired MIR/refinement gate")
    cases = [("positive", "none", "positive")]
    cases += [(f"c{i}-unwind-false", f"c{i}_unwind_false", "false")
              for i in (1, 2, 3, 4)]
    cases += [("normal-false", "normal_false", "false")]
    cases += [(name, "none", kind) for name, kind in
              (("source-refusal", "source"), ("extra-body", "extra"),
               ("malformed", "malformed"), ("mixed", "mixed"),
               ("default-off", "off"))]
    false_locations = {
        "normal-false": "verified/lib.rs(577,9-40): error: Assertion might not hold. (Cannot prove false.)",
        "c1-unwind-false": "verified/lib.rs(387,22-93): error: Assertion might not hold. (Cannot prove false.)",
        "c2-unwind-false": "verified/lib.rs(442,18-99): error: Assertion might not hold. (Cannot prove false.)",
        "c3-unwind-false": "verified/lib.rs(504,18-75): error: Assertion might not hold. (Cannot prove false.)",
        "c4-unwind-false": "verified/lib.rs(561,18-75): error: Assertion might not hold. (Cannot prove false.)",
    }
    refusal_reasons = {
        "source-refusal": "NATIVE-C4-BOUND: verified source SHA256 differs",
        "extra-body": "NATIVE-C4-BOUND: isolated exact-one body, unwind/full checks required",
        "malformed": "NATIVE-C4-BOUND: malformed opt-in",
        "mixed": "NATIVE-C4-BOUND: isolated exact-bound environment required",
    }
    results = {}
    source_bytes = (fixture / "verified/lib.rs").read_bytes()
    original_bytes = (fixture / "original/lib.rs").read_bytes()
    for name, control, kind in cases:
        case_root = root / "cases" / name
        case_fixture = case_root / "fixture"
        (case_fixture / "verified").mkdir(parents=True)
        (case_fixture / "original").mkdir()
        altered = source_bytes
        if kind == "source":
            altered += b"\n"
        if kind == "extra":
            altered += b"\nfn native_c4_extra_body() {}\n"
        (case_fixture / "verified/lib.rs").write_bytes(altered)
        (case_fixture / "original/lib.rs").write_bytes(original_bytes)
        case_env = dict(active)
        case_env["SORT4_NATIVE_C4_BOUND"] = "0" if kind == "off" else (
            "bad" if kind == "malformed" else "1")
        case_env["SORT4_NATIVE_C4_BOUND_CONTROL"] = control
        if kind == "mixed":
            case_env["SORT4_NATIVE_C4_CAPTURE"] = "1"
            case_env["SORT4_NATIVE_C4_CAPTURE_SOURCE_SHA256"] = certificate["verified_sha256"]
        row = driver.stage(a, case_root, "verification",
                           [str(tool / "bin/verifast"), "-rustc_args",
                            "--edition 2021", "-verbose", "4",
                            "verified/lib.rs"], case_env, 240, cwd=case_fixture)
        raw = (case_root / "verification.log").read_text(errors="replace")
        first_error = next((line for line in raw.splitlines()
                            if ": error:" in line or
                            line.startswith(("Fatal error:", "error:"))), None)
        admitted = (f"NATIVE-C4-BOUND admitted pre_ast={manifest['pre_transform_ast_sha256']}"
                    in raw)
        pre_ast = case_fixture / "native-c4-bound-pre-ast.ml"
        post_ast = case_fixture / "native-c4-bound-post-ast.ml"
        if pre_ast.is_file():
            shutil.copy2(pre_ast, case_root / pre_ast.name)
        if post_ast.is_file():
            shutil.copy2(post_ast, case_root / post_ast.name)
        source_immutable = (sha(case_fixture / "verified/lib.rs") ==
                            hashlib.sha256(altered).hexdigest() and
                            sha(case_fixture / "original/lib.rs") ==
                            certificate["original_sha256"])
        if kind == "positive":
            classification = ("NATIVE_C4_BOUND_VF0_CANDIDATE_RAW_REVIEW_REQUIRED"
                if row.get("exit") == 0 and admitted and source_immutable and
                   pre_ast.is_file() and post_ast.is_file() and
                   sha(pre_ast) == manifest["pre_transform_ast_sha256"]
                else "NATIVE_C4_BOUND_POSITIVE_INCONCLUSIVE")
        elif kind == "false":
            classification = ("INTENDED_FALSE_ASSERTION"
                if row.get("exit") in (1, 2) and admitted and
                   first_error == false_locations[name] and source_immutable and
                   pre_ast.is_file() and post_ast.is_file() and
                   sha(pre_ast) == manifest["pre_transform_ast_sha256"]
                else "FALSE_CONTROL_INCONCLUSIVE")
        elif kind in ("source", "extra", "malformed", "mixed"):
            classification = ("INTENDED_ADMISSION_REFUSAL"
                if row.get("exit") in (1, 2) and not admitted and
                   refusal_reasons[name] in raw and source_immutable and
                   not post_ast.is_file()
                else "ADMISSION_CONTROL_INCONCLUSIVE")
        else:
            classification = ("DEFAULT_OFF_NOT_ADMITTED"
                if not admitted and row.get("exit") != 0 and source_immutable and
                   not pre_ast.is_file() and not post_ast.is_file()
                else "DEFAULT_OFF_INCONCLUSIVE")
        results[name] = {
            "classification": classification, "verifier_exit": row.get("exit"),
            "first_error": first_error,
            "first_causal_stage": "verification" if row.get("exit") else "NONE_OBSERVED",
            "admitted": admitted, "control": control, "source_immutable": source_immutable,
            "source_sha256": sha(case_fixture / "verified/lib.rs"),
            "original_sha256": sha(case_fixture / "original/lib.rs"),
            "pre_ast_sha256": sha(pre_ast) if pre_ast.is_file() else None,
            "post_ast_sha256": sha(post_ast) if post_ast.is_file() else None,
            "verification_log_sha256": sha(case_root / "verification.log"),
            "proof_credit": False}
        driver.save(case_root / "case-result.json", results[name])
    result = {"classification": results["positive"]["classification"],
              "cases": results, "source": certificate, "support": support,
              "tool": {"translator": sha(tool / TR),
                       "kernel": sha(tool / "src/verifast.ml"),
                       "verifast1": sha(tool / "src/verifast1.ml"),
                       "console": sha(tool / "bin/verifast"),
                       "head": after["head"]},
              "target_proof": "RAW_REVIEW_REQUIRED",
              "actual_caller_proved": False, "callable_summary": False,
              "profile_accepted": False}
    driver.save(root / "result.json", result)
    return result
