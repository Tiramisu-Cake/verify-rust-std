# KANI5116 KF2 — smoke: контракты на `default fn` реализациях `small_sort` в core с патченным Kani

**Выдано координатором 2026-11-11, в рамках GO владельца на работу по kani#5116.** Research-ветка, в подачу не идёт.
Dispatch только после exact-packet PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani5116**, ветка **experiment/kani-k1-kani5116-20261110** от KF1 PASS
  `cdc6e09aef` (RESULT-KANI5116-KF1.md). **Tooling base: `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`**; tooling, пин
  `f046b70644`, toolchain не менять.
- Kani = пин + **KF1 patch** `research/challenge-8/kani-k1/kani5116/kf1/kani-fix.patch` (SHA-256
  `fd510b8a47ffff2005cc2362af6c25db790d1b579a23c0c990f6d606a983aa71`) через `kani_patch` в request, kind
  **`diagnostic`** (маршрут verify-std с patch реализован в KT1, ещё не исполнялся — это часть проверки).
- Slug **kani5116**, stage `kani5116-kf2`, stable owner **k1-merge**, request `kani5116-kf2-*`.
- Свой cap **$0.80**; одна сборка, repair — только если фактический расход + новый резерв ≤ $0.80. Лимиты ветки
  (накопительно $2.30, timeout ≤ 59 мин) уже в tooling: строк × timeout + 30 ≤ 59. Окно: main 300 + closeout 30.
- Параллельно в /root/verify-rust-std-kani-traitpfc идёт другой этап — не трогать.

## Цель

Показать на реальном core, что с исправлением kani#5116 контракты ставятся прямо на **`default fn`** реализации
`small_sort`, и PFC/`stub_verified` выбирают именно default impl:
- D1 `<Cell<u8> as StableSmallSortTypeImpl>::small_sort` — default `impl<T>` (insertion);
- D2 `<Cell<u8> as UnstableSmallSortTypeImpl>::small_sort` — default `impl<T>` (fallback);
- D3 `<NonCopyU8 as UnstableSmallSortFreezeTypeImpl>::small_sort` — default `impl<T: FreezeMarker>` для Freeze !Copy
  — свой verification-only `NonCopyU8(u8)` в новом модуле (без Copy/Drop) с `kani::Arbitrary`, генерирующим
  произвольный байт (нужен для `write_any_slice` в `modifies` stub; тип из forwarding_contracts приватен).
Это resolution/frame smoke, **не** доказательство сортировки.

## Library-изменения

1. `smallsort.rs`: на трёх `default fn small_sort` — только `#[cfg_attr(kani, crate::kani::requires(...))]` (то, что
   реально нужно телу, обосновать; если ничего — без requires) и `#[cfg_attr(kani, crate::kani::modifies(v))]`
   (D1 `_scratch` не читает и не пишет: в harness'ах передавать `&mut []`, в modifies не включать, ёмкость не
   требовать). **Не** `#[safety::requires/ensures]` (их собственный parser не
   исправлен). Тела, сигнатуры, bounds, `inline`, `default` — байт-неизменны; `ensures` нет (если PFC требует —
   только помеченный калибровочный `ensures(|_| true)`).
2. Новый opt-in модуль `verify/default_contracts.rs` целиком под `#[cfg(kani_smallsort_controls)]` + одна строка в
   `verify.rs`. Обычный набор (235) не трогать.

## Строки (kind diagnostic, controls on, inventory false, standard4/jobs1, флаги организаторов без изменений)

Компаратор — один именованный function item на маршрут (без coercion к fn pointer в P3/S0/S1/S2), читает оба
аргумента. Геометрия N2. Covers P1–P3 — ровно 3: обе стороны предвычисленного порядка входной пары и возврат.

