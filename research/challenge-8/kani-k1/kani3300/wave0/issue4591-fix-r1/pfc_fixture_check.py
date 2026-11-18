#!/usr/bin/env python3
"""Narrow lexical regression for these fixtures, not Rust parsing or MIR proof."""

import re


POSITIVE = "tests/kani/FunctionContracts/ordinary_stub.rs"
NEGATIVE = "tests/expected/function-contract/ordinary_stub_fail.rs"


def functions(text):
    # Fixture grammar: line comments, attributes and balanced function braces.
    # This deliberately does not claim to parse arbitrary Rust or resolve DefIds.
    text = re.sub(r"//[^\n]*", "", text)
    result = {}
    for match in re.finditer(r"^((?:#\[kani::[^\n]+\]\n)*)fn (\w+)[^\n{]*\{", text, re.M):
        start = match.end()
        depth = 1
        end = start
        while depth and end < len(text):
            depth += (text[end] == "{") - (text[end] == "}")
            end += 1
        if depth:
            raise AssertionError("unbalanced fixture function")
        result[match[2]] = (match[1].splitlines(), re.sub(r"\s+", "", text[start:end - 1]))
    return result


def inspect(texts):
    selected = []
    for path, text in texts.items():
        for name, (attrs, body) in functions(text).items():
            for attr in attrs:
                match = re.fullmatch(r"#\[kani::proof_for_contract\((\w+)\)\]", attr)
                if match:
                    target = match[1]
                    # A lexical direct call in this very harness is mandatory.
                    if not re.search(r"(?<![\w:])" + re.escape(target) + r"\(", body):
                        raise AssertionError(f"{path}:{name}: exact selected-target call missing")
                    selected.append({"path": path, "harness": name, "target": target,
                                     "assurance": "LEXICAL_DIRECT_CALL_ONLY_NOT_MIR"})
    pos = functions(texts[POSITIVE])
    neg = functions(texts[NEGATIVE])
    # Require unconditional standalone calls, in order. Comments/dead branches,
    # calls in another harness and removal of the copied call cannot pass.
    assert pos["replacement_contract_target"] == (
        ["#[kani::proof_for_contract(contracted_replacement)]",
         "#[kani::stub(f, contracted_replacement)]"],
        "contracted_replacement(0);f(kani::any());")
    assert neg["replacement_provider_postcondition"] == (
        ["#[kani::proof_for_contract(discriminating_replacement)]",
         "#[kani::stub(f, discriminating_replacement)]"],
        "discriminating_replacement(0);f(1);")
    assert neg["discriminating_replacement"] == (
        ["#[kani::ensures(|result| *result == 0)]"], "x")
    assert pos["contracted_replacement"] == (
        ["#[kani::requires(x < 16)]", "#[kani::ensures(|result| *result == x + 3)]"],
        "x+3")
    # Source arithmetic, checked only after pinning the exact fixture expressions.
    assert 0 == 0 and 1 != 0  # identity provider: direct PASS, copied FAILURE
    assert 0 < 16 and all(x + 3 <= 255 for x in range(16))
    return selected


def regression_checks(texts, frozen):
    selected = inspect(texts)
    checks = ["per_harness_selected_target_lexical_calls", "positive_direct_and_copied_calls",
              "negative_direct_pass_copied_failure", "provider_exact_identity_and_zero_postcondition"]
    for path, name, old, new in [
        (POSITIVE, "positive_missing_direct", "    contracted_replacement(0);\n", ""),
        (NEGATIVE, "negative_missing_direct", "    discriminating_replacement(0);\n", ""),
        (NEGATIVE, "comment_only_direct", "    discriminating_replacement(0);", "    // discriminating_replacement(0);"),
        (NEGATIVE, "dead_direct", "    discriminating_replacement(0);", "    if false { discriminating_replacement(0); }"),
        (NEGATIVE, "direct_also_fails", "    discriminating_replacement(0);", "    discriminating_replacement(1);"),
        (NEGATIVE, "copied_also_passes", "    f(1);", "    f(0);"),
        (NEGATIVE, "missing_copied", "    f(1);", ""),
        (NEGATIVE, "postcondition_weakened", "#[kani::ensures(|result| *result == 0)]", "#[kani::ensures(|result| *result == x)]"),
    ]:
        assert texts[path].count(old) == 1, name
        mutated = dict(texts)
        mutated[path] = texts[path].replace(old, new)
        try:
            inspect(mutated)
        except AssertionError:
            checks.append("reject:" + name)
        else:
            raise AssertionError("accepted mutation: " + name)
    for path in (POSITIVE, NEGATIVE):
        mutated = dict(texts)
        mutated[path] = frozen[path]
        try:
            inspect(mutated)
        except AssertionError:
            checks.append("reject:frozen_unreachable:" + path)
        else:
            raise AssertionError("accepted original W11-01 fixture")
    mutated = dict(texts)
    mutated[NEGATIVE] = texts[NEGATIVE].replace("    discriminating_replacement(0);\n", "") + (
        "\n#[kani::proof]\nfn other_harness() { discriminating_replacement(0); }\n")
    try:
        inspect(mutated)
    except AssertionError:
        checks.append("reject:direct_in_different_harness")
    else:
        raise AssertionError("cross-harness reachability credit")
    # All pre-existing functions/attributes/bodies outside the two repaired
    # harnesses remain unchanged, including bad_contract and safety controls.
    for path, original in frozen.items():
        current = functions(texts[path])
        for name, value in functions(original).items():
            if name not in ("replacement_contract_target", "replacement_provider_postcondition"):
                assert current[name] == value, (path, name)
        allowed = {"discriminating_replacement"} if path == NEGATIVE else set()
        assert set(current) - set(functions(original)) == allowed
    checks.append("all_other_fixture_functions_and_attributes_preserved")
    return {"status": "STATIC_AND_MUTATION_PASS", "checks": checks,
            "selected_targets": selected,
            "negative_model": {"body": "x", "postcondition": "result == 0",
                               "direct_input": 0, "direct_return": 0, "direct_expected": "PASS",
                               "copied_input": 1, "copied_return": 1, "copied_expected": "FAILURE"},
            "assurance": "Restricted lexical fixture guard and Python arithmetic only; exact FnDef reachability, MIR, compilation and native semantics NOT_RUN"}
