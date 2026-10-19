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

### R1 Build3 terminal / singleton candidate (20:36Z)

Build `e7b74165-b8ac-4d40-b541-396540104e08` FAILURE20:26:29Z, charge598s/execution597s. Total3builds1705s, no active Build. Fresh smallsort-brief plus Reader v6/Processor0.7.0 receipt/index hashes verified; compact derived artifacts R1-BUILD3-*. All7 build milestones observed exit0. Prefix and fullbody sourceexact/HRTB/firstContinue/actualfirstcall claimsTrue, exporter/decode/refinement0,VF1, jointCURRENTfalse/true/panicFalse. Recovery now passes CURRENT owner closes and first foreach; next observed error list.rsspec181 missing foreach(t3,own<u64>) on second/tail foreach close (derived context verified188:487). Whole-Build causal_status UNKNOWN. Five dependent groups explicitly sourceNOT_RUN_PREFIX_PREREQUISITE_FAILED; B1 sourceall_matchedTrue. No independent proof credit/B2.

Next concrete hypothesis recorded before implementation: existing checked length_drop/length_take/drop_length facts establish both original singleton list lengths1 and last suffix nil before callback lifetime. Six pure proof commands; no heap/owner assumptions, no entry=CURRENT equality, no weakened posts/whitelist/CFG. Tool08d6a578/profile82973e1e/patch4aa84aa5 unchanged; only first-callback.py differs among106proofrecipepaths. Seven synthetic tests and14/16/14/18 source-only preflight PASS. Independent Luna High final GO, R1-SINGLETON-REVIEW-20261018.json. Full mandatory matrix retained for next Build; actual success unknown.

## Final Build4: 5f668cd9-fb34-4570-ad1c-4b97abbb36d0

All results below are source claims or bounded Reader observations, not independent full proof credit.

| Obligation/control | Latest established result | Remaining limit |
| --- | --- | --- |
| Translator/exporter/decoder/console/refiner builds, tracked-md preparation/compile | all individual exit0 | No target proof implication |
| Exact source/HRTB/local first Continue/official first-edge qualifier | source flagsTrue | Positive flags alone do not establish all admission controls |
| Normal false CURRENT restoration | joint false/true/panic flagFalse | No separate successful branch receipt |
| Normal true restoration before tail.read/guard | actual_read_lineTrue; points_to(tail0,_) missing at read | read/guard success and full resources not proved |
| First Continue-panic full CURRENT recovery/frame/F | not established; jointflagFalse | No separate successful unwind receipt |
| Source-linked prefix with explicit cut | INCONCLUSIVE; exporter/decode/refinement0,VF1 | Placeholders not allowed at verified214:17-23 |
| Full-body unchanged-post diagnostic | INCONCLUSIVE; exporter/decode/refinement0,VF1 | missing points_to<u64>(tail0,_) verified203:42-48 |
| lost_reference_fraction | source NOT_RUN_PREFIX_PREREQUISITE_FAILED | no intended-negative credit |
| lost_reference_token | source NOT_RUN_PREFIX_PREREQUISITE_FAILED | no intended-negative credit |
| lost_current_f | source NOT_RUN_PREFIX_PREREQUISITE_FAILED | no intended-negative credit |
| lost_cell_owner | source NOT_RUN_PREFIX_PREREQUISITE_FAILED | no intended-negative credit |
| HRTB/binder/Output/projection/lifetime/admission controls | group source NOT_RUN_PREFIX_PREREQUISITE_FAILED | no admission/control credit |
| First-unwind intended mutant, late-Cleanup refusal, new5CURRENT negatives | same admissiongroup sourceNOT_RUN | static definitions retained; execution not established individually |
| Ordinary normal/unwind smoke | source PASS | bounded smoke only |
| Helper positive +3 negatives | source bounded fragment /3EXPECTED_CONTROL | no first-callback/B2 credit |
| SelectedDrop positive +6 negatives | source all_matchedTrue | bounded positive fragment only, acceptedFalse |
| Generated admission/default-off/compatibility | retained, parent sourceall_matchedTrue | individual nested details not projected Processor |
| Receiver/end/retirement4 | source4EXPECTED_CONTROL/all_matchedTrue | no late actual Drop proof |
| B2 / independent proof credit | OPEN / none | shift,gap,loop,latepanic,actualcleanupDrop,fullcallerposts remain |

### Final missing-fact attribution

- Reader v6 index/receipt available, hashes match; no Reader transport failure.
- Separate successful normalfalse/normaltrue/panic source receipts not present in supported projection; jointFalse is in source result. Presence of other raw source receipts unknown, not NOT_RUN.
- Prefix exact statement is not extracted in Processor's bounded diagnostic (line text WITHHELD); location/error/sourceSHA known. First try static pinned templates; optional separately authorized bounded audit: Build5f668cd9, prefix verified214±4 and source hash.
- Nested source binding/prerequisites/tool_hashes/ordered patches and individual admission details are not extracted Processor (UNSUPPORTED_NESTED_SOURCE_DATA), not Reader unavailable. Candidate closure/pins independently checked statically.
- Whole Build cause/stage order/last completed remain UNKNOWN/NOT_ESTABLISHED in Processor; presence of source causal receipt unknown. Separate admin request, if needed: exact causal receipt/failed command and exit only for5f668cd9; no raw archive/log download.
- None of these reporting gaps justifies retrying unchanged inputs or claiming PASS/NOT_RUN from absence.
