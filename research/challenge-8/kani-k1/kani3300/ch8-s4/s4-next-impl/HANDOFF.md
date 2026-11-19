# HANDOFF — S4 next offline implementation

Stage complete: **READY_FOR_EXACT_PACKAGE_REVIEW**. Final Validate is
**PREPARED_NOT_RUN**, execution count0. Stop at this HANDOFF. This implements
plan `c0de8471801ac22b38e3290c7a6b75742135af6b` under every constraint of independent plan-only APPROVE
`762a2a678eb624d1ddd18f0764a365e7787392c0`. It grants no exact-package approval, GO, execution,
qualification, provider admission or proof credit.

Exact local commits (source/control authored and committed as Tiramisu-Cake
<igkharin@gmail.com>, both with `[skip ci]`):

- Std `7b31b060b90ce286e94547993f6a698c549bc5fa`, tree `fccf3284bd678626c8f8cea72bbe6ec72964dbd9`;
  sole parent `8faf8e62af8f82b5c46af020086f8df591b6757e`.
  Worktree `/root/verify-rust-std-ch8-s4-next-w15`, branch
  `experiment/ch8-s4-next-source-w15`.
- Control `65a9ea656a4b5f1e66f7b31eceffb5eefeba7541`, tree `09938d27a127351f5c51b6c9f451602d797a1c0f`;
  sole parent `3d3fb715271e3b195c6e0eee3557d5b0a6aad00d`.
  Worktree `/root/kani-ch8-s4-next-control-w15`, branch
  `experiment/ch8-s4-next-control-w15`.
- Stock tool unchanged `0aac16ef62da9e9d5645782d458593e5d78143ba`, tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`.
- G0 task origin `0a9b091f2112391e16ea2086b50c6afd7f5c80ef`. The request pins task-containing snapshot
  `778418b5a6c59e9b649435fd4bbc7a61ae0cd2ec`; its CURRENT-TASK blob is identical to the origin.
  Unrelated coordinator commits advanced G0 concurrently and were left intact.
  The containing final package commit seals MANIFEST.json and is reported
  externally to avoid self-reference.

Request SHA256 `693e12689bfee859560d5042a36fd8b80051e9fca4082fd1a612642d7e389e30`;
workflow SHA256 `fc21d9f44a403b6294daaca2b25fdfcebe38d3dd7e89a927af0d289a86c177a0`. PINS.json and DEPENDENCIES.json bind
exact identities, plan/review/task blobs and173 payload-file hashes. The source,
control and tool worktrees are clean. No publication occurred.

Std changes only the new `sorting_s4_full_lengths_next.rs` and four-line cfg
registration. The actual network calls use literal [1..9], [1..10], [1..14],
[1..18], respectively. All34 independent initialized full-u8 bytes, V34/base1,
Original/null, original comparator and callee, active u8/span/pair guard, owned
snapshot/full sortedness and multiplicity oracle, full34-index frame and
arbitrary outside canary remain. Four SUCCESS roles and six covers per positive
are source-bound:16 assertion sites,24 covers. DOMAIN-EQUIVALENCE.md provides
the finite specification correspondence and explains the static witness limits.

The four existing negatives remain byte-identical and first, including Cell
active SUCCESS and exact intended count failure. Production kernels, models,
contracts and old harnesses are unchanged. Shared runner/check_package/collect
edits are dispatch only: inverse removal reproduces parent bytes exactly.
Campaign is an exact namespace copy; native acceptance and role-matching ASTs
are unchanged. ZERO_U/REJECT_ALL and safety/unwind/unsupported-guard/role/SAT/
location/source-stage/target checks remain strict. No old producer ID, accepted
unreachable site, missing-location exclusion or strict0 rejection is promoted.

Offline checks on the exact final control:

- 23 new synthetic tests PASS (14.223s wrapper elapsed), covering
  each call/pre/post length, unrestricted bytes, full frame/canary, guard, callee,
  unwind and roles/covers; request/identity/U/guard mutations; timeout, signal,
  partial, missing, null, wrong-type, NOT_RUN and source-stage/target mismatch;
  original exit/exception and protected snapshots remain preserved.
- 30 retained synthetic tests PASS (20.659s): eight S4P2 routing tests
  plus all22 network-r2 regressions under immutable old fixtures.
- Existing source preflight PASS uncached (50.659s), including all four
  source maps,64 cfg projections,32 legacy contexts and8 ACTIVE contexts.
  Existing control gate PASS with local Git and a synthetic CI environment only.
- Four parent/stock patches replay to exact source/control trees. Local shallow
  clones PASS at source7/control9/tool2, retaining both sole parents and historical
  stock bases. One extra ancestry generation requires7/9 for this new profile;
  old r2 profile/fixtures keep6/8. All old files/tests are preserved. Python AST,
  request/map parsing and parent-diff whitespace checks PASS; no Rust tool ran.

All366 old tests remain selected; with23 new tests the prepared final Validate
contains389. `FINAL-VALIDATE-PREPARED.json` freezes command, cwd, exact control/
request/workflow pins,1080-second deadline and margin>=1.5 (elapsed<=720s).
**Do not run it in this stage.** Final elapsed/margin remain unmeasured. Targeted
or historical timings do not substitute for this gate. A later authorized
execution must bind these exact bytes and satisfy both tests and margin.

N17 does not reach merge: it sorts the13-element prefix and shifts tails13..16
before returning. N9/N13 retain zero-body shift entry plumbing; N8 is insertion
only. Unwind36 is unchanged on positives/Cell,34 on the first three negatives;
all flags/caps remain unchanged, including child600 with compile<=180, slot720,
local6GiB/outer12GiB/reserve2GiB and campaign6900. The6180 envelope/720 reserve
is arithmetic only. Native600-second fit, lowered loop sufficiency, native
inventory/covers and strict peak-memory assurance remain UNKNOWN. Source bounds
in LOOP-COST.json confer no lowered or generic proof credit.

PRECURSORS.json preserves the rejected missing-crate binding candidate and the
incorrect offline test selector run; neither is relabelled as final evidence.
The binding fix retains strict validation, and correcting the offline selector
made no final control delta. `freeze_request-precursor.stdout` retains the
pre-correction request hash; final identities are only those in PINS.json.

REVIEW-CONSTRAINTS.md maps all six review findings to this candidate.
Read-only final packet check:
`PYTHONDONTWRITEBYTECODE=1 python3 research/challenge-8/kani-k1/kani3300/ch8-s4/s4-next-impl/check_packet.py`.
No compiler/Cargo/rustc/rustfmt/Kani/CBMC/native tool, push, CI, raw-evidence,
ledger/coordinator/phase or subagent operation was performed by this task.
New qualified cases0; independent proof obligations closed0; proof credit NONE.
Exact-package review, final Validate execution, publication and native execution
are separate future stages. Generic/MIR/type/init/ownership/Drop/caller/provider,
remaining finite lengths and independent B1/B2 remain OPEN.
