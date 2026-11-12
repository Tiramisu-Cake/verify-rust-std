# KANI3300 R0 — Inventory raw_eq guard admission paths

**Stage:** W1-R0, planning only; runtime Codex. Source clone is read-only at
`/root/kani-fix-3300-a1`, pinned `a0a2386001a15fecfe2facc2f6cd87f3dee13b60`. Compare base
`bf9c58e662fd65c64381ef2ac97a6397ffc0693a` and R1
`1cd96e354ec45346b61c245554a50a8af8cb5ce7` with R2. Audit:
`research/challenge-8/kani-k1/AUDIT-REPORT-KANI3300-PART1-R2-RU.md` at `124a45e373`.
Accepted planning response:
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/PLANNER-AUDIT2-RESPONSE.md`.
Destination: `research/challenge-8/kani-k1/kani3300/r0/`.

**Decision boundary:** inventory admission paths and design a guard only. Stop for owner
choice between (A) direct-MU export with flat-slot operations rejected, or (B) preserving
flat-slot support while release remains blocked on the `raw_eq` provenance/state model. Do not
choose, implement, or imply acceptance of either policy.

## Context and objective

R2 expands `raw_eq` checks to the full byte extent, including padding, using `CheckAs<[u8;
size]>`; it also admits bytewise shadow-state copy/update on `[MaybeUninit<T>; N]` and
slices of slots. Restoring older `raw_eq` behavior alone can expose reads of uninitialized
flat-slot storage. The audit establishes static risk and reports ordinary array-equality
failures, but does not establish MIR/runtime causality. The accepted planning response
requires a complete inventory before proposing a narrow guard.

Produce an evidence-backed inventory and guard design for both owner options. Find where
each form first becomes supported, how it lowers to shadow operations, and which shortcuts
may bypass a guard. Record unknowns. Type/layout evidence does not establish runtime
object identity, provenance, causal ordering, or proof acceptance.

## Read-only scope

- Inspect only the pinned source tree and specified g0 planning materials; cite source
  file/line locations or commit paths.
- Trace shared `Copy` and `SetSliceChunk` dispatch; typed assignment,
  aggregate/repeat/conversion, argument/return transfer, checks, and `SetRef` shortcuts.
- Distinguish `MaybeUninit<[T; N]>` (wrapper around an array) from `[MaybeUninit<T>; N]`
  (flat slots) and `[MaybeUninit<T>]`.
- Cover nonzero and zero extents, ZST inner `T`, local/global storage, aliases/offsets,
  and cross-call transfers. Mark unestablished handling unknown.
- Compare base, R1, R2, and proposed policy as source-level behavior.

Do not write in the source clone, change branches, fetch, compile, run
Cargo/rustc/Kani/CBMC/Miri, or execute tests. Fork GitHub Actions CI is available, but do
not run it; only the coordinator submits CI. No Cloud dispatch; budget is $0. No Kani
source commit/push, other edits, or nested delegation. Research is static evidence/proposal.
Mentioned MIR/runtime checks are proposed controls marked **NOT_RUN**, never results.

## Required inventory

Create `NOTES.md` (≤60 lines), preferably a Markdown table. Each row
records MIR/input shape; visitor/classifier and `MemoryInitOp`; layout/dispatch; direct MU
vs flat-slot admission (or unclear); zero/nonzero behavior; local/global, alias/offset and
call-boundary status; and evidence. Cover:

1. Typed `Copy`/`Move`, raw-pointer projected assignment, union/storage cases,
   `Aggregate(Array)`, union aggregate, `Repeat`, and typed `Cast(Transmute)` both
   directions.
2. `CopyNonOverlapping` statement and copy/volatile-copy intrinsic routes;
   `WriteBytes`/volatile-set `SetSliceChunk`; other byte writes affecting the range.
   Follow each through shared check-uninit dispatch.
3. `BeginArgumentTransfer`, `StoreArgument`, `LoadArgument`, return slot, move-source
   `SetRef(false)`, unpaired/unresolved calls and protocol guard. Distinguish pointer
   check/set from shadow transfer.
4. Delayed/check paths (`Check`, `CheckRef`, `CheckAs`, slice checks), generic
   `SetRef(true/false)` early returns, and layout classification. State whether each
   admits, skips, or may bypass a diagnostic; include empty-entry, terminator-only, and
   last-instruction placement risks.
5. Shape/extent distinctions for `MaybeUninit<[T; N]>`, `[MaybeUninit<T>; N]`, and
   `[MaybeUninit<T>]`; N>0/N=0, ZST inner `T`, zero-byte extent. Describe rustc
   stride/layout only as source supports it, never as runtime provenance.

Separate base, R1, and R2 support columns. Proposed guard coverage has its own column and
uses `proposed`, `unknown`, or `not applicable`, not PASS/verified. Identify indirect
admission through shared dispatch so a guard in one syntactic visitor arm is not mistaken
for complete coverage.

## Guard design

Add `GUARD-DESIGN.md` (≤35 lines): describe the earliest common recognition boundary or
boundaries that reject unsupported flat-slot effects before shadow transfer/check
instrumentation. Trace the proposed diagnostic to an emitted safety property; address
empty entry, terminator-only, and last-instruction retention plus check/SetRef shortcuts.
No type-only raw_eq provenance rule; no claim that a body-local coexistence guard
suffices.

Compare both options, without selecting either:

- **A — direct MU only:** preserve `MaybeUninit<T>` and `MaybeUninit<[T; N]>` typed-mask
  behavior and legacy array equality. Design complete flat-slot rejection across
  assignment, aggregate/repeat/conversion, `Copy`/`SetSliceChunk`, and arg/return routes.
  List lost flat-array/slice support, compatibility risks, and positive/negative controls.
  Do not reject direct MU array payloads accidentally.
- **B — retain flat support:** keep release blocked until a raw_eq provenance/init-state model
  covers identity, extent, aliases/offsets, writes/overwrites, local/global storage, and
  cross-call effects. State required model/evidence and why type-only or body-local
  coexistence checks cannot establish it. Do not design/implement the model here.

Specify fallback for unknown shapes/layouts, zero extent, unresolved aliases/calls, and
any path lacking a guaranteed diagnostic. No silent skip or optimistic initialized mask;
no guard based solely on raw_eq appearing in the same body.

## Proposed controls (all NOT_RUN)

Create `RESULT-KANI3300-R0.md` (≤15 lines): summarize inventory, both options,
uncertainty, and owner decision needed. Include a compact control matrix with expected
properties for: legal direct `MaybeUninit<[T; N]>` typed transfer; flat-slot raw copy with
unwritten byte; flat zero/nonzero extents; local/global and alias/offset; cross-call
arg/return; guard positive/negative; ordinary array equality regression; and matched
base/R1/R2 cases. Mark every control **NOT_RUN** and state expected property (Unsupported
diagnostic, uninitialized-byte failure, or legal equality success). No claims of
execution, lowering, MIR binding, or causality.

## Completion and stop

Write only `NOTES.md`, `GUARD-DESIGN.md`, and `RESULT-KANI3300-R0.md` under
`kani3300/r0/`. Keep evidence and unknowns explicit. Make no scope choice or guard
implementation. After preparing the design, commit and push to g0 without further
permission. Use `[skip ci]`; set author and committer via `git -c` to
`Tiramisu-Cake <igkharin@gmail.com>`. Stage only this task’s `kani3300/r0/` paths.
On concurrent g0 updates or non-fast-forward, hand off to the coordinator; no reset,
stash, or force. No third-party PR links.

Return exact final line `READY <sha>`, where `<sha>` is the resulting g0 research commit.
READY means prepared for owner review, not proof acceptance.

Это верификация корректности, не security-работа.
