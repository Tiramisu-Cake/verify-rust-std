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
