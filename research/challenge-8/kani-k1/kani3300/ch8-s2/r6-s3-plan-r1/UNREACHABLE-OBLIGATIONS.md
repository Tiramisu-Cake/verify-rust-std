# Swap positive roles and four unreachable checks — source-local plan

All changes NOT_APPLIED. W11 ebd77a9 VERDICTS.json `/inventory/0` reports native
swap SUCCESS, 314 SUCCESS/4 UNREACHABLE checks, four SATISFIED covers and absent
S2_ACTIVE_SWAP_PFC/S2_SWAP_EXACT_TRANSFER/S2_SWAP_FULL_FRAME descriptions.
Literal normalization in LABELS.md preserves and exposes those three distinct
positive obligations; exact pair/frame predicates and loop-instance coverage
remain mandatory. A new label cannot turn an unreachable assertion into a
proved success or close the strict gate by itself.

The following exact W11 property coordinates are matched only to pinned bd62
source text, with hashes in INPUTS.json. They do not establish caller-to-MIR or
contract/property origin. Do not attribute a check to a particular contract from
its name or source line alone.

| W11 swap property / source location | Pinned source expression | Source-local obligation for a later candidate |
|---|---|---|
|num::<impl usize>::abs_diff.assertion.1; num/uint_macros.rs:3222|under self<other, other-self|Prove branch-local unsigned subtraction safe (other>=self), including equality in opposite branch; preserve default overflow checks and full usize domain. Establish actual caller/property binding before calling it a swap-contract check|
|num::<impl usize>::abs_diff.assertion.2; num/uint_macros.rs:3224|otherwise self-other|Prove self>=other from branch complement; retain original same-allocation/range-disjointness and arithmetic predicates. A pure arithmetic lemma alone does not prove pointer validity/provenance|
|fmt::Arguments::<'_>::from_str.assertion.1; fmt/mod.rs:820|s.len()<<1, in static Arguments construction|Identify exact panic/formatting instance in the native chain. Shift count1 is within usize bit width; prove relevant definedness without changing compiler checks. Literal kani::assert can remove a formatting path, but fresh inventory must establish what actually disappears; no assumed causal claim|
|ptr::const_ptr::<impl *const ()>::is_aligned_to.assertion.1; ptr/const_ptr.rs:1479|align-1 after power-of-two guard|Prove returning guard implies align!=0 and subtraction safe; retain non-power-of-two panic and all pointer/alignment premises. Do not replace it by an address-only ownership claim or assume guard truth|

Proposed useful bounded arithmetic roots could establish the abs_diff branch
theorems on arbitrary usize operands and the nonzero-power-of-two implication.
They would be auxiliary actual/checked lemmas with new identities, not qualified
swap providers and not an extra run allocated by this plan. Prefer proving them
within the first S3 candidate if native evidence is needed; no std runtime body
rewrite is proposed just to change check status. Source-level reasoning here is
not a Kani proof or independent check-origin audit.

Future validation must compare complete pre/post native/rich inventories,
preserve unsupported-construct records, default safety assertions, intended
role sites, literal descriptions and required covers, and reject missing/null/
wrong-source/wrong-instance/unreachable role records. Each check that disappears
requires an explained source/instance difference; a filtered report is not a fix.
If U remains in a fresh candidate, the current zero-unreachable success gate
still refuses qualification. No reclassification, whitelist, check removal,
compiler flag change or policy waiver is authorized here. Continue independent
leaf preparation without claiming swap admission. Any future policy decision
would be separate from this source-local proof plan and the frozen R5 verdict.
