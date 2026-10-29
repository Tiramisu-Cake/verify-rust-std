# SCOPE: вариант B — предложенный состав, пригодность для CI не проверена

2026-10-29. Основа — библиотека `e96555151df91080fa0ccc106f60ee38a919c50e`; ветка подачи не менялась. Сборок, Kani, CBMC и внешних CI-запусков для выбранного SHA не было. Это решение о составе, не подтверждение CI-прохождения. Значения macOS — исторические оценки из TSV и вычислений; 4 C3a значения остаются UNKNOWN.

## Основания и правило выбора

П-6: исторические 8/8 ordinary partition jobs в Actions run `40748125754` относятся только к `6cfc76cb211d088aebaff8a449bcac953e97f942` (до C3a). Не переносить это свидетельство на весь `e9655515` или на новый SHA. Пакет `e9655515` даёт 328 исходных harness names; 4 C3a types/smoke имеют UNKNOWN macOS VT, включая изменённую smoke-модель. Источники и ограничения C3a сохранены в [evidence](c3a-evidence.json), [notes](c3a-notes.md) и [RESULT-C3A copy](RESULT-C3A-source.md).

Сначала сохраняются полезные свойства с соответствующими доказательствами контрактов того же домена, затем удаляются дорогие дубли. B добавляет к ядру A (116) девятнадцать general/stable merge callers (u64 N0..8, u8 N0..9) и девять matching exact merge contracts (u64 N5..8, u8 N5..9). Среди callers четыре простых N0/1 без вызова merge и пятнадцать нетривиальных callers с доказательствами того же type/N/comparator. В ordinary нет stub caller с matching T/N/comparator контрактом, оставшимся только в opt-in. Это не закрывает композицию между разными аллокациями: exact-N ↔ scratch48 и shifted tails остаются gaps; композиция имеет условный статус.

Неизменённые источники и evidence SHA для каждой гармоники, а также реальные domain edges отражены в [scope.tsv](scope.tsv). Исторические имена не доказывают новый SHA. `proof_for_contract` считается зависимостью только для соответствующего типа, длины, компаратора и региона.

## Решения по семействам

Количество — исходное → ordinary B; VT — сумма известных macOS секунд до → после. T600 цензурирован и не включён в VT; U4 — четыре неизвестных C3a времени. Полные основания по harness — в [scope.tsv](scope.tsv).

| Семейство | Остаётся / уходит; влияние на заявление | VT до → после, с |
|---|---|---:|
| correct fallback, 17→0 | u64 N8..16/u8 N9..16 остаются opt-in; fallback caller домены не ordinary | 1769,7→0 |
| correct scratch/general, 3→0 | u8 scratch48 и general/stable N14/15 вместе с соответствующими contracts opt-in | 462,8→0 |
| merge general callers, 29→19 | Ordinary: u64 N0..8, u8 N0..9; 15 нетривиальных callers имеют matching T/N proof, плюс N0/1 без вызова merge. Higher lengths opt-in | 1740,9→251,4 |
| merge exact contracts, 24→9 | Ordinary: u64 N5..8 и u8 N5..9; higher exact-N contracts opt-in | 3894,7 + T600→685,6 |
| real fallback, 9→7 | u8/u64 N0..6 остаются; combined N7 и u8 N8 opt-in | 369,5→50,2 |
| Drop, 14→13 | Counts до N16, tags до N8; tag-permutation general/stable N16 opt-in | 369,8→98,0 |
| three-route safety, 31→3 | Полные три-route доказательства только N2/8/16; остальные lengths opt-in | 3100,7→74,7 |
| shifted tail contracts, 15→0 | START1..15 для `[u64;17]` opt-in; не переносит доказательство на другие регионы/allocations | 3145,3 + T600→0 |
| network correctness, 27→13 | u8/u64 N0..7 и N9, плюс u8 N13; прочие lengths opt-in | 2943,7→181,5 |
| suffix permutation, 10→4 | u8/u64 N10/14 остаются; N11/12/15 opt-in | 640,5 + T600→17,5 |
| insertion safety lower, 10→2 | Plain/Cell N1..5 offsets остаются; N6..14 opt-in | 650,9→13,5 |
| insertion safety upper, 56→10 | Plain/Cell N20 со всеми offsets1..20 остаются; N15..19 opt-in | 1709,3→450,3 |
| u64 network safety, 6→2 | Freeze N0..17 и u64 unstable30..32 остаются; N18..29 opt-in | 862,0→381,4 |
| trait dispatch safety, 22→18 | Сохранены bytes/drop/u8 dispatch до N32; u64 general/noncopy/stable N31/32 opt-in | 2007,4→1473,9 |
| swap types, 8→6 | u8/u64/bytes16/17/Cell/Drop остаются; bytes85/86 opt-in | 742,8→143,4 |
| swap indices, 8→0 | Exact allocations9/12/13/16 opt-in; самостоятельные17/four-position остаются в других harnesses | 222,5→0 |
| mutating Cell routes, 4→3 | Traits N0..8 и13..16 остаются; N9..12 opt-in | 188,9→152,9 |
| C3a types/smoke, 4→4 | Logical Cell N0..2/N7, Drop N0..2 и predicate matrix остаются; four VT UNKNOWN | U4→U4 |
| Остальные 31, без изменений | Assembly, unit-ZST, prefix u8, merge contracts N2..4, sort4, reachability, swap17/four-position, mutating permutation | 546,0→546,0 |

