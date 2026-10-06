# Independent H_align gate: hosted results

## Stock generic baseline and experimental fieldless layout — 2026-10-07

Current phase IN PROGRESS. Stock baseline **PASS independently for const/mut**;
experimental layout profile implementation starts only after this gate. Budget
3/6 NEW runs,235/10800 summed job-seconds including all preparation/replay/upload.
Earlier phases below retain their original outcomes and evidence.

[Stock run37540829027](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37540829027),
source/head968c073983e0fa27112c5d8a4e10a36b05828323, created2026-10-06T22:28:46Z.
Job112533159277,22:28:51–22:29:34Z,43seconds. Whole workflow FAILURE solely because
stock concrete ZST controls stay INCONCLUSIVE; that does not weaken generic gates.
Both generic cases exporter/decode/VF/refinement0; named caller/helper1, helper
execution6, pointer operation3,72 statements verified each. Reachable i<1/i<2/i<3/
otherwise ghost branches prove i==0/1/2/3 from old bounds, all normal posts/resources/
leak checks finish, whole-unit dead-code check passes. Original on_unwind_ens false,
outer req, byte resources and ghost-stripped runtime remain unchanged.

| Original case | Stock outcome |
| --- | --- |
| positive_generic_const | PASS, VF0 independently |
| positive_generic_mut | PASS, VF0 independently |
| positive_zst_layout | INCONCLUSIVE at size0 assertion20, align8 not reached |
| positive_zst_add | INCONCLUSIVE at typed add21 pointer_within_limits |
| negative_source_byte_offset | EXPECTED_FALSE_POST_FAILURE at marked modulus8 assertion25, add22/cast23 reached |
| negative_destination_byte_offset | EXPECTED_FALSE_POST_FAILURE at same independent dst assertion |

Official archive/schema/source/compiler and binary/spec pins match prior stock
profile. Six exports/decodes/refinements0; pre/post and each-stage source hashes
match actual archived sources. Full logs, MIR, returned resources and final gates
inspected. Wrapper19.00s, peakRSS620572KiB, no timeout/OOM. Historical replay3 groups/
30 mutation checks PASS; original parse errors stay INCONCLUSIVE and raw evidence
unchanged. Artifact11447599817,573681bytes, API/upload archive SHA256
27ff629da5275b4a172dcd60104903622ae1474d42586dcf87ec818b71b3c4f7.

