# KANI3300 Г1 STEP1 — анализ CI (ISSUED 2026-11-13 → worker15)

Это верификация корректности, не security-работа. Только локальный Python/чтение исходников; никаких cargo/rustc/Kani/CBMC/CI/скачиваний.

## Вход
- CI run 43393496999 (Tiramisu-Cake/kani, branch uninit-ci/h1-resource-20261113, CI-only HEAD 2657d2bc3b).
  Две попытки до неё (43392342927, 43392900278) упали в обвязке до CBMC: python3.10 `str(signal.SIGTERM)` в тесте
  и строгая проверка `cbmc --version` (фактически `6.11.0 (cbmc-6.11.0)`). Исправлено координатором коммитами
  1c492f014 и 2657d2bc3 в /root/kani-fix-3300-h1-ci; источник 4f64 не менялся. Записать это в INPUTS/RESULT.
- Receipts всех 10 плеч и build уже скачаны координатором: /root/kani3300-h1-ci/r3/<CASE>/ (h1-tools не скачивать).
  Новые скачивания не нужны и не разрешены.
- Пакет и оракулы: kani3300/h1-step1/ (MATRIX.json, ORACLES.md, CI-REQUEST.md), STEP0: kani3300/h1-step0/.

## Предварительные цифры координатора (проверить, не принимать на веру)
| Case | first CNF vars / clauses | Kani RSS | Итог |
|---|---|---|---|
| E8-P1 | 256 060 / 585 791 | 0.25 GiB | 1 of 316 failed |
| D10-P1/P2 | 850 492 / 2 064 959 | 0.56 GiB | 1 / 3 failed |
| C12-P1/P2 | 3 228 220 / 7 981 631 | 1.81 GiB | 1 / 3 failed |
| B14-P1/P2 | 12 739 132 / 31 648 319 | 6.59 GiB | cbmc exit 15, без вердикта |
| A16-P1 | — | 6.37 GiB | cbmc exit 15 |
| F12-P1 no-slice | 580 817 / 6 407 436 | 0.85 GiB | 1 failed |
| H16-P1 UF-always | 25 257 555 / 203 206 | 5.74 GiB | 1 failed |
Наклон по B14−C12: ≈1926 клауз и ≈774 переменных на элемент таблицы = 321·6 и 129·6, т.е. D=6, C=0 (совпадает со STEP0 R1).

## Задачи
1. Ресурс: независимо извлечь счётчики/статусы всех плеч; fit клаузы/переменные = A·2^b + r по E8/D10/C12/B14 с остатками;
   экстраполяция на 16; F12 и H16 как дискриминаторы; exit 15 у B14/A16 — классифицировать по receipts (watchdog/RSS/сигнал).
   Итог SUPPORTED / COUNTEREVIDENCE / INCONCLUSIVE по правилу §2.6 R3 и PLANNER-R3-H1-REVIEW.md.
2. Семантика (новое, важно): P1 при всех завершённых плечах падает ровно на
   `kani::internal::apply_closure::<MaybeUninit<u8>, {closure@scalar-pfc-legal.rs:14:17}>.unsupported_construct.1`
   — "Cannot determine layout for an unsupported type {closure...}" (ensures-closure). P2 — 3 отказа: две uninit read в
   `std::ptr::read::<u8>` (safety_check.1/.4) плюс, вероятно, тот же Unsupported. По чтению исходников 4f64 и upstream bf9c58e662
   (Kani clones read-only) выяснить: откуда этот Unsupported (какой pass/visitor, почему closure layout не определяется),
   есть ли он на upstream без Part 1 (по коду), связан ли он с S3/M2-B (delayed-UB через registration trampoline) или с
   B1-изменениями resolve_call; почему он не был виден раньше (16 бит → OOM до вердикта; quick-тесты frame/clause).
   Дать конкретную гипотезу и минимальный путь исправления (не реализовывать). Проверить, соответствует ли P2 оракулу
   «ровно одно упавшее свойство — uninit read в ensures» и что значат два safety_check одного read.
3. Сохранить в `kani3300/h1-step1/`: RESULT-H1-STEP1.md (≤40 строк), FIT.json, CASES.json, SEMANTIC-FINDING.md.
   Не менять source/goldens/historical files.

Research-коммит [skip ci], автор Tiramisu-Cake <igkharin@gmail.com> через -c, глобальный git config не менять, без push.
Финальная строка `READY <sha>`.
