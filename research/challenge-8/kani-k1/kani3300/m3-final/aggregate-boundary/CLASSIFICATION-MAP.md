# Aggregate transfer classification

Existing `transfers_shadow` and `maybe_uninit_storage` are byte-for-byte unchanged.
`shadow_transfer_kind` is admission only; it never returns a recursively widened
transfer predicate or supplies field offsets/masks to the flat protocol.

| Type shape | Classification / boundary |
| --- | --- |
| top-level union / MU<T> / flat [MU<T>;N] or [MU<T>] | existing supported carrier; stop traversal, preserve existing limitations |
| scalar, ordinary tuple/struct/array/enum | ordinary, provided no inline carrier exists |
| tuple/struct containing MU/union, including arrays of these | UnsupportedNested; report root type, argument/return and discovered inline carrier |
| closure environment | use actual instantiated internal upvar_tys, then public types; borrowed captures stop at refs |
| enum | inspect every variant; inactive shadow variant rejects conservatively |
| zero-sized field or zero-length array | inspect field/element type despite zero bytes; nested slot rejects conservatively |
| refs / raw pointers | terminal ordinary values; never inspect pointees |
| Box<T>, PhantomData<T> | inspect actual instantiated ADT fields; T as a generic argument alone is not inline storage; no new Box/realloc support claim |
| pattern type | follow its constrained base type |

Iterative worklist and HashSet<Ty> avoid recursive stack growth and repeated types.
Rust's inhabited inline layouts are finite; pointer cycles terminate at pointer
fields. No layout query, arbitrary unwrap, byte-offset assumption or constant
array-length evaluation is added by classification. Existing supported carriers
are terminal even if their payload is itself aggregate; existing layout/model
limitations remain, including nested MU-of-flat and B3 union/ZST/enum limits.

Entry: validate argument locals 1..arg_count and local0 at the first instruction,
before union_args filtering and LoadArgument. A rejection returns only explicit
Unsupported targets, avoiding later payload/layout fallback in that body.
Call: resolve selected instance, validate all actual operands and destination,
and separately all available selected signature inputs/output. Generated Item,
Shim, intrinsic and foreign/no-body paths share this validation. Rejection breaks
before operand traversal or any return Load, Begin, Store, snapshot or deinit.
Unresolved calls also validate actual arguments/destination before any operand
visiting; a nested value receives the specific aggregate diagnostic, otherwise
the existing Unsupported resolution boundary remains.
Return: independently revalidate local0 before StoreArgument. Entry validation
already excludes unsupported returns, including uncalled selected bodies.

Forget: only resolved InstanceKind::Intrinsic / Intrinsic::Forget bypasses nested
classification. It consumes without payload read, copy result or return transfer.
The existing flat unsized guard remains. Ordinary mem::forget wrappers remain
ordinary call boundaries; no skip-list-wide or new intrinsic exemption exists.

For admitted calls, paired predicate, argument numbering/counts, snapshot-all
before deinit-any, Move-only source clearing and normal-edge return LoadArgument
are unchanged. The supported handoff still calls actual relay(Move(source)),
saves source's pointer, writes23 on the repair branch before read_source, returns
the actual relay value42 through a top-level MU return, and writes the observed
scalar through *mut u8 before return. Both legal assertions and the no-repair
source read remain. No runtime, DFCC, points-to, body selection or JSON change.

Pointer admission control: references can read the existing supported MU field
path; the positive raw pointer case only compares a null *const Packet, with no
pointee read. A separate known-outcome control retains raw aggregate-pointer
read's existing UnionAsField layout Unsupported. No aggregate-pointee support
is inferred from a pointer's ordinary transfer classification.
