# Independent W14 S4P1-r1 intake and location review

Disposition: **APPROVE_INTAKE_WITH_PRESERVED_LIMITS**. No blocking or nonblocking findings. Exact intake `842984040e87b8b8594653634b72df7d800ca198` / task `0f39a22f0148755e7ba881736e77b54f74b01cb5` / root inputs `27cdf2a7e7895344aa3be9c47b2867a9298c3e0f`. All eight requirements are individually addressed in AUDIT-COVERAGE.json.

Location recommendation: **RECOMMEND_TWO_EXACT_CASES**, separately **NOT_APPLIED**. LOCATION-DECISION.json pins each full dictionary, same-invocation inventory/counts, role/cover/U/guard partitions and protected tuple. Root must verify the actual committed review, then root/coordinator independently decide any location/admission change. No active producer, parser or policy changes follow from this review.

| Root | Native verdict | Properties | Status U |
| --- | --- | --- | --- |
| checker_order_corrupt | FAILURE | 24 | 8 |
| checker_count_corrupt | FAILURE | 26 | 1 |
| sort13_weak | FAILURE | 25 | 8 |
| s4p_cell_count_corrupt | FAILURE | 64 | 1 |
| s4p_fallback_b01_n00_02_fullbyte | SUCCESS | 228 | 4 |
| s4p_fallback_b01_n03_04_fullbyte | SUCCESS | 227 | 4 |
| s4p_network_b01_n00_02_fullbyte | UNKNOWN_INCOMPLETE_EXPORT | UNKNOWN | UNKNOWN |
| s4p_network_b01_n03_04_fullbyte | UNKNOWN_INCOMPLETE_EXPORT | UNKNOWN | UNKNOWN |

Strict expected matches remain0/8. Two fallback native SUCCESS inventories have228/227 records, each220 checks(216SUCCESS+4U), covers8/7 SAT. Exactly one unlocated class=`unreachable`/status=`SUCCESS` record per fallback, full selector`.unreachable.1`, both file/line present-null and exact lib.rs:0:0 display. All other227/226 properties are positively located. Four literal SUCCESS roles, length SAT3/2 plus five feasible witnesses, three SUCCESS guards and one unwind SUCCESS per fallback remain mandatory gates. Class unreachable SUCCESS is distinct from status UNREACHABLE.

Four negatives each contain one intended located literal FAILURE; the Cell control also has ACTIVE SUCCESS. Source [0,1]->[0,0] is still sorted and fails count; sort13weak is fixed descending [12..0]. No claim that actual sorting failed. Positive fallback source uses all34 independent full logical bytes, initialized Cell new/get/set, V34/base1, exact N0..2/3..4, actual small_sort_fallback, no positive stubs/providers. Full multiplicity count and complete outside frame remain intact. U arguments are sound site-local definedness explanations under stated premises, not independently established emitted-property/MIR proofs. Every observed unsupported SUCCESS guard remains recorded, without general support claims.

The sealed packet is complete at36 committed files/35 manifest hashes and119 structured members. Independent566 checks pass. Exact frozen reporting rerun reproduces1163 checks,29 authentic reader adverse checks,66 hypothetical location adverse checks,220 supplemental checks,11/11 main and9/9 supplemental projections. The66 tests restrict a hypothetical exact packet boundary; they do not fix a runtime reader or prove a common emitter. Fresh local/upload-only replay agrees; selected_roots is genuine int8, terminal schema exact, all8 ordered starts/seals, no global stop. Protected E0/pre/worker BEFORE/AFTER/controller post checks pass for every row, including UNKNOWN rows; original errors, epochs, omitted events, exits and supervision remain in the immutable intake. No missing-AFTER recovery was used.

Both network results remain UNKNOWN after CHILD600_WALL_INCLUDING_COMPILE: wholechild601.428/601.401s; initial-export compile upper48.195/45.976s; sampled RSS3515064/3516320KiB against observed effective6291456KiB. Signal15/original exit-15, verified shutdown/reap/no survivors; outer/slot/compile180/RSS cutoff not observed. Native verification time/peak and exact backend/symex subphase remain censored UNKNOWN. Fallback native verification140.741771488/144.622441392s differs from wholechild189.05/193.6s, setup total721.679s and campaign1779.707s. Sampled nonatomic PGID/owned-census RSS does not establish a kernel/cgroup/tree true peak. Caps unchanged; no inference that more memory solves the wall timeout.

Old sort4same f740/merge8 ff193 and their independently reviewed exact cases were compared only in original-run scope. Same display-zero/null shape is not common-emitter, source or MIR proof. No suffix/wildcard/stdlib/unreachable waiver, coordinate substitution or future-run rule is recommended.

Only two finite fallback SOURCE_REPORTED candidates may proceed to a separate exact admission decision; possible union0..4 remains conditional. Network, fallback5..16/network5..32/general/initmask/provider/function-summary/caller/ownership/panic/generic trait/fullN16N32/MIR/B1B2 remain OPEN/NONE. No proof obligations closed. ProducerUNKNOWN, U-REJECT_ALL, proposalDISABLED and history unchanged. No acquisition/raw/ZIP/GCS/native/fullValidate/CI/model/settings/delegation/source/policy/ledger/publication action.
