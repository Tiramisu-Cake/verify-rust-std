# checker_order_corrupt: eight-row U proposal (DISABLED)

Evidence is source-reported/native metadata plus source-local conditional reasoning only. Profile remains REJECT_ALL; enabled=false; qualification=0; independent B1/B2=none; proof credit=0. No control is admitted.

Frozen intake: `1d8a06c8bd418de6261a1cbbb24ea0f35bae1712`; source: `513341f41ce53833a279571401c924bdddddb6c8`; tool: `0aac16ef62da9e9d5645782d458593e5d78143ba`. Exact identities, file hashes, invocation/cfg and read boundary are in INPUTS.json. SOURCE-CITATIONS.json retains exact source spans and full file hashes. No new artifacts or native runs were obtained.

The native observations contain 24 checks: 15 SUCCESS, the intended literal S2_NEG_CHECKER_ORDER FAILURE, eight UNREACHABLE, and zero covers. This argument uses the actual predicate, not covers or statuses as proof. PROPOSAL.json retains every native row verbatim, including full property IDs, class, description, file, line and location_display.

## Fixed-source derivation

At sorting_s2_batch.rs:136-141, the proof root constructs input=[1u8,2] and out=[2u8,1], then calls snapshot/post with u8,KeyLess<u8>. Lines1-7 import the sorting_model facade. In sorting_model.rs:137-158 the source specialization active_model!(u8) dispatches to active_snapshot/active_post. This is source-supported dispatch, not independently verified compiled dispatch.

CAP is 32 (model:9). active_snapshot (64-89) returns an owned valid snapshot with len2 and copied bytes1,2. The length guard in active_post:92 passes. At i=1, the loop test1<2 is true; Project<u8>::value (30-37) reads the byte. The predicate at model:97 is out[1]<out[0], namely1<2, true, with safe indices1 and0 and subtraction1-1. Line98 returns false. It precedes both line100 and the whole counting phase104-118. Therefore every source candidate below has zero visits on this exact source path. The literal checker assertion receives false; agreement with the observed failure is corroboration, not independent causality proof.

## All eight distinct native rows

Every ID below has prefix `slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.`; class is assertion, status remains UNREACHABLE, reported file is /home/runner/work/kani/kani/export/library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs. Full unabridged rows and binding gaps are in PROPOSAL.json.

| Suffix | Line:column | Native description | Source expression candidate | Local reason / source loop instance |
| --- | --- | --- | --- | --- |
| 4 | 100:9 | attempt to add with overflow | `i += 1` | Line100 follows the line97 true branch and line98 return in the first order iteration. The increment is never evaluated. If reached with i=1, 1+1=2 is safe; this safety fact alone does not establish native U. ordering-loop tail; i=1. |
| 5 | 106:21 | index out of bounds: the length is less than or equal to the given index | `before.values[i]` | Line106 is in the multiset outer body after the order loop. The earlier return at line98 prevents line104 and every multiset iteration, so this bounds check is never evaluated. multiset outer loop (source initializes i=0 at line104). |
| 6 | 111:16 | index out of bounds: the length is less than or equal to the given index | `before.values[j]` | Line111 lookup is in the inner counting loop at lines110-114, after the returning order test. Neither loop is reached, so this bounds check is never evaluated. multiset outer i / inner j loops (j initializes0 at line109). |
| 7 | 111:44 | attempt to add with overflow | `old_count += 1` | Line111 increment additionally requires equality before.values[j]==query. The whole inner loop is unreachable after line98, independent of that equality, so the addition/overflow check is never evaluated. multiset outer i / inner j; conditional before.values[j] == query. |
| 8 | 112:16 | index out of bounds: the length is less than or equal to the given index | `values[j].value()` | Line112 output lookup belongs to the same unreachable inner loop. The order-test return occurs before any multiset query or counter is initialized, so this bounds check is never evaluated. multiset outer i / inner j loops. |
| 9 | 112:45 | attempt to add with overflow | `new_count += 1` | Line112 increment additionally requires output projection==query. The whole inner loop is unreachable after line98, independent of that equality, so the addition/overflow check is never evaluated. multiset outer i / inner j; conditional values[j].value() == query. |
| 10 | 113:13 | attempt to add with overflow | `j += 1` | Line113 increment is at the inner counting-loop tail. The preceding order-test return prevents entry to that loop, so the addition/overflow check is never evaluated. multiset inner-loop tail. |
| 11 | 118:9 | attempt to add with overflow | `i += 1` | Line118 increment follows the inner loop and the line115 count comparison/possible return. The first order-test return already precludes all of that, so the addition/overflow check is never evaluated. multiset outer-loop tail after old_count != new_count test. |

## Limits and invalidating changes

Native rows report active_post::<u8> and root selection, but supply no independently established caller edge, loop/SSA instance or property-expression-to-MIR/AST binding. Line111 and112 each contain more than one expression; metadata suggests the lookup/addition candidates, without establishing compiler lowering. Assertion suffixes are opaque identifiers. All eight rows retain these UNKNOWNs separately. The source path predicts only i=1 in the ordering loop and no visits to the listed sites; it does not report measured native iterations.

The intake catalogue lists keys for export/properties/binding metadata; a key list is not binding proof. Intake SOURCE-TRACE contains frozen control-side spans for protected evidence rejection; it is not an active_post compiler-origin trace. The new SOURCE-CITATIONS adds only locally available frozen Git text. Provenance has source-reported std/tool/cfg/selector identities. Recorded binary hashes agree, but physical realpath/stat/device/inode/etc. are absent, setup inventory is missing, and unobserved intermediate changes remain UNKNOWN. Neither matching hashes nor exact source coordinates resolves those gaps. In particular, sorting_model.rs is absent from the emitted changed_file_sha256 and source_under_test.file_sha256 lists. Its exact hash/text here is established from the frozen Git source object; the reported std SHA/tree agrees, but no separate model-file measurement or compiled-origin binding is supplied.

If out becomes [1u8,2], the first comparison becomes2<1=false: line100 executes, then the multiset loops execute. Each candidate expression is visited (its error condition can still be safe). If the comparison is hypothetically changed to >= with original out,1>=2=false also invalidates the dominance argument. These are meaningful source-local counterfactuals, without edits to source or native execution. Changes to lengths, input/output, projection, dispatch, guard/return, source/tool/cfg or actual instance require a fresh argument. Matching multisets alone does not avoid rejection of the original reversed order. No argument transfers to new positive leaves or arbitrary callers.

## Handoff boundary

Historical STOPPED/prefix0/firstrowINTERRUPTED-UNKNOWN, later8 NOT_RUN, deferred8 NOT_SELECTED, qualification0 and proofcredit0 are preserved. This is a reviewable proposal only, never a rollout or an automatic U whitelist. Roles may never become UNREACHABLE success. Any future enablement needs separate exact candidate review by a non-author and coordinator GO. S3 pathfix13/review14 proceed independently; #4591 GO14ab HOLD until owner+1 morning remains unchanged. No CI/tool reactivation, source/control/map/policy/test-runtime edits, history/ledger/budget writes, external publication or new acquisition occurred.
