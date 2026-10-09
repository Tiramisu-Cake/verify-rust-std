# Merge allocation-span NO-GO research package

Owner merge; maintainer recipient is the VeriFast repository role. Publication is
review availability only, not receipt, integration, common-profile acceptance or
upstream publication. User explicitly authorized this package/channel.

Base VeriFast f76012fb518703b1d98e243ac4f487f16877cfcb.
Candidate commits: 2f61f966a4a2549cb016164e35848abd21594a6f,
8c1386a802ba2ff43ffdd6787eaef5e47bf068e1.
Only src/verifast.ml changes (35 lines) in the transferable tool chain.
DO NOT INTEGRATE this candidate: the translated local storage lifetime boundary
is not soundly related to lawful Rust address reuse. See RESULT.md and rationale.
Use `git -c core.whitespace=cr-at-eol am code/commits.mbox` from exact base, or fetch code/candidate.bundle
merge/allocation-span-20261009. Bundle verify requires base already present.
Combined code patch lives in inputs/.../insertion-onecell/allocation-span.patch.

Mechanism: at actual Rust address-taken local creation compare its true numeric
extent against exposed existing live generic typed storage with proved positive
real coefficient. Add pure conditional disjoint intervals; consume/create nothing.
No provenance inequality or arbitrary raw pointer implies disjoint addresses.
Exclude dummy coefficients; both zero extents guarded. Restrict to scalar/pointer/
abstract generic extents; concrete structs/arrays/unsupported size forms skipped.
Closed predicates/other resource forms stay outside coverage.

Trust change: kernel local allocation semantics. Translator/parser/prelude/exporter/
refiner/copy contract and leak/validity/unwind checks unchanged by this patch.
Existing six-patch and tracked-MD profile dependencies are supplied separately;
do not silently incorporate this candidate into a common accepted profile.
Concrete struct sizeof positivity is a known existing ZST layout limitation;
generic instantiation through T=() is NOT qualified by abstract size0 controls.
The actual source-linked fragment's positive-size domain/premises stay explicit.

Source integration stores only constructor-proved pure geometry in guard own;
canonical FBC returns it for current physical src/dst. Runtime tmp/read/shared src/
guard constructor and signatures unchanged. Actual std lines550/551 are linked by
prepare.py to sourceSHA85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1.
The completed copy/recovery fragment would still not prove Drop/glue, comparator,
all insert_tail or firstshift557/558.

Fresh Cloud results/evidence and final state are added in RESULT.md and manifest.
Original MD4 controls are historical only, NOT_RUN on the candidate profile.
All five actual fragment cases including FBC/owner controls are selected in the second Build.
Local static checks and synthetic classifier/replay have no proof credit.

Reproduce only under a newly authorized Cloud account/window and existing v2
coordinator, owner/ledger slot admission; never reopen this phase's final account.
Final exact infra/proof 3346ba22e17aa1ad3206db565f2f9743dd6e4e26 selects merge recipe,
pinned-objects source and timeouts. Full profile dependencies, release exporter/
refiner/compiler/solver pins are recorded in input PROFILE.json and evidence.
