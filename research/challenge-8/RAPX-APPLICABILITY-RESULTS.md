# RAPx applicability and detector coverage: results

## Automatic evidence replay (new processing authorization)

**CLOSED — reproducible automatic NO-GO.** Owner-authorized processing-only
follow-up from3e628c6a2d1197c069abf46fba33b3453c2de57f used **1/2 NEW replay
runs**,30min cap, one active at a time. No active run. Semantic experiment was
not repeated: no RAPx installation/build/verification or new target analysis.
Original manual closeout and failed automatic JSONs below remain historical.

Input: [original run37508888778](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37508888778),
source `929ea803ffff1c4f534716cc8c37bbbfa06a5960`,
[artifact11434810024](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37508888778/artifacts/11434810024).
Archive SHA256 `d9c5300fd4ac5c6267a8516e33ff4a8ba713795dc9e393e6eff3d8f2a71edf38`
verified locally on download and again on the hosted replay. Hosted run/artifact
metadata and archived source-commit card also matched. Extracted input stayed
read-only; mutated copies existed only in hosted temporary test directories.

Processor: **`1c0b5171375c1198ef0e94b6a26d5e3a13cf1a15`**;
[replay37513897141](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37513897141),
workflow_dispatch, rapx_evidence_replay/budget30, GitHub-hosted ubuntu24.04.
Job18:46:45–18:46:57UTC12s, replay script5s; normal push/remote exact SHA/no
other active run confirmed. Existing verification/bootstrap job explicitly
SKIPPED. Only checkout, metadata/archive fetch/hash checks, Python tests and
saved-log classification ran. The manual-only replay selection remains separate
from the original verifier runner.

### Actual format, strict association and rejection tests

[Classifier](classify-rapx-applicability.py) now matches the exact local function
path without a crate prefix and its full diagnostic DefId; checkpoint, path,
DefId index/hash metadata are explicitly scoped to these six frozen-source
functions. Callee matching permits only std/core reexports of
ptr::copy_nonoverlapping, with the exact src/dst/count signature and ordered
contract arguments. No general prefix stripping or arbitrary alias is trusted.

Six displayed contracts map to eight diagnostic records: Align(src/dst)=0/1,
ValidPtr(src) components=2/3, ValidPtr(dst)=4/5, NonOverlap=6, ValidNum=7.
All record indexes/kinds/checkpoints/paths and adjacent vm-check results must
match. Summary reconstruction follows pinned display.rs's origin grouping:
all ValidPtr components AND-fold under the shared origin name, while Align
rows retain their order or exact repetition count. Final SOUND/UNSOUND and
unproved/hazard counts must agree with primitive results. Missing, extra,
unmapped, wrong-target and contradictory data remain rejected evidence.

[Hosted tests](test-rapx-applicability-classifier.py) **9/9 groups PASS**,2.964s
test-suite time (3.06s wall, peak RSS32592KiB). They require the authentic six
paired logs; synthetic examples are not the compatibility basis. Deliberate
mutations reject removed/duplicated/unparseable records, wrong function or
DefId, wrong callee/signature, src/dst contract substitution, checkpoint/block/
path/property replacement, vm-check disagreement, missing or conflicting
summary rows/verdicts and unsupported/skipped warnings. Alias acceptance is
limited to the two named reexports. Aggregate tests cover missing/duplicate
cases, rejected/contradictory records and the CLI JSON write/read roundtrip.

### Automatic closeout facts

| Case | Automatic outcome | Other Failed / Unknown |
| --- | --- | --- |
| zst_aligned | PROVED_VALID | None |
| zst_source_misaligned | **SOUND_MISS**, Align(src) incorrectly ProvedByRule | None |
| zst_destination_misaligned | **SOUND_MISS**, Align(dst) incorrectly ProvedByRule | None |
| u64_aligned | PROVED_VALID | None |
| u64_source_misaligned | INTENDED_ALIGN_DETECTION_WITH_OTHER_UNPROVED; Align(src)#0 Failed, Align(dst)#1 Proved | NonOverlap#6 Failed; ValidPtr(src) remainder#3 Unknown |
| u64_destination_misaligned | INTENDED_ALIGN_DETECTION_WITH_OTHER_UNPROVED; Align(src)#0 Proved, Align(dst)#1 Failed | ValidPtr(dst) remainder#5 Unknown |

