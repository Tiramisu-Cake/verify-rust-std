# INTEG — интеграция консервативного DIRECT и дешёвых возвратов в состав Part 1

Дата: 2026-10-30. Исполнитель: Codex, одна свежая сессия, окно до 4 ч. Worktree `/root/verify-rust-std-kani-integ`,
ветка `experiment/kani-k1-integ-20261030` от `5545bbf548` (итог DIRECT `4746a5d01d` + повышение потолка). Library
tree `e16a8ee5` = дерево Part 1 (`2532dc57`) + пилот DIRECT. **Бюджет Cloud Build: не более $2,5 и не более 3 сборок**
(своё spent+reserved), агент `k1-network`, пул k1-standard4; `CAP_USD 73.96` не менять; перед сборкой
`k1g.sh budget`. Сборку ждать **только через `k1g.sh watch BUILD` и завершать ход**; не опрашивать `status` в цикле.
Actions/CircleCI — нет. Ветки `submission/*` не трогать: перенос в ветку подачи делает координатор.
Параллельно работают OPT (только новый блок в конце `merge.rs`) и UNSTABLE8 (`types.rs`). INTEG владеет исходными
DIRECT `cfg`, oracle/контролем/комментарием и составом; чужие блоки не трогать и не ждать. Координатор переносит
отдельные library-diff; после объединения нужен общий manifest и CI — branch-level evidence объединение не проверяет.

## Входы

- `RESULT-DIRECT.md`, `direct/results.tsv`; ревью DIRECT (координатор, GO_WITH_NITS; findings ниже).
- `scope/` (манифесты ordinary/extended-positive/controls-failed, `budget-gates.tsv`, `pr2-ungate.patch`, SCOPE.md).
- Манифест времени: `/root/smallsort-pr-drafts/smallsort-harnesses.tsv` (П-6 партиции `40748125754`, П-7 autoharness).

## Что сделать

1. **Состав DIRECT в ordinary (консервативный).** Ordinary: `merge::general_stable_direct_u64_n2..n5`,
   `general_stable_direct_u8_n2..n8`, `merge_scratch48_contract_u8_n9`. Под `cfg(kani_smallsort_controls)` как
   положительный opt-in: `general_stable_direct_u64_n6/n7`, `merge_scratch48_contract_u64_n5..n8`,
   `merge_scratch48_contract_u8_n5..n8`. Как opt-in диагностику (не expected FAILED и не positive): `general_stable_direct_u64_n8`,
   `general_stable_direct_u8_n9` (TIMEOUT 600 с в G1). Item-level `cfg` на вызовах макросов, тела не менять.
2. **Дубли старых stubbed callers — ровно 11:** `general_stable_sorted_permutation_*` для u64 N2..5 и u8 N2..8 →
   opt-in класса «retired duplicate» (не удалять); соответствующие B остаются ordinary. Сначала проверить: тот же
   helper/T/F/N, обе ветви, общий oracle, ничего от них не зависит. C u64 N6..8, u8 N9 и N0/1 не гейтить.
   Существующие `merge_contract_*` и выбранная A u8 N9 — ordinary; остальные DIRECT A — ровно по п.1. Условность
   ordinary C u64 N6..8 (поддерживающие A u64 — opt-in) сохранить и записать.
   Итог по DIRECT: 12 новых ordinary (4 B u64 + 7 B u8 + 1 A u8), 10 positive opt-in, 2 TIMEOUT-диагностики,
   2 controls-only.
3. **Findings ревью DIRECT:**
   - контроль `general_stable_direct_value_corruption_control_u64_n2` должен вызывать настоящий
     `assert_sorted_and_probe_preserved`, а не копию проверки. Ожидаемый отказ сопоставить по месту (file:line /
     property id) или иным проверяемым способом; если меняешь общий oracle (например `kani::assert` со статическим
     сообщением) — обосновать, что положительные гармоники не меняют смысл, и записать;
     предпочтительно общий oracle не менять. Если всё же меняется — сохранить булевы свойства, review эквивалентности и
     положительный smoke через него. Контроль обязан падать на permutation при сохранённой key-sortedness;
   - `merge.rs:853` «only merge is stubbed» больше не верно для B — перенести замечание к stubbed макросу.
