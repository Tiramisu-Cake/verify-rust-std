# Challenge 8: минимальный план — Kani как основной путь, VeriFast только точечно

> **Заменено 2026-10-26:** §1, §4–§7 этой редакции заменены редакцией 3 — `CH8-MINIMAL-PLAN-R3-2026-10-26.md` (K-1 закрыт как отрицательный, переход к гибриду Kani + stock VeriFast для слияния). Приложения A–E остаются в силе.

Редакция 2 от 2026-10-24. Первая редакция — скрининг по брифу `ALTERNATIVE-TOOLS-BRIEF-2026-10-24`, рекомендовала «оставить форк VeriFast». Эта редакция пересматривает выбор инструмента по планке **М** (минимум для приёма) из `REQUIREMENTS-INTERPRETATION-2026-10-24.md`. Фактическая база скрининга не изменилась и вынесена в приложения A–C. Поменялись критерии отсева, а с ними и вывод.

Состояние источников:
- `model-checking/verify-rust-std` `main` = `c0bd09c3` (2026-10-22);
- Kani `main` = `cd355b0` (2026-10-23), в CI запинен `9461e07a`;
- VeriFast в CI — 26.10, бинарный релиз с attestation-хэшем (`verifast-proofs/setup-verifast-home`).

## 1. Резюме

**Рекомендация: минимальный план строить на Kani. Форк VeriFast заморозить как основной путь и вернуться к нему только как к необязательному слою К.** Так выходит из-за смены планки. Unwind-путь и обобщённое по `T` доказательство были единственными требованиями, которые выполнял только форк, а теперь оба — уровень К. Остальные требования М Kani закрывает средствами, уже включёнными в CI: `-Z loop-contracts -Z function-contracts -Z stubbing -Z quantifiers` (`scripts/run-kani.sh:87`).

У VeriFast против минимума два структурных препятствия:
- **допустимость** — CI тянет релизный бинарник 26.10, а решение на патченном форке не будет «одобренным и ранее интегрированным» инструментом, пока патчи не войдут в upstream; PR 1046 открыт без ревью, upstream ведёт один мейнтейнер;
- **сам stock 26.10** не проходит A2 (реальные тела всех callee) из-за `ManuallyDrop::new`, отсутствия спеки `select_unpredictable` и union.

Три главных риска Kani-плана:
1. **Стена длины 32.** `sort13_optimal`, `bidirectional_merge`, general и network на len 32 не укладываются в 10 мин ни в одном из четырёх Kani-PR. Снимать её можно только композицией: проверенные контракты callee плюс `stub_verified`. Это эксперимент K-1, от которого зависит весь план.
2. **UB-категория «uninitialized read»** на scratch в `MaybeUninit` в CI автоматически не проверяется: `-Z uninit-checks` выключен и для union-pointee не поддержан. Нужен эксперимент K-3; иначе — раскрытие или точечное дополнение VeriFast.
3. **Конкуренция.** #678 (приоритетный у ревьюера), #694 и #701 идут тем же путём. Выигрывать придётся не скоростью подачи, а полнотой и строгостью (G1–G3, B4, C3, F1). Этого ни один из них пока не закрывает.

## 2. Что изменилось по сравнению с редакцией 1

| Было (ред. 1) | Стало | Почему |
|---|---|---|
| Жёсткий критерий К2: проверенный `CopyOnDrop::drop` на unwind | Уровень К (D3), не отсев | Организаторы не требовали; Ch5/Ch19 приняты с `-ignore_unwind_paths`; #734 называет это пределом обоих инструментов |
| Жёсткий критерий К3: универсальный `T` и stateful `FnMut` | М — представительные типы по веткам (C2/C3) и произвольный результат comparator (D1); обобщённый `T` — К (C5) | В тексте Ch8 нет «no monomorphization»; вариант A в #734 |
| Главный вывод «форк VeriFast — единственный путь» | Kani — основной путь минимума | Единственное, в чём форк был незаменим, ушло в К |
| Kani — «страховочный путь» | Kani — основной путь, но с обязательной проверкой стены 32 (K-1) | Минимум достижим, если композиция пройдёт |
| Риск «PR 1046 не влит» как неудобство | Риск допустимости: форк в CI не запускается, CI тянет бинарник 26.10 | `setup-verifast-home` скачивает релизы с attestation |

