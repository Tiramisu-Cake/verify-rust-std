# Runtime extent gate — exact missing rule

Read-only investigation pinned to tool75099c958eb6a6d46016babf0a845a624f77d9ab
and proofa74d612731f41969e688326456b34b55a880c5a7; origin candidate
6cb7b6736c4ef7978d2f3a80737952ac7148cccb does not change size semantics.

`sizeof_core` maps GhostTypeParam/BoundedGhostTypeParam to `sizeof(typeid)`
(src/verifast1.ml6487–6490). All Rust struct sizes are assumed strictly positive
(the `_size_limits` axiom near6519). Unit is `StructType("std_tuple_0_")`
(rust_parser.ml112–115; translator unit translation near1900), declared empty
in bin/rust/prelude.rsspec13. Thus modeled sizeof(()) is positive, despite
Rust runtime size_of::<()>() being zero. Current abstract size-zero negative
provides no concrete-unit qualification. The new phase includes a concrete
unit diagnostic; its stage and obligation must be reported exactly.

The exporter does not serialize target-specific type Layout::size. FieldInfo
isZeroSize is set from `ty.is_phantom_data()` (vf_mir_exporter/src/lib.rs2397),
not actual Rust layout. Generic MIR leaves T abstract. This bit cannot certify
positive runtime storage and is not a bridge for arbitrary T.

Missing rule: the size term used for typed physical storage, pointer arithmetic,
object limits and incoming/local interval geometry must denote actual Rust byte
extent of T on the pinned target/compiler, including zero and arbitrary supported
struct/array layouts. A generic instantiation must preserve that interpretation;
ManuallyDrop<T> must share T's layout. Unsupported types must remain unsupported,
and no all-struct positivity axiom may contradict a valid ZST instantiation.
This interpretation must be justified by the lowering/model, not an extra caller
separation premise or a positive modeled sizeof assertion. Removing positivity
alone is conservative but cannot discharge the current line69 span obligation.

Actual caller matters: T=() satisfies size_of::<T>()*48<=4096, so the default
smallsort specialization selects small_sort_general. Its loop calls insert_tail
at std smallsort.rs272–274. The separate insertion_sort_shift_left pointer loop
may skip a ZST, which does not eliminate the general-with-scratch caller.

Minimal layout reproducer: function with no premises returning
core::mem::size_of::<()>(), assertion that its runtime value is zero, plus a
separate direct ghost assertion std::mem::size_of::<()>()==0. A mismatch is
layout evidence, not an origin negative. Minimal generic reproducer retains
T and supplied physical tail/owner, actual tmp=ManuallyDrop::new(tail.read()),
guard src=&*tmp,dst=tail,len=1 and the unchanged separation assertion before FBC
(the preserved actual positive fixture in checkpoint a74d6127). Do not add a
supplied separation premise. The new origin-only profile cannot eliminate its
known separation refusal; actual rerun is NOT_RUN on this profile.

Permitted geometry remains fixed scalar/pointer extents. A scalar specialization
would be limited evidence, not generic proof or acceptance of the true caller
with comparator. No layout patch is claimed: available MIR payload does not
support a narrow independently justified generic layout change in this phase.
