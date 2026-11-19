# Independent w13 S4 next-lengths plan review — HANDOFF

**Verdict: APPROVE (PLAN ONLY).** No required plan changes and no soundness
finding within the reviewed scope. This approves the proposed coverage and
implementation contract; it grants no implementation, execution, admission,
provider-summary or proof credit. Stop at this HANDOFF.

## Reviewed identities and method

- Sealed plan: `c0de8471801ac22b38e3290c7a6b75742135af6b`, directory
  `research/challenge-8/kani-k1/kani3300/ch8-s4/s4-full-lengths-next-plan/`.
- Std: `8faf8e62af8f82b5c46af020086f8df591b6757e`, tree
  `91f097cdb4085d30c4b94afbb843aeb34f1d3287`.
- Tool: `0aac16ef62da9e9d5645782d458593e5d78143ba`, tree
  `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`; inspected committed tool
  source in `/root/kani-upstream-ch8-s1`.
- Existing control: `3d3fb715271e3b195c6e0eee3557d5b0a6aad00d`.
- Network admission: `8896f60ae9e0ea1c706c6b8693d00e2500190676`.
  Historical fallback admission: `9bb6e2b7a18e338f532ec817f8acfd7515fc2fc9`.
- Review started on `experiment/kani-k1-kani3300g0-20261111` at
  `cf0b8f4e9f58eba06099bfb1e813fe416587c0c1`. The plan directory has no
  delta from the sealed commit. Unrelated pre-existing untracked work was left
  untouched.

I independently read the pinned algorithm, dispatch, model, existing fixtures,
tool unwind resolution and structured historical admission/cost records. I
recomputed the length/size splits, region offsets, insertion tails, merge sizes,
scratch geometry and source loop bounds without running the author's validator.
Historical results below retain their source-reported assurance; no native
evidence or proof acceptance was independently re-established.

## Findings

### 1. Coverage is exhaustive for the declared finite goals

`COVERAGE.json` retains every original structural field of the old matrix:
17 fallback rows N0..16, 33 network rows N0..32, and 50 general rows
(N0..15 shared across sizes; N16..32 split at size16). All14 classes remain.
The116 typed rows are exactly Cell fallback17 + u8 network33 + u8 general33 +
NonCopyByte general33, with no duplicate or missing typed length. The separate
large-type requirement includes N0..15 through the shared structural rows; it
does not disappear from the goals merely because those rows have no distinct
large-type entry in the116-row typed set.

All34 internal general-sort8 contexts agree with the source: at each N16..32,
left `(V+0,S+0,S+N)` and right `(V+h,S+h,S+N+8)`, h=floor(N/2).
Both temp intervals fit scratch48, are disjoint from their output intervals,
and remain distinct proof contexts. Network absolute bases are correctly
base1 and, for the second region, base1+h. The N25 mixed9/13 boundary and
N26 two-sort13 entry are correct.

Existing fallback/network N0..4 are correctly distinguished as historical
matching-dependency versus exact source-reported admissions. General remains
open. The13 bridges explicitly retain dispatch, type, initialization, scratch,
caller and provider obligations. Exhaustiveness here concerns the stated finite
length/size map; it supplies no generic or all-geometry theorem.

### 2. N8/N9/N13/N17 are the right first boundary package

At pinned `smallsort.rs:332–392`, `no_merge = len < 18`. Therefore:

| Root | Actual path | Shift tails | Final merge/copy-back |
| --- | --- | --- | --- |
| N8 | one region, insertion from1 | 1..7 | none |
| N9 | actual sort9, offset9 equals length | none | none |
| N13 | actual sort13, offset13 equals length | none | none |
| N17 | actual sort13, insertion from13 | 13..16 | none |

N8 is the last insertion-only length; N9/N13 isolate the two actual network
entries; N17 is the last single-region length and reaches insertion span17.
**N17 does not reach the final merge.** That begins at N18, appropriately
assigned to a later bridge package. N9/N13 still call shift and its entry
plumbing even though its loop has zero bodies. Literal slices
`[1..9]`, `[1..10]`, `[1..14]`, `[1..18]` implement these exact lengths.
Cell N16 next reaches fallback's threshold without introducing a Copy/Freeze
premise. The later gap lists cover every residual length without treating
boundary success as interpolation.

### 3. Roles, oracle and covers preserve the obligations

The first four control rows match the existing definitions except for planning
metadata. Their exact intended failures and Cell-active success remain required.
The four proposed positives have16 unique assertion labels and24 unique cover
labels, Original mode, null target and no summary edges.

Each positive retains independent full-domain input bytes for all34 positions,
the owned pre-state snapshot, sortedness and full-value multiplicities, complete
outside frame and a separately arbitrary outside canary. The pinned oracle's
input-value count queries suffice: equal total lengths and unchanged counts for
every input value leave no room for an additional output value. No distinctness,
input-order or value restriction is added. Canary selection restricts only its
index and leaves both outside sides feasible at every proposed length.

