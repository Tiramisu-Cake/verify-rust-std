# Sort4 full-contract admissibility review

2026-10-06; owner-authorized **documentation-only analysis**, entry
`826d74b45546f9ce1319e2cd4cac8b6d42a2f41f`, fork
`Tiramisu-Cake/verify-rust-std`, branch `challenge-8/research`.
**CLOSED — admissibility unresolved; organizer clarification recommended.**
The [research contract](SORT4-CONTRACT.md) is a motivated sufficient specification
for the audited caller routes. It is neither an accepted specification of the
entire challenge target nor a proved generic theorem. This review changes no
contract, std source, signature, proof code or trusted tool semantics and adds
no proof coverage. No Actions dispatch, compilation, verification or executable
tests occurred. No question was sent externally.

## Target and acceptance boundary

The reviewed [actual body and short SAFETY comment][sort4] have Git blob
`e555fce440872898e47fd5114f32eb15401d07df`. The comment specifies four source
reads, four destination writes and result location. The signature is unrestricted
`T, F: FnMut(&T, &T) -> bool`. Its `pub` visibility is inside a crate-private
[module][module]; “public target” here means the function explicitly named in
[Challenge 8][challenge], not a callable external stable std API.

Challenge 8 separately requests absence of UB for `sort4_stable` and sorting
contracts for the three `small_sort` trait implementations, at arbitrary valid
lengths. Sort4's arity is exactly four; it does not remove generic type/callback/
allocation obligations. A strong functional sort4 summary is useful for later
composition, but is not itself an additional explicit challenge acceptance
criterion. The four required UB categories and source SAFETY obligations remain
independent of sortedness. [General rules][rules] require source/documented safety
conditions, approved integrated automation and unchanged runtime logic; functional
premises must not restrict safety coverage.

“Declared” below means explicit short comment/signature together with applicable
Rust operation requirements. “Caller-established” means a static audit of the
existing routes, not a verified callee composition. “Clarify” means the premise
or post is stronger than the short comment, or its use as the challenge-wide
domain has not been accepted. Safety requirements are assessed at the actual
operation, not inferred merely from an entry pointer's numeric address.

## Assumption ledger

Roles: **S** Rust safety; **F** functional summary; **R** full resource accounting
in our proposed model. A row marked R does not thereby become a Rust UB rule.

