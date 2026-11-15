# Contract scope

Preparation only; Rust/Kani qualification NOT_RUN. Semantics are conditional on
exact model pairs u8/KeyLess<u8>, Cell<u8>/KeyLess<Cell<u8>>, and
NonCopyByte/KeyLess<NonCopyByte>. Inactive=false facade is a disclosed boundary,
not a theorem for arbitrary T/F. Never require enabled for all runtime users.

Each actual body uses old(snapshot::<T,F>(v)) as an owned Copy value token. The
postcondition requires equal length, adjacent pure-key sortedness and every
full-value multiplicity; it never calls FnMut. Snapshot CAP32 applies to model,
while smoke N0..3 only qualifies mechanism. Cell get and transparent byte
projection represent full values, not lossy keys. Invalid active snapshots fail.

Borrowed input/scratch validity and exclusivity come from actual safe fixtures;
MU scratch is separate and never read by assertions. No panic/helper/comparator
stubs, assumes of result, presorted input, runtime code, signature or bound edits.
No new contract is a stub_verified summary or a Replace qualification in S1.

The six write frames (v, and Stable Freeze scratch) are qualified only for the above named ZST
comparators: active v, permitted stable scratch, comparator ZST. They do not
establish an arbitrary FnMut footprint or full generic theorem. Future summary
use requires full domain/frame qualification. Organizer --no-assert-contracts
remains enabled; target PFC activation negatives must expose postcondition failure.

Stock Kani checks only one generic instantiation per PFC. An effectful arbitrary
FnMut can write outside these frames, so this source spec must not be treated as
an arbitrary-F theorem. Sorting-enabled future callers with other F and all new
summary consumers require a separate frame design/review; they are outside S1.
The frozen batch retains --no-assert-contracts and checks only listed instances.
Independent review accepted that bounded scope; actual frame proof NOT_RUN.
