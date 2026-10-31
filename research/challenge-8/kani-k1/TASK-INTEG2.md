# INTEG2 — интеграция раунда оптимизаций в кандидат Part 1 (P1-max) и Part 2

Дата: 2026-10-31. Исполнитель: Codex, одна свежая сессия, окно до 5 ч (4,5 работа + 0,5 закрытие). Worktree
`/root/verify-rust-std-kani-integtwo` (сессия может быть открыта в `/root` — `cd` в worktree), ветка
`experiment/kani-k1-integtwo-20261031` от `e6a8ad05c9` (итог ASSEMBLY, library `d4e5a0907b`, P1 182 ordinary, CI
организаторов зелёный; процедуры, скрипты и форматы — по образцу `research/challenge-8/kani-k1/assembly/` и
`RESULT-ASSEMBLY.md`). **Бюджет Cloud Build: не более $2,9 и не более 3 сборок**, пул k1-standard4, `CAP_USD 73.96` не
менять; учёт по собственным UUID/request_id (agent label общий). Перед каждой сборкой `k1g.sh budget` + свой
spent/reserved + полный envelope + резерв закрытия. T0 — фактическое начало сессии, не первый dispatch. Ждать только
`k1g.sh watch BUILD` и завершать ход. Evidence Brief и процедуры Select/Merge не применяются; остальные глобальные
инструкции действуют. Pin Kani, toolchain, flags, lane-файлы не менять.
Actions/CircleCI — нет (macOS-прогон делает координатор после тебя). Ветки `submission/*` не трогать.

## Источники (только library-diff перечисленных коммитов; whole-file cherry-pick нельзя)

- M9 `b2930031d8` (merge.rs): general/stable direct u64 N9; отчёт
  `/root/verify-rust-std-kani-m9/research/challenge-8/kani-k1/RESULT-M9.md`, final `7fd3d250a1`.
- START1 `b98ee415fd` (network.rs): три tail-группы + shared frame checker + 2 controls; `RESULT-START1.md`.
- CONSTWAVE `a9daab85b0` (merge.rs); `RESULT-CONSTWAVE.md` (d69c8617c7).
- U8N9 `2c65b6cdd9` (merge.rs); `RESULT-U8N9.md` (29bb494053).
- CORR14 — не переносить (combined остаётся в P2 как есть).

## Что сделать (library)

1. **9 возвратов в P1** (снять opt-in gate, тела не менять): `network::network_correctness_u8_n10`,
   `network::network_correctness_u8_n11`, `network::network_correctness_u8_n12`,
   `network::insertion_permutation_u8_n11`; `merge::route_safety_all_routes_n3`, `_n4`, `_n5`, `_n6`, `_n7`.
2. **stable direct u64:** один helper `stable_direct_u64_properties` с const-repeat scratch
   (`[const { MaybeUninit::<u64>::uninit() }; SMALL_SORT_GENERAL_SCRATCH_LEN]`, тело CONSTWAVE/M9), guard `6..=9`;
   ordinary `stable_direct_u64_n6..n9` (N9 новый). Один N8 wrapper, без old/const дублей. Прежнюю aggregate-форму
   сохранить opt-in: отдельный aggregate-helper и три wrapper N6/N7/N8 как fallback (до решения по macOS), без
   последующего изменения тел. `scratch_view` оставить для controls; не импортировать второй const-helper/N8 wrapper.
3. **general direct u64:** guard `general_direct_u64_properties` до `6..=9`, ordinary `general_direct_u64_n9`.
   C `general_stable_sorted_permutation_u64_n9` оставить opt-in класса retired-duplicate; P2 его не разгейчивает.
4. **general_route_properties** (общий для u64 и u8): исходный generic helper оставить для u8. Добавить отдельный
   const-helper для u64 (тело CONSTWAVE, function item `lt_u64`, тот же oracle и оба covers; без `size_of`-ветвлений,
   closure/fn-pointer, нового selector) и направить на него семью B u64 N2..N5 (`general_stable_direct_u64_n2..n5`).
   Для каждой B u64 N2..N5 сохранить также opt-in nonconst-wrapper, вызывающий исходный generic helper: это fallback
   только cfg-выбором. Согласованно перевести stable-ветвь `general_stable_direct_value_corruption_control_u64_n2`
   (merge.rs ~1055). Старые conditional/retired C u64 не трогать, кроме классификации C N9 из п.3.
5. **Не трогать:** `stable_general_u64_safety_body`/R16, `merge_scratch48_length_body`/P9, control ~1130,
   `correct.rs:194`, все u8-места (остаются nonconst).
6. **u8 N9:** ordinary `general_direct_u8_n9` + `stable_direct_nonconst_u8_n9` (имена можно привести к соседним);
   C `general_stable_sorted_permutation_u8_n9` перевести в opt-in как provisional retired/fallback; тело сохранить.
   При недопуске новой u8-пары C можно вернуть в P1 только cfg-изменением. A u8 N9 остаётся в P1.
7. **START1:** ordinary три `network::insert_tail_contract_u64_start1_tail2_to8`,
   `network::insert_tail_contract_u64_start1_tail9_to12`, `network::insert_tail_contract_u64_start1_tail13_to16`.
   Baseline `network::insert_tail_contract_u64_start1` — timeout-diagnostic, не разгейчивать в P2; оба frame-controls
   оставить opt-in. При недопуске пакета все три новых PFC уходят в P2, старый baseline не возвращается ordinary.
