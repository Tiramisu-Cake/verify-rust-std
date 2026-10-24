# Challenge 8 "SmallSort": complete record of organizer statements

Compiled: 2026-10-24. Repository: github.com/model-checking/verify-rust-std.

## 0. Method, limits, and how to read this file

- **Access method.** Direct `curl`/`gh` access to github.com, api.github.com and raw.githubusercontent.com was blocked by the sandbox egress proxy (HTTP 403, verified). Every item was fetched through the WebFetch tool from api.github.com JSON endpoints or raw.githubusercontent.com. Some items were re-fetched with narrower prompts to get near-verbatim wording.
- **Quoting caveat.** WebFetch passes content through a summarizing model that refuses quotes longer than about 125 characters. So text shown in "quotes" is verbatim but split into fragments, usually under 20 words each. Text without quotes is a faithful paraphrase that keeps every demand, number, type and threshold the tool reported. **Before citing any sentence in a formal decision, open the linked URL and check the wording against the original.**
- **"Organizers"** means the committee in `.github/pull_requests.toml` (celinval, rahulku, pnkfelix, feliperodri, remi-delmas-3000, tautschnig, patricklam, ranjitjhala, carolynzech, HuStmpHrrr, jswrenn, havelund, jorajeev, rajath-mk, thanhnguyen-aws, btj, rafaelsamenezes, lucasccordeiro, dkcumming, DiuDiu777), plus qinheping (challenge author) and zhassan-aws.
- **Year tags.** Every organizer statement carries one of **[2024]**, **[2025]** or **[2026]**.

### Corpus checked (complete list)

