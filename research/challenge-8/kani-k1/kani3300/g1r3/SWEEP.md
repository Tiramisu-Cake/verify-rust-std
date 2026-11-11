# KANI3300 G1R3 — std/core wrapper sweep (static only)
Scope: all 23 G1 main.rs fixtures + shared types.inc (154 harnesses); includes unchanged B fixtures, no B artifact edits.
Source pins: Kani 6bb067476116704763502763984b225014dce221, production 3d085249c9; nightly Rust 7189d39d9ce936881b8132c6addeaf3e295cd455; hashes in RUST-SOURCES.json.
Pinned core mem/mod.rs:191–193: mem::forget<T> calls ManuallyDrop::new(t); manually_drop.rs:181–182 constructs ManuallyDrop<T>.
Before repair negative/main.rs:737,747,760,772 therefore passed NonCopyFieldC/R unions into ManuallyDrop<union>; this is unintended G2.
After repair negative/main.rs:738,748,760,772 call core intrinsic forget directly; intrinsics/mod.rs:797–809 declares a bodyless, safe intrinsic, no wrapper constructor.
Kani uninit_visitor.rs:604–622 recognizes Intrinsic::Forget and Operand::Move, clears full source extent with SetStorage(false) Before; :1112 retains its no-effect intrinsic model.
These unions contain ManuallyDrop<NonCopyWord>, not a nested union; ty_layout.rs:262–271 recursively validates fields, so direct union arguments avoid UnionAsField.
Moved NonCopyWord source remains checked: uninit_visitor.rs:175–188 collects Move and emits SetRef(false); constructor :262 and projected assignment :477/:522 call it.
All four original raw u32 moved-from reads remain, and negative/expected is byte-identical (70 failures); no SUCCESS/FAILURE result inferred statically.
Other intrinsic forget sites negative:782,791 consume MoveC/R directly; reject_forget_union_array:12 intentionally passes [U;0] and retains G2 rejection (B unchanged).
ManuallyDrop::new elsewhere: positive:318–413,656–678 and negative:335–461,734–766 wrap Padded, tuple, or NonCopyWord only; those payload types contain no union.
reject_manuallydrop_union/main.rs:10 intentionally constructs ManuallyDrop<U>; same entry/formal/return guard at uninit_visitor.rs:82–90/142–150 and ty_layout.rs:266.
Its expected:1 now names observed std::mem::ManuallyDrop::<U>::new.unsupported_construct.1; FAILURE, reason, harness and 0/1 summary unchanged.
MaybeUninit: only negative:588,599 use MaybeUninit<u32>::uninit(); no G1 call to MaybeUninit::new<U>, Option<U>, Some(U), or Result<U> found.
ptr::read/write in positive/negative and raw-pointer .read() rejection fixtures transfer U directly; pinned ptr/mod.rs:1715–1754/1939–1964 use read_via_copy/write_via_move, no container.
ptr::read_unaligned/write_unaligned rejection fixtures intentionally reach Unaligned<U> (ptr/mod.rs:1833–1852/2043–2056; struct :2856); guards/goldens unchanged.
Remaining std/core calls (copy/copy_nonoverlapping, write_bytes, pointer/address/casts, size/offset, NonZeroU32::new().unwrap(), volatile, transmute, typed_swap/select_unpredictable) introduce no unintended by-value union wrapper; explicit rejection controls retained.
Static sweep + rustfmt/git/application checks only; compiler/Kani/native NOT_RUN, no proof credit or dispatch authorization; Cloud $0.
