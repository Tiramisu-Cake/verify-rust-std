# RAPx applicability and detector-coverage phase

Prepared and approved for the next agent on 2026-10-06 after the owner accepted
the [remaining-tools assessment](ALTERNATIVE-TOOLS-ASSESSMENT.md) and requested
the documentation update and continuation prompt. Entry research HEAD:
`b7416c18035c714258e2a476eebdfa1609f7f66c`, fork
`Tiramisu-Cake/verify-rust-std`, branch `challenge-8/research`.

## Current gate-A continuation

**CLOSED / NO-GO — owner-authorized continuation on 2026-10-06 completed.**
Entry expected and actual HEAD `1fc89566800f8152d218de7f9a757f665626f220`.
Two new runs used; second run37508888778 at929ea803 analyzes all six controls.
Both misaligned alignment-eight ZST copies are SOUND with Align ProvedByRule.
Manual paired-contract/diagnostic/MIR audit confirms the miss; automatic
classifier remains fail-closed/unmapped for the actual renderer. See
[complete results](RAPX-APPLICABILITY-RESULTS.md). Stop before B/C, no active run.
The authorization below is preserved as the completed continuation's scope;
unused slots do not authorize further replay, tool changes or full sort4.
The latest owner instruction supersedes the earlier stop only for preparation
and **gate A**. Preserve the earlier CLOSED / INCONCLUSIVE result and two runs
as historical evidence in [results](RAPX-APPLICABILITY-RESULTS.md).

Separate budget: **up to four NEW GitHub-hosted Actions runs**, each at most
90 minutes including setup, one active run. The earlier one-technical-correction
limit is replaced by this overall new budget; ordinary setup/runner/classifier
repairs are autonomous. No blind retries; each changed source gets a new SHA/run.
The older budget below describes the initial session, not this continuation.

Authorized corrections: do not require `.cargo-checksum.json`; retain exact
package/version/archive SHA256/VCS/lock checks and compare installed sources
with the verified archive and pinned upstream. Use `--debug-contracts` ONLY
in separate contract-printing diagnostics: pinned driver.rs returns from that
branch before verification. Real verification must omit that flag. Feed the
classifier corresponding separate logs, bind the precise function/checkpoint/
Align(src/dst), reject missing/unknown/unsupported/unmapped evidence, and test
the classifier executably only on Actions. Statically inspect all remaining
setup/analysis paths before the first dispatch and repair related issues together.

Run the six existing gate-A controls; preserve actual target/path/obligation
evidence. Never execute negative fixtures as ordinary programs. Pins, trusted
semantics, std runtime and meaning of the predicates are frozen. All builds,
analysis and executable tests stay on GitHub-hosted Actions.

Stop after a substantive A result or budget exhaustion, **before B/C**. Even
a sufficient A pass only permits READY FOR NEXT DECISION (A only), not B/C
execution. A confirmed missed negative or required semantic change gives a
scoped NO-GO/next decision; setup/unknown/ambiguous evidence gives INCONCLUSIVE.
No verifier patch/upgrade, whole-sort4 proof, alternative tool or external
publication is authorized. Current checkpoint: [STATUS](STATUS.md).

### Historical initial-session closeout

**CLOSED — INCONCLUSIVE on 2026-10-06.**
[Results](RAPX-APPLICABILITY-RESULTS.md) preserve two setup failures: planned A
and the one shared technical correction. No fixture alignment obligation was
checked; B/C NOT RUN. The unused later-gate slots do not authorize more A
retries. This document preserves the approved scope/profile/gates, not new
authorization. A new preparation/A retry needs an owner decision; earlier
phases, full sort4 and verifier development remain closed/unauthorized.
Current checkpoint: [STATUS](STATUS.md).

## Question and target boundary

Can the unchanged integrated RAPx profile analyze the generic memory operations
and callback/panic behavior needed by actual `sort4_stable<T,F>`, with observable
obligations for all four required UB categories and without hiding unsupported
cases? Target source remains
`library/core/src/slice/sort/shared/smallsort.rs`, blob
`e555fce440872898e47fd5114f32eb15401d07df`.

Keep the full target [normal and five panic posts](SORT4-CONTRACT.md) on the
experiment card: current source state, exactly one ownership sequence, valid
storage/permissions, callback state and frame, legal interior effects, and raw
scratch with its correct initialization state. Normal return initializes copied
representations without creating a second independent drop right. All five
callbacks precede sort4 writes; panic preserves the state after legal callback
effects, not an invented rollback. Safety has no Copy/Freeze/purity/no-panic
restriction; ordering premises remain separate.

These posts are the applicability yardstick. Microfixtures test particular
mechanisms and need not already prove all posts. Every partial result must say
what it does not cover. Equivalent semantic evidence is acceptable; do not impose
VeriFast-specific tuple predicates, tokens or recovery syntax on RAPx.

