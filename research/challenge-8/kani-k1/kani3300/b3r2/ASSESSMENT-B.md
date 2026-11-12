# B: static assessment (2026-11-12)

Observed compiler/CBMC/verdict/exit/cover for every new input: **NOT_RUN**.
Semantic expected result: SUCCESS under default checks. No crash, Unsupported,
ignored or expected-failure surrogate is installed in the active suite for B.

The A change chooses an empty physical Unit only for a wholly zero-sized arm
with positive wrapper padding. Both padding and union width come from rustc
layout: padding == union_size iff the logical arm width is zero. The logical
unionfield type and padding bits remain unchanged. Nonzero payloads retain
exactly their old Type; padding == 0 bypasses the wrapper entirely.

## Inputs and layout obligations

- tail_bytes_first.rs: repr(C) Probe fields bytes, tail; Copy Tail fields b, z.
- tail_first.rs: same input except Probe fields tail, bytes (first-arm companion).
- Both assert rustc Tail size 1, Probe size 8, b offset 0, z offset 1;
  wrapper padding is therefore 56 bits. Tail is nonzero and retains [(); 2].
- tuple_first.rs: Probe fields pair, bytes; pair is (u64, [(); 2]).
  Both arm and union assert size 8 (zero wrapper padding); nested array retained.
  Tuple layout is rustc-defined; no tuple field offset is assumed here.
- All three perform actual full-extent 8-byte writes to src, then ptr::read(src)
  and ptr::write(dst). Post-copy reads assert initialized b/u64 data and nested
  array length/index projection. Tail padding is never read as data.
- Distinct post-copy covers require SATISFIED per harness; no run has established it.

## Minimal union-only extension assessment

A candidate would need a separate physical payload for nonzero Tail, preserving
its byte field, field offsets, total width and logical projection paths while
replacing nested zero-width arrays. The no-padding tuple also needs a physical
representation even where the current branch returns the original Type.
Simply substituting Unit for a nonzero arm discards data and is invalid.
Editing Tail's shared StructTag globally is outside the union-only boundary.
Cloning and recursively rewriting struct/tuple representations would introduce a
new logical/physical projection contract across nested members, assignments and
reads, including arrays and recursive tags. That contract is not established by
this change; a one-line union-only substitution is not justified statically.
No such extension is implemented in B3R2. Coordinator CI must distinguish base,
v2 and v3 outcomes before a separate narrowly scoped repair is selected. Base
PASS -> v3 FAIL/ICE is a new regression and blocker, never a known limitation.