| Item | Body | Issue comments | Reviews | Inline review comments | Organizer content found |
|---|---|---|---|---|---|
| Issue #56 (tracking) | yes | 5 (fetched incl. `since=2026-10-01`) | n/a | n/a | qinheping x2 (2025) |
| Issue #56 timeline | 16 events (paged 5 per page) | | | | rename by feliperodri (2024) |
| PR #57 (challenge proposal) | n/a | 0 | 2 | 1 | celinval, tautschnig (2024) |
| PR #234 (ShoyuVanilla) | yes | 5 | 0 | 0 | tautschnig x2, rahulku x1 (2025), process only |
| PR #247 (challenge edits) | n/a | 0 | 11 | 21 | tautschnig whitespace question on 0008 file (2025) |
| PR #576 (Samuelsills) | yes | 1 | 3 | 2 (Copilot bot) | feliperodri x2 reviews (2026) |
| PR #640 (sankalpsthakur) | yes | 1 | 0 | 0 | none (withdrawn unreviewed) |
| PR #678 (samiam713) | yes | 0 | 1 | 0 | feliperodri x1 review (2026) |
| PR #694 (kasimte) | yes | 0 | 0 | 0 | label only (feliperodri, 2026-09-24) |
| PR #701 (v3risec) | yes | 0 | 0 | 0 | label only (feliperodri, 2026-09-30) |
| Search `smallsort` | 12 results | | | | nothing new beyond the above |
| Search `"challenge 8"` | 26 total, 14 visible, page 2 came back empty | | | | Ch8 items: #56, #576, #640, #678, #694, #701 only |
| Search `sort13_optimal` | 3 results (#56, #576, #678) | | | | |
| History of `0008-smallsort.md` | 5 commits | | | | see section 1.2 |
| General rules, README, PR template, `copilot-instructions.md`, `kani.yml`, `run-kani.sh` | yes | | | | general policy (section 1.3) |
| rust-lang/rust#135984 | status only | | | | |

**Unreachable:** `CONTRIBUTING.md` (client error). Of the 26 "challenge 8" search hits, 12 never displayed, but all visible results and the `smallsort` / `sort13_optimal` searches agree on the same Ch8 set.

---

## 1. Challenge text and repository policy (primary sources)

### 1.1 `doc/src/challenges/0008-smallsort.md` at `main` (fetched 2026-10-24)

**Metadata**
- Status: Open.
- Tracking issue: #56.
- Start date: 2024/08/17.
- Reward: 10,000 USD.
- End date: none. It was removed on 2026-08-28; the previous value was 2025/04/10.
- Contributors: none listed.

The README table also lists Ch8 as "Open", "10,000 USD", with an empty Proof column.

**Goal (verbatim fragments)**
- The traits `StableSmallSortTypeImpl`, `UnstableSmallSortTypeImpl` and `UnstableSmallSortFreezeTypeImpl` in the `smallsort` module "are the sorting algorithms with optimized implementations for slices with small lengths." (wording as changed in #247, 2025-03).
- "In this challenge, the goal is to, first prove the memory safety of the public functions in the `smallsort` module, and, second, write contracts for them to show that the sorting algorithms actually sort the slices."

**Assumptions section:** none.

**Success criteria, part A: prove absence of undefined behavior for these 7 functions**
1. `<T as slice::sort::shared::smallsort::StableSmallSortTypeImpl>::small_sort`
2. `<T as slice::sort::shared::smallsort::UnstableSmallSortTypeImpl>::small_sort`
3. `<T as slice::sort::shared::smallsort::UnstableSmallSortFreezeTypeImpl>::small_sort`
4. `slice::sort::shared::smallsort::swap_if_less`
5. `slice::sort::shared::smallsort::insertion_sort_shift_left`
6. `slice::sort::shared::smallsort::sort4_stable`
7. `slice::sort::shared::smallsort::has_efficient_in_place_swap`

**Success criteria, part B: write contracts showing they sort the slices**, for the three `small_sort` implementations (items 1–3) only.

**Domain sentence:** the memory safety and contracts "must be verified for all possible slices with arbitrary valid length."

**Note** (added at tautschnig's suggestion in #57): "Note that most of the functions listed above call functions that contain loops." It continues that function contracts and loop contracts of those callee functions may be required.

**UB list.** All proofs must automatically ensure the absence of the following, "in addition to any properties called out as `SAFETY` comments in the source code". The list links to the Rust Reference "behavior considered undefined" at a pinned commit.
- Accessing (loading from or storing to) a place that is dangling or based on a misaligned pointer.
- Reading from uninitialized memory.
- Mutating immutable bytes.
- Producing an invalid value.

**Closing note:** all solutions must satisfy the criteria in the challenge book (`../general-rules.md`).

**Not mentioned anywhere in the challenge text:**
- the comparator `is_less` or any ordering;
- bounds on `T`, or which types to use;
- panics or unwinding;
- permutation or multiset preservation;
- stability (beyond the trait names);
- Freeze (beyond the trait name);
- ZSTs;
- `sort13_optimal`, `bidirectional_merge`, `small_sort_general`, `small_sort_network`;
- thresholds 16 and 32;
- CI time;
- tools;
- partial solutions;
- primitive-type restrictions.

### 1.2 History of the challenge file

| Date | Commit / PR | Author | Effect on Ch8 text |
|---|---|---|---|
| 2024-08-18 → 2024-08-20 | PR #57 "Challenge proposal: SmallSort" | qinheping | Original text. Approved by celinval on 2024-08-19 ("That's great! Thanks") and tautschnig on 2024-08-20 (no body). tautschnig's inline suggestion on 2024-08-20 added the loops note: "Note that most of the functions listed above call functions that contain loops." ([r1723291382](https://github.com/model-checking/verify-rust-std/pull/57#discussion_r1723291382)) |
| 2024-08-20 | 62e241afb3, #60 | carolynzech | Added the `.md` extension. |
| 2024-09-05 | Issue #56 rename | feliperodri | Renamed from "Tracking issue for verification of SmallSort" to "Challenge 8: Contracts for `SmallSort`". |
| 2024-09-07 | c6cecce731, #79 | feliperodri | Fixed challenge numbering. |
| 2024-11-22 | e2db4357df, #176 | celinval | Added reward information and postponed end dates. |
| 2025-03-21 | 00169b76e9, #247 | thanhnguyen-aws | Reworded the Goal sentence only ("sorting algorithms optimized for slices with small lengths" became "...with optimized implementations for slices with small lengths"). No change to criteria. tautschnig asked on 2025-03-18 why the paragraph's whitespace changed ([r2000639267](https://github.com/model-checking/verify-rust-std/pull/247#discussion_r2000639267)). |
| 2026-08-28 | e26a070a3b, #629 | feliperodri | Removed the "End date: 2025/04/10" line, because challenges no longer have fixed deadlines. Same PR added KMIR to the accepted tools. |

**Conclusion:** the success criteria have never been amended since August 2024. All later clarifications live only in issue and PR comments.

### 1.3 Repository-wide policy relevant to Ch8

**`doc/src/general-rules.md` (current `main`)**
- Solution requirements:
  - "The contribution must be automated and should be checked and pass as part of the PR checks."
  - "The solution should run as part of the CI."
  - "All tools used by the solution must be in the list of accepted tools".
  - "The solution cannot impact the runtime logic of the standard library unless the change is proposed and incorporated" upstream.
  - Contributors must have the rights to submit, and all contributors must be mentioned.
  - "Any exception to these requirements will only be considered if it is specified as part of the acceptance criteria" of the challenge.
- Acceptance:
  - "Acceptance will be based on a review by a committee."
  - "Each contribution will be reviewed on a first come, first served basis."
  - Merge needs approvals from at least two committee members.
- Committee review criteria (in the Committee Applications section):
  - "Does the pull request implement a solution that respects/meets the success criteria of the challenge?"
  - "Do the contracts and harnesses incorporate the safety conditions stated in the documentation" (source comments and the official std docs).
  - "Note that we currently focus on safety verification."
  - "Pre- and post-conditions towards functional correctness are acceptable as long as they do not negatively impact verification of safety, such as over-constraining input values or causing excessive verification run time."
  - Code must be "of adequate quality, idiomatic, and stands a chance to be accepted into the standard library".
- Tools: "Solutions must be automated using one of the tools previously approved". README lists "Flux, GOTO Transcoder (ESBMC), Kani, KMIR, and VeriFast" (KMIR added 2026-08-28).
- **Topics general-rules does not address:** reward splitting, partial solutions, payment, eligibility, AI use, stubs or assumptions, panics, CI time limits.

**`.github/copilot-instructions.md`**
- Added by feliperodri on 2026-03-31 (#581). These are organizer-authored review rules.
- Challenge solutions get the "strictest review". The PR must meet "every" success criterion, and partial solutions should be flagged.
- Vacuity: proofs must not pass trivially, e.g. through an "unsatisfiable precondition or an empty harness body".
- Assumptions: every `kani::assume` / `requires` must be justified by the safety contract or API invariants. Over-constraining is flagged.
- Contracts must match the `# Safety` docs.
- Harnesses must cover "meaningful input ranges", not trivial or degenerate cases.
- CI must actually run the new proofs.
- Verification code must be gated behind `#[cfg(kani)]` (or another tool-specific cfg). No new public API.
- Red flags:
  - harnesses with no or only trivial assertions;
  - `kani::assume(false)`;
  - assumptions stricter than the docs;
  - contracts that do not match `# Safety`;
  - ungated code;
  - runtime changes;
  - unapproved tools;
  - oversized PRs.
- Approved tools listed there: Kani, VeriFast, Flux, ESBMC. This list is older than the KMIR addition.
- No T-codes (for example "T7") are defined in this file.

**PR template:** asks for a description, a check against the book's rules, "Resolves #ISSUE-NUMBER", and the Apache-2.0/MIT licence confirmation. There is **no AI-disclosure requirement**.

**CI configuration** (configuration only, not an organizer statement):
- `kani.yml`:
  - `--harness-timeout 10m` on the autoharness step;
  - the ubuntu runners are commented as "4-core/16 GB runners" that can "get OOM-killed";
  - `KANI_JOBS=2` on ubuntu;
  - the `check-kani-on-std` job is split across 4 partitions;
  - matrix of ubuntu-latest and macos-latest.
- `scripts/run-kani.sh`:
  - `-Z function-contracts -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing`;
  - `--no-assert-contracts`;
  - `--cbmc-args --object-bits 12`;
  - no per-harness timeout of its own.

PR authors #678 and #701 both describe a "10-minute per-harness" CI cap that they hit.

---

## 2. Chronological record of every organizer statement

### 2024

**O-1. tautschnig, 2024-08-20, PR #57 inline comment**
- URL: https://github.com/model-checking/verify-rust-std/pull/57#discussion_r1723291382
- Context: review of qinheping's challenge proposal.
- Content: suggested adding the sentence "Note that most of the functions listed above call functions that contain loops." This is now in the challenge text.

**O-2. celinval, 2024-08-19, PR #57 review, APPROVED**
- Content: "That's great! Thanks". No requirements.
- tautschnig also APPROVED on 2024-08-20 with no body.

**O-3. feliperodri, 2024-09-05, issue #56 rename**
- Content: renamed the issue to "Challenge 8: Contracts for `SmallSort`". This signals that contracts are the headline deliverable.

**O-4. qinheping, 2024-08-17, issue #56 body**
- URL: https://github.com/model-checking/verify-rust-std/issues/56
- Content: "Link to PR: #57" and a link to the challenge file. No requirements.

### 2025

**Context for O-5 and O-6: question from BusyBeaver-42 (non-organizer), 2025-01-09, issue #56**
- URL: https://github.com/model-checking/verify-rust-std/issues/56#issuecomment-2580563254 (edited 2025-01-24)
- Q1, missing safety requirement:
  - "I believe `merge_down` is missing a requirement in the `SAFETY` comment."
  - `dst.sub(1)` is not guaranteed to stay "within the same allocated object". This is harmless in practice because the function is private and the call site is fine.
  - Opened upstream as rust-lang/rust#135984.
- Q2, invalid values and a separate tool:
  - Example: input `[1, 2, 3]` becoming output `[1, 1, 1]` is sorted but creates an "invalid value". This is no safety issue for `Copy` types but "could become one for non-`Copy` types".
  - Checking with Kani that the input multiset equals the output multiset "is extremely slow". "For example, `sort4_stable` already takes approximately 6 minutes to verify."
  - Asks: "Can the absence of "invalid values" be verified with a separate tool?"
- Q3, how arbitrary `is_less` must be:
  - For safety, `is_less` is user-provided, so it must be "a function that returns a random boolean (`kani::any()`)".
  - For correctness, is "default ordering of integers" sufficient, or "a custom type with 32 distinct values, allowing for testing of any weak total ordering"? The latter is "likely to perform poorly".
  - "Additionally, what types `T` should be tested?"
- Q4, memory and runtime limits:
  - Uses `stub_verified` on `sort13_optimal` because the analyzed code "becomes too large when verifying the sorting methods".
  - Verifying `sort13_optimal` itself "requires 50 GB of memory and takes 40 minutes (38 GB of this is swap memory...)". Links model-checking/kani#3797.

**O-5. qinheping, 2025-01-24T02:27:43Z, issue #56. Key 2025 clarification.**
- URL: https://github.com/model-checking/verify-rust-std/issues/56#issuecomment-2611410906
- On Q1: "The safety comments should be updated in the upstream if the proof shows that the current comments is actually not enough."
- On Q2: "Yes, other tools are welcome." This was answered as a tools question. It is **not** an answer on whether a permutation check is required.
- On Q3, verbatim in three fragments:
  - "The ultimate goal is to prove the correctness for arbitrary types and arbitrary ordering."
  - "However, we understand that model arbitrary ordering itself is very challenging."
  - "So proofs for primitive types with default ordering will be considered as a solid solutions."
- **Not answered:** "what types `T` should be tested?" beyond "primitive types". Also not answered: whether the `kani::any()` comparator is required for the safety part (BusyBeaver asserted it; qinheping did not contradict it).

**O-6. qinheping, 2025-01-24T18:07:20Z, issue #56**
- URL: https://github.com/model-checking/verify-rust-std/issues/56#issuecomment-2613110847
- On Q4, verbatim fragments:
  - "We expect to run all proof on CI."
  - "So ideally the running time of a single proof should be less than ~2 minutes on a GitHub standard runner."
  - "However, if the proof is running into the limitation of Kani/CBMC, we suggest you to open a PR with the proof so that we could merge it once we have made performance improvements that get the CI time down to a reasonable amount."
- **Not answered:** whether `stub_verified` on `sort13_optimal` is acceptable. qinheping did not address the stub question explicitly.

**O-7. tautschnig, 2025-03-13T13:26:18Z, PR #234 (ShoyuVanilla, draft)**
- URL: https://github.com/model-checking/verify-rust-std/pull/234#issuecomment-2721256452
- Content: "Would you be able to revisit this PR?"
- ShoyuVanilla replied that local attempts mostly ran out of memory or took tens of minutes, and asked "Would it be better to close this PR for now?"

**O-8. tautschnig, 2025-03-13T13:34:23Z, PR #234**
- URL: https://github.com/model-checking/verify-rust-std/pull/234#issuecomment-2721280330
- Content: "Entirely up to you how you deal with this PR." He only wanted to confirm it was not abandoned.

**O-9. tautschnig, 2025-03-18, PR #247 inline comment on `0008-smallsort.md`**
- URL: https://github.com/model-checking/verify-rust-std/pull/247#discussion_r2000639267
- Content: asks why the whitespace of the goal paragraph was changed. Editorial only.

**O-10. rahulku, 2025-04-29T17:19:58Z, PR #234**
- URL: https://github.com/model-checking/verify-rust-std/pull/234#issuecomment-2839649268
- Content: "any chance we can still push this through?"
- ShoyuVanilla closed the PR on 2025-04-30. He needed "couple of months to study the related topics and VeriFast".
- This is the only organizer signal of interest in merging a partial or draft Ch8 effort. No requirements were stated.

### 2026

**O-11. feliperodri, 2026-03-29 / 2026-03-31 / 2026-04-01, PR #576 timeline**
- Labelled "Challenge" on 2026-03-29.
- Requested a Copilot review on 2026-03-31. The Copilot bot's inline comments are not organizer statements, but they flagged the fixed `[i32; 4]` size and suggested `0..=small_sort_threshold()` or sizes 0, 1, 2, 3, 4, 8, 16, 32.
- Assigned the PR to Samuelsills on 2026-04-01.

**O-12. feliperodri, 2026-08-16T22:04:28Z, PR #576 review, CHANGES_REQUESTED. Key 2026 statement #1.**
- URL: https://github.com/model-checking/verify-rust-std/pull/576#pullrequestreview-4947412389
- Responds to Samuelsills' PR: 9 Kani harnesses, all at length 4 on `i32`, sortedness via an `is_sorted` helper, plus `#[safety::requires]` on `insert_tail` and `insertion_sort_shift_left`.
- Verdict: harnesses "technically **sound**".
  - Found no cfg-swap vacuity, no `#[cfg(not(kani))]` body gating, no trivial invariants, and no assume-the-conclusion. The assumes present are legitimate.
  - Credits correct `#[cfg(kani)]` wiring. All 7 UB-target functions have at least one harness. The `has_efficient_in_place_swap` and `swap_if_less` proofs are fine.
- **Blocking 1: no permutation check.**
  - The five correctness harnesses are `verify_sort4_stable`, `verify_insertion_sort_shift_left`, `verify_stable_small_sort`, `verify_unstable_small_sort` and `verify_unstable_freeze_small_sort` (smallsort.rs:928–976). They assert only `is_sorted`, which checks monotonicity (878–892). A constant-overwriting implementation would pass.
  - Verbatim: "Sorting correctness requires **both** "output is sorted" **and** "output is a permutation (multiset) of the input."" He asks for a multiset or count-based comparison.
- **Blocking 2.** Heading, verbatim: "Blocking 2 — Fixed length 4 only; challenge requires "arbitrary valid length"".
  - Verbatim fragments: "SmallSort is inherently bounded (thresholds `SMALL_SORT_FALLBACK_THRESHOLD = 16`, `SMALL_SORT_GENERAL_THRESHOLD = SMALL_SORT_NETWORK_THRESHOLD = 32` at `smallsort.rs:176-194`), so bounded harnesses are the right approach — but pinning to a single length of 4 leaves most of the dispatch tree and all the loop-bearing sort code unverified:"
  - Gaps at length 4:
    - `verify_stable_small_sort` takes the `len < 8` branch (260–265), so `sort4_stable`/`sort8_stable` in the general path and the `presorted_len` network branches are never exercised;
    - `verify_unstable_freeze_small_sort` never reaches the `sort8`/`sort12` network regions (`region.len() >= 9/13`, 341–351);
    - the bidirectional merge and the `insert_tail` loop run over only 4 elements.
  - Fix, verbatim fragments: "cover the full valid range up to each variant's `small_sort_threshold()`"; "either loop over sizes 0..=32 (with matching `kani::unwind`) or add representative harnesses at the boundary sizes" (8, 9, 13, 16, 32).
- **Non-blocking items:**
  - Contracts without harnesses: the `#[safety::requires]` on `insert_tail` (line 544) and on `insertion_sort_shift_left` (583) have no `proof_for_contract`. "In a plain `#[kani::proof]` the callee's `requires` is neither assumed nor asserted, so these are currently documentation only."
  - `insertion_sort_shift_left` already enforces its precondition at runtime via `intrinsics::abort()` (590–591).
  - `verify_swap_if_less` (914–923) assumes `a < 4 && b < 4`, which allows `a == b` and makes the post-assertion trivial. He suggests `assume(a != b)`.
  - Types, verbatim: "Correctness is only checked for `i32`. Acceptable for a bounded proof, but worth noting the challenge scope is generic `T`."
- Bottom line: "Sound but incomplete." Blocking 1 and 2 must be fixed before approval.

**O-13. feliperodri, 2026-09-12T21:01:18Z, PR #576 second review, CHANGES_REQUESTED. Key 2026 statement #2.**
- URL: https://github.com/model-checking/verify-rust-std/pull/576#pullrequestreview-5188053006
- Context: re-review with no new commits since March.
- Opening, verbatim: "Reviewed Challenge 8 with our vacuity tooling" … "Requesting changes — doesn't meet criteria:"
- (1) "Fails unbounded":
  - "every harness uses concrete length 4, monomorphized to i32."
  - Ch8 mandates "verified for all possible slices with arbitrary valid length."
  - `#[kani::unwind(6)]` is "sound" only because the length is concrete.
- (2) "0/3 sorting-correctness contracts":
  - "The PR body claims correctness contracts + `proof_for_contract`; the diff has neither."
  - Sortedness is "asserted inside plain `#[kani::proof]`" via a local `is_sorted` helper, not encoded as `#[safety::ensures]`.
- (3) "Two T7 violations — decorative contracts:"
  - `#[safety::requires(begin < tail)]` on `insert_tail` has no `proof_for_contract(insert_tail)`.
  - `#[safety::requires(offset > 0 && offset <= v.len())]` on `insertion_sort_shift_left` is only exercised in a plain `#[kani::proof]`, so it is unchecked, and trivially met because `offset=1` and `v.len()=4` are hardcoded.
  - "T7" is an internal code of the reviewer's tooling. It is not defined in any repo document found.
- (4) Type coverage:
  - `has_efficient_in_place_swap` is tested only for u8, u64, u128.
  - Verbatim: "T-generic behavior for u16/[u8;9]/ZSTs/!Freeze not covered."
- Unexercised branches: they are "entirely unexercised at length 4". Named: `small_sort_general`, `small_sort_network`, `sort8_stable`, `sort13_optimal`, and the "32/17 thresholds".
  - The 17 probably refers to `len >= 17` / `SMALL_SORT_FALLBACK_THRESHOLD + 1` style checks; the review does not explain it.
- Needed to close Ch8, verbatim fragments:
  - "To close Ch8 this needs symbolic-length harnesses over T"
  - "(primitive-mono per Ch8 doc if allowed — but here it's not; challenge says arbitrary length is required)"
  - "real `#[ensures]` sortedness contracts on the 3 small_sort impls with matching `proof_for_contract`".
- Note: the Ch8 doc itself does not say primitive-monomorphic proofs are allowed. That permission comes from qinheping in #56 (O-5, 2025).

**O-14. feliperodri, 2026-09-12T21:01:33Z, PR #678: labelled "Challenge".**

**O-15. feliperodri, 2026-09-13T00:45:55Z, PR #678 review, CHANGES_REQUESTED. Key 2026 statement #3, and the most recent substantive organizer statement.**
- URL: https://github.com/model-checking/verify-rust-std/pull/678#pullrequestreview-5188832758
- Context: samiam713's self-declared partial PR. 46 harnesses; sortedness plus multiset permutation; fully symbolic contents; strict `a < b` comparator; no stubs; correctness in harnesses.
- Opening, verbatim: "Thanks @samiam713. Reviewed against Challenge 8."; "This is substantially stronger than the prior Ch8 solution (#576)".
- Credits:
  - "all 7 no-UB fns exercised on the real trait impls/callees (no body swap)".
  - All 3 `small_sort` impls have correctness oracles: `assert_sorted` plus an `assert_permutation` multiset check using per-value occurrence counts.
  - Types, verbatim: "across i32, Cell<i32> (non-Freeze), NonCopyI32 (Freeze non-Copy), u128, [u64;11], u8."
  - Contents fully symbolic, no cfg or assume tricks, no decorative contracts.
- Changes requested because the solution is partial:
  1. **Bounded, not arbitrary-length.**
     - Length caps around 8–9: i32 stable/unstable at 0–8; Cell at {0, 1, 2, 3, 7}; u128 at length 2; large types at 2–3.
     - Coverage must reach the thresholds, verbatim: "up to the fallback threshold 16 and general/network threshold 32."
  2. **Missing or reduced coverage.**
     - "sort13_optimal is not verified at all (neither composed nor direct)".
     - `bidirectional_merge` is verified only at tiny composed lengths.
     - The `sort9_optimal`/network band is verified only at u8 width. Verbatim: "sound reduction via zero-one principle, but a reduction."
  3. **Contracts.**
     - "Correctness is expressed as in-harness oracles, not #[ensures]/proof_for_contract."
     - He suggests real contracts on the 3 impls, matching the challenge's "write contracts" requirement and being reusable.
- Priority, verbatim: "Between the open Ch8 solutions we're prioritizing this one (it strictly dominates #576)."
- Closing, verbatim: "To close Ch8 it needs coverage up to the real length thresholds and, ideally, the correctness expressed as contracts."
- **Unanswered from the #678 body:** "whether and how a partial result counts toward Challenge 8", and whether the committee wants the frontier harnesses extended on larger hardware.

**O-16. feliperodri, 2026-09-24, PR #694: labelled "Challenge". No review as of 2026-10-24.**

**O-17. feliperodri, 2026-09-30, PR #701: labelled "Challenge". No review as of 2026-10-24.**

**Silence (as of 2026-10-24):** organizers have not answered any of the following.
- Issue #56: TheodorNEngoy (2026-09-05) and Tiramisu-Cake (2026-10-23).
- PR #678 body questions.
- PR #694 and PR #701: no reviews.
- PR #640: withdrawn 2026-08-26 citing "no maintainer signal".

---

## 3. Non-organizer statements: claims, limits, and open questions

### PR #234, ShoyuVanilla (2024-12-27 → closed 2025-04-30, draft)
- Body: "Towards #56". About 387 lines, Kani.
- Limits: approaches ran out of memory or took tens of minutes ("Kani lacks some features"). The author considered VeriFast.
- No organizer technical feedback was given.

### Issue #56, BusyBeaver-42 (2025-01-09)
- See the context box before O-5.
- Answered: safety comments, tools, types and ordering, CI time.
- **Left unanswered:**
  - whether `stub_verified` of `sort13_optimal` is acceptable;
  - which types `T` beyond "primitive";
  - whether a `kani::any()` comparator is mandatory for the safety part;
  - the 32-distinct-value weak-order idea.
- Upstream rust-lang/rust#135984 ("Missing Safety Guarantee in `merge_down` Function Documentation (`smallsort` Module)"): opened by BusyBeaver-42 on 2025-01-24, labels A-docs and T-libs, **still open** as of 2026-10-24.

### PR #576, Samuelsills (opened 2026-03-28, open, CHANGES_REQUESTED twice)
- Claims "Resolves #56":
  - all 7 functions memory-safe;
  - 3 `small_sort` variants "proven to produce sorted output (arr[i] <= arr[i+1] for all i)".
- Coverage report (2026-03-29):
  - 9 harnesses, array size 4, `i32`;
  - `#[safety::requires(begin < tail)]` on `insert_tail`;
  - `#[safety::requires(offset > 0 && offset <= v.len())]` on `insertion_sort_shift_left`;
  - the four UB categories are "checked automatically".
- Did not respond to either review.

### PR #640, sankalpsthakur (2026-08-20 → withdrawn 2026-08-26)
- Body:
  - "Kani safety contracts and proof harnesses";
  - "Runtime stdlib logic is unchanged";
  - "Fixes #56";
  - AI disclosure ("Grok and/or Codex agent-assisted editing", reviewed by a human).
- Withdrawn: "Withdrawing this; no maintainer signal and we are cutting the queue."
- No organizer comment, so the AI disclosure drew no response.

### Issue #56, TheodorNEngoy (2026-09-05). UNANSWERED.
- URL: https://github.com/model-checking/verify-rust-std/issues/56#issuecomment-5551156885
- Q1: does the USD 10,000 award remain available to a new contributor with a complete accepted solution, given existing work? "How would prior or overlapping contributions affect award allocation?"
- Q2: "would complete i32 coverage for every length up to each SmallSort variant's threshold, including sortedness and multiset preservation, satisfy the intended sorting-correctness scope?" Also: "For insertion_sort_shift_left as a standalone helper, is proof beyond those thresholds required?"
- Q3: "Are human-reviewed, AI-assisted contributions eligible", and is there a published eligibility and payment process for an individual in Norway?

### PR #678, samiam713 (2026-09-07, open, "partial")
- Claims:
  - "This is a partial contribution — it does not close Challenge 8";
  - 46 Kani harnesses, all in `#[cfg(kani)] mod verify`, zero production lines changed.
- Properties and techniques:
  - sortedness plus multiset permutation;
  - `kani::any()` contents;
  - comparator is a fixed strict order `a < b`;
  - stability explicitly **not** asserted;
  - no stubs; assumes only for documented preconditions;
  - unwind `len + 2` with unwinding assertions on.
- Why no contracts: "function-contract syntax cannot currently express the permutation property for these specialized methods".
- Coverage tiers:
  - default `small_sort` at lengths 0–3 and 7 with `Cell<i32>`;
  - `insertion_sort_shift_left` at 1–4 with symbolic offset;
  - `small_sort_general_with_scratch` with i32 at 0–8, plus u128 and non-Copy types;
  - `small_sort_network` with i32 at 0–8 and u8 at 9;
  - per-callee: `sort4_stable`, `sort8_stable` (len 8), `swap_if_less`, `sort9_optimal` (8-bit elements).
- Gaps:
  - `sort13_optimal` and `bidirectional_merge` at lengths ≥16 "resisted even direct verification";
  - adversarial or panicking comparator not modeled.
- Tooling: Kani 0.67.0 at `d4df833c`, `nightly-2025-11-25`, cadical and kissat solver pins.
- Timings: i32 network len 9 about 1030 s; stable general i32 len 32 over 3600 s (timeout); `sort8_stable` 513 s.
- CI: four harnesses timed out against the "10-minute per-harness cap", leading to the 48 → 46 cut and per-harness solver pins.
- AI: "substantial AI assistance (Claude, Anthropic)", with a Co-authored-by trailer.
- **Questions left unanswered by the 2026-09-13 review:**
  - whether and how a partial result counts;
  - whether the committee wants the frontier harnesses extended on bigger hardware.

### PR #694, kasimte (2026-09-23, open, no review)
- Claims:
  - 25 harnesses (one self-tests the oracles) plus 2 verified contracts (`swap_if_less`, `insertion_sort_shift_left` with `#[safety::requires]` + `kani::modifies` + `proof_for_contract`);
  - `has_efficient_in_place_swap` over 8 width classes;
  - each `kani::assume` paired with a `kani::cover` witness (25 covers);
  - fallback route proven with symbolic length [1, 16];
  - sorted plus permutation at the "deepest completing length per family", with sort13 split into separate sorted and permutation harnesses at length 13 (permutation on a small value domain).
- Limits:
  - length 32 on the general and network routes does not complete in 20 minutes (18 does);
  - wide elements only at shorter lengths;
  - contracts on the three impls fail to compile: `E0520` (specialization) and `E0599` (`old()` needs `T: Clone`);
  - `-Z uninit-checks` is unusable on this module.
- Cites the #56 guidance (solver-limit PRs; primitive default ordering is "solid").
- Commits after opening:
  - 2026-10-12: corrected the sort13 permutation comment and added a "decoupled bounded-domain harness" for sort13 permutation;
  - 2026-10-21: merged main.
- No AI disclosure.

### PR #701, v3risec (2026-09-29, open, no review)
- Claims end-to-end harnesses on the real implementation "without introducing unverified stubs or path pruning":
  - sortedness "under a valid ordering";
  - multiset preservation;
  - symbolic lengths up to each specialization's threshold.
- Stable small sort:
  - non-Freeze fallback ≤16;
  - Freeze general ≤32;
  - 8-element presort for `size_of::<T>() <= 16`, 4-element presort above 16;
  - non-Freeze split into safety, sorted and permutation proofs.
- Unstable small sort: non-Freeze fallback; Freeze+Copy network; Freeze+Copy general (small and large); Freeze+Copy oversized fallback; Freeze+!Copy general; Freeze+!Copy oversized fallback. Freeze impl covered equivalently.
- Helpers:
  - `swap_if_less` and `sort4_stable` with safety contracts plus `proof_for_contract`;
  - `insertion_sort_shift_left` with symbolic length and offset over the range current callers use;
  - `has_efficient_in_place_swap` on ZST, small, large and interior-mutable types.
- Limits:
  - some full-domain proofs exceed the "current 10-minute per-harness verification budget";
  - len-32 Freeze general and network paths make one big SAT instance;
  - a stable-Freeze full-domain run took more than 20 minutes locally;
  - sorting properties are harness assertions because of "specialization and generic old-state handling in the pinned toolchain";
  - "No `assume(false)` path pruning or unverified behavioral stubs are used."
- "Resolves #56". No AI disclosure.

### Issue #56, Tiramisu-Cake (2026-10-23T21:20:35Z). UNANSWERED (posted the day before this record).
- URL: https://github.com/model-checking/verify-rust-std/issues/56#issuecomment-6374966537
- Restates its reading of #678's review: "length means up to the specialization thresholds", namely "16 for the fallback path, 32 for the general/network paths", and "sort13_optimal, bidirectional_merge and contract-form correctness are expected."
- Q1, element types: is coverage by "representative element types that exercises every specialization (Freeze / non-Freeze, Copy / non-Copy, size_of <= 16 and > 16, ZST, interior mutability)" sufficient, or "is a proof that is generic over T" "required for the memory-safety part?"
- Q2, comparator: for no-UB, "is it sufficient to verify with a pure, total, non-panicking is_less, or must the proofs also cover comparators that may panic or keep state (the CopyOnDrop-style unwind recovery paths in insert_tail / small_sort_general)?" Also: "If panicking comparators are required, is a proof of "no UB on unwind" enough, without any functional guarantee after a panic?"

### Other
- runtimeverification/mir-semantics PR #1033, "Re-execution: Challenge 8: Contracts for SmallSort" (Stevengre, cross-referenced 2026-04-09, closed). External KMIR work; no organizer statement in this repo.
- Issue #617 (KyleClouthier, 2026-07-27) proposes a reachability requirement ("Every assumption carries a reachability witness, and CI fails on `UNREACHABLE`") and mutation adequacy for all harnesses. It has **no organizer response** and is not Ch8-specific. Its relevance: the `kani::cover` pairing in #694 follows this proposal, not an organizer rule.

---

## 4. Synthesis: requirements as stated by organizers

The statement IDs (O-n) refer to section 2. Tag key: **[T]** = challenge text; **[2025]** / **[2026]** = date of the organizer statement.

### (1) Functions in scope
- **[T]** No-UB for 7 functions: the three `small_sort` impls, `swap_if_less`, `insertion_sort_shift_left`, `sort4_stable`, `has_efficient_in_place_swap`.
- **[T]** "Write contracts" showing sorting for the three `small_sort` impls only.
- **[T]** Callees with loops may need function or loop contracts.
- **[2026]** feliperodri treats internal callees as part of what must be exercised or verified, even though they are not in the list:
  - O-12: `sort8_stable`, sort8/sort12 network regions, `presorted_len` branches, bidirectional merge, the `insert_tail` loop.
  - O-13: `small_sort_general`, `small_sort_network`, `sort8_stable`, `sort13_optimal`.
  - O-15: "sort13_optimal is not verified at all (neither composed nor direct)"; `bidirectional_merge` only at tiny lengths; the `sort9_optimal` band only at u8.
- **[2026]** Reached through "the real trait impls/callees (no body swap)" (O-15). Swapping function bodies under cfg is not allowed (O-12, "no cfg-swap vacuity").
- **Evolution:** the list was fixed in 2024. In 2026 the review focus widened to every internal branch reachable within the thresholds.
- **Open:** whether `insertion_sort_shift_left` as a standalone helper needs proofs beyond the small-sort thresholds (TheodorNEngoy, unanswered). Its runtime precondition is enforced by `intrinsics::abort()` (O-12).

### (2) Length domain
- **[T]** "must be verified for all possible slices with arbitrary valid length."
- **[2026-08-16]** O-12: "SmallSort is inherently bounded (thresholds ... 16 ... 32) so bounded harnesses are the right approach". Fix: "cover the full valid range up to each variant's `small_sort_threshold()`", either sizes 0..=32 with matching `kani::unwind`, or "representative harnesses at the boundary sizes" 8, 9, 13, 16, 32.
- **[2026-09-12]** O-13: "Fails unbounded"; "To close Ch8 this needs symbolic-length harnesses over T"; "challenge says arbitrary length is required"; concrete-length unwind is "sound" only because the length is concrete. Branches and thresholds named: "32/17 thresholds".
- **[2026-09-13]** O-15 (latest): coverage "up to the fallback threshold 16 and general/network threshold 32"; "To close Ch8 it needs coverage up to the real length thresholds".
- **Contradiction / evolution:**
  - O-12 accepts bounded harnesses, even representative boundary sizes.
  - O-13 says "symbolic-length" and "fails unbounded".
  - O-15, the latest, reverts to "up to the real length thresholds" (16 / 32).
  - The consistent reading across all three: every length 0..=threshold for each dispatch route (16 for fallback / non-Freeze insertion paths, 32 for general and network), proven either with a symbolic length up to the threshold or for every concrete length. O-12's "representative boundary sizes" option was not repeated later.
- **Open:**
  - whether "every length up to the threshold" may be a family of concrete-length harnesses or must be one symbolic-length harness (O-13 suggests symbolic; O-15 is silent);
  - whether lengths above the threshold matter for the helper functions. `small_sort` is only called by the driver for `len <= threshold`. The doc's "arbitrary valid length" is literally unbounded, and no organizer has addressed `len > threshold` for `small_sort`.

### (3) Types T
- **[T]** Generic `T` in the impl paths. No bounds or type lists.
- **[2025-01-24]** O-5: "ultimate goal ... arbitrary types and arbitrary ordering"; "proofs for primitive types with default ordering will be considered as a solid solutions."
- **[2026-08-16]** O-12: "Correctness is only checked for `i32`. Acceptable for a bounded proof, but worth noting the challenge scope is generic `T`." This is non-blocking.
- **[2026-09-12]** O-13: "symbolic-length harnesses over T (primitive-mono per Ch8 doc if allowed — but here it's not ...)". `has_efficient_in_place_swap`: "T-generic behavior for u16/[u8;9]/ZSTs/!Freeze not covered."
- **[2026-09-13]** O-15 praised coverage across "i32, Cell<i32> (non-Freeze), NonCopyI32 (Freeze non-Copy), u128, [u64;11], u8". Type choice was **not** listed among the blocking reasons. The u8-only network band was called a "sound reduction via zero-one principle, but a reduction."
- **Reading:** the latest organizer practice accepts a set of representative monomorphic types covering the specializations (Freeze / !Freeze, Copy / !Copy, sizes, ZST for `has_efficient_in_place_swap`). Primitive types with default ordering are explicitly "solid" (2025). Width reductions such as u8 are tolerated but flagged as reductions.
- **Open:** whether a proof generic over `T` is required for the memory-safety part (Tiramisu-Cake Q1, unanswered); which minimum type set suffices; whether u8-width for the sort9/sort13 networks is acceptable for final acceptance.

### (4) Comparator / ordering
- **[T]** Silent.
- **[2025-01-24]** O-5: arbitrary ordering is the ultimate goal; "model arbitrary ordering itself is very challenging"; primitive types "with default ordering" are a solid solution.
- **[2026]** No organizer statement on comparators. O-15 accepted #678's fixed strict order `a < b` without comment. #678's own "adversarial comparator ... not modeled" gap was not listed as blocking.
- BusyBeaver's claim (non-organizer, 2025) that safety needs a `kani::any()`-returning comparator was neither confirmed nor refuted.
- **Open:** whether no-UB must hold for arbitrary, inconsistent, stateful or panicking `is_less` (Tiramisu-Cake Q2, unanswered). The general-rules safety focus and the fact that `small_sort` is a safe function with a user-supplied closure suggest it should; no organizer has said so.

### (5) Panics / unwind
- **[T]** Silent.
- **Organizers:** no statement in 2024–2026. "unwind" appears only in the Kani sense: O-12 asks for "matching `kani::unwind`"; O-13 says `#[kani::unwind(6)]` is sound only for concrete length.
- **Open:** panicking comparator and the `CopyOnDrop` / `GapGuard` unwind recovery in `insert_tail` / `small_sort_general`; whether "no UB on unwind" without a functional guarantee is enough (Tiramisu-Cake, unanswered).

### (6) Properties

**Safety / UB categories**
- **[T]** Dangling or misaligned access, uninitialized reads, mutating immutable bytes, invalid values, plus `SAFETY` comments.
- **[2025]** O-5: if proofs show `SAFETY` comments are insufficient, they "should be updated in the upstream" (see rust-lang/rust#135984, still open).
- **[2026]** No organizer comment on `-Z uninit-checks` (#694 says it cannot be used on this module).

**Sortedness**
- **[T]** "actually sort the slices".
- **[2026]** Required in O-12, O-13 and O-15.

**Permutation / multiset**
- **[T]** Implicit only.
- **[2026-08-16]** O-12 made it **blocking**: "Sorting correctness requires **both** "output is sorted" **and** "output is a permutation (multiset) of the input."" A count-based check is acceptable.
- **[2026-09-13]** O-15 praised #678's "assert_permutation multiset check using per-value occurrence counts".
- The 2025 question about the cost of the multiset check was answered only with "other tools are welcome".

**Stability**
- **[T]** Silent, apart from the trait name `StableSmallSortTypeImpl`.
- **Organizers:** no statement. O-15 did not object that #678 explicitly does not assert stability.
- **Open:** whether stability must be proven for `StableSmallSortTypeImpl` / `sort4_stable`.

**ZST / !Freeze**
- **[2026-09-12]** O-13, only for `has_efficient_in_place_swap` type coverage (u16, [u8;9], ZSTs, !Freeze).
- **[2026-09-13]** O-15 credits `Cell<i32>` as non-Freeze coverage.

**Vacuity-related properties**
- **[2026-08-16]** O-12: the `swap_if_less` harness allowing `a == b` makes the assertion trivial; assume `a != b`.

### (7) How correctness must be expressed
- **[T]** "write contracts ... to show that the sorting algorithms actually sort the slices."
- **[2026-08-16]** O-12: non-blocking. `requires` without `proof_for_contract` are "documentation only".
- **[2026-09-12]** O-13: "0/3 sorting-correctness contracts". Sortedness "asserted inside plain `#[kani::proof]`" instead of `#[safety::ensures]`. Needs "real `#[ensures]` sortedness contracts on the 3 small_sort impls with matching `proof_for_contract`". "Decorative contracts" are a violation ("T7").
- **[2026-09-13]** O-15: "Correctness is expressed as in-harness oracles, not #[ensures]/proof_for_contract". To close: "ideally, the correctness expressed as contracts."
- **Evolution:**
  - O-12 did not demand contracts.
  - O-13 demanded them as a closing requirement.
  - O-15 (latest) softens this to "ideally", and does not mention permutation inside the contract.
- **Technical obstacles reported by authors, never addressed by organizers:**
  - #694: `E0520` on the specializing impl, and `E0599` because `old()` requires `T: Clone`;
  - #701: "specialization and generic old-state handling";
  - #678: contracts "cannot currently express the permutation property".
- **Open:** is an in-harness oracle acceptable for final acceptance if contracts are technically impossible on the specialized impls? Must the `ensures` include permutation or only sortedness (O-13 says "sortedness contracts")? Would contracts on non-specialized internal callees (for example `small_sort_general_with_scratch`, `insertion_sort_shift_left`) plus `proof_for_contract` satisfy "write contracts"?

### (8) Assume / stub / cover / vacuity policy
- **[2026-08-16]** O-12 checks against:
  - cfg-swap vacuity;
  - `#[cfg(not(kani))]` body gating;
  - trivial invariants;
  - assume-the-conclusion.
  It accepts "legitimate" assumes and flags degenerate assumes such as `a == b`.
- **[2026-09-12]** O-13: "Reviewed ... with our vacuity tooling". Contracts not checked via `proof_for_contract` are "decorative" ("T7"); the T-code taxonomy is not published.
- **[2026-09-13]** O-15 praises "no body swap", "no cfg/assume tricks", "no decorative contracts".
- **`copilot-instructions.md` [2026-03-31, feliperodri]:**
  - no vacuous proofs (an "unsatisfiable precondition or an empty harness body");
  - every assume justified by safety docs or API invariants;
  - no over-constraining;
  - "meaningful input ranges";
  - `kani::assume(false)` is a red flag;
  - gate with `#[cfg(kani)]`.
- **Stubs:**
  - BusyBeaver's `stub_verified` on `sort13_optimal` (2025) was never answered.
  - O-15 requires `sort13_optimal` to be verified "composed" or "direct". So `stub_verified` (a contract-verified stub) is implicitly OK only if `sort13_optimal` has its own verified contract. Unverified stubs: no organizer statement, but they count as vacuity.
- **Cover:** no organizer statement. The #617 proposal ("CI fails on UNREACHABLE") is unanswered.
- **Open:** the exact vacuity tooling and T-code rules; whether `kani::cover` witnesses are expected.

### (9) Performance / CI time budget
- **[2025-01-24]** O-6: "We expect to run all proof on CI"; "ideally ... less than ~2 minutes on a GitHub standard runner"; if Kani/CBMC limits are hit, "open a PR with the proof so that we could merge it once we have made performance improvements".
- **[2026]** No organizer statement. PR authors report a "10-minute per-harness" cap (`kani.yml` uses `--harness-timeout 10m` on the autoharness step), 4-core / 16 GB ubuntu runners, and OOM kills.
- general-rules: functional-correctness conditions must not cause "excessive verification run time".
- **Open:**
  - Whether over-budget proofs (for example len-32 general and network, `sort13_optimal`) can be merged under the 2025 "merge once performance improves" policy and still count toward closing Ch8.
  - O-15 demands threshold coverage without addressing that this is the cost wall reported by #234, #678, #694 and #701.

### (10) Tools
- **[T]** Only via general rules.
- **[2025-01-24]** O-5: "Yes, other tools are welcome" (in reply to using a separate tool for the invalid-values / multiset part).
- **Current list:** Flux, ESBMC (GOTO Transcoder), Kani, KMIR (since 2026-08-28), VeriFast. New tools need an application first.
- **Open:** whether mixing tools per property is accepted (for example Kani for UB, another tool for permutation). O-5 implies yes.

### (11) Partial solutions / reward / process
- **[2025-04-29]** O-10 (rahulku) wanted to "push this through" for a draft partial PR (#234). This is a weak signal that partial or incremental merges are welcome.
- **[2025-01-24]** O-6: open a PR even if proofs exceed limits, so it can be merged later.
- **[2026-09-13]** O-15: "we're prioritizing this one (it strictly dominates #576)". The PR is "partial", and closing Ch8 needs threshold coverage and ideally contracts. This implies review-time comparison among competing PRs (general-rules: "first come, first served").
- `copilot-instructions.md`: the PR must meet "every" criterion, and partial solutions should be flagged.
- **Reward:** 10,000 USD in the doc and README. No organizer statement on splitting among contributors or the effect of prior work (TheodorNEngoy Q1, unanswered). No published payment or eligibility process (TheodorNEngoy Q3, unanswered).
- **AI-assisted contributions:** no organizer statement and no template requirement. #640 and #678 disclosed AI use; organizers did not comment (O-15 reviewed #678 on the merits without mentioning it). TheodorNEngoy's eligibility question is unanswered.
- **Process facts:**
  - two committee approvals are needed;
  - "Resolves #56" in the PR;
  - Apache-2.0/MIT;
  - no runtime changes unless upstreamed;
  - code under `#[cfg(kani)]`.
- **Open:** whether a partial PR can be merged without closing Ch8, and how the reward is then allocated.

---

## 5. Short list of all open (unanswered) organizer-facing questions as of 2026-10-24

1. Is `stub_verified` on `sort13_optimal` acceptable? (BusyBeaver-42, 2025-01-09)
2. Which types `T` beyond "primitive" are needed? Is a T-generic proof required for no-UB? (BusyBeaver 2025; Tiramisu-Cake 2026-10-23)
3. Must no-UB hold for arbitrary, stateful or panicking `is_less`? Is "no UB on unwind" sufficient? (Tiramisu-Cake 2026-10-23)
4. Is complete `i32` coverage up to each threshold, with sorted plus multiset, enough? Does `insertion_sort_shift_left` need proofs beyond the thresholds? (TheodorNEngoy 2026-09-05)
5. Award availability and allocation among overlapping contributors; AI-assisted eligibility; payment process (TheodorNEngoy 2026-09-05).
6. Does a partial result count, and should frontier harnesses be extended on larger hardware? (samiam713, #678 body)
7. Are in-harness oracles acceptable when contracts on specialized impls fail to compile (`E0520`/`E0599`)? (#694, #701, #678 bodies; O-15 says only "ideally" contracts)
8. Must stability be proven for the stable variant? (never raised to or by organizers)
9. Can proofs that exceed the CI budget count toward closing Ch8? (2025 policy vs 2026 practice)
10. #694 and #701 have no organizer review yet.

## 6. Bottom line: the most authoritative current reading

Based on the latest statements (O-15, 2026-09-13, plus O-12 and O-13), a solution should:

1. Exercise the real implementations of all 7 functions, with no body swap, cfg trickery, or vacuous or over-constrained assumes.
2. For each `small_sort` impl and each dispatch route, cover all lengths up to the real thresholds: 16 (fallback) and 32 (general / network). This includes `sort13_optimal` (composed or direct) and `bidirectional_merge` at real lengths.
3. Prove sortedness **and** multiset permutation.
4. Use a set of types spanning the specializations. Primitive types with default ordering are explicitly "solid" (2025). Representative types like Cell, non-Copy, u128 and [u64;11] were praised; u8-width reductions are tolerated but flagged.
5. Preferably express correctness as `#[ensures]` contracts with `proof_for_contract` ("ideally"). Any `requires` / `ensures` written must be checked by `proof_for_contract`, or it is "decorative".
6. Run in CI. The 2025 target was about 2 minutes per proof; the 2026 practice is a 10-minute per-harness cap.

Comparator panics and unwind, stability, generic-`T` proofs, reward splitting and AI eligibility remain **unaddressed by any organizer**.
