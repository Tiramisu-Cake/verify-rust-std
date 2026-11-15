# Slice03 validation — static only

Candidate `d0345ddf4f70d10caf5ee34ddca402867264379e` has exactly accepted2 as its parent;
one source commit,44 changed paths (five production Rust files,38 fixture/golden paths,
one intrinsics docs row). No existing test was modified, removed, ignored or weakened.

STATIC-VALIDATION.json checks the accepted parent reconstruction, deterministic mapped
extraction,22 effective source parts (20 original + UintTy import pair), canonical
part hashes and earlier-owner preservation,19 whole exact-F fixtures, nine deferred
owner3 fixtures absent, protected paths unchanged, git diff --check, and exact source/
residual patch endpoints in temporary alternate indexes. No future source commit is
claimed by the residual endpoint check.

Mandatory compile-seam check: SEAM-AUDIT-03.json at the final immutable SHA reports
PASS_BOUNDED_STATIC_SEAM_AUDIT, errors[],24 changed Rust files; ten synthetic checker
tests pass. COMPILE-SEAMS.md supplies manual import/impl/consumer review. The automated
token check does not resolve names: its initial PASS missed UintTy's absent import;
manual review caught and corrected that prerequisite (SEAM-PRIOR.json and
SOURCE-MAP-CORRECTION.json). A draft validation assertion was also narrowed to enum
fields because legitimate union fields use absolute offsets; no source change was
made for that assertion correction.

The research repository's whole-patch whitespace check reports literal single-space
context lines inside the saved unified patches. Their exact bytes are retained for
patch identity/application; the non-patch research whitespace check passes. The Kani
source diff itself passes git diff --check without exclusions.

Canonical research maps are untouched; this package supplies the exact neutral-import
ownership delta, to be applied before future4 extraction. Ancestor1/2 source parts and
their historical receipts remain unchanged. READ-INPUTS.json pins planning/reference
inputs; historical F acceptance does not qualify this intermediate head.

Native fmt/build/clippy/unit/expected/verifier results, local builds, push, CI and full
logical recomposition: **NOT_RUN**. Worker15 independent review and coordinator Quick:
**PENDING**. No formal proof credit. Nested Pat/enum offsets and multi-root raw-eq-uninit
qualification remain PENDING exact cumulative4; owner1 integration stays PENDING4/5.
