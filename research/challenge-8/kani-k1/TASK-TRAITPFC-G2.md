# TRAITPFC G2 — содержательные `ensures` прямо на trait-методах `small_sort` (u64, N2)

**Выдано координатором 2026-11-10, в рамках GO владельца на пилот.** Research-ветка, в подачу не идёт. Dispatch только
после exact-packet PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-traitpfc**, ветка **experiment/kani-k1-traitpfc-20261110**, от G1 PASS
  **feb589a306** (RESULT-TRAITPFC.md: контракты `requires`/`modifies` на T1–T3, PFC и `stub_verified` работают).
- Пин Kani `f046b70644`, nightly-2026-10-23; **tooling base для check-tooling: `9b1758ab817af005e96fd52a5fc940d4b6acf984`**.
  Tooling, workflows, пин, toolchain не менять.
- Slug **traitpfc**, stage `traitpfc-g2`, stable owner **k1-merge**, request `traitpfc-g2-*`.
- Свой cap **$3.00** (проверь фактический остаток проекта, cap $118.96). **Одна основная сборка**; один
  compile-error repair второй сборкой, если own spent + reserve ≤ cap. Retry, третьей сборки и расширения cap/окна нет.
- Окно: main 300 + closeout 30 мин; T0 — при GO.

T1 = `<u64 as StableSmallSortTypeImpl>::small_sort` (impl `T: FreezeMarker`), T2 = `<u64 as
UnstableSmallSortTypeImpl>::small_sort` (impl `T: FreezeMarker`), T3 = `<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort`
(impl `T: FreezeMarker + CopyMarker`).

## Цель

Добавить на T1–T3 **содержательные `ensures`**: для u64, длины 2 и канонического comparator результат отсортирован
и является перестановкой входа (полные значения u64); доказать их `proof_for_contract` и использовать через
`stub_verified` в реальном вызывающем пути. Это пилот формы postcondition, не перенос всей модели на generic `T`.

## Дизайн (обязательный)

1. **Verification-only модель, диспетчер по паре `(T, F)`.** Трейт вида `M<T, F>` с blanket impl с `default`-методами и
   специализацией для `(u64, U64Cmp)`, где `type U64Cmp = fn(&u64, &u64) -> bool`. Runtime API, bounds, тела, сигнатуры
   методов не меняются. Принятие такой специализации Rust/Kani — гипотеза; отказ = результат (blocker), не повод
   обходить через специальный `impl for u64` у самих SmallSort-трейтов.
2. **Default** (все прочие `T`/`F`): `enabled = false`, sorted/permutation = `true`, snapshot нейтральный; ничего не
   разыменовывает. **Специализация:** `enabled` только при `len == 2` и указателе comparator, равном одному
   конкретному чистому `canonical_less_u64` (сравнение адреса — как в существующем `profile_canonical_comparator`);
   никаких downcast/transmute произвольного `F`, никакого `size_of::<F>()`.
3. **Условные ensures:** `!old(enabled) || (sorted && pair_permutation)`. Новый `requires` на канонический comparator
   **не** добавлять: прочие comparators сохраняют прежний frame-only scope. G1 `requires`/`modifies` не менять.
4. **Old-capture:** `old(M::snapshot(v.as_ptr(), v.len()))`, результат — Copy-кортеж `(u64, u64)`; не `old(v)`, не
   clone, не сохранённая ссылка. Snapshot читает только при `len == 2` и безопасен при eager-вычислении. Permutation
   для N2: `post == pre || post == swapped(pre)` по полным u64; sorted: `post.0 <= post.1`.
   **Оговорённый fallback** (только если native `old` не компилируется/не разрешается): readonly ghost `PRE_PAIR` +
   **дополнительный условный** `requires`, связывающий его с фактической парой в enabled-домене (G1 `requires`/`modifies`
   сохраняются). Все enabled PFC/consumer устанавливают `PRE_PAIR` до вызова; ghost вне write set. Сохранение
   pre-state `enabled` — через ghost snapshot либо обоснованную неизменность по frame; не подменять pre-state guard
   ослабляющим post-state guard. Одного `kani::assume` в harness или несвязанного ghost недостаточно. Применение
   fallback — отдельная пометка в RESULT, новые `requires` дословно.
5. **Видимость:** модель и `canonical_less_u64` доступны при `cfg(kani)` **без** controls (атрибуты на настоящих
   методах иначе сломают ordinary cfg-off компиляцию); только новые harnesses — opt-in под
   `cfg(kani_smallsort_controls)`. Не прятать модель в полностью cfg-gated `trait_contracts.rs`.
6. В корнях **E1–E3 и C1** `let mut cmp: U64Cmp = canonical_less_u64;` (не function item — иначе выберется default)
   и `kani::assert(enabled)` / cover до вызова.

## Строки (10)

Все входы `kani::any()`; T1: `[u64; 2]` + scratch 18; T2, T3 и consumers: backing `[u64; 4]`, активный `v = [1..3]`,
внешние элементы проверяются. Covers сильных PFC: обе ветки входа (по условию до вызова), равные значения, возврат.

