# R13 shared-reference ownership representation design (before implementation)

The exact R12 source chain is in H-A1-R12-OPTION-REF-OWN-BOUNDARY-2026-10-21.md.
The relevant effective patches do not change rust_parser.ml or general.rsspec.
At f76012fb, generic enum fields use TypePredExpr(T,"own"); after substitution
T=&'a U this denotes opaque own(ref_typeid(a,U)). In contrast translate_ref_ty
(Mir.Not) uses the pointee's `shr` callback, and translate_param_ty defines it
as `[_](<U>.share)('a,t,r)`. rustbelt.ml explicitly requires `shr` to be
duplicable. general.rsspec:68 already defines shared_ref_own with this dummy
share interpretation. Neither rule requires Copy/Freeze for U.

Proposed minimal representation normalization: give shared-reference `.own`
a definitional predicate constructor in the existing RustBelt spec, whose body
is exactly that existing dummy-share interpretation, and register it using
existing type_pred_def machinery (as for raw pointers). This is a change of
representation implementation, not a checked consequence of the old opaque
symbol. No reverse lemma may be postulated; no `assume`, axiom, leak command,
empty reference-own definition or numeric address rule is permitted. Independent
review must decide whether this source-backed definition qualifies as the
explicitly authorized normalization rather than an additional trust bridge.
If it does not, do not dispatch it or claim that opaque-own entails share.

Correspondence: constructor application is indexed by both lifetime and U type
identity, takes the same thread/value arguments, and unfolds to exactly the
existing generic reference interpretation. Generic Option_own's substitution
must still select U own for non-reference U, reference own for &'a U, and no
new rule for &'a mut U. None stays emp; Some retains its field resource. Cleanup
may discard only the already persistent dummy share, retaining thread_token;
non-reference field ownership must fail erasure. Runtime source, generic
signature and all normal/unwind/abort posts remain unchanged. Canonical helper
adds an explicit checked open in Some; it cannot assume value=None.

First faithful Cloud target: arbitrary generic Option<&'a U> cleanup using the
same canonical helper text, plus: Some extraction preserving the exact share;
shared-reference own roundtrip; generic non-reference Option roundtrip; negative
generic Option erasure; negative mutable-reference erasure; negative lifetime
redirection. Controls use actual verifier bodies and source/AST spans, not just
static string matches. All controls must be classified at their intended body
and resource. The mini unit has no caller receipt, no matrix admission and no
B1/B2 credit. Canonical P0c still needs fresh exact helper/caller same-Build
receipt. Full26 remains mandatory after prerequisites.

The effective source chain must include/pin this spec patch and resulting spec
SHA in snapshots and tool identity before any probe runs; all other specs and
tool hashes remain pinned. Existing compile preflight precedes target/controls.
No local compiler/preparer/verifier is permitted.
