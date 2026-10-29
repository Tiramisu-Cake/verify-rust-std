# Итоговые измерения C3b

Все числа ниже взяты из сохранённых bounded k1g summary/rows/peaks.
COMPLETE означает полноту разбора run, а не успешный proof всех строк.
INCONSISTENT/PARTIAL/UNKNOWN/TIMEOUT/NOT_RUN не получают proof credit.

| Набор | Build UUID | K1 / terminal без артефакта | Память driver / CBMC / Kissat, GiB | Verify wall |
|---|---|---|---|---|
| light60-before | `02bacd6a-52d0-4c9e-ad76-7fe1edb81f4c` | COMPLETE | 1.20 / 1.50 / — | — |
| heavy6-before-j3 | `311f6aa7-0e7c-4e0b-828f-eed3d3b68e56` | INCONSISTENT | 5.04 / 3.49 / — | — |
| heavy3-before-j1 | `02b3bd09-26e8-401d-84b5-b33c6d55f759` | COMPLETE | 5.03 / 3.49 / — | — |
| light12-before | `586c0d76-5fcb-454b-9147-7c6c4e6aa0ec` | COMPLETE | 1.14 / 0.77 / — | — |
| light60-covers | `bdd23fac-2fd0-4c1d-a104-04da43821dd1` | CANCELLED | — | — |
| heavy6-covers-j3 | `6196139d-3428-4e11-8c70-39dcde7c25d2` | INCONSISTENT | 5.04 / 3.32 / — | — |
| heavy-split-j3 | `e5995b00-2205-413c-8dc5-b691a0aaebda` | CANCELLED | — | — |
| timeout-baseline6 | `bc9ee7b8-a3e8-43e4-8aa7-2f91c175b2de` | PARTIAL | 1.94 / 2.85 / — | — |
| timeout-no-traces6 | `d7c18274-1281-4c8c-95fd-6bc9148102bb` | PARTIAL | 1.66 / 2.85 / — | — |
| kissat-partitions-pilot | `3d1251b6-c028-45f6-a6af-1fa11832ca0e` | НЕ СОБРАНО | — | — |
| screen-1of6 | `45a0dd0c-8f94-49d1-932b-ba5759453cac` | COMPLETE | 1.88 / 2.81 / 0.60 | 1:00:52 |
| screen-2of6 | `aad9e376-d86f-45d4-9ab1-c6b4d7157778` | EXPIRED | — | — |
| screen-3of6 | `881ea993-c360-4caa-8c70-1a1c118ebca8` | НЕ СОБРАНО | — | — |
| repair-screen2-r1 | `0709a628-b472-4f0b-b0c3-c6f0fb514883` | НЕ СОБРАНО | — | — |
| repair-priority-1 | `031fa8c0-d86b-49e9-a19e-67b4cd420725` | НЕ СОБРАНО | — | — |
| repair-priority-2 | `3b7557e0-0c2b-4d56-b1a0-ba00f52b7634` | НЕ СОБРАНО | — | — |

## Полнота текущего набора

Source prediction: 395 имён. Bound remote inventory итогового SHA отсутствует.
Принятых по identity и source freshness измеренных имён: 60.
Без актуальных измерений: 335; без SUCCESS: 15;
SUCCESS, но больше90с: 3.
Отброшенных старых merge-route rows: 4.
Полный допуск: **False**. Binding errors: [].
Pending result sets: ['screen-3of6', 'repair-screen2-r1', 'repair-priority-1', 'repair-priority-2'].

Список каждого имени, source SHA и build UUID — в ordinary-timings.tsv;
missing/not_proved/over_budget/stale — в screen-analysis.json.

## Критические последние пробы

### repair-priority-1

Результат не собран; proof/timing credit отсутствует.

### repair-priority-2

Результат не собран; proof/timing credit отсутствует.

## Бюджет и validation

Own-UUID ledger: `финальный запрос ещё не выполнен` (count / used USD / reserved USD).

53 unit tests PASS; bash -n для обоих shell scripts PASS.
Python analysis syntax PASS; git apply --check OPTION-OPTIN.patch PASS (patch не применён).
Rustfmt --check с заданным config и проверка всех изменённых Rust строк≤100 выполнены;
обязательный rustfmt повторяется после итогового commit. Локальные компиляторы не запускались.
Все proof/code изменения ограничены verify-модулями, organizer scripts/workflow и runtime не менялись.
Все commits с [skip ci], push только experiment/kani-k1-memory-20261029.
