# S1 criteria assessment — run44416629057

| Root | Native | Checks S/F/U | Covers SAT/required | Literal roles | S1 assessment |
|---|---|---:|---:|---|---|
| checker_order_corrupt | FAILURE | 15/1/8 | 0/0 | 1/1 | provisional source-reported |
| checker_count_corrupt | FAILURE | 24/1/1 | 0/0 | 1/1 | provisional source-reported |
| s3_swap_u8_geometry | SUCCESS | 309/0/4 | 7/7 | 3/3 | provisional source-reported |
| s3_sort4_u8_separate | SUCCESS | 309/0/7 | 4/4 | 4/4 | provisional source-reported |
| s3_sort4_u8_same_alloc | SUCCESS | 351/0/5 | 7/7 | 5/5 | location decision pending |
| s3_insert_tail_u8_rel16 | UNKNOWN | 0/0/0 | 0/9 | 0/3 | no completed result |
| s3_merge8_u8_separate | SUCCESS | 369/0/9 | 6/6 | 4/4 | provisional source-reported |
| s3_merge8_u8_same_alloc | UNKNOWN | 0/0/0 | 0/11 | 0/5 | no completed result |
| sort13_weak | FAILURE | 16/1/8 | 0/0 | 1/1 | provisional source-reported |


Checks exclude covers. Zero counts on unfinished roots mean no property inventory exported, not zero obligations. All seven completed native results have exact singleton selectors and same-invocation literal source-site bindings. The three negatives each fail exactly their intended assertion: S2_NEG_CHECKER_ORDER at sorting_s2_batch.rs:140, S2_NEG_CHECKER_COUNT at134, S2_NEG_SORT13_WEAK at149. There are no additional failures, failed unwinding checks or safety failures in these completed inventories. Producer failure_kind PANICS_ONLY on negatives is the stock classification of the intended literal assertion, not evidence of an incidental panic. Property classes named unsupported_construct have SUCCESS; exported unsupported_constructs arrays are empty.

Strict producer outcome remains **0/9 expected matches**: REJECT_ALL, proposal DISABLED, unknown/role-U rejected. No policy, ledger qualification or native verdict is rewritten. S1 criteria yield six provisionally eligible source-reported results and sort4same eligible conditional on a location-only decision. The two capped leaves have no completed native result. This is an assessment for root/coordinator; admission and B1/B2 credit remain NONE.

Every U occurrence has its own root, full producer ID/class/description/status, site, exact source hash/context, effective cfg, provider context, predicate, premises and source-local argument in QUALIFICATION.json/U_instances (42 entries). No U is waived because of a status, cover, library name or whitelist. Arguments cover guarded abs_diff subtraction, constant formatting shift, guarded align-1, guarded allocation-size division, sort4 boolean offsets, merge length8 arithmetic, and each guarded checker index/count increment. Frozen93f158 is a disabled reference; no historical instance is substituted for this invocation and no proposal argument is automatically reused. Independent caller-to-MIR origin remains UNKNOWN.

PFC source-reported registration and contracted-function context match native core metadata for all six candidates; actual-body targets are swap_if_less, sort4_stable, insert_tail and bidirectional_merge. Selected PFC harnesses have no ordinary/verified stubs. The sort13 weak negative deliberately has its source-bound ordinary seam replacement and is never an actual sort13 proof. Existing ordinary/cfg/provider/contract-stack/lexical static gates pass. This is Profiles v4 SOURCE_REPORTED assurance, not independent MIR/compiler transformation proof.

All independent bytes remain0..255. Domain/backing/offset/order, concrete u8/KeyLess, source/outside frame, canaries, destination MaybeUninit and typed post-call loads are per-row bindings in JSON. Stock checks and successful system checks stay visible. No separate experimental uninit-checks or valid-value-checks flags were enabled; no independent initialization theorem is claimed. SAT covers (24/44 selected positive source covers observed) show witnesses at exact required source sites; they do not prove U, frame, generic allocation or callers. Forty-four covers and71 total literal role sites are source inventories, not native check counts. Completed inventories contain43 literal role sites; incomplete leaves retain the remaining28 as UNKNOWN.

Positive SUCCESS roles, with exact producer matches and coordinates in JSON:

- s3_swap_u8_geometry: S3_SWAP_ACTIVE, S3_SWAP_EXACT_TRANSFER, S3_SWAP_FULL_FRAME
- s3_sort4_u8_separate: S3_SORT4_SEPARATE_ACTIVE, S3_SORT4_SEPARATE_SORTED_FULL_COUNT, S3_SORT4_SEPARATE_SOURCE_FRAME, S3_SORT4_SEPARATE_CANARIES
- s3_sort4_u8_same_alloc: S3_SORT4_SAME_ACTIVE, S3_SORT4_SAME_SORTED_FULL_COUNT, S3_SORT4_SAME_OUTSIDE_FRAME, S3_SORT4_SAME_SOURCE_FRAME, S3_SORT4_SAME_CANARY
- s3_insert_tail_u8_rel16: S3_INSERT_ACTIVE, S3_INSERT_SORTED_FULL_COUNT, S3_INSERT_OUTSIDE_FRAME
- s3_merge8_u8_separate: S3_MERGE8_SEPARATE_ACTIVE, S3_MERGE8_SEPARATE_SORTED_FULL_COUNT, S3_MERGE8_SEPARATE_SOURCE_FRAME, S3_MERGE8_SEPARATE_CANARIES
- s3_merge8_u8_same_alloc: S3_MERGE8_SAME_ACTIVE, S3_MERGE8_SAME_SORTED_FULL_COUNT, S3_MERGE8_SAME_OUTSIDE_FRAME, S3_MERGE8_SAME_SOURCE_FRAME, S3_MERGE8_SAME_CANARY

No assumed summary is promoted. S3-2 must preserve exact identities and caller geometry, value domain, frame/init/locality and provider applicability, and obtain whatever root/coordinator admission decisions remain required.