B содержит **144 ordinary**; **184** перемещены в opt-in, ни одна гармоника не удалена. Разделение возвращает 19 merge stub callers с 9 exact contracts в дополнение к двум grouped N2..4; переносы между аллокациями остаются недоказанными. Дыры по lengths не выводятся из соседних доказательств.

Следующий шаг — вариант C: поднять границу merge до N10 для обоих типов (150 ordinary); отдельное решение после проверки стоимости и доменных зависимостей.

## Прогноз времени и памяти

[metrics.json](metrics.json) и [scope.tsv](scope.tsv) дают 144 ordinary: 140 с известными macOS VT и 4 C3a UNKNOWN. Сумма известных времён — **4520,3 с (75,3383 мин)**; известный max — **230,2 с**; **8** известных harnesses выше 120 с; >300 с — 0 известных. Полный прогноз — 4520,3 с + U1+U2+U3+U4, max `max(230,2; U1..U4)`, а число >120 равно `8 + count(Ui>120)`. 120 с — ориентир из organizer guidance #56, не hard limit. Наша рабочая цель около 1 часа и max 300 с превышена по известной сумме; данный B выбран ради возврата нужных contract/caller domains. При jobs=3 идеальная сумма известных VT соответствует 25,11 минутам параллельного времени без compiler/setup/прочего std, но не wall-time гарантии.

Арифметика B: A=3583,3 с + VT callers251,4 с + contracts685,6 с = 4520,3 с. Масса переноса — 184 harnesses, всего positive opt-in **252 = 68 прежних + 184 перенесённых**, FAILED controls 26 и deferred unsupported 1; controls cfg inventory прогнозируется как 423 имён. При jobs3 одновременно возможны до трёх тяжёлых proofs; каждый из четырёх UNKNOWN также может оказаться тяжёлым. Источники — [metrics.json](metrics.json), П-6 [mac-times.tsv](../c3c-inputs/mac-times.tsv) и ограничения [RESULT-C3C](../RESULT-C3C.md); фактический `kani list` не выполнялся.

П-6 partition history описывает исторические proof outcomes, не память нового набора. По [C3c baseline per-harness-memory.tsv](../c3c/per-harness-memory.tsv) (library `e9655515`, head `f9bdf626`, build `e358163c-9006-4ea0-a402-c12a5a009747`) у moved route/tail checks есть индивидуальные peaks: u64 route N31/N32 — около 3,92/4,12 GiB CBMC HWM, shifted tail START1 — около 2,85 GiB. У большинства выбранных proofs атрибутированной памяти нет. Эти значения не предсказывают одновременный пик B. Не складывать независимые PID maxima; новый simultaneous peak и C3a per-harness memory остаются неизвестны.

## PR2 — отдельный вариант