The three u8 model guards are the correct active specializations. Cell16 must
use its own sorting-model guard and `.get()` observations; requiring the inactive
u8 span/pair guards there would be wrong, and the plan explicitly avoids it.
All six cover predicates are feasible for each proposed length. Strictly
descending full-byte input exists through17 and, after the13-element prefix is
sorted, each remaining descending tail is below every prior element. Thus it
exercises the maximal source sift distances at N17, as claimed. Covers remain
separate existential witnesses, not input assumptions or native branch-origin
proofs. Network prefixes and their complete insertion suffixes stay within the
same active slice; the end-to-end post detects suffix corruption.

### 4. Loop arithmetic is sound; lowered sufficiency remains an execution gate

All100 per-row source-loop records agree with the pinned source formulas.
For N8/N9/N13/N17, total sift-body bounds are28/0/0/58; the maximum single
sift is7/0/0/16. The actual networks contain25/45 literal swap calls, matching
the committed pair lists. N17's algorithm comparator upper bound is45+58=103.
Cell16 has15 insertions and at most120 sift bodies/comparisons.

The oracle inner loops have depth N, not N squared; total count work is
64/81/169/289 for the proposed network roots. Every frame loop still has34
bodies; Cell initialization adds another34-body loop. Unwind36 is therefore
consistent with these source maxima. It is not established sufficient for all
lowered loops, intrinsics, array construction or contract plumbing, exactly as
`LOOP-COST.md` states.

Pinned tool `kani-driver/src/call_cbmc.rs:762–769` resolves explicit CLI unwind
before harness annotation before default unwind. With the proposed unchanged
flags and no explicit override, annotations34/36 take priority over default50.
The same file's check-flag logic retains unwinding checks unless explicitly
disabled. Actual resolved argv, loop/property inventories and unwinding results
must still be bound to each future invocation; a source bound or old inventory
cannot establish them. No unwind/check disabling is proposed.

### 5. Cost claims are honest; 600-second fit is UNKNOWN

The committed run44548842328 structured costs report native verification
3.061/3.846/4.692s for N2/N3/N4 and33.428s for N0..1, with whole-child costs
41.716/43.751/44.183/72.998s. Those measurements do not predict N8/N9/N13/N17.
Old600s timeouts are censored, so neither an exact speedup factor nor a compiler
causal attribution follows.

N9/N13 add25/45 actual compare-exchanges; N17 combines45 with up to58 insertion
comparisons and289 oracle inner bodies. Pointer/spec lowering, symbolic swaps,
duplicates, memory and solver growth can dominate those counts. No evidence
establishes that these roots, or later Cell16, fit the unchanged600s whole-child
cap. Merge cost is a separate N18+ risk. The plan preserves this uncertainty
and does not promise success or authorize an identical timeout retry.

The resource snapshot matches all10 top-level fields of the existing resource
record. Arithmetic `8*720+180+240=6180`, leaving720 within6900, is correct;
the five-root Cell envelope4020 is also correct. These are static campaign
envelopes, not measured fit, a new budget, or execution authority. Compile180
is inside child600 inside slot720. Lowered verification, compile/export limits,
memory and future deadline checks remain binding.

### 6. No hidden target/oracle change or weakened obligation found

The sealed commit adds plan documents only. Relative to the original matrix's
std, the pinned kernel changes by one cfg sort4 postcondition attribute, with
no runtime-body delta; this dependency change is disclosed. The proposed new
module will require a separately reviewed source revision and exact pins.
There is no proposed runtime algorithm, type/comparator, model, oracle, flag,
cap, control, frame, target-mode or provider change. Existing strict0,
ZERO_U/REJECT_ALL and case-specific U/property admission boundaries are
preserved. Missing locations, inactive checks or previous merge-unreachable
exclusions cannot be inherited as success.

## Validation and stop

Independent read-only Python/Git checks passed1352 assertions:11 manifest
entries,12 checksum-list entries,14 provenance inputs,26 source references,
830 retained structural fields, all geometry/cardinality/typed-length checks,
100 source-loop records,100 no-credit records, both network site lists,
10 resource fields and four unchanged controls. A separate check passed the
positive selectors/modes/caps and16 assertion/24 cover-label inventory.
Digests and structural consistency establish document/source binding only.

No compiler, Cargo, rustc, Kani, CBMC, native runner, CI, push, raw evidence
access or ledger operation was performed. No source, flags, caps, historical
evidence or admission was changed. New qualified cases:0; independently closed
proof obligations:0; independent B1/B2 credit:NONE. No subagents were used.

The coordinator can issue the separate implementation stage for the approved
four-controls-then-N8/N9/N13/N17 contract, followed by independent candidate
review and separately authorized execution. No further stage is taken here.
