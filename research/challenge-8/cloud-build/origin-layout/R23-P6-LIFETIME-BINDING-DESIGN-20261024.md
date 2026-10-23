# R23 checked-helper lifetime inventory repair

The fixed paired helper declares `fn<'a>(s: &'a mut [u64])` and retains its
source signature and runtime body. The old validator expects one lifetime in
`Body.generics`, while the exporter fills that list from
`tcx.generics_of(def_id).own_params` (exporter1933–1938). Function late-bound
lifetimes belong to the source/HIR inventory rather than early-bound item
parameters; the expected exported shape remains Cloud-UNVERIFIED.

The candidate checks an empty early-bound MIR list and exactly one plain HIR
lifetime named `'a`, through the existing Reader APIs used by the translator.
Missing, anonymous, renamed, extra, type, const, or early-bound parameters
refuse. Helper identity, captured MIR hash/phase, nonempty contract, complete
typed signature and cast-body equivalence remain mandatory. No erased region
is equated with a logical lifetime and no resource or authority is added.

Changing the helper to force an early lifetime with a where-bound was rejected:
the existing source declaration already expresses the intended lifetime, and
the exported source HIR is the appropriate binding inventory. Actual caller,
std, helper signature, bodies, contracts, normal/unwind, and controls stay fixed.

Primary references: [rustc generic parameters](https://github.com/rust-lang/rustc-dev-guide/blob/main/src/generic-parameters-summary.md)
and [early/late bound lifetimes](https://rust.googlesource.com/rustc-guide/+/e218184b6884f0dcee14e043c83e7c7ff4c0fb6b/src/early-late-bound.md).
These support the static design, not compiler acceptance or proof credit.

The same candidate removes only the unused `mut` binding reported by P5;
`deny(warnings)` remains enabled. Profile6 and phase8 service checks pass;
compiler, HIR inventory and actual proof execution remain unverified.
