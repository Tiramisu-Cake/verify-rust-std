# Exact native caller applicability / preserved c1 boundary

Fresh model used by all new cases is Cloud-built O26 production at base
f76012fb518703b1d98e243ac4f487f16877cfcb, experimental/unaccepted. No new kernel,
translator, rsspec or alias-model patch in this phase. Full identity inventory is
FIRST-TOOL-SNAPSHOT and final snapshot. Source linkage is to the selected first
call in original caller; added exact-domain path filters are diagnostic boundaries,
not claimed byte-identical complete caller execution. The original prefix can
be reconstructed by removal of exact insertions in certificates. Refiner proves
only the filtered ghost source pair. This cannot be upgraded to wholecaller proof.

Native generated mutable slice FBC in vf_mir_translator slice_ref_ty_info2013ff /
prelude_core445ff is array<T>(strip_metadata(v),ptr_len(v),values) plus
foreach(values,own<T>(thread)). Scratch uses the same shape for MaybeUninit<T>,
not initialized T. Mutable elided F input uses sized pointee FBC current cell plus
F.own. gen_contract5729ff produces thread/currentThread and lifetime tokens,
not explicit T/F type_interp. Stock arrays provide count*sizeofT<=isizeMAX.
Availability after real len/as_mut_ptr prefix and finalframe restoration remains
subject to case verification. Assertions before a later failed VC are observed
steps, never accepted standalone entailment theorem.

Native aliasing.rsspec102–107 slice create/reborrow uses reqtrue TODO and result
identity; shape alone does not prove lawful creation, provenance or borrow recovery
for every actual reference. The prefix can exercise these stock contracts, but
all-legal-entry qualification needs accepted reference/lifetime semantics. Source,
scratch and F full permissions may represent lawful exclusive mutable resources;
point inequality creates no permissions and no model premise may replace a real
caller origin. F.own remains opaque; no no-alias/purity/Copy/no-panic is added.
Compatible lawful indirections/aliases in F are not universally discharged here.

Original condition NOT(sizeT<=16 AND len>=16) with len>=8 does not imply sizeT>0.
T:FreezeMarker copies original specialized-marker trait and implT:Freeze exactly;
core Freeze excludes direct UnsafeCell, includes legal indirection and ZST such
asunit. It supplies neither Copy nor logical thread/type/owner facts by its name.
Currentc1 size>0 is still supplied or tested in a conditionalghostguard. Legal ZST
8..15, othercalls/paths, generic legalshared-entry and universalaliases remainopen.

Previous c1 checkpoint19f82018 remains unchanged: exactactual continuation admitted;
direct-unwind conditional recovery/join/post/leak observed; normal recovery/join
only intermediate successful steps in failedwholeVC followedby c2 missing
ref_precreated_token. Fullnormalpost/return/leak NOTREACHED. Both missingdebt
negatives savedrawreplay. No acceptedstandalonec1/fullsort4/R6 theorem. The previous
strictscope/relocation profile is unaccepted. New callerentry cases do not execute
c1, c2–c5 or pointerselect; old conditional pointerselect e2b249674cbe505f2d073e0df8da023a6e6406ce
preserved only inexactconfiguration. Newc1branchintegration NOTRUN, even if a
partial/native bridge laterpasses; no transfer of priorproofto newunit/profile.
