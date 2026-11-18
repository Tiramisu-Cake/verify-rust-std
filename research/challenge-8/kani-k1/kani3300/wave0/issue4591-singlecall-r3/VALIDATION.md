# Offline validation

Run `python3 -B validate.py /root/kani-issue4591-singlecall-r3-w15` from this
package. tests/VALIDATION.json records the actual result. It covers source
pins/parent/tree/clean status; exact two-file repair; unchanged compiler,
workflows, actions, scripts, libraries, toolchain and dependencies; patch seals
and recorded replays; all declared controls and PFC harnesses; semantic golden
inventory; both failed baseline shapes and repaired shapes; guard and source
arithmetic oracles; source mutations; connected job accounting; and mock final
publication metadata gates. Three actual isolated-index patch replays are in
PATCH-REPLAY.json, with argv, exits and resulting trees.

The actual source repair passes git diff --check. The staged package passes
the same check with literal .patch artifacts excluded: their required blank
context lines contain a space, which Git reports as trailing whitespace when
the patches themselves are added as text files. Patch bytes and hashes are
preserved for exact replay.

The bounded call model in tests/callshape.py follows local source calls,
ordinary body source and explicit Check/Replace/Assert/Original selection for
these fixtures. It reports branching/recursion/explicit overlap as outside its
straight-line scope. The affected two harnesses and providers are straight
line. Both frozen baselines yield exact target reachability and two effective
checks; both repairs yield one. Missing selected calls, duplicate selected calls
and alias-only calls are discriminated. Removing direct0 alone keeps one check
but loses exact selected-provider reachability. This closes the gap in the
old lexical direct-call test, whose historical PASS stays unchanged.

The boolean guard model is a sequential projection of the retained configured
CBMC source excerpt: completed=false permits the first check, completion sets
it true, the next check fails. It is not a native verifier. The arithmetic
oracle accepts only identity/x+literal bodies and equality posts parsed from
these source fixtures; it checks all16 admitted positive u8 inputs and the
source negative input1. Provider postcondition and mode mutations remove the
intended negative failure while preserving the caller post. The issue's i32MAX
caller-addition overflow remains a source arithmetic counterexample.

PFC-AUDIT.json revisits all13 PFC harnesses. All38 original harnesses remain;
all36 unaffected harness definitions and existing functions are unchanged. All
expected descriptions and harness totals remain unchanged; no property quota
is introduced. The model's source string checks and arithmetic assumptions
are explicit; Rust name resolution, typechecking, generated MIR/closure
identity and runtime/native proof still require CI.

check_push_head.py is read-only. Its metadata tests reject changed trees,
oldmain or merge parents, extra/missing ancestors, skip directives anywhere in
main..final and a skipped candidate in range. A valid metadata mock grants no
authority. Actual invocations against the local skipped candidate and old6f
reject; tests/ACTUAL-GATE-REJECTIONS.json retains argv/exits/results. An actual
new nonskip final head has not been created or tested.

No compiler, Cargo, rustc, rustfmt, expansion, Kani, CBMC, verifier, full runner,
CI, rerun/cancel, push, PR, issue/comment, raw-log/archive, GCS, ledger,
reservation or budget operation occurred. Python/Git source checks do not
establish a native PASS, AST/MIR binding or formal proof credit.
