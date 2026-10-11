# Rust size lower bound repair — pre-implementation semantic review

2026-10-11 session start 08:33:37 UTC; main deadline 10:33:37 UTC;
finish-only 11:03:37 UTC. Owner select-sort4. Read/adopted full policy commit c7ca8c467aecf10a4b53039372ee97714f854ee3,
current fork origin/main; WORK-POLICY file-history commit
6726a08d30b37d6d0f4ae65c3d8c2861615d249a also recorded.
Initial checkpoint 69e8ffe5c8b7607cedd9295a4e0a3a53c0d3a38a; clean assigned
worktree/branch, fork fetch completed. New 3600-second account, no carry.

## Authorized minimal candidate, experimental/unaccepted

Exact consumer: source-linked native C1 research fragment, scratch
array<MaybeUninit<T>> entry. Hypothesis: correcting the struct size lower bound
will leave both generic sizezero/nonzero branches feasible and close C1 with
full native normal/direct-unwind/early posts. The added research guard is not
proof of caller guards or standalone sort4 generic ZST safety.

Change only src/verifast1.ml struct size axiom: Rust dialect uses 0 <= size;
C/C++ retain 0 < size; every dialect retains size <= max_uintptr. Rust repr(C)
is still Rust: its empty structure may be ZST. No union representation change.
For a Rust structure whose present complete body has an entirely empty field list, add size = 0.
Do not apply this equality to opaque declarations, enum union representations
with real fields, or structures with real fields (including MaybeUninit), or ghost-only annotation structures.

Rust Reference https://doc.rust-lang.org/reference/type-layout.html specifies
nonnegative size, positive power-of-two alignment, size divisible by alignment,
array size N*size(T), fieldless Rust ZST and repr(C) empty size zero. Removing an
invalid universally-positive premise is sound weakening; it does not assert
that arbitrary fielded structs actually have zero size. Existing exact primitive
and MaybeUninit equality still derive non-ZST sizes. Empty struct equality is a
narrow layout rule, not a general ABI/exact field-layout mechanism. No exact
alignment is invented. Existing alignment, padding/offset, upper/array footprint,
validity, provenance, ownership and fraction constraints remain untouched.

Changed old inference: introducing native MU<T> size no longer proves Tsize>0.
Only a real nonzero branch plus existing nonnegative size may prove positivity.
C/C++ nonempty/empty semantics retain their prior positive lower bound.
Permissions are never obtained from size zero. Existing native array/foreach
resources and full posts remain required; false reachable assertions must fail.

Trust assumptions: existing MU size equality is Rust's documented same-layout
property; translator preserves actual types/native reference resources; existing
solver handles nonnegative integers. This patch does not qualify the frozen chain,
prove its whole model sound, repair exact alignment metadata, or compose peer
profiles. Frozen snapshots never rewritten. Record full base/result hashes and
all effective profile identities in separate manifest/evidence.

## Acceptance/regression gates before consumer

Same callback-free guarded bodies with/without unused MU scratch: full VF0.
Both first-body false positive-size assertions: assertion refusal, before guard.
Positive size legally derived after real nonzero branch. Concrete unit/MUunit,
empty struct/repr(C) empty, ordinary u8/MUu8, empty and ZST arrays, alignment
invariants: positive bodies without fabricated runtime branches. Reachable false
at admissible concrete/generic ZST entry: intended assertion refusal. Resource
negative cannot acquire permission from ZST. C and C++ positives maintain prior
sizes; false claims remain refusals. Small matrix only for affected rules.

Then fresh native C1 exact source/MIR/AST on patched profile; verifier exit0,
real zero-route execution, retained complete posts and strict/deadcode/refinement/
unit/free/leak checks. Fresh normal/unwind negatives at mapped assertions and
source/extra-body/malformed/mixed/default-off admission controls. Stop consumer
if model gates fail. No C4 until full gates/C1; then actual sequential C1–C4
CURRENT native resources and each unwind, only within remaining window/budget.
Architecture beyond these size rules is a blocker, not permission to extend.

## Static review correction before Cloud

Independent review identified that `no Real fields` also matches ghost-only
logical structures. Candidate narrowed to `fmap = []`, excluding any ghost
field, and body_opt must be Some (complete); opaque declarations remain excluded.
This uses the existing parser distinction between complete definitions and
opaque specification declarations, not new compiler ABI metadata. Existing
translator filters only PhantomData (size0/align1) from physical fields; this
assumption is explicitly part of applicability. Complete zero-field spec
structures model zero-field Rust definitions; incorrect complete spec declaration
for a nonempty actual struct remains preexisting spec trust, not a new provenance
bridge. No source/ADT representation is changed. No exact alignment is asserted.
