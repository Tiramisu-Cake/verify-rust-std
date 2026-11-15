# Accepted interface S1 v1

Worker11 source 3f469d3ba2e94d7129e66e53ea76df883ff9c946, integrated cherry-pick
1313f7c329 (only two authorized sorting_model*.rs files). Candidate reported ready
with Luna HIGH GO_WITH_NITS; Rust/Kani NOT_RUN. Runtime API as in worker11 INTERFACE.md.
Worker11 research handoff ef874d993f1a4bfd8bfc09e5b0fe3b9ebafebb0e.
Frozen interface SHA256: c06217c2f8138d0c915639d9d29571a56e4ca4952578b27c354fef6e68a900de.

Accepted: unconditional enabled<T,F>(), snapshot<T,F>(&[T])->Snapshot,
post<T,F>(Snapshot,&[T])->bool; KeyLess<T>::new(), NonCopyByte::new(u8).
Facade visibility pub(in crate::slice::sort::shared::smallsort), module pub(super)
inside verify; private fields, Project/Model stay private. fn_traits is gated by
all(kani,kani_smallsort_sorting). No raw adapter or new T/F bound. Snapshot Copy
owns [u8;32], len, valid; inactive invalid/read-free; active invalid/overflow false;
post pure full-value multiset+length+order. Exact pairs u8/Cell<u8>/NonCopyByte
with corresponding KeyLess. API changes go back to worker11 before refreeze.

Stock macro source shared::build_ensures lifts and clones old expression before
body/wrapper creation; check::make_check_body evaluates post after consuming body
closure. This supports the proposed owned snapshot design by source inspection,
not an actual Rust borrow-check or Kani qualification.
