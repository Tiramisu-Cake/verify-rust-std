# Pinned-source type/signature audit

Authority: exact parent/candidate blobs in DIAGNOSTIC-MANIFEST.json and frozen dependencies in INPUTS.json. STATIC-AUDIT.py checks full expected compiler-file equality, exact one-file deltas, byte-identical parent runtimes, all normalized runtime declarations and14 markers, compiler function-body equality, dependencies and patch/tree reconstruction. This is a source audit, not Rust compilation. First coordinator build must check actual expansion/types/-D warnings, including B3 E0308/E0277 lessons.

| Changed expression / consumer | Source-established type and use |
| --- | --- |
| KaniModel::InitializeMemoryInitializationState | Existing unit enum variant, kani_functions.rs:146–147; same serialized marker used by runtime initializer |
| KaniFunction::Model(...) | Existing enum constructor taking KaniModel, kani_functions.rs:34–36; result KaniFunction |
| KANI_INITIALIZE_MEMORY_INITIALIZATION_STATE | Explicit const type KaniFunction, same style as adjacent constants; only definition and SKIPPED_ITEMS entry references |
| SKIPPED_ITEMS | Existing `&[KaniFunction]`; new entry has exact element type; existing imports already include KaniFunction,KaniModel |
| TryFrom<Instance> / contains(&f) | Existing Result<KaniFunction,()> mapping and slice contains(&KaniFunction), KaniFunction derives PartialEq; bool guard returns unchanged body |

No imports, trait bounds, calls, borrows, argument lists, return types, casts or generics change. The new const is used; no added unused import/reference. Full compiler-file hash and compiler subtree match between candidates; both parents have the same original compiler file. Existing method signatures and both provider call arities are unchanged.

Initializer stays `fn initialize_memory_initialization_state()->()` with no generic/value arguments. `ptr_uninit/mod.rs:101–138` resolves it with GenericArgs(vec![]), inserts vec![] and a Ty::new_tuple(&[]) unit return. tracked_object_id and tracked_offset are usize, so both any calls specialize usize; value and R1 argument_buffer_active are bool. No integer/bool inference changed. In R6-02b ARGUMENT_BUFFER has Option<ArgumentBuffer> type; None is inferred from that assignment target, in the existing unsafe block. ArgumentBuffer derives Clone+Copy and contains selected_argument:usize,saved_address:*const (),layout_size:usize, so Option-by-value reads do not move a non-Copy static. The skip does not repair or alter Option's layout.

Preserved model API closure (implicit unit results shown explicitly):

| Model / helper | Existing signature / value arity |
| --- | --- |
| store_argument / load_argument | `<const LAYOUT_SIZE:usize,T>(*const T,usize)->()` /2 |
| copy_init_state | `<const LAYOUT_SIZE:usize,T>(*const T,*const T,usize)->()` /3 |
| copy_init_state_single | `<const LAYOUT_SIZE:usize,T>(*const T,*const T)->()` /2 |
| copy_by_id | `<const LAYOUT_SIZE:usize>(&mut self,usize,usize,usize,usize,usize)->()` /5 plus self |
| bless_by_id | `<const LAYOUT_SIZE:usize>(&mut self,usize,usize,usize)->()` /3 plus self |

All other get/set/slice/chunk/str model declarations and generic order/results are normalized in STATIC-CHECKS.json and match R1. Hcopy/GLUE helpers and their call sites are whole-file frozen from each parent; copy/copy_by_id/bless/bless_by_id/copy_init_state/single bodies are additionally compared with R1. In mandatory store selection, selected_argument:usize fixes literal0 to usize and the `||` RHS any to bool. Pointer-buffer matched load still calls copy_init_state_single::<LAYOUT_SIZE,()>(saved_address,to_ptr) with two *const () operands, then exact R1 copy<N,()> with count1:usize. Scalar control retains original usize object IDs/offsets and bool active. Reset types and scope are unchanged.

Frozen resolver caveat from R6 remains: str models declare const N while existing resolver supplies const+type; no broader str input admission claimed. P1 remains scalar, exact pinned bytes. No new Rust test/compile result is inferred from source checks or Luna review. Pinned TASK-M1 wrapper/binary/config identities are checked; rustfmt --check and git diff --check pass for both candidates. Compilation/build/solver NOT_RUN, emitted signatures/paths UNKNOWN until coordinator CI.
