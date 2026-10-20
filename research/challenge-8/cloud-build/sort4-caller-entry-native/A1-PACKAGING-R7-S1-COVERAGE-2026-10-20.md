# R7 S1 Evidence coverage

Build `025378b9-d36b-4837-bd19-6df8ed1471c4` is reported by the Brief as `VERIFIED_ARCHIVE_AND_INVENTORY`, with source-reported run exit 0 and verdict `NOT_ACCEPTED_AS_REPORTED`. The Brief’s outer `evidence_complete=true` describes archive processing. The inner `proof-audit.json` says `evidence_complete=false`, `diagnostic_complete=false`, `matrix_complete=false`, `proof_credit=false`, `proof_verdict=null`, and `first_causal_stage=UNESTABLISHED`. These are source claims; independently established proof credit remains 0.

The complete catalogue identified `proof-audit.json` as file ID `cc20cf422e3f3828330adb99a0a55222711961bbb855f3b12dfc360c537a3e96`, SHA-256 `ea903197e23bbf2a3b01605779116cce3e8d5c76664a3854da82a279d38b0f5d`. Its archive SHA-256 is `5ca376510b641093d8ce8fc498442385338b6a078d97848c5785bac34d9f5e21`; index SHA-256 is `0ee96db82e2a0974b685496bd1cbd4c114e096f2315d0add224905f8f9c38591`. The root object was read in two explicit pages at offsets 0 and 20; the 26 row objects were each read through an exact, complete JSON pointer with the expected file SHA. Request IDs and row values are in [the structured evidence record](A1-PACKAGING-R7-S1-EVIDENCE-2026-10-20.json).

| Case | Status | Observed stage | Observed outcome | Reason | Reader request ID |
|---|---|---|---|---|---|
| N-alpha-valid | NOT_RUN | null | null | expected input identity or run pins unavailable | `b74281fc26150bf1288e4220bbc5ce91e173af17b4f472cac8faa9b27f429949` |
| N-binder-collapse | NOT_RUN | null | null | expected input identity or run pins unavailable | `a8277efe73046ba63f5502ae6bb21e5615b00108893f56683dc1b023ec50b520` |
| N-binding | NOT_RUN | null | null | expected input identity or run pins unavailable | `10be3c85e358f04e96eef6eb5dce041f632c291ee1fb4020c7b200c23488939f` |
| N-clause-redirect | NOT_RUN | null | null | expected input identity or run pins unavailable | `c329b2c95dba761a1d9d639a86f3334abd8341fb37a4d1f71ac8c11d0404b20a` |
| N-clauses | NOT_RUN | null | null | expected input identity or run pins unavailable | `3e1052afd10c99aadcc4b3926f84df954a2c0dc403cdc3720dc27a9d8c45c1d3` |
| N-default-contract | INCONCLUSIVE | null | null | current raw source observation missing | `c7cdc7d3ecc069a1e47f1430b1df9b6102158befbbb5fe6a241460ba16523b8c` |
| N-duplicate | NOT_RUN | null | null | expected input identity or run pins unavailable | `1fa50e927e4799552bf1cb5be183c1749b4d51eeb1e52746eef2d543bef9e262` |
| N-false31 | NOT_RUN | null | null | null | `ea51de9f3e386e47cf6cd27809dcd56c35444a898ae32b0ef124dc41c40852e2` |
| N-free-region | NOT_RUN | null | null | expected input identity or run pins unavailable | `67f45a7146870ab1f6878fe10c1e5013876c970691c6e07df5b16354885bf7c2` |
| N-freeze-contract | INCONCLUSIVE | null | null | current raw source observation missing | `83c3d95d15aaf82d7b766f2160da161fdc5d6321177bbf1bd29c0f3f5a81d6d7` |
| N-no-F | NOT_RUN | null | null | expected input identity or run pins unavailable | `68a3a7ffbbce580b887f4197bddfaef5bdc729608cebe2ab13c74c68fc1fda62` |
| N-region-swap | NOT_RUN | null | null | expected input identity or run pins unavailable | `71838f64eb4ac0fbb9588bfba31ce055983377295b089d939ba47d0b51342ade` |
| N-source | NOT_RUN | null | null | expected input identity or run pins unavailable | `4df4b3519a82de14afe3496a2f2d8ef8bf6b517273b0f0dbc05ddb321635ada5` |
| OFF | INTENDED_CLASSIFIED | frontend | BASELINE_ONLY | null | `e6de1e11b5f3766a0c66f1cb4c58c99b3f68e07eb8bc2282530df17a522cd578` |
| P-dispatch | INCONCLUSIVE | null | null | current raw source observation missing | `46b549e35b81da50b230efc7dcf04b204fc5b87d42e3de7ed6d7de70cf9d45f0` |
| P0a | INCONCLUSIVE | null | null | current raw source observation missing | `3d72c0d332b6fc5df4a66af91aee4db87172ea740b503f9c8a2710d37e9c8aee` |
| P0b | NOT_RUN | null | null | null | `43c44891e75118ac9fa10d07af1456feb8616f0c648c9dcc410cfd70a35cd331` |
| P0c | NOT_RUN | null | null | null | `98da7eb8adba198195763eda01982627a32e147fddfe3d5f1066d048d632c1e3` |
| P1 | INCONCLUSIVE | null | null | current raw source observation missing | `0cccbba6154ab65c8e33da1fee1e32b805e5508e9cd4caf9fc951f9d8edd5f0e` |
| R1 | INTENDED_CLASSIFIED | NONE_OBSERVED | POSITIVE_INTENDED | null | `fae93323411d3f7509a7e9acd9823f0871e6a6c0f9d455b79681fb0bde46cc41` |
| R2 | INTENDED_CLASSIFIED | NONE_OBSERVED | POSITIVE_INTENDED | null | `1454fbd790c86159bfb6ca90c1e61609665e7bd002242adb493c1b8d5a75bcf9` |
| R3 | INTENDED_CLASSIFIED | NONE_OBSERVED | POSITIVE_INTENDED | null | `3c5b95bccda567406fcfe9de743abcf05b432c12c4c16dfc37ba80e1b42e4d3d` |
| R4 | INTENDED_CLASSIFIED | verification | NEGATIVE_INTENDED | null | `7a1ed8576653e7f94d06cd1a805c2871fa0abe35c099a667e58779b71c25d4d0` |
| R5 | INTENDED_CLASSIFIED | verification | NEGATIVE_INTENDED | null | `4434415913d4b0eb4036a6e0361a0c1ca37be0e0ce69063e8d7359fecab9350c` |
| R6 | INTENDED_CLASSIFIED | verification | NEGATIVE_INTENDED | null | `ddc9decf829fbb476b6a320068fb6c0ae7a2b8b859ac88f714a9ca6c0ea32add` |
| R7 | INTENDED_CLASSIFIED | NONE_OBSERVED | POSITIVE_INTENDED | null | `b668c2b3ddd427482d533dbda49eef5efed92e4aa282382b3da2a80c58e12bf4` |

