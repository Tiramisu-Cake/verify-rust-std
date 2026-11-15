# Worker14 extraction handoff — slice03

Source `d0345ddf4f70d10caf5ee34ddca402867264379e` is a single coherent commit on accepted
`932fb8395a58f8c86c0d702ba2cae835823b2962` (coordinator acceptance run43701587141).
This is author static review; worker15 independent review is **PENDING**. No native
compilation/verification, push or CI was performed.

The delta restores A1/A2 and RawEq from F without changing the accepted model: Pat keeps
its enclosing offset, enum variant masks are compared in local coordinates then composed
once, and RawEq checks every byte of both pointees, including padding. Layout failure
emits Unsupported. RawEq is removed from the skip list; both reference operands seed
delayed relevance. CheckAs reborrows reference places through a raw address and reports
the explicit checked pointee type. The shared helper and builder changes are paired;
all other CheckAs users keep their signatures and existing raw-pointer behavior.

Source ownership is canonical20 parts plus the two-line minus/plus UintTy import hunk
assigned to its first consumer by SOURCE-MAP-CORRECTION.json. That neutral import was
missed in the original stage0 map and caught by manual compile-seam review. No storage,
protocol, runtime, closure or F7 semantic part was moved. Canonical source-map/oracle-map
areas and all historical receipts are unchanged. SOURCE-MAP-DELTA.json records the
effective correction and consumed parts; extraction from4 must honor that correction.

Nineteen whole final fixture pairs are introduced at their mapped earliest head3:
four owner3 u8 mixed raw/eq orders, plus15 owner2 immutable masks, promoted RawEq and
immutable static/subrange/relocation controls. Exact sources, flags, assertions and
goldens equal F. Original B1/upstream and accepted1/2 tests remain byte-identical.
ORACLE-DELTA.json preserves the actual oracle precision (exact property blocks/counts
where provided, literal-only where F uses them), with no stronger claim invented.
The intrinsics raw_eq row is exact F and retains layout/origin qualification.
All19 selected goldens are literal-only in F (10 SUCCESSFUL,9 FAILED); none is promoted
to an exact property-count oracle. The legal-subrange fixture intentionally keeps its
documented false-positive FAILED outcome and `[u8; 3]` diagnostic.

Nine complete owner3 fixtures remain absent and PENDING on4, without splitting roots:
four raw-MU mixed fixtures, nested-pat-data, nested-pat-padding,
nested-enum-same-padding, nested-enum-different-padding and raw-eq-uninit.
Their exact F input/golden hashes, assertions and source parts are retained in SLICE.json
and ORACLE-DELTA.json. In particular u8 RawEq does not qualify nested offsets or the
multi-root raw-eq-uninit oracle. Owner1 integration remains pending4/5 and owner2 later
storage/contract consumers retain their earlier pending receipts.

COMPILE-SEAMS.md documents the mandatory whole changed-file inventory, current imports/
impls, inherited and new API call contracts and manual symbol bindings. Its final audit
is bounded static evidence, not Rust compilation. STATIC-VALIDATION.json also checks
deterministic extraction,22 original part hashes, protected paths, existing tests,
fixture equality and patch endpoints using temporary alternate Git indexes.
Applying residual-to-F.patch reaches F's tree; that endpoint test does not establish
that unimplemented heads4–7 have been correctly recomposed or qualified.

Next owner: worker15 reviews exact source/tree plus this correction and prepares its
own CI-only overlay/request. Coordinator alone accepts review and dispatches Quick.
No PR description/publication or change to B1/freeze refs is authorized here.