PR2 получается одним коммитом, возвращающим файлы `library/core/src/slice/sort/shared/smallsort/verify.rs` и `verify/*.rs` ровно к `e9655515` (ревью 2026-10-29: [pr2-ungate.patch](pr2-ungate.patch) снимает 175 бюджетных cfg из [budget-gates.tsv](budget-gates.tsv) и даёт ту же раскладку гармоник, но оставляет комментарии варианта B и разделённые импорты, которые `imports_granularity="Module"` потребует слить). Прежние controls (26 ожидаемых FAILED) остаются под cfg.
В копии дерева статически восстановлены 328 ordinary `e9655515` (325 + C3a); FAILED26 неизменны — [прогноз PR2](pr2-static-check.json), [список](pr2-ordinary.txt); сборок не было.
Партиции `check-kani-on-std` исторически прошли на `6cfc76cb` (П-6), 8/8, Actions run `40748125754`; на новом SHA не проверено — источник [TASK-SCOPE, правка 1](../TASK-SCOPE.md#правки-по-обсуждению-с-планировщиком-обязательны-имеют-приоритет-над-текстом-ниже).
История `kani_autoharness`: три macOS TIMEOUT600 и гибель Ubuntu runner — [TASK-C3C](../TASK-C3C.md); причина остановки Ubuntu не установлена — [RESULT-C3C](../RESULT-C3C.md); на новом SHA не проверено.
Эта история не гарантирует результат нового PR2 SHA; C3a имеют отдельное evidence, все четыре macOS VT UNKNOWN, полный ordinary std и autoharness требуют проверки.

## Covers и ограничения композиции

E не включён: тела harnesses и политика covers сохраняются; item-level cfg переносит proof вместе с его covers. Если позже менять covers или выбирать C3c splits, нужен новый union map и аудит migrated/retained covers на обеих конфигурациях. C3c split timing получено в другом сочетании E/K/solver и требует повторного замера перед переносом на B.

Для general/noncopy/stable u64 trait-safety N31/32 больше не ordinary. Сохраняются три-route N2/8/16, u64 Freeze unstable N30..32, bytes/drop/u8 dispatch до N32 и insertion safety offsets до20; эти утверждения ограничены типами/маршрутами из конкретных harnesses. Они не составляют generic maximum theorem для всех trait families.

Ordinary merge callers используют `stub_verified(bidirectional_merge)`; matching type/N/comparator `proof_for_contract` остаются в B. Эти зависимости нужно подтвердить фактическим раскрытием. Exact-N proofs не покрывают scratch48 и shifted regions. Поэтому caller+callee в одной ordinary конфигурации устраняет меж-конфигурационный разрыв, но композиция между allocation models остаётся условной.

## Статическая проверка и текущее состояние

Library-коммит B `b3213b9be0` поверх `c8fce2fe` снимает только 28 proof cfg; отдельный review-fix `d627e2ffbd` гейтит 14 helpers/imports и исправляет комментарии без увеличения числа их строк. Итоговый library tree: `462e8f1cc3d4104d1513fba0303c4591f32a1da4`. Тела всех items, assertions, домены, covers, solver/unwind и импортированные имена сохранены; импорты только разнесены по cfg.

[static-check.json](static-check.json): 423 уникальных имени, ordinary144/opt-in279, 15 matching contract edges и 4 caller N0/1 без merge. Всего 175 новых cfg: correct28/merge58/network89 = 161 proof + 14 helper gates. [helper-use-check.json](helper-use-check.json) не прогнозирует новых unused_macros/imports/dead_code в обеих конфигурациях; прежние allow(dead_code) merge/network сохранены. Rustfmt по заданному wrapper/config — exit0, строки Rust≤100. Это статический прогноз, не компилятор, macro expansion, фактический `kani list` или доказательство CI.

Воспроизведение из корня: `python3 research/challenge-8/kani-k1/scope/prepare_scope.py`, затем `check_scope.py`, `check_helpers.py`, `prepare_pr2.py` из той же папки. `reproduction_commands.py --manifest ordinary|extended-positive|controls-failed` только печатает будущие команды и ничего не запускает. Полный будущий [план проверки](VALIDATION-PLAN.md) не выполнялся; сборки запрещены этим этапом.

## English PR draft (proposed scope, not a CI result)

The default SmallSort suite keeps 144 ordinary harnesses; extensions use
`RUSTFLAGS="--cfg kani_smallsort_controls"` with separate exact-name manifests for 252 positive
extensions, 26 expected failures and one deferred diagnostic. Proof bodies and covers are preserved,
following the runtime guidance in [#56](https://github.com/model-checking/verify-rust-std/issues/56).
Merge callers through u64 N8/u8 N9 retain matching T/N contracts; scratch composition stays conditional.
The selected SHA has not been validated by CI; four C3a macOS timings remain unknown.

- `correct` opt-in: insertion-stub fallback u64 N8..16/u8 N9..16, u8 scratch48 and general/stable N14/15; earlier u64 scratch/N15 controls remain opt-in.
- `merge` opt-in: contracts u64 N9..16/u8 N10..16, general/stable callers u64 N9..12/16 and u8 N10..13/16, real fallback N7/8, tag N16, three-route safety except N2/8/16.
- `network` opt-in: shifted u64 tails; correctness u8 N8/10..12/14..17 and u64 N8/10..14; suffix N11/12/15; insertion N6..19; u64 safety18..29/Cell9..12; standalone dispatch31; swap widths85/86 and allocations9/12/13/16.
- Negative controls remain opt-in; the four C3a timing values remain unknown.
