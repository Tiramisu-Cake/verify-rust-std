# R1: obligations и границы evidence

Все результаты ниже — source claims из проверенных derived Reader records,
кроме отдельно помеченных observed stage exits/diagnostic excerpts. Целостность
VERIFIED_ARCHIVE_AND_INVENTORY не является independently accepted proof.
Whole-Build causal_status UNKNOWN в обоих terminal reports. B2 OPEN.

| Run | Build / proof=infra / tool / profile SHA | Charge |
| --- | --- | --- |
|1|2f7ba4a0 /762932d3 /52ba7e25 /84949dd9|528s|
|2|b4c78447 /251a83ad /2a507868 /566457f4|579s|
|3|e7b74165 /e87f0d09 /08d6a578 /82973e1e; submitted|reservation960s|

[Run1 exact provenance/results](R1-BUILD1-RESULT-20261018.json),
[Run2 exact provenance/results](R1-BUILD2-RESULT-20261018.json).

| Obligation/control | Run1 | Run2 | Remaining boundary |
| --- | --- | --- | --- |
| Translator/exporter/decoder/console/refiner/tracked-md builds | observed0 | observed0 | Actual target proof separate |
| First campaign invocation | target records present | target records + CAMPAIGN_RETURNED receipt | Dispatch gives no proof credit |
| Exact prefix / fullbody source | source_exactTrue both | source_exactTrue both | Fullbody posts not weakened |
| Actual first FnMut statement | source traceFalse | source traceTrue | TraceFalse alone is not NOT_RUN |
| HRTB registration | sourceTrue | sourceTrue | Registration alone not full admission |
| Local first Continue mechanism | sourceFalse | sourceTrue | Does not establish resources |
| Official first-Continue positive | sourcequalifiedTrue/refinement0 | sourcequalifiedTrue/refinement0 | Mutant/controls separate |
| Normal false CURRENT resources/Return | jointflagFalse | jointflagFalse | Separate successful branch receipt absent |
| Normal true CURRENT resources before tail.read | jointflagFalse | jointflagFalse | Separate successful branch receipt absent |
| First Continue panic CURRENT resources/frame | jointflagFalse | jointflagFalse | Which recovery branch failed is not established |
| Explicit-cut prefix theorem | INCONCLUSIVE/VF2 | INCONCLUSIVE/VF1 | No successful prefix credit |
| Separate fullbody diagnostic | INCONCLUSIVE/VF2,Not_found3138 | INCONCLUSIVE/VF1,missingown(entryxshead) | No fullbody proof; firstcall reached, later read/shift/gap/late traceFalse |
| lost_reference_fraction | explicitNOT_RUN_PREFIX_PREREQUISITE_FAILED | same | Not intended resource rejection |
| lost_reference_token | explicitNOT_RUN_PREFIX_PREREQUISITE_FAILED | same | Not intended resource rejection |
| lost_current_f | explicitNOT_RUN_PREFIX_PREREQUISITE_FAILED | same | Not intended resource rejection |
| lost_cell_owner | explicitNOT_RUN_PREFIX_PREREQUISITE_FAILED | same | Must reject missing physical array cell after valid recovery |
| First admission group | explicitNOT_RUN_PREFIX_PREREQUISITE_FAILED | same | None of grouped controls credited |
| Compiler Output/binder count/order/identity/ref mismatch/ambiguous projection/sourceF/u64 | group skipped | group skipped | Individual runs not claimed |
| Ghost F/u64/lifetime | group skipped | group skipped | Individual runs not claimed |
| Legacy8 HRTB regressions | group skipped | group skipped | No transfer from historicalprofile |
| Late Cleanup marker refusal | group skipped | group skipped | No new late Cleanup mechanism |
| Official first-unwind intended mutant | group skipped | group skipped | Positive qualifier alone insufficient |
| NEW CURRENT pointer/binder/owner/array/append5 | not part of candidate | not part of candidate | Required after owner approval for Run3 |
| Ordinary normal/unwind smoke | sourcePASS | sourcePASS | Bounded smoke only |
| Helper positive+3negatives | sourceboundedfragment +3expected | sourceboundedfragment +3expected | Not firstcallback or B2 |
| Selected Drop positive+6proof negatives | sourceall_matchedTrue | sourceall_matchedTrue | Bounded normal domain only |
| Generated admission/default-off/compatibility | sourceparentall_matchedTrue | sourceparentall_matchedTrue | Nested individual detail not projected Processor |
| Receiver/end/retirement4 | sourceall_matchedTrue | sourceall_matchedTrue | Not late-panic proof |
| New independent proof credit / B2 | none /open | none /open | Shift/gap/loop/latepanic/actualDrop/fullcallerposts remain separate |

## Missing-fact attribution

- Reader index is available for both runs; hashes agree with receipt. No Reader
transport blocker and no raw evidence fallback.
- Nested B1 admission/compatibility and service receipt source_binding/prerequisites
are not projected by Processor. This does not mean source absent.
- Per-branch successful CURRENT receipts are absent from supported source results;
only a jointfalse claim exists. No PASS/NOT_RUN is inferred perbranch.
- Global cause/order/lastcompleted are not established by Processor despite all
stage summaries being retained. Presence of a source causal record is unknown.
- Run1 new service paths outside/cases were not projected. Run2 corrected paths
show both classifications, confirming supported Reader projection for those paths.
- No admin audit was performed. Old e3252f3a remaining questions and bounded request
are in R1-BASELINE-INDEX-ASSESSMENT-20261018.md; no need to request translator build
confirmation again. Run3 tests a new concrete CURRENT candidate, not old history.
