# CONSTWAVE — пилот: const-repeat stable scratch на активных merge-fixtures

Дата: 2026-10-31. Исполнитель: Codex, одна свежая сессия, окно до 5 ч (4,5 ч работа + 0,5 ч закрытие; основное
время — ожидание сборок, envelopes 150 + 90 мин). Worktree `/root/verify-rust-std-kani-constwave` (сессия может быть
открыта в `/root` — работать только в этом worktree, `cd` в него), ветка `experiment/kani-k1-constwave-20261031` от
`e6a8ad05c9` (итог ASSEMBLY, library `d4e5a0907b`, CI организаторов P1 зелёный). **Бюджет Cloud Build: не более $3,3
и не более 2 сборок** (свой список build UUID/request_id; agent label общий и расходы не разделяет), пул k1-standard4;
`CAP_USD 73.96` не менять; перед каждой сборкой `k1g.sh budget` и полный envelope + резерв закрытия в остатке окна.
Сборку ждать **только через `k1g.sh watch BUILD` и завершать ход**. Результаты своих сборок — штатно через `k1g.sh
summary/peaks/inventory/log-grep/log-lines/check-tooling`; Evidence Brief и процедуры Select/Merge не применяются.
Pin Kani `9461e07a`, toolchain, flags, lane-файлы не менять. Actions/CircleCI — нет. Ветки `submission/*` не трогать.
Параллельно пилот U8N9 пишет **только новый opt-in блок в конце `verify/merge.rs`**; ты пишешь только `verify/merge.rs`,
новые блоки — рядом с соответствующими helper-ами, не в конце файла; существующие символы не менять. Соседний пилот в
свою базу до окончания измерений не переносить; новые helper/macro names уникальны и не затеняют существующие
определения/imports; общие probe/oracle/модули/импорты ради копий не менять; source/request identities — свои.

## Зачем

M9 (`experiment/kani-k1-mnine-20261031`, `RESULT-M9.md`, 7fd3d250a1) на real stable u64 N9, один SHA: non-const
`[MaybeUninit::<u64>::uninit(); 48]` TIMEOUT600 / 8,03 GiB; const `[const { MaybeUninit::<u64>::uninit() }; 48]` SUCCESS
430 с / 0,82 GiB; aggregate `MaybeUninit<[u64;48]>` + `scratch_view` 434 с / 1,60 GiB. Механизм не установлен; на
stubbed `correct` u8 N14 форма scratch эффекта не дала. Цель — matched old/const на активных fixtures P1/P2 с реальными
телами, чтобы интеграция могла перевести их на const (и убрать aggregate+adapter из ordinary stable_direct N6..8).

## Что сделать

Новые helper-ы/гармоники — private opt-in (`cfg(kani_smallsort_controls)`), отличаются от исходных **только** формой
stable scratch: `[const { MaybeUninit::<T>::uninit() }; SMALL_SORT_GENERAL_SCRATCH_LEN]`. Для non-const → const тип
storage и extent прежние; для aggregate → const тип storage меняется, размер/alignment/borrow-интерфейс сохраняются.
Input/probe/oracle/comparator/covers/symbolic selectors/unwind/attributes — как у исходной гармоники.

1. **stable_direct u64 N6/N7/N8:** const-вариант `stable_direct_u64_properties`: donor — M9 `7fd3d250a1`, library `b2930031d8`,
   только helper `stable_direct_const_u64_properties`, но с guard baseline 6/7/8 (не 6..=9 из M9); guard-ы ordinary
   функций и прочие гармоники M9 не переносить. Гармоники `stable_direct_const_u64_n6/n7/n8`.
   Baseline — существующие ordinary aggregate `stable_direct_u64_n6/n7/n8`.
2. **`general_route_properties`** (`merge.rs:854–878`, symbolic `stable`): const-копия и
   `general_stable_direct_const_u64_n5`; baseline ordinary `general_stable_direct_u64_n5`.
