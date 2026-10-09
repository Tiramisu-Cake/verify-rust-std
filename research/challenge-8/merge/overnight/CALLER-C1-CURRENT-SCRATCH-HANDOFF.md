# Current scratch handoff at actual guard construction

DAY-MERGE source-linked design, not a verified caller contract. Source/blob
85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1 /
40939f922bcb6fdc7ee0d30427fa861827043827. Applies only to
small_sort_general_with_scratch:220–291, the source site constructing guard279.
Other callers have different storage protocol and receive no credit.

The nearest missing actual transition is immediately before279: initialized
CURRENT scratch values must carry the unique existing input owner pool, while
v retains initialized old bytes as destination options without a second owner.
Construction packages that state into a nonFalse own; no source snapshot,
address equality, copied bytes, slice.share or Freeze marker creates owners.
The independent construction fragment under supplied payload is partial: it
checks the physical value formation only, not this missing input derivation.

Source operations242–275 seed each scratch half through initial copy or
sort4/sort8 and extend the prefixes through insert_tail. A future actual-source
invariant must track (1) current initialized scratch prefix and matching current
owner list, (2) uninitialized MaybeUninit suffix, (3) initialized destination
old-options with no duplicate owner list, and (4) current comparator ownership
separately. Each source-linked seed/sort/insert callee must be verified at this
source before composing its summary. Native owner permutations alone do not
establish the bytes equality that authorizes owner relocation.

C1 source/destination extent/provenance and all12 G2 coordinates/posts remain
mandatory. Public exclusive borrows offer a derivation target, not automatic
numeric interval/object-limit facts. Callback answers remain arbitrary for
safety; SWO/immutable-key/faithful-answer premises belong only to functionality.
FnMut does not imply a frame; captured raw aliases must be analyzed with actual
borrow/provenance/permissions, not address comparison. Current callback state
and current values survive every transfer; no entry snapshot substitution.

Unwind requires source owner pool/current values sufficient for verified actual
Drop full-copy pre; normal requires owner pool moved to destination exactly once
and scratch bytes without duplicate ownership before forget. Payload-own would
be consumed by generic forget and therefore needs a checked cancellation/
ownership protocol. Field/padding resources remain separate from payload pool.

Pinned canonical safe-Drop FBC pre has field chunks/padding + guard own, but
canonical post returns fields/padding only. Full actual Drop post also preserves
arrays/owners, so nonFalse payload-own exposes a header compatibility leak.
Per-field limits/padding do not establish whole-guard numeric geometry or
self-vs-array interval disjointness. Both proof and contract gaps must be closed;
replacing safe-Drop pre by stronger conditional req is rejected, not a fix.
A future source-specific post/glue rule must retain canonical pre, justify
payload output from a checked actual callee, prove construction formation and
all callsite preconditions, and account for field/padding slot death. No semantic
patch is authorized by this card alone; current user phase allows implementing
a justified separately reviewed rule, with full positive/negative gates.

Next decision after construction fragment: derive current scratch handoff from
actual source operations, or first prove source-specific canonical Drop payload
post and guard geometry if frozen model supports it. Arbitrary-n actual merge,
normal ownership/forget, unwind restoration and generic/ZST remain OPEN.
