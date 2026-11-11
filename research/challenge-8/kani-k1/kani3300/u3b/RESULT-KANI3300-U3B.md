# RESULT-KANI3300-U3B — PRE-BUILD, native NOT_RUN
Research branch: experiment/kani-k1-kani3300u3-20261111; request kani3300-u3b-20261111-01.
Kani: 0ab9cc703aed799f6f73d826b60281a4632ab585; tree ef32d0009a730c26dc99e8ab828744128de69b15.
Pin: f046b70644e113be0df9c22c2e6ea44a65a57566; tooling: 3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c.
Patch SHA256: 129fa3742499ad06700e35519a711e2b555a29d6f2eedcff5b21236c7795bb4e.
Request SHA256: cf447c650c10c2559e66d81f95f2d4f0dc53c0941c6090a66f12e6fbb5fa77db.
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
Static validate9/rustfmt6/production equality/fresh applied tree identity PASS.
Pinned prepare-kani BLOCKED: REQUEST_INVALID: patch diffstat exceeds bounded report size (4483 >4096 bytes).
Предложение: сначала отдельно разрешить устранение preflight blocker; готовность v2/known limitation не установлена.
Spend $0; reserved $0; proposed $0.540; cap $0.60; Builds0.
Exact PRE-BUILD review/GO pending; no dispatch authorization inferred.
