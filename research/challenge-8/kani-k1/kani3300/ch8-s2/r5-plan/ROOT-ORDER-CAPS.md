# Root / launch / cap table

**PROPOSED_NOT_IMPLEMENTED / NOT_RUN**. This is a planning table, not an execution request. W11 exact intake pending. All costs/order rankings are hypotheses until that intake; no measurement or launch-order trace was repeated.

| Rank | Root | Expectation / covers | Child / compile / slot seconds | RSS target | Rationale |
|---:|---|---|---|---|---|
| 1 | checker_order_corrupt | DETECTED /0 | 600 /180 /720 | 6GiB tree | Concrete2-element checker negative; no actual sorting body. Lowest structural work hypothesis, cost UNKNOWN. |
| 2 | checker_count_corrupt | DETECTED /0 | 600 /180 /720 | 6GiB tree | Concrete32-element multiplicity negative; full-value checker may still dominate, cost UNKNOWN. |
| 3 | swap_pfc | SUCCESS /4 | 600 /180 /720 | 6GiB tree | Small actual swap/PFC target and four covers; prioritize qualification information. Cost UNKNOWN. |
| 4 | sort13_weak | DETECTED /0 | 600 /180 /720 | 6GiB tree | Fixed descending13 input and no-op swap seam in checked caller copy; cost UNKNOWN, copy scope only. |
| 5 | merge_count_corrupt | DETECTED /0 | 600 /180 /720 | 6GiB tree | Actual merge32 plus constant-input assumption and tagged count corruption; assumption follows merge, so cheapness is not established. Cost UNKNOWN. |
| 6 | merge_order_corrupt | DETECTED /0 | 600 /180 /720 | 6GiB tree | Actual merge32 plus ordered-output corruption, symbolic halves; cost UNKNOWN. |
| 7 | merge32_real | SUCCESS /5 | 600 /180 /720 | 6GiB tree | Primary actual-body32/sorted-halves probe, five covers; cost UNKNOWN. |
| 8 | sort13_assumed | SUCCESS /4 | 600 /180 /720 | 6GiB tree | Symbolic13 consumer with assumed swap summary; cost UNKNOWN, DIAGNOSTIC_ASSUMED. |
| 9 | summary_witness | SUCCESS /3 | 600 /180 /720 | 6GiB tree | Constructive insertion fixture at lengths8..16 and32, full-count checks; name does not imply cheapness. Put late provisionally; cost UNKNOWN. |
| — | general32_assumed | SUCCESS /4 | DEFERRED; no budget spent | not selected | Separate full-u8/N32 invocation only by new exact option decision; excluded from prefix to avoid repeating a censored costly consumer. |
| — | general32_weak | DETECTED /0 | DEFERRED; no budget spent | not selected | Separate full-u8/N32 invocation only by new exact option decision; excluded from prefix to avoid repeating a censored costly consumer. |

Selected nine =4 expected positive observations +5 exact negatives +16 required covers. Deferred general32 pair =1 positive +1 negative +4 covers. Union remains11/20/6 in the obligation inventory; unselected roots are DEFERRED/NOT_SELECTED, outcome UNKNOWN, not passed or removed. Root IDs/required messages retain their meaning; future invocation IDs/profile/request hashes must be fresh.

Every selected root gets a reserved full720s slot. The600s child wall covers compilation, specialization/instrumentation and CBMC; compile180s is a subcap inside600, not an additional allowance.120s bounds all source/hash checks, snapshots, termination/reaping, metadata/decoder work and durable receipt publication around it. These targets need future implementation/review/GO; the current runner does not implement them. No phase gets an implicit extension if a slot is exceeded.

Stock CBMC --harness-timeout remains600s as an inner ceiling; an external whole-invocation cap may censor earlier. No assertion, cover, unwind34, full-u8 value-count domain, failure oracle, cfg or stub is weakened. Lower service limits can produce UNKNOWN and are not proof of infeasibility.

Merge and sort13 failures terminate only their singleton tree after safe cleanup; each later selected root remains scheduled. Hard global deadline/source/tool drift/uncontained orphan/storage integrity failures can still block later launches and must produce explicit NOT_RUN reasons.