8. Экспериментальные u64 nonconst/aggregate N9, const u8 N9 и лишние baseline-триады не переносить, кроме fallback
   п.2/4. Выбранная **nonconst u8 N9 из п.6 переносится**. Никакие диагностические копии не добавлять в ordinary/P2.
Итог: «P1-max» = 182 + 9 + 2 (u8 N9) − 1 (C u8 N9) + 2 (u64 N9) + 3 (START1) = **197 ordinary** (проверить точно).
Комментарии — по бюджету соседних, без истории разработки; rustfmt по образцу пилотов; строки ≤ 100.

## Part 2

Обновить static P2-patch/скрипт ASSEMBLY: расширенный P2 включает P1-max и оставшиеся selected P2-only, без повторного
включения retired C u64/u8 N9, baseline START1, fallback/diagnostic/negative/unsupported и historical-копий.
A u8 N5..8 — **не ретирить** в этой сессии (нужен отдельный аудит consumers, вкл. nested sort8_stable→merge).
Прогноз P2 = **343 = 339 + 1(U8 pair вместо C) + 1(M9 pair вместо C) + 2(START1 partition вместо baseline)**.
Девять возвратов меняют P1/P2-only, но не размер расширенного P2. Точное множество — static apply/name check;
native P2 не заявлять. Для будущей macOS-раскладки при r=0: P1=191+u+2m+3s, P2=344−u,
где u/m/s=1 лишь при допуске соответствующих полных u8/M9/START1 пакетов. При u=0 P1 сохраняет C u8 N9,
а P2 включает этот C и две новые u8-гармоники. Замены const/fallback сами по себе cardinality не меняют.

## Сборки (перед первой: commit + push, `PRE-BUILD REVIEW <sha>`, завершить ход, ждать GO)

Library tree после GO заморожен для всех трёх запросов. У каждого отдельные published request SHA/UUID;
какой-либо результат пилота не переименовывать в measurement этого tree.
1. G1: `kind:inventory`, controls:false, inventory:true, harnesses:[], work30min; reserve60min/$0,810.
   Exact set =197 ordinary, не только количество; отдельно проверить новые зависимости и предупреждения.
2. G2: отдельный `kind:inventory`, controls:true, inventory:true, harnesses:[], work60min;
   reserve90min/$1,215. Полный cfg-on set заранее вывести из static manifest, включая fallback и новые controls;
   не приравнивать его к прежним463. Нельзя соединить две cfg одним inventory-build и назвать это двумя списками.
3. G3: `measurement`, jobs1, controls:true, timeout10min, **ровно три ожидаемых FAILED controls**:
   `merge::general_stable_direct_value_corruption_control_u64_n2`,
   `network::insert_tail_contract_u64_start1_prefix_frame_control`,
   `network::insert_tail_contract_u64_start1_suffix_frame_control` (полный std namespace в request).
   Reserve60min/$0,810. Ровно один intended FAILED каждого: общий count-assert при sortedness без отказа;
   shared START1 prefix-/suffix-frame asserts, не OOB. Covers достижимы, прочих отказов нет. expect_check задать по
   известному тексту, а location/class вручную сверить с frozen source; matcher mismatch не переименовывать в gate=true.
   Положительные integration harnesses здесь **не измеряются**: их проверит macOS job координатора, затем полный CI.

Это три плановые сборки, четвёртого резерва нет. Общий максимум указанных envelopes210min/$2,835 укладывается в лимит
$2,9; лимит не повышать. G3 запускать только если фактический own spent+reserved+$0,810≤$2,9 и полный envelope
помещается в окно. Иначе G3=NOT_RUN, итог PARTIAL, передать точный готовый request и недостающий расход координатору;
к macOS не передавать статус «controls приняты». 
Retry возможен лишь вместо ещё не выполненной стадии, в оставшихся трёх slots/бюджете, с PARTIAL при пропуске;
semantic fix требует committed delta-review/GO. Timeout proof не сокращать ради остатка, пустые/padding entries не добавлять.
Исходный расширенный measurement имел17 entries (170 harness-minutes), что превышает lane cap150 до учёта setup;
не восстанавливать его одним request. Финальный ordinary inventory после macOS/cfg-отбора — отдельный этап
координатора/следующего задания, не четвёртая сборка этой сессии.

## Результат

`research/challenge-8/kani-k1/RESULT-INTEG2.md` (≤ 100 строк): SHA, library tree, build IDs, стоимость; COMPLETE/PARTIAL;
список P1-max (197) и static P2 (343) с diff к ASSEMBLY; что реально inventory/proof-checked и что NOT_RUN;
controls с location; карта cfg-fallback: aggregate N6..8, nonconst B u64 N2..5, C u8 N9, демоция M9/START1 в P2
без изменения тел и без воскрешения старых baseline-дублей. Source audit: изменённые items перечислены точно,
остальные items и их resolved dependencies сохранены; production/tool/lane не затронуты. До macOS это только
кандидат P1-max, не новый зелёный P1. Оговорки: native P2/macOS/full CI не запускались, controls могут быть NOT_RUN.

## Ограничения

Коммиты `[skip ci]`, library отдельно от research, push без force. Локально только Python и rustfmt. Логи — только
k1g.sh summary/peaks/log-grep/log-lines (≤ 200). Код/ветки/аудиты PR #576/#678/#694/#701 не открывать. Не упоминать
rust-lang issues. Спорное решать самому. Завершение: commit + push, последние строки `REVIEW REQUEST <sha>` и
`INTEG2 ЗАВЕРШЁН`, после маркера не продолжать.
