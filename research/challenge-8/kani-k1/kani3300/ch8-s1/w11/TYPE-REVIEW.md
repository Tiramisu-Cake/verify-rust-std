# Static type / width / lifetime review

NonCopyByte is repr(transparent) over u8, with private field, const constructor,
no Copy/Clone/Drop impl. It inherits Freeze and ordinary u8 auto traits. Cell<u8>
contains UnsafeCell and is !Freeze; projection reads get() without writes. u8 is
Freeze+Copy. All three size/align expectations are1/1, no drop glue; positive roots
assert size/align/needs_drop. Worker13 checks actual route/threshold selection in
its six-body roots; wrapper layout alone does not prove body selection.

KeyLess<T> uses PhantomData<fn()->T>; this marker occupies zero bytes, contains
no pointer value and does not own/drop T. Its private representation cannot carry
runtime state. Three separate concrete FnOnce/FnMut impls are generated, with
independent 'a/'b lifetimes for the two references and Output=bool; call_once owns
the ZST, call_mut receives &mut ZST. Both evaluate a.value()<b.value(). No reference
escapes, mutation, function-pointer coercion, FnPtr/vtable/address guard or Fn
summary. Core prelude supplies FnOnce/FnMut; fn_traits is needed to define their
methods, unboxed_closures already exists. Actual rust-call/Kani tuple lowering is
NOT_RUN, required in combined CI; core/tool changes beyond feature registration
remain STOP conditions.

Private Project applies to T, returning u8: Copy is required of the projected
logical value/snapshot, not of T. Private Model<T,F> has an unconditional blanket
impl for () and three concrete substitutions. Defaults are method-default items,
not specialization on a trait bound, const or lifetime. No facade bounds escape.
Baseline min_specialization is present; acceptance by actual core rustc/Kani is
NOT_RUN and must not be inferred from this source review.

Facade visibility is restricted to the smallsort module, enough for actual attrs
and verify controls. Worker13 accepted this correction before freeze; sorting_model
registration must be pub(super) inside verify. Private Project/Model/fields stay
private. There are no module/lib/Cargo/tool changes in worker11 source commit.

All lengths, indices and counts use usize; N<=32 before active loops, j/i guarded
before indexing, count<=32. No narrowing cast or signed/sentinel arithmetic. Even
16-bit usize holds all counters; i starts1 for adjacency, so N0 causes no reads.
Snapshot.len>CAP check precedes indexing. Snapshot is fully initialized Copy
storage; only valid initialized active prefix carries logical data. MaybeUninit
controls construct valid references to initialized MaybeUninit wrappers with
uninitialized payloads; no references to uninitialized u8 or invalid addresses.

Control unwind5 covers loops of at most3 (insertion constructor at most2 inner
iterations). Corruption unwind4 covers at most2; boundary companion unwind34
covers loops of at most32. Nested bounds are per-loop, not multiplied; CBMC must
retain unwinding assertions. No loops in unchecked inactive/activation helpers.
No compiler, rustfmt or verifier was run locally.
