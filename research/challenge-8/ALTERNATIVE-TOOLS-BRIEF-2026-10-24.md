# Challenge 8 (SmallSort): повторное исследование альтернативных и комбинированных инструментов верификации

Дата: 2026-10-24. Заказчик: владелец проекта. Исполнитель: отдельный research-агент вне VPS проекта.
Это постановка задачи и контекст. Документ не выдаёт полномочий менять инструменты, план или
proof-ветки; результат исследования ложится в решение владельца.

## 1. Что мы верифицируем

Challenge 8 из [model-checking/verify-rust-std](https://github.com/model-checking/verify-rust-std):
[условия](https://github.com/model-checking/verify-rust-std/blob/cd371e035c7e573760c43bf934d53e8118ee3e7d/doc/src/challenges/0008-smallsort.md),
[общие правила](https://github.com/model-checking/verify-rust-std/blob/cd371e035c7e573760c43bf934d53e8118ee3e7d/doc/src/general-rules.md),
[список интегрированных инструментов](https://github.com/model-checking/verify-rust-std/blob/cd371e035c7e573760c43bf934d53e8118ee3e7d/doc/src/tools.md).
Целевой файл: [library/core/src/slice/sort/shared/smallsort.rs](https://github.com/model-checking/verify-rust-std/blob/cd371e035c7e573760c43bf934d53e8118ee3e7d/library/core/src/slice/sort/shared/smallsort.rs)
на baseline `cd371e035c7e573760c43bf934d53e8118ee3e7d` (SmallSort blob `40939f922bcb6fdc7ee0d30427fa861827043827`).

Требуется:

- **Безопасность семи целей** (R1–R7): три trait entrypoints `small_sort` (Stable / Unstable / UnstableFreeze
  со специализациями), `swap_if_less`, `insertion_sort_shift_left`, `sort4_stable`, `has_efficient_in_place_swap`.
  Домен: произвольные допустимые длины, **любой** `T` (включая non-Copy, non-Freeze, ZST), **любой** comparator
  `F: FnMut(&T,&T)->bool` с состоянием и возможным panic; корректность на normal и unwind путях.
- **Три sorting-контракта** (F1–F3): отсортированность и сохранение вхождений для entrypoints при согласованном
  strict weak order. Stability — отдельное усиление, не обязательный минимум.
- **Четыре категории UB** должны проверяться автоматически на actual операциях: dangling/misaligned access,
  uninitialized read (в том числе `MaybeUninit` scratch), mutation of immutable bytes, invalid values.
- Автоматизированный запуск в CI, допустимый (интегрированный или одобренный через tool application)
  инструмент, runtime std без изменений. Подача принимается комитетом проекта.

Код использует: raw pointers и `ptr::read/copy/write`, `ManuallyDrop`, `MaybeUninit<[T; N]>` на стеке
(union ADT), `CopyOnDrop`-guard с восстановлением состояния при panic в comparator, `select_unpredictable`
(branchless выбор указателя), generic специализации через trait-dispatch, сети сравнений 9/13 и merge
произвольной длины с scratch-буфером. Полный инвентарь функций: строки 199–700 файла по ссылке выше.

## 2. Что сделано и чем мы платим

Основной инструмент сейчас — **VeriFast** (Rust-frontend через MIR exporter). Вспомогательно **Kani**
(bounded, i32 fixtures). Состояние на 23.10.2026 по внутреннему индексу готовности
(10 целей по 10%, ступени 0/25/50/75/100): **15%** — R4/R5/R6 по 25% (bounded фрагменты), R7 75%
(isolated generic теорема, перенесена на текущий baseline в stock VeriFast 26.09), остальные 0%.
Индекс не менялся с 11.10 при ~45 сессиях и ~30 Cloud-часах.

Главная проблема: **мы в основном дописываем верификатор, а не пишем доказательства.** VeriFast
Rust-frontend не покрывает нужные конструкции, поэтому:

- ветка Merge в форке VeriFast: +3193 строк в `vf_mir_translator.ml`, +1084 в `vf_mir_exporter`,
  +800 в refinement checker (~90 commits над upstream);
- Select накладывает 24 proof-time overlay-патча на translator/parser под конкретное MIR-тело
  (жёстко зашитые имена локалов и номера cleanup-блоков);
- каждый новый caller вскрывает новый tool-blocker.

Конкретные blockers, встреченные за октябрь (это и есть «тест на применимость» для любого кандидата):

| № | Конструкция / свойство | Что сломалось или потребовало патча |
| --- | --- | --- |
| B1 | `ManuallyDrop::new` в generic-коде | Identity successors в CFG translator'а; патч ушёл upstream (verifast PR 1046) |
| B2 | `MaybeUninit<[T; N]>` как union ADT, частично инициализированный scratch | Parser/inventory не принимал union kind; потребовались отдельные certificates |
| B3 | Raw pointer ownership без pointee (`*mut T` у `select_unpredictable`, `raw_ptr_own`) | Fractional/ghost-ресурсы, leak-check на constructor results, dead-code отказы после leak-check |
| B4 | `&mut [T]` → `as_mut_ptr` / unsize coercion, borrow lifecycle original caller | Exporter стирает region variables; попытка захвата owned NLL-фактов; сейчас «unsupported projection step» в exporter |
| B5 | `FnMut` comparator с panic внутри `insert_tail`, guard `CopyOnDrop::drop` на unwind | Late/first-panic recovery потребовала callback-recovery механики в translator |
| B6 | Generic `T` non-Copy, ZST, alignment/provenance | Historical Kani только i32; VF generic ownership требует ручных ресурсов |
| B7 | Dead-code/vacuity, source refinement (ghost-strip = original bytes), leak/resource closure | Нужны как gates; любой инструмент должен давать эквивалентные гарантии нетривиальности |
| B8 | Scale: fingerprint/evidence чтение, review-циклы, 1200 с на Build | Организационная цена; не критерий инструмента, но влияет на выбор |

## 3. Прежние оценки (не повторять, а обновить)

| Документ | Дата | Вывод |
| --- | --- | --- |
| `ALTERNATIVE-TOOLS-ASSESSMENT.md` (ветка `challenge-8/networks`) | 2026-10-06 | Из интегрированных: ESBMC (другой backend над Kani GOTO, не закрывает frontend gaps), Flux (unwind cleanup TODO), KMIR (нет unwinding/Drop), RAPx (кандидат на bounded applicability gate; позже NO-GO по ZST detector). VeriFast/Kani — основные |
| `refinedrust-feasibility/FEASIBILITY-REPORT.md` (ветка `research/refinedrust-feasibility-20261011`) | 2026-10-11 | RefinedRust (пин `332d945f`): логика покрывает generic ownership, Drop, unwind; frontend без slices и union ADT; CONDITIONAL для `insert_tail`, NO-GO для миграции; нет в списке tools → нужна tool application |
| Задание Network N6 (ветка `challenge-8/networks`, `network/rr/N6-OWNER-DIRECTIONS.md`) | 2026-10-24 | Запуск G1: один диагностический прогон unpatched RR на exact `insert_tail`; критерии GO_G2 / STOP_RR. Идёт параллельно с этим исследованием |

Ссылки на форк: `https://github.com/Tiramisu-Cake/verify-rust-std` (ветки выше). Если доступа нет,
запросить у владельца экспорт нужных файлов.

## 4. Критерии оценки кандидата

Жёсткие (несоответствие = инструмент не основной путь):

1. **Generic unsafe Rust без переписывания исходника**: raw pointers с provenance, `ManuallyDrop`,
   `MaybeUninit`/union, `ptr::copy` с alias-условиями, `&mut [T]`/slices, trait-специализации.
   Runtime std менять нельзя; допустимы только внешние/ghost аннотации.
2. **Panic/unwind семантика**: comparator может паниковать в любой точке; guard `Drop` на unwind должен быть
   реально проверен (не «continue to normal target»).
3. **Универсальный `T` и `F`**: не монофорфизация под i32; non-Copy, ZST, stateful callback.
4. **Автоматическая проверка четырёх категорий UB** на actual операциях (не только functional контракт).
5. **Soundness-гарантии и gates**: нетривиальность (no vacuity), отсутствие assumed summaries/axioms по умолчанию,
   видимый ledger доверия (trusted premises, shims, admits).
6. **Воспроизводимый автоматический запуск** в CI на Linux без ручных шагов; допустимое время на одну цель.
7. **Допустимость для challenge**: уже интегрирован или реалистичный путь tool application
   (что требуют правила, какие прецеденты есть).

Мягкие (влияют на ранжирование):

- Доля ручного proof-труда на одну цель (SMT-автоматизация против интерактивного Rocq/Lean/F*).
- Зрелость frontend на текущем nightly; частота обновлений; активность сопровождающих.
- Готовые спецификации std (`core::ptr`, `mem`, slices) в экосистеме инструмента.
- Возможность **комбинации**: например, bounded model checking (Kani/ESBMC) для F1–F3 в ограниченном
  домене + дедуктивный инструмент для safety; или один инструмент для чистой математики сетей (уже есть
  в VeriFast/stock) + другой для memory safety. Комбинация допустима, если домены и trust boundaries
  явно согласованы и комитет это примет.
- Стоимость нашего «долга»: что из сделанного (VeriFast overlays, Kani harnesses, математика N9/N13,
  R7) переносится, что теряется.

## 5. Что именно нужно исследовать

Кандидаты (минимум): Flux, Creusot, Prusti, Verus, Aeneas (+Lean/F*), hax (+F*/Coq/Lean),
Gillian-Rust, RefinedRust, Kani (+CBMC), ESBMC, KMIR, RAPx, VeriFast (upstream, без наших патчей),
Iris/Rocq напрямую через любой MIR-экспорт, а также любые инструменты 2025–2026, которых в этом
списке нет. Для каждого:

1. Точный пин (commit/tag, nightly), дата последнего релиза, статус сопровождения.
2. Таблица против критериев 1–7: по каждому пункту **факт из исходников/документации с ссылкой**,
   а не впечатление. Явно разделять «документация утверждает» и «подтверждено примером/исходником».
3. Проверка на blockers B1–B7 из §2: как инструмент моделирует каждую конструкцию; где заведомо
   потребуется патч frontend/semantics (это дисквалифицирующий признак для «основного пути», но может
   быть приемлемо для узкого вспомогательного).
4. Оценка ручного труда: есть ли опубликованные proofs похожего кода (сортировки, unsafe буферы,
   `ManuallyDrop`/`MaybeUninit`, callback с panic) — ссылки и размеры.
5. Путь к допустимости в challenge: интегрирован / tool application / не подходит.
6. Стоимость первого эксперимента: что нужно, чтобы за 1–2 Cloud-прогона получить фальсифицируемый
   ответ по `insert_tail` (как мы делаем с RefinedRust G1).

Комбинированные схемы: предложить 2–3 варианта разбиения (safety vs functional; математика vs память;
bounded vs generic) с явными trust boundaries и объяснением, как их принял бы reviewer проекта.

## 6. Формат результата

Один markdown-отчёт:

1. Резюме на 10–15 строк: рекомендация (оставить VeriFast / сменить / комбинировать), 3 главных риска.
2. Сравнительная таблица кандидатов по критериям 1–7 (+ мягким), с оценкой «да / частично / нет /
   неизвестно» и ссылкой на основание каждой клетки.
3. Разбор blockers B1–B7 по 2–3 лучшим кандидатам.
4. Предложение экспериментов: для каждого кандидата из топ-3 — минимальный фальсифицируемый опыт,
   входы, ожидаемый результат, критерий STOP, оценка затрат.
5. Список источников с датами доступа и exact commits.

Правила: не придумывать поддержку конструкций; при отсутствии данных писать «неизвестно» и чем проверить.
Не предлагать менять runtime std, ослаблять домен (cutoff длины, только Copy, без panic) или
«assume» summaries как способ пройти — такие варианты можно перечислить только как явно отвергаемые.
Срок и объём согласовать с владельцем; ориентир — 1–2 дня работы агента.

## 7. Контакты и артефакты для сверки

- План завершения и критерии закрытия целей: `research/challenge-8/COMPLETION-PLAN.md` (ветка
  `docs/evidence-brief-policy-20261017` форка).
- Разбор прогресса и решений: `research/challenge-8/PROGRESS-REVIEW.md`, §9 (там же).
- Исторические результаты и ограничения: `research/challenge-8/coverage.md` (ветка `challenge-8/networks`).
- Патчи VeriFast для оценки масштаба долга: форк `https://github.com/Tiramisu-Cake/verifast`, ветки
  `merge/actual-glue-instance-20261011`, `merge/r22-*`; overlays Select —
  `research/challenge-8/overnight-assume-actual/*.patch` на ветке `research/night-select-sort4-cloud-2026-10-09`.