3. **`stable_general_u64_safety_body`** (`merge.rs:590`) через `all_upper_routes_safety_body` (selector из трёх
   маршрутов сохранить): const-копии обоих и `route_safety_all_routes_const_n16` с теми же атрибутами, что задаёт
   `define_route_safety_harness!` (`proof`, unwind 34, stub `panic_on_ord_violation → abort_on_order_violation`), три
   route choices и их covers; baseline ordinary `route_safety_all_routes_n16`.
4. **`merge_scratch48_length_body`** (`merge.rs:1066`, PFC `bidirectional_merge`): const-копия только для
   `stable_scratch` (actual `proof_for_contract(bidirectional_merge)`, function item `lt_u8`, aggregate
   `general_scratch`, обе backing-ветви, prefix-инициализация, отдельный dst, requires/modifies, оба covers — прежние) и `merge_scratch48_contract_const_u8_n9`; baseline ordinary `merge_scratch48_contract_u8_n9`.
5. Не трогать: `correct.rs:194` (эффекта нет), строки 1055/1130 (контроли — их переведёт интеграция согласованно с
   positive fixture), `scratch_view` (нужен BACKING controls). Новых controls не нужно: oracle/adapter/probe не
   меняются; в отчёте — source audit, что const-копии отличаются только initializer-ом.
6. Source audit: побайтовая сохранность старых items и их resolved helper/macro dependencies.
7. Имена — по образцу соседних (вариант выше или лучше по смыслу); комментарии — по бюджету соседних, без истории.

## Сборки

Перед первой: commit + push кандидата, последней строкой хода `PRE-BUILD REVIEW <sha>`, завершить ход; ждать GO
координатора. До dispatch записать T0 и резерв закрытия. Library tree для G1/G2 заморозить.
1. `measurement`, jobs=1, controls:true: 6 baseline + 6 const = **12 entries, envelope 150 мин ≈ $2,025**. Все в одном
   frozen tree; baseline TIMEOUT — тоже данные (expect остаётся SUCCESS). Решение по строкам **для каждой пары** (baseline/const одного
   target, не общие максимумы): статус, VT, CBMC RSS, covers, checks. При baseline TIMEOUT VT нет, его VmHWM — пик
   до остановки (цензурированный); при MISSING no-regression не придумывать; малые RSS-разницы одиночного замера не
   выдавать за устойчивый эффект.
2. `diagnostic`, `kani_jobs: 3`, `controls:true`: только const-entries, которые в G1 SUCCESS с covers и не хуже своего
   baseline (максимум 6: три `stable_direct_const_u64_n6/n7/n8` + три const-варианта п. 2–4); envelope
   `count×10+30` ≤ 90 мин ≈ $1,215; другие проверки ради заполнения не добавлять. Непрошедшие пары — PARTIAL, успешные
   не теряются.
   Реальное перекрытие CBMC, пики, OOM/missing; это Linux 16 GiB, не macOS. Если остатка окна не хватает на полный
   envelope + закрытие — G2 не запускать, записать NOT_RUN.
Timeout 600 не менять.

## Результат

`research/challenge-8/kani-k1/RESULT-CONSTWAVE.md` (русский, ≤ 100 строк): SHA, build ID, стоимость; COMPLETE / PARTIAL
/ STOP; таблица пар (гармоника, форма, статус, VT, CBMC RSS, covers, checks) с разницей; jobs=3; для каждого из 4
мест — рекомендация интеграции (перевести исходный helper на const / оставить) и **карта интеграции с M9**: у M9 и CONSTWAVE совпадут имя const-u64 helper и
`stable_direct_const_u64_n8` — нужен один согласованный helper (guard 6..=9 при переносе G9/S9const M9 в P2) и один N8
wrapper без дублей; whole-file cherry-pick не делать; опытные baseline/копии остаются opt-in и не разгейчиваются
старым P2-патчем; что меняется в ordinary (замена
aggregate stable_direct N6..8 на const — тот же домен T/F/N/input/probe, другая fixture-геометрия, не transfer старого
PASS); оговорки (fixture48 ≠ любой backing; механизм не установлен; macOS UNKNOWN; пригодность — только CI организаторов).
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
CONSTWAVE ЗАВЕРШЁН
```
После маркера сессию не продолжать.
