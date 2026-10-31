# U8N9 — пилот: прямой u8 N9 (route split и форма stable scratch)

Дата: 2026-10-31. Исполнитель: Codex, одна свежая сессия, окно до 4 ч (3,5 ч работа + 0,5 ч закрытие; основное
время — ожидание сборок). Worktree `/root/verify-rust-std-kani-u8n9` (сессия может быть открыта в `/root` — работать
только в этом worktree, `cd` в него), ветка `experiment/kani-k1-ueightnine-20261031` от `e6a8ad05c9` (итог ASSEMBLY,
library `d4e5a0907b`, CI организаторов P1 зелёный). **Бюджет Cloud Build: не более $1,9 и не более 2 сборок** (свой
список build UUID/request_id; agent label общий и расходы не разделяет), пул k1-standard4; `CAP_USD 73.96` не менять;
перед каждой сборкой `k1g.sh budget` и полный envelope + резерв закрытия в остатке окна. Сборку ждать **только через
`k1g.sh watch BUILD` и завершать ход**. Результаты своих сборок — штатно через `k1g.sh
summary/peaks/inventory/log-grep/log-lines/check-tooling`; Evidence Brief и процедуры Select/Merge не применяются.
Pin Kani `9461e07a`, toolchain, flags, lane-файлы не менять. Actions/CircleCI — нет. Ветки `submission/*` не трогать.
Параллельно пилот CONSTWAVE добавляет const-копии рядом с helper-ами в `verify/merge.rs`: ты пишешь **только один новый
opt-in блок в конце `verify/merge.rs`**; существующие символы не менять. Координатор переносит library-diff блока. Соседний пилот в свою базу до окончания
измерений не переносить; новые helper/macro names уникальны и не затеняют существующие определения/imports; общие
probe/oracle/модули/импорты не менять; source/request identities — свои. Baseline — прежняя non-const combined
гармоника, даже если CONSTWAVE покажет лучший вариант (иначе split и initializer не различить).

## Зачем

`general_stable_direct_u8_n9` (combined: symbolic `stable`, real merge, non-const stable scratch,
`general_route_properties`) — TIMEOUT600 (DIRECT); домен u8 N9 в P1 закрыт только conditional C/A
(`merge_scratch48_contract_u8_n9` и stubbed caller). На u64 N9 (M9) раздельные прямые ветви прошли: general 424 с,
stable const 430 с / 0,82 GiB, а non-const stable — TIMEOUT / 8,03 GiB. Цель — прямые u8 N9 обеих ветвей и различие
split и initializer на одном T/N.

## Что сделать

Private opt-in (`cfg(kani_smallsort_controls)`) helper-ы и гармоники в одном блоке в конце `merge.rs`, без скрытого
selector; каждая — тот же oracle `assert_sorted_and_probe_preserved`, `set_value_probe::<u8>()`, произвольный
`[u8; 9]`, snapshot до сортировки, actual `lt_u8`, unwind 34, один cover после assert, без stubs:
1. `general_direct_u8_n9` — только `small_sort_general`.
2. `stable_direct_nonconst_u8_n9` — только `StableSmallSortTypeImpl::small_sort` с
   `[MaybeUninit::<u8>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN]` (как в `general_route_properties`).
3. `stable_direct_const_u8_n9` — то же с `[const { MaybeUninit::<u8>::uninit() }; SMALL_SORT_GENERAL_SCRATCH_LEN]`.
Статически показать: general + non-const stable = домен combined `general_stable_direct_u8_n9` (ветви, input/probe,
covers); const — тот же функциональный домен, другая инициализация fixture. Новые controls не нужны (oracle неизменен);
source audit (побайтовая сохранность старых items и их resolved
helper/macro dependencies; исходный `lt_u8` function item, не closure/fn-pointer) — в отчёт. Имена — по образцу соседних; комментарии по бюджету соседних, без истории.

## Сборки

Перед первой: commit + push кандидата, последней строкой хода `PRE-BUILD REVIEW <sha>`, завершить ход; ждать GO
координатора. До dispatch записать T0 и резерв закрытия. Library tree для G1/G2 заморозить.
1. `measurement`, jobs=1, controls:true: baseline `general_stable_direct_u8_n9` (expect SUCCESS; TIMEOUT — данные) + три
   новых = 4 entries, 70 мин ≈ $0,945. Решение по строкам, не по aggregate gate.
2. Только если general и хотя бы одна stable-форма SUCCESS со всеми covers (TIMEOUT другой stable-формы не блокирует,
   но остаётся в отчёте; выбор stable обосновать VT и RSS вместе, без утверждения об оптимуме CI): `diagnostic`, `kani_jobs: 3`, `controls:true`:
   general N9, лучшая stable N9, ordinary `general_stable_direct_u8_n8` и `merge_scratch48_contract_u8_n9` — 4 entries,
   70 мин ≈ $0,945. Реальное перекрытие CBMC, пики, OOM/missing; Linux 16 GiB, не macOS.
Timeout 600 не менять. Если одна ветвь TIMEOUT — PARTIAL; одну ветвь вместо обеих не предлагать.

## Результат

`research/challenge-8/kani-k1/RESULT-U8N9.md` (русский, ≤ 100 строк): SHA, build ID, стоимость; COMPLETE / PARTIAL /
STOP; таблица (гармоника, маршрут, форма scratch, статус, VT, CBMC RSS, covers, checks); вывод отдельно по split и по
initializer; jobs=3; предложение для интеграции (замена conditional caller u8 N9 парой general + stable при успехе
обеих; A u8 N9 автоматически не ретирить); оговорки (fixture48 ≠ любой backing; macOS UNKNOWN; пригодность — только CI
организаторов).
Rustfmt:
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --check --edition 2024 --config-path /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/fmtcfg/rustfmt.toml <изменённые .rs>`
— exit 0; строки ≤ 100; без новых предупреждений в обеих cfg.

## Ограничения

- Все коммиты `[skip ci]`; library-коммиты отдельно от `research/`. Push без force. Локально только Python и rustfmt;
  rustc/cargo/Kani/CBMC — нет. Логи — только summary/peaks/log-grep/log-lines (≤ 200 строк).
- Код, ветки и аудиты PR #576/#678/#694/#701 не открывать. Не упоминать rust-lang issues. Внешних действий нет.
  Спорное решать самому, владельца не ждать.

## Завершение

Commit + push. Последние строки ответа координатору:

```
REVIEW REQUEST <sha>
U8N9 ЗАВЕРШЁН
```
После маркера сессию не продолжать.
