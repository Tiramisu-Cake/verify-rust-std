# Challenge 8 coverage ledger

This table tracks requirements, not inferred coverage from an Actions badge.
All completed experiments use the actual repository std implementation. See
[README run log](README.md#run-log) for checked source SHAs and evidence.
No full Challenge 8 target is complete.

## Safety targets and sorting contracts

| Actual target | Established evidence | Remaining obligations |
| --- | --- | --- |
| `StableSmallSortTypeImpl::small_sort` | None | Default / Freeze specialization; arbitrary valid lengths and scratch; sorting contract; generic ownership and comparator behavior |
| `UnstableSmallSortTypeImpl::small_sort` | None | Default / Freeze dispatch; arbitrary valid lengths; sorting contract; generic ownership and comparator behavior |
| `UnstableSmallSortFreezeTypeImpl::small_sort` | None | General / Copy network / fallback choices and stack-size thresholds; arbitrary valid lengths; sorting contract |
| `swap_if_less` | Two bounded i32 harnesses, fixed positions 1/2 in a four-cell initialized allocation; 5/5 covers (37383583285) | Generic values, arbitrary valid indices/allocations, ZST, comparator mutation/panic, all required UB checks |
| `insertion_sort_shift_left` | Direct bounded i32 functional proof, lengths/offsets 1..4, sorted prefix, 7/7 covers (37389298278) | Arbitrary valid lengths, actual outer-loop contracts, independent safety domain, generic types, ZST, ownership and panic restoration |
| `sort4_stable` | None | Four-read/four-write validity, aliasing contract, generic ownership/comparator behavior, stable sorted permutation |
| `has_efficient_in_place_swap` | None | Generic type/size domain and optimization dispatch obligations |

`insert_tail` is an internal callee. Its verified bounded contract is on a proof-only i32
adapter, with sorted-prefix precondition (37389298278, 6/6 covers). The three-call summary harness proves
that research caller only. It does not establish modular verification of std's
actual pointer loop or safety for unsorted prefixes.

## Required UB categories

| Category | Current configuration / evidence | Remaining work |
| --- | --- | --- |
| Dangling / misaligned loads and stores | Default Kani memory safety checks in bounded bootstrap | Measure alignment and bounds checks on each target; add extra pointer checks where relevant; arbitrary allocations/types |
| Uninitialized reads | Explicit control detected uninitialized i32 read (37394356873), positive read2/2covers | Apply measured instrumentation to actual targets; generic ownership remains separate |
| Mutating immutable bytes | Write-only passes37394356873; observed write9/volatile-read/assert9 and1/1cover pass37397720683: confirmed concrete detector gap | Investigate lowering/check behavior; cannot claim this required category from current Kani configuration |
| Invalid values | Invalid bool control detected (37394356873); valid bool read2/2covers | Apply typed-value checks to target experiments and broader generic types |

API statements above are grounded in Kani pin
`152c6a8c875d9886a67e229247b4826d6105ccfd`:
`kani-driver/src/call_single_file.rs:143-152` and
`kani_metadata/src/unstable.rs`. These flags are capabilities, not proof results.
Do not infer absence of all four UB categories from default checks.

## Cross-cutting domains

- Lengths: completed bootstrap has one four-cell backing allocation; arbitrary
  valid slice lengths remain unproved. Bounds 16/32 are performance milestones.
- Types: completed evidence is i32 only. Non-Copy ownership, Drop, interior
  mutability / non-Freeze, large types, invalid bit patterns and ZST need coverage.
- Comparators: bootstrap includes arbitrary single swap decisions; insertion
  functionality uses pure, nonpanicking i32 `<`. Separate memory safety from
  ordering axioms, stateful comparators and panic/unwind behavior.
- Loop proof: initial insertion uses unwind 6 and retains unwind assertions.
  An outer invariant alone does not eliminate the inner loop bound.
- Summary integrity: prove actual callee at the same source version before use.
  Pinned Kani `stub_verified` still asserts `requires` with the repository's
  `--no-assert-contracts`; that flag disables assertions at ordinary contracted
  calls, not the replacement mode. Verified in
  `kani-compiler/src/kani_middle/transform/contracts.rs` and
  `library/kani_macros/src/sysroot/contracts/mod.rs`.
- Submission: use approved integrated tools; no runtime/signature changes; no
  upstream PR, comments or bounty claim without separate user authorization.

Actual insertion with explicit uninit/valid-value/pointer flags reached a compiler
ICE before verification (37395779522): unsupported Formatter function pointer
in the delayed-uninit pass. This is neither a safety finding nor proof. The
prepared harness-only slice-construction change tests an unreachable formatted
indexing-panic hypothesis under the same domain; target runtime is unchanged.

Raw-slice harness resolves that compiler ICE in37396688760, but validity
instrumentation rejects actual copy_nonoverlapping as unsupported (pinned
check_values.rs:387-393 TODO). All7covers and unwind assertions pass, yet no
completed UB safety proof exists. Retain validity flags; independent immutable
write control also exposes a gap. These are concrete tool limitations.
