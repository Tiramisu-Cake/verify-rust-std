# TRAITPFC G1 — контракты прямо на trait-методах `small_sort`: разрешение и frame (пилот)

**Выдано координатором 2026-11-10, GO владельца на исследование.** Research-ветка, в подачу не идёт. Dispatch только
после exact-packet PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-traitpfc**, ветка **experiment/kani-k1-traitpfc-20261110**.
- База: library = подаваемое дерево SmallSort (`slice/sort` и `library/core/Cargo.toml` байт-идентичны `872d5a4338`),
  слит upstream main `25b2b24c82` (nightly-2026-10-23), затем коммит **9b1758ab817af005e96fd52a5fc940d4b6acf984**:
  пин Kani **`f046b70644e113be0df9c22c2e6ea44a65a57566`** (Kani main с kani#5135: разрешение method-level generics в
  trait contracts/stubs). Toolchain Kani на этом коммите — тот же nightly-2026-10-23.
- **Tooling base для check-tooling: `9b1758ab817af005e96fd52a5fc940d4b6acf984`** (не 59893bff1f: пин и toolchain
  изменены намеренно, с GO владельца). Tooling, workflows, `kani-version.toml`, `rust-toolchain.toml` дальше не менять.
- Slug **traitpfc**, stable owner **k1-merge**. Request_id/stage/ledger `traitpfc-*`.
- Project cap **$118.96** (использовано ≈ $109.20 — проверь фактический остаток), свой cap **$2.00**. **Одна сборка G1**;
  один compile-error repair второй сборкой, если own spent + reserve ≤ cap. Retry нет. Сборка Kani из исходников
  нового пина входит в стоимость — учти в резерве.
- Окно: main 300 + closeout 30 мин.

## Цель

Проверить на реальном коде, что Kani `f046b70644` принимает контракты и `proof_for_contract`/`stub_verified` на
**не-`default`** реализациях трёх trait-методов в `smallsort.rs`:

| Цель | impl | тело |
|---|---|---|
| T1 `<u64 as StableSmallSortTypeImpl>::small_sort` | `impl<T: FreezeMarker> StableSmallSortTypeImpl for T` (L51–66) | `small_sort_general_with_scratch` |
| T2 `<u64 as UnstableSmallSortTypeImpl>::small_sort` | `impl<T: FreezeMarker> UnstableSmallSortTypeImpl for T` (L92–106) | форвард в Freeze-трейт |
| T3 `<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort` | `impl<T: FreezeMarker + CopyMarker> UnstableSmallSortFreezeTypeImpl for T` (L144–172) | network/general/fallback |

Это калибровка механизма, **не** доказательство сортировки: содержательные `ensures` (sorted + full-value) — следующий
этап (G2) отдельным заданием.

## Library-изменения

1. `smallsort.rs`: на трёх методах T1–T3 — контрактные атрибуты в стиле существующих хелперов
   (`#[safety::requires(...)]`, `#[cfg_attr(kani, crate::kani::modifies(...))]`; поддержку `safety::ensures` не
   предполагать). `requires` — только то, что действительно нужно телу (обосновать по коду, например ёмкость scratch у
   T1); `modifies` — `v`, а у T1 также память scratch, если тело в неё пишет (выяснить, как Kani выражает это для
   `&mut [MaybeUninit<T>]`; весь scratch не читать как инициализированный `T`). `ensures` в G1 не добавлять; если Kani
   требует непустой postcondition для PFC — только явно помеченный калибровочный `ensures(|_| true)`.
   **Нельзя:** менять тела, сигнатуры, bounds, `inline(always)`, `default fn`; добавлять специальные `impl for u64`.
2. Новый opt-in модуль `verify/trait_contracts.rs` целиком под `#[cfg(kani_smallsort_controls)]` + регистрация в
   `verify.rs` (карта модулей — одна строка). Обычный набор (235) не трогать.

## Строки G1 (kind diagnostic, `controls: true`, `inventory: false`, jobs 1, standard4)

Один именованный function item-компаратор `u64 <` (не arbitrary, не захватывающее замыкание) во всех строках.
Геометрия: P1, P2 — `[u64; 2]` из `kani::any()`; **P3, S0, S1, S2 — один backing `[u64; 4]` из `kani::any()`,
активный `v = &mut backing[1..3]`** (длина 2), внешние `backing[0]`, `backing[3]` сохраняются и проверяются.
Covers P1–P3: по условию, сохранённому **до** вызова, `input_descending = v[1] < v[0]` (обе ветки) и возврат —
ровно 3 на строку; ожидаемый набор covers всех строк зафиксировать в пакете до dispatch.

