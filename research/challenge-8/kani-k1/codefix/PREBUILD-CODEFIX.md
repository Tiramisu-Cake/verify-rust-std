# CODEFIX v8: exact packet for coordinator review

Status: READY after the coordinator's requested doc correction; no build dispatched.
Slot `k1-network` is occupied by VALIDVAL. Wait for explicit coordinator GO before dispatch.
Previous packet `3c8dcf8bd1d4b68a9c7144dd3fe8f74111b54196` was accepted with this one correction.

- Worktree: `/root/verify-rust-std-kani-codefix`.
- Branch: `experiment/kani-k1-codefix-20261104`; stable owner `k1-network`; slug `codefix`.
- Task: `6844af7ac0`; library candidate: `56efe5c477ded5bc06a975f6a843822d09100894`.
- Library v7 comparison: `e470652790`; tooling base: `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`.
- Upstream: `233f96f66a`; Kani `cd355b0b`; nightly `2026-10-22`.
- Request: `codefix-v8-20261104-02`; stage `codefix-v8-prebuild`.

## Changes 1–7

1. ZST comparator doc describes the observed pointer-check failures without assigning a cause.
2. N >= 9 network harness doc says order only; suffix permutation is checked separately.
3. `verify.rs`, `wrap.rs` and `merge/specfix.rs` distinguish geometry from initialization and
   permissions supplied by constructed fixtures; predicates and contract code are unchanged.
4. Module opening records the two current-pin trait-contract limitations with links to
   model-checking/kani issues #5116 and #4908 and reproduction on pinned cd355b0b.
   No Actions run ids in std source. Helper profiles fix one comparator; no blanket limitation
   on free generic functions. This correction is a separate library-only [skip ci] commit
   above original library candidate `41f11f397dbd9579989b6d7c4ea5119b11adec6c`.
5. Ordinary `network::swap_same_position_u8`: real helper, identical positions, arbitrary u8,
   nondeterministic comparator, full-byte assertion, two branch covers; no swap profile.
6. Ordinary `network::unstable_freeze_noncopy_bytes86_fallback_n2`: transparent `[u8; 86]` wrapper,
   const size/stack-budget assertions, FreezeMarker type bound and negative CopyMarker type check
   (ambiguity on CopyMarker, which also excludes Copy via its blanket impl). Real Unstable entry,
   N2, volatile reads, all 86 bytes of both output elements checked, three covers.
7. Both module-level dead_code allowances removed. No confirmed orphan remained to delete.
   All five ArbitraryValue impl families are used: u8 by dispatch/StrictU8; u64 by StrictU64;
   arrays by dispatch/KeyB16/KeyB17; DropValue by dispatch/DropU8; Cell<i32> by CellI32.
   PFC and macro dependencies retained; both cfg configurations examined statically.

## Static validation

- `codefix/check_codefix.py`: PASS, 202 -> 204 ordinary; cfg-on 210 -> 212, same eight controls.
- All previous 210 root bodies and attributes match v7 tokens, ignoring comments/whitespace.
- All retained helper tokens match v7; no removed helper or static orphan in either cfg mode.
- Library diff against `e470652790` stays in `smallsort/verify*`; runtime/tooling unchanged.
- Verify source lines: 3065 -> 3147. All lines <= 100; `git diff --check`: PASS.
- rustfmt --check, edition/style 2024 with `codefix/rustfmt.toml`: PASS.
  Binary wrapper: `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`.
- Original packet validation (tooling unchanged):
  `python3 -B -m unittest discover -s research/challenge-8/kani-k1/tools
  -p test_kani_k1.py`: 71 tests, OK.
- Static comparison, line-width and rustfmt checks repeated after doc correction: PASS.
- Updated request validation: PASS. Lane paths compare byte-identically with `59893bff1f` locally.
  Build-bound `k1g.sh check-tooling BUILD 59893bff1fbb2af1a0c08862afd7e3bb87c19cdd` awaits a build identity.
- Source checks are not compiler inventory or proof results. Compilation/warnings with cfg off/on
  will be checked by inventory and verification, respectively, in the single authorized build.

## Proposed build and acceptance

`RUN-REQUEST.json`: diagnostic, inventory=true (cfg off), controls=true (verification cfg on),
gcb-e2-standard-4, jobs=1. Exactly two new SUCCESS roots plus the existing mutant FAILED control.
The control expects `assertion failed`, the pinned core assert placeholder; inspect its failed
checks and reject unrelated failures when reporting the result.

Request watchdog is 15 minutes per harness, 45 harness-minutes plus 30 overhead = 75 minutes,
reserve $1.0125 at $0.0135/min. This also gives the cfg-off full-std inventory preparation room
(the existing runner documents ~49 minutes; its time is charged against the build window).
The acceptance bound for each new harness remains <= 60 seconds; any larger observed time must
be reported as failing that bound, with no extension. All five new covers must be satisfied.
Project budget observed 2026-11-04T19:31:43.864566+00:00: used $93.8895, reserved $0, cap $118.96;
own spent $0, cap $1.50. Recheck before dispatch; one compile/warning repair only within own cap.

After GO: dispatch this exact pushed packet, record BUILD, run `k1g.sh watch BUILD`, end turn.
After wakeup: bounded summary/rows, inventory identity/count/delta, tooling identity, warnings via
`k1g.sh log-grep BUILD 'warning|smallsort/verify' 200` and targeted bounded context if needed;
then actual own cost and RESULT-CODEFIX.md <= 35 lines. Do not infer proof from source checks.
