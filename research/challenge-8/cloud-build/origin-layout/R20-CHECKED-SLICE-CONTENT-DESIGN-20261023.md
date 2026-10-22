# Checked array3 and slice content prerequisite

Defect: the original caller has no checked, source-linked conversion between its
owned three-element span and slice borrow content. Metadata equality alone does
not supply either memory or a borrow. The new helper is a bounded resource
representation prerequisite, not a repair of the original caller.

Applicability: initialized `u64` span of exactly three elements, same complete
data pointer after stripping only the slice metadata, slice length exactly 3.
Both directions require actual resources. Borrow conversion additionally
requires an existing full borrow and proves both implication witnesses before
calling the existing `full_borrow_implies`. It neither creates a source borrow
nor identifies a compiler region with a semantic lifetime.

Invariant: opening and closing the same element array and its element owners
preserves the complete CURRENT contents. The pointer premise includes provenance;
it is not address equality. There is no axiom, assume, leak, new memory/alias
model, cast between RawPtr and Ref operations, or inferred lifetime replacement.
Runtime, actual algorithm, generic signatures, normal/unwind posts and controls
are unchanged. The original `[u64;3]` reference lifecycle remains OPEN.

The helper definitions will be included as checked ghost declarations in the
raw caller fixture, whose source gate reconstructs its exact expected bytes.
Cloud must verify all lemma bodies before any completion claim. Existing
array3/array11 and wrong-metadata controls remain required on compatible pins.
No local compiler or verifier runs are authorized, and no service test that
only mirrors these lemma bodies is used as proof evidence.
