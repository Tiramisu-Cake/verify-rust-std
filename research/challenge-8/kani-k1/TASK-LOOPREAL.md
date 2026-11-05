# LOOPREAL — loop invariants на настоящих циклах insertion-пути

**Выдано координатором 2026-11-05, продолжение пути B после принятого LOOPPIN.** Dispatch только после
exact-packet PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-loopreal**, ветка **experiment/kani-k1-loopreal-20261105** от **4b05b98a3c**
  (LOOPPIN: library = кандидат v8b + opt-in `verify/looppin.rs`; Kani `cd355b0b`).
- Slug **loopreal**, stable owner **k1-network**. Request_id/stage/ledger `loopreal-*`.
- Project cap **$118.96**, свой cap **$2.00**. **До двух сборок** G1/G2, G2 — после разбора G1 и GO координатора.
  Retry нет. Один compile-error repair на сборку, если own spent + reserve ≤ cap.
- Tooling base для check-tooling: **59893bff1f**. Tooling не менять. Lane передаёт `-Z loop-contracts`.
- Окно: main 240 + closeout 30 мин.

## Контекст

LOOPPIN (`4b05b98a3c`, читать RESULT-LOOPPIN и `verify/looppin.rs`): калибровка верного/ложного инварианта
работает; копия внешнего `while` из `insertion_sort_shift_left` со `stub_verified(insert_tail)` на backing 5 —
SUCCESS, 121 с, CBMC 5.9 GiB. Параллельно идёт WIDEDOMAINS (bounded PFC `insert_tail` до tail 19 через unwinding);
его код не трогать и на него не опираться.

Цель — путь к **произвольной длине**: стоимость доказательства с loop contracts не должна расти с длиной.

## Что сделать

1. **Инварианты на настоящих циклах в `smallsort.rs`**, только атрибутами под `cfg(kani)`
   (`#[cfg_attr(kani, crate::kani::loop_invariant(...))]` и, если нужно, `loop_modifies`), по конвенциям `core` в
   этом репозитории (пример — `num/imp/dec2flt/decimal_seq.rs`). Тела, сигнатуры и существующие контракты не менять.
   - внешний `while` в `insertion_sort_shift_left`;
   - внутренний `loop` в `insert_tail` (`sift`, `gap_guard.dst`). Если на `loop` с `break` атрибут не принимается
     или нужна правка тела — записать точную причину и ограничиться внешним циклом.
2. **PFC с растущим backing** (новый opt-in модуль `verify/loopreal.rs` под `cfg(kani_smallsort_controls)`), u64,
   компаратор с произвольным ответом:
   - `insert_tail` на настоящем теле с инвариантом: backing 8, 32, 128 (tail `kani::any()` в пределах);
   - `insertion_sort_shift_left` на настоящем теле со `stub_verified(insert_tail)`: len и offset `kani::any()` в
     пределах backing 8, 32, 128. Домен заглушки должен совпадать с доказанными PFC `insert_tail` (тот же T, F,
     backing); если не совпадает — consumer не засчитывается.
   Смысл: если время почти не растёт от 8 к 128, это аргумент за независимость от длины.
3. **Отрицательный контроль:** ложный инвариант на настоящем цикле (в отдельной cfg-копии или через контрольный
   cfg, не меняя runtime-вариант) должен падать на invariant-step.
4. **Регрессия (обязательна):** инварианты на настоящих циклах меняют способ проверки всех харнессов, которые через
   них проходят, в том числе ordinary v8b и харнессы `sort` вне smallsort, потому что CI организаторов передаёт
   `-Z loop-contracts`. Статически найти такие корни (grep по вызовам) и включить 3–4 представительных ordinary-корня
   с прежними временами для сравнения.

## Сборки

Kind diagnostic, `controls: true`, jobs 1, gcb-e2-standard-4, лимит на корень минимальный разумный (≤ 10 мин).
G1 ≤ 10 строк. G2 — по итогам (например backing 512 или исправление инварианта).

## Коммиты

- Library-коммит (атрибуты в `smallsort.rs` + модуль) и research-коммит отдельно, `[skip ci]`. Push без force.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание сборки: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход. Не
  опрашивать статус в цикле.

## RESULT

**RESULT-LOOPREAL.md**, ≤ 40 строк: identities; точный текст инвариантов; таблица строк (status, check, время,
peak RSS) по backing; рост времени от длины; регрессия до/после; что это даёт для произвольной длины и чего ещё не
хватает (generic T/F, merge, остальные циклы, termination).

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep. Raw logs, archives, Cloud Logging и credentials не
  читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наш код, наши RESULT и документация Kani. Чужие PR, их ветки и код не открывать.
- Тела runtime-функций, workflows, скрипты и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **LOOPREAL ЗАВЕРШЁН**, одна стадия, затем стоп.
