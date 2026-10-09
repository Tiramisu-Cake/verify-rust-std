# Generic `MaybeUninit::new<T>` source/MIR capture lane

The opt-in `o26-generic-new-capture` Cloud lane first runs the unchanged
canonical O26 refreshed baseline, including its exact source/MIR/refinement
and proof evidence. It then prepares a distinct disposable unit from the
pinned complete repository std source and captures NORMAL and readonly MIR
plus refinement for that unit. No new verifier profile, kernel, parser,
translator, schema, specification, predicate, summary or actual select source
is installed. The baseline does not supply an actual generic constructor
summary.

The source card and exact full-file pins are in
`overnight-generic-select/CLOUD-GENERIC-NEW-SOURCE-CARD.md` and
`SOURCE-PINS.json`. The same Cloud Build must run `prepare.py` and
`capture.py` in fresh `allprooflogs/cases/generic-new-capture`. The local
copy's DefId differs from core; the independent wrapper calls the unchanged
external `std::mem::MaybeUninit::<T>::new(val)`. Runtime source pair bytes
must be identical. Both exporter modes, both decodes, and refinement must
exit zero and retain full binary/text hashes. The complete source
certificate, local-body inventory, observed union/field/move details,
external call target and substitutions, and normal/unwind successors are
review material. Missing exporter details are `UNOBSERVED`, never guessed.

The outer audit may say `GENERIC_NEW_SOURCE_MIR_CAPTURE_COMPLETE` only when
the baseline is complete, helper exits zero, source certificate and pair
match, required full MIR artifacts hash correctly in both modes, refinement
passes, and a unique local method and two wrapper bodies are inventoried.
That classification remains diagnostic. `verification_accepted=false`,
`actual_callee_proved=false`, and generic helper closure is not credited.
The VeriFast dead-code check is not run for the new source/MIR unit, so its
result stays unobserved. An export, decode, refinement, source, or inventory
failure is `INCONCLUSIVE`. No cold-constructor or migration experiment is
part of this lane.

The recipe transports the complete canonical O26 proof set, both refresh
patches, the four generic-source diagnostic files, and all transitive
Cloud infrastructure under `exact-recipe-v1`. Source-input negative controls
must select the new lane's exact infrastructure closure. This card records
no acceptance of generic union ownership, ZST layout, panicking Drop,
actual external DefId linkage, or the prior C8 SAFE prototype barrier.
