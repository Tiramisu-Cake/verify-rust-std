# DIRECT — пилот: корректность general/stable малых длин без stub merge

Дата: 2026-10-30. Исполнитель: Codex, одна свежая сессия, окно до 4 ч (основное время — ожидание сборок).
Worktree `/root/verify-rust-std-kani-direct`, ветка `experiment/kani-k1-direct-20261030` от `2033363967`
(library tree `2532dc57` = дерево Part 1 `770d222a`; lane с kind `measurement`). **Бюджет Cloud Build: не более $4 и
не более 3 сборок** (своё spent+reserved), лейн `k1-network`, пул k1-standard4. Глобальный `CAP_USD 63.96` не менять;
перед каждой сборкой `k1g.sh budget` и полный timeout/setup envelope (остаток на старте ≈ $8,8 — справка).
Actions/CircleCI — нет. Ветки `submission/*` не трогать.

## Зачем

Ordinary general/stable корректность (`merge::general_stable_sorted_permutation_{u64_n0..8,u8_n0..9}`) использует
`stub_verified(bidirectional_merge)`. Контракт merge доказан (`merge::merge_contract_*`, `merge_length_body`) на точных
аллокациях, а настоящий вызов в `small_sort_general_with_scratch` читает префикс длины N 48-элементного scratch и пишет
в `v`. Этот перенос не доказан — главная условность решения. Цель: **устранить посылку о переносе merge-контракта для
конкретных клеток** в модели Kani на прежних pin/flags: sortedness относительно прежних `lt_u8`/`lt_u64` (они сравнивают
ключ `x >> 1`, допуская равные ключи с разными значениями) и сохранение мультимножества полных значений. Пилот не
обещает uninit, aliasing, generic T, unwind и других trait-маршрутов.

## Вариант B (основной): настоящий merge

Новые ordinary гармоники, вызывающие наш существующий `general_route_properties` **без пользовательских stubs**:
`set_value_probe`, полные символические значения, тот же comparator, sortedness и probe-count, `unwind(34)`, прежние
solver-настройки, оба covers ветви `stable` (прямой `small_sort_general` и `StableSmallSortTypeImpl` со scratch48).
Существующие гармоники, контракты, домены, covers не менять. Новый макрос — рядом с `define_general_sortedness_harness`,
имена по образцу соседних (например `general_stable_direct_*`). N0/1 merge не вызывают — их не дублировать.
Достижимость настоящего merge обосновать по графу вызовов/исходнику (N2..7: копирование + `insert_tail`, N8/9:
`sort4_stable`, затем merge); `cover(N>=2)` сам по себе не свидетель. Covers проверить явно по summary: SUCCESS не
делает unreachable cover ошибкой.

Обязательный домен: Copy+Freeze u64 N2..8, u8 N2..9. **Не входят** (отдельная задача): stable non-Freeze (fallback,
merge не вызывает), unstable general для Freeze !Copy, unstable trait u8/u64 (там network).

## Вариант A (условный): контракт на фактической геометрии

Открывать только если B упрётся в время/память или как отдельно обоснованная оптимизация. Тогда: новые
`proof_for_contract(bidirectional_merge)`, где merge получает срез длины N от offset 0 backing-аллокации на 48
(инициализирован только префикс N; stable — `[MaybeUninit<T>;48]`, прямой general — `MaybeUninit<[T;48]>`, оба случая
или проверяемое обоснование эквивалентности), destination — отдельный инициализированный `[T;N]`; `modifies` прежний
(dst[..N]), scratch в write-set не добавлять. Приёмка A — совпадение T, F, probe-состояния, N, offset 0, границы половин
`floor(N/2)`, инициализации, destination, no-alias и frame с каждым относимым caller.

## Порядок сборок (kind `measurement`, явные списки)

1. **Gate:** B для u64 N2..4 (группой, как `_n2_to4`, если это не раздувает время — обосновать), u8 N2..4, u64 N8,
   u8 N9 + контроль B (ниже).
2. При положительном gate — остальные B (u64 N5..7, u8 N5..8).
3. Резерв: повтор/A только при необходимости и в остатке бюджета.
Если всё не помещается — отчёт PARTIAL с точным продолжением; не урезать timeout и проверки.

## Контроли (под `cfg(kani_smallsort_controls)`)

- B: проверка чувствительности оракула — controls-only вариант, где выходное утверждение ловит потерю/подмену полного
  значения (ожидается FAILED на конкретном assert). Production-контракты и ensures не трогать; `assert!(false)` не
  годится. Фиксировать check и место отказа; compile error / unsupported / иной FAILED контроль не закрывают.
- A (если открыт): controls-only вызов настоящего verified stub с нарушенным sorted-halves requires при корректной
  памяти; ожидать precondition check при штатном `--no-assert-contracts`.

## Результат

`research/challenge-8/kani-k1/RESULT-DIRECT.md` (русский, ≤ 100 строк): SHA, build ID, стоимость; COMPLETE / PARTIAL /
STOP; таблица по клеткам T/N/маршрут: статус, VT GCB, RSS, covers; controls; непроверенные клетки. **macOS — UNKNOWN**:
исторические отношения Mac/GCB только как справочный сценарий, не граница и не критерий. Отдельно: какие клетки
перестают зависеть от посылки scratch-transfer; ожидаемая чистая delta Part 1 (добавление B рядом со старыми
stub-гармониками или их замена — описать, ничего не удалять). Пилот ≠ зелёный CI организаторов.
Rustfmt: `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --check --edition 2024 --config-path /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/fmtcfg/rustfmt.toml <изменённые .rs>` — exit 0; строки ≤ 100.
Комментарии в коде — по бюджету соседних (1–2 строки на группу).

## Ограничения

- Все коммиты `[skip ci]`; library-коммиты отдельно от `research/`. Push без force. Локально только Python и rustfmt;
  rustc/cargo/Kani/CBMC — нет. Логи — только summary/peaks/log-grep/log-lines (≤ 200 строк).
- Код, ветки и аудиты PR #576/#678/#694/#701 не открывать. Не упоминать rust-lang issues. Внешних действий нет.
  Спорное решать самому, владельца не ждать. Указания `/root/AGENTS.md` про Evidence Brief к задаче не относятся.

## Завершение

Commit + push. Последние строки ответа координатору (запрос review — не полученный GO):

```
REVIEW REQUEST <sha>
DIRECT ЗАВЕРШЁН
```
После маркера сессию не продолжать.
