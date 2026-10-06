# Challenge 8 coverage ledger

This tracks requirements, not inferred coverage from an Actions badge.
Current stop/phase: [STATUS.md](STATUS.md). Evidence and exact source/tool
identifiers: [experiment log](EXPERIMENT-LOG.md). Distinguish actual-source
proofs, bounded adapters, synthetic fixtures and prefixes of failing proofs.
No complete Challenge 8 solution is established.

The [sort4 phase](SORT4-PHASE.md) completed on 2026-10-06 under the
[revised roadmap](PLAN.md). [Hosted closeout](SORT4-RESULTS.md) establishes
the actual-body functional domain: four arbitrary full-range i32 keys in
fixed/disjoint initialized buffers, plus separate tagged-item stability.
Generic safety and complete four-category UB coverage remain open.

The subsequent [contract-diagnostics phase](SORT4-CONTRACT-PHASE.md) completed;
[run37466906281](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37466906281),
source7f96aa2, validates unchanged values0/267failed/12covers, coincident actual
copy overlap negative, shifted original-multiset negative with all other default
checks passing/unreachable, and independent zero-output witness0/130failed/1cover.
The44-case classifier rejection gate passes. Coincident first copy violates
non-overlap; shifted individually disjoint copies lose original values, NOT an
UB finding. Prior memcmp-unwind and formatted-panic-label fixture failures are
preserved in [closeout](SORT4-CONTRACT-RESULTS.md). No generic safety/UB coverage
or new VeriFast result follows; [adopted research contract](SORT4-CONTRACT.md) and
[one selected architecture/gate](SORT4-SAFETY-DECISION.md) remain unproved research
specifications. That phase stopped at the owner decision; its proposed verifier
capability remains NOT AUTHORIZED.

The bounded [no-patch review](SORT4-NO-PATCH-ASSESSMENT.md) completed with no
new experiment and **no generic coverage gain**. Static comparison of official
VeriFast26.09/26.10 preserves relevant tuple/HRTB/direct-unwind/typed-scratch gaps;
Kani remains a concrete monomorphized evidence route. Target-source compilation/
refinement on26.10 NOT RUN. These are feasibility observations, not new target
failures or proofs. The historical patched proposal remains unauthorized;
the later explicit-domain decision below changes no tool finding or proof count.

The [remaining-tools screening](ALTERNATIVE-TOOLS-ASSESSMENT.md) selected the
[RAPx applicability phase](RAPX-APPLICABILITY-PHASE.md). Its preceding session
closed [INCONCLUSIVE](RAPX-APPLICABILITY-RESULTS.md). Hosted runs
[37492790456](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37492790456)
and [37493697524](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37493697524)
failed in runner setup (direct-driver version argument channel, then absent
Cargo checksum metadata). Exact package installation/version/binary identities
were recorded, but installed-source audit, layout, MIR, target preparation and
all six alignment controls were NOT RUN. Zero fixture paths/obligations and
**no generic or detector coverage gain**. B/C NOT RUN because A did not pass.
The suspected ZST alignment gap and callback/panic concerns remain source-review
concerns, not executed counterexamples in that historical session.
The subsequent owner-authorized A-only continuation used2/4 NEW runs and closes
**NO-GO**: run37508888778 at929ea803 completed identity audit and all six actual
controls (48 primitive records, six checkpoint paths). Both deliberate
alignment-eight ZST source/destination byte-offset1 copies are SOUND with the
violated Align ProvedByRule; optimized MIR retains the defect. Valid ZST/u64
controls prove; u64 negatives fail intended Align with separate ValidPtr Unknowns.
Manual contracts/DefId/checkpoint/property/MIR audit establishes these observations;
all automatic JSONs remain fail-closed/unmapped, not successful checks. This adds
concrete detector-limit evidence, **no generic or actual-sort4 proof coverage**.
B/C NOT RUN, no further dispatch/patch authorized. All safety/sorting tables below
retain earlier established proofs.

