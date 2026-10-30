# ASSEMBLY — объединённый кандидат Part 1: INTEG + UNSTABLE8 + прямой u64 N6..8

Дата: 2026-10-31. Исполнитель: Codex, одна свежая сессия, окно до 3 ч. Worktree `/root/verify-rust-std-kani-assembly`
(сессия открыта в `/root` — работать только в этом worktree, `cd` в него), ветка `experiment/kani-k1-assembly-20261031`
от `6817cb831c` (итог INTEG, review GO_WITH_NITS). **Бюджет Cloud Build: не более $3 и не более 3 сборок** (свой
список build UUID/request_id; agent label `k1-network` общий и расходы не разделяет), пул k1-standard4; `CAP_USD
73.96` не менять; перед каждой сборкой `k1g.sh budget`. Сборку ждать **только через `k1g.sh watch BUILD` и завершать
ход**. Результаты своих сборок — штатно через `k1g.sh summary/peaks/inventory/log-grep/log-lines/check-tooling`; не
применяются Evidence Brief и процедуры Select/Merge, заменённые штатным K-1 интерфейсом. Pin Kani `9461e07a`,
toolchain, flags, lane-файлы не менять. Actions/CircleCI — нет. Ветки `submission/*` не трогать: ветку подачи и CI
организаторов делает координатор. **Срок: кандидат с inventories и controls — как можно раньше; ночью по нему
запускается единственный полный CI организаторов.**

## Источники (переносить только library-diff указанных блоков, не целые файлы/деревья)

- **UNSTABLE8** `255935369e` (ветка `experiment/kani-k1-unstable8-20261030`, `verify/types.rs`, library `78c040559f`):
  в ordinary — `types::sorted_permutation_traits_general_drop_u8_n8` (combined, 194 с / 0,46 GiB),
  `types::sorted_permutation_traits_stable_fallback_cell_u8_n8` и `..._unstable_fallback_cell_u8_n8` (fixed route,
  222/206 с, 0,19 GiB). Opt-in остаются: combined `sorted_permutation_traits_fallback_cell_u8_n8`, `..._drop_u8_n9`
  (TIMEOUT-диагностика). Helper/macro fixed-route — разгейтить ровно под нужное; убрать комментарий-историю «after the N8
  measurement timed out» (комментарии без истории разработки).
- **Прямой u64 N6..8** (ветки OPT `1354970c94` → library `f052d6b7ec`; BACKING/BACKING2
  `experiment/kani-k1-backing-20261031`): general — `opt_split::general_direct_u64_n6/n8` (OPT G1/G2) и
  `backing::general_direct_u64_n7`; stable aggregate — `backing::stable_direct_u64_n8` (BACKING) и
  `backing::stable_direct_u64_n6/n7`. **N6/N7 из BACKING2 — только если координатор подтвердит их SUCCESS** (ждать
  сообщения; до него готовить код). Перенести эти 6 гармоник (и их helper-ы, adapter `scratch_view`) в ordinary в
  виде, не зависящем от `cfg(kani_smallsort_controls)`-модулей: одна ordinary-группа рядом с прочими DIRECT, тела и
  oracle байт-в-байт по смыслу, имена — по образцу соседних `general_stable_direct_*` (новые имена записать с картой
  «старое имя → новое»). Старые opt_split/backing экспериментальные гармоники в ordinary не тянуть; stable split со
  старым backing (`[MaybeUninit<u64>;48]`) и A u64 — не ordinary.
- **Замена:** для каждого N ∈ {6,7,8}, где обе ветви (general + stable) прямые и SUCCESS, — прежний combined stubbed
  caller `general_stable_sorted_permutation_u64_n<N>` перевести в opt-in класса retired duplicate (не удалять); если
  одна ветвь N не подтверждена — оставить C этого N ordinary и записать условность. DIRECT combined B u64 N6/N7 и
  TIMEOUT u64 N8 остаются opt-in. Контроли BACKING (порча значения, unsorted-halves, bounds) — opt-in controls.
- **Ничего больше из Part 2 не возвращать** (решение владельца и планировщика на эту ночь).

## Проверки и сборки

1. Статически: список ordinary (прогноз ≈ 182 = 176 + 3 UNSTABLE8 + 6 direct u64 − 3 C), список controls,
   `budget-gates.tsv`/манифесты, `pr2-ungate.patch` (Part 2 = Part 1 + снятие budget-gates + positive opt-in;
   retired/TIMEOUT/controls не возвращает). Rustfmt (ниже), строки ≤ 100, без новых предупреждений в обеих cfg.
2. Commit + push library (отдельно от research), последней строкой хода `PRE-BUILD REVIEW <sha>`, завершить ход;
   ждать GO координатора.
3. Сборки после GO: (1) `inventory` ordinary; (2) `inventory` controls:true — два отдельных build, можно отправить
   подряд; (3) `measurement` controls: B-контроль DIRECT (`general_stable_direct_value_corruption_control_u64_n2`),
   A-контроль DIRECT, три контроля BACKING на итоговом коде. Для count-контролей `expect_check` будет
   `This is a placeholder message` — лейн сверяет только текст, поэтому **обязательна ручная сверка по summary
   location**: единственный FAILED — строка count-assert `assert_sorted_and_probe_preserved`, sortedness-assert прошёл.
   Inventory должен совпасть со статическим списком по именам.

## Результат

`research/challenge-8/kani-k1/RESULT-ASSEMBLY.md` (русский, ≤ 100 строк): library SHA и tree, источники каждого
перенесённого блока, таблица изменений состава, итоговые числа ordinary/controls для Part 1 и Part 2, inventory
(совпадение имён), предупреждения, контроли (с location), стоимость, что не проверено (macOS, jobs=3 на итоговом
наборе, полный CI). Rustfmt:
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --check --edition 2024 --config-path /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/fmtcfg/rustfmt.toml <изменённые .rs>`
— exit 0.

## Ограничения

- Все коммиты `[skip ci]`; library-коммиты отдельно от `research/`. Push без force. Локально только Python и rustfmt;
  rustc/cargo/Kani/CBMC — нет. Логи — только summary/peaks/log-grep/log-lines (≤ 200 строк).
- Код, ветки и аудиты PR #576/#678/#694/#701 не открывать. Не упоминать rust-lang issues. Внешних действий нет.
  Спорное решать самому, владельца не ждать.

## Завершение

Commit + push. Последние строки ответа координатору:

```
REVIEW REQUEST <sha>
ASSEMBLY ЗАВЕРШЁН
```
После маркера сессию не продолжать.