| Row | Что | expect |
|---|---|---|
| P1 | `proof_for_contract(T1)`; scratch `[MaybeUninit<u64>; L]`, L — минимально достаточная ёмкость по `requires` | SUCCESS, covers все |
| P2 | `proof_for_contract(T2)` | SUCCESS, covers все |
| P3 | `proof_for_contract(T3)` на backing `[u64; 4]`, `v = [1..3]`; assert: `backing[0]`, `backing[3]` не изменились | SUCCESS, covers все |
| S0 | точный unstubbed-двойник S1/S2: вызов через T2, тот же backing/срез/компаратор, без стаба; assert `v[0] <= v[1]` и внешние элементы не изменились | SUCCESS |
| S1 | consumer: `stub_verified(T3)`, вызов **через T2** (реальное тело T2 форвардит в застабленный T3); backing/срез как у P3; assert: элементы вне `v` не изменились | SUCCESS |
| S2 | контроль: как S1, но assert `v[0] <= v[1]`; со слабым контрактом обязан упасть ровно на этом assert (доказывает, что тело заменено стабом) | FAILED, 1 проверка = назначенная |
| R1, R2 | регрессия: по одному существующему ordinary-харнессу, вызывающему stable и unstable trait entry для Freeze-типа (выбрать и обосновать) — контрактные атрибуты и новый пин их не ломают | SUCCESS |

`--harness-timeout 5m` (N2; 10m только если расчёт показывает необходимость); paid build timeout — численно, по
расчёту setup + сборка Kani + 8 строк, не больше 120 мин; в PRE-BUILD — полный расчёт резервации. Cap и окно
автоматически не расширять.

## Приёмка G1 и как фиксировать отказы

- PASS: P1–P3 SUCCESS с 0 failed и всеми covers; S0, S1 SUCCESS; S2 FAILED ровно на назначенной проверке; R1–R2
  SUCCESS. Пара S0 SUCCESS / S2 FAILED калибрует действие стаба; по доступной диагностике подтвердить, что
  `stub_verified` привязан именно к T3. Это проверка механизма, не содержательный sorting-контракт.
- Статическая приёмка (скрипт в `research/challenge-8/kani-k1/traitpfc/`, лексер/expander из `renamemods/`): 235
  прежних ordinary имён, их тела/атрибуты и T/F/домен/stub/unwind/solver сохранены; тела, сигнатуры, bounds, `inline`
  и `default` методов `smallsort.rs` байт-неизменны, кроме новых контрактных атрибутов на T1–T3; изменены только три
  файла; cfg-on = 248 + 6 новых корней (P1–P3, S0–S2) = **254** (R1, R2 — существующие корни). Полный native
  inventory отдельной сборкой в G1 не нужен. `rustfmt --check` — ноль diff; строк > 100 нет.
- Различать и записывать дословно: ошибка разрешения/frontend (compile error, текст Kani), unsupported-проверки,
  TIMEOUT, обычный FAILED. Отказ разрешения T1/T2/T3 — **результат** (новый blocker с минимальным текстом ошибки), а не
  повод обходить: не менять код core, чтобы «помочь» резолверу. Допустим один repair только путей/квалификации в
  атрибутах harness'ов и синтаксиса контрактных атрибутов.
- Сохранить точные T/F/N/геометрию scratch, флаги, covers, число проверок.

## RESULT

**RESULT-TRAITPFC.md**, ≤ 40 строк: identities (library SHA/tree, diff к базе — только `smallsort.rs`, `verify.rs`,
`verify/trait_contracts.rs`; пин Kani); тексты добавленных контрактов (дословно); таблица строк (status, время,
failed/total, covers, упавшие проверки полностью); отказы по классам; warnings; расход; что это значит для G2
(какой `ensures` выглядит выразимым, что мешает).

## Коммиты и ожидание

- Library-коммит отдельно от research-коммитов, все `[skip ci]`. Push без force. Глобальный git config не менять.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание сборки: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход.

## Запреты

- Evidence — через **`smallsort-brief` BUILD** (Evidence Brief, основной интерфейс результата); `k1g.sh` — для
  dispatch/watch/summary. Этот интерфейс не обходить: никаких прямых GCS/storage/download/logging-команд. Raw logs, archives, Cloud Logging и credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC (rustfmt через обёртку
  `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --edition 2024 --config-path
  research/challenge-8/kani-k1/codefix/rustfmt.toml` разрешён), Actions/PR/issue/комментарии на GitHub.
- Только наш код, наши RESULT, документация и исходники/тесты Kani на `f046b70644` (синтаксис контрактов и
  `proof_for_contract` для trait-методов). Чужие PR verify-rust-std, их ветки и код не открывать.
- Workflows, скрипты и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **TRAITPFC G1 ЗАВЕРШЁН**, одна стадия, затем стоп.
