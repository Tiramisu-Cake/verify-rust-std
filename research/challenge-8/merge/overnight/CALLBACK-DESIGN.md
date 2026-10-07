# M2a: actual merge callback/resources — BEFORE implementation

Authorized dependency of OVERNIGHT-MERGE-26.10. W1 remains experimentally
separate; combined profile cannot be accepted by transferring its green cases.
Actual repository source is pinned by SOURCE-ADMISSION-CD371.json and the
three complete Git blobs in wrapping-PROFILE.md. First actual callee: exact
merge_up, then merge_down. Extraction/injection happens only hosted; every
runtime byte and generic signature must match the pinned body after ghost strip.

## Target contracts

Safety: unrestricted T and arbitrary legal FnMut normal answers/effects/panic.
Require current-thread token, type_interp(T/F), valid initialized source cells
with single own(T) resources, independent writable destination, callback own(F),
and sufficient ordinary-add/sub geometry. Source cells may coincide: the general
callee goal must admit shared read access and not require two exclusive chunks
at the same location. Begin with explicitly distinct-source diagnostic, keeping
the shared-candidate obligation separate (paired bidirectional state can make
up and reverse candidates coincide). Destination is a shadow: initialized bytes
do not create a second own(T). No Copy or Freeze is added to these callee goals.

On normal callback return, recover current valid source values lv1/rv1 and F's
current state. A callback can mutate via interior mutability; equality with the
old values is not a safety post. Exact branchless selected pointer is copied
before cursor updates. Return source own(T), updated F own(F), destination copy
of the selected current value (without its own(T)), full pointer associations
for the arbitrary returned Boolean. On callback unwind: source ownership/current
values and F's current state restored, destination untouched, no cursor update.
The complete actual callee return/leak/dead-code and both posts are required.

The actual bidirectional_merge already has FreezeMarker. Its source snapshot
model needs a separately justified translation of that repository marker and
resource protocol. Functional B additionally assumes fixed finite SWO, immutable
keys, sorted halves and faithful normal answers; those are not callee safety
premises. Whole-merge panic can leave a partial shadow destination; ownership
remains source-side until occurrence guard proves a complete permutation and
the caller's commit/CopyOnDrop protocol transfers/restores ownership.

## Minimum frontend dependencies found in stock26.10

1. Tuple-2 ownership: stock Rust parser emits opaque std_tuple_2__own. Replace
   only this exact generated two-field shape with the separation of its two
   field own predicates. The constructor carries thread and tuple value;
   all other tuples/ADTs keep stock behavior. This is a transparent nominal
   representation rule, not an ownership introduction axiom.
2. HRTB Output: stock drops bound-region Projection clauses. Retain an exact
   compiler-origin FnOnce Output=bool bound for F over two shared T refs and
   instantiate it only at an actual matching FnMut::call_mut with typed source
   and ghost substitutions checked. Universally quantified lifetimes permit
   instantiation at a common short lifetime; do not invent type equalities or
   accept wrong F/T/output/lifetime substitutions. Prefer preserving existing
   tuple/parser ABI; no exporter/schema/refiner changes initially.

Trust: parser ownership expansion and frontend bound instantiation are new
semantic dependencies, separate callback.patch over f760. Kernel, ordinary
arithmetic, ownership/borrow primitives, pointer provenance, exporter and refiner
remain frozen for M2a. Earlier26.09 patches are design evidence only, not applied
wholesale or treated as accepted26.10 support.

Further open dependency: source's unsafe block spans callback and copy. Recovery
must end the genuine reference loan before copy, also on unwind. Stock lifetime
binding scope may block this. No unchecked early lifetime cut: first collect
exact actual source/MIR diagnostics; if a cut is needed, design it separately,
prove temporary ref initialization fractions returned, prohibit escaped aliases
and ensure unwind cleanup cannot be skipped before implementing. An actual
callee must not receive a summary based on an incomplete lifetime-debt post.

Further open dependency: stock copy_nonoverlapping requires initialized typed
destination. An uninitialized-destination byte/initialization-preserving primitive
is separate from callback typing. Validate source read, alignment, provenance,
nonoverlap, count bounds, raw destination writability and no own(T) duplication.

## M2a matrix before acceptance

Tuple: exact tuple2 close/open with each field own(T), two independently linear
field resources, correct thread and value. Negatives omit first/second/one linear
frame, use wrong thread/value, and unrelated tuple arities remain unchanged.
No proof assumptions or missing resource hiding. Return/leak gates mandatory.

HRTB: generic Boolean comparator exact two typed shared args/common short lifetime;
wrong F, T, nonbool output, unconstrained output, unrelated body or missing source
bound reject at intended equality gate; two calls independently matched. Full
MIR source substitutions and source-clause evidence retained. Translator-only
positives are not successful callback resource proofs.

Actual: isolated exact merge_up before merge_down; original vs ghost source
identity/export/decode/refinement; full bodies normal/unwind/leak/dead-code. Missing
source/destination/comparator ownership/read initializedness must reach intended
resource predicates. Retain legal interior mutation and panic routes explicitly.
Full W1/G2/A/B/Rust/native compatibility matrix before combined acceptance.