| Assumption or obligation in our contract | Exact basis | Role and strength | Status for the named target |
| --- | --- | --- | --- |
| Four accessible logical positions at each base; valid pointer arithmetic, liveness and provenance at every access | [Sort4 comment/body, lines610–624][sort4]; [pointer validity and reference conversion1–96][ptr-validity] | S: required for actual nonzero accesses and `add`; addresses/bounds alone are insufficient | Four reads/writes declared; precise access/reference interpretation follows Rust operations. Callers supply initialized slice storage. Lifetime/permission proof remains open. |
| Compared source elements initialized and valid as T, with legal shared references | `&*` at [626,627,641,642,649][sort4], [ptr reference-conversion61–96][ptr-validity] | S: required when converting these raw pointers to &T; stronger than raw readable bytes alone. Padding need not be initialized scalar data | Declared read wording is abbreviated; actual body/Rust rules justify reference validity. Not a Copy/Freeze premise. |
| Alignment, including alignment-sensitive ZST; source references nonnull even when size is zero | [ptr conversion61–96][ptr-validity], [copy458–471][copy] | S: explicit operation requirements; empty byte ranges do not eliminate alignment/reference conditions | Derived from actual operations, not full-range separation. RAPx's reproduced misses violate this independent requirement. Raw zero-byte access validity and reference validity must not be conflated. |
| Each of four copy pairs locally non-overlapping at its copy time | [copy451–471][copy]; [sort4653–656][sort4] | S: mandatory per `copy_nonoverlapping`, irrespective of ordering | Omitted as an explicit relation in short sort4 comment. It is an actual callee requirement; existing callers satisfy it. Clarify how it enters the accepted standalone contract. |
| Entire source/destination four-slot byte ranges separated for non-ZST | [contract spatial premises](SORT4-CONTRACT.md#current-comment-actual-body-and-distinct-premises); [callers220–255][callers], [sort8663–679][sort8] | S/F sufficient spatial condition; R convenient separation. Not demonstrated necessary for every individual safe or correctly sorting input | Caller-established. Does not follow from separate read/write validity alone. **Clarify** acceptance as a uniform target precondition. For ZST, empty-region separation supplies no logical ownership theorem. |
| No earlier destination write changes a not-yet-copied source representation after c5 | Pointer selection then ordered copies [628–656][sort4]; [shifted result](SORT4-CONTRACT-RESULTS.md#diagnostic-evidence) | F: sufficient preservation invariant for the V5 occurrence summary. Continued readability/validity is S, but bit-for-bit old-value preservation is not universally necessary for no UB, or even for a weaker final multiset post | Full separation establishes it for callers. Not declared separately. **Clarify** requested functional domain; do not equate the i32 multiset failure with invalid Rust values. |
| Destination may initially be uninitialized, with enough writable storage | Untyped copy and initialization preservation [446–463][copy]; [MaybeUninit scratch205–224][callers] | S: writes need storage validity, not prior T initialization. R: track actual initialization map, including initialized slots | Compatible with declared four writes and established callers. Requiring initialized T scratch would exclude the actual route. No generic transport proof yet. |
| No hidden prior destination ownership is silently overwritten; prior resources have an explicit disposition | [copy465–468][copy]; [research RawDst](SORT4-CONTRACT.md#resource-notation-and-sufficient-unrestricted-safety-precondition); [forget docs54–77][forget] | R: necessary for our full-accounting post. Overwriting a live resource can leak without itself proving Rust UB; later use of invalid/stale resources can be unsafe | Stack scratch has no prior live T owner. Arbitrary writable destination does not specify its resource policy. **Clarify** challenge-wide protocol; no no-leak restriction may be imposed on otherwise legal callback effects. |
| SrcOwn grants full recoverable cells/ownership, Cb and Frame have an explicit effect-aware split | [research resource notation](SORT4-CONTRACT.md#resource-notation-and-sufficient-unrestricted-safety-precondition); [ptr borrowing rules][ptr-validity] | R: a sufficient proof organization, potentially stronger than readable shared source access required by runtime | Caller v is an owning mutable slice, but sort4 takes `*const T` and does not explicitly require exclusive source ownership. **Clarify** whether a caller-specific summary suffices; do not present full permissions as the language's minimum UB condition. |
| One logical ownership sequence; copied non-Copy representations grant no second independent right to drop/use | [copy465–468][copy]; [MaybeUninit callers][callers]; [contract protocols](SORT4-CONTRACT.md#full-normal-post-and-ownership-protocol) | S: prevent unsafe duplicated-resource use where applicable. R: selected retained-source/Shadow protocol accounts for resources. Bit duplication itself is permitted; non-Copy is not synonymous with a double-free resource | Retained originals and nondropped scratch match the audited route. Exact SrcOwn/Shadow encoding and universal single-sequence post are not stated by sort4. **Clarify** acceptable ownership/access summary; later scratch references/moves need a proved relation. |
| Arbitrary legal callback state/interior effects and arbitrary Boolean results allowed for safety | [FnMut signature/calls][sort4]; [UnsafeCell2118–2180][cell]; [safe sort_by144–172][slice-sort] | S domain: no purity, ordering, Copy, Freeze or no-panic restriction. Cb must model legal effects rather than rule them out | Signature imposes no such bounds. Callers' [FreezeMarker impl][module] does not bound sort4. Required future proof must account for all effects relevant to continuing accesses and posts; assumed unchanged reachable ownership is insufficient. |
| Fixed consistent strict weak order on keys and preservation of relevant elements/keys for original-value sorting/stability | [sort4 pairing/selection comments625–651][sort4]; [sort_by ordering144–150][slice-sort]; [research functional premises](SORT4-CONTRACT.md#full-normal-post-and-ownership-protocol) | F sufficient premises for the proposed original-occurrence theorem; not required for unrestricted S and not asserted necessary for every accidentally sorted execution | Conditional research functionality, not short SAFETY contract. Safe slice docs use total-order wording; the bool-summary's strict-weak-order/equivalence formulation still needs a checked theorem. Legal counter/state updates need not be excluded. |
| Normal and each direct panic return current callback/source/frame resources, scratch initialization, and end temporary borrow obligations | [all five calls before copies][sort4]; [safe slice panic guarantee167–172][slice-sort]; [contract panic posts](SORT4-CONTRACT.md#all-five-panic-posts) | S: continued valid access/drop invariants. R: exact full-accounting post/no local proof debt. No callback rollback or original-key sorting on unwind | Body justifies no sort4 copy before a callback panic; caller/source/resource restoration is **not proved**. Safe API guarantee motivates composition but does not alone establish this unsafe helper's full post. |
| Normal source unchanged since V5 and destination initialized with selected V5 representations | [sort4653–656][sort4]; [full normal post](SORT4-CONTRACT.md#full-normal-post-and-ownership-protocol) | F/R: sufficient separated-range normal summary, includes valid fields and permitted padding initialization state | Conditional on preservation/separation and legal callback state. Not promised for every overlap by the short comment. Generic proof and admissibility remain open. |

## Copies, preservation and existing counterexamples

Use S_i for the source slot, D_j for the destination slot and pi for the selected
source-index order after c5. The selection table and pair exchanges statically
form a permutation of the four **positions** for any five Boolean answers. They
do not snapshot T values. For each j=0..3, the actual requirement is readable
S_pi(j), writable D_j and non-overlap of those two one-element regions at that
time. To preserve the chosen V5 values, separating D_j from each later
S_pi(k), k>j, is sufficient. Full separation implies both predicates and also
the stronger post that every source representation remains unchanged.
Preserving unread sources alone does not imply that stronger source post: a
write could change an already-read source. None of these observations proves a
minimal necessary spatial precondition for every permutation/type/input.

The existing [run37466906281][overlap-run], source
`7f96aa2f3262cf209ff3dcafd06e355e5590885b`, gives two distinct actual-body facts:

- Coincident initialized i32 ranges on ascending [0,1,2,3] fail only the first
  0→0 `copy_nonoverlapping` non-overlap precondition. Read/write storage validity
  alone does not express this missing relationship. No post-UB output is claimed.
- Shifted [0,4)→[1,5) has locally disjoint 0→1,1→2,2→3,3→4 copies. Earlier writes
  replace later inputs; the separate witness yields [0,0,0,0] instead of the
  original [0,1,2,3]. Only the original-multiset assertion fails in that default
  initialized-i32 profile. This is a functional counterexample, **not a
  demonstrated UB** or a full classification of overlapping generic inputs.

The [report](SORT4-CONTRACT-RESULTS.md) preserves the exact check locations,
positive control, independent witness, failed preparations and hashes. The
earlier [functional theorem](SORT4-RESULTS.md) remains four arbitrary i32 values
in fixed separated initialized buffers, pure nonpanicking ordering and a
separate tagged Copy stability proof (18/18 covers). No result supplies the
missing generic ownership/permission theorem.

## Scratch and caller ownership boundary

The existing [caller audit](SORT4-CONTRACT.md#mapping-to-actual-callers), checked
against the unchanged source, establishes these spatial/initialization facts:

| Route | Actual ranges and bounds | Established scope |
| --- | --- | --- |
| Direct sort4, [253–255][callers] | v[0,4)→scratch[0,4), v[h,h+4)→scratch[h,h+4), h=floor(len/2), len>=8; scratch.len>=len+16 | Distinct mutable v/scratch regions; initialized source T, MaybeUninit output. First actual sort4 here is at254, c1 is626. |
| sort8 internal, [671–672][sort8] | v[0,4)→temp[0,4), v[4,8)→temp[4,8) | Bounds/separation follow from the audited outer callers, not solely sort8's abbreviated SAFETY comment. |
| Two outer sort8 calls, [241–249][callers] | len>=16, size(T)<=16; v halves at0,h; output scratch at0,h; temp scratch[len,len+8), [len+8,len+16) | h>=8 and h+8<=len, all relevant nonzero byte regions separate; scratch bound covers both temps. |

The stack allocation is `MaybeUninit<[T;48]>`; no automatic destructor for its
T replicas runs. FreezeMarker restricts these callers, not this named sort4
target, and implies neither Copy nor comparator purity. For non-Copy T, source
representations remain present after normal sort4; retained-originals plus
nondroppable Shadow is our selected accounting interpretation, not an automatic
second owner created by byte copying. Moving logical ownership to dst is another
possible protocol, with different later source-use/drop requirements.

Rust permits resource leaks ([forget][forget-doc]); unrestricted safety cannot
require every legal callback to preserve all entry resources or run destructors.
Our full post must account for permitted callback resource replacement, transfer
or forgetting through Q/H, and must not introduce additional unexplained losses
by sort4. Requiring no proof debt is a verification-model requirement. It is not
a new Rust prohibition on leaking. Shared source access and resource-bearing ZST
occurrences also need an appropriate protocol; empty addresses or full byte
permissions alone do not establish it.

Later insertion through scratch, sort8 merging, `CopyOnDrop` and final ownership
return to v are **unproved separate composition obligations**. A static caller
audit cannot establish standalone contract completeness or prove that Shadow
supports all later generic shared references/moves. No ownership bridge is assumed.

## Comparator effects and five direct panic exits

All five sites invoke the real comparator; a false Boolean is an ordinary return,
not a panic branch. A legal comparator may update counters/captured resources
and interior mutable data; current state Vk/Qk/Hk incorporates successful calls
and effects of the panicking call. It may replace/drop/forget resources legally;
recovering current invariants must not falsely restore their entry identities.
Changes to keys prevent unconditional sorting of entry snapshots. A consistent
ordering/key-preservation premise belongs only to the conditional F theorem.

| Direct callback panic | Actual arguments / line | Required current-state boundary |
| --- | --- | --- |
| c1 | s1,s0 /626 | c1 effects, source current invariant, incoming raw dst modulo callback effects; no preceding sort4 call within this invocation |
| c2 | s3,s2 /627 | completed c1 and c2 panic effects; recover any comparison-borrow resources |
| c3 | c=s_(2+c2), a=s_c1 /641 | c1/c2 effects plus c3; selected pointers retain valid provenance |
| c4 | d=s_(2+!c2), b=s_(!c1) /642 | c1..c3 effects plus c4; all current source/callback/frame resources |
| c5 | selected unknown_right,unknown_left /649 | c1..c4 effects plus c5; four destination copies have still not begun |

Every row shares the full research unwind post: one current ownership sequence
in the selected protocol, actual raw destination initialization, callback/frame
effects and discharged temporary borrows. No sortedness, rollback or restored
V0/F0/H0 is promised. Destination is unchanged **by this sort4 invocation**;
callback-accessible memory uses its actual effect post. On the audited private
stack scratch route the comparator cannot access that scratch, so its incoming
state remains. For the second sort4 in a caller, an earlier invocation may already
have written scratch: these five local exits do not roll that back.

The body contains no local T drop guard/cleanup that could recover a missing
proof resource. `select_unpredictable` is instantiated with pointer values;
the [actual helper][select] must still be proved at the matching source before
using a summary. No synthetic cleanup-only control is an actual first-callback
sort4 path. The table is control-flow/resource analysis, not a generic panic
proof; the earlier tool feasibility gaps remain in
[the no-patch assessment](SORT4-NO-PATCH-ASSESSMENT.md).

## Available official clarification and its limits

Checked read-only on2026-10-06: published [Challenge 8][challenge] and
[general rules][rules]; tracking [issue56][issue56] including all four API-returned
comments; challenge-opening [PR57](https://github.com/model-checking/verify-rust-std/pull/57)
comments/reviews; related [PR576](https://github.com/model-checking/verify-rust-std/pull/576)
comments/reviews; [PR701](https://github.com/model-checking/verify-rust-std/pull/701)
description/review list (open, no reviews returned). No other solution's
proof code was used. Scoped searches for sort4 overlap/precondition explanations
identified no additional organizer answer; this is a bounded search, not proof
that no explanation exists anywhere.

Organizer [qinheping's answer][organizer-answer] says insufficient safety comments
should be corrected upstream, and recognizes primitive/default-order proofs as
valuable functional solutions despite the eventual arbitrary-type/order goal.
It addresses a merge_down question, **not** sort4 range separation or scratch
ownership, and does not authorize purity/Copy/Freeze/no-panic restrictions on
unrestricted safety. Later [PR576 review][review576] stresses permutation and
length coverage; it supplies no sort4 overlap-domain acceptance. Neither an open
proposal nor valid current callers is a committee decision accepting our stronger
precondition. **No explicit organizer answer to this contract question was found
in these inspected sources.**

Official [copy docs][copy-doc] corroborate local non-overlap, initialization-state
preservation and alignment for ZST. [UnsafeCell docs][cell-doc] permit interior
mutation while retaining aliasing obligations; [safe sort_by docs][slice-doc]
preserve elements and interior effects on panic, and separate ordering from
safety. These explain Rust operations and safe API composition. They do not
settle what strengthened standalone challenge contract organizers will accept.
The pinned repository documents above govern our unchanged target; live official
std docs were checked as corroboration, not substituted source/version semantics.

## Historical runner limitation and closed RAPx evidence

Static inspection at entry HEAD shows
[run-rapx-applicability.sh:219][old-runner] calls
`run_stage classifier-tests python3 "$classifier_tests"` without `--evidence-dir`.
[The test entrypoint:254][tests] now requires that argument. The
[corrected classifier:13–27][classifier] binds exact six-case names, DefId/hash,
checkpoints and paths to source929ea803/run37508888778 on x86_64. It is not a
general classifier for future freshly built cases. The old runner and replay
interface are therefore incompatible for a fresh verifier run.

This is a static preparation limitation, **not an observed new failing run**.
It was not repaired or executed. Any separately authorized future runner use
must first review evidence provisioning and source-specific metadata/test scope;
adding an arbitrary directory or weakening matching would not solve that contract.
This finding neither invalidates the successful saved-data replay nor reopens
gate A. The [semantic report](RAPX-APPLICABILITY-RESULTS.md) preserves run37508888778
and [replay37513897141][replay] at processor
`1c0b5171375c1198ef0e94b6a26d5e3a13cf1a15`: two ZST SOUND_MISS, automatic NO-GO,
two valid controls and two u64 intended Align detections with other Failed/Unknown.
B/C were not run and remain closed. No new tool screening or experiment follows.

## Decision and unsent organizer question

**Justified:** actual copy preconditions must be accounted for; complete separation
is a sufficient way to protect copies and remaining source values; existing
callers provide that separation and MaybeUninit scratch; legal callback effects
and all five direct panic exits must stay in safety scope. Existing measured
overlaps demonstrate two different omissions in the short comment's interpretation.

**Unresolved:** whether a full caller-motivated, separated-range/raw-scratch
summary is an admissible complete contract for the named standalone safety
target, and whether our explicit resource accounting is an acceptable summary
rather than an exclusion of legal readable-source/destination protocols.
It is premature to call the current full research contract challenge-complete.
The recommended next owner decision is to approve seeking this specific
clarification, or retain the stop. No sending/publication is authorized here.

| Organizer answer | Consequence for a separately approved next task |
| --- | --- |
| Accept sufficient caller-motivated separation and explicitly described scratch ownership protocol | Record the accepted domain and distinguish R from S; only then decide a source-exact proof route. Five-panic/copy/ownership proofs remain absent, and RAPx NO-GO is unchanged. |
| Require safety for every input satisfying literal four-read/four-write wording, or a broader source/ownership protocol | Current separated/full-own summary cannot close that target. Clarify the missing operation-level premises and any upstream safety-doc correction; do not claim a false universal theorem or modify std ourselves. The shifted case separately prevents unconditional original-value functionality on that domain. |
| Require weaker, operation-specific spatial conditions instead of full separation | Separately authorize a specification analysis of local copy safety, continued source validity and preservation/source post; do not assume every overlap unsafe or silently weaken the frozen contract. |

Draft for issue56, **recorded only, not sent**:

> For Challenge8's standalone `sort4_stable` safety target, may we use an explicit
> sufficient contract with separate four-element source/output ranges and raw,
> possibly uninitialized scratch, accounting for non-Copy representations without
> a second independent drop owner? The [pinned SAFETY comment/body][sort4] states
> only four reads/four writes. Our [actual-body diagnostics][diagnostics] show
> coincident ascending i32 ranges violate the first copy's non-overlap, while a
> one-cell shift has four locally non-overlapping copies but loses the original
> multiset (functional failure, not demonstrated UB). The [caller audit][audit]
> establishes separation for existing routes. Should the accepted helper domain
> follow those caller invariants, require weaker per-operation conditions, or
> cover every range allowed by the literal comment? We keep legal comparator
> effects and all five panic exits in safety scope; ordering premises are separate.

No new experiments are recommended before that decision; no previous phase is
reopened by this analysis. Current checkpoint is [STATUS](STATUS.md).

[sort4]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/826d74b45546f9ce1319e2cd4cac8b6d42a2f41f/library/core/src/slice/sort/shared/smallsort.rs#L610-L658
[callers]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/826d74b45546f9ce1319e2cd4cac8b6d42a2f41f/library/core/src/slice/sort/shared/smallsort.rs#L205-L292
[sort8]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/826d74b45546f9ce1319e2cd4cac8b6d42a2f41f/library/core/src/slice/sort/shared/smallsort.rs#L660-L679
[copy]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/826d74b45546f9ce1319e2cd4cac8b6d42a2f41f/library/core/src/ptr/mod.rs#L437-L471
[ptr-validity]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/826d74b45546f9ce1319e2cd4cac8b6d42a2f41f/library/core/src/ptr/mod.rs#L1-L96
[slice-sort]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/826d74b45546f9ce1319e2cd4cac8b6d42a2f41f/library/alloc/src/slice.rs#L134-L172
[cell]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/826d74b45546f9ce1319e2cd4cac8b6d42a2f41f/library/core/src/cell.rs#L2118-L2180
[forget]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/826d74b45546f9ce1319e2cd4cac8b6d42a2f41f/library/core/src/mem/mod.rs#L54-L77
[module]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/826d74b45546f9ce1319e2cd4cac8b6d42a2f41f/library/core/src/slice/sort/shared/mod.rs#L1-L13
[select]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/826d74b45546f9ce1319e2cd4cac8b6d42a2f41f/library/core/src/hint.rs#L836-L884
[challenge]: https://model-checking.github.io/verify-rust-std/challenges/0008-smallsort.html
[rules]: https://model-checking.github.io/verify-rust-std/general-rules.html#committee-applications
[issue56]: https://github.com/model-checking/verify-rust-std/issues/56
[organizer-answer]: https://github.com/model-checking/verify-rust-std/issues/56#issuecomment-2611410906
[review576]: https://github.com/model-checking/verify-rust-std/pull/576#pullrequestreview-4947412389
[copy-doc]: https://doc.rust-lang.org/std/ptr/fn.copy_nonoverlapping.html
[cell-doc]: https://doc.rust-lang.org/std/cell/struct.UnsafeCell.html
[forget-doc]: https://doc.rust-lang.org/std/mem/fn.forget.html
[slice-doc]: https://doc.rust-lang.org/std/primitive.slice.html#method.sort_by
[overlap-run]: https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37466906281
[replay]: https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37513897141
[old-runner]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/826d74b45546f9ce1319e2cd4cac8b6d42a2f41f/research/challenge-8/run-rapx-applicability.sh#L217-L219
[tests]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/826d74b45546f9ce1319e2cd4cac8b6d42a2f41f/research/challenge-8/test-rapx-applicability-classifier.py#L252-L256
[classifier]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/826d74b45546f9ce1319e2cd4cac8b6d42a2f41f/research/challenge-8/classify-rapx-applicability.py#L13-L27
[diagnostics]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/826d74b45546f9ce1319e2cd4cac8b6d42a2f41f/research/challenge-8/SORT4-CONTRACT-RESULTS.md#diagnostic-evidence
[audit]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/826d74b45546f9ce1319e2cd4cac8b6d42a2f41f/research/challenge-8/SORT4-CONTRACT.md#mapping-to-actual-callers
