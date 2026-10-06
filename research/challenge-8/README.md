# Challenge 8 research

We are developing our own solution. Existing PRs are references for requirements,
review feedback and performance observations; their proof code is not imported.

For agent onboarding and autonomous GitHub-only execution, read
[AGENTS.md](../../AGENTS.md) and [the agent runbook](AGENT-RUNBOOK.md).
The owner's server is for editing and orchestration only; do not build or verify there.

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

In the fork's Actions tab, enable workflows if GitHub asks, choose **SmallSort
research**, click **Run workflow**, select `challenge-8/research`, and select
`proof=insertion_outer_invariant_4` and `budget_minutes=90` for the next experiment.
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
experiment has no verification result yet.

## Approved alternative feasibility probe

`verifast_insert_tail_probe` prepares exact live std source spans for CopyOnDrop,
insert_tail and insertion_sort_shift_left in an isolated crate, then invokes
repository-pinned VeriFast 26.09 and its refinement checker on hosted Actions.
See [probe design and limits](verifast-probe.md). Only insert_tail receives a
non-vacuous `req true; ens true;` diagnostic contract; because this lacks the
unsafe pointer/ownership requirements it should fail, and no proof is claimed.
The goal is to expose a concrete frontend or first ownership obligation without
ignoring unwind paths or adding assumptions. This is preparation for evaluating
arbitrary-length separation-logic proofs, not a replacement verified algorithm.
The Kani pin and completed bounded evidence remain unchanged.
