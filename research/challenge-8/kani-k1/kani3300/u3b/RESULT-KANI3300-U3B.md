# RESULT-KANI3300-U3B — PRE-BUILD, native NOT_RUN
Research branch: experiment/kani-k1-kani3300u3-20261111; request kani3300-u3b-20261111-02.
Full test commit: 0ab9cc703aed799f6f73d826b60281a4632ab585; build tree 4de67d7ead14bdc4060d2b08060e7ee7651625bb.
Pin: f046b70644e113be0df9c22c2e6ea44a65a57566; tooling: 3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c.
Build patch SHA256: d9417e68ec3ee9c8c27bb8e7ac829e2af712c4d124ac59078416ab34feebd85c.
Request SHA256: f839b593b08b53953a408528e8833d54be50dc9abff281c27291e18c09b46f4a.
Production byte-equal U3 repair1; details STATIC-CHECKS.json / PRE-BUILD-KANI3300-U3B.md.

|offset|selector|expected Kani|actual/time/memory|
|---:|---|---|---|
|0|isolated PFC positive|SUCCESS|NOT_RUN / UNKNOWN / UNKNOWN|
|1|positive no-uninit|SUCCESS|NOT_RUN / UNKNOWN / UNKNOWN|
|2|isolated PFC negative|uninit FAILURE u16|NOT_RUN / UNKNOWN / UNKNOWN|
|3|negative no-uninit|SUCCESS diagnostic only|NOT_RUN / UNKNOWN / UNKNOWN|
|4|frame negative|assigns FAILURE, user line22|NOT_RUN / UNKNOWN / UNKNOWN|
|5|wrap positive, all7 including empty_harness|SUCCESS|NOT_RUN / UNKNOWN / UNKNOWN|
|6|plain buffer negative|uninit FAILURE u16|NOT_RUN / UNKNOWN / UNKNOWN|
|7|review positive, all7|SUCCESS|NOT_RUN / UNKNOWN / UNKNOWN|
|8|U1T overwrite-copy negative|uninit FAILURE [u8;2]|NOT_RUN / UNKNOWN / UNKNOWN|

PFC terminal causes and comparison: UNKNOWN, no native build submitted.
Static validate9/production equality/selected source-golden identity/fresh build tree PASS; prior rustfmt6 retained.
Pinned prepare-kani PASS exit0: manifest-only patch diffstat1595 <=4096 bytes; tooling unchanged.
Предложение: новый exact PRE-BUILD GO; полный test-коммит сохранён; готовность v2/known limitation решать после native.
Spend $0; reserved $0; proposed $0.540; cap $0.60; Builds0.
Exact PRE-BUILD review/GO pending; no dispatch authorization inferred.
