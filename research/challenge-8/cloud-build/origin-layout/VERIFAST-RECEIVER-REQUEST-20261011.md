> Historical diagnostic material. 2026-10-11 owner correction: development ownership remains **merge**; maintainer receives a developed candidate for review/compatibility/integration. This request does not replace development and has not been sent.

# Prepared VeriFast owner request — not sent externally

Frozen profile `experimental-merge-qualified-guard-onecell-v1`, SHA256
`0b8cf55b0e7b5a1d0e0595b1483726459cb1d2f40264311e2014d3580ad189b8`,
NOT_ACCEPTED / NOT_FOR_INTEGRATION. Effective source/dependencies are pinned in
EFFECTIVE-SOURCE.json and prior qualification receipts. Domain concrete-u64,
x86_64, len==1. No trusted semantic patch is proposed for implementation in this
session. This request is a local review artifact, not a message or upstream issue.

## Minimal reproducer

Exact committed recipe is the existing merge Cloud lane, BUILD-MODE.json
caller-composition-minimal, and onecell-caller-composition.py `_prepare`.
New case `receiver_origin_probe` differs from existing positive by one ghost
assertion after full physical field-frame production and before checked helper:

```rust
//@ assert (*guard_ptr).src |-> guard_src &*& (*guard_ptr).dst |-> guard_dst &*& (*guard_ptr).len |-> guard_len &*& struct_CopyOnDrop_padding(guard_ptr);
//@ assert ref_origin(guard_ptr) == guard_ptr; // TARGET: receiver origin fixedpoint
checked_len1_body(guard_ptr);
```

The second assertion is the diagnostic only; checked_len1_body remains the saved
control and is not presented as an actual Drop method. Source read/constructor
are actual tail.read and CopyOnDrop {src:&*tmp,dst:tail,len:1}. Generated/injected
source is emitted solely into disposable Cloud artifacts, not committed.
Fresh Build846517a9-5a8b-4a18-827c-3f74fa148903, exactproof=infrac8962f4b8e10a8a1b457826272d101631fd23d97, archive
d5a86538d2ace52897d8974697eab0c3af6ad99627143874d35d30ed836e9527:
full archive/inventory/config/source/text index and chunks verified. Source/MIR/AST/refinement admit; physical frame158 executes; first error159:42–44:
`Cannot prove ref_origin(gap_guard_addr) = gap_guard_addr.`
Raw CloudFAILURE/INCONCLUSIVE retained; corrected exact-message savedreplay4/4
is not a new proof. RECEIVER-QUALIFICATION-20261011.json pins raw inputs and replay.

Input resources at the probe: caller-derived full src/dst/len fields and padding,
source-quarter singleton, full destination gap, CURRENT u64 owner, type_interp,
thread token/currentThread, live guard/tmp geometry and separation. No receiver
origin premise, no invented ref_mut_end_token, no assumed body summary.

## Existing rules and precise question

create_ref_mut gives physical points-to plus opaque end-token, without origin
fixedpoint; end_ref_mut only returns original storage. The actual frozen mutable
Ref path emits AddressOf and therefore produces neither token nor creation-call
result. Origin geometry/idempotence do not establish fixedpoint of an arbitrary g.

Full-borrow construction is possible: close full FBC from fields/padding/own,
begin_lifetime, borrow(k,FBC(t,g)). reborrow_ref_mut then transfers FBC to r and
ensures ref_origin(r)==r. This does not ensure r==g and is a regular function,
not an arbitrary ghost lemma. Do not fix the problem by adding full_borrow or
origin as a caller precondition, or by replacing the actual receiver with r.

Question for owner: which existing checked, source-bound operation establishes
a receiver r for the actual CopyOnDrop Drop DefId from these physical caller
resources and returns/recovers the original guard/payload? If no existing rule
applies, provide a separately reviewed rule/lowering/interface proposal with
alias/provenance rationale and admission/regression controls BEFORE a patch.
The review must cover full-borrow conversion, source receiver binding, preserved
fields/padding and borrow-end/lifetime conservation, not just origin geometry.

## Separate dispatch interface boundary

An explicit Drop::drop runtime call is forbidden by Rust (E0040). Frozen Drop
terminator lowers to generic std::ptr::drop_in_place(AddressOf(place)); its
current contract returns storage/thread without the CopyOnDrop CURRENT effect.
Calling or proving a different raw-pointer helper does not reach actual method
DefId, and a stronger assumed generic summary would bypass the obligation.

Needed next experiment: smallest compiler-selected destructor caller with unique
source/DefId/MIR bindings, same-source checked actual Drop body, and full-FBC
handoff into that receiver. A verified explicit body dispatch and generated glue
are separate results; do not claim panic cleanup from an ordinary unwind smoke.
If the existing framework offers a way to expose the method separately, its
relationship to actual code must be supplied and checked before using it.

## Required controls for a future bridge

- Saved helper-positive retained; false just before actual call and after returned
  CURRENT effect, with the target reached and no dead-code/vacuity.
- Remove necessary receiver/FBC ownership from the sole caller resource set,
  leaving no alternative full frame/owner or reconstruction path. The failure
  must occur at actual receiver contract, not frontend/binding/preparation.
- Missing-source quarter at the actual checked copy/callee obligation.
- One original source/destination/CURRENT resource set cannot satisfy two
  simultaneous full effects. Use a Sep assertion requiring both full predicates;
  do not use close;close, whose auto-open/refold is a known bad negative oracle.
- Preserve original full normal posts and return/free/leak checks, source/MIR/AST
  identity and no assume/leak/unchecked summary. Preserve normal/unwind smokes.
- Prove any suppression of automatic second destructor call. Do not use an
  unverified forget/ManuallyDrop wrapper as an ownership/effect bridge.

These actual-method controls are NOT_RUN in the receiver-localization probe.
Historical len1 missing-source/duplication controls remain saved evidence at
1396ff47/d491b937 and their qualified replay; no new proof credit from rereading.

Pure-origin workaround audit: r=ref_origin(g) is idempotent, but no points_to,
array or to_u8s rule transfers g-indexed guard permissions to different r
provenance. Struct frame matching uses exact SMT pointer identity. Heap-allocation
origin postconditions do not apply to the actual stack guard. Such a ghost
substitution would still leave FBC(t,r) and actual compiled receiver binding open.
