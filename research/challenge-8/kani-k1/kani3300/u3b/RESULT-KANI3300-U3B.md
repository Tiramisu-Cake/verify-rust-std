# RESULT-KANI3300-U3B — known limitation PFC/uninit
Build `9f964706-4b89-4340-a1ee-022aa23ecbe9`: Cloud FAILURE; TOOL_ERROR, gate=false; native7 PASS/2 ERROR; tool build PASS.
Head `a3e082da37f65095f85ebf998170775d7b75db9c`; request `kani3300-u3b-20261111-02`.
Full test commit `0ab9cc703aed799f6f73d826b60281a4632ab585`; build tree `4de67d7ead14bdc4060d2b08060e7ee7651625bb`.
Build patch SHA256 `d9417e68ec3ee9c8c27bb8e7ac829e2af712c4d124ac59078416ab34feebd85c`; production byte-equal U3 repair1.
Request SHA256 `f839b593b08b53953a408528e8833d54be50dc9abff281c27291e18c09b46f4a`; pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; tooling `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c` check PASS.

|offset|root / selector|terminal cause / outcome|selector wall s|RSS|
|---:|---|---|---:|---|
|0|contracted_roundtrip_harness, uninit on|Kani-reported OOM (native-field excerpt, kani_stdout:7)|50.284|UNKNOWN|
|1|same root, uninit off|SUCCESS, require-success PASS|5.400|UNKNOWN|
|2|contracted_uninit_read_harness, uninit on|Kani-reported OOM (native-field excerpt, kani_stdout:7)|51.350|UNKNOWN|
|3|same root, uninit off|SUCCESS diagnostic control, require-success PASS|5.107|UNKNOWN|
|4|frame_negative|PASS: assigns FAILURE *var_7, golden binds user line22|124.419|UNKNOWN|
|5|wrap-u3-positive, including empty_harness|PASS: all7 SUCCESS|6.037|UNKNOWN|
|6|plain buffer negative|PASS: uninit FAILURE u16|1.620|UNKNOWN|
|7|review-positive|PASS: all7 SUCCESS|9.850|UNKNOWN|
|8|U1T overwrite-copy|PASS: uninit FAILURE [u8;2]|1.771|UNKNOWN|

Оба OOM установлены явной строкой Kani и именем root, не отсутствием Failed Checks; kernel/cgroup/RSS подтверждения нет.
Native4–8 property/count claims bound by exact source/golden + validated native result; literal success excerpts не сохранены producer.
У negative PFC Failed Checks в compiletest_stdout:10 — эхо отсутствующего golden; в own output диагностический поиск false; ожидаемый uninit FAILURE не получен.
KT2 не содержит per-root memory fields; whole-run RSS/wall MISSING, cap not tracked; время в таблице включает selector wrapper, не solver-only.
Предложение: **known limitation** PFC+modifies+uninit на standard4; два изолированных 29-line repro в [PFC-LIMITATION.md](PFC-LIMITATION.md); механизм UNKNOWN.
Полная U3/PFC приёмка остаётся OPEN; unexpected SUCCESS on-negative не наблюдался; off-negative SUCCESS не даёт correctness credit.
Evidence: [POST-BUILD-OBSERVATIONS.json](POST-BUILD-OBSERVATIONS.json), bounded native/native-field в evidence/native-9f964706/; без raw logs и general proof credit.
Расход $0.1620, резерв $0, cap $0.60; одна сборка, repair не разрешён; стадия завершена, дальнейшие Builds только по новому GO.
