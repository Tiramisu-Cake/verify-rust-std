#!/usr/bin/env python3
"""Synthetic source-marker placement and R9 recovery-environment checks."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
TOOL = Path("/root/verifast-merge-actual-glue/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")
VERIFIER = Path("/root/verifast-merge-actual-glue/src/verifast.ml")
TRACE = "SMALLSORT_R9_GUARD_TRACE"
RECOVERY = "SMALLSORT_R9_GUARD_RETURN_RECOVERY"
R9 = "experimental-merge-guard-current-return-r9-v1"
R10 = "experimental-merge-moving-gap-r10-v1"
R8 = "experimental-merge-owned-array-allocation-r8-v1"


def load():
    spec = importlib.util.spec_from_file_location("r9_marker_callback", HERE / "first-callback.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load first-callback.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    callback = load()
    old = SimpleNamespace(WRAPPER_SIGNATURE=b"pub unsafe fn wrapper(")
    anchor = b"        }\n    }\n}\n\npub unsafe fn wrapper("
    source = b"fn body() {\n" + anchor + b"\n}"
    r9 = callback._prepare_r9_guard_return_recovery(source, old)
    assert r9.count(callback.R9_GUARD_RETURN_MARKER) == 1
    assert callback.R9_GUARD_RETURN_MARKER in r9
    assert b"CopyOnDrop_drop_effect" not in callback.R9_GUARD_RETURN_MARKER
    assert b"assume" not in callback.R9_GUARD_RETURN_MARKER
    assert b"leak" not in callback.R9_GUARD_RETURN_MARKER
    assert b"open [1/4]array::<u64>(r9_guard_ref, 1, ?r9_drop_current)" in r9
    assert b"open [1/4]array::<u64>(r9_guard_ref + 1, 0, nil)" in r9
    rejoin = (
        b"assert *tail |-> ?r9_tail_current;",
        b"close array::<u64>(tail + 1, 0, nil);",
        b"close array::<u64>(tail, 1, cons(r9_tail_current, nil));",
        b"open array::<u64>(begin + 1, 1, _);",
        b"assert *(begin + 1) |-> ?r15_middle_current;",
        b"close array::<u64>(begin + 1, 2, cons(r15_middle_current, cons(r9_tail_current, nil)));",
        b"open array::<u64>(begin, 1, _);",
        b"assert *begin |-> ?r15_first_current;",
        b"close array::<u64>(begin, 3, cons(r15_first_current, cons(r15_middle_current, cons(r9_tail_current, nil))));",
        b"assert array::<u64>(begin, 3, ?r9_current_values);",
        b"r9_current_u64_owners(t, r9_current_values);",
    )
    positions = [callback.R9_GUARD_RETURN_MARKER.index(command) for command in rejoin]
    assert positions == sorted(positions)
    lemma = callback.R9_CURRENT_U64_OWNERS_LEMMA
    assert r9.count(lemma) == 1
    assert r9.index(lemma) < r9.index(old.WRAPPER_SIGNATURE)
    for required in (b"lem r9_drop_u64_owners", b"req foreach(vs, own::<u64>(t));",
                     b"ens true;", b"open foreach(vs, own::<u64>(t));",
                     b"open own::<u64>(t)(v);", b"open u64_own(t, v);",
                     b"r9_drop_u64_owners(t, rest);", b"lem r9_make_u64_owners",
                     b"req true;", b"close u64_own(t, v);",
                     b"close own::<u64>(t)(v);",
                     b"close foreach(vs, own::<u64>(t));",
                     b"lem r9_current_u64_owners",
                     b"req foreach(?r9_previous, own::<u64>(t));",
                     b"ens foreach(vs, own::<u64>(t));",
                     b"r9_drop_u64_owners(t, r9_previous);",
                     b"r9_make_u64_owners(t, vs);"):
        assert required in lemma
    assert b"assume" not in lemma and b"leak" not in lemma

    for bad_source in (
            source.replace(b"pub unsafe fn wrapper(", b"pub unsafe fn other(", 1),
            source.replace(anchor, anchor + callback.R9_GUARD_RETURN_MARKER, 1)):
        try:
            callback._prepare_r9_guard_return_recovery(bad_source, old)
        except ValueError:
            pass
        else:
            raise AssertionError("wrong wrapper anchor or duplicate R9 marker was accepted")

    case = {}
    def capture(_case, _args, env):
        case.update(env)
        return {"stage": 0}

    parent = {"KEEP": "yes", TRACE: "stale", RECOVERY: "stale"}
    for profile in (R9, R10):
        case.clear()
        callback._execute_case_with_r9_trace(
            capture, object(), object(), parent, profile=profile,
            prefix=False, actual_callback_case=True)
        assert case[TRACE] == "1" and case[RECOVERY] == "1"
    assert parent == {"KEEP": "yes", TRACE: "stale", RECOVERY: "stale"}
    for profile, prefix in ((R9, True), (R8, False), ("baseline", False)):
        case.clear()
        callback._execute_case_with_r9_trace(
            capture, object(), object(), parent, profile=profile,
            prefix=prefix, actual_callback_case=True)
        assert TRACE not in case and RECOVERY not in case

    translator = TOOL.read_text()
    assert 'SMALLSORT_R9_GUARD_RETURN_RECOVERY" = Some "1"' in translator
    assert "R9 guard-return marker contains a command outside the checked recovery whitelist" in translator
    assert "R9 guard-return recovery target body is missing its checked source marker" in translator
    returning_start = translator.index('Ast.SwitchStmtClause (loc, call "returning"')
    unwinding_start = translator.index('Ast.SwitchStmtClause (loc, call "unwinding"', returning_start)
    drop_end = translator.index('Ok ([ghost "close_points_to" [address]', unwinding_start)
    returning = translator[returning_start:unwinding_start]
    unwinding = translator[unwinding_start:drop_end]
    assert "r9_guard_return_commands" in returning
    assert "r9_array_u64_close" in translator
    assert "r9_array_u64_join" in translator
    assert "r9_current_owners_call" in translator
    assert "Ast.PureStmt (plan.r9_guard_return_loc" in returning
    assert "Ast.BlockStmt (plan.r9_guard_return_loc" in returning
    assert "r9_guard_return_commands" not in unwinding
    assert "r9_guard_return_edges" in returning
    verifier = VERIFIER.read_text()
    pure_rule = verifier[verifier.index("| PureStmt (l, s) ->"):verifier.index("| GotoStmt (l, lbl)")]
    assert "verify_stmt (pn,ilist) blocks_done lblenv tparams boxes true" in pure_rule
    print("R9 source-marker placement, R9-only environment, checked returning-edge dispatch synthetic checks PASS")


if __name__ == "__main__":
    main()
