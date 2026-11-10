# TRAITPFC G3 — PR-готовые контракты сортировки на trait-методах `small_sort` (u64, N2 и N3)

**Выдано координатором 2026-11-10, GO владельца на расширение.** Research-ветка; цель — library-патч, который можно
одним коммитом добавить в поданный PR после того, как пин verify-rust-std включит kani#5135. Dispatch только после
exact-packet PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-traitpfc**, ветка **experiment/kani-k1-traitpfc-20261110**, от G2 PASS
  **3a16a173b0** (RESULT-TRAITPFC-G2.md). Пин Kani `f046b70644`, nightly-2026-10-23; **tooling base для
  check-tooling: `9b1758ab817af005e96fd52a5fc940d4b6acf984`**. Tooling, workflows, пин, toolchain не менять.
- Slug **traitpfc**, stage `traitpfc-g3`, stable owner **k1-merge**, request `traitpfc-g3-*`.
- Свой cap **$3.50** (проверь фактический остаток проекта, cap $118.96). **Не больше двух сборок**: Build 1 —
  пакет ниже; Build 2 — либо один compile-error repair, либо финальное сужение (п. «Build 2»), не оба. Retry,
  третьей сборки, расширения cap/окна нет. После Build 1 пересчитать остаток и зафиксировать точный план Build 2.
- Окно: main 360 + closeout 30 мин; T0 — при GO.

T1 = `<u64 as StableSmallSortTypeImpl>::small_sort`, T2 = `<u64 as UnstableSmallSortTypeImpl>::small_sort`,
T3 = `<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort` (не-`default` impl, как в G1/G2).

## Цель

Одна окончательная модель и условные ensures на T1–T3: для u64, канонического comparator и длин **2 и 3** результат
отсортирован и является перестановкой входа с полными кратностями u64. Сильные PFC и matching consumer — **ordinary**
(в обычном наборе), калибровки — opt-in. Каждое утверждение — bounded по перечисленным instantiations/layouts.

## Дизайн (обязательный)

1. **Одна модель вместо `PairModel`.** `trait_model.rs` → один нейтрально названный трейт (например
   `SortModel<T, F>`) в cfg(kani)-модуле, компилируемом **без** controls: `enabled`, `snapshot`, общий post checker
   (sorted + permutation). `PairModel` не оставлять параллельно. Blanket default: `enabled = false`, нейтральный
   snapshot, checker `true`, ничего не разыменовывает. Специализация только `(u64, U64Cmp)`,
   `U64Cmp = fn(&u64, &u64) -> bool`, точное значение `canonical_less_u64` (сравнение адреса); function item сильную
   модель не получает.
2. **Whitelist по entry.** `enabled` отражает конкретный метод/T/F/значение/N: verification-only тег entry (T1/T2/T3)
   как аргумент модели, без изменения runtime API. Длина включается для метода только если в пакете есть его
   ordinary real-body leaf на этой длине. Неподтверждённая длина не остаётся enabled.
3. **Условные ensures:** `!old(enabled(...)) || check(old(snapshot(...)), текущее состояние)`. Новых `requires` нет;
   G1 `requires`/`modifies` не менять. Postcondition не вызывает `F`; sortedness — чистым модельным порядком `<=`.
4. **Snapshot:** фиксированная Copy-структура `{ len, valid, vals: [u64; 3] }`, полностью инициализированная; читает
   только живой префикс `len` активного среза, не scratch. Неподдержанная длина → invalid без чтения; молчаливого
   `min(len, K)` нет. `kani::any` в ensures/`old` нет. Native `old` Copy-snapshot — первый выбор; если не
   компилируется — blocker в RESULT (или заранее чистая Copy-форма тем же repair), без ghost-протокола.
5. **Permutation:** одинаковая длина, `valid`, `len <= 3`; для каждого живого `pre[i]`
   `count(pre[..len], pre[i]) == count(post[..len], pre[i])`; padding не участвует; без сумм/хешей/set-only.
   Для N2 допустим короткий путь, эквивалентный G2 pair-формуле. Один post-snapshot, без повторных чтений.
