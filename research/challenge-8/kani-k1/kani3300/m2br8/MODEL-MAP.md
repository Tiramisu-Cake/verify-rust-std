# R8 state and operation map

Main: tracked_object_id:usize, tracked_offset:usize, value:bool — unchanged.
Unique main marker and distinct ArgumentBuffer marker/actual global resolution remain.

| Buffer field | Type / constructor | Runtime writes | Runtime observation |
|---|---|---|---|
| active | bool/false | Begin/return true, depletion/reset false | Begin/Store/Load protocol |
| selected_argument | usize/0 | Begin/reset/consumption MAX, selected Store index | Load pairing/depletion |
| signature | usize/0 | Begin/return Store | Store/Load equality |
| count | usize/0 | Begin count, return Store0 | Store/Load count |
| written | usize/0 | Begin0, return1, argument +=1 | Store limits/Load completion |
| remaining | usize/0 | Begin count, return1, Load -=1 | Load/depletion |
| last_stored | usize/0 | Begin0, argument Store index | strict Store order |
| last_loaded | usize/0 | Begin/return0, argument Load index | strict Load order |
| has_witness | bool/false | Begin/reset/depletion false, selected Store exact match | selected Load guard |
| value | bool/false | selected Store captured main value | selected witness Load && mask |
| saved_base | *const u8/null | selected witness Store live thin source, no-witness null | selected witness/source-follow Load metadata |
| saved_byte | *const u8/null | selected witness Store base.wrapping_add(r), no-witness null | same guarded Load metadata |
| layout_size | usize/0 | selected Store N | selected Load equality |

13 fields: 8usize/3bool/2pointers. No numeric source ID/offset/relative in buffer.
Only the const static initializer constructs the whole record. Runtime writes are
scalar cells; no write to padding, whole buffer or source allocation is added.
Reset retains exactly two nondet usize main seeds, main false, then active false,
selected MAX, has_witness false. Pointer/value/counters need no reset while inactive.
Begin and all non-carrier functions are unchanged. Store/Load signatures, markers,
attributes and generic ordering stay byte-identical to base. No new helper.

Store predicate is unchanged; has_witness/value are captured before new helper calls.
relative lives only as a local. Constructors/no-witness branch use null pointers.
Load never rereads MEM_INIT_STATE.value for source-follow propagation. False witnesses
run the same codec as true witnesses. Zero/no-witness cannot decode/add pointers.
All original protocol operations/assertions and demonic branch placement remain.

DFCC: whole-main lambda plus 13 buffer member-lvalue lambdas (private subtotal14;
public targets vary). Field count is independently checked; no two-lambda assertion.
New members have Type::unsigned_int(8).to_pointer(). Lambda retains member lvalue,
without cast/deref. Intended target addresses are &ARGUMENT_BUFFER.saved_base and
&ARGUMENT_BUFFER.saved_byte; extents are sizeof(*const u8), object is ARGUMENT_BUFFER,
never the saved source object. Actual emitted address/extent/object/write-scope binding
is UNKNOWN until coordinator CI. No pointer-value range or blanket frame exemption.