All 26 case objects report `proof_credit=false`; only the eight intended-classification rows report `matrix_gate_passed=true`. The 13 `NOT_RUN` rows are not inferred from missing evidence: each is the exact status reported in its row. `N-false31` retains a null reason, stage, and outcome. The five INCONCLUSIVE rows are P0a, P1, P-dispatch, N-default-contract, and N-freeze-contract.

## Focus lifecycle and tool receipts

The first blocker is P0a, `source-constructor`, `adapter_error`, with `execution_started=true`: `RuntimeError: A1-FOCUS: published A1 profile identity`. Its row remains INCONCLUSIVE with no observed verifier stage/outcome. P1 reports the same adapter error at its P1 stage, also INCONCLUSIVE. N-false31 is explicitly NOT_RUN with null stage, outcome, and reason. These observations do not establish a compiler or verifier failure in P0a/P1 and do not exercise the dead-code hypothesis.

The tool receipt source reports `A1_TOOL_BUILT_UNRUN_PROOF`, build exit 0, 23 reconstruction patches, and proof credit false. It records the final R patch SHA `9cdca995…`, final C patch SHA `e7cdc8a8…`, and tool head `f76012fb…`. The separately built R-only native reference reports exit 0, `c_patch_applied=false`, translator SHA `9391bff0…`, and proof credit false. These are tool-build claims, not proof results.

R7 itself is source-classified `INTENDED_CLASSIFIED` / `POSITIVE_INTENDED` with matrix gate true and proof credit false. Its detail is `FRESH_VF0_CANDIDATE_RAW_REVIEW_REQUIRED`: paired support and input identity are reported true, proof AST captured, all seven recorded stages exit 0, and `first_causal_stage=NONE_OBSERVED`; `actual_caller_proved=false`, `actual_sort4_proved=false`, and `accepted=false`. The collector explicitly reports that its pass is not proof. The Brief’s `run_exit=0` and this candidate record do not establish verification acceptance.

The catalogue and exact JSON requests were read through the ordinary Evidence Brief/Reader path. A concurrent Reader attempt failed identity-token acquisition; it returned no source data. Subsequent sequential requests succeeded. No raw logs or archives were opened or downloaded, no local evidence copy was used, and no `NOT_RUN`, proof credit, or causality was inferred from a no-match. Historical R6/S3 records were not copied into this S1 record.
