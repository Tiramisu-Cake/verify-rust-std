# Current-owner physical memory-cell permission probe

## Question and scope

This isolated fixture asks whether the pinned verifier's separation heap permits
one full points-to permission for the destination head after the existing
current-owner resource helper transfers owners, and rejects requesting two full
permissions for that same physical cell. It uses the same generic `T`, `F`,
thread token, source and destination resources, native-`usize` domain, normal
posts, and false unwind post as the checked `current_owner_transposition`
fixture. The positive case is named
`current_owner_transposition_memory_cell_positive`; the matched negative is
`current_owner_transposition_memory_cell_duplicate_negative`.

The checked helper prefix is copied intact from
`current-owner-permutation-cases.rs`, including list definitions, recursive
length and owner-transfer lemmas, the full pointer/domain predicates, and
`current_owner_transposition_resource`. In each case that helper first turns
source-owned resources plus the existing transposed destination values into
source values plus destination-owned resources. The positive body opens the
resulting destination-owned predicate and `array`, asserts exactly one full
`*dst |-> head(transposition_values(vs, i, j))` permission, then recloses both
predicates. The negative performs the same sequence and asserts two such full
permissions to the identical `dst` and identical current head value. Since
`i < j < n` and `n >= 2`, the head is a positive-stride array cell in the
non-ZST domain.

## Trust premises and soundness question

The pinned source `prelude_core.original.rsspec` defines nonempty `array<T>`
as full `*p |-> value` plus recursive `array(p + 1, ...)`, with the value list
cons matching that head. Thus opening the destination array exposes physical
head-cell permission directly. The probe relies on the verifier's separation
heap accounting for full points-to chunks at one pointer. It introduces no new
axiom, lemma, ownership bridge, `T.own` claim, or changes to the prelude or
verifier. The `foreach(..., own::<T>(t))` resources remain only the existing
transferred owner sequence; the duplicate request concerns physical memory
permission, even if `T::own` is empty or copyable.

This is a calibration of the pinned memory-permission semantics, not a new
soundness argument. A refusal at the duplicate target would support only the
specific same-cell permission uniqueness behavior exercised by this proof. A
failure before that target, at a helper, in the frontend, or at an unrelated
VC does not count as the intended negative. A successful duplicate assertion
would falsify the expected uniqueness behavior and must be investigated before
any claim is made.

## Expected stages and gates

The positive case should check every helper body and the case body, prove the
single full head permission, restore the complete destination array and owned
predicate, and satisfy the unchanged full normal post. It must also pass source,
refinement, return, leak, and dead-code gates. The negative shares the same
full preconditions and full normal/unwind posts; its sole intended failure is
the `TARGET` assertion requesting duplicate full permission for the same head
cell. The first hosted run is **CALIBRATION_ONLY**: do not classify its result
as a target negative or encode an expected diagnostic until the complete Cloud
evidence identifies the refusal stage, predicate, and target location. Both
cases must retain unchanged F framing, source bytes, payload, and unwind post.

No result here proves an actual copy, actual SmallSort behavior, a caller or
Freeze/share bridge, callback behavior, or ownership/resource transfer for a
real invocation. The fixture is a conditional ghost-resource probe only.

## Fresh Cloud evidence — Build 742d setup refusal

Build `742da9ef-c853-473d-b2c1-d38ff55a04c1`, proof/infra
`8b3d747109fc643215bce4906dc0834836200623`, archive SHA-256
`fe3f288581abb4c6b15fb69ed0e47eb1da9c2dcb47710d1426f3ac301fd1fe64`.
The archive and external text logs were collected; the summary reports
`diagnostic_complete=true`, `evidence_complete=true`, but `smoke_success=false`
and `verification_accepted=false`.

Both profiles report both cases `INCONCLUSIVE`. For the positive and duplicate
cases in both `checked-current-owner-memory-cell` and its `-stock` counterpart,
the exact first failure is at **exporter**, exit `127`:

`vf-rust-mir-exporter: error while loading shared libraries: librustc_driver-d58e90066811bb5c.so: cannot open shared object file: No such file or directory`

Per case the stage vector is exporter `127`, decode `125`, VeriFast `125`,
refinement `0`. Decode and VeriFast were explicitly not run after exporter
failure. Each case has zero visited/expected-body executions, zero returns and
leak checks; there is no VeriFast assertion error, dead-code finding, or target
location. Refinement success does not make the proof executable. Group driver
exit codes are zero because the harness retained these as inconclusive rows;
they are not theorem results.

This is an exporter runtime-loader/setup failure shared by both cases and both
tool profiles, not a memory-permission proof refusal. The positive never
established one valid full head-cell permission, so the duplicate assertion
cannot be calibrated from this Build. Leave it without expected rejection
metadata and keep both cases inconclusive. No proof annotation change is
justified by this evidence; the next useful result requires a fresh hosted run
whose exporter can load the pinned Rust compiler driver, then inspect the full
positive obligation before judging the duplicate-cell target.

