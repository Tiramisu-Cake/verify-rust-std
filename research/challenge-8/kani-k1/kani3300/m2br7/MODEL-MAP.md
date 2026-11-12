# R7 field and operation map

Old owner/prefix: `MEM_INIT_STATE.argument_buffer_`; new owner: `ARGUMENT_BUFFER.`.
Names below are the suffix, unchanged except ownership. B=begin, S=store, L=load, R=reset.
All operation order and conditions are the base algorithm; STATIC-AUDIT checks tokens after
inverse field renaming for every existing non-constructor function, including reset.

| Suffix (old -> same new) | Type / constructor | Runtime reads | Runtime writes | Epoch reset |
|---|---|---|---|---|
| active | bool / false | B,S,L | B true; S(return0) true; L depleted false | false |
| selected_argument | usize / 0 | L match/return0/depletion | B MAX; S selected index; L matched MAX | MAX |
| signature | usize / 0 | S,L equality | B/S(return0) signature | untouched |
| count | usize / 0 | S limit; L equality | B count; S(return0) 0 | untouched |
| written | usize / 0 | S limit; L completion | B 0; S(return0) 1; S(argument) +=1 | untouched |
| remaining | usize / 0 | L >0/depletion | B count; S(return0) 1; L -=1 | untouched |
| last_stored | usize / 0 | S strict order | B 0; S(argument) index | untouched |
| last_loaded | usize / 0 | L strict order | B/S(return0) 0; L(argument) index | untouched |
| has_witness | bool / false | L source-follow guard | B false; S live range match; L depleted false | false |
| value | bool / false | L saved false/true | S live MEM_INIT_STATE.value | untouched |
| relative_offset | usize / 0 | L saved offset | S tracked_offset.wrapping_sub(from_offset) | untouched |
| layout_size | usize / 0 | L selected equality | S LAYOUT_SIZE | untouched |

Constructor closure: exactly these twelve scalar fields (9usize/3bool), no pointer/Option,
no omitted/default field and no dynamic call. ArgumentBuffer::new is called only by its static
initializer. Main constructor retains tracked_object_id=0, tracked_offset=0, value=false.
Reset retains two nondet usize calls and main value=false before the three partial buffer resets.
All runtime writes to the new object are these scalar field lvalues; no aggregate/byte/padding write.

Main fields retain original names/types/marker and get/set/copy/copy_by_id/get_slice/set_slice
methods. Store observes live source object/offset and main value before Move; no saved pointer.
Load follows only saved has_witness + value + relative_offset to the live destination and typed
mask, or takes the unchanged optimistic destination branch. False is not replaced by true on
the source-following branch; no-witness is not missing protocol. Return0 is mandatory, arguments
compete demonically including none, selected layout/count/signature/order assertions are retained.

Every pre-existing fn_marker and model signature is unchanged. New static marker is distinct
from the unique original main marker. Begin(signature:usize,argument_count:usize)->();
Store<const LAYOUT_SIZE:usize,T>(*const T,usize,usize)->();
Load<const LAYOUT_SIZE:usize,T>(*const T,usize,usize,usize,[bool;LAYOUT_SIZE])->().
Reset has no args/generics and returns (). Caller indices, masks, model enum/cache and ABI unchanged.

DFCC field set equals this full table, independently of lambda count: one whole-main target,
twelve buffer member targets, no whole-buffer/padding target. Both exact emitted identities are
mandatory with uninit/PFC; zero targets allowed only without uninit and neither object emitted.
All actual emitted write scopes/identities and semantic outcomes await coordinator CI.