| Row | Что | expect |
|---|---|---|
| P1 | `proof_for_contract(D1)`, `[Cell<u8>; 2]`, covers: обе ветки входа + возврат | SUCCESS, covers все |
| P2 | `proof_for_contract(D2)`, то же | SUCCESS, covers все |
| P3 | `proof_for_contract(D3)`, backing `[NonCopyU8; 4]`, `v = [1..3]`, внешний frame | SUCCESS, covers все |
| S0 | unstubbed-двойник S1/S2: тот же Freeze-forwarder, backing/срез/F; assert frame и порядок `v[0] <= v[1]` | SUCCESS |
| S1 | consumer: `stub_verified(D3)`, вызов через реальный `<NonCopyU8 as UnstableSmallSortTypeImpl>::small_sort` (Freeze impl, форвард в D3), тот же backing; assert frame | SUCCESS |
| S2 | как S1, но assert `v[0] <= v[1]` (по модели) — со слабым контрактом обязан упасть ровно здесь (тело заменено стабом) | FAILED, 1 = назначенная |

Для S0/S1/S2 можно взять исходно упорядоченную пару (`assume` до вызова), чтобы пропуск вызова не дал ожидаемого
отказа; S1 подтверждает возврат. `--harness-timeout 4m` (6 × 4 + 30 = 54 ≤ 59, резерв $0.7290), unwind по телам N2.
У S2 — уникальный `expect_check`; вручную сверить ровно 1 failed с нужной локацией (gate проверяет статус и
подстроку, но не полноту covers и единственность отказа); P1–P3 — 0 failed и 3/3 covers.

## Приёмка

- PASS: P1–P3 SUCCESS с 0 failed и всеми covers; S0, S1 SUCCESS; S2 FAILED ровно на назначенной проверке. До
  dispatch зафиксировать, где bounded способом видно привязку `Verified stub`/target; если прямого свидетельства
  нет — записать эффект S0/S2 как проверенный, прямой target trace — UNCONFIRMED (raw logs не читать). Identity: pin + patch SHA-256 + applied tree в summary, check-tooling PASS.
- Отказ компиляции/разрешения — **результат** (blocker с дословным текстом), не повод менять core или Kani-патч.
  Repair — только атрибуты/квалификация путей в harness'ах.
- Не проверяется: обычная cfg-off компиляция 235 с этими атрибутами (`cfg_attr(kani, …)` действует и там;
  inventory не в этом этапе — NOT_RUN), сортировка, произвольный FnMut, safety-атрибуты, upstream CI. Вывод
  ограничен N2 и выбранными T/F/геометрией.
- Статика: изменены только `smallsort.rs` (атрибуты на трёх default fn), `verify.rs` (одна строка),
  `verify/default_contracts.rs`; rustfmt — ноль diff; строк > 100 нет.

## RESULT

**RESULT-KANI5116-KF2.md**, ≤ 35 строк: identities; дословные атрибуты; таблица строк (status, время,
failed/total, covers, упавшие проверки полностью); привязка stub/PFC; расход; что это значит для подачи (что
понадобится после попадания фикса в пин verify-rust-std).

## Коммиты, ожидание, запреты

- Library-коммит отдельно от research, все `[skip ci]`; push без force; глобальный git config не менять; без
  `git stash`.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание: `k1g.sh watch BUILD`, затем конец хода.
- Evidence — bounded `k1g.sh` summary/rows (как в KT1/KF1); raw logs, archives, credentials не читать; прямых
  GCS/storage/download/logging нет.
- Никаких локальных cargo/rustc/Kani/CBMC; rustfmt через обёртку
  `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --edition 2024 --config-path
  research/challenge-8/kani-k1/codefix/rustfmt.toml`. Никаких Actions/PR/issue/комментариев, fork или push в Kani.
- Чужие PR verify-rust-std, их ветки и код не открывать.

Маркеры `REVIEW REQUEST <sha>` / **KANI5116 KF2 ЗАВЕРШЁН**, одна стадия, затем стоп.
