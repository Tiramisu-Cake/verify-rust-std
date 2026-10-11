# Corrected caller resource review — conditional GO to fresh Cloud

Independent read-only GPT-6 Sol review of exact prepared commit
`7c7e24655c7bdf6e6b00df995da6c8152e315ddc`, experiment card and immutable
saved-byte fixture. No compiler, extraction or proof was run locally.

Caller entry is the unchanged prep.CONTRACT: tail physical storage/held owner,
thread/type interpretation and scalar geometry. Actual tail.read constructs tmp;
the adjacent three-field guard derives src=held_ref, dst=tail and len1.
Nonempty own and canonical FBC consume these original resources; two half-own
opens and merges restore the source quarter, destination gap, full field frame,
padding and type interpretation before singleton array packaging. There is no
injected standalone helper input.

Existing close_points_to folds the initialized physical guard. Actual mutable
borrow and reference-to-pointer cast produce the referenced aggregate; the
caller opens it and checks its exact ref_mut_end_token. The helper's full
contract consumes that frame and payload, executes the mechanically specialized
dynamic copy, and closes the defined CURRENT effect inline. The caller returns
the original local allocation with close_points_to/end_ref_mut, opens the effect,
ends readonly source reference/lifetime and targets the unchanged full normal
post. Field/padding and ownership fractions remain explicit.

The remaining falsifiable question is whether frozen refinement and verifier
support this exact aggregate/borrow/token handoff; current fresh Build must
decide. This review provides no proof credit. Normal-return/leak classifier
anchors are scoped to each target function's source closing brace, with dead
code refused. Source/MIR/AST gates identify a manually specialized helper;
actual Drop receiver-origin, compiler-produced glue, whole insert_tail and panic
cleanup must remain open regardless of this fragment's outcome.

Focused method-origin audit: frozen tool `bin/rust/aliasing.rsspec:55–69` create_ref_mut ensures only returned points_to plus opaque ref_mut_end_token; end_ref_mut returns the original chunk. ref_origin geometry/idempotence lemmas at10–23 do not imply pointer fixedpoint. Translator mutable Ref selects create_ref_mut at3293–3300, while generated actual Drop contract at4585–4613 explicitly requires ref_origin(self)==self and full borrow content. rust_belt/aliasing.rsspec:1–4 reborrow_ref_mut supplies fixedpoint only from full_borrow/lifetime_token, which this physical token/aggregate route does not provide. Therefore the current rawhelper route does not discharge actual method applicability; this is a minimal explicit blocker alongside absent selected Drop/glue lowering. No token-to-origin equality may be inferred.

Fresh419034 addressed correction GO: actual MIR mutableRef at155 is translated into $_68=AddressOf(gap_guard), then guard_ptr=AddressOf(Deref($_68)), proof-ast550–552. No create_ref_mut or token-producing call occurs. Log folds the original aggregate154 and opens it atactualguardpointer156, then refuses only invented token157. Replace token assertion with exact derived pointer equality plus unchanged physical field/padding checks; remove end_ref_mut and unnecessary final fold, retain returned physical fields for ordinary StorageDead cleanup as in passing direct consumer. This repairs an annotation to actual frozen lowering; no ownership/resource/helper-pre/post weakening or semantic patch. Actual method fixedpoint/glue remains OPEN. Fresh run required.
