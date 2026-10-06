# Challenge 8 coverage ledger

This tracks requirements, not inferred coverage from an Actions badge.
Current stop/phase: [STATUS.md](STATUS.md). Evidence and exact source/tool
identifiers: [experiment log](EXPERIMENT-LOG.md). Distinguish actual-source
proofs, bounded adapters, synthetic fixtures and prefixes of failing proofs.
No complete Challenge 8 solution is established.

The [revised roadmap](PLAN.md) and [sort4 phase](SORT4-PHASE.md) were approved
on 2026-10-06. This is a planning change only: no new proof evidence or covered
UB category is claimed. The next functional domain is four arbitrary i32 keys
in fixed/disjoint buffers, plus a separate tagged-item stability harness.
Generic safety and the four required UB categories remain separate obligations.

## Safety targets and sorting contracts

| Actual target | Established evidence / tool | Remaining obligations |
| --- | --- | --- |
| `StableSmallSortTypeImpl::small_sort` | None | Default / Freeze specialization; arbitrary valid lengths and scratch; sorting contract; generic ownership and comparator behavior |
| `UnstableSmallSortTypeImpl::small_sort` | None | Default / Freeze dispatch; arbitrary valid lengths; sorting contract; generic ownership and comparator behavior |
| `UnstableSmallSortFreezeTypeImpl::small_sort` | None | General / Copy network / fallback choices and stack-size thresholds; arbitrary valid lengths; sorting contract |
| `swap_if_less` | Kani: two bounded i32 harnesses, positions 1/2 in a four-cell initialized allocation; 5/5 covers (37383583285) | Generic values, arbitrary valid indices/allocations, ZST, comparator mutation/panic, all required UB checks |
| `insertion_sort_shift_left` | Kani: direct bounded i32 functional proof, lengths/offsets 1..4, sorted prefix, 7/7 covers (37389298278) | Arbitrary valid lengths, actual outer-loop contracts, independent safety domain, generic types, ZST, ownership and panic restoration |
| `sort4_stable` | None; approved phase, not yet implemented/run | Four-read/four-write validity, aliasing contract, generic ownership/comparator behavior, stable sorted permutation |
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
| Dangling / misaligned loads and stores | Default memory safety checks in bounded bootstrap | Measure alignment/bounds checks on each target; arbitrary allocations/types and relevant pointer checks |
| Uninitialized reads | Explicit uninitialized i32 read detected in37394356873; positive read2/2covers | Apply measured instrumentation to actual targets; generic ownership remains separate |
| Mutating immutable bytes | Write-only passes37394356873; observed write9/volatile-read/assert9 and1/1cover pass37397720683 | Concrete detector gap in this measured profile; cannot claim this required category |
| Invalid values | Invalid bool detected in37394356873; valid bool read2/2covers | Broader target/type coverage; actual copy_nonoverlapping validity instrumentation is unsupported in37396688760 |

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

- Lengths: memory-touching public-target successes are bounded to four cells;
  arbitrary valid lengths remain unproved. Bounds 16/32 only measure performance.
- Types: internal Drop and recovery fixtures have conditional generic results,
  not generic safety of public entrypoints. Interior mutability/non-Freeze,
  invalid bit patterns, large types and ZST model adequacy remain explicit gates.
  The pure size helper accepts unrestricted T without allocation/comparator.
- Comparators: bounded swap allows arbitrary single decisions; insertion
  functionality uses pure nonpanicking i32 `<`. Safety must separately cover
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