Generic result is an abstract arithmetic/provenance/byte-resource theorem under
its explicit aligned-base/array domain. It does not repair stock concrete Z,
prove copy UB checking or full sort4 safety. Prototype tests will preserve this
baseline separately and use the [pre-recorded matrix](SORT4-ALIGNMENT-PHASE.md#stock-generic-and-fieldless-layout-prototype--2026-10-07).


Experimental runs [37542669720](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37542669720)
(source f9697b8f3f894eb24115684a41da3d88566ddc9e,82 job-seconds) and
[37543115091](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37543115091)
(source55b856cd5285961e02323dd269044d2d194183d6,110 job-seconds) fail console build.
First unary minus_big_int misuse; second missing Ast namespace on RustLayout.
Exporter build and ALL experimental matrix cases NOT RUN. Preparation/pin/patch
checks PASS; full logs/artifacts inspected and identities preserved in journal.
These are build failures, not positive or negative layout results.


## Historical generic completion/layout review checkpoint

Current checkpoint 2026-10-07: **generic completion/layout review CLOSED at the
2-run limit; generic INCONCLUSIVE**. Used **2/2 NEW runs,85/3600 job-seconds**,
including preparation, proof, unchanged historical replay and artifact upload.
The second run discharges the residual i==0, pointer identity and alignment posts,
but the unchanged dead-code check rejects the three impossible guard bodies.
No accepted whole-unit generic proof is claimed. Layout review/regression design
is complete; no tool patch or patch-regression execution. Previous phases below
remain historical, with their original raw evidence and outcomes preserved.

## Generic completion and layout review — two NEW runs

Entry clean matching b523959d2032b28086aa8b11dd35a50a2eb7c7e0, fork/research branch
correct, no active experiment. The owner explicitly allowed this generic subtask
to continue independently of the known concrete ZST boundary, plus documentation-
only upstream/layout/component review. Maximum2 NEW manual hosted runs /60min jobs.
Both pushes and run head_sha matched; no Re-run, duplicate or third dispatch.

| NEW run / full source SHA | Hosted job / outcome | Specific hypothesis / first failure |
| --- | --- | --- |
| [37537448952](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37537448952) /16aaf1b993f62c8dad0390b74de3e877983beb37 | Created2026-10-06T21:57:32Z; job112521963302,21:57:37–21:58:15Z,38s,FAILURE | Explicit residual assert i==0 was expected to follow old bounds/disequalities. Both generic cases stop at verified/lib.rs:53: Cannot prove i=0; pointer identity/alignment assertions not reached |
| [37537868053](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37537868053) /519a3707136d2ae4e589c44b837afac6c58b939b | Created2026-10-06T22:01:18Z; job112523342669,22:01:22–22:02:09Z,47s,FAILURE | Checked order splits successively derive i<=2,i<=1,i==0. All four return/post/leak paths finish; afterward the dead-code gate rejects unreachable assertions at lines53,55,57 in both cases |

Both selections are `verifast_sort4_alignment/30`, same official unchanged
VF26.09/nightly2026-02-05; requested30min cap includes setup. Verification-step
failure remains a real failure; replay/tests and artifact uploads SUCCESS, RAPx
replay SKIPPED. No timeout/OOM. Wrappers15.29s/RSS621304KiB and18.57s/RSS619440KiB;
job totals, not wrappers, are charged to the budget. Stop proof edits/runs at2/2,
with3515seconds unused. Fixture remains exactly the tested second-run revision.

### Separate final results for six cases

| Case | Final classification | Evidence / remaining gate |
| --- | --- | --- |
| positive_generic_const | INCONCLUSIVE | Helper/local bounds/.add and all four normal return/post/leak paths finish; residual checked i==0, result==base and modulus post assertions pass. VF1 due unreachable guard-body assertions at53,55,57 |
| positive_generic_mut | INCONCLUSIVE | Same facts independently checked, same dead-code failure; no const-to-mut verdict transfer |
| positive_zst_layout | INCONCLUSIVE | Original line20 assert size==0 fails (__result=0 unproved); align8 assertion not reached |
| positive_zst_add | INCONCLUSIVE | Original line21 typed .add reaches and fails pointer_within_limits(ptr_add_(base,i,Z_type_info)); return equality/post unproved |
| negative_source_byte_offset | EXPECTED_FALSE_POST_FAILURE | Original byte add22/cast23 reached; exact assertion25 rejects %(get_pointer_address(ptr_add_(src,1,uint8_t_typeid)),8)=0 |
| negative_destination_byte_offset | EXPECTED_FALSE_POST_FAILURE | Same exact named assertion/stages with dst, independently checked |

**What the second generic trace establishes:** the old unsigned bounds and excluded
i=1,2,3 cases are sufficient when exposed via existing integer-order case splits.
In the residual branch, checked comparisons give i<=2, then i<=1, then i==0;
result==base and its old alignment assertion are subsequently discharged. The
three positive indexed branches retain their original checked arithmetic lemmas.
No i==0 premise, stronger outer req, new trusted lemma or axiom was introduced.
Original byte resources, normal post and on_unwind_ens false remain intact; all
normal return/resource/leak checks are reached. No full-profile theorem is accepted
because the verifier exits1 at its final dead-code gate.

**First remaining generic blocker:** assertions in the impossible `3<=i`, `2<=i`
and `1<=i` guard bodies never execute after the original excluded-index conditions.
The unchanged console check records statement reachability and returns1 for those
three locations ([vfconsole.ml:268–282](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/vfconsole/vfconsole.ml#L268)).
This is a proof-structure failure, not an alignment/kernel or Rust-layout requirement.
Pinned integer comparisons use unit gaps in the existing solver
([redux.ml:1041](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/redux.ml#L1041),
[1080](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/redux.ml#L1080));
no solver semantics were changed. A later candidate could preserve checked ordered
splitting without placing proof statements in impossible branches. That candidate
is **NOT IMPLEMENTED / NOT RUN / NOT AUTHORIZED** by the exhausted run budget;
removing the dead-code check or accepting nonzero exits is inadmissible.

All six exports/decodes/refinements are0 in each run; logs say No refinement errors
found, and every actual source-stage hash is unchanged. Timed named caller headers1
per case, helper headers1/body records6 per generic, marked pointer-operation
records3 per generic/ZST-add/negative. Original MIR calls and Continue unwind edges
remain. Whole/six-case ghost-stripped Rust, all outer contract bytes and four
concrete case texts match b523959 and previous archived originals. Classifier,
workflow, runner, checks, flags and std blob are unchanged. Official archive,
binaries/rsspec/source/schema/compiler identities match the prior frozen profile.

Each run executes unchanged hosted historical replay: all six initial parse errors
stay INCONCLUSIVE; syntax-run four positives stay INCONCLUSIVE and two negatives
are recognized only at intended alignment assertions. Separate derived outputs,
3 unittest groups and30 fail-closed mutation checks PASS each; archived tree hashes
unchanged. No historical raw JSON/logs are overwritten. No classifier status change
was used to compensate for the generic dead-code failure.

### Layout review and next implementation scope

[The expanded model review](SORT4-ALIGNMENT-MODEL-BOUNDARY.md#follow-up-layout-model-review-documentation-only-2026-10-07)
checks official26.09/source809de459 and26.10/live-master
f76012fb518703b1d98e243ac4f487f16877cfcb. Both retain positive concrete struct size
and omit repr-alignment transfer; upgrading to26.10 alone is not the layout fix.
The reviewed26.10 profile uses nightly2026-09-25, and was not run here; current
proof profile remains26.09/nightly2026-02-05.

Recommend a separately reviewed compiler-backed Rust layout repair: exporter /
wire schema/generated bindings / AST carrier / translator / engine; Rust-only
nonnegative struct bounds, plus same-typeid/target exact size and ABI-alignment
facts for closed Sized repr(Rust)/repr(C) structs with optional repr(align).
Ordinary nonempty structs are included to check compatibility with field-offset
constraints; exact generic-ADT/niche/packed/enum/DST layouts remain outside that
minimum scope. Generic functions retain symbolic valid-layout/size_align facts.
Changing >0 to>=0 alone only permits zero, and establishes neither exact size0
nor align8. No correction is implemented or authorized by this review.

Specific independent candidate Kani0.67.0 can calibrate the exact original Z at
the same source/toolchain/target, but current evidence covers only i32/tagged Copy
sort4 instances. No existing Z proof, exhaustive all-T domain split or checked
cross-model interface allows it to replace the full layout component. A separate
Z component must never instantiate VF's incompatible concrete Z or import numeric
facts as ownership/permission resources. Prefer layout repair for future review.

Future acceptance gates are DESIGN ONLY / NOT RUN: original Z size0/align8 and
const/mut zero-stride add; ordinary supported structs/padding/compiler agreement;
symbolic generic geometry and exact instantiation linkage; no constant-layout
reuse across generic ADTs; unchanged C/C++ behavior; intended false size/align/
stride assertions and assertfalse under normal premises; malformed/mismatched
metadata fail-closed. A complete generic geometry gate additionally needs VF0 with
dead-code/leak/refinement checks intact. Layout repair does not resolve arbitrary
FnMut effects, all five panic posts, raw-copy ownership/validity, selected-pointer
permissions or automatic copy UB. No historical insertion/FnMut/Drop chain is added.
RAPx remains CLOSED / NO-GO; B/C NOT RUN; ZST remains in adopted contract.

### New evidence identities

| Run | Artifact / ZIP SHA256 (downloaded, API/upload matched) | Other digests |
| --- | --- | --- |
| 37537448952 | [11446714044](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37537448952/artifacts/11446714044),574870bytes; bdb909a3ada2c4754a7beaf86df4de4b349f167a2fdc84fd36a58e856baca098 | Full Actions log d4d315a6457e4b39b7db2a91c4b6e06218cceca9f372a8f6f1cb95c23c969387 |
| 37537868053 | [11447620706](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37537868053/artifacts/11447620706),573769bytes;84a6adcc3f46e20fc7c2b4792f971d4be0c11b874b9345668bbbe1f548a7d37a | Full Actions log f6e03c2e7d1d5a5d1b67fc0aaef9a753ab33d7c67ff4f77023b8fce88fa645ac |

Both live aggregate SHA256 values equal
48b2ffd48241e358fc5b039593babffab42d1ad9f0aa53736eb411e3b132d157 because their
classification/count records agree; their different failures/source identities
are retained in separate full logs and case sources. Second replay JSON SHA256
9559c09b53b1af444cb70066028a9a6a8502d0b3a0987333ba944f5ff4e8134b. Complete logs,
MIR, source/profile/stage manifests and separate historical replay inspected;
downloaded evidence stays outside the repository. No active experiment. STOP at
2/2 run limit; review complete, accepted generic proof still incomplete.

## Historical checkpoint at b523959

Current checkpoint 2026-10-07: **bounded no-patch continuation CLOSED at a concrete
ZST model boundary**. Used **1/3 NEW runs, 38/5400 job-seconds**, including setup,
verification, historical replay and artifact upload. Two unused slots are retired
at this phase boundary; they are not authorization for further experiments.
Generic geometry remains INCONCLUSIVE; classifier replay and both intended
negative assertions are confirmed. RAPx remains CLOSED / NO-GO; B/C NOT RUN.

## Bounded proof/reclassification continuation — closed at model boundary

[Run37535499783](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37535499783),
NEW manual dispatch `verifast_sort4_alignment/30`, source/head_sha
`ea635ea152f9ff3a491b57b7b6a9df84dc99a4be` (pushed remote matched).
Created 2026-10-06T21:40:10Z; job112515246039 ran 21:40:14–21:40:52Z, **38s**,
FAILURE. The verifier step failed positive posts; historical replay/tests and
artifact upload succeeded. RAPx replay job SKIPPED; B/C NOT RUN. Runner wrapper
16.88s, peak RSS620268KiB; no timeout/OOM. The remaining 5362s and two run slots
are unused because the concrete layout route requires a prohibited model change.

The owner authorized classifier repair and checked proof development on unchanged
VeriFast from f1c0774. Local/remote entry was clean and matching; no active run.
Only generic ghost helper req adds explicit `0 <= address` and `0 <= stride`;
caller ghost steps derive bounds through existing resources/specifications.
Six outer contracts, all final posts, original Rust after ghost removal, all
`.add` operations, case order and four concrete case texts are byte-identical to
f1c0774. No type replacement, outer premise, axiom or verifier/spec change.
Static AST/bash-n/diff and payload comparison preceded the dispatch. All executable
checks ran only on the GitHub-hosted runner.

Official VeriFast26.09 archive SHA256
`da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa`,
source809de4596839b739dd999f9e462242c835e3af46, nightly2026-02-05/compiler
`db3e99bbab28c6ca778b13222becdea54533d908`, all binaries/rsspec/schema hashes
match the previous frozen profile. Std blob e555fce440872898e47fd5114f32eb15401d07df
and original exporter/VF/refinement flags/checks are unchanged. Job timeout is
30min including preparation; no semantics or checks changed to fit that cap.

### Six cases, independently classified

All six exporter, MIR decoder and refinement exits are0; every source-stage hash
is unchanged and every refinement log says `No refinement errors found`. VF exits
are1 for each case. Actual named caller headers1 each; generic helper headers1
and helper-body execution records6 each; generic/ZST-add/negative marked pointer
operation records3 each. These counts establish reachability, not whole proofs.

| Case | New result | First substantive failure / evidence |
| --- | --- | --- |
| positive_generic_const | INCONCLUSIVE; checked arithmetic helper completes | Caller normal post, verified/lib.rs:23: Cannot prove %(get_pointer_address(result), alignof(T_typeid)) = 0. `.add` line41 succeeds; local bounds and all reached helper calls discharge; i=1,2,3 paths finish post/leak checks; residual path fails alignment post |
| positive_generic_mut | INCONCLUSIVE; checked arithmetic helper completes | Same post and path boundary as const; no const-to-mut theorem assumed |
| positive_zst_layout | INCONCLUSIVE; concrete no-patch route blocked by model | verified/lib.rs:20, `assert size == 0`: Cannot prove __result = 0. size_of and align_of calls reached; align==8 assertion not reached |
| positive_zst_add | INCONCLUSIVE; concrete no-patch route blocked by model | verified/lib.rs:21 `.add(i)`: Cannot prove pointer_within_limits(ptr_add_(base, i, Z_type_info)). Return/base equality and final alignment unproved |
| negative_source_byte_offset | EXPECTED_FALSE_POST_FAILURE | Byte `.add(1)` line22 and cast line23 reached; intended modulus8 assertion line25 rejects %(get_pointer_address(ptr_add_(src, 1, uint8_t_typeid)), 8) = 0 |
| negative_destination_byte_offset | EXPECTED_FALSE_POST_FAILURE | Same exact intended assertion and reachability with dst instead of src |

**Generic progress:** both checked helper bodies prove divisibility preservation
under their explicit nonnegative local req and finish leak checks. At the actual
callers, existing `array__inv::<u8>` preserves the same byte resource and supplies
base/end provenance limits; existing min/max provenance lemmas justify address
bounds. `is_valid_layout_size_of_align_of`, `is_power_of_2_pos` and `size_align`
justify nonnegative stride, positive alignment and stride divisibility. Explicit
extent and multiplication bounds, `.add` and all six helper call sites per caller
are reached without a precondition failure. Each new local bound is thus discharged
where reached from the old external resources; no stronger external contract.

The i=1,2,3 proof branches reach final leak checks. The remaining branch
`i != 1 && i != 2 && i != 3` has no helper call and fails the final alignment post.
In the Rust input domain, usize i<=3 leaves i=0; the current ghost proof does not
complete that final case. This is the first remaining generic proof blocker,
not a measured model-extension requirement for generic arithmetic. No whole-unit
normal/no-unwind/resource theorem or complete generic alignment post is claimed.
Symbolic zero stride remains in the generic domain; concrete Z fidelity is separate.

### Saved-evidence replay and classifier regression

The actual header format includes `verified/lib.rs(span)` between timestamp and
`Verifying function`. Recognition now keeps source prefix, exact function name,
one named header, operation reachability, stage/integrity gates, and exact marked
alignment assertion location/content. Diagnostic-note duplicates are not counted
as timestamped execution. Negative acceptance also checks the exact src/dst
byte-add modulus expression; failures before that assertion remain INCONCLUSIVE.

The hosted replay downloads both pinned historical archives, validates zip hashes,
run/head_sha/artifact metadata and actual archived original/verified source hashes,
and writes **separate** derived JSON and full before/after evidence-tree manifests.
The archived logs and classification/aggregate JSON remain unchanged:

| Historical run | Original raw result, preserved | Separate reclassification |
| --- | --- | --- |
| 37529855468 /17ad1f4 | All six INCONCLUSIVE due parse errors | All six INCONCLUSIVE; no intended negatives inferred |
| 37532204465 /9474453 | All six INCONCLUSIVE due missed function headers | Four positives INCONCLUSIVE; both negatives EXPECTED_FALSE_POST_FAILURE on intended assertions |

Hosted tests: **3 unittest groups PASS; 30 fail-closed mutations PASS**. Mutants
cover wrong name/header, missing/duplicate header, missing operation, wrong
assertion location/text/error expression, failed exporter/decode/refinement or
integrity, and parse/unrelated/earlier errors. Input tree manifests before==after.
This is evidence-classification regression, not an additional verifier run at the
historical SHAs and not a replacement for their original recorded outcomes.

### Concrete ZST boundary and composition consequence

[Source-to-model audit](SORT4-ALIGNMENT-MODEL-BOUNDARY.md) traces original
`#[repr(align(8))] pub struct Z;` through exporter/schema/translator into the
unchanged engine. The ADT carries only isReprC=false and empty fields; repr alignment
is absent. Engine verifast1.ml:6508 imposes `0 < sizeof(Z)` on concrete structs,
with no size0 equation for this fieldless nonpacked type. This contradicts the
actual Rust ZST layout, rather than merely omitting a convenient checked lemma.
Typed pointer add uses `i * size_of(Z)`; a positive symbolic stride cannot be
justified from the fixture's zero-byte extent. This provides a source-model explanation
for the limits failure, not a measured causal implication between the two diagnostics.

`size_align` and valid-layout properties cannot consistently prove the missing
size0/align8 calibration. Adding those as trusted premises, changing Z, or deriving
a result from an inconsistent context is inadmissible. The no-patch concrete-Z
route is therefore blocked. This is the phase stop condition; no additional proof
edit or dispatch follows the result. No model correction is implemented.

Generic prefix progress and false-post rejection establish neither automatic copy
UB detection nor repr layout fidelity, current ownership, callback effects or all
sort4 normal/panic posts. They cannot close RAPx's alignment gap by transfer between
models. Restricting RAPx to diagnostics remains justified; a generic composition
is still unavailable. ZST stays in the adopted contract; Kani's prior concrete
results are unchanged and provide no missing universal or layout premise.

**Necessary versus optional VeriFast work:** if this concrete type is proved in VF,
faithful Rust ZST size and repr alignment encoding must be supplied by an explicitly
reviewed model correction, or covered by another independently justified component.
An ordinary new arithmetic lemma cannot repair the existing incompatible size axiom.
Generic bound/divisibility progress required only checked annotations; it supplies
no evidence that a generic alignment-kernel extension, new trusted builtin or the
historical insertion/ManuallyDrop/Drop patch chain is necessary. Remaining callback,
unwind, raw-copy and provenance obligations retain their independent status.

Recommended next decision: review admissibility and minimum scope of Rust layout
encoding/struct-size correction versus another independent layout component before
any implementation. No extension is authorized. One possible later unchanged-tool
proof diagnostic has a new hypothesis: explicitly derive i==0 on the residual
branch from the old usize bounds and prove its existing alignment post. It is
**NOT RUN / NOT AUTHORIZED** after this closeout and cannot close the concrete ZST
boundary by itself. No speculative fourth case, axiom or domain restriction proposed.

### Evidence retained

[Artifact11446132505](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37535499783/artifacts/11446132505),
574662bytes, contains complete live evidence and historical replay bundle, including
original pinned ZIPs/logs/JSON/sources/MIR and separately derived results/tests.
Downloaded ZIP SHA256 (matches API/upload digest):
`45d8363c9b25fb6c2332ae77ee468d2912a765a53fed80651e62d5a79eef1d05`.
Live aggregate SHA256
`48b2ffd48241e358fc5b039593babffab42d1ad9f0aa53736eb411e3b132d157`;
reclassification JSON SHA256
`9559c09b53b1af444cb70066028a9a6a8502d0b3a0987333ba944f5ff4e8134b`;
full Actions log SHA256
`b4c36fcbfa056e27ceff866bf17a6f311326b68c7ccdca291796c8f9b86b9a43`.
Full logs and artifacts inspected; downloads remain outside repository. Historical
reports below, original two runs and their INCONCLUSIVE outcomes are preserved.

## Historical syntax-only checkpoint at f1c0774

Current checkpoint 2026-10-07: **syntax-only continuation CLOSED / INCONCLUSIVE**,
additional budget1/1 used. Generic geometry and ZST calibration remain unproved;
both false-post controls reach and reject the intended assertion on manual audit.
The unchanged automatic classifier reports all six INCONCLUSIVE because it misses
source-prefixed function headers. No active run or further proof/run authority.
Initial37529855468 remains historical INCONCLUSIVE, unchanged below.

## Syntax-only continuation — one NEW run

[Run37532204465](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37532204465),
NEW workflow_dispatch verifast_sort4_alignment/90, exact corrected source
`9474453f231eb600e1ec35d571c8ac4f70fa7138`. Owner specifically authorized this
correction and exactly one additional run from b1ae937. Entry clean local/remote
b1ae937 matched; fork/branch correct, no active experiment. Pushed corrected
SHA matched remote and new head_sha; no Re-run of the initial source.
Created2026-10-06T21:12:28Z; job112504123478 ran21:12:33–21:13:15Z (42s),
FAILURE; replay job SKIPPED. Hosted ubuntu24.04/x86_64. Total cap90min includes
runner setup; wrapper's remaining timeout5390s, runner21.57s/maxRSS529212KiB.
No timeout/OOM, no second dispatch or further proof correction.

Only two helper signature semicolons removed and six contract blocks split.
Adjacent @*//*@ ends/starts are distinct annotation ranges and add no non-ghost
bytes. Static comparison with checked recover_pair (release run37437514808) and
separate contract ranges in verifast-drop-caller-cases.rs preceded dispatch.
All ghost payload tokens, lemma bodies, predicates and //@ statements/assertions
unchanged except the two authorized semicolons. Whole/per-case ghost-stripped
Rust byte-identical to b1ae937; archived originals independently match the old
fixture byte-for-byte. All six cases/markers/order intact. No other source change;
runner/driver/workflow/std, profile, premises, domain, posts and classifier frozen.

Official26.09 archive, binaries, every rsspec, source/schema, Rust/compiler and
SmallSort hashes match the initial profile listed below. Fresh release install
and paired bin/libz3 audit pass. Source809de4596839b739dd999f9e462242c835e3af46,
nightly2026-02-05; no tool/spec/kernel changes. Export args readonly/edition2021/
crate-type lib; VF -rustc_args '--edition 2021' -verbose1; refiner unchanged.
Exporter internally emits -Coverflow_checks=off as before from the same pinned
binary; no new check suppression or skip_specless. Original domain/posts/card
remain [unchanged](SORT4-ALIGNMENT-PHASE.md#experiment-card).

### Per-case proof evidence

All six exporter/decode/refinement exits0; VF exits1. Every stage leaves sources
unchanged, refinement logs say No refinement errors found. MIR preserves generic
const/mut .add<T>, Z .add, byte .add(1) then cast, and size_of/align_of calls with
unwind-Continue. Separate contract ranges are exported and parsed; no parse error.
No full positive normal/unwind/resource theorem is established.

| Case | First substantive VF blocker / exact isolated location | Manual stage evidence | Outcome (raw automatic JSON separately preserved) |
| --- | --- | --- | --- |
| positive_generic_const | prelude_core.rsspec:64: Cannot prove 0 <= address, called at verified/lib.rs:11 div_rem_nonneg | aligned_step_const header1, helper-body records3; caller0, .add not reached | Generic geometry INCONCLUSIVE |
| positive_generic_mut | Same condition/call location | aligned_step_mut header1, helper-body records3; caller0, .add not reached | Generic geometry INCONCLUSIVE |
| positive_zst_layout | verified/lib.rs:20, assert size == 0: Cannot prove __result = 0 | Named caller header1; size_of/align_of calls reached; next align==8 assertion not reached | ZST size0/align8 calibration INCONCLUSIVE |
| positive_zst_add | verified/lib.rs:21 .add: Cannot prove pointer_within_limits(ptr_add_(base,i,Z_type_info)) | Named caller header1, operation records4; no return/post proof | ZST pointer geometry INCONCLUSIVE |
| negative_source_byte_offset | verified/lib.rs:25, assert bad as usize % 8 == 0: Cannot prove %(get_pointer_address(ptr_add_(src,1,uint8_t_typeid)),8) = 0 | Named caller header1, byte-add operation records3, cast and marked assertion reached | Intended false-post rejection observed manually; automatic INCONCLUSIVE |
| negative_destination_byte_offset | Same marked assertion line25 with dst instead of src | Named caller header1, byte-add operation records3, cast and marked assertion reached | Intended false-post rejection observed manually; automatic INCONCLUSIVE |

**First generic blocker:** the checked ghost helper's initial divisibility-lemma
call requires nonnegative address. Its present req does not establish that fact
in the ghost model; the written usize type did not supply it in this proof.
Do not infer a Rust runtime negative address or H_align falsity. No helper post,
generic caller or size_align/caller derivation is reached. A future bound proof
would need separate design/authorization, without silently strengthening the
adopted caller contract or adding a trusted premise.

ZST calibration fails earlier than alignment: this run does not prove size0,
so neither align8 nor base.add(i)==base is available for composition. Decoded Z
has isReprC=false; failure alone does not show every no-patch layout strategy
impossible or that a verifier semantic patch is necessary. ZST add's limits
failure is a separate measured obstacle, not automatic misalignment detection.

Both negatives fail EXACTLY on the intended modulus8 assertion AFTER byte add /
cast; source/export/refinement and legal raw-byte premises preserved. This meets
the original intended-stage requirement on manual audit. It is a false-post
control, with no dereference or copy. It does not establish VF recognition of
Rust repr(align8), automatic copy UB detection, generic geometry, full sort4
safety or a RAPx-to-VF bridge. No false alignment conclusion was proved.

### Automatic classification limitation — no repair or reclassification

Raw aggregate/classification JSONs retain all six INCONCLUSIVE, caller/helper
header counts0. TIMESTAMP_HEADER in the unchanged driver expects
`<time>s: Verifying function 'name'`; actual verbose headers are
`<time>s: verified/lib.rs(<span>): Verifying function 'name'`. The named headers
exist; the count0 does not mean those bodies were unvisited. Manual timed-header
counts above exclude diagnostic note repeats and generated Z support functions.
Negative error-line predicate itself matches line25, but caller_count==1 gate
fails from this header-format mismatch. Pointer/helper statement counting works:
3 per helper,4 for Z add,3 per byte add. No classifier change, replay execution,
threshold relaxation or raw JSON overwrite. Overall gate remains INCONCLUSIVE.

### Evidence and stop

[Artifact11445280961](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37532204465/artifacts/11445280961),
159files/123767bytes; downloaded archive SHA256 matches API/upload digest
`7ef6d71628a06b3c853cd165a3984669b1b4e1d4e1e282f87ec7998ce87411cd`.
Aggregate SHA256 `089dceee6406a531c7a07a1aa39cc73072da07845ac25c4b9e5b1aacc410770d`;
full run log SHA256 `38f9b9bc4d7168d67fb2e52803b93726f0576479e0e737c3f4235df80d252737`.
Corrected fixture SHA256
`eadb4ec6dc234c8cfb94a5f581681d7c2f404b12ea0af8c092105998a52cd3b4`;
runner/driver SHA256 unchanged (listed in initial evidence below).
Full log, six VF/refinement/export/decode logs, MIR and annotation/source boundaries,
profile/integrity/resource records inspected. Exporters .01–.02s, VF .11s each,
refiners .07–.08s, decoders <.01s. Unused-variable/Actions Node warnings noncausal.
Downloads stay outside git; no downloaded code or local verifier/compiler/runner
executed. Local checks are non-executing text/document parsing and diff --check.

**STOP regardless of result, additional budget1/1 used.** Documentation closeout /
commit/push only. No proof/runner/classifier/tool/spec repair or further dispatch.
RAPx0.7.50 stays CLOSED / NO-GO, B/C NOT RUN, Kani unchanged. No generic safety /
layout / operation-UB coverage gained; limited manual assertion-control evidence
is explicitly separate from the automatic result. No semantic VF change shown
necessary by this run. Any further proof correction or NEW run needs a new decision.

## Historical initial hosted result — INCONCLUSIVE

2026-10-06 UTC (2026-10-07 Moscow). **CLOSED / INCONCLUSIVE — fixture annotation syntax failure before
proof obligations.** The one authorized NEW run is used; no active run. This
neither proves nor refutes H_align, and is not a new VeriFast semantic NO-GO.
[Phase/card](SORT4-ALIGNMENT-PHASE.md), [composition design](SORT4-COMPOSITION-ASSESSMENT.md).

## Run and frozen profile

[Run37529855468](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37529855468),
workflow_dispatch, verifast_sort4_alignment/budget90, exact source
`17ad1f48b1eb97f806e03a97b7bf64b24f8ac50b`. Clean fork/research heads matched
at entry and before dispatch; no other active experiment. Created20:53:28UTC,
verification job20:53:33–20:54:10UTC,37s, FAILURE; replay job SKIPPED.
One hosted ubuntu24.04/x86_64 runner. No rerun, alternate profile, patches or
local executable checks. Workflow remains manual-only.

Official VF26.09 archive checked against
`da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa` before
fresh extraction in RUNNER_TEMP; no cached/custom verifier substituted.
VeriFast source/schema809de4596839b739dd999f9e462242c835e3af46, schema SHA256
`7f3ebce320a33bcb956d51b8387754729e6516f4d15ba8dfdc61e6e36f90dfd9` checked.
Rust nightly-2026-02-05 / rustc1.95.0-nightly
`db3e99bbab28c6ca778b13222becdea54533d908`, LLVM22.1.0,
host x86_64-unknown-linux-gnu. Effective ldd resolves paired bin/libz3.so.

Recorded binary SHA256: verifast
`dc672335da76fe1bb06cf7ebca916185c34edb65466df0a937645a437c7f0ecc`,
refinement-checker
`9f38829f30cb3295653ca111b53592946a97807eee54cba438fffed14c8c1ffe`,
exporter
`2b8ebb5373d0bdd82cc163f5a298a4291b89dcdb8630a01bf74149987f2d5e0c`.
All installed rsspec hashes retained; relevant prelude_core
`aba25fb4b0fc4aac2b26537b130c900697bf69933598878eed8e163f8aafa571`,
std/lib
`24c86cd57364d1962e13232bde46117f16b71dc4b8ba6264a4577903cfc53ecb`.
Target SmallSort blob e555fce440872898e47fd5114f32eb15401d07df actively checked,
SHA25632574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959.
No actual sort4 body/callee proof was run by these source-linked geometry fixtures.

## Six isolated cases

Every case has exporter0, Cap'n Proto decode0, refinement0 (No refinement errors
found), verifier1 and per-stage source hashes unchanged. Each original is the
exact ghost-stripped fixture; source/export/ghost boundaries and hashes are
archived. Five pointer cases preserve their actual .add in exported/decoded MIR:
generic const/mut T, concrete const Z, and source/destination byte .add(1) before
cast back to Z. The layout case preserves size_of/align_of calls. MIR includes
the emitted direct unwind-Continue edges; it is not a verified no-unwind result.

| Case | First actual VeriFast error in isolated verified/lib.rs | Intended proof stage reached? | Classification |
| --- | --- | --- | --- |
| positive_generic_const | line10, opening `{` of ghost lemma: Parse error | No helper or caller header/body; no .add proof record | INCONCLUSIVE |
| positive_generic_mut | line10, opening `{` of ghost lemma: Parse error | Same | INCONCLUSIVE |
| positive_zst_layout | line12, `ens`: Parse error | No layout/assertion proof | INCONCLUSIVE |
| positive_zst_add | line13, `ens`: Parse error | No .add/result proof | INCONCLUSIVE |
| negative_source_byte_offset | line14, `ens`: Parse error | Marked alignment assertion at line23 NOT REACHED | INCONCLUSIVE, not intended negative |
| negative_destination_byte_offset | line14, `ens`: Parse error | Marked alignment assertion at line23 NOT REACHED | INCONCLUSIVE, not intended negative |

Total caller headers0, helper headers0, helper-body records0, pointer-operation
records0. Hosted classifier rejects every case as INCONCLUSIVE, retaining raw
exits/errors; no unrelated parser failure counts as intended alignment detection.
No geometry, ZST-layout, full normal/unwind resource post, operation-level UB
coverage or generic-sort4 coverage has been established. No claim of a missed
alignment negative or unsupported repr(align8) follows from this parse failure.

## Cause and exact proposed formatting correction

This was an avoidable fixture-preparation error, not tool installation or a
failed mathematical/resource theorem. Both new ghost lemma signatures were
terminated by `;`, which declares a bodyless lemma, then followed by a body.
The Rust functions put `req`, `ens`, and `on_unwind_ens` in one annotation block;
the pinned frontend expects them as separate contract annotation ranges.
Existing checked recover_pair and natural-block callers show the supported
syntax. Successful Rust export/refinement does not parse/check those contracts
like VeriFast, so their success could not validate the proof annotation syntax.

A separately authorized syntax-only correction would change the two ghost
signatures to the following form, keeping their existing req/ens/body intact:

```text
lem aligned_step_const(address: usize, stride: usize, alignment: usize)
    req ...;
    ens ...;
{ ... }
```

Apply the same removal of the signature semicolon to aligned_step_mut. For all
six Rust functions, keep their exact predicates/assertions/operations but split
contract comments:

```text
/*@ req ...; @*/
/*@ ens ...; @*/
/*@ on_unwind_ens false; @*/
{ ... }
```

No runtime/type/algorithm/signature change, predicate weakening, added premise,
new trusted lemma, disabled check or verifier/parser/spec patch is proposed.
Driver case metadata is generated on the hosted runner and would track new
source lines; no classification relaxation is needed. The correction is described
only, **NOT APPLIED / NOT VERIFIED**. It requires a fresh source SHA and a NEW
hosted run, never rerunning37529855468. The original failing fixtures and evidence
stay intact. A new narrow decision could authorize that formatting correction
and one fresh90min diagnostic under the identical profile/cases/target posts;
it would not reopen any other tool phase.

## Evidence and cost

[Artifact11443817617](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37529855468/artifacts/11443817617),
159files,112183-byte zip; download SHA256 matches API/upload digest:
`f1ca30c7bc50125c09a901e9442ef2af8e596bc06e3dbd6c50bebb4e00ef663f`.
Aggregate JSON SHA256
`2e5d8fce61ee88fc0821139c20f2e9f0e8a6c35e21d0cca85164f1f47e8ea389`;
full Actions log SHA256
`490df197e2dbec659c5c64291d3a7d99582e01fed161479e8654f6fed8435e3c`.
Input fixture SHA256
`36fb4aaf8f070d0be22ff43578b8409d79e6b4fa4b4b8bb4c22e4f4c71547443`,
runner4712c5b8149a52e4f36b47596076eb7610d7b749c745720e7d171fce5ddb75d8,
driver8737ea905ea7472f559349586b5bd4ee2bc42de005ee7efeb6fda57594b59240.
Full per-case original/verified/MIR and stage hashes/resources remain in artifact.
Downloads/logs stayed outside the repository and were not committed.

Runner including verifier/toolchain/schema setup and all cases18.05s,
peak RSS622004KiB; each exporter~.02s, decode<.01s, verifier~.07s,
refinement~.07–.09s. No timeout/OOM. Compiler unused-variable warnings (size,
bad and the unused other pointer) are noncausal; full exporter logs retained.
Actions Node deprecation warnings are noncausal. Full six verifier/refinement
logs, exporter/decoded body/annotation locations, identities and artifact data
were inspected. No downloaded script/processor/verifier was executed locally.

## Remaining boundary and stop

Source-model audit remains: size_align plus valid-layout positivity can support
geometry; .add models provenance/limits separately. Typed copy/points_to do not
expose the needed alignment obligation in inspected pinned paths; byte-to-typed
conversion demands aligned input. No legitimate independent raw-copy detector
negative has been established. This is not repaired or measured by manual
alignment assertions. ZST layout calibration, geometry, caller/selected-pointer
routing, ownership and all five panic posts remain open.

**STOP at1/1 used; no active run.** Documentation closeout/commit/push only.
RAPx0.7.50 A/replay remain CLOSED / NO-GO, B/C NOT RUN, Kani results unchanged.
No full-sort4 proof, new trust extension, extra verification, external message or
publication is authorized. Proposed syntax correction needs a separate decision.