The u64 negative outcomes establish the intended Align detection and preserve
all other unproved obligations; neither is a completely successful control.
All six records have evidence_complete=true and retain the exact contract,
DefId, copy checkpoint/path and all eight primitive checks. Totals:
**43 Proved / 3 Failed / 2 Unknown** across48 records. Aggregate output separates:

- commands_succeeded=true: the original paired commands exited0;
- evidence_parsed=true: all six complete records are matched and consistent;
- gate_outcome=**NO-GO**: fully parsed ZST negatives have SOUND_MISS.

The replay command/test execution also succeeded (exit0). This is successful
processing of a failed semantic gate, not a gate PASS. A matched SOUND_MISS
still gives NO-GO if another case is missing, while evidence_parsed=false
prevents a successful complete replay closeout. Unparsed evidence can never
yield PASS. The workflow validates command/parse success separately from NO-GO.

### Output identities and preservation

[Replay artifact11436755991](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37513897141/artifacts/11436755991)
contains automatic-gate-a-report.json, six new per-case JSONs, input/processor
identities and file hashes, test output/resources and historical copies of the
original six JSONs plus gate-a-summary.json. Those seven old files compare
byte-identically with the original artifact; the old unmapped classifications
were not overwritten or relabelled. Full old logs/MIR stay in their original
artifact; the preceding manual record remains below and at3e628c6.

- New artifact27files/20371bytes, zip SHA256
  `7c475ec07ead8d4d83441d9d41c50bab4b067b6d05e7595c5eedbd351cea032b`.
- Automatic JSON report SHA256
  `b60eac77f855d955ff48586eb90b05c9d2fcad8c642a6836f5ddd8a869c1cf91`;
  artifact manifest `8470abd711b10ba038f87572a5c711b67fbfb09e383eb17a0044f78fd653ee9e`.
- Full replay log SHA256
  `bf64af71bb16775c98ddea93d1683e487f9e1851d86ee2081f75d454c8972e9f`.
- Classifier file SHA256
  `b3df7cae08d2702f3e22beb048c0bdcc3e6998649c10cee696229896cac671b2`;
  tests `9413cc4465b8877cd717bef681a94cbececb2a5abbf706295c87d43cdbba3f32`;
  replay runner `3e468fdfbd71d46e6ab1c6eecd8e851b5db58b2e555fa6efb240a943dc06f1d1`.

The JSON identity links both original experiment/source/artifact and exact
processor/replay revision; evidence input hashes are captured separately.
Downloaded logs/MIR/output artifacts were inspected outside the repository and
not committed. Local validation was static only; every executable test and
classifier invocation ran hosted. Noncausal Actions Node deprecations/git hints
do not affect parsing; no timeout/OOM. No extra run is needed.

