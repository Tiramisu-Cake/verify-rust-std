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