The separately authorized automatic replay37513897141, processor1c0b517,
uses only original artifact11434810024/source929ea803. All six real pairs parse;
9/9 hosted replay/mutation test groups pass. It reproduces two PROVED_VALID,
two ZST SOUND_MISS and two intended Align detections with separate Failed/Unknown.
commands_succeeded/evidence_parsed=true, gate_outcome=NO-GO. Original unmapped
JSONs/manual result preserved. This adds reproducible processing, **no new
verifier run or semantic coverage**. Replay scope CLOSED at1/2 allowed runs.

## Safety targets and sorting contracts

The documentation-only [joint-route assessment](SORT4-COMPOSITION-ASSESSMENT.md)
adds **no proof or detector coverage**. Multiple tools may prove independent
obligations, but current evidence supplies no generic composition or checked
model bridge. RAPx presently remains diagnostic; other properties are not
automatically reliable after the scoped Align finding. ZST is retained with
independent geometry/operation/resource obligations, A NO-GO and B/C NOT RUN.
The unchanged-VF alignment gate was NOT RUN / NOT AUTHORIZED at that review;
its separate [phase](SORT4-ALIGNMENT-PHASE.md) now closes INCONCLUSIVE at1/1.
[Run37529855468](SORT4-ALIGNMENT-RESULTS.md), source17ad1f4, passes all six
exports/decodes/refinements but every VeriFast case fails annotation parsing.
Zero helper/caller proof bodies or intended negatives were reached; this adds
**no geometry, layout, detector or generic-sort4 coverage**. Proposed formatting
correction was separately authorized and applied at9474453; the ONE additional
[run37532204465](SORT4-ALIGNMENT-RESULTS.md#syntax-only-continuation--one-new-run)
now closes INCONCLUSIVE. All six exports/decodes/refinements pass. Generic helpers
reach bodies but fail 0<=address before callers; ZST layout fails size==0, ZST add
fails pointer limits. Both byte-offset controls reach and reject intended line25
alignment assertion on manual audit. This adds limited false-post control evidence,
**no geometry/layout/automatic-copy UB or actual-sort4 coverage**. Raw all-six
INCONCLUSIVE/header counts0 retained; actual source-prefixed named headers exist
but unchanged classifier misses them. No classifier repair, proof fix or further
run authorized; additional budget1/1 used.
Arithmetic evidence alone would not count as automatic UB coverage. Required VF
callback/unwind/raw-copy capabilities are separated from optional historical
insertion patches. Existing Kani results retain their exact concrete domains.

The documentation-only [admissibility review](SORT4-ADMISSIBILITY-REVIEW.md)
adds **no proof or detector coverage**. Full range separation is sufficient and
caller-established, not shown necessary for every safe overlap or accepted as
the complete standalone target domain. Our full ownership/Shadow/no-debt protocol
is a resource-accounting choice, not the language's minimum no-UB condition.
Legal callback effects/all five panic exits stay in safety scope; order/key
preservation belongs to conditional functionality. The owner subsequently
adopted this explicitly delimited [research domain](SORT4-CONTRACT.md#adopted-domain-and-caller-obligations)
after the [authority check](C-VERIFICATION-ARTIFACTS.md#authority-and-separation-precedents).
Caller-precondition proofs are required for composition; no such new proof was
produced by the decision. Organizer clarification is deferred, not a planning
gate; committee acceptance is unconfirmed. **No coverage counts change.**
The old RAPx runner's evidence-dir/processor-scope mismatch is only a static
preparation limitation; it changes none of the historical measured claims.

| Actual target | Established evidence / tool | Remaining obligations |
| --- | --- | --- |
| `StableSmallSortTypeImpl::small_sort` | None | Default / Freeze specialization; arbitrary valid lengths and scratch; sorting contract; generic ownership and comparator behavior |
| `UnstableSmallSortTypeImpl::small_sort` | None | Default / Freeze dispatch; arbitrary valid lengths; sorting contract; generic ownership and comparator behavior |
| `UnstableSmallSortFreezeTypeImpl::small_sort` | None | General / Copy network / fallback choices and stack-size thresholds; arbitrary valid lengths; sorting contract |
| `swap_if_less` | Kani: two bounded i32 harnesses, positions 1/2 in a four-cell initialized allocation; 5/5 covers (37383583285) | Generic values, arbitrary valid indices/allocations, ZST, comparator mutation/panic, all required UB checks |
| `insertion_sort_shift_left` | Kani: direct bounded i32 functional proof, lengths/offsets 1..4, sorted prefix, 7/7 covers (37389298278) | Arbitrary valid lengths, actual outer-loop contracts, independent safety domain, generic types, ZST, ownership and panic restoration |
| `sort4_stable` | Pinned Kani actual body: sorted exact multiset for four arbitrary i32; separate symbolic-key/fixed-ID item stability and complete-item permutation; source unchanged;18/18 covers (37459631500) | Fixed disjoint initialized buffers/pure nonpanicking `<`/Copy layouts only. Generic validity, aliasing/provenance/ZST, ONE ownership, comparator effects and all five panic exits remain open; see refined contract and selected architecture. Concrete overlap diagnostics37466906281 expose the short-comment safety/functionality gap; they add no generic coverage |
| `has_efficient_in_place_swap` | Unchanged VeriFast 26.09: actual unrestricted generic const body, req true, exact size_of(T)<=8 on LP64; VF/refinement pass (37401540878) | Dispatch callers and full-core integration; no other target follows from this pure helper proof |

Only the size helper has an isolated generic proof among these seven targets.
The other six and all three sorting contracts remain incomplete.

## Internal callees and fixtures — separate from public target completion

| Artifact / run | Source and tool boundary | Established / still open |
| --- | --- | --- |
| Bounded `insert_tail` adapter, 37389298278 | Actual std callee via proof-only i32 adapter; pinned Kani | Contract has sorted-prefix precondition, 6/6 covers. Three-call summary harness proves that research caller only; not std's modular pointer loop or unsorted-prefix safety. |
| Generic insertion diagnostic, 37417173472 | Exact-source unrestricted T/F; experimental patched VeriFast | Prefix reaches first FnMut/partial synthetic unwind, lifetime cut/recovery, tail.read, guard and first copy/dst update; fails at compiler Drop. Not a proved callee or completed exit contract. |
| Actual `CopyOnDrop<T>::drop`, 37419989766 | Exact extracted std body; experimental patched VeriFast | Generic T/arbitrary valid len with fractional initialized src, full initialized dst and ONE ownership sequence; exact copied values, VF/refinement pass. Conditional internal body proof only. |
| Local Drop callers, 37435525052 | Actual Drop plus two synthetic one-element callers; experimental `tuple_local_drop` profile | Whole normal caller and FnMut() normal/unwind caller pass with exact destination/ONE ownership/leak checks. All 25 controls and 7 intended negatives pass. Not actual insertion, held &T release or arbitrary FnMut(&T,&T) provenance. |
| Two-cell normal recovery, 37437514808 | Synthetic i32/unrestricted T callers and actual recovery helper; UNCHANGED release 26.09 | Genuine share/init, natural block exit, full initialized current cells/T.own; two positives and three intended negatives pass, refinement passes. No callback/panic/ManuallyDrop or std integration. |
| ManuallyDrop recovery, 37441463201 | Synthetic control; `manually_drop_only`, existing single translator patch on 26.09 | FAILURE: new common recover_single helper blocks all seven callers before intended tests. ManuallyDrop positive also fails RawPtr refinement. No new lifecycle or intended-negative result; earlier unchanged-release baseline remains established. |
| Isolated recover_single, 37448257248 | Synthetic helper, same minimal single-patch profile | Actual conditional full current tmp-cell/T.own recovery body passes,16records and leak-check. Neither MD caller reaches reference or helper call: immutable tmp half storage fails full-borrow precondition. Positive RawPtr refinement still fails; missing-init negative NOT established. |
| Rechecked release recovery, 37448682524 | Same source f0f417c, UNCHANGED26.09 | Both original full-cell positives,3 intended negatives, all5 export/decode/refinement checks pass; optional helpers absent. No new std target completed. |

The old local-cleanup failure37423762729 was superseded by the complete
caller gate37435525052; callers are no longer "unexecuted". Negative refinement
was intentionally not run in that caller gate, so no such result is claimed.
The 25 controls include matcher rejection tests, not 25 proved comparator bodies.

Still open: source-exact first false return/direct panic recovery; genuine
held-reference release/provenance; second comparison; generic gap invariant;
full normal/late-unwind range restoration and actual outer loop.
`COMPARISON_DEBT_POST` is diagnostic, not the final full storage post.
Patched-tool success does not establish verifier soundness or admissibility.
See [resource ledger](INSERTION-RESOURCE-LEDGER.md) and
[borrow applicability gate](BORROW-RECOVERY-DESIGN.md).

## Required UB categories

| Category | Current measured evidence / pinned Kani | Remaining work |
| --- | --- | --- |
| Dangling / misaligned loads and stores | Default bootstrap checks; sort4 actual comparison reference-alignment/invalid-pointer checks and copy source/destination alignment, readable/writeable regions, overlap/null/dead/bounds checks pass in both concrete domains (37459631500) | Arbitrary allocations/types, generic provenance/permissions, ZST and relevant stronger pointer profile |
| Uninitialized reads | Explicit uninitialized i32 read detected in37394356873; positive read2/2covers. Sort4 uses initialized fields by construction; explicit target uninit profile NOT RUN | Apply measured instrumentation to actual targets; generic ownership/raw scratch remains separate |
| Mutating immutable bytes | Write-only passes37394356873; observed write9/volatile-read/assert9 and1/1cover pass37397720683 | Concrete detector gap in this measured profile; cannot claim this required category |
| Invalid values | Invalid bool detected in37394356873; valid bool read2/2covers. Sort4's i32/u8 scalar fields admit every bit pattern; explicit target validity profile NOT RUN | Broader target/type coverage; actual copy_nonoverlapping validity instrumentation is unsupported in37396688760 |

These claims concern Kani pin `152c6a8c875d9886a67e229247b4826d6105ccfd`,
not all versions/tools. API flags in `kani-driver/src/call_single_file.rs:143-152`
and `kani_metadata/src/unstable.rs` describe capabilities, not proof results.

Actual insertion's explicit uninit/valid-value/pointer profile first hit an
instrumentation ICE37395779522 (unsupported Formatter function pointer in the
delayed-uninit pass). The harness-only raw-slice construction resolved that ICE
in37396688760; validity instrumentation then rejected copy_nonoverlapping as
unsupported (pinned check_values.rs:387-393 TODO). All7covers/unwind assertions
passed, but no completed UB safety proof exists. Keep the checks enabled.
The immutable-write control is an independent measured limitation.

## Cross-cutting completion gates

- Lengths: insertion remains bounded to four cells; sort4's four cells are its
  complete arity, but buffers/types/comparator remain restricted. Arbitrary valid
  lengths at the three small_sort entrypoints remain unproved. Bounds16/32 only
  measure performance.
- Types: internal Drop and recovery fixtures have conditional generic results,
  not generic safety of public entrypoints. Interior mutability/non-Freeze,
  invalid bit patterns, large types and ZST model adequacy remain explicit gates.
  The pure size helper accepts unrestricted T without allocation/comparator.
- Comparators: bounded swap allows arbitrary single decisions; insertion
  and sort4 functionality use pure nonpanicking key `<`. Safety must separately cover
  stateful/mutating comparators and panic, without borrowing ordering premises.
- Loops: bounded insertion uses unwind6 with unwinding assertions. An outer
  invariant alone does not remove the inner bound.
- Summaries: actual callee proof at the same source/profile must precede reuse.
  Pinned Kani `stub_verified` still asserts requires under the repository's
  `--no-assert-contracts`; that flag affects ordinary contracted calls, not
  replacement mode (contracts.rs and kani_macros contracts module).
- Submission: approved integrated tools and documented trust boundaries; no
  runtime/signature changes. Tool-semantic expansion, external publication and
  bounty submission each require the owner's separate decision.
