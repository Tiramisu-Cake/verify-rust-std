# RESULT-KANI3300-U3C — сравнение завершено с ограничениями evidence
Clean `87c1def4-07d7-4233-84ea-5b01eda765a2`: Cloud FAILURE / TOOL_ERROR; tool build PASS.
U1 `36f4b5c4-c9fc-4f44-b9d0-537889168954`: Cloud FAILURE / INCONSISTENT (`native timing missing/corrupt`); tool build PASS.
Exact source/request/patch/tree и tooling checks PASS; hashes — IDENTITIES.json и {clean,u1}/POST-BUILD-OBSERVATIONS.json.

|exact root|uninit|clean, wall s|U1†, wall s|v2 U3B, wall s|
|---|---|---|---|---|
|contracted_roundtrip_harness|on|TIMEOUT, 162.497|TIMEOUT, 180.002|Kani-reported OOM, 50.284|
|contracted_roundtrip_harness|off|SUCCESS, 3.237|SUCCESS, 0.967|SUCCESS, 5.400|
|contracted_uninit_read_harness|on|FAILED / slow, 124.869|FAILED / slow, 143.950|Kani-reported OOM, 51.350|
|contracted_uninit_read_harness|off|SUCCESS, 1.069|SUCCESS, 0.917|SUCCESS, 5.107|
Clean timeout — классификация координатора (162s > per-test150); U1 timeout — вывод по outer-limit180s, wall180.002 и exit−9; timed_out не сохранён.
Оба FAILED установлены own-output `VERIFICATION:- FAILED`; actual Failed Check UNKNOWN: KT2 не сохраняет excerpt при native PASS; targeted field отсутствует.

|MU-free контроль write_u16_harness|clean, wall s|U1†, wall s|v2|
|---|---|---|---|
|PFC, uninit on|SUCCESS, 1.471|SUCCESS, 1.168|NOT_RUN|
|PFC, uninit off|SUCCESS, 1.069|SUCCESS, 0.917|NOT_RUN|
|plain, uninit on|SUCCESS, 0.767|SUCCESS, 0.667|NOT_RUN|

† Все U1 строки — UNVALIDATED_DIAGNOSTIC_ONLY из diagnostic_artifacts.native; INCONSISTENT не переопределён ручной сверкой identities/argv/diagnostics.
SUCCESS читается из own-output diagnostic SUCCESSFUL, а не из native PASS; off-negative без correctness credit. Нет independent B1/B2 credit.
На старых базах positive-on тоже не прошёл; OOM явно сообщён только v2. Существовавший upstream OOM и регрессия от проходившего root не установлены.
Причинность buffer-in-MEM_INIT_STATE открыта; MU-free SUCCESS не воспроизводит общий PFC/uninit отказ. RSS/kernel OOM confirmation отсутствуют.
Расход: clean $0.1755 + U1 $0.2295 = $0.4050; reserve0, cap$0.95; ровно2/2 сборки, repair не предусмотрен.
Следующий отдельный этап: уменьшенный MU-repro и сохранение actual Failed Checks/timeout в bounded отчёте; не переходить сразу ко второму marker.
