# Challenge 8 experiment log

This is evidence, not authorization. Read [STATUS.md](STATUS.md) for current
stop/resume state and phase; use [the runbook](AGENT-RUNBOOK.md) for procedures.

Append future experiment cards/results under "New records", without deleting
older results. Include actual-source obligation, hypothesis, domain/full target
posts, profile/pins, expected positive/negative failure locations, source SHA,
run URL/selection/budget, observed outcome/checks/cost and next decision.
Record partial diagnostics and unexecuted stages explicitly.

## New records

### 2026-10-06 — documentation/rules checkpoint, experiments still paused

Based on stopped source checkpoint
`126e23d35c26bb336ca5e975f0ec696ef1fa88d0`. No proof source, tool patch, workflow,
or preserved draft changed. No new Actions run or proof claim.

Latest experiment remains failed minimal-profile run
[37441463201](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37441463201)
at `d198907e7eec57f8bcd880304fa1345b97b0ef53`; see the full result at the end of
the historical snapshot below. `recover_single` blocks all callers; the
ManuallyDrop positive separately hits unsupported RawPtr refinement. Existing
baseline result37437514808 and completed cleanup caller gate37435525052 remain
valid within their recorded domains/tool profiles.

The owner approved documentation rules, not resumption. Current instructions
now enforce phase-limited autonomy, a frozen semantic tool boundary, predeclared
experiment decisions, isolated controls, full normal/unwind recovery and an
explicit actual-source applicability gate. Historical instructions are superseded.

## Historical README snapshot — through 2026-10-06

The remainder is the complete, unedited README from
`126e23d35c26bb336ca5e975f0ec696ef1fa88d0`. Old "next", "resumed", "pending" and
dispatch instructions are historical, not current commands. Some statuses were
superseded by later entries; consult STATUS/coverage for consolidated claims.
This preserves scope, source/run SHAs, measured costs, failures and diagnostics.

---

# Challenge 8 research

We are developing our own solution. Existing PRs are references for requirements,
review feedback and performance observations; their proof code is not imported.

For agent onboarding and autonomous GitHub-only execution, read
[AGENTS.md](../../AGENTS.md) and [the agent runbook](AGENT-RUNBOOK.md).
The owner's server is for editing and orchestration only; do not build or verify there.

**Resumed at the owner's request — 2026-10-06.** Read
[the consolidated handoff](HANDOFF-2026-10-06.md) for what is proved, what is
unfinished, the current regression bug and places requiring a fresh view.
The historical stopped status in that handoff is superseded by the current
runbook; the owner authorized autonomous push/dispatch/inspection again.

Read [the revised plan](REASSESSMENT-2026-10-06.md) for the fresh source/evidence
review and continuation criteria. Complete the all-path resource ledger and
trust-boundary review before expanding the verifier. No new proof result or
Actions run was produced by this documentation checkpoint.

After resumption, the [all-path resource ledger](INSERTION-RESOURCE-LEDGER.md)
records desired full normal/unwind posts, actual MIR cleanup ordering and each
experimental verifier boundary. The complete local-cleanup diagnostic passed
in37435525052, including both callers and all negative controls. Full generic
insertion remains open; next isolate baseline genuine share/recovery on normal
return while keeping full direct-panic recovery as a separate architecture gate.

Potential independent VeriFast contributions are tracked in
[the upstream-candidates note](VERIFAST-UPSTREAM-CANDIDATES.md), including
the general address-taking bugfix and the less mature frontend/kernel extensions.

## Target and scope

- Target: the standard library in this repository, not a reimplementation.
- Requirements: `doc/src/challenges/0008-smallsort.md`; discussion: upstream issue #56.
- Initial upstream commit: `dd2bbad51eb50fdf9730e14802dcaf8a9290092a`.
- Kani is pinned by `tool_config/kani-version.toml`, initially
  `152c6a8c875d9886a67e229247b4826d6105ccfd`.
- Runtime code in the standard library must not change.

## First experiment

`smoke.rs` contains two original proof harnesses for the actual `swap_if_less`:

1. For arbitrary four-element `i32` arrays, comparing positions 1 and 2 with `<`
   produces an ordered pair, preserves the exact values and leaves both neighbours unchanged.
2. For either symbolic comparator decision, those same positions preserve the
   exact values and leave both neighbours unchanged. This does not assert sortedness
   for an invalid comparator.

There are no input assumptions, behavioral stubs or copied sorting algorithms.
Reachability covers exercise less-than, equality, greater-than and both swap decisions.
These are bootstrap checks for a fixed allocation and two fixed positions. They
do not establish generic type/index coverage, comparator panic safety, uninitialized
memory safety, or the full Challenge 8 contracts. Kani's default enabled checks
apply; we do not claim that these cover every UB required by the challenge.

## Insertion experiment (bounded stages verified)

See [the specification and scope](insertion-contract.md).

- `insertion_contracts_4`: first verify the contract on a proof-only i32 adapter
  calling the actual std `insert_tail`; then check a three-insertion caller using
  `stub_verified`. Stages stop at the first failure.
- `insertion_direct_4`: check the actual `insertion_sort_shift_left`, with symbolic
  length 1..4 and offset 1..length, assuming only the necessary sorted prefix
  for the functional-correctness property.
- `insertion_all_4`: run all three stages in the above order.

All values are arbitrary i32, including duplicates and extremes. The experiment
checks ordering, exact multiset preservation and the untouched suffix. It uses
bounded loop unwinding (6), not loop invariants. The adapter contract is not a
contract on generic std `insert_tail`, and the summary-based caller is not std's
outer pointer loop. A passing result will establish only this small compositional
experiment; general types, arbitrary lengths and unwind safety remain future work.

## Run

Agents dispatch and inspect each run autonomously using `gh` and the runbook.
After the resource/architecture review, resumption and the nested-match fix,
the first hosted diagnostic selection is
`verifast_local_drop_caller_gate`,budget90min, on
`challenge-8/research`. Its experimental `tuple_local_drop` source build adds
restricted reuse of an annotated same-unit Drop contract for bare-local compiler
cleanup. It retains all eight HRTB, twelve lifetime-scope and five reference
fixtures and the [actual generic destructor body gate](verifast-drop-gate.md),
which passed37419989766. One-cell raw-pointer callers check exact destination
values and one logical ownership sequence on normal and callback-unwind exits.
Negative fixtures check required permissions, element ownership, actual-body
postconditions and the restricted frontend boundary. See
[the translator boundary](verifast-local-drop-call.md).
Held-reference release, the actual insertion loop and the complete insertion
contract remain open; raw-pointer caller fixtures do not prove those obligations.

The earlier insertion profiles preserve their exact-source diagnostic probes.
See [the scope cut](verifast-end-lft-binding.md),
[address traversal](verifast-address-taken.md) and
[held-reference patch](verifast-manually-drop-ref.md).
Other profiles retain their pinned release tools.
The existing `all`, `orders_i32_pair` and
`preserves_i32_values_for_any_decision` choices still run the original bootstrap.

The workflow definition must exist on the default branch for GitHub to expose
the manual trigger. Its dispatch branch is the source being verified.
After a source fix, start a new **Run workflow** on the updated branch. **Re-run
jobs** on an older run checks that run's original commit and will not pick up the fix.

Agents dispatch and monitor this workflow themselves using the commands in
[AGENT-RUNBOOK.md](AGENT-RUNBOOK.md). Do not execute the research runners,
Kani scripts, compilation or executable tests on the owner's server.

Use a disposable checkout: each runner appends only its cfg(kani) proof module to
`smallsort.rs` at execution time. It refuses to append twice. Kani's repository
script builds the pinned verifier and installs its dependencies; that cold build
counts toward the time budget. The initial cache retains Cargo downloads only,
not a complete verifier installation.

Every run records the source commit, source checksums, runner information, Kani
pin, complete verification log, exit status and GNU time resource statistics.
The appended source is included in the artifact so the checked input is reviewable.

Success requires every requested harness to verify and every reachability cover
to be satisfied. A timeout, build error or absence of harnesses is not a proof.
### Run log

- **Baseline generic normal borrow recovery passed:** [37437514808](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37437514808),
  source `2a16b2421e81590e91025bf8b662e96be0660369`, recovery90min,
  pinned release26.09/nightly2026-02-05/no experimental patches. Full evidence
  inspected: all5readonly exporter/decode/refinement0, exact ghost-strip/source
  hashes unchanged after each tool. i32 and unrestricted generic T callers VF0
  with full current cells/T.own; actual ordinary nonghost-only helper body proves
  at same source version. Each case caller/helper header1, body18, explicit call1.
  All3 negative VF1 diagnostics match missing token/debt at helper precondition
  and false caller post after recovery; each refinement0 with same body/call
  counts. VF.08s per case, refinement.04s (.05generic/missingdebt); runner16.35s,
  RSS637,208KiB, release setup dominates. No source build/covers/loop bounds.
  This establishes normal genuine sharing/recovery for two owned generic cells,
  without FnMut panic, temporary storage or insertion. Next actual ManuallyDrop
  normal lifecycle control, keeping the complete first/late panic obligations.

- **Baseline recovery declaration diagnostic:** [37437183634](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37437183634),
  source `f9a7159c3e3320726cbb0b286ea9d233b1e4c0c8`, baseline recovery90min,
  release26.09/nightly2026-02-05/no experimental patches. Full evidence inspected:
  all5export/decode/refinement0, source unchanged after every tool. VF1 for all5
  before any helper/caller body: wrapper precision fails on imprecise close-token
  predicate. All body/header/call counts0; all3 negative classifications reject
  this unrelated failure. No recovery/negative proof claimed. VF.10s (.11s
  generic), refinement.05s (.06s generic); runner17.65s,RSS640,548KiB, release
  setup dominates. No source build/covers/loop bounds. Correct the debt wrapper's
  invalid precise declaration, preserve all conjuncts/posts, then NEW baseline run.

- **Complete local-cleanup diagnostic passed:** [37435525052](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37435525052),
  source `51dcf65b10a5c0d8ee4f39a17086d8493be8dcfb`, localcaller90min,
  derived26.09/nightly2026-02-05, unchanged resource contracts/domain/std.
  Full evidence inspected; all source-byte/ghost-strip/MIR/patch-output/four-file/
  tool/prelude/pairedZ3 audits pass. Binary
  3fe106494bd73803b4800410f6a0b50399b51233303b0d6b32659b3e62b1d141;
  build0/33.51s,RSS426,896KiB. All25 controls pass1.71/2.27/1.33s with compiler/
  decode0; eight HRTB controls still expect ownership failures. Direct actual
  Drop and both cleanup callers VF0, same-unit checked body named1/copy1/5copy
  statements. Both caller named1, normal/unwind exact destination and ONE
  ownership posts/leak pass; VF.13s each, refinement0/.09/.10s. Callback call1,
  localDrop6 log records; MIR retains normal/cleanup Drop nodes and UnwindResume.
  All7 negatives reject as intended: missing source/destination/ownership,
  unannotated generic Drop, false actual method post, extra field and Copy-bound
  shape; VF.13s for five body/resource cases, .08s for two frontend cases.
  Negative refinement is intentionally unexecuted (sentinel99). Overall0,
  runner1:41.25,RSS626,048KiB; setup dominates. No covers/loop bounds. This
  completes the one-element local-cleanup gate, without establishing insertion,
  generic sharing or temporary-storage recovery. Next baseline explicit normal
  recovery control; the proposed auto-lemma route is statically invalid because
  lifetime APIs require nonghost-only callers, forbidden for auto-lemmas.

- **Callback declaration fixed; projection-name frontend failure:** [37434307481](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37434307481),
  source `36c60b38f1653b1e749a19d2a1869f22a3a8cb1b`, localcaller90min,
  same derived26.09/nightly2026-02-05/contracts/domain/checks. Full evidence
  inspected; source/patch-output/four-file/tool/prelude/pairedZ3 audits pass.
  Build0/18.93s,RSS426,800KiB; binary
  4d6767809510f3a9ea65d0ad006d3d33d5d43a292e63cb8e5aae857b1a12ad8b.
  All25 controls pass1.75/2.31/1.35s with compiler/decode0. Direct actualDrop
  and cleanup_one VF/refinement0 (.13/.10s each); named1/copy1/5copy records,
  exact destination and ONE ownership post/leak pass. cleanup_callback
  compiler/decode0, VF2/.14s before caller statements: missing runtime pure
  function `core::ops::FnOnce::Output_typeid`. Refinement0/.10s. All7 negatives
  not reached; overall1,runner1:25.95,RSS646,476KiB, setup dominates. No covers/
  loop bounds. Full normal/unwind callback cleanup and insertion remain open.
  Next canonicalize projection-predicate trait names using the translator's
  existing alias-type rule and rerun the whole gate on a new pushed SHA.

- **Normal local Drop caller verified; callback declaration failure:** [37433028854](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37433028854),
  source `46021223da019526f4ad67f6e3921fc60d2c434f`, localcaller90min,
  same derived26.09/nightly2026-02-05/contract/domain/checks. Full evidence
  inspected; strict source/tool/prelude/pairedZ3/patch/four-file and source-byte/
  MIR audits pass. Build0/18.63s,RSS426,676KiB, binary
  6328c230d1859d97a0634626672e7a9b06dcd33d8dfd6b21fdc23cfe6e64e8b4.
  All25 regressions pass1.71/2.28/1.35s, all compiler/decode0; direct actual
  Drop named1/copy1/5copy records,VF/refinement0 with same d7a090ed contract.
  cleanup_one compiler/decode/VF/refinement0, caller/actualDrop named1 each,
  exact destination and ONE ownership post/leak check pass; VF.13s,refiner.09s.
  This proves the raw-source normal caller under its explicit resource contract.
  cleanup_callback compiler/decode0, VF1/.13s before caller statements:
  `A local variable whose address is taken must be declared at the start of a block.`
  Refinement0/.10s; all7 negatives not reached. Overall1,runner1:30.31,
  RSS648,144KiB; setup dominates. No covers/loop bounds. Full panic cleanup,
  held-reference/storage recovery and insertion remain open. Next diagnose
  reconstructed CFG declaration placement and preserve all checks.

- **Nested-match repaired; caller dead-code diagnostic:** [37431775757](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37431775757),
  source `197d5a1efdaa1d42e7a69df1a811dbe3ba82648d`, localcaller90min,
  derived VeriFast26.09/nightly2026-02-05, unchanged contracts/domains/checks.
  Full logs/artifacts inspected. Strict source/tool/prelude/pairedZ3/patch-output/
  four-file audits pass; build0/19.00s,RSS426,608KiB, binary
  4b56ad0190f36fc8af4da8eb038207d12bff547bbc714368621ffbb8cfcde1d9.
  All25 regressions pass (8HRTB/12scope/5refs,1.75/2.34/1.36s), every compiler/
  decoder0. Actual directDrop named1/copy1, exact source/ghost/MIR audits and
  VF0/.13s/refinement0/.10s pass. First cleanup_one caller export/decode0,
  same-unit actualDrop named1/copy1/5copy statements, caller named1; VF1/.13s
  after post/free-locals/leak trace reports `verified/lib.rs(38,1-49,2): dead code`.
  No `error:` line; refinement0/.09s. Remaining8 fixtures not reached.
  Overall1,runner1:23.62,RSS626,532KiB; setup dominates. No covers or bounded
  unwind settings in this deductive gate; full caller cleanup is not yet proved.
  Next inspect reachability/CFG bookkeeping and preserve all checks.

- **Local Drop build passes; regression exposes nested-match bug:** [37423762729](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37423762729),
  source `b3da9a5ef53b8001e63ce511ba27ae8efce67343`, local_drop_caller_gate90min.
  Full logs/artifacts inspected. Same pins/four-file/pairedZ3 audits pass.
  Console build0/19.14s,RSS426,676KiB; binary
  b603f7f3ac0963892f88dad3bdafe446707ce04e845b3054c7b087a1480a184e.
  First2/8 HRTB cases have intended finite rejections; third hrtb_no_output
  export/decode0 then VF2: local_drop_call outer type match fails on generic F.
  All3 visited compiler/decode0; suite1/.69s,RSS85,400KiB. Remaining regressions,
  actualDrop/body/callers/refinement not executed. Overall1,runner1:15.12,
  RSS646,784KiB,setupdominates. Compiler Warning11 and source confirm nested
  substs match captures the intended outer fallback; explicit begin/end is the
  next source fix. Owner requested stop; no active run and no further dispatch.

- **Local Drop gate source-build diagnostic:** [37423344712](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37423344712),
  source `3a020357cfe5cb6e01eaaf1ef3575dd0abeea00b`, local_drop_caller_gate90min.
  Full logs/artifacts inspected. Same26.09 source/tool/prelude/dependency/decoder
  pins and exact4-source-file audit pass; patchf8f259e9 applies on f8751fab and
  yields910a2b79. Console build2/12.73s,RSS426,848KiB: translator7740 cannot
  resolve item.def_id without an explicit D.trait_impl_item annotation.
  No regressions, extraction, compiler MIR, derived runtime/Z3 audit, actual
  destructor/caller proof or refinement executed. Overall2,runner1:07.68,
  RSS646,360KiB,allsetup. Prepared record-type-only fix, patchbc13ff90,
  translator03bf4a5c; unchanged contracts/domain/source and mandatory checks.
  Next NEW hosted localcaller gate at the corrected source SHA.

- **Generic actual destructor body verified:** [37419989766](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37419989766),
  source `19e74b59f9f2235c26b208cc3c9a96149e3d6cb5`, copy_on_drop_gate90min.
  Full logs/artifacts inspected. Same26.09 source/tool/prelude/pairedZ3/4-file
  pins and exact364byte source/ghost/hash/MIR audits pass. Build0/27.85s,
  RSS426,932KiB; binary380b990b68b1adf1ec37f5221ee8b1db6d2cf622af435489b1fd57bdf873a410.
  All8HRTB guards0/1.73s,12scope cases0/2.30s and5references0/1.37s pass,
  everycompiler/decode0. ActualDrop compilerexport/decode0, onebody/onecopy.
  Compatibility safety_proof opens ORIGINAL private own=False; afterward ACTUAL
  Drop body enters separately, one exact named target and one copy call at32
  with5execution records. Exact destination values and ONE foreach(T.own)
  normalpost, functiontoken cleanup and leakcheck pass. VF0/.14s,RSS85,732KiB;
  refiner0/.10s,RSS84,508KiB;0errors/45total statements INCLUDE generatedsupport,
  not45callee statements. ContractSHAd7a090ed7ee9611434d889d7aa84f9e99d4987d9bd33889625c83c985a961e7f.
  Originalcrate e9b48887; verifiedcrate793e2fc6; genericT/arbitraryvalidlen,
  fractional initializedsrc/fullinitializeddst, no Copy/Freeze/nonZST restriction.
  Overall0,runner1:29.65,RSS646,180KiB,setupdominates. No active run.
  Directmethod contract is proved; compiler-generated cleanup reuse, heldref
  release on normal/panic, loop invariants and fullinsertion remain open.
  Next restricted same-unit annotatedDrop lowering with checked exactADT/generic/
  impl/field identity, normal/unwind CFG and ordinary storage accounting. Sol
  and Astra reviewed architecture; require caller source/dst/ONE Town resources,
  never synthesize own, erase tokens or treat defaultown=False as body evidence.
  See verifast-drop-diagnostic.md for acceptance and heldref release ordering.

- **Drop compatibility before body verification:** [37419467454](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37419467454),
  source `e119de8ca9f53685d673f012e1d024e35df14181`, copy_on_drop_gate90min.
  Full logs/artifacts inspected. Same source/tool/pairedZ3/originalprelude/4-file
  pins and ghost-byte/hash audit pass. Build0/16.44s,RSS426,804KiB; binary
  380b990b68b1adf1ec37f5221ee8b1db6d2cf622af435489b1fd57bdf873a410.
  All8HRTB0/1.35s,12scope0/1.79s and5reference0/1.09s pass. ExactDrop compiler
  export/decode0, one body defPath/one copy call, source hash roundtrip pass.
  Refinement0/.07s,RSS84,360KiB. VF1/.10s,RSS85,728KiB BEFORE substantivebody:
  function prototype implementation check cannot supply explicit type_interp<T>.
  NamedactualDrop0/copyexecution0; generated support lemma records are not a
  callee proof. Overall1,runner1:19.97,RSS586,840KiB,setupdominates. No active run.
  Prepared explicit safety_proof opens generatedfullBorrow and its ORIGINAL
  private own=False to discharge unreachable defaultcaller; concrete req/ens
  and mandatory actualbody/copy-line checking unchanged. No assume/new own or
  resource removal. Root reviewed delta and staticAST/diff pass. Next NEW hosted
  gate source; a successful compatibility check alone is insufficient.

- **Destructor gate MIR counter correction:** [37419199218](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37419199218),
  source `16aa63f8e05e3b38b9e10b5bfa8030cb04149421`, copy_on_drop_gate90min.
  Full logs/artifacts inspected. Same pinned26.09 source and4-source-file audit,
  pairedZ3/exporter/refiner/originalprelude pass. Build0/18.89s,RSS426,292KiB;
  binary380b990b68b1adf1ec37f5221ee8b1db6d2cf622af435489b1fd57bdf873a410.
  All8HRTB0/1.71s,12scope0/2.32s and5reference0/1.35s pass; compiler/decode0
  for every fixture. Exact364byte genericDrop extraction/ghost-strip/hash audits
  pass, contractSHAf98226d6bed50c546c9299823727c5cf8b20cbcb8550f71f29126a1bd206c203.
  ActualDrop compilerexport/decode0 and original/verified/std hash roundtrip pass.
  MIR has one body defPath plus one trait item defId referencing the same method;
  runner's bare name grep incorrectly counts2 and stops. No actualDrop verifier
  or refinement executed; no callee proof. Overall1,runner1:21.00,RSS647,204KiB,
  setupdominates. No active run. Prepared narrow counter correction: count exact
  body defPath, not trait item defId; unchanged contract/source/tools/domain.
  Next push and dispatch NEW copy_on_drop_gate90min; inspect actual method proof.

- **Held reference and actual first shift:** [37417173472](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37417173472),
  source `3eb19991b1d8c2312d9feae535b02068335f5162`, manually_drop_ref90min.
  Full logs/artifacts inspected. Same26.09/tool/prelude pins, pairedZ3,
  exact4sourcefiles, ghost-byte/sourcehash/compilerMIR audits pass. Patch5500204a
  on translator15a9 yields f8751fab; consolebuild0/18.86s,RSS426,436KiB;
  binaryc76b4255ec5d5d55c011dc2dede8f4e862f80fef7a342980acb23c5c7398161f.
  All8HRTB guards0/1.73s and12scope cases0/2.31s pass. All5trackedreference
  fixtures pass0/1.37s: scalar exact7 (18records), ManuallyDrop exact7 (30records),
  and three intended negative missingprecreate/init/readpermission errors;
  everycompiler/decode0. Actual unrestrictedT/F,n>=2: firstFnMutBool/synthetic
  unwind and strictcut/recovery pass; tail.read147, heldref148-149, actualguard
  creation150, firstcopy_nonoverlapping156 and dst=sift157 pass. On sift==begin159
  path compiler cleanup169 needs opaque CopyOnDrop.own at std/lib.rsspec567.
  Secondcomparison165, furtherloop/cleanup/restoredrange/fullfunction remain
  unproved; initialfalse-comparison return not claimed checked. Named2 includes
  errorcontext duplicate,248execution/return records. VF1/.25s,RSS92,704KiB;
  refiner0/.15s,RSS91,704KiB;overall1,runner1:22.47,RSS642,920KiB,setupdominates.
  No active run. Next exact-source destructor/restoration gating experiment and
  sound guard ownership route; method contract alone must not be treated as
  replacement for generic compiler drop_in_place summary. Sol investigates.
  Runtime std hash/domain unchanged; no T/F restriction or assumed own bridge.

- [Address-taking traversal and reference initialization](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37415731049),
  source `17e96da0c56bd51c587c6023bbedf72bec588583`,address_taken90min.
  Same26.09 pins/pairedZ3/ghost-byte/sourcehash/MIR audit and exact4sourcefiles
  pass. Patch2c44ad1c builds0/18.79s,RSS426,804KiB; binary
  1e59705130b70b0b934a980702de1148f5e5b7c265638b449f184b871710740d.
  All8HRTB guards0/1.71s and12scope cases0/2.30s pass. Scalar address-after-
  merge fixture verifies0,onebody18records. ManuallyDrop compiler/decode0;
  address succeeds, then reborrow_ref requires ref_initialized<i32>(tmp_addr).
  Suite1/.77s; finalnegativecase/actualtarget/refiner not reached. named2
  includes errorcontext, not two proofs. Overall1,runner1:20.05,RSS625,540KiB,
  setupdominates. Next sound reference-initialization proof/translation route,
  preserving actual Rust and all checks; no manual wrapper ownership bridge.

- [Actual full-token recovery, restored cells and tail read](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37414755368),
  source `dc0a359d94f0a79fe41f400d79571199690aca7d`,lft_cut90min.
  Independently reviewed outermetadata rebase patchbd95733e; same26.09,
  prelude/exporter/refiner pins, pairedZ3/ghost-byte/sourcehash/MIR audits pass.
  Build0/19.17s,RSS426,624KiB; binary
  d26c815ef4c2d6fe27b4a0580daa52fc4708083b1d581f057b8b46a7621e24e9.
  All8HRTB guards0/1.78s and12scope cases0/2.31s, compiler/decode0 each.
  ActualfirstFnMut bool and syntheticunwind post/leakcheck pass. Normal
  accessclosure134-137, strictcut140, fulltoken141, endLife142, bothborrowEnd/
  fullcontent openings143-146, tail.read/ManuallyDropnew147 pass. New failure
  CopyOnDrop.src &*tmp148: address of this expression unsupported.
  Guard/loop/restoredrange/fullfunction and actualfalse-comparison-return
  remain unproved. VF1/.21s,RSS92,716KiB;refiner0/.15s,RSS91,820KiB;
  overall1,runner1:20.89,RSS626,948KiB,setupdominates. Next inspect realMIR
  and representation-faithful ManuallyDrop dereference/address translation.

- [Strict exit chunk diagnostic](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37413756431),
  source `6209eb7dc5dc306a7fef09a17b84f61051aa2bac`,lft_cut90min.
  Diagnostic patche17492b5 builds0/22.55s,RSS426,536KiB; same pinned26.09
  prelude/exporter/refiner, pairedZ3/sourcehash/actualMIR audits pass; binary
  81e4dbe4d20801252505a4bf6e56686cc333b3aad5419ff1c3d76321f75eea15.
  All8HRTB guards pass0/1.48s and12scope cases0/1.89s, compiler/decode0 each.
  First actual FnMut unwind rejects points_to<F> (bound metadata only):
  outerF metadata retains the local HRTB equality containing cmp. VF1/.16s,
  RSS92,716KiB;refiner0/.12s,RSS91,828KiB;overall1,runner1:22.12,
  RSS643,832KiB,setupdominates. Normalcut/move not reached.
  Next independently reviewed rebase of outerparameter bounds to entrycontext
  on strict exit, conserving heap and rejecting genuinely local typed resources.

- [All lifetime-scope regressions and actual unwind rejection](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37413224006),
  source `5181cb3c003954d3adbf824aef71d8c141bfa835`,lft_cut90min.
  Same pinned26.09 source/patch76c3f6db/prelude/exporter/refiner, pairedZ3,
  ghost-byte/sourcehash/actualMIR audits pass. Build0/13.99s,RSS426,784KiB,
  binary e1037db742e3b038796a0fe92d2b6606cb208d24c72315c6088a77061028a571.
  All8HRTB guards pass0/1.13s; all12scope cases pass0/1.55s, two positive
  proofs and ten intended failures, compiler/decode0 each. Actual first FnMut
  preconditions/bool pass; synthetic unwind return125 rejects a live chunk
  parameterized by local lifetime at strict scope end140. Exit post/normalcut/
  fulltoken/recoveredcells/move remain unproved. VF1/.15s,RSS92,708KiB;
  refiner0/.10s,RSS91,816KiB;overall1,runner1:10.88,RSS658,248KiB,setupdominates.
  Next identify offending predicate/typeargs and check local cleanup versus
  actual escaping resources, preserving rejection and unrestricted T/F domain.

- [Scope regressions after successful source build](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37412915463),
  source `81f235e8856fde9208f387bb0b9ec9b6b1492abf`,lft_cut90min.
  Patch76c3f6db builds0/26.80s,RSS426,932KiB; binary
  e1037db742e3b038796a0fe92d2b6606cb208d24c72315c6088a77061028a571.
  Pins/pairedZ3/sourcehash/actualMIR audits pass. All8HRTB guards pass0/1.76s.
  Two positive scope proofs and seven intended negative cases pass; every
  attempted fixture compiler/decode0. Case10 fails No such function: payload
  before borrowing: fixture declared a predicate rather than a constructor.
  Final two cases and actual insertion VF/refiner not reached. Scope suite1,
  1.97s; overall1,runner1:30.14,RSS641,168KiB,setupdominated. Next correct
  precise constructor/application in fixture and rerun unchanged patch/domain.

- [Strict binding source-build attempt](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37412281007),
  source `7b349f115e75ebcd030bb0788f0e8184b42fc112`,lft_cut90min.
  Rawkernel/translatorprecedingpatch and three-modified-file pins pass;
  originalsource/ghost audit0. OCaml scoped_ids bb infers debug_info from
  duplicateidlabel and cannotfindchildrenfield; sourceconsole2/12.19s,
  RSS426,180KiB. No compiler MIR/regression/actualVF/refiner execution.
  Overall2,runner1:16.46,RSS644,292KiB,allsetup. Next explicitbasicblock
  type annotations in new helpers; semantic cut checks/domain unchanged.

- [HRTB guards and actual borrow-access closure](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37410979109),
  source `3184c40f4a00745712bdce4a28ccdc76f352562c`,fnmut_hrtb90min.
  Sourcebuild0/15.42s; pinnedparser/HRTBtracepatch/prelude/exporter/refiner,
  pairedZ3 and source/MIRhash audits pass. All8matcher cases pass0/1.49s:
  each compiler/decode0,real/translatedcallcounts agree,expected ownership1,
  registrations correct forbool/u8/noOutput/wrongF/wrongT/unequalLfts/
  secondunannotatedcall/bodyisolation. These are translator tests, notcalleeproofs.
  Actual comparator bool/unwind exit pass. Both normal initialization access
  closures and merge/half-token assert pass; firstfailure end_lifetime at140
  needsfull lifetime_token(cmp_k), still halfreserveduntilunsafe-blockexit.
  VF1/.17s,RSS92,728KiB;refiner0/.12s,RSS91,696KiB;overall1,
  runner1:04.76,RSS646,280KiB,setupdominates. No move/guard/loop/fullrange
  proof/covers. Next reviewed strict early ghost binding cut with negative
  resource/token/escape/CFG regressions, preserving runtimecode andreproducer.

- [Isolated HRTB regression cases](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37410552459),
  source `905fd9d0b3fa84a187b932c47bbad5bbe52402bc`,fnmut_hrtb90min.
  Sourcebuild0/25.76s; pairedZ3/originaltargetMIR/sourcehash pass. Boolean/u8
  cases pass (compiler/decode0,one real MIR+translatedcall each,VFownership1,
  registrations1/0). Unconstrained case has zero projection predicates;
  overly broad runner search mistakes a local FnOnce::Output alias for one,
  stops before case3 VF. Suite1/incomplete,noactualtargetVF/refiner.
  Overall1,runner1:24.32,RSS646,648KiB,setupdominates. Next guard checks
  projectionTerm records, keeping all eight semantic cases and strict checks.

- [HRTB regression setup](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37410021241),
  source `ca6ed8d91a0d369ad76a20a519a3cb053f2bd0cf`,fnmut_hrtb90min.
  Trace-only addition to tested HRTB semantics builds0/14.88s; pairedZ3 and
  original target MIR capture/sourcehash pass. Positive fixture exporter0,
  decoder0,one real call; VeriFast then parses inactive cfg ghost req and
  fails before call translation. Regression suite correctly fails1; no case
  pass,actual insertion verification or refinement execution. Overall1,
  runner1:10.86,RSS620,492KiB,setupdominates. Next isolate physical source for
  each of the eight cases, retaining strict compiler/call/registration checks.

- [Compiler-bound FnMut instance](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37409198258),
  source `e7ac80db4016bf6cf41b40920e3af11dcfb30470`,
  verifast_insert_tail_fnmut_hrtb90min. Independently reviewed translator-only
  HRTB patch c35c4b4 plus tuple2 parser; same Rust/req/posts as previous probe,
  original prelude and release exporter/refiner. Console build0/15.01s;
  paired source Z3 and unchanged readonly MIR/source hash roundtrip pass.
  Derived binary SHA0fd865ddb9a8211a828c2b452e6b2758ece63f094594577d9faf672f4b441d66.
  Actual comparator preconditions, normal Output=bool type and synthetic
  unwind exit resource/leak checks pass. First failure is real tail.read at
  verified134: missing points_to<T>(tail0,_), held by comparison borrows.
  VF1/.17s,RSS92,704KiB;refiner0/.12s,RSS91,704KiB;overall1,
  runner1:03.07,RSS645,516KiB,setup dominates. No covers/full insertion proof.
  Next real-compiler matcher regressions and normal comparison-access closure
  before ending the lifetime/recovering exclusive cell ownership.

- [First run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37381869926),
  2026-10-06 (Europe/Moscow), source `99af1446fc89bf3792be88090eb534982d688313`:
  runner preparation and the pinned Kani 0.67.0 build succeeded. Compilation of
  the bootstrap failed with five E0433 errors: this std integration exposes
  `kani::cover` as a function, not the `kani::cover!` macro. No proof was checked.
  The five calls were changed to the function form, whose signature was checked
  in the pinned Kani source. The following run used the corrected function calls.

- [Second run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37383583285),
  2026-10-06 (Europe/Moscow), source `34d008324e10a66bf59de705acd609d9509e7c36`:
  both bootstrap harnesses verified, zero failures. The arbitrary-decision proof
  satisfied 2/2 covers in 0.2443 s; the ordered-pair proof satisfied 3/3 covers in
  0.4219 s. These times are Kani verification times, excluding environment setup
  and tool compilation. Coverage remains the fixed i32 allocation/positions
  described above.

- [First insertion run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37386722977),
  2026-10-06 (Europe/Moscow), source `78e99a270f7b711e4d510877de4d93a9a2da51ea`:
  Kani built successfully, but compilation stopped at stage 1 with two E0502
  errors from `old(*values)` in the adapter postconditions. No insertion proof
  was checked; composition and direct stages did not execute. The adapter now
  receives a by-value `before` snapshot constrained to equal the input. All
  three functional postconditions are retained. A fresh run is required to
  validate this workaround.

- [Snapshot insertion run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37388333245),
  2026-10-06 (Europe/Moscow), source `4c125165c78383f575d65536941c3ddc421150ca`,
  `insertion_all_4`, 90 minutes, pinned Kani 0.67.0 / CBMC 6.10.0:
  the snapshot workaround compiled. Stage 1 failed solely on `memcmp.unwind.0`
  (`<builtin-library-memcmp>:25`): array equality checks 16 bytes, exceeding
  unwind 6. Other 306 checks and all six covers were undetermined; later stages
  were skipped, exit 1. Verification took 3.1742 s; the full runner took 3:45.06
  including cold build, peak RSS 1,809,900 KiB. This is not a contract proof.
  Replace the snapshot equality with the existing elementwise predicate over
  all four cells, retaining the exact domain, postconditions and unwind checks.

- [Successful insertion run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37389298278),
  2026-10-06 (Europe/Moscow), source `ec5556cf37fc31af4b25d27476c88f5fbc8e77c9`,
  `insertion_all_4`, 90 minutes, unchanged Kani pin / Kani 0.67.0 / CBMC 6.10.0:
  all three requested harnesses verified. Actual adapter/insert_tail contract:
  0/292 failures, 6/6 covers, 22.868813 s. Summary-based research caller:
  0/288 failures, 2/2 covers, 5.359691 s. Actual direct insertion_sort_shift_left:
  0/168 failures, 7/7 covers, 16.718891 s. Each stage has four unreachable
  incidental checks (formatting/alignment/unsigned-difference branches), no
  undetermined checks; every emitted unwind assertion succeeds. Runner exit 0,
  total 5:38.03 including cold build and three compilation stages, peak RSS
  1,944,792 KiB; reported verification times sum to 44.947395 s.
  Domain: arbitrary four-cell i32 backing values, valid tails / lengths /
  offsets and the stated sorted-prefix assumptions, pure nonpanicking `<`.
  Sortedness, exact multiplicities and untouched suffix hold. Summary is
  justified by stage 1 at this same source. No generic/unbounded/full-UB claim.

- [First actual outer-loop run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37390232978),
  2026-10-06 (Europe/Moscow), source `9dd5410ba262feccdd864140acfe716693d21cdc`,
  `insertion_outer_invariant_4`, 90 minutes, unchanged Kani pin:
  cold tool build succeeded, core compilation failed E0433 at injected line 599:
  unqualified `kani::loop_invariant` is not in scope in smallsort. No harness
  or cover was checked, exit 1. Runner 4:04.95, peak RSS 1,312,076 KiB.
  Fix only the macro path to `crate::kani::loop_invariant`; invariant/domain
  and checks stay the same. A new run at the fixed source is required.

- [Qualified actual outer-loop run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37390973809),
  2026-10-06 (Europe/Moscow), source `a3da2d490ca6129f0abd4c59063b8100ed73981b`,
  `insertion_outer_invariant_4`, 90 minutes, unchanged Kani pin:
  compilation succeeded and selected the actual safety harness. CBMC repeatedly
  warned of missing arguments to same_allocation_internal and pointer add from
  the invariant, inserting nondeterministic values. Symex took 458.716 s,
  60,787 steps, 1,244 VCCs (828 after simplification). Process then stopped
  with SIGTERM/143; job 14:55, no final proof/cover outcomes or resource data.
  Artifact upload and post steps were skipped, zero artifacts; full job log
  fetched. No explicit termination cause was reported. See
  [essential diagnostic and next obligation](outer-invariant-diagnostic.md).
  Preserve this reproducer; do not accept any proof with those substitutions.

- [First VeriFast exact-source probe](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37392725459),
  2026-10-06, source `fa55288edde480ae581f8deaf24d20bdca458ed7`,
  `verifast_insert_tail_probe`, 90 minutes, VeriFast 26.09 (pinned Linux archive
  SHA256 `da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa`),
  Rust nightly-2026-02-05 / rustc `db3e99bbab28c6ca778b13222becdea54533d908`:
  exact three source spans and ghost-only audit passed. Refinement-checker exit0,
  "No refinement errors found"; verifier exit1, parser error at `ens true;`
  (verified/smallsort.rs:26) inside the combined req/ens comment. No target body
  or safety theorem was verified. Overall runner exit1, 14.24 s including tool
  setup, peak RSS620,856KiB; verifier/refiner calls about0.09/0.12 s per job log.
  Fix splits req and ens into separate ghost comments matching existing repo
  syntax. Original std SHA256 stays
  `32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`.

- [Parsed VeriFast target probe](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37393312268),
  2026-10-06, source `8f1fc630b590c89c99270f23fd9bb7f2e32b8eb8`,
  `verifast_insert_tail_probe`, 90 minutes, unchanged VF26.09/nightly pin:
  parser accepts separate clauses and explicitly verifies actual generic
  `smallsort::insert_tail`. It fails the first real pointer-safety obligation
  at `tail.sub(1)` (verified/smallsort.rs:28): cannot prove
  `pointer_within_limits(ptr_add_(tail0, (0 - 1), T_typeid))` under `req true`.
  This is the expected missing-range diagnostic, not a safety proof. Exact
  source/ghost audit and refinement checker both pass (refiner exit0); verifier
  and overall exit1. Runner13.38s including tool setup, peakRSS620,128KiB.
  Next specify initialized owned range for arbitrary mathematical length and
  comparator ownership, preserving actual bodies and explicit Drop/unwind gaps.


- [Generic owned-range probe](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37394022890),
  2026-10-06, source `2ba502bc71cd25657584592fb83da044a7323252`,
  `verifast_insert_tail_range`, 90 minutes, unchanged VF26.09/nightly pin:
  symbolic usize n >= 2, initialized generic range and owned comparator,
  no fixed allocation length or sortedness assumption. Contract parses and
  actual insert_tail is analyzed, but first tail.sub(1) still cannot establish
  pointer_within_limits (verified/smallsort.rs:37). Exact extraction/ghost-only
  audit and refinement pass (refiner exit0); verifier/overall exit1. Runner
  14.10s including setup, peak RSS636,068KiB. No completed safety proof or
  covers; next expose/prove range's interior-pointer bounds through ghost facts,
  preserving arbitrary valid lengths and avoiding assumed pointer conclusions.


- [Pinned Kani UB detector controls](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37394356873),
  2026-10-06, source `6e0503febfe9c162e2e89a7ccfbd6126c9ca3be9`,
  `ub_detector_controls`, 90 minutes, Kani pin152c6a8 /0.67.0, CBMC6.10.0;
  `-Z uninit-checks -Z valid-value-checks --extra-pointer-checks`, default
  checks retained, repository --no-assert-contracts unchanged. All7 controls ran:
  initialized i32 and valid bool reads verify (0/213 and0/224 non-cover checks,
  2/2 covers each; 19/16 unreachable, none undetermined). Uninitialized i32,
  invalid bool and misaligned u32 each fail exactly their intended property.
  NULL read has explicit pointer-NULL failure plus uninitialized/OOB failures;
  strict all-failures-one-category classifier records it inconclusive (4 checks
  undetermined), not detector absence. Immutable static write unexpectedly
  verifies (0/192,19 unreachable): immutable-byte detector is missing for this
  concrete configuration. Suite exit1 /not validated. Verification times in
  control order: 0.25681174,0.28259882,0.35621458,0.2963091,0.26803493,
  0.16986255,0.14558381s. Suite497s including cold build and7 compilations;
  first stage4:10.74, subsequent38.35..42.66s; max RSS1,808,612KiB.
  This is detector evidence only, no SmallSort safety claim. Investigate exact
  immutable-static lowering/check behavior and retain gap in any target result.


- [Explicit array-bound lemma probe](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37395348422),
  2026-10-06, source `6851c1a9edc96f26f724efca2bc78acc78ef2a42`,
  `verifast_insert_tail_range`,90min, same VF26.09/nightly pins and range
  contract. Added ghost `array_inv::<T>()` is accepted, preserves resources,
  but actual insert_tail still fails first tail.sub(1) pointer limits at
  verified/smallsort.rs:38. Refinement0 and exact-source audit pass; verifier
  and overall1. VF0.10s,RSS165,456KiB; refinement0.09s,RSS162,844KiB;
  runner15.66s including setup,RSS620,480KiB. No completed proof/covers.
  Next prove an interior-pointer bound for arbitrary mathematical index from
  endpoint facts, including required pointer-add algebra, without adding a
  pointer-validity assumption. Pinned VF reference confirms ghost integer
  formals are mathematical integers; an i32 ghost parameter does not cap lengths.


- [Actual insertion UB safety frontend failure](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37395779522),
  2026-10-06, source `fe7567964629b627cf2bcb96ab71b8834316abcc`,
  `insertion_ub_safety_4`,90min, same Kani pin and detector flags. Actual outer
  loop with arbitrary i32 inputs/comparator decisions, no sortedness or loop
  annotations. Kani compiler ICE before checking any harness/property/cover:
  delayed_ub/initial_target_visitor.rs:107 unwraps a failed function-pointer
  resolution for fmt::Formatter -> fmt::Result. Diagnostic explicitly says
  uninit checks with function pointers/vtable calls are unsupported (#3300).
  Overall/Kani1, runner3:56.45 including cold build, RSS1,631,772KiB.
  No safety result. Suspected path is formatted panic in harness `backing[..len]`
  (input len<=4 already assumed). Next harness constructs the same valid slice
  with from_raw_parts_mut and keeps all input/domain/check/callback/covers
  obligations; constructor safety is justified by the live initialized array.
  This tests that hypothesis without changing actual std runtime code.


- [Interior-pointer lemma first obligation](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37396479423),
  2026-10-06, source `da5f16efdcf604582e3646b9f4518bbce71165b6`,
  `verifast_insert_tail_range`,90min, same VF pins. Own ghost helper parses,
  but first mul_mono_l call cannot prove0<=sizeof(T_typeid). Actual insert_tail
  is not reached in this run; no completed safety proof. Exact-source/ghost
  and refinement audits pass; VF1(.12s,RSS165,172KiB),refiner0(.11s,
  RSS162,776KiB),runner12.75s,RSS636,748KiB. Endpoint/monotonicity proof
  needs that wellformed-type fact as a derived caller obligation, without
  adding it as an assumed insert_tail precondition. Integer annotation types
  are mathematical integers, including ghost i32; no runtime i32 cap applies.
  Conditional cleanup works: whole job33s instead of multi-minute Kani cleanup.


- [Raw-slice actual insertion UB safety](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37396688760),
  2026-10-06, source `43f133c72fcd4f3dffe033582aa96aa2500bf860`,
  `insertion_ub_safety_4`,90min, unchanged pin/UBflags/inputdomain. Equivalent
  raw-slice harness construction resolves the Formatter compiler ICE. Actual
  std safety harness now executes; all7/7covers satisfied, no undetermined
  checks, all unwind assertions pass. Sole failure among469 non-cover checks:
  `ptr::copy_nonoverlapping::<i32>.unsupported_construct.1`, "Kani currently
  doesn't support checking validity of copy_nonoverlapping for *const i32".
  440 checks succeed,28 unreachable. Verification3.1836462s; runner3:54.96
  including cold build/compilation,RSS1,821,596KiB,overall1. This is an
  unsupported-instrumentation result, not a safety counterexample or proof.
  Pinned check_values.rs:387-393 unconditionally inserts this unsupported
  property for MIR CopyNonOverlapping (TODO value check). Keep valid-value
  flag and actual copy runtime; approved generic VF direction remains necessary,
  along with the independently measured immutable-byte gap.


- [Owned-cell interior bound established](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37397404058),
  2026-10-06, source `91392b65f2dcc122a33a55f94377b6e372c74760`,
  `verifast_insert_tail_range`,90min, same VF pins. Helper obtains nonnegative
  T size via points_to_limits on first owned cell, returns the initialized
  range and proves its interior-pointer bound; actual insert_tail's first
  tail.sub(1) passes. Generic mathematical n>=2, no fixed length or new input
  assumption, exact-source isolated crate. Next obligation at &*tail (line56):
  ref_precreated_token<T>(tail0,_) missing; proper shared-reference creation
  from element ownership remains to prove. Overall/VF1, not a completed function
  safety proof. Exact-source/ghost audit and refinement0; VF0.13s,RSS165,196KiB;
  refiner0.11s,RSS162,724KiB; runner13.73s,RSS636,440KiB.


- [Observed immutable-store detector gap](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37397720683),
  2026-10-06, source `75799de75efab17d9c386deea6c49047db16cb60`,
  `ub_immutable_observation`,90min, same Kani/CBMC pins and all UBflags.
  Both positive controls pass2/2covers each,0/213 and0/224 non-cover failures,
  no undetermined. New negative writes9 to immutable static, volatile-reads it,
  asserts9 and covers9: Kani verifies0/205 (189success,16unreachable),1/1cover,
  exit0. The modeled store is observable; no immutable-byte detector rejected
  it. Suite correctly exits1/notvalidated. Control verification times
  .21481459,.27654117,.19491471s; suite306s including cold build/compilations,
  stage times3:48.23,38.47,38.60s,maxRSS1,807,488KiB. This strengthens the
  original write-only gap; no ambiguous optimized-away-store explanation.
  Keep original reproducer and required checks. Generic ownership/permissions
  via an approved alternative or a separately validated model fix is necessary.

- [Shared-reference syntax diagnostic](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37398670146),
  2026-10-06, source `6540b15cf54fa805224f594709d0b1a5613d23ee`,
  `verifast_insert_tail_range`,90min,VF26.09/nightly-2026-02-05 unchanged.
  Original symbolic generic owned-range precondition retained; new ghost
  lifetime and final-two-cell preparation leave actual Rust bytes unchanged.
  VF fails parsing verified/smallsort.rs:60 at the second ghost statement
  in a multiline ghost block; no new proof obligations reached. Exact-byte
  audit/refinement0, VF1(.07s,RSS165,324KiB),refiner.10s,RSS164,720KiB;
  runner16.19s,RSS636,172KiB,overall1. Full logs/artifacts fetched.
  Next fix ghost-statement syntax against pinned parser, preserve all resources.

- [Shared-cell preparation milestone](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37398942673),
  2026-10-06, source `d1bd9d6b235a9072c90ad4256eba55290cbd5eda`,range90min,
  same VF/Rust pins, symbolic generic owned range and original req unchanged.
  Parser accepts ghost statements; both last-cell splits, generic ownership,
  full borrows, shared borrows and reference initialization pass. Next failure:
  second open_frac_borrow needs [1/2]lifetime_token(cmp_k), consumed by first
  still-open borrow. First actual comparator call not reached; no completed
  function proof/covers. Exactbyte/refinement0,VF1(.17s,RSS165,376KiB),
  refiner.10s,RSS162,900KiB,runner14.68s,RSS619,784KiB,overall1. Full evidence
  fetched. Next fix lifetime fractions from pinned open/close specifications.

- [Lifetime merge diagnostic](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37399426683),
  2026-10-06, source `9c5f12fb41caf4d5d359e6a4e3b4527d9ffaa581`,range90min,
  same pins/domain. Pinned begin_lifetime provides full token and preparation
  APIs preserve fractions; added merge_fractions is accepted. Same second
  open_frac_borrow lacks [1/2]lifetime_token(cmp_k). Fragmentation hypothesis
  not confirmed, first callback remains unreached. Exactbyte/refinement0,
  VF1(.18s,RSS165,424KiB),refiner.11s,RSS162,824KiB;
  runner14.22s,RSS633,700KiB,overall1. Full logs/artifacts fetched.
  Next add proved assertions between token-preserving operations to locate
  actual resource loss; retain original req and every safety obligation.

- [Lifetime token localization](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37399630653),
  2026-10-06, source `83fd40c7ab9e4b0b1a231d74e0382cb59576a50c`,range90min,
  unchanged pins/domain. Full-token assertion immediately after merge fails,
  before either reference opening: the resource loss occurs earlier than
  previously inferred from the second-open error. Later assertions unreached.
  Source-spec conservation alone does not establish conservation in the
  translated body. Exactbyte/refinement0,VF1(.11s,RSS165,524KiB),
  refiner.07s,RSS162,968KiB,runner10.97s,RSS624,500KiB,overall1.
  Full evidence fetched. Next assert token ownership earlier around the
  lifetime binding and each preparation operation, no new assumptions.

- [Lifetime binding localization](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37399825118),
  2026-10-06, source `e8fac271c7a83004a957e0e7fd364a72622bd7a0`,range90min,
  same pins/domain. Full-token assertion immediately after begin_lifetime
  passes; the next assertion immediately after let_lft fails at line56.
  Borrow/share/init not reached in this diagnostic revision. Resource change
  is localized at lifetime binding; earlier conservation claim across that
  binding is withdrawn. Exactbyte/refinement0,VF1(.09s,RSS165,512KiB),
  refiner.08s,RSS162,992KiB,runner12.02s,RSS620,200KiB,overall1.
  Full logs/artifacts fetched. Next account pinned binding-scope token
  reservation and prove the usable fractions, without narrowing input domain.

- [Accounted-quarter comparator frontend](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37400101276),
  2026-10-06, source `86edc719f6aefcbe5acc66d1203bd6dbcf0e761a`,range90min,
  same pins/domain. Pinned let_lft reserves half token until block exit;
  revised accesses use quarter each with checked fractional assertions.
  New error at actual comparator expression: Incorrect number of type
  arguments for ghost::<'cmp>. No quarter-resource error reported, but no
  full callback proof; static error ordering must be inspected before claiming
  all preceding statements verified. Exactbyte/refinement0,
  VF1(.11s,RSS165,508KiB),refiner.08s,RSS163,032KiB;
  runner11.53s,RSS621,304KiB,overall1. Full evidence fetched.
  Next inspect supported FnMut lowering/generic argument count. Lifetime
  binding's block-wide reserve remains a separate recovery issue before tail.read.

- [Actual shared-reference creation milestone](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37400422055),
  2026-10-06, source `9d4a01fc9388b53d2bc4cfc53651a3b728914457`,range90min,
  same pins/domain. Full MIR inference retained. All quarter-token assertions,
  preparation and both actual &* expressions pass. FnMut::call_mut then lacks
  Args tuple own at std/lib.rsspec:47; its reference types contain two inferred
  lifetime placeholders. Need explicit sound tuple ownership/type matching.
  No completed callback/function proof. Exactbyte/refinement0,
  VF1(.19s,RSS165,384KiB),refiner.11s,RSS162,836KiB;
  runner1:12.85,RSS617,796KiB,overall1 (extra setup time, not solver time).
  Full logs/artifacts fetched. Next derive tuple ownership with supported
  lifetime substitutions, no new assumptions or length restrictions.

- [Explicit tuple syntax diagnostic](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37401170274),
  2026-10-06, source `661cee7cdf711f2996721bf0361151a34fb158b6`,range90min,
  same pins/domain. Parser rejects ghost tuple value `(a,b)` in explicit own
  close at line102; no revised function proof attempted. The pinned parser
  supports tuple types, but values require std_tuple_2_ numeric-field struct
  syntax. Exactbyte/refinement0,VF1(.09s,RSS165,376KiB),
  refiner.11s,RSS162,824KiB,runner13.32s,RSS634,536KiB,overall1.
  Full logs/artifacts fetched. Next use supported equivalent tuple constructor;
  original req, Rust behavior and complete FnMut generic substitutions retained.

- [Tuple ownership model diagnostic](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37401357731),
  2026-10-06, source `ae09e983ef430fc03dc49fc4724d36dbb0cab7e9`,range90min,
  same pins/domain. Numeric-field tuple constructor parses. Explicit close of
  tuple own fails No such predicate instance; first callback still unproved.
  Need a supported synthetic-tuple type_pred model/folding operation, not an
  assumed chunk. Exactbyte/refinement0,VF1(.17s,RSS165,428KiB),
  refiner.10s,RSS162,788KiB,runner12.85s,RSS635,404KiB,overall1.
  Full logs/artifacts fetched. Independent pure generic size target prepared
  for next serial experiment while this ownership-model issue is investigated.

- [Generic size helper verified](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37401540878),
  2026-10-06, source `9fb8940437be22b316c45a3b23f9ece325944aae`,
  `verifast_swap_size`,90min,VF26.09/nightly-2026-02-05 unchanged.
  Actual const has_efficient_in_place_swap<T> body, unrestricted generic T,
  req true, exact result size_of<T><=8. One named target body confirmed plus
  four body execution/return records; 0 errors (40 statements including pinned
  prelude lemmas, not 40 target statements), x86_64-unknown-linux-gnu LP64.
  No slice/pointer/comparator premises or bounded allocation. Pure query and
  comparison have no memory access, uninitialized reads or immutable writes;
  returned bool is produced by the comparison. Covers/unwind bounds not used.
  Exact source-span/ghost audit and refinement0,all stage/overall exits0;
  VF.10s,RSS160,772KiB,refiner.07s,RSS154,324KiB,
  runner12.70s,RSS585,516KiB (setup dominates). Full logs/artifacts fetched.
  Span197bytes,SHA256 eeb87db6d322c8b28de87b203cdd44ec1cdffd29ec1388ba5c00267bf40f88bf.
  This closes the isolated LP64 generic helper proof; dispatch callers, other
  six safety targets and all three small_sort sorting contracts remain open.
  Next resume insertion tuple ownership through an explicit transparent model
  definition of field ownership, with model compatibility obligations recorded.

- [Tuple model namespace diagnostic](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37401753468),
  2026-10-06, source `72dd333ed19c9f1c7a95ceb98957cf2f61fd9dba`,range90min,
  same pins/domain. Transparent external tuple own definition in smallsort
  module triggers VeriFast internal assertion at verifast1.ml:2309, verifier2.
  Source requires root package for a type-predicate definition whose struct is
  external to current module; no implementation counterexample/proof result.
  Exactbyte/refinement0,VF.11s,RSS165,616KiB,refiner.10s,RSS162,936KiB;
  runner16.91s,RSS634,396KiB,overall1. Full logs/artifacts fetched.
  Next move only the ghost model to verified crate root and extend byte-stripping
  audit/manifest to both files; no runtime/source/precondition changes.

- [Root tuple model naming diagnostic](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37402093844),
  2026-10-06, source `b777d8d78d50ab79422ac1101111662e3fc4397e`,range90min,
  same pins/domain. Root placement resolves prior internal namespace assertion.
  New error at lib.rs:5: Predicate constructor name clashes with existing pure
  function name. No comparator proof. Both files pass independent ghost-byte
  audits and refinement0,VF1(.14s,RSS165,436KiB),
  refiner.12s,RSS162,896KiB,runner13.76s,RSS637,500KiB,overall1.
  Full logs/artifacts fetched. Next inspect existing opaque tuple-own symbol
  and supported named-predicate/type-predicate alias route; no assumed ownership.

- [Bundled tuple overlay duplicate diagnostic](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37402802085),
  2026-10-06, source `c0742d522d83264003b7872444b402ef12a80c97`,
  `verifast_insert_tail_tuple_overlay`,90min,same binary/Rust pins.
  Original prelude SHA d7058d43557a2b5147eb1377e85bb67d04b94c83594b6c1c27650c9c571841b5
  matches; exact194-byte insertion produces patched SHA
  fa59c4585f1460bba408dd9ca7e25a4b5f41cc12aaa76f482e4383934e9982e8.
  Original/patched specs, insertion hash and byte-roundtrip retained; tool binary
  hashes unchanged. VF rejects duplicate tuple2 type predicate own, conflicting
  with prelude struct declaration line15. Automatic alias exists even without
  explicit own text; previous no-duplicate expectation withdrawn. No target
  execution. Runtime ghost-byte audits/refinement0,VF1(.09s,RSS165,492KiB),
  refiner.11s,RSS162,860KiB,runner14.17s,RSS527,852KiB,overall1.
  Full evidence fetched. Next trace automatic tuple ownership semantics and a
  supported transparent folding/replacement route; no speculative rerun/axiom.

- **Pinned tuple ownership blocker confirmed by independent source review.**
  `rust_parser.ml:1139-1149` automatically emits an opaque bodyless fixpoint
  std_tuple_2__own and its type_pred alias for the RSSPEC tuple declaration.
  It has no field-ownership body to close. Same-name fixpoint completion is
  rejected (verifast1.ml:2815), a same-name predicate ctor clashes (3985-3988),
  another alias duplicates the automatic definition (4065-4077), and aliases in
  another file are forbidden (4079-4082). Ghost syntax has no raw struct escape.
  Existing tuple0/tuple4 close lemmas are unproved library declarations; adding
  an analogous tuple2 bridge would violate this experiment's no-opaque-bridge
  contract. Stop spec naming retries. Next justified diagnostic: Actions-only
  source build at809de4596839b739dd999f9e462242c835e3af46 with a reviewed
  parser change only for synthetic std_tuple_2_, transparent field ownership
  and one alias. Other structs/models remain unchanged. Build recipe and patch
  are being prepared; no local verifier/build or new run. Compatibility and
  actual insertion/unwind/loop proof remain separate requirements.

- **Prepared tuple2 parser source-build diagnostic.** Manual choice
  `verifast_insert_tail_tuple_parser` exposed on default main by workflow-only
  commit `569ff40`; dispatch source remains challenge-8/research. Build only
  pinned26.09 console on Ubuntu22.04, parser patch SHA
  ff2576f727d13d9dfcd9616a030b72ad0b0a27ce87cc96014af2d2ba42249660.
  Pinned VFDeps archive and decoder source revision; unchanged source prelude;
  same generic owned-range contract, no length cap or sortedness assumption.
  Build/proof/refinement logs and hashes are separate under one budget.
  Experimental source-derived verifier, baseline pin unchanged.
  Run [37405435682](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37405435682)
  checks `3d68d61ba5e8a95dfa67677a4cea294fb337b309`,90min. Full logs/artifacts
  fetched: source/parser/prelude/patch and ghost-byte extraction pass; VFDeps
  archive hash matches, but -xJf selected xz while upstream uses bzip2 -j.
  Setup fails2 before decoder/build/verifier/refiner; no proof/covers.
  Runner22.60s,RSS629,004KiB, entirely setup. Corrected to upstream -xjf;
  next NEW commit/run required;
  actual callback normal/unwind, tuple-share compatibility, cell recovery and
  remaining function are still unproved. See verifast-tuple-parser.md.

- **Source-build prerequisite diagnostic:**
  [37405631794](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37405631794),
  source `5dcf5348447174f3a9a8c23cce3bad80d70188ca`,tuple_parser90min.
  Full evidence fetched; original source/parser/prelude+deps pins and exact-byte
  audit pass. Decoder install0,3.93s; experimental OCaml console compiles.
  `make verifast` additionally regenerates C STDLIB manifests; bitops.c18
  precondition x<pow_nat(2,N32) fails at Z_of_uint32 call, overall2.
  Seven preceding C manifests verify, but C library as a whole is unproved.
  No actual insertion verifier/refiner/covers. Buildstage1:18.67,RSS426,740KiB;
  runner2:22.22,RSS642,736KiB,all setup. Next build ../bin/verifast only:
  all-.rs inputs skip final C manifest linking (vfconsole.ml), Rust frontend
  loads adjacent unchanged prelude. No C manifest reuse/fabrication or model
  assumptions; preserve this failed broad-target evidence and inspect new run.

- **Tuple parser reached actual comparator call:**
  [37406214235](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37406214235),
  source `45487efb5c9fda8ed4aa32d848dd179d946eb83c`,tuple_parser90min.
  Full evidence fetched. Console-only source build0,18.51s,RSS426,068KiB;
  exact Rust bytes/refinement0,unmodified prelude. Derived VF binary SHA
  08431fb200f070b5a4c37f9dd267108f337729d2ab6a53ae1ca9f7d512fec594.
  Tuple2 own closes and actual FnMut preconditions pass. First failing path
  is comparator unwind, mapped to synthetic return at call line103; actual
  early return104 and tail.read112 not reached. Empty default on_unwind_ens
  leaves lifetime/refInit/borrowEnd/F/thread/range-prefix resources, leakcheck
  fails. No full insert_tail or panic restoration proof. VF1,.22s,RSS92,680KiB;
  refiner0,.14s,RSS91,828KiB;runner1:15.64,RSS645,520KiB,overall1.
  No covers/unwind-disable flags. Runtime ldd metadata was collected before
  the parent's explicit source-bin LD export; next helper will assert paired
  Z3 resolution in that environment. Next prove or explicitly return genuine
  unwind ownership resources, then proceed to normal cell recovery. Model
  compatibility beyond this generic reference-tuple use remains open.

- **Comparison resources accounted on exit:**
  [37407173581](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37407173581),
  source `ff413cfbee73e42c576eee96bdc461b80ca76255`,tuple_parser90min.
  Full logs/artifacts fetched; input domain/Rust unchanged. Transparent normal
  and unwind assertions return every reported comparison-resource chunk;
  no normalization or full owned-range restoration claimed. Sourcebuild0,
  19.14s,RSS426,676KiB,same derived binary08431fb2; actual ldd/assert resolves
  paired source-bin Z3. Exact-byte/refinement0. Exit assertion consumption and
  leakcheck pass, then normal FnMut output type mismatch atcall125:
  <F as FnOnce<tuple2<&'cmp T,&'cmp T>>>::Output versus bool. No completed
  call/function/read/cleanup proof. VF1,.22s,RSS92,712KiB;refiner0,.15s,
  RSS91,704KiB;runner1:15.93,RSS643,776KiB,overall1,setupdominated.
  No covers/check-disable/assumed bridge. Next propagate/instantiate the actual
  signature's FnMut(&T,&T)->bool associated-output constraint after ghost
  lifetime substitution; retain arbitrary legal F and both execution outcomes.

- **Compiler projection capture setup failure:**
  [37407937980](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37407937980),
  source `a627dec2fbdf76479c219a2edcc6de1225b4cfbc`,tuple_parser90min.
  Full logs/artifacts fetched. Source build/paired Z3 and ghost-byte audit pass;
  Rust hashes unchanged before/after capture. Direct exporter127: supplied
  target-libdir lacks librustc_driver; working rust_fe uses sysroot/lib.
  No MIR/decode, actual verifier/refiner, proof or covers. Overall127,
  runner1:21.70,RSS624,152KiB,setup/capture only. Next correct driver path,
  record driver hash, capture actual HRTB before new translator semantics.

- **Actual compiler HRTB projection captured:**
  [37408278446](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37408278446),
  source `d34616e2b0652be92ec5130737977ae0a7c8834e`,tuple_parser90min.
  Full logs/artifacts fetched. Readonly compiler MIR export0,.03s;Capnpdecode0,
  .01s; inputhashes unchanged. Captured binary193,920bytes SHA395d1301cf8e9759ef0004b70e155818e36024467202e1f0ee933262c0410311.
  Actual insert_tail HRTB projection core::ops::FnOnce::Output takes F and
  tuple(&'__23 T,&'__24 T),RHSBool,with bothboundregions; FnMuttrait sameargs.
  Actual methodcall MIR takes F and refsErased,lateBoundGenericParamCount1,
  while ghosts select F,tupleCmp,cmp. Pinnedtranslator4793-4801 dropsbound
  projections. Sourcebuild0/14.16s;pairedZ30; originalOutput/bool errorreproduced
  VF1,.15s,RSS92,708KiB;refiner0,.10s,RSS91,568KiB;overall1,
  runner1:05.79,RSS584,844KiB,setupdominated. No fullfunctionproof/covers.
  Next narrow compiler-bound instantiation in source-only experimental
  translator patch, preserving all non-lifetime types and actual boolRHS.
  No assumed output lemma or extra F constraint. New fnmut_hrtb selection
  keeps tuple_parser reproducer unchanged; proof/unwind restoration stillopen.

## Next experiments

1. **Completed:** bootstrap confirmed on Actions; both harnesses and all five covers pass.
2. **Completed bounded milestone:** adapter contract, modular research caller
   and direct insertion proof all pass (15/15 covers) at the SHA recorded above.
3. Develop reusable contracts and loop invariants for the actual insertion
   helpers/loops, then prove reuse on an actual std caller. The current modular
   research caller does not establish the real outer loop.
4. Expand domain and type coverage while recording assumptions and runtimes.
   Bounds up to 16 are optional milestones, not a substitute for arbitrary
   valid lengths. Develop merge specifications after the insertion approach.
5. Cover the remaining primitives and all three small_sort implementations.
   Investigate length-32 scalability, contracts on specialized trait methods,
   ownership/unwinding and uninitialized-read coverage as separate obligations.
   Choose VeriFast or a hybrid approach on evidence from these experiments.
   See the runbook for the detailed continuation plan.

Experiments may use a larger time budget than the upstream CI; the final solution
must remain automated and acceptable to the upstream CI and review committee.

## Actual outer-loop invariant experiment

`insertion_outer_invariant_4` injects a cfg(kani) pointer-range invariant into
std's actual outer loop in a disposable Actions checkout, then checks arbitrary
four-cell i32 inputs and independent comparator decisions without a sortedness
assumption. See [experiment specification](outer-invariant.md) and
[coverage ledger](coverage.md). The inner loop remains bounded; the new
experiment has no completed proof yet; compiled attempt37390973809 ended with
argument-substitution warnings and SIGTERM. The frozen-pointer/stride rewrite
is prepared but unverified.

## Approved alternative feasibility probe

`verifast_insert_tail_probe` prepares exact live std source spans for CopyOnDrop,
insert_tail and insertion_sort_shift_left in an isolated crate, then invokes
repository-pinned VeriFast 26.09 and its refinement checker on hosted Actions.
See [probe design and limits](verifast-probe.md). The frontend profile keeps
`req true; ens true;` as a deliberately incomplete diagnostic contract.
`verifast_insert_tail_range` supplies a symbolic initialized owned range and
generic comparator ownership, but no completed insertion proof has been obtained.
The old insertion probe specifies only insert_tail. The actual CopyOnDrop Drop
body now has a separate successful conditional contract proof37419989766;
compiler cleanup reuse and the actual outer loop remain unverified.
The goal is to expose a concrete frontend or first ownership obligation without
ignoring unwind paths or adding assumptions. This is preparation for evaluating
arbitrary-length separation-logic proofs, not a replacement verified algorithm.
The Kani pin and completed bounded evidence remain unchanged.

## First minimal-profile result

[37441463201](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37441463201)
checked `d198907e7eec57f8bcd880304fa1345b97b0ef53`, 90min. Full logs/artifacts
inspected. Exact one-translator-file source audit, unchanged parser/prelude,
patch/output pins, paired Z3 and source byte/hash checks pass. Console SHA-256
`b1012430ca97595b5ee70e5e16778d2b7f008897dba2e910b953d3e4034ebaf6`,
build0/14.75s,RSS426,796KiB. All7readonly exporter/decode0; all7VF1 before any
caller because the common new recover_single helper fails its first close of
[first_fraction]ref_initialized(tmp_ref). Its wrapper contains two fractions
of the same precise predicate; exact fractional bookkeeping must be corrected.
The independently checked recover_pair still has18 body records; caller/call
counts0 for all cases, and strict negative classifiers reject this unrelated
failure. No new lifecycle proof or intended negative is claimed.

Six refinements pass; the positive MD case separately fails because the pinned
refiner does not support RawPtr (addr_of(tmp)), although its command dump shows
the same original/verified operation. This failure is retained. The readonly
MIR audit passes new1/deref1/read2/write1/into_inner0. VF.08s percase, refinement
.04s (.05generic), runner1:22.18,RSS585,528KiB; cold setup/build dominate.
No covers/loopbounds. Next fix same-reference recovery and use a sound,
independently checked original-provenance pointer route; all full posts remain.

## 2026-10-06 explicit resumption: isolated same-reference bookkeeping diagnostic

Owner explicitly resumed only STATUS's prepared feasibility phase. Clean tree,
origin fork, FF 126e23d -> f50b237; no active run; auth/push/workflow access checked.
Actual obligation: eventual insert_tail held temporary must recover full current
T storage/ONE own, not merely two ref_initialized accesses. This diagnostic first
checks the helper independently of pointer feasibility; it is NOT step 3's
accepted seven-case lifecycle gate.

Hypothesis: precise same-reference chunks auto-merge when both are opened;
packaging each initialization access in an imprecise predicate and closing each
sequentially restores both exact quarter lifetime tokens without new coefficient
premises. Both original quarter accesses remain. No split/assume/tool patch.
Draft critically rejected: split_fraction's `by` is a relative multiplier
(verifast.ml:1521-1552), not an absolute coefficient. open_frac_borrow does not
state numerical bounds on its result; we must not manufacture them. Each package
keeps its original coefficient and close token; opening one at a time avoids
co-resident precise chunks and requires no new split inequalities.

Domain/posts unchanged: unrestricted T, initialized cell + current full T.own;
normal-only synthetic natural block, no callbacks. Full cell/T.own normal post.
Original two-cell controls retain their full posts and three intended negatives;
they now exclude optional single-cell helpers under BOTH profiles. Optional
ManuallyDrop positive still uses original owner-address addr_of!(tmp), read/write;
we deliberately retain the unsupported RawPtr refinement failure. Saved draft
remains unapplied, not a candidate to dispatch wholesale.

Frozen profile: manually_drop_only, source809de4596839b739dd999f9e462242c835e3af46,
Rust nightly-2026-02-05, sole patch SHA2565500204aadd0ea0a2996d63d064160185457b6d337782aa4300c11272ab450cc;
translator7319d2638c3fc49a1663b50925d565ca2e10d95754933ed58e37f27239936803
->60ece6e90f4dd3c623a99ea31feebb3210359daa38850255332118b2316eac39.
No parser/kernel/prelude/exporter/refiner change. Selection
verifast_borrow_recovery_manually_drop, budget90 minutes, all seven cases.

Expected stages: baseline two positives VF/refinement0; missing-token and
missing-debt negatives at recover_pair precondition, false-post at caller post;
MD missing-init at actual &*tmp/create_ref's ref_initialized precondition, before
helper call. recover_single actual body should pass; MD positive should reach
its explicit helper and owner-provenance read, with full posts checked. Its
refinement is EXPECTED FAILURE at original addr_of!(tmp) RawPtr; whole-unit
failure is retained and cannot establish lifecycle gate. Inspect full source/MIR
and actual named body/call traces, source/ghost-strip/hash audits, every exit,
leaks/unwind, no covers/loops. No other failure counts as an intended negative.

Pointer review independently found cast `_tmp_shared as *const T` refiner-supported
but no permission bridge: create_ref proves origin equality, not child/owner
heap identity; borrow_end restores owner location, ptr::read lowers to Deref of
saved child. Actual guard.src is child/reference-derived in saved insertion MIR.
Do not change pointer semantics, assume equality or bypass RawPtr checker.
If bookkeeping passes, STOP at this documented pointer-support/provenance and
actual first-false/first-panic architecture boundary; no callback or AST-routing
implementation. If bookkeeping fails, only evidence-backed fixture fixes within
frozen profile are allowed. Run identifiers/results to follow after exact-SHA push.

Diagnostic result [37448257248](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37448257248):
f0f417ce9913f53a90591c89593b31b359b87032, minimal/90min, completed failure.
Full4267-line Actions log and all artifacts downloaded/read. Exact tool/profile
hashes retained: console b1012430..., exporter2b8ebb..., refiner9f3882...,
prelude d7058d...; sole patch/source/parser audit and paired Z3 pass. All7
readonly export/decode and source/ghost-strip/hash checks pass. Both original
positives VF/refinement0; all3 baseline negatives intended VF1/refinement0,
each caller/header/helper1, pair body18, explicit call1. Optional actual
recover_single body now completes16records, return and leak-check in both units.

New FIRST caller failure in BOTH MD cases: general.rsspec203 precondition at
close_full_borrow_content<T>(t,&tmp), positive generated source95, missing-init
source95: no points_to<T>(tmp_addr,_). Caller/header1, helper16, explicit
recover_single call0, actual temp reference0. This is NOT the intended missing-init
negative; classifier correctly reports misclassified. MD positive refinement
still fails original RawPtr; remaining6 refinements0; MIR audit new1/deref1/read2/
write1/into_inner0. No lifecycle, callback, provenance or pointer gate passed.
Helper conditional resource proof is established, caller construction is not.
VF .08s each; total runner1:29.24,RSS625580KiB, console build23.83s,RSS425988KiB;
cold setup dominates, no covers/loop bounds. Next inspect tmp storage translation
within existing profile; no address-taken or other patch expansion authorized.

Separate unchanged-release baseline card: same SHA f0f417c, selection
verifast_borrow_recovery,90min, no patches. Hypothesis: per-case helper exclusion
preserves exact five release controls after runner changes. Expected2 positives
VF/refinement0 and3 intended resource/post negatives VF1/refinement0, actual pair
body/call/header counts and source/hash/leak audits; no MD helper in any unit.
This checks profile isolation, not optional helper or actual insertion. One run
only, after37448257248 completes; outcome to record below. No new semantics/posts.

Separate baseline result [37448682524](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37448682524):
same f0f417ce9913f53a90591c89593b31b359b87032, unchanged26.09/90min,
completed success. Full2178-line log/artifacts inspected. All5 exports/decodes/
refinements and source/ghost-strip/hash checks0; optional single helpers absent;
2positives VF0,3negatives intended VF1; each helper/header/caller1,pair18/call1.
Console dc672335da76fe1bb06cf7ebca916185c34edb65466df0a937645a437c7f0ecc,
prelude d7058d43557a2b5147eb1377e85bb67d04b94c83594b6c1c27650c9c571841b5;
no patches/source compilation. VF wall .11-.13s/case, refinement .05-.07s;
runner19.13s,RSS639268KiB. Setup dominates; no covers/loop bounds. For preceding
minimal run, VF CPU .08-.09s, wall .12-.13s; refinement wall .07-.10s (earlier
"VF .08" was CPU), total89.24s and console build23.83s.

Static root cause of new MD caller failure independently verified at pin809de459:
translator1880-1892 maps immutable local Not -> ConstTypeExpr; verifast.ml991-993,
1042-1044,1111-1118 produces half points_to for addressable const locals;
general.rsspec202-204 requires full points_to + T.own. Actual insert_tail also
uses immutable tmp (smallsort.rs556). A mutable fixture, extra full-storage
premise, fractional post weakening or altered immutable-local tool rule is not
a permissible routine fix. Address-taken patch doesn't repair fractional size
and is excluded. No source/tool change or further dispatch made after diagnosis.

PHASE CLOSED: helper resource bookkeeping established conditionally; MD full
caller/refinement gate not passed, intended missing-init negative not reached.
Pointer draft retained unapplied; no same-address ownership bridge claimed.
Actual normal-true source scope remains unestablished; false return bypasses
recovery, first panic Continue skips it before guard. Full n-current-cells/ONE
ownership/F/thread/type/frame posts remain mandatory, unrestricted T/F without
Freeze/Copy/purity or sortedness safety premises. No callback/AST routing work.
See PREPARED-PHASE-2026-10-06.md for exact CFG/source evidence and options:
review immutable-local storage plus pointer/refinement support separately;
review source-exact scope/direct-unwind semantics with trust/regression gate;
or choose another source-faithful route/simpler target. Owner decision needed
before new architecture/semantic patches or next phase. No active run.

## 2026-10-06: approved sort4 functional experiment card

Authorization: owner's explicit continuation of phase approved at
68fcc98b79fc69b717d3e2ed42605cae8b4ffc05. Clean entry, fast-forward to this
commit, no newer instructions/active or queued runs. Actual obligation:
library/core/src/slice/sort/shared/smallsort.rs::sort4_stable, blob
e555fce440872898e47fd5114f32eb15401d07df. Contract and caller resource audit
will be preserved in SORT4-CONTRACT.md; generic feasibility is independent.

Falsifiable hypothesis: the unchanged five-comparison/four-copy real body
returns a sorted exact multiset for four full-range symbolic i32 values, and
returns a stable sorted permutation of four symbolic-key/fixed-ID items.
Existing actual-source swap/insertion Kani successes justify this route; finite
rewritten-model observations are guidance only, not proof evidence.

Domain: two separate live fixed allocations, each exactly four initialized
cells. Values src is four independent arbitrary i32, dst [0;4]. Tagged src
has independent arbitrary i32 keys and IDs0..3; concrete Copy item representation
and initialized destination are in sort4.rs. Comparator is literally pure,
nonpanicking `<` (keys only for tags). No key restriction or target summary.
Normal posts: destination adjacent nondecreasing and exact counts for every
input value; tagged complete key/ID items each once, equal-key IDs increasing;
source unchanged. Covers include strict decision representatives, all-equal,
mixed duplicates, reverse/ascending inputs and full-range extremes. Helper
loops bound four with unwind6 and unwinding assertions retained. The domain
has no reachable comparator unwind; no unwind theorem is claimed. The full
generic target still requires current valid cells/ONE ownership sequence,
restored borrows/F/frame on each normal and all five panic exits, preserving
allowed callback effects rather than assuming unchanged reachable state.

Profile: unchanged Kani152c6a8c875d9886a67e229247b4826d6105ccfd,
repository nightly-2026-02-05, default checks through unchanged scripts/run-kani.sh,
exact harness selection, --jobs1, --object-bits12, repository unstable options
and --no-assert-contracts. No contracts/stubs in these harnesses and no disabled
checks. This is a FUNCTIONAL BASELINE, not the explicit uninit/validity/extra
pointer profile. Known CopyNonOverlapping validity unsupported operation and
immutable-store detector gap remain open; no duplicate diagnostic is needed.
No VeriFast patches/profile changes or generic hosted probe are planned.

Expected positives: prove_sort4_values and prove_sort4_stability both reach
actual generic body and all assertions/covers with no failed checks, unwinding
assertions or unsupported operations. No negative controls are introduced in
this positive functional experiment; historical UB controls retain their
recorded classifications. Acceptance: full logs/artifacts, exact unchanged
std-prefix+appended-proof byte audit, source/tool/configuration hashes, both
named verified harnesses and every cover. No VeriFast refinement/leak result
is inferred from Kani's result. Source edits only in disposable hosted checkout.

Selection sort4_functional; budget90min including cold Kani build and both
serial harness stages; ubuntu-24.04 GitHub-hosted. Expose only this narrow
workflow selection on default branch if dispatch validation requires it.
Outcome map: green -> record bounded functional theorem and close phase after
generic static assessment; routine compile/harness/runner error -> fix within
frozen profile and dispatch NEW SHA; actual failed property -> inspect precise
counterexample and contract before change; required semantic change or repeated
failure without new evidence -> stop affected route and document decision.
No automatic advancement to swap/networks/insertion or external publication.

Dispatch resolved: [37459631500](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37459631500),
2026-10-06 11:55:16 UTC, workflow_dispatch on challenge-8/research, full source
SHA1bc9cb718efc07315082334cded2d2362ecbbde1. Expected covers12/12 values and
6/6 tagged. Workflow exposure26a43bed5b162e542a4e0cc7cbf5ce08bd4d4bee;
default branch3d8c8c082a69dbb66c4ab566892e6be71d87a86d is a narrow cherry-pick
of those two workflow lines only, not a merge of research history. Dispatch
accepted once; no duplicate. Existing unrelated main Flux/RAPx push jobs are
not SmallSort research experiments. Await full proof/artifact outcome.

Result: completed SUCCESS at11:59:55 UTC. Full4448-line Actions log, complete
values/tagged stage logs and all12 artifact files inspected outside repo.
Both exact names verified individually, one harness/zero failures each;
run-sort4 acceptance guards pass. Values:0/267 failed,4 unreachable,12/12covers,
CBMC5.2731695s. Tagged:0/233 failed,4 unreachable,6/6covers,CBMC4.0439544s.
All six explicit functional/source-preservation posts SUCCESS. Each has22
properties directly attributed to real sort4: ten reference alignment and ten
pointer-validity checks plus two index-arithmetic checks. Copy source/dst
alignment, overlap, readable/writeable regions and null/dead/out-of-bounds
pointer checks pass. The four unreachable properties per harness are two
usize abs_diff overflow checks, formatting shift and is_aligned_to subtraction;
none is a post or cover. Three unsupported-operation guards per harness are
SUCCESS (unallocated-memory pointer reasoning/panic runtime/caller_location),
not failed unsupported operations. No compiler/refiner claim is substituted
for a Kani theorem; no VeriFast proof/refinement/leak result is asserted here.

Loop traces: sorted/stability three iterations, count/permutation/source
helpers four. Harness bound6 is not reached; no cutoff unwind property emitted,
no assertion suppression or no-unwinding-assertions flag. No target callback
panic in this pure domain. Source audit PASS; downloaded full std+proof artifact
independently equals git-show(sourceSHA,std)+git-show(sourceSHA,harness) byte
for byte. Target blob unchanged e555fce440872898e47fd5114f32eb15401d07df.

Tool: Kani0.67.0 at152c6a8c875d9886a67e229247b4826d6105ccfd,
nightly-2026-02-05,CBMC6.10.0,CaDiCaL3.0.0, unchanged default profile/args.
Runner193.07s/RSS1810908KiB; values164.64s includes cold build and24.20s std
compile; tagged28.39s includes24.00s std compile. CBMC total9.3171239s,
remaining runner183.75s setup/compilation/orchestration; whole job275s.
No budget bottleneck and no retry needed. Kani driver SHA256
9ae446cbe90b2eb9a394506d83e26624de675c3fd0eb80f5674ff4fd2d61d842;
CBMC05f93fd2f2ba6247b345f2bfb3d74c38402966515c65ff69f94adf7a674593f0.
All input/config SHA256 values are retained in SORT4-RESULTS.md.

Artifact digest evidence (SHA256): values log
c811768f20c673496abc66a41ddb11191e638e3cfbad2e3d6402ac8cf3da9691;
tagged log72bc73f98b983bd7bd88aa12f28a89429c6788545222000e2d3f6f4032006489;
combined logdbb566fd10ce158c10258fba6291e7c9af28f7b4b8da39ca89116efe3023573c;
environment31f1a56b493b6036fc6d6756736f5ca40bd2af19229d0cec0afbf515a2c3ded6;
injected full source3b9e2bf669ca332d9dc3968325ef763d6c79463ed5c9c5c09b043335862cbcb5.
Raw logs/generated source/build output are not committed.

Independent generic feasibility is STATIC: no established exact-source route
under unchanged26.09 at809de4596839b739dd999f9e462242c835e3af46;
existing actual tuple/HRTB evidence predicts the same callback boundary, not
an executed sort4 failure. No new falsifiable existing-semantics route justified
a probe, so no generic hosted diagnostic or semantic patch was made. Complete
source contract/caller ranges/ownership/five panic posts and architecture
question are in SORT4-CONTRACT.md and SORT4-SAFETY-DECISION.md.

UB classification: concrete default pointer/alignment/copy checks pass;
uninitialized fields avoided by construction, explicit uninit target profile
NOT RUN; immutable-store detector gap37397720683 unchanged; explicit validity
target profile NOT RUN, copy instrumentation unsupported37396688760 unchanged.
No generic safety/allocation/ownership/non-Copy/non-Freeze/ZST/stateful/panic
theorem or complete Challenge8 result follows. PHASE CLOSED; no active research
run, no later phase begun, insertion draft stays unapplied/unverified. Recommended
next decision: separately review tuple/HRTB capability plus full source-exact
normal/direct-unwind recovery and explicit overlap/ONE ownership contract,
trust/admissibility criteria and regression gate BEFORE implementation.
Closeout edits are documentation-only; successful source/harness/runner/tool
inputs remain unchanged and no cold rerun is warranted.


## 2026-10-06 — sort4 contract diagnostic card (before implementation)

Authorization: owner commit54485d632bfca9d69fee853bd6aa30bc330647c9 and explicit
request to complete SORT4-CONTRACT-PHASE. Entry tree clean, no active research
run; correct fork/branch. Target actual sort4_stable, std blob
 e555fce440872898e47fd5114f32eb15401d07df (unchanged).

Hypotheses: (1) coincident initialized [0,1,2,3] selects source0 to dst0 and
fails actual copy_nonoverlapping's memcpy overlap precondition; (2) shifted
source[0,4),dst[1,5) in initialized [0,1,2,3,4] gives [0,0,0,0] with every
individual copy disjoint and no default memory-check failure, but violates the
original multiset. Separate witness confirms output. Original unchanged
prove_sort4_values must verify 12/12 covers first. Raw pointers derive from
one mutable allocation for overlap cases; no conflicting live references;
original input snapshot taken by value. T=i32; F pure nonpanicking <.

Full diagnostic posts: control sorted exact old multiset and unchanged source;
shifted safety checks plus sorted output and concrete [0,0,0,0] witness, with
original multiset deliberately asserted as the falsifiable negative. Witness
returns backing[0..5]=[0,0,0,0,0], snapshot=[0,1,2,3], F unchanged; frame outside
allocation unchanged. Coincident claim ends at FIRST UB (first copy); no post-UB
values/normal ownership theorem inferred. Unwind is absent in this concrete
pure callback domain; target generic normal/all-five-panic resource posts are
separate open obligations in SORT4-CONTRACT. Diagnostic does not restrict the
unrestricted generic safety target.

Tool profile: Kani152c6a8c875d9886a67e229247b4826d6105ccfd,
Rust nightly-2026-02-05, scripts/run-kani.sh unchanged default checks, exact
harnesses serial --jobs1, unwind6 with assertions. No disabled checks or added
explicit uninit/valid-value instrumentation; known detector gaps retained.
Selection sort4_contract_diagnostics, budget90min incl cold setup/build (common
workflow preparation separately measured). Workflow dispatch only, hosted Linux.

Permitted coincident failures: ONLY ptr::copy_nonoverlapping::<i32>.
precondition_instance.N, description exactly "memcpy src/dst overlap", location
library/core/src/ptr/mod.rs:555:14. May include repeated instances of that
obligation; verify first call causally from source/all-false comparison route.
Shifted permitted failure: ONLY negative_shifted_original_multiset.assertion.N,
message "original multiset preserved", at that explicit harness assertion;
output/sortedness asserts and every other default check must pass. Exact
process exit1 and single failed harness required. Compiler/setup/unsupported/
unwind/timeout/nonmatching failure is INCONCLUSIVE, never accepted negative.
Witness must verify concrete output and 1/1 cover; baseline 12/12 covers.
Fail-closed parser retains all IDs/descriptions/locations/statuses and raw codes.
Source audit full original prefix plus checked-in baseline+diagnostics only;
record tool/config/harness/runner hashes and all case resources.

Outcome map: expected suite -> refine contract/close phase at architecture
proposal; runner/harness routine issue -> bounded fix and NEW exact-SHA run;
unexpected check/output -> investigate first actual cause and record revised
hypothesis (no suppression); semantic prerequisite/repeated unexplained failure
-> stop that route, complete independent docs. No new VeriFast run/application/
patch edit, source behavior change, later target or external publication.


Dispatch resolved: run37464581019, created2026-10-06T12:37:22Z,
source a082e0cf0c45d8bccf4c7df46eff9b84278a9f67, selection
sort4_contract_diagnostics/90min. Research workflow exposure cdf1b98; only its
two workflow lines cherry-picked to main0b54bf8. No research history merged.
Remote full SHA confirmed before dispatch; no duplicate active experiment.


### First diagnostic result and routine fix: run37464581019

Completed FAILURE,12:37:27–12:43:28UTC, sourcea082e0c,90min. Full hosted log
and all23 artifact files inspected. Source audit PASS, pins/source hashes
unchanged. Values control0/267 failed,12/12covers, accepted. Coincident raw1,
ONLY failed check54 ptr::copy_nonoverlapping::<i32>.precondition_instance.1,
"memcpy src/dst overlap" at core/ptr/mod.rs555:14, accepted. This is causal
first source0->dst0 copy on all-false ascending comparator decisions, not a
claim about values after UB. Shifted raw1 but failed memcmp.unwind.0 at
<builtin-library-memcmp>:25,1/168failed (167undetermined); witness raw1 same
memcmp.unwind.0,1/111failed (110undetermined),0/1cover undetermined. Neither is
an intended negative/result. The classifier correctly rejects both; its
rejection regression stops because genuine shifted input is not accepted yet.

Cause: own harness array equality lowers to byte-wise memcmp over16/20bytes;
unwind6 cannot cover that loop. This does not falsify the actual shifted-copy
hypothesis; the intended multiset assertion/output witness were not established.
Routine fix: exact same element-value equality expressed as a helper iterating
4/5 i32 cells, at unchanged unwind6. No target/functional baseline/tool/check/post
change, no suppression of memcmp or unwind checks. New source requires NEW run.
Card otherwise unchanged; this fixes fixture interference with the experiment.

Cost: suite271.83s,RSS1814676KiB; case timings control187.22s,coincident28.20s,
shifted28.38s,witness27.65s. Job361s; preparation78s separately. CBMC verification
control6.8403997s,coincident0.24010427s,shifted0.32779193s,witness0.28451073s (see raw logs for exact
values). No budget bottleneck. Kani0.67.0 driver9ae446cbe90b2eb9a394506d83e26624de675c3fd0eb80f5674ff4fd2d61d842;
CBMC6.10.0 hash05f93fd2f2ba6247b345f2bfb3d74c38402966515c65ff69f94adf7a674593f0.
Artifact11414508459 zipSHA256d92813b7a6e00278ccbed38b414ac75901b3588c82d0d64f363558b7bc152c96.


Retry dispatch resolved: run37465676476, created2026-10-06T12:46:11Z,
source6ff3d9f8f559555c17f722f500a1c7de16d9fe7d, selection
sort4_contract_diagnostics/90min. Only proof equality helper changed; exact std,
values/stability functional source, runner/classifier/checks/pins unchanged.
No overlap conclusion inferred from the first run's undetermined shifted checks.


### Second diagnostic result and diagnostic-label fix: run37465676476

Completed FAILURE,12:46:15–12:53:57UTC, source6ff3d9f,90min. Full log/artifacts
inspected, source audit PASS. Control0/267failed,12/12covers; coincident1/86failed
ONLY same actual memcpy overlap property; witness0/130failed,1/1cover, all-zero
backing and original snapshot assertions pass. Shifted1/170failed (4unreachable),
ONLY check30 negative_shifted_original_multiset.assertion.15 at actual
smallsort.rs1192:9. Every other default check passes/unreachable; trace and sorted
assertions pass. Thus manually audited location/condition matches predicted
multiset loss with individually disjoint copies. No memory UB inferred.

Automation still rejects the shifted case because Rust assert! with a message
is lowered to formatted panic and the pin emits description "This is a
placeholder message; Kani doesn't support message formatted at runtime", not
the predeclared unique message. Classifier correctly refuses this generic
placeholder; rejection regression stops at non-accepted genuine shifted input.
This is a harness diagnostic-label mismatch, not changed counterexample values.

Routine fix: same_multiset condition is now expressed by kani::assert with the
exact static string "original multiset preserved". Source inspection at pinned
Kani152c6a8c/library/kani_core/src/lib.rs185–191 confirms AssertHook accepts a
static str (declared by kani_lib macro for verification/core). No check removal,
post change, tool patch or classifier allowance for generic placeholder. Update
classifier's audited source spelling to that exact line; property ID/location/
message criteria otherwise unchanged. NEW exact-SHA run required. Hypothesis,
domain, target normal/unwind posts, pins,90min profile and decision map unchanged.

Cost: suite357.15s,RSS1812152KiB; control241.30s,coincident38.00s,shifted39.03s,
witness38.36s. CBMC10.390069s/.31998605s/1.0314885s/.6312619s respectively;
job462s, common preparation96s. No timeout/budget bottleneck or semantic failure.


Third dispatch resolved: run37466906281, created2026-10-06T12:56:04Z,
source7f96aa2f3262cf209ff3dcafd06e355e5590885b, same selection/90min.
No active predecessor; exact remote SHA confirmed. Pending fixed assertion label
and complete fail-closed suite/rejection gate. No hypotheses/checks suppressed.


### Final contract suite and architecture closeout: run37466906281

SUCCESS, source7f96aa2f3262cf209ff3dcafd06e355e5590885b,
sort4_contract_diagnostics/90min,12:56:09–13:06:10UTC. Full hosted log/all artifacts
inspected. Baseline values raw0,0/267failed,12/12covers; coincident raw1,1/86failed
ONLY check54 copy_nonoverlapping::<i32>.precondition_instance.1 at ptr/mod.rs555:14
"memcpy src/dst overlap"; shifted raw1,1/170failed ONLY check76
negative_shifted_original_multiset.assertion.15 at injected smallsort.rs1192:9
"original multiset preserved". Trace/sorted and every other default check pass
or unreachable. Witness raw0,0/130failed,1/1cover: backing[0,0,0,0,0], snapshot
[0,1,2,3]. Concrete all-false comparator route copies0→1→2→3→4 sequentially;
individual one-cell copy regions disjoint, original multiset lost, NOT an UB
finding in this i32 domain. Coincident first0→0 copy is first UB boundary;
no post-UB execution/ownership claim. Suite raw0; all4 cases accepted and44
malformed/nonmatching variants rejected by hosted classifier gate.

Each case22 actual sort4 reference/alignment/index checks. Final no unknown or
undetermined status/unwind failure. Unsupported guards SUCCESS. Typical4
unreachable arithmetic/format checks per case; shifted5 includes helper i+=1
overflow unreachable because key0 count mismatch returns immediately. Neither
assertions/covers/resources nor checks were weakened or removed.

Source audit PASS; independent downloaded full source equals git-show7f96aa2,std
plus unchanged baseline plus diagnostics byte-for-byte. Exact std blob remains
e555fce440872898e47fd5114f32eb15401d07df. Kani0.67.0/Rustnightly-2026-02-05/
CBMC6.10.0 unchanged pins/default checks/exact serial jobs1/unwind6. Target,
functional proofs, all VeriFast patches, scripts/run-kani.sh and configs unchanged.
No explicit uninit/valid-value/extra-pointer checks, no generic theorem inferred;
known immutable-write detector and copy validity instrumentation gaps retained.

Suite363.05s,RSS1811800KiB; cases253.57/35.90/36.46/36.73s;
CBMC9.252569/.30528224/.95132405/.58405024s, total11.09322553s;
rest351.96s setup/build/compile/orchestration. Common workflow preparation227s,
whole job601s. All3 jobs1424s; no budget bottleneck, no blind unchanged rerun.
Artifact11415738147 zipSHA2568cfd3a37812afb6b2ceda7358c4596dd5cde0af56b1c82a16df3b6cc6fddc5c6.
Exact all input/tool/raw-file hashes saved in SORT4-CONTRACT-RESULTS.md;
injected full sourceSHA256851ca4918a01e26577f50c1b2f11d51ce9d50af6f55c33fac2977030b8271431.

Contract refined: per-copy validity/non-overlap vs sequence preservation vs
functional ordering; optional uninitialized scratch/padding; one owner and
nondropped scratch representations; legal callback/F/frame effects; complete
normal and c1..c5 direct-panic resource posts; real len>=8/16 caller range map.
This is proposed sufficient research contract, not accepted strengthening of
short public SAFETY comment or verified caller composition.

Read-only architecture review: choose explicit source-defined normal/direct-
Continue recovery continuations, one c1-only generic full-resource gate first.
Historical tuple/HRTB/strict-cut patches do not implement full direct-unwind
recovery; strict-cut changes kernel AND translator and earlier unwind post
returns debt. Clean pinned VF source review additionally finds initialized-dst
copy summary incompatible with uninitialized scratch and no established actual
hint::select_unpredictable pointer helper/model proof. Repeated five-call sharing,
ZST/padding/provenance and scratch ownership/access transport remain named gaps.
First prospective experiment, profile/dependencies/full normal/unwind posts,
positive/negative matrix and trust/admissibility Go/No-Go are in
SORT4-SAFETY-DECISION.md, explicitly NOT AUTHORIZED.

Independent review corrected cross-copy generic validity wording, full-epoch
normal recovery position and current scratch init after legal callback effects.
No new VF run/build/apply/patch edit or model/kernel/refiner implementation.
PHASE CLOSED at owner decision: approve/reject the narrow exceptional-continuation
trust/design and implementation gate plus clarified sufficient contract.
No later sort/insertion phase/external publication, no active research run.
Closeout docs only need static review, not another cold verification run.


## 2026-10-06 — sort4 no-patch feasibility (source review, NO RUN)

Owner explicitly opened [SORT4-NO-PATCH-PHASE](SORT4-NO-PATCH-PHASE.md) from
`11e8ead9389cc95fc7d13a24d0c28d7d2d6ba3c5`; earlier phases stay closed and
SORT4-SAFETY-DECISION's patched experiment is excluded. Entry local/remote research
heads match, tree clean, origin intended fork, main0b54bf8; Actions in-progress/
queued lists empty. Runtime blobs unchanged: smallsort e555fce440872898e47fd5114f32eb15401d07df,
hint fe59166363b9cc049c0d48f4349f4dc9c0e458b8.

[Assessment](SORT4-NO-PATCH-ASSESSMENT.md) preserves exact sources/profile identity,
obstacle matrix, historical run domains, static observations/inferences/unknowns,
and decision gate before any implementation. Official26.09 source809de459 was
compared read-only with released26.10 sourcef76012fb518703b1d98e243ac4f487f16877cfcb.
26.10 linux asset611766606,97,804,993bytes, release API SHA256
5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd,
nightly-2026-09-25; binary not installed/download-hashed/run. Tuple prelude identical;
HRTB bound_regions filter, direct Continue return and typed initialized-dst copy
contract persist. Trait-name canonicalization and mutable-slice contract changes
are insufficient for the full generic c1 gate. Selection helper proof remains open.
Actual target export/refinement with new nightly NOT RUN, not a reported failure.

Alternative checked annotation placement reuses established normal recovery but
no tuple/HRTB/full direct-panic mechanism was identified. Kani is the one detailed
approved/integrated alternative, pin152c6a8c/Rustnightly-2026-02-05: prior actual-body
concrete functionality does not supply universal generic ownership/effects/unwind
or close measured CopyNonOverlapping validity/immutable-write gaps. No alternative
installation/integration/run. No change to pins/prelude/parser/translator/kernel/
memory/refinement, std runtime/signatures, existing proofs/checks or workflows.

Decision: no new falsifiable candidate; do not repeat the understood callback
failure under another label or dispatch only for the toolchain bump. No experiment
card advanced to implementation; no new positive/negative/covers, no run ID/URL,
0/2 permitted runs used, no compute cost. Historical runs remain evidence only;
latest proof run37466906281 is unchanged. Local validation: git diff --check and
lightweight document/link/source-diff review only. No executable proof/build/tests.

CLOSED at owner decision: recommended next task is bounded clarification/review
of the full separated-range/single-owner scratch safety contract. Generic coverage
unchanged. All no-patch routes are not proved impossible; undiscovered checked
mechanisms,26.10 source compatibility and whole generic proof obligations remain
unknown. No custom verifier development selected/authorized. No active run or
unfinished proof edit; subsequent experiments need separate owner authorization.


## 2026-10-06 — remaining-tools screening and RAPx READY checkpoint (NO RUN)

After the no-patch closeout, the owner requested a short review of the remaining
approved tools for generic Rust, pointers and panic; then accepted the RAPx
candidate and asked to update repository documentation and provide the next
agent prompt. Entry/remote research HEAD was
`b7416c18035c714258e2a476eebdfa1609f7f66c`; current inspected research Actions
were all completed, latest run37466906281. The std SmallSort blob is still
`e555fce440872898e47fd5114f32eb15401d07df`.

[ALTERNATIVE-TOOLS-ASSESSMENT](ALTERNATIVE-TOOLS-ASSESSMENT.md) records the
source-based comparison: ESBMC8.5 consumes Kani-generated GOTO in this integration;
Flux's pinned checker leaves cleanup checking unimplemented; KMIR0.4.226 lists
monomorphized types, partial pointers, no panic unwinding and no user Drop.
RAPx0.7.50 has relevant generic layout, copy-contract and selection mechanisms,
but unrestricted callback effects/direct-panic state are unestablished.
Its concrete-ZST alignment shortcut is a source-level suspected coverage gap,
NOT a reproduced false SOUND result. Official sources and inspected upstream
revisions are pinned in the assessment. No broad all-tools impossibility claim.

The owner-approved next task is
[RAPX-APPLICABILITY-PHASE](RAPX-APPLICABILITY-PHASE.md), status READY, not started:
A alignment/ZST, then B generic memory and required UB categories, then C callback
effects and normal/direct panic. Exact RAPx0.7.50/nightly-2026-02-05 profile;
installed package/source identity must be audited. Maximum four hosted runs,
90 minutes each including setup, one active at a time; used0/4. Critical misses
or essential unsupported behavior stop later gates. Even all-green fixtures stop
at an owner decision before any full target proof, upgrade or verifier patch.

This checkpoint changes only the assessment/phase and current status, roadmap,
index, coverage context and this log. No proof fixture/runner/workflow/pin/std
change, installation/build, semantic patch or dispatch. Latest proof evidence
and all established coverage remain unchanged. Contract admissibility stays
independent and unresolved; no external contact or publication is authorized.
Validation is static document/diff/link/profile consistency review only.


## 2026-10-06 — RAPx gate A experiment card (before implementation)

Owner resumed the approved phase at documentation commit
`ad54f67d655c4106762016fba47534c58601f3ec`. Entry tree clean; origin is
Tiramisu-Cake/verify-rust-std; branch challenge-8/research fast-forwarded;
no queued/in-progress Actions. No unrelated changes.

- Actual obligation: alignment of both pointers at the four
  `copy_nonoverlapping` operations in actual `sort4_stable<T,F>`,
  smallsort.rs653–656, std blob e555fce440872898e47fd5114f32eb15401d07df.
- Falsifiable hypothesis: unchanged RAPx 0.7.50 generates and proves valid
  alignment obligations and rejects misalignment, including a size-zero,
  align-eight type. Source-level zst_guard concern is not yet a reproduced miss.
- Diagnostic domain: isolated concrete ZST align8 and non-ZST u64 copies,
  count one, aligned positive and independently source-/destination-misaligned
  negatives. No reference is constructed from a misaligned pointer before the
  copy. No manual assertion replaces the automatic alignment check.
- Deliberately partial posts: valid copies return without UB, source storage
  retained, writable scratch receives a representation and is not independently
  dropped. These fixtures do not prove arbitrary T/F, ownership transport,
  comparator effects, sorting or unwind.
- Full target yardstick (SORT4-CONTRACT): unrestricted valid T/F, initialized
  four-source storage and possibly uninitialized writable separated scratch,
  legal provenance/borrows and exactly one owner. Normal: current V5 retained,
  scratch initialized with pi(V5) replicas, current callback/frame/storage and
  no borrow debt. For each panic k=1..5: current Vk/Qk/Hk after legal callback
  effects, source ownership recovered, scratch current initialization state,
  no sort4 writes, no rollback, no leaked borrow/resources. Ordering premises
  are separate; no Copy/Freeze/purity/no-panic premise for safety.
- Frozen profile: exactly Cargo rapx '=0.7.50', --locked, explicit
  nightly-2026-02-05 for install and analysis, upstream reviewed
  7d61d9377033c48a4df8954f34cc076e97a93816. Audit package VCS/source, checker,
  call model, contracts, dependency lock, executables and sysroot. No patches.
  Fixtures use toolchain std, not extracted repository std; no exact-body claim.
- Expected: selected valid body SOUND with actual copy checkpoint and proved
  source/destination alignment; each negative unproved/disproved alignment at
  that copy. UNSOUND/Unknown/unsupported/setup/missing checkpoint are distinct.
- Decision: reproduced critical miss -> NO-GO, stop B/C; required unsupported
  behavior -> stop; ambiguity/setup/unknown -> INCONCLUSIVE or one evidence-backed
  shared technical correction; all sufficient A evidence -> allowed gate B.
- Selection rapx_applicability, explicit gate A, one hosted run at most 90min
  including setup, maximum four runs overall with one shared correction. One
  active run; no local build/verifier/test execution. Record exact SHA/run and
  all predicates, paths, logs/artifacts/costs after dispatch.

Dispatch resolved: [run37492790456](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37492790456),
created 2026-10-06T16:04:30Z, source
`b55ae850d1cef67ddbcd02d8d97b4763c9c4a9f1`,
workflow smallsort-research.yml / proof rapx_applicability / rapx_gate A /
budget_minutes90. Remote full SHA matched before dispatch; no active relevant run.
Direct branch dispatch succeeded, so no default-branch workflow change was needed.
Budget used1/4; no B/C implementation or dispatch. Static review only on server:
`git diff --check`, `bash -n`, code/YAML reads; no local compile/verifier/test.

### Run37492790456 result and shared technical-correction card

Completed FAILURE, job 16:04:37–16:08:18 UTC (221s), runner exit2.
Exact RAPx0.7.50 Cargo package successfully installed with --locked (reported
release compilation1m24s). Pinned rustc1.95.0-nightly commit
`db3e99bbab28c6ca778b13222becdea54533d908`, hostx86_64-unknown-linux-gnu.
Archive checksum/VCS/lock match the phase. First causal failure is runner setup:
`rapx --version` makes the direct compiler driver parse empty RAPXFLAGS, prints
usage and exits2; src/bin/rapx.rs reads options from RAPXFLAGS, not argv.
Installed-source comparison, layout reporter, target preparation, six analyses
and classifier NOT RUN. No alignment hypothesis tested and no detector miss.
Full log and ten artifact files downloaded/read outside repository.

Shared technical correction, before implementation: retain the same six cases,
full target normal/five-unwind yardstick, exact pins/checks/flags/resources and
90-minute budget. Change direct driver version invocation only to
`RAPXFLAGS=--version rapx`; Cargo wrapper version invocation remains explicit
`cargo +nightly-2026-02-05 rapx --version`. Falsifiable setup hypothesis: correct
argument channel obtains version0.7.50 and permits unchanged identity/target/
alignment diagnostics to execute. Expected stage: executable version audit.
No trusted semantics, std source, fixture premises or detector checks change.
Use the one shared correction run; gate-A miss -> NO-GO/stop, ambiguity/another
setup issue -> INCONCLUSIVE/stop (no second technical correction), sufficient A
pass -> planned gate B; C only after B. New source SHA and NEW dispatch required.
Budget used1/4; reserve the shared correction; B/C unused and still gated.

Shared correction dispatched as NEW [run37493697524](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37493697524),
created2026-10-06T16:11:16Z, source
`772def3ce7e5e3585ac0c9a909f97afbcdb9a821`; remote matched; prior run
completed before dispatch. Selection/gate/budget unchanged. Used2/4, shared
correction consumed; planned B/C slots cannot be used as more gate-A retries.
Prior full Actions log SHA256
`3e3fb0dc237c6724c083774524fb18996f712d8dfdf8da6a0e7f5d30800b03db`;
artifact11426930280 zip digest
`a149d4858471a0f6ac58de351120abeb452303916cc76d8b51280c0b70d1122d`,
ten files. Full read-only audit confirms only setup failed, no target/negative.


### Run37493697524 final result — phase CLOSED / INCONCLUSIVE

Source772def3ce7e5e3585ac0c9a909f97afbcdb9a821; A/90min; FAILURE/exit1;
job16:11:22–16:18:02UTC400s, Prepare runner306s, install/identity step81s
(release build1m04s). Both version queries0.7.50 passed; binary/package/lock/
sysroot identities recorded in RAPX-APPLICABILITY-RESULTS.md. No lock-update
warning; all104 compiled name/version entries match the saved154-package lock.

First causal failure: runner assumes registry `.cargo-checksum.json` exists;
FileNotFoundError at16:17:58.205UTC. Installed registry source directory found,
but source comparison not reached. This is setup failure, not checksum mismatch,
unsupported operation or semantic failure. Layout/MIR/target prep/all six A
analyses/classifier NOT RUN, zero paths/obligations; B/C NOT RUN because A did
not pass. Source-level ZST concern remains unreproduced. No generic coverage.

Full log SHA256 c4ee3f87c3d2f4e7bc0b508ca3186f539baf49e4e5c8b62b8e4edcbe0f0ea86f;
artifact11426617314 (11 files,16573bytes) zip SHA256
314f42868159afb7ce54b0197c56a8d8d0d4a4a29b3bdde56e985f13cc36ac20.
Both full logs/all21 files inspected and kept outside repo. No timeout/OOM,
no per-case RSS/time because cases never began. Noncausal warnings are Actions
Node deprecations/default-branch git hints. No new active run or proof draft.

Used2/4: planned A plus single shared correction. Do NOT repurpose unused B/C
slots as A retries. Phase closes INCONCLUSIVE; a new narrow preparation/A
retry requires an owner decision. Proposed correction: byte-compare exact
archive to installed source rather than require optional checksum metadata;
not implemented or dispatched. No verifier patch/upgrade/full-sort4 authorization.
Results/status/coverage/roadmap/index updated; documentation-only closeout
requires static validation, no extra hosted verification run.


## 2026-10-06 — new owner-authorized RAPx gate-A continuation, card before edits

Entry HEAD/local/remote `1fc89566800f8152d218de7f9a757f665626f220`; tree clean,
origin Tiramisu-Cake/verify-rust-std, branch challenge-8/research, no active or
queued Actions, no newer/unrelated changes. Owner explicitly resumes only
preparation and six existing A controls. Separate budget0/4 NEW runs,90min
including setup each, one active. Ordinary runner/setup/classifier corrections
are autonomous within the new budget; historical two attempts remain preserved.

- Obligation: source/destination alignment at actual std sort4_stable's four
  copy_nonoverlapping operations, smallsort.rs653–656; std blob
  e555fce440872898e47fd5114f32eb15401d07df unchanged.
- Hypothesis: after correct stock-profile identity audit and true verification
  (without debug-contracts early return), RAPx distinguishes valid/misaligned
  pointers including concrete align8 ZST, at intended copy Align predicates.
- Domain/resources: same six isolated annotated functions. ZST aligned/source+1/
  destination+1, no earlier invalid reference; ordinary u64 copy uses distinct
  initialized allocated backing, tested pointer byte offset1 only, other aligned.
  Count1; zero-byte ZST ranges do not overlap. No manual alignment assertion.
- Partial posts: valid operation retains source and initialized scratch replicas
  with one owner; these concrete controls do not prove generic T/F, ownership
  transport, ordering, current callback effects or unwind.
- Full target yardstick: unrestricted valid T/F, four initialized source slots,
  possibly uninitialized separated writable scratch, legal provenance/borrows
  and exactly one ownership sequence. Normal: current V5 retained, scratch
  pi(V5) replicas initialized, current callback/frame/storage recovered, no
  borrow debt. Each panic k=1..5: current Vk/Qk/Hk after legal callback effects,
  source ownership and raw scratch current initialization recovered, no sort4
  writes, no rollback/leaked resources. Ordering premises remain separate; no
  Copy/Freeze/purity/no-panic premise for safety.
- Profile unchanged: RAPx '=0.7.50' --locked, nightly-2026-02-05 explicit for
  install/analysis, archive SHA e210328ce0e6c417ecf0498118ca0738f80851e9f2d204432a095ad703f8c0b8,
  VCS7d61d9377033c48a4df8954f34cc076e97a93816. Check archive/VCS/lock/version,
  byte-compare installed package source to archive and relevant upstream; no
  required .cargo-checksum.json. Fixture calls toolchain std, not repository core.
- Cases: positives actually analyzed SOUND with both Align predicates proved.
  Negatives require failed tested Align at its copy checkpoint, other Align
  proved; SOUND with incorrect discharge is a miss. Unknown, unsupported, absent
  or unmapped target/path/obligation and setup/frontend/timeout remain distinct.
- Preparation: separate target list, per-case contracts (--debug-contracts) and
  per-case verification WITHOUT debug-contracts; classifier receives the paired
  logs and binds function/checkpoint/argument/property/path. Hosted tests reject
  printed-only, wrong-target/checkpoint/path/argument, missing/unknown/unsupported
  and contaminated evidence. No negative fixture program is executed.
- Decision map: routine pipeline error -> evidence-backed repair and NEW run
  within4; substantive miss or essential semantic gap -> scoped NO-GO/stop;
  unknown/ambiguous or budget exhausted -> INCONCLUSIVE/stop; sufficient A pass
  -> READY FOR NEXT DECISION (A only)/stop. B/C remain NOT RUN regardless of A.
- Selection rapx_applicability, rapx_gateA, budget_minutes90; no other suite,
  upgrade/model/contract change or local compiler/verifier/test/extractor.

Final pre-dispatch static audit: pinned driver.rs715 returns after contract
printing; real checks now omit that flag. Archive/upstream full src comparison
is byte-identical (204 files); runner compares installed full src and build.rs,
Cargo.toml and Cargo.lock independently of Cargo checksum metadata. Isolated
install root, exact executable versions, source manifests, raw per-stage exit
codes and separate contract/verification logs are retained. Hosted-only classifier
tests run before controls. Source copy locations: zst.rs14/31/48 and
u64_controls.rs9/24/39, respectively aligned/source-offset/destination-offset.
Full runner path, wrapper/filter behavior, diagnostic renderers, timeout/trap,
artifact paths and layout-only program statically reviewed; bash -n and
git diff --check passed. No executable local validation.

First new dispatch: run37508216376, source
cbbbb430d0091191141819843b3c8b476d0ff9f6, created2026-10-06T18:02:30Z,
workflow_dispatch/rapx_applicability/A/90min, GitHub-hosted ubuntu24.04.
Normal push and remote full SHA confirmed, no other active run before dispatch.
New budget1/4; monitor the specific run. Historical two remain outside budget.

Run37508216376 completed FAILURE, job18:02:35–18:06:14UTC219s.
Package version/archive/VCS/lock and full installed-source comparison to archive
and pinned upstream PASS. Hosted classifier tests11/12 pass; one malformed-log
test accidentally removes only the row's suffix, concatenating its remaining
RAPx prefix with the next line. Fail-closed parser returns missing/unparsed
checkpoint rather than the intended summary-count mismatch. This is a test
preparation failure, no alignment result. Layout/preparation/MIR/six controls
NOT RUN. Preserve full log SHA256
ac8047b8d338fb951f961356018b76498f9c4f9258888c3847c1efe34f34c2dc;
artifact11432717926,41files,47484bytes, zip SHA256
4ef1061cfacce2726fe51bc0503fb8c1a37c0dfad065285856b6da097cf342fc.

Next-run card before repair: same actual std copy obligation, six concrete
domains, full normal/five-panic yardstick, frozen package/toolchain/predicates
and A-only decision map as above. Correct synthetic row deletion to remove the
entire prefixed log line and review other test mutations together. No classifier
weakening or semantic/fixture/std change. Falsifiable preparation hypothesis:
the missing-summary-property sample is syntactically a log and is rejected at
summary/detail count mismatch; all12 hosted classifier tests pass. Only then
run actual layout/target preparation and six paired contract/verification cases.
New budget permits run2/4,90min including setup, no active run now. A substantive
result stops before B/C; no retry of old source, no local executable validation.

Second new dispatch: run37508888778, source
929ea803ffff1c4f534716cc8c37bbbfa06a5960, created2026-10-06T18:07:39Z,
rapx_applicability/A/90min. Only malformed synthetic deletions repaired; all
other test mutations reviewed, classifier/fixtures/profile unchanged. Static
checks pass; normal push/remote full SHA/no other active run confirmed. Budget2/4.

### Run37508888778 final result — continuation CLOSED / NO-GO

Exact source929ea803ffff1c4f534716cc8c37bbbfa06a5960; workflow_dispatch,
rapx_applicability/A/90min; commands SUCCESS, gate A NO-GO. Job18:07:43–18:10:57UTC
194s; runner183s including recorded preparation. First new job219s; total413s.
No timeout/OOM. Package/archive/VCS/lock/executable versions and complete
installed src/archive/upstream comparisons PASS. Frozen exact RAPx0.7.50,
nightly2026-02-05 and std blob unchanged. Release install84.84s/~1.52GB RSS;
actual cases1.06/.70/.70/.72/.75/.75s/~243–246MB RSS. All executable work hosted.

Classifier rejection tests12/12 PASS, layout x86_64 Z.size0/align8,u64.size8/align8.
Prepare-targets and six separate contract calls ran; six true verification
commands omit debug-contracts, all exit0. Every exact local function has one
copy checkpoint and one path, eight primitive records:48 total. Positive ZST
bb0/DefId43 and u64bb2/34: all8 Proved,SOUND. ZST source-negativebb3/44 and
destination-negativebb3/45: both Align indexes0/1 ProvedByRule, all8 Proved,
SOUND. Hosted optimized MIR retains raw aligned local→u8 wrapping_add1→Z and
copy count1 at bb3, no prior invalid reference/access. Thus respective Align
violation at an 8*n+1 address is a **confirmed critical SOUND miss**, despite
zero copied bytes. Pinned check_align zst_guard shortcut explains the false proof.

u64 source-negativebb4/DefId37: Align0 Failed,Align1 Proved; ValidPtr component3
Unknown,NonOverlap6 Failed,UNSOUND(3). Destinationbb4/40: Align0 Proved,Align1
Failed; ValidPtr component5 Unknown,UNSOUND(2). Expected Align detection is
observed separately from incomplete/unrelated obligations, not a full case pass.
Total43 Proved/3 Failed/2 Unknown; Align10 Proved/2 Failed. No unsupported/missing
target in raw verifier evidence. Paths and exact obligation mapping are in results.

All six raw classifier JSONs remain CONTRACT_EVIDENCE_MISSING_OR_UNMAPPED;
all_expected=false, never counted as green controls. Real renderer omits crate
prefix, contracts print std::ptr vs checkpoint core::ptr; ValidPtr compound
expansion yields8 checks and grouped origin summary. Synthetic tests assumed
other forms; static audit missed those assumptions. Full manual paired-contract/
DefId/checkpoint/property/optimized-MIR review supplies the result independently.
No classifier rewrite or confirming run after the decisive miss, no untested
repair presented as complete. Raw automatic outcomes and this limitation retained.

Full log SHA256 c3820617663f69f9018cf558bd7cdbaa46b972f050d57a77f486f56d19c428ad;
artifact11434810024,2832822bytes,3216files(3012MIR/96DOT/108other),zip SHA256
d9c5300fd4ac5c6267a8516e33ff4a8ba713795dc9e393e6eff3d8f2a71edf38;
manifest SHA2561dd4f1e5bfddc28bc83bbd7f4b11cdc133720210a6f0c448d3389e85ee5466fb.
Both new full logs/artifacts inspected outside repository. Noncausal install
PATH/git hints/Actions Node deprecations distinguished from Failed/Unknown rows.

STOP at2/4 NEW runs, no active run or pending proof draft; B/C NOT RUN.
Unused budget cannot authorize more experiments after the critical miss.
NO-GO is scoped to stock RAPx0.7.50 alignment detection for concrete align8 ZST;
not a std runtime bug, generic proof, tool-universal claim or Challenge8 solution.
Full current-state normal/five-panic target contract and ordering separation
unchanged; no generic uninit/raw ownership/callback/unwind coverage gained.
Results/STATUS/phase/index/roadmap/coverage updated; documentation closeout
requires only static checks. Any later parser replay/tool change/new route needs
a separate decision; no patches/upgrades/full-sort4/external publication.

## 2026-10-06 — owner-authorized automatic evidence replay, card before edits

Entry3e628c6a2d1197c069abf46fba33b3453c2de57f matches local/remote, branch
challenge-8/research, origin fork verified, tree clean, no active Actions/newer
or unrelated changes. New scope only classifier/tests/docs/minimal manual
replay mode; budget0/2 NEW hosted30min runs, one active. Semantic gate remains
NO-GO, no RAPx install/build/verification, no negative program execution or B/C.

Input fixed to original run37508888778/source929ea803ffff1c4f534716cc8c37bbbfa06a5960,
artifact11434810024/zip SHA256
d9c5300fd4ac5c6267a8516e33ff4a8ba713795dc9e393e6eff3d8f2a71edf38, downloaded
read-only and SHA verified. Old paired logs/JSON and manual conclusion immutable.
Falsifiable processing hypothesis: actual renderer, DefId/checkpoint/path and
ordered Align(src/dst), eight primitive/compound-origin records can be strictly
mapped, reproducing two PROVED_VALID, two SOUND_MISS, two targeted Align Failed
with separate other Failed/Unknown and no whole-case pass. Deliberately corrupt
authentic logs must be rejected at missing/wrong/unmapped/inconsistent evidence;
synthetics alone are insufficient. Command success, complete evidence parse and
semantic NO-GO must remain distinct in automatic aggregate.

Actual std yardstick unchanged: sort4 copies653–656/blob e555fce440872898e47fd5114f32eb15401d07df;
unrestricted T/F, one source ownership sequence, possibly uninitialized disjoint
scratch. Normal retains current V5 and initializes pi(V5) replicas; each of five
panics preserves current Vk/Qk/Hk/source ownership/raw scratch initialization
after legal callback effects, no sort4 writes/rollback/debt/leaks. Ordering
premises separate. Replay proves none of these target posts; it only processes
existing concrete detector evidence on stock RAPx0.7.50/nightly2026-02-05.
No tool/std/contract semantic change; processor is untrusted evidence handling.

Selection rapx_evidence_replay/budget30; new exact processor SHA identifies new
outputs independently of original verifier source. SHA-check archive/run/artifact
metadata, preserve original outputs, test and classify hosted. Rejected evidence
or command failure -> repair within2-run budget, no fabricated result; fully
parsed authentic evidence with ZST misses -> automatic NO-GO and STOP. No
coverage gain, new verification, patch/upgrade/full-sort4 or external publication.

Pre-dispatch static review: replay selection skips the existing bootstrap job;
its separate hosted job has hard30min cap and read-only contents/actions token.
Only checkout, fixed-artifact download/hash/metadata validation, Python tests and
classification execute. No Cargo/RAPx invocation or dependency installation.
Original extracted input is read-only; old JSON copied to historical output,
new records written separately. Actual callee signature, all eight indexed
diagnostics, compound-origin summary folding and verdict counts are matched;
exact frozen-case DefId/checkpoint/path metadata is explicitly scoped to the
original source. Mutations use unique authentic-log anchors. JSON roundtrip
aggregate consistency is tested. bash -n and git diff --check passed locally;
no executable classifier/test/extractor validation on the server.

First replay dispatch: run37513897141, processor
1c0b5171375c1198ef0e94b6a26d5e3a13cf1a15, created2026-10-06T18:46:37Z,
rapx_evidence_replay/30min. Full remote SHA confirmed and no other active
research run; budget1/2. Original verifier experiment is not rerun.

### Replay37513897141 closeout — reproducible automatic NO-GO

Processor1c0b5171375c1198ef0e94b6a26d5e3a13cf1a15, workflow_dispatch,
rapx_evidence_replay/30min; job18:46:45–18:46:57UTC12s SUCCESS. Original
verification/bootstrap job SKIPPED, no steps. Input run37508888778/source929ea803/
artifact11434810024 checked against exact archive SHA and hosted metadata/source
card; no RAPx install/build/verification or new semantic experiment.

Hosted authentic six-log replay/mutation/aggregate tests9/9 groups PASS,
2.964s suite (3.06s wall,RSS32592KiB). Strict exact target/DefId/checkpoint/path,
signature/arguments and eight-record/compound-summary/verdict checks pass.
Mutations reject missing/duplicate/unparsed records, wrong fn/DefId/callee/srcdst,
bb/path/property, vm-check and summary/verdict contradictions, warnings and
unsupported paths. JSON serialization/aggregate consistency verified hosted.

CLI-produced records and automatic JSON aggregate: zst/u64 aligned PROVED_VALID;
both ZST negatives SOUND_MISS; both u64 negatives
INTENDED_ALIGN_DETECTION_WITH_OTHER_UNPROVED. Source Align#0 Failed plus
NonOverlap#6 Failed/ValidPtr remainder#3 Unknown; destination Align#1 Failed plus
ValidPtr remainder#5 Unknown. No whole-case promotion. All six evidence_complete,
43 Proved/3 Failed/2 Unknown. commands_succeeded=true, evidence_parsed=true,
gate_outcome=NO-GO; replay command itself exits0. Full report has exact original
source/artifact and processor/replay identity, not only expected classifications.

Artifact11436755991,27files/20371bytes,zip SHA256
7c475ec07ead8d4d83441d9d41c50bab4b067b6d05e7595c5eedbd351cea032b;
automatic-gate-a-report.json SHA256
b60eac77f855d955ff48586eb90b05c9d2fcad8c642a6836f5ddd8a869c1cf91;
manifest8470abd711b10ba038f87572a5c711b67fbfb09e383eb17a0044f78fd653ee9e;
full logbf64af71bb16775c98ddea93d1683e487f9e1851d86ee2081f75d454c8972e9f.
Replay script elapsed5s; no timeout/OOM. Full log/all27 files inspected outside
repo; seven historical JSONs cmp byte-identical with original artifact. Source
logs/MIR/manual conclusion remain historical; new data never overwrites them.
Only noncausal Actions Node deprecations/git hints. Local static bash -n/diff
checks only; all executable classification/tests hosted.

STOP at1/2 new30min replay runs, no active run/pending implementation. Results,
STATUS, phase, coverage, README and PLAN updated; closeout is documentation only.
Automatic NO-GO agrees with earlier semantic/manual result, adds no generic/std
proof or detector coverage. No second run needed, no B/C/tool patch/upgrade,
new verification/full-sort4 or external publication authorized.

## 2026-10-06 — documentation-only sort4 admissibility review

Owner explicitly authorized a separate source/primary-source analysis,
documentation, commit and push from expected/actual research HEAD
826d74b45546f9ce1319e2cd4cac8b6d42a2f41f. Entry tree clean; origin fetch/push
is Tiramisu-Cake/verify-rust-std; local and remote challenge-8/research heads
match. No in-progress or queued Actions. Newer run37518141083 is unrelated
main/schedule/Subtree Update, completed SKIPPED; no research result superseded.
Read AGENTS, STATUS, PLAN/runbook, contract/diagnostic/no-patch/tool-screening/
RAPx reports, Challenge8/rules and actual sort4/callers/ptr/cell/slice docs.
Std blob e555fce440872898e47fd5114f32eb15401d07df unchanged.

Created [SORT4-ADMISSIBILITY-REVIEW](SORT4-ADMISSIBILITY-REVIEW.md): assumption
ledger with exact primary/source basis, S/F/full-resource roles and declared vs
caller-established vs clarification status. Local copy non-overlap is required
at653–656; full four-slot separation is sufficient, not proved necessary for
each overlap/permutation/type. Existing run37466906281 retains coincident-copy
UB boundary and shifted i32 multiset loss/zero-output witness as distinct claims.
No new experiment/classification. Preservation of unread source values alone
does not imply the stronger unchanged-all-source post.

Caller len>=8/16 bounds and distinct v/output/temp MaybeUninit routes statically
support sufficient premises. Exclusive SrcOwn/Shadow/no proof debt are the chosen
accounting protocol, not all minimum Rust no-UB requirements. Duplicated bytes
do not supply a second independent drop owner; legal leaks/callback resource
replacement remain allowed. No Copy/Freeze/purity/no-panic restriction is added
to safety. Conditional ordering/key-preservation assumptions stay separate.
All c1..c5 direct callback panic boundaries at626/627/641/642/649 precede this
invocation's copies; current callback/interior/frame effects persist, including
effects of panicking call. Earlier caller invocations may already have written
scratch; no full caller rollback/resource proof is inferred. Later scratch
access/merge/ownership transport and all generic resource proofs stay open.

Official clarification check: published Challenge8/general rules, issue56 and
all4 comments, PR57 discussion/reviews, PR576 discussion/reviews, PR701 metadata/
review list, scoped primary-source searches. Organizer qinheping's
issuecomment-2611410906 calls for upstream correction of insufficient comments
and considers primitive/default-order functional proofs; it does not answer
sort4 overlap/scratch domain or relax unrestricted safety. No explicit answer
to our precise question found in inspected sources; search is not exhaustive.
Read no other solution proof code. Draft question with pinned body, diagnostics
and caller-audit links recorded only; no external message/publication.

Static technical limitation: historical run-rapx-applicability.sh:219 invokes
classifier tests without their now-required --evidence-dir; corrected classifier
is scoped to six exact original-source DefId/checkpoint/path cases. Not repaired
or executed. Separate resumption requires evidence/interface/scope preparation
review. Historical saved-data replay37513897141/processor1c0b517 and two ZST
SOUND_MISS remain CLOSED/NO-GO; B/C NOT RUN. No unused budget reopened.

Removed stale STATUS next-action instruction to dispatch gate A; current
authorization/closeout now permits only this analytic documentation scope,
followed by STOP. PLAN adds completed stage1f and removes present-tense RAPx
execution permission. README indexes review; coverage clarifies claim boundaries
only. Existing reports/journal/source/contract/proof/tool/workflow preserved.
Validation: static Markdown local-target/reference/anchor review and
git diff --check; no executable research tests, builds or Actions dispatch.

**CLOSED — admissibility unresolved, no new coverage.** The sufficient research
contract is motivated for existing callers, but is not organizer-accepted as the
complete standalone target domain. Recommend owner decision on seeking the
drafted clarification; its answer determines a separately authorized contract/
proof decision. No active run or proof draft. No automatic next experiment.

## 2026-10-06 — owner adopts explicit sort4 contract after C-source authority check

Owner chose to settle the specification question by stating the premises
explicitly, as in the C work, subject to checking that work's authority.
Entry remote research head was
`43bc758625157febb496804f346b7433f1a21d5a`, tree
`88cdd4a29d13e40d3384d606d236479716cc4ba7`. Files read at that immutable head;
edits prepared separately and applied through the fork's Git data API with
an expected-head lease, not a force update. No local git checkout was present.
The latest ten Actions runs were completed; latest research evidence remained
replay37513897141. Source blob e555fce440872898e47fd5114f32eb15401d07df unchanged.

[Authority assessment](C-VERIFICATION-ARTIFACTS.md#authority-and-separation-precedents):
publisher/conference primary records confirm P1's VMCAI2019 peer-reviewed chapter,
DOI10.1007/978-3-030-11245-5_8. Its versioned author text supplies the inspected
separation/per-call example. Fraunhofer README/license and pinned ACSL merge
contract/results support a distinct institutional reference-artifact claim;
VeriFast's pinned mergesort example is a supporting tool artifact. No ranking,
unverified peer-review label for artifacts or independent proof replay claimed.

[SORT4-CONTRACT](SORT4-CONTRACT.md#adopted-domain-and-caller-obligations) now adopts
full source/output byte-range separation explicitly. Nonempty overlapping ranges
are outside this theorem; separation is sufficient, not shown minimally necessary.
ZST byte separation allows equal addresses and preserves alignment/reference/
logical-ownership duties. Existing initialized-source, raw possibly-uninitialized
scratch, retained-originals/Shadow and effect-aware normal/panic posts remain the
target. Clarified that legal callback leaks/replacement do not violate a supposed
Rust no-leak rule or require restoration of consumed resources. No Copy/Freeze/
purity/no-panic restriction is added to safety. Future composition must prove
the entire precondition at each used caller; the static audit is not that proof.

Project specification choice is settled. Organizer inquiry is deferred and no
longer a prerequisite for planning under the stated domain. External acceptance
is unconfirmed; no claim of a complete standalone Challenge solution follows.
The earlier review/ledger and unsent draft remain historical. STATUS, PLAN,
README, coverage and survey now point to this owner decision; prior experimental
reports and log entries remain intact. RAPx gateA/replay stay CLOSED/NO-GO, B/C
NOT RUN; no historical budget or patched VeriFast route is reopened.

Scope: research documentation only. Static diff, repository-relative link/anchor
and changed-path checks; no compilation, executable research tests, proof runs,
Actions dispatch, std/tool/workflow edits or external messages. Proof and detector
coverage are unchanged. The next technical phase remains a separate decision.

## 2026-10-06 — joint RAPx / VeriFast / Kani composition analysis, docs only

Owner requested analysis and documentation/plan update, commit/push only;
no verifier patches, builds, checks, dispatch or external messages. Clean entry
local43bc758; remote research head contained the newer adopted-domain decision
eda527922ec96468a804e3a62fbc1ca96f23691d. Inspected fetched commit/diff and
fast-forwarded without reset. origin is Tiramisu-Cake/verify-rust-std, branch
challenge-8/research; entry Actions listing contained no queued/active run.
Latest research run remains replay37513897141; unrelated scheduled37518141083
completed SKIPPED. No proof run has been added by this task.

[Composition assessment](SORT4-COMPOSITION-ASSESSMENT.md) gives the exact
obligation/tool/evidence/missing-check/dependency matrix and common source/domain
conditions. It does not require a single tool to close the entire contract.
Conditional prospective allocation: independent layout/primitive facts, VF current
callback/resources and all five unwind posts, checked pointer/index/copy
composition, conditional generic order theorem, then later caller use. Existing
Kani i32/tagged normal functional results remain concrete; no universal lift or
RAPx-to-VF ownership/provenance/initialization bridge is assumed. ZST stays in the
adopted contract; RAPx0.7.50 A/replay remain CLOSED / NO-GO, B/C NOT RUN.
Other RAPx properties are not automatically reliable after a scoped Align miss.
Present RAPx contribution is diagnostics, with no actual-sort4 proof component.

Read the actual SmallSort and selection helper, contract, run closeouts, measured
Kani UB gaps and VF feasibility/recovery evidence. Subagent read-only VF review
returned capability constraints; no implementation delegated. Rechecked target
blobs e555fce440872898e47fd5114f32eb15401d07df and
fe59166363b9cc049c0d48f4349f4dc9c0e458b8. Local immutable RAPx archive source
VCS metadata identifies7d61d9377033c48a4df8954f34cc076e97a93816; VF readonly
checkout identifies809de4596839b739dd999f9e462242c835e3af46. Read pinned RAPx
memory/util/call sources: zst_guard also appears in Allocated/Init, and selection
builtin gives numeric either-argument disjunction but first-available provenance
without condition linkage. These are static dependency concerns, not newly run
counterexamples or universal tool-unsoundness claims.

Separated necessary VF capabilities from a mandatory patch chain: checked tuple /
HRTB call handling, full direct-unwind recovery and current one-owner resources
are required for its proposed role; raw scratch/copy representation and actual
selection still need proved implementations/interfaces. Historical insertion
address-taken/ManuallyDrop/local-Drop/declaration/projection patches are not
speculatively required for sort4's own body. No finding licenses new trusted
semantics or proves that kernel/prelude changes are intrinsically unavoidable.

One proposed check, NOT RUN / NOT AUTHORIZED: H_align on unchanged VF26.09,
generic legal .add(i), i0..3, including size0/align>1, with caller/resource-derived
base alignment and existing size_align facts. Bounded future hosted manual gate,
max90min, no other-tool reruns or B/C. False-post controls test the lemma, not an
UB detector. Acceptance explicitly audits the actual reference/copy enforcement
boundary; the pinned typed copy summary has no explicit alignment clause and
requires initialized dst. Arithmetic alone cannot close automatic operation,
raw-dst, provenance, ownership or panic obligations. Failure/missing enforcement
checkpoints need a separate decision, not a patch or weakened post.

Updated STATUS/PLAN/README/coverage/current safety-decision pointer and RAPx
planning pointer without rewriting historical experiment evidence. Local
validation: git diff --check, lightweight non-executing Markdown table/local-link
parsing and manual anchor/diff/source review. No build/verifier/research runner
or executable test ran. **CLOSED: conditional design, no generic coverage gain.**
STOP after docs commit/push; no active run or uncommitted proof draft.

## 2026-10-06 — H_align owner resumption and experiment card

Owner explicitly requests the proposed check. Entry clean HEAD98c0f4f53eca6467a1e0ead8f0260f96b7d53dbc matches remote research head; origin fork/branch correct, no active/queued runs. [Phase/card](SORT4-ALIGNMENT-PHASE.md) freezes one NEW hosted manual run/90min, unchanged official VF26.09/nightly-2026-02-05, isolated generic pointer geometry, ZST layout calibration and two false-post alignment controls. No local executable verification or semantic changes. Full eventual normal/five-unwind resources remain the contract; fixture is a partial geometry theorem. Read-only explorer traced pinned pointer/typed-memory model: valid-layout positivity separate from size_align; copy summary has no explicit alignment, byte-to-typed conversion requires it; no justified automatic copy negative found without assuming misaligned typed resources. repr(align8) export/model support unknown, isolated calibration required. Status IN PROGRESS/preparation,0/1 used, no active run.

H_align dispatch: preparation commit17ad1f48b1eb97f806e03a97b7bf64b24f8ac50b pushed and remote SHA confirmed. No other active research run before dispatch. Manual selection verifast_sort4_alignment/budget90 created [37529855468](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37529855468) at20:53:28UTC, exact matching head, queued at resolution. Budget1/1 used. All local validation was static: bash-n, Python AST/YAML/fixture-marker parsing, git diff--check and source blob audit. No local executable research code/compile/test/verifier. Six isolated original/annotated fixtures, full export/decode/proof/refinement evidence. Further proof source/run not authorized under this budget.


## 2026-10-06 UTC — H_align one-run closeout, INCONCLUSIVE

[Run37529855468](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37529855468)
at exact source17ad1f48b1eb97f806e03a97b7bf64b24f8ac50b completed FAILURE.
Created20:53:28UTC; verification job112496162422 ran20:53:33–20:54:10UTC,
37s; replay job SKIPPED. Selection verifast_sort4_alignment, budget90.
Official unchanged VF26.09 archive/source/schema hashes and target SmallSort
blob checks pass, paired binaries/prelude identities recorded. Nightly2026-02-05,
x86_64 hosted runner, no semantic patches or local executable checks.
[Detailed closeout](SORT4-ALIGNMENT-RESULTS.md) preserves exact profile,
per-case failures, stage/source hashes and remaining model boundary.

All six isolated cases: exporter0, decode0, refinement0; stage source integrity
unchanged; verifier1 at annotation parsing. Generic const/mut helpers stop at
opening ghost body `{` line10. Layout stops at `ens` line12, ZST .add at line13,
source/destination byte-offset negatives at line14. Caller/helper proof headers,
helper-body and pointer-operation records all0. Intended negative alignment
assertions line23 NOT REACHED. Aggregate INCONCLUSIVE; no H_align, layout,
operation-detector, resource or generic-sort4 theorem follows. Export/refinement
success does not check VeriFast annotation grammar. This is our avoidable fixture
syntax mistake, not an intended negative or new VeriFast semantic NO-GO.

Read-only audit of checked Rust lemma/function examples confirms two corrections:
remove `;` after both body-bearing ghost lemma signatures; split each of the six
runtime function req/ens/on_unwind_ens clauses into separate annotation comments.
Exact predicates, resources, bodies, controls and frozen tool profile stay the
same. Correction described in report, NOT APPLIED / NOT VERIFIED. No verifier
or proof-source change after failed run, no second dispatch. One fresh source
SHA/run with that exact formatting correction requires a new bounded decision.

[Artifact11443817617](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37529855468/artifacts/11443817617)
downloaded outside repo;159files,112183bytes, SHA256 matches API digest
f1ca30c7bc50125c09a901e9442ef2af8e596bc06e3dbd6c50bebb4e00ef663f.
Aggregate SHA2562e5d8fce61ee88fc0821139c20f2e9f0e8a6c35e21d0cca85164f1f47e8ea389;
full Actions log SHA256490df197e2dbec659c5c64291d3a7d99582e01fed161479e8654f6fed8435e3c.
Inspected full run log, all six verifier/refinement/export logs, pointer/layout
MIR and source/annotation boundaries. Runner18.05s/maxRSS622004KiB, no OOM or
timeout. No downloaded processor or verifier executed locally, no artifacts
committed. Local closeout validation limited to diff/document parsing.

**CLOSED / INCONCLUSIVE, budget1/1 used; no active run.** STATUS, PLAN,
README, composition, coverage and phase closeout updated. RAPx0.7.50 ZST A/replay
stay CLOSED / NO-GO; B/C NOT RUN; Kani and all prior proof counts unchanged.
Documentation commit/push only after result. No external message/publication.


## 2026-10-07 — authorized H_align syntax-only continuation card

Owner explicitly grants only report-b1ae937 formatting correction and exactly
one additional NEW hosted manual run/90min including runner preparation.
Entry clean matching HEAD/origin research b1ae937f901ad34aeef8bcdbd98997abd1fd1969,
correct fork/branch, no active/queued Actions. Separate budget0/1; original
37529855468/source17ad1f4 stays CLOSED / INCONCLUSIVE. Phase/STATUS recorded
before proof edits. Target H_align, arbitrary valid sized T including ZST,
Storage alignment/byte permissions, i0..3, full eventual normal/five-unwind
contract versus partial geometry/no-unwind/frame post all unchanged. Same six
cases and intended negative assertion markers/classification; no automatic-copy
or whole-sort4 claim. Official VF26.09/nightly2026-02-05 pins/flags/checks frozen.
Only helper-header semicolons and function contract-comment boundaries may change.
Static preservation/example audit, correction commit/push, one exact-SHA dispatch,
full hosted evidence inspection and documentation closeout; STOP after result
regardless of outcome. No further proof repair, runner/classifier/tool/spec/premise
change, local executable check, RAPx/Kani rerun, B/C or external message.

Preparation static audit: compared helper form against recover_pair in
verifast-borrow-recovery-cases.rs:19 (release26.09 run37437514808 body checked)
and separate req/ens/on_unwind_ens ranges in verifast-drop-caller-cases.rs:23–36
and empty Drop bodies:98. Split comments are adjacent @*//*@ ranges to retain
byte-exact ghost-stripped Rust. Non-executing text comparison confirms all six
case order/markers, every //@ statement/assertion, all contract/lemma ghost
payload tokens unchanged except the two authorized signature semicolons. Whole
and per-case Rust bytes after stripping are identical to b1ae937. No runner,
workflow, classifier or std diff; SmallSort blob e555fce440872898e47fd5114f32eb15401d07df.
Only local text/document parsing and git diff --check; no research code executed.

Syntax-only continuation dispatch: correction commit9474453f231eb600e1ec35d571c8ac4f70fa7138
pushed, remote matched, no other active run. [NEW manual37532204465](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37532204465)
created2026-10-06T21:12:28Z, head_sha exactly matches, selection
verifast_sort4_alignment/budget90; queued at resolution. Additional budget1/1
used. No further proof corrections or dispatch; monitor/full evidence/docs only.


## 2026-10-06 UTC / 2026-10-07 Moscow — syntax-only H_align closeout

[NEW run37532204465](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37532204465),
exact corrected SHA9474453f231eb600e1ec35d571c8ac4f70fa7138,
verifast_sort4_alignment/90, completed FAILURE. Created21:12:28UTC;
job11250412347821:12:33–21:13:15UTC (42s), replay SKIPPED.
Additional budget1/1 used; no duplicate dispatch/Re-run/further proof correction.
Official VF26.09 archive/source/schema/bin/prelude audit and paired Z3 pass,
nightly2026-02-05/compiler and target SmallSort identities unchanged from initial
run. Runner/driver/workflow hashes/code unchanged. Corrected fixture SHA256
eadb4ec6dc234c8cfb94a5f581681d7c2f404b12ea0af8c092105998a52cd3b4.
All six archived originals independently byte-match b1ae937 after ghost stripping;
per-stage source hashes unchanged. No predicates/assertions/body/premise/post
change. No local research executable/compiler/verifier/test executed.

All six export/decode/refinement0, VF1. Two annotation-format repairs are effective:
no VF parse errors. First substantive generic blocker is prelude_core.rsspec64,
Cannot prove0<=address at helper line11 div_rem_nonneg(address,alignment).
Each helper has one actual timed header and3 body trace records; generic callers
and pointer operations not reached. ZST layout reaches named body/calls but
fails size==0 assertion line20 (Cannot prove __result=0); align8 assertion not
reached. ZST add reaches .add line21 (4 operation records) but fails
pointer_within_limits(ptr_add_(base,i,Z_type_info)); no normal/resource post.
Generic geometry and ZST calibration remain INCONCLUSIVE, not H_align refutation
or proof that every no-patch strategy is impossible.

Both source/destination negatives reach named caller, actual byte .add(1) line22
(3 operation records), cast line23 and intended alignment assertion line25:
Cannot prove %(get_pointer_address(ptr_add_(src/dst,1,uint8_t_typeid)),8)=0.
Manual intended false-post rejection2/2; no dereference/copy/automatic UB claim.
All original criteria remain; raw aggregate/classification JSONs all-six
INCONCLUSIVE preserved. Unchanged TIMESTAMP_HEADER expects time immediately
followed by Verifying function, while actual logs include verified/lib.rs(span)
between them. Raw caller/helper header counts0 therefore miss real named headers
(1 per relevant body, excluding diagnostic note repeats/generated Z lemmas).
Error-line detection itself matches intended line25, but caller_count gate fails.
No classifier repair, reprocessing execution, JSON overwrite or relaxed criterion.

[Artifact11445280961](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37532204465/artifacts/11445280961),
159files,123767bytes; downloaded zip SHA256 matches API/upload digest
7ef6d71628a06b3c853cd165a3984669b1b4e1d4e1e282f87ec7998ce87411cd.
Aggregate SHA256089dceee6406a531c7a07a1aa39cc73072da07845ac25c4b9e5b1aacc410770d;
full run log SHA25638f9b9bc4d7168d67fb2e52803b93726f0576479e0e737c3f4235df80d252737.
Full logs/MIR/annotations/sources/hashes/resource records inspected. Runner21.57s,
RSS529212KiB; exporter .01–.02s, VF .11s/case, refinement .07–.08s, decode<.01s.
No timeout/OOM; unused-variable and Node warnings noncausal. Downloads outside
repo, not committed or executed. [Detailed report](SORT4-ALIGNMENT-RESULTS.md).

**CLOSED / INCONCLUSIVE; STOP regardless of outcome at1/1 additional runs.**
Initial37529855468 INCONCLUSIVE retained historically. STATUS/phase/report/log /
PLAN/README/coverage/composition updated; no positive geometry/layout or generic /
automatic-operation coverage. RAPx0.7.50 remains CLOSED / NO-GO; B/C NOT RUN;
Kani unchanged. No semantic VF patch shown necessary. Documentation commit/push
only after result; any further proof correction/run requires a new decision.


## 2026-10-07 — bounded H_align proof/reclassification phase authorized

Owner resumes f1c0774b3a8662ca4e9d838a4a1ad06f7f625e55; entry clean local/remote
match, correct fork/branch, no active/queued Actions. Separate budget0/3 NEW runs,
0/5400 summed job-seconds used including all setup; <=30min cap per run.
[Card](SORT4-ALIGNMENT-PHASE.md#current-bounded-no-patch-proofreclassification-phase--2026-10-07).
Host classifier tests/replay from BOTH pinned historical artifacts without altering
original JSON/logs; refine generic checked helper/local bound proofs from existing
resources without outer req/post change; trace original repr(align8) Z layout
model. Existing array__inv/provenance/layout/size_align applicability is a hypothesis.
All six runtime cases, .add operations, domain/posts/pins/flags/checks unchanged.
Official VF26.09/nightly2026-02-05; no tool/spec/kernel patches/new axioms or local
executable verification. Stop at goals/budget/model-or-contract extension boundary.
RAPx CLOSED / NO-GO, B/C NOT RUN, no full-sort4 or external message.

Read-only phase preparation: pinned VF source809de4596839b739dd999f9e462242c835e3af46
verified. Generic next candidate responds directly to failed0<=address/stride:
checked helper req explicitly adds both nonnegative bounds; unchanged external
req retains array_<u8>4*sizeofT/base alignment/i<=3. Explicit existing array__inv
and provenance min/max expose base/end limits; existing valid-layout supplies
size>=0 and power-of-two positive alignment, size_align supplies divisibility.
Checked assertions/calls must prove local bounds and every strengthened helper
call; no assumption/outer-domain change. These remain hypotheses until new proof.

Concrete ZST source audit finds a model boundary: exporter lib.rs1100 passes only
adt_def.repr().c(), schema AdtDef269–284 has isReprC but no repr alignment/layout.
Translator vf_mir_translator/vf_mir_translator.ml6048–6061 maps fields/onlyReprC;
verifast1.ml6465–6510 maps struct sizeof to symbolic sizeof(typeid) and unconditionally
assumes struct _size_limits0<size<=max_uintptr. Fieldless nonpacked Z gets no size0
or align8 equation. This incompatible positive size explains size==0 failure and
unknown nonzero typed .add offsets against zero-byte backing. No sound new checked
lemma can derive size0 against that existing axiom; no existing repr alignment
metadata restores8. This closes the concrete-ZST no-patch layout route, not the
generic arithmetic theorem; no tool/model/contract patch or type replacement.
Finish separately required hosted saved-evidence replay and the already grounded
generic proof diagnostic, then checkpoint this concrete boundary without expansion.

NEW dispatch: run[37535499783](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37535499783),
created2026-10-06T21:40:10Z, head_sha/source ea635ea152f9ff3a491b57b7b6a9df84dc99a4be
confirmed, pushed remote matches. verifast_sort4_alignment/30min; budget1/3
NEW runs dispatched, final job time pending. Active run monitored, no duplicate.
Static AST/bash-n/diff and six ghost-stripped runtime/outer-contract byte checks pass;
four concrete cases unchanged. No local executable checks.

### Bounded no-patch continuation closeout — run37535499783

NEW manual verifast_sort4_alignment/30, source/head_sha
ea635ea152f9ff3a491b57b7b6a9df84dc99a4be matched pushed remote. Created
2026-10-06T21:40:10Z; job112515246039 ran21:40:14–21:40:52Z, FAILURE,38s.
Verification step failed positive posts; replay/tests/upload SUCCESS, RAPx replay
SKIPPED. Charged1/3 NEW runs,38/5400seconds including setup; no timeout/OOM.
Runner16.88s, peakRSS620268KiB. Full logs/artifacts inspected.

Six exports/decodes/refinements0 and every stage source hash unchanged; VF1 each.
Official archive da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa,
source809de4596839b739dd999f9e462242c835e3af46, binaries/rsspec/schema/compiler
and std blob match frozen profile; no flags/checks/spec/axiom/runtime changes.
Whole/per-case ghost-stripped Rust and all outer contracts unchanged from f1c0774,
four concrete case texts unchanged. All execution hosted only.

Generic const/mut: both arithmetic helper bodies complete/leak checks under
explicit nonnegative req. Array/provenance/layout/size_align facts discharge
local bounds and all reached helper call preconditions; .add line41 succeeds.
i=1,2,3 branches each complete full posts/leak checks. Remaining no-helper branch
fails final alignment post line23: Cannot prove
%(get_pointer_address(result), alignof(T_typeid)) = 0. Not a whole generic theorem;
residual i==0 inference is a possible future checked-proof hypothesis, NOT RUN.
ZST layout: line20 size==0 Cannot prove __result=0, align8 not reached. ZST add:
line21 pointer_within_limits(ptr_add_(base,i,Z_type_info)) unproved. Both reflect
concrete layout-model mismatch audited separately, not a claimed causal implication
from one log to the other. Both negative controls reach byte add/cast and fail
exact marked line25 src/dst modulus8 assertions: EXPECTED_FALSE_POST_FAILURE.
Named callers1 each, generic helpers1/body records6, marked add records3 each.

Historical hosted replay SUCCESS:37529855468 six parse errors stay INCONCLUSIVE;
37532204465 positives4 remain INCONCLUSIVE, negatives2 reclassified as intended
failures in separate outputs. Raw JSON/logs/ZIPs/historical outcomes preserved;
actual source/run/artifact/archive hashes checked, full tree before==after.
3 unittest groups and30 fail-closed mutation checks PASS. No historical verifier
rerun and no automatic copy UB/full-sort4 theorem.

[Artifact11446132505](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37535499783/artifacts/11446132505),
574662bytes, ZIP SHA matches API/upload
45d8363c9b25fb6c2332ae77ee468d2912a765a53fed80651e62d5a79eef1d05.
Aggregate48b2ffd48241e358fc5b039593babffab42d1ad9f0aa53736eb411e3b132d157;
reclassification9559c09b53b1af444cb70066028a9a6a8502d0b3a0987333ba944f5ff4e8134b;
full-logb4c36fcbfa056e27ceff866bf17a6f311326b68c7ccdca291796c8f9b86b9a43.
Downloaded evidence outside repo, no generated source/log/build output committed.

**CLOSED at concrete ZST model boundary; STOP, no active run.** Unused2 slots /
5362seconds retired, no additional fix/dispatch. Faithful original Z requires
reviewed size/repr-alignment model correction or another independent component;
no such extension implemented/authorized, ZST retained in contract. Generic proof
progress did not require a tool patch; residual complete post remains open.
Results/STATUS/card/plan/README/coverage/composition/model note updated. Next
recommended decision: minimum faithful layout encoding and trust/admissibility
review versus separate component; residual index proof diagnostic remains proposed
NOT RUN / NOT AUTHORIZED. RAPx CLOSED / NO-GO; B/C NOT RUN; Kani unchanged.
Documentation commit/push only after this result.

## 2026-10-07 — generic H_align completion and layout review authorized

Owner checkpoint b523959d2032b28086aa8b11dd35a50a2eb7c7e0; local/remote match,
clean tree, correct fork/branch, no active Actions. New budget0/2 NEW hosted manual
runs,0/3600 job-seconds; <=30min each including setup/replay/upload. Previous
37529855468,37532204465,37535499783 and original raw evidence remain preserved.
[Card](SORT4-ALIGNMENT-PHASE.md#current-generic-completion-and-layout-review--2026-10-07).

Specific hypothesis from37535499783 residual-post failure: checked i==0 assertion
in residual i!=1,2,3 branch follows old usize bounds, then result==base proves
original alignment post. Runtime/.add/resources/external contracts/final posts/
classifier/pins/flags/checks unchanged; no new premise or axiom. Expected generic
whole-unit0 incl helper/caller/post/leak checks; concrete original Z retains honest
size==0/assertion20 and pointer-limit/add21 INCONCLUSIVE classifications. Negatives
expected exact source/dst byte-offset modulus8 assertion25 after op22/cast23.
Generic failure -> at most one measured no-patch correction; generic success ->
stop proof runs and finish layout review. Existing concrete Z boundary explicitly
does not stop this independently authorized generic subtask. All execution hosted.

Layout task is source/document review only: verify live upstream and official26.09/
26.10 precise source identities, design minimal layout correction vs independent
component and future regression acceptance, no implementation/patch tests. RAPx
CLOSED / NO-GO; B/C NOT RUN, Kani unchanged, no full sort4 or external messages.

NEW run37537448952 created2026-10-06T21:57:32Z; source/head_sha
16aaf1b993f62c8dad0390b74de3e877983beb37 confirmed with pushed remote, selection
verifast_sort4_alignment/30min. Budget1/2 dispatched, final duration pending.
Static whole/per-case ghost-stripped runtime, six outer contracts and four
concrete fixtures identical to b523959. No classifier/runner/tool/profile changes.

### Generic run1/2 — measured failed direct-zero derivation

[Run37537448952](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37537448952),
source/head16aaf1b993f62c8dad0390b74de3e877983beb37; exact remote/head audit passed.
Job112521963302 ran2026-10-06T21:57:37–21:58:15Z, FAILURE,38s. Budget1/2 NEW,
38/3600s including setup/replay/upload. Full logs/artifacts inspected.
Exports/decodes/refinements6/6 zero; stage hashes and pins/bin/rsspec/compiler/std
identities match prior profile. Classifier unchanged: positives4 INCONCLUSIVE,
negative source/destination EXPECTED_FALSE_POST_FAILURE. Historical replay3 groups/
30 mutants PASS; original tree hashes unchanged.
Generic const/mut helpers and i=1,2,3 paths complete; residual first blocker is
verified/lib.rs53 assert i==0: Cannot prove i=0. Subsequent result==base/alignment
assertions not reached. Concrete ZST layout/add fail at original lines20/21, and
intended negative assertions25 are reached/rejected; known concrete boundary
does not halt this separately authorized generic subtask.

Next specific hypothesis/correction for run2: use checked order splits in the
residual branch: if3<=i derive i==3 (excluded), then i<=2; if2<=i derive i==2
(excluded), then i<=1; if1<=i derive i==1 (excluded), then i==0 from old0<=i.
Pinned Redux src/redux.ml1041–1042 handles integer strict/non-strict comparisons
with unit gaps; existing neq constraints alone did not finish the derivation.
Every bound/assertion remains a checked proof obligation; no assumed i==0/new
lemma axiom/external req. Runtime/.add/posts/classifier/tool checks preserved.
Allocate final30min hosted cap; max2/2 then stop proof runs regardless of outcome.

NEW final run37537868053 created2026-10-06T22:01:18Z; head_sha/source
519a3707136d2ae4e589c44b837afac6c58b939b matches pushed remote. Selection/30min;
new budget2/2 dispatched, prior38s plus current job pending. Checked ordering
splits in residual branches only; static runtime/contracts/concrete cases/runner/
classifier/workflow identity check passes before dispatch. No additional run.

### Final generic run2/2 and layout review closeout

[Run37537868053](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37537868053),
head/source519a3707136d2ae4e589c44b837afac6c58b939b matched remote. Job112523342669
ran2026-10-06T22:01:22–22:02:09Z, FAILURE,47s; selection/30min including setup.
Budget2/2 NEW,38+47=85/3600 job-seconds; unused3515seconds, no third run.
All6 export/decode/refinement0, stage source hashes unchanged, official binaries/
rsspec/compiler/source/schema/std match frozen profile. MIR runtime/.add/Continue
edges and old external posts unchanged. Classifier/runner/workflow checks unchanged.

Generic const/mut helpers and all four return/post/leak paths finish. Checked
residual order splits derive i<=2,i<=1,i==0,then result==base and old modulus post.
No assumed bound/new axiom. First final blocker is DEAD CODE at verified/lib.rs
53/55/57: impossible guard bodies' assertions never execute; console reports them
and exits1. Not a PASS/accepted full-profile theorem. Original three indexed
branches remain green prefixes. No -allow_dead_code/annotation/check suppression
or classifier change. Tested failed fixture retained, no proof fix after2/2.
ZST layout/add unchanged at assert20/operation21; intended src/dst negatives25
EXPECTED_FALSE_POST_FAILURE after .add22/cast23. Historical replay3 groups/30
mutants PASS each run, source/ZIP/original JSON/log tree preserved separately.
Full logs/artifacts/profile/source audits completed; no local execution.

Artifact11446714044 for run1,574870bytes, downloaded ZIP/API/upload digest
bdb909a3ada2c4754a7beaf86df4de4b349f167a2fdc84fd36a58e856baca098.
Artifact11447620706 for run2,573769bytes, downloaded ZIP/API/upload digest
84a6adcc3f46e20fc7c2b4792f971d4be0c11b874b9345668bbbe1f548a7d37a.
Full-log digests run1 d4d315a6457e4b39b7db2a91c4b6e06218cceca9f372a8f6f1cb95c23c969387;
run2 f6e03c2e7d1d5a5d1b67fc0aaef9a753ab33d7c67ff4f77023b8fce88fa645ac.
Both aggregates48b2ffd48241e358fc5b039593babffab42d1ad9f0aa53736eb411e3b132d157
(their classification/count records match; failures/sources are separately preserved);
second replay9559c09b53b1af444cb70066028a9a6a8502d0b3a0987333ba944f5ff4e8134b.
Runner1 15.29s/RSS621304KiB; runner2 18.57s/RSS619440KiB. No timeout/OOM.

Layout/source review only: as-of2026-10-06T22:01UTC live master and official26.10
f76012fb518703b1d98e243ac4f487f16877cfcb retain repr-alignment omission and positive
struct-size axiom, matching26.09 pin809de459. Releases26.09 published2026-09-06,
26.10 published2026-10-05;26.09.20 identity/date recorded, not a new proof profile.
Recommend bounded compiler-backed closed Sized Rust struct layout facts through
exporter/schema/bindings/AST/translator/engine, Rust-only nonnegative size bound,
typeid/source/target consistency; existing offsets checked against imported facts.
>=0 only removes contradiction, not exact size0/align8; no sampled genericADT
constants. C/C++ behavior retained. Concrete Kani Z component is possible only as
new calibration, no existing full-domain/interface theorem; no contradictory VF Z
instantiation admitted. Future regression design positive/negative/typeid/language/
generic/metadata/normal-premise-assertfalse gates NOT IMPLEMENTED / NOT RUN.

**CLOSED at run limit; generic INCONCLUSIVE, review complete.** No active run,
no tool patch/new axiom/patch test, ZST exclusion, full sort4/copyUB theorem or
external messages. RAPx CLOSED / NO-GO; B/C NOT RUN; Kani prior evidence unchanged.
Documents updated, commit/push closeout. Next proposed implementation requires
separate approval/trust review; ghost ordered-split reachability repair also
requires a new bounded verification decision. No draft fix or third run applied.

## 2026-10-07 — authorized stock generic then fieldless layout prototype

Entry clean matching e170656b7ff00e8de8ac9d5ebc949d2dbf3cfd75, correct fork/research branch, no active experiment. Max6 NEW hosted manual runs /10800 summed job-seconds including builds/setup; 0 used. [Pre-implementation card and full domain/posts/trust/regression matrix](SORT4-ALIGNMENT-PHASE.md#stock-generic-and-fieldless-layout-prototype--2026-10-07) recorded before proof/tool edits. First hypothesis: reachable i<1/<2/<3 ghost partition resolves prior dead-code blocker with exact old contracts/runtime/checks. Experimental patch starts ONLY after BOTH stock generic VF0 plus integrity/refinement PASS. Historical phases preserved; no external publication, RAPx/B/C or historical verifier chain.

### Stock gate PASS — run37540829027

NEW manual verifast_sort4_alignment/30, exact pushed/source/head_sha
968c073983e0fa27112c5d8a4e10a36b05828323, created22:28:46Z on2026-10-06.
Job112533159277,22:28:51–22:29:34Z,43s. Workflow FAILURE only because stock
ZST cases remain INCONCLUSIVE; both generic const/mut PASS, exporter/decode/VF/
refinement0, one caller/helper body each, helper records6 and pointer records3.
Both finish72 statements, all four normal/resource/leak paths, no dead-code error.
Runtime/outer contracts/concrete cases unchanged by static and stage hash audits.
Zlayout still size0 assertion20; Zadd pointer limits21. Both original negatives
reject exact modulus8 assertion25 afteradd22/cast23. Historical replay3groups/
30mutants PASS. Official archive/binaries/schema/compiler/specs/std identities
match stock profile. Artifact11447599817,573681bytes, API/upload ZIP digest
27ff629da5275b4a172dcd60104903622ae1474d42586dcf87ec818b71b3c4f7; full logs and
artifacts inspected. Budget1/6,43/10800sec; stock gate permits layout implementation.

Initial prototype hypothesis: fieldless original Z gets compiler size0/ABIalign8
at its same nominal typeid via new explicitly optional metadata; Rust>=0 removes
contradictory positivity, unchanged pointer-add specs then permit zero-strideadd.
Use pre-recorded matrix/card. Five logical layers may touch AST serializers too;
no other semantics, offset/ownership changes or historical patch chain allowed.

### Prototype run candidate — experimental-rust-fieldless-layout-v1

Stock prerequisite PASS as above. New source hypothesis: compiler-backed fieldless
size0/ABIalign8 plus Rust-scoped nonnegative bound discharges original Z layout/add
without changing pointer/offset/ownership rules. Patch over source809de459 has
SHA256 2ac05bddbf3c3bd9be9fe9a79dd04da0a9917ec8988b495784cb308cf30f015d;
eight physical files across the five reviewed logical layers (AST serializers and
Capnp reader alias included). Origin/API review in verifast-rust-fieldless-layout.md.
Original raw field/generic/repr eligibility and duplicated ADT/definition span/
target/width bindings validated. Absent remains abstract. Rust fieldless sanity
requires zero size, power-of-two positive ABIalign/divisibility/target limits.
C/C++ old positive inequality preserved literally; exact generic/fielded/packed/
transparent/enum/union/DST facts excluded. Source pin, decoder/VFdeps/archive/compiler
pins recorded in separate hosted-only runner. No historical patches or local build.

NEW manual selection verifast_rust_fieldless_layout/30; host Ubuntu22.04, build
exporter AND console from synchronized schema. Stock retained independently.
Pre-recorded card/matrix unchanged: original six cases, Z mut add, default/aligned
reprRust/C empty structs, exact generic const/mut calls at Z/u64; named false size
assertion20, falsealign20, nonzero-stride27 afteradd25, assertfalse20 underreqtrue.
Seven metadata controls: absent fails size0 assertion20; malformedsize/align and
wrong ADT/source span/target/width fail explicit RustLayoutMetadata validation, not
parse/setup. Canonical/mutated MIR and hashes archived separately. New strictnegative
classifier12 hosted selfchecks; old six-case classifier/runner unchanged. Three
pinned existing Rust/C/C++ tests plus two smoke controls run on both profiles,
source hashes checked. All independent cases attempted; overall fail-closed until
ALL required gates pass. No green badge or partial prefix substitutes for acceptance.
Static patch applicability, AST/YAML parsing, ghost/source/contract audits, bash-n
and diff-check PASS; executable tests/compilation/VF NOT RUN before hosted dispatch.
If build/API/fixture failure, classify INCONCLUSIVE and fix within same scope;
out-of-scope layout/offset/ownership requirement means STOP. Budget remains1/6,
43/10800seconds before dispatch. Artifact download archive digest matched API;
stock full Actions log SHA256 08a83f9b57fe116f6049597ddbb99c8c9b5cd37ce109445704f325cd8e745974.

Dispatched NEW prototype run37542669720, source/head f9697b8f3f894eb24115684a41da3d88566ddc9e (pushed/remote/head_sha match), created2026-10-06T22:46:19Z, verifast_rust_fieldless_layout/30. Budget2/6 slots,43 completedseconds+activejob. No other active experiment; branch workflow selection accepted directly, no main change or external publication.

### Prototype build failure — run37542669720

Exact f9697b8f3f894eb24115684a41da3d88566ddc9e, job112539146765
22:46:24–22:47:46Z,82seconds, FAILURE. Official archive/source pin, patch
applicability/eight-file identities, compiler install/VFdeps/decoder preparation
PASS. Console build exits2: vf_mir_translator.ml:6066, unary minus_big_int applied
to two arguments in max-target-size construction. Exporter build and whole
experimental positive/negative/metadata/compatibility matrix NOT RUN; no layout
claim inferred. Full logs/artifacts inspected, artifact11449447487,38311bytes,
API/upload ZIP digest618c839889ab891874e8083a2f42254cdb3b2ab3b5a61e5fbd83f15cd716f6eb.
Budget2/6,125/10800sec; no active run. Next new hypothesis/correction: binary
sub_big_int (2^width) 1 expresses same allowed bound and typechecks; no rule/domain/
profile/check change. Stock run37540829027 theorem remains separately PASS.

Run3 candidate corrects only minus_big_int->sub_big_int in metadata max bound; patch SHA256 fd37c158aecd1d383d32e1a7656fc9a1bc4f9d73504baf2f15a9f5714d79ee7a. Same schema/domain/engine rules/fixtures/flags/gates/30min selection. Static applicability/diff checks PASS. This tests the measured build failure; no unchanged rerun.

Dispatched NEW run37543115091, source/head55b856cd5285961e02323dd269044d2d194183d6, created2026-10-06T22:50:41Z; exact pushed/remote/run match, verifast_rust_fieldless_layout/30. Budget3/6,125completedsec+activejob. Same eight-file profile corrected subtraction only, original stock/experimental matrix and all checks retained.

### Prototype build failure — run37543115091

Exact source/head55b856cd5285961e02323dd269044d2d194183d6,
job112540598709,22:50:46–22:52:36Z,110seconds, FAILURE.
Earlier preparation/pin/patch gates PASS; console build exits2 at translator6096:
Unbound constructor RustLayout. Exporter build and entire experimental matrix
NOT RUN. Full log and artifact11449258539 inspected (38197bytes; API/upload
SHA256 afb0823e78e7dd8573d67e51f908f1f45062fb815278bc7f00580a16add2bf69).
Full Actions log SHA256 3fdcd2655ce922af08181fb2de3710b3986e7051fc9e453dc902340424ba647a.
Budget3/6,235/10800seconds, no active run. Candidate4 qualifies Ast.RustLayout,
consistent with existing translator Ast.Struct usage; other constructor sites
already open Ast. Patch SHA256 bb31a6e119a19aee2fee66b3afd07df412b54ceb991e34c672b783b8446b6a9b.
Only namespace resolution changed, no semantic/check/domain/profile weakening.
Static patch applicability/diff checks PASS; next NEW hosted run tests this measured
build blocker. Stock generic result remains independently PASS.

Dispatched NEW run4/37543687813, source/head0950bc40852fd94176d4293cd191a60dda6bb650,
created2026-10-06T22:56:26Z; pushed/remote/head_sha match. Same selection/30 and
pre-recorded matrix; only Ast constructor qualification since prior failed run.
Budget4/6,235 completed seconds plus current job. No other active experiment.

### Prototype build failure — run37543687813

Exact source/head0950bc40852fd94176d4293cd191a60dda6bb650;
job112542474551,22:56:31–22:58:26Z,115seconds, FAILURE. Console build exits2 at
translator6117: Unbound constructor ReprC. The added attribute concatenation
removes the old local type inference; Ast.ReprC is the explicit existing AST
constructor. Console elapsed33.15s/RSS382392KiB, no timeout/OOM. Exporter build
and ALL experimental matrix NOT RUN. Full log/artifact11449318697 inspected,
38245bytes, API/upload SHA2567d938f6f0d31a1192739596025c016df43620d7e736ff1be13e9d9add27611ac;
full log SHA2565f8c4a1f8c9f3ead3385e74d4ffa94eaa659e8eee26edb2831c2cb430cbc9211.
Budget4/6,350/10800seconds; no active experiment. Next candidate qualifies ReprC
and audits all modified AST construction expressions for the same issue before
NEW run. Rules/domain/contracts/checks unchanged; stock generic theorem stays PASS.

Run5 candidate patch SHA256 d4a12525bcdbdaa4deb82058d6cc0037c8c09fa508ad2eeb14386b2753693a14;
only Ast.ReprC qualification since tested run4. Modified translator AST constructors
are now explicitly qualified; other affected modules open Ast. Static source
patch applicability/diff checks PASS. Same complete pre-recorded matrix/flags.

Dispatched NEW run5/37544058075, source/head063acbae79fce823bff65245d8a9772fe5d74457,
created2026-10-06T23:00:22Z, exact pushed/remote/head_sha match. Selection unchanged
verifast_rust_fieldless_layout/30; candidate only qualifies ReprC after measured
run4 failure. Budget5/6,350 completedseconds plus current job. One active only.

### Prototype builds and original-six prefix PASS — run37544058075

Exact source/head063acbae79fce823bff65245d8a9772fe5d74457,
job112543713772,23:00:27–23:03:04Z,157seconds, FAILURE at matrix harness.
Console/exporter builds exit0 with synchronized schema, source809de459/compilerdb3e99b,
patch SHA256 d4a12525bcdbdaa4deb82058d6cc0037c8c09fa508ad2eeb14386b2753693a14.
Experimental binaries console03af81bfc531c8f7625b196b181e4172d001689d88eb2a6c6bd2088eb9b265b8,
exporter31a46637839d57051e41ad12b5bcb9778ad73a160faf85cb4097bf570f77cb2e;
schema97785b763fd03e242229fe780428ced26a4dc04bb12fcbf3889ae00ed8fb6413.
Unchanged spec tree/refinement/C++ exporter and pairedZ3 checks PASS.
Full logs/artifact11449439944 inspected,297540bytes, API/upload digest
b56ffb35a2677ebd9d0244bbdec5b3391aee65edb4ec30904d9bdc9b0c1ac85b;
full log SHA2563eb12c29d3cb0cee407114aa00bd22ea25f27148830befa0d0a070d6ac3a568e.
Original experimental six: generic const/mut VF0/72statements each; original
Zlayout VF0/44statements, original Zadd VF0/43statements. All exports/decodes/
refinements0; every-stage hashes unchanged; named functions/add executions present.
Both old negatives fail intended modulus8 assertions25 afteradd22/cast23.
Stock comparison preserves generic PASS, Z cases INCONCLUSIVE, negatives expected.
This is an executed prefix, NOT accepted whole prototype: marked_cases raised
ValueError because final POSITIVES included four dynamically generated application
names absent from physical fixture markers. ALL extra positives/false-layout/
metadata/native/selfcheck cases NOT RUN. Budget5/6,507/10800s; no active run.
Candidate6 validates PHYSICAL_CASES separately from GENERATED_APPLICATIONS, retaining
all four applications in final POSITIVES/required matrix. Only harness validation
changed; same patch/binaries/source fixtures/contracts/classifier/flags. Static
Python AST parsing/diff check PASS. Last NEW hosted run must attempt full matrix;
after it STOP regardless of result.

Dispatched final NEW run6/37544574703, source/head e472aa27a93b15904c702a2484d9e2fdf6f5554a,
created2026-10-06T23:05:30Z, exact pushed/remote/head_sha match. Same profile patch
and flags, only physical/generated marker validation fix. Budget6/6,507 completed
seconds plus current job. Monitor full result/artifacts then STOP, no seventh run.

### Final prototype matrix / STOP — run37544574703

Exact source/head e472aa27a93b15904c702a2484d9e2fdf6f5554a;
job112545369857,2026-10-06T23:05:34–23:08:00Z,146seconds, FAILURE.
Console/exporter builds0, exact patch d4a12525bcdbdaa4deb82058d6cc0037c8c09fa508ad2eeb14386b2753693a14,
binary/schema hashes identical to run5. Stock archive/refinement/C++ exporter/spec
identity gates PASS; applied patch byte-identical and eight-file manifest confirmed.
Full matrix attempted: original experimental six expected gates; extra9positives,
4intended false assertions,5unsupported absence cases PASS; metadata5/7 accepted,
2INCONCLUSIVE; native prior Rust/C/C++ regressions6/6 PASS across both profiles,
new C/C++ smoke controls4/4INCONCLUSIVE due ensures parse errors; classifier12/12 PASS.
Source/stage hashes match actual37 archived Rust units; seven mutation hashes and
shadow base identities checked. Full logs/MIR/stage artifacts inspected; original
classifications preserved, no post-hoc reclassification. Metadata_absent really
fails intended size0 assertion20 but harness counts7generated helpers+caller and
requires total1. Wrong-span really fails binding-mismatch but audit truncates
nested span before lo.line mutation, so shape gatefalse. C/C++ requires/ensures
shared blocks parse-fail ensures10/8 before assertions on both profiles.
No full acceptance; no demonstrated need to expand model semantics. No code fixes
or runs after final result. Exact per-case table and applicability/trust caveats in
[SORT4-ALIGNMENT-RESULTS.md#fieldless-layout-prototype-closeout](SORT4-ALIGNMENT-RESULTS.md#fieldless-layout-prototype-closeout).
Artifact11450580233,807421bytes, downloaded ZIP matches API/upload SHA256
205a9df3ac4c65676ea02b3d25a3a13adb4580949aeca4336c9a0065b1ac5881;
full Actions log SHA256515e728b6b6fcd97edbf58808aa1245b072208b54075e852b5ad92f0a6fe862b.
Wrapper125.28s/RSS737008KiB, console25.95s/exporter17.43s, no timeout/OOM.
Full146seconds charged. Budget6/6 NEW,653/10800sec (10m53s) including all setup/build;
STOP at run limit, no active experiment. Stock independent generic PASS, narrow
experimental layout/geometry evidence gained, full prototype acceptance INCONCLUSIVE.
Proposed next unchanged-patch harness/annotation repair plus NEW full matrix check
NOT AUTHORIZED / NOT RUN; remaining time does not provide dispatch slots.
RAPx CLOSED/NO-GO; B/C NOT RUN; full sort4/old FnMut-Drop/external publication excluded.

## Autonomous night authorization — 2026-10-07

Owner explicitly opens SORT4-NIGHT-PHASE from clean matching e7eae592dcda42ad330cd8f565c1411bffdf7519,
no active run at23:30UTC October6. Separate12 NEW/10800 job-second budget,
30min per run, deadline06:00UTC October7; repair sublimit2 NEW included.
Historical6/6 budget remains closed. Exact d4a12525 layout patch unchanged;
stock26.09 independent tasks, no historical semantic patch chain. Full allowed
sequence and trust/stop boundaries in the phase card. Initial budget0/12,0s.

### N1: unchanged layout profile acceptance repair — prepared hypothesis

Actual obligation: H_align for sort4 source/dst offsets0..3; partial geometry,
not typed ownership/callback/full sort4 proof. Previous run37544574703 showed
actual intended absent/span rejections masked by harness and native annotation
parse errors. Hypothesis: named target counting, full balanced nested span
comparison, ordered wrong-span mutation and split native blocks repair processing
without semantic changes or weakened checks. Domain, resources, normal/unwind
posts, all cases, primitive/prelude/refinement/patch identical to original matrix
in SORT4-ALIGNMENT-PHASE. Expected: every positive complete VF0/integrity/refinement;
negatives reject named assertions; corrupt metadata rejects translator identity;
false/assert-false never proves; both native profiles parse/verify; full old matrix
and targeted classifier mutants pass. If routine harness error, one remaining
repair run may correct it. Semantic or false-proof failure quarantines affected
profile and redirects to independent stock tasks. Selection
verifast_rust_fieldless_layout/30; new repair budget0/2,total0/12. Exact SHA/run
recorded at dispatch. No executable local validation.

N1 dispatched: run37547307118, source/head6bbd25a240ff4d2966c2dcdfed5d79936bc0638f,
created2026-10-06T23:34:33Z, selection verifast_rust_fieldless_layout/30,
exact pushed/remote/head_sha match. Night1/12,repair1/2; job time pending.
One active experiment; unchanged patch digest confirmed before dispatch.

### N1 result and N2 correction card

Run37547307118/source6bbd25a240ff4d2966c2dcdfed5d79936bc0638f,
job112554275354,2026-10-06T23:34:37–23:37:02Z,145seconds,FAILURE.
Full log and artifact11451073890 inspected (812889bytes, uploaded ZIP SHA256
ef45f1657175390132508a3b7416a398ceca70523c5d88aed4bf9c24efebd845).
Base809de459/compilerdb3e99bb/x86_64 pins and exact d4a12525 patch unchanged.
Both original-six profile comparisons match expected; all18 extra cases,
7/7 metadata gates,31/31 classifier/span tests pass. Native C and previous
Rust/C/C++ regressions pass both profiles. Only new C++ smoke fails BOTH at
ensures line8 before body: `No such variable...: CppEmpty` in sizeof(CppEmpty).
This is annotation parser/name syntax, not a false layout theorem. Full acceptance
still INCONCLUSIVE. No false assertion proved. Night1/12,145/10800s,repair1/2.

N2 hypothesis: elaborated `sizeof(struct CppEmpty)` selects pinned parser's type
path (as in its C/C++ type syntax), unlike unqualified sizeof(CppEmpty) interpreted
as an expression. Change ONLY the new C++ fixture's ensures and assertion spelling;
retain empty complete object and >=1 post. All N1 domain/posts/profile/expected
matrix checks unchanged. Full matrix rerun, selection verifast_rust_fieldless_layout/30;
second and last repair run included in12-run total. On PASS accept only exact narrow
experimental profile for later authorized tasks; on failure close repair INCONCLUSIVE
and continue independent stock work. No semantic repair or third repair run allowed.

N2 dispatched run37547890530/source3f5c9e3126a6db0599f1b989f03146e143342d04,
created2026-10-06T23:40:58Z; exact pushed/head_sha match, same layout/30 selection.
Night2/12,completed145s plus active job;repair2/2. No further repair slot.

### N3 stock pure index theorem — prepared card

Actual sort4 obligation: the exact a,b,c,d/min/max/unknown_left/unknown_right/lo/hi
formulas at unchanged std blobe555fce440872898e47fd5114f32eb15401d07df.
Hypothesis: for all32 answers(c1..c5), without comparator coherence/purity/order,
all intermediate and final logical IDs lie0..3, pairwise distinct and each of0..3
occurs exactly once. Checked ghost definitions/lemma bodies in sort4-index.gh;
index application positive, isolated mutant duplicates min in hi's position with
all five replies false. Positive req true, full local post intermediate+final
bounds/distinctness/four exact counts; no memory resources/runtime/unwind path.
Frame follows ghost semantics; not target Rust normal/five-unwind contract.
Stock official26.09/source809de459, archive SHA da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa,
no patch/new axioms/assumed summaries. Exact source/formula string/Boolean-cast
mapping recorded on hosted runner; no assumed pointer/callee bridge. Negative
must reach s4_wrong_hi_duplicates_min TARGET_ASSERTION and fail exactly there
with otherwise checked header/application. Zero exit on this false assertion
quarantines stock profile; earlier unrelated failure INCONCLUSIVE. Normal proof
errors may be fixed within night budget with NEW source/run. Success advances to
actual callee/independent order gate, not whole sort4. Logical IDs remain distinct
for ZST even if addresses coincide. Selection verifast_sort4_components/index/30.

Manual workflow exposure: main-only b3c9835ad5ba7c68e7ea666cb4830095d5e6c143,
13 inserted/1 changed line in workflow, components option/input/time cap/plumbing.
No research-history merge, triggers remain workflow_dispatch only; equivalent
minimal change prepared on research. Order/select are separate isolated choices,
so an unsupported actual-callee cannot block independent ghost theorem checks.

### N2 complete matrix result

Run37547890530/source3f5c9e3126a6db0599f1b989f03146e143342d04,
job112556200127,2026-10-06T23:41:03–23:43:37Z,154seconds,SUCCESS.
Artifact11450964297,813748bytes, uploaded ZIP SHA256
01d045b42a17a767124240a5962ed194b225ef80fa5d269e55d2672115b99ab8;
full log/artifacts downloaded outside repo. Original stock/experimental comparisons,
all18 extra cases,7metadata controls,10native paired checks and31 classifier/span
selfchecks PASS. New C++ control reaches named body/assertion/return/leak check,
VF0 under both profiles; C/C++ nonzero complete object claim retained. Exact layout
patch d4a12525 unchanged. Full independent evidence audit is in progress; no new
semantic or model-soundness theorem is implied. Night2/12,299/10800s;repair2/2.

N3 dispatched run37548195599/source03e23cbf56ff3d9e7d79923a0a1d8f15e88fe879,
created2026-10-06T23:44:22Z; exact pushed/remote/head_sha match. Selection
verifast_sort4_components/index/30; one relevant run (queued at resolution).
Night3/12,299completedseconds plus active job. No layout-dependent claim needed.

N2 final full evidence audit PASS: unchanged eight-file patch/spec tree and exact
profile pins; all18 per-case export/decode/refinement/integrity/metadata checks,
4named assertion negatives,4generic caller/callee/helper/application records,
7metadata mutation gates,10native controls and31selfchecks confirmed. Ordered wrong
span mutates only hi.line7->8, lo7; translator binding rejection genuine. No material
acceptance gap; exact narrow experimental profile accepted for already authorized
night tasks, no model-soundness/automatic operation UB or whole-sort4 inference.

### N3 first causal failure / N4 syntax correction card

N3/37548195599/source03e23cbf56ff3d9e7d79923a0a1d8f15e88fe879,
job112557198047,2026-10-06T23:44:26–23:44:49Z,23seconds,FAILURE.
Full log/artifact11451551878 inspected;10142bytes/ZIP digest
31c3e1d982122f689c141732215f0678f614ee1acbc9b1e5650b451ec207f933.
Source/formula binding and source hashes pass, official stock archive digest matches.
Both cases parse-fail at lemma void (positive6/negative5); no lemma body/negative
assertion reached, no proof claim. C parser source809de459 explains: initial
parse_include_directives_core consumes the opening ghost range to handle includes;
parse_decls then sees bare lemma, not a fresh ghost block. Existing supported idiom
is standalone //@ #include followed by a NEW /*@ declaration block.
N4 changes only that include/block boundary in index positive/negative and the
as-yet-unrun order fixtures; all formulas/lemma bodies/posts/negative markers/checks
identical. Hypothesis: separate ghost include restores pure declaration grammar,
then original stock lemma and intended duplicate-index assertion are reached.
Same index/30 selection, same domain/full local posts/decision map as N3; no trusted
semantic change. Night3/12,322/10800jobseconds; repair2/2closed. N4 NEW because
changed source, not an old run retry. No active run.

N4 dispatched run37548475221/sourcefa74d92a120cc6990e5f65b94b31e72f2fb50d2f,
created2026-10-06T23:47:27Z,stock index/30, exact pushed/remote/head_sha match.
Night4/12,322completedseconds plus active job; layout repair complete2/2.

### N4 index theorem PASS; intended negative manually confirmed

Run37548475221/sourcefa74d92a120cc6990e5f65b94b31e72f2fb50d2f,
job112558083331,2026-10-06T23:47:31–23:48:15Z,44seconds,workflowFAILURE only
negative classification. Full log/artifact11451990423 inspected (14639bytes,
ZIP SHA256601c48a893dfc5f2ef0fa80189b3a8c240e9ffa4a125157b40615aa1f8430055).
Official stock pins/hash/source binding/source integrity PASS. Positive VF0, named
s4_index_permutation AND s4_index_application checked with bodies/normal returns/
leak checks,8statements verified. Thus pure theorem covers ALL five independent
Boolean answers, intermediate/final bounds0..3,pairwise distinctness,each ID once.
No comparator/order/type/callee/memory premise; no Rust pointer/refinement claim.
Negative reaches intended assert12 and fails its predicate equality at expression
end14: cannot prove s4_perm(min,lo,min,max)<==>true. Checked header before it; one
real timestamped caller header and a diagnostic trace note. No false proof.
Raw negative classification INCONCLUSIVE because initial processor counted the
trace note as a second header and expected the error at statement-start12 rather
than comparison-token14. Raw outputs remain unchanged; manual target rejection
confirmed. No further index verifier rerun is needed or planned.
Night4/12,366/10800summed seconds; no active run.

### N5 independent rank theorem + saved N4 processing replay card

Order hypothesis/domain/posts/profile/negative in SORT4-ORDER-LEMMA.md remain
unchanged: arbitrary mathematical integer ranks, fixed preserved values/keys,
exact five less-than comparisons and index choices; full permutation + adjacent
lexicographic rank/original-ID order. Functional premises do NOT narrow unrestricted
safety. Integer-rank theorem transfer to arbitrary SWO quotient is a mathematical
argument, actual callback/T bridge unverified. Negative all-equal reverses middle
occurrence IDs2,1 and must fail marked stability assertion only. Stock26.09 no
patch/axiom/check changes, ghost-only no runtime/unwind/resource contract.
Hosted saved-N4 replay additionally tests corrected exact timestamped-header and
statement-end error-location processing on immutable sourcefa74d92 artifact;
no index verifier is rerun. Derive a separate JSON, preserve original INCONCLUSIVE.
Source/profile/header and before/after hashes bound before replay; positive VF0,
negative named assertion error on14 after execution12 must both classify as expected.
Positive order/negative stability fixtures isolated from callee/range helpers.
Routine proof/annotation errors may be fixed by NEW source/run; false theorem
quarantines stock profile. Success accepts abstract rank result only, then callee
and scalar geometry independent tasks. Selection verifast_sort4_components/order/30.

N5 dispatched run37548811698/source6a12b4e39621eb057712f9084b809f86da6c9b77,
created2026-10-06T23:51:11Z;exact pushed/head match,order+saved-replay/30.
Result:job112559155806,23:51:15–23:51:56UTC October6,41s,SUCCESS.
Full log/artifact11452435478 downloaded/being audited;34922bytes,uploaded ZIP
SHA25608a40ffcdd1759c84ef7096ce3a7f5c7ddddfb6a14f70a65a283280727561c78.
Index raw N4 outputs preserved; separate replay confirms original positive and
intended negative error14/execution12 with exact timestamped headers. Order positive
VF0,named header/order lemma bodies verified,source unchanged; stability negative
EXPECTED_TARGET_ASSERTION_FAILURE. No false theorem. Night5/12,407/10800jobseconds.

### N6 actual pointer-callee component diagnostic card

Target library/core/src/hint.rs select_unpredictable,blobby
fe59166363b9cc049c0d48f4349f4dc9c0e458b8,SHA256
 d94ef86fbdac952fe7c9a6028536e15539b33dc188966fa4e9340fa7d94c30f8.
Actual sort4 instantiation is outer callee T=*const Element, Element arbitrary
Sized (no Element:Copy/Freeze). Hosted extraction preserves ENTIRE body byte-for-byte,
MaybeUninit locals,local DropOnPanic generic struct/drop impl,all THREE intrinsic
calls,drop_in_place,forget,assume_init. Runtime std untouched. Adapter specializes
only function signature/removes const/Destruct surface for pinned older compiler,
aliases std's same core modules; original/verified adapter equal after ghost strip.
Source-to-adapter restriction documented; NOT whole generic core helper theorem.
Hypothesis: pinned stock frontend either checks pointer instantiation's full
condition-correlated model pointer equality/provenance and no-unwind frame, or
reveals first missing intrinsic/local destructor mechanism. Static source809de459
has no select intrinsic match or spec; this predicts a blocker, not an observed one.
Req thread_token(t),t=currentThread;normal same token and full pointer equality
result=condition?true_val:false_val (not numeric address equality);on_unwind false.
No Element dereference/ownership consumption; applicable unrelated resources frame
by normal verifier rule. Original sort4 source/dst/callback ownership/five-unwind
post remains open; callee target does not assume it. Stock26.09/archive da1b619,
compiler nightly2026-02-05/schema7f3ebce,targetx86_64 unchanged. No patch/stub/if rewrite.
Expected stages: source/extraction3intrinsic guard+ghost-strip integrity,export,
decode,VF,refinement. Positive only accepted at complete VF0/named body/integrity/
refinement0/full posts. Unsupported/frontend/resource failure recorded exactly at
first causal location; no intended-negative claim unless positive reaches proof.
Pointer selection summary unavailable until actual proof; if mechanism needs trusted
extension, document minimum scope and move to independent range task. No historical
FnMut/Drop/tuple patch chain, new primitive spec or semantic implementation allowed.
Selection verifast_sort4_components/select/30; remaining7NEW before dispatch.

N5 full audit complete: stock abstract rank theorem accepted,39statements verified;
32index and24feasible order return/leak checks. All intermediate min/middle/max and
final lexicographic rank/ID posts checked; stability negative fails only line17.
Source/pins/before-after hashes exact; saved N4 replay derives expected target
failure without modifying original logs/JSON or rerunning verifier. Actual SWO/T
callback simulation, pointer selection/memory/unwind composition remain open.

N6 dispatched run37549040942/sourceaed1d970acb656cd29149241bf6720198895adac,
created2026-10-06T23:53:46Z;exact pushed/head match,select/30.
Result:job112559882836,23:53:50–23:54:22UTC October6,32s,FAILURE.
Full log/artifact11451463714 inspected;43392bytes,ZIP SHA256
6cc3354d63c2f06a9428d941d95fed179bf28a52cf219cae6e9932925b77cf2e.
Export/decode/refinement0,source/exact extracted body/ghost-strip integritytrue,
threeactual intrinsic calls and DropOnPanic retained,named caller checked once.
FIRST causal failure is verified/lib.rs21,24-50: `No such function:
std::mem::MaybeUninit::<T>::new`, at first actual constructor. Thus select intrinsic
absence remains a later STATIC concern, not the observed first blocker. Full
pointer selection/provenance/frame/no-unwind posts NOT PROVEN. No missing runtime
constructor summary/stub/model rewrite added; actual-constructor/source-capability
review follows while independent geometry advances. Night6/12,439/10800jobseconds.

### N7 exact-selection scalar range theorem card

Source: actual sort4 blob e555fce...,min/lo/hi/max expressions paired with dst0..3,
owned checked index theorem reused at same frozen stockprofile. Hypothesis: full
separated half-open4slot spans imply every selected unit interval is within its
own full span and separated from paired destination interval for all5Boolean
answers and arbitrary nonnegative stride (including0). Domain: mathematical base
integerss,d,stride>=0,ordered disjoint spans s+4stride<=d or d+4stride<=s;
helper i,j0..3,derived selected indices via proved index theorem. Complete post:
permutation + all four source/dst unit containment inequalities + per-copy interval
separation. No pointer equality/provenance/permissions/initialization/alignment,
machine overflow or actual memory execution/resource/unwind claim; ghost theorem
has no runtime/unwind path. For stride0,empty regions allow coincident addresses,
not collapsed logical occurrence IDs. Source/pin/no-assumption guards retained.
Positive isolated sort4-range-lemmas.c; named s4_selected_cells_within_disjoint_spans
calls checked index/range/multiplication lemmas. Negative isolated
s4_range_wrong_final_endpoint: satisfiable stride>0/full-separated-spans premises,
mutant last-slot endpoint d+5stride<=d+4stride must fail only targetassertion.
Other/setup failure INCONCLUSIVE; false theorem quarantines stock. Success accepts
only scalar geometric component; pointer/resource/raw-scratch bridge remains future
design. Ordinary proof errors may be corrected by NEW source/run within budget.
Selection verifast_sort4_components/range/30. Full card/spec-boundary in
SORT4-MEMORY-OPERATIONS.md. Main0970b84 only adds range/swo manualinput options;
no other workflow change/main research-history merge or semantic extension.

N7 dispatched run37549385441/sourceb288370f1a1e6b34c26ef63764c73be2ced452c9,
created2026-10-06T23:57:40Z; job112560988475,23:57:45–23:58:25UTC,40s,FAILURE.
Artifact11452326327,13760bytes,ZIPsha256
 d0fa2dd31e7ca9965a045afef66ec2362f5636eccfe87c0aeac512436b01e0e4.
Positive first fails at sort4-range-lemmas.c14: cannot prove n==4 after exclusions
under0<=n<=4. Scalar theorem not yet reached; this is an ordinary missing integer
case proof, not evidence of false geometry. Negative reaches exact targetline10
and rejects d+5stride<=d+4stride with stride>0 and separated spans. No false theorem.
Night7/12,479/10800jobseconds; no active run.

### N8 scalar-range arithmetic repair card

Same exact N7 source mapping, full domain/post and frozen stock profile. Hypothesis:
existing stock prelude.h checked-profile lemma mul_mono_l(0,n,stride) and
mul_mono_l(n,4,stride) establish product bounds without finite integer case
exclusions; apply also to i+1,j+1 to establish endpoints. No new axiom/spec/model
change; full selected-cell containment/separation and ZST stride0 retained.
Negative and classifier unchanged. Expected positive complete named composition
body VF0, negative intended endpoint only. Ordinary failure may be repaired with
new evidence/run; semantic need becomes design-only blocker. Manual range/30.

N8 dispatched run37549955948/source9b25c410f6f69bdf5649aabf98481501824cec1e,
created2026-10-07T00:03:59Z; job112562823507,00:04:03–00:04:30UTC,27s,SUCCESS.
Full logs/artifact11452042275 inspected;13796bytes,ZIPsha256
 f2033a3382ac24a48f204833bdd04bad52692ab8fcff4b45080f61359638edcf.
Positive VF0,24statements, four named index/multiplication/cell/composition bodies
checked with final/leak checks. Exact source/formulas/header/profile hashes match,
before/after fixture hashes unchanged. All four selected unit ranges contained and
separated for arbitrary nonnegative stride, including0; intended endpoint negative
fails only line10. No pointer/resource/operation-UB or machine-overflow conclusion.
Night8/12,506/10800jobseconds; no active run.

### N9 finite strict-weak-order quotient bridge card

Independent step5 extension: arbitrary16Boolean relation on exactly four logical
occurrence IDs,4irreflexive and64strict/incomparability-transitivity laws. Exact
ID predicate enumerates0,1,2,3 (entire domain, not samples). Hypothesis: predecessor
count ranks0..3 preserve less iff rank< and equivalence iff rank= for any two IDs,
with helper bodies derived from laws, no assumed contract. Full req/posts and
negative in SORT4-SWO-BRIDGE.md; no executable runtime/unwind or Rust resource claim.
Frozen stock26.09/prelude/compiler/target, no patch/axiom/model extension. Isolated
positive application must check named bridge and helper bodies once,VF0/leak checks;
negative all-tied valid relation rejects marked ID-as-rank assertion only. Source
and all own header/fixture hashes recorded before/after. Success closes pure finite
quotient transfer only; actual preserved-T/callback correspondence remains open.
Ordinary ghost proof errors may be repaired with NEW source/run, false assertion
PASS quarantines profile. Manual components/swo/30; no repeated rank-network run.

N9 dispatched run37550139106/source4d7aebcea01c58472e7ef03c4c1611a12d3c673d,
created2026-10-07T00:05:52Z,manualswo/30; exact remote/source matched before dispatch.
Night9/12,506completed seconds plus active job.

N9 finished run37550139106/source4d7aebcea01c58472e7ef03c4c1611a12d3c673d,
job112563387583,00:05:56–00:36:06UTC,1810s,CANCELLED/TIMEOUT. Workflow configured
30minutes; upload/cleanup added10seconds to complete job duration, fully counted.
Artifact11453441016,10919bytes,ZIPsha256
0ca55f4c66811407c4efd2e2d3f8c507c4c945339a386fa8ca1a82f1c19f94c5.
Full log/artifact inspected. Archive/profile/source/header hashes exact; source
binding generated. No final classifier/source-after output exists due timeout;
no complete theorem and negative NOT RUN. Trace laws_at all64paths/leak checks
finishes0.239s, equivalent_predecessor0.270s. FIRST observed hotspot: equivalent_ranks
line108 assertion s4_predecessors(r,x)==s4_predecessors(r,y), after four checked
calls returning equality of each Boolean predecessor. Last progress0.285659s;
no proof error or false assertion accepted. Do not blame the fast64case lemma.
Night9/12,2316/10800jobseconds; no active run.

### N10 same finite-SWO theorem — explicit count proof card

N9 isolates sum/fixpoint reduction as hotspot after pointwise Boolean equalities.
Hypothesis: checked explicit 0/1 contribution equalities/finite case reductions
make predecessor-count equality and later strict-count arithmetic tractable,
without changing relation16/4diagonal/64laws/ID4/full iff+bounds posts. The fast
laws_at proof remains unchanged. Same stock26.09/kernel/prelude/compiler/target;
no axiom/summary/semantic change or verifier flag change. Exact repair rationale
recorded below before dispatch. Positive full bridge/application required VF0;
all-tied ID-as-rank negative must fail intended assertion only. Timeout or helper
failure is inconclusive; after timeout the negative is NOT RUN. Ghost fixture
limit300s, outer job30min with120s upload/cleanup reserve (N9 overhead correction);
no verifier check disabled and incomplete proof cannot be classified PASS.
Success permits new pure SWO/network composition; failure permits one evidence-
based repair within remaining NEW slots, otherwise preserve unproved design.
Manual components/swo/30; source changes require NEW exact-SHA run.

N10 repair rationale: new OWNED checked s4_predecessor_count_equal requires exactly
four pointwise Boolean equalities, proves each conditional 0/1 equality then count
sum, without carrying unrelated SWO laws. equivalent_ranks invokes it after the same
four checked calls; all existing requires/ensures/definitions remain unchanged.
Expected first progress: new helper full return/leak and equivalent_ranks full return.
Later strict-count/rank bounds are not assumed; any new first failure recorded.

N10 dispatched run37553115842/source3ea303b682b63da3237a3d543ce3229b48c2848b,
created2026-10-07T00:39:32Z,manualswo/30. Night10/12,2316 completedjobseconds plus
active N10. No concurrent relevant run;30min maximum fits06:00UTC deadline.

### Conditional pure SWO/network composition card — NOT RUN

Only after accepted quotient bridge: arbitrary relation16 satisfying ALL finite
SWO laws, exact five operands/selection formulas, preserved fixed relation across
all comparisons. Hypothesis: predecessor rank bridge justifies all5 actual logical
comparison replies, checked rank theorem yields s4_final plus adjacent
!less(next,prev) and (equiv(prev,next)=>prevID<nextID). This is the entire four-
occurrence SWO domain, no value sampling; actual T/callback/memory/unwind interface
unproved. Reuse original N5 declarations/body BYTE-UNCHANGED in new owned ghost
header; original N5 C fixture retained byte-unchanged. Require named index/rank/
SWO bridge/network bodies,VF0/all return-leak checks, all source/profile/before-after
hashes. Minimal NEW relation-stability negative uses valid all-tied relation,
exactly swapped middle logical selections, proves non-less/equivalence first,
then rejects marked combined stable-order predicate only. No weakening/unproved
summary. Frozen stock26.09, no semantic change;300s fixture cap/120s cleanup reserve,
manualswo_network/30. This new composition does not rerun a completed standalone
rank task; dependencies are checked at same profile while proving a new caller.
Ordinary local proof fixes permitted by NEW run within remaining budget; semantic
need is design-only, false theorem quarantines. Main input exposure is a minimal
manual choice, no new automatic trigger/job or research-history merge.

N10 result:run37553115842/source3ea303b682b63da3237a3d543ce3229b48c2848b,
job112573025501,00:39:37–00:45:00UTC,323s,FAILURE/INCONCLUSIVE_TIMEOUT124.
Full log/artifact11453956993 inspected;12897bytes,ZIPsha256
07b2ce4a17a7b26cdd15418c57da592aa8226dbb5a199258938800098405c6e6.
Source/profile/hash integrity exact before/after; new count_equal and
 equivalent_ranks COMPLETE with return/leak checks under0.39s. Targeted repair
therefore works, but full bridge not reached. NEW first hotspot is less_rank143
strict count inequality after four subset facts and x case;last progress0.415506s.
No proof error/false theorem. Perfixture300s timeout correctly classifies partial
INCONCLUSIVE_TIMEOUT and skips negative (NOT RUN);120s reserve retains artifact.
Night10/12,2639/10800jobseconds; no active run. Main4771dd9 only adds manual
swo_network choice after prior minimal exposure, no research merge/automatic trigger.

### N11 strict predecessor-count and bound proof repair card

N10 demonstrated that isolating arithmetic from large SWO context completes
count equality. New falsifiable hypothesis: same technique completes strict
count monotonicity and bounds. Owned checked helpers carry ONLY four pointwise
subset implications, ID4(x), own absent/extra witness for strict comparison; or
ID4(x) and own absence for bounds. Explicit four indicator inequalities and x
cases derive strict sum; indicator0..1 plus missing own entry derive count0..3.
Full original relation16/64laws/all theorem requires/ensures unchanged. Earlier
fast laws/equality proofs retained. No new axiom/summary/prelude/model/solver flag.
Positive named full bridge/application,VF0/all return-leak/source/profile/hash gates;
negative unchanged all-tied ID-as-rank assertion must fail intended location only.
300s perfixture,30min job with120s cleanup reserve; timeouts INCONCLUSIVE/negative
NOT RUN. Success accepts full finite quotient and permits the already-carded NEW
network composition; another localized ordinary failure may use FINAL NEW slot,
otherwise retain draft composition explicitly NOT RUN. Manual components/swo/30.

N11 implementation follows card: minimal checked strict-count and bounds helpers
use explicit indicator locals/inequalities and all four exact x cases. less_rank
and full bridge call these; fast law/equality bodies unchanged. SIGKILL137 is
reported as INCONCLUSIVE_TERMINATED rather than attributed to timeout without
cause evidence; timeout124 remains INCONCLUSIVE_TIMEOUT. Both stop dependent
negative processing. New pure composition/header/negative committed as UNVERIFIED
conditional drafts with full card, not accepted proof. Original N5 fixture stays
byte-unchanged; copied ghost declarations/body match it exactly.

N11 dispatched run37553933186/source3c3f0f338559675c5b4ce0859126bbedf8d9495c,
created2026-10-07T00:49:02Z,manualswo/30; exact HEAD/remote matched, no other active
relevant run, maximum fits06:00UTC. Night11/12,2639completedjobseconds plus active.

N11 result:run37553933186/source3c3f0f338559675c5b4ce0859126bbedf8d9495c,
job112575651725,00:49:07–00:49:37UTC,30s,SUCCESS. Full log/artifact11453277736
inspected;46488bytes,ZIPsha256
63d7940aa8aecb6cf6884f4952b64c8f8c371e30ceb768d0690f8d99e0970e3a.
Positive VF0,104statements, all8named checked helpers+application finish/leak-check;
full less iff rank<,equiv iff rank=,both count bounds0..3 over arbitrary finiteSWO.
Header SHA2563ef0b15ff749acc25fde3cab71ee99ab82da1745c593dbd5526e27519b0e1fbd,
all fixtures/hash/source/profile identities exact, before/after unchanged.
All-tied negative proves valid SWO/equal counts, then rejects ID-as-rank only at19;
no false theorem. Pure finite quotient bridge ACCEPTED; actual T/callback/pointer/
resource/unwind interface unproved. Night11/12,2669/10800jobseconds,no active run.

### N12 FINAL NEW slot — pure SWO/network composition

Previously conditional composition card now enabled by full N11 acceptance.
Same complete relation16/SWO domain, exact five operand/selection expressions and
full permutation+adjacent non-less/tie-ID-order posts. Copied N5 theorem byte-
unchanged; dependencies checked at frozen stock profile within new caller proof.
New isolated relation-stability mutant must fail marked combined stable-order
predicate after non-less/equivalence checks; not a repetition of standalone rank
or quotient tasks. Actual Rust runtime/callee/memory/unwind is outside this PURE
claim. Manual components/swo_network/30,300s fixture limit/120s cleanup reserve;
full hashes/bodies/return-leak gates retained. PASS accepts pure network theorem;
any failure/timeout leaves composition UNPROVEN with first diagnostic saved, no
13th run. False assertion acceptance quarantines profile. After finish/audit save
final checkpoint/report and push; night NEW budget exhausted regardless outcome.

N12 dispatched run37554258065/source1803ad0be54a41d97059ad28a0400a7cf851aed3,
created2026-10-07T00:52:51Z,manualswo_network/30; exact pushed source matched,
N11 completed/full audit before dispatch, no concurrent relevant run. Full
read-only preflight found exact5cmp operand mapping and byte-unchanged N5 ghost
header extraction, no semantic/domain/post issue. Night12/12 NEW allocated,
2669completedjobseconds plus active FINAL run; no13th run permitted.

N12 result:run37554258065/source1803ad0be54a41d97059ad28a0400a7cf851aed3,
job112576705436,00:52:57–00:53:25UTC,28s,FAILURE/SETUP_HARNESS_INCONCLUSIVE.
Full job log/artifact11453903478 inspected;2853bytes,ZIPsha256
06ed1171c0a8c874e3cc292aac79273169bc448450290a29185a2be048317737.
Official archive/hash setup passed. FIRST failure before any verifier invocation:
generic fixture-hash branch incorrectly includes swo_network and requests absent
sort4-swo_network-lemmas.c and sort4-swo_network-negative.c. Root's broad string
replacement caused this wiring defect. Composition AND negative NOT RUN; no
proof/disproof or coverage gain. Exact one-line harness branch repaired to range
or swo only, preserving dedicated composition hash branch; bash-n/diff-check pass.
This repair is UNRECHECKED on hosted Actions, and cannot confer proof acceptance.
NO13th run: budget12/12 NEW exhausted,2697/10800summed jobseconds(44m57s),repair2/2.
N9 extra10s cleanup fully counted; later runs retained120s reserve/300s fixture cap.
All runs complete, no active run. Original std/runtime/generic signatures and
all frozen tools/specs/model/refinement/layout patch unchanged. Full run artifacts
stay /tmp; no downloaded logs/generated std/build output committed.

Closeout: accepted exact narrow layout profile, independent stock index theorem,
abstract integer-rank sortedness/stability, finite-SWO quotient transfer and scalar
selected-cell ranges. Pure network composition remains committed UNVERIFIED draft;
actual pointer callee blocked at MaybeUninit::new; reference/copy/raw-scratch and
callback/five-panic resource interfaces remain open/design-only. Final report
SORT4-NIGHT-RESULTS.md and compact STATUS close the night. Future proof-only retry
needs separately approved NEW budget; future trusted capability needs explicit
rationale/trust review/regression gate BEFORE implementation. Historical budgets
remain closed. No further experiments authorized by this exhausted phase.

## New composition/constructor phase — 2026-10-07

Entry85d82998e148394e5dbbb0a4ed8c326780130b75, clean research tree,
origin research matches; main4771dd9894b28312edf40e16d6398628beaf498f.
No active relevant Actions at entry. New owner authorization and5400s budget
recorded separately in SORT4-COMPOSITION-CONSTRUCTOR-PHASE.md; night CLOSED.

### C1 — stock pure SWO network composition

Actual obligation: logical expressions of pinned smallsort.rs sort4_stable,
not runtime memory/callback verification. Hypothesis: repaired85d runner wiring
now reaches the checked composition of unchanged index/rank/SWO components.
Domain relation16 on four distinct logical IDs with all original diagonal/64
triple strict-weak-order laws and fixed/preserved values. Full posts: original
SWO retained, exact final index permutation/bounds and adjacent sortedness with
original-ID stability for equivalent keys. Pure ghost theorem has no runtime
unwind path; actual Rust's resource/panic obligations remain separate.
Profile official stock26.09/pins unchanged. Static preflight: component selection
swo_network in workflow and runner; checker maps existing composition*.c and
copies index/order/swo headers for positive, index/swo for negative; order header
includes index. Runner's separate hash branch names those same existing files.
No assumed/automatic lemma. All named checked components must verify and leak
checks remain enabled. Positive s4_swo_choice_network must pass; equal-key
reversed-middle mutant must fail the marked combined stability assertion ending
line22, after equivalence/non-less premises. Wrong stage/timeouts inconclusive;
false theorem acceptance quarantines stock usage. Ordinary proof/harness repair
allowed with all posts intact. PASS accepts PURE mathematical composition only.
Manual verifast_sort4_components/swo_network/30, fixture300s, cleanup120s;
new phase budget0/5400 before allocation, one run.

C1 dispatched run37585795831/source0383012d9a8e5266c6ac34503b6b886fa795882a,
created2026-10-07T07:11:13Z; exact remote source matched, no concurrent relevant run.
URL https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37585795831.

C1 result: run37585795831/source0383012d9a8e5266c6ac34503b6b886fa795882a,
job112675499341,07:11:19–07:12:02UTC,43s. Full log/artifact downloaded/read.
Positive VF0/194 statements, all11 named checked bodies and leak checks; exact
source/header hashes unchanged. Negative VF1, sole intended assertion failure
21,42–44 on compound operator (statement spans21–22), after target execution.
Raw automatic negative INCONCLUSIVE due checker requiring error onlastline22.
Pure positive theorem verified; full acceptance pending range-based saved-evidence
audit with intended-VC/location mutants. No theorem change or rerun needed.
Newbudget43/5400jobseconds,no active run.

### C2 — hosted saved-C1 processing audit PASS

Card SORT4-SWO-COMPOSITION-AUDIT.md before implementation/dispatch.
Run37586573468/source4e7ee103a6dbfea7d64a88ebbec62d484eea95cc,
URL https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37586573468,
job112677972360,07:19:05–07:19:31UTC,26s. Full log/artifact inspected.
Replay never invoked verifier; exact C1 source/profile/tool/command/binding and
all original/current proof/header hashes agree. Positive194statements/return/leak
PASS; raw negative classification preserved, derived intended assertion21,42–44
accepted. Other assertion line, outside column and wrongVC mutants3/3 rejected.
Pure mathematical composition ACCEPTED under original fixed SWO premises;
checked post is permutation plus3 adjacent stable/non-less steps. Global sorted
order follows mathematically by transitivity of ranks; equal nonadjacent endpoints
force all intermediate ranks equal, so transitive ID< yields global stability.
That implication is explanatory, not an extra checked6-pair post. No actual Rust
callback/memory/provenance/copy/unwind bridge supplied. Newbudget69/5400s.
No active run. Changed future proof cannot use replay as new verification.

### C3 — valid-span control and full immutable-layout matrix

Preimplementation card SORT4-LAYOUT-CONTROL-REPAIR.md. Hypothesis: replacing
invalid hi=(8,13) by valid prefix hi=(7,12), lo=(7,0), within actual pub struct Z;
line, preserves metadata/defSpan and fails specifically binding mismatch at
definition line7. Exact full nested payload differs only hi.col.pos. New narrow
coordinate audit checks both endpoints against selected source/hash, canonical
binding==defSpan, strict ordering; truncated/duplicate/ambiguous span fields fail
closed in positive/negative audit. Retained nested line/column/sourceName/quoted
whitespace comparisons; no general parser framework or semantics extension.
Profile immutable d4a12525 SHA256 unchanged over official source/compiler pins.
Full original stock/patched comparisons,18extra,7metadata,10native and updated
classifier/span selfchecks must pass; unknown/helper/refinement/source/setup
failure is inconclusive. No resource/whole-sort4/automaticUB claim. PASS repairs
this negative calibration gate only. Manual verifast_rust_fieldless_layout/30,
one run, current69/5400s used; allow no concurrent relevant run.

C3 dispatched run37586921301/source3844c5fe708f59bab7f5c4b7aff4d6a0de54985d,
created2026-10-07T07:22:27Z; exact remote matched and C2 fully audited/completed.
URL https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37586921301.

### Constructor technical design reviewed BEFORE semantic edits

SORT4-MAYBEUNINIT-NEW-DESIGN.md is the preimplementation design/regression gate.
Root reviewed scope against new explicit owner authorization: certified source-local
actual body plus narrow active-value translation into existing MaybeUninit model
and external pointer-call to CHECKED local body. Newly trusted applicability/
representation/source-equivalence links are explicit; not general union support
or runtimecall-name→ghost-fixpoint/prototype. Signature specialization/source-local
renaming recorded; original std unchanged. Safe freefunction adapter retains
generated safety/template obligations and own transport cannot be assumed.
If opaque MaybeUninit_own is required, STOP this expansion and record next design.
Source/MIR/type/name/field gates, full pointer equality/Some initialization/token/
frame/no-unwind and falsevalue/post/assertfalse controls defined before patch.
Stock controls remain separate; old layout profile immutable and never combined.
Implementation assigned only narrow translator patch and fixture checker; root
will review before new-profile hosted experiment. No semantic change was made
before the written design/review.

C3 result:run37586921301/source3844c5fe708f59bab7f5c4b7aff4d6a0de54985d,
job112679094538,07:22:32–07:25:31UTC,179s including setup/build/matrix/upload.
Full log/artifact inspected. Exact d4a12525 patch reapplied unchanged; full original
stock/patched6+6 comparisons,18extra cases,7metadata,10native paired and41
classifier/span checks PASS. Existing nonmatching layouts remain unsupported.
Corrected wrong-span: lo7,col0; hi7,col12 vs canonicaldefSpan hi7,col13; actualline
pub struct Z; length13, both endpoints in same exactsource, ordered/nonempty.
Full metadata payload preserves everyotherfield anddefSpan. Canonicalbinary
SHA69bcc09fdc91fe3ef159109171b79c6ce75054ad3749fc58d2d06ad51be31740→
mutated5ad14d134a464f42f3d56ec85cb0f5983970a1cfc594abc98e00bd59ad665d20.
Export/decode/encode0,source/refinement0,VF1 solely `RustLayoutMetadata: binding
mismatch: ADT identity, definition source span, or target differs` at7,1–14.
SelectedsourceSHA97a7737e677df33158291876d0ea7f8f6f6d002173c31d856c4420a7fc9cb6ac.
Truncated/ambiguous span positive/negative audit gates pass failclosed controls.
Historical N2 preserved; valid-span calibration now accepted without patchchange.
No whole-model/automaticUB/ownership/actualsort4 claim. Newbudget248/5400s,noactive.

Default-main exposure per runbook: reviewed minimal workflow-only change196121c11fee754327692a6aae7c97670d809c74
from4771dd9 adds manualconstructor selection/Ubuntu22/30min cap/job-start/runnercase.
No research-history merge or automatic trigger; localunrelated main heads preserved.

### C4 preexperiment card — constructor feasibility ONLY

Actual obligation: repository MaybeUninit::new at core/mem/maybe_uninit.rs396–398,
called twice by unchanged core/hint select_unpredictable at *const Element.
Hypothesis: a source-linked SAFE local copy of this exact body, specialized only
at *const Element with no Element Copy/Freeze bound, can verify under existing
opaque MaybeUninit model without a new ownership bridge. Earlier N6 establishes
missing runtime constructor resolution; this experiment asks the next resource
question, not whole-callee success. Positive wrapper uses actual std constructor
call and preserves full modeled pointer inner==some(val), thread/currentThread,
normal return, no unwind, conditional fractional pointee permission and disjoint
u8 frame; safe constructor's generated safety/template/leak checks retained.
Original source/ghost-strip/refinement checks required at every stage.
Profile official stock26.09/source809de459 plus ONLY translator patch SHA256
047b92a866afafd81632d9b5135f4482bc82994135c6336491b8c48bc5589614;
compiler nightly-2026-02-05/exporter/schema/refiner/specs unchanged; never combine
layout patch. Design committed d67fa0c BEFORE semantic edits. Local union adapter
omits unused Copy derive/Clone implementation, retains exact generic fields,
reprtransparent and copied body; std source/signature unchanged.
Stock and patched baseline false-assert controls must fail solely marked proof
VC (exit1; no constructor calls/redirects); stock/patched pointer-frame and C/C++
controls must verify. Unexpected false-assert success quarantines profile.
C4 is deliberately PARTIAL: source/type/span/value-field/one-inner-call/one-
aggregate/external-redirect gates exist but no exhaustive MIR dataflow/no-extra-
operation whitelist yet. Runner --feasibility-only records UNACCEPTED even if
positive passes; constructor negatives and actual callee NOT RUN. This is not an
acceptance gate. False value/post/resource/applicability cases are designed but
not evidence until separately run after full MIR gate.
Ordinary compile/frontend/proof/harness error: inspect first causal failure and
fix within narrow design before a NEW exact-SHA run. Opaque MaybeUninit_own or
new general union/alias/ownership/copy/Drop mechanism: STOP extension and record
minimal next design without implementation. If positive passes, develop focused
full MIR gate and intended negative matrix before acceptance/actual callee.
Manual verifast_maybeuninit_new_pointer/budget30, timeout1800 incl setup/build,
cleanup reserve120, each matrix stage<=300s, one relevant run. Current budget
248/5400s; no active run. No local executable checks/builds occurred.

C4 dispatched37590641832/sourceac6dfcf246a72f4e9066041b0e31b810553d117d,
created2026-10-07T07:57:56Z; exact remote matched, no other relevant active run.
URL https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37590641832.
Selection verifast_maybeuninit_new_pointer/30, feasibility-only, profile UNACCEPTED.

C4 result:37590641832/sourceac6dfcf246a72f4e9066041b0e31b810553d117d,
job112691033566,07:58:00–07:59:35UTC,95s. FAILURE at console-build before
constructor/checker execution. Full log/artifacts inspected; patch applied exactly
and only translator changed, stock archive/compiler/dependencies/decoder installed.
OCaml line399 D.RawPtr pattern inferred D.terminator_kind due duplicate D.kind
record labels; required explicit D.ty annotations. This is a build error, no
resource/front-end/proof result. Constructor/negative/callee NOT RUN, profile
UNACCEPTED; ordinary type-disambiguation fix within existing design precedes C5.
New budget343/5400s, no active run.

### C5 preexperiment card — C4 build repair, same partial diagnostic

Concrete change: explicit D.ty annotations disambiguate D.kind/D.RawPtr and
adjacent union-field/output records. Patch SHA256 now
bf66cc6f81dcb5ebcf56a9992684215f99653ca2ca5461cbc76e9434a52504af.
No semantics/domain/posts/gates expansion from C4; exact safe source-local body,
actual std pointer constructor call/frame, generated safety, no-unwind and all
stock/refinement/source controls retained. Hypothesis: console now builds and
C4's existing feasibility question reaches source/frontend/proof obligations.
C4 failed before any constructor VC; repeating with explicit typing is a new
build hypothesis. Same deliberately partial --feasibility-only mode, UNACCEPTED
even if green, full-MIR gate/acceptance negatives/actual callee NOT RUN.
Opaque ownership/general model requirement STOP; routine build/harness/front-end
errors fix within design. Manual same constructor selection/30, one relevant run,
remaining5057s admits full1800s cap; no active run at preparation.

C5 dispatched37591112968/sourcebc72f28cbffe0fb61927c1be2756db430c82e931,
created2026-10-07T08:02:14Z; exact remote matched and C4 fully completed/audited.
URL https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37591112968.

C5 result:37591112968/sourcebc72f28cbffe0fb61927c1be2756db430c82e931,
job112692558457,08:02:18–08:04:05UTC,107s. Console BUILD PASS on typed patch;
stock schema/exporter/refiner/C++ exporter/specs identical, dependency link audited.
Four C/C++ paired stock/patched controls PASS. Four Rust baselines export/decode/
refinement0 and all source audits unchanged but VF1 at ens line4 parse error.
Stock parser requires separate ghost ranges per spec clause; current checker put
req/ens/unwind in a single range. This is harness syntax, not model/false VC result.
Constructor/negatives/callee NOT RUN and profile UNACCEPTED. Fix ghost clause
format and matching source-certificate exact bytes before C6; no post weakening.
New budget450/5400s, no active run.

### C6 preexperiment card — Rust annotation repair, same partial diagnostic

Concrete correction to C5: each req/ens/on_unwind_ens clause now has its own
ghost range, matching stock Rust parser and prior actual-callee annotation style.
Checked helper exact source-certificate bytes updated solely for this annotation
format; runtime body unchanged. Patch SHA256
cbf7b7dabb6ab50c74688ca5a96ab24e7df0aac8ec3970eaa17f7b255e25a70c.
C5 successfully built and reached parsing, so hypothesis: separate clauses allow
stock/patched Rust baselines and exact constructor body to reach their intended
VCs. Same full domains/posts/resourceframe/pins/cases/stop rules as C4/C5; no
weakening or new semantics. Same --feasibility-only diagnostic, UNACCEPTED even
if positive; full-MIR gate, acceptance negatives and dependent callee NOT RUN.
Expected false controls fail marked assert VC (VF1), pointer/native pass; then
safe constructor innerSome/token/frame/no-unwind posts and generated template.
Unexpected false success quarantines; opaque ownership/general model STOP;
ordinary new harness/source-gate/proof errors repaired only with new evidence.
Manual same constructor selection/30, one run;450/5400s used, no active at prep.

C6 dispatched37591620888/source39181a39ffa25b07ad2c47a520bd0bba001a5a5e,
created2026-10-07T08:06:53Z; exact remote matched, C5 fully audited/completed.
URL https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37591620888.

C6 result:37591620888/source39181a39ffa25b07ad2c47a520bd0bba001a5a5e,
job112694220280,08:06:58–08:08:57UTC,119s. BUILD PASS; stock/patched assertfalse
now fail the intended sole marked VC at14,16–21 (Assertion might not hold/Cannot
prove false), exit1; complete raw headers/execution/source/export/decode/refinement
controls audited. Four native paired cases PASS. Pointerframe baselines VF1 at
req4,49–50: `List expression must not contain patterns`; `[?f]*p` needs stock
points-to parentheses `[?f](*p |-> ?pv)` (existing verified stock examples).
No constructor VC reached, profile UNACCEPTED; fix only fractional resource
annotation syntax in checker, preserve domain/frame/posts/patchcbf7b7da.
Budget569/5400s, no active run; full-MIR/acceptance negatives/callee NOT RUN.

### C7 preexperiment card — fractional predicate syntax, same partial diagnostic

Concrete new hypothesis: parenthesized fractional points-to syntax from pinned
stock verified examples permits unchanged pointer-resource frame to parse and
verify. C6 already establishes intended stock/patched false VC and native passes;
its list-expression parse failure cannot decide constructor resources. Checker
now writes `[?f](*val |-> ?slot_value)` / `[f](*val |-> slot_value)` (also baseline
p and resource-negative clauses), preserving exact permissions/posts, not changing
runtime source or constructor semantic patch SHAcbf7b7da. All source/integrity/
refinement/no-unwind/leak/generated-safety gates retained. Other C4/C6 domains,
expected baseline/positive outcomes, partial --feasibility-only/noacceptance
classification and opaqueownership STOP rules unchanged. Full MIR/acceptance
negatives/actual callee NOT RUN. Manual same constructor selection/30, one run;
569/5400s used, remaining4831 admits cap1800, no active at preparation.

C7 dispatched37592046851/source2e2eaa7d641b05a3109f1c6ac3fe0f5c40cab058,
created2026-10-07T08:10:48Z; exact remote matched, C6 completed/audited.
URL https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37592046851.

C7 result:37592046851/source2e2eaa7d641b05a3109f1c6ac3fe0f5c40cab058,
job112695625360,08:10:52–08:12:54UTC,122s. BUILD PASS, all8baselines PASS:
stock/patched false sole intended VC14; stock/patched pointerframe39statements,
return/leak checks and paired native4, all source/export/decode/refinement audits.
Constructor fixture first compiler error E0658 transparent unions unstable at4;
export1/decodeNOTRUN/VFNOTRUN/refinement1 same original compile error. Existing
core uses feature transparent_unions; fixture omitted cratefeature. Ordinary
adapter compiler-feature omission, not unsupported VeriFast/resource mechanism.
Add only this cratefeature to original/verified fixture under same nightly/target,
keep repr/body/posts/patch unchanged. Constructor still UNACCEPTED; fullMIR,
acceptance negatives/dependent actual callee NOT RUN. Budget691/5400s, noactive.

### C8 preexperiment card — existing core cratefeature in adapter

New concrete correction: constructor original/verified fixture enables
#![feature(transparent_unions)], already in pinned library/core/src/lib.rs189,
under unchanged nightly-2026-02-05. No new compiler/target/representation or
runtime constructor change. Certificate dynamic source spans continue to bind
same exact body/fields/signature. Semantic patch remains SHAcbf7b7da. Hypothesis:
C7's E0658 omission is removed and source-linked safe constructor can now reach
VeriFast source/applicability/body/template obligations. Same partial feasibility
mode,8 stock/patched baselines, full pointer/Some/token/frame/no-unwind posts,
all source/refinement/safety/leak gates; no acceptance/actual callee in this run.
Opaque ownership/general model STOP, ordinary adapter/front-end/proof fixes only
with concrete evidence. Manual same selection/30;691/5400s used, noactive.

C8 dispatched37592506846/source53b64a780650f6bece661ad751429f628966a63a,
created2026-10-07T08:15:00Z; exact remote matched, C7 completed/audited.
URL https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37592506846.

C8 result:37592506846/source53b64a780650f6bece661ad751429f628966a63a,
job112697141612,08:15:05–08:17:10UTC,125s including setup/build/upload. Full
logs/artifacts inspected. All8stock/patched baselines PASS, schema/exporter/refiner/
C++ support/specs unchanged, patch appliedexactly onlytranslator. Positive
constructor export/decode/refinement0, every-stage source integrity0; exactsource
certificate accepted, inner1/aggregate1/redirect1 with MIR externalcall1.
First sole VF1 error at verified/lib.rs10,75–102 in Function prototype
implementation check: No matching heap chunks:
std::mem::MaybeUninit_own(pointer_typeid(Element_typeid))(_t,result0).
This is generated SAFE-template compatibility BEFORE checking the constructor
runtime body (checked constructor/header0 and frameprobe0). Neither body value
preservation nor resource/no-unwind theorem is proved. No false assertion passed.
Opaque ownership interpretation/transport is needed; STOP extension per owner
boundary. Do not makeconstructorunsafe, delete safety template, assumeown,
registertrustedsummary or importhistoricalchain. Profile UNACCEPTED, fullMIRgate
and constructor proof/applicability negatives NOT RUN, dependent actualcallee
NOT RUN. Historical N6 actualcallee remains blocked at runtimeconstructor; no
claim about a next intrinsic/Drop VC in realcallee. C8 reaches a narrower
constructor requirement separately, not a verifiedcallee summary.
Budget816/5400s=13m36s,8NEWruns, noactive. Remaining4584s retired at scope boundary.
Post-result harness guard now rejects non-feasibility mode immediately because
full MIR gate unimplemented; no new executable run or proof claim for this
fail-closed orchestration guard. Finalpatch cbf7b7da unchanged from C8.

Phase CLOSEOUT: SORT4-COMPOSITION-CONSTRUCTOR-RESULTS.md records all8runs/full
SHAs/jobseconds, accepted composition/layout, exact newpatch/trust limitations,
C8 causal ownership boundary and unimplemented future project. STATUS/PLAN/
README/coverage/callee/design pointers reconciled. Root and independent read-only
reviews confirm prototype check BEFORE body (no checkedbody header), no ordinary
value lemma can introduce opaque own. No dependentcallee or unauthorized model
extension. Final budget816/5400seconds, noactive; unused4584seconds retired.


## O1 — new pointer ownership phase, design before implementation

Owner authorization 2026-10-07, entry e0920ec. [Card](SORT4-POINTER-OWNERSHIP-PHASE.md)
records actual new body, exact domain/normal+unwind posts, narrow ownership equation,
trust delta, full MIR/proof/source controls and outcome-to-decision mapping.
Hypothesis: initialized thin raw-pointer wrapper owns only its value, so a defined
option-based resource interpretation discharges SAFE return-own without pointee
permissions or effects, while full MIR whitelist authenticates the copied body.
Profile: NEW experimental pointer-own-v2 over stock26.09/809de459; exact patch SHA
pending implementation. Selection verifast_maybeuninit_new_pointer,30 minutes/job,
300s/proof,5400 NEW summed job seconds. No carried budget; no active run.
All acceptance/actual-callee checks NOT RUN at this pre-implementation checkpoint.

O1 dispatched [37598560122](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37598560122)
at source798863a89d8d9420670dd8b3c56766a861a6db34, patch31d3ca507cc7ec4a090ef45330b0f3758c1fbcdbbb4c68d66c256166801d6aea.
Selection/budget30min confirmed; full matrix+conditional actual callee; outcome pending.

O1 completed failure,137jobseconds (09:08:42..09:10:59UTC). Full logs and artifact
smallsort-research-37598560122-1/11471388654 inspected: console build0; classifier
4groups PASS;14stock/experimental Rust/C/C++/pointer/false controls PASS;
full typed MIR/source/export/decode/refinement0. SAFE prototype requires DEFINED
MaybeUninit_pointer_own(Element_typeid)(_t,result0) at10,75–102; body headers0.
This is not an accepted constructor. Negatives/actual callee NOT RUN.

## O2 — explicit checked defined-predicate introduction

Same domain/posts/source/pins as O1; hypothesis: explicit own post and a ghost
call to a BODY-VERIFIED introduction lemma discharge the generated ownership
resource while preserving SAFE/thread token/no-unwind. Predicate DEFINITION is
unchanged; checked lemma case-splits existing inner option and closes existing
raw_ptr_own and defined wrapper predicate. No opaque summary or axiom. Translator
emits ordinary ghost call after the certified aggregate; kernel checks that call.
Source runtime/body and complete MIR certificate unchanged. Trust detail recorded
here BEFORE dispatch; allowed proof/model implementation fix within phase.
Patch023e12f00a132ca8fd2dd46e0515c296317eeca573bb5a6c413321b2fe9ba292.
Expected: checked lemma return/leak, SAFE prototype, actual imported body return/
leak, full matrix at intended gates; acceptance also requires lemma execution.
Failure => routine proof/harness correction; success => dependent callee only.
Budget remaining5263s;30min job/300s proof; one run, no carried historical budget.

O2 dispatched37599522829/source0f5b790cc58b30ee3aee12e8989a169e19998fb5,
https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37599522829, outcome pending.

O2 completed128jobseconds (09:16:59..09:19:07UTC), summed265/5400. Artifact
smallsort-research-37599522829-1/11472570359 and full logs inspected. Profile023e12f0:
constructor positive SAFE/prototype/defined introduction and body/caller return/
leak PASS,54statements. Frame owns no val pointee; independent u8 fractional+i32
resources retained; none/some predicate cases executed. Five proof negatives PASS
at intended locations: wrong inner42; false-uninit41; falseassert41; falsepost35;
duplicate resource42.14stock/experimental Rust/C/C++/pointer/false baselines PASS.
Source negatives actually reject precise applicability gates with exit2 (uncaught
certificate Failure); classifier incorrectly required1. Three expected reasons
also pointed to later source checks instead of earlier typed certificate. Integer
SAFE identity contract omitted own in/out, so automatic prototype correctly fails
opaque MaybeUninit_own(int32_t_typeid) at52. This is a harness bug, not model loss.
MIR mutants and actual callee NOT RUN, model/constructor acceptance still withheld.

## O3 — complete metadata admission and harness corrections

Same semantic definition/source/posts/pins. Hypothesis: fixing exact-stage/code/
reason classification and resource-preserving integer contract lets existing
strict source/proof matrix pass; exhaustive HIR/contract/ADT metadata checks close
remaining typed source-binding gaps before acceptance. No wider model extension.
MIR operations graph already O2 PASS; unknown HIR/contract/item forms must reject,
not be ignored. Add corresponding admission controls. Rule remains selected for
all extension controls, reject before semantic activation when invalid. Artifact
must retain canonical/mutated binary/text, original-source integrity and refiner.
Scope/pins unchanged; new profile hash/source recorded at dispatch. Expected stage
mapping per updated fixture metadata; proof exits1 separate from applicability2.
Full matrix => only dependent actual callee; any new alias/borrow/copy/FnMut/Drop/
unwind boundary STOP. Remaining5135s,30min/job,300s/proof.

O3 dispatched37600901979/sourcea452018e98e8894c66f9da41becaa8cf7a4a83c5,
https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37600901979,
patch325af428910cff44fb51e8c11ef0e4c9c3ba928c015f1fdf657580745857ca8d;
16source/proof/specialization+9MIR cases,14baselines, classifier; outcome pending.

O3 completed126jobseconds(09:28:59..09:31:05UTC),sum391/5400. Artifact
smallsort-research-37600901979-1/11473245626/full logs inspected. Model325af428:
full HIR/contract/type/source/graph gate and constructor54statements PASS;
5proof negatives and opaque integer missing-own prototype control PASS;
7/8 source mutants reach their precise expected gates;14baselines+5classifier
selfcheck groups PASS. Integer positive annotation supplied manual typeid as a
predicate index => "Incorrect number of indexes" at55; exact-field source mutant
changed reprC too => earlier representation rejection. Both are harness bugs,
not accepted negatives. MIR9/actual callee NOT RUN; acceptance withheld.

## O4 — harness-only exact-target correction, frozen325af428 profile

Hypothesis: use ordinary <MaybeUninit<i32>>.own syntax for SAFE identity's original
opaque resource, and add an extra ZERO-SIZED field while retaining reprtransparent
so the extra-field control reaches exact field count/types. Preserve body/domain/
posts/SAFE checks and all profile pins. No semantic or MIR gate change.
Full matrix required before dependent actual callee; new source SHA/run recorded
at dispatch;30min/job,300s/proof,budget5009s remaining. Exact expected negative
stages unchanged; wrong-stage failures remain INCONCLUSIVE. No SWO/layout reruns.

O4 dispatched37601511894/source182ddf29dc73961723bf32be6b65643c524ca927,
https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37601511894;
unchanged325af428 model, outcome pending.


O4 completed127jobseconds(09:34:13..09:36:20UTC),total518/5400,new4runs.
https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37601511894
source182ddf29dc73961723bf32be6b65643c524ca927,
profile experimental-source-linked-maybeuninit-pointer-own-v2,
patch325af428910cff44fb51e8c11ef0e4c9c3ba928c015f1fdf657580745857ca8d;
artifact11473086721/smallsort-research-37601511894-1.
Full raw logs/MIR/source/mutation/profile audit PASS, including independent
read-only matrix review: SAFE prototype, checked lemma/imported body54statements,
frame/inner/token/no-unwind/return/leak PASS; nonpointer opaque-own transfer PASS
and omitted-own SAFE prototype negative exact. All5proof negatives at marked
inner/none/false/false-post/duplicate fractional chunk targets;8source and9MIR
mutants exit2 at exact applicability conditions, frontend/refinement/integrity0,
no proof header, canonical/mutated evidence and hashes retained.5classifier groups
and14 paired stock/experimental Rust/C/C++ baseline controls PASS. No skipped
constructor/MIR cases. Model/constructor accepted experimentally only now.
Feasibility-only restriction lifted only after full criterion implementation.

Dependent actual select RUN in same immutable profile/source: N6bodySHA0d4233fe,
originalhintblobfe591663/corehintSHAd94ef86f, all3intrinsics/guards/drop/forget/
assume_init/posts retained; export/decode/refinement/source integrity0 and typed
constructor certificate PASS. Actual SAFE prototype and body reached, both new
calls verified at22/23 using same-source/profile body proved in positive unit.
First remaining error verified/lib.rs(38,20-41),No such function:
std::mem::MaybeUninit::<T>::as_mut_ptr. Target as_mut_ptr(&mut self) casts wrapper
storage address; value-only own grants no storage/borrow rights. New storage/
reference/alias/provenance bridge outside scope =>STOP extension. Actual final
pointer/frame/no-unwind/return/leak and later runtime operations NOT PROVEN.
Helper body not revisited before actual unit's error; no summary assumed.
Exact reproduction and full hashes in SORT4-SELECT-CALLEE and final results.

Phase CLOSED at boundary,remaining4882s retired;no active/queued relevant run,
no pending implementation draft. All builds/verifier/classifier executable tests
hosted; no local execution of proof/builds. Runtime std/signatures unchanged;
RAPx CLOSED/NO-GO,B/C NOT RUN,fullsort4 NOT PROVEN. Final documentation-only
commit/push does not change the proof SHA or rerun old evidence. Archive shadow
profiles are large;770 evidence files excluding binary profile copies downloaded
and inspected, full original archive retained in Actions. No upstream PR/messages.


## S1 — NEW pointer select completion, existing-model cast diagnostic

Owner2026-10-07 opens newphase atcd44e1bb;oldpointerphase budget retired.
Full dependency map and existing storage/reference/cast assessment in
SORT4-SELECT-POINTER-DESIGN,phase contract in SORT4-SELECT-POINTER-PHASE.
Actual as_mut_ptr obligation: SAFE &mut MaybeUninit<*const Element> returns
*mut *const Element with full modeled storage-pointer equality, token/borrow/frame
and no unwind; no initialized-content or Element permissions created.
Hypothesis: exact source two-cast body verifies with existing opaque full_borrow
contract; no new spec/translator rule, all accepted325af428/frozen26.09 pins.
Adapter specializes T and renames sole receiver self->storage, retains actual
body expression/comments; runtime std/signatures unchanged. Partial diagnostic:
no method redirect/full typed admission/negative matrix or wholehelper acceptance.
Named helper SAFE prototype/body/return/leak and unsafe caller fractional frame
must reach proof; export/decode/refinement/source integrity retained. Unconstrained
inner; no concrete none/some setup in this first nonreading body probe.
Success means existing-model body feasibility only; next complete as_mut_ptr
component gate/storage candidate if needed, then listeddependency integration.
A frontend/proof/metadata failure remains INCONCLUSIVE, fix withinphase; unsupported
name alone does not stop. Forbidden kernel/general alias/provenance bridge only
stops with minimal reproducer and exact obligation. One active manual run,30minjob,
300sproof,totalnew5400jobseconds. Selectionverifast_maybeuninit_new_pointer now
routes to run-select-pointer.sh,S1 profileunchanged.
Nearest hostedjob also unitchecks compact evidence packaging and creates<=25MiB
current+O4 archive with source-artifact manifest; fullhistorical11473086721 retained.
O4 constructor raw positive/proofnegative/applicability/mutation logs inspected;
no rerun solelyforrepack. Originalaccepted O4 body remains same-source linked.
SourceSHA/runID/artifact registered at dispatch;initialspend0,noactive.

S1 dispatched37607108528/sourcef19f077457da722e326f88df362b0d14731987e0,
https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37607108528;
unchanged325af428 semantics,nootheractive;outcomecostpending.

S1 completed108jobseconds(10:23:49..10:25:37UTC),newbudget108/5400.
Run37607108528/sourcef19f077457da722e326f88df362b0d14731987e0,
unchanged325af428profile. Fullartifact11475248345;compact11474994216,
https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37607108528/artifacts/11474994216
ZIPsort4-select-compact-evidence.zip1050469bytes(<25MiB),843includedfiles:
O4770+current73.5packaging safetygroups PASS, manifestincludedSHA/CRC/sizeaudit
843/843matches; excludedbinarieslistedwithCRC/sizes/reasons,noinventedSHA.
OriginalO4artifact11473086721unchanged. RawO4acceptance/log/mutationevidence
rechecked;constructorSAFEprototype/body54/frame/leak+intendednegativesretained.
S1positive INCONCLUSIVE beforebody: SAFEprototype leaksfull_borrow at1,1–15,6.
Export/decode/refinement/integrity0. Cause explicitnamedlifetimecontract returns
borrow that generatedconsuming-referencepostdoesnotretain. This is harness/contract
mismatch,notmodelboundary. S2 tests actualelidedreceiver IN/OUT storageprotocol.

## S2 — elided receiver, existing wrapper cell/value ownership transport

Hypothesis: use actual as_mut_ptr elided &mutshape so generatedSAFEpre/post own
wrappercellandvalue; the exact two-cast body and frame can verify withoutnewmodel.
Unchanged325af428pins;certificate-disableddiagnosticusesoriginalopaquevalueown
explicitlygiveninpreandretainedinpost,neverintroduced. SAFEhelper preserves
*storage|->samevalue+own+token+completepointerequality+nounwind. Unsafe callers
unknown/none/some preserveinnerstateandfractionalframe.5negativecallerposts/assert/
leak reachtargetonlyafterhelperbodyreturn/leak; genericwrongstageINCONCLUSIVE.
No methodredirect/fullMIRadmission/constructororhelperacceptanceclaimed.
Success=>withinphaseexacttypedMIRgate/activepointermodelcomponent; failure=>precise
harness/resourcecorrection,notstoponname.30minjob/300sproof,remaining5292s,oneactive.
Runtime/stdsignatures/sourcepinsunchanged;compactcurrent+O4packagingonnextjob.

S2dispatched37608166705/sourcea20e64856822850c76e13ad7bc0d1248af0676a0,
https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37608166705;
completed130jobseconds(10:33:20..10:35:30UTC),total238/5400.
Unchanged325af428profile/fullartifact11476420394,compact11476196005ZIP1221330bytes
(current227+historicalO4770files).3positivesbody+SAFEprototype+frame/return/leak
PASS,innerunknown/none/somepreserved;4proofnegativecontrolsintendedpreciselocations
PASS. LostwrappercellnegativeDOESreachfunctionleakat32,1–2points_to<MU<*Element>>,
classifierwronglyexpectsheader=>rawINCONCLUSIVEpreserved,nofalseacceptance.
No semanticmodelboundary: ordinaryas_mut_ptr bodyworks existingelidedin_outcell
protocol. Componentacceptancewithheld pendingcompleteadmission/activepointerown/
classifiers/fullconstructorregressions. S3design9e02c4f commits exactsource/HIR/MIR
certificate+typedexternalredirect BEFOREtranslationedit;noFBC/alias/kernelchange.
One relevant run/noactive aftercompletion;wholehelper/intrinsics/drop/forget/
assume_init stillNOTRUNinthe newprofile.

### S3 — exact source/HIR/MIR as_mut_ptr admission and active-rule acceptance

BEFORE dispatch: domain SAFE elided &mut MaybeUninit<*const Element>, arbitrary
unknown/none/some inner; thread+same wrapper cell+defined pointer-own, full modeled
result pointer equality, unchanged option state and caller fractional u8 frame;
on_unwind_ens false. No Element permissions/Copy, no general storage/fbc rule.
Hypothesis: the S2 checked two-cast body also satisfies active type-own safety
contracts and a complete pinned source/HIR/typed-MIR fail-closed certificate.
Design committed9e02c4f before semantic implementation. New separate profile
experimental-source-linked-select-pointer-as-mut-ptr-v1, patch
e9b4d025934b6c91674feb4c3b5aa35ce4bbd74cdfc1c42ce9bfefdb3fe266e6,
frozen VF809de459/nightly2026-02-05/export/schema/refiner/kernel/alias model.
3 positive SAFE body/state/frame cases;6 proof controls wrong result/false post/
assert false/duplicate frame/lost wrapper cell/invented Some. Expected proof exit1
after named checked body and probe: source-marked assertion/post or final leak.
8 source+9 MIR mutants target exact certificate reason, verifier exit2 after
export/decode/refinement/integrity and before body/probe, separately classified.
Classifier risk mutants stage/source/certificate/location/message/leak gates;
complete O4 constructor matrix and14stock/patched Rust/C/C++ baselines required.
No SWO/layout dependency. All acceptance gates must pass before component acceptance;
any wrong-stage failure is INCONCLUSIVE, fix specific implementation/harness defect.
Next after acceptance: actual receiver/reborrow integration, then remaining mapped
operations autonomously; real forbidden semantic necessity alone stops extension.
Selection verifast_maybeuninit_new_pointer;30minutes job/proof<=300s;
new budget spend238/5400before run, one active run, compact current+O4 evidence.

S3 result: 37610022772/source489416d21b52858b124638d88180378ef2b4b8d0,
177jobseconds, total415/5400; fullctor+14baselines+classifs PASS, activeasptr
3positive+5proofnegative PASS. Sixth correctNone→Some proof rejection has exact
constructor-instance diagnostic, classifierincorrectgenericcondition expectation.
INCONCLUSIVE retained,17admissioncontrols andactual NOT RUN. Compact11477915575,
full11477880702; rawfullMIR/body/prototype/return/leak andmutationlogs retained.

S4 BEFORE dispatch: unchanged semanticprofilee9b4d025/S3 exactdomain/posts.
Falsifiable harnessfix: exact None→Some postdiagnostic (notgenericCannotprove)
classified atline24 with allSAFE/body/location/stage/fullMIR gates,4newmessage
mutants must reject. Repeatfullcomponentmatrix+constructorregressions because
admission17NOTRUN and integration depend on acceptance; noSWO/layout.
Afterall3/6/8/9andclassifs/ctorpass, verifyexactactualN6body unchanged with both
checkedcomponents+2new/2asptr/3intrinsics/guard/drop/forget/assume_init andfullnormal/
unwindposts; no newrule yet, expectedfirstremainingintrinsic/resourceobligation
INCONCLUSIVE namedline/predicate. Unsupportedlistedop triggersnextdesignedstep.
Selectionverifast_maybeuninit_new_pointer/job30min/proof300s;spend415/5400before.

S4 result 37610819914/source6f5d285/samee9b4d025:205s,total620/5400.
3positive/6proofnegative/8source/7MIR PASS; contractmutator expected1predname
whileSAFEcontractlegitimatelyhas2. Exportwrapper exits98, INCONCLUSIVE,
remainingMIR2 andactual NOT RUN. Fullctor/14baselines/classifiers PASS.
Compact11477701950/full11477662208, run37610819914 preservesrawmutationrecord.

S4b BEFORE dispatch: exactsameS3profile/domain/fullposts. Hypothesis: one
preannotation MIRmutation (assert2pre/post occurrences, replacefirstONLY)
reaches exact exportedSAFEcontract certificate failure, exit2 before proof;
not frontend/mutatorerror. Entireacceptance gates remain unchanged; run last
extraopMIRnegative andactualbodyafterCOMPONENT_ACCEPTED. Selection/job30/proof300,
spend620/5400before; unsupportedmappedop continuesnextdesignedcomponent.

S4b result37611745252/source7c14ab6/e9b4d025:247s,total867/5400.
Fullasptr3/6/8/9 ACCEPTED, ctor/baselines/classifier PASS. Actualcombinedbody
RUN butexternalredirectlateboundaritycertificate rejects beforebody. RawFnDef
confirmedsolepointertype+latebound1, effectivesubsts stockadds 'erased lifetime.
Compact11477673504/full11477848970;fullactualMIR/source/diagnosis retained.

S5 BEFORE dispatch: newprofileexperimental-source-linked-select-pointer-intrinsics-v1,
patche566390327dda7e08e9874d2a7909da7e5f9bc5fb98c132fe7268ba496c5114f;
design1e970b2+exactasptrfix7fc98da committedbeforesemanticimplementation.
Falsifiable hypothesis1 exactlateboundredirect passesactualtwoasptrcallswith
checkedSAFEbody/noresourceweakening; hypothesis2 fixedcompilerstandaloneintrinsic
MIR matches candidate2-block typedgate andIfExpr+checkedMUownlemma verifies.
Firstfeasibilitycasesptrsymbolic/MUunknown SAMEfullposts/thread/frame/noUnwind,
trustedcompilerselection TWOexacttypes only (notintrinsicRustbodyproof).
Noacceptancepossibleyet: fullintrinsicadmission/negative/actualgraph NOT RUN.
Completector+asptrfullmatrices/stockRustC/C++regressions required,new62classifier
gatemutants. ExportcanonicalMIR/source/refinement/integrity evenifcandidategraph
fails; fixexactobservedshape/implementation thenfullacceptance, no blindrepeat.
Existingactualintegrationrunswithoutintrinsicoptin first; fullintrinsicactual
gate initiallyrejectsunknownactualshape ratherthantrustcallcounts.
Selection/job30min/proof300s, spend867/5400before, oneactive,compactcurrent+O4.

S5 result37612975447/sourcef7543ce/07930fff:97s BUILD FAILED atOCamlline8783
stringmodulebody shadows BodyRd.tparameter, noMIR/proofcases. Spend964/5400.
Compact11479045470/full11479215424, sourcesandsemanticprofilepreserved.
S5a BEFORE dispatch: sameS5domain/hypotheses/posts/feasibilityonly, newpatche566390327dda7e08e9874d2a7909da7e5f9bc5fb98c132fe7268ba496c5114f
renamesmoduleconstant local_body soMIRparameterretainscorrecttype, nosemantic
change. Completector/asptrregressions andtypedactualredirecttest then2intrinsic
canonicalshapeprobes. Selection30min/proof300s,newbudget964/5400before.
Evidence-only optimization: newfullarchivesexcludeshadowtools/libs, retainexact
wrapper.py outsideexcludedfolder; historicalfullO4/otherarchives unchanged.
No verifier/harnessclassification gates weakened andnoproofrepeatsolelyrepack.

S5a result37613525435/source6b6d033/e5663903:138s,total1102/5400, fullctor/
asptr/regressions PASS,60(not62) classifiergate mutants PASS. Bothactualtyped
callee gates+2redirectseachPASS; firstPROOF failureasptrline38 incorrecttypeargcount.
Standaloneintrinsics both export/refinepass, canonical7locals invalidates4locals
guess. Fullsource/log/MIR preservedcompact11479611306/full11479026615.

S5b BEFORE dispatch: new2cd1a04a35e58f5337e392cc5e27899ac7de20ad5d821f47045438e0348c732b
profileexperimental-source-linked-select-pointer-intrinsics-v1 sameexactpointer
domain/posts/trust asS5; stockinferredVF lifetimearg followingdesign6f705b9;
canonical7typedlocals, Live/Copyx3, exactFnDef Bool/T/T Move `_4,_5,_6`, bb1
Dead `_6,_5,_4`/Return, noextraops, nounwind. Hypothesis theseexactfullyadmitted
SAFEbodies nowprovecompletevalue/inner/thread/frame/noUnwind underactiveIfExpr
rule+CHECKEDdefinedowntransfer; actualexternalasptrsafecontract alsoinstantiates.
FULLmatrix:3+3positive,5+5proofnegative,7source+13MIR/type=40admissions,60classifier
mutants, ctor/asptrfullsameprofile/regressions. Wrongresultfirstmessageunknown
classifiesfailclosedINCONCLUSIVE, thennarrowexactrawtargetnextiteration; other
negativesnamedtarget/oneerror/body/stagesstrict. Unknownsource/CFG/type/path/
predecessor/resulterrorsmustrejectBEFOREproofat exactcertificate.
Fullactualintrinsicgraph notimplemented yet, optinremainsfailclosed; actual
integrationwithoutintrinsicoptinretainsalloriginalops andfullposts. Noacceptance
possibleuntilallfullmatrixchecks PASS; nofeasibility-only acceptancepath.
Selection30min/proof300s,total1102/5400before,oneactive,compactcurrent+O4.

S5b result37615266238/source2fb924f/2cd1a04a:150jobseconds,total1252/5400.
All6 intrinsic positives PASS; pointerwrongresult andMUwronginner reach correct
normalpost26 but failclosed exactmessage classification. Remaining8proofnegative
and40admissions NOT RUN. Ctor/asptr/classifs/14baselines PASS. Actual firstintrinsic
49 after bothSAFEasptrcalls pass. Compact11478479176/full11478894018 preserve
raw adapters/logs/MIR/profile/O4; no component/fullhelper acceptance.

S5c BEFORE dispatch: SAME 2cd1a04a profile, exacttwo intrinsic types/domain/full
normal/unwind/frame posts, same verified bodies/compiler trusted selection rule.
Hypothesis: exact S5b post diagnostics (result0, condition?a:b, pointer_typeid and
none) classify intended negative while ten substituted message mutants reject;
all60 gate mutants remain required. Then remaining8 proof negatives and40 source/
MIR admission controls reach intended stage/predicate/location with rule ACTIVE.
No semantic changes; unknown diagnostics still INCONCLUSIVE. Complete ctor/asptr/
Rust/C/C++ regressions and all6+10+40 checks required for COMPONENT_ACCEPTED.
Actual integration still intrinsic-OFF until full typed actualgraph implemented
and component accepted. Outcome: localized harness fixes if target mismatch,
otherwise continue authorized helper dependencies. No SWO/layout repeats.
Selectionverifast_maybeuninit_new_pointer,30min/job,300s/proof,1252/5400 before.

S5c result37616835826/source6a9ddc9/2cd1a04a:100jobseconds,total1352/5400.
All6positive+10proofnegative PASS, classifier60+10PASS. Sourceidentity admission
PASS; sourceinputtype correctlyfails BEFOREproof at HIR generic count/kind, but
expectedsource-marker different=>INCONCLUSIVE. Remaining38admissions NOTRUN.
Compact11480431752/full11480376847; intrinsiccomponentunaccepted/helperNOTPROVEN.

S5d BEFORE dispatch: SAME2cd1a04a exactdomain/fullposts/source/pins/rule. Hypothesis:
observed sourceinputtype HIRreason classifies correctly with4message mutants;
all40independent source/MIRmutations nowrecordtargetdiagnostics without stopping
at another unrecognized message (everymismatch remainsINCONCLUSIVE; acceptance
stillrequiresALL). Full6+10proofcases,60+10+4classifiers andctor/asptr/baselines.
Separate authorized pointerdrop diagnostic: exactunsafe mut_ptr.rs1514 body,
T=*constElement, initializedpointercell/thread +samecell/value/noUnwind target,
unsafe framecaller. Frozenexistingfree-drop spec gives unknownvalue andunwind;
hypothesis body export/refinement succeeds then post/noUnwind proof rejects,
with canonical completeMIR and firstcausalobligation saved. No newdrop semantic
rule active; bodyfail NOTcomponentacceptance orsemanticstop. Design1caf569.
Selection30min/proof300s,1352/5400before,oneactive. NoSWO/layoutrepeat.

S5d result37617734037/d08fa8a/2cd1a04a:147s,total1499/5400.
Ctor/asptr/baselines/classif PASS. Pointermethod export/refine/source PASS, stock
free-drop firstrequires own(pointer_typeid)(t,value), empty butnotclosed. After
proof evidence run_case cannotreadmissingfixture.json; diagnosticsetupFAILURE.
Intrinsicmatrix NOT RUN. Compact11480588490/full11480018683. Noacceptance/STOP.

S5e BEFORE dispatch: NEW experimental-source-linked-select-pointer-intrinsics-v2,
patch1c9637f5269d464685ca0fe4e5600571a7618658e4da804e073629fc1ece661f,
design41a3f43 andprior1e970b2. Sameexactintrinsic semantics/domain/fullposts; NEW
completeactual31locals/14BB source/HIR/guard/typedcalls/ordereddataflow/CFGgate.
Falsifiable hypotheses: complete6+10+40matrix and60+10+4classifs pass undernew
profile; then exactactual3intrinsics pass andfirstauthorizedremainingop reached.
Sameprofilector/asptrfullmatrices/14Rust/C/C++baseline controls mandatory.
Diagnosticfix: writefixturebeforecommonrunner; closeexistingemptyrawpointerown
beforestockfreedrop(noElementpermission), recordsfirstnormal/unwindtargetfailure.
Separateassume-init canonicalexport: exactsourceunsafe body/localcertunion copy,
Somep/token/definedown pre, fullp/token/nounwind post; ghostopen/closeexistingMU,
NO bridge. Currentassume lowerings inactive, no component acceptance; canonical
MIR maps fieldaddr/cast/read for nextexactgate. Design41a3f43 BEFORElowerings.
Source/export/decode/refinement failure inconclusive; retainalllogs/MIR/hashes.
Selection30min/proof300s,total1499/5400before,oneactive,noSWO/layoutrepeat.

S5e pre-dispatch contract review: assume diagnostic returns explicitexisting
raw_ptr_own<Element>(t,result), opensDEFINEDwrapper-own first, withSomepre retaining
rawpointerown; noresource deleted/leakhidden. Ghoststrip byte-equality asserted
beforeexport. Separateassumeenv bypassescertctorrequirement withoutweakeningits
certificate; currentinactiveexport expectedunionfrontendinconclusive, notreadresult.

S5e result37618952909/bd4a63d/1c9637f:90s,total1589/5400. BUILD FAIL generated
ScalarInt.size_get int cannotpassUint8.to_int8842. Allnewproof/MIRstages NOTRUN.
Compact11480883970/full11480619259; safety/O4packaging PASS.
S5f BEFORE dispatch: v2sameS5e domain/hypotheses/fullposts/matrix/actualgraph,
new9181630fb00a2a1d6a1fe85ec7e74919cb49be61df78a4edd409afd59e08a445
removesonlyredundantUInt8APIconversion, retains size==1 exactcheck. No semantic
change. Entire6+10+40matrix/60+10+4classifs/ctor/asptr/baselines +diagnosticcanonical
exports +actualintrinsic-on same-runacceptedcomponent required. Source/refinement/
SAFE/body/leak/nounwind gates unchanged. Selection30min/proof300s,1589/5400before.

S5f result37619547036/08e16f3/9181630f:43s,total1632/5400. Setupcanonical
applied.patch !=repo: staleblob/indexhash aftermanualAPIpatch. No build/proof.
Compact11481671010/full11481451361 preserveexactauditfailure.
S5g BEFORE dispatch: v2sameS5e/f domain/fullposts/allmatrix/actualgraph/diagnostics.
Patch ec841d1c95fde729279cfba5c22b678cf15fdba2981dfee342a1184a89220d48
regeneratedfromBASE809+9181630f incleanRAMworktree; onlyoneindexheaderlinechanged.
Hypothesis strictapplied.patch audit nowpasses, retainingALLtrusted-file/code
checks; then unchangedproofhypotheses. NoS6scratchchangesincluded. Selection30min/
proof300s,1632/5400before,oneactive, noSWO/layoutrepeat.

S5g result37619961051/53f4d94/ec841d1c:93s,total1725/5400. Canonicalpatchaudit
PASS, BUILD FAIL8978 untypedguard_type ty.kind ->Unboundrecordfieldkind. NoMIR/
proof. Compact11482375375/full11482115571. S5h hypothesis explicitD.typarameter
resolvesgeneratedrecordlabel whileallgraph/typechecks unchanged; canonicalpatch
regeneration required. Samev2S5e/f/g domain/fullposts/fullmatrix/diagnostics;
selection30min/proof300s,1725/5400before. No semanticdelta/SWO/layoutrepeat.

S5h exactpatch73f0904f11e2f1827a51e3ca83bfe432cbbb1edef142d3d93101917cba4f3e02; cleanbasecanonicalcmp/apply/diffstaticPASS.

S5h result37620410162/634de56/73f0904f:129s,total1854/5400. BUILD FAIL9197
D.uint128record !=Stdint.uint128. Allproof/MIR NOTRUN. Compact11482281192/full11482311201.
S5i BEFORE dispatch: samev2domain/fullposts/6+10+40/classifs/regressions/actualgraph.
Patch7bb39a84b95fd15ed5be29864c3a22774d37c660baafa694188b14970c344320
usesexistingCapnpAux.uint128_get schema reader; canonicalgitdiff/cmp/applystatic
PASS. NEWstorage ghost-only diagnostic per41a3f43: initializedcast-self open/
assert/close+SAMEcanonicalwrapper/frame control; sameSomewrapper targetfullunion
variant pointer cell; None/unknown targetinitializedCASTcell (separates state from
provenance). Allframe/token/noUnwind/resources kept. Noassume bodyclaim/bridge;
unknownmessagesfailclosed untiltargetrawpermissionobserved. Eachindependentcase
saved evenifproofinconclusive. Sameprofileactiveintrinsicregressions stillrequired.
Selection30min/proof300s,1854/5400before,oneactive,noSWO/layoutrepeat.

S5i result37621093604/3d822b0/7bb39a84:154s,total2008/5400. BUILD/ctor/asptr/
classifs/baselines PASS; pointermethod reachespost10 nounwindfalse understock
unwind-permittingfree-drop. AssumeexportE0658 missingtransparent_unions feature;
intrinsic40admissions/ghost NOTRUN. Compact11481794092/full11481549245.
S5j BEFORE dispatch: SAMEv2/7bb39a84/domain/fullposts/allcriterion. Hypothesis
transparent_unions fixturefeature permits exactsourceadapterexport/refinement;
stockunion frontend maystillreject beforebody, classifyinconclusive andgive
canonicalMIRfor nextsourcegate. Independentdiagnostics collectedevenifsetupfailure;
retainexitcodes/nonzerofinalstatus, fullcomponentgates unchanged. GhostcastSome/
unionSome/castNone/unknown probes asS5i, nobridge; sourcebodyclaim separate.
Completeintrinsic6+10+40/60+10+4 +ctor/asptr/14baselines gateactualON. Selection
30min/proof300s,2008/5400before,oneactive,noSWO/layoutrepeat/newsemantics.

S5j result37621751848/2454e86/7bb39a84:190s,total2198/5400. Ctor/asptr/14baseline/
classifiers PASS; intrinsic6+10 PASS,40admissions run32classifiedPASS/8exactmessage
mismatch at intended certificate beforeproof. CORRECTED2026-10-07 from original
S5j logs: canonical assume5local4BB source/export/decode PASS; refinement EXIT1
RawPtr unsupported bb1command4 original25/verified33. Separately after-tail ghost
invalid normal Rust preprocessing, no read proof. Earlier refinement-PASS claim wrong.
GhostSome invalid nested binder, None/unknown initialization requirement reached.
Compact11481774726/full11482378240 retain raw evidence. No newcomponent accepted.
S5k BEFORE dispatch: SAMEv2/7bb39a84 domain/fullposts/fullmatrix/actualgraph.
Hypotheses: profile-specific exact8message corrections plus24reason/16stage/cert
mutants accept intended rejects only; all6+10+40 complete beforeactualON. Remove
illegal after-tail ghostclose while runtimebody byteexact and fullposts/leaks
remain; ghostSome ordinary parameter fixes binder, init-target classification
separates initialization from union provenance. No bridge/permission/kernel change.
Ctor/asptr/14baselines required; intrinsic-on actual full31local14BB graph must
pass and report first causal proof obligation. 2198/5400before,30minjob/300proof,
oneactive/noSWO/layoutrepeat. New04d67f4b assume diagnostic profile NOT RUN here.

S5k result37624082376/128dd56/7bb39a84:175s,total2373/5400. All6+10+40 intrinsic
matrix and60+10+28 classifier/selfchecks/ctor/asptr/14baseline PASS=>component
ACCEPTED. Fullactual31local14BB/all3intrinsic translations/refinement PASS; first
proof error drop_in_place57. Wholehelper NOTPROVEN. Independent assume normal
refinementRawPtrunsupported(bb1command4 original25 verified33), VFunionTodo;
no readpermissionresult. Compact11482879763/full11482659442. Semanticextensions
FROZEN by latest user; S5k dispatched before that correction.
S5r BEFORE dispatch: replay ONLY S5j37621751848/2454e86/v2/7bb immutable compact
artifact11481774726 outerSHA1a5e4957da5db048d02cb56bc518eb8afa195be5384d60f300281ed8f0f036c7.
No verifierbuild/proof execution. Hypothesis all8 oldexact_fatal-only mismatches
are correct intended rejection given rawmutants/sourceMIR and exactmessages;
recompute all56 classifications from saved sameprofile evidence, preserveoriginal
classifications and independently save replay. Exactmessage/stage/cert/profile
mutants must reject; no arbitraryerror or crossprofile reuse. Diagnostic parse/
refinement statuses independent, no ownershipboundary claimed. Budget2373/5400
before, max30minjob, oneactive. PrioractualS5k evidence remains sameprofile,
no repeat needed to establish first remaining callee. No new semanticpatch.

S5r result37625744772/adf1554:11s,total2384/5400. Artifact/GitHubmetadata/all3839
manifest/selfcheck gates PASS; first positive exactclassificationequality failed
because replay computed positive_prerequisite=false while original usesallprevious
positives/vacuoustrue. NoVF/export/refinement/proof execution. Artifact11484166969.
S5r2 BEFOREdispatch: SAME savedS5j/v2/7bb/outerSHA/domain/all56cases/exact8deltas.
Fix original ordered prerequisite calculation, require3positives beforeanynegative,
savecorrectedrecord beforeexactequality. Hypothesis oldproof classificationsnow
identical; remaining40admission+profile/stage/msg regressions mustallpass.
2384/5400before,max30minjob,oneactive, NO semanticchange/build/proof rerun.

S5r2 result37626031885/586c9ae:14s,total2398/5400,3002remain/noactive.
REPLAY_COMPONENT_ACCEPTED fromsavedS5j2454e86 SAMEv2/7bb only;3839memberSHA/size/CRC
PASS,6+10proof classifications unchanged,32admissions unchanged,exact8reason-only
corrections. Alloriginal60classificationfiles+byteexactinputarchive retained;
56correctedrecords separately. Classifier60+10+28/16stagecert+replay36mutants PASS.
NO VFbuild/export/refinement/proof execution. Compact11483952705 ZIP3851647bytes
SHAb12419118ff31e05dccfa91bded8d6660156018754b2c098b4002ec1020c9d75 inclS5j+O4.
Actualfirstblocker remainsS5k128dd56/7bb/v2 drop_in_place57 after fullsource/MIR/
refinement/all3intrinsic translations. WholehelperNOTPROVEN. Semanticextensions
FROZEN, draftsNOTRUN/refinerunchanged/readpermissionhypothesisNOTRUN.
No furtherdispatch needed for latest requested priority; checkpoint budget stays
withinthisphase. RAPxCLOSED/NO-GO,B/CNOTRUN,fullsort4NOTPROVEN.


## S6 experiment card — pointer drop only, 2026-10-07 (pre-implementation)

Entry bea62488b44f8c557e45e04cb4eb259b0173422f; owner authorizes S6 only.
Actual obligation: hint.rs select_unpredictable<T=*const Element>, runtime method
drop.drop_in_place at adapter57; checked mut_ptr.rs method, trusted compiler free
glue, NOT recursive placeholder proof. Hypothesis: exact pointer glue preserves
initialized pointer-cell complete value/thread/frame and never unwinds; existing
caller resources may or may not supply that initialized-cell precondition.
Domain/posts/trust/certificate/matrix: design S6 authorization review above.
New separate cumulative drop-v1 profile from immutable 7bb/v2, only reviewed narrow
translator + checked identity lemma delta. Full patch identity recorded before run.
Expected negatives: wrong value/false post/assertion at caller post/assert; lost
cell at caller leak; duplicated frame at caller post; none/unknown initialization
at drop-call pre; all source/MIR mutations at full certificate before proof.
Independent full case collection, preserving setup/unsupported failures as
INCONCLUSIVE. Same-profile ctor/asptr/intrinsic/full native+Rust regressions.
Outcome: matrix failure -> localized evidence-backed fix/replay; accepted -> actual
helper; missing initialized-cell -> precise obligation STOP; passed call -> next
blocker STOP. No guard/forget/assume-init semantic work or kernel/memory expansion.
Selection verifast_maybeuninit_new_pointer, budget_minutes=30; <=1800/job,
<=300/proof; cumulative used2398/5400, remaining3002; one active hosted run only.


S6 BEFORE dispatch — source-linked drop-v1 implementation:
Cumulative patch SHA256 cd660fe9f470293cc16712a4a71714c8f5f6e802608cedb5b486c3d8a1d27413
from immutable7bb/v2+base809 only; translator+std/lib.rsspec delta reviewed.
Checked identity lemma requires/returns SAME initialized pointer cell+thread;
compiler correspondence trusted separately, no runtime placeholder theorem.
Full exact method3locals/2BB certificate + full actual31locals/14BB gates precede
redirect. Actual baseline and exact5-ghost stock projection variants both retained;
no runtime call/cleanup removed. Complete independent matrix2positive/11proofnegative,
8adapter-source/12MIR/2method-glue-pin controls, classifier64gate/12message/4admission
mutants. All accepted ctor/asptr/intrinsic and14Rust/C/C++ baseline gates repeated
in this exact profile before actual. Original mismatches preserved; reason-only
changes require hosted replay of this run, no repeat proofs for classifier alone.
Local checks only static git apply/diff and bash-n; no build/verifier/test executed.
Selection verifast_maybeuninit_new_pointer/budget30; used2398,remaining3002 before
run,<=1800/job and300/proof. New run follows exact-SHA push; no other active run.

S6 dispatch resolved37637630477, headde7ed9de861eea7346301f6807e242862a68c0ab,
created14:33:02UTC/jobstarted14:33:07UTC, selection confirmed30min/drop-v1.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37637630477).
Before cost2398/5400; job cost/cumulative recorded after completion; one active.

S6/37637630477/source de7ed9de861eea7346301f6807e242862a68c0ab completed,
drop-v1/cd660fe9:194s14:33:07–14:36:21UTC,cumulative2592/5400,2808remain.
Build/canonical patch/spec/schema audits PASS. Fullctor/asptr/intrinsic/14native+Rust
regressions PASS. All13proofcases+22admissions independently collected; bothpositives
VF0 with identitylemma/method/probe returns/leaks. Unsafe method has no generated
SAFE-prototype log; wrong scaffold gate keeps13classifications INCONCLUSIVE.
Additional exact raw diagnostic differences: changed/value normalized to value/value;
cell predicate printed *Element; lost-resource leaks at actual closing line32;
none/unknown optional cell rejects at points_to definition prelude_core213 with
exact caller call31 note, NOT at source errorline31. Original classifications retained.
22admissions:16PASS;3exactreason mismatches(sourceoutput,MIRoperand/destination);
3SETUP failures: sourceinput E0282 unused Element (caller needs explicit ::<Element>),
MIRoutput invalid unique tuple target; MIRcontract pre/post thread_token occurs twice.
None is an intended admission negative until repaired/rechecked. Actual NOT RUN,
gated by component acceptance. No semantic failure or resource boundary established.
Compactartifact11490457470/3990694bytes;full11490457483/8290901bytes inclfullrawlogs.
[Compact](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37637630477/artifacts/11490457470).
Next same-profile hosted replay only for classifier/diagnostics; NEW checks of
3changed admission fixtures and actual after full acceptance, no proof repeat solely
for classifier. Compiler/std/kernel/memory/refiner/runtime/signatures unchanged.

S6 BEFORE completion dispatch — frozen drop-v1, no semantic delta:
Obligation remains exact *const Element payload/*mut *const Element receiver,
initialized cell + thread-token/full-value/frame preservation, nounwind; actual
full selected-pointer/final frame and unwind posts unchanged. Hypothesis: saved
2 positives/11 proof negatives/19 valid admission controls accept after exact
unsafe/log-location corrections; NEW source-input/MIR-output/MIR-contract controls
reject at the typed source/MIR certificate, never setup. All original35
classifications and manifest-verified raw evidence remain unchanged and identified
as run37637630477/source de7ed9de861eea7346301f6807e242862a68c0ab.
Hosted rebuild MUST match full effective tool/spec bytes, std-source hashes,
patch cd660fe9 and exporter/schema/refiner/kernel pins before evidence transfer.
Same-profile accepted ctor/asptr/intrinsic/14 regressions retain original run
provenance. No repeat executable proofs solely for diagnosis changes.
Composite complete2+11+22 gate precedes actual baseline + exact stock5-ghost
projection. If saved replay/admission setup/certificate gates fail, fix only
precise classification/setup and use appropriate replay/new affected controls.
If actual cannot derive initialized selected cell, record exact resource
obligation and STOP; if drop passes, record next blocker and STOP. No guard,
forget, assume, union/refinement or general memory/Drop semantic extension.
Selection verifast_maybeuninit_new_pointer/budget30, <=1800/job, <=300/proof;
used2592/5400,remaining2808 before dispatch; one relevant hosted run only.

S6 completion dispatch resolved37640750987, exact head
 dbb70d0ba1f36e7cf6021da319b65234cc890b18; created14:55:15UTC,
job112858754006 started14:55:22UTC, one hosted job, same30min/drop-v1.
[Completion run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37640750987).
Budget before run2592/5400 used,2808remaining; cost pending completion.

S6 completion37640750987/source dbb70d0 completed14:57:46UTC, cost144s
(14:55:22–14:57:46), cumulative2736/5400,2664remain. Build/profile audits and
classifier selfchecks PASS. Import of replay-pointer-drop.py fails SyntaxError144
(multiline if lacked parentheses) BEFORE any replay/three controls/actual proof.
This is harness SETUP, no new component result or intended negative. Original
source/run/classifications remain retained in37637630477; this failure archived
compact11492611069/full11492226327. No semantic delta. Fix syntax, add HOSTED
py_compile preflight before build; same before-dispatch obligations/outcome mapping
apply, next NEW source run continues exact drop-v1/composite/actual only.

S6 BEFORE retry dispatch: syntax repair/hosted syntax preflight only. No semantic
profile/source/post/precondition delta; no old proof rerun. Same pinned13+19
replay + NEW3admission checks + actual only after35-case acceptance. Full previous
before-card domain/normal-unwind posts/trust/certification/outcome mapping apply.
Budget2736/5400used,2664remaining;<=1800/job,<=300/proof,one hosted run only.

S6 retry dispatch resolved37641538816, exact head
41bb6b651fd2a3eb048fa2fd234fc63812ccaa39,created15:01:07UTC,
job112861495841 started15:01:12UTC. Before cost2736/5400,2664remaining.
[Retry run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37641538816).

S6 retry37641538816/source41bb6b6 completed15:03:38UTC,146s
(15:01:12–15:03:38),cumulative2882/5400,2518remain. Hosted syntax checks PASS;
full effective tool/spec/std/patch bytes IDENTICAL to original37637630477.
All13 proofcases replayed and accepted; original JSON retained byte-identically.
Replay stops on first already-accepted admission source_identity: in-memory tuple
expected_reasons differs from saved JSON list; no evidence/diagnostic delta.
Normalize both objects to JSON values before equality, no acceptance weakening.
Compact11492831906/full11492801889 retain complete initial profile evidence and
successful proof replay. NEW3 admissions/actual NOT RUN in this retry.
Next harness-only retry must collect/save every replay result/delta independently
and run/save NEW3 admissions before replay final classification, avoiding another
first-classifier abort. Full strict composite gate still precedes actual.
Budget2882/5400,2518left; no profile/pre/post/runtime/refiner/kernel delta.

S6 BEFORE independent completion retry: only JSON representation normalization
and independent evidence collection/order changes; frozen cd660fe9/drop-v1.
Full effective profile/std/audit equality still precedes any new checks. All
NEW3admission controls collected/saved before replay classification; original
13proof/19validadmission logs reclassified independently, original35 JSON retained,
per-case deltas archived, no early diagnostic abort. Composite35strict gate remains
mandatory before actual full contract/CFG/stock projection test. Same falsifiable
obligation/domain/posts/trust/expected stages/outcome map as initial completion
card; no repeated proofs solely for classifier. used2882,remaining2518;<=1800/job,
<=300/proof,one relevant hosted run. Stop at actual drop pre or next blocker.

S6 independent completion source4d0e3070ca93e01b7a5ccfad18ea83900bc7536b
committed locally15:07:26UTC. Ordinary git pushes repeatedly return remote Internal
Server Error (also HTTP1.1/no-thin attempts); branch initially remained41bb6b6.
Git Data API safely published identical tree eca47338c16c917e735c313095fb84d10ecb1a89
and IDENTICAL commit4d0e307 with original parent/author/committer/date/message;
ref updated force=false, ls-remote and fetch confirm origin matches. No force-push.
workflow_dispatch repeatedly HTTP500 (numeric workflow ID and named endpoint,
structured same selection/budget JSON); read API works, no new run appears.
GitHub status endpoint says operational, so no general incident claim is made.
This external dispatch failure has no job cost and supplies no new proof evidence.
Budget remains2882/5400,2518remaining; latest completed run37641538816.
Pending exact-code source4d0e307 is READY for composite35 acceptance/actual when
hosted dispatch becomes available; no semantics/pre/posts/tool pin changed.

Dispatch recovered15:17:43UTC without workflow/profile changes. NEW run37642650884
resolved exact head4d0e3070ca93e01b7a5ccfad18ea83900bc7536b, one hosted run,
selectionverifast_maybeuninit_new_pointer,budget30. Earlier HTTP500 requests made
no run. Before cost2882/5400,2518remaining; job duration pending completion.
[Recovered completion run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37642650884).
Local external-blocker draft docs will be updated from this run's actual outcome.

S6 completion37642650884/source4d0e307 completed15:19:40UTC,113s
15:17:47–15:19:40, cumulative2995/5400,2405remaining. SAMEfulltool/spec/std profile;
full35-case COMPONENT_ACCEPTED:13proofcases/19validadmissions replay,3NEW controls
intendedrejections; initial JSON/logs/MIR retained, complete original regressions
keep37637630477 provenance. Compact11493485379 innerSHA4da675062fa21eb2a8a26205ae3fa5bb22a953ed3aaf113bbe53f12060260426;
full11493285528. Actual baseline fullsource/export/decode/refinement/method+actual
MIR/redirectPASS; body reaches drop57 and fails initialized cell requirement
verified/lib.rs110,55–58: No matching heap chunks: points_to<*Element>(__result2, _).
Projectedactual source/export/decode/refinementPASS, VF2 certificate failbefore
proof `actual projection ghost source span`. NOT a resource verdict/intendednegative.

S6v2 BEFORE implementation card in design: exact5ghost ordinary inclusivehi and
explicit half-open parser coordinates checked TOGETHER. Independently reviewed
raw MIR shows exporter convention; current gate uses wrong half-open ordinaryhi.
Trustedadmissiondelta within onlyS6, newdrop-v2 profile, freshfullcomponent/proof/
admission/regression gates +2independent actual ghostcoordinate negatives before
projectedactual. No oldprofile proof reuse; no memory/refiner/runtime/body/glue
semantic expansion, no04d. Normal/unwind/domain/post/pre/outcome map in design.
Budget2995/5400,2405remain;<=1800/job,<=300/proof,onehostedonly. If projected/drop
pre fails STOP precise resource; ifdrop passes STOP nextactual blocker.

S6v2 BEFORE dispatch implementation pin:
experimental-source-linked-select-pointer-drop-v2, cumulative patch SHA256
8e62e6c3044fda7533637d242fb5e8a575eac0d7600213e8e3ba00a182dc0d7c.
Independent static review confirms ONLY8ghost-coordinate certificate lines plus
patch offsets differ fromcd660fe9. Stdlib ghost/glue lemma/method semantics/body/
contract untouched; exporter/schema/refiner/kernel/prelude fixed. Fullfresh ctor,
asptr,intrinsic,S6 independent2+11+22 matrices and14baselines beforeactual;
no oldprofile proof reuse. NEW2actual MIRmutants regularhi92→93 and explicitend94→93
require distinct exact source-span/explicit-coordinate fatalities beforeproof with
source/stage/refinement/mutation integrity; both collected independently. Canonical
projectedactual only afterbothcontrols AND baseline fullcert/intrinsic/drop redirect
infrastructure (baseline initializedcell proofnegative permitted). User's exact
actual normal/unwind target preserved, stop at stockprojection/drop pre or nextblocker.
Localchecks diff-check/bash-n only; hosted Python syntax preflight precedes build.
Budget2995/5400used,2405remain;selectionverifast_maybeuninit_new_pointer,budget30,
<=1800/job,<=300/proof,one hosted run only. No04d/broadersemantic extension.

S6v2 dispatch37645561507 resolved exacthead
85ec1711700ff85c899b18b7e021f076aeddb8e6,created15:38:34UTC,
selectionverifast_maybeuninit_new_pointer,budget30,one relevant hostedrun.
[Fresh v2 run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37645561507).
Beforecost2995/5400,2405remaining; jobduration pending completion.

S6v2/37645561507/source85ec171 completed173s15:38:39–15:41:32UTC,
cumulative3168/5400,2232remaining. Fresh constructor/asptr/intrinsic/S6 matrices and
14baselines PASS; S6COMPONENT_ACCEPTED full13proof/22admission in8e62/drop-v2.
BothNEWactual ghostcontrols SETUPfailed (normal second exporter invocation) with
`first regular ghost hi changed`; not intended negatives. Readonly mutationpayloads
were retained (regularhi92→93, explicitend94→93), but later NORMALexporter produces
shifted ghost spans. Wrapper exception overwrote mutationrecord; VF frontend98.
Baselineactual stillmissinginitializedcell req110/call57; projectedNOTRUN(controlgate).
Compact11493408570 innerSHAb160edcd347c02ffafcd94ac0258e805d488bed10a500b64cd3e632b5d8d49ae;
full11493098966. Original setup classifications remain INCONCLUSIVE.

Reassessment from pinnedexporterpreprocessor.rs/lib.rs + all5normal traces:
normalmode injects crate::VeriFast_ghost_command(); length32 before each //@
command; readonly doesn't. GhostRange.span bytehigh shifts32, explicitline/column
start/end remainoriginal. Normal source spans (1-based) ends125/126/71/130/131 vs
readonly93/94/39/98/99. Not nondeterminism/source/tool drift. No v3patch made.
Existing v2certificate checks readonly geometry, cannot matchnormal consumed MIR.

BEFORE normal MIR diagnostic implementation: hypothesis same exactfrozen normal
exporter input has stock32byte ghosttag coordinates; fullnormalgraph must be
captured before anyfurthercertificate change. Domain/source actualprojected
37e5original/8a82verified fromacceptedv2run pinnedcompact+manifest; FULL source
normal selected-pointer/thread/frame and unwindfalse target unchanged but NOT
PROVED bythis diagnostic. Compiler nightly2026-02-05, stock26.09 archive/exporter
2b8ebb... andschema7f3eb...809 pin unchanged. Hostdownload/compiler/export/decode
ONLY, noverifier/consolebuild/refiner. Capturefulltypedlocals/blocks/callees/CFG/
5rawghostordinary+explicitcoordinates, sourceintegritybeforeafter, originalmatrix
provenance. Expectedpositive exporter/decode0 exactsource; anysetupfail stays
inconclusive; no intendednegative/componentacceptance/helperproof claim.
If normalgeometry is exact documentedstockinjection andtypedruntimegraphpreserved,
review ONLYS6admission correction+freshgates beforeimplementation. If it requires
broaderghost/parser/refiner/kernel/memory semantics, STOP at exacttrust/applicability
boundary. No speculativepatch/no04d. Budget3168used2232remain;sameworkflowselection
30min,onehostedrun; <=1800/job,<=300/proof. No localexecution.

Normal-MIR diagnostic dispatch37648838042 resolved exacthead
8f1b8f44a655fcfde1fd12106d79dbbb58917332,created16:02:08UTC;
selectionverifast_maybeuninit_new_pointer,budget30,one hostedrun.
Independent static audit passed stockpins/NORMALmode/no proof or refiner/fullraw
evidence/failureclassification. Beforecost3168/5400,2232remain; durationpending.
[Normal MIR diagnostic](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37648838042).

Normal diagnostic37648838042/source8f1b8f44a655fcfde1fd12106d79dbbb58917332
completed65s16:02:13–16:03:18UTC,cumulative3233/5400,2167remain.
Artifact/manifest/fullfixture/toolpins authenticated andsourceunchanged.
Exporter1 BEFORE Rust compilation: `Option 'error-format' given more than once`.
NORMAL exporter appends overflow/crate/error-format flags itself; diagnostic
duplicated these input arguments. No MIR/proof/resource result. Structured
DIAGNOSTIC_EXPORT_OR_DECODE_FAILED kept;compact11496405518 innerSHA
5d1bbb3a9e895f73d3801eda20709c86ed0141787188c7ea307e0551388bdfbf,
full11496575242. Next orchestration-only argument repair removes built-in flags
from NORMAL input, retains exact sysroot/edition andeffectivecompilertrace;
samecomponentprofile/source/exporter/schema/trust/card, NEW diagnostic run.

Normal diagnostic37649244205/sourcef6fdf5ba4c3a1bee44bdb3566ab354d1e558fe6d
completed69s16:05:10–16:06:19UTC,cumulative3302/5400,2098remain.
DIAGNOSTIC_EXPORT_DECODED: exactfixture/artifact/manifest/toolpins/effectivecompiler
arguments/sourceintegrityPASS, export/decode0, NO verifier/refiner/proof.
FullNORMAL actual36locals19BB retained;readonly31/14. Five regularghost high
columns124/125/70/129/130 (0-based),explicit parserhalf-open ends94/95/40/99/100
(1-based) atlines40/41/59/61/62. Fullstockinjection/runtime/cleanup correspondence
must be reviewed beforeanyadmissionupdate. Compact11495097694 innerSHA
ead2a0c8a501becdbf0bbcf6c521d356a3457fb232f5e5a4b09793a618e2c093,
full11495657034. No intendednegative orcomponent/helper theorem follows.
[Successful normal capture](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37649244205).

S6v3 BEFORE dispatch implementation pin: profile
experimental-source-linked-select-pointer-drop-v3, cumulative patch SHA256
94ffc64ce15811ac0de62e55489fb1e61242883b7258aa22969bbefa9ec184e8.
Static independent cert/harness review PASS; root confirms entire stdlibspec patch
section byte-identical to8e62/v2. Separate projected-only36/19 exact graph/source/
scaffold checker; baseline31/14 unchanged, no execution/AST/MIR rewrite. Frozen
exporter/schema/refiner/prelude/kernel/memory unchanged. Freshfullcomponent/
regression matrices beforeactual, then18NORMAL-only independent certificate
mutants; unchangedreadonly bytes/refinement and separateNORMAL mutationevidence.
Expectedexactpredicates/types/callees/operands/results/normal-unwind/source spans
reviewed against captured fullMIR. No localexecutablechecks, diff-check/bash-nPASS.
Canonicalstockprojection only afterbaseline infrastructure +all18; stop first
resource/droppre failure ornextactual blocker, no broader semantic extension.
Budget3302/5400used2098remain;onehostedrun,sameworkflowselection30min,<=1800/job,
<=300/proof. Prior classifications and failed hypotheses retained, not overwritten.

S6v3 dispatch37651717720 resolvedexacthead
`dfc1f1d740689de8f427ac549da558d64a4318eb`,created16:24:03UTC;
selectionverifast_maybeuninit_new_pointer,budget30,one relevant hostedrun.
Beforecost3302/5400,2098remain; durationpending. User's latest steering preserves
samegoal/budget/stop and requires explicit normal/readonly correspondence; table
now records eachghost local/BB and regular/explicit coordinates from diagnostic,
expanding the earlier preimplementationfaef1a3 mapping, no new semantic change.
[Fresh S6v3 proof and integration run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37651717720).

S6v3/37651717720/source dfc1f1d740689de8f427ac549da558d64a4318eb
completed266s16:24:07–16:28:33UTC,cumulative3568/5400,1832remain.
Fresh S6 full2+11proof/22admissions COMPONENT_ACCEPTED; ctor16source/proof+9MIR,
asptr3+6proof/17admissions,intrinsic6+10proof/40admissions,14baselines PASS.
Two newNORMAL coordinate controls intendedreject; allreadonly outputs/refinement
preserved. Other16controls independently SETUPfailed `MIR item must begin with
 a parenthesis`: block/localregex start includedindent whitespace. No intended
negative/resource verdict for those16; canonicalprojected gatedoff. Actualbaseline
fullinfrastructure/drop redirectPASS, same initializedcell pre110/call57 failure.
Compact11497076310 innerSHA f2c9a1dcda5785af850a51e103bc0c7d07df38c39ed9809afb33211bde997fb0;
full11496683381; rebuiltconsole b8cf77ce12692022bcd9a30043d7066b1fbdb7f1b2eab44847de048861db68cb.

BEFORE v3completion implementation: narroworchestration repair ONLY indexesfirst
'(' insideblock/localregex match; nosemanticpatch/expectedpredicate/diagnostic
change. Separate pinned-v3 completion imports immutable fullproof/regression/two
coordinate acceptance evidence from37651717720/dfc1f1d/artifact11497076310,
checksfullmanifest+source/profile/patch/compiler/effectivebinary/spec/std hashes
against freshIDENTICALprofilebuild, retains byte-exact originalclassifications/
rawlogs and all16setupfailures. Replays two intended coordinatecontrols fromsaved
logs atsameprofile; NEW independently collected16controls atunchanged exact
certificate obligations, then composite18/18+acceptedcomponent/regression gates.
Actual baseline +stockprojected proof only afterstrictcomposite infrastructure.
No repeatfullproofmatrices merelyforharness fix; nofrozenv1 replay edit. Hosted
mutator parsing/preflight ofsaved fullMIR permitted beforebuild, notproof. If any
profile/compiler/spec/tool mismatch failclosed, no evidence transfer. Domain/full
normal-unwind target/stockprojection/trust/stop asfaef1a3 unchanged.
Budget3568used1832remain,one relevant hosted dispatch<=1800,proof<=300.

S6v3completion BEFORE dispatch staticreview PASS. Patch94ffc64c unchanged;
no expectedfatal/predicate alteration. Pinned import checks immutable fullproof/
regression rawtree and allmanifestmembers/tool/compiler/spec/std identities.
Hosted16mutatorparse+capnpencode preflight is before consolebuild and explicitly
NOTproof. Complete repeats exactordered16/status/encode0/diagnosticflags checks.
Two priorcontrols replay sameclassifier fromrawlogs/MIR, wrapperbytes rehydrated
only in disposablecopy andSHAchecked; require exact original JSON equality,
no verifier/refiner invocation/relabeling. Fresh16 collected independently and
composite18/18 gate runs BEFORE baselineactual; canonicalstockprojection follows
only ifbaselineinfrastructure also matches. Original16setupfailures retained.
Independent finalimport/replay/gate review foundno staticblocker. Diff-check/
bash-nPASS, no localexecution. Budget3568used1832remain/noactivebeforedispatch;
<=1800/job,<=300/proof,one relevanthosted,same30min selection. No newprofile/budget.

SAME-v3 completiondispatch37654585346 resolvedexacthead
`f1774d54b0d3ced96724b07aba9acfecb51b1633`,created16:45:47UTC,
selectionverifast_maybeuninit_new_pointer,budget30,one relevant hostedrun.
Beforecost3568/5400,1832remain; durationpending. Profile/patch94ffc64c unchanged;
onlymutatoropeningfix+pinnedcompletion orchestration, noexpecteddiagnostics change.
[Completion run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37654585346).

V3completion37654585346/sourcef1774d5 completed184s16:45:53–16:48:57UTC,
cumulative3752/5400,1648remain. Immutableprofile/compiler/tool/std identityPASS;
rawcoordinate replay2 unchangedJSON +16NEW intendedadmission rejects =>18/18PASS.
Baseline fullinfrastructure/dropredirect PASS, same initializedcellpre110/call57.
Projected source/export/decode/refinement/full36/19 actual+methodcert PASS, then
finalredirect checkpointreject `actual pointer method receiver` BEFOREproof:
hookhardcodesbaselineMove23 butcertifiednormalDropBB9usesMove26. Notresourceproof.
Compact11498401742 innerSHA7ec6ae18297d2c1deffb9b7641479d317379f4d224e23c94c3eec59309fcac79,
full11497209013. No classificationrewriting or prooftransfer across profiles.

BEFORE S6v4 semanticimplementation: ONLYlastreceivercheckpoint chooses26 after
fullcertified exactprojection,23 afterfullcertified baseline; retainallotherguards,
noOR/genericmapping/ASTrewrite/stdspec/body/glue/runtime/CFG/resource change.
Designcard mapsR23→N26 fromsamepinnednormaldiagnostic+completed18negativecontrols.
NEWprofile drop-v4 =>freshfullS6+ctor/asptr/intrinsic/14baselines, NEW19NORMAL
admissions (prior18+explicit oldreceiver26→23, intendedfullgraphplace_26), then
stockprojectionuntilprecisecellpre ornextactualblocker; STOP. No broaderfreeze
lifted. Budget3752used1648remain; capnextjob25min1500 includingcoldsetup andcleanup,
runnerreserve120,proof<=300,onehostedworkflow_dispatch. SAME5400 budget.

V4 static implementation/review PASS; profile drop-v4/patch
c7cc08a995bac5879901f4fe08030f09d23bdfefb1a3ab5893be12a8dd1f8fc1.
Final guarded receiver-only delta, no stdspec/glue/source/runtime/CFG change;
fresh full matrices +19 independent NORMAL negatives before actual. Workflow
selection input30/effective cap25, runner reserve120/proof<=300. Before3752used,
1648remain/noactive. Preimplementation card a649f96 localcommit precedes code.
Ordinary Git push HTTP500 twice, GitData blob write500; readAPI works, no force.
Publishing exact ancestor/implementation SHA before any dispatch remains mandatory.

Git push recovered: a649f96 and75681fbc57bda633f59096cdc28f0c1aa61daef8
published ordinary fast-forward. V4 dispatch37656621026 created17:07:29UTC,
exactimplementationSHA verified, one relevant hostedrun, input30/effective25min.
Beforecost3752/5400,1648remain, durationpending. No local executablechecks.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37656621026).

S6v4 final37656621026/source75681fbc57bda633f59096cdc28f0c1aa61daef8,
202s17:07:34–17:10:56UTC ->3954/5400used,1446remain/noreset/noactive.
Fresh fullconstructor/asptr/intrinsic/drop matrices+14baselines PASS; drop2+11+22,
19independent NORMAL negatives intended exact predicates beforeproof incloldreceiver.
Readonly/source/refinement unchanged; projected full36/19+methodcert/redirectPASS.
Rawactual prooftrace accepts stockopens40/41, split59, retained runtime drop60
(req115 initializedcell consumptionretry), closes61/62; firsterror forget(guard)63
stockreq420 nominal own(DropOnPanic_type_info(pointer_typeid(Element_typeid))).
Knownsome +existingwrappercells +exactreceiverpointer +stockopen/points_to_ equivalence
supply droppre; preservedcell/value/thread allowstockreclose. No newElement rights.
Currentprefix only: no printed branchheap/condition, finalreturn/leak/unwind contract
unproved. Classifier INCONCLUSIVE/kindintrinsic_select retained; raw exact obligation
reported separately. STOP at nextguard-own blocker; no guard/forget/memory changes.
Independent audit fullmatrices/raw19 controls PASS. Compact11500295662/full11500150817,
innerSHA5ed34fef59d69e3f766186952338c44a09b5016e5caa0e2b601fe0b0b184a549,
manifest5177/5177hash/CRC/sizeverified. Effectiveconsole799fac7491db7d43e786713ae4ff75427d7e77c227fb4f7438e433b297514cd0;
exporter/schema/refiner/compiler frozen matching recordedpins. No local executabletests.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37656621026),
[compact](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37656621026/artifacts/11500295662).

S7 BEFOREimplementation authorization fromffa370a: exact localguard forget only,
same3954used/1446left. Design SORT4-SELECT-FORGET-DESIGN.md records sourcebody,
existingtrusted ManuallyDrop identity, unsafe checkedbody with reachable tokenpre,
no guardown declaration/SAFEfalseown claim, wrappercells/borrowtokens externalframes.
Independent static investigation/review finds route plausible but forgetfullMIR and
no-unwind/Drop evidence absent. S7a frozenv4 diagnostic only (new isolated files),
focus helper/frameprobe, positive+independent intendedproofnegatives, source/NORMAL/
readonly/refinement capture, no actualredirect. Cap20min1200 with120reserve/proof300,
one hostedrun. Fullnewprofile matrix/admission/regressions beforeactualintegration;
STOP if separate guardownership/Dropmodel needed, otherwise nextactualblocker.

S7a staticfocusreview BEFOREimplementation: same-file nestedfocus also selects
outerfunction inclusive range, whose first prooffailure would preempt helper.
Do not count that as bodyproof. Amended design chooses separate helper/probe
include! item files inside sameactualguard lexicalscope, preserving nominal ADT,
focus byactual expansion filepath excludesparent. Source/ghoststrip/stage hashes
and readonlyrefinement coverallthree filepairs. FullNORMAL+readonlycapture verifies
nominalidentity/macrolocations/noextraactualruntimeops; this isolation is untested
untilhosted and no admission accepted. Parent/setup failure remainsINCONCLUSIVE.

S7a BEFORE code staticisolation refinement: explicitlyunsetall admissionREPO_ROOT
flags; insertedincludes are outsidev4 exactsourcegate and mustnotexpandthatgate.
Retainfullactualselect/guard/Drop prefix, omitONLYunused appended checkedcallee
items whoseunion bodies requireactiveconstructorcert, record omissions/sourcebytes.
Noactualtranslation/admission/redirect accepted fromdiagnostic; stock MDidentityonly.

S7a BEFOREimplementation importisolation correction: eachincludefile singlefnitem;
put lexicaluse std::mem::ManuallyDrop inparentbeforetwoincludes. Manifest exactthree
nonexecuteditems, sourceghoststrip/removeitems originalactualprefixexact. Diagnostic
negative requiresintendedfunction/stage/predicate/post/assertlocation, leakonlyafter
bodyreturn+leakcheck; samefilegenericerrornotintended. Borrowtokens/fulladmissions
NOTRUNinS7a, documentedratherthanclaimed. No semantics/admission/ownership change.

S7a implementation BEFOREdispatch staticpins/source review PASS. Newdiagnostic file SHA256 0cae92cb49911903368a3d3b447293a3c5a340ac3484430fd1ab0058501f053f;
newrunner 8f4b4f050c54f3eb92e63729689e608fbad1845cf50bdf0b8e53e5f2e87cd783.
Nochanges v4patch/runner/matrices/sourcecontracts; defaultworkflow route retained.
Newdiagnostic adds lexicalimport+2singlefnincludeitems inexactlocalguardscope,
allthreeoriginal/verified filesghoststrip/stagehashed. Samev4patch c7cc08a9 butall
admissionroutesinactive. BothNORMAL+readonly export/decode+refinement collected
independently for9cases; focusedbody/helper+frameprobe, exactfirsterrorobligation
classifiers; unknownoutcomeINCONCLUSIVE originalrawJSON/logs retained. Noaccepted
component/actualredirect/newtrustmodel fromdiagnostic. Before3954used/1446left,
onehostedjob cap20min1200,reserve120,proof300. No localexecutableverification.

S7a staticindependentreviewPASS, firstdispatch37665233357 created18:14:01UTC,
source2ba63774e964e2ca76b3b1639e550cb93e70769e exactremoteSHAconfirmed,
selectionverifast_maybeuninit_new_pointer/forget_guard_stage=forget_diagnostic,
input30/effectivecap20/reserve120; one relevanthostedrun. Before3954used/1446left,
noreset; durationpending. Frozenv4patch/noactiveadmission/noactualredirect.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37665233357).

S7a37665233357/source2ba63774e964e2ca76b3b1639e550cb93e70769e,
133s18:14:05–18:16:18UTC,4087used1313remain. All9 independentlySETUPfail ValueError
helper source changed beyondannotations BEFOREexport/proof; zero intendedoutcomes.
Greenbadge onlydiagnosticcollectioncomplete, NOTproof. Compact11502119135/full11503445316.
Rootcause: strip_ghost_annotations leaves4newlines fromghost_block separators;
originalhelper/probe incorrectlyomitthatexactscaffold, fixedexpectedhelpercompare
alsoomitsit. BEFORErepair: originalcounterparts useEXACTstrippedcontract whitespace,
verifiedruntimebody unchanged; requirethat exactsignature/scaffold/body, no generic
whitespacenormalization/no expectedmessage/classification rewrite. Hostedpreflight
constructsall9sourcepairs BEFORE toolbuild, thennewindependentsamev4diagnostic.
No semanticchange/newadmission/ownmodel/redirect. Nextjobcap20min1200with120reserve,
proof300,onehostedrun,samebudget. Old9rawclassifications retained.

S7a scaffoldrepair staticreviewPASS, patch c7cc08a9 unchanged. Verifiedhelper/probe
contracts/runtimebody unchanged; original nowexactstrippedscaffold. Hostedall9
constructionpreflight beforedownload/build, fullphase regeneratesall9 +requires
exact6fileSHAmanifest match beforetools. No classifier/expectedobligation change.
RepairdiagnosticscriptSHA 61517acb3002454c5f9b942dea8cfd8351194f9c808477d530e0d1417b847122
runnerSHA 6ed0ae2031a5c00a44776049d621dc75b6820e9b209d4a484f3c412956689bab.
Firstcompact11502119135 innerSHA3b7d1c7e7d4d25dbea43098b915bda2c59f728e38ba5e5fecddf1f5bb41f20b4,
manifest872/872hash/CRC/sizeverified; original9classifications retained.
Before4087used/1313remain, onehostednextcap20min/reserve120/proof300, noreset.

S7a repairednewdispatch37666273705/source3a4b0e9d375e8871b541ed18e6b340cf152734be,
created18:22:04UTC, exactremoteSHA confirmed; samev4patch c7cc08a9, inactiveadmission,
noactualredirect, original9setupclassificationsretained. Before4087used/1313left,
cap20/reserve120/proof300, onehostedrun durationpending/noreset.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37666273705).

S7a repaired37666273705/source3a4b0e9d375e8871b541ed18e6b340cf152734be,
122s18:22:08–18:24:10UTC ->4209used1191remain. Hostedall9sourcepairs preflight and
full regenerationSHA PASS; all9independently compilerFRONTENDfail NORMAL/readonly,
focusedVF/refiner1: expected `{` found keyword `fn` and non-statementmacro include.
No MIR/proof/intendednegative. Samev4/noadmission/redirect; originalclassifications
retained. Compact11503186835/full11502367969. Pinned rustc db3e99bb primarysource
source_util.rs ExpandInclude implementsmake_expr/make_items, no make_stmts override;
base.rs defaultmake_stmts attempts expression, explaining failure. Changing braces
alone would still use statement expansion; don't speculate/countit as a proof fix.
Investigating lexicalconst_:()=include!(blockfile) with helper+probe declarations in
oneblockexpression, unchangedactualguardtype/no runtimeoperation. No implementation
or newsemantics before reviewedcard. Same1191remaining/noreset/noactive.

S7a expression-isolation BEFORE card: reviewed const-expression include candidate
in SORT4-SELECT-FORGET-DESIGN.md. Single actual guard/Drop, four source files pinned
by preflight/regeneration, separate focus lines, same nine intended predicates.
No admission/profile semantic change. Capture exact nominal type, macro spans,
NORMAL/readonly MIR/refinement and nonvacuous body. STOP new guard/Drop/memory model.
Budget4209used1191remaining; next cap18min1080/reserve120/proof300, samebudget.

S7a expression-isolation dispatch37667942855/source f101203bfe5e6100ee2ae60fc0cae62ef7c6149b,
created18:35:03UTC; exact remote confirmed, no other active relevant job.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37667942855).
Static independent review PASS; cap18/reserve120/proof300; before4209used1191remain.
V4 unchanged/admission inactive/no redirect; raw prior9+9 failures retained.
Second compact11503186835/full11502367969 audited: innerSHA
83e6f295232a92d14c22555f2460e556edc958f76786cac965134d86915ce836,
1099/1099 entries hash/CRC/size PASS. No proof gain from packaging.

S7a37667942855/source f101203bfe5e6100ee2ae60fc0cae62ef7c6149b:99s,
18:35:08–18:36:47UTC ->4308used1092remaining. All9 independently readonly export/
decode/refinement0, normal/focus1 compiler incomplete_include. Frozen preprocessor
appends3fnstubs after everyfile (preprocessor.rs207), invalid after included single
expression. No helper body/proof negative. Readonly exact nominal local guard and
helper select_unpredictable::_::checked_forget_guard captured; sole MDnew Move
call normalBB1,cleanupBB2 UnwindResume, no Drop in helper. Cleanup retained and
nounwind unproved. Actual guard cleanup remains in parent CFG. No guard-own/model
change, no admission/redirect, original classifications retained.
Compact11503762679/full11502754044; raw full console downloaded/read.
Source-only isolation alternatives investigated before another card/change;
direct impl include unsupported by pinned MacResult make_impl_items defaultNone.
No lint weakening/toolchain-path skip/preprocessor/model patch permitted.

BEFORE S7a macro-item card: exact original guard ident passed to macro from separate
item module, preserving actual lexical scope/body/contract and frozen toolchain.
Read-only investigation rejects inline focus parent contamination/directimplinclude.
Full design final section defines ghost span/nominal/body gates and STOP if route
fails; no v4 admission relaxation or classifier rewrite.4308used1092remain,
nextcap18/reserve120/proof300/onehostedrun. No semantic tool change.

Macro-item diagnostic dispatch37669436220/source a5ce1b5f71d2f0a2ecd1f74e44063ba079683b4d,
created18:46:46UTC, exact remote confirmed, sole active relevant run.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37669436220).
Independent static review PASS; no classifier/v4 semantic change; cap18/reserve120.
Before4308used1092remain; durationpending. Previous compact innerSHA
a3e1ce82a09bca102434d5c266fd5602f7ff673e06f74824a73dc809e98807dd,
1099/1099 hash/CRC/size PASS. Compiler scope supports caller lexical item/type import
per Rust Reference macro mixed-site hygiene; MIR association still unproved.

S7a final37669436220/source a5ce1b5f71d2f0a2ecd1f74e44063ba079683b4d:
103s18:46:51–18:48:34UTC ->4411/5400used989remaining;457s S7 total, samebudget.
All9 NORMAL+readonly export/decode/refinement0, source/preflight hashes PASS.
Exact original local guard, helper4locals/3BB and probe7locals/3BB complete records
identical between NORMAL/readonly. Helper isFromExpansiontrue, MDnew typedMove,
normalReturn/cleanupUnwindResume retained, noDrop. No general expansion admission.
Bothpositive bodies reachreturn/leak, thenfocusedVF1 on globaldead-code inventory
(vfconsole265–282/check_focus verify_expr154–162). Nonvacuous body prefix is not
accepted complete proof. Seven firsterrors match exact intended annotations;
regexdoublecounts diagnosticnoteheaders, rawall9INCONCLUSIVE retained/no repair.
STOP independentpositive acceptance; no allow_dead_code/scopedexemption/preprocessor/
focus/model patch or reverse-order actualredirect. No guard-own deficiency proved
in body; actualS6 forget63 nominalown stillmissing, S7 actual NOTRUN. Full S7
admission/mutations/borrow/newprofile regression NOTRUN. Report/details in
SORT4-SELECT-FORGET-RESULTS.md; STATUS/Currentresult/coverage/ledger updated.
Compact11503963988/full11503793868 innerSHA
12c3f3f509fc845dd1aa1bb7d8b80f8fcf70e6ab6064af3436168f0b9489dd83,
1135/1135hash/CRC/size PASS. Console/full artifacts read, source/v4pins unchanged.
Noactive job; next needs independentacceptance design, remaining989notnewbudget.

S7b BEFORE card from8fdb579: owner authorizes standalone unrestricted generic unsafe
forget body theorem, exact MDnew source, whole minimal crate nofocus/actual/guard/
macro. Samev4 existingMD trust, thread pre/post and unwindfalse; completeexit0/body/
return/leak+exports/refinement/hash needed, declarationdeadcode meansSTOPcausaltrace.
Separate classifier replay fromimmutable376694 rawlogs, original classifications
retained, neverdeadcodeexit1positive. Firstcap8min480/reserve120/stage60/proof120;
replaycap2min120 nobuild; before4411used989remaining/noreset/onehostedrun.
S7b full timed inventory fixed from same-v4 accepted37656621026 log:6 pinned
prelude lemma functions +sole checked_forget_generic, exact order in design.
No arbitrary outside-source headers allowed; diagnostic notes do not count.

S7b first standalone dispatch37675513854/sourcec9c59a85807da0135a8192b1912b15d510c68028,
created19:34:31UTC, exact remote confirmed, soleactivejob. Selectionforget_generic,
cap8min480/reserve120/fullVF120/otherstage60; before4411used989remain, noreset.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37675513854).
Independent staticreviewPASS; strict classifier separatecommit0c4fff1. Replay
provenancefix independentlyreviewed/pinswholeinnerZIP +selectedtreebytes, notrunyet.

S7b first37675513854/c9c59a85807da0135a8192b1912b15d510c68028:
178s19:34:36–19:37:34UTC ->4589used811remaining. Hostedwholeunitnofocus, all7exact
functionheaders/body/return/leak; fullVF1 sole verified/lib.rs(3,1-16,2):deadcode.
NORMAL/readonly/decode/refinement0; fulldecodedMIR hashesidentical3b08b5835f03ff152e6dae68bbf4ce05d1491d7919124f06222794f844b8553d.
No completebodytheorem/SAFEcorrespondence/actualredirect. Genericunit removesother
focused-deadcode inventories, leavesadapterdecl exact mandatoryfailure. Read-only
provenanceaudit underway; no syntaxvariants orsemanticchanges. Compact11507342250/
full11506168168 downloaded/read. Replayfix separate: cap2min120 nobuild/verifier,
wholepinnedoldarchive +bytewiseinputtree checks, originalclassespreserved.

S7b classifier-only replay37676357686/processor dd4b0493b8411d92f61f525a3c7ef6ec0429d021:
12s19:41:18–19:41:30UTC ->4601/5400used799remaining. SUCCESS immutable input
37669436220/sourcea5ce1b5f71d2f0a2ecd1f74e44063ba079683b4d, wholeinnerZIP SHA,
261 selected inputfiles exact, all9 original classificationbytes preserved.
Seven classifier controls PASS; new separate map2INCONCLUSIVE(deadcodeexit1),
7INTENDED_NEGATIVE(exactfirsterror/no deadcode). No proof run/semantic change or
fullmatrix admission. Artifact11506224082 SHA
be6bb45df5034f8be8d992906dfd08f1f0183d30b2dbf7796d389b93894f7691.
New BEFORE AST provenance card: samegenericunit/contract/profile +existing
-dump_ast_with_locs only; test orphancleanupReturnStmt hypothesis, not proof.
Cap6min360/reserve120, remaining799; no semantic/admission/actual change.

S7b AST-only diagnostic dispatch37678089113/source
`a6f077a5aa89ad25df94295320cdbe18ebe4b9d9`, created19:54:58UTC,
remote exact confirmed, sole relevant active run. BEFORE card0c58df5; independent
static review PASS. Existing console -dump_ast_with_locs only, samegenericunit,
fullnofocus VF/deadcode and exports/refinement. Cap360/reserve120/fullVF120,
before4601used799remaining. No semantic/actual redirect or classification rewrite.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37678089113).

S7b AST diagnostic37678089113/sourcea6f077a5aa89ad25df94295320cdbe18ebe4b9d9:
151s19:55:03–19:57:34UTC ->4752/5400used648remaining, noreset/noactive.
Source pairs, complete NORMAL/readonly MIR and all effective schema/tool/spec/patch
hashes match first37675513854. Exports/decode/refinement0; fullVF1 soleadapter-span
deadcode afterall7body/return/leak, INCONCLUSIVE. AST2746bytes SHA
172fbc51f8592fbdad092a7f0abaa1895077d72c4dd60cd887b37fa9e196aecc:
Decls7–9; normalassign/Goto1 at11–13; label2/Return(unwinding)14–15 hasnoincoming
branch; label1/Return(returning)16–17. Frozen FnCallResult lowering dropsunwindbranch
buttargetinventory retainscleanup; registeredsyntheticreturn sharesprintedwholefn
span. Physical loc-key identity notserialized/uninstrumented, so structuralcause
supported but exactresidualkey notproved. STOP frozen translation/deadcode obstacle;
no syntaxvariants/semanticpatch/admission/redirect, no successfulauxiliarytheorem.
Compact11507826485/full11507796366 innerSHA
13bc43d3fe0e095b4aed890760fa4759965205e75963722923c829e556d2be47,
853/853 SHA/CRC/size PASS; fullconsole/artifactread. Full S7 matrix/regressions NOTRUN.
Actual stays lastS6 forget63 nominalown atspec420; fullhelper/sort4 NOTPROVEN.
Iteration341s=178+12+151; checked c9c59a8/a6f077a diagnostics, dd4b049 classifierreplay;
finaldocumentationHEAD has no proof run. No further dispatch in this closeout.

## S7c BEFORE — authorized CFG diagnosis/repair (2026-10-07)

Entry070b9236, owner authorization overrides S7b STOP only for narrow CFG scope.
[Complete causal/domain/trust/control/outcome card](SORT4-SELECT-FORGET-DESIGN.md#s7c-cfg-repair-before-implementation)
is recorded BEFORE implementation. Budget4752/5400 used,648remain/noreset;
no active run. Physical-loc diagnostic precedes repair; acceptance build has no
instrumentation. Existing S6v4 unchanged; experimental MD::new normal-target
successors only. All tests hosted, single relevant run; actual redirect excluded.

S7c diagnostic dispatched37681688627, source32d909a7b1015a9417b882676d349bab5c80481f;
selection verifast_maybeuninit_new_pointer/forget_cfg_trace, input30/effective5min,
60s artifact reserve/10s kill grace. Remote exact SHA confirmed; no other active
run. Plain S6v4 then traced console sequentially; no CFG repair applied. Trace
patchSHA23d77777faea6f932ca93dd0a6ee48b48ca667fa641b0a4fffeaf374447a1b7e.

S7c diagnostic37681688627 COMPLETE:132jobseconds,4884/5400 used,516remain.
Plain+traced bothVF1 solely dead-code; all7bodies/return/leak; other5stages0.
Residual physicalid52=label2 ReturnStmt(unwinding), REGISTER1/EXEC0/RESIDUAL1;
normal returnid53 executes. Exact same sourcepair/completeMIR/AST. Causal repair
now permitted; no CFG candidate had been applied during diagnosis.
Compactartifact11510235246/full11509725710; tracebinary927e0892d4176dde4c9f706c57169eee0d0677609d13de8e6f6c270779a1ef62.

S7c acceptance dispatched37683136287/source7185d8bae4a25fa2be278424fa9f5c6a80b93956,
selection verifast_maybeuninit_new_pointer/forget_cfg_accept, input30/cap6min,
60s evidence reserve/10s kill grace. Remote fullSHA confirmed, diagnostic complete,
no duplicate active direction. Old plainS6v4 then new plain overlay89b0d80b build;
all source/effective-diff/binary identities saved separately. No tracepatch applied.

S7c acceptance37683136287 COMPLETE/FAILURE,283jobseconds,5167/5400used/233remain.
Exact autonomous body fullVF0/export+decode/refine0/body+return+leak/dead-code0;
old plainVF1 reproduced, sourcepair and completeMIR same. New binarye8090971,
translator89b76a1a, unchangedspec70f09d29. False normalpost9:27–32 and falsepre
4deadcode intended. Constructor/asptr/intrinsics complete; pointerdrop proofcases
2+11pass, admission8source+9MIRpass, timeout at mir_cfg_unwind, tailNOTRUN.
Unwind controls incorrectly presented combined ghosts: parser ens4:1–4, never
intended negatives. Scalar shared MIR Continue, no common cleanup. ProfileUNACCEPTED.
New focused continuation hypotheses/expected obligations and 3min/45s reserve are
recorded in design before dispatch; patch unchanged, no repeated fullmatrix.

Focused run37684590509/source6b63670c21bfa57d2531c4be57ac098df6111c5f resolved
at20:46:33UTC, selection forget_cfg_accept focused, input30/cap3min,
45s evidence reserve/10s kill. Remote exactSHA confirmed; no other active run.
Remaining233 entry; same overlay89b0d80b, separate-clause control syntax and generic
common-cleanup hypothesis only; profile cannot be accepted while drop tail incomplete.

S7c focused37684590509 COMPLETE:131jobseconds20:46:37–20:48:48UTC;
total5298/5400used102remain. Autonomous fullVF0 unchangedsource/MIR, ordinary
unwind and generic sharedcleanup3 positive complete; sharedcleanup retained and
normal+unwind returns executed/leak checked. False normalpost and falsepre intended.
False unwind strict classifier INTENDED_NEGATIVE acceptedtrue at23:15–20,
caller unwind return26:14–38 executed. Aggregate INCONCLUSIVE because it wrongly
required later normal branch/return/leak after false unwind stopped proof.
This is an aggregation error, not a verifier failure/weakening; preserve rawsummary.
Compact11510757595/full11510870158. Pointerdrop five-case tail still NOTVERIFIED.

### S7c immutable classification replay BEFORE dispatch

Only saved focused run37684590509/source6b63670c21bfa57d2531c4be57ac098df6111c5f,
compactartifact11510757595. Hypothesis: intended false unwind failure prevents
normal path from executing; positive-only normal-return requirement is inapplicable
to this negative. No new compiler/exporter/verifier invocation or toolprofile.
Require pinned run/artifact, all manifest hashes/sizes, exact source per stage,
export/decode/refine0 and fullVF1, exact eight executed functions, sole false
condition at23:15–20, actual caller unwind ReturnStmt executed26:14–38.
Predeclared replay controls: correct obligation accepts; wrongline, wrongpredicate,
setupfailure, exit0 and unknownfunction reject. Keep original summaries byte-identical,
write separate classification map only. Positive acceptance/real table checks remain.
Cap1minute including upload fits102remaining; no concurrent direction. No replay
can complete missing pointerdrop gates or accept profile/actual linkage.
Migration supplement: source comparison/plan only, no migration CI/profile switch.

Immutable CFG replay37685560355/processor7eea51399d570b0eba895605c5d05d0de9cf3ed1
resolved20:54:31UTC; sole relevant job20:54:35–20:54:43=8seconds. Success,
new separate INTENDED_PROOF_REJECTION; six controls PASS. Original focused
summary313675ae and falseunwind11384c7d byte-identical; raw artifact pin verified.
No compiler/exporter/verifier invocation. Artifact11511500191/zipSHAfd6c568c.
Final budget5306/5400used94remain, noreset/noactive, iteration STOP. Unverified
pointerdrop mir_cfg_unwind(partial), mir_extra_operation, mir_contract,
method_source_pin, glue_source_pin. New profile UNACCEPTED despite autonomousVF0.
Compact manifests894/4605/1042 SHA/size/ZIPCRC verified, whole logs read.
Actual linkage/redirect NOTRUN, oldS6v4 proofs preserved, MD semantics TRUSTED.
Documentation-only closeout is not a proof run.26.10 supplement sourceanalysis
and migrationplan only, no merge/rebase/newprofile/migrationCI.

2026-10-08 documentation/source-only migration assessment: compared repository
dd2bbad51eb50fdf9730e14802dcaf8a9290092a ->cd371e035c7e573760c43bf934d53e8118ee3e7d
and VF809de4596839b739dd999f9e462242c835e3af46 ->f76012fb518703b1d98e243ac4f487f16877cfcb.
PR714 is model-checking/verify-rust-std toolsetup update, mergea4e1cd0c21238ecadfce813c29174e42d5b5797d.
Active S6v4 and S7c exactrules notcovered statically; archive projection-name
canonicalization covered, other archived patches separately classified, notactive.
Compiler/std/sourcecert and exporter/schema/refiner/spec deltas and staged repro
plan recorded in VERIFAST-26.10-MIGRATION.md. No build/verification/CI/rebase/merge/
profile switch; budget remains5306used94remaining, old proofSHA notrelabelled.

## 2026-10-08 upstream sync — Git/documentation only, CI0

Separate sync branch directly merges pinned upstreamcd371e035c7e573760c43bf934d53e8118ee3e7d
over its own original parent. No conflicts, rebase, force-push, inter-agent merge
or our-main merge into agent branch. Old proof/profile/patch/control bytes retained;
root std/nightly/standard-VF setup now upstream, research runners still old pins.
No builds/verifier/tests/workflow_dispatch; budgets5306/5400(94) and512/1800(1288)
unchanged. S7c UNACCEPTED5admissiontail; G2/A/B9projections retain oldboundaries,
new sources/tools NOTREVALIDATED. UPSTREAM-SYNC records exactparents/mergetrees,
sourcecaller ledgercorrection and preparedfuturetasks. All newcommits[skip ci].


## 2026-10-08 — STOCK-26.10-BASELINE BEFORE

Owner explicitly authorizes stock26.10 baseline and migration plan after sync;
new separate1800 hosted jobseconds, old5306/5400(94) untouched/S7c UNACCEPTED.
Full hypothesis, domains, normal/unwind posts, stock pins/source hashes, eleven
isolated controls, exact diagnostic expectations and decisions are in
[BEFORE card](STOCK-26.10-BASELINE.md). Effective patches NONE; source pin f76012fb,
nightly2026-09-25/std cd371e03. First manual dispatch ceiling600s including artifacts;
no executable work on server. Proof SHA/run appended after dispatch; no run yet.

### STOCK26.10 run1 / run2 BEFORE

37693718508/source4baed189:37s setup only; release-generated Rocq .aux failed
overstrict source audit. Artifact11515150111/digest13caace621e93e8b601c3b4282f4c2246af65f57b4da9ec3fe48f598dd1b7154.
No fixture executed. Correct package-vs-effective-spec audit only; full *.rsspec
bytes/inventory remain required exact, all package files remain hashed.
[Detailed outcome/new hypothesis](STOCK-26.10-BASELINE.md). New run cap600s,
37used/1763remaining of separate1800; prior account unchanged.

### STOCK26.10 run2 and phase closeout

[37694000195](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37694000195),
proofa0cfd30e066acbaf1b5406cd9773f54388cc45be, job113040941877,
22:06:34–22:07:36UTC=62s. Stock/unpatched sourcef76012fb, nightly2026-09-25.
11NORMAL+11readonly exports,22decodes,11refinement,66stage source checks PASS.
4fullVF0 positives: u32/raw/ordinary unwind/shared cleanup;4intended false normal/
unwind negatives at6:27–32,6:40–45,9:27–32,23:15–20;2separate contradictory-pre
dead-code controls (original strict INCONCLUSIVE retained). Exact forgetVF1 after
body/normal return/leak: sole3:1–16:2 dead code, no proof error. New complete MIR
normal==readonly f6aa0ef4, AST172fbc51 establishes orphan label2 unwind ReturnStmt
structurally; physical-key attribution UNKNOWN, not old52. Reachable ordinary and
sharedcleanup3 unwind+normal returns/leaks execute; falseunwind rejects intended post.
Full binaries/spec/schema/std-export audit and migration map in
[phase report](STOCK-26.10-BASELINE.md); relevant repo/sysroot forget/drop bodies
unchanged, MD/MaybeUninit/SmallSort whole files equal. Refiner unwind TODOs retained.
Artifact11515215378 ZIP18f1796c2be90f483402db00d2aacb868e8229a8ca2d490e8248bdc2c38be91f,
325entries CRC PASS. No patch/code/model migration. Separate budget99/1800used,
1701remaining; old5306/5400(94) untouched/S7cUNACCEPTED. CLOSED at stock blocker,
plan ready, no active run. Next requires separate narrow diagnostic/trust decision.
Final docs HEAD is not proof SHA.


## OVERNIGHT-SELECT-SORT4-26.10 — entry / O1 BEFORE

Owner authorization: broad autonomous phase through2026-10-08 06:30UTC, new21600
hosted jobseconds; historical budgets unchanged. Entry80d9c0c3, own branch
research/overnight-select-sort4-26.10. See [full phase/card](OVERNIGHT-SELECT-SORT4-26.10.md)
and [verbatim prior checkpoint](overnight/STATUS-ENTRY-HISTORICAL.md). O1 will test
independent stock+MD::new CFG causality and complete normal/unwind/negative controls;
no physical-loc number requirement, no S6 import in this profile. No active run/0used.

O1 COMPLETE: run37698481357/e6c02f22,104summedjobseconds. Independent stock+CFG
profile accepted:5positive/4intendedfalseposts/2deadcodecontrols, complete source/MIR
pair equality, ordinary/shared unwind+leak retained. [Full result and O2 BEFORE](OVERNIGHT-SELECT-SORT4-26.10.md).
Old S7c untouched/unaccepted. O2 source-reviewed5family S6 diagnostic authorized next;
no new acceptance before complete new MIR/content review and negative matrices.

O2 SETUP_BUILD_FAILURE run37699058032/b8cc3cfa,89s; S6 fixtures NOT_RUN;
old Body.predicates/D.decode_predicate API needs exact clause migration. Full logs
and artifact11516448008 retained outside Git. [O2b BEFORE](OVERNIGHT-SELECT-SORT4-26.10.md).
New account193/21600, no active run; CFG acceptance unchanged.

O2b DIAGNOSTIC_ONLY run37699461058/1d57dee9,133s: strict Clause port builds,
five complete new MIR export/refinement pairs; four fullVF0 positives, asptr
fails exact parameter-local count. [Full result/O3 BEFORE](OVERNIGHT-SELECT-SORT4-26.10.md).
No S6 acceptance/actual helper gain yet. New budget326/21600; no active run.

## O3 result / O4 BEFORE — unchanged semantic profile, corrected diagnostics

O3 proof1378f0ffc8342233349fae3df5a938c4a021c8d7,
[run37700450091](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37700450091),
job11306237081023:07:52–23:16:21UTC=509s including artifacts. All8 S6 matrix
stages exit0 and report ACCEPTED; complete artifact audit remains pending.
All5 new graph diagnostics fullVF0/export/decode/refinement0. Helper fixture
creation NOT_RUN: dynamically imported dataclass module absent from sys.modules.
Callback positive normal-export1 (evidence under review); negative fixture generator
erroneously retained previous positive body, so exact single-call certificate rejects.
No helper/callback intended proof negative. Full logs/artifact11517239239 retained,
zip digestbb5d42b13ca5a4a2c46bcbea98c9673a8081193f1e7d147965b939a26c9e31c8.
Account835/21600,20765remain. Large artifact accidentally dereferences disposable
mutation-profile/bin symlinks; next upload excludes only those copied binaries,
retaining separate wrappers, manifests, full MIR, mutation records and proof logs.

O4 falsifiable hypothesis: registered Python module imports and isolated callback
case extraction restore diagnostic setup without changing any source/MIR/proof
acceptance predicate or VeriFast profile. Run hosted helper certificate tests first.
Investigate positive callback exporter error before retrying its route. G1/A1/actual
helper and callback retain O3 domains and full normal/unwind posts. No S6 matrix
repeat while translator/spec/compiler/profile bytes remain identical; all5 positive
smoke/export/refinement stages plus stock baseline remain for setup integrity.
Any newly exposed unsupported primitive or proof-resource error is INCONCLUSIVE,
not falsepost acceptance. Trust boundary unchanged. Main static review and agent
review confirm import lifecycle/case isolation defects, no trusted semantic change.

## O4 result / O5 BEFORE — proof entry visibility and diagnostic isolation

O4 [run37702049156](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37702049156),
proof86e84ace59d0f65b5690e56e62818875ed7c0578, job113067557446
23:24:06–23:26:09UTC=123s. Semantic console36a769ab/spec3c035910 identical to
O3; all5 S6 diagnostics fullVF0/all support0. Hosted5 helper certificate tests pass.
G1 two positive bodies reach return/leak but entire unused private entry gets deadcode;
10 intended resource/post negatives confirmed, no_thread/contradictory-pre initial
classification INCONCLUSIVE retained. A1 method/transmute and actual helper now have
complete NORMAL/readonly MIR and refinement0. A1 first missing assert_inhabited;
transmute first typed MU-to-pointer mismatch; helper first missing MU constructor.
Neither actual helper nor A1 is proved. Callback all support0, fullVF2 before any
proof header: optional AST serializer MergeFractionsStmt TODO. Negative fixture
normal-post certificate rejects multiline post; no intended negative established.
Account958/21600,20642remain. Full original outcomes/logs retained unchanged.

O5 hypothesis: public G1 proof entry retains same body/posts and removes whole-entry
unused deadcode; explicit mandatory deadcode/precondition classification repairs
observation, not verification. Callback mandatory full proof without optional AST
serializer reaches its first real obligation; diagnostic AST remains a separately
reported opt-in stage. Unique exact normal-ens source span locates multiline falsepost.
Same unrestricted domains/full O3 posts/semantic profile; any new first proof blocker
is diagnostic, not intended negative. A1/linkage semantic components remain separate
next work after O4 graph review. No unchanged retry: entry visibility/dump separation
and exact classifier defects have causal log evidence. Include fixed-binary cache:
only host-built console plus applied-diff+binary digest manifest; exact patch inventory
key, no fallback restore; all source/spec/compiler/exporter/refiner pins re-audited.
Cache does not change profile. New job cap1200s, available20642 including cache/artifacts.

## O5 result / O6 BEFORE — actual constructor linkage

O5 [run37702922138](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37702922138),
proof7a176e9fafc993d59906a8d9015940f581f429f6, job113070401883
23:33:17–23:35:21UTC=124s. Workflow SUCCESS is diagnostic only. Profile unchanged.
G1 publicentry hypothesis disproved: same whole-function deadcode after return/leak.
Synthetic unwind=continue at checked_forget_generic call with false unwind remains
candidate causal explanation; no suppression or call-link acceptance. 11 intended
negatives; contradictory-pre classifier still INCONCLUSIVE on original output.
Callback allsupport0; both now execute proof to stdspec47 FnMut Args.own failure
for tuple2 reference values. Falsepost not reached. This supports exacttuple2
ownership next component, not HRTB/unwind acceptance. Cache built/saved exact console
36a769ab with applied-diff manifest. Account1082/21600,20518remain. No active run.

O6 obligation is the actual helper's two MU constructor calls, current first error.
[Linkage review](overnight-linkage/REVIEW.md) documents same-source checked local
constructor module, certified representation and exact existing S6 redirection.
No translator/spec/compiler/exporter change. Same unrestricted raw-pointer helper
normal selected-pointer post and false unwind; later operations intentionally remain
unmodeled, so this is partial diagnostic, not helper theorem. Falsifiable: prepend
O3-approved exact constructor module to unchanged actualbody; pinned env +fullsource/
typedMIR gate enables exactly2redirects, checked localbody executesreturn/leak before
actualbody reaches asptr missingoperation. Two compile-valid localbody/union mutants
reject exactsourcecertificate beforeproof. Different later error remains diagnostic.
Same profilebyte audits and5positive source/MIR/refinement smokes retained. Previous
G1/callback route is not rerun without new evidence; their next components develop
inparallel. Exactcache only; no compilerbuildtools requiredonhit, versions marked
cached ratherthan invoking missingtools. Next decision from causal gate logs.

## O6 result / O7 BEFORE — first new semantic profile checkpoint

O6 [run37703486878](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37703486878),
proof40c66d4e5ab845869348fd1dff74281e9d3fda82, job113072244744
23:39:23–23:40:18UTC=55s with verified exact console cache. Positive proves local
constructor and links both actual calls; first next unsupported operation is asptr.
wrong_active_field intended source rejection. extra_union_field originally
INCONCLUSIVE: exact earlier typed-ADT gate rejects `certified union fields or types
differ`, not the later source-text reason expected by classifier. Original result
preserved; classifier exactreason corrected, fresh run scheduled. Account1137/21600,
20463remain. Main completed remaining O3 intrinsic/drop full-log audit: 91logs,
6+2positives with body/return/leak, 21exact sole proof negatives, 62exact preproof
admission rejections, no unexpected errors/fatal. With agent constructor/asptr and
baseline audits, four separate S6 components at O3 accepted for explicit contracts.

O7 profile: stock26.10 + accepted CFG593d0940 + S6 candidate20f7d07a + separate
A1 raw-pointer inhabited, A1 initialized-pointer transmute, exact tuple2 own overlays.
Only translator, rust_parser and std/lib.rsspec change; kernel/memoryalias/schema/
exporter/decoder/refiner remain frozen. New components experimental pending full
positive/negative gates; S6 regression success cannot accept them or whole profile.
Written component reviews precede code: helper/A1-FRONTEND-REVIEW,
helper/A1-PRIMITIVE-MATRIX, callback/TUPLE2-TRANSFER-BEFORE, linkage/REVIEW.

Main self-review found and resolved before dispatch: Regular RSSPEC functions return
fn_outcome, so typed transmute primitive uses existing checked outcome projection
and falseunwind post; VF rawpointer type erases mutability, so each TrBody gets its
own decoded localtype map and admits only plain Move of exact MU<*const sameParam>
into constrawpointer. No newwire/globalstate/typecoercion. Remaining unapproved const
pointer transmute shapes fail explicitly, after stock BoxAsNonNull path; this is an
unsupported admission, never a proof negative. Physical union/transparent layout to
abstract initialized inner correspondence is TRUSTED, does not grant Element cells.
Tupleown requires exact2publicReal instancefields T1/0,T2/1 and no extras; otherwise
stockopaque. Only structuralfieldownership, stockshare/FnMut contracts retained.
All5patches compose statically with gitapply/diffcheck; no local execution/build.

Falsifiable tests: compile cumulative console on hosted; independent constructor
and asptr actual-link captures (unchanged runtimehelper/full target posts); hosted
helper certificates, exact A1 localbody with fullvalue/thread/own/noUnwind, 2positive
and10proofnegative+5wrongtype controls with provisionalclassification/fullMIR;
G1 exact directbody value/frame lane distinct from still-unaccepted nounwind calllane.
Tuple close/open/share/nonCopyrefs +resource/scope negatives; unchanged callback should
advance Args.own, expose HRTB or genuine resource/unwind obstacle, never declare its
falsepostnegative before intended location. Full S6 fourcomponent matrix including
ordinary/sharedcleanup regressions on extendedprofile. Onejob1200cap/1080inner,
allsetup/build/artifactseconds counted. A failure localizes onecomponent; progress on
independent captures continues. Source/libcallees still require proof before actual
summary linkage; helper/sort4 generic/ZST and guardprotocol NOT_PROVEN.

### OVERNIGHT O7 — 2026-10-07 23:56–23:59 UTC

Proof `5463571c7e8924f77b73b665e6291bd62488f9ac`, [run37705052264](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37705052264), job113077309170, 190s (phase total1327/21600). Fivepatch console `caf140b61619aec1b4d4eb38d7dc24eb2ff6b2181f1d5959688a642b41eb1465`; kernel/schema/exporter/refiner stock. Full S6 eightstage regressions PASS, constructor3 and asptr2 source/linkage cases as intended, nextactualcall intrinsic. Source-exact transmute localbody VF0; A1 initialized/frame controls under full audit, method fails missing external transmute_neo. G1 directbody frames VF0 with13named negatives; generic SAFE/callable forget not accepted. Tuple setup rejects untracked pinnedrelease VERSION/sharedlibrary before any fixture; failure remains recorded, precision repair validates both against pinned archive/extraction. Workflow failure is setup provenance gate, not tuple negative or helper proof.

### OVERNIGHT O8 — 2026-10-08 00:08–00:11 UTC

Proof `95e871c6de3b7a74e2b6df97b398095e914e60bd`, [run37706123317](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37706123317), job113080788158,187s; phase1514/21600. Same fivepatch profile/console caf140b6 asO7, fullS6 eightstage PASS. Constructor/asptr remain linked diagnostic. All3newintrinsic/drop cases INCONCLUSIVE at exact SAFE source-signature annotation gate (same req/ens/unwind with differing ghost formatting), no proof. Tuple releasefile gate passes then fails difftext-vs-patch comparison before any fixture; exact composed parser replay replaces it. These are admission repairs only, source/post/kernel unchanged. Completeoriginal logs/classification retained. NewA1capture and actualsort4 source/graph diagnostics prepared forO9.

### OVERNIGHT O9 — 2026-10-08 00:18–00:20 UTC

Proof `0781cdbdf3de0ec3969ed0e0f440026791a2aeaf`, [run37707055478](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37707055478), job113083812093,150s; phase1664/21600. Same exact5patch profile, O8 S6 reuse hashgate PASS, builtconsole cached independently of diagnostic failure. Three tuple ownership positives fullPASS; share lacks field-share/type metadata, then falsepost-span parser abort (original preserved). Actual intrinsic fixture ghost-stripped gap whitespace abort, actualsort4 anchor backticks mismatch abort, no actualproof. A1 combinedcallee/caller fullsource+typedMIR captured, callee fullproof then sole caller missingstdtransmuteNeo. Stockcopy initialized AND optional-none dst pass53stmts/fullbody/return/leak, allsupport0: initial missing-scratch-model hypothesis falsified. Original uninit classificationINCONCLUSIVE (classifier allowed onlyinitialized), full0errorlog retained. Falsepost and ownercreation at targetpost line6 asintended afterfulloperation. No ownerfrombits, ZST notcovered. O10 has precise gate/resource repairs plus arbitraryowner-frame+duplication controls, same semanticprofile.

### OVERNIGHT O10 — 2026-10-08 00:26–00:28 UTC

Proof `6bf58027ec193859e191ab519bdd28c6fbf66589`, [run37707814634](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37707814634), job113086298353,72s; phase1736/21600. Exactconsolecache HIT andO8regressionreuse hashgate pass. Actualintrinsic2+1 andpointerdrop call/linkage certified, localsproved; targetfirstreal missinginitializedpointercell pre at checkedpointerdrop contractline50. Drop-source mutant intendedpreproofreject. Fullactualsort4 source/signature/body andbothfullgraphs captured, exports/decode/refinement0, deliberatecapturepre firstpointerboundsfailure. M1 threefullVF0rawrepresentation positives incl arbitraryoneownerframe, threexactpostnegatives rejectfalse/ownercreation/ownerduplication; noTownershipduplicated, noCopy/Freeze, explicitnonZSTpartialdomain. Tuple3ownpositive, false/dup intendedneg; resource-loss andnonmatchingclassifiersneedobservedlocationrepair; fieldshareboundaryunchangedopen, callbackArgsownlackrealclose, notHRTByet. Completefailedandpositivelogs retained.

### O11 — sixth-component profile and H2 captures (2026-10-08)

Proof SHA `480cb9f10fa8bf11cb70b7f9925e19eaadf6c92a`, [run37709227889](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37709227889), job113090925634 00:43:19–00:45:54UTC,155s; cumulative1891/21600. Consolec6a80333, translatora99ef5cd, parser7bf12f12, specd33b2a7a; exporter/schema/refiner unchanged. All8S6 matrix stages PASS; combined profile remains experimental. A1link all15method cases reject exact MIRplace `_2` beforeproof, sourcecontrols inconclusive. H2a localgenericmethod/frame return/leak full0, missingowner atcallee pre line6 and false normal/unwind targetposts fail; actualgenericmethodlink notyetadmitted. H2b ownerfixtures parseerror34 beforeproof, ordinaryDrop full0. Callbackaliasaudit harness NameError beforefullverification; originalerror retained, ghostArgs correction untested. Tuple3ownpositive/3intendedresourcepostnegative/arityopaque controls pass; shareboundary remains open including newroundtrip. Fullactualsort4 graph andM1 threepositives/threeintendednegatives reproduced. Noactualhelper/sort4 proof. Nextnarrow setuprepairs +fresh fiveghostprojection; no rerun oldcode.

### O12 — actual projection prefix and isolated A1 body (2026-10-08)

Proof SHA `165659d0b350fc9622bf43d899ccbc6d98e778c4`, [run37710354025](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37710354025), job113094595744 00:56:27–01:00:26UTC,239s; cumulative2130/21600. Six-component consolef6cecf6916abe3dbcad130a5b04ee50826e57bf164eb97f11e6b88bfd7d755bb, translator9eb7ae14; exporter/schema/refiner/spec/parser pins retained. FullS6 eightstagePASS. Actualprojection completeMIR andallfiveghosts admitted, initializedslot drop+bothwrappercloses pass then genuine stockforget nominalguardown requirement fails atstd420; finalhelper posts/unwind/leak NOTreached. A1baseline source-exact transmute callee+assume_init adapter wholeunitVF0, allNORMAL/readonly/refinement0/sourceintact/returnleak/no deadcode; 3source negatives exactreject. All15probe fullgraphs matchreviewedmanifest; two positiveprobes leakrawptr_own becausepostomittedreturnedvalueowner, frame/threadloss contaminated. Repair explicitprobe ownershippost, no targetmethod orfrontendpostchange; originalclassifications preserved. H2bgenericguardconstructor return/leak pass; scalarwitness lacks stocku32own atcallee pre, missingcell/wrongtarget intended nominalclose failures, ordinaryDropfull0. Callbacktupleghostsyntax parseerror beforebody; sort4memorypre ghoststrip extra newline abort beforeMIR. Bothminimalsetuprepairs retainedforO13. ExistingG1framedpositives inlineexactbody and DONOTqualify a callablecallee; newisolatedG1c candidate separates that obligation. Combinedprofile remains experimental, fullhelper/sort4 notproved.

### O13 — local A1 matrix and genuine unwind/reference blockers

Proof d3363d2e6525b2c27cdfc3e83006db94a04921da, [run37711416854](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37711416854), job113097971830 01:08:39–01:09:51UTC,72s; cumulative2202/21600. Exact O12 sixpatch profile/cache f6cecf69 and sevenhash S6 reuse gate pass. A1 local wholeunit3positive/12intendedproofnegative/3source rejects independently audited; no outer actual call summary yet. Callback source/MIR/refinement0 and FnMut call passes; normal recovery passes, full unwind post first misses current left points_to at line65. HRTB patch unwarranted. Actualsort4 ghost identity/MIR/refinement0, checked interior_pointer_limits discharges first add bounds; next reference precreated token missing at aliasing88. M1 unchanged3pos3neg. G1 isolatedcallee mostly preparation failure due eager other-variant marker lookup (one intended thread duplication reaches post); original inconclusive preserved. H2 concrete witness close <u32>.own parse restriction before body; direct stock u32_own repair pending. Combined profile experimental; full helper/sort4 open.

### O14 — H2a hosted build rejection

Proof 3b949e4ceb254736bff89f81a4e31fad7931814f, [run37713105162](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37713105162), job113103339079 01:28:35–01:30:30UTC,115s; cumulative2317/21600. Console build fails translator9481: decoded D.Ref inner D.ty passed to reader-expecting guard_ty. Stock baseline/source capture complete; no new callee/linkage/S6 proof ran. Minimal API repair needs new SHA/run. Separately dormant H2b AST review found DummyVarPat would produce initialized cell; must use DummyPat (stock textual optional `*slot |-> _`) before any activation. This semantic correction is not a green result; H2b stays unaccepted/inactive.

### O14b — callee qualification and earlier nominal resource blocker

Proof 021f8beb0374b8b432587587bd95b6768875b60b, [run37713536492](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37713536492), job113104712709 01:33:44–01:37:03UTC,199s; cumulative2516/21600. Sevenpatch console06c194f09b3fb27a2fd9a787b447e681349957c23c24c61666a5af06f8e77c05, translator1c9620aa; spec/parser/exporter/refiner/schema unchanged. FullS6 eightstagePASS. G1c exactstdforget-body unsafegeneric localcallee fullVF0, return/leak/nodc, sourceidentity/NORMAL/readonly/refinement0; falsepost/threadloss/dup andcontradictorypre exactly intended. Contract currentthread→currentthread,falseunwind, noTown/Copy; trusted MD identity/destructor suppression, SAFE const std redirect notproved. Minimal H2localmethod requalified1pos+3owner/normal/unwindneg. Linkedguard allgates admit, localcallee proof complete then missing FBC atverified51; intended optionalstorage-leak hypothesis notyetwitnessed. Method/guardoperand source2neg exactfatalbeforeproof. Genericownerctor+stocku32witness bodyreturn/leak complete; sameFBCfailure inDrop; owner2negativepoints_to andordinaryDropfull0. Mainhypothesis: two ghostcommands samephysical line resolve firstopen twice under stockline-based matching; inspect beforefixing. H2b inactive. A1localmatrix/M1/callbackunwind/actualsort4 bounds boundaries reproduced; noactualhelper/sort4 proof.

### O15 — causal optional-storage leak, call dead-code, and source setup failures

Proof63e2cf46db4da00643603aec798260808830ae44, [run37714432761](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37714432761), job113107566886 01:44:41–01:47:19UTC,158s; phase2674/21600. Console5e83cc87, translator4c1c292c, otherpinsunchanged; fullS6 eightstagePASS. Two separate ghostlines eliminate duplicateFBCopen; truthfulGuardOwn opens andgenericcheckedmethod verifies, guardreachesnormalreturn/leak then exactremainingoptional `points_to_<T>(inner,dummy)` leak atverified54. This is now causalbasisfor separateH2b optionalpost, notguardacceptance. Source2mutants exactreject; generic4localcontrols fullasintended. Ownerconstructor/u32 witness pass, unlinkedownercapture latermissinggenericmethod; ordinaryDropfull0. G1framedgenericcall sameunitcalleeproved, full NORMAL/readonly canonicalcallergraph1f1f8e96/calleec493d14b andrefinement0, caller normalreturnleak pass thenmandatorydeadcode at17(body) fromsyntheticunwindfalse switch; newexactcall CFGcandidate justified, no globalcleanuppruning. Actualownerprojection fullgraphsglobalnominalpredicateexported, fullproof parseerror76 secondopen inonecomment, so nestednamespace stillunanswered. Sort4borrowprefix fullgraphs/refinement0 thenlet_lft parseerror95 beforecheckedresourceprotocol; nottargetnegative. Originalclassifications retained; source-onlyprecisefixes next. M1/A1/callback oldboundariesreproduced. Combinedprofileexperimental, actualselect/sort4NOTPROVEN.

### O16 — callback admissions and actual first comparator unwind obligation

Proofb149418ce76ea2e877bb2107dd09afced69f6df5, [run37715395739](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37715395739), job113110583923 01:56:31–01:59:37UTC,186s; phase2860/21600. Eightpatch consolebab314338e70ead89bdbf1c47a7adec07d2c2e083c8e127c4e2509c30bc09eb2, translatorb162c74e, otherpinsunchanged; fullS6 eightstagePASS. Markedcallback source/MIR/refinement+orderedtuplealias audits0; missing/duplicate/moved/foreignmarker4 exactfatalexit2 beforetargetproof, positive/falseNORMAL/falseUNWIND/duplicateF/duplicateleft5 cases firstghostfractionnonpure-context at93. ExtractedsourceAST operations lostouterPureStmt; preservingpurecontexts is precise nextrepair, goto mustremainnonpure. No callbackacceptance. Actualsort4 split_four_owned_cells checkedfulllemma, allstockborrow/share/precreate/init_ref/Args passes andfirstrealFnMut executes; directContinue returns then fullsourcearray unwindpost failsat73. Newprefixnowqualifiesactualfirstcall, nofullsorttheorem. Actualowner syntax namespaceparses/exportfullgraphs/refinement0, mandatorySAFEprototypecompat at7 leaks addedraw_ptr_own resultpost beforebody. Pointermodelpredicate istrue, needcheckedpost-equivalence/completiontheorem ratherthan assumedownershipbridge or silentlydroppingtarget. G1framedcallsyntheticunwinddeadcode remainsrecorded; gatedCFG draftunactivated. H2aoptionalstorageleak reproduced, H2b unactivated. Semanticcomponentsremainexperimental.

### O17 — recovered after interrupted session; full local guard and callback unwind

Proof `11d888ba8ff2231a80c759148194aa9ae6b9d30e`, [run37717092130](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37717092130), job11311595059302:16:55–02:20:49UTC=234summed hosted seconds; cumulative3094/21600. SUCCESS denotes diagnostic collection, not target acceptance. Nine-patch console0495b7e5f49048707e3256ad2c7d6b0a532178ec8cc4380898a034281fc3d514, translator2472f5ecfb65ba01ffb934f6cf9ef94f77380ca396b444413ad5c92181319535; parser7bf12f12/specd33b2a7a/exporterb00c75f4/refinerb049c8d1/schemaf48fcf29 unchanged. Added H2b c9afb4bfd696efc38f2bc71e10463a34170d9d769e851a07388c01278e99b2ff and callback pure-context repair61d7525cc8ff3e6e9c736ea00178c002f071b521c78845bf68d0e4890e2be07a. Full S6 eight-stage matrix passes freshly.

Local H2b unit full VF0/71statements: checked generic pointer method and source-shaped SAFE Drop each execute two normal/unwind return/leak paths; truthful constructor, concreteu32 witness and ordinary Drop in same unit complete. All original/verified hashes, paired NORMAL/readonly exports/decode and refinement pass. Owner is initialized target cell+one T.own; generic destruction returns optional cell only, without value/T.own. Four source controls method_operand/guard_operand/owner_predicate/field_visibility reject exact source certificate VF2 before method proof. Missingcell/wrongtarget fail constructor ownerclose points_to at28; duplicatecellpost fails extra slotcell at37 after constructor return. H2b LOCAL_CANDIDATE_PROVED, NOT COMPONENT_ACCEPTED: full source/ADT/typed-MIR/template-post mutation/admissibility matrix still open, actual nested DefPath/linkage NOT_PROVEN. Genericcallee positive fullnormal/unwind; owner/false normal/false unwind/retainedowner controls hit intended boundaries. Retains_initialized remains original INCONCLUSIVE: optional-vs-initialized dummy/some entailment fails prelude_core213 from callerpost25, distinct from classifier's expected missingchunk. A future repair/replay must preserve original class.

Callback four marker controls reject exact admission VF2 with paired support+orderedalias audits0. Falseunwind fails addedfalse at67, duplicateF at67 andduplicateleftT at65 fail secondowner after actual unwind debtclose→checkedrecover→scopeexit→fullpost. Positive/falseNORMAL finish unwind post and leak checks, then fail NORMAL call assignment96 on FnOnce::Output vs bool. No full callback acceptance. Paired MIR retains HRTB FnMut and FnOnce::Output=bool projection; translator currently drops projection clauses with nonempty bound_regions. Any correction needs per-call sound instantiation and independent HRTB/resource/admission controls.

Checked pointer-value completion lemma positive full VF0; four negatives at lemma post11 reject false, Elementpointee rights, duplicate thread andwrong selectedpointer. This creates only definitionally-empty raw_ptr_own; no actualhelper theorem. Actual nominal-owner completion candidate now passes SAFEprototype and enters helper, stops at25 missing MaybeUninit::<T>::new because stock S6 runner env/admission only admits frozen five-ghost inventory. New truthful protocol has separate ghost inventory and needs explicit exactsource/fullMIR qualification, not another primitive axiom. Source-only stock safety_proof and G1exactcallCFG drafts preserved, untested. Actualsort4 first comparator unwind-array obligation unchanged; no fullhelper/sort4 proof.

Recovery2026-10-08 after usage-limit interruption: local/remote HEAD still11d888ba, no newer run or active workflow. Prior09:30MSK CI authorization expired. Owner authorized continued analysis/preparation/static checks and requires extension before any new hosted run. New pending components must not be activated as checkpointing; historical S6/S7c and budgets unchanged.

### Resumed authorization — 2026-10-08

Owner selected continuation until14:30MSK/11:30UTC8Oct with new separate7200summed
GitHub-hosted jobseconds. Oldovernight3094/21600/18506unspent is historical, not reused.
Full scope/preconditions/check integrity in RESUMED-SELECT-SORT4-26.10-08.md; no
phase-stopping between approved priorities. At most one rootworkflow. O18 will
advance H2b admission and exact linkedowner capture, with G1 independent CFG and
freshfullS6; HRTBoutput/strictlifetime separate inactive components.

### O18 — local nominal admission and two precise setup/certificate failures

Proofbb9c46bc423a43cccf0e93a0ad7651c3faee6f1b, [run37745138207](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37745138207), job11320472474707:42:54–07:46:08UTC=194s,newaccount194/7200(7006remain), old3094/21600history unchanged.11patchconsolea6cb3156bd62f1b84d5aca1d5dc1a4dec2e86fc6d6e3d3ebf0f5dbf75755837c, translator4284859a36f2d23aaaebfa810e948f98795a80d3a1c78cf0a0c3cb74ce4105ae; stockexporter/refiner/schema/parser/spec unchanged. FullfreshS6eightstagePASS. WorkflowFAIL solelyactual-owner-linked stage1; no timeout/buildfailure.

H2source matrix8: positivefullVF0 bothgenericmethod+SAFEguard normal/unwind return/leak, constructor/u32witness/ordinaryDrop full0;7sourcecontrols exactFatalVF2 beforemethodproof withpairedsupport/refinement0. reprpacked/C/align+fieldalias atnewH2c preADTboundary;extrafield/ghost/guardcast exactsourceownerbody. MIRmatrix independentunwrappedpositivefull0+12directMIRmutants exactintendedFatal2 beforeproof, allmutant_exact/sourceunchanged/independentNORMAL/readonly/refinementtrue:receiver/callee/calleeT/Move/local/projection/destination/normaledge/unwindedge/cleanup/extraop/ghostinventory. Originalfullsource andcanonical/mutateddecoded/binary/hash records retained, TESTmutationwrapper only, productionexporter unchanged. Generic6 controls allintended; retainedinitialized callerpost25 auto-closeprelude213 dummy/some entailsfailure reclassifiedONLYfreshO18, originalO17INCONCLUSIVE preserved. LocalH2b strengthenedcandidate; templateASTpost adversarial andactualnestedlink remainopen.

G1all9cases source/MIR/refinement passes butcommonfrontendcertificate rejects `callee/caller signature source span` BEFOREproof: exportedrawcol0 translatesASTcol1; draftexpected0. Twooriginalwrongcallee/weakunwind labels claimedintended becauseclassifier matchedanycertificateprefix. Independentfullaudit revisesALL9toINCONCLUSIVE for intendedcontrol, preserves originalJSON/logs; exactreasonmatching repair required. Commonsetup/spanrefusal mustnever countasnegative. Genuinecallee isolatedG1c proof persists separately.

Actual-owner-linked sourcepreparation stops `actual contract/safety proof insertion anchor changed`: S6 actualcontract closesens andhasadjacent `@*//*@ on_unwind_ens false; @*/`, neitherreviewedstandaloneanchor. ExistingS6localbodies presentinlinkedbase; newownerfixture fullMIR/refinement/proof NOT_RUN. Repaironeexactactual-contract format withghoststripunchanged; no newprimitive/model. HRTB/lifetime inactive; callbacknormal Output/bool andactualsort4 unwindarray unchanged. NextO19 usesnewSHAafter causalspan/sourceanchorfixed, separately reviewed target-scopedHRTB, fullsource/controls; no unchangedretry.

## O19 — G1 call repair, callback normal/unwind and linked owner MIR (2026-10-08)

Proof `a6f9d5e00cc99c06f8c49fa2e27e6a92308a1a79`; [run37746579002](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37746579002), job113209380990,07:56:37–08:00:29UTC=232s. New account426/7200; remaining6774; no active workflow. Before/review in `overnight-linkage/O19-BEFORE.md`. Collector success is not component acceptance.

G1 repaired source-span col1: exact generic callee and framed caller fullVF0. False post, frame/thread loss/duplication and two exact source/unwind admissions intended. Wrong-value first error line22 `Cannot prove flag == !(flag)` is preservation post, original classifier INCONCLUSIVE; record retained and narrow correction pending.

Callback positive now fullVF0 with real FnMut, normal and unwind debt/recovery, resource posts and leak. False normal61/unwind67 and duplicate F67/T65 fail intended post, four marker controls exact admission rejection. HRTB per-call registration closes Output=bool mismatch. Isolated matcher controls12/15 expected; missing_projection actually exports compiler projection; shadowF/T parse before translator. No full HRTB admission yet and no actual sort4 theorem.

Linked owner source paired MIR/refinement passes, outer normal full MIR hash `0bb582fcf2baf193c8a25267b74b34572c6b1bb6c701d920bba78634cad483be`, nested normal `5f31dc01e01a659b80fa90326d3dd2fc3f13f7db74ddb77a587416c29b73e8f3`. Readonly outer `7ff18621be59b543166b68ea05773b10a805ab1ef524dae27b4f61e306ca2b9d`, nested `6770a073b7315aa5ae0e708687ca3139cb40d040cc200e47ee8b6017490bb400`. Frozen S6 refuses changed SAFE contract/source signature before proof. Nested ghost opens are actual exported ghost-command call terminators; capture boolean must distinguish from ghostStmts. New certificate required; actual helper/nested Drop/forget unproved.

Fresh fullS6 eight-stage regression passes. Production12-patch profile includes target-scoped HRTB, excludes H2d TEST and strict-lifetime drafts. Evidence artifact `overnight-drop_v4-37746579002-1`; full logs audited, source certificates/compiler/model correspondences remain explicit trusted boundaries.

## O20 — isolated generated Drop posts and repaired admission controls

Proof `e30bdc72d7af37222c401dd54ed50759eb840547`; [run37748156620](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37748156620), job113214536937,08:11:09–08:12:34UTC=85s. New ledger511/7200,6689remaining,no active run. Production twelve-patch console/source/spec exact O19 identity; S6 freshO19 matrix cited without rerun. Isolated TEST console built separately only for H2d and never used for actual/S6/cache.

No-key TEST positive fullnormal/unwind0; five generated-post mutants reach real guard call then exact initialized/owner/duplicate-storage/false-normal/false-unwind post failures. Full paired source/MIR/refinement evidence and first-error/outcome traces root audited in `overnight-guard/O20-POST-ADMISSION-REVIEW.md`. H2b accepted **only local source-shaped optional-storage profile** using production O19 proof plus O18/O19 source/MIR/resource admissions and O20 adversarial post tests. Actual nested guard remains open.

G1 all9 now intended, including exact preservation equality predicate classifier correction; O19 original INCONCLUSIVE unchanged. HRTB all15 matcher controls intended after projection-clause counting and parsed local ghost declaration fixes; no owner proof claim from matcher-only controls. O19 full callback normal/unwind/resource/leak proof remains separate evidence. Generated complete decoder captured for read-only audit of actual-owner fingerprint representation.

Strict-lifetime draft remains inactive: static review found mutable inference references inside aliased entry metadata snapshot; fail-closed freezing/inference/escape controls are prerequisite to activation. No verifier/kernel checks weakened.

## O21 — full decoded owner repeat, ordinary join-four and source-anchor failure

Proof `d2f657be87ba58d77618950d8c030a31a21cbfb8`; [run37750512251](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37750512251), job113222299883,08:32:33–08:35:25UTC=172s. Ledger683/7200,6517remaining,no active run. New thirteen-patch console (default-off mandatory-refusal probe) built and fresh fullS6 eight-stage matrix passes.

Complete eager decoded VfMir bytes60174 and all five Bodies4498/4849/3503/38915/4920 repeat byte-identically across two same-binary/source invocations. Unit SHA256 `3075b627aab5c0548f6f30a3727af5215bc6859a446009263de718b20a18d66e`; outer `e44b5f3aec64a0ccf97cbf473c0d5fb348e5dd4e68b597e63a03ef255245c1e9`, nested `70493e53b55743ead2f08035908d251656f3b55da123bee5c1ac2e93370e767f`. Full source/refinement passes; probe always refuses before redirect. No digest-only semantic acceptance; next source/typed-fullunit admission needs separate strong integrity and pointer/cleanup/resource review.

Ordinary current-cell join-four full proof0 (74statements), lemma and caller leakchecks; paired export/decode/refinement/source all0. MissingthirdTown fails at lemma pre8, duplicatefirstTown at caller post61, shiftedbase at missingfifthcell pre9. Reviewed local resource join, no comparator/sort4/initial-values theorem. Bounds obtained from four stockpoints_to_limits, no new provenance axiom.

Workflow FAIL from actualsort4 calibration preparation only: BORROW_PREFIX_FIRST_CALL contains inline ghost typearguments, while source builder searched unannotated `is_less(...)`. Zero sort4MIR/proof in O21; none of setup failure counts as negative. Precise annotatedanchor repair prepared for a fresh run, source ghost-strip identity preserved. Strict-lifetime kernel draft inactive; revised deepfreeze/inference/sourcepath/CFGchecks under root review.

### O22 — exact owner boundary and preserved generic forget, 2026-10-08

Proof `02945280d4f335948c6edd60feb7ac62092a0256`, [run37754201983](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37754201983), job11323460431709:05:16–09:09:08UTC=232s; resumed915/7200,6285remain. CollectorFAIL only sort4source stripping and CUTmatrix genericheader setup. Main14 console699e83e5,translatorc66a3f4a; fullS6 eight-stagePASS bothmain14 and isolatedCUT; disabledCUTcallback9PASS. Newexactsource/fullunit actualowner gate passes; source3/mir2 negative controls at exactgates withpairedexport/refinement0, no actualproof fromadmission. Later nested translationNot_found line3817: two qualifiedDrop opens are inouter Body.ghostStmts, missing fromnested; newreparentoverlay willmoveexistingrecords/text/spans only. Genericunsafe exactbody checked_forget_owned full0/52statementsnormal+leak, same T.own returned once, unwindfalse; fivepost/leak controlsanddeadcodeintended plusseparateweakenedunwindfixturetargetreject. Localcomponentacceptance reviewed, noSAFEactualstdlink. CUTconsolebuildpassed; positivebasic/ordinaryunmarked/earlyreturn/directunwind full0, nooptinexactreject; remaining13NOT_RUN sourceheaderexpected '(' actual'<'. Sort4builder firstcallanchorcorrected but markerindent ghoststrip failedbeforeexport; COLUMNZEROcommentfixretainsfullruntimebyteguard. O22 originalclassifications/setupfailures preserved, nextO23newproofSHArequired.

### O23 — source-command ownership fixed, first SAFE outcome obligation

Proof94d055d5a0a531a3920acdc74e4cede5e9d0800b,[run37756681437](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37756681437),job11324284611009:26:42–09:30:56UTC=254s; resumed1169/7200,6031remain. Main16consoleeb0c7455/translatorafe841ec; fullS6PASS separately from actualprogress. Exactowner2nestedghostrecords transferred preservingall12 sourcecommands, text/span/realcalls/normal/unwind; oldNot_foundclosed. Source3/MIR3 includingnestedghostsource-line exactstronggatesreject, pairedsource/refinement0. Fivebodyowner first newerror checkedSAFEinterface77: fn_outcome<*Element> passedto pointerrawown; noactualbodymemory proof yet. Newsourceonlyoutcome_result ghostprojection prepared, fullnormal+falseunwindunchanged, needsfreshcertificate. 7/9sourceconstructionfailedbeforeexports because scopedmodule ManuallyDrop importincorrectlytreatedtop-level; minimalboundaryfixprepared. Sort4markerindentfixed, secondstripresidual twoblankline separatorsbeforeactualsignature; exactstrip guard retained and newmismatchcandidatefiles prepared. CUTfourpositives/eightintendednegatives, genuineFboundpositive unresolvedentrytype rejection; lastfour NOT_RUN secondgenericheaderguard; lawful live<T>positiveVF0/60. Bothproduction+isolatedS6 PASS and disabledCUTCB9PASSare regressionsnot actualcoverage. Latestownersteering prioritizes hostedsourcepreflightbeforebuild and one stableactualowner/sort4prep; pauseindependentnewmodelwork, preserveallcandidatefiles.

### O24 — preparation closed, complete graph and first actual sort4 barrier

 [run37760135524](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37760135524),
proof `2ca66b89ed3b17c3a054c6bb5b9d1b4b3ad2348b`,09:56:44–09:57:37UTC=53s.
Resumed **1222/7200**,5978remaining; no active run.
Hosted independent owner9/sort4 sourcepreflight PASS BEFORE console, exactruntime
strip/fragments retained. Cached main16 reused with exactprofile; unchangedS6 not
rerun. Both whole NORMAL/readonly MIR exports/refinement0. Owner9 completeunit+
9body eager snapshots captured, mandatoryrefusal remains: no semanticadmission,
no actualhelperproof yet. Selectedowner source8629849c, original466882d7.
Sort4 wholegraph obtained; fullsource check enters actual `sort4_stable`, first
error `verified/lib.rs(185,13-36): No such function: __vf_sort4_first_unwind`.
This closes preparation barriers O22/O23; reservedunwind handler is next exact
translation obligation, fullcallback/arrayposts remain unproved. Runtimewholebody
identity, all5FnMut/8select/4copy retained; no prematureacceptance.
Next: exact9 source/MIR admission+existing nestedguard/forget/A1 integration;
review firstFnMut handler against complete sourcegraph. [O24](overnight-linkage/O24-RESULTS.md).

### O25 — exact9/H2 integration and first A1 linkage obligation

**Last completed O25:** [run37761756051](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37761756051),
proof `8a7a698ed6001273b953987cd6fd7517ff6219d5`,10:10:51–10:13:56UTC=185s.
Resumed **1407/7200**,5793remaining; no active run.
Main18 builds, exact9source/fullMIR and nestedH2 gates PASS; qualified nested
call links but its body has not yet been verified. Prefix generic method
normal/unwind return+leak checks pass, checked_transmute_neo_pointer fullbody
passes. First realprooferror now `verified/lib.rs(117,13-35): No such function:
std::mem::transmute_neo` in localchecked_assume_init_pointer. Actual SAFE
prototype/body and nested Drop occur later, remain NOT PROVEN.
Source2 controls exactsourceSHA intended; cleanup24->23 directMIR control
exactunitSHA intended. Move/Copy control INCONCLUSIVE setup (stale_34 vs exact9
Move_32); originalclassification retained, minimalrepair prepared. FullS6 all
8stages freshPASS separately. Next exact9 A1local+actualcall links and SAFE
forget ownedsummary/normalCFG composition, preserving other9cleanup preds.
[O25 evidence](overnight-linkage/O25-RESULTS.md).

### O26 — actual body reached after A1/SAFE links

**Last completed O26:** [run37763468180](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37763468180),
proof `c19e4c50470d32199178d5229a2819554fc6b2f1`,10:26:27–10:29:36UTC=189s.
Resumed **1596/7200**,5604remaining; no active run.
Main20 fullsource/refinement/exact9/H2/ownedforget/A1gates pass; allprefixchecked
callees verify, including localassume_init and ownedforget, SAFEoutcomeprototype
passes; actual `select_unpredictable` BODY STARTED. Firsterror at198,77-82:
closeGuardOwn(t,guard) sees actual **Element vs qualified Guard<*Element>.
Rustshadow debug-name map resolves ghostguard to earlier pointer. Next source-only
logicalrecord owner closure mustmatch realconstructedGuard from initializedcell
+Town; runtime unchanged, freshsource/fullMIR snapshot/certificate required.
No nominalowner fabrication. ActualnestedDrop body occurs later and remains
unverified; helper notfullproved. All source2/MIR2 negativecontrols intended,
staleMove repair confirmed; historicalO25INCONCLUSIVE unchanged. FullS6eightstage
PASS separately. Sort4 O24 fullgraph/firstreservedmarker unchanged.
[O26 evidence](overnight-linkage/O26-RESULTS.md).

### O27 — external initialization failure before runner allocation

Proof6165296266ee17ae8f91f7550034452cd0ebb0cf/run37764722707 created10:37:46 thenFAILED10:37:51. ListRun/JobsAPI showqueuedjob113269452142 runner_id=null/no steps; GetRun/GetAttempt/logs404, noartifact. CheckSuiteFAILED, CheckRunqueued/noannotations; repoActionsenabled. No proof/preparation execution, notnegative. Budget1596confirmedallocated seconds plus5provisionalreserve until metadata resolves; no hidden PASS. Fresh narrowedsourcecapture-only nextSHA justifies one recovery dispatch; preserveO27plannedTESTscopework but avoid expensiveindependentbuild until primaryevidence.

### O27b — external Actions account refusal; final checkpoint

Fresh source-only recovery dispatch from proof
`847bd01709d4a1269ff02ef63a436dd8cacf67c2` was rejected with exact GitHub
`HTTP 422: Actions has been disabled for this user`. No run/job was created.
This is external account refusal, not source prep, classifier, admission or
proof failure, and cannot count as a negative control. O27 remains completed
FAIL before allocation (one orphan queued job/no runner/no steps and six
skipped/unallocated jobs); no active workflow. Stop retries; preserve all
drafts and unchanged historical results. Confirmed1596 jobseconds plus
5 provisional reserve,5599 available of7200; deadline11:30UTC unchanged.
[Final checkpoint](overnight-linkage/RESUMED-EXTERNAL-HANDOFF-2026-10-08.md)
records exact main20/profile, unverified changed source, actual delta versus
O22, remaining controls and next permitted hosted action. No local proof/build.

### CLOUD-BUILD-MIGRATION before A/B/C, 2026-10-09

Entry89e0a36f8df67bb2f66cf0564f497a0a4bad4aac clean; newownbranch
research/cloud-build-migration. Owner explicitlyauthorizesexistingCloudBuild
smallsort-ci/global,
e2-standard-2 andexistingbucket. Noactivebuild initially; owner smoke
f6f0f600-5558-4ac1-9011-0b73e4533a83 SUCCESS confirmedread-only.
Freshphase3600seconds/max1800/build, separatefromhistory.
Hypothesis: exactpublishedSHAs/pinnedUbuntu/provider-only guards preserve
stock source/export/decode/refinement/proofclassifications and complete
acceptedconstructor matrix on coldsourcebuiltS6+CFG.
A probes must store/readhashes and fail finalverdict for original42/124.
B history a0cfd30e066acbaf1b5406cd9773f54388cc45be, C history
1378f0ffc8342233349fae3df5a938c4a021c8d7/run37700450091.
Domains/posts/classifiers unchanged; baselineforgetinconclusive remains
inconclusive, noadmissionhelper/sort4/merge. Allnewresource proofworkexcluded.

### Cloud A0 setup outcomes and A1 packaging repair

Two no-Build API validation refusals (4000-byte substitution /10000-byte
step-argument limits), exactdispatchtoken lookups empty, zero timecharged.
Request encoding repaired with bounded compressed chunks/package; commit
inputs checked beforedispatch. A0 Build7bda20f0-cef7-4ff4-8c21-697374572b34,
infrastructuree863c2503789ecb307448959894626c7a481aebb, executes smoke0,
then package step127 Python3 absentfromSDKPATH and finalstep cannotstart.
No bucketobjects/archive, incomplete evidence, no storageacceptance. Both
pinnedimages match actualBuildStepImages. FullCloudLogging diagnostic retained
by BuildID; budget charged conservativecreate→finish fromAPI. New repair uses
SDKbundledPython absolute path; no tool/proofsemantic change.

### Cloud A success and managed error confirmed

Infrastructureac74f00c27207a0f23660b6a4de2e625dbec050e; smokepreparation
proofSHA89e0a36f8df67bb2f66cf0564f497a0a4bad4aac (no proof tool invoked).
fd0020bd-967d-4e4b-ac20-83c578733389 SUCCESS,47conservativeseconds;
config59d2bed90e6e4dacb8fda9345fb20f607a487a1dc9bfcfe977a817013479c90d,
archivedbbc6c7d8294ca6d5360e7807ec2c0c12e50b6997e4540b371b869f9620c387e.
Cloudbuilder createdprobe+manifest anduploadeduniqueBuildIDprefix; VPS
dispatcher downloaded/readprobe andverifiedallarchive/inventory/config/pins/
receipt. CPU2, Ubuntu22.04.5, x86_64, MemTotal8147688kB.
63862150-33e7-4b9d-b692-1231f9c34520 FAILURE,53seconds; originalexit42
preserved, failureclass infrastructure-probe-error, uploadcompleteandVPS
hashvalidationtrue. Configd773eb4b0da288c33daa59eacc48150e8ce9fc876b20b3a6139bea81d5426b4a,
archived7416a4a8223dfca3dc76beb6166fcf1f1a0272ed658adc1dbf326c070387ab5.
Eachprefixgs://smallsort-ci-evidence-504462351565/cloud-build/<BuildID>/.
Neitherprobe is proof acceptance; smoke verification_acceptedfalse.
Total39+47+53=139/3600; prioraccountsunchanged.

### Cloud A timeout confirmed; A complete

Build6604590a-f626-4ca0-81da-71f3d9091e25, infrastructure
0de62646ddfdc36a8f2254a555f9a35cba94b000, FAILURE with original124,
infrastructure-probe-timeout. Full evidence uploaded; VPS download/inventory/
config/input/receipt/archive validation PASS. Archive
1e103e19acedf068ed84b8ee95812fdbc2ea9e19675dbd010b1c4e81841b044c;
configa3cd91b0a45aaef61eadad0b7eb52408f256474c993ddcff45a935cee8a4ea08.
A positive/error/timeout accepted only as infrastructure controls; no proof.
Accounting correction from API: conservative39+47+54+59=199/3600, remaining3401; old accounts unchanged.
B hypothesis: frozen stocka0cfd30e fixtures retain original outcomes and all
source/export/decode/refinement/body/return/leak/unwind gates under real
cloud-build provider guard. Full stock diagnostic audit retains historical
forget-positive/deadcode limitations; no upgrade to whole generic forget proof.
B infrastructuref694acddad88d4c353850f3a170adb7adb30bdb0, cold timeout800.

### Cloud B0 source-access failure, not a proof-negative

Build3e4c62e0-744b-4278-b10e-fc74f599dbe7, infrastructuref694acdd,
proofa0cfd30e, configf2108dd2bb82e9a2df20a56f861d65cc6f01e67cfe1e4e64a2ebf57a81c68138,
FAILURE/original128 during anonymous GitHub fetch; no proof tools executed.
81 conservative seconds, total280/3600,3320 remaining. Archive
c474f40ca1209292cfafbb1f7424a8d2c58bb22e2b1fdda0e395dcf1e532b995
complete available material downloaded and hash-verified; summary incomplete
for proof, accepted=false. Anonymous API/raw/codeload also404, authenticated
repository metadata PUBLIC. No invented GitHub identity or token export.
Owner asked about credential-free pinned source archive transport; awaiting
answer before dependent Cloud dispatch. Prepared infrastructure repairs:
JSON helper fall-through prevented nested manifest/audit parsing (must not
weaken acceptance); VFDeps root compiled-in prefix symlink points into
/workspace alongside historical /tmp prefix. Neither changes proof semantics.

### Prepared pinned-source transport; dispatch awaits owner answer

Problem: public fetch is inaccessible despite PUBLIC repository metadata.
Proposed infrastructure semantics: transmit only original commit/tree/blob
objects for an explicit narrow allowlist, with gzip and SHA256 transport hash;
restore a partial Git repository at the original SHA and verify each selected
path/mode/blob before proof generation in Cloud Build. No runtime, contract,
expected classifier or verifier semantics change; no credential transfer.
Trust boundary: original published commit and content-addressed tree paths,
explicit source bundle hash, unchanged source certificates/refinement/proof gates.
Self-review corrected raw Git tree binary decoding and expanded dependency
closure for C native fixtures and both provider-only checker overlays. Package
and VPS checker require matching source archive/certificate for proof acceptance.
Source reconstruction and B/C proof controls remain UNRUN. Current A evidence
is unaffected; prior B original128 remains setup-only, never proof-negative.
New module/control/provider/packaging preparation is reviewable in migration
branch, not authorization to dispatch the alternative route before response.

### Cloud migration resumed: pinned object delivery authorized

Owner explicitly approves delivery of original committed Git objects from VPS;
this supersedes anonymous-fork fetch requirement. Budget not reset:280 used,
3320 remaining. Pure Git/hash/config preparation checked every transmitted
object; B bundle255463bytes/10proofpaths and C343353bytes/16proofpaths at infra
24ff4ff5, max step argument8579/8581bytes, env29/33, substitutions107/140.
No compilation/verification/fixture generation or restore test on VPS.
Cloud must validate all original OIDs, selected closure, SHA256 and exactHEADs
before tools; static source restore review confirms no remote configured.
MCP separate logs/index <=8MiB, permanentCloud workflow and trigger inventory
prepared before next cold B. HistoricalA not repeated, no proof claim yet.

### Cloud B1 stock reproduction and source delivery confirmed

Buildce77c943-f657-47da-9dfa-4b6e16d3679e SUCCESS; infrastructure
30fc3b42a2fb980b49174d459ec5cfbea778379b, frozenproof
 a0cfd30e066acbaf1b5406cd9773f54388cc45be, config
f532b8cccd907fef8076a02ba80c7cd4784d8a312825870b6180afcff59d55e0.
Sourcebundlea1ab7bad2340b84cc556eecb08d5bf99ee658e4f86523f6720cac880de584b3f,
261950bytes, Cloud confirms original commit/HEADs and selected object closure.
Archive dac3492bb16ff5501403449ddad5a404c989e928259360dac5f20f9c305d4ad6,
index6a62d9809e31d62b43235a3a12aaa063ab435287407f3ba1603174dd0ceb4d28.
VPS downloaded archive/index and all separate chunks, all hashes/inventory/
reconstruction verified. Four positives/four intendedpost-or-unwindnegatives/
two exactdeadcode rejects; genericforget remains INCONCLUSIVE. All11
normal/readonly export/decode/refinement and source-integrity gates zero/true.
Accepted operational stock chain only, with original historical limitations.
164 conservative seconds, cumulative444/3600,3156remaining. A not repeated.
NextC: historical accepted constructor1378f0ff/run37700450091 with exact
S6candidate20f7d07a thenCFG593d0940, cold source-built console and all16source/
proof+9MIR/native10/false-frame4 controls; actualcallee NOT_RUN. Unchanged
semantics/posts/classifiers. Max1500s build withinremaining; no otherbuildactive.


### Cloud C1: historical constructor reproduced; migration A/B/C accepted

2026-10-09 Buildd9e4538a-c6c0-4881-b422-de6ceae72d19 SUCCESS,328 conservative
seconds. Infra30fc3b42a2fb980b49174d459ec5cfbea778379b; proof1378f0ffc8342233349fae3df5a938c4a021c8d7,
comparison O3/run37700450091. Config15db37f3bb8b331e06f747c51078d0430e17ecba827ef28c9aeec8269e83fc99;
sourcebundle5a36ec008dbc0db57bcf69efe616057bc93c54c82cb8d97a2e9500344bf78b1c.
Cloud verified original HEADs/object closure/file hashes before cold VF source build.
Exact historical S6candidate20f7d07a thenCFG593d0940 only; source console compiled,
16source/proof+9MIR+10native+4false/frame accepted at original expected boundaries.
Exporter/decode/refinement/source-integrity/return/leak gates preserved. Independent
artifact review confirmed component profile, ownership controls and admission
failures. Actualcallee NOT_RUN; source-localcopy applicability/def-path matching is
not DefId equality. No helper/sort4/merge, wholeS6/O26 or generic/ZST theorem added.

Archived2ef48f11744fd622520524e2ab859c479a400e17385ddcf982546b0f885d18c;
textindex72007409313e1d94691b7e465ee214451ceb6d52391aa5d0bd576b30f6136f15.
VPS verified archive, externalmetadata, inventory and all482 separate text files,
including lossless reconstruction. Sourcebuiltconsolef0d3c92651d98d91ceed57d58d93087bee0106a094b7efc1e956820c46132642;
no historicalbinary byteidentity assumed. Existing permitted duplicate mutation
profile tool omission810entries explicitly inventoried; all MIR/wrappers/logs retained.
2CPUs, MemTotal8147688KiB; compile53.49s/398136KiB/185%CPU; largeststageRSS546084KiB.

Total772/3600,2828remaining; historicalaccounts preserved, no active/queuedbuild.
A not repeated; Aerror42/timeout124 still FAILURE with verified evidence. B retains
strict classifier/deadcode/genericforget historical limits. A/B/C accepted only as
[reported](cloud-build/ACCEPTANCE.md). PermanentCloud workflow, source delivery,
MCPreader/separate<=8MiBlogs and exact second-direction commands documented;
no resumed proofwork, external publication or automaticActions trigger changes.


## NIGHT-CLOUD-1 — minimal shared interface and O26 restore card

Actual target: repository hint.rs select_unpredictable, nested DropOnPanic::drop;
then smallsort.rs sort4_stable. Infrastructure-only common interface retains
accepted images, no-source Git-object restore and full bucket publisher. Atomic
flock covers global reconciliation/API ongoing check/reservation/submit; uncertain
response or crash keeps owner/token/BuildID; independent phase ledgers and ready
requests arbitrate turns. No proof semantics are changed by orchestration.

First falsifiable proof hypothesis: unchanged O26 source/profile reproduces its
198 guard-shadow type rejection and prefix callees, while prepared guard-literal
source has exact runtime twin and fresh full paired MIR/refinement/nine-body
inventory. Old17/20 must refuse changed source; refusal is admission, not intended
ownership negative. Historical proof c19e4c50470d32199178d5229a2819554fc6b2f1;
20-patch manifest O26-PROFILE-MANIFEST.json, stdcd371e03/VFf76012fb/nightly2026-09-25.
Pointer-specialized T=*const Element, unrestricted implicit-Sized Element:
thread_token(t), t=currentThread; normal same thread plus condition-selected
pointer and raw_ptr_own<Element>; unwindfalse. No Element pointee permission.
Actual nested Drop and complete helper/return/leak remain open until verified.
Source/MIR/setup refusal cannot count as resource failure. Full checks retained.

O26 baseline and candidate results are isolated; no historical constructor smoke
or unchanged full S6 matrix. Record new console/profile hashes and original
exporter/refiner equality. Fresh body/unit digests and ghost ownership/inventory
review permit separately identified17/20 refresh and affected source/MIR refusal
controls; parser/resource error instead selects a narrow causal repair. A collector
PASS is explicitly diagnostic_complete, never verification_accepted by itself.
No unchanged failure rerun. Initial timeout1200 plus60 queue, within1800 and own
10800/deadline08:00UTC. Semantic/card/regression requirements apply to each later
change. Runtime/std/signatures are unchanged.


NIGHT-CLOUD-1 pre-dispatch: O26 config refused bounded180-part source payload;
no reservation or Build,0s. New source-input v2 transports a shared original
Git-object pool once across infrastructure/proof/baseline. Each repository still
checks its exact required closure, object identity/type/size, original commit/tree,
mode/path bytes and HEAD. Pool must equal union of all three original closures;
no additional objects or missing references. Legacy v1 remains readable and is
used when no baseline. This is transport only, no verifier semantics or source
change. Fresh actual O26 restore is the positive gate; old A/B/C need no replay.

Second pre-dispatch refusal also0s: shared-pool archive704024bytes still exceeds
transport. Original-object gzip before base64 reduces measured same input to
471949bytes; each decompressed raw object retains original type/size/Git ID check.
Source substitution chunk3900 (below API4000) with180part cap leaves margin;
config evidence transport remains3500. No input removed or source compressed
lossily. New Cloud restore checks exact original bytes; no verifier profile change.

Third preflight refused expanded restore script in >10000-byte execute argument,
no Build0s. Move pinned restore bytes into explicit env like existing packager;
execute argument decodes that value. Source/script bytes remain in hashed exact
submitted config, local-vs-infra source-input check unchanged. API env mechanism
already exercised by packager; actual new restore/O26 is the joint fresh gate.


## NIGHT-CLOUD-TRACE — independent CUT instrumentation card

Actual sort4 first FnMut recovery requires current four-cell/F resources on
normal and each unwind before subsequent calls. Current isolated CUT blocks local
positive_f_bound at84:9-38 strict entry freeze; actualsort4 handler185 unproved.
Hypothesis: an erased nonparameter temporary declared outside the scoped callback
is first unresolved outer_tenv entry. Prepared bc129b38 TRACE print-only overlay
must name/type each entry before unchanged freeze and retain the EXACT strict
entry rejection. No inference assignment, owner creation, resource/post change,
exception suppression or production/kernel promotion. Keep TEST console separate:
production source → isolated unchanged d557082b strictCUT (translator+kernel) →
print-only TRACE affecting only src/verifast.ml. Verify exact resulting diff/file
inventory, exporter/refiner/schema/spec identities and production unchanged.

Run only exact positive_f_bound same source pair/full NORMAL+readonly/refinement,
F:FnMut current cells and unchanged normal/unwind recovery contracts. Existing
lawful CUT positive not rerun. Expected diagnostic error at original84:9-38
Strict lifetime binding has unresolved inference in entry outer type; last
STRICT-CUT-ENTRY identifies cause. Changed error/stage, no trace, missing MIR,
refinement/source mismatch or production mutation means inconclusive, not negative.
Outcomes: named dead local permits new separate liveness/alias/admission review
before saved relocation TEST; live formal/bound/heap type needs a different sound
scope/inference design. Never skip unresolved live types or borrow-end resources.
This independent diagnostic can join a later new actual candidate Cloud build;
its success is not CUT/actualsort4 acceptance. No extra infrastructure smoke.


### NIGHT-CLOUD-1 result — SETUP, no actual proof

Cloud Build680ea0b2-a453-476b-800b-85cb631a455a FAILURE,
infra/proofc43300c027752e7baffc1aaca3326564baabe7a2, timeout1200/reserve1260,
create01:04:08.919889445Z/start01:04:09.658136434Z/finish01:09:29.270511Z,
charged321s (own321/10800,10479remaining). Three original Git-object checkouts
restored with selected closure/path/type/mode/byte hashes and exact HEADs.
Source pool8ac1128f32c46031a6677b529baefb3ba50b124dfcc50c9471b18450be1c8427;
config4ab5e78809de7734cb505110a15a0fd0d281c88200832724f95bde0bb454a5ea.
Cold exact O26 twenty patches/applied6c4c5a77, exporter b00c75f4/refinerb049c8d1,
specd33b2a7a/parser7bf12f12/translator737e16e3/schemaf48fcf29 match historical.
Consolee1b447b65c32d7177734b05481ead86c989d14be3cfdef6660df44e179d8839c;
console bytes differ from historical, no equality assumed. Kernel unchanged.

First failure baseline-capture PREP.write_case → constructor source certificate
imports missing overnight-s6/prepare-and-check-sort4-select.py. This is a registered
input-dependency omission despite correct selected Git closure; no generated actual
source/MIR/cert17/20 or body proof/negative result. Falsifiable next change: add
exact missing file to both current and baseline and generate both sources BEFORE
console/tool preparation; freeze/compare runtime twin/source fingerprints. Further
import failures fail early. A successful cold tool build alone is not O26 acceptance.

Publisher/evidence complete true, run-exit1, diagnostic_completefalse,
verification_acceptedfalse; full bucket prefixcloud-build/680ea0b2-a453-476b-800b-85cb631a455a.
Archive361ca3c7f8521930e7e2e9d2e34f819ac4824a2178eb354d0044a08d0eed0c8c
and all included files/input/config/upload receipt/text index verified on VPS in
/tmp/smallsort-cloud-evidence-680ea0b2-a453-476b-800b-85cb631a455a.
Separate text chunks not redundantly downloaded; original included logs retained.
No migration or second-agent budget spent, no Actions/local proof execution.


### NIGHT-CLOUD-2 result — complete O26/TRACE diagnostics

Build a24604cd-e1d2-43ef-8e4e-f2e313ec44e5 SUCCESS, infra/proof
ad1e0e9f8ac776f3814426015fa270b55b4fcffc, laneo26-trace, timeout1200/reserve1260.
create01:21:29.299093871/start01:21:30.053984064/finish01:26:42.306230UTC,
charged314s: own635/10800,10165remaining. Exact three original Git checkouts,
input closure/source bytes/modes/HEADs passed. Inputf47982434b5b99f631065ce5963400545834e799cf0e44d6496cb96e8f9766c3,
configdcf1f395288ac91d55ee0712fd2c1452908bd69e8f6d94ffe59f67542657ff9d.
Full archivee41b837f9d141c46594dc3f861f02e755b291d50bb1feb02aa5395110fee95a3
and every inventory file/config/input/upload receipt/text-index verified in
/tmp/smallsort-cloud-evidence-a24604cd-e1d2-43ef-8e4e-f2e313ec44e5; full included
logs read, no old-log redownload or duplicate textchunks.

Early source-only preparation and repeated post-build source comparison passed.
Both independent baseline/candidate exports NORMAL+readonly/refinement/all9
complete records and10 Marshal.No_sharing snapshots complete. Baseline exact
source8629849c/original466882d7 reproduces first guard shadow error198:77-82
Element-vs-DropOnPanic. Candidate source1798132ff7a1585db7367779365c88e5ef5f417adcff0bf82779bf6a674945e6
is refused by old17 at owner exact verified source SHA256 before admission.
Verified source diff is EXACT two logical owner-close arguments; runtime original
identical. Of9 Marshal body snapshots, only body7 changed:
9577c64905c4a45eecc4aab506f6276fea076f8a7a18d2f7ca0304cf70205b86;
unit10cf6e4d2a462082d456135078a77ea6670358f1ad15e0d81901104e8a102b43.
Other8 match historical, saved_guard and fullposts unchanged. These observed data
permit separately reviewed refresh17/20, not ownership acceptance.

Exact production20diff6c4c5a77; non-console historical pins match. Rebuilt console
e1b447b65c32d7177734b05481ead86c989d14be3cfdef6660df44e179d8839c differs
from historical56bb; no byteidentity inherited. Kernel production unchanged.
Isolated d557strictCUT+bc129print-only TRACE source audit passes; console
83f6e0e19679ae326d75ec31b859d9697909ae8b7269f93f871bcfc7af2f8361.
positive_f_bound rawcapture1/fullproof1, support exports/decode/refinement all0,
exact first84:9-38 strict entry freeze unresolved preserved; last trace
$_32:&?T, preceded cmp_k,$_37..$_33. Same pinned source66bf5a6e/original9b41aef5,
NORMALbody10356bf1/readonly9fdee764. Production unchanged/spec/tool identity checked.
This diagnoses erased local declaration scope; saved e718 relocation TEST may be
run under separate profile/card, never skip strict freeze of live/formal/heap types.
Direct Continue unwind bypasses StorageDead, so AST continuation recovery must
be checked; mandatory liveness/alias/bound/heap/CFG mutants remain open.

Publisher evidence_complete true/runexit0/diagnostic_complete true,
verification_accepted false/actual_helper_proved false/actual_sort4_proved false.
Collector SUCCESS proves no actual function or lifetime profile acceptance.
Next: independent refreshed17/20 proof candidate and isolated relocation diagnostic,
no unchanged historical full matrix. No budget borrowed or local proof execution.


## NIGHT-CLOUD-3 — refreshed select and independent sort4 obligations

Actual select contract/domain unchanged from NIGHT-CLOUD-1: T=*const Element,
implicitSized Element, current thread; normal exact condition-selected pointer
plus its raw_ptr_own, unwindfalse, no Element pointee permissions. Only observed
17/20 source/certificate constants and exact two owner literal reconstructions
change via separate21/22 deltas; frozen20 and kernel remain unchanged.
Hypothesis: truthful nominal owner admission now reaches next real resource
obligation/fullbody. New profile translator0862e635; exact patches/profile/card
O26-REFRESH-PROFILE/O26-REFRESH-CARD. Fresh pairedMIR/refinement/9bodies/10Marshal
must stillmatch observed1798132f/466882d7/10cf6e4d/9577c649 and8oldbody hashes.
All7actualprefixcallee proofs must occur before helper, actualnestedDrop later
must fully verify, fullnormal/unwind/return/leak/dead/validity remain required.
No collector success establishes full theorem or profile acceptance.

Affected owner17 controls use four separate fresh source pairs and real paired
exports/refinement: ownerpredicate/outcome ghost-only source mutations refuse
exactverifiedsourceSHA; actualforgetMove32→Copy andcleanup24→23 TESTexporter
wrappers refuse complete decodedunitSHA. Check exact mutation/realexporter/
console/sourcecanonicalbytes; only named first fatal at17 counts. Earlier
setup/frontend/helper errors do not count; these are not A1-specific negatives.
Independent A1 gates stillOPEN before combined acceptance; no summary borrowed.

Independent isolated CUT+e718sixdeclaration relocation TEST uses unchanged exact
source66bf5a6e/original9b41aef5 and wholeNORMAL10356bf1/readonly9fdee764 graph.
Baseline must preserve strict84:9-38 refusal, relocation trace6/1 andunchanged
kernelstrictCUT/spec/exporter/refiner checks; full0 orone genuine nextbarrier
onlydiagnostic. Fullgates in CLOUD-RELOCATE-TEST-CARD remainOPEN, no production
kernel promotion. Independently capture actualsort4 on same Cloud tool, exactO24
source/pairedwholeMIR/refinement and5/8/4inventory, proposedfirstcallaudit,
firstreservedhandler185 refusal. No handler/CUT/HRTB semantic optin for actual;
partialnormal diagnosticdomain sizeT>0 separated from fullnormal+fiveunwind
safety targets and generic/ZST/ordering. Normalbranchverifiedfirst: its error
cannotcountas directunwindhandler proof. Actualsort4 capturecard recordsposts.

Newlaneo26-night combines these isolated records inonecoldCloud console session,
no A/B/C/constructor/baselineO26/TRACE/unchangedS6repeat. Exactoriginal2Gitobject
closures, pins/no-source/fullbucket evidence retained. Timeout1200+60queue
within1800/own10165remaining/deadline08UTC. A ready request waitsunder shared
flock foractive mergebe12e7b2; failed submit refusal0s, no ownBuild/reservation.
Outcome: resource/type/parser blocker→causal repair withnewcard/sourcecertificate;
positivebody→affectednegativegates/admissibility review; TRACEscopeTESTnextblocker
→separateTESTalternative; actualsort4certificate→defaultoffhandler design, never
weaken normal branch to force unwind. Everychangedinput requiresnewBuild.


NIGHT-CLOUD-3 static pre-dispatch review corrected a draft shared-owner regression:
unconditional literal reconstruction also affected oldfive path. No ownBuild,
reservation or expense. Revised21 selects literal onlyifnine; historicalfive
owner371bytes SHA d4408b1ae832380f9fa31abceace42c58c3aee4a2e5b39725dcf6f8994fa6d82
matches exactCloudbaseline; nine485bytes SHA22746c3b0a7b0fad00cbce75075d1b4572b1a63867b122ef1852fb838baff8f6
matches exactCloudcandidate. StaticGit applycheck on savedmatchingfrozen20 source
(no compiler/verifier/runner) passed21+22. Translator0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a,
patch21 0a6ac67c31b785acd5b2ab5eb9eb0158e0b5603dafda05033b7c58a6ef941c54.
Cloud freshchangedprofile stillmandatory; unchangedhistoricalmatricesnotreplayed.


NIGHT-CLOUD-3 dispatch preflight0s: exact2repo o26-night payload551915bytes,
base64735888chars requires189 old3900parts, exceeds180. NoBuild/reservation.
Existingclient source transport now191parts*3990, plus9configparams=200exact,
within officialCloudBuild200/4000 limits (checked2026-10-09), no inputomission
or semantic/source/object-closure change. Samearchive remainsindividuallygzip
originalobjects/sharedpool. Updatedtransport gate combineswithnewresearchBuild,
noinfra-only smoke/A/B/C replay; overlimitstillfailclosedbeforedispatch.


NIGHT-CLOUD-3 outcome: Build546547c0-60e1-4d32-a7f5-8404790a5630,
infra cbd1e103ca15f99b207b6edc5606a06edf6a3d71/proof4ab01bd1a0c13868732abe2e24ad7ee59b5e522e,
02:01:38.114535–02:06:46.007526 UTC,308 conservative seconds. FAILURE.
Cloud execute completed: candidate proof_exit1/source unchanged; four17negative
reports exact; actualsort4 O24 graph+reserved185 marker diagnostic reported;
relocation capture failed its compound source/MIR/AST admission condition.
No full archive: packager found nested shadow bin but its manifest indexing
required a direct child of cases; actual adjacent manifests already had four
identities. Cloud log/Build metadata retained in /tmp/o26-night-terminal.log and
/tmp/o26-night-build-detail.json. Download attempt confirmed all publication
objects absent; do not count any provisional result as accepted proof/control.
Budget943/10800,9857remaining, noownactive. Source transport189parts completed;
full evidence publication still needs changedcomponent fresh Cloud gate.

NIGHT-CLOUD-4 pre-experiment: unchanged actual9pointer select normal return
<T>.own for selected value, no unwind (pointer domain), unselected pointer guard
ownership discharged; full return/leak/dead/refinement enabled; genericnestedDrop
normal+unwind optionalcell/thread post unchanged. Tool frozen20+21/22
translator0862e635, production kernel/spec/exporter/refiner unchanged.
Hypothesis: depth-correct identity manifest discovery restores complete archival
publication; full canonicalproof log reveals actual nextresource/type blocker.
Isolated TEST card A1-ISOLATED-TEST-CARD.md changes only synthetic NORMAL
assume_init Move(_37)→Copy(_37); canonical NORMAL/readonly/refinement retained.
Production firstfatal17unitSHA expected; separate TEST17twoobservedhash refresh
must admit17then exactA1 move-selected-wrapper fatal20 before proofentry. No
TESTacceptance/theorem/kernel change, all8otherbodyhashesunchanged. Four17
controls and exactO24/relocation diagnostics recollected because previousfull
artifact was lost; no infrastructure-only smoke/migration/constructor/matrix.
CUTrelocation semantics unchanged, source/MIR/strictbaseline84 and6/1trace
conditions retained; new visibility names preciselyfailed conjunct. Fullgates
remainOPEN. ExactinputGitclosures/no-source/fullbucketpublication mandatory.
Outcomes: canonicalproofblocker→causal ghost/proof repair; A1 exactfatal→record
isolatednegative only; anyearlierfatal→inconclusive; relocationnextcondition→
localizeusingcompletearchive, neverdisablefreeze/liveness/unwind/resources.
Timeout1200+60queue within own9857/deadline08UTC; oneglobalatomicreservation.

NIGHT-CLOUD-4 outcome: Build `6c560082-2359-4444-85ec-8bb247aea7ae`,
infra `accb752d22df6e39c148576086da3d6d591a4a00`, proof
`61034fd53009056deff0ae1d70650a9f1542322f`; 371 conservative seconds,
own account 1314/10800, 9486 remaining, no active Build. Full archive SHA-256
`0df8a1682e6fe47123273ab30eaa58bec0d3d92d10160afb60cf1616dd65969e`
and text index `6fc4ff7ec5a4df8cff031017827135e3cb610b20fe19f6450b854347a577bfed`
verified after the depth-only packager fix. Publisher run_exit0/evidence_complete
true, diagnostic_complete false, verification_accepted false. This fresh
archive does not retroactively complete 546547, whose evidence was lost.

Canonical refreshed20+21/22 profile translator SHA `0862e635` and exact
nine-body source/paired MIR/refinement gates pass. All seven prefix callees
verify their returns and leak checks. Actual `select_unpredictable` enters its
body; line198 truthful nominal guard close, line203 unselected guard Drop call,
and line210 SAFE forget pass. At the final normal
`select_unpredictable(condition, true_val, false_val).assume_init()` call,
stock `lib.rsspec(462,47-48)` first rejects absent
`MaybeUninit_pointer_own<Element>(t,
MaybeUninit::new(pointer_typeid(Element), payload))`. This is an ownership
precondition failure, not a proved return or leak post. The actual nested Drop
body, outer normal/unwind completion and generic theorem remain unproved; no
new ownership bridge or weakened post was admitted.

Four owner17 controls independently reach their intended first certificate
refusals after source/MIR setup: two exact verified-source SHA mutations and
the real-exporter-wrapped forget Move-to-Copy and cleanup-target MIR mutations
at complete decoded-unit SHA. The isolated A1 TEST first reproduces the
production17 unit-SHA refusal, then a separate TEST17 observed-hash variant
first rejects synthetic NORMAL selected-wrapper Move-to-Copy at A1 component20.
It is a diagnostic negative only; production A1 root mismatch and actual
positive helper proof remain open.

Independent actual sort4 capture has byte-exact O24 verified/original source
`fddb6f1a`/`3602050e`, complete NORMAL/readonly body hashes
`667e4347`/`925b05a8`, refinement zero, five FnMut/eight select/four copy,
and first stock refusal `verified/lib.rs(185,13-36)` at reserved
`__vf_sort4_first_unwind`. Its first-call audit is only
`CALIBRATION_REVIEW_REQUIRED`; active sized-T normal post is partial, and
full normal/five unwind safety, generic/ZST and ordering are unproved.

Separate strict CUT relocation TEST retains exact source/MIR support and the
baseline strict `84:9-38` refusal, but relocation fails earlier at
`verified/lib.rs(52,1-56,10): Strict relocation local type inventory changed`.
The comparison used raw versus translated local IDs; this is a diagnostic
admission failure, not a changed proof verdict. A mapped-ID TEST is the next
separate diagnostic; six-declaration relocation, liveness/alias/bound/heap/CFG
controls and production acceptance remain open. Next actual select work must
derive the missing pointer MaybeUninit owner from valid source resources and
recheck the full original contract; no summary is assumed from this failed
body proof.


NIGHT-CLOUD-5 pre-experiment: see cloud-build/night-select-sort4/INDEPENDENT-TESTS-CARD.md
and separate wrapper-rebase/nested-order/AST-scope cards. Pointer outer exactnormal
thread_token+selectedpointer equality+raw_ptr_own, falseunwind; actual genericnested
Drop fulloptionalcell owner/thread normal/unwind remain unchanged. Hypothesis:
two reversible ghostblocks consume both prior wrapper-indexed owners and reconstruct
current-wrapper owners via existingcheckedlemma (no pointee permission), thenfresh
source/MIR/refinement/nine-body inventory supplies source/unit/body7 certificate pins.
Captureonly, no refresh/proof of changed source yet. Expected8otherMarshalbody hashes
unchanged; mismatch/unsupported/setup remainsinconclusive. Independent translator-only
TEST changes only proof scheduling to exposeactualnested before blockedouter; printonly
ASTPROBE off/on retainsreserved185 and identifiesrealCMPscope; isolatedcoordination
10controls exerciseschangedcommonclient withmockAPI/privateCloudstate. RequiredsameBuild
canonicalbaseline fullpairedcapture/proof; no owner17/A1/relocation matrices repeated.
All independent results keepverification_acceptedfalse; fullarchive mandatory.
Outcome→observednewsourcepins/fullgraph then separate opt-in component23 decision;
nestedbodyblocker→causalresource repair; ASTscope→bounded frontend scope design with
no-resource-loss/escape gates; orchestrationrefusal→fixboundary before nextdispatch.

Dispatched Build347068de-0fb2-45e6-bc00-f8ac3ccd2581, infra
fa3afaf422a2d95404ec325ab3bf1c8f44ec1d27/proof73493da558365dcc8c83d6d6941e782d7dfee455,
config770cef0847d297fa4186f64cc3def80239fafe1f6c94b90aa28fb7ca33ae8e50,
dispatch-f7658e28265541e09895a00b22163035; exactsourceinput
4bcb378c3dcc2d28835144f46012524791974428d79719befdb3ee9078257418.
Timeout1200/reserve1260, ownremaining9486/deadline08UTC. Globalflock reconciled
foreignterminal60fdb811 to sharedreceipt without foreignledger/state writes; no
foreignbudget borrowed. One earliercommand usedabbreviatedSHA andwas refused
beforeBuild/reservation0s; fullpublishedSHA dispatch succeeds. Awaitfullartifact.


NIGHT-CLOUD-5 outcome: Build347068de-0fb2-45e6-bc00-f8ac3ccd2581 FAILURE,
03:08:03.408903781–03:13:25.081645 UTC=322 conservative seconds; own
1636/10800 used,9164 remaining/noownactive. Fullarchive249350fcdd5b33682d11f4a081c65e34c1b64b939fd333ca0f6ff91ec48dc329
and textindex864484b51ce4588755e313f97092540e884e097a7d75236ef2a1da03761a6e6a
plusinventory/config/originalobjectclosures/textindex verified. Canonical source/MIR/
profileunchanged, same462missingwrapper-owner firstfailure. Newsource-onlycapture
NORMAL+readonly+refinement+all9records+10Marshal PASS: verified
86e00ada7a1fbc3edfad3ebd0742170531b452a48571aeb9bef6f2dc7df26be5, original
466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5, unit
355184057d09d9623e7ebe8c30b8cec8159b9ba3390845708d66a98cfac217e2, body7
784dd0c7676ef741164f46ff194202e36e23f01ae5303382a07e39257c04c4fd. Root
independently rehashedall10files;8otherbodysha identical, ghost-strip unchanged.
Falsified assumption of unchangedtypedCFG: ghostpreprocessingunit locals/match
adds44vs42locals/27vs25blocks, forgetblock15Move33 successor16cleanup26,
assumeinitblock22Move39 successor23cleanup26. Three-hash-onlyrefresh invalid.
Rootdecision: separateprofile23 exactconditional17/19/20 metadata/local/call/
cleanupre-certification; source/runtime/spec/kernel frozen, alloldcanonical/five
paths unchanged; writtenprofilecard BEFOREextension. No partialcapturetheorem.
Coordination10 syntheticAPI/privateCloud controlsPASS, actualcommonclient used
foreignterminalreadonlyreceipt; no foreignbudgetwrite. NestedorderTEST failed
beforeheader atfullspancheck: raw MIR cols0based vsAST+1; exactBody.span and
fnSigSpan gates plusall9ASTcolumns corrected(SHA6ecf8184...), pendingnewRun.
ASTprintPROBE consolebuildfailed Unbound Args.body_name, correspondingbody
metadata resides State/bodylocalbinding;3references corrected(SHA3686a672...),
no ASTsemanticrewrite. Bothare setup/admission failuresnotproofnegatives.
Next: actualnewpointerouterfullproof+affected17/19/20controls; independent
changedTEST/AST thenlawfulactualsort4 scope/recovery. No unchanged failedrunrepeat.


NIGHT-CLOUD-6 pre-experiment and dispatch: Build
`b0382472-9685-44b3-955f-88f037d1c144`, lane `o26-wrapper-profile`.
Infra `f5a82bcdbdabcbf290f6f9f3d9be363dfe8bbf04`; proof
`debd540555206a4694250b7586c4cec70d95a727`. Config
`418d7912d846c590670e8c2d0f56179ba355c3d8b0fcd8a131db88a9e87aea80`,
source input `a37053c6e92c6b985e8a65bdf099a1f2120af122c212aa7f3bb9ae35b2a09a80`,
token `dispatch-344fe23e8b2f46d4ac5284b95dafc839`. Timeout1200, reserve1260.
The shared lock reconciled foreign terminal Build b34c2f3c to a receipt
without charging or modifying its owner's ledger. Previous foreign-active
submission refusal cost0s and created no Build.

Cards: `overnight-assume-actual/CLOUD-WRAPPER-REBASE-PROFILE-CARD.md` and
`cloud-build/night-select-sort4/WRAPPER-REBASE-PROFILE-CARD.md`. Hypothesis:
existing checked ghost lemmas lawfully reconstruct both canonical wrapper
owners from their current cells, allowing the final actual intrinsic and
assume_init under the full pointer-domain normal equality/owner/thread post
and false unwind post. The actual generic nested Drop full normal/unwind
optional-owner/thread posts remain unchanged. Experimental component23
recertifies the exact observed44-local/27-block graph; it changes translator
admission metadata, not the kernel/spec/std runtime. The canonical profile
and actual seven same-version prefix callees are checked before the candidate.

Controls: unchanged canonical source with flag off must reproduce the462
owner blocker; changed source without opt-in must refuse at17 sourceSHA.
Four source/MIR owner mutations must refuse first at17's intended SHA gates.
A separately rebuilt two-hash TEST must admit synthetic owner17 then reject
selected-wrapper Move-to-Copy at20 before any proof header. Full tool/spec/
kernel/parser/exporter/refiner/stock-binary and source snapshots must match
after all stages. Baseline and candidate outcomes remain separate.

Outcome mapping: positive full outer and nested return/leak completion enables
remaining changed-profile controls before any admissibility claim; a new
resource failure drives source-grounded ghost repair; a source/graph/setup
refusal is inconclusive and requires exact correction with a fresh Run.
Collector success does not prove the function; accepted remainsfalse in this
experimental lane. No historic A/B/C or unrelated matrix is repeated.


NIGHT-CLOUD-6 outcome: Build b0382472-9685-44b3-955f-88f037d1c144 FAILURE,
03:43:02.609532970–03:49:09.958351 UTC;368 conservative seconds. Own
2004/10800 used,8796 remaining/no active Build. Full archive
`baa28829915a2d1ecfb101b5fad0eb7c5c02d266d9d039dca7f7e590fb0fd2b6`,
text index `0250be132778ea4b1b2b52c97ced34f46085f9c81babd19148d9c4992be14ad3`,
config/inventory/original Git closure/publication hashes verified. Publisher
run_exit0/evidence_complete=true/diagnostic=false/verification=false.

Canonical paired capture and proof reproduce the462 owner barrier. Separate
component23 console builds and fresh wrapper source/MIR/refinement/all10
Marshal plus exact graph pin checks pass. Positive translator emits all
17/18/19/20 admission markers, then ghost parser refuses the second assertion
at verified/lib.rs178:5–11. There is **no function verification header** in
the positive log. Therefore no seven-prefix or actual outer/nested proof is
credited for this changed source, despite successful frontend admission.

All four component17 source/unit-hash negatives first fail at the intended
certificate obligations. Independent A1 TEST17 observed two-hash delta first
allows owner17 and refuses at20's selected-wrapper Move requirement, no body
header. Off-canonical same first462 and off-rebase old source-pin refusal
pass. Complete production/profile source/spec/kernel/parser/exporter/refiner/
stock binary snapshots remain equal after all stages. No component19 TEST
run yet; its separate hook is ready, not accepted.

New evidence requires stock-parser-compatible source ghost commands, with
old-wrapper binding scope preserved. This changes source identities and may
change CFG; obtain fresh paired capture and full nine-body inventory before
new exact pins. No parser extension or weakening is justified. The next
bounded recovery lane also checks the three previously corrected independent
TEST/PROBEs. No unchanged failed positive is rerun.


NIGHT-CLOUD-7 pre-experiment and dispatch: Build 293435cf-8457-42ea-97a0-b37589f4fa76,
lane `o26-recovery-tests`; infra `8d299748b14c3d5b567d935f96ec75e357dfe650`,
proof `96289411a12da79ed4a410a882be5c856952b546`, config `cf796e9b8c49abce9fbb9c98a567eb095cc5de5369309ce73cda6f6382d1a440`,
source input `758a0dae42e7bf0b87dfbed27ae2d7f366ab08eb157f08456210969eceddcc9e`, token `dispatch-1122178b105743ec86c0f26eb5dc5dc4`.
Timeout1200/reserve1260; own2004 used/8796 remaining before reservation.
Shared lock reconciles foreign terminal a3553e9e by read-only receipt and
grants the ready select request; no foreign ledger/state or budget change.

Cards: RECOVERY-TESTS-CARD and EXACT-INFRA-TRANSPORT-CARD plus separate
nested/AST/mapped-ID/source-only cards. Fresh wrapper syntax uses ten
single-statement ghost comments with unchanged ordered operations/runtime/
posts; capture must produce new exact hashes and complete graph before pins.
Old component23 is disabled. Separate corrected nested proof scheduling,
print-only actualsort4 AST and strictCUT mapped-ID relocation retain full
source/MIR/refinement and all original resource checks. None is accepted.

Previous combined legacy-policy payload617750B was refused in local Git-
object transport preflight, no reservation/Build and0s. Opt-in exact policy
selects all reviewed scenario dependencies and original selected object
closures: committed payload570901B fits the unchanged bound. Five Cloud
transport negatives target exact missing/extra/mode/hash/object obligations;
canonical restored inputs stay untouched. Stock/constructor/unmarked policy
unchanged; no A/B/C replay or separate smoke. Shared interface84e61f58 was
published with atomic HANDOFF before proof completion.

Outcome: new fingerprints/graph drive explicit profile recertification;
actual nested first resource failure drives lawful ghost repair; AST label/
scope evidence drives bounded scope TEST only; changed relocation failure
localizes the lifetime obligation. Setup/wrong-negative/timeout remains
inconclusive; full artifacts and baseline/test verdict separation required.


NIGHT-CLOUD-7 outcome: Build293435cf-8457-42ea-97a0-b37589f4fa76 FAILURE,
04:08:51.805650851–04:14:52.739756 UTC;361 conservative seconds.
Own2365/10800 used,8435 remaining; no active own Build. Full archive
`13b4fbe0054c2d6e29fc0fbec9476494a4136b2d6f0288cec089856e96625d89`,
text index `74394e052bc5a5aa5e9a877e0d228192a64e605b38b2a1853b2db20d92dc1676`;
publication/config/inventory/original Git closure verified. run_exit0,
evidence_complete=true, diagnostic_complete=false, verification_accepted=false.
Exact infra transport restoration plus five intended pathset/mode/hash/blob
negative refusals PASS; no general proof/profile acceptance follows.

Canonical O26 paired source/MIR/refinement/all9+10 and same first462 PASS.
Fresh one-statement source candidate captures source11067f06ba7c745cfb221a559fb29778eba8d7b6e65f6db1a814ff7ce72bdfd4,
unit9c63ec19fcbc7f6c6e1b336b59c5af2bab470bd1b17c0345f0a57ac777a7cb00,
body7 00fafebcaf338797daa681da8f4631be56a98d285fd945e76dfd7725b162a286;
other8 body hashes and original466882d7 unchanged. Root rehashed all10 records.
Observed graph52 locals/35 blocks,2 SAVE_OLD and8 REBASE_BOTH ghost calls,
18 cleanup predecessors drives R2 exact certificates; old pins do not transfer.
Capture only; no changed-source actual outer proof yet.

Separate nested-order TEST builds, admits exact unchanged nine AST declarations
with one checked permutation, and proves actual generic nested Drop body165–170:
checked generic drop call169, normal return/leak170 and unwind return/leak170.
Seven actual prefix bodies pass first; outer still fails462. This is actual-body
TEST evidence only; reordered profile not admitted or combined with R2 yet.
Print-only sort4 PROBE captures whole Func AST89699B/dc7e8487ae46470ebcb9f964cb158c44d9bf75042cffa79d465f4d7e67001d39,
exact source/paired complete MIR/refinement; default-off first185 unchanged.
Observed cmp lifetime child root138, reserved markers22, callback switch32,
normal debt close33, lifetime end34, recover35/join36, original goto54/return.
Type/operand/chunk details remain unobserved; follow-up print-only PROBE required.
Mapped-ID relocation fails translator7030 compilation: local record inferred
var_id_trs_entry instead of Mir.local_decl. Setup failure earns no negative.
Explicit record type annotation changes no relocation selection/resource rule;
fresh Cloud rerun needed. No local verifier/compiler/test was run.


NIGHT-CLOUD-8 pre-experiment/dispatch:218568df-ca79-43c5-a758-44764f1bac5c,
lane o26-wrapper-controls, infra77238833cd1dc0f558d0c3798a1e383228d51447,
proof00ccde64680e53236ca29c17f035cade2cb9f791,
configf4046d5a239a323ac5e6bafa78abe29f21b29a382f6d99aac1e431a7fedd46ff,
source input187e189343ab42508fafc8b3f44b0d0c7c2be46a37384d462d8176f6876d30d8,
token dispatch-1754b98a495f440ab676cc9cce5426bd. Timeout1200/reserve1260,
own2365 used/8435 remaining before reservation. Common lock reconciles foreign
74227266 terminal read-only, then dispatches own ready request; no foreign charge.

R2 cards record exact observed source/normal/readonly/nine+10 inventory52/35,
2+8 ordered ghost sites and18 cleanup predecessors. Hypothesis: source-only
symmetric wrapper rebase closes missing462 indexed pointer owners without any
Element permissions or changed runtime. Component23R2 is distinct NOT_ACCEPTED
profile; kernel/parser/spec/frozen20 and default-off branches unchanged. Actual
outer diagnostic T=*const Element normal thread+selected result+raw_ptr_own,
false unwind; generic nested Drop posts preserve storage/field/padding both
outcomes. Seven actual prefix callees, nested header and full proof exit remain
separate observations. Generic/ZST whole-helper target is not closed by this.
Four owner17 source/unit controls, independent A1 Move(_47)/Copy(_47) and
component19 SAFE forget Move(_34)/Copy(_34) must fail at exact expected gates;
production/tool/source identities must remain equal. Positive success enables
new combined-profile controls/scheduling review before acceptance; substantive
failure drives lawful repair; setup/wrong control/timeout is inconclusive.

Original combined recipe at infraeb2e209d/proof00ccde64 payload606345B exceeds
unchanged transport bound, rejected locally before reserve/Build/0s. Split retains
complete committed inputs and original Git closure separately. R2 payload511544B,
171 parts. Changed AST and mapped-ID recovery recipe512e0b19 remains a later
independent slot; no unchanged nested/source-only/coordination stages repeated.


NIGHT-CLOUD-8 outcome:218568df-ca79-43c5-a758-44764f1bac5c SUCCESS diagnostic,
04:37:23.014533561–04:43:45.847774 UTC,383 conservative seconds;2748/10800,
8052 remaining. Fullarchive f87639b62f606c21053dfbb5474e78433f8e05ef05ead32ab432cc31afa8f457,
textindex48a6bae22057dac4dedeadf0e1323a8fa4ee5544474c788db104f40b911c5950;
publication/config/inventory/originalGitclosure verified. diagnostic=true,
run_exit0/evidence_complete=true/verification=false; positive actual proof exit1.
R2 source/typed52/35/2+8/18 admission, NORMAL/readonly/refinement/all9+10 and
unchanged eight canonical bodies PASS. Full positive log proves seven prefix
callees, executes both ownership rebase closes236–237, selected-wrapper
intrinsic241 and checkedassume_init241, reaches normal return243/free_locals/
thread token consumption. Old stdspec462 missing owner is absent. FIRST error
verified/lib.rs143:45–47 pure post: cannot prove result6 equals condition-selected
original input. No full outer normal/unwind/leak theorem, and nested body not
reached in R2. A source-only checked input/payload/wrapper equality diagnostic
is the next hypothesis; assertions are obligations, never assumptions.
All four owner17 negatives first refuse at intended exactsource/unit gates with
zero function headers. Independent A1 negative reaches exact Move requirement;
component19 negative reaches exact forget argument plainMove requirement, both
zero body headers and correct shadow-only two-hash delta. Full logs inspected.
Offcanonical same462/offR2 old17refusal, production/profile/kernel/parser/spec/
schema/exporter/refiner/stockbinary identities unchanged. R2 NOT_ACCEPTED.

NIGHT-CLOUD-9 pre-experiment/dispatch:bf77d8a1-cda1-4426-9fc9-1a0f119e926f,
laneo26-recovery-tests; infra512e0b19989f821b923124dea9b403477c90e474,
proof00ccde64680e53236ca29c17f035cade2cb9f791,
config77871f4871f27bc7c4c10ad03a59817f315721790cea63895e36f8cdda82f999,
source input5e99795b4dce986d29ce7bae6090e6c5f9f54b32eb4aa792205f7f26930872d2,
tokendispatch-129c04f5416347c48afa615703203d04. Timeout1200/reserve1260;
own2748 used/8052 remaining before reservation. Complete exact transport
payload558131B/187parts. Cards retain strictCUTfreeze,6raw/translated matching
with explicitMir.local_decl annotation (compilefixonly) and print-only AST
R2descriptor extension with unchanged fullFunc snapshotdc7e8487. Hypotheses:
relocation proceeds to its actual strict lifetime obligation, AST captures exact
localdeclaration/Close/call/free metadata without altering AST/stock first185.
Each has separate raw proof/diagnostic verdict; acceptedfalse. Unchanged nested,
coordination and source-wrapper stages absent. Next decision uses actual observed
scope/operand metadata or first substantive relocationblocker; setup is inconclusive.

NIGHT-CLOUD-9 outcome: Build `bf77d8a1-cda1-4426-9fc9-1a0f119e926f`
**SUCCESS, diagnostic only**, 04:51:07.810619030–04:57:00.963114 UTC;
354 conservative seconds charged, own account **3102/10800**, 7698 remaining,
no active Build. Exact infrastructure `512e0b19989f821b923124dea9b403477c90e474`,
proof `00ccde64680e53236ca29c17f035cade2cb9f791`, config SHA-256
`77871f4871f27bc7c4c10ad03a59817f315721790cea63895e36f8cdda82f999`.
Full archive SHA-256 `990877254380a79c5a0612ca8aa6bb42b9245bfe8515b1c42e1113b9089f9883`,
text index `365f17f57d63950593f4b844d4656a20f9fafab7fb124bb298f6c48a862bb7e0`;
publication, original Git-object closure and complete archive verified.
Runner exit0, `diagnostic_complete=true`, `verification_accepted=false`.

The isolated mapped-ID strict CUT TEST retains the unmodified baseline's first
`verified/lib.rs(84,9-38)` lifetime-inference refusal, verifies the six matched
raw/translated local declarations and exactly one moved inner binding, and
preserves exact source pair, paired NORMAL/readonly MIR and refinement exit0.
The changed translated-ID patch compiles. Relocated fixture verification exits0
with **0 errors, 95 statements and 20 leak checks**; the full log contains
both normal and unwind return/leak paths. Its source/MIR hashes and production
tool/spec identities are recorded, and the isolated relocation changes only
its translator relative to the strict CUT baseline. This is a fixture result,
not a validated change to production lifetime semantics or actual sort4.
All-path liveness, alias/address escape, heap/bound retention, source/MIR
mutation negatives, combined S6/no-CUT regression and actual-sort4 admission
remain OPEN; no direct actual-sort4 unwind result follows from this VF0.

The independent print-only AST PROBE observes all seven requested R2 metadata
groups: root local declarations, comparison `typeid` declaration and block-free
metadata, first FnMut operands, local assignment descriptors, normal debt close
and recovery call. Complete function snapshot SHA-256
`dc7e8487ae46470ebcb9f964cb158c44d9bf75042cffa79d465f4d7e67001d39`
is unchanged. The first callback is inside the unique comparison block
`root[138]`, with switch `root[138]/block[32]`, returning arm 0 and unwinding
arm 1. Probe-on and probe-off retain the same stock first error at
`verified/lib.rs(185,13-36)`: missing `__vf_sort4_first_unwind`; neither
verifier execution exits0. This observation does not establish direct unwind,
resource recovery, actual sort4 safety or accepted frontend semantics.

NIGHT-CLOUD-9 resolves the prior translator record-type setup failure and
the missing AST-detail observation. Next decisions: source-only checked
input/payload/wrapper relation capture for the separate R2 actual-helper
identity blocker at line143 (fresh hashes/graph before any R3 admission), and
a separately reviewed strict CUT negative matrix before any semantic adoption.
No unchanged nested/coordination/source-wrapper stages or local verifier run.

NIGHT-CLOUD-10 pre-experiment/dispatch: f9617843-c38b-4a64-91da-86d65548d40c,
lane o26-input-relation-capture, infra eac773eadb46b72dd3af99656739aaeb164a5ed0,
proof d253128ac42f5788cc322201bdfcc6c1e2e36f76,
config f89c2050de008d57afc89acaaf5bd0df77ae611ba1f17186153a9a5d9cb55ff8,
source input 7cc56715768ab852269d59bfb14a8617b59828e538769b28e83779641bfe72e4,
token dispatch-d454b092f5c44e4397d56aec84ba1454. Timeout1200/reserve1260;
own3102 used/7698 remaining before reservation. Complete original Git transport
payload474405B/159parts. New9 checked ghost commands in3 byte-reversible
regions retain runtime/fullposts and introduce no assumptions/resources.
Two bindings inline preserve nested Drop spans; eight unchanged body hashes
are predictions until observed. This run captures fresh source/MIR/refinement/
nine bodies/ten Marshal records only. Fingerprint collector refusal is observed
separately from predicted oldowner17 refusal; no actual proof is requested.
Fresh evidence permits explicit R3 pin/graph review; mismatch/setup/refinement
failure is inconclusive and permits only evidence-based repair.

NIGHT-CLOUD-10 outcome: f9617843 FAILURE/run_exit1,05:22:26.894056453–
05:25:24.621011UTC=178s; own3280 used/7520remaining. Complete archive
2f20a83a6d8b58a2dc874c68594f3f459644aafca5dce86bb883824d7e10c5ff
and textindexd7f0e9c87cdc14affb5b631e64c870e983824bfd4dc1b43f3d9dd08559a358e9
verified. Published evidence incomplete for requested scenario: missingcases,
refresh21 patch FileNotFoundError before candidate proof/capture. This is setup,
not an intended negative. Source/proof unchanged; repair infrae4e9eacfebef52293b5404c74b316fe76a413e4b
adds both baseline21/22 patches. Static complete canonical path set and
refresh manifest references checked for both newscenarios. Newpayload477962B/160parts,
b77202087a2344ed472e8762b1827d4ebcc12870b8581f8ecdf6677b3288cf59.

NIGHT-CLOUD-11 dispatch:84076ff3-a9bd-4fa9-bae4-ce6bc5dc6aa1,
laneo26-strict-cut-controls,infra9dc0f99a59fdfee75b8740d18160e483373f379a,
proofd253128ac42f5788cc322201bdfcc6c1e2e36f76,
configecfcc78bd5fcdc12cccf1a390898b756331553014355788d369478611befb2a2,
sourceinput742513f8eaf8a3c38871fade3932f02d7245c901668a1e36c0561fbc121fc260,
tokendispatch-98b54306c6344639a19e5dde9cf77530. Timeout1200/reserve1260;
3280used/7520remaining before reserve. Exactsource/Gitpayload515185B/173parts.
Same-Build isolated relocation FULLVF0 is prerequisite for17 matrix/off
controls. All negative stage/predicate/source locations are prospective until
full source/MIR/log review; classificationDISCOVERY_REVIEW_REQUIRED, allacceptedfalse.
False-normal/unwind, liveness/alias/heap/bounds and actualscope gates OPEN.

NIGHT-CLOUD-11 outcome:84076ff3 FAILURE,05:30:27.594882163–05:35:54.265608UTC,
327 conservative seconds; own3607used/7193remaining. run_exit0 and complete
evidence are diagnostic collector results only, diagnostic_complete=false,
verification=false. Archive b2f63f0a0096174586cd8bd9661e18557c7d74da891ef568b8ebca25886e56e0
and textindex445c471fb66ae6cceb1872a217d487d4817ceea0d205a0b153da215bbe629cd3
verified. Unchanged baseline462 and isolated relocated fixture VF0 repeated
inside the requested dependency run. Strict preflight source/tool/patch/Fbound
gates pass, then CLI KeyError classification before overlay/matrix creation.
No intended-negative credit. baf9dfb7 adds the missing preflight report field
without tool/fixture change; 9f22416a adds isolated normal/unwind false-post
controls to the first genuinely executed strict17 discovery matrix. Its
source-only Git transport preflight530397B/178parts, SHA256
ba841e72e891cd69612ddceb47f76c06bf223767327b6375bf21535c0abbac57.
Expected refusal stage/predicate/span remains prospective until full logs;
wrong-stage failures are INCONCLUSIVE, all acceptance flags stay false.

NIGHT-CLOUD-12 dispatch:93da48d0-d720-4179-8d2c-d8b7495703bf,
infra e4e9eacfebef52293b5404c74b316fe76a413e4b, proof d253128ac42f5788cc322201bdfcc6c1e2e36f76,
lane o26-input-relation-capture, config d6029fc2c39e3f3833b1b9f20a22b7cb070bccd0ff0628495a296b9e602f221a,
token dispatch-8bfd49680e934814b330aa5ccd3f5348. Same source/profile and target
as NIGHT-CLOUD-10; only missing baseline input recipe repaired. No unchanged
infrastructure smoke. Complete original-Git payload477962B/160parts verified
pre-submit. Fresh full source/MIR/refinement/nine-body capture, no proof credit.

NIGHT-CLOUD-12 outcome:93da48d0 SUCCESS/DIAGNOSTIC ONLY, create06:05:38.847973128,
start06:05:41.055016382,finish06:11:15.525771UTC=337s charged; own3944/10800,
6856remaining. All requested evidence uploaded and archive/textindex integrity
verified: archivee5c4a3a4feecf49ae6ae02ec65ef0a595ca7db815954847afe5a3b423291ec7a,
textindex0e7768f3b43e1126dd1bb7a63cea89f2d47f0ffb0ee187a1862590aee7fabc13.
WRAPPER_INPUT_RELATION_SOURCE_CAPTURE_COMPLETE, actual_helper_proved=false,
actual_nested_drop_proved=false, verification_accepted=false. Source
a95aff14592b167c62c53c7ed726128ee86c7c19768cfe613504cdec841f8463; original
466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5 unchanged;
unit407acbaea262ba908ed88434231e9fce1128678840f5d929deaad71838290a92,
body7f8374652a11e36073ad6ed10ec39b0f8de62da53265dd80d2dc2c3565491cee1.
NORMALwhole5b241f4f51d9ba7e72dd4d24cf295a95a8f64d7750867821dc70dac982609509,
readonlywholec5fe3880640143c2805697f8fb4c46f380fc62eb01f3344ee1ec606e7aadf121.
All5 export/decode/refinement stages exit0/sourceunchanged; collector exit2
at deliberate no-proof-rule snapshot refusal. Nine exact ghost commands in
three reversible regions and ten independent Marshal hashes checked; all8
other body hashes unchanged. Historical owner17 refusal remains NOT_RUN,
expected only. Full target normal/unwind/return/leak and nested Drop are open.
These observed pins permit distinct R3 admission/control development, not
source-only proof credit. Genericcapture proof8c2f3d8a/infra8a7c0c8f is separately
ready: originalGitpayload484940B, base64source163parts (172 total substitutions),
SHAeb556bf0a8b3a3eafb29b71f6914d4e49a0b4ad7aa5db922063a6d6a07b70959.
No generic ownership/callee proof, no repeated migration acceptance.

NIGHT-CLOUD-13: Build673526ac-6556-40bc-9ebe-7792e257bfcd,
infra9f22416ac13ac006f505605b57b50f37629caef1,proofd253128ac42f5788cc322201bdfcc6c1e2e36f76,
laneo26-strict-cut-false-posts,config0d3bdf60f461b0fb6eff7c55664ccd7ab094ac179f59be611c66294989e28e25,
tokendispatch-6fa7a303993f43e08337c7fd55707c92. create06:24:32.391924017,
start06:24:33.134531877,finish06:30:56.110265UTC=384s; own4328/10800,
6472remaining. FAILURE at diagnostic gate (run_exit0 != proof), evidencecomplete;
archive11ebebd82f74b42b4fd1a66cfa9959dc58bc4793629569545d35a2447c20e861
and textindex43ea695cc1298b245e59d19509e80f2ca40301b8f0fc328236da8b2751c65878
integrityverified. All17matrix cases actually executed: five support stages
exit0/refinement0 each; four enabledpositives VF0;12 negatives +one off
case have one raw refusal each. Manual full-log review attributes repeated
end_lifetime refusal to actual missing lifetime_token(cmp_k) precondition
at pinned lifetime_logic.rsspec78:9–23 and note-derived second caller
verified/lib.rs15:13–25 (first call14). Audit wrongly requires the error
itself pointtoverified source; it aborts before finalmatrixsummary. No audited
combined acceptance or actualsort4 proof; exact raw outcomes preserved.
Both false-post controls did NOT_RUN due prerequisite auditexit1. Next permitted
change is narrow callee-contract attribution auditrepair; other cases/rules
unchanged. Reuse complete verifiedmatrix evidence for affected auditreview
and new falseposts when exacttool/profile/source identities match, ratherthan
regenerating unchanged17cases.

New infrastructure95a99685da166325f13d676281cc897c41e65ffb published separately
from proof18816e160c4b76180b4e11c1bc431cb74a88b77e. OriginalGit payload preflights:
R3 lane538853B/181sourceparts,9cb6ef509f2c1f0ac26ea43b442ff56713aedf5bcccdfa0e17e7512af4de3a3f;
generic/postmark552813B/185sourceparts,41651703a25e7815d937f4161b4d3165a2116dd013b075d1e53df7d526f281f5.
Both canonical/profile/dependency path sets checked, below191sourceparts bound.
R3pendingactualcallee scheduling, independentbody7/ghostCFG targetnegatives,
fullnormal/unwind/return/leak; printcoreTEST changesonlyisolatedinstrumentation,
requireson/off185boundary and ASTidentity, no cleanup orsemanticacceptance.

NIGHT-CLOUD-14 dispatch: {"build_id": "755bf768-3700-407b-9c70-3605b4d8f4a4", "create_time": "2026-10-09T07:06:04.732807983Z", "dispatch_token": "dispatch-891ec6af6c3548319c43c7ea48ac202c", "finish_time": null, "infra_sha": "5a0a819ac782cc80a3050386614a3bcd7913627b", "lane": "o26-wrapper-r3-nested-diagnostics", "owner": "select-sort4", "phase_id": "NIGHT-SELECT-SORT4-CLOUD-2026-10-09", "proof_sha": "256254c01a77653ec056c91755ac636e9e76fb9d", "publish_text_logs": true, "reserved_seconds": 1260, "source_input_sha256": "b62338015145328176452bf8245dd38f3919d202352f973027e9ef4a90b1ddc9", "source_mode": "pinned-objects", "start_time": "2026-10-09T07:06:05.646300624Z", "status": "WORKING", "submitted_config_sha256": "b5a2f9b2aa8cb4b3d31907421ff5f2e8d43d1bba423b492d1d509cd37965b9dd", "timeout_seconds": 1200}
Separate R3 component24 first semantic run plus isolated scheduling TEST;
full canonical baseline, fresh paired source/MIR/refinement/nine-body inventory,
R3 controls and TEST evidence separately retained. Original runtime/fullposts
unchanged; TEST grants no nested/whole-helper credit. All selected paths and
parent proof dependency sets checked before client original-Git object closure
transport preflight under atomic API/reservation/submit lock. No repeated smoke.

Strict17 reuse/fresh2 next infrastructure99f4269b8f84f1b85d2092d41bd830243ae8a681,
proofd253128ac42f5788cc322201bdfcc6c1e2e36f76: all original input closure preflight
544365B/182sourceparts, SHA3cb3fd1eccf2cbc470f76930160a8e2493019a60c3f0f673a894ad08058e1ab9.
No unchanged17case execution; fresh tool/profile must equal verified673 evidence.
Historical source/MIR/log re-audit and two NEW falseposts stay separate.

Build755 pinned payload source SHA b62338015145328176452bf8245dd38f3919d202352f973027e9ef4a90b1ddc9,
186sourceparts/195total substitutions. Child nested scheduling TEST always
actual_nested_drop_credit=false; parent TEST lane actual_helper_proved forcedfalse.

NIGHT-CLOUD-14 outcome:755bf768 FAILURE, create07:06:04.732807983,
start07:06:05.646300624,finish07:11:58.852172UTC=355s conservative charged.
Own4683/10800,6117remaining,no ownactive. Full Cloud console downloaded,
SHA7d677b7748677ea3f83caf1893dbaaf32f86a0d9778845d6a4b230f90bd96ae3;
console reports R3 positive did not reach first outer boundary cleanly and nested
AST permutation certificate incomplete. Exact raw first-error/AST rows UNKNOWN:
helper did not echo raw proof logs, and packaging rejected symlink
allprooflogs/cases/wrapper-r3-profile/controls/forget_move_to_copy/test-tool/examples/usbkbd/build/usbkbd_keycodes.c.
No summary/archive/upload receipt exists; INCOMPLETE_EVIDENCE gate rightly refused.
No download-verified/negative/proof acceptance credit. Canonical baseline's
lib.rsspec462 refusal remains console-visible but is NOT the R3 candidate error.
Necessary infrastructure repair: all disposable verifier and exporter execution
copies outside evidence, raw sources/MIR/proof logs/identity deltas retained, full
proof stdout backup; packager symlink refusal unchanged. Fresh same-source run is
justified by this changed evidence component, not an unchanged semantic retry.

R3 evidence-only rerun READY:infra cbe6c439ff625b43328e304373b79465481cb94d,
proof256254c01a77653ec056c91755ac636e9e76fb9d, same compound lane.
Full original Git closure preflight556947B/187sourceparts,
SHAd1abe8f216fb173157d2171de512c5cb2b4de8f659fb2a7a2bf29b8ecdb7a2e9.
Semantic/source/runtime/posts/pins unchanged; all execution directories now
outside evidence, proof logs immediately echoed. Static AST/diff gates passed.
Foreign Builda643d1e1-48e4-4b24-bc6e-90e8c1bc11e7 takes next fair turn;
its account is separate and never charged to select.

NIGHT-CLOUD-15 dispatch:{"build_id": "03b0aa85-d825-4ccb-b5ec-b42939db7520", "dispatch_token": "dispatch-d6994e88824d455da38131fd2a06992f", "infra_sha": "cbe6c439ff625b43328e304373b79465481cb94d", "lane": "o26-wrapper-r3-nested-diagnostics", "owner": "select-sort4", "phase_id": "NIGHT-SELECT-SORT4-CLOUD-2026-10-09", "proof_sha": "256254c01a77653ec056c91755ac636e9e76fb9d", "publish_text_logs": true, "reserved_seconds": 1260, "source_input_sha256": "d1abe8f216fb173157d2171de512c5cb2b4de8f659fb2a7a2bf29b8ecdb7a2e9", "source_mode": "pinned-objects", "status": "QUEUED", "submitted_config_sha256": "674c80c0b7a8896e40418412a6d6289e6c7dc3070be079cd1e3b5e421d0e9ee3", "timeout_seconds": 1200}
No semantic/source/post/pin changes from14; isolated execution copies outside
evidence and full proof stdout backup repaired. Freshrun requiredfor full witness.

NIGHT-CLOUD-15 outcome03b FAILURE/diagnosticincomplete,evidencecomplete:true,
create07:26:31.650355492,start07:26:32.402623330,finish07:32:17.972492UTC=347s.
Own5030/10800,5770unused,15terminal,no ownactive/requestwithdrawn.
Archive2375dcd912679550a44e0971b0c4601ee1e291b3a55a7de1f310b143f11fe904,
textindexf36378fb59b6f8fa66d041955eab7cdef22efef9b6e39d4e3c8961aa446b489b
verified. Actual R3/nestedfullrawlogs both firstFatal ghostscope inventory before
VFheaders. Exact savedlet2/nestedopen2 mismatch localized; full6control logs
independently reviewed at intended owner17source/unit,A1Move,SAFEforgetMove gates.
No actualproof/semanticadmission. Separate R3scopeTEST proof7b68fc9b,
infra2bee8747 prepared/staticchecked/NOT_RUN. Source-shadowDRAFT staysBLOCKED;
no observed latebinding failure. No new hosted run fits remaining deadline with
fullpreparation/queue/upload margin. Complete checkpoint saved; authorization
ends08UTC. All runtime library diff checks and accepted65a456b8 ancestry pass.

Final original-Git transport preflights infra2bee8747/proof7b68fc9b:
[{"bounded": true, "lane": "o26-r3-ghost-scope-test", "payload_bytes": 554457, "sha256": "3acd0e021d597d096474c86247f81fe2ee7c1f0f4b2d8eb06cfedf114b7c3b99", "source_parts": 186}, {"bounded": true, "lane": "o26-input-relation-shadow-capture", "payload_bytes": 500155, "sha256": "1820dad739f1f543e0566e5bf48de8892ab9fe81eda132b398f7154dee8158a6", "source_parts": 168}, {"bounded": false, "lane": "o26-shadow-generic-sort4-diagnostics", "payload_bytes": 582727, "sha256": "9a13219618d7cbf627f70d12e2764298a94de68071d00a2d3ababc669b0c34bb", "source_parts": 195}]
No Clouddispatch fromthese profiles; blockedsourceJSON remainsunchanged.

## DAY-SELECT-SORT4 startup / first R3 TEST — 2026-10-09 08:45:54 UTC

New owner phase/day ledger3600s, main10:45:54UTC/absolute11:15:54UTC. Clean own
worktree and remote HEAD20258b67c17d7e17ae25967488a98060969915a8 agree; no active
coordination record/requests; gh run list returned no runs. Historical5030/10800
is not reset. Read current instructions/roadmap/runbook/checkpoint/requirements/
shared handoff, actual hint select and scope cards/runner before editing.

First obligation: actual hint::select_unpredictable pointer-specialized result
identity, with two saved inputs preserved in outer and original nested opens
transferred to actual nested Drop. Hypothesis: exact R3 let2+open2 routing mismatch
alone explains prior pre-header refusal; TEST can cross it without source/MIR/
post/resource/kernel/spec/exporter/refiner delta. Domain T=*const Element only,
no pointee ownership; full normal selected-input identity/current value ownership
and pointer-unwind-false target retained; generic normal selected current T.own /
unwind cleanup consumes both inputs remains open. Off must repeat exact inventory
Fatal pre-header exit2, partial must reject exact opt-in pre-header exit2, on must
emit scope marker once and retain full log; next binding/type failure may justify
shadow source, otherwise inspect nearest proof resource obligation. Setup is
inconclusive, not intended negative. Profile experimental R3 ghost-scope TEST,
proof7b68fc9b36b0341210d48b857b010caea7344e9e / baseinfra2bee8747b2aa5f73f120989e2fb1de6a2d9d6791;
TEST translator ed8ee5ed8a7f8abb7d9c7cee3a978059b55c0a02e34f908170a80d6cc3ed4102.

Orchestration self-review: old control rejects every ledger after08UTC and
requires local control bytes equal infra. Register exact day phase/owner3600s/
absolute deadline while preserving night cutoff and all coordination/transport/
per-build gates. Hence actual submitted infra is a published descendant rather
than literal2bee8747; every prepared semantic/proof/runner input stays unchanged.
No verifier semantics changed by phase registration; static AST/diff/payload review
before submit. First timeout1200+60queue fits account/calendar with checkpoint reserve.

First day dispatch Build5c8cd72b-2e5d-4927-a9e3-72a885cfb309, create08:52:59.469643243UTC,
start08:53:00.294273213UTC; infra6eb1da5b5c3962c356ebd9a658c06decaeaa023d,
proof7b68fc9b36b0341210d48b857b010caea7344e9e, timeout1200/envelope1260.
Payload554581B/186parts SHAa30ec9f8b49cfc5a7b2de173bfeeaaa4dfda7081c6391e467dfc592f974e0bf6;
config6317aca779bdda898bbc58cbcabe6e1007d60cd9848dacbf41a73b3ee0d46d57.
Published remote SHA confirmed; no duplicate dispatch. Actual proof/profile/runner
files have zero diff from prepared2bee8747; source-input preflight validates recipe
sorted paths/closure/modes/OIDs. Build is WORKING; no result credit yet.

First day R3 setup failure: exact original-object restoration succeeded, then
exact-infra-transport-controls.py:189 refused `reviewed transitive Cloud runner
dependency absent from recipe`. Static literal REQUIRED comparison isolates only
recipes/o26-r3-ghost-scope-test.json itself: transport already includes that committed
object automatically, but the reviewed minimum expects it explicitly in infra_paths.
Minimal fix adds the exact recipe self-path to its sorted list, preserving all input
files and verifier/proof/profile semantics. No preflight guard disabled; recipe
bytes/infra SHA/payload change; same proof7b68fc9b. Before next submission review
entire REQUIRED, schema/entrypoint/path lists and unchanged dynamic runner chain.
The first setup failure is not a negative and reached no verifier header.

Setup Build5c8cd72b terminalFAILURE finish08:54:26.310751UTC; conservative87s,
newaccount87/3600,3513remaining. Archive79022eeef76db914c4c2463f2e011970813acd64ad1fa9df11c2a3442d6ceabf,
textindexbab4a642ef32a2329f193eae1d2c63d958fc7ab3777e8fc585eac5dc46b6489a
verified (full archive and index; no independent text chunk download). Archive
captures full setup failure; proof evidence_complete=false and no proof credit.
Recipe fix published infra574484e7cff6c53a15ff7e76b3aec133f6c87ef2,
payload554599B/186parts SHA657f087857cc328bcdddbe79cbb4c29b544ada364c528b0aced06c852cc039f3.
Static42Python/7JSON/5shell syntax and every reviewed dependency/path gate pass.
Next submit refused before reservation because ownermerge Build3c26cfa6-5263-4287-9f1c-fe1a13068ef2
is WORKING. Own ready request remains registered; no new own Build,0extracharge,
foreign account/worktree unchanged. Continue through existing atomic client after
that run reaches terminal state. No shadow source experiment authorized by setup failure.

## Day R3 ghost-scope TEST observed — Build9bdd5622

Build9bdd5622-7000-483f-8e83-e9847412ddba SUCCESS for diagnostic only,
create09:07:18.632667678/start09:07:19.459354113/finish09:12:58.818151UTC;
341conservative seconds (340execution), new428/3600used/3172remaining.
Infra574484e7cff6c53a15ff7e76b3aec133f6c87ef2, proof7b68fc9b36b0341210d48b857b010caea7344e9e;
configc294829ba90c0fde1d9a896914229d28677000656d3df26c4f1082b0890b0dcc,
payload657f087857cc328bcdddbe79cbb4c29b544ada364c528b0aced06c852cc039f3,
actual186sourceparts/3990max/195allsubstitutions. No source/profile/runtime post change.

Off exact inventory Fatalexit2preheaders, partial exact TEST opt-in Fatalexit2preheaders,
on emits `R3-GHOST-SCOPE-TEST: retained two input lets; nested opens transferred`
once and clears prior inventory mismatch. FIRST enabled failure is instead
`SORT4-AS-MUT-PTR: certificate mismatch: actual external receiver operand/binding`,
translate_fn_call_rexpr3714, still before ANYproof function header. Two constructor
redirects occur before this receiver refusal. This is a frontend/certificate setup
boundary, not an intended proof negative, pointer relation failure or shadow binding
failure. Do NOT activate shadow draft. Scope routing diagnostic complete; profile
admissibility/source/open mutation controls and fullactual outer/nested proof OPEN.
Next: exact typed R3 receiver/binding inspection and isolated default-off receiver
recertification TEST preserving old gate, observed source/unit/body/domain, checked
as_mut_ptr body and memory/provenance/borrow contracts; affected gate negatives.
Complete archive download remains pending here; collector alone is not proof credit.

Full scope archive022c270e720db480f9e9bef027bd6cda787a99395217b1e30b8ad7dbb4350c66 and textindex63de8b090cca213b5f3709da2267711f0c48f571061f3c5976be54c8eaac5996 verified on VPS. Full logs extracted for reading; no independent text chunk download needed because complete archive checked. Enabled log has no VF headers; setup gate above is confirmed.

## DAY select-sort4 — R3 NORMAL receiver TEST dispatched 2026-10-09

Observed Build9bdd first AS-MUT-PTR receiver refusal is explained by exact NORMAL
Move(_11)/Move(_13) from wrappers _6/_8 vs frozen _9/_11 (READONLY ghost-let removal).
Preimplementation card committed7c3e5cbc; isolated TEST patch284a135f0c43c0ef50a7d48cd5bc6e294415e0168fa9e11a9238c0ab9c0c6c09,
parented8ee5ed8a7f8abb7d9c7cee3a978059b55c0a02e34f908170a80d6cc3ed4102,
newtranslator7451dee6edcd63a4151eb45816a882f51107c7f096b047762cc482b154f61fd6.
Full runtime/posts/source/kernel/spec/exporter/refiner unchanged. Exact scope/R3/nine
opt-ins, defaultoff frozen receivers, partial refusal and wrong first/second checker-ID
fault injections. These are mapping diagnostics, not malformed-place soundness proof;
acceptance/whole-function fields false. Main/static review corrected OCaml let scope,
R3+scope env propagation, timeout refusal, snapshot key sets, marker order/log-binary
hashes and failclosed aggregate. Existing scope lane explicit receiver entrypoint
enables1; base scope launcher remains default0.

Buildb4e9a631-e8bf-4b9a-a86d-6fcb920da4a9, infra/proof
b6a45161cdf7309b10f0198a1bbd1f43c225d715, timeout900+60, payload555348bytes/186parts
SHA01e703f3d812540d796ef4a77882214014a9255239ef454cd93c4e93d6c8201e.
Config125e739a38abf029764a250ff3c835d3003b6d5ca0ebd034b303f9d0d7d2f0fb.
Outcome pending; no source-shadow activation absent actual late-binding evidence.
Next candidate same-source scheduling requires fresh receiver-parent pins and complete
AST-node inventory; generic nested body only calls same-unit prefix generic-drop,
no dependency on outer. No old preheader failure grants nested credit.

### R3 receiver result — 2026-10-09 09:49UTC

Buildb4e9a631-e8bf-4b9a-a86d-6fcb920da4a9 terminalSUCCESS: create09:40:46.802719669,
start09:40:47.545930907,finish09:47:29.689782UTC;403conservative seconds.
Collector and receiver diagnostic complete; verification_accepted/actual-source/
whole-function false. Off repeats exact AS-MUT-PTR receiver refusal; partial exact
opt-in refusal; on markers_11 then_13; wrongfirst/second isolate intended receiver
predicate (second after one positive marker). Parent/source/tool snapshots unchanged
except translator/bin-verifast in each isolated copy. Positiveconsole
291d498652c00a1f357cf039f14551bbca96bcb25406b95622fe5963718853bd.
All7same-version prefix bodies through normal returns/leaks; generic drop also unwind
return/leak. Full on log518lines; actualouter header135, firsterror155:9-25
Declaration hides existing local variable saved_true_input. Not a postcondition
negative and not late shadow binding; nested not reached. Investigate first saved
let scope/execution duplication; source-shadow staysBLOCKED. Independent scheduling
of actual nested before failedouter is now source-linked justified, not circular.

Fullarchivea3b6e79c2a5a7eba8ab269b689b6698c56f2d6c5a421d92fd0cd77c41905afa5,
textindex863c21d23ebb8a6894166e53c5288c96ba61b76f20459a03e83bfe371f7c0ff1
integrityverified. Day831/3600,2769remaining, no own active.

### First causal analysis — same-line ghost lookup, not source duplication

Read of baseline TrBody ghostcommand arm confirms List.find matches line only and
does not consume list. Both MIR ghost calls are155, first0..31/dest_4/target1,
second72..103/dest_5/target2. One-based call spans1..32/73..104; parser annotations
start1 and41/end41 and83. Thus secondcommand selects firstsavedlet again. The R2
input_saved_ghosts body_text reconstruction is only admission checking, not executable
AST insertion; dropping MIR let2 is rejected because it would remove active bindings.
New preimplementation cardd39b01ad defines isolated source-pinned COLUMN mapping,
all bindings/posts retained, fresh affected fault controls, then independent exact
AST scheduling to verify actual generic nested Drop before outer. Scheduler only
uses a completed COLUMN-on parent; receiver-parent alternative is not implemented.
No late242-244 shadow failure observed, source-shadow remainsBLOCKED.

### 10:27 UTC — bounded COLUMN + nested candidate ready

Infra/proof8bf37946451829978451731a77f622144826ae11, scope lane, explicit COLUMN
entrypoint and receiver/scope parents. Original062d static payload576640/193parts
NOT_READY; never submitted. Reviewed selection removes only eight historical
documents from delivery, retaining all runtime closure, REQUIRED scope card and
new semantic cards. Actual563721bytes/189parts, source-inputSHA
9818cb226242b80d129644da3dddfa943a2740aa154cac914f6b089b857e744a.
Timeout900+60queue reserve, no new budget charge. Shared global gate correctly
refused submit while foreign merge9ed49fda active; own ready request retained.
No duplicate/uncertain own submit, old account and foreign ledger untouched.

10:30UTC: shared slot released and exact candidate Build5a3d3312-3a9e-4bad-9488-714ad62b48be submitted,
config6b7cc4f27bf9d5df12817375e0ddca277ab25b9ddf5fb53ab19ce73b2b9d9341.
Actual submitted flags189parts, max3990; no proof credit until full evidence reviewed.

### 10:40 UTC — COLUMN preparation audit filename failure

Build5a3d3312 terminalFAILURE,442s (day1273/3600,2327left). Fullarchive
45109f1ded3fc05ed7b0354ab09f4821e541d9bf9ad17555afca303f8880f2c6 and
textindex9c99381605ec2a1d526c8961ab56e0e5255e0e0aa214e384cb81c0aba7ea4f66 verified.
COLUMN tool and isolated fault copies built; COLUMN-off repeated exact old155 hide.
Helper then hashes missing inner/on-console-build.log, but build_copy emits log
under a.evidence root. COLUMN-on/nested not run; not intended theorem negative.
Minimal audit-only fix uses outer evidence root and maps nested off/partial/on
to their actual shared nested-on build log, fault to own build log. All affected
preparation paths reviewed before one addressed completion check. No semantic/
source/post/resource/check/packager changes; same translator/patch profile pins.

10:55UTC: one addressed completing Buildb23ab12e-fecf-4a0c-ad99-191b24c057d6,
infra/proofbfdb776bcebfd51a0829bf4451869f8b6dee6529, scope lane, actual189parts.
Payloadbc05a87ee325454c436d34337e9d6787153aaecce890ef467519e0ea7bde7abf,
config12e3de6df5ed6b8c9eb7bee3a3eb139b2029c49fb69cc7aa9f0408d45f34ddb6.
Timeout720+60 queue after fair shared-turn wait; unchanged target/control scope,
no semantic patch change. Main deadline completion extension only. After terminal
evidence/checkpoint stop; no additional dispatch in this session.

### Final daytime evidence — b23, checkpoint

Buildb23ab12e-fecf-4a0c-ad99-191b24c057d6 FAILURE461s, infra/proofbfdb776b
(full pins/result COLUMN-RESULT.json), actual189parts. All evidence/archive/textindex
integrity verified. COLUMN-on exact two route markers, first payload assertions
183/184 pass; firstouter prooferror240 current-wrapper/pure input equality, BEFORE
late shadow242–244; no outer return/leak and no nested body. Wrong-first intended
ordered-route refusal exit2 before receiver marker/header; immutable source/unit
and gates active. Helper expected later receiver marker, incorrectly aggregate
INCONCLUSIVE. Wrongsecond/missingcandidate/nested not executed.

Audit-only temporal correctionc0436cd5e964c91424f7bf0f648e65d7801120a1 NOT_RUN:
exactfatal+exit2+scope+noheaders/receiver+routecount0/1 retained/strengthened.
No additional Cloud check after one addressed finishing run. Day1734/3600,1866
unused,5terminal, no ownactive/unresolved, readyrequestwithdrawn. Scope/receiver/
COLUMN conditional component evidence, frontendprofiles/admissibility unaccepted;
wholeactualselect/nested/genericT/ZST/sort4 functionaltheorems OPEN.
Remote concurrently advanced290c299d->e4224b0f via externalCI PR2/two-slot merge;
preserved without forcepush by ordinary merge. All own experiments used earlier
one-slot dispatcher pins, no experiment with external change. Final checkpoint
head is documentation/integration only, not verifiedproofSHA. Stop until new task.


### AFTERNOON phase, corrected COLUMN and actual nested Drop — 2026-10-09

New account3600, start11:20:06UTC/14:20:06MSK, main13:20:06UTC/16:20:06MSK,
absolute13:50:06UTC/16:50:06MSK. Closed DAY1734/3600 untouched. PR2 present;
merge-owner dispatcherregressiona0f40e03 18/18PASS, no duplicate charge.
Infra02dad/c043 pair193parts NOT_READY. Coalesced infra=proof02dad7a520318295574a9e6199bf6a1d69476110 has190parts, all74proofpaths exactc043
blobs; sourcepayload559476f72f31715c5c5e7fe3817066f46f576c91ec2d44a044a9758191cca791.
Build1e75b8ec-5f8e-4647-9e41-898a7da35dc7 FAILURE478conservative seconds,
11:40:41.366571795Z->11:48:38.504160Z, timeout900. Config3cbb77237ed22656c20552ca3ad2f7322334c535efd0cb6599ffbfb3985ca5e7.
Fullarchive24a3343977a87e2f39daf80844172ef9b6b88b04bcfedb963ced8ca152b4e6b8,
textindex5969bacb33f61e90963f324042b96fec2b3c62e176acbbdd16d91cf4ed8253ab,
integrity complete. COLUMN6cases and nested4cases execute; source/tool/profile pins
unchanged from DAY card. Three early negatives exactfatal+exit2+scope/no receiver/
noheaders, route0/1/0. Nestedon full9body AST permutation,3signatures invariant,
actual nested Drop two normal/unwind completions return/leak/lifetime/free-locals,
then outer240 failure. The original nested-body-evidence flagfalse counts outer
prototype leak (3ratherthan2), not nested failure. Wrongpermutation intentionally
refuses combined key/multiset gate; helper incorrectly expected shape-construction
fatal. Audit-only attribution/oracle fix prepared; collector verdict preserved.
Per-case observations and correction rationale in afternoon phase. No rerun of
unchanged matrix solely for audit bookkeeping; component evidence conditional.
Line240 reason: selected payload existentially hidden by GuardOwn and forgotten
by same-index own contract, while unselected pointer-drop preserves exactvalue.
Source-shadow not evidenced. Separate reviewed THREADONLYFRAME sourcecapture
candidate being prepared; no snapshot substitution or assumed exact-value post.
478/3600 charged,3122remain, no own active. Wholeactualselect/generic/sort4 open.

## 2026-10-09 AFTERNOON FRAME source-only capture

Build4077ed0a-75ba-4f2b-9ada-1e20a036098d SUCCESS,290conservative seconds;
infra=proof70e5dfa3917a36620b0ac6a1734a677f97332db4,laneo26-input-relation-frame-capture,
actual165parts, full archive6791b8894d9832f6d2f8e78acaf41b098cfde2b8e44c5e31d2d7c7b0cd22c64c
and textindex282dae5b02d2aded9a89cf24db6e88082d607f7c4c1e3ba86e0790b6e7ec7a2b
verified. Source8543e99940897e3289f9f57fe3edc30fa4cffbba713b68aab36eb49d3faac816,
original466882d7 unchanged, unitdd53398bd088a3eff17985ad1f0069398ce5b87acf295b2345828c568f1d01f0.
Complete NORMAL/readonly9body export/decode/refinement and10Marshal diagnostic
snapshots, NOT a proof. Only helpercontract/body6+outerghost/body7 differ;
actualnestedbody8 unchangede0508d6c. Source FRAME keeps selectedcell concrete,
thread-only same-runtime forget. Full observedpins and typed56local/39block/18cleanup
certificate recorded in O26-R3-FRAME-TEST.json before enabling experimentalrule.
Phase768/3600; oldaccountsuntouched.

## 2026-10-09 AFTERNOON exact FRAME TEST

Build6ad52849-ff34-43f4-bd4a-49b810d52d45 terminal FAILURE351s, infra=proof
4ab4d568a852c0848a9160a53f90df103b4e789a, laneo26-input-relation-frame-test,
actual186parts/payload053dbdbb4184172718814999075cc323339bc2d89cee35b6a593ff7aab3df28a.
Fullarchive61bb5e45d531251f7589a17423d02b19e8da021eb754dfb690c5225db9a86746
and textindexa2dbe0e6e4c85a61117b80373db486ddf4f220e6951b1d30a8ee158fd538316d
verified. Translatora8421aac6bc2863e6df8d5ca9fc94b15251123f5203cf92d271529a595bad243;
source8543/unitdd53398b, oldR3 source off still240; FRAMEsourceoff/partial exact
preheader refusals. On prefix7/helper complete one normal return (false unwind),
actualnestedtwo normal/unwind returns/leaks/lifetime/free before outer. Outer
executes229/230 currentwrapper=input assertions on conditiontrue, then231 type
mismatch: inner(true_val) selects original *Element input rather than shadow
MaybeUninit. CapturedNORMAL/readonlydebug-name order + frozen translator binds
true_val_1/false_val_1 to actualwrappers. Newsemanticcard before three lateghost
substitutions; no runtime or fullpost/resource change. CollectorINCONCLUSIVE due
incorrect helper count2expected, actual1normal/no-unwind under existing pure
ManuallyDrop constructor. Audit-only fix prepared, not rerunning unchangedmatrix.
No fullouter/acceptedprofile/genericselect/ZST/sort4 theorem; 1119/3600 newaccount.

## AFTERNOON FRAME completion — 2026-10-09

6ad52849-ff34-43f4-bd4a-49b810d52d45, proof/infra4ab4d568a852c0848a9160a53f90df103b4e789a: conditional generic thread-only helper and actual nested normal/unwind checks before outer; current wrapper equality229/230 passes reached conditiontrue, next231 is exact input-vs-wrapper ghost binding type mismatch. FRAME-SHADOW card proposes exact3lateghost refs to observed internal wrappers, no runtime/post/resource weakening.

bb8d295e-40d1-4b6f-927d-11054739c6bf,cab9d1ca6dc2ea61a7d6338ed923601403eab537,318s: setupmissingFRAME parentJSON. Fullaffectedimport/read/collector pathclosure audited and repaired; fullarchive/textverified. 60bf2727-0ff3-4dc0-946a-555423217eb6,27d7fe6cd39dffab0da9868fc283074fc66bd3d8,335s: allsource/MIR/refinement/10snapshot stages reached; finalcollector NameError NAMES. Rawcapture manually identity-validated; archive4c67905dd95218ea6813f0f1935c72133410d363e06542faa362f75d13258671/allfiles/indexverified. Corrected classifier is audit-only, no new theorem/replay result asserted. Newsource7ec86f52b362f7f8b2ed26e3fa108212eb3d6288820bab9c6db3fa37bf8cabe0; source/profile pins inO26-R3-FRAME-SHADOW-TEST.json.

Completion-only finalproof44ea4417-876e-4a4a-bdb5-a6eea81cf95c,infra=proof f4be77062fa16a1fcad6f08fb3c5630f437ecea9,timeout540;190parts afterNOT_SUBMITTED192pair. OnlyunusedoldFRAME metadata removed from transport. Diagnosticon must pass three lateassertions231–233, not merely reachouter. Outcome appended afterfullraw analysis. Policy d389ff64 read/integrated; closedhistorical budgets untouched.

Final44ea4417 terminalFAILURE298s: exact finaltranslator54fd5dd6/console484f4535 compiled, frozen toolidentity verified, thenadapter artifactrename uses wrong evidence root. Freshcaptures/baseline/off/partial/on/proofbodies NOT_RUN. Fullarchive5d1e25788c7d86b8d3108ad1f9c93889f639fb2c75869e4a5e1dd7a25fbf42ab/allcontainedfiles/indexverified; packager run_exit0 is not proofsuccess. Path-only fix0378ee1ca2606faac8394667cf23ee8e6115552b NOT_RUN/staticready190parts, selectedproofblobs identicalf4be7706. Final2070/3600,1530unusedclosed;6terminal, ownrequests/reservations/unresolved0. Wholepointerselect/genericT-ZST/sort4 andprofileadmission remainopen. Nearestactual nextstep correctedTEST in freshphase, no cold repeat for audit-onlychange.

## NEXT-SELECT-FRAME-CALLER first corrected TEST — 2026-10-09

Policy d389ff641194364e5eeda4ea4e66bedac4915a79; owner override60min14:03:33–15:03:33UTC, absolute15:33:33UTC; new3600ledger, closed accounts untouched. Build4763ca49-4420-4ab8-9bdc-bcee05246228 infra=proof0ecff7ee7e6fd5d88082915252cae5dd2395bf93,191parts, all selectedproofblobs/modes identical0378. TerminalFAILURE347conservative seconds. Fullarchive0e68c01a435cf1cfd5e14edf734bce71e7f0d75a2ae766c2e90d0b81fd5495eb/allfilehashes/textindex verified. CollectorINCONCLUSIVE because on-auditor omitted strict deadcode classification; raw actualfourcases intact.

Old-231 baseline exit1 exacttypefailure; freshoff exit2 exactowner-source refusal; partial exit2 exactShadowpair refusal; freshon exit1. New exactsource7ec86f52/unit20398964/body7404bf9da, translator54fd5dd6. Helper1normal/no-unwind and actualnested2normal/unwind complete return/leak/lifetime/free beforeouter. Both conditionpaths pass229–233 and final239 return/resourcechecks; first remaining3deadcode spans correspond exactcleanup-onlybb36/37/38. Fullpointer-select NOT_PROVED withstrictdeadcode remaining. Frozenkerneladbf2c3d unchanged. Sourcecertified narrowfalse-unwind projection card recorded beforeimplementation, not a check-disabling patch. Separate saved6ad and4763 classifierreplays preserve raw exit/verdict and give no new theorem. First-case observations and cleanup-classifier replay track hashes; admission/genericZST/sort4 open.

## NEXT phase full conditional pointer-select — 2026-10-09

Semanticcard/selfreview before defaultoff exactcleanup projection. Buildf4dc1ddf-c995-4650-a4d0-896cf14ad565 infra=proofe2b249674cbe505f2d073e0df8da023a6e6406ce,191parts571518bytes,340s. Exactnewtranslator9cf8bc32 (patch74694608) preservesfullsource/MIR and freezeskernel/spec/exporter/refiner; onlytwo checkedfalseunwind ASTcall successors projected. Sixrawcases execute: old231/off/partial preserved; projectionoff bothnormalposts then3deadcleanup; partialexactFatal; projectionon exit0/141statements,helper1/nested2/outer2 fullreturn/leak/lifetime/free andbothcondition231–233 twice. Fullconditionalselectedinput/thread/rawpointerown/falseunwind contract, no pointee rights or profileacceptance/genericZST theorem.

CloudFAILURE onlyaggregatecollector stale4case oracle; rawhelperaudit COMPLETE. Archive8482a76817dac9413f0bc7ee7d37c6665d28941de67ca6eb8c8e5dc82f65592f/allfiles/textindex verified. ASTisolatedclassifier replay corrects6case classification;4syntheticservice negativesreject, rawunchanged, no coldproofrepeat. Source-linked nearestsort4c1 currentfourcell/F/thread recovery remainsreservedhandler/scope admission blocker; actualcaller NOT_RUN, supplieddiagnosticpremises explicit. Final687/3600 (347+340),2913unusedclosed,ownterminal/reconciled/0reservations/requestwithdrawn. Checkpoint next-select-frame-caller/END-CHECKPOINT-2026-10-09.md.

## SORT4-C1-CURRENT-RECOVERY-CLOUD-2026-10-09 entry card

Start15:08:25UTC, main16:08:25, absolute16:38:25; policy d389ff64. Own isolatedselect worktree/branch clean/equald707d79e afterfetch. New3600sec no2913carry. Actualcaller sort4_stable std620 orderedc1 (cells1/0), direct Continue unwind. [Preimplementation transition/trust/controls card](cloud-build/sort4-c1-current-recovery/PHASE.md). Hypothesis: exact fullsource/MIR/AST scope placement runs stock debtclosure/currentpair recovery/fourjoin onnormal/directunwind without filtering resources. Entry strongowners/dst/F/type/thread supplieddiagnostic; actualcaller derivation andlegalshared-entry completenessOPEN. Newproof/replay/NOT_RUN separate; existingselecte2/raw0 andcollectorFAILURE preserved.

First Build9b1cbdbd, infra=proof4058e8bf, terminalFAILURE371conservative seconds. Fullarchivef48211eb integrityverified. Rawrelocation fullVF0 with exactninechecks; topgate wrongly demanded absent diagnostic_match. Audit-only replay identical; schemafix doesnot upgradeoriginalCloudverdict. Actual c1/controls/overlay NOT_RUN. Fresh exactSHA needed for previouslyunexecutedcases.

Second c1 Build3221200b, infra=proof337ea6a5, FAILURE335s; archive400693a2 integrityverified. Fresh actual O24 source/MIR/refinement calibration passed; draft AST patch rejected by ordinary gitapply at6273. Actual overlay/newcontrols NOT_RUN. Static patchcontext repair gives byteidentical translator26eb4a73 from strictrelocation7bfc8af2, no semantic change; newpatch5b9cac96. Current706/3600, both ownbuilds terminal/reconciled. Fresh exactSHA required for unexecuted c1 gates.

Thirdc1 Build4fa47604-3792-4533-88da-1e4ae7d52a23 infra=proof12ceb64996156f2a07c60987e59d388f687b8791 FAILURE354s; archivebc500a145dd09f8e70ffc382f9a5fb58ff71b4bd22558788ce1ff7d730ca6859/index6f23895b integrityverified. Exactpatchcompiledtranslator26eb4a73/frozenkernel37ed2550. Freshselectedisolatedscopepositives0; directunwindhelperbeforecaller+2targetreturn/free/leak checks. Typedlive/missinglifetime resource negatives intended; wrong/duplicate marker negatives frontendonly. Bothfalseposts rawintendedfail; aggregateauditmissingimpSpancoordinate normalization and note-vs-trace header distinction. Savedreplay separatefromoriginalCloudFAILURE; actualoff/on/c1normal/c1directunwind NOT_RUN. After60min no newbuild; ledgerclosed1060/3600+2540unused, ownterminal3/reconciled/readywithdrawn/reservations0. Checkpointsort4-c1-current-recovery/END-CHECKPOINT-2026-10-09.md.

Completion-only saved4fa falsepostreplay: normalizeonlyline/pos insideimpSpan asspan; parse timestampedproofentries separatelyfromnotes, exactsource/rawcontract/fullgraph/refinement checksretained. Bothnormal9false anddirectunwind17false intendedfirstpostsconfirmed, helperbeforecaller; four parsernegativeschecked. OriginalCloudFAILURE/rawsavedcaptures unchanged; actualc1normal/directunwind stillNOT_RUN. FALSE-POST-SAVED-RAW-REPLAY.json recordsfullrawhashesandtool/sourcepins. No freshproof after60min.


## 2026-10-09 16:52:10UTC — exact actual c1 execution authorized

Separate SORT4-C1-ACTUAL-EXECUTION account3600s, main17:52:10/absolute18:22:10.
Experiment card/rationale/domain/posts/decision gates: cloud-build/sort4-c1-actual-execution/PHASE.md.
Old7fa5da3a/d707d79e and exact select e2b24967 preserved. Service replay is not new proof.


### First actual result and bounded type-interface step

Build3c845267-3008-4921-8d1f-de6027a837c7, infra=proofe878dcf21e382935a1b31fe39a17f40fbb5bde5d,
SUCCESS diagnostic only, raw actual-on1,312s conservative; archive d3d615ee
full integrity/index verified. Actual-off opt-in refusal only; actual-on exact
source/MIR/preAST linked continuation. recover_pair/join verified before caller
same unit. Direct c1 unwind debt186/recover187/join188/return190/leak226 done;
normal Output projection/bool mismatch190 before normal assignment/recovery.
FIRST-ACTUAL-RESULT.json separates paths. No whole function/normal proof credit.
Compiler-origin HRTB clause in exact full MIR16950–16991 explains mismatch.
Preimplementation rationale C1-OUTPUT-EQUALITY-RATIONALE.md; new separate exact
c1-only typing patch65495dcf, no kernel/alias/prelude/runtime/post changes.
Fresh strict/false-post gates plus actual equality-OFF type negative precede ON.


### Output interface patch transport correction

Build57753d6f-5151-4403-afb3-bd370f9cc1b4 terminalFAILURE350s; infra=proof65495dcf159226692852646c12e8d24e8a236f28.
Archive39482cf4 full integrity/index verified. Normal git apply --check rejected
hunk7375 lacking trailing context; no actual-off/output-off/on. Source/MIR baseline
fresh, but setup-only failure gives no resource negative/new recovery credit.
Added unchanged trailing block context, no changed desired translator bytes;
repair0f3389ca published, ordinary patch structural counts checked. No unidiff-zero.
Audit-only note-stage improvements separately replayed on first new Build raw.
Third exact Cloud submission0f3389ca with900s timeout started within main window.


### Exact actual c1 final — main deadline / checkpoint

Thirda80d95f6/0f3389ca terminalFAILURE378s, archive7a47136c verified. Actual-on1
reaches both c1 recovery/join continuations; unwind fullpost/leak226, normal
first later c2 ref_precreated_token failure195. Cloud collector rejected library
error span; saved-raw audit corrects interpretation only, originalFAILURE retained.
Default-none actual missing-debt controls rationale/conservation before4ad3 patch.
Last0e77d0f7-9d34-406b-88eb-1e18f1fde2d2/4ad3b12f terminalSUCCESS355s;
archive84954e457b10a4994d61cfb7da50c4f4a2960383545c9220e49cd1323fea6ac1
integrity/index verified; rawpositive1 same exactc1/postAST/fullposts, c2 stillblock.
Twoactualcontrols1 intendedmissing comparison_debt atcallee requires68, targeted
caller193normal/187unwind. OriginalcollectorINCONCLUSIVE dueprimaryspanexpected
atcaller preserved; precise saved-raw replay plus independent review confirms
intendedprecondition, no newproof byreplay. Individualraw/status/results survive
aggregate. Sameunitrecover/join beforecaller andfreshprerequisites documented.
Normal intermediateCURRENT owner/frame/debt closure only; fullnormalfunction
post/return/leakNOT_REACHED, dstinitializationNOT_PROVED. Unwind branchconditional
fullpost/leak, no wholesort4 theorem orprofileacceptance. ActualRustcallerstrong
premises/legalsharedentry/genericZST remainOPEN; no Freeze/purity/no-panic added.
No c2/selector experiments. Aftermain17:52:10 onlyevidence/account/checkpoint.
Final1395/3600 (312+350+378+355),2205unusedclosed; ownterminal4/reconciled,
allarchiveverified, active/unresolved/reservations0, readywithdrawn, v2/max2intact.
Finalsort4-c1-actual-execution/END-CHECKPOINT-2026-10-09.md. Nextsingle task derive
suppliedc1entryfromoneactualcaller/bounddomains before proceedingbeyondc1.


## SORT4-C1-CALLER-ENTRY-CLOUD-2026-10-09 — entry card

18:17:12UTC start,main19:17:12/absolute19:47:12;3600newbudget/old2205closed.
Readpolicy d389ff64; fetchownremote19f82018equalclean; noforeignhistory transfer.
ActualfirstSmallSort254 caller mutable v/scratch/F, original branch guard retained.
Nativegeneratedreference contract—not rawownerpre supplied—to actual commonprefix
and explicit c1 pre entailment boundary; fullcaller andsort4summary notused.
Preliminarymap identifiesMUstorageconversion and native reborrow representation;
positive-sizeT NOTentailed forZST8..15. Minimalrange/duplicatepermission controls.
Rationale+conservation/selfreview in phase; firstsupportrefusal remainsadmission,
never intendednegative. Sourceextraction/pairedMIR/proof/refinementCloudonly.
Portablecoord487dc adopteded6b2b6a afterphasebaseline42a28caa, phaseAST preserved,
ownACK only/currentv2max2 no sharedmigration. Conditionalc1oldresultsnotupgraded.

Closed callerentry883/3600=290+305+288, unused2717nocarry. Buildpins4ab62d12/
c1b0b56a/ed4651e4, IDs c7ab932c/ff3a7698/43f10d3a exactledger/evidencecheckpoint.
AllrepresentationMIR/refiner supportsPASS; firstoverflow, secondannotationparse,
thirdmissingstd::intrinsics::abort on notyet-excluded scratchfailurepath. Third
array_inv/largeTbound steps intermediateonly; no selectedcallsite/currentsource4/
Fthread/dst/type entailment ortargetpost/leak. Source-frame subsetcase separately
executed buttargetNOTREACHED. Zero c1premises eliminated, bothresourcecontrols
INCONCLUSIVE/wrongfirstobligation. Raw/case/stageevidence saved; firstindividual
collectorfile initialbug correctedfuture, priorincrementalresults retained.
Audit-only replays no newproof. No semanticpatch/c1integration/c2/selector.
Nativeentrymodel shape exists but slice-reborrowTODO/aliases/ZST/generic qualification
OPEN; originalFreezeMarker not logicalstrengthening. Lastbuildcreated19:11:30 and
terminal19:16:18, aftermainonlyfinishingevidence/account/checkpoint. Ownterminal3
accounted/downloadverified; readywithdrawn, active/unresolved/reservation0, sharedv2/
max2 unchanged andpeerstatepreserved. Nextone: actual scratch-success source-linked
prefix admission and SAME callsitepremise lane. Details finalcheckpoint/map/reproducer.


## SORT4-C1-CALLER-BRIDGE-CLOUD-2026-10-09 — closed

Continued789b0daf in own select-night worktree; main19:43:08–20:43:08UTC,
aftermain only evidence/account/checkpoint. Source-linked success selector retains
original scratch check; actual first-sort4 boundary reached, invocation absent.
Builds15056f9e/e97528f0 (332s), f854de72/c8ae2005 (303s), 5e821db1/4a7eedc5
(299s), exact full SHA/buildIDs/archivehashes in final checkpoint/ledger/result.
All raw caller positives1; third source4/owners/F/thread and native selected-return
checks intermediate only due strict dead code abort/fallback. No supplied premise
eliminated as fully admitted caller theorem. Bridge optionalstorage assembly
reached then pure-bool-as-predicate syntax error126. Bool/classifier734af5d8 and
trace needles9be26c41 NOT_RUN. type_interp, generic MU identity/owner restoration,
ZST applicability remain OPEN; no inverse/ownership assumption or disabled check.
Narrow exact slice as_mut_ptr value-only candidate patch f200a581: independent
review and third all4 projection controls PASS; native T/MU raw0+post/leak,
wrongvalue/rawdst rights negatives intended1; source range/duplicate intended1.
Experimental profile NOT_ACCEPTED; historical select/c1 preserved, c2 NOT_RUN.
Saved first hash and third deadcode replays/manual AST CFG add no proof. Final
934/3600 used,2666 unused closed/no carry; all3 terminal/integrityverified/accounted,
ownreservation/active/unresolved0, readywithdrawn, v2/max2 unchanged. Temporary
foreign file incident restored with no lastingdiff, no foreignindex/ref/build/ledger
mutation. See sort4-c1-caller-bridge checkpoint and semantic card. Stop.

## 2026-10-10 native entry / c1 session (start 21:52:33 UTC 9 October)

Direct owner resume; policy c7ca8c467aecf10a4b53039372ee97714f854ee3 adopted at
6726a08d30b37d6d0f4ae65c3d8c2861615d249a; branch-local docs/status archived.
Main 23:52:33 UTC, absolute 00:22:33 UTC10October; new3600Cloudsec, ownerselect-sort4.
[Phase/card](cloud-build/sort4-native-entry-c1/PHASE.md) and
[independent design review](cloud-build/sort4-native-entry-c1/ENTRY-DESIGN-REVIEW.md).
Hypothesis: standalone native-resource entailment closes source4/CURRENT owners,
F cell/F.own/thread/frame with full VF0, avoiding structurally unreachable branches
of historical filtered fragment. No original caller CFG projection or full caller
claim; exact read-only source operation correspondence only. All T incl ZST,
all native lengths, queried ghost len>=8 boundary. Full native normal/unwind return
and leak checks; no comparator/copy. Range/duplicate/false-post negatives isolated.
Stronger optional-dst bridge separately tracks size/type_interp/MU restoration.
Preparation fixes734af5d8/9be26c41 already applied; saved replay before fresh proof.
Fresh proof NOT_RUN at card preparation; no proof credit from docs/replay.

Fresh native Build `bef9a3fd-a991-41b4-bca3-3d8e4a424b0d`, proof=infra
`d4b2d6f2e0dc6b1c9f1e0f8362bb08f04bf67d4d`: prefix-native/source-frame-positive/
native-scratch-frame VF0 with paired refinement/full native posts+return+leak.
Source4 CURRENT owners/F cell/F.own/thread and exact source/F frame preservation
assertions derive from native pre; no size/type/dst assumption in this subset.
Separate lemma signature/source operations exact; actual caller CFG and sort4 call
absent. Scratch kept opaque native frame, bridge fails inverse MU equality105
(after identity97 observation). Range/duplicate/CURRENT false-value raw negatives
intended; mapping classifier multiline ghost span repaired by saved replay only.
Archive dd421621c255db15e0e0cbdea91dd3628ed9d9e19a87495bd8201c122cb138bc,
562 files/text integrity checked; 287 Cloudsec,3313 remaining. Experimental profile
unaccepted. See [fresh evidence](cloud-build/sort4-native-entry-c1/NATIVE-ENTRY-EVIDENCE.md).

C1 Build32c43f9f-bcef-4a15-bc95-1455305ebaeb / proof=infra7511ddcd failed
isolated frontend console compilation (contract tuple versus option at7491), before
new c1 cases, all NOT_RUN/no proofcredit.352Cloudsec accounted inclfailure,
639/3600total,2961remaining; 354files/hashverified archive9b6bd493. Corrected only
falsepost tuple reconstruction, independentreview; newpatch2e1621b7, translator
59048330, profileunaccepted, exact frozen source unchanged. See preparationfailure.


2026-10-10 native-entry session fresh C1 65d6/1fe60: raw bounded VF0/147,
actual FnMut190, normal recovery193/join194/post140 and direct-unwind187/188/post147,
return/leak; fulltarget still c2token88/source195 VF1. Six causal negatives intended
at exactVCs; classifier stockwrappermultiset replay changes no proof. See fresh
phase evidence for fullSHA/time/archive/profile/debts. Earlier dbe/7456 stopped
collector attribution, prefixNOT_RUN;412s. Total1438/3600,2162 remaining at23:03:46.

DBB9 dbb9d393-e8e7-4caa-9b84-5592c17443b9 / proof=infra0b26303a1d873bcd5ca3d40428fa1dcb79abf244:
fresh C1 confirmedVF0/allcontrols, C2translatorcompile/default-offC1VF0/sourceECD83/
exports0/refinement0; decode1 stdoutstderrmixing, actualC2diagnosticNOT_RUN.
360Cloudsec,total1798/3600; archivec4144a11/inventory711. Exact failure
and independently reviewed infrastructure stream fix in C2-PREPARATION-DBB9.

FreshC974 c9746cd5-7ef6-4481-9011-63c472db3afb/proof=infradfe8a19de11ca583a02a5ab20f41591909c127be: C2 completeexport/decode/
refinement0,82/164normal and28/110readonly graphs; ghostparse196 midblocklet_lft
blocks originalAST, noC2proof. Exact sourcehashmutant admissionnegative passed.
319Cloudsec,total2117/3600,1483remain. Archivea92288cc/inventory755.
See C2-FRESH-C974-EVIDENCE for exactgraph/tool/profile/source; typednativefallback
reviewed/prepared afterthisfailure, no assumption or disabledchecks.

### 2026-10-09 23:48 UTC — typed native entry, fresh46bb/ff5d

See cloud-build/sort4-native-entry-c1/TYPED-NATIVE-FRESH-46BB-EVIDENCE.md.
Positive raw VF0/82 statements: stock logical T/F production, source4/CURRENT
owners, F cell/F.own/thread, identity helper and exact full native frame/posts/return/leak.
No callback; automatic unwind post captured/vacuous, no actual caller CFG or sort4.
Both missing-producer controls independently reviewed at exact callee16/caller43;
raw service labels remain UNREVIEWED, no rerun/replay proof credit.
Charged368sec; cumulative2485/3600; archive/text receiptsverified.

Next C2 diagnostic hypothesis: source196 second let_lft can be represented by a
stock-parsed singleton declaration inside a closed unresolved placeholder block,
while preserving full runtime AST/call inventory. Exact ECD83/fullunwind source;
semantic rationale/review C2-UNBOUND-SCAFFOLD-CARD.md. Expected intentional
UNBOUND_C2_LIFETIME_NOT_PROOF refusal AFTER fresh scaffold emission, beforekernel.
Source-operand mutation must refuse before AST. DefaultoffC1mustremain VF0.
Success only unlocks separately reviewed sibling-scope projection; parse/shape
failure remains a localized frontend preparation blocker, noC2proof.

### 2026-10-10 00:02 UTC — A5DE terminal, close session

Builda5de0e51-3663-4c7d-9844-ff6b122436ee proof=infra
f925546602be4c606c0ce60416f1f12047412c6a SUCCESS transport,406sec.
See cloud-build/sort4-native-entry-c1/C2-FRESH-A5DE-EVIDENCE.md. Exactunbound
scaffold captured, all5/8/4calls, mandatory refusal before proof; no C2 theorem.
Full normal/readonly MIR/refinement pass, source mutant refusesbeforeAST/body,
fresh default-off C1VF0 unchangedpre/postpins/all6causalcontrols. Independent
Sol code+artifact review complete. No newexperiment/build after23:52:33.

Account closed2891/3600,709unused/no carry;8terminal/verifieddownload, own
reservation/request/unresolved empty, v2/max2 unchanged. Native subset and
bounded conditionalC1 remain separate; fullcaller/sort4 andprofileacceptance OPEN.
Checkpoint END-CHECKPOINT-2026-10-10.md; no automaticnextsession.

## 2026-10-10 00:34:15 UTC — new native→C1 session

Direct owner resumes actual sort4/caller mission on assigned select-night branch.
Main02:34:15, absolute03:04:15, fresh3600 Cloudseconds/no carry. Policyc7ca8c46,
adoption6726a08d/ownACK preserved; previous5fa94c49 clean starting checkpoint.
Saved evidence premise map in [phase](cloud-build/sort4-native-compose-c1/PHASE.md),
no unchanged matrix repeated. Fresh internal no-dst C1-only helper then native
resource composition chosen to avoid unsupported inverse MU equality; original
whole-sort4 contract unchanged. Semantic card/review precede narrow bindings;
all native callback outcomes CURRENT normal/unwind/frame/post/return/leak required.
C2 follows useful result or precise dependency blocker. No proof verdict yet.
New own phase registration tested with pure isolated synthetic ledger: exact
owner/window/ceiling passes; wrong owner/main/start/ceiling rejected, no coordinator
or evidence mutation, no compiler/proof. No Actions or foreign state writes.

### Fresh preparation fc01881e

Proof=infra24c1c33f;337Cloudseconds, full archive/textinventory verified. Exports
and refinement fail at compiler E0255 duplicateFreeze (verified/original10,
import6). MIR/AST/verifier/composition NOT_RUN; no proof credit. Source generator
corrected to read/check but not emit coreFreeze, matching oldnative import.
[Exact evidence](cloud-build/sort4-native-compose-c1/PREPARATION-FC01881E.md).
New source will be rerun; no unchanged failure or native matrix repetition.

### Fresh capture e71803aa

Proof=infraeb631c22;367seconds, session704/3600. Both normal/readonly full
MIR and refinement pass. AST/full verifier fail at source226 second assert
in one multiline ghost annotation, before target proof entry. No composition
credit. Exact archive/source/MIR pins and next falsifiable correction in
[capture evidence](cloud-build/sort4-native-compose-c1/CAPTURE-E71803AA.md).
Raw graph's lowercase Continue is preserved; initial uppercase string count
is diagnostic only, not unwind admission. Next source assertions separated;
stock strict/HRTB opts only in verifier, no proof-mode flags in exporter/refiner.

### Fresh helper boundary 4a0b4f8b

Proof=infra5dc32b47;304seconds, session1008/3600; archive6dfe29f4 full hash/text
inventory verified. Support normal/readonly export/decode/refinement0. FullVF1
entered helper, firstunknownmarker source189, native notentered; stockASTdump2
FailureTODO. [Exact source/MIR/tool and decision](cloud-build/sort4-native-compose-c1/BUILD3-REVIEW.md).
Independent Sol capture-only concrete review GO (852257patch/4dc5translator):
same immutable target Func only, full verifier capture-off; missing targetfile
fails capture and cannot authorize splice. New own tool reproduces Cloud4d3
base from verified candidatepatch4113; old8e467chain/worktree preserved. No
composition proof credit. Saved-MIR service replay passes ordered1/0, native
args,8callback locals and synthetic mutation refusals; replay is not proof.

### Fresh immutable helper capture 0904f144

Proof=infrafa4c46d3;322sec/session1330. Archive49695c2e and all text chunks
verified. Supportall0, source/full pairedMIR unchangedfreshpins; exact helper
Func64c01593 emitted unchanged under capture-only4dc5 translator. Wholemodule
dump stillFailureTODO; ordinarycapture-offVF stillmarkerrefusal189, native
notentered. [Capture/tool identities](cloud-build/sort4-native-compose-c1/CAPTURE-0904F144.md).
No proofcredit; independent rawAST/designreview precedes helper-only binding.
Hourreport delivered01:34:15, continues without ownerresponse.

### Native composition dependency reassessment, switch to C2

Independent rawAST review finds native4dc5/kerneladbf lacks operative strict
end_lft_binding/heap/type-escape mechanism; SORT4_STRICT_LFT_CUT env was inert
except captureguard. Established C1/C2 profile has kernel37ed2550; importing
its combined kernel-adjacent dependency is a new admission boundary, not a
translator-only helper repair. Proposed Noop explicitly NO-GO; no semantic
implementation performed. [Review](cloud-build/sort4-native-compose-c1/FRONTEND-FRESH-REVIEW.md).
Per direct assignment step4, switch without ownerwait to bounded C2 under
existing frozen strict profile/kernel37ed and own translator-only4851 delta.
Native/C1 separate proofs unchanged; completed composition stillabsent, no
premises inferred from assertions insidefailedhelper. No unchanged failure rerun.

### C2 preparation interface refusal ae8ac387

Fresh proof=infra `c011988a43ff6c3a09b4aec6341975a98d81bc70`; Build
`ae8ac387-fa50-46ca-93b2-c715057f4ad3`, create01:45:41.249497390,
finish01:52:06.891261 UTC, FAILURE386sec. Session1716/3600,1884 remaining.
Archive `b3c136474a10e7f92b491afa85542c6301419ef397dcdc42074b4b3ba9f979e8`
and full text index/chunks verified. Fresh existing bounded C1 VF0 including
normal/direct-unwind CURRENT posts/return/leak and causal controls. Fresh C2
normal/readonly export/decode/full-MIR/refinement all0, exact A5DE pins retained;
unbound scaffold obligatorily refused before target; default-off C1 VF0 and
source-hash refusal retained. Collector stops at runtime-inventory interface
gate before C2 bound patch/console build/positive/controls: those are NOT_RUN.
Saved inventory has5/8/4 and exact source223 FnMut. Localized worker repair must
first replay saved/live row shapes and causal mutants; no profile/classifier
acceptance change and no new proof credit from this preparation failure.

### Fresh bounded C1+C2 full verdict f4abe251

Proof=infra `7c8e34610a52bebc7212c6e611d1afa2e70c085b`, Build
`f4abe251-23f9-459e-a418-6372b6553057`, create02:00:53.445494900,
finish02:07:47.784247 UTC, SUCCESS diagnostic415sec. Session2131/3600.
Archive `e2c500fdce968124c177dfbce638e5f812ce598c4834c87e643bc6da2c1adad4`
and all text chunks/index verified. **Fresh positive VF0,184 statements**;
actual source-linked first and second FnMut, separate sibling cmp/cmp2 bindings
and compiler Output=bool registrations. Full original CURRENT source/F/thread/
optional-dst normal, C1-direct-unwind, C2-direct-unwind posts/return/leak;
same-version recover_pair/join verified before target. Strict dead-code retained.
C2 entry CURRENT resources follow C1 normal recovery/join within this one proof;
C1 unwind exits before C2. Raw entry source/F/thread/types/sizeT>0/dst remain
supplied; native→c1/actual caller CFG/caller→sort4 absent. Normal boundary227
before c3/select/copy; not a whole-sort4 callable summary.

All7 controls reached their intended first VC; source operand mutant refused
before target. Default-off C1 VF0 and mandatory unbound scaffold refusal remain.
Saved service replays are not proof. Independent review directly verified pins,
postAST96b7declaration143=125+8+10/future18absent, sibling bindings and raw
outcomes/control attribution. Per-local chunk identity is not printed at verbose2;
allocation admission is justified separately by deterministic frozen DeclStmt
block registration/fresh producer and free_locals on each observed scope/root
exit, not inferred from a green count. [Exact fresh evidence](cloud-build/sort4-c2-bound-prefix/FRESH-F4ABE251-EVIDENCE.md)
and [independent raw/kernel review](cloud-build/sort4-c2-bound-prefix/FRESH-F4ABE251-REVIEW.md).
Experimental proof/projection assessment does not accept a tool profile or
rewrite the original collector's pending fields. No new run solely for verbosity.

Own session account closed2026-10-10T02:17:57Z:2131 charged,1469 unused closed,
carry0. All6 terminal/downloadverified; own reservation/request absent, v2/max2
preserved. Read-only C3 design identifies dynamic cross-half CURRENT ownership
and third lifetime/Output binding as next fullsort4 gate; no C3 experiment.
Final checkpoint/evidence/coverage changes are documentation only, no proof upgrade.

## 2026-10-10 10:20:59 UTC — new actual C3 session

Direct owner instruction lifts prior STOP within actual-sort4/caller mission.
Worktree `/root/verify-rust-std-select-night`, branch
`research/night-select-sort4-cloud-2026-10-09`, clean initial HEAD
`fafb91f0d59d070dac8b9ac72c71143a4224a78b`; distinct git-dir/index verified.
Fetch completed; existing adoption/ACK retained; policy commit
`c7ca8c467aecf10a4b53039372ee97714f854ee3` read. Main deadline12:20:59,
finish-only absolute12:50:59 UTC. Fresh 3600-second account, no old carry.

[Experiment card](cloud-build/sort4-c3-bound-prefix/SEMANTIC-CARD.md): first
prove selected cross-half ownership/CURRENT complementary frame, third named
callback binding, then bounded C1→C2→C3 normal/all direct-unwind closure.
Independent design review conditional GO precedes semantic implementation.
First Cloud capture remains diagnostic-only: fresh source/paired full MIR/
preAST and mandatory refusal, no target proof credit. On fresh certificate,
review and pin exact bound projection before proof; continue C4/C5 if complete.
Native→C1 is secondary and requires separate compatible strict-cut semantic
card/review; no repeated preparation on incompatible frozen chain.

C3 Build1 `b38ac0e8-c818-4424-8480-8fe2386be1eb`, proof=infra
`3b675ffba979ce7c2af6f482459ce29549ac923f`: FAILURE,413 create→finish
seconds (10:36:47.248569910→10:43:40.066372 UTC),412 execution. Download
verified archive `7ddae56cdf841faaad05887287dc0850ab959d77a535f4ca5ee629bdf45b01f5`,
all text chunks/inventory. C3 capture console compiled, default-off C2 VF0
184 statements and mandatory unbound C2 refusal retained. Source ghost-strip
identity succeeded; C3 normal exporter then panicked: helper annotation was
inserted between the `pub` token and `unsafe fn sort4_stable`, not at item
boundary. This is a source-preparation failure before C3 MIR/preAST/target,
not a semantic negative. Candidate source78b9feff retained in raw evidence.
Localized fix: anchor full `pub unsafe fn sort4_stable` so helper precedes
visibility/header. No helper/translator/kernel semantic change; new fresh
capture required. Remaining3187/3600; no own unresolved Build.

C3 Build2 `bdef4a7c-3a5e-4253-8fa0-65ccbbba8f89`, proof=infra
`b8441cb06f77cd24bc349bbbfd0d3658ecbe023f`: SUCCESS,449 create→finish
seconds (10:52:40.415586201→11:00:09.061883 UTC). Full archive verified
`40485adcd4bb1b7213b04c88fb7e0f215340e1adb5d9e9106b0022ee79ed9dde`;
external text chunks not fetched, complete raw files recovered from archive.
Fresh source087123b1, normal MIR7582215b (112 blocks/194 locals), readonly
MIR9622479f (28/110), preAST7dbc4ed8. Capture deliberately refused before
target: `FULL_ORIGINAL_AST_CAPTURED_NOT_PROOF`, not proof/semantic negative.
Source ghost-strip equals original runtime3602050e; refinement/export gates0.
Default-off C2 VF0/unbound refusal retained; frozen nontranslator tool inputs
unchanged. Fresh callback locals `_124.._129`, c3 bool`_123`; former `_98..103`
are ghost units and are not moved under this profile. Exact bound delta and
independent addressed review precede next Cloud target. Total862/3600,
remaining2738; both own Builds terminal/accounted/download-verified.

C3 Build3 `a956b0b2-4e05-4c19-90b4-408f381ba1fc`, proof=infra
`aa6e5a725f71506602903f95b1832a32fa849e50`: SUCCESS,461 charged seconds,
full archive c62db4d3 verified. Unified actual C1→C2→C3 VF0 candidate,335
statements; same-version selected helpers precede target, full CURRENT posts/
unit return/leak/dead-code gates. Eight target-first negative candidates and
source-hash refusal before target retained; independent raw/allocation/control
review pending. PostAST9ca21fdc. Total1323/3600, remaining2277, own slot free.
C4 preparation remains conditional on complete C3 review; no C4 experiment yet.

Independent C3 a956b0b2 raw/correspondence/allocation/control review PASS for
this exact bounded projection (review SHA d528bfa5...). Root155+child8/10/6,
futurecallback12 absent, bool c3 outer; frozen block allocation/free rules plus
observed normal/direct-unwind frees justify scope conservation. Per-local
chunks not printed; no count-only soundness claim. All8 intended firstVCs
confirmed. Conditional proof boundary now C1→C2→C3; global profile remains
unaccepted. C4 capture profile pins review and is enabled for next exact run.

C4 capture submit from79ccdd5c refused before Build creation: pinned source
payload exceeded the bounded191-substitution transport. No Cloud time charged,
no Build/reservation recorded. Narrow recipe fix removes documentation that
the executed runner does not read; preserves all source/patch/profile/infra
dependencies, C1 card, relocation card and hash-pinned independent C3 review.
Documents stay committed in repository; transport bound/allowlist unchanged.
A new exact source commit is required for retry.

2026-10-10 11:50 UTC: C4 capture Build eb66efc6-a85f-4ffd-b20a-9382f22c5538
SUCCESS, proof=infra f0c7b0d0ae185cdb9c733e3aa49fd4af597bb7d9.
517 seconds createTime→finishTime charged; cumulative1840/3600.
Archive720f397460c56944b38aedcde10ede08bb2f4597e3007111c5eaacea6c57f835
and inventory/index verified; external text chunks not separately fetched.
Fresh C4 source ba9e6ad3633004c3d934c590462443951ddd6dec80a5df9ffb687ec940958c6f;
ghost strip original3602050 unchanged; refinement0. C3 default-off335 statements
and mandatory unbound refusal retained. Capture refusal2 before target: NOT proof.
Exact C4 bound projection and independent fresh correspondence review in progress.

2026-10-10 11:58:43 UTC: C1→C4 bound Build a5180cd7-3ad7-4199-9b1f-56c31876cc4d
created on proof=infra203b59258b00ccc8bc2ecc030726fafde3a57d05,
token dispatch-bab7b0f048514dd8948af5eb2ae790ee, config61186e354ea278c50c8cb8fe7da5ff01bd675cfb9fe6caa318cb800e8aa924c4.
Independent fresh C4 correspondence/delta review gave conditional exact GO
before dispatch; parent expressly exercised user-authorized diagnostic dispatch.
Later automatic review hash gate added for future source commits, not retroactively
claimed for this pinned run. New gate/docs do not change its pinned inputs.

2026-10-10 12:04 UTC: isolated non-toolchain classifier configuration replay
via ast.parse/literal_eval confirms unsupported outer-type/bound fixtures stay
in NOT_RUN source forms and are excluded from runnable negative candidates.
No live evidence/coordinator mutation, proof/build/import of driver involved.
Strict profile is enabled solely for reviewed CAPTURE_ONLY_NO_STRICT_ON_PROOF;
exact two-file candidate01f52d92 and independent/design/parent reviews committed.
Full trust matrix and native helper/composition remain NOT_RUN.

2026-10-10 12:10 UTC: a5180cd7 SUCCESS,487charged; cumulative2327/3600,
remaining1273. Archive/inventory/index verified. C4bound VF0(370), fullposts,
5sameversionhelpers,9intendedfirstVC candidates, source mutant admissionrefusal.
Independentraw allocationreview pending. Firstselect qualification blocker
saved; conditional historicalFRAME/cleanup chain is not currentprofileproof.
Secondarystrictcapture-only submit onf7ff82a29b914c04181ecab4070d64555a61a58f
under separate explicitlane/sameownerbudget. No strictONproofcredit.

Strict capture-only Build31f58a87-9dc0-4f74-ad3a-ac4888f6ffbd created
on proof=infra f7ff82a29b914c04181ecab4070d64555a61a58f; token
dispatch-7751e0569e6340b6afec4f8a60928ff1, config
f59aa28de60495a14281a90762eded3d10c73e4b7006de019ab4451e72897714, input
e6937a228e4baeb8585181674280a10280e96a1f9161a3a6129b9b71d6e0ba7c.
Two-file experimental patch01f52d929a3678aed81bef8659f4e0ad6926487da1667139e7a66d6664526154;
new resulttranslator753166a81e886bb4e3139614706f9a9b4fb9840f546153f27db7a0a073975704
andkernel7870f3eb6b2978577de54fb23bf8e8bc4daf21a4d7cad18055ee008bbfaf4608.
Fresh compile/sourceMIR/refinement/preAST diagnostics only; strictONtargetproof
NOT_RUN and all trust/admission/native-composition obligations remain open.

2026-10-10 12:15 UTC: independent a5180cd7 raw review PASS for exact
conditional bounded C1→C4 projection. Actual postAST184outer+8/10/6/6children
=214declarations; C4tuple$_161child, c4+recoveryunitsouter. Frozenkernel37ed
producer/free rules plus normal/directunwind frees at484 androot502 establish
allocation correspondence; individual object creation not printed/count-only
claim not made. Nine intendednegative firstVCs confirmed; sourcehashrefusal
notsemanticnegative. Globalprofile/collectoracceptancependingfields untouched.

2026-10-10 session closure at 2026-10-10T12:30:48Z: strict capture-only Build
31f58a87-9dc0-4f74-ad3a-ac4888f6ffbd terminal FAILURE,348 seconds,
proof=infra f7ff82a29b914c04181ecab4070d64555a61a58f. Archive
0442704490f86bc585e1fd2681054a4715efbd2c200ea13a8b1162044422d65a
and inventory/index integrity verified. Exact two-file patch check/apply and
Cloud compile exit0; new binary253f9f0f283f67eb36cb986c35b40d96869a51b9cbf7e66e29443207f177f122.
All11 executed fixtures paired MIR export/decode/refinement0. Three marker
admission refusals; eight config failures at HRTB_OUTPUT zero/empty guard.
No AST captures/target entries/leak/return proof traces. Outer-type/bound
fixtures NOT_RUN. Independent raw review confirms no semantic-negative or
strict/native proof credit. Finish-only runner correction removes both HRTB
variables, static parse/guard review only, DRAFT Cloud NOT_RUN; profile disabled.
Main ended12:20:59; no new Builds/experiments afterward. Six own Builds fully
accounted/download_verified,2675/3600sec,925unused closed/no carry; active=null,
terminal reservations reconciled, own ready request withdrawn. Final checkpoint
cloud-build/sort4-c3-bound-prefix/END-CHECKPOINT-2026-10-10.md. No automatic restart.

2026-10-10 13:00:22 UTC: new native→actualC1–C4 session, main15:00:22,
absolute15:30:22 finishing-only; fresh3600Cloudsec no carry. InitialHEAD9240f9d4
clean,separategitdir/index,originforkfetch,policyc7ca8c46 read/adoptionretained.
NewownphaseSORT4-NATIVE-C4-CLOUD-2026-10-10, canonicalc1lane, stableowner/v2max2.
Card cloud-build/sort4-native-c4/SEMANTIC-CARD.md records exactprofile/resource
gap and isolated native/guard/MU/admission diagnostics. No earlyreservation,
no selector,strictdraft or newtrustedsemantic implementation. OldC4/nativePASS
remain original profile results, newcomposition NOT_RUN.

2026-10-10 14:00 UTC first-hour update: native/C4 effective translator/kernel
mismatch and non-callable exact-file binding documented before proof. First
Build07e046f8-3d43-4016-8f83-f6429a5bd9a2, proof=infra538662831180e6b21549c12b3d1275872fc56c28,
create13:41:51.066290394 finish13:47:32.773023Z, FAILURE342seconds. It refused
shell preflight at missing CLOUD-RELOCATE-IDS-TEST-CARD.md, before strict
relocation/C4/native target; no semantic negative, all intended cases NOT_RUN.
Archivecddf07221a4ad383e158b31935bb431ce7832ca859c9a6b56804c46975def050,
complete payload/inventory/index integrity verified by canonical download.
Transport closure corrected without bypassing the guard; exact required
document and three typed-native .gh files restored. Static required-path,
Python syntax/diff checks only. Buildd5a0f8da-a2ed-416c-9eac-a9ffff926c87
submitted proof=infrae12df71d57923d346ba0640b9bd0ea23d2835365, create13:59:41.174458427Z,
WORKING/no target verdict yet; account342/3600, one own active, v2/max2.

2026-10-10 finish-only closure: fresh independent3584fb04/285220a3 SUCCESS
(diagnostic collector only),382create→finish seconds, archive84208867c4ed920d3ab41012e56ab4a887396ae1da1d387dae317efcf6fab633 integrity verified. Pure guard/ZST witnessVF0/53; native guard firstlen+16 overflow obligation; CURRENT MU owner missing afterrewrap; castexpression ghostparserrefusal. Both exact-one-body and comment-only sourceSHA admission gates freshly refuse beforetarget. No connectednative/C4 orcaller proof. Startedparenthesis/earlyreturn/minimaloverflow draft saveddisabled, NOT_RUN; no fourthBuild or newexperimentafter15:00:22. Canonicalown readyrequestwithdrawn, noreservation,3terminalverifiedbuilds1165/3600sec,2435unusedclosed/nocarry. Newcontrol secondmain-deadlineguard is staticreviewedfinish-onlydraft, notnewCloudinfraPASS. Exactfinalcheckpoint cloud-build/sort4-native-c4/END-CHECKPOINT-2026-10-10.md;noautomaticnextsession.

2026-10-10 19:27:14UTC new opaque-native session from e5f3f1a, correct own
worktree/branch/separate git-dir/index clean. Main21:27:14, finish-only21:57:14,
new3600Cloudsec; old1165seconds closed/no carry. Policyc7ca8c46/adoption preserved.
New exact phase SORT4-NATIVE-OPAQUE-CLOUD-2026-10-10, canonical C1 lane, owner
select-sort4 v2/max2. Resource card identifies actual external pointer/checkedadd
rules by19:35UTC and permits separate internal non-ZST helper boundary; no
nativecaller/composition credit, no competing general VF implementation.

Fresh Build1ba7fdb3-c2ba-470a-84e5-e6b4077ffda4 proof=infra9b86096ec897577d11cd8efa4302aaccbf15b8ef,
create19:39:25.109943465 finish19:46:19.816185Z, SUCCESS diagnosticcollector,
415sec; archivec4104f376f209613f5a80c9386eaf8e64ddd150ca136a99b7213db190c2c371b
canonical payload/config/inventory/index/upload integrity verified. Independent
raw review: opaque interface VF0/73, all4helper bodies precede native consumer,
CURRENT rejoin preserves source/F/thread/types plus untouched full MU frame;
full automatic normal post/free/leak. False helperpost intended at43:74–79.
Actualearlyreturn VF0/81, no callback path. Pointer/C1 refused parser at second
statement of bare multi-statement ghost annotation; intended binding/proof
NOT_RUN. Saved admission classifier replay PASS; static recipe closure PASS.

Follow-up86e38e3a fixes only harness ghost syntax, preserving posts/marker/cut.
Exporter unconditionally appends overflow_checks=off at lib.rs:69; fresh minimal
len+16 standard MIR has add/no Assert, VF arithmetic refusal3:17–25. Follow-up
adds diagnostic pinned-rustc --emit=mir overflow-checks=on/panic=unwind capture,
no proof or general toolrule change. Buildd77612a5-5620-47a7-819d-3fa499cd15c0
submitted config1c1f752d16b9f5ac55acf0a9be92a9278e6121af262723b38ee404d3dc0ff9f6,
input74c29c394aba6900d78b341390438ca26d1107b4d5756f520507d5d09158dec1,
token dispatch-d899abe2e00c4ba4b64ac576dd5c5211, outcome pending.

2026-10-10 first-hour progress20:27UTC: opaque73/early81/pointer90 component
PASS, native actualC1/C4 absent. Freshd776/86e38e3a terminalSUCCESS344sec,
total759/3600; archivee467a5f23dcc9718b010eb16d78d1a4112c94f1ddffd2649244d2b8b0096e9d3
canonical integrity verified. Nativecandidate reaches split/lifetime then refuses
strictentry unresolved outertype172:1–30. Fullpackage ASTdump TODO beforecapture;
no comparator/currentunwind/completeposts theorem. Minimal checkedrustc MIR
AddWithOverflow+Assert(successbb1,unwindcontinue) capturedfresh; frozenexporter
appends overflowoff, normalMIR ordinaryadd/noAssert, VFoverflowrefusal3:17–25.
No runtimeunsafety or bound claimed. See FRESH-D776-REVIEW.md /artifactindex.

Thirdbatch prepared source transfer/borrow/undo candidate + intended Argsfalse
control; reviewed exactnative preASTcapture-only delta from1eab→86952a6a,
patch4a549366, kernel37ed unchanged, independentreview GO fordiagnosticonly.
Exactsource7eb/sourcecall210:21–92/markers194,212; newmodealwaysrefusesbeforeproof.
Default-off pointer recheck justified solely bynewtranslator opt-in0 surface.
OldC4normal/all4unwind/fullposts remain priorPASS, notcompositioncredit.

2026-10-10 20:58UTC freshbatch3 Build081275a9-032a-4053-a088-c173f12f05c9,
proof=infra7fc22c0452ee1fb89677da13de52a9433a383906; token
dispatch-8e3ce5fb68d34f2c8a1f302fce5a5dfc, config
8e255f39eea042dcbd3e42ed5bb7856e93d62cf1d0f3da68f574047956524166,
inpute732b18123dc7945d7f8222c707381ca03728480a6b2223a6b4bfb6b54cc56bf.
Earlier846 transport preflight refused before reservation/API, noBuild orcharge;
7fc omits only unused C4 preparation inputs, pack188<=191. No globalgate removed.
New single-native capture alwaysrefuses, defaultoff uses checked old semantics.
Independent serializer review: global recover_pair MergeFractionsStmt likely
explains fullpackageTODO; native-only dump may avoid it, pending fresh evidence.
Own terminal raw review duplicates and dispatch transport flags removed only
after archive byte/hash matches and canonical accounted/downloadverified state;
canonical archives/config/input/inventories remain preserved. No foreigndata changed.

2026-10-10 close main21:27:14UTC. Fresh081275a9/7fc22c04 SUCCESS416sec
(create20:58:01.833350812 finish21:04:57.129708), total1175/3600. Earlier
commentary396/1155 was arithmetic error, corrected from canonical account.
Canonical archive449ed1367c076dfa9429e7df3b7028ab4a837ab867135dd0159138d1bc5a365c
integrity verified after own ENOSPC retry. CapturepreAST18973de5 diagnosticonly,
mandatoryexactsource/extrabodyrefusals, pointerdefaultoffVF0/90. Preparedboth
parserfail198/199 beforeentry/intendedfalsecontrol. FreshAST independentreview:
76outerdecls,7decls/8inferredlifetimes including_5lenborrow; one actualFnMut,
normal/directunwind, four recoveryblocks includingnativeMU/F/thread/tail/posts.
No allocation/free or lifetimebinding theorem fromcapture. Stockshared_ref_own
identitynotestablished, no inverseassumed. Syntaxonlyownconstructorvariant and
exacttwo-case recipe published1e2d53c522a4f3a92fadc3dd3bee58da18940f16;
controllerdeadlineguard definitive refusal before Build/reservation, zerocharge.
No newexperimentaftermain; remainingtime evidence/account/checkpointonly.
Opaqueinterface/earlyreturn/pointer remain fresh independentPASS; native→actual
C1/C4 and caller absent; prior C1→C4fullnormal/all4unwind/posts unchangedPASS.

2026-10-10 newnativeC1session start21:49:42UTC,main23:49:42,finish00:19:42UTC11. Checkpoint93f902c2 clean ownbranch/gitdir/index; policyc7ca/adoption retained. Separate3600Cloudsec, ownerselect-sort4/v2max2/one own; old1175closed/no carry. First useful Cloud is exact revisedprepared2 from1e2d53c5 on frozen1eab/kernel37ed, no oldmatrix. Semantic card sort4-native-c1-bound/SESSION-SEMANTIC-CARD.md separates strict-entry/argument boundary/undo/nativeposts and intendedfalsecontrol; no referenceinverse assumed. MaingoalconnectednativeC1normal+directunwind, thenC4onlyaftercompleteC1. GeneralVFchangespeerowned; narrowbindingrequiresindependentreview/freshpins.

### 2026-10-10 22:24 UTC — corrected prepared boundary

Fresh34bddbf7-e536-4ef0-bb7f-82e07ef439fc, proof/infra16bbfa6c7f4340e0643426560c4ff33531aff370,
362Cloudseconds. Paired MIR/refinement0; strict entry and native-derived Args/F/
thread/opaqueMU assertions reached. FalseArgs expected190 fails; positive fails198
reverse own wrapper, no assumed inverse. No actual comparator or full native
post PASS. Independent pinned MIR/kernel/free review permits narrow actualC1
binding implementation in isolated translator; entry observer unnecessary/NOT_RUN.

### 2026-10-10 22:33 UTC — native C1 bound planned experiment

Hypothesis: eight compiler callback locals scoped inside the checked cmp child,
plus compiler-derived HRTB/Output=bool binding at actual C1 (operands1,0), allow
native-derived Args/F/thread to pass actual normal/direct unwind and complete
CURRENT native posts/unit/free/leak with opaque MU. Exact unaccepted profile
3efc917d/ed95e901 on capture869/frozenC4, kernel37ed unchanged. Independent review
and pre-verifier exact MIR/refinement gate; positive, two after-call negatives,
default-off and four address admission controls. First new failed proof resource
or general semantic dependency will be recorded instead of repeating the refusal.
No C4/C5/select/copy or actual external caller credit from admission/capture.

### 2026-10-10 22:49 UTC — native C1 pre-AST placement refusal

Fresh7456/e729,387seconds(total749). Both exact MIR/refinement gates pass;
mandatory four admissions/defaultoff strict172 retained. Target/2false controls
pre-AST refusefc2 vs18973, no semantic negative or C1 proof. Independent byte
diff identifies early generic strict preprocessing; narrowly reviewed binding
mode cut-retention fix preserves18973 and checked strict child, no fingerprint
substitution/general semantic change. First-hour update delivered22:49UTC.

2026-10-10 23:34 UTC native-bound10006623 / proofinfra8ec0214:
417sec, cumulative1166/3600. Fresh admission/callback/CURRENT normal+direct
cleanup/full automatic post/free/leak traces, intendedfalsecontrols226/210;
positiveexit1 solelydeadcode228,2. Archive5b0b69c1 integrity/indexverified.
Independent narrow CFG review GO; translator381e80eb/patcheea19eda places
unwindepilogue before exact original finalnormalreturn, allchecksretained.
Fresh correction scheduled; no complete nativeC1/C4 proof claim yet.

2026-10-11 native C1-bound session CLOSED: fresh3521e3b3-5979-4c35-b931-93c4e165176b,
proof=infra2e995605f5183907817d92db082624281665d61e, translator381e80eb,
unchanged kernel37ed2550. Actual C1 operands1,0 and normal/direct-unwind CURRENT
native recovery/post/unit/free/leak terminal traces reached; positive exit1
`dead code228,2`, no connected theorem. False normal226/unwind210 intended
cleanup assertions reached; all8 paired support/refinement and4 admission
refusals retained. CFG placement-only hypothesis falsified; root131 sizezero
route candidate needs exact-node diagnosis. No general rule necessity inferred.
C4 NOT_RUN; prior raw C1→C4/components independent. Scratch MU opaque; no MU
inverse/optional destination or re-supplied raw C1 resources. Four Builds
34bddbf7/7456e9be/10006623/3521e3b3 charged362+387+417+390=1556/3600,
all accounted/download-verified, unused2044 closed/no carry, no active Build,
reservation or ready request. Exact pins/commands/reviews/limitations:
cloud-build/sort4-native-c1-bound/END-CHECKPOINT-2026-10-11.md.

## 2026-10-11 native C1 exact-node/ZST diagnostic session

Direct continuation fromd2c739b, assigned select worktree/branch, ownerselect-sort4.
Policyc7ca8c46 read; separate3600Cloudsec/no carry; main00:21–02:21UTC,
finish-only≤02:51. Diagnostic-only general code; binding/harness repair in scope,
general model/kernel semantics repair excluded. Full obligation/hypothesis/pins
and outcome mapping in cloud-build/sort4-native-c1-bound/SESSION-2026-10-11.md.

Prepared143eec6d isolated physical-loc REGISTER/EXEC/DEAD plus AST kind/root/
predecessor diagnostics, unchanged source/translator/kernel decision; callback-
free with/without native opaque MU scratch controls, paired source/MIR/refinement.
Buildb05354e9 failed setup-only old shell phase-ID guard before driver/cases;
VF target/probes NOT_RUN, no semantic credit. Integrity archive5fd8c143,276sec.
1286f1dc repairs exact wrapper ID (not guard removal); newBuild8dc2562a started.

Fresh009ad1c2 /proof=infra f8115f33 terminal SUCCESS/390sec, integrity archive
48b943568293e42d56374af931963a85637fc69c2c62324f15df1ad90c5efc5d verified.
Nativepositive stillVF1 dead228,2; exactphysical203 postlist138 Goto63 afterLabel3,
originalroot131; equalprinted202/204 visited. All6source/MIR/ASTpins match3521;
strict/defaultoff/admission/cleanup negatives retained. MinimalnoMU sameguardVF0,
withunusednativeMU[]VF1deadzero. Constraint localized to frozen model chain;
verbose4 observesentryMUarray_invterm beforecalls but notnamedtrigger.
Entry-beforecalls positive-size assertion/verbose6 follow-up b81f1c3c documented
before dispatch; same frozen semantics, no assume/proofcredit or C4 extension.
Currentcharge1076/3600. Full details FRESH-009AD1C2-REVIEW.md/sessioncard.

Final9ae319b8/b81f1c3c diagnosticSUCCESS354sec, archivef23156ad5744bace48a0dd1c36b4eae7a2e05c672787331539644298fdc70466 integrityverified. BothnamedMUsizeaxioms
trigger during implicit entryarray_inv beforebody/calls; firstpositivequery
passeswithMU/failswithoutMU. Nativepositive stillVF1 physical203; all6program
pins/8pairedsupport/strict/admission/addresscleanup controls retained. Established
frozen MU/struct model limitation; no authorized binding-only repair. C1INCOMPLETE,
connectedC4NOT_RUN; generalmodelrepair notimplemented. Ready maintainerblocker
and END-CHECKPOINT-2026-10-11-ZST.md recordscope/pins/commands/exactnode/cause.
SessionCLOSED1430/3600, unused2170 retired/no carry; all4buildsterminal/accounted/
downloadverified, active/reservations/requestempty, v2preserved, profileclosed.
Hourprogress01:21UTC thencheckpoint/pushcontinued; noautoresume.


## 2026-10-11 Rust ZST size repair session, first gates

Policy c7ca8c467aecf10a4b53039372ee97714f854ee3; owner select-sort4, new account
3600seconds/start08:33:37/main10:33:37/finish11:03:37UTC, checkpoint69e8ffe.
Buildb1babb85/proof=infra95f181fb: semantic repair permits native MU ZST entry;
sameguard genericpair and postnonzero positivesVF0, entry positivity negatives
assertion-fail, reachableZSTfalse and missingpermission intended refusals; C/C++VF0.
Matrix size assertionspass, missing existing unit alignment lemma call fails14.
C1skipped/C4notrun;339seconds accounted.
[Full review](cloud-build/sort4-native-c1-bound/FRESH-B1BABB85-REVIEW.md).


## 2026-10-11 fresh ZST repair and native C1 PASS

Builded016f05/proof=infraf1e13905: every model gate passes, including nonvacuity
and missingpermissions; nativeC1VF0/196, retainedLabel3Goto63 nowEXEC203 afterzero
assumption withfullnativeposts/unit/free/leak. Normal226/unwind210 falsecontrols
reachintendedassertions; alladmissioncontrolsretained. Exactsource/MIR/AST unchanged.
Profileexperimental/unaccepted; researchguarddoesnotprovecallerorgenericactualZST.
398seconds; total737/3600,2863remaining. ConnectedC4nextinscope.
[Rawreview](cloud-build/sort4-native-c1-bound/FRESH-ED016F05-REVIEW.md).


## 2026-10-11 native C4 capture before binding

Build55f876c4/proof=infra0c1bd9d7: freshmodel/C1 gates retained; actual four-call
native sourcepair/MIR/refinement/preAST captured, intentional beforeproofrefusal.
Full CURRENT native cleanup posts present on normal andeachunwind, not yetproved.
428seconds; total1165/3600,2435remaining. Experimental/unaccepted; no callercredit.
[Full raw review](cloud-build/sort4-native-c1-bound/FRESH-55F876C4-REVIEW.md).


## 2026-10-11 native C4 bound candidate frontend blocker

Buildd128e368/proof=infraa868bfd3: fresh ZST model and native C1 gates pass;
source-pinned C4 normal/readonly MIR/refinement and preAST identities match.
However, C4 positive and all5 false controls stop before admission/postAST at
`complete native AST/HRTB inventory`; classify INCONCLUSIVE, with no proof
negative. Four admission refusals behave as intended; default-off stays
unadmitted with a parse error. Profile remains experimental/unaccepted, with no
proof/caller credit. 466sec; total1631/3600. Independently checked1041
inventory entries. [Review](cloud-build/sort4-native-c1-bound/FRESH-D128E368-REVIEW.md).


## 2026-10-11 native C4 inventory count diagnostic

Build310f38b5/proof=infra736691964: fresh ZST model and native C1 gates pass;
C4 paired source/MIR/refinement/preAST remain pinned. Inventory prints body284,
locals239, projections0, epilogue0, HRTB F:T against stale body gate282; positive
and five false controls stop before admission/postAST, so INCONCLUSIVE, not proof
negatives. Admission controls retained. This is the old a1be12ce candidate, not
corrected 8de4cda/66e266d3; its fresh result is recorded in the next entry. No proof/caller credit.
430sec; total2061/3600,1539remaining. [Review](cloud-build/sort4-native-c1-bound/FRESH-310F38B5-REVIEW.md).


## 2026-10-11 corrected native C4 fragment VF0 candidate

Build3b7431bb/proof=infra8de4cda4: fresh model and native C1 prerequisite gates
pass; C4 corrected 284-root inventory admits, positive four-call fragment VF0
(485 statements), normal plus all4 direct-unwind false controls hit intended
assertions, and admission controls retain intended refusals. Paired source/fullMIR/
refinement/AST identities unchanged. Diagnostic only: external caller is NOT_PROVED,
C1-to-C4 execution NOT_RUN, profile unaccepted and no proof credit. 465sec;
total2526/3600,1074remaining. [Review](cloud-build/sort4-native-c1-bound/FRESH-3B7431BB-REVIEW.md).


## 2026-10-11 actual caller entry: first experiment card (before dispatch)

Owner select-sort4; phase SORT4-ACTUAL-CALLER-ENTRY-CLOUD-2026-10-11.
Checkpoint0f673c4f05b5c04f0704244e93f929c78611e0fa; policy full revision
c7ca8c467aecf10a4b53039372ee97714f854ee3, adopted6726a08d. New account3600
Cloudseconds, start13:54:02/main15:54:02/finish16:24:02UTC; no budget carry.
Lane o26-sort4-c1-current-recovery, unchanged v2 coordinator and limits.

Actual obligation: small_sort_general_with_scratch entry to first direct
sort4_stable at pinned SmallSort line254. Domain is the actual generic signature
with native v/scratch/F/lifetime/thread resources, without selected-path or
nonzero assumptions. Original len<2, scratch.len()<len+16/abort, pointer calls,
scratch cast and sort8/direct/short decisions remain in the runtime prefix.
The explicit diagnostic cut at the call boundary supplies no callee summary.

Hypothesis: the exact slice as_mut_ptr symbol may use the existing typed
metadata-stripping cast after fresh verification of the same-version canonical
body. Only the historical one-symbol own-lane patch is rebased onto our pinned
ZST/C1/C4 chain; all other model/kernel/spec rules remain unchanged.
Rationale and static applicability/trust/gates precede implementation in
cloud-build/sort4-caller-entry-native/CALLER-ENTRY-RATIONALE.md. Independent
static review found no additional permissions or ownership in this rule.

Gates: canonical generic T and MU operations, then real method consumers with
complete generated normal/unwind/free/leak posts, paired full MIR/refinement,
strict lifetimes and physical dead-code checks. Wrong pointer assertion and
missing raw authority must fail at their own assertions. Default-off, malformed,
wrong-source and extra-body controls must refuse before proof. Source-pair,
MIR/AST inventory and tool hashes are recorded fresh; unknown fresh AST counts
are captured before any inventory-dependent binding, never guessed.

Outcome mapping: canonical/component or consumer failure blocks method credit
and motivates only a localized permitted correction. An earlier overflow or
explicit-abort failure in the unfiltered prefix is an OPEN caller obligation,
not an intended negative or caller PASS. If entry resources are derived, proceed
to current native C1-C4 composition within scope/budget with fresh exits and
negatives. No MU-to-initialized-T inverse, artificial sizezero return, supplied
nonzero premise, full caller/sort4 theorem or accepted profile is claimed.
Exact published proof/infra SHA and target identities follow in the fresh review.

First dispatch: proof=infra46ffa84f717d428a5da91ef2f86d9024ede90fcd,
Builda125db66-0204-47bb-964f-c3134d4b6eef. Exact published payload
94a5e50964eb5f15c6e7e84bc4f37f4584aea1d6857a13c7a0caf1cc74c91c19,
532691bytes/179parts<=191;74proof paths/8recipeinfra plus exactcore.
Phase guards/controller/wrapper/driver/manifest agree. All nine snapshot std
inputs retained; new AST inventory captured in Cloud before new inventory binding
(the only new tool rule is an exact pointer symbol). Timeout1200/reserve1260.
No proof verdict until raw target evidence and intended controls are reviewed.

Fresh a125db66 terminalFAILURE/394seconds (archive045e43a1, independent588
file inventory and390textchunks, download integrity verified). Canonical native
T/MU casts VF0/53statements each/all55physicalIDs, real native slice method
consumer VF0/62/all63IDs with full posts. Both assertion negatives reached
line14 at intended pointer predicate/missing array<T>, but classifier wrongly
required AST dump exit0 (dump writes AST then runs the same failing proof).
Unfiltered actual prefix stopped in normal-export at missing semicolon line55;
NO semantic prefix verdict. Collector also lacked accepted=false typed audit
at mandatory allprooflogs path. No caller/C1-C4/model acceptance credit.
Full raw review: cloud-build/sort4-caller-entry-native/FRESH-A125DB66-REVIEW.md.

Second experiment card, before dispatch: same exact tool chain and one-symbol
binding, fix only fixture semicolon, negative AST classification and required
audit publication. All targets/gates rerun freshly. Positive consumer now tests
actual scratch.as_mut_ptr() as *mut T while keeping native opaque MU array/own
resources. One targeted permission-risk control under reachable scratch.len()>=1
first confirms native MU storage and then asserts initialized array<T>; expected
No matching heap chunks at that exact assertion. No inverse or supplied raw
authority. Original helper runtime checks/len+16/abort/direct-sort4 condition
still unfiltered; expected first true obstacle is recorded, never counted as
a negative or caller PASS. No tool-semantic change beyond the reviewed binding.

Second dispatch proof=infra0a61febf105b29dcb89d6fc25ec993bdcfd17e46,
Build1d2237d7-2183-48ff-8aa9-a6c8d29fcd83. Published source payload
3e714aad37c315b3a600a1ab70fa48c21fecaed1e2c08c9227087df3e7cdcac5,
533480bytes/179parts. Timeout1200/reserve1260;394seconds alreadyaccounted.
Precise firstcollector cause: packager accepts root OR allprooflogs audit,
but firstrootaudit lacked Boolean accepted and was rejected as untyped. Both
paths and accepted=false/diagnostic_complete are now supplied. No proofupgrade.

Fresh second Build1d2237d7 terminal collector SUCCESS; target diagnostics
complete, proof accepted=false. Archive9a0aa14a804981b9fed0feca217c706827bab7bda563238bd800221d609d288c;
standard download integrity verified. Conservative374seconds; session768used,
2832remaining. Both actual prefix variants have paired support/refinement and
verifier1 at verified/lib.rs(20,24-32), actual smallsort.rs:230 len+16 overflow
obligation (ptr_len(v)+16<=usizeMAX). Abort and pointer calls are not reached.
Exporter overflow_checks=off; no runtime UB claim and no arithmetic/model
repair in this scope. Canonical T/MU and real casted scratch consumer VF0,
full posts; exact wrong-pointer/missing-array/MU-cast-no-initialized-T negatives
and source/phase/default-off controls pass. This does not prove actualcaller
entry or compose native C4. Public source guard transfer remains OPEN.

Third experiment card before dispatch: proof-only public stable::sort first
T::IS_ZST guard, exact T/F/BufT signature and source-pinned BufGuard context;
cut BEFORE len/likely. Positive asserts nonzero on actual guard continuation,
native source/F/thread/lifetime/type resources and full posts. Two negatives:
false zero-size continuation assertion and reachable ZST-branch assert false,
each expected at its source-derived assertion after paired MIR/refinement.
All pointer/component controls and unfiltered helper prefix rerun. No new
translator/model/spec rule; no transfer of public nonzero into helper.
Rationale written before implementation in PUBLIC-GUARD-PREFIX-CARD.md.
Main static review confirms BufGuard is copied solely as unused generic context,
both method signatures match pinned source, IS_ZST definition is source-pinned,
and negative modifies only ghost assertion. Public source/MIR/AST identity is
captured freshly in Cloud; no inventory-specific replacement uses guessed IDs.

Third dispatch: Buildd352b4a6-d86d-48b4-86ca-cdccb0af4d89, proof=infra
3ed89d79a4d0c389607fac7eb0b3909d7e7d4b28; config
9a9a0cdd5b69160d7e8ccd340191822c81bdb31f04d568f0ef558b0026b369e9;
source payload322b2a2746a4c163368b65f874c04a157ac811cb140669c2f6f73bda0adfe798,
538968bytes/181parts<=191,76proof/8recipeinfra paths. Timeout1200/reserve1260.
Fresh public guard source/MIR/AST/physical IDs required; no old inventory
assumption, no actual helper premise transfer or caller PASS asserted.

Third Buildd352b4a6 collector SUCCESS/389conservative seconds;1157used/2443
remaining. Archiveae39f373baf16748479cb05c0874e5c51536a8a692bfcfd63037778b6e1e9e75
and748inventory/478textchunks independently verified, standard download verified.
Pointer positives/three intended negatives freshly pass; helperoverflow unchanged.
ALLthree public stable guard cases stop before guard at verifier type-resolution
lib.rs(6,8-27), T in BufGuard::as_uninit_slice_mut; paired support passes.
NOpublicguard positive or semantic negative credit. Historical failure retained.

Fourth experiment card BEFOREimplementation: exact public unstable::sort<T,F>
where F:FnMut(&T,&T)->bool first T::IS_ZST guard, cut before len/likely.
This is an actual separate public route, avoids stable's BufGuard fixture
frontend obstacle, and changes no trait/ADT/model/translator/spec rule.
Keep positive nonzero/native-resource/full-post checks and two exact assertion
negatives, including reachable ZST assertfalse; repeat component and helper
gates. The stable public guard and transfer down either actualcallchain remain
OPEN unless freshly proved. No helper nonzero premise supplied.

Final fourth dispatch: Build00e90a4b-b7ed-4b92-8b07-bbf168dbc820, exact
proof=infra4871e8a6b47d9f863d42df802233496a051a7242, config
fb1d06685ea9ac6442eb564f2e90a140ed16b39c83c79a2679449a8049af35a6;
payload3e23cf565b23df66db2f45824834279599df7df62b85ed05a1940a2dc4e876da,
541394bytes/181parts,77proof/8recipeinfra. Timeout1200/reserve1260.
All admission/deadline/transport checks passed before dispatch. No inventory
constants guessed, no newmodel/tool rule, no assumedhelperdomain.

Final Build00e90a4b collector SUCCESS/432seconds; total1589/3600, unused2011
retired/no carry. Archive2c3e5c6870d51c605221f875abf87d7d21e7ef814b53614d2f84fefde7782760,
748/748 inventory and478textchunks independently checked; standard download
verified. Allpointercomponents/fullposts and3intendedpermission/pointernegatives
freshpass; helperoverflow remains actual firstVC bothprofiles. Publicunstable
ZSTfalse assertion reaches exact lib.rs10 Cannotprovefalse; positive andfalse
zero continuation fail unrelated ghost size_of lookup at12, NOsemanticcredit.
Publicprofileprebinding66e266d3, consumerspostbinding21ca026a, no composition.
Establishednextproofnotation std::mem::size_of::<T>() from prior modelgates;
no codefix/newBuild after15:54 maincutoff. AccountCLOSED15:57:57.997385Z, all4
terminal/accounted/downloadverified, ownres/request/unresolvedempty, v2max2
checked, owncloudmanifestdisabled. Checkpoint/reviewpackage/finalfullmanifest
record exactsource/MIR/AST/tool/model/proof limits. No fullactualcaller/sort4
proof or newnativeC4composition; no automatic nextsession.

## 2026-10-11 caller-derived bound session from64922e1e

# Caller bound session — raw review and checkpoint

Initial checkpoint `64922e1e5978b7204a6664e33a9f202aa6eea920`.
Policy revision `c7ca8c467aecf10a4b53039372ee97714f854ee3`; fetched fork main.
Owner select-sort4, existing assigned worktree/branch and lane unchanged.
Start16:25:01UTC; owner extended main to18:55:01UTC afterlongpause,
finish-only19:25:01UTC. Fresh budget3600; actual1449 seconds, unused2151
retired without carry. Four terminal/accounted/download-verified Builds.
Own advisory ready request withdrawn; no own active Build/reservation.
No Actions, merge, upstream publication, external messages or local compiler/proof.

## Separate verdicts

| Obligation | Verdict / exact limit |
| --- | --- |
| Public guard ghost lookup | FIXED by fully qualified std::mem::size_of::<T>() |
| Public guard positive nonzero | OPEN: T::IS_ZST lowers to opaque unevaluated_constant<bool>; no link to sizeof(T) |
| Public false-zero continuation | Intended assertion rejection, does not establish nonzero; both zero/nonzero are unprovable |
| Reachable ZST-arm assert false | Intended assertion rejection at lib.rs10 |
| Actual selected threshold body / const32 | VF0 plus native generated safety-template/normal/unwind checks |
| Two-impl selected/default probes | Selected32/default16 VF0 on experimental source/clauses binding; compiler-resolved target not yet exported |
| False31 / missing Freeze / changed threshold source | Intended semantic assertion / distinct admission refusals |
| Wrong selected impl control (+Copy) | INCONCLUSIVE: compiler export cannot specialize Copy/Clone; no intended admission credit |
| Actual caller transfers bound to selected method/helper | NOT_PROVED / NOT_RUN |
| Helper len+16 overflow | OPEN at lib.rs20; no caller premise supplied |
| Helper abort / pointer order / first-call resources | NOT_REACHED in actual helper proof |
| Pointer-only canonical T/MU + native consumer | VF0, full posts/refinement/cleanup; intended pointer/authority/MU-initialized negatives retained |
| Caller→C4 / full sort4 C5 copies / secondcall / sort8 | NOT_RUN / OPEN; historical guarded C1–C4 credit separate |

Model verdict: frozen inherited experimental/unaccepted. Tool verdict:
threshold-only candidate compiled at5dde9c2f; isolated body/name routing works,
but selection by exact source/clauses remains an unaccepted trust inference.
Proof verdict: local threshold body/probe and pointer candidates only; no actual
caller/helper/C4 upgrade. Positive public guard is not PASS.

## Evidence and causal results

0b7b3e53: qualification fixes lookup, first positive >0 lacks size fact;
negative-zero/ZST false intended; pointer consumer fullVF0; helper overflow.
379098e8: constant32 body VF0; trait probes stop duplicate prototype because
both compiler DefPaths are `<T as StableSmallSortTypeImpl>::small_sort_threshold`.
5a60dd5f: tool build fails OCaml record-kind ambiguity; no final-profile public
or threshold proof executed. Exact source annotation fixed in next candidate.
8fa3210b: source/clauses-bound names preserve both safety templates and both
impl bodies. Selected/default positives and false31 execute intended stages;
public positive fails semantic sizeof!=0 linkage before layout lemma/resource
assertions. Wrong-impl Copy control is frontend refusal, never proof negative.
Archive integrity independently checked: first748, third494, fourth981 listed
files. Standard download verifies each receipt/inventory/text index. Raw archives
are external evidence, not committed generated output. Full IDs/pins/accounting
are in SESSION-RESULT-MANIFEST.json and the ledger.

## Prepared but not executed

selected-branch-cases.rs retains real base guard and same-argument selected
method/helper transfer; explicit cuts exclude later quicksort/sort8/copy work.
selected-branch-binding.patch is a default-off text candidate only, with native
pre-only len<=32 interface and narrow existing abort semantic alias. No Cloud
compiler/source pair, selected target, resource proof, overflow or abort credit.
It requires runner-attested compiler binding; no runner sets that flag. It is
not registered in the runnable driver/recipe. Compilation and further trust
review remain required, including complete decoded clauses/generic lifetimes,
call-graph gates and same-source compiler target evidence.

Pinned exporter serializes raw trait FnDef, not selected impl; traitImpls=[]
because its HIR inventory admits concrete struct self types, excluding blanketT.
Stock pinned rustc Instance::try_resolve is a possible narrow evidence query in
real Freeze-qualified caller TypingEnv. Literal unconstrained quicksort TypingEnv
cannot be silently strengthened. No invented env, general specialization model,
size axiom, ownership bridge or MU inverse is authorized. Source API reading is
not observed compiler selection.

Next permitted action requires a new session/window/account: finish exact
compiler evidence for qualified selected route, admit observed target, integrate
reviewed native interface and run true/false-bound/resource/pointer/unwind gates.
Then prove helper len+16, abort and ordered pointer prefix. Preserve native posts
and direct-unwind/free/leak/dead-code/refinement. Nonzero has separate provenance;
len<=32 alone cannot permit nonzero C4. Public associated-const linkage is an
explicit blocker outside current size-model scope. Maintainer reviews candidate;
select-sort4 retains ownership of caller mission. No automatic next session.

Final draft review: selected-branch call counters lack a final cardinalitycheck;
full T,F callerclauses/lifetimeinventory pending. Candidate is not runnable.
Evidence-only compilerquery candidate uses exact local fixture DefPaths, real
TypingEnv and resolvedimpl source span; uncompiled/unexecuted, no target credit.


## 2026-10-11 19:22:51UTC — compiler binding and helper prefix session

Direct owner continuation from `5ffebdf53cc37b5814fa78ad3acb4081519288d8`.
Policy `c7ca8c467aecf10a4b53039372ee97714f854ee3` fetched/read; local common
policy files identical. Assigned branch/worktree clean at start, own git-dir/index
confirmed. GitHub Actions read-only inspection; none dispatched.
Phase SORT4-COMPILER-BINDING-PREFIX-CLOUD-2026-10-11, own separate ledger3600;
main21:22:51UTC, absolute21:52:51UTC. Existing lane and v2 coordination preserved.

First hypothesis: pinned compiler `Instance::try_resolve` in real body TypingEnv
resolves both actual stable trait calls to Freeze impl in qualified generic caller,
and fallback in Cell<u8> control; unconstrained result recorded separately.
Minimal query inventory includes both actual blanket and Freeze impls, their
real methods/call operands and source mapping; suffix callees may be diagnostic
cuts with no proof credit. Capture full caller clauses, original/resolved args,
InstanceKind, DefIds/impl identity/source spans. Query changes no runtime MIR or
compiler selection; exporter default-off observational patch only. Outcome:
correct complete evidence permits narrow admission design; API mismatch gets
addressed within pinned API scope; unresolved qualified selection is a blocker,
not permission to construct a stronger TypingEnv or general specialization model.

Target later native theorem is qualified T: FreezeMarker, real F:FnMut clauses,
all native source/scratch/F/thread/lifetime/type resources and full normal/unwind
posts. Pure len<=32 only in selected small_sort/helper interface, never root.
Root must derive it from verified threshold32 and actual guard, same args. Helper
must traverse original early return/scratch abort/pointers/branches, preserving
opaque MU and rejecting invented initialized-T permissions. Controls: guard31
semantic assertion, lost source array precondition, bad impl/callsite/evidence
admission, touched pointer/resource/unwind cases. Historical Copy refusal remains
frontend-only. Public IS_ZST/sizeof blocker unchanged; no new size model or C4
nonzero assumption authorized. No status upgrade from preparation.

First two submissions refused at local preflight before reservation/Build creation:
unsorted recipe paths (fixed) then bounded transport exceeded (query-only closure
pruned to actual runtime dependencies). No Cloud cost or proof-negative credit.
Full former proof closure remains committed in cd4ad0b7; re-add required profiles/
patches before selected proof mode. Query compiler inputs/semantics unchanged.

### 2026-10-11 compiler query d071: pinned API setup refusal

Phase SORT4-COMPILER-BINDING-PREFIX-CLOUD-2026-10-11; owner select-sort4. Build `d0710ad2-df8c-418d-8894-fdd9cefe7a6f`, proof/infra `72428327d733abe9fecf73738122a6e32ac4d467`: FAILURE at exporter-build, before query. Pinned API errors: FnDef args Binder, impl_of_method removed, caller_bounds iterator Debug; deny(warnings) parentheses. No selection/proof credit. Exact body TypingEnv preserved in narrow API fix using existing exporter no_bound_vars/impl_of_assoc APIs; added Cloud-only full MIR decode for admission review. Hypothesis: corrected pinned API executes six observations with both impls, selected Freeze/fallback Cell/unqualified generic contexts. No native proof gate yet. Archive SHA256 `76249ea297a295d270c08b8f0da9d49db9f3b52d5d66f0da0f4b1aa4a5fb371a`; full evidence `/tmp/select-binding-prefix-d071-read`, extracted `/tmp/select-binding-prefix-d071-raw`. Conservative charge342s, remaining3258s. This is setup refusal, not semantic negative.

### 2026-10-11 both-impl compiler observation / numeric DefId classifier replay

Build `3aa3d0eb-7f9a-49c1-82ee-6d7acbce01b5`, proof/infra `04c9208d266305b04645b26fcb858916e0f08d94`, exporter patch `38f8276f6fd198d39a4e5fe536c3ce3f5a396cbae5c12f701b4102bc14fbd160`, patched exporter source `57fcd1f44ea58fd21325fa83690eb5f6efbe0f00b28575014ec6ee1b7fff04bb`: exporter build, both queries and MIR decode PASS. Compiler `f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f`, real body TypingEnv PostAnalysis; both original impls retained exact. Freeze-qualified caller resolves both methods to selected impl line46 / methods48,53; Cell fallback to blanket impl27 / methods29,35. Unqualified generic context resolves neither method (`None`), never substituted with Freeze. Raw audit INCONCLUSIVE because cross-invocation Debug clause equality incorrectly compared numeric DefIds of higher-ranked regions. Full DefPaths/binder positions are identical; methods/impls mapped within each invocation. Classifier-only correction preserves full DefPath/TypingEnv/binder structure and ignores numeric indices; permitted isolated replay `/tmp/select-binding-prefix-3aa-classifier-replay.json` PASS with changed DefPath/typing-mode rejected, classifier SHA `1b531ef56d7d4a70bb11e9176138b9599ff1ad19be565d70c1e39ae1485da09a`. Original raw audit unchanged; no new proof credit.

Full MIR structural review: selected root/helper explicit clauses Sized<T>,Sized<F>,FreezeMarker<T>,FnMut<F,(&T,&T)> with two shared bound regions, FnOnce::Output<bool>; impl clauses Sized<T>,FreezeMarker<T>. Threshold substs[T], lateBound0,args0; selected method/helper[T,F],lateBound3,args3, exact reborrow provenance v/scratch/is_less. The compiler TypingEnv additionally retains elaborated FnOnce/MetaSized clauses. Native binding/admission and selected-only correspondence still gated; no proof or bound transfer yet. Archive `f91e69e7a01c77b8491f67050fd30e585a6ce478bf3ad3d695a14297827de06a`; full `/tmp/select-binding-prefix-3aa-read`, extracted `/tmp/select-binding-prefix-3aa-raw`. Charge355s, aggregate697/3600, remaining2903.

### 2026-10-11 native selected-prefix experiment card (before execution)

Obligation: Freeze-qualified diagnostic actual quicksort base-case call pair obtains len<=32 from selected threshold32 and real guard; selected small_sort/helper preserve all native resources and full normal/unwind posts under only pure ptr_len(v)<=32 interface. Root has no bound premise. Original helper order: len<2 return, scratch check len+16 and nonreturning abort, v.as_mut_ptr, len/2, opaque MU scratch pointer cast, original size/length branch order, resource boundary before first sort4. Nonbase/sort8/short-copy and firstcall are explicit diagnostic cuts, no downstream proof credit; no supplied nonzero.

Hypothesis: fresh compiler selection + exact source/MIR/clauses/substs/reborrow admission allows selected native call interfaces, proves arithmetic overflow bound and preserves resources at first callsite. Exact final profile keeps frozen kernel/memory/lifetimes, existing pointer/cast semantics and helper-only intrinsic abort alias to existing nonreturning process abort. Positive threshold-body + canonical T/MU and pointer/resource controls, selected positive and intended false31 assertion / source-array removal at selected call. Evidence corruption controls distinguish pre-verifier admission refusal. Expected negative locations are actual source ghost assert len<=31 inside guard and selected call precondition array matching. Any earlier API/parser/alias/temp/cardinality failure is setup/admission inconclusive, not intended proof negative.

Next mapping: binding/MIR mismatch→close gate and localized matching repair only; full native VF0 + AST/resources review→prefix-only credit, first nonzero obligation blocks caller→C4; real semantic failure→preserve exact predicate and resource/arith lemma within scope, no post weakening. Existing IS_ZST public blocker unchanged and no repeated publicguard matrix. Final-profile source/tool/binary hashes captured in evidence; planned patch `18041de31214f764cc4f46a3560821251fc94fba7bab54c1e971a70c0ae0eb2c`, translator `94c330afd5dbe6f80d0f188d7cdc3187fd08cbe741d2a0d58530a4cb76a1d7e6`, experimental/unaccepted.

### 2026-10-11 723 compiler admission PASS / native setup refusal

Build `723dd8e5-9e88-42fe-9cf1-e33780b1d423`, exact proof/infra `05cb227be53225266ee775643a5d28e96376a94f`: fresh exporter query both selected/default pairs and unconstrained None, normal/readonly full MIR admission and evidence corruption controls PASS. Source-selected-only correspondence certificate generated. Frozen base reconstruct/pre-slice console build PASS. Final selected translator console failed OCaml syntax: `String.ends_with ~suffix=...` uses equality instead of labelled-argument colon; `Unbound value suffix` at translator line555. Controls, selected-only prebinding MIR and native verifier NOT_RUN; no semantic negative/proof credit. Fix only those two labelled-argument colons; exact same obligations/profile semantics, new source/tool SHA and run required. Earlier preflight reductions incurred no Cloud charge. Full checksum-verified archive `/tmp/select-binding-prefix-723-fast`, extracted `/tmp/select-binding-prefix-723-raw`; official evidence integrity/accounting download in progress.

### 2026-10-11 b229 final compiler/control PASS, selected admission refusal

Exact proof/infra8562527b76accbeb2405313d032ccbb6802173a6, Build b22985f8-7aae-4058-9e3e-bae10f222a6f. Query both impls PASS with actual body TypingEnv: qualified pair selected, Cell pair fallback, generic pair None. Complete MIR/clauses/substs/lifetimes and source correspondence PASS; nine corrupt/missing evidence controls refuse before verifier. Selected console compile PASS, final translator cba50fa1ad56b5ec640d2cfbcc67e7867cd7ff6591e3699fc3cfa1317f5528a6, patch ce6b707264d071a4a0a8fa9b05391f152abde5b8f4574167e3de9d212802c7b4, native console d9fe5a32e5dc7247d8084945848ff0e471104dccbf5e39fe1fb90717d162bd2f. Frozen kernel/memory/resource semantics unchanged. Canonical T/MU positives VF0/53 statements each, consumer positive VF0/63, threshold32 full normal/unwind posts VF0/51; all leak checks reached and paired refinement/export passed. Pointer negatives at intended verification locations: wrong pointer line14 inequality, missing raw rights line14 array<T>(unrelated,1,_), MU cast line17 array<T>(strip_pointer_metadata(scratch),1,_) absent. These are isolated exact-profile controls, no actual helper/caller credit.

Selected-positive paired export/decode/refinement PASS, then admission refused literal MIR temporary mismatch: normal args_17,_18,_19 vs query/readonly_16,_17,_18; exact reborrow roots unchanged v/scratch/is_less. Extra normal VeriFast_ghost_command for guard assertion shifts temps. Selected verifier, full AST/native-post graph audit, false31/source-array semantic controls NOT_RUN. Gate remains closed; refusal not semantic negative. First open obligation is exact mode-specific mapping plus observed AST mode; next authorized session may repair narrowly without loosening provenance/clauses/identity. Main deadline passed before result inspection; no new experiment or Build initiated thereafter. Public IS_ZST/sizeof and nonzero obligations unchanged; no ZST return/nonzero supplied, no C4 composition.

Archive SHA6c0f0c6ccebe5d3dd0fbdb5d91a4cdcdadc8fd47d6510a7853e8ea736dc75c3f; raw /tmp/select-binding-prefix-b229-raw, official verified evidence /tmp/select-binding-prefix-b229-read. Charge420s; aggregate1521/3600, remainder2079 retired. Four terminal Builds, no own unresolved/reservation/request. Model experimental/unaccepted; tool compiled but admission closed; proof local threshold/pointer only. Full per-stage identities, raw hashes, controls and prior-session preservation in SESSION-RESULT-MANIFEST.

## Session #2 / mode-specific MIR admission — 2026-10-12 MSK

Policy 6e1a8e59c56669abe5e6ec2013478e45ed2cc267 adopted in e92176fd;
checkpoint 8b6545094fea0ea25079bda51505d7f990ef2d1a. Start21:49:02 UTC,
main23:49:02, finish-only00:19:02; fresh3600 conservative seconds, owner select-sort4,
one existing o26-sort4-c1-current-recovery lane, v3 max3/one owner-ledger.

Actual obligation: stable quicksort threshold/selected method/helper entry bound
through len+16, then helper prefix/native C1–C4 with resources from caller.
Initial falsifiable hypothesis: the b229 refusal is solely the ghost-command
normal-local shift, not differing original argument provenance. Exact query
both-mode caller16/17/18, selected-positive normal17/18/19 and readonly16/17/18;
helper5/6/7. Per-case/mode maps are independently pinned after observations,
never arbitrary local sets/unions. Negative-case maps must first be observed
in Cloud; unobserved maps refuse binding. Replay saved immutable b229 source/MIR
and synthetic wrong-input-source, wrong move/projection/temp/clauses/binders
controls before dispatch. Retain old verdict and separate replay/hash identities.

Authorized narrow auditor/translator change: validate exact map and one direct
mutable reborrow from each original formal, retain raw maps, compare semantic
call graphs only after map admission. Original callee, full clauses/binders,
substs, source identity, exact edge/cardinality checks remain. No new trusted
memory/layout/alias/kernel rules; runtime/proof assertions/posts unchanged.
Before replacing translator literal operands, Cloud capture-only diagnostic
observes translated Ast.Var operands and paired MIR for all three cases;
compiler binding flag is set only by successful runner gate, never manually.
Capture grants no proof credit. Existing strict translator rejects mismatch
and prints incoming operands at the translated call; missing maps remain refused.

Fresh final-profile regression set: six both-impl compiler records with original
TypingEnv/Instance/args/clauses, query corruption/source/MIR controls; canonical
T and opaque MU, as_mut_ptr positive/wrong-pointer/missing-rights/MU-cast negatives,
actual threshold body; selected positive/false31/source-array. These exercise
every modified binding and inherited pointer/resource interface; unchanged
public-guard experiment is excluded. Old PASS is not transferred. False31 must
fail its actual assert len<=31, source-array its source-array call precondition;
earlier stages are NOT_RUN/inconclusive. Native full normal/unwind/F/thread/
lifetime/source/scratch/free/leak/dead-code posts stay enabled. Target C1–C4
requires normal plus all four direct-unwind posts, MaybeUninit remains opaque.

Domain: selected diagnostic Freeze-qualified T and FnMut F, unrestricted
generic caller applicability OPEN; generic None has no permissible Instance.
No supplied root bound/nonzero, no size guard, no IS_ZST/sizeof repair. PASS
permits original helper traversal in scope; causal model/resource failure is
checkpointed and assessed, never bypassed. Profile remains experimental.

Session2 capture hardening rationale (before next dispatch): retain exact source/
clause/subst gate and operand observation, then explicitly refuse on runner-only
SORT4_SELECTED_OPERAND_CAPTURE_ONLY=1 before selected-call binding. This
diagnostic-only rejection avoids relying on an operand mismatch to stop the
console before its verification engine. Default-off proof semantics/callgraph
remain unchanged; missing/malformed mode refuses. No kernel/console changes.
Next capture will use independently admitted observed negative-case MIR maps,
retain normal/readonly maps and actual Ast.Var evidence, with zero proof credit.

Session2 Build1:5bd2b7c3-ec17-45aa-a60e-7bdda819233c, proof=infra
83b1d4451910902a8d6ef931a05e32b8d46e3624,435s, verified archive
70aa987852c8129e409dda94f4b4dddc6e3bd4447f7502edcfe0e806de016071.
Fresh compiler admission, paired MIR/refinement all three fixtures, selected
console build completed. Positive intermediate Ast.Var normal caller17/18/19
and helper5/6/7 observed; literal16/17/18 refused before selected proof.
No full selected AST/post audit or selected proof credit. Capture-only expected
collector false/Build FAILURE; evidence complete, run_exit0. Saved-data replay
5BD2 independently checks positive/false31 normal17/18/19, source-array
normal21/22/23; all readonly16/17/18, all helper5/6/7, all source roots unchanged.
Eight causal MIR negatives per case refuse, including wrong original source.
Old capture verdict retained separately from replay; raw evidence unchanged.

Build2 hypothesis: with negative-case exact normal/readonly maps now pinned,
the same console translates their root Ast.Var operands consistently with
those admitted maps. Capture only false31/source-array to observe actual mode
and operands; explicit translator diagnostic stop prevents verification.
Do not repeat positive capture. Exact full source/clause/subst/binder/reborrow
and query/consumer checks still precede flag; no operand set union. If both
observations match, align translator exact source-MD5-specific literal operands
and run all fresh selected proof/regression gates. Any earlier failure keeps
A1/A2 OPEN and is classified. Main23:49:02UTC/absolute00:19:02;3165s remaining.

Session2 Build2:b8779246-8ef6-4a9e-922d-27e8747a8089, proof=infra
ce1b9c19d9f865698aa9fcf1eb1f2e0cee5120b2,407s, archive
 e2d406312435677bf33316861cd26333cd042ba932a830cc12848ad7deabb78f.
Official source/config/inventory/text chunks verified; evidence complete.
Both negatives admitted their full mode maps; intermediate normal Ast.Var
false31=17/18/19, source-array=21/22/23, helper both5/6/7. Both diagnostic2
at explicit capture stop; no AST/verification/proof credit. Old verdict remains.
842/3600 accounted;2758 remaining; no active own build after accounting.

Before fresh selected proof: source-MD5-specific operand gate now uses independently
Cloud-observed normal maps for each exact case, never union or arbitrary temps.
Readonly and source-origin maps remain independently validated. Translator
source/callee/subst/full clauses/binders/interfaces/abort/three-edge gates and
normal/unwind resource posts preserved; kernel/prelude/layout untouched.
Regression scope remains the seven final-profile canonical T/MU, pointer rights
and actual threshold controls plus three selected cases, fresh compiler evidence,
paired source/MIR/refinement and full post AST. Their sufficient coverage rationale
is the unchanged preceding session2 gate plan. Public-guard repeat excluded.
Classifier correction: -dump_ast_with_locs also executes verifier. Positive
requires diagnostic0; intended negatives require diagnostic1 AND verification1
with identical first causal error, exact intended source line, full mandatory
post AST and immutable paired source. Diagnostic2/mismatched first failure refuses.
Eleven isolated synthetic classifier negatives per case and thirteen AST controls
pass; replay final maps preserves old b229/b877 verdicts and input hashes.
Hypothesis: exact binding now reaches actual selected threshold/guard transfer
and original helper len+16/abort/pointers without supplied root bound. Positive
must pass full posts; false31 must fail assert31; missing source must fail array
call precondition. Earlier causal refusal is inconclusive, not an intended negative.
Profile experimental/unaccepted; Freeze diagnostic cannot discharge unrestricted
original generic applicability (None unresolved). No nonzero or scratch rights
created by cast; any resource/model boundary is checkpointed without bypass.

Session2 Build3:132d75f9-61ae-4bfa-9f63-ac7fbc0e56a1, proof=infra
3490c28761fc21ac9af82a4b7350545992a48df4,428s, archive
9a2d703a27b1e9487a24c839360f4ceb2636a11a5ce1c83921a817500e3bbf6b.
Official hashes/config/source/inventory/text logs complete. Exact binding compiles,
positive paired source/MIR/refinement and full AST present. Verifier invocation
exit1 at verified/lib.rs(13,8-18): Duplicate type parameter ''_'. AST trait
small_sort declares Self and three repeated '_ lifetimes, lacks F parameter
while its parameter/resource type refers to F, and reference types name three
separate '__35/36/37 regions. This is a translator trait-declaration interface
blocker, before symbolic caller/helper proof; no bound, arithmetic, abort or
C1-C4 credit. No generic semantic rewrite is authorized by local-map repair.
Auditor itself then refused two threshold Func records: bodyless stock prototype
plus explicit-post implementation definition. All seven final-profile controls
were executed before selected positive (full report follows raw review).
Negative selected cases not invoked because that audit refusal stopped runner.
1270/3600 used,2330 remaining; own build/reservation closed, ready request retained.

Before Build4: parser-only distinction of precisely one threshold prototype and
one definition, identical header fields, separately preserved prototype posts,
and one implementation for every other selected function. Exact callgraph edges
still three, all post/resources checked; duplicate definitions/prototypes or
header mismatch refuse. Replay on copied saved AST, not live evidence; no proof
credit. No translator/profile/source change from Build3. Hypothesis: after this
collector correction, every selected case executes its existing fresh proof
invocations and full AST audit. Expected observed blocker is duplicate trait
lifetime parameter; this is deliberately an inconclusive diagnostic at frontend,
not a successful false31/source-array negative. It completes the requested fresh
cases and exposes full error/AST identities for the minimal reproducible blocker.
No repair/removal of trait declaration, binder rewriting, F omission repair,
post weakening, nonzero premise or public-guard repeat is authorized here.

Session2 final Build077360e8-b6d7-4d79-a101-dd4792ea328f, exact proof=infra
8763e495475505b247e1a354ec805bd5ab4b4558,416s, collector SUCCESS/evidence complete;
archive f9c37561d7760dffe9b4e512389fe317214d4fc4f39129c5f1309209a1bc5ace.
All3 cases ran paired support, dump and verification; full normal/unwind resource
post AST and strict3edges PASS structurally. Each first/only error is duplicate
trait parameter at13; neither caller/method/threshold/helper is verified.
Negatives correctly inconclusive, not their intended predicates. Seven fresh
regression gates genuine (four VF0 candidates, three intended rights/assertion
negatives). Critical/modified sources,RSSpec and console identical to Build132d;
profile experimental/unaccepted, equality to prepatch posts RAW_REVIEW_REQUIRED.
No A1/A2 upgrade, bound/helper/firstcall/C4 normal/four unwind NOT_PROVED/NOT_RUN.

Closed session#2 at2026-10-11T23:48:10.935492+00:00,1686/3600 used,1914 retired,
remaining0; old2079 retired unchanged. All4 Builds accounted and official
archive/config/source/inventory/text hashes verified; ownreservation/request none.
Runnable manifest disabled. No new experiments in finish-only period; docs/evidence
checkpoint only. Mandatory A1/A2 review before third; precise trait/F/lifetime
blocker and shared checked trait-contract plus opaque-MU C4 alternatives in
END-CHECKPOINT-2026-10-12-SESSION2.md. New generic/trusted rules require owner
scope decision before implementation; no third phase authorized, score unchanged.

### 2026-10-12 — A1 approach decision package, DESIGN/UNRUN, Cloud 0

Owner-assigned read/design window after two closed select-sort4 proof sessions;
initial a22282dac3765c7d9948e6edfb0ae74102a4280b, T0 00:18:36Z, main01:18:36Z,
finish-only01:48:36Z. Existing ACK of policy6e1a8e59... confirmed, no re-adoption.
No tool/proof patch, compiler/extractor/verifier or dispatch executed. Counters
and accounts unchanged. Own status, existing checkpoint and this log updated.

Prepared [owner package](cloud-build/sort4-caller-entry-native/A1-TRAIT-CONTRACT-REVIEW-2026-10-12.md)
plus exact-source translator rationale and fixture plan (all UNRUN): common
threshold16..32 checked against both actual impls, genuine generic trait call
transfers original guard to n<=32/n+16<=48; full native normal/unwind interface
keeps unrestricted T/F, callback panic and opaque MU. Full small_sort theorem
requires both actual bodies and dependencies, no assumed summary. A1 route
change needs owner decision because generic None is not a selected Instance.

Static pinned source finding: RequiredFn schema f760:878 has no method F/generic
clauses; exporter f760:819 serializes printable binder names independently of
inputs. Representation requires narrow required-item exporter/schema/decoder
and translator work, separately from safe required-method contract and both-impl
conformance. Exact final saved translator independently hashes e484d9...d807e64.
No kernel/layout/alias change suggested. First proposed Build threshold/interface
only with actual both-impl bodies and bad-impl/binder/region/F/source/binding
negatives, full posts and seven regressions:900s timeout,960s reservation AFTER
authorization. No fresh proof credit from this package/static checks.

A2 proposed prefix resource envelope retains exact opaque MU frame through normal
and four direct-unwind exits, with CURRENT initialized source/F and closure of
all borrow debts. ZST source split/borrow protocol still unproved; len8–15 does
not derive nonzero. Full destination writes/copies need further proof; no MU→T
bridge. A1/A2 NOT ACHIEVED, score15% unchanged, all prior verdicts preserved.
Own reproducible translator scratch cleanup and retained evidence recorded in
the existing session2 checkpoint. Next: owner/maintainer review, not execution.
Design closed00:42:16Z within main window. Static link/fence/hash/whitespace checks
pass; compact explorer review fixed actual AST no-redirect gate plus forced
legacy clause-ignoring redirect control. P0 arithmetic is explicitly a caller
lemma; actual helper transfer and full small_sort proofs remain P2/UNRUN.


## 2026-10-17 — A1 checked trait-contract bounded session (ACTIVE / UNRUN)

Direct owner authorization: R/C/G only, first matrix in
A1-FIXTURES-UNRUN-2026-10-12.md; common contract route accepted, A1 not closed.
T0 00:28:49Z, main02:28:49Z, finish-only02:58:49Z, owner select-sort4,
new ledger BUDGET-A1-TRAIT-CONTRACT-2026-10-17.json:960seconds, one900s Build
plus60s queue reserve, no carry/retry. Initial proof/infra candidate base
39c73ebb391ec9432644338f84f3cfd453d990a0. Coordinator v3 not modified.
Policy2026-10-17 Evidence Brief read; local instruction changes preserved.

Semantic rationale/gates recorded before implementation in
A1-RCG-SEMANTIC-GATES-2026-10-17.md. Independent source review recorded in
A1-RCG-INDEPENDENT-REVIEW-2026-10-17.md; corrected kernel EnsuresAsn analysis
in A1-KERNEL-CONFORMANCE-SOURCE-REVIEW-2026-10-17.md. Code drafts add required-item
transport, threshold common contract, generic no-redirect path, staged admission
and source/tool-bound receipt services. Review found generic-use identity,
alpha-renaming, argument-order and signature-shape issues; in-scope fixes underway.
No local compiler/verifier/extractor, Cloud submit or raw evidence read.
All first-matrix proof gates NOT_RUN; no Brief exists for a new Build.
Synthetic service checks are not threshold/interface proof. A1/A2 and profile
status unchanged. Final checkpoint/account to be appended at session close.


## 2026-10-17 — A1 R/C/G common checked contract, NO-GO checkpoint (без Build)

Owner select-sort4; source candidate `bc2af77223428df14b61300a81eb99541c49723e`;
сессия 00:28:49Z–01:46:25Z, до основного deadline 02:28:49Z. Прочитаны
WORK-POLICY 2026-10-10 и owner Evidence Brief 2026-10-17; pre-existing локальные
инструкции сохранены вне commits. До реализации записаны semantic rationale
и gates; R/C/G source patch прошёл независимый review с локальными исправлениями.

Первый установленный blocker запуска — отсутствует полный P1 native small_sort
interface gate: required/impl signatures, scoped Self/F/regions/clauses и полные
native pre/returning/unwind AST под корректной alpha map. Threshold/call-shape
gate этого не заменяет. Полное выполнение/классификация всех 26 строк и exact-pair
N-false31 receipt также не интегрированы; runtime900s feasibility не проверена.
`run(a)` остаётся закрытым preflight; source profile `fbdb28dc43582b9b9bb695929f0b8200148761ed66c2c7b78def0df1da7b75d0`
имеет cloud_build_enabled=false и null proof/infra run pins.

Локально 96 synthetic parser/classifier tests PASS, Python AST parse и exact
R→C application/result SHA checks PASS. Это только сервисные source/structure
results. Обе actual threshold bodies, generic proof, P1, все N-* и свежие R1–R7
**NOT_RUN**; Brief gates отсутствуют. Source claims не повышены до proof.
Ни Cloud request, ни Build, ни Actions не запускались; raw logs/archives и
Cloud Logging не читались. Расход **0/960 Cloud s**, Builds **0/1**; новый
счёт закрыт NO-GO, 960 unspent retired без carry. Исторические записи неизменны.

[Точный checkpoint](cloud-build/sort4-caller-entry-native/A1-RCG-CHECKPOINT-2026-10-17.md)
фиксирует pins, исправленные focus/receipt gates и следующий конкретный шаг:
полный P1 AST mapping/equality gate, затем сквозная матрица и N-false31 lifecycle,
независимый review и exact run pins в новом разрешённом окне/счёте.
Threshold/interface hypothesis не подтверждена; A1/A2 NOT ACHIEVED,
index 15%, experimental profile UNACCEPTED. P2/A2/ZST/resources/copies/sort8
не входят в результат или разрешение этой сессии.


## 2026-10-17 — A1 continuation, independent source review complete / Cloud NOT_RUN

New owner account960s/one900s Build, start09:58:22Z/main11:58:22Z/absolute12:28:22Z;
prior960 retired unchanged. Checkpoint1cfb60e0/candidatebc2af772 retained.
Implemented full P1 compiler/binder/signature/native-tree observation gate with
separate R-only ORIGINAL impl reference, all26 live adapters/classifier/admission
routes, own-pair false31 two-body receipt ordering, bounded exact-pair support
reuse and existing-lane/recipe/phase binding. Independent Luna High review fixed
localized findings;137 synthetic tests and55 final targeted tests PASS, static
pins/closure checks PASS. No local scientific execution, no Cloud Build yet,
no raw evidence read. All actual matrix/proof gates NOT_RUN; no Brief yet.
See A1-CONTINUATION-2026-10-17.md and independent review for source pins and
runtime estimate. Next authorized step: publish exact pins, preflight, one Build.


## 2026-10-17 — A1 continuation: sole Build, Brief reporting limitation

Source P1/all26 routes/false31 own-pair lifecycle completed, source-reviewed and
published `9678ddf631902765d7013f5ed1b9fd05159463a6`; binding `801dca35`.
Full source preflight PASS:33 infra/105 proof paths,158 shared Git objects,
502283-byte payload,168/191 substitutions, unchanged coordinator bounds.
Cloud Build `57ea65a3-475e-4370-810c-19ad36803174`: FAILURE,330s charged (329s
execution),1/1 authorized Builds, unused630s retired. Existing account untouched.
`smallsort-brief` retrieved: VERIFIED_ARCHIVE_AND_INVENTORY, source
NOT_ACCEPTED_AS_REPORTED, run exit0, evidence_complete=True, but no aggregate
or representative cases. P1/all26/false31 actual states and scientific causal
blocker UNESTABLISHED. No raw evidence read/downloaded, no proof credit.
Stop reason: external A1 reporting gap; need detailed Brief or separately
authorized administrative audit before evidence-based scoped diagnosis.
See A1-CONTINUATION-CHECKPOINT-2026-10-17.md and machine result for all26 rows,
lifecycle, pins/account/next step. Full A1/A2 and other excluded targets stay open.


## 2026-10-18 — authorized minimal unused_mut R candidate

Start d2444867/remote exact; T008:37:29Z main10:37:29Z absolute11:07:29Z.
Updated Brief confirms old R-only build exit2, two unused_mut,26NOT_RUN.
New full R patch preserves old file and removes only approved two mut tokens;
exporter c29d0d46…b463ad verified through full43-patch source chain/R/C maps.
New ledger960s/max1 Build900s/no carry; old330/960+630retired untouched.
New authorization explicitly bound to unchanged C protocol, no semantic input
changes beyond approved fix.10+4 isolated service/reuse checks PASS; independent
Luna High source review has no blocker. New Cloud candidate NOT_RUN pending
published-source closure/config preflight. Source/synthetic PASS is not proof.
