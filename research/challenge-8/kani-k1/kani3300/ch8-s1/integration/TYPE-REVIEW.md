# Source type review (actual verifier NOT_RUN)

u8: initialized arbitrary byte, Freeze+Copy, size/align1; efficient swap size<=8.
Cell<u8>: UnsafeCell-backed !Freeze, size/align1, !Copy, pure shared projection
Cell::get (u8:Copy). Forces stable/unstable default fallback threshold16.
NonCopyByte: worker11 repr(transparent) u8, no Copy/Drop, Freeze; size/align1;
48-byte scratch<=4096 selects Freeze default general threshold32.

KeyLess is named ZST with private PhantomData and concrete FnOnce/FnMut impls;
argument lifetimes independent; no fn-pointer coercion, state or writes. Core
already enables unboxed_closures/min_specialization; manual rust-call Fn impls
need fn_traits under the sorting Kani cfg. Snapshot owns [u8;32], len and validity;
Copy applies to snapshot/key, not T. All lengths are usize bounded by fixture N<=3
or checked model CAP32. No element reference survives the mutable sort call.
Reborrow ends before post-call snapshot/checks. Scratch MaybeUninit<T> stores no
assumed initialized value, and unused scratch is never inspected.

Worker11 committed model3f469d3ba2 received with research handoff ef874d993f.
Facade visibility is pub(in crate::slice::sort::shared::smallsort), with module
pub(super) in verify. Independent source review of integrated75a4d1e is GO for
this bounded scope; exact target/Fn/macro/frame qualification remains NOT_RUN.
