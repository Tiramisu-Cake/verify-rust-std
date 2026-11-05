# LOOPPIN — loop contracts на новом pin: калибровка

**Выдано координатором 2026-11-05, решение владельца: проверить путь к произвольной длине.** Dispatch только после
exact-packet PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-looppin**, ветка **experiment/kani-k1-looppin-20261105** от **4fa6151b6a**
  (VEIGHTINTEG: library = кандидат v8b с контрактами на настоящих хелперах; Kani `cd355b0b`).
- Slug **looppin**, stable owner **k1-network**. Request_id/stage/ledger `looppin-*`.
- Project cap **$118.96**, свой cap **$1.20**. **Одна сборка**, retry нет. Один compile-error repair, если own spent
  + reserve ≤ cap.
- Tooling base для check-tooling: **59893bff1f**. Tooling не менять. Lane уже передаёт `-Z loop-contracts`
  (`gcb-k1.sh`, `unstable_args`).
- Окно: main 150 + closeout 30 мин.

## Контекст

LOOPINV (`92ded02d10`, ветка `experiment/kani-k1-loopinv-*`, читать RESULT-LOOPINV и код) на старом pin `9461e07a`:
3/3 TIMEOUT, CBMC ~15 GiB под DFCC loop contracts даже на тривиальной копии цикла на `[u64; 2]`. Механизм не
засчитан. Цель этапа — тот же факт на новом pin. Без работающей калибровки направление закрываем.

## Что сделать

Новый opt-in модуль `verify/looppin.rs` под `cfg(kani_smallsort_controls)`, регистрация одной строкой в `verify.rs`.
Существующие файлы не менять. ≤ 4 корня:

1. **Положительная калибровка:** маленький `while` в самом модуле (не в `smallsort.rs`) с верным
   `kani::loop_invariant`, произвольная длина в пределах малого массива. Ожидается SUCCESS.
2. **Отрицательный контроль:** тот же цикл с заведомо ложным инвариантом. Ожидается FAILED на проверке инварианта
   (`expect_check` по фактическому тексту).
3. **При запасе:** копия внешнего `while` из `insertion_sort_shift_left` с инвариантом
   `v_base < tail <= v_end` (в терминах копии) и `stub_verified(insert_tail)` вместо тела, на u64, len —
   `kani::any()` в пределах backing. Не утверждать произвольную длину: это ещё фиксированный backing.

Атрибуты на настоящие циклы в `smallsort.rs` этот этап не ставит.

Исходы различать: SUCCESS, FAILED на нужной проверке, неподдержанная операция (точный текст), compile error,
TIMEOUT/память (peak RSS из bounded peaks).

## Сборка

Kind diagnostic, `controls: true`, jobs 1, gcb-e2-standard-4, `harness_timeout_minutes` минимальный разумный.

## Коммиты

- Library-research коммит и research-коммит отдельно, `[skip ci]`. Push без force.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание сборки: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход. Не
  опрашивать статус в цикле.

## RESULT

**RESULT-LOOPPIN.md**, ≤ 30 строк: identities; таблица строк (status, check, время, peak RSS); сравнение со старым
pin (LOOPINV); вывод — работает ли путь loop contracts на новом pin и что нужно для следующего шага.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep. Raw logs, archives, Cloud Logging и credentials не
  читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наш код, наши RESULT и документация Kani. Чужие PR, их ветки и код не открывать.
- Runtime `smallsort.rs`, workflows, скрипты и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **LOOPPIN ЗАВЕРШЁН**, одна стадия, затем стоп.
