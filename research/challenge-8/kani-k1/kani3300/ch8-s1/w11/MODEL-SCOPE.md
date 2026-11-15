# S1 model scope, v1

| T | Exact F | Projection / full value | Body-selection expectation |
| --- | --- | --- | --- |
| u8 | KeyLess<u8> | dereferenced u8 | Freeze+Copy overrides / forwarding |
| Cell<u8> | KeyLess<Cell<u8>> | Cell::get() | !Freeze defaults |
| NonCopyByte | KeyLess<NonCopyByte> | private u8 field | Freeze, !Copy, no Drop; general default |

These are three closed pairs, not a theorem for arbitrary T/F. Comparator state
is a private zero-size PhantomData, no runtime pointer or address identity test.
Constructing KeyLess<unsupported T> is legal; calling it has no Fn impl. Arbitrary
other comparator types, including descending and effectful closures, are inactive.

Model domain is N0..32 inclusive; enabled depends only on T/F, never N. Snapshot
for an active N>32 returns invalid before reading an element; post rejects an
invalid snapshot, any active output N>32, or changed length. No truncation/panic.
Inactive snapshot and post ignore both length and elements. Inactive snapshot is
invalid; inactive post=true is explicitly no semantic claim, guarded in actual attrs.

Snapshot owns Copy byte storage, original len and validity, with no references to
input/scratch. All 32 bytes are initialized to zero, only input active prefix is
projected; neither snapshot nor checker reads unused input/scratch tails. Model
fields are private. Snapshot is semantically meaningful only paired with the same
T/F and input pre-state; it does not authenticate tokens from arbitrary callers.

Post checks adjacent nondecreasing full-byte values and equal counts of every
byte present in pre-state. Repeating checks for duplicates is intentional. Let V
be the finite distinct pre-state values. The sum of their old counts is N; equal
counts in an N-element output also sum to N. Hence all output elements belong to
V, their counts agree, and no novel value can substitute a missing value. No
fixed arbitrary probe is used. Counts/indices use usize and are bounded by32.

Checker is allocation-free and calls only private pure projections, never FnMut.
Cell reads are get() only; an owned pre-state remains unchanged after Cell::set
in the control fixture. The closed comparator reads two projections and uses <;
no capture, external writes, assumptions of sortedness, or comparator invocation
from post. Future payloads need separate key/full-value models; not claimed here.

S1 positive roots symbolically cover N0..3 and arbitrary bytes/duplicates. The
fixed N32 checker identity checks a boundary only. No actual SmallSort body,
threshold sorting theorem, full generic type coverage, frame/Replace proof,
extra-UB check or Challenge8 acceptance is established by this preparation.
