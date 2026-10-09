# Initial c1 premise provenance map — static, not proof

Selectedactualfirstcall SmallSort254. Path len>=8; scratch.len()>=len+16;
!(size_of<T>()<=16 && len>=16), retaining original constcondition, no cutoff.
OriginalFreezeMarker bound only; definition shared/mod.rs implT:Freeze, core
marker.rs Freeze unsafeauto excludesdirectUnsafeCell butallows indirections.
Geometry plus numericpointer inequality alone createsno permissions.

| Supplied c1 premise | Actual caller source / model | Initial classification |
|---|---|---|
| initializedsource0..3 | v:&mut[T]; native slice_full_borrow_content is array<T>(stripmetadata(v),len,elems) | Existingmodel candidate; native contract/prefix must check |
| CURRENT T owners0..3 | same FBC foreach(elems,own<T>(t)); array_split+foreach_split | Existingchecked lemma candidate; no rawread→own axiom |
| optionaldestination4 | scratch:&mut[MaybeUninit<T>]; first4 physical MaybeUninit cells | Checkedconversion needed; open_MaybeUninit yields optionT storage, no T own |
| CURRENT F cell/F.own | is_less:&mut F fullborrow/pointee content | Existingmodel candidate; generated entry and boundary check pending |
| threadtoken/currentthread | generated RustBelt contract context | Tool-generated premise; not from pointervalidity; inspectexacttemplate |
| T/F type_interp | generated genericcontract context | Tool-generated premise; exactfraction/availability mustmatchc1 |
| positive-sizeT | c1 pre asks0<size; actualbranch admitsZST when8<=len<16 | Doesnotfollow overallbranch; conditional positive-size fragment or c1 interface gap |
| geometry/provenance | arraylimits+actualslice len/as_mut_ptr+MaybeUninit same layout | Existingmodel contracts/lemma supportmustcheck; addressrights forbidden |
| lifetime/borrowtokens | &mut slice/F lifetime and actualreborrows to len/as_mut_ptr | Toolrepresentation/prefixsupportmustcheck; no debt assumedclosed |
| remaining source/scratchframe | source elems4..len; scratch4..scratchlen; outercallerborrowcontext | split/join conservation proofrequired; nativepost/leak restore |
| all legalcompatibleFaliases | F.own+separatedborrows only supports modeledcompatible states | Completenessnotderived; actualFreezeallowsindirection, no purity |

No premise is marked derived before freshCloud execution. Native reference
representation is the first possible blocker; scratch storage conversion is a
second candidate. Source validity contract alone is insufficient. Current c1
normal fullfunctionposts remainNOT_PROVED, c2untouched.

Stock definitions inspected at exactVerifierbasef76012fb518703b1d98e243ac4f487f16877cfcb
(prelude_core sliceFBC/array split; std/lib MaybeUninit open/close) and must match
fresh effectiveCloudhashes before a result. Static reference review is not
accepted source/toolprofile soundness. Actual sourceinputs are read fromownrepo;
source extraction and all compilation/proof run onlyCloud.
