# Cross-challenge precedents: how the verify-rust-std committee interprets recurring requirements

Compiled 2026-10-24. Scope: every challenge except Challenge 8 (Ch8 PRs #234, #576, #640, #678, #694, #701 and issue #56 are deliberately excluded and covered elsewhere).

Sources and method:
- A local git clone of `model-checking/verify-rust-std` at `main` (HEAD `c0bd09c`, 2026-10-22). It gives challenge texts, squash-merge PR bodies, CI workflows and the VeriFast proof sources.
- The GitHub REST API, read through WebFetch: issue comments, PR reviews and inline review comments, plus the search API.
- WebFetch paraphrases API content and caps verbatim quotes at about 125 characters. Quotes below are short excerpts returned by the API. Everything else is a faithful paraphrase. Where a page could not be read, this file says so.

Abbreviations: "FR" = feliperodri, "TS" = tautschnig, "CZ" = carolynzech, "Ch" = Challenge.

---

## 0. Executive summary for the Challenge 8 ruling

1. **The "unbounded / arbitrary length" wording is now enforced as a blocker for Kani submissions.**
   - Since 2026-09-12, FR has blocked bounded Kani submissions (`kani::unwind`, `MAX_LEN`, fixed arrays) to Ch4/16/17/18/25 on this criterion alone ([#549](https://github.com/model-checking/verify-rust-std/pull/549#pullrequestreview-5187932615), [#602](https://github.com/model-checking/verify-rust-std/pull/602#pullrequestreview-5187932804), [#603](https://github.com/model-checking/verify-rust-std/pull/603#pullrequestreview-5188000592), [#651](https://github.com/model-checking/verify-rust-std/pull/651#pullrequestreview-5188033558), [#577](https://github.com/model-checking/verify-rust-std/pull/577#pullrequestreview-5188053034)).
   - "Unbounded" with Kani is recognised only when loop contracts are used with no `kani::unwind` and no length constant ([#681 review](https://github.com/model-checking/verify-rust-std/pull/681#pullrequestreview-5188867006)).
   - The earliest precedent agrees. In 2024 CZ told a Ch5 contributor that a bounded Kani harness does not meet an "unbounded" requirement ([#29](https://github.com/model-checking/verify-rust-std/issues/29#issuecomment-2501534218)).
   - One softer data point: on 2026-08-16 FR wrote that he would not block on bounded length alone ([#603](https://github.com/model-checking/verify-rust-std/pull/603#pullrequestreview-4947445617)). By 2026-09-12 it was a blocker.

2. **Bounded input ranges are tolerated only where the challenge text does not demand unboundedness**, and only if the gap is documented.
   - Ch12 (#637/#656) and Ch2 (#649) accepted bounded ranges as documented tool-limitation gaps.
   - Ch13, Ch26, Ch27 and Ch29 accepted bounded lengths ≤100 or ≤1024 because those challenges allow bounds or say nothing about length.

3. **Generic `T`**: there is no ruling yet. Issue [#734](https://github.com/model-checking/verify-rust-std/issues/734) (FR, 2026-10-21) is still open.
   - The only resolved challenge whose text has the "generic T (no monomorphization)" clause is Ch19, and it was solved by VeriFast.
   - Representative-type instantiation is accepted wherever the challenge text allows it: Ch3, Ch5, Ch6, Ch12, Ch26, Ch27 and Ch29.
   - **Ch8's text has no generic-T clause.** It says "for all possible slices with arbitrary valid length" and lists no type restriction, so it falls in neither group cleanly.

4. **Panics and unwinding**: the two VeriFast precedents (Ch5, Ch19) were accepted with `-ignore_unwind_paths`, disclosed as a caveat.
   - Kani solutions are accepted while treating panics as failures, with `should_panic` harnesses for documented panics.
   - Panic safety (for example a panicking `Drop`) has never been required for acceptance. FR asked for it once, as a non-blocking request ([#602](https://github.com/model-checking/verify-rust-std/pull/602#pullrequestreview-4947444324)), and in 2026 listed it as a known gap of the VeriFast guarantee ([#734](https://github.com/model-checking/verify-rust-std/issues/734)).

5. **Closures**:
   - VeriFast Ch5 modelled the user closure as an `assume_correct` wrapper with a semantic-well-typedness spec.
   - VeriFast Ch19 inlined `Result::map` / `map_err` and proved the rewrite equivalent with the refinement checker.
   - Kani submissions make closures nondeterministic ([#681](https://github.com/model-checking/verify-rust-std/pull/681)).
   - Comparator closures that receive elements by reference are a known Kani obstacle ([#703](https://github.com/model-checking/verify-rust-std/pull/703)).

6. **Assumes and stubs**:
   - In 2026 every `kani::assume` is expected to be paired with `kani::cover`. This was the decisive reason #637 won Ch12.
   - Hand-written stubs need explicit committee sign-off ([#681](https://github.com/model-checking/verify-rust-std/pull/681#pullrequestreview-5188867006)).
   - Stubbing the very algorithm under test is rejected as circular ([#538](https://github.com/model-checking/verify-rust-std/pull/538#pullrequestreview-4947262491)).
   - The VeriFast precedents contain about 10 `assume(false)` lemma bodies or safety proofs, several `assume_correct` wrappers, and `assume(alloc lifetime == 'static)`. They were accepted with a README note saying they "must be carefully audited".

7. **Contracts**:
   - `proof_for_contract` is expected for each contract. A `#[requires]` checked only through a `kani::assume` mirror is called "decorative" and blocks ([#549](https://github.com/model-checking/verify-rust-std/pull/549#pullrequestreview-4947356961)).
   - Where Kani cannot attach a contract (generic trait methods, trait-object generics, const-generic intrinsics), plain assertion harnesses or forwarding wrappers are accepted, provided this is disclosed.

8. **Vacuity**: FR's "vacuity tooling" checks for the following patterns:
   - `cfg(kani)` / `cfg(not(kani))` body swaps,
   - `loop_invariant(true)` / `invariant(true)`,
   - assume-the-conclusion,
   - contracts with no `proof_for_contract`.

   Since 2026-08 FR applies it to every review. From 2026-10, mutation testing also appears in reviews ([#587](https://github.com/model-checking/verify-rust-std/pull/587#pullrequestreview-5608878227)).

9. **Selection among competing PRs**: not first come, first served in practice.
   - For Ch12, #637 (opened 2026-08-19) beat #544 (2026-02-08), #565 (2026-03-24) and #600 (2026-06-12), on "soundness of the proofs, not breadth".
   - No reward splitting has been observed.
   - Earlier partial PRs were merged as "Towards #N" contributions.

---

## 1. Challenge inventory (doc/src/challenges at main)

Status as of 2026-10-22 (`main`). The README table is in sync after [#629](https://github.com/model-checking/verify-rust-std/pull/629) (FR, merged 2026-08-28), which removed all end dates and marked Ch15 resolved, and [#663](https://github.com/model-checking/verify-rust-std/pull/663), which marked Ch12 resolved.

| Ch | Title | Reward (current) | Status | Tracking issue |
|---|---|---|---|---|
| 1 | core transmuting methods | 10,000 USD (was N/A at resolution, raised by #502) | Resolved | #19 |
| 2 | intrinsics using raw pointers | 10,000 | Open | #16 |
| 3 | raw pointer arithmetic | N/A | Resolved | #76 |
| 4 | BTreeMap node | 10,000 | Open | — |
| 5 | LinkedList | 20,000 (was 5,000 at resolution, raised by #459) | Resolved | #29 |
| 6 | NonNull | N/A | Resolved | #53 |
| 7 | Atomic types | 10,000 | Open | — |
| 8 | SmallSort | 10,000 | Open | #56 (out of scope here) |
| 9 | Duration | N/A | Resolved | #72 |
| 10 | String | 10,000 | Open | — |
| 11 | Floats/ints | N/A | Resolved | #59 |
| 12 | NonZero | 10,000 | Resolved | #71 |
| 13 | CStr | 10,000 | Open | — |
| 14 | Primitive conversions | N/A | Resolved | #220 |
| 15 | SIMD intrinsics | 20,000 | Resolved | #173 |
| 16–29 | Iter, slice, slice iter, RawVec (19), str pattern 1/2, str iter, Vec 1/2, VecDeque, Rc, Arc, flt2dec, boxed | 5k–25k | All Open except 19 (Resolved) | 280 (Ch16), 283 (Ch19), … |

That makes 10 resolved challenges: 1, 3, 5, 6, 9, 11, 12, 14, 15 and 19.

Reward history notes. Both raises happened after the challenge was already resolved, which suggests rewards are set by the separate rewards committee and are not tied to the date of resolution:
- [#459](https://github.com/model-checking/verify-rust-std/pull/459) (TS, merged 2025-10-08) raised Ch5 from 5,000 to 20,000 USD after Ch5 had been resolved on 2025-08-20.
- [#502](https://github.com/model-checking/verify-rust-std/pull/502) (TS, 2025-10-20) changed Ch1 from N/A to 10,000 after Ch1 had been resolved on 2025-09-09.

---

## 2. Resolved challenges: winning PRs and what was accepted

| Ch | Winning / closing PR(s) | Tool | Merged | Length/size domain accepted | Types accepted | Panics/unwind | assume / stubs / trusted | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | Partial PRs [#185](https://github.com/model-checking/verify-rust-std/pull/185), [#264](https://github.com/model-checking/verify-rust-std/pull/264), [#405](https://github.com/model-checking/verify-rust-std/pull/405) (align_to), then status PR [#433](https://github.com/model-checking/verify-rust-std/pull/433) | Kani | #433: 2025-09-09 | Bounded slices (align_to). FR later called this merged align_to work a bounded precedent ([#603 review](https://github.com/model-checking/verify-rust-std/pull/603#pullrequestreview-4947445617)) | Per-instantiation harnesses. celinval: "you can only verify one instantiation of the target function" ([#19](https://github.com/model-checking/verify-rust-std/issues/19#issuecomment-2455620236)) | n/a | Transmute contracts only "to the extent… expressible by Kani"; "trivially safe" functions got no harness (#433 body) | Accepted at the 75% function threshold; approved by TS and FR with empty bodies ([TS](https://github.com/model-checking/verify-rust-std/pull/433#pullrequestreview-3201073619), [FR](https://github.com/model-checking/verify-rust-std/pull/433#pullrequestreview-3202557709)). Committee member patricklam is a listed contributor |
| 3 | Partial PRs #113, #154, #166, #168, #188; closing PR [#212](https://github.com/model-checking/verify-rust-std/pull/212) | Kani | 2024-12-12 | Bounded | Challenge text names the sample pointee types: integers, a dyn Trait, a slice, unit, a composite | n/a | Usage proofs done without stubbing, because stubbing was blocked by kani#3732 (disclosed in the #212 body) | 2024 student-team era, no reward |
| 5 | [#238](https://github.com/model-checking/verify-rust-std/pull/238) | VeriFast | 2025-08-20 | Unbounded: "arbitrary shape" via inductive predicates | Generic T. VeriFast proves for all T; the challenge allowed primitive types only | `-ignore_unwind_paths` (disclosed in the PR body addendum of 2025-01-23 and in the README caveats) | `-allow_assume`: `assume(alloc lifetime == 'static)`, `assume(len < usize::MAX)`, `assume(false)` bodies for subtyping/upcast lemmas and 3 `safety_proof {assume(false)}`, 5 `assume_correct` wrappers including the user closure call; trusts VeriFast's `lib.rsspec` | Code changes to linked_list.rs justified by the refinement checker. `contains`, `remove` and `retain` carry no spec and are skipped by `-skip_specless_fns` (argued safe via verified callees) |
| 6 | Partial PRs #103, #107, #126, #127, #144, #149; closed by [#247](https://github.com/model-checking/verify-rust-std/pull/247) | Kani | 2025-03-21 | Fixed `ARR_SIZE` = 1000 accepted by TS: "entirely fine" ([#53](https://github.com/model-checking/verify-rust-std/issues/53#issuecomment-2518176799)) | Sample types. zhassan-aws: Kani can't prove for all types, so use the Ch3 sample list ([#53](https://github.com/model-checking/verify-rust-std/issues/53#issuecomment-2369588904)) | n/a | — | Closed by an organizer (thanhnguyen-aws), who added the last 3 functions himself |
| 9 | [#136](https://github.com/model-checking/verify-rust-std/pull/136) + [#224](https://github.com/model-checking/verify-rust-std/pull/224) | Kani | 2024-12-10/11 | "All possible input values" (scalars; exhaustive) | concrete | n/a | — | |
| 11 | #91, #96, #102, #111, #112, #114, #134; closed by [#206](https://github.com/model-checking/verify-rust-std/pull/206) | Kani | 2024-12-06 | 32/64/128-bit `unchecked_mul` checked only over value intervals (`generate_unchecked_mul_intervals!` in `library/core/src/num/mod.rs`) | per integer type | n/a | `kani::assume` intervals | My analysis: intervals such as `[i32::MAX-1000, i32::MAX]` for both operands, together with `assume(!overflow)`, admit no input, so those particular harnesses are vacuous. This is the same pattern #637 later fixed in NonZero |
| 12 | [#637](https://github.com/model-checking/verify-rust-std/pull/637) (stefanzetzsche) | Kani | 2026-08-25 | Full range up to 32 bits; value ranges at 64/128 bits for mul/isqrt. `pow` unbounded via a strengthened loop invariant. Gaps tracked in [#656](https://github.com/model-checking/verify-rust-std/issues/656) | One harness per NonZero type (12 types) | `abs`/`neg` at MIN covered by `#[kani::should_panic]` | Every `kani::assume` paired with `kani::cover`; plain harnesses where contracts are impossible | Chosen over #544, #565 and #600 |
| 14 | [#233](https://github.com/model-checking/verify-rust-std/pull/233); closed by [#247](https://github.com/model-checking/verify-rust-std/pull/247) | Kani | 2025-02-12 / 2025-03-21 | All values (scalars) | per macro instance | Challenge required proving the panic in the fallible case | — | |
| 15 | [#423](https://github.com/model-checking/verify-rust-std/pull/423) (Bhargavan, Buyse) | Testable models (a CI test job, not a prover) | 2025-09-24 (marked resolved 2026-08-28 in #629) | n/a | n/a | n/a | Challenge "Assumptions": the user must trust the hand-written semantics | TS required a CI job running the tests ([review](https://github.com/model-checking/verify-rust-std/pull/423#pullrequestreview-3079215975)) |
| 19 | [#422](https://github.com/model-checking/verify-rust-std/pull/422) | VeriFast | 2025-08-14 | Unbounded | Generic T and A (no monomorphization) | `-ignore_unwind_paths` | `-allow_assume`: 2 `assume(false)` lemma bodies (verifast#610); `Result::map`/`map_err` closures inlined and checked by the refinement checker | Ch19 is the only resolved challenge whose text has the "generic T, no monomorphization" clause |

Approvals: two committee approvals are required ([general-rules.md](https://github.com/model-checking/verify-rust-std/blob/main/doc/src/general-rules.md); `.github/pull_requests.toml`).
- #238 and #422: TS ([review](https://github.com/model-checking/verify-rust-std/pull/238#pullrequestreview-3109991564), "Approving having reviewed VeriFast's internal library specs", with comments filed in [verifast#863](https://github.com/verifast/verifast/issues/863)) and remi-delmas-3000 (empty bodies).
- #637: FR and rajath-mk ([review](https://github.com/model-checking/verify-rust-std/pull/637#pullrequestreview-5021323228), "my analysis is similar to that of @feliperodri").

---

## 3. Per-topic synthesis

### (a) "Arbitrary length / unbounded / for all": is a bounded proof acceptable?

**How it is interpreted in practice.**
- Where the challenge text says "unbounded" or "arbitrary length", the 2026 reviewer (FR) treats bounded unrolling as not meeting the criterion. He demands loop contracts or another accepted unbounded encoding.
- Where the text does not demand it, bounded lengths are accepted if they are documented as CI budget or tool limits.
- Bounded *value ranges* for scalars (Ch12) were accepted only as explicitly tracked tool-limitation gaps.

Precedents, chronological:

1. **2024-11-26, CZ, Ch5** ([#29](https://github.com/model-checking/verify-rust-std/issues/29#issuecomment-2501534218)). She answered a contributor who proposed a Kani harness that builds a list of symbolic `i8` size: "Kani is a bounded model checker, while this challenge explicitly requires unbounded proofs." She pointed the contributor to other tools. Ch5 was then solved by VeriFast.
2. **2024-12-04, TS, Ch6** ([#53](https://github.com/model-checking/verify-rust-std/issues/53#issuecomment-2518176799)). A fixed `ARR_SIZE` of 1000 was "entirely fine". Ch6 has no unbounded clause.
3. **2024-12, Ch11** (closed by #206). Interval-restricted harnesses for wide multiplication were accepted. Ch11 has no unbounded clause.
4. **2025-03, challenge authoring.** thanhnguyen-aws introduced "The verification must be unbounded—it must hold for slices of arbitrary length" in Ch16–19 and Ch23–25 ([#260](https://github.com/model-checking/verify-rust-std/pull/260), [#265](https://github.com/model-checking/verify-rust-std/pull/265), [#314](https://github.com/model-checking/verify-rust-std/pull/314), [#267](https://github.com/model-checking/verify-rust-std/pull/267)).
   - He explained: "this challenge requires unbounded proofs" ([#260 r1978395569](https://github.com/model-checking/verify-rust-std/pull/260#discussion_r1978395569), 2025-03-03).
   - TS asked "Is there a realistic path (for some tool) towards accomplishing this?" ([#265 r2000760195](https://github.com/model-checking/verify-rust-std/pull/265#discussion_r2000760195), 2025-03-18). thanhnguyen-aws replied "I think Verifast can handle it" ([r2001420936](https://github.com/model-checking/verify-rust-std/pull/265#discussion_r2001420936)).
   - Ch8's wording ("for all possible slices with arbitrary valid length") is older: [#57](https://github.com/model-checking/verify-rust-std/pull/57), qinheping, 2024-08-20. Ch5 ("must be unbounded—arbitrary shape", 2024-07) and Ch4 ("must be unbounded for functions that use recursion or contain loops", 2024-07) are also older.
5. **2025-04-28, [#327](https://github.com/model-checking/verify-rust-std/pull/327)** (thanhnguyen-aws). Loop invariants were added to int `pow` functions. FR later described them as giving autoharness "unbounded `pow` coverage" ([#544 review](https://github.com/model-checking/verify-rust-std/pull/544#pullrequestreview-4947343751)).
6. **2026-08-16, FR, Ch17 [#603](https://github.com/model-checking/verify-rust-std/pull/603#pullrequestreview-4947445617).** He quoted the unbounded clause against fixed `ARR_SIZE` 64/100 arrays but said he would not block on that alone, because it matches the merged `align_to` work.
7. **2026-08-16, FR, Ch16 [#602](https://github.com/model-checking/verify-rust-std/pull/602#pullrequestreview-4947444324).** Fixed backing arrays plus `#[kani::unwind(N)]` were blocking. He wanted "loop contracts or another accepted unbounded encoding instead of finite unrolling". A doc comment claiming that a symbolic slice capped at `MAX_LEN` is "unbounded" was called inaccurate.
8. **2026-08-16, FR, Ch25 [#577](https://github.com/model-checking/verify-rust-std/pull/577#pullrequestreview-4947407591).** Every harness was bounded (arrays of length 2–4, `unwind(4)`). This was blocking, and was made worse because it was not disclosed.
9. **2026-08-18, Ch12 contributors.**
   - #544: isqrt harnesses for wide types hit the "10-minute per-harness timeout", so the author kept u8/u16/u32 at full range and moved to bounded windows "clearly marked as bounded" ([#544 comment](https://github.com/model-checking/verify-rust-std/pull/544#issuecomment-5327765778)).
   - #565: full `pow` comparison "exceeds CI time limits" ([#565 comment](https://github.com/model-checking/verify-rust-std/pull/565#issuecomment-4180477187)).
10. **2026-08-25, Ch12 resolution (#637 / #656).**
    - FR's comparison comment noted that #637 handles the multiplication blow-up with "small full-range inputs and value-range checks at wide types… instead of silently narrowing" ([#637](https://github.com/model-checking/verify-rust-std/pull/637#issuecomment-5414567888)).
    - The gaps were filed as [#656](https://github.com/model-checking/verify-rust-std/issues/656): CBMC cannot handle full-width 64/128-bit multiplication; "smaller widths, up to 32 bits, are verified exhaustively"; `pow` is proved for any exponent, but only "the result is nonzero", not its exact value.
    - The challenge was accepted with these documented gaps.
11. **2026-09-12, FR, batch of Kani reviews.** Bounded proofs became a hard blocker:
    - [#549 (Ch16)](https://github.com/model-checking/verify-rust-std/pull/549#pullrequestreview-5187932615): unwind-capped `array_chunks::fold`, `next_chunk` and others are blocking. "*_unbounded" harnesses that re-implement the loop body with hand-written inductive fragments, instead of proving the real function, are also blocking.
    - [#602 (Ch16)](https://github.com/model-checking/verify-rust-std/pull/602#pullrequestreview-5187932804): "The challenge requires arbitrary length throughout."
    - [#603 (Ch17)](https://github.com/model-checking/verify-rust-std/pull/603#pullrequestreview-5188000592): backing arrays ≤100 and unwind-capped `binary_search_by` / `partition_dedup_by` are now a blocking item. He defers to the committee on "representative types plus an unbounded-length strategy".
    - [#651 (Ch18)](https://github.com/model-checking/verify-rust-std/pull/651#pullrequestreview-5188033558): "The challenge mandates arbitrary length and generic `T` throughout."
    - [#577 (Ch4)](https://github.com/model-checking/verify-rust-std/pull/577#pullrequestreview-5188053034): Ch4 "explicitly requires these to be verified unbounded"; claimed unbounded proofs were absent.
12. **2026-09-13, FR, Ch25 [#681](https://github.com/model-checking/verify-rust-std/pull/681#pullrequestreview-5188867006).** This is the positive model of "unbounded with Kani".
    - `any_deque` has symbolic capacity, with "no `kani::unwind`, no `MAX_LEN`, no length constant anywhere" and "real loop invariants". FR called it the strongest Ch25 submission and "unbounded".
    - Caveats: the `cfg(kani)` path runs a hand-written loop paraphrase ("the proof runs the paraphrase, not the shipped body"). Slice drop glue is a compiler-generated loop that cannot carry a loop contract, so it is checked only at `len <= 4`, and the PR labels those harnesses as "bounded evidence", not proofs ([#681 comment](https://github.com/model-checking/verify-rust-std/pull/681#issuecomment-5652358150)).
    - The PR carries the "Accepted Solution" label but is still open with CHANGES_REQUESTED, pending the #734 ruling.
13. **Bounded accepted where the challenge allows it, 2026-09.**
    - Ch13 [#638](https://github.com/model-checking/verify-rust-std/pull/638#pullrequestreview-5187725491): "Bounded harnesses are explicitly allowed for this challenge."
    - Ch26 [#582](https://github.com/model-checking/verify-rust-std/pull/582#pullrequestreview-5188082622): slice length ≤100, iterator loops `unwind(6)`.
    - Ch27 [#587](https://github.com/model-checking/verify-rust-std/pull/587#pullrequestreview-5188093198): slice length capped at 100 "as a CI budget".
    - Ch29 [#639](https://github.com/model-checking/verify-rust-std/pull/639#pullrequestreview-5188108532): `unwind(4)` for len ≤2, called "non-vacuous".
    - Ch2 [#649](https://github.com/model-checking/verify-rust-std/pull/649#pullrequestreview-5187846135): `compare_bytes` bounded to 8 bytes; `arith_offset` checked only over a [2^32, 2^45] address window because CBMC mismodels near-NULL/wrap edges. Disclosed and accepted.

**Loop contracts.**
- Not required by any resolved challenge's text, except as a hint. Ch8 itself says "Function contracts and loop contracts … may be required."
- In practice, loop contracts are the only route the 2026 reviewer accepts for "unbounded" with Kani ([#602](https://github.com/model-checking/verify-rust-std/pull/602#pullrequestreview-4947444324), [#681](https://github.com/model-checking/verify-rust-std/pull/681#pullrequestreview-5188867006)).
- Trivial loop invariants (`loop_invariant(true)`) are flagged:
  - [#549, 2026-08-16](https://github.com/model-checking/verify-rust-std/pull/549#pullrequestreview-4947356961): either the havoc'd index needs justification, or, if the loops are still unwound, the "unbounded" claim must be corrected.
  - [#719](https://github.com/model-checking/verify-rust-std/issues/719) (FR, 2026-10-05): the `checked_pow` invariant makes `pow` imprecise under loop contracts.
- Removing an existing loop invariant is an out-of-scope regression. "A green CI run doesn't demonstrate that coverage was preserved" ([#544](https://github.com/model-checking/verify-rust-std/pull/544#pullrequestreview-4947343751)).

**Drift and contradiction.**
- 2024: bounded was fine where there was no clause (Ch6, Ch11). It was explicitly not fine for Ch5's unbounded clause (CZ).
- 2026-08-16: FR was mild on bounded length (#603). 2026-09-12: bounded is a hard blocker on every "unbounded" challenge.
- The Ch12 acceptance shows that, for a challenge without an unbounded clause, value-range bounds caused by tool limits are acceptable if tracked as an issue.

### (b) Generic `T`: which instantiations are accepted

- **Per-type instantiation is the norm for Kani** wherever the challenge allows it:
  - Ch1: celinval, 2024-11-04 ([#19](https://github.com/model-checking/verify-rust-std/issues/19#issuecomment-2455620236)). He suggested covering differing sizes, ZSTs and padding.
  - Ch3: the challenge text itself lists the instantiation set: integers, a `dyn Trait`, a slice, unit, a composite with multiple non-ZST fields.
  - Ch6: zhassan-aws, 2024-09-23 ([#53](https://github.com/model-checking/verify-rust-std/issues/53#issuecomment-2369588904)): use the Ch3 sample types, since Kani cannot prove for all types.
  - Ch12: 12 integer types ([#71 closing comment](https://github.com/model-checking/verify-rust-std/issues/71#issuecomment-5414585900)).
  - Ch26 and Ch29: primitives, called "challenge-allowed" ([#639](https://github.com/model-checking/verify-rust-std/pull/639#pullrequestreview-5188108532)).
  - Ch27: integers, bool, unit, `[u8;4]` ([#587](https://github.com/model-checking/verify-rust-std/pull/587#pullrequestreview-5188093198)).
  - Ch7: `AtomicPtr` over pointee sizes 0–4 ([#683](https://github.com/model-checking/verify-rust-std/pull/683#pullrequestreview-5188843822)).
- **Ch5 text**: "It is OK to assume that the generic type `T` … is primitive types". The VeriFast solution nonetheless proves for all T.
- **The "no monomorphization" clause** (Ch16–19, Ch23–25) was introduced at TS's suggestion ([#260 r1993550517](https://github.com/model-checking/verify-rust-std/pull/260#discussion_r1993550517), 2025-03-13). Two weeks earlier CZ had asked, on the same PR, for explicit concrete types ([r1977823380](https://github.com/model-checking/verify-rust-std/pull/260#discussion_r1977823380)). This is a contradiction at authoring time, resolved in favour of "no monomorphization".
- **Pending ruling [#734](https://github.com/model-checking/verify-rust-std/issues/734)** (FR, 2026-10-21, label "Question"):
  - Option A: representative types with a coverage argument, amended so that the set must hit every `size_of` / `align_of` branch, including callees, for example a type larger than 1 KiB for Vec/VecDeque.
  - Option B: only tool-level polymorphic proofs, which today means VeriFast.
  - Option C (future): kani#5041, an abstract `T` with symbolic size and alignment.
  - The issue's precedent section: Ch19 is the only resolved challenge with the clause and was solved by VeriFast; Kani per-type instantiation was accepted for Ch6, which lacks the clause.
  - Responses so far:
    - DiuDiu777 favours A, with symbolic size/align and separate contracts for Drop/Clone ([comment](https://github.com/model-checking/verify-rust-std/issues/734#issuecomment-6331645128)).
    - patricklam left a placeholder ([comment](https://github.com/model-checking/verify-rust-std/issues/734#issuecomment-6332316452)).
    - FR ran a Lean/Aeneas experiment: "The Lean proof covers every T, which no list of instances does" ([comment](https://github.com/model-checking/verify-rust-std/issues/734#issuecomment-6349628311)).
- **Before the ruling, reviewers block on it.** "Every harness is monomorphized to concrete element types", blocking for Ch16 ([#549](https://github.com/model-checking/verify-rust-std/pull/549#pullrequestreview-5187932615)); [#602](https://github.com/model-checking/verify-rust-std/pull/602#pullrequestreview-5187932804) calls it a "hard requirement". For #681, FR would approve "if the committee accepts representative-type monomorphization" ([#681](https://github.com/model-checking/verify-rust-std/pull/681#pullrequestreview-5188867006)).
- **ZST.**
  - Included as `()` in #681 and #602.
  - #603's `swap_unchecked` omits ZSTs because of a documented CBMC limitation. This was non-blocking ([#603](https://github.com/model-checking/verify-rust-std/pull/603#pullrequestreview-4947445617)).
  - #734 shows that #681's largest shape (16 bytes) leaves RawVec's >1 KiB branch unchecked.
- **Non-Copy / Drop types.**
  - #681 includes a `WithDrop` shape.
  - FR asked #602 for "a drop-requiring, ideally panicking-drop, type" in `map_windows` (non-blocking) ([#602](https://github.com/model-checking/verify-rust-std/pull/602#pullrequestreview-4947444324)).
  - #577 was flagged because contracts constraining bounds but not initialization are "unsound for generic `T`" ([#577](https://github.com/model-checking/verify-rust-std/pull/577#pullrequestreview-4947407591)).

**Relevance to Ch8.**
- Ch8's text has no "generic T" or "no monomorphization" clause and no "primitive types OK" clause either. It only says "all possible slices with arbitrary valid length".
- By the Ch1/3/6/12 precedent, per-type instantiation would be the default reading for clause-less challenges.
- But the comparator is user-supplied: Ch8 is generic over both `T` and `F: FnMut(&T,&T)->bool`. Whatever #734 decides about size/align coverage would likely be applied by analogy.

### (c) Closures, callbacks, comparators and trait methods from user code

- **VeriFast Ch5 (accepted).** In `extract_if`, the call to the user predicate `F: FnMut(&mut T) -> bool` is routed through `call_pred__VeriFast_wrapper`.
  - The wrapper is annotated `//@ assume_correct`.
  - Its spec requires and ensures only ownership and type validity of `f` and `element` (`<F>.own`, `<T>.own`), including on unwind (`on_unwind_ens`).
  - In other words, the closure is trusted to be any well-typed function (`verifast-proofs/alloc/collections/linked_list.rs/verified/linked_list.rs`, line about 4045).
  - btj described this in Dec 2024 as wrapping an `FnMut` call in an unverified helper ([#29](https://github.com/model-checking/verify-rust-std/issues/29#issuecomment-2518580876)).
  - `retain` (which takes a closure) has no spec and was argued safe through its verified callees ([#29](https://github.com/model-checking/verify-rust-std/issues/29#issuecomment-2515111675)).
- **VeriFast Ch19 (accepted).** "VeriFast does not currently support verifying code that involves lambda expressions, we inlined the calls of `Result::map` and `Result::map_err`." The rewrite is checked by `refinement-checker` (`verifast-proofs/alloc/raw_vec/mod.rs/README.md`).
- **Kani, 2026 (pending).**
  - #681 (Ch25): "the only value-dependent code is the user closures, which the harnesses make nondeterministic" (PR body). FR did not object.
  - #703 (Ch17): `binary_search_by` stays bounded because `get_unchecked`'s precondition is not discharged "when the comparator closure receives the element by reference". `partition_dedup_by` is bounded because `loop_modifies` cannot name compiler temporaries (PR body; no review yet).
  - #549: a traversal loop inside a capturing closure in a generic default method cannot carry a loop contract (PR body).
  - #561 (VeriFast Ch23 draft) lists "calls that pass closures" as out of reach.
- **Generic trait methods.**
  - Kani cannot attach contracts to them. #637 used plain assertion harnesses for `max`, `min`, `clamp` and `bitor` (cf. #202), and this was accepted ([FR review](https://github.com/model-checking/verify-rust-std/pull/637#pullrequestreview-4986123644)).
  - For trait-object generics, #639 used assume-mirrors in plain proofs. Accepted, with a note to upgrade when Kani supports it ([#639](https://github.com/model-checking/verify-rust-std/pull/639#pullrequestreview-5188108532)).
  - #651 created "inherent-twin" methods to make trait-method contracts checkable. FR praised the technique but flagged that the extraction sits in shipping std code (see (i)).
- **No organizer statement found** that defines what a user comparator may do: arbitrary or inconsistent ordering, panics, or interior mutation through `&T`. The closest models are VeriFast's "any well-typed closure" spec and Kani's "nondeterministic closure".

### (d) Panics and unwinding

- **Challenge text precedent.** Ch7 "Panicking (Optional)": "This section is not required … since panicking is not undefined behavior." Ch14 conversely requires proving that fallible conversions panic.
- **VeriFast precedents accepted while ignoring unwind paths:**
  - #238 PR body addendum (2025-01-23): "neither version of the proof verifies unwind paths."
  - README caveats for both proofs: "`-ignore_unwind_paths`: This proof ignores code that is reachable only when unwinding."
  - Both verify scripts run `verifast -skip_specless_fns -ignore_unwind_paths -allow_assume`.
  - No reviewer objected. TS's and remi-delmas-3000's approvals have no unwind remarks ([#238 reviews](https://github.com/model-checking/verify-rust-std/pull/238#pullrequestreview-3109991564)).
  - The VeriFast tool doc describes "ignore unwind paths" as a way to "postpone dealing with certain complexities" (`doc/src/tools/verifast.md`).
- **2026 re-characterisation.** #734 (FR) lists among VeriFast's limits: "Panics are allowed, and the proofs run with `-ignore_unwind_paths`. Panic safety, such as a `T` whose `Drop` panics mid-operation, goes unchecked. Kani fails on any panic but does not model unwinding either" ([#734](https://github.com/model-checking/verify-rust-std/issues/734)). This acknowledges that both accepted routes leave panic safety unproven, but it is not a new requirement.
- **Kani.**
  - Documented panics are covered with `#[kani::should_panic]` harnesses alongside `assume(x != MIN)` harnesses (#637).
  - A missing `should_panic` pair was a blocking item for #600: "Add a per-type `#[kani::should_panic]` neg-at-MIN harness" ([#600](https://github.com/model-checking/verify-rust-std/pull/600#pullrequestreview-4947448453)).
  - #683 used six `should_panic` proofs for illegal orderings ([#683](https://github.com/model-checking/verify-rust-std/pull/683#pullrequestreview-5188843822)).
- **Panic safety was requested once, non-blocking**: a panicking-drop type to exercise panic-safety ordering in `map_windows::push` ([#602](https://github.com/model-checking/verify-rust-std/pull/602#pullrequestreview-4947444324)).
- **No statement found** requiring unwinding verification for acceptance in any challenge.

### (e) assume, stubs, `stub_verified`, trusted specs, axioms, `-allow_assume`

- **VeriFast (accepted 2025).**
  - `-allow_assume` with the README note "These must be carefully audited."
  - Ch5 explicitly assumes the allocator lifetime is `'static` (so the result holds only for the global or an immortal allocator). btj found a `Box::leak` spec unsoundness with non-global allocators and recorded it ([#238 comment](https://github.com/model-checking/verify-rust-std/pull/238#issuecomment-3038925164)).
  - Actual content of the accepted proofs:
    - `assume(false)` as lemma bodies for upcast/variance lemmas (verifast#610).
    - `//@ safety_proof { assume(false); }` for `iter_mut`, `IterMut::next` and `next_back`.
    - `assume(self0.len < usize::MAX)`.
    - 5 `assume_correct` wrappers (Box::into_inner, Allocator::clone, mem::take, NonNull::from, the user closure).
  - #734 counts "10 `assume(false)` statements" across the two proofs and "130 std functions … trusted through hand-written specs in VeriFast's `lib.rsspec`".
  - The trusted-spec audit was done by TS in [verifast#863](https://github.com/verifast/verifast/issues/863) (2025-08-12), which raised `unsafe`-marker consistency. That audit is the basis of his approval.
  - Tool-application audit: remi-delmas-3000 recruited auditors and published findings in [#213](https://github.com/model-checking/verify-rust-std/issues/213#issuecomment-2631704089) (2025-02-03).
- **Kani (2026 practice).**
  - "No unjustified assumptions. Every `#[kani::assume]`, `requires` … must be justified by the function's documented safety contract" (`.github/copilot-instructions.md`, [#581](https://github.com/model-checking/verify-rust-std/pull/581), FR, 2026-03-31).
  - **`kani::cover` beside each `kani::assume`** became the winning differentiator in Ch12. #637 "systematically pairs every `kani::assume` with a `kani::cover`" ([#565 closing](https://github.com/model-checking/verify-rust-std/pull/565#issuecomment-5414580506), [#544 closing](https://github.com/model-checking/verify-rust-std/pull/544#issuecomment-5414580840), [#600 closing](https://github.com/model-checking/verify-rust-std/pull/600#issuecomment-5414581203)).
  - Assumes limited to caller-side preconditions are fine: "limited to layout, slice length, and caller-side obligations" ([#587](https://github.com/model-checking/verify-rust-std/pull/587#pullrequestreview-5188093198)); "legitimate caller preconditions, not assumed conclusions" ([#603](https://github.com/model-checking/verify-rust-std/pull/603#pullrequestreview-4947445617)).
- **Stubs.**
  - Rejected when they replace the algorithm under test and assume the asserted property. In #538 (Ch21) the Two-Way searcher's `new()`/`next()` are replaced under `cfg(not(kani))` with nondeterministic stubs that `kani::assume` the char-boundary conditions the harness later asserts. FR called this circular: "stub the allowed external dependencies … at their real call sites, not the searcher itself" ([#538](https://github.com/model-checking/verify-rust-std/pull/538#pullrequestreview-4947262491)).
  - Body replacement under `cfg(kani)` that changes the shipping loop is treated as vacuous for the real function: "verifies the stub, not the shipping function" ([#632](https://github.com/model-checking/verify-rust-std/pull/632#pullrequestreview-5187932719)).
  - Hand-written over-approximating stubs whose soundness "rests on argument" need committee sign-off, with a suggested move to `stub_verified` once Kani allows it ([#681](https://github.com/model-checking/verify-rust-std/pull/681#pullrequestreview-5188867006)). The #681 author documents each stub in a table of what it replaces, what it asserts and what it over-approximates, and found `stub_verified` did not terminate for `u8` ([comment](https://github.com/model-checking/verify-rust-std/pull/681#issuecomment-6037355222)).
  - Stubbing as a scoped workaround was suggested by FR in [#544](https://github.com/model-checking/verify-rust-std/pull/544#pullrequestreview-4947343751) ("stubbing `checked_pow` within the affected NonZero harnesses").
  - Substitute models for intrinsics Kani cannot model were accepted with a request to swap back later ([#649](https://github.com/model-checking/verify-rust-std/pull/649#pullrequestreview-5187846135)).
  - 2024, Ch3: proving usages without stubbing, because stubbing was blocked by kani#3732, was accepted (#212 body).
- **Contract semantics clarification** (zhassan-aws, 2024-09-13): with `proof_for_contract`, a `requires` clause is an assumption and `ensures` an assertion; with `stub_verified` the roles reverse ([#53](https://github.com/model-checking/verify-rust-std/issues/53#issuecomment-2349608447)).

### (f) Contracts vs harness assertions; `proof_for_contract`; where contracts are impossible

- Review-guideline basis: contracts must "incorporate the safety conditions stated in the documentation". Functional-correctness conditions are fine "as long as they do not negatively impact verification of safety, such as over-constraining input values or causing excessive verification run time" (`doc/src/general-rules.md`, [#226](https://github.com/model-checking/verify-rust-std/pull/226), TS, 2024-12-12).
- **Thin non-UB harnesses are not enough when the challenge asks for contracts or correctness.** "The main concern for acceptance is that most Part 2 harnesses are thin proof-of-non-UB" ([#565](https://github.com/model-checking/verify-rust-std/pull/565#pullrequestreview-4041319153), FR, 2026-04-01).
- **"Decorative" contracts** (`#[requires]` with no `proof_for_contract`, mirrored by `kani::assume`) are blocking:
  - [#549](https://github.com/model-checking/verify-rust-std/pull/549#pullrequestreview-4947356961) and [#632](https://github.com/model-checking/verify-rust-std/pull/632#pullrequestreview-5187932719).
  - On the trait-impl case: "accepts the Kani trait-impl limitation but notes the criterion asks to write and prove the contract" ([#549, 2026-09-12](https://github.com/model-checking/verify-rust-std/pull/549#pullrequestreview-5187932615)).
- **When the challenge explicitly asks for a contract,** a plain proof needs "the contract or an owner-approved waiver", even if the contract slows 128-bit harnesses ([#600](https://github.com/model-checking/verify-rust-std/pull/600#pullrequestreview-4947448453)).
- **Accepted fall-backs where Kani cannot attach contracts:**
  - Generic trait methods (`max`/`min`/`clamp`/`bitor`) and `from_mut` aliasing, via assertion harnesses ([#637 FR comment](https://github.com/model-checking/verify-rust-std/pull/637#issuecomment-5414567888)).
  - Const-generic intrinsics, via contracted wrappers (kani#3345) ([#683](https://github.com/model-checking/verify-rust-std/pull/683#pullrequestreview-5188843822)).
  - Body-less intrinsics, via forwarding wrappers (kani#3325) ([#649](https://github.com/model-checking/verify-rust-std/pull/649#pullrequestreview-5187846135)).
  - Trait-object generic `downcast_unchecked`, via assume-mirror ([#639](https://github.com/model-checking/verify-rust-std/pull/639#pullrequestreview-5188108532)).
- **`assume_init` via `kani::proof` rather than `proof_for_contract`** was flagged as an incorrect comment but "not a soundness hole" ([#587](https://github.com/model-checking/verify-rust-std/pull/587#pullrequestreview-4947435658)).
- **Tool-agnostic contracts.** For Ch27, FR first required the `safety` crate's `requires`/`ensures` instead of `cfg_attr(kani, kani::requires)` as a blocker ([#587, 2026-08-16](https://github.com/model-checking/verify-rust-std/pull/587#pullrequestreview-4947435658)). The same point was non-blocking for Ch26 ([#582](https://github.com/model-checking/verify-rust-std/pull/582#pullrequestreview-4947435155)), which is an inconsistency.
- **Loop-abstraction trade-off accepted.** For `checked_pow`, a contract stating only "result is nonzero" (not the exact value) was accepted because the exact value is unprovable after loop abstraction ([#656](https://github.com/model-checking/verify-rust-std/issues/656)).

### (g) Vacuity checking and coverage

- **Organizer rule (2026-03-31).** "No vacuous proofs … A proof that passes trivially (e.g., with an unsatisfiable precondition or an empty harness body) is unacceptable." Also: "Harnesses must cover meaningful input ranges, not just trivial or degenerate cases" (`.github/copilot-instructions.md`, [#581](https://github.com/model-checking/verify-rust-std/pull/581)).
- **FR's "vacuity tooling"** is cited in reviews from 2026-08-16 onwards. The checklist items named in reviews are:
  - `cfg(kani)` / `cfg(not(kani))` body swaps,
  - `loop_invariant(true)` / `type_invariant{true}`,
  - assume-the-conclusion,
  - contracts without `proof_for_contract`,
  - reliance on the autoharness allowlist.

  The categories are labelled "T1/T2/T7" in [#603](https://github.com/model-checking/verify-rust-std/pull/603#pullrequestreview-5188000592) and [#577](https://github.com/model-checking/verify-rust-std/pull/577#pullrequestreview-5188053034). Examples: [#587](https://github.com/model-checking/verify-rust-std/pull/587#pullrequestreview-5188093198), [#683](https://github.com/model-checking/verify-rust-std/pull/683#pullrequestreview-5188843822), [#681](https://github.com/model-checking/verify-rust-std/pull/681#pullrequestreview-5188867006), [#649](https://github.com/model-checking/verify-rust-std/pull/649#pullrequestreview-5187846135).
- **Precedent of vacuity found in merged code.**
  - #637 found that the pre-existing NonZero `unchecked_mul` harnesses "were passing without checking anything", because both operands came from the same near-extreme range. The fix removed "16 previously vacuous proofs" ([FR review](https://github.com/model-checking/verify-rust-std/pull/637#pullrequestreview-4986123644); [#637 body](https://github.com/model-checking/verify-rust-std/pull/637)).
  - Those harnesses came from #338 (TS, merged 2025-06-14). The same interval pattern exists in Ch11's `generate_unchecked_mul_intervals!` (see the table in §2).
  - **This is the clearest drift:** 2024–2025 merges did not check vacuity; 2026 reviews do.
- **`kani::cover` as reachability witness.**
  - Decisive for Ch12 (§(e)).
  - Credited in Ch13 ([#638](https://github.com/model-checking/verify-rust-std/pull/638#pullrequestreview-5187725491)) and Ch27 ("all 441 covers are satisfied", [#587](https://github.com/model-checking/verify-rust-std/pull/587#pullrequestreview-5608878227)).
  - The #681 author warns that macOS timeouts were reported as success with collapsed property counts and no cover witnesses, and removed the affected harnesses ([comment](https://github.com/model-checking/verify-rust-std/pull/681#issuecomment-6037355222)).
- **Community proposal [#617](https://github.com/model-checking/verify-rust-std/issues/617)** (KyleClouthier, 2026-07-27): reachability witnesses for every assumption and contract, with CI failing on UNREACHABLE, plus mutation adequacy. No maintainer reply in the thread, and CI has not adopted it.
- **Mutation testing has appeared in practice.** FR's final Ch27 review: "Six of six seeded mutants were killed" ([#587](https://github.com/model-checking/verify-rust-std/pull/587#pullrequestreview-5608878227), 2026-10-22).
- **Harness weakening against main is checked.**
  - patricklam requested changes on Ch13 because three earlier equality checks had disappeared ([#638](https://github.com/model-checking/verify-rust-std/pull/638#pullrequestreview-5307823215)).
  - FR asks reviewers to diff replaced harnesses for smaller bounds (same PR).

### (h) CI time, memory, macOS, timeouts

- **Kani workflow** (`.github/workflows/kani.yml`):
  - Matrix `os: [ubuntu-latest, macos-latest]` × 4 partitions.
  - On ubuntu, `KANI_JOBS=2`, because 4-core/16 GB runners get OOM-killed when memory-hungry harnesses (up to about 10 GB each) run concurrently.
  - The autoharness job uses `--harness-timeout 10m --default-unwind 1000 --jobs=3`.
  - Unicode conversion harnesses were removed from autoharness because they "exceed the 10m timeout on macOS".
- **Reviewers and contributors treat 10 min per harness as the cap**:
  - #544 ("exceeded the 10-minute per-harness timeout", [comment](https://github.com/model-checking/verify-rust-std/pull/544#issuecomment-5327765778)).
  - #681 ("against the 10-minute CI cap", [comment](https://github.com/model-checking/verify-rust-std/pull/681#issuecomment-6037355222)). #681 split a harness after a macOS autoharness timeout, noting the macOS runner is more than 3× slower ([comment](https://github.com/model-checking/verify-rust-std/pull/681#issuecomment-6040379068)).
  - FR flagged CBMC-heavy unbounded harnesses and asked to "confirm the full suite is green in CI" ([#681](https://github.com/model-checking/verify-rust-std/pull/681#pullrequestreview-5188867006)).
- **macOS for VeriFast.** TS asked btj to add CI jobs "at least on macOS, as done for Kani" ([#238](https://github.com/model-checking/verify-rust-std/pull/238#issuecomment-3107146297), 2025-07-23). btj questioned the value, since macOS is LP64 like Linux ([reply](https://github.com/model-checking/verify-rust-std/pull/238#issuecomment-3107753547)). The PR was merged and `verifast.yml` still runs ubuntu-only, so the request was not enforced.
- **Architecture caveat** (VeriFast results hold for the target triple only) was added to the README at TS's request ([#238](https://github.com/model-checking/verify-rust-std/pull/238#issuecomment-3042434897)).
- **CI cost issue [#730](https://github.com/model-checking/verify-rust-std/issues/730)** (FR, 2026-10-20):
  - The autoharness jobs average about 67–69 min (worst 197 min); partitions average 34–47 min.
  - The issue proposes moving autoharness and metrics jobs to the merge queue (4 h timeout).
  - No per-harness budget change is proposed.
- **Bounds justified as CI budget are accepted where the challenge allows bounds**: Ch27 slice cap 100 ([#587](https://github.com/model-checking/verify-rust-std/pull/587#pullrequestreview-5188093198)); macOS `len <= 1024` guards ([#587 first review](https://github.com/model-checking/verify-rust-std/pull/587#pullrequestreview-4947435658)).
- **Over-constraining for run time** is discouraged by the general rules (§(f)).

### (i) Changes to std source

- **Rule**: "The solution cannot impact the runtime logic of the standard library unless the change is proposed and incorporated into the Rust standard library" (`doc/src/general-rules.md`).
- **VeriFast precedent (accepted).**
  - Ch5/Ch19 change copies of the source: annotations, inlining closures, unsafe markers, ghost-command braces.
  - celinval questioned the diff ([#238](https://github.com/model-checking/verify-rust-std/pull/238#issuecomment-2605591608), 2025-01-21). remi-delmas-3000 asked whether cosmetic or indentation changes were needed ([inline](https://github.com/model-checking/verify-rust-std/pull/238#discussion_r1945191188)) and required that CI fail on drift ([inline](https://github.com/model-checking/verify-rust-std/pull/238#discussion_r1945184054)).
  - Resolution: btj built `refinement-checker`, which checks that the original refines the verified copy, plus a `diff` against `library/` ([#213](https://github.com/model-checking/verify-rust-std/issues/213#issuecomment-2640869190); [#238](https://github.com/model-checking/verify-rust-std/pull/238#issuecomment-2934030684)).
  - remi-delmas-3000: "We also cannot ask upstream developers to change their code solely for compatibility" ([#213](https://github.com/model-checking/verify-rust-std/issues/213#issuecomment-2631852641)).
- **Upstream route used.** For Ch19, btj opened a rust-lang PR to add `unsafe` to `RawVecInner` methods that are unsound as safe functions ([#283](https://github.com/model-checking/verify-rust-std/issues/283#issuecomment-3165564267)).
- **Kani: verification-only annotation edits are allowed.**
  - #637 strengthened `loop_invariant` in `int_macros.rs` / `uint_macros.rs`.
  - Loop invariants are "inert in the `runtime.rs` safety backend" ([#600](https://github.com/model-checking/verify-rust-std/pull/600#pullrequestreview-4947448453)).
  - But removing existing ones is an out-of-scope regression ([#544](https://github.com/model-checking/verify-rust-std/pull/544#pullrequestreview-4947343751)).
- **Kani: shipping-code refactors are flagged.** "This repo mustn't change std runtime logic." Inherent `iterator_get_unchecked` twins and the `checked_sub(...).unwrap_or(0)` rewrite must be `cfg(kani)`-gated or upstreamed first ([#651](https://github.com/model-checking/verify-rust-std/pull/651#pullrequestreview-5188033558)).
- **`cfg(kani)` body swaps** that replace shipped logic are vacuity defects (§(g)). A benign for-to-while rewrite under `cfg(not(kani))` that adds loop invariants was accepted as non-blocking in Ch26 ([#582](https://github.com/model-checking/verify-rust-std/pull/582#pullrequestreview-4947435155)).
- **Ch1 text**: new `Transmutability` impls must land upstream first.

### (j) Partial solutions, reward splitting, first come first served, AI-assisted contributions

- **Rules.**
  - "Each contribution will be reviewed on a first come, first served basis" (`general-rules.md`). This concerns review order.
  - "Solutions … should be submitted as a single Pull Request."
  - Copilot instructions: "Partial solutions should be flagged" ([#581](https://github.com/model-checking/verify-rust-std/pull/581)).
- **Partial PRs were merged ("Towards #N"):**
  - In 2024 for Ch3, 6 and 11, many partial PRs by student teams, then a closing PR (§2).
  - For Ch1, partial PRs #185, #264 and #405 were merged during 2025.
  - For Ch12, partial PRs #109, #184/#338, #199, #200, #202, #345 and #346 were merged during 2024–25. The challenge was nonetheless awarded to a later single comprehensive PR, #637.
  - CZ on authoring PRs: "I don't think we should merge incomplete PRs" ([#260 r2001413952](https://github.com/model-checking/verify-rust-std/pull/260#discussion_r2001413952); about challenge docs, not solutions).
- **Ch1 completion at a threshold.** Accepted at 75% of functions, with "trivially safe" functions left unharnessed and Kani-inexpressible parts of the transmute contracts left partial (#433 body; approvals by TS and FR).
- **Approved but not "solved".** FR approved #587 (Ch27) as sound but said it "does not fully solve Challenge 27" and left three UB items for follow-ups pending [#733](https://github.com/model-checking/verify-rust-std/issues/733) ([#587](https://github.com/model-checking/verify-rust-std/pull/587#pullrequestreview-5608878227)).
- **#733's proposed rule** (FR, 2026-10-21/23, no ruling yet): accept solutions covering what Kani can express, and list caller-side "mutating immutable bytes", data races and invalid values as out of scope "until a tool can establish them". The issue says this matches Ch6, 9, 11 and 14, and the approvals of #683 and #587 ([#733 comment](https://github.com/model-checking/verify-rust-std/issues/733#issuecomment-6369823800)).
- **Competition and selection.**
  - Ch12 was decided by comparison, not chronology. #637 (opened 2026-08-19) won; #544 (2026-02-08), #565 (2026-03-24) and #600 (2026-06-12) were closed on 2026-08-25 with "We're closing this PR since the challenge has now been solved … we've merged #637 as the winning solution".
  - FR's rationale was "mostly reach similar coverage numbers" but #637 is stronger on "soundness of the proofs, not breadth" ([#637](https://github.com/model-checking/verify-rust-std/pull/637#issuecomment-5414567888)).
  - FR had earlier approved #565 (emoji-only, [2026-08-16](https://github.com/model-checking/verify-rust-std/pull/565#pullrequestreview-4947420501)), yet it lost. A single approval is not acceptance.
  - FR now ranks submissions per challenge ("front-runner", "leading of N", "prioritizing"): [#549](https://github.com/model-checking/verify-rust-std/pull/549#pullrequestreview-5187932615), [#603](https://github.com/model-checking/verify-rust-std/pull/603#pullrequestreview-5188000592), [#651](https://github.com/model-checking/verify-rust-std/pull/651#pullrequestreview-5188033558), [#638](https://github.com/model-checking/verify-rust-std/pull/638#pullrequestreview-5187725491), [#649](https://github.com/model-checking/verify-rust-std/pull/649#pullrequestreview-5187846135), [#639](https://github.com/model-checking/verify-rust-std/pull/639#pullrequestreview-5188108532), [#582](https://github.com/model-checking/verify-rust-std/pull/582#pullrequestreview-5188082622).
  - The label "Accepted Solution" is applied to front-runners before merge: open PRs #683, #681, #649, #639, #638 and #582 carry it.
- **Reward splitting.** None observed. No statement on splitting was found in issues or PRs.
  - Rewards are set by a separate rewards committee: "This should only be filled by the reward committee" (`doc/src/challenge_template.md`). CZ asked to block merge until "we get the go-ahead" from the reward committee ([#260 r2008792087](https://github.com/model-checking/verify-rust-std/pull/260#discussion_r2008792087)).
  - AWS blog (Rahul Kumar, 2024-11-20): a separate rewards committee is responsible for "reviewing and disbursing" ([AWS blog](https://aws.amazon.com/blogs/opensource/verify-the-safety-of-the-rust-standard-library/)).
  - Rust Foundation: "The challenge rewards committee is responsible for reviewing activity and dispensing rewards" ([Rust Foundation](https://rustfoundation.org/media/rust-foundation-collaborates-with-aws-initiative-to-verify-rust-standard-libraries/)).
- **AI-assisted contributions.**
  - There is no written policy in the README, the book or the PR template.
  - Organizers themselves use AI review: GitHub Copilot review instructions were added "to help us triage the coming wave of challenge solutions" ([#581](https://github.com/model-checking/verify-rust-std/pull/581)), and FR cross-references Copilot findings in reviews ([#600](https://github.com/model-checking/verify-rust-std/pull/600#pullrequestreview-4947448453)).
  - AI-disclosed PRs are reviewed on the merits. #639 (Ch29, AI-assisted) was approved as "Complete and sound as-is" and labelled Accepted Solution ([#639](https://github.com/model-checking/verify-rust-std/pull/639#pullrequestreview-5188108532)).
  - A batch of 10 AI-assisted PRs from one contributor (#640–#648) was withdrawn by the author for "no maintainer signal" ([#643](https://github.com/model-checking/verify-rust-std/pull/643#issuecomment-5427812819)), not closed by organizers.

### (k) Combining tools in one solution

- No resolved challenge combines tools. The general rules only require "All tools used by the solution must be in the list of accepted tools". Per the README: Flux, ESBMC/goto-transcoder, Kani, KMIR, VeriFast, plus RAPx documented in 2026-08 ([#491](https://github.com/model-checking/verify-rust-std/pull/491), [#631](https://github.com/model-checking/verify-rust-std/pull/631)).
  - Note: `.github/copilot-instructions.md` still lists only four tools.
- **The 2026 pending rulings explicitly contemplate complementary proofs:**
  - #733 suggests "A complementary VeriFast proof for obligations like 3 could then be an optional, separate contribution" ([#733](https://github.com/model-checking/verify-rust-std/issues/733)).
  - #734 frames Kani (catches layout-dependent bugs) and Lean/Aeneas (covers all T) as complementary ([comment](https://github.com/model-checking/verify-rust-std/issues/734#issuecomment-6349628311)).
  - Neither makes a combination required or explicitly sanctioned for a single award.
- Ch15 was accepted with a non-prover approach (testable models with a dedicated CI workflow `testable-simd-models.yml`), because its success criteria asked for tested contracts.

---

## 4. 2025 → 2026 drift and contradictions (summary)

| Topic | 2024–2025 practice | 2026 practice | Evidence |
|---|---|---|---|
| Bounded lengths under an "unbounded" clause | Not acceptable with Kani (CZ, Ch5); solved with VeriFast | Hard blocker (2026-09-12); briefly "would not block alone" on 2026-08-16 | [#29](https://github.com/model-checking/verify-rust-std/issues/29#issuecomment-2501534218), [#603 08-16](https://github.com/model-checking/verify-rust-std/pull/603#pullrequestreview-4947445617), [#603 09-12](https://github.com/model-checking/verify-rust-std/pull/603#pullrequestreview-5188000592) |
| Vacuity | Not checked; vacuous interval harnesses merged (#338, Ch11) | Systematic tooling; cover-per-assume decisive; mutation testing | [#637](https://github.com/model-checking/verify-rust-std/pull/637#pullrequestreview-4986123644), [#587](https://github.com/model-checking/verify-rust-std/pull/587#pullrequestreview-5608878227) |
| Unwind paths (VeriFast) | Ignored, accepted silently | Explicitly listed as an unproven limit of the guarantee, not yet required | [#238 body](https://github.com/model-checking/verify-rust-std/pull/238), [#734](https://github.com/model-checking/verify-rust-std/issues/734) |
| Generic T | Concrete types requested (CZ), then "no monomorphization" added (TS) | Blocking for Kani pending the #734 ruling | [#260](https://github.com/model-checking/verify-rust-std/pull/260#discussion_r1977823380), [#260](https://github.com/model-checking/verify-rust-std/pull/260#discussion_r1993550517), [#734](https://github.com/model-checking/verify-rust-std/issues/734) |
| Contracts | Plain harnesses common | `proof_for_contract` expected; "decorative" requires block; waivers need the owner | [#549](https://github.com/model-checking/verify-rust-std/pull/549#pullrequestreview-4947356961), [#600](https://github.com/model-checking/verify-rust-std/pull/600#pullrequestreview-4947448453) |
| Tool-agnostic `safety` crate | n/a | Blocking for #587, non-blocking for #582 (inconsistent) | [#587](https://github.com/model-checking/verify-rust-std/pull/587#pullrequestreview-4947435658), [#582](https://github.com/model-checking/verify-rust-std/pull/582#pullrequestreview-4947435155) |
| Review depth | Two empty-body approvals common (#238, #422, #433, #423) | Long checklist reviews by FR; second approver often defers to FR (#637 rajath-mk, #582 HuStmpHrrr) | §2, [#582](https://github.com/model-checking/verify-rust-std/pull/582#pullrequestreview-5240260116) |
| Committee | — | Roster changed 2026-08-24: btj, rafaelsamenezes, lucasccordeiro and dkcumming added; qinheping (Ch8 author), zhassan-aws and others removed | [#635](https://github.com/model-checking/verify-rust-std/pull/635) |

---

## 5. Gaps and pages that could not be read

- Tracking issue #76 (Ch3) comments: the API fetch failed twice (client error).
- #173 (Ch15), #247, #433, #656, #624 and #617 returned empty comment arrays. The PR bodies were read from squash-commit messages in git.
- #725 (Ch10, discloses bounded "unbounded" functions) and #703 (Ch17) had no human reviews yet.
- No organizer statement was found on what a user comparator may do (inconsistent order, panics, interior mutability), nor on reward splitting.
- GitHub Discussions (25 threads) contain only 2024–2025 technical Q&A, with no policy statements ([discussions](https://github.com/model-checking/verify-rust-std/discussions)).
- `general-rules.md` has had no substantive changes since 2024-12 (only end-date removal in #629, 2026-08-28).
