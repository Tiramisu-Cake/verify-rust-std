# Static comparator migration

Base std872d. Source-only candidate identities are in static-audit.json and review-spec.json.
This package claims preparation, not compilation, MIR lowering, PFC acceptance or B1/B2 credit.

| Files / edge | Change / invariant |
|---|---|
| merge/profiles.rs Profile + identity_profile | CMP storage becomes fn cmp; macro directly calls original comparator expression. No fn value is stored or cast. |
| swap_profile → swap_if_less | No comparator parameter/identity requires. Direct typed closure invokes P::cmp. Geometry, two-cell frame, transfer/order posts unchanged. |
| sort4_profile → sort4_stable | Same direct closure, exact original geometry/destination frame/order/full-model count. Reading adapters retain both volatile reads. |
| insert_tail_profile → insert_tail | Same direct closure; sorted-prefix premise, span geometry, full-model probe count and frame unchanged. |
| merge_profile → bidirectional_merge → merge_up/down | Same direct closure through generic F; FreezeMarker bound, disjoint spans, length, sorted halves and posts unchanged. |
| network.rs | All Profile impls, wrapper callers and branch covers call cmp directly. Existing PFC roots retain domains/indices/unwind bounds. Eleven new relation roots. |
| merge.rs | All sort4/merge length/scratch48 callers drop CMP argument, retaining source/destination allocation geometry and lengths. |
| forwarding_contracts.rs | Three concrete N2 adapters become callback-free; typed direct closure calls original local comparator; identity guard disappears by API construction. Geometry, frame, full-value count and ordered posts unchanged. |
| profiles consumers | Five new verified-summary roots: swap LtU8/backing4; sort4 Sort4ReadU64/B16 exact disjoint arrays; insert LtU8/backing17 symbolic tail; merge LtU8/len4 disjoint arrays. Each has an exact existing PFC companion in request. |
| existing helper_contracts{,_wide}, insert_tail_contracts | Already use direct FnDef/arbitrary-bool callbacks. No Profile references or pointer values. Their existing summary consumers and frame controls remain untouched. They do NOT qualify new profile closure instances. |
| verify.rs | Documentation updated only; no module registration, runtime/sorting model changes. |

| Profile | Runtime comparator / independent model order |
|---|---|
| LtU8 / LtI32 / LtU64 | Original corresponding lt function, x>>1 keys (signed i32 shift remains signed). Full scalar model. |
| Sort4ReadU64 | Both volatile argument reads, then original lt_u64. Full u64 model; x>>1 order. |
| Sort4ReadB16 | Both volatile argument reads, then original lt_b16 (byte0). Full16-byte model. |
| StrictU8 / StrictU64 | Original strict_less with full scalar order. |
| CellI32 | Original cell_value_less, get() full scalar model and order. |
| DropU8 | Original drop_value_less, full payload model/order, original Drop type retained. |
| KeyB16 / KeyB17 | Original array_key_less::<M>, first-byte order, all bytes in model. |
| three forwarding adapters | Original upper7-bit order on u8, Cell<u8> and Freeze non-Copy u8. Full byte models. |

No profile is replaced by S KeyLess. These are closed audited instances, not a lawful-order,
purity, arbitrary FnMut footprint, unbounded sorting or stability theorem. Bad test-only
profiles are never lawful domains for a summary and receive no PFC/Replace admission.

Static graph audit: every migrated profile wrapper owns its one closure expression. Leaf and
consumer call that same wrapper monomorphization; consumer does not invent a separate helper F.
Concrete forwarders likewise own their closures. Actual generic SmallSort helpers pass &mut F
and call it directly; source has no comparator storage/trait object/erased function pointer.
Existing as-usize/data-pointer casts in smallsort.rs are region geometry or branch selection,
not function coercions. The full verification subtree is scanned for explicit fn-pointer types,
function address casts/equality and as-fn coercions; audit_static.py also checks byte-identical
smallsort.rs and exact preservation of seven contract attribute sets except identity requires.

Source search cannot certify MIR absence of hidden indirect dispatch or FnDef-shim/layout
support. CI must inspect actual selected-instance/lowering/replacement inventory; any unexpected
indirect edge, Unsupported shim/layout/codegen demand is STOP, not permission to patch the tool
or substitute a comparator. No required worker13 smallsort.rs proposal was identified statically.

The base tool_config still names cd355b0b; OFF explicitly uses stock0aac via a CI-control external
KANI_TOML_FILE or a directly bound exact built binary. Never silently use the base default.
All actual bodies, old arbitrary-bool safety roots, payload/frame controls and source/runtime
signatures remain on the base bytes. All old proof credit is invalid for the migrated instances.