6. **Без изменений:** тела, сигнатуры, bounds, `inline`, `default`, feature gates, API core; нет `impl for u64` у
   SmallSort-трейтов; ensures не ослаблять до `true` ради PASS; `default fn` (kani#5116) вне scope.

## Library-раскладка (PR-кандидат)

- `smallsort.rs`: ensures G2 заменить новой формой на T1–T3 (с тегом entry).
- `verify/trait_model.rs`: модель п. 1–5.
- `verify/trait_contracts.rs`: **обычный** модуль (без cfg-gate на модуле); ordinary positives ниже; каждый
  control/FAIL-root — свой `#[cfg(kani_smallsort_controls)]`. G1/G2 исследовательские корни не переносить (они
  сохранены на 3a16a173b0); общий helper контроля не терять.
- `verify.rs`: регистрация и module map — PR-качество: что доказано (entry/T/F/N/геометрия), условность контракта,
  ограничение callback-frame; поправить строку «Not covered: Trait methods have no contracts…» под новое состояние
  (не-`default` impl покрыты на перечисленном домене, `default fn` — kani#5116).
- Имена/доки property-oriented, без stage-меток (G1/G2/G3, traitpfc) в library.

## Строки Build 1

Входы — `kani::any()` без ограничений значений/дубликатов. T1: `[u64; N]` + scratch `N + 16`; T2/T3/consumer: backing
`[u64; N + 2]`, активный `v = &mut backing[1..N + 1]`, внешние элементы проверяются. В positive roots `let mut cmp:
U64Cmp = canonical_less_u64;`, `kani::assert(enabled)` и cover до вызова; covers: ascending, descending, с дубликатом,
возврат (фиксировать ожидаемый набор в пакете).

| Row | Вид | Что | expect |
|---|---|---|---|
| A1, A2 | ordinary | PFC T1 N2, N3 (реальное тело) | SUCCESS, covers все |
| A3, A4 | ordinary | PFC T3 N2, N3 (реальное тело, внешний frame) | SUCCESS, covers все |
| A5, A6 | ordinary | PFC T2 N2, N3 (реальное тело T2; допустим `stub_verified(T3)` при matching A3/A4 leaf) | SUCCESS |
| C1 | ordinary | consumer N3: `stub_verified(T3)` через реальный T2; независимая pre-copy, typed reads: порядок, полные кратности, внешний frame | SUCCESS |
| K1 | opt-in | oracle N3: checker принимает неизменённый снимок, затем XOR старшего бита одного значения | FAILED, 1 = назначенная |
| K2 | opt-in | кратности: `pre=[a,a,b]`, `post=[a,b,b]`, `a<b` (те же множества) | FAILED, 1 = назначенная |
| K3 | opt-in | reverse pointer того же `U64Cmp`, assert `!enabled`, `stub_verified(T3)` через T2, assert sorted | FAILED, 1 = sortedness |
| K4 | opt-in | default calibration: function-item `F` (default модель), consumer N3 через stub, assert sorted | FAILED, 1 = sortedness |
| R1, R2 | ordinary | G1/G2 R1/R2 без изменений | SUCCESS |

Итого ordinary = 235 + 7 = **242** (пересчитать по фактическому manifest); cfg-on manifest — заново полным списком.
`--harness-timeout 5m`, unwind новых корней 32 (проверь циклы oracle/тел), R1/R2 прежние; флаги организаторов
(`--no-assert-contracts`, object-bits 12) без изменений; uninit/value-validity выкл.; standard4/jobs1. **`inventory:
true`** — native cfg-off inventory нового ordinary-набора (ожидание 242, точное совпадение имён) в той же сборке, с
атрибуцией флагов как в G2. Paid build timeout — численно по расчёту, ≤ 120 мин; в PRE-BUILD — расчёт резерва и
стоимость worst-case Build 2 в пределах $3.50.

## Build 2 (только одно из двух, по результатам Build 1)

- **Repair:** только синтаксис/квалификация атрибутов или форма old-capture п. 4, тот же набор строк.
- **Финальное сужение**, если часть ordinary-строк не прошла (TIMEOUT/FAILED не из-за ошибки кода): соответствующие
  длины убрать из whitelist и из ordinary (оставить opt-in или удалить), C1 — на наибольшей прошедшей длине;
  проверить **финальное** library tree: inventory + все оставшиеся ordinary positives + K1–K4. Без новых длин/типов.
- Если Build 1 PASS целиком — Build 2 не нужен.

## Приёмка

- PASS: все ordinary positives SUCCESS со всеми covers и `enabled` до вызова; K1–K4 FAILED ровно на назначенной
  проверке; R1, R2 SUCCESS; native cfg-off inventory = фактический ordinary manifest точно; финальное library tree =
  проверенное. Если N3 не прошёл где-то и сужение сделано — PASS по оставшемуся scope, непрошедшее — resource-open.
- Composed SUCCESS без matching real-body leaf proof credit не даёт; такой consumer не ordinary.
- Статика (скрипт в `traitpfc/`, лексер/expander из `renamemods/`): прежние 235 ordinary имён/тела/атрибуты/домены
  неизменны; 13 controls прежнего набора неизменны; тела/сигнатуры/bounds/`inline`/`default` и G1
  `requires`/`modifies` неизменны. Whitelist library: `smallsort.rs` (только ensures на T1–T3), `verify.rs`,
  `verify/trait_model.rs`, `verify/trait_contracts.rs`. rustfmt — ноль diff; новых строк > 100 нет.
- **PR-применимость:** library-diff от `9b1758ab81` до финального library-коммита должен чисто применяться к поданному
  head `872d5a4338` (проверить без изменения веток submission, например `git apply --check` на временном worktree в
  scratchpad, затем удалить его по литеральному абсолютному пути); сохранить patch в `traitpfc/g3/`.
- Различать дословно: frontend/resolution/specialization error, unsupported, TIMEOUT, обычный FAILED. Новые panic
  cuts/assumptions и отключение unwinding assertions ради времени запрещены.

## RESULT

**RESULT-TRAITPFC-G3.md**, ≤ 45 строк: identities (library SHA/tree по сборкам, patch SHA-256); дословные ensures и
сигнатуры модели; old-capture; таблица строк (status, время, failed/total, covers, упавшие проверки полностью);
inventory; раздельно: code-ready, bounded proof PASS, resource-open; поддержка по entry/T/F/N/геометрии; ΣVT новых
ordinary строк; baseline→final delta (ordinary/cfg-on); расход; что не доказано (generic `T`/`F`, другие длины/типы,
прочие UB-классы, unwind, реальный PR-CI на pin с #5135 — не заявлять).

## Коммиты, ожидание, запреты

- Library-коммит(ы) отдельно от research-коммитов, все `[skip ci]`; push без force; глобальный git config не менять;
  `git stash` не использовать.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO (перед каждым Build). Ожидание: `k1g.sh watch BUILD`,
  затем конец хода.
- Evidence — сначала `smallsort-brief BUILD`; если сборка не индексирована/поля нет — зафиксировать и использовать
  bounded K-1 summaries/rows/peaks/log-grep через `k1g.sh`. Прямых GCS/storage/download/logging-команд нет; raw
  logs, archives, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC (rustfmt через обёртку
  `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --edition 2024 --config-path
  research/challenge-8/kani-k1/codefix/rustfmt.toml`), Actions/PR/issue/комментарии на GitHub.
- Только наш код, наши RESULT, документация и исходники/тесты Kani на `f046b70644`. Чужие PR verify-rust-std, их
  ветки и код не открывать. Workflows, скрипты и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **TRAITPFC G3 ЗАВЕРШЁН**, одна стадия, затем стоп.
