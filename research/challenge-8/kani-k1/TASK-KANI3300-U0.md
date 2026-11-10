# KANI3300 U0 — разведка: `-Z uninit-checks` на путях SmallSort, Kani `f046b70644` без патчей

**Выдано координатором 2026-11-11, GO владельца на ночную работу по kani#3300 (общий бюджет проекта ≤ $6.40).**
Research-ветка, в подачу не идёт. Dispatch только после exact-packet PRE-BUILD review/GO координатора. Runtime
**Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani3300**, ветка **experiment/kani-k1-kani3300-20261111** от `c98d7cee0d`
  (tooling base; пин Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, nightly-2026-10-23). Tooling, пин, toolchain
  не менять. **Без `kani_patch`** (чистый пин).
- Slug **kani3300**, stage `kani3300-u0`, stable owner **k1-merge**, request `kani3300-u0-*`.
- Свой cap **$0.80**: одна сборка `kind: diagnostic`, `uninit_checks: true`, controls on, inventory off,
  standard4/jobs1, флаги организаторов. Repair — только если факт + новый резерв ≤ cap. Окно: main 240 + closeout 30.
- Параллельно в tmux другой агент готовит патч Kani (U1) в `/root/kani-fix-3300` — его не трогать; другие
  worktree (`kani5116`, `kani-traitpfc`) не трогать.

## Цель

Повторить нашу прежнюю 6-строчную таблицу `-Z uninit-checks` (на старом пине cd355b0b) на `f046b70644` и
классифицировать каждую строку; найти **первое препятствие** на путях scratch (`[MaybeUninit<T>]`) и дать его
минимальный repro. Источник прежних строк — наш код: `git show 690bdea1c7:library/core/src/slice/sort/shared/smallsort/verify/pincheck.rs`
и `…/verify/assembly.rs` (дерево 690bdea1c7), страница результатов
`git show fc72b71178:research/challenge-8/kani-k1/en/kani-pin-check.md` (раздел 2).

## Library-изменения

Новый opt-in модуль `verify/uninit_probe.rs` целиком под `#[cfg(kani_smallsort_controls)]` + одна строка в
`verify.rs`. Перенести на текущее дерево шесть строк с той же семантикой (тот же T/F/N/геометрия/assert/cover;
имена допустимо сохранить); если исходный fixture опирается на модуль, которого больше нет, — перенести минимально
нужный код в `uninit_probe.rs` и записать отличия. Core-код (`smallsort.rs` и др.) не менять.

| Row | Что (как в старой таблице) | Ожидание по смыслу |
|---|---|---|
| U1 | калибровка: `MaybeUninit<u8>` без записи → `assume_init` | FAILED на uninit-чтении |
| U2 | калибровка: тот же слот после записи → `assume_init` | SUCCESS |
| U3 | `raw_uninit_read_sensitivity` | FAILED на uninit-чтении |
| U4 | `swap_contract_four_positions_u8` (fn-pointer comparator, как было) | SUCCESS |
| U5 | `sorted_permutation_insert_tail_u8_n2` | SUCCESS |
| U6 | `permutation_merge_u8_n4` (scratch) | SUCCESS |
| U7 | новый: U4 с **function item** comparator вместо fn pointer | SUCCESS |
| U8 | новый: один реальный путь через scratch — `small_sort_general_with_scratch` для u8, N4, function item comparator | SUCCESS |

Для каждой строки зафиксировать: status, failed/total, все failed checks дословно с локацией, класс
(**unsupported** / ожидаемый uninit-FAILED / ложный отказ / SUCCESS / TIMEOUT). «Ожидание по смыслу» — то, что
показал бы корректный инструмент; расхождение — результат, не повод менять harness. `--harness-timeout 3m`
(8 × 3 + 30 = 54 мин, резерв ≈ $0.73), unwind — по прежним строкам и телам.

## Приёмка

- Сборка завершена, identity (pin без patch, head, request) и check-tooling PASS; все 8 строк классифицированы по
  bounded evidence; сравнение с таблицей cd355b0b (что изменилось).
- Для первого препятствия на scratch-пути (U6/U8, иначе первого unsupported) — минимальный standalone repro
  (≤ 30 строк, в стиле `tests/expected/uninit/`, `--edition 2021`) в `kani3300/u0/` + указание места в исходниках
  `/root/kani-src-f046b70644/kani-compiler/src/kani_middle/transform/check_uninit/` (файл:строка), которое его
  отвергает. Repro не запускается в этой стадии.
- Статика: изменены только `verify.rs` (одна строка) и `verify/uninit_probe.rs`; rustfmt — ноль diff.

## RESULT

**RESULT-KANI3300-U0.md**, ≤ 35 строк: identities; таблица 8 строк; сравнение с cd355b0b; первое препятствие,
repro-путь, место в исходниках; расход; что это значит для патча U1.

## Коммиты, ожидание, запреты

- Library-коммит отдельно от research, все `[skip ci]`; push без force; глобальный git config не менять; без
  `git stash`.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание: `k1g.sh watch BUILD`, затем конец хода.
- Evidence — bounded `k1g.sh` summary/rows; raw logs, archives, credentials не читать; прямых GCS/storage/download/
  logging нет. Никаких локальных cargo/rustc/Kani/CBMC; rustfmt через обёртку
  `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --edition 2024 --config-path
  research/challenge-8/kani-k1/codefix/rustfmt.toml`. Никаких Actions/PR/issue/комментариев на GitHub.
- Чужие PR verify-rust-std, их ветки и код не открывать.

Маркеры `REVIEW REQUEST <sha>` / **KANI3300 U0 ЗАВЕРШЁН**, одна стадия, затем стоп.