## Frozen executable profile

- RAPx **exactly 0.7.50**, Rust **nightly-2026-02-05**, based on
  [the existing integration](../../.github/workflows/rapx.yml).
- Reviewed source tag v0.7.50 resolves to
  `7d61d9377033c48a4df8954f34cc076e97a93816`. Hosted installation must use an
  exact package requirement (for Cargo, `--version '=0.7.50'`), retaining the
  package lock where available. Record resolved dependencies, executable version,
  toolchain, artifact/source hashes and package VCS metadata where available.
  Check that the installed relevant checker/call/contract sources match the
  reviewed profile. Do not assume a package and Git tag are byte-identical.
- Explicitly select the pinned Rust toolchain for installation AND analysis;
  do not accidentally inherit the runner's active default toolchain. Freeze and
  record target/sysroot/contract sources and analysis flags. If a diagnostic uses
  toolchain std instead of the repository target, state that boundary; no actual
  repository-body claim follows from it.
- No custom parser, MIR/AST rewriting semantics, kernel, prelude, pointer/alias/
  memory model, call summary, property-checker or refinement changes. No historical
  VeriFast patches. RAPx 0.7.54/upstream HEAD is source-review context only, not
  an authorized fallback. Do not silently update global pins or tool workflows.

If this exact profile cannot be installed or matched, record the causal setup
blocker. A newer version or custom tool fix needs a new decision.

## Ordered gates

Before each gate, append the experiment card required by the runbook: falsifiable
hypothesis, exact domain and assumptions, target/partial posts, cases, expected
predicate and source location, coverage evidence, profile, budget and decision map.
Use isolated small cases so one frontend/helper failure cannot mask the controls.
Advance only after the preceding gate passes. A decisive critical miss or essential
unsupported mechanism stops later executable gates; mark them NOT RUN.

### A. Alignment, with the concrete ZST concern first

Hypothesis: the intended `copy_nonoverlapping` alignment obligation is generated
and distinguishes valid from invalid pointers, including zero-sized types with
alignment greater than one.

Prepare paired aligned/misaligned cases for `#[repr(align(8))] struct Z;` and
ordinary non-ZST controls. Construct pointers so there is no earlier invalid
reference or unrelated failure; identify the first intended unsafe operation.
For the ZST negative, empty byte ranges are not an overlap violation: the intended
failure is source/destination alignment at the copy or its corresponding check.
Log the concrete size/alignment and exact checkpoint. Do not add an independent
manual alignment assertion that substitutes for RAPx's required safety coverage.

A negative counts as detected only at the intended predicate and location. A
generic `UNSOUND` label, setup failure, unsupported intrinsic or unrelated pointer
failure is inconclusive for the alignment hypothesis. A valid control must be
analyzed and proved, not skipped. If the invalid case is actually reported SOUND
with the relevant obligation skipped or incorrectly discharged, preserve a minimal
reproducer and close this profile's gate as NO-GO. Do not patch the checker.

### B. Generic copying, initialization and the four UB categories

Only after A passes, assess an actually analyzed generic helper with valid source
storage and disjoint writable `MaybeUninit` destination. It must not require
`T: Copy` or `T: Freeze`. Retain one logical owner; scratch representations must not
be independently dropped. Use a destructor-bearing concrete control to expose
accidental duplicate ownership, while keeping it separate from generic evidence.
Do not infer generic support merely because Rust accepts the signature.

Use valid controls and deliberately invalid counterparts to inventory the required
checks. Existing A alignment cases count toward this inventory; do not rerun
unchanged cases merely to inflate the count.

| Required property / operation | Intended negative boundary |
| --- | --- |
| Dangling, bounds and alignment | Access through a dead/out-of-range pointer; A supplies the alignment pair. Distinguish the exact cause. |
| Uninitialized reads | Read an uninitialized typed value. Raw copying of uninitialized bytes alone is not the negative. |
| Mutating immutable bytes | Write to immutable storage through a raw pointer; distinguish legal UnsafeCell mutation. |
| Invalid values | Produce/read an invalid scalar representation, such as an invalid bool, at the intended operation. |
| Copy non-overlap | A nonzero-size overlapping copy violates its own contract; keep separate from cross-copy value preservation. |

Record which claims arise from automatic operation checks and which from user
annotations. Do not assume the tested property as a fixture precondition, use
contradictory premises, or manually assert each defect to manufacture detection.
Do not require initialized padding or already-initialized destination values as
a way around missing raw-memory support. Numeric address equality alone is not
evidence about provenance, borrowing or ownership. If a required mechanism is
unsupported, skipped, unknown or misses a negative, report the limitation and stop
the route; a positive generic copy fixture does not prove full ownership safety.