Новые факты после ред. 1:
- открыты рулинги #733 и #734 (21–23.10);
- qinheping выведен из комитета (#635, 24.08);
- doc-комментарий трейта определяет «valid length» как `len <= small_sort_threshold()` (`smallsort.rs:19`);
- внешние вызовы `insertion_sort_shift_left` идут на длинах до 20;
- `panic_on_ord_violation` в `bidirectional_merge` достижим при несогласованном comparator;
- `#[kani::should_panic]` даёт SUCCESS, если все упавшие проверки — паники (`docs/src/reference/attributes.md` в Kani).

## 3. Отсев по планке М

Новые критерии отсева. Требования из `REQUIREMENTS-INTERPRETATION` указаны в скобках.

- **Н1** — проверяется реальный исходник std без переписывания, включая все callee (A2, F5).
- **Н2** — допустимость сейчас: инструмент одобрен и интегрирован (I1).
- **Н3** — отслеживаются значения в памяти, то есть выразимы сортировка и перестановка (E3).
- **Н4** — корректная семантика нормального пути: `Drop` guard в `insert_tail` на нормальном выходе копирует элемент обратно, это часть нормального пути.
- **Н5** — неограниченные циклы через инварианты (B4).

| Инструмент | Н1 | Н2 | Н3 | Н4 | Н5 | Итог |
|---|---|---|---|---|---|---|
| Kani 0.68 | да [Ka2] | да [Ka6] | да | да: drop glue на нормальном пути исполняется | да: `-Z loop-contracts` в CI; применимость к raw-pointer циклам — K-2 | **основной путь** |
| VeriFast 26.10 (stock) | нет: `ManuallyDrop::new` (PR 1046 не влит), нет спеки `select_unpredictable`, union `failwith` [VF2][VF6][VF7] | да [VF9] | да | да | да | только точечно, если V-1 пройдёт |
| VeriFast-форк | да (частично, 15%) | **нет** — CI запускает релиз 26.10 [VF9] | да | да | да | не путь минимума; слой К после upstream |
| ESBMC | как Kani | да | да | как Kani | как Kani | только как запасной решатель для харнессов K-1; 32 крэша на slice [Es3] |
| Flux | частично | да | **нет** — значения за указателями не отслеживаются [Fl2] | неизвестно | частично | отсев |
| KMIR | нет: nightly-2024-11-29 [KM1] | да | частично | **нет** — Drop no-op [KM2] | — | отсев |
| RAPx | частично | да | нет: тег-чекер [RA2] | **нет** — деструктор не исполняется [RA3] | — | отсев |
| Creusot, Verus, Prusti, Aeneas, hax, Gillian-Rust, RefinedRust, Corten, Soteria, crux-mir, Miri, BifRust | см. прил. A | **нет**: не интегрированы; Tool Application занимает 2–17 мес | — | — | — | отсев для минимума; Miri — внутренний санити-чек |

## 4. Kani против требований М

| Треб. | Как закрывается в Kani | Статус | Эксперимент |
|---|---|---|---|
| A1, A2 | Харнессы на реальных impl, без подмены тел; callee — композиционно через `proof_for_contract` + `stub_verified` | закрываемо | K-1 |
| A3, A4 | Контракты callee проверены отдельно; preconditions проверяются при вызове из stub | закрываемо | K-1 |
| B1, B2 | Символьная длина 0..=порог: fallback ≤16 — уже достигнуто в #694; general/network ≤32 — **стена** | риск №1 | K-1 |
| B4 | Loop contracts на цикле `insertion_sort_shift_left` и цикле `insert_tail` (raw pointers, `CopyOnDrop`) | неизвестно; запасной вариант — до len 20 с раскрытием | K-2 |
| B6 | `swap_if_less` с `a != b`, `sort4_stable` ровно 4 элемента | закрыто в #694/#701 | — |
| C2, C3 | 11 инстанциаций по ветвям `Freeze`/`Copy`/`size_of` (≤8, ≤16, ≤85, ZST) | закрываемо; бюджет CI растёт в 11 раз | K-1 (типы `[u8;85]`/`[u8;86]` — самые дорогие) |
| D1 | Comparator `kani::any()` на каждом вызове | закрываемо | — |
| D2 | (а) произвольный comparator в путях с merge — harness с `#[kani::should_panic]`: нет UB до паники, кроме паники ничего не падает; (б) строгий слабый порядок — отдельный harness | закрываемо | K-4 |
| E1 | Dangling/misaligned — проверки по умолчанию. Мутация неизменяемых байтов и invalid value — вне области при принятии #733. **Uninit read** не проверяется | риск №2 | K-3 |
| E3 | `assert_sorted` + подсчёт вхождений (как в #678) | закрываемо до 32 только при K-1 | K-1 |
| E5 | Зафиксировать `merge_down` (rust-lang/rust#135984) | — | — |
| F1, F3 | Контракты на `swap_if_less`, `insert_tail`, `insertion_sort_shift_left`, `sort4_stable`, сетях, `bidirectional_merge` с `proof_for_contract`. На трёх impl — проверки в harness с раскрытием E0520/E0599 | закрываемо | K-5 |
| G1–G3 | `kani::cover` на каждый `assume` (как в #637/#694), отсутствие `assume(false)`, ledger stub и флагов | закрываемо | — |
| G4 | Внесённые мутанты в `swap_if_less`, `insert_tail`, `bidirectional_merge` | К, дёшево | — |
| H2 | ≤10 мин на harness, 4 ядра / 16 ГБ, ubuntu + macOS | риск №1 | K-1 |

## 5. Эксперименты минимального плана

Порядок задан зависимостями: K-1 решает судьбу плана, K-2…K-5 идут параллельно и независимо. На каждый эксперимент — 1–2 Cloud-прогона.

| ID | Минимальный фальсифицируемый опыт | Входы | Успех | STOP / откат | Затраты |
|---|---|---|---|---|---|
| **K-1** | Композиция на len 32. Порядок: контракт `swap_if_less` (compare-exchange + перестановка); `sort9_optimal`/`sort13_optimal` — безопасность и перестановка через `stub_verified(swap_if_less)`, сортированность первых 9/13 на ширине u8 (принцип 0–1, раскрыть как редукцию); контракт `bidirectional_merge` с loop contract; затем `small_sort_network` и `small_sort_general_with_scratch` на символьной len ≤32 со `stub_verified` всех callee | Kani `9461e07a`, `run-kani.sh` с флагами CI; типы `u8`, `i32`, `u64`, `[u8;85]` | Каждый harness ≤10 мин на 4 ядрах / 16 ГБ, `cover` достижимы | Контракт `bidirectional_merge` не доказывается или верхний harness >10 мин и со stub → Kani-план минимум не закрывает. Откат: подать как «Towards #56» с B1 до 18 и вернуться к выбору (ESBMC как решатель; VeriFast после upstream) | 2–3 прогона |
| **K-2** | Loop contracts на `insertion_sort_shift_left` + `insert_tail` для **символьной неограниченной** длины, comparator `kani::any()` | тот же пин; `#[cfg_attr(kani, kani::loop_invariant(..))]` в исходнике (прецедент #637) | Нет `kani::unwind` и констант длины; `cover` достижимы | `loop_modifies` не выражает raw-pointer-гэп (как в #703) → B4 закрывается до len 20 (реальные call site), раскрыть | 1–2 |
| **K-3** | `-Z uninit-checks` на `small_sort_general_with_scratch` и `small_sort_network` (scratch `MaybeUninit<[T;N]>` → `*mut T`), len 4–8 | тот же пин | Чтения scratch проверяются без «unsupported» | «unsupported check» → E1-uninit вне области с раскрытием; запросить решение в рамках #733 или закрыть точечным VeriFast (V-1) | 1 |
| **K-4** | `#[kani::should_panic]` с произвольным comparator в `small_sort_general_with_scratch` (len ≥2) и `sort8_stable`; парный harness со строгим порядком без паники | тот же пин | SUCCESS: только паники; парный — без паники, sorted + perm | Отказы, не связанные с паникой → это реальная находка (UB до паники): зафиксировать и сообщить | 1 |
| **K-5** | `#[safety::ensures]` на трёх `small_sort` impl на текущем пине | тот же пин | Компилируется | E0520/E0599 воспроизводятся → F3 (контракты на внутренних функциях + проверки в harness), раскрыть | <1 |
| **V-1** (необязательный) | Stock VeriFast 26.10 на `insert_tail` + `insertion_sort_shift_left` без патчей форка | `VFVERSION=26.10` | Проходит → VeriFast может закрыть B4/E1-uninit для этих функций как дополнение | Падает на `ManuallyDrop::new` (ожидаемо без PR 1046) → дополнение невозможно до upstream | 1 |

## 6. Что делать с уже сделанным

| Актив | Судьба |
|---|---|
| Kani-харнессы на i32 (вспомогательные) | Переносятся основой, расширяются на набор C3 |
| R7 в VeriFast (75%) | Под минимум не нужен: в Kani это несколько инстанциаций. Оставить как слой К (обобщённый `T`) |
| Математика сетей N9/N13 в VeriFast | Аргументация переносится в обоснование редукции 0–1 для K-1 |
| Патчи форка (5–7 тыс. строк), overlays Select | Заморозить. Апстримить только то, что нужно для V-1 и для слоя К: PR 1046, спека `select_unpredictable`, спека `[T]::as_mut_ptr` |
| Методические гейты (nonvacuity, ledger, evidence index) | Переносятся без изменений — это и есть ось конкуренции (G1–G3) |
| RefinedRust G1 (N6) | Вне минимума; довести только диагностический прогон, если он уже запущен |

## 7. Решения, нужные от владельца

1. Принять Kani как основной путь минимума при условии K-1. Если K-1 провалится, вернуться к этому выбору.
2. Разрешить внесение `loop_invariant`/контрактов как атрибутов `cfg_attr(kani, …)` в `smallsort.rs` (K-2, K-1). Runtime они не меняют; прецеденты #637 и #600.
3. Решить, задавать ли организаторам вопросы из `REQUIREMENTS-INTERPRETATION` §6 до или после K-1. Отправка требует отдельного поручения.

---

Ниже — приложения из редакции 1. Факты в них не изменились. Колонки К2 и К3 больше не дисквалифицирующие: см. §2–3.

## Приложение A. Скрининг 18 кандидатов по критериям ред. 1 (К1, К2, К3, К7)

Критерии: **К1** — generic unsafe Rust без переписывания исходника std; **К2** — семантика panic/unwind с верифицированным Drop-guard на unwind; **К3** — универсальные `T` (non-Copy, ZST) и stateful `FnMut`; **К7** — допустимость (интегрирован / реалистичный путь Tool Application). Сноски — в списке после таблицы.

| Кандидат | Пин (commit/tag, rustc) | Последний коммит / релиз | Сопровождение | К1 | К2 | К3 | К7 |
|---|---|---|---|---|---|---|---|
| **Flux** | main `1b04d5e6` (nightly-2026-10-22); CI-пин vrs `6769bb9c` (2026-10-13) | 2026-10-23 / релизов нет | активно (180 коммитов/6 мес) [Fl1] | частично [Fl2] | нет [Fl3] | частично [Fl4] | да [Fl5] |
| **Creusot** | master `7896a3f1` (nightly-2026-08-03); v0.14.0 | 2026-10-23 / 2026-10-12 | активно (622/6 мес) [Cr1] | нет [Cr2] | нет [Cr3] | да [Cr4] | нет (ожидание) [Cr5] |
| **Prusti** | prusti/prusti main `22804f71` (nightly-2026-08-15) | 2026-10-23 / ежедневные теги | активно (200/6 мес), переезд 2026-10-19 [Pr1] | нет [Pr2] | нет [Pr3] | частично/неизвестно [Pr4] | нет [Pr5] |
| **Verus** | main `32dede6e` (stable 1.99.1); ветка verify-rustlib `ef6b2b75` (1.95.0) | 2026-10-23 / rolling | активно (200+/6 мес) [Ve1] | нет [Ve2] | частично [Ve3] | частично [Ve4] | нет (ожидание) [Ve5] |
| **Aeneas + Charon** (Lean/F*/Rocq/HOL4) | aeneas `74aabd52`, charon `e550d706` 0.1.296 (nightly-2026-09-17) | 2026-10-23 / nightly-2026.10.23 | активно, ежедневные теги [Ae1] | нет [Ae2] | нет [Ae3] | частично [Ae4] | нет [Ae5] |
| **hax** | `721d1a27` (nightly-2025-11-08); v0.4.2 | 2026-10-22 / 2026-10-01 | активно, ежемесячные релизы [Hx1] | нет [Hx2] | нет [Hx3] | частично [Hx4] | нет [Hx5] |
| **Gillian-Rust** | `83d739e8` (nightly-2024-05-10) | 2025-05-21 / тег `before-type-proofs` | **не сопровождается** 17 мес [Gi1] | частично [Gi2] | нет [Gi3] | нет [Gi4] | нет [Gi5] |
| **RefinedRust** | апстрим `332d945f` (недоступен); форк Hinata-Mikami `e675088d` (nightly-2026-02-28) | апстрим неизвестно; статья OOPSLA'26 окт 2026 | активно (по статье); код после 2026-03-01 не прочитан [RR1] | частично [RR2] | нет [RR3] | да/частично [RR4] | нет [RR5] |
| **Kani (+CBMC)** | kani-0.68.0 `0d2328a9`; vrs-пин `9461e07a` (nightly-2026-10-12); CBMC 6.11.0 | 2026-10-23 / 2026-09-15 | активно (231/6 мес) [Ka1] | да [Ka2] | нет [Ka3] | частично [Ka4] | да [Ka6] |
| **ESBMC** (GOTO от Kani) | v8.6 `5836d7c4`; CI-пин v8.5 `6411c933` | 2026-10-23 / 2026-10-14 | активно [Es1] | да (те же харнессы) [Es2] | нет (наследует) [Es2] | нет (наследует) [Es2] | да [Es1] |
| **KMIR** | `4d793252` = v0.4.226 (nightly-2024-11-29) | 2026-06-25 / 2026-06-25 | **без коммитов с июня 2026** [KM1] | частично [KM1] | нет [KM2] | нет [KM3] | да (CI только Ch11) [KM5] |
| **RAPx** | HEAD `5ef09468`; v0.7.60; CI-пин 0.7.56 (nightly-2026-09-25) | 2026-10-24 / 2026-10 | очень активно (300/2 мес) [RA1] | частично [RA2] | нет [RA3] | частично [RA4] | да [RA5] |
| **VeriFast upstream** (26.10/master, без патчей форка) | master `0a83dba4`; 26.10 `f76012fb` (nightly-2026-09-25); CI `VFVERSION=26.10` | 2026-10-09 / 2026-10-04 | один мейнтейнер; 26 коммитов/6 мес, пауза фев–авг [VF1] | частично [VF3] | нет (на практике) [VF4] | частично/нет [VF5] | да [VF9] |
| **Iris/Rocq через MIR/THIR** (Corten, coq-of-rust) | Corten — репозитория нет; coq-of-rust `43df3f25` (nightly-2025-12-07) | 2026-09-03 (arXiv) / 2026-10-23 | прототип / активно, но не Iris [Ir1][Ir2] | неизвестно / нет [Ir1][Ir2] | нет [Ir1] | частично [Ir1] | нет [Ir1] |
| **Soteria-Rust** (2025–26) | opam 0.2.3; репозиторий недоступен | неизвестно / 2026 | «in heavy development» [So1] | частично [So1] | неизвестно [So1] | нет [So1] | нет [So1] |
| **crux-mir / crucible-mir** (2025–26) | crux-v0.12 `…`; mir-json nightly-2026-03-21 | 2026-10-20 / 2026-01-29 | активно [Cx1] | частично [Cx1] | неизвестно [Cx1] | нет [Cx1] | нет [Cx1] |
| **Miri** (+Tree Borrows) | upstream rust-lang | 2025-12 (GenMC sync) / — | активно [Mi1] | да (интерпретация) [Mi1] | конкретное исполнение, не проверка [Mi1] | нет [Mi1] | нет [Mi1] |
| **BifRust / Brush_rs** (2025–26) | codeberg, Charon v0.1.160 | 2026-10-15 / — | прототип, вклад закрыт [Bf1] | неизвестно [Bf1] | неизвестно [Bf1] | нет (вероятно) [Bf1] | нет [Bf1] |

### Сноски к таблице (основание для каждой клетки)

**Flux.** [Fl1] исходник: https://github.com/flux-rs/flux (main `1b04d5e6f8247766cfb0f9c6040c2944eb9c87c4`, `rust-toolchain.toml` nightly-2026-10-22; один тег `wick-eval-base`); CI-пин `FLUX_VERSION` в https://github.com/model-checking/verify-rust-std/blob/main/.github/workflows/flux.yml. [Fl2] исходник: спецификации `*mut[@p] T` и `ptr::read/write/copy` в `lib/flux-core/src/ptr/mod.rs`; `RawDerefMode::None` по умолчанию в `crates/flux-config/src/lib.rs` L507–513; док.: `doc/src/tools/flux.md` — отслеживает свойства указателей, но не значения за ними. [Fl3] исходник: `crates/flux-refineck/src/checker.rs` ~L620–727 — `Drop` даёт только `target`, `UnwindResume => bug!("TODO…")`, `Call`/`Assert` без unwind-преемника. [Fl4] исходник: `lib/flux-core/src/mem/mod.rs` — extern spec `MaybeUninit` только `impl<T: Copy>`; тесты `closure00.rs`, `closure02.rs`; док.: issue #362 (POPL'25 generic refinements). [Fl5] исходник: `doc/src/tools.md` на `c0bd09c3`; issue #362 закрыт 2025-07-16; whitelist `[package.metadata.flux] include` в `library/core/Cargo.toml` не содержит `slice/sort`. [Fl6] исходник: `#[flux::trusted]`/`ignore` в `global_env.rs` L814–901; ledger не найден.

**Creusot.** [Cr1] исходник: https://github.com/creusot-rs/creusot (master `7896a3f13e4c57e6b3f9a9d89aac14d746708728`; `rust-toolchain` nightly-2026-08-03; теги v0.14.0 2026-10-12). [Cr2] исходник: `creusot/src/translation/function.rs` L100 — разыменование raw pointer запрещено, требуется `Perm`; `creusot-std/src/std/slice.rs` L80–145 `as_mut_ptr_perm`; док.: `guide/src/erasure.md` — верификация требует изменения кода, `#[erasure]` сверяет копию. [Cr3] исходник: `creusot/src/translation/function/terminator.rs` L139–180 (`Drop`→`Goto`, `UnwindResume`→`unreachable!()`); `creusot/src/analysis/liveness_no_drop.rs` L19–27 (Drop не поддерживается); `creusot-std/src/std/panicking.rs` (`#[requires(false)]` на panic). [Cr4] исходник: `creusot-std/src/std/ops.rs` (`FnMutExt`, prophetic postcondition); док.: `guide/src/tutorial/gnome_sort.md` (полиморфный `T: Ord`), `guide/src/limitations.md` (ZST — слепое пятно). [Cr5] API: issue #493 открыт; 2026-09-15 — интеграция ок без Alt-Ergo; CI-PR не подан. [Cr6] исходник: `ManuallyDrop` в `creusot-std` отсутствует; `creusot-std/src/std/mem.rs` — `MaybeUninit` как `Option<T>` без массивов; https://github.com/Lysxia/creusot-rust-std @ `d8f3cb5e` — README: `MaybeUninit` TODO, `ptr::copy` `#[requires(false)]`.

**Prusti.** [Pr1] исходник: https://github.com/prusti/prusti (main `22804f71443daba55b409fb0f4829d007a0f5fa0`; nightly-2026-08-15; коммит `b4f9f32` 2026-10-19 о переезде). [Pr2] исходник: `prusti-tests/tests/verify/fail/unsupported/{rawptr,rawptr_deref,union,unsize}.rs` с ожидаемыми ошибками «not supported»; док.: `docs/dev-guide/src/config/flags.md` — `UNSAFE_CORE_PROOF` «very incomplete». [Pr3] исходник: `prusti-encoder/src/encoders/mir_impure.rs` ~L1817, ~L2402 — unwind-пути не поддерживаются, `exhale false`. [Pr4] док.: `docs/user-guide/src/verify/closure.md` — closures «NOT YET SUPPORTED». [Pr5] API: поиск `repo:model-checking/verify-rust-std prusti` — заявки нет.

**Verus.** [Ve1] исходник: https://github.com/verus-lang/verus (main `32dede6e7820d18680e86c077dfac6feb200e6b7`; `rust-toolchain.toml` 1.99.1; `git ls-remote` ветка `verify-rustlib` `ef6b2b75c10dcd658861f160ba1def88ebe25ac1`, 2026-07-27, 1.95.0). [Ve2] исходник: `source/rust_verify/src/rust_to_vir_expr.rs` ~L4647 — `unsupported_err!` на deref raw pointer; `source/vstd/raw_ptr.rs` L570–615 — `ptr_mut_read/write(ptr, Tracked(&mut perm))`; в vstd нет `copy_nonoverlapping`/`select_unpredictable`; док.: `source/docs/guide/src/reference-attributes.md` (код вне `verus!{}` — external), `features.md` (raw pointers «Partially supported»). [Ve3] исходник: `source/vir/src/well_formed.rs` ~L1724–1742 — impl `Drop` обязан быть `no_unwind`, без `requires`; док.: `reference-unwind-sig.md`, `features.md` («Panic-unwinding: Partially supported», «Drop: Not supported»). [Ve4] док.: `exec_closures.md`, `features.md` — closures без mutable captures. [Ve5] API: issue #554 — «This LGTM» 2026-05-11; 2026-10-21 — «nearly ready», raw-pointer support затянулась. [Ve6] исходник: `source/vstd/std_specs/manually_drop.rs` (spec `ManuallyDrop::new`), `std_specs/maybe_uninit.rs` (`MemContents`, без массивов/`as_mut_ptr`); док.: `reference-unions.md`.

**Aeneas + Charon.** [Ae1] исходник: https://github.com/AeneasVerif/aeneas (`74aabd52f77001cf9eaad51b4f4b867a7dc6b111`, `charon-pin` `260ba2c8`), https://github.com/AeneasVerif/charon (`e550d706b99a71ef7d1d6bdfae525874891f32af`, `Cargo.toml` 0.1.296, `rust-toolchain` nightly-2026-09-17). [Ae2] исходник: `src/interp/InterpPaths.ml` L196–197 (`craise` на deref raw pointer), `src/llbc/TypesAnalysis.ml` L541 (unions), `tests/src/raw_pointers.rs` `known-failure`, `backends/lean/Aeneas/Std/RawPtr.lean`; док.: README «Targeted Subset…» — только safe Rust. [Ae3] исходник: `src/interp/InterpStatements.ml` L786 (`UnwindResume` → craise), `src/Config.ml` `drop_as_no_op = true`; charon `charon/src/options.rs` L279–282 (`reconstruct_fallible_operations` теряет unwinding). [Ae4] исходник: `tests/src/closures.rs` — `call_fn_mut` закомментирован (`TODO: monomorphisation in Charon`); док.: `docs/user/src/README.md` — closures «ongoing work». [Ae5] исходник: `doc/src/tools.md`; единственное упоминание — Discussion #619.

**hax.** [Hx1] исходник: https://github.com/cryspen/hax (`721d1a2710b1d7020a0b32de7291fe791885d215`; `rust-toolchain.toml` nightly-2025-11-08; CHANGELOG 0.4.2 2026-10-01). [Hx2] исходник: `engine/backends/fstar/fstar_backend.ml` L2024, `lean_backend.ml` L97 — первая фаза `Phases.Reject.RawOrMutPointer`; `engine/lib/phases/phase_reject.ml` L64–82; `engine/lib/import_thir.ml` L1955 — unions не поддерживаются (#998); док.: `docs/manual/faq/trust.md` — hax «only targets safe Rust». [Hx3] исходник/док.: `docs/manual/fstar/tutorial/panic-freedom.md`, `docs/manual/lean/tutorial/panic-freedom.md`, `proof-libs/lean/Hax/MissingAeneas.lean` — модель «нет паники», слово unwind в `docs/manual` отсутствует. [Hx4] исходник: `tests/src/legacy/traits/lib.rs` L64, L124 (`F: FnMut` проходит, legacy-lean fail); док.: issue #420 (`&mut` aliasing). [Hx5] исходник: `doc/src/tools.md`; заявки нет.

**Gillian-Rust.** [Gi1] исходник: https://github.com/GillianPlatform/gillian-rust (`83d739e83034d71162fb66b569041cf301123df7`, 2025-05-21; `rust-toolchain.toml` nightly-2024-05-10); док.: README — «prototype… unstable». [Gi2] исходник: `tests/noproph/vec_std.rs` (raw pointers, `from_raw_parts_mut`), `gilogic/src/stubs.rs` L192–222 (`PointsToMaybeUninit`), `lib_rust_to_gil/src/global_env/genv.rs` L362 (`fatal!("Unions not handled yet")`). [Gi3] исходник: `lib_rust_to_gil/src/codegen/body.rs` L103–105 (cleanup-блоки не транслируются), `codegen/block.rs` L106–110 (`Drop` → goto с warning). [Gi4] исходник: `codegen/function_call.rs` L273 (closures не поддерживаются); док.: arXiv 2403.15122v2 — ZST исключены. [Gi5] исходник: `doc/src/tools.md`.

**RefinedRust.** [RR1] док.: https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev (недоступен: proxy 403/robots); исходник (форк): https://github.com/Hinata-Mikami/RefinedRust — последний апстрим-коммит `e675088d` (Gäher, 2026-03-01), `rr_frontend/rust-toolchain.toml` nightly-2026-02-28; `332d945f` в форке отсутствует; док.: https://iris-project.org/pdfs/2026-oopsla-refinedrust2.pdf (OOPSLA'26, DOI 10.1145/3839484). [RR2] исходник (форк): `rr_frontend/translation/src/types/translator.rs` L1603–1608 (slices не поддерживаются), L951–954 (union ADTs); док.: OOPSLA'26 — unsized types главная недостающая фича. [RR3] исходник (форк): `rr_frontend/translation/src/body/translation/terminator.rs` L288–294 (`UnwindResume`/`UnwindTerminate` → Unimplemented), `body/translation/mod.rs` L91–92 (unwinding пропускается). [RR4] исходник (форк): `case_studies/tests/src/closures.rs` L80, L364 (`FnMut`); док.: OOPSLA'26 (closures с ручными SL-спеками). [RR5] исходник: `doc/src/tools.md`; заявки нет.

**Kani.** [Ka1] исходник: https://github.com/model-checking/kani (тег `kani-0.68.0` = `0d2328a93f0e0ff66132d6bfa1a7d884877cf862`, 2026-09-15; main `cd355b0bccd32300713bc2ce4f765dafa1510607`; `kani-dependencies` CBMC 6.11.0, Kissat 4.0.1); vrs `tool_config/kani-version.toml` → `9461e07af7ec929f050aa4192f29363c9be07779`. [Ka2] док.: `doc/src/tools/kani.md`; исходник: 28 файлов `library/**` с `kani::proof`. [Ka3] док.: https://model-checking.github.io/kani/rust-feature-support.html#panic-strategies — unwinding не поддерживается (issue #692); исходник: `kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs` ~L655 (требует `-Cpanic=abort`), `kani_compiler.rs` ~L370 (флаг «soundness-critical»), `codegen/statement.rs` L460–502 (`Drop { unwind: _ }`, `Resume`/`Abort` unimplemented), ~L668 (TODO #221), `codegen/assert.rs` L214–243 (`assert(false); assume(false)`). [Ka4] док.: https://model-checking.github.io/kani/reference/experimental/autoharness.html#generic-functions (одна инстанциация — underapproximation); исходник: `kani_middle/transform/check_uninit/ty_layout.rs` ~L163; `library/kani/src/arbitrary.rs` L262–320 (`nondet_fn2_ref_ref` — чистые nondet-функции, не stateful). [Ka5] исходник: `kani_middle/transform/check_uninit/mod.rs` L318–323 (union-pointee — «unsupported check»), `tests/expected/uninit/fixme_unions.rs`; vrs `scripts/run-kani.sh` L87 — без `-Z uninit-checks`/`-Z valid-value-checks`. [Ka6] исходник: `doc/src/tools.md`; `.github/workflows/kani.yml`.

**ESBMC.** [Es1] исходник: https://github.com/esbmc/esbmc (теги v8.5 `6411c933…` 2026-08-29, v8.6 `5836d7c4…` 2026-10-14; master `75c8bbab7e845b380a9e0a0c7d286c2f3550df9b`); vrs `scripts/run-goto-transcoder.sh` (качает v8.5, `esbmc --binary … --function`), PR #710 (2026-10-04). [Es2] исходник: `esbmc/src/` — фронтенды clang-c/cpp, jimple, python, solidity, ld; Rust-фронтенда нет; док.: `docs/roadmap/cprover-support-roadmap.md` — цель = тот же вердикт, что у CBMC. [Es3] док.: та же roadmap — свод 2026-08-26: 1110/1113 совпадений, 76 крэшей, 155 таймаутов; `slice` — 32 крэша («rvalue reference to array»).

**KMIR.** [KM1] исходник: https://github.com/runtimeverification/mir-semantics (master `4d793252bcd77091ee759ca6cd1629db41ed5496` = v0.4.226, 2026-06-25; `rust-toolchain.toml` nightly-2024-11-29; `package/version`); vrs `.github/workflows/kmir.yml` (Docker `ubuntu-jammy-0.4.226`). [KM2] док.: `docs/feature-checklist.md` (2026-06-18) — Drop no-op, unwinding не поддерживается; исходник: `kmir/src/kmir/kdist/mir-semantics/kmir.md` ~L693–700 (`termDrop` → `#execBlockIdx(TARGET)`). [KM3] док.: checklist — type parameters «monomorphized before MIR». [KM4] исходник: `rt/data.md` ~L1853 — нельзя построить неинициализированное `Value`. [KM5] исходник: `doc/src/tools.md`; CI запускает только `kmir-proofs/0011-floats-ints`.

**RAPx.** [RA1] исходник: https://github.com/Artisan-Lab/RAPx (HEAD `5ef09468569ffeab2d77461d8f366711837583e0`, 2026-10-24; теги v0.7.57/58/60; `Cargo.toml` 0.7.61; `rust-toolchain.toml` = floating `nightly`); vrs `.github/workflows/rapx.yml` (`RAPX_VERSION 0.7.56`, `TOOLCHAIN nightly-2026-09-25`, `--module slice --mode targeted`). [RA2] док.: `doc/src/tools/rapx.md` (атрибуты `rapx::verify/requires`, теги); исходник: 38 целей в `library/core/src/slice/mod.rs`. [RA3] исходник: `rapx/src/verify/vm/rules/terminator.rs` L102–116 (`exec_drop` → `facts.dead = true`, деструктор не исполняется), `verify/vm/call.rs` ~L475–490 (в worklist только `target`). [RA4] исходник: `verify/vm/memory.rs` L283–303 (символьный `sizeof_T >= 0`), `verify/vm/call.rs` ~L356–390 (`IS_ZST` для generic `T` сворачивается в `false`); модель вызова `FnMut`-аргумента не найдена (неизвестно). [RA5] исходник: `doc/src/tools.md`.

**VeriFast upstream.** [VF1] исходник: https://github.com/verifast/verifast (master `0a83dba42db7ce0b445034ece5298afe980e57dc`, 2026-10-09; тег 26.10 = `f76012fb518703b1d98e243ac4f487f16877cfcb`, 2026-10-04; `rust-toolchain.toml` nightly-2026-09-25; 26 коммитов за 6 мес, по месяцам 2026-02:2, 03:2, 04:0, 05:1, 06:0, 07:0, 08:0, 09:11, 10:14). [VF2] исходник: https://github.com/verifast/verifast/pull/1046 — open, 3 коммита, head `ac6a63d5cad3a028e5d6f7ee4439169ba443468b` (2026-10-20), «No reviews», `git merge-base --is-ancestor` → нет. [VF3] док.: `verifast-proofs/README.md` — верифицируется копия `verified/`, сверка `refinement-checker` + `diff original/ library/`; исходник: `src/refinement_checker/refinement_checker.ml` L248–285 `failwith "TODO"` для Alias/Dynamic/Coroutine. [VF4] исходник: commit `3971ac32` (#664, 2025-01-16) — unwind-пути без ghost-команд «excludes most programs»; `vf_mir_translator.ml` L3659 (`-ignore_unwind_paths` отбрасывает cleanup-блоки), L2916–2960 (Drop-терминатор без unwind-ребра; `unwind_action_get` только для Call/Assert); `verifast-proofs/alloc/*/verify.sh` — все с `-ignore_unwind_paths -allow_assume -skip_specless_fns`. [VF5] исходник: `tests/rust/safe_abstraction/tparam_own.rs` (`<T>.own`, `ptr::read/write` на `&mut T`), перевод `IS_ZST` (translator L2220), `raw_vec` ZST через `logical_capacity`; commit `33a249c5` (#1007, 2026-09-14) + `src/verify_expr.ml:2879` — вызовы с closure в generic-аргументах → `assert_false`; `bin/rust/std/lib.rsspec` L44–50 — generic контракт `FnMut::call_mut` с `on_unwind_ens`. [VF6] исходник: translator L208/3180/5277/5772/6307 — `Union` → `failwith "Todo"`; `lib.rsspec` L429–495 — `MaybeUninit` как opaque-структура с леммами `open/close_MaybeUninit`, `Array__MaybeUninit_to_Array_MaybeUninit`, spec `write`; `tests/rust/safe_abstraction/btree_node.rs` — `[MaybeUninit<K>; CAPACITY]` с 47 `assume`. [VF7] исходник: `hint::select_unpredictable` отсутствует в `bin/rust/*.rsspec` и трансляторе; `[T]::as_mut_ptr` в prelude не найден; exporter `vf_mir_exporter/src/lib.rs` L824/829 `todo!()` для `BoundRegionKind::Anon`/`ClosureEnv`, L306 — подстановка `'static` «in general unsound». [VF8] исходник: https://github.com/Tiramisu-Cake/verifast — `merge/actual-glue-instance-20261011` +60 коммитов, 5083 вставок (translator +3186); `merge/r23-source-borrow-adapter-20261024` +85, 7100 вставок (translator +4743, exporter +1040, capnp +138); `master` форка = апстрим master. [VF9] исходник: `doc/src/tools.md`; `.github/workflows/verifast.yml`; `verifast-proofs/setup-verifast-home` на `c0bd09c3` — `VFVERSION=26.10` с attestation-хэшем, `RUST_VERSION=nightly-2026-09-25`.

**Iris/Rocq через MIR/THIR.** [Ir1] док.: Corten — arXiv 2609.04372 (2026-09-03; THIR через hax/`hax2rocq`, Iris; «simple generics»; деструкторы с нетривиальным Drop — future work; репозитория/URL артефакта нет). [Ir2] исходник: https://github.com/formal-land/coq-of-rust (`43df3f2524e07ea31c30b0c9724915afbaca4c94`, `rust-toolchain` nightly-2025-12-07); док.: README — монадическое shallow-вложение THIR, не Iris, unsafe/raw pointers не упоминаются. [Ir3] исходник: VeriFast `-emit_rocq` `bin/rust/rocq/VfMir.v` — только Assign/StorageLive/StorageDead/Nop и Goto/SwitchInt/Return/Unreachable/Call; док.: arXiv 2601.13727 — loops, structs, generics, unwinding — future work. Пайплайн «RefinedRust» = строка RefinedRust выше.

**Новые инструменты 2025–2026.** [So1] док.: arXiv 2511.08729v4 (Soteria-Rust: Tree Borrows, strict provenance, «monomorphic for now», bug finder, Kani-харнессы через `cargo soteria --kani`; closures/panics не обсуждаются); https://ocaml.org/p/soteria/0.2.3/doc/README.html; GitHub-репозиторий недоступен из сессии. [Cx1] API/док.: https://api.github.com/repos/GaloisInc/crucible/releases (crux-v0.12 2026-01-29), mir-json README (nightly-2026-03-21), `crux-mir/CHANGELOG.md` 0.11 — «pointer safety attributes aren't tracked»; README — bounded symbolic tests. [Mi1] док.: https://raw.githubusercontent.com/rust-lang/miri/master/README.md (`-Zmiri-tree-borrows` опционально, «cannot ensure… sound»); POPL 2026 «Miri: Practical UB Detection». [Bf1] док.: https://codeberg.org/firefighterduck/Brush_rs (BifRust, biabduction над Charon; `--monomorphize-upfront` 2026-10-15; «Contributions are currently not accepted»).

## Приложение B. Blockers B1–B7 по кандидатам

B1 — `ManuallyDrop::new` в generic-коде; B2 — `MaybeUninit<[T; N]>` (union) с частичной инициализацией scratch; B3 — владение raw-указателем без pointee, `select_unpredictable`, leak-check; B4 — `&mut [T]` → `as_mut_ptr`, unsize, стирание регионов; B5 — паникующий `FnMut` в `insert_tail` + `CopyOnDrop::drop` на unwind; B6 — non-Copy `T`, ZST, выравнивание/provenance; B7 — гейты вакуумности/dead-code, ghost-strip = исходные байты, ledger допущений.

| Кандидат | B1 | B2 | B3 | B4 | B5 | B6 | B7 |
|---|---|---|---|---|---|---|---|
| Flux | нет спеки [Fl6] | bool-refinement, только `T: Copy` [Fl4] | только spatial `(base,addr,size)`, нет значений; `select_unpredictable` нет [Fl2] | для slice размер/выравнивание сбрасываются; temporal safety вне области [Fl2] | не моделируется [Fl3] | ZST-исключение в `valid()`; `MaybeUninit` требует Copy [Fl4] | `trusted`/`ignore`, ledger не найден [Fl6] |
| Creusot | нет спеки [Cr6] | `Option<T>`-view, без массивов; в порте std TODO [Cr6] | ghost `Perm`-токены (переписывание); `select_unpredictable` специфицирован [Cr6] | только `as_mut_ptr_perm` + `#[erasure]` [Cr2] | panic = `requires(false)`; Drop не поддерживается [Cr3] | layout-факты есть; ZST — слепое пятно; `ptr::copy` `requires(false)` [Cr4][Cr6] | `#[trusted]` обходит и erasure; синтаксическая сверка; vacuity нет [Cr2] |
| Prusti | блок фронтенда [Pr2] | union отвергается [Pr2] | raw ptr отвергается [Pr2] | отвергается [Pr2] | unwind отвергается [Pr3] | — (moot) | `#[trusted]`; ledger неизвестно |
| Verus | spec есть [Ve6] | `MemContents`, без массивов/`as_mut_ptr`; unions нативно [Ve6] | `PointsTo` tracked-токены (переписывание); `select_unpredictable` нет [Ve2] | `[T]::as_mut_ptr` spec не найден; ветки `-borrows/-sliceindex` в работе (неизвестно) [Ve2] | `Drop` обязан быть `no_unwind`; unwind — только сигнатура [Ve3] | `vstd::layout` + `PointsTo`; ZST неизвестно [Ve6] | `external_body`/`assume_specification`; ledger не найден [Ve2] |
| Aeneas+Charon | нет модели [Ae2] | Charon транслирует unions, Aeneas отвергает [Ae2] | `TRawPtr` opaque, deref отвергается [Ae2] | unsize ок, дальше B3 [Ae2] | `UnwindResume` → craise; drop no-op [Ae3] | функциональная модель без адресов; ZST неизвестно | Lean `sorry`-free проверяем; Charon «known unsoundnesses» #583 (док.) |
| hax | нет модели [Hx3] | union #998 [Hx2] | `Reject.RawOrMutPointer` [Hx2] | отвергается (B3) + #420 [Hx4] | нет unwind-модели; Drop неизвестно [Hx3] | нет памяти/ZST неизвестно | `-i` может молча исключать код (док. `trust.md`) |
| Gillian-Rust | неизвестно (нет тестов) [Gi2] | union `fatal!`; но `PointsToMaybeUninit` есть [Gi2] | raw ptr + uninit points-to есть; `select_unpredictable` нужен shim [Gi2] | `as_mut_ptr`/`from_raw_parts_mut` в `vec_std.rs` [Gi2] | cleanup пропущен, Drop = goto, closures нет [Gi3][Gi4] | `Ownable`; ZST исключены [Gi4] | леммы «trusted and unproven» (док. arXiv) |
| RefinedRust | shim не найден (неизвестно) [RR2] | union ADT блок [RR2] | raw ptr да (Vec/ACE); `select_unpredictable` неизвестно [RR4] | slices не поддерживаются — сигнатура `&mut [T]` не транслируется [RR2] | `UnwindResume` Unimplemented [RR3] | refinement-типы; ZST неизвестно (`lang.v` L361 исключает) | Rocq проверяет всё; TCB = фронтенд + Radium (док.) |
| Kani | не блок (мономорф.) [Ka4] | `-Z uninit-checks` «unsupported» для union-pointee; флаг не включён в CI [Ka5] | fallback-body интринсика; `DropOnPanic` в `hint.rs` не исполняется [Ka3] | slices «Yes», coercions «Partial» (док.) | **блок**: cleanup-ребро отброшено, panic = `assert(false)` [Ka3] | по инстанциациям; nondet-closure без состояния [Ka4]; док. противоречит себе по misaligned deref | `UNREACHABLE`/`kani::cover`/`--coverage`; ledger `assume` нет (док.) |
| ESBMC | как Kani | как Kani | как Kani | крэши «rvalue reference to array» на slice-харнессах [Es3] | как Kani [Es2] | как Kani | стоп на первом сбое, нужен `--multi-property` (док.) |
| KMIR | только внутри `MaybeUninit`-transmute `IntoIter` [KM4] | нельзя представить uninit-значение [KM4] | raw ptr «partially», без адресной модели (док.) | fat-pointer metadata нет (док.) | **блок**: Drop no-op, unwinding нет [KM2] | адресной модели нет; `char` нет (док.) | `kmir show --leaves`; cover нет (док.) |
| RAPx | Drop = «dead»-пометка [RA3] | только тег `Init`, модели инициализации нет (неизвестно) | `select_unpredictable` неизвестно | теги `from_raw_parts`/`get_unchecked` есть (док.) | **блок**: cleanup не исполняется [RA3] | символьный `sizeof_T`, но ветка `IS_ZST` свёрнута [RA4] | `Proved/Unproved`, `--debug-contracts`; cover нет (док.) |
| VeriFast upstream | нет — фикс только в открытом PR 1046 [VF2] | opaque `MaybeUninit` + леммы; настоящие unions `failwith` [VF6] | specs `read/write/copy_nonoverlapping`; `select_unpredictable` нет [VF7] | `&mut [T]` (#1015/#1027) есть; `[T]::as_mut_ptr` нет; `todo!()` на регионах [VF7] | **блок**: closure-вызовы отвергаются; ghost на unwind нет; Drop без unwind-ребра [VF4][VF5] | `<T>.own`, ZST (RawVec), provenance в `ptr_offset_from`; известные unsoundness aliasing/variance (док.) [VF5] | `-allow_dead_code`, `-allow_assume`, refinement-checker (unwind-соответствие TODO); ledger нет [VF3] |
| Corten / coq-of-rust | неизвестно | неизвестно | неизвестно | неизвестно | Drop — future work [Ir1] | неизвестно | Rocq / аксиомы (док.) |
| Soteria-Rust | неизвестно | неизвестно | TB-теги, strict provenance [So1] | неизвестно | неизвестно | мономорфно [So1] | нет ledger (bug finder) |
| crux-mir | неизвестно | неизвестно | provenance не отслеживается [Cx1] | неизвестно | неизвестно | мономорфно | нет |
| Miri | исполняет | исполняет | provenance/TB (конкретно) [Mi1] | исполняет | реальный unwind, но одна трасса [Mi1] | конкретные типы | — |

## Приложение C. Вердикты ред. 1 по кандидатам (до пересмотра планки)

**Flux** — не подходит как основной путь; даже как UB-gate почти бесполезен для smallsort: нет значений за raw-указателями (sortedness/permutation через `ptr::copy` невыразимы), deref выключен по умолчанию, `UnwindResume` — `bug!`-TODO, `MaybeUninit` только для `T: Copy`. Единственный плюс — уже в CI.

**Creusot** — не подходит: каждый raw-deref требует ghost `Perm`-аргументов, т. е. верифицируется переписанная копия (`#[erasure]`), Drop не поддерживается, паника = обязательство недостижимости (ровно обратное B5); заявка #493 без CI-PR 13 месяцев. Сильная сторона (prophetic `FnMut`, полиморфный `T`) не компенсирует.

**Prusti** — не подходит: raw pointers, unions, unsize, unwind отвергаются фронтендом; closures не поддерживаются; заявки нет.

**Verus** — узкий кандидат «на будущее»: лучшие среди недопустимых модели для B1/B2/B3 (`ManuallyDrop` spec, `MemContents`, `PointsTo`, нативные unions, понятие unwind в сигнатурах), но код нужно завернуть в `verus!{}` и переписать `ptr::read/write` на `ptr_mut_read/write` с tracked-пермиссиями; `Drop` обязан быть `no_unwind` (нельзя доказать «восстановление на unwind»), `FnMut` с mutable captures не поддержан; интеграционный PR не подан (7,5 мес после «LGTM»).

**Aeneas (+Charon, Lean/F\*)** — не подходит: Charon уже несёт unsafe/unions/unwind, но Aeneas жёстко отвергает deref raw pointer, unions и unwinding, drops = no-op; закрытие smallsort требует переписать его в safe Rust, что запрещено правилами.

**hax** — не подходит: первая же фаза движка `Reject.RawOrMutPointer`; unions #998; документация прямо ограничивает safe Rust; Lean-бэкенд наследует ограничения Aeneas.

**Gillian-Rust** — не подходит: единственный среди «не-VeriFast» с моделью raw ptr + uninit points-to, проверенной на std `Vec`, но не сопровождается 17 месяцев, nightly-2024-05-10, cleanup-блоки пропущены, Drop = goto, closures и ZST нет.

**RefinedRust (и «Iris/Rocq через MIR» в целом)** — не подходит: сигнатура `v: &mut [T]` не транслируется (slices unsupported), unions блок, `UnwindResume` Unimplemented (снимок март 2026, OOPSLA'26 не сообщает об изменениях); апстрим-лог после `332d945f` не прочитан. Corten — прототип без репозитория, Drop — future work; coq-of-rust — не separation logic и не про unsafe.

**Kani (+CBMC)** — основной страховочный путь по планке комитета и единственный допустимый инструмент, достающий весь граф вызовов без переписывания; но критерий 2 закрыт структурно (`-Cpanic=abort`, cleanup-ребро отброшено, паника = `assert(false); assume(false)`), критерий 3 — только по инстанциациям и с nondet-компаратором без состояния; ограниченная верификация упирается в длину 32 (>20 мин, до 50 ГБ на `sort13_optimal`), uninit-категория на union-scratch не дискаржится.

**ESBMC** — не подходит как самостоятельный путь: второй SMT-бэкенд над тем же Kani-GOTO (та же мономорфизация, тот же abort), собственного Rust-фронтенда нет, на slice-харнессах корпуса — 32 крэша. Разве что как независимая перепроверка Kani-харнессов, что уже делает CI для `checked_unchecked.*`.

**KMIR** — не подходит: rustc nightly-2024-11-29 (23 месяца старше библиотеки), Drop no-op, unwinding нет, uninit-значения не представимы, коммитов нет с 2026-06-25.

**RAPx** — только UB-gate (допустим, в CI): тег-чекер валидности/выравнивания/in-bounds на не-паникующих путях; деструктор не исполняется, cleanup не обходится, `IS_ZST`-ветка свёрнута, модель вызова `FnMut`-аргумента не найдена. Низкая ценность для smallsort; в фазу 2 не брать.

**VeriFast upstream (26.10/master без патчей)** — не подходит как замена форку: B1 (PR 1046 не влит), B2 (unions `failwith`, scratch только через opaque-леммы с `assume`), B3 (`select_unpredictable` без спеки), B5 (closure-вызовы отвергаются, ghost на unwind нет, Drop без unwind-ребра). Зато это единственный допустимый дедуктивный инструмент с `<T>.own`, и обе принятые VeriFast-решения показали, что комитет принимает `-ignore_unwind_paths -allow_assume -skip_specless_fns` с документированными caveats.

**Soteria-Rust / crux-mir / Miri (+TB)** — только UB-gate, недопустимы как инструмент решения; Miri и Soteria дают то, чего нет у Kani (aliasing/provenance по Tree Borrows), crux-mir слабее (provenance не отслеживается). **BifRust, Corten** — наблюдать, не применимы.

## Приложение D. Пробелы: что не удалось проверить и как проверить

| Пробел | Как проверить |
|---|---|
| Апстрим RefinedRust после `332d945f` (slices/unions/unwind), wiki, Radium-unwind | `git clone https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev.git && git log --oneline 332d945f..main`; `grep -rn ManuallyDrop stdlib/`; `grep -ri unwind theories/` (вне прокси); https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/wikis/home |
| Допустимость патченной сборки VeriFast в CI vrs | Спросить в https://github.com/model-checking/verify-rust-std/issues/56 и /issues/213; прочитать `verifast-proofs/setup-verifast-home` на `main` |
| Намерение btj по PR 1046 | https://github.com/verifast/verifast/pull/1046 (комментарии/ревью) |
| Верифицирует ли апстрим 26.10 generic-тело с `F: FnMut`-параметром (vs отказ только при closure в generic-args) | Минимальный `fn f<T, F: FnMut(&T,&T)->bool>(v: &mut [T], is_less: &mut F)` с `//@` спеками под `verifast 26.10`; см. `src/verify_expr.ml:2879` |
| Поведение Kani `-Z uninit-checks` на `scratch.as_mut_ptr() as *mut T` | Харнесс на 4 × i32 для `small_sort_general_with_scratch` с `-Z uninit-checks`, искать «unsupported» |
| Конфликт док. Kani по misaligned deref (feature table «No» vs soundness «checked») | Харнесс с deref `*const u32` по нечётному смещению |
| Статус issues Kani #692, #221, #3300, #1150 | Открыть https://github.com/model-checking/kani/issues/692 и др. |
| Ревью #694 и #701 | `https://api.github.com/repos/model-checking/verify-rust-std/pulls/694/reviews`, `/701/reviews` |
| Verus `verify-rustlib`: аннотационный режим без `verus!{}`, `std_specs/slice.rs`, ZST/align аксиомы | `git diff main..verify-rustlib -- source/rust_verify/src`; `source/vstd/std_specs/slice.rs`, `source/vstd/layout.rs` на ветке; спросить в #554 |
| Flux: принимает ли std-CI `RawDerefMode::Ok`; ledger trusted-элементов | grep `FLUXFLAGS`/`allow_raw_deref` в `library/core/Cargo.toml`, `flux.yml`; `flux-config` |
| Creusot: примет ли комитет `#[erasure]`-копии | Спросить в #493 / #56 |
| RAPx: модель вызова `FnMut`-аргумента; `Init` на union-scratch; версия, на которой наблюдался «ZST detector» | `cargo rapx verify --mode targeted --debug-contracts` на `insertion_sort_shift_left` на 0.7.56 и HEAD; https://safer-rust.github.io/RAPx-Book/8.4-pipeline.html |
| ESBMC на smallsort-харнессе; эффект `--k-induction` | `run-kani.sh --kani-args --keep-temps --only-codegen` → `esbmc --binary … --function …` |
| KMIR: ветки с новым rustc-пином | `git ls-remote --heads` (120 веток), `rust-toolchain.toml` в них |
| hax: принимается ли generic `&mut F` с `F: FnMut`; трактовка Drop | `cargo hax into fstar` на минимальной функции; извлечь struct с `impl Drop` |
| Aeneas: ZST; charon#280 состояние | `rg "size_of::<T>\(\) == 0" tests/src`; `gh issue view 280 -R AeneasVerif/charon` |
| Gillian-Rust: Zenodo-артефакт 15231378, DOI 10.1145/3729289 | https://zenodo.org/records/15231378 |
| Soteria-Rust: последний коммит, rustc-пин, поведение на smallsort | `https://api.github.com/repos/soteria-tools/soteria/commits?per_page=1`; `cargo soteria --kani` на fork @ nightly-2026-10-12 |
| Corten: артефакт/репозиторий; §3.3 (raw ptr/MaybeUninit) | PDF arXiv 2609.04372 (раздел Data availability) |
| crux-mir: unwind/Drop; собственный `rust-toolchain` | `#[crux::test]` с паникующим `FnMut` + Drop-guard; mir-json README |
| Даты approval-комментариев #108/#362/#296/#444; инлайн-треды #238 | `https://api.github.com/repos/model-checking/verify-rust-std/issues/<n>/comments`; `/pulls/238/comments` |
| Лимит времени job в CI vrs; память macOS-раннеров; per-harness timeout в `run-kani.sh` | Полная функция `run_verification_subset` в `scripts/run-kani.sh` на `main` |
| Содержание arXiv 2510.01072 о VeriFast | https://arxiv.org/pdf/2510.01072 |
| Патчи overlay форка (24 заявленных) | Каталог доказательств в `Tiramisu-Cake/verify-rust-std` |

## Приложение E. Источники (доступ 2026-10-23/24)

Цель и правила: https://github.com/model-checking/verify-rust-std — `main` `c0bd09c354a50bf9fe4dcc7cc5f9c34503658479` (2026-10-22), пин `cd371e035c7e573760c43bf934d53e8118ee3e7d` (2026-10-05): `doc/src/general-rules.md`, `doc/src/tools.md`, `doc/src/tool_template.md`, `doc/src/challenges/0008-smallsort.md`, `doc/src/tools/{verifast,flux,kmir,rapx,goto-transcoder,kani}.md`, `README.md`, `.github/pull_requests.toml`, `.github/workflows/{kani,verifast,verifast-negative,flux,kmir,rapx,goto-transcoder,pr_approval}.yml`, `scripts/run-kani.sh`, `scripts/run-goto-transcoder.sh`, `tool_config/kani-version.toml`, `rust-toolchain.toml`, `verifast-proofs/README.md`, `verifast-proofs/alloc/{collections/linked_list.rs,raw_vec/mod.rs}/{verify.sh,README.md}`, `verifast-proofs/setup-verifast-home`, `library/contracts/safety/src/lib.rs`, `library/core/Cargo.toml`, `library/core/src/slice/sort/shared/smallsort.rs`, `library/core/src/hint.rs`, `library/core/src/intrinsics/mod.rs`; коммиты `1231f86`, `f66ba41`, `a914785`, `4070e2f`, `ffda6a8`, `955577c`. Issues/PR (API + страницы): #56, #108, #213, #234, #236, #238, #239, #296, #310, #362, #403, #422, #444, #455, #491, #493, #554, #576, #631, #637, #640, #678, #694, #701, #710, #723, #727, #732; Discussion #619; `api.github.com/search/issues?q=repo:model-checking/verify-rust-std+smallsort`, `…issues?labels=Tool Application&state=all`.

Инструменты: flux-rs/flux `1b04d5e6f8247766cfb0f9c6040c2944eb9c87c4`; creusot-rs/creusot `7896a3f13e4c57e6b3f9a9d89aac14d746708728`, Lysxia/creusot-rust-std `d8f3cb5eff327409d3391b7fe6efa1ce7c3d2311`; prusti/prusti `22804f71443daba55b409fb0f4829d007a0f5fa0`; verus-lang/verus `32dede6e7820d18680e86c077dfac6feb200e6b7` (ветка verify-rustlib `ef6b2b75c10dcd658861f160ba1def88ebe25ac1`); AeneasVerif/aeneas `74aabd52f77001cf9eaad51b4f4b867a7dc6b111`, AeneasVerif/charon `e550d706b99a71ef7d1d6bdfae525874891f32af`, AeneasVerif/mechanized-llbc `afc4862b8ab9efb7c0d1e4e685c393fed331f778`; cryspen/hax `721d1a2710b1d7020a0b32de7291fe791885d215`; GillianPlatform/gillian-rust `83d739e83034d71162fb66b569041cf301123df7`, GillianPlatform/Gillian `469aa5c1`; Hinata-Mikami/RefinedRust `e675088d` (апстрим-срез) / `ce336481`; model-checking/kani `0d2328a93f0e0ff66132d6bfa1a7d884877cf862` (0.68.0), main `cd355b0bccd32300713bc2ce4f765dafa1510607`; esbmc/esbmc v8.5 `6411c933…`, v8.6 `5836d7c4…`, master `75c8bbab7e845b380a9e0a0c7d286c2f3550df9b`; runtimeverification/mir-semantics `4d793252bcd77091ee759ca6cd1629db41ed5496` (v0.4.226); Artisan-Lab/RAPx `5ef09468569ffeab2d77461d8f366711837583e0`; verifast/verifast master `0a83dba42db7ce0b445034ece5298afe980e57dc`, тег 26.10 `f76012fb518703b1d98e243ac4f487f16877cfcb`, PR #1046 head `ac6a63d5cad3a028e5d6f7ee4439169ba443468b`, коммиты `3971ac32` (#664), `33a249c5` (#1007); Tiramisu-Cake/verifast ветки `merge/actual-glue-instance-20261011`, `merge/r23-source-borrow-adapter-20261024`; formal-land/coq-of-rust `43df3f2524e07ea31c30b0c9724915afbaca4c94`; GaloisInc/crucible (crux-v0.12), GaloisInc/mir-json `1d2f07d`; rust-lang/miri README (blob `66971d5f`); codeberg.org/firefighterduck/Brush_rs (2026-10-15); soteria 0.2.3 (ocaml.org).

Публикации/страницы: arXiv 2403.15122v2/v3 (Gillian-Rust, PLDI'25); https://iris-project.org/pdfs/2026-oopsla-refinedrust2.pdf (OOPSLA'26); arXiv 2601.13727 (Foundational VeriFast); arXiv 2603.28326 (Tas & Jacobs); arXiv 2609.04372 (Corten); arXiv 2511.08729v4 (Soteria-Rust); arXiv 2410.18280 (crux-mir); arXiv 2606.17374 (campaign paper, июнь 2026); arXiv 2510.01072; arXiv 2212.12976; POPL'26 Miri; https://aws.amazon.com/blogs/opensource/verify-the-safety-of-the-rust-standard-library/; https://rustconf2026.sched.com/event/2KI4j; ETAPS 2026 programme (RW2026); https://model-checking.github.io/kani/{soundness,rust-feature-support,undefined-behaviour,verification-results}.html и `reference/{attributes,arbitrary,experimental/autoharness,experimental/loop-contracts,experimental/stubbing,experimental/coverage}.html`.

Заблокированные источники в сессии: gitlab.mpi-sws.org и gitlab.rts.mpi-sws.org (RefinedRust, Simuliris), github.com/soteria-tools/soteria, zenodo.org (15231378, 10800313), doi.org, model-checking.github.io (mdBook; прочитано из git-дерева), safer-rust.github.io/RAPx-Book, aeneasverif.github.io/aeneas/user/features.html, прямой `curl`/`gh` к api.github.com (частично компенсировано WebFetch).
