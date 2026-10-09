# Narrow allocation-span candidate

Design selected before implementation (commentary at minute18); written rationale
file creation initially targeted the wrong directory and was corrected before any
commit or execution. Owner merge; authorized phase MERGE-ALLOCATION-SPAN-PATCH-CLOUD-2026-10-09.

Missing fact: sizeof(T)>0 implies src+sizeof(T)<=dst OR dst+sizeof(T)<=src.
Consumer: actual insert_tail550/551 tmp=ManuallyDrop::new(tail.read()), shared &*tmp,
CopyOnDrop literal-one diagnostic recovery. Existing storage conversions conserve
fraction/value and derive alignment, bounds/nonoverflow; actual constructor span
failed before FBC. Actual557/558 remain subsequent.

Only at creation of an actual non-ghost address-taken Rust local, after initializer
evaluation and before local storage production: compare numeric extent to exposed
existing generic initialized/uninitialized points-to chunks whose real fraction
is proved positive. Each chunk denotes simultaneously live physical storage covering
sizeof(U), including the incoming tail uninitialized gap after read. The new local
is independent live stack storage; allocation identity is its creation event, not
fresh symbol/provenance inequality. Subobjects are covered only by their own extent.
No arbitrary raw pointer or closed predicate is scanned. Both zero extents are guarded.
Dummy leaked fractions excluded; unproved-positive coefficients are skipped.

No resource is consumed/produced by the rule, and no value, fraction, initialization,
validity, reference debt, lifetime token or T.own changes. Existing tmp complementary
share, shared reference, guard fields/padding and sole CURRENT owner are preserved.
Source-specific own stores pure separation proved at constructor; FBC open returns
it for current src/dst, without an unrelated old held_ref equality or supplied span.

There is no permanent registry: facts concern those exact pointer numbers at creation.
Once old storage has retired, a later local is not constrained against an old raw
pointer, so lifetime address reuse remains possible. Same-allocation aliases are
not compared to each other; overlapping readonly fractions stay legal. Hidden storage
means incomplete coverage, not a claimed global allocation invariant.

Trust change: verifast.ml kernel allocation semantics only. Translator/parser/prelude,
exporter/refiner/copy spec and checks unchanged. Candidate NOT_ACCEPTED; independent
Sol semantic review found no concrete counterexample under full-size live storage
interpretation, noted closed/other resource forms and unsupported sizeof limits.
Tests are evidence, not a global soundness proof. Broad memory model rewrite excluded.

Predeclared gates: actual pre/post-FBC span, full positive and after_recovery_false;
new generic live local against fractional live incoming storage with restoration;
same-allocation readonly overlapping aliases reject at marked span assertion;
raw pointer without physical storage rejects at marked span assertion; ZST no
address-distinctness claim; retired-local pointer no address-distinctness claim.
Setup failures are INCONCLUSIVE. Recovery false counts only after actual recovery.
All compiler/extraction/verifier executions Cloud-only; old PASS not new evidence.

Critical code review before first dispatch identified two existing size-model traps:
sizeof_core is partial on Rust function/projection types; concrete StructType size
is axiomatized positive even for legal ZSTs. Revision8c1386a8 restricts BOTH new and
exposed pointee extents to scalar/pointer or abstract generic parameter types, skipping
all concrete structs, arrays and unsupported forms. Actual transparent MD tmp is T.
The generic condition remains sizeof(T)>0; abstract zero extent supplies no separation.
No new concrete struct/ZST layout claim is made. This scope restriction avoids relying
on the misleading concrete struct positivity axiom. Dedicated generic zero-extent and
retired-local numeric distinctness controls must reject at intended assertion; they
are no longer omitted gates. Concrete layout qualification remains open independently.

Remaining independent review caveat: the whitelist does not repair the upstream
concrete-struct sizeof axiom through generic specialization (e.g. T=()). The new
conditional formula is valid with true live byte extents, and the actual fragment
has its original positive-size domain. This candidate therefore is NOT an all-T/
ZST model qualification. Generic size0 and retired-address controls probe the rule;
they do not certify accurate concrete ZST instantiation. Maintainer review must
retain this existing trusted-size-model gate before common-profile acceptance.

## Retirement gate finding before main cutoff

Fresh11cc507f evidence proves q!=saved in the proposed retired-local control, because the Cloud proof AST hoists tmp0/tmp1 DeclStmt into one function block and frees storage only at return. Ending the readonly reference lifetime k0 is not the storage lifetime end of tmp0 in this AST. Therefore this test cannot certify lawful runtime local address reuse. More seriously, the current rule's premise that every exposed local storage chunk denotes a simultaneously live actual Rust byte extent is not yet justified under that hoisting/StorageDead abstraction. Treat this as an integration-blocking semantic gate, not as a demonstrated upstream bug or a global soundness result. No permanent registry exists in the candidate, but that alone does not resolve translator-extended resource lifetimes. Need to distinguish genuinely live incoming regions from same-function locals whose runtime lifetimes may have ended. The final bounded Build already begun checks minimal positive and owner/bytecopy assertions; it does not repair or qualify this lifetime boundary. No new mechanism or firstshift alternative starts after main cutoff.