### C. Comparator effects and normal/direct-panic behavior

Only after B passes, test the actual first-callback shape
`is_less(&*v_base.add(1), &*v_base)` with unrestricted `T`/`F`, four initialized
source positions and separate raw scratch. Audit its source correspondence and
direct unwind shape; this is a prefix fixture, not a whole-sort4 proof.

Include a legal stateful/interior-mutating comparator control and normal/panicking
variants. The proof obligations must use the resulting current state. Check
whether arbitrary `F` has a justified effects model; a fresh Boolean return with
unchanged reachable memory is not sufficient. Concrete comparator bodies may
diagnose this gap but do not establish arbitrary-F coverage.

Add an isolated synthetic negative whose invalid memory operation is reachable
only on a cleanup/unwind path, with a valid counterpart. Audit that MIR actually
contains that path and the checker visits its intended obligation. This is a
detector control, not a claim that sort4 has such a cleanup block. Keep the actual
c1 direct-panic gate separate. Do not treat a legal callback mutation or panic
itself as UB; the negative must have an identified invalid operation or violated
required postcondition. No panic-abort substitution, assumed no-panic callback,
discarded effects, trusted callback stub or skipped cleanup can close this gate.

If the necessary normal/unwind state argument cannot be expressed or checked on
this profile, preserve that limitation. Do not redesign the verifier or substitute
a normal-only theorem for the full target requirement.

## Allowed implementation and execution budget

Own small fixtures, annotations and a diagnostic runner/classifier under
`research/challenge-8` are allowed, together with the minimal manual selection
`rapx_applicability` in `.github/workflows/smallsort-research.yml`. Keep other
selections unchanged. The runner/card must identify A, B or C explicitly; do not
implicitly run all phases or other proof suites. Any necessary default-branch
workflow exposure follows the runbook's narrowly scoped procedure.

Do not change std runtime behavior/signatures or commit generated/injected source.
Use an isolated hosted checkout for any exact-source extraction/injection. Do not
import other solutions' proof code, add assumed semantic models, weaken required
posts/checks, suppress relevant unsupported warnings, or hide a failing case.
Source inspection is allowed; no new broad survey or alternative-tool experiment.

ALL compilation, verification, extraction and executable classifier/control tests
run on GitHub-hosted Actions. The server only edits/orchestrates and performs the
permitted non-executing static checks. Use one active exact-SHA manual experiment
at a time and inspect full logs/artifacts, including successful runs.

Historical initial-session budget (superseded for the current continuation):
**at most four hosted runs total, at most 90 minutes each including setup**:
one planned run for each reached gate and one shared correction run for an
identified fixture/runner/setup problem. Unused later-gate slots are not a license
for repeated attempts on one gate. No blind retry, new tool version or budget
escalation. A critical semantic miss needs no confirming rerun if its evidence is
already unambiguous. Stop when the budget is exhausted or the next change would
expand the trust boundary.

The classifier must distinguish intended detection, proved valid case, unknown,
unsupported, skipped/missing target or checkpoint, frontend/setup failure and
timeout. Pinned RAPx's `UNSOUND` includes unproved/Unknown obligations: it is not
automatically a counterexample. No SOUND count or green job can replace the case,
path, obligation and source audit. Document tool limits on path exploration.

## Deliverables and mandatory stop

Write `RAPX-APPLICABILITY-RESULTS.md` with source/tool/package identities, experiment
cards and exact run URLs/SHAs, cases and intended/observed predicates, warnings,
obligation/path counts, generic versus concrete domains, full log/artifact hashes,
costs and each gate's status. Preserve minimal reproducer code; do not commit
downloaded logs/build output. Update STATUS, EXPERIMENT-LOG, coverage and relevant
index/plan claims, distinguishing NOT RUN from failed or passed.

Use one of these scoped conclusions:

- **NO-GO for this profile/route:** a required negative is missed or an essential
  semantic capability is unsupported; identify the exact evidence and boundary.
- **INCONCLUSIVE:** setup, timeout, unknown proof or ambiguous coverage prevents
  testing the hypothesis; state the concrete next decision, without calling it UB.
- **READY FOR NEXT DECISION:** all three gates pass with sufficient evidence
  to propose one bounded actual-source follow-up. This is not full generic sort4,
  universal tool soundness or challenge acceptance.

Stop after that report even if every fixture passes. No full sort4 proof phase,
insertion/other sorting target, verifier patch/upgrade, external issue/comment/PR,
tool application or bounty submission is authorized. The
[public-contract admissibility question](SORT4-CONTRACT.md#established-concrete-theorem-and-required-contract-clarification)
remains separate and unresolved; diagnostics may use the explicitly stated
research premises without presenting them as accepted challenge assumptions.
