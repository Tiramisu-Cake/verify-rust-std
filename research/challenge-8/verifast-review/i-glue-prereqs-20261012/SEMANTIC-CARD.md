# Narrow I prerequisites: unqualified candidate

Decision: **NOT_QUALIFIED / NOT_ADOPTED**. The additive implementation exists and
has independent design and final diff/evidence reviews. It has not executed a
proof, closed C0–C2 or established preservation on the new effective tool.

Exact domain: concrete u64 and one nongeneric CopyOnDrop, x86_64-unknown-linux-gnu,
compiler f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f, complete admitted source SHA-256
pairs in fixture-admission.json. Baseline tool I b6cb276afd13107c2a90ca50acbb12ff0a992dd8;
glue reference a158398e336edce9817f62a55733a3470a986d7b; starting project98bd08b1.
New tool c23278c3ea716b64d2fdeee134b834095956ac56, tree3a2c16640c10958a5d185dc8d928c47950406907.
Opt-in: SMALLSORT_I_GLUE_PREREQS=experimental-i-glue-prereqs-u64-v1.

B-ORIGIN uses compiler local bindings, actual StorageLive/Dead and live storage
incarnations. Incoming resource association is physical Chunk identity; equality
of addresses or chunks cannot grant it. Consumption/reproduction loses the
association. Retirement removes liveness; new storage may reuse a numeric address.
Numeric separation applies only to live supported u64 resources with existing I
bounds checked. Existing points_to__limits is invoked as an ordinary checked
resource lemma; no arbitrary allocator bounds axiom was introduced.

B-LAYOUT admits exact compiler/source/type/target/field/layout metadata before
facts. The one guard layout is size24, align8, recorded offsets0/8/16 and field
sizes8, with full shape and mutability checking. Compiler metadata constant is
corroborated by independent runner compiler pin; DefPathHash alone is insufficient.
Guard liveness supplies no general numeric guard24 bounds/separation rule.

B-FREEZE retains strict inference/type/bounds and scoped-escape checks. At strict
heap reconstruction only the current surviving old Chunk can map to its checked
frozen replacement. Mapping and incoming/storage state restore per continuation.
The consumer's tmp allocation precedes tail.read, so no general transport through
resource-transforming reads is needed. Strict-survivor and reconstruction controls
are prepared, not verified.

B-DEFAULT isolates markers, qualified layout, tracked MD references and concrete
normal Drop effect post under the exact opt-in profile/source admission. Invalid,
partial and mixed profiles are explicit refusals. Profile-off I paths are retained
by static diff, but new-tool regression evidence remains NOT_RUN. Stock unwind
post stays intact; actual Drop body and canonical safety_proof remain required.
The effect post is necessary for the safety_proof's existing canonical close;
no generated Drop routing or assumed callee summary is introduced.

No generic/ZST/array model extension; no whole merge chain, Instance observation,
refiner rewrite, C3 theorem, B1/B2/O23 closure or adoption. I empty Rust structs,
MDnew, as_mut_ptr, certified pointer-drop, FRAME/Bool/native/selector rules remain
required invariants. Existing PASS/upstream candidates retain their original pins.
F1 fixed copy is preserved, not newly qualified. Merge-owned v8, insert_tail,
panic cleanup, inputs and coordinator were not edited.

Rejected rules with reasons are in DESIGN.md: local-name span exclusion lacks
live allocation evidence; chunk similarity recreates consumed authority; broad
freeze bypass drops I's trust checks; new whole-guard numeric bounds lack a checked
resource derivation. Passing hashes or a built exporter justify none of these.

See RESULTS.json and GATE-RESULTS.md for executed substeps versus NOT_RUN;
PINS.json records exact executed runner pins. No effective verifier/refiner binary
set exists because console generation failed. Independent FINAL-REVIEW.md confirms
NOT_QUALIFIED and identifies scalar-list decoder support as the next hypothesis.
