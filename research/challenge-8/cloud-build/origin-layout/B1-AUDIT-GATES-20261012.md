# B1 actual-glue runner audit gates

Read-only basis: maintainer review K (`drop-glue-body-v3-20261011-k`), the
current v8 profile and runner, and tool candidate `a158398e336edce9817f62a55733a3470a986d7b`.
This card adds runner evidence only. It changes no compiler semantics, source
posts, trust profile, or provider/build pin.

## Existing gates retained

The generated-glue route keeps its positive plus six caller/body controls, nine
official-refiner admission mutants, and four receiver controls. All must reach
their existing exact stage, predicate, and source-location classifiers. The
post-retirement control remains a diagnostic only and must fail at the actual
caller Drop after the real guard `StorageDead`.

The current `copy-on-drop-prove.py` pipeline already executes
`ordinary_call_normal_unwind` on the rebuilt combined candidate before the
selected-drop campaign and records the effective tool hashes. Do not add a
second copy of that smoke to the generated-glue runner. Historical v4 smoke
receipts do not substitute for the current candidate receipt.

## Additional audit requirements

The positive runner receipt must bind the selected method's actual safety-proof
slot to the pinned source contract/template and show the verifier checked the
actual selected method in the same exported unit. The generated private
function must expose exactly the selected method's single receiver lifetime
binder and one `&mut CopyOnDrop` input using that binder. This records the
translator's existing static checks in typed-AST evidence.

The v6 official-refiner Return-local exception is restricted to a body tagged
as generated glue with unit output and unit `_0`; the original/verified pair
must remain equal as `Some`/`None` options. Additional refiner controls should
exercise untagged unit missing `_0`, non-unit missing `_0`, and populated vs
absent `_0` mismatch through the exact rebuilt refiner. A failure at an earlier
setup/shape gate is not evidence for the Return-local rule.

The rebuilt candidate needs one current normal/unwind smoke (already supplied
by the parent pipeline), plus a default-off/ordinary Drop compatibility control
that includes the two legacy synthetic Drop records. It should show no
generated-glue selection or receiver rewrite for ordinary Drop and preserve
the synthetic records' unqualified defaults. It grants no source-proof credit.

These controls are qualification evidence only. The profile remains
experimental and the concrete-u64/x86_64/len-one scope remains unchanged.
