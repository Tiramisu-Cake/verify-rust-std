# UNSTABLE8 — пилот: логическая корректность trait-маршрутов DropKey и Cell на N8

Дата: 2026-10-30. Исполнитель: Codex, одна свежая сессия, окно до 4 ч (основное время — ожидание сборок).
Worktree `/root/verify-rust-std-kani-unstable8`, ветка `experiment/kani-k1-unstable8-20261030` от `5545bbf548`
(итог DIRECT + повышение потолка). **Бюджет Cloud Build: не более $4 и не более 3 сборок** (своё spent+reserved),
агент `k1-merge`, пул k1-standard4; `CAP_USD 73.96` не менять; перед каждой сборкой `k1g.sh budget` и полный envelope.
Сборку ждать **только через `k1g.sh watch BUILD` и завершать ход**; не опрашивать `status` в цикле. Actions/CircleCI —
нет. Ветки `submission/*` не трогать. Параллельно INTEG и OPT меняют `merge.rs`/`network.rs`: работать только в
`verify/types.rs` (и при необходимости `research/`).

## Зачем

`types.rs` уже проверяет через настоящие trait-входы (`StableSmallSortTypeImpl` и `UnstableSmallSortTypeImpl`, symbolic
`stable`) sortedness по логическому ключу и сохранение мультимножества логических значений (`trait_properties`,
`check_output`): `DropKey` (Freeze, не Copy: stable → general-with-scratch, unstable → Freeze-default → general с внутренним scratch;
порог 32) и `Cell<u8>` (!Freeze: stable — insertion, unstable — fallback; порог 16). Comparator здесь read-only — не
путать с mutating-Cell семейством. Ordinary сейчас: N0..2 для обоих и Cell N7; `*_n7_to9` — opt-in без записанного PASS.
Цель: **прямой результат на N8** для обоих типов через настоящие тела, без stubs (у DropKey — настоящий merge; перенос
A/B u8/u64 на не-Copy тип не допускается).

## Что сделать

- Гармоники N8: `DropKey` и `Cell<u8>` через существующий `fixed_trait_case`/`trait_properties` (оба маршрута,
  covers stable/unstable + nontrivial input). Имена по образцу соседних. Новые гармоники/helper-ы — opt-in под
  `cfg(kani_smallsort_controls)`; в ordinary переводит координатор.
- Если N8 одной гармоникой упирается во время/память — route-fixed helper и раздельные гармоники (только stable /
  только unstable trait-вход) без скрытого `kani::any()` selector, с тем же `check_output` и covers unsorted/duplicate;
  обосновать, что объединение = исходный домен. Если оба combined прошли — split ради split не делать; если не прошла
  одна ветвь/тип — сохранить частичный результат другой.
- После принятого N8 и при остатке — отдельно N9 для выбранного типа и тех же маршрутов; неизменённый N8 не
  повторять. N0..2+N8/N9 не равны непрерывному диапазону — так и писать.
- Контроли (gate собирается с controls:true и явным списком: 2 positive N8 + 2 named negative): прогнать существующие opt-in `reject_logical_permutation_drop_n2`, `reject_logical_sortedness_cell_n2`
  (ожидаются FAILED именно на counts для Drop и sortedness для Cell при корректном setup) как свидетельство чувствительности общего oracle; новый контроль нужен только
  при изменении oracle.
- Ensures/oracle/домены/flags не ослаблять, timeout не повышать.

## Сборки (kind `measurement`, jobs=1, явные списки)

1. **Gate:** DropKey N8, Cell N8 + два контроля.
2. По итогам gate: split по ветвям (если TIMEOUT/память) или соседние длины.
3. Резерв — повтор/добор в пределах бюджета.
Если всё не помещается — PARTIAL с точным продолжением.

## Порядок review

- **Review до первой proof-сборки:** закоммитить и запушить кандидата, последней строкой хода написать
  `PRE-BUILD REVIEW <sha>` и завершить ход; координатор пришлёт GO или правки. Pin Kani `9461e07a`, toolchain, flags и
  lane-файлы не менять. Вести свой список build UUID/request_id (agent label общий с другими заданиями и расходы не
  разделяет); новый полный envelope плюс резерв должен помещаться в остаток окна и бюджета — расходовать все
  разрешённые сборки не обязательно.

## Результат

`research/challenge-8/kani-k1/RESULT-UNSTABLE8.md` (русский, ≤ 100 строк): SHA, build ID, стоимость; COMPLETE /
PARTIAL / STOP; таблица: тип, N, маршрут, статус, VT GCB, RSS, covers; контроли; что доказано (логический ключ,
логический мультимножество, настоящие маршруты) и чего нет (drop-счёт, unwind, generic T); кандидаты в ordinary
Part 1 с оговоркой: macOS UNKNOWN, пригодность устанавливает только CI организаторов; указывать индивидуальный пик
CBMC/driver и метод измерения, числовой safe-gate не назначать.
Rustfmt:
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --check --edition 2024 --config-path /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/fmtcfg/rustfmt.toml <изменённые .rs>`
— exit 0; строки ≤ 100; комментарии по бюджету соседних.

## Ограничения

- Все коммиты `[skip ci]`; library-коммиты отдельно от `research/`. Push без force. Локально только Python и rustfmt;
  rustc/cargo/Kani/CBMC — нет. Логи — только summary/peaks/log-grep/log-lines (≤ 200 строк).
- Код, ветки и аудиты PR #576/#678/#694/#701 не открывать. Не упоминать rust-lang issues. Внешних действий нет.
  Спорное решать самому, владельца не ждать. Указания `/root/AGENTS.md` про Evidence Brief к задаче не относятся.

## Завершение

Commit + push. Последние строки ответа координатору (запрос review — не полученный GO):

```
REVIEW REQUEST <sha>
UNSTABLE8 ЗАВЕРШЁН
```
После маркера сессию не продолжать.
