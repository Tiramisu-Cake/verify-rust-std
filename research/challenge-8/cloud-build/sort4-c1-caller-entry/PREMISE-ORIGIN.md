# First actual caller / premise origin

This is a map of pinned mechanisms and pending obligations, not proof credit.
Selected actual caller: `small_sort_general_with_scratch`; first call at
SmallSort line254, source SHA25685c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1,
blob40939f922bcb6fdc7ee0d30427fa861827043827. Entry references: v:&mut[T],
scratch:&mut[MaybeUninit<T>], is_less:&mutF. No previous comparator/copy on this path.

| Exact c1 premise / context | Actual origin and existing mechanism | Obligation / classification before Cloud |
|---|---|---|
| Initialized source cells0..3 | Generated mutable-slice full-borrow-content: whole array<T> of len; actual v.as_mut_ptr; checked array_split at4 | Existing mechanism; native entry/pointer contract and range must verify |
| CURRENT T owners0..3 | foreach(source_all,own<T>(thread)) from native slice FBC; checked foreach_split at4 | Existing mechanism; must stay CURRENT rather than snapshots |
| Writable optional destination slots4 | Whole scratch array<MaybeUninit<T>> from native mutable-slice FBC; scratch.as_mut_ptr cast; stock open_MaybeUninit percell → optional T cells; array_ construction | Checked lemmas/provenance required; no initialized T or additional T.own follows |
| CURRENT F cell / F.own | Generated elided mutable-reference FBC for is_less; no callback before callsite | Existing mechanism; actual raw-pointer and opaque-owner transmission must verify |
| Thread/currentThread | Native generated contract | Existing mechanism; actual entry must verify |
| T/F type_interp | Existing c1 requires both; native generated contract excerpt has no explicit type_interp | Availability unresolved; do not supply or infer from Rust type checking |
| Positive sizeof<T> | Existing c1 precondition | Does NOT follow full selected branch: ZST with8<=len<16 remains legal; local ghost guard only conditional restricted result |
| Source/scratch range/provenance | len>=8, scratch.len>=len+16 on selectedpath; actual as_mut_ptr contracts and typed storage permissions | Must derive from authorized resources; inequality/equal addresses create no rights |
| Comparator/reference borrow tokens | Not raw c1 memory-entry premises; c1 proof creates comparator borrow state from owned cells | Caller entry must preserve native lifetimes/reborrows; no c1 scoped debts or recovery assumed |
| Remaining v/scratch/caller frame | v tail array+foreach; scratch tail array plus opaque full MU foreach; native ref lifetime/context resources | Must remain framed and be returned without duplication/leak; exact MU identity roundtrip may need tool support |

Actual path: len>=8, scratch.len>=len+16 and
NOT(size_of<T>()<=16 AND len>=16), using original const condition.
No invented upper cutoff or size restriction in actual entry. T:FreezeMarker
is copied with actual blanket specialization T:Freeze, not interpreted as Copy,
purity, absence of lawful indirection/alias, or restrictions on F aliases.

Cloud fragment retains exact common operations/conditions, saves complete original
caller bytes, but stops each branch at an explicit boundary and uses no sort4
summary. Refiner compares fragment ghost pair only. Successful bridge would
establish exact captured c1 MEMORY_PRE_CONTRACT entailment inside size>0 ghost
branch, then restore native caller post/frame/leak; it is not a full caller proof.
Native prefix and full resource bridge are distinct. Experimental O26 production
profile here is separately pinned; previous c1 strict scope overlay is inactive.
No transfer of prior branch results to this unit/profile without integration.

Initial source pin:4ab62d12ef95e3f2da2440359c3bec8594535568. Cloud
Buildc7ab932c-204a-4cbc-a29e-f8c076d51dfb submitted. All new proof statuses pending.

## Final proof status

ALL c1 callsite premises remain supplied / NOT_DERIVED. Fresh native entry and
whole sourcearray+array_inv/large-type arithmetic are observed intermediary steps
in failed prefix VC, not standalone entailment theorem. Source4/owner split, F/
thread targetassertions, scratch conversion, type_interp and identity-call targets
NOT_REACHED. Fullnativeframe/post/return/leak at target NOT_REACHED; rawleakchecks
are from excluded-path earlyreturns. Representation(MIR/refiner) PASS separate
from missingstd::intrinsics::abort proofadmission. Scope-control PASS never proves
arbitraryFnMut recovery. Final replay and exactreproducer recorded independently.