**STOP at automatic NO-GO.** This repairs evidence handling only; it does not
change the earlier detector conclusion or add semantic/generic/std proof coverage.
B/C, RAPx patches/upgrades/new verification, full sort4 and external publication
remain unauthorized. Scope: [automatic replay](RAPX-APPLICABILITY-PHASE.md#automatic-evidence-replay).

## Historical gate-A continuation: manual closeout

**CLOSED — NO-GO for stock RAPx 0.7.50 / nightly-2026-02-05.**
Gate A now has a reproduced critical detector miss: both source-misaligned and
destination-misaligned alignment-eight ZST copies are reported SOUND, with the
violated Align predicate incorrectly discharged as ProvedByRule. This conclusion
comes from manual contract/diagnostic/MIR inspection; the automatic classifier
remains fail-closed and does not map the actual renderer format.

Owner resumed from `1fc89566800f8152d218de7f9a757f665626f220` on 2026-10-06,
only for preparation and the six existing A controls. Entry tree clean, origin,
branch and remote SHA verified, no newer/unrelated changes or active Actions.
Separate budget **2/4 NEW runs used**, each at most90min, one active at a time;
historical two attempts below stay outside this budget. No active run or pending
proof draft. Stop now before B/C; unused slots are not authority to patch RAPx,
confirm an already decisive miss, upgrade the tool or prove sort4.

### New run ledger

| Run / exact source | Hosted result | Reached boundary |
| --- | --- | --- |
| [37508216376](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37508216376), `cbbbb430d0091191141819843b3c8b476d0ff9f6` | FAILURE, job18:02:35–18:06:14UTC,219s | Full identity audit PASS; synthetic classifier tests11/12; no layout, target prep, MIR or A analysis |
| [37508888778](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37508888778), `929ea803ffff1c4f534716cc8c37bbbfa06a5960` | Commands SUCCESS, job18:07:43–18:10:57UTC,194s; **gate A NO-GO** | Identity audit PASS, classifier tests12/12, layout, target prep, six separate contracts calls and six actual verification calls, MIR and detailed checks |

Both are exact-SHA workflow_dispatch on GitHub-hosted ubuntu24.04/x86_64,
rapx_applicability/A/90min. Remote full SHA and absence of another active run
confirmed before each dispatch. First new failure was a test-log construction
error: deletion left a fern prefix concatenated with the next line. Only the
two synthetic deletions were repaired for the second source; classifier,
fixtures, predicates and verifier were unchanged. No blind rerun.

### Completed preparation and profile audit

The runner no longer requires `.cargo-checksum.json`. All installed package
source files and published Cargo.toml/Cargo.lock/build.rs are byte-compared
with the SHA-verified archive; optional installed VCS metadata is compared
when present. The complete installed `src` tree (204 files) and build.rs also
match pinned upstream. Both new runs complete this audit.

- Exact installation: cargo +nightly-2026-02-05 install rapx --version '=0.7.50'
  --locked into an isolated root; both driver and wrapper report exactly0.7.50.
- Archive SHA256 `e210328ce0e6c417ecf0498118ca0738f80851e9f2d204432a095ad703f8c0b8`;
  VCS `7d61d9377033c48a4df8954f34cc076e97a93816`, path_in_vcs=rapx.
- Installed/archive Cargo.lock SHA256
  `23822a0ee3ecb55aadb77fbf3d6c36d6f4ef16b037233c42c08c98ff9e8ef76c`;
  Cargo.toml `83bbcea83043db2da4a14abbf4fbd9975c9dcaef0c3b4f09edd6aef238eee850`;
  build.rs `f60929fdb736203dcef1f75228b9d9dd6c20c9cea9564e4974586a9703d27607`.
  Locked installation succeeds without lock-update warnings; no dependency
  update or verifier patch is applied.
- Binary hashes in both new runs: rapx
  `39afc1cbd1e22bbda19444233c90fcc32d2fe0b22af1fe3e7b65cc97a4883f52`;
  cargo-rapx `b357ca2faf83ecbcb69acdf7ee6d1c0c213545674919934cf26cfcded1036382`.
  Installed/upstream full-source manifests both hash to
  `1e928d98d423badc9a5984f96e0df35d21488a249c921936a8835f0b2bee6da2`.
- rustc1.95.0-nightly, commit `db3e99bbab28c6ca778b13222becdea54533d908`,
  nightly-2026-02-05; cargo1.95.0-nightly(fe2f314ae2026-01-30), LLVM22.1.0.
  Sysroot core ptr/intrinsics source manifest SHA256
  `970c212bc73d318baab64efe264f83c82ca94f7919737731029c8226f6a6ed5f`.
  Native libz3-dev4.8.12-3.1build1, pkg-config Z3 version4.8.12.0,
  libclang-dev1:18.0-59~exp2, pkg-config1.8.1-2build1.
- Repository std blob remains `e555fce440872898e47fd5114f32eb15401d07df`,
  SmallSort SHA256 `32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`.
  No runtime/signature/contract/tool semantic changes. These fixture calls use
  the pinned toolchain core; the repository sort4 body is not analyzed by RAPx.

Target preparation, contract diagnostics and true verification are separate.
Pinned driver.rs715's debug-contracts branch returns before verification.
Only the six contract-printing calls include that flag. Real commands use
--mode targeted --crate rapx-applicability --module <case-module>
--postfix-repeat auto -- --lib, without debug-contracts. RAPX_LOG=debug,
RUSTFLAGS=--cfg=rapx with per-case -Zdump-mir=all/-Zdump-mir-dir outside target.
The wrapper's internal defaults retain MIR optimization level0 and suppress
cross-crate inlining. Separate stage logs/resources/raw exits are preserved.
Only the layout binary executes: Z.size=0/Z.align=8, u64.size=8/u64.align=8.
Negative copy functions are analyzed, never run as ordinary programs.

### Six controls: manually audited actual obligations

All six contract calls and verification commands exit0. Target preparation
lists all six functions. Each real check has one exact local DefId, checkpoint#0,
one path#0 and eight property records; **48 records, six checkpoint paths**.
The same per-case optimized MIR retains the source body and copy call.

| Fixture / copy source line | DefId index / copy block | Align(src), Align(dst) | Final RAPx / manual interpretation |
| --- | --- | --- | --- |
| zst_aligned / zst.rs14 | 43 / bb0 | ProvedByRule, ProvedByRule | SOUND, valid control proved; all8 properties Proved |
| zst_source_misaligned / zst.rs31 | 44 / bb3 | **ProvedByRule**, ProvedByRule | **SOUND MISS: source Align violation**; all8 Proved |
| zst_destination_misaligned / zst.rs48 | 45 / bb3 | ProvedByRule, **ProvedByRule** | **SOUND MISS: destination Align violation**; all8 Proved |
| u64_aligned / u64_controls.rs9 | 34 / bb2 | ProvedByRule, ProvedByRule | SOUND, valid control proved; all8 Proved |
| u64_source_misaligned / u64_controls.rs24 | 37 / bb4 | **Failed**, ProvedByRule | Intended source Align detected; UNSOUND(3), separate ValidPtr component Unknown and NonOverlap Failed; whole-case evidence remains incomplete |
| u64_destination_misaligned / u64_controls.rs39 | 40 / bb4 | ProvedByRule, **Failed** | Intended destination Align detected; UNSOUND(2), separate ValidPtr component Unknown; whole-case evidence remains incomplete |

Every diagnostic DefId names `rapx_applicability[e215]::<module>::copy`; contract
and final summary paths omit the crate prefix. Contract callee is displayed as
std::ptr::copy_nonoverlapping::<T>, final checkpoint as core::ptr::copy_nonoverlapping,
and optimized MIR as std::ptr::copy_nonoverlapping::<zst::Z/u64>. These are the
same reexported function, with matching argument positions and checkpoint.

Contract property order begins Align(src,T), Align(dst,T). Their actual report
indexes are0/1. Each ValidPtr expands into two checks: NonNull plus an unnamed
component at indexes2/3 for src and4/5 for dst; NonOverlap=6, ValidNum=7.
Summary folds compound properties under their origin name and can combine the
two ValidPtr origins, so its row counts are not eight primitive counts.
Observed totals:43 Proved,3 Failed,2 Unknown; Align alone10 Proved/2 Failed.
Unknown at u64 source property3 and destination property5 is preserved separately;
an UNSOUND label containing Unknown is not a demonstrated counterexample for
that component. The u64 source NonOverlap failure is not an actual overlap claim
about the distinct fixture arrays. No unsupported-operation or skipped-target
warning occurred in real checks.

Path descriptions: ZST aligned[0]; both ZST negatives[0,5,1,2,6,3]; u64
aligned[0,4,1,5,2]; source[0,6,1,2,7,3,8,4]; destination[0,6,1,7,2,3,8,4].
These are RAPx checkpoint-prefix descriptions, including transformed CFG nodes;
they do not establish arbitrary path/unwind coverage or a whole-function proof.

Both ZST negative optimized MIRs preserve raw address of an aligned Z local,
cast to u8, wrapping_add(const1_usize), cast back to Z, then copy count1 at bb3.
No prior invalid reference or dereference appears. Required alignment is8, so
an address8*n+1 violates it even though the copied byte range is empty. The
other pointer remains aligned; empty ranges do not overlap. Thus the intended
unsafe-operation defect is concrete and isolated, not an inferred source concern.
Pinned property_checker/memory.rs25–46 returns ProvedByRule on zst_guard before
calculating required alignment; util.rs432–465 resolves the callee type as ZST.
This source path explains the observed false proof; the run and MIR establish
the detector miss independently of source suspicion. No RAPx patch follows.

### Automatic-classifier limitation and stop

All six saved JSONs are **CONTRACT_EVIDENCE_MISSING_OR_UNMAPPED**, and
gate-a-summary.json has all_expected=false. They are preserved as such;
no missing/unmapped result is promoted to success. Hosted synthetic acceptance/
rejection tests pass12/12 but model full crate paths, core callee spelling and
six unexpanded primitives. Actual logs instead have the shapes described above.
Thus the classifier is not validated for these actual logs. Static pre-dispatch
review failed to catch those formatting/compound-expansion assumptions.

Manual review of every paired contract/verification log, detailed DefId/property/
path record and corresponding optimized MIR supplies the substantive A evidence.
This report does not relabel the raw JSONs. Once the critical ZST miss is confirmed,
the mandatory stop takes precedence: no further parser repair/replay/verification
dispatch, and no untested classifier revision is committed as a solution.
Future automated replay would need a separately authorized correction and hosted
tests against the actual renderer, including compound-origin grouping.

### Evidence integrity, cost and boundaries

- Run37508216376 full-log SHA256
  `ac8047b8d338fb951f961356018b76498f9c4f9258888c3847c1efe34f34c2dc`;
  artifact11432717926,41files,47484bytes, zip SHA256
  `4ef1061cfacce2726fe51bc0503fb8c1a37c0dfad065285856b6da097cf342fc`.
- Run37508888778 full-log SHA256
  `c3820617663f69f9018cf558bd7cdbaa46b972f050d57a77f486f56d19c428ad`;
  [artifact11434810024](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37508888778/artifacts/11434810024),
  2832822bytes, zip SHA256
  `d9c5300fd4ac5c6267a8516e33ff4a8ba713795dc9e393e6eff3d8f2a71edf38`.
  3216files:3012MIR/96DOT/108other; artifact manifest SHA256
  `1dd4f1e5bfddc28bc83bbd7f4b11cdc133720210a6f0c448d3389e85ee5466fb`.
  Logs and downloaded/generated artifacts retained outside the repository;
  minimal reproducer remains the unchanged checked-in six-function fixture.
- New jobs total413s, both far below90min; runner clocks209s/183s include
  recorded preparation. RAPx installs84.56s/84.84s, peak RSS~1.53GB.
  Actual six verification wall times1.06/.70/.70/.72/.75/.75s, peak RSS
  246316/243048/242928/243016/244820/245244KiB respectively. No timeout/OOM.
  Synthetic classifier tests0.11s in the second run. Expected install PATH
  reminder/git default-branch hints and Actions Node deprecations are noncausal;
  failed/Unknown obligation rows and UNSOUND warnings remain evidence.
- Server did only editing, git/gh and read-only evidence inspection, bash -n
  and git diff --check. Every build, verifier and executable test ran hosted.

**Gate A: NO-GO; B/C: NOT RUN.** The reproduced failure is specific to this
unchanged RAPx profile and concrete alignment-eight ZST copy controls. It is
not a runtime bug in repository sort4, a universal claim about all RAPx versions,
or a new generic proof. Generic uninitialized destination/ownership/provenance,
the other mandatory UB categories, arbitrary comparator effects and five panic
posts remain untested here. Full [sort4 contract](SORT4-CONTRACT.md) is unchanged,
including current-state normal/panic posts and separate ordering premises;
its public admissibility question remains unresolved. No tool patch/upgrade,
contract weakening, B/C or full-sort4 phase is authorized. Scope/cards are in
[phase](RAPX-APPLICABILITY-PHASE.md#current-gate-a-continuation) and
[experiment log](EXPERIMENT-LOG.md).

## Historical initial-session closeout

**INCONCLUSIVE — gate A stopped at setup, no detector hypothesis tested.**
The owner resumed
[the approved phase](RAPX-APPLICABILITY-PHASE.md) on 2026-10-06 from documentation
commit `ad54f67d655c4106762016fba47534c58601f3ec`. This report distinguishes
source review, actual detector observations and unexecuted target obligations.

## Source, profile and execution

- Fork Tiramisu-Cake/verify-rust-std, branch challenge-8/research. Entry tree
  clean, origin verified, fast-forward to the requested documentation commit;
  no queued/in-progress Actions. No unrelated changes were present.
- Actual target: `library/core/src/slice/sort/shared/smallsort.rs`, std blob
  `e555fce440872898e47fd5114f32eb15401d07df`, unchanged. The gate tests the
  alignment obligation needed at sort4's four copies, not the whole body.
- Diagnostic source `b55ae850d1cef67ddbcd02d8d97b4763c9c4a9f1`;
  [run37492790456](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37492790456),
  workflow smallsort-research.yml, proof rapx_applicability, rapx_gate A,
  budget 90 min; created 2026-10-06T16:04:30Z. Job began 16:04:37Z on a
  GitHub-hosted ubuntu-24.04 runner. All builds and executable diagnostics run
  there; server validation was `bash -n`, `git diff --check` and static reads.
- Two runs used out of four; the shared technical correction consumed; B/C
  unused and gated.
  Direct research-ref dispatch accepted the selection; no main-branch update.
- Frozen package RAPx exactly '=0.7.50', installation --locked; explicit
  nightly-2026-02-05 for installation and analysis. Reviewed upstream
  `7d61d9377033c48a4df8954f34cc076e97a93816`; package archive SHA256
  `e210328ce0e6c417ecf0498118ca0738f80851e9f2d204432a095ad703f8c0b8`.
  The read-only downloaded package VCS metadata names that commit and path rapx.
  The first hosted run obtained the archive/lock/sysroot evidence but stopped
  before executable-version/installed-source checks; the correction run audit
  did not complete.
- Diagnostic flags: --mode targeted, --crate rapx-applicability, one module per
  case, --postfix-repeat auto, --debug-contracts, -- --lib; prepare-targets
  precedes analyses. RAPX_LOG=debug, --cfg=rapx, -Zdump-mir=all. No checker,
  model, contract, kernel or std semantic changes; no skip-invariant flag.
  The fixtures call pinned toolchain core, not the repository core build.

## Experiment card and semantic boundary

Gate A hypothesis: RAPx emits source/destination Align obligations at
copy_nonoverlapping and distinguishes aligned pointers from misaligned pointers,
including a concrete size-zero type with alignment eight. The source-review
shortcut in check_align was only a candidate miss before execution.

Six functions in the checked-in [fixture crate](rapx-applicability/src/lib.rs)
are designed for individual selection; actual preparation/selection did not run. The ZST is `#[repr(align(8))] struct Z;`. A layout-only
binary is designed to report size/alignment without executing invalid fixtures;
it was not run. ZST negatives
use wrapping byte offset one from an aligned local raw pointer; no invalid
reference is formed. Since an aligned address is 8*n, its offset-one address
is 8*n+1, including wrapping arithmetic. Count one copies zero bytes; empty
ranges do not create an overlap violation. The intended defect is alignment.

The u64 negatives use distinct initialized [u64;2] backing arrays; the tested
pointer alone is offset one byte and the other remains aligned. The eight-byte
ranges fit within separate sixteen-byte allocations. No dangling, overlap,
invalid scalar or uninitialized-read defect precedes the copy. The aligned
ordinary control uses separate initialized one-element u64 arrays.

These concrete microfixtures test automatic unsafe-operation contracts. They
add no independent manual alignment assertion and do not assume the negative
property as a precondition. Expected positives: analyzed named body SOUND with
actual copy checkpoint and both Align obligations proved. Expected negatives:
the tested Align predicate fails at the copy, while the other remains proved;
Unknown, unsupported, skipped/missing checkpoint and setup are separate results.
An adverse detector result can coexist with a successful evidence-capture job.

Full target yardstick remains [SORT4-CONTRACT](SORT4-CONTRACT.md): unrestricted
valid T/F, initialized four-position source and possibly uninitialized writable
separated scratch, legal provenance/permissions/borrows and exactly one logical
ownership sequence. Normal return retains current V5 and initializes scratch
replicas pi(V5), with current callback/frame and full storage resources and no
borrow debt. For each panic k=1..5, recover current Vk/Qk/Hk after legal callback
effects, source ownership and raw scratch with its actual initialization state,
no sort4 writes, rollback or leaked resources. Ordering assumes preserved keys
and a fixed strict weak order separately; safety has no Copy/Freeze/purity or
no-panic restriction. Gate A proves none of those full posts or generic domains.

Decision map: critical reproduced miss or essential missing semantics -> NO-GO
and stop B/C; setup/unknown/ambiguous coverage -> INCONCLUSIVE or one permitted
technical correction supported by evidence; sufficient A pass -> gate B only.
Even all gates passing would stop before a full sort4 proof or tool changes.

## Observations

First run37492790456: **INCONCLUSIVE / setup failure**, job 221 s
(16:04:37–16:08:18 UTC). Exact package compilation/install succeeded (reported
1m 24s release build); pinned rustc is 1.95.0-nightly, commit
`db3e99bbab28c6ca778b13222becdea54533d908`, LLVM 22.1.0,
host x86_64-unknown-linux-gnu. The runner's direct `rapx --version` exited 2 and
printed usage: the direct driver parses RAPXFLAGS rather than argv. No installed
source comparison, layout, preparation, target, MIR or negative executed.
This result says nothing about alignment. Noncausal warnings: Actions Node.js
deprecation and git default-branch hints.

Before correction, the experiment card recorded the unchanged full target and
six-case domain, expected executable-version checkpoint and result-to-decision
mapping. The sole code change is `RAPXFLAGS=--version rapx`. Correction source
`772def3ce7e5e3585ac0c9a909f97afbcdb9a821`,
[run37493697524](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37493697524),
created 16:11:16 UTC, same selection/gate/budget. Both full logs and all
artifacts were inspected after completion; results below. No further gate-A
technical retries; B and C: NOT RUN because A did not pass.

First full Actions log SHA256:
`3e3fb0dc237c6724c083774524fb18996f712d8dfdf8da6a0e7f5d30800b03db`.
[Artifact11426930280](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37492790456/artifacts/11426930280),
10 files, zip digest
`a149d4858471a0f6ac58de351120abeb452303916cc76d8b51280c0b70d1122d`.
Artifacts downloaded outside the repository and all files/full log inspected.
Package Cargo.lock SHA256
`23822a0ee3ecb55aadb77fbf3d6c36d6f4ef16b037233c42c08c98ff9e8ef76c`.


## Final correction-run result

Run37493697524: **INCONCLUSIVE / setup failure**, raw runner exit 1,
job 16:11:22–16:18:02 UTC,400 s. The earlier version-query correction worked:
`RAPXFLAGS=--version rapx` and `cargo +nightly-2026-02-05 rapx --version` both
report 0.7.50; `cargo install --list` lists only that package and its two binaries.

First causal failure, at 16:17:58.205 UTC:

```text
FileNotFoundError: [Errno 2] No such file or directory:
'/home/runner/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/rapx-0.7.50/.cargo-checksum.json'
```

The runner incorrectly requires this metadata file. The registry source
directory was found, but the checksum lookup fails before the upstream fetch
and installed-source comparison. This is a diagnostic-runner preparation error,
not a verifier rejection, profile mismatch, unsupported memory operation,
Unknown obligation or a reproduced UB miss. No additional correction was applied:
the single shared technical correction is consumed, and the unspent B/C slots
are not authorized as more attempts at A. There is no active run or applied draft.

| Gate / case | Intended checkpoint | Observed result |
| --- | --- | --- |
| A: zst::aligned::copy | Both Align at copy, valid control | NOT RUN |
| A: zst::source_misaligned::copy | Source Align fails at copy | NOT RUN |
| A: zst::destination_misaligned::copy | Destination Align fails at copy | NOT RUN |
| A: u64_controls::aligned::copy | Both Align at copy, valid control | NOT RUN |
| A: u64_controls::source_misaligned::copy | Source Align fails at copy | NOT RUN |
| A: u64_controls::destination_misaligned::copy | Destination Align fails at copy | NOT RUN |
| B: generic copy/initialization/four UB categories | Prior A pass required | NOT RUN |
| C: actual c1 normal/direct panic and synthetic cleanup | Prior B pass required | NOT RUN |

Analyzed fixture functions 0; prepared fixture targets 0; measured fixture paths 0;
checked fixture obligations 0. No SOUND, UNSOUND, Failed or Unknown target result.
No actual unsupported operation was reached. No concrete layout measurements,
MIR, callback shape, cleanup path or executable classifier/control test was
produced. The declared ZST/u64 sizes and alignment remain the fixture design;
the layout-only binary was not compiled/run. The source-level ZST alignment
shortcut remains a suspicion, not an end-to-end reproduced false pass.

## Identity evidence and its limits

Both runs used x86_64-unknown-linux-gnu, nightly-2026-02-05 sysroot. Rustc
1.95.0-nightly commit `db3e99bbab28c6ca778b13222becdea54533d908`,
LLVM 22.1.0; Cargo 1.95.0-nightly (fe2f314ae 2026-01-30). Native dependencies
recorded: libz3-dev 4.8.12-3.1build1 (pkg-config 4.8.12.0),
libclang-dev 1:18.0-59~exp2, pkg-config 1.8.1-2build1. No dependency installation
was performed on the editing server.

Package archive SHA256 matches the frozen requirement in both runs; its
VCS metadata is the reviewed commit. Cargo.lock version 4 has 154 package entries.
All 104 compiled name/version rows in the second cargo-install.log match that
lock; no lock-update warning or evidence of dependency drift. This is a
read-only audit of saved build evidence, not a local compiler/verifier test.
The log retains every resolved compilation version.

Installed executable SHA256 in run37493697524:

| Binary | SHA256 |
| --- | --- |
| rapx | 39afc1cbd1e22bbda19444233c90fcc32d2fe0b22af1fe3e7b65cc97a4883f52 |
| cargo-rapx | b357ca2faf83ecbcb69acdf7ee6d1c0c213545674919934cf26cfcded1036382 |

The downloaded archive's relevant sources were compared read-only with the
reviewed upstream source before dispatch. However, the hosted audit linking
installed registry sources/checker/call/contract files to that source did NOT
complete. No claim that the complete executable/source audit passed. The native
profile is identified as far as the saved artifacts permit, without treating
missing metadata as an observed checksum discrepancy.

The sysroot ptr/intrinsics hash manifest has SHA256
`970c212bc73d318baab64efe264f83c82ca94f7919737731029c8226f6a6ed5f`.
It identifies toolchain core sources, but the verifier never analyzed them in
these experiments. Repository target SHA256 in both environment records is
`32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`;
std blob remains `e555fce440872898e47fd5114f32eb15401d07df`. There is no
repository-body or generic-safety result.

## Evidence, costs and next decision

Second full Actions log SHA256:
`c4ee3f87c3d2f4e7bc0b508ca3186f539baf49e4e5c8b62b8e4edcbe0f0ea86f`.
[Artifact11426617314](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37493697524/artifacts/11426617314),
11 files, 16,573 bytes, zip SHA256
`314f42868159afb7ce54b0197c56a8d8d0d4a4a29b3bdde56e985f13cc36ac20`.
Core record hashes:

| Artifact file | SHA256 |
| --- | --- |
| cargo-install.log | 21ffd82b9cfad2f280d263b6715533f2a59d8767c34acd3484ad5b1a8eb10972 |
| experiment-environment.txt | f050db4afcea5e50b017e7f81f632583a4559e59e4c8b8a188f0d2f7ee19fe8c |
| installed-package-Cargo.toml | 83bbcea83043db2da4a14abbf4fbd9975c9dcaef0c3b4f09edd6aef238eee850 |
| installed-package-Cargo.lock | 23822a0ee3ecb55aadb77fbf3d6c36d6f4ef16b037233c42c08c98ff9e8ef76c |
| package-vcs-info.json | 5625f0c14aaf643dd14f95e3bf080a6642110a0e2534b3fab25545215ba5f4b0 |
| rapx-version.txt | 160b57633e4e1197377f745808edbe4455f866dd6f7c28e3747aea77730aa731 |
| cargo-install-list.txt | f6185ad9ac55622b71e548984e8aa2ac428c8ec6a6feef8b92ed0a451fce94e4 |
| rustc-version.txt | 7fcaf1436fa62824527ec1ead2712e804a1e8bf1fb9669b0f4602b1d1111bc4f |
| sysroot-core-source-hashes.txt | 970c212bc73d318baab64efe264f83c82ca94f7919737731029c8226f6a6ed5f |
| sysroot-path.txt | 1f29118e5116fefa88eb2d9ee8ef698da52bbb347d6ce7286fa7915b7cc43f57 |
| target-libdir.txt | 7ea31b33565253e9fbca6ea2ec81204dd3c78cca48dafab7abeedeab7f2ef991 |

Both full logs and all 21 artifact files were inspected outside the repository;
no downloaded logs, generated source, build output or archives are committed.
Noncausal warnings in the second run: Actions cache/upload Node.js
punycode/url.parse deprecations and Node 20 forced to 24; git default-branch hints.
No fixture unsupported warning, skipped-target warning or semantic failure exists
because the analysis stage was never reached.

| Run | Job elapsed | Relevant setup cost | Verification cost |
| --- | --- | --- | --- |
| 37492790456 | 221 s | RAPx release build 1m 24s, plus runner/nightly setup | 0, NOT RUN |
| 37493697524 | 400 s | Prepare runner306 s; install/identity step 81 s, including RAPx build 1m 04s | 0, NOT RUN |

Neither run approaches the 90 min limit; no timeout/OOM. Per-case wall time/RSS
files are absent because no case ran. Used 2/4 runs: planned A and shared
correction. Planned B/C remain unused and conditional, not a retry reserve.

**Stop: INCONCLUSIVE.** No generic coverage was gained and no critical detector
miss was confirmed. The bounded phase closes before A's applicability decision;
B/C/full sort4 proof and verifier patches/upgrades remain unexecuted and
unauthorized. The public-contract admissibility question is still independent.

A next owner decision could authorize one newly bounded setup-and-gate-A retry:
replace reliance on optional Cargo checksum metadata with an archive-to-installed
source byte comparison, retaining exact archive/VCS/lock/executable identities
and the original frozen profile, then execute the same six controls. That is
a proposed preparation correction, not an applied patch or a permission to
reuse B/C slots. No next run is dispatched or promised.