4. **Возврат из Part 2 в ordinary** (только снятие бюджетных `cfg`, тела не менять):
   `network::swap_contract_u64_n9`, `swap_contract_u8_n9`, `swap_contract_u8_n13`;
   `network::mutating_route_safety_cell_n9_to12`;
   27 гармоник plain u64 insertion safety N6..19 (`network::insertion_safety_u64_*`, в манифесте part1=opt-in,
   part2=ordinary). Ровно 31 = 3 swap + 1 mutating-route + 27 plain insertion; широкие/устаревшие insertion-группы
   не разгейтить по wildcard. Mutating-Cell insertion N6..19 — не возвращать. Helper-ы, которые станут нужны ordinary, разгейтить
   точечно; без новых предупреждений в обеих конфигурациях.
5. **Документы:** `scope/` — манифесты с классами (budget-deferred, retired duplicate, positive diagnostic, TIMEOUT
   diagnostic, expected-fail, deferred), `budget-gates.tsv`, новый `pr2-ungate.patch`: Part 2 = новый Part 1 + один
   коммит, снимающий только budget-gates и принятые positive DIRECT; не возвращает 11 дублей, 2 TIMEOUT и controls.
   Статический прогноз планировщика: **176 ordinary P1** (144+12−11+31), **339 ordinary P2** (328+22−11), с controls
   ≈449 имён — сверить, расхождения объяснить. Манифесты пометить «после INTEG, без OPT/UNSTABLE8», с library tree
   и источником каждого результата; positive DIRECT в P2 — candidate, не подтверждённый macOS CI. Справка по стоимости: ΣVT добавленного и убранного по П-6 партициям/GCB — только для приоритизации, не
   прогноз autoharness (не складывать с П-7, не делить на jobs, не переводить GCB→Mac коэффициентом).

## Сборки

1–2. Два отдельных `inventory` на новом SHA (у kind inventory одно значение controls): ordinary и controls:true.
   Фактический список = статическому; `log-grep` предупреждений `unused_*`/`dead_code` в `smallsort/verify*`.
3. `measurement` controls (после review координатора): исправленный B-контроль (ожидается FAILED на нужной проверке) и A-контроль; при остатке —
   две-три самых дешёвые из новых ordinary как smoke. Если инвентарь нашёл ошибку — исправить, повторную сборку
   делать только в пределах бюджета.

## Порядок review

- **Review до measurement-сборки:** закоммитить и запушить кандидата, последней строкой хода написать
  `PRE-BUILD REVIEW <sha>` и завершить ход; координатор пришлёт GO или правки. Pin Kani `9461e07a`, toolchain, flags и
  lane-файлы не менять. Каждое задание ведёт свой список build UUID/request_id (agent label общий у INTEG и OPT и
  расходы не разделяет); новый полный envelope плюс резерв должен помещаться в остаток окна и бюджета —
  расходовать все разрешённые сборки не обязательно.

## Результат

`research/challenge-8/kani-k1/RESULT-INTEG.md` (русский, ≤ 100 строк): SHA, build ID, стоимость; таблица изменений
состава (что стало ordinary / opt-in / диагностикой, почему); аудит дублей; контроли; inventory и предупреждения;
числа для обеих частей; что требует полного CI организаторов (решение координатора). Library-коммиты отдельно от
`research/`; rustfmt:
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --check --edition 2024 --config-path /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/fmtcfg/rustfmt.toml <изменённые .rs>`
— exit 0; строки ≤ 100. Комментарии — не больше строк, чем было; без истории разработки в коде.

## Ограничения

- Все коммиты `[skip ci]`. Push без force. Локально только Python и rustfmt; rustc/cargo/Kani/CBMC — нет. Логи —
  только summary/peaks/log-grep/log-lines (≤ 200 строк).
- Код, ветки и аудиты PR #576/#678/#694/#701 не открывать. Не упоминать rust-lang issues. Внешних действий нет.
  Спорное решать самому, владельца не ждать. Указания `/root/AGENTS.md` про Evidence Brief к задаче не относятся.

## Завершение

Commit + push. Последние строки ответа координатору (запрос review — не полученный GO):

```
REVIEW REQUEST <sha>
INTEG ЗАВЕРШЁН
```
После маркера сессию не продолжать.
