# M2-B/S3 coordinator-only request — prepared, no dispatch

Candidate `58497d98d085a5144a70c358205c0e46318feeb6`, tree `56df2bc406106d3950f0543a4e53482e2d1ab2a4` in local
/root/kani-fix-3300-m2b-seed, branch fix/kani-3300-contract-immutable-mask.
Based on exact5f7 and documentation-only handoff d2500db20b; Kani NOT pushed. Worker Cloud $0.
Use existing authorized Quick/probe transport, normal limits and one root/compiler/solver at a time;
this request does not authorize worker CI, new lanes, workflow edits or full Quick/heavy PFC.

1. Build/fmt/clippy preflight FIRST. Record each exit/stage; setup error means solver NOT_RUN.
2. Unchanged M2-A C03 legal_ordinary_transfer, default Assert; then C04 no-assert diagnostic and C05/C06
   undecorated companions. New tests/expected/uninit/contract-immutable-masks/ordinary-singleton.rs
   is byte-identical to C03 and must also satisfy its regression oracle (SUCCESS). Keep array3 and
   body/ensures/root checks. Do not weaken or remove a failure/property to obtain acceptance.
3. Retain target MIR/GOTO snippets: graph now follows emitted registration body into selected closure;
   `_16=assume_init` normal-return edge must have the existing typed SetRef(true) before C03:30;
   `*out=value` must have its existing normal post-write setter before ensures. Confirm no setters on
   unwind/abort paths or premature payload-read bypass. Runtime bind selected object/range/shadow
   history of BOTH operands; numeric IDs can change. Value50:2 from old run is not a new selector.
4. New ensures-left-hole.rs and ensures-right-hole.rs: ordinary Assert modes, no PFC substitution.
   Require the designated raw_eq operand initialization read to FAIL and the lawful all-Some operand
   to SUCCEED, with no earlier UB/Unsupported/frame/extra failure. Retain valid flat MU references,
   original Some/None masks and first payload read in ensures. Generic failure alone is insufficient.
5. Reuse ALL unchanged m2bs/CI-REQUEST.md section B controls: both D0 legal harnesses, six
   promoted-allocations selectors, four immutable-masks selectors, five registry unit controls,
   original M2 false-transfer/postcondition/out-pointer/normal-abort oracles. Keep false source
   propagation and mutable overwrite/reset controls. Resource-unqualified PFC stays separately held;
   do not call a cutoff PASS or replace it by ordinary Assert to close that gate.
6. Separate exact mixed composition remains required: ALL16 fixture files at composition
   83ceadf0485f30548c92b77c87b3c08a53f0b019, tree15d3d3ecb5d353da3ae1c51567d9b0d04cc9f5fb,
   fixed C1-T2-A7f9eec41e8. Verify prior manifest hashes, materialize test-only on candidate, record
   independent composition SHA/tree. No partial repair-only cherry-pick or production6134 import.

No change to immutable admission, reset-only seed rule, raw None masks, ABI/DFCC/transfer/retarget
model or trusted premises. Stack normal-return instrumentation is restored by relevance, not by
seeding/reseeding it as immutable storage. Out setter absence is static in old MIR; its actual
execution and resulting ensures success remain unverified, since old witness stops at body equality.

Receipt must identify source/candidate/composition/toolchain/sysroot/CBMC/target/layout/recipe,
actual argv/env (nonsecret), root/mode, all stage exits/signals, every property status including extra
failures/Unsupported/unreachable checks, both operands and Some/None masks, epoch and final setter,
elapsed/RSS units/actual limits/sampling/overshoot. Reuse timeout300s and CBMC RSS>6GiB watchdog;
compiler/preparation limits remain enforced too. Cutoff INCOMPLETE, no retries outside owner budget.

## Explicit unresolved generalization boundary

The alias analyzer recursively follows regular calls without a cycle/fixpoint guard. This candidate
can expose contract-clause cycles formerly hidden by raw registration panic bodies. Reviewer found
none in C03 or these controls; general contracts are not accepted. A bounded non-solving control is:
function f returns a byte without recursion in its body; its ensures invokes helper h; h calls f.
Runtime clause depth selects Original for that call, but static raw-body overapproximation can cycle.
Run only with existing compiler timeout/memory enforcement and only under coordinator authorization;
record noncompletion/diagnostic separately. No silent visited-node cutoff or assumed alias summary is
approved. If hit, stop general acceptance and request a separate scoped cycle-safe analysis design.

After targeted semantic gates, M2-B/R resource qualification is STILL independent; original PFC and
full unchanged Quick/final gates remain HELD until authorized. M3 HELD. No independent B1/B2 credit.