Operational repair before next run: the outer memory-cell invocation must
provide the same retained compiler/tool LD_LIBRARY_PATH as run.sh; the child
run.sh export does not propagate to merge.sh. No new library/dependency/tool
is installed, and exporter/compiler/schema hashes stay pinned. Set only this
group command environment to sysroot/lib:toolhome/bin:/tmp/vfdeps-adf88dc/lib
plus existing path; record sysroot/toolhome identity. Hypothesis exporter now
reaches decode/VF, then positiveonecell and raw duplicate calibration. Any
remaining setup/frontend/helper failure retains INCONCLUSIVE/nooracle.

## Fresh Cloud evidence — Build 9ed4 raw calibration

Build `9ed4` completed for both `checked-current-owner-memory-cell` and
`checked-current-owner-memory-cell-stock`. In both profiles the positive case
is `PASS`: exporter, decode, VeriFast, and refinement all exit zero; all six
expected bodies are visited (the case plus the five checked helpers); all ten
return and ten leak records are present; source hashes remain unchanged; there
are no VeriFast errors or dead-code records; and `full_positive_gate` is true.
This establishes the one-full-head-cell assertion and successful restoration
to the original complete normal post under the fixture's unchanged domain,
frames, `F`, owners, and false unwind post.

In both profiles the duplicate case reaches its unique `TARGET` assertion
after all six expected bodies are visited. Its raw VeriFast refusal is exactly:

`verified/lib.rs(240,76-79): error: No matching heap chunks: points_to<T>(dst, head(transposition_values(T_typeid, vs, i, j)))`

The negative has no target-case return/leak record, as expected after this
assertion failure; the five helper bodies have their expected ten return and
leak records. Exporter, decode, and refinement exit zero, sources are unchanged,
and there are no dead-code records or earlier errors. This is raw calibration
evidence only; both aggregate classifiers still report the negative as
`INCONCLUSIVE` because no rejection oracle was yet declared.

For the next fresh hosted run, annotate only the duplicate `TARGET` line with
`EXPECT_REJECTION` kind `memory_permission`, file `verified/lib.rs`, dynamic
`error_line=TARGET`, columns 76–79, and the exact diagnostic above. The
classifier must continue to require a full-positive pass in the same profile
and the negative's exact target-only refusal. Keep the source/helper prefix,
both complete posts, and all resources unchanged. A fresh run is required to
accept this oracle; Build 9ed4 itself remains a calibration result and does not
change the existing fixture's original positive or false-entry cases.

## Fresh matched oracle — closing DAY Build2bd4

Build `2bd48b65-6eff-4233-b2d8-fabcfb97360a`, exact infra/proof
`4cc1211c4120c8701577f2b2a922ca6f47d0480f`, collector SUCCESS451 seconds,
10:44:50.596–10:52:20.817UTC. Archive SHA-256
`5a2461f607f1b32a3fb5d5f2f3d3da8eb161ab5bbf020819ace7505c735cc3f5`.
Fixture SHA-256 `19dfab09c5b0069fada151517d642bec24c19f0333507db094c7dd358f28114b`,
source-admission SHA-256 `a280e8ff994ae5dbe7bb579a3fea9b44b355df3187caaa7509f5840d0017375f`.

Both stock and six-component profiles have positive PASS, all stages0, six
checked bodies,10returns/10leaks, unchanged sources/fullposts, noerror/dead.
Both duplicate cases are EXPECTED_REJECTION, stage exporter/decode/VF/refinement
0/0/1/0, all six bodies reached, sole exact TARGET error at241:76–79:
`No matching heap chunks: points_to<T>(dst, head(transposition_values(T_typeid, vs, i, j)))`.
Five checked helpers have9returns/9leaks; target has0/0 after its intended refusal.
No earlier/unrelated errors or dead-code records. All12positive and28negative
fail-closed classifier controls pass perprofile. Ghost stripping preserves
runtime bytes; expected oracle kindmemory_permission and exact location/message
match. The extra comment shifts the target from240 to241, not its obligation.

Erratum for the preceding9ed raw-calibration paragraph: its five helpers also
have **9** return/leak records, not10. The positive's total10 includes the
positive target. Reinspection of retained9ed classification confirms9/9 for
the negative; no theorem/classification changes from this count correction.

This completes this specific same-cell physical-permission calibration under
the pinned profiles. The source/destination/current owners and F frame remain
conditional supplied resources; destination bytes must already equal the
current transposition. It does not prove actualcopy/caller, unrestricted safety,
T.own uniqueness, arbitrary-n actualmemory/callback, generic/ZST, or soundness
of six/kernel/cleanup. Overall verification_accepted remainsfalse.
