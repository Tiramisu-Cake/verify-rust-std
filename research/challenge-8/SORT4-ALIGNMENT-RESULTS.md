# Independent H_align gate: hosted results

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