| Row | Что | expect |
|---|---|---|
| E1 | `proof_for_contract(T1)`, сильный ensures, `U64Cmp = canonical_less_u64` | SUCCESS, covers все |
| E2 | `proof_for_contract(T2)`, то же | SUCCESS, covers все |
| E3 | `proof_for_contract(T3)`, то же, внешний frame | SUCCESS, covers все |
| C1 | consumer: `stub_verified(T3)`, вызов через реальный T2, та же геометрия/F; assert sorted, pair permutation по **независимо сохранённой** паре прямыми сравнениями u64, внешний frame | SUCCESS |
| N1 | oracle: специализированный checker; сначала неизменённая пара проходит, затем XOR старшего бита одного u64 и тот же checker | FAILED, 1 = назначенная |
| N2 | weak summary: G1 S2 без изменений (function-item `F`, default-модель) | FAILED, 1 = sortedness |
| N3 | wrong comparator: тот же тип `U64Cmp`, значение `reverse_less`; assert `!enabled`; `stub_verified(T3)` через T2; assert sorted | FAILED, 1 = sortedness (не requires) |
| W1 | G1 P3 без изменений (function-item `F`) — актуальный weak leaf/frame | SUCCESS |
| R1, R2 | G1 R1/R2 без изменений | SUCCESS |

`--harness-timeout 5m`; unwind новых корней 32, R1/R2 — прежние; флаги организаторов (`--no-assert-contracts`,
object-bits 12) без изменений; uninit/value-validity выкл. **`inventory: true` в той же сборке** — если gcb-k1.sh
выполняет list до экспорта controls RUSTFLAGS, это cfg-off inventory 235 (подтвердить по evidence фактические флаги);
иначе не выдавать за native: inventory NOT_RUN, интеграционная часть этапа — PARTIAL (proof-результаты сохраняются).
Данные list и rows атрибутировать их фактическим флагам и одному library tree. Paid build timeout — численно по расчёту, ≤ 120 мин; резерв
(setup + inventory + 10 строк) и worst-case repair ≤ $3.

## Приёмка

- PASS: E1–E3, C1 SUCCESS, все обязательные covers (включая `enabled` до вызова); N1–N3 FAILED ровно на назначенной
  проверке; W1, R1, R2 SUCCESS; native inventory cfg-off = 235 точное совпадение. Без него — PARTIAL, не PASS: модель
  используется атрибутами core, и controls-on компиляция не подтверждает ordinary-конфигурацию.
- Статика (скрипт в `traitpfc/`, лексер/expander из `renamemods/`): 235 ordinary имён/тела/атрибуты/callback items
  неизменны; тела/сигнатуры/bounds/`inline`/`default` и G1 `requires`/`modifies` неизменны. Whitelist library:
  `smallsort.rs` (только `ensures` на T1–T3 и, в fallback, условный ghost-`requires`), `verify.rs` (регистрация/карта),
  `verify/trait_contracts.rs` (новые корни; G1-корни неизменны), новый model-модуль. Feature gates и API core не
  менять; G1 opt-in корни неизменны; cfg-on = 254 + 6 = **260**; rustfmt — ноль diff; новых строк > 100 нет.
- Различать дословно: frontend/resolution/specialization error, unsupported, TIMEOUT, обычный FAILED. Невыразимость
  модели/binding без изменения runtime API — **blocker в RESULT**, не ослабление ensures до `true` ради PASS.
- Repair (одна сборка) — только синтаксис/квалификация атрибутов, форма old-capture или оговорённый fallback п. 4;
  не менять тела/API core и feature gates, не подменять blanket impl конкретным `impl for u64`, не убирать проверки.

## RESULT

**RESULT-TRAITPFC-G2.md**, ≤ 40 строк: identities; дословные ensures и сигнатуры модели; old-capture native или
fallback; таблица 10 строк (status, время, failed/total, covers, unreachable, упавшие проверки полностью); inventory;
классы отказов; расход; что доказано (u64/N2/канонический fn-pointer, перечисленные layouts) и что нет (generic `T`/`F`,
другие длины, прочие UB-классы, unwind).

## Коммиты, ожидание, запреты

- Library-коммит отдельно от research-коммитов, все `[skip ci]`; push без force; глобальный git config не менять.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание сборки: `k1g.sh watch BUILD`, затем конец хода.
- Evidence — сначала `smallsort-brief BUILD` (основной интерфейс); если сборка не индексирована или нужного поля нет —
  зафиксировать ограничение и использовать bounded K-1 summaries/rows/peaks/log-grep через `k1g.sh`, как в G1. Прямых GCS/storage/download/logging-команд нет; raw logs, archives, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC (rustfmt через обёртку
  `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --edition 2024 --config-path
  research/challenge-8/kani-k1/codefix/rustfmt.toml`), Actions/PR/issue/комментарии на GitHub.
- Только наш код, наши RESULT, документация и исходники/тесты Kani на `f046b70644`. Чужие PR verify-rust-std, их
  ветки и код не открывать. Workflows, скрипты и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **TRAITPFC G2 ЗАВЕРШЁН**, одна стадия, затем стоп.
