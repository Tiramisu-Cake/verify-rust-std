# Kani #3300 Part 1 — отчёт для независимого аудитора, раунд 4

Срез: **14 ноября 2026**, research-ветка `experiment/kani-k1-kani3300g0-20261111`. Аудитор может читать отчёт без предыдущего контекста.
Это верификация корректности инструмента, не security-работа. Новых запусков этим отчётом не запрашиваем.
Код и свидетельства заморожены; решение о дальнейшем объёме владелец хочет принять вместе с аудитором.

## 1. Состояние и главный вопрос

Part 1 расширяет экспериментальные `-Z uninit-checks` Kani для storage `MaybeUninit` и некоторых передач состояния.
Полный Linux regression gate на C1b прошёл, по отчёту координатора: run **43521643425**, все 29 стадий `EXIT_ZERO`.
Это существенный прогресс относительно R3: есть легальное PFC-свидетельство, lawful-modifies и завершённый regression.
Но **положительные SmallSort строки с uninit ON не прошли**: Gate B run **43533328479** заблокирован по scope.
Причины — `select_unpredictable` и вызов компаратора через fn-item/`FnMut`/fn-pointer, а не ложный uninit в этих строках.
Все 6 OFF companions прошли; ON negative обнаружил предназначенное чтение незаписанного элемента, но имеет ещё Unsupported.
Это не завершённое доказательство SmallSort и не положительный ON replay. Исходный критерий Gate B не выполнен.
Развилка: выпустить ограниченный инструментальный этап с названными границами либо добавить недостающие конструкции
в Part 1, заново заморозить экспорт и повторить gates. Обе возможности разобраны в §10 без предрешённого выбора.
Мнения координатора и планера указаны отдельно от фактов. Ни READY, ни зелёный expected-negative не означают proof SUCCESS.

## 2. Зачем Part 1 и что именно проверяется

[Kani #3300](https://github.com/model-checking/kani/issues/3300) — широкий tracking issue об автоматическом контроле initializedness.
Наш Part 1 — ограниченный вклад в эту поддержку; закрытие всего #3300 не заявляется.
Практическая цель SmallSort: проверять scratch `[MaybeUninit<T>;N]`/срез слотов и `MaybeUninit<[T;N]>`,
где записан лишь используемый префикс, а остальная память законно остаётся неинициализированной.
Нужны legal SUCCESS и различающий bad-read negative при сохранении raw copy, typed transfer и byte masks.
Контракты нужны для модульной проверки реальных helpers; одного uninit-OFF regression для этой цели недостаточно.

Заявляемый ограниченный домен: поддержанные direct-MU/flat-slot layouts, storage extent, typed data masks,
записи/reset/copy, перенос true/false через квалифицированные обычные аргументы/возвраты, immutable masks,
ordinary/Assert и nonrecursive SimpleCheck paths, реально охваченные тестами.
Не заявляются произвольные T/N, полная Rust move/alias/valid-value семантика, все unions/compound layouts,
Replace/shadow transfer через `stub_verified`, RecursiveCheck/shadow transfer, realloc/foreign effects и весь SmallSort.
Вложенные by-value агрегаты с MU/union не получили общей поддержки. Публичная документация прямо предупреждает,
что эти пути могут давать false positives **или пропускать uninitialized reads**, то есть не гарантированы fail-closed.
Нельзя распространить наблюдаемый tuple-return false FAIL на все неподдержанные агрегаты как гарантию консервативности.
`select_unpredictable`/компараторы остаются открытыми практическими границами; их выпускная формулировка ещё предмет решения.

## 3. Архитектура модели и карта кода

**Один nondet byte-witness.** Runtime выбирает `(object, offset)` и хранит Boolean initializedness этого байта;
это не полная bitmap всей памяти. Reset начинает со false; get/set/copy обновляют состояние относительно свидетеля.
Чтение вне выбранного диапазона не опровергает безопасность; настоящий плохой байт должен иметь свидетельствующую ветвь.
Пропущенный setter способен дать false positive, а необоснованный bless/потерянный check — false negative.
Код: [mem_init.rs][k-runtime], прежде всего state, get/set, copy_by_id и argument buffer.

**Storage против typed data.** Rustc extent/stride определяют диапазон. Typed MU transfer сохраняет payload data mask,
а не обещает initializedness padding T. Raw byte copy и full-range byte read имеют другую маску/обязательство.
`Some(0)` — инициализированный ноль; `None` — hole, даже если backend записал нулевые bits.
Код: [ty_layout.rs][k-layout], [операции check_uninit][k-uninit], [raw_eq operand lowering][k-operand].

**Call protocol.** Caller снимает snapshot живого source: witness membership/relative offset/value;
снимки предшествуют source deinit при in-place `Call(Move)`. Pairing проверяет текущий call, indices и layouts.
Callee получает argument state, return использует обязательный slot0; caller загружает его на normal edge.
False не равен отсутствию выбранного свидетеля. Перечитывать уже умерший source вместо snapshot нельзя.
Код: [uninit_visitor.rs][k-visitor] и runtime store/load_argument; nested aggregates не покрыты этим обещанием.

**Delayed UB.** Локальный проход видит raw/union операции; points-to/relevance направляют дополнительные checks/setters
в обычные typed операции. Анализ должен видеть те generated contract bodies, которые реально вызывает codegen.
S3 добавил такой путь; CC1–CC4 устранили выявленные им crash/ложные scalar/ref отказы и уточнили границы.
Код: [delayed_ub][k-delayed], [points_to_analysis.rs][k-points]. Общий cache T1b остаётся отдельным риском (§8).

**Immutable origins.** Registry связывает actual allocation, emitted symbol и точную byte mask, затем сеет её
после normal reset completion. M1 покрыл квалифицированные anonymous/promoted origins, E2 — named immutable statics.
Нельзя благословить произвольный referent по одному типу ссылки; subrange/mutability/relocations требуют квалификации.
Код: [immutable_allocations.rs][k-immutable], [static emission][k-static], [anonymous origins][k-anonymous].

**DFCC/frame.** Verifier-private `MEM_INIT_STATE` включается в assigns, чтобы bookkeeping не нарушал user frame.
Маркер/private assigns уже существовали upstream; Part 1 не изобрёл этот механизм. User pointees от этого не становятся writable.
Гипотеза о таблицах DFCC размером `2^object_bits` получила сильную ресурсную поддержку (§6.1). Marker lookup всё ещё использует
`unwrap_or_default()`; зависимая от реальных effects диагностика отложена (§7), существующий код не заменён.
Код: [contract.rs][k-contract]. Положительные lawful-modifies и отдельный user-frame negative нужны вместе.

## 4. Замороженные идентичности и размер пакета

| Роль | Фиксированная идентичность |
|---|---|
| Исследовательская upstream base | `bf9c58e662fd65c64381ef2ac97a6397ffc0693a` |
| C1, fork `freeze/kani-3300-part1-c1` | `1658f4cadfa83139e41180ce3865e23f79d889aa` |
| C1 tree | `bfb5eb9db13ffb91ec4585b7c7ef41ddfe0008fb` |
| C1b, fork `freeze/kani-3300-part1-c1b` | `3f2c12f46e9e32899e8d84e89c65cb6483ba685a` |
| C1b tree | `e629978d8f0746bddf896d58a156bad2c59f14ce` |
| Gate A C1b CI overlay / run | `7ff2292142` / `43521643425` |
| Gate B C1 CI overlay / run | `ac49cf8f62` / `43533328479` |
| Kani dependencies C1b | nightly `2026-10-23`, CBMC `6.11.0`, Kissat `4.0.1` |

C1b — direct child C1: только 10 JSON-suite файлов, **+278/−107**, нормализация paths и adversarial tests.
Compiler/runtime/library source между ними неизменен. Gate A относится к C1b, Gate B фактически к C1;
перенос применимости Gate B на C1b опирается на отсутствие production delta, а не на повторный запуск Gate B.
Baseline для будущего upstream/rebase — отдельное решение: этот отчёт не утверждает, что исследовательская base есть current main.

Прямой `git diff --numstat/--shortstat base..C1b`, прочитанный при подготовке: **331 файл, +21 422/−406**.

| Подсистема | Файлов | Добавлено / удалено |
|---|---:|---:|
| kani-compiler | 21 | +2 267 / −342 |
| library/kani_core runtime | 1 | +204 / −64 |
| docs | 1 | +19 / −0 |
| tests/expected/uninit | 279 | +6 096 / −0 |
| tests/json-handler | 29 | +12 836 / −0 |

Это размеры diff, не количество доказанных обязательств. Большая доля — fixtures и сериализованные inventories.
Новые группы включают padding/typed transfer, argument/return pairing, unresolved calls, immutable masks/mixed origins,
closure/capture, semantic edges, composition, два точных contract/mode suites и mixed-root JSON suite.
В export нет research handoff docs и исследовательских workflow overlays. Сама история многих диагностических стадий
не предлагается как удобная нарезка upstream PR; reviewable decomposition остаётся открытым вопросом.

## 5. Хронология: ранние ограничения и исправления модели

Строки ниже — исторические свидетельства, не перенос acceptance со старого tool/source на C1b.
Fork Actions facts взяты из reports/хронологии координатора; ранние Cloud UUID — из curated RESULT, не из raw архивов.
READY/NOT_RUN в подготовительном RESULT не переписывается задним числом: поздний CI указан отдельно.

| Стадия | Симптом → причина → решение | SHA/run и источник |
|---|---|---|
| U0 | Layout/transmute/raw-pointer+union/fn-pointer Unsupported; scratch MU array отвергается. Установлены исходные границы, не исправление. U5 insert_tail SUCCESS не означает общий replay. | Kani `f046b70644`; run `51f228c7-615f-4027-8bae-d68fb293e132`; [U0 RESULT][r-u0] |
| U1→U2 | Storage/primitive-array ремонт дал discriminating raw negatives и U6 union-output SUCCESS; U8/U9 и U7 остались блокированы. | U2 `6a2f4260-c343-427f-a6ef-6ed0bce50b7c`, head `108551d92b`; [U2 RESULT][r-u2] |
| U3 | Flat state и calls расширены; repaired run17/20 native PASS,3 ERROR. PFC buffer/negative не приняты. | `45287677-98cb-4dc4-b98d-7ccae4782f5f`; [U3 RESULT](kani3300/u3/RESULT-KANI3300-U3.md) |
| U3B | Два PFC+uninit roots дали Kani-reported OOM, OFF companions SUCCESS; ограничение записано, не исправлено. Kernel/RSS причина тем ранним пакетом не доказана. | `9f964706-4b89-4340-a1ee-022aa23ecbe9`; [U3B](kani3300/u3b/RESULT-KANI3300-U3B.md) |
| CMP0/CMP1 | `IntoIter`/compound MU fields потребовали product-layout; CMP0 — дизайн, CMP1 частичный 15 PASS/3 ERROR, остальные причины UNKNOWN. Этот эксперимент не принят как Part 1 support. | CMP1 `77e4765a-d82a-48c8-bf2e-cb6ae2fcdc07`; [дизайн][r-cmp0], [RESULT][r-cmp1] |
| Первый Part 1 R1 | `1cd96e354` прошёл старый Ubuntu CI, но аудит нашёл typed MU padding false SUCCESS. Старый зелёный CI не оправдывает старую маску. | `43027843249`; [первый аудит](AUDIT-REPORT-KANI3300-RU.md), [R3 brief](AUDIT-BRIEF-KANI3300-PART1-R3.md) |
| A1 | Storage extent отделён от typed D(T), учтён stride/false. Четыре padding negatives на R1 ошибочно SUCCESS, на исправлении отвергаются. | `613c188313`, prod `fc37f9021`; runs `43105165870`85/0 и baseline `43105207965`81/4; [A1](kani3300/a1/RESULT-KANI3300-A1.md) |
| A2/A2R/A2R2 | Pat offset и enum-local masks исправлены. Blanket raw_eq Unsupported оказался слишком широким; восстановлены full-range checks обоих operands. Legal false FAIL ещё оставался. | `3dc0227cee`→`b207847932`→`585c93b2ff`; `43107071880`, `43111242922`, `43117585146`; [A2R2](kani3300/a2r2/RESULT-KANI3300-A2R2.md) |
| A3/A3R | Snapshot до Move, current-call pairing и обязательный return0; затем ремонт dependency/custom-MIR fixture. Это protocol repair, а не новое обещание всех aggregates. | `0b1d68ac69`→`a0a2386001`; `43116356531`64/30→`43118703581`93/1; [A3R](kani3300/a3r/RESULT-KANI3300-A3R.md) |
| B1I/B1I-A | Resolver Err терял накопленные operand checks/loads; сохранены один walk/flush, fallible seeds и no-body guard. Затем исправлены 6 неверно привязанных fixtures. | prod `cdb439b0a4`, tips `dc5f5a4067`→`6134e42dd1`; `43196180814`111/7→`43199156872`119/1; [B1I-A](kani3300/b1ia/RESULT-KANI3300-B1IA.md) |
| D0→M1 | Legal raw_eq падал на promoted immutable RHS: bytes Some, shadow false без seed. Registry/masks и reset-completion seeding закрыли этот путь. | D0 `43209338134`; M1 `254ae69662`/`5abdcf982d`, `43222702257`130/0; [D0](kani3300/d0a/RESULT.md), [M1](kani3300/m1/RESULT-KANI3300-M1.md) |
| C1-T2-A | Первые promoted-only тесты проходили и до M1, потому не различали модели. Исправленные mixed stack/promoted controls различили 6 legal cases и сохранили holes. | snapshot `7f9eec41e8`; M1 `83ceadf048`, `43230532195`138/0; baseline `43230538511`127/7; [bindings](kani3300/c1t2a/BINDINGS.md) |
| M2 | Qualification ordinary/PFC/ensures выявила Assert false positive и отдельный ресурсный блокер. Незавершённые Quick не acceptance. | `5f7f2b7364`; probes `43243491671`/`43244391200`; [M2](kani3300/m2/RESULT-KANI3300-M2.md) |
| S3 | Delayed analysis видел source registration body, а codegen — trampoline с closure. Следование реальному registration body восстановило setters обычного Assert/ensures. | prod `58497d98d0`, tip `4f64cc617c`; restricted Quick `43257528539`135/0; [S3](kani3300/m2bs3/RESULT-KANI3300-M2BS3.md) |

Restricted Quick S3 исключал `legal-pair` и `postcondition-hole` из-за ресурса. Он не был полным gate и не дал PFC acceptance.
Также M1 не завершил общий provenance/offset/alias model; узкие различающие controls важнее общего слова «mask support».

## 6. После R3: ресурс, closures, совместимость и финальная композиция

### 6.1. Ресурс: отказ от неверного направления поиска

R1–R8 перебирали представления/местоположение argument buffer. D1 собрал модель/SSA, но первый анализ не нашёл offender.
Аудитор R3 указал confounder «buffer внутри DFCC frame или вне» и чтения таблиц размера `2^object_bits`.
Поэтому прежний вывод «object/offset representation — установленная причина OOM» снят; R7/R8 не вошли в export.
Г 1 STEP0 пересчитал сохранённые потоки; STEP1 проверил production `4f64cc617c` при 8/10/12/14 bits и диагностические флаги.
Run **43393496999**: точные fits первых CNF для 8/10/12/14 — `V=774·2^b+57916`, `C=1926·2^b+92735`, residual0.
При 12 P1 имел 3 228 220 variables/7 981 631 clauses, sampled group RSS1 901 724KiB=1.814GiB;14/16 остановил RSS watchdog.
`--no-slice-formula` при 12 уменьшил V на 82.0%; это диагностика, не принятая глобальная замена профиля.
Связь с 6 sliced reads поддержана данными, но полная owner/read/version binding кандидата не установлена одними fits.
Все завершённые P1 тогда ещё давали closure Unsupported; PFC postcondition был UNREACHABLE. Ресурсное облегчение не было proof.
Владелец принял 12 bits для тяжёлых fixtures; это не уменьшение N/geometry/числа проверок, но object capacity надо проверять.
Источники: [STEP0](kani3300/h1-step0/RESULT-H1-STEP0.md), [STEP1](kani3300/h1-step1/RESULT-H1-STEP1.md), [finding](kani3300/h1-step1/SEMANTIC-FINDING.md).

### 6.2. Closures и S3-COMPAT

| Этап | Причина и изменение | Подтверждение и предел |
|---|---|---|
| CLOSURE-ZST | apply_closure требовал layout capture-free closure; sized zero-size environment получил пустую маску. | `0ad35c0a93` + flags `e0340be9ff`; `43403281233`:18/18, P1 SUCCESS; [handoff](kani3300/closure-zst/RESULT-CLOSURE-ZST-PREP.md) |
| Возврат heavy tests | `ee2695e5a2`: legal-pair/postcondition-hole на 12 bits. | Quick `43419217261`:expected155/0,kani22/0,ui14/0,script1/0; legal_pfc_transfer SUCCESS. Поздняя оценка координатора: прежние exit143 были memory exhaustion на 16 bits. |
| LAWFUL-ORACLES | Lawful twin проверяет реальные разрешённые writes, отдельный negative — нарушение user frame. | `0beeb6b79e`/`7b2d5631b`; `43424583581`/`43428996316` lawful SUCCESS; c2 `43434557435`8/8 strong oracles. |
| S3 regressions | Generated bodies сделали достижимыми points-to recursion, незасеянные bool/ref parameter/upvar slots и неподдержанный captured layout. | c2 `fef9e0f38`; [FINDINGS](kani3300/mode-findings/FINDINGS.md). Это внесённые Part1 проблемы, не только upstream boundaries. |
| CC1 | Active instance/body keys и cycle error без выхода partial graph; compiler overflow заменён Unsupported. | `b2e1a392a`, Quick `43442603191`expected162/0; [CC1](kani3300/s3-compat/cc1/RESULT.md). Cycle support не добавлен. |
| CC2 | Entry setters для ordinary scalar/ref argument slots; ref setter инициализирует representation, не pointee. | `9631aaf89`, `43448885164`expected165/0; bool исправлен, captured &bool ещё требовал CC3; [CC2](kani3300/s3-compat/cc2/RESULT.md). |
| CC3 | Layout closure по actual monomorphized upvars/offsets, recursive masks. | `76a706f8f`, `43453928092`:ordinary/SimpleCheck companions PASS;2 capture cases дошли до прежних union/UnsafeCell Unsupported; [CC3](kani3300/s3-compat/cc3/RESULT.md). |
| CC4+collector | Provenance циклов,2 точных boundary expectations; исправлена grouping covers в generated/original copies, не семантика проверки. | `d7151a220` + `6fad97f47`→`94c00a885`; Quick `43465107918`:expected168/0,json2/0; [CC4](kani3300/s3-compat/cc4/RESULT.md). |

На 94 ordinary/SimpleCheck Replace companions и bounded recursive SimpleCheck проходят; genuine recursive ordinary/check
дают явный analysis-cycle Unsupported. Это документированная граница, а не SCC/recursive-contract verification.
Перезапуска с source panic-body вместо registration override для «возврата к upstream» не вводили.
Ранние сообщения о recursive_simple_check Unsupported были исправлены: проблема была в collector covers, root фактически SUCCESS.

### 6.3. E1/E2 и откат aggregate guard

E1 `dc24745c6` материализует constant ordinary-union operand mask, ставит setter для `(*ptr).field=v`
на точный field range и явно отклоняет unsupported unsized by-value transfer. Добавлены 17 singleton controls.
C0 run **43474396386** выявил 5 immutable failures:4 fixture transmute errors и named-static legal false positive.
E2 `19588e0af` исправил формы сравнения и добавил exact masks квалифицированных named immutable statics.
После coordinator clippy/rustfmt и disposition subrange: C0 `53d883add`, Quick **43481108546** всё PASS, expected185/0.
Nonzero-offset immutable subrange не получил общий seed: его legal false FAIL сохранён как известное ограничение.
Relocation-bearing test PASS не означает общей admission всех relocation layouts.
Источники: [E1](kani3300/final-edges/RESULT.md), [E2](kani3300/final-edges/e2/RESULT.md), coordinator chronology.

M3 R1 `34d54caf1`→`dc9c77db6`→`aac27ed95`, Quick **43488479150**: offset fixtures исправлены, legal Move/return false FAIL.
`handoff` возвращал `(MaybeUninit<u8>,u8)`; nested slot не получал top-level Store/LoadArgument.
Пропуск установлен по source, но общий transmute property не локализует конкретный dynamic assume_init без trace.
R2 `88c532d6c` добавил общий nested-slot guard; Quick **43494738738**expected202/16 показал diagnostic regressions B1,
ранние иные Unsupported, Cell<MU>/aggregate отказы. Guard признан слишком широким и **целиком исключён**.
R3 `6c29e38c5` от исходногоaac: top-level MU return + scalar out сохраняют Move, repair23, returned42 и bad-read companion.
Исходный tuple-return вынесен в known false-positive test; семантически legal root должен SUCCESS, его FAILED не UB credit.
Quick **43498489470**expected202/0; JSON тогда BINDING_PENDING, это ещё не его acceptance.
Источники: [STOP-R1](kani3300/m3-final/STOP-R1.md), [R3 result](kani3300/m3-final/r3/RESULT.md), coordinator chronology.

### 6.4. Циклы, binding и C1→C1b

Capture сначала вскрыл runner validation error PFC, затем реальные различия T1b и нестабильные числовые Ty/AdtDef diagnostics.
`3a29b3323` исправил capture validation; `ada5c7bd4` сохраняет все сравнения и явно ограничивает T1b allowance.
`585768eb1` заменил compiler-local числовые frames на читаемый cycle path; это diagnostic stability, не устранение цикла.
Capture r4 **43506774865**:11 invocations,18 accepted comparisons =12 exact +6 scoped T1b; cycle inventory384 checks:
337SUCCESS,46UNREACHABLE,1FAILURE `cycle_root.unsupported_construct.1`. Все 4 mixed selections сохранили его точно.
`3912b8e03` связал 6 roots; C1 `1658f4cad` — седьмой cycle root. BINDING_PENDING=0.
Квалификационный Quick **43509654772** на C1: kani22/0,expected202/0,ui14/0,script1/0,json3/0.
Первый полный Gate A обнаружил зависимость oracle paths от cwd/checkout, не compiler/model failure.
C1b `3f2c12f46` нормализует только корни checkout/rustup и traversal depth, включая paths внутри closure/cycle identities;
toolchain/source suffix/coordinates/check metadata остаются проверяемыми. Добавлены adversarial normalization tests.
Bounded C1b replay/Python validation:24/24 strong-checker и 53/53 composition synthetic tests; verifier не запускался.
Источники: [T1b capture](kani3300/m3-final/r3-capture-t1b/RESULT.md), [cycle binding](kani3300/m3-final/r4-cycle-binding-worker14/RESULT.md), [C1b](kani3300/final-gate/c1b-worker14/RESULT.md).

## 7. Что сделано по рекомендациям аудитора R3

Основание: [AUDIT-REPORT-KANI3300-PART1-R3-RU.md](AUDIT-REPORT-KANI3300-PART1-R3-RU.md), ответы 9–13 и findings F1–F11.

| Рекомендация | Состояние R4 |
|---|---|
| Не сужать PFC scope из-за неустановленного OOM; прекратить carriers R9+/G-SC | Выполнено: G-SC не реализован, R7/R8 не экспортируются. |
| Проверить DFCC hypothesis STEP0/1 и единицы RSS | Выполнено с указанными пределами binding; fits и KiB/GiB в §6.1, полный ресурсный профиль не уникально доказан. |
| Вернуть heavy tests при достаточных lowered object bits | Выполнено:12 bits, комментарии в fixtures; P1/ordinary/PFC legal прошли. |
| Lawful-modifies плюс user frame negative | Выполнено в bounded oracle suite и финальном regression; не общее доказательство DFCC. |
| Точные negative oracles | Восемь strong cases и 7 bound composition roots; P2 реально имеет 2 checks одного read, а не требуемый буквально 1. Дубль явно учтён, лишние failures запрещены. |
| Replace/Recursive tests или явное исключение | Docs+6 mode roots есть; general support не заявлен, cycles Unsupported. Это ограничение, не полное исправление. |
| Ошибка вместо `unwrap_or_default()` private assigns | **Отложено**: нет обоснованного extent-specific required-state fact; production lookup неизменён. Gate PASS не закрывает missing-marker case. |
| Constant-union ICE / projected field store / DST boundary | E1 + controls; DST — explicit Unsupported, не поддержка. |
| Immutable вне M1 | Named statics расширены E2; nonzero subrange false positive остаётся. Общий outside-admission scope не закрыт. |
| M3 на final export | Composition/move companions и bound suite включены; nested aggregate transfer не добавлен. |
| Два фактических codegen order, shared-unit property isolation | **Не закрыто**: CLI orders проверены, actual producer order ORDER_UNCONTROLLED; scoped T1b allowance не isolation proof. |
| Полный regression Linux x86_64 и AArch64 | Linux Gate A пройден по координатору; отдельного полного финального AArch64 gate в источниках нет — NOT_RUN/UNKNOWN. |
| SmallSort ON replay: legal+hole, оба scratch backing | Частично: реальный negative достигнут, positive ON блокированы (§9); исходный критерий не выполнен. |
| Убрать handoff docs и CI overlays из export | Выполнено; research-ссылки из JSON README удалены, но tooling по-прежнему велик. |
| T1b/ресурсные upstream замечания отдельными треками | T1b не исправлен; сообщение по DFCC/`kani#3611` и эффектам clause helpers остаётся последующей работой. |

Почему отложена marker-диагностика: наличие helper/маркированного static не доказывает private write именно данного wrapper;
нужны transitive effects, delayed injection, no-write cases и корректная классификация UNKNOWN независимо от самого marker.
Заменить lookup на blanket missing-marker error означало бы добавить необоснованную границу.
Координатор принял отдельный STOP этого дизайна: [REQUIRED-STATE.md](kani3300/marker-modes/REQUIRED-STATE.md).

## 8. Границы export и цена JSON-оракулов

[Публичный contracts.md][k-contract-doc] описывает Replace/RecursiveCheck, interprocedural cycles и nested by-value aggregates.
Существующие ограничения union-as-field/UnsafeCell и union-field dereference продолжают давать Unsupported.
Nonzero-offset immutable subrange false positive явно описан **в fixture/research**, но отдельной строки в public docs не найдено.
Политика 12 bits/причина memory limit также в heavy fixture headers; её не надо представлять как уже написанную user guide.
Новые Gate B границы select/comparator ещё не отражают принятого выпускного решения — это важный пробел текста для варианта A.

JSON suites решают реальную проблему: substring `FAILED` не отличает intended payload failure от раннего Unsupported/frame error.
Strong suite связывает 8 cases: ordinary/PFC legal, lawful modifies, P2, postcondition hole, user frame и clause transfer.
Проверяются useful SUCCESS, полный failure multiset и metadata; expected negatives не считаются legal proof.
Mode suite имеет 6 roots и не приравнивает наблюдение Replace к квалификации режима.
Composition suite имеет 7 bound roots: immutable legal/hole, ordinary ensures, PFC legal/negative, cycle и unrelated legal.
Его manifest в C1b — **8 238 строк, около 432KiB**, а не прежняя оценка «~5.8k»; это не размер production compiler patch.
Он привязан к source hashes и конкретным isolated inventories; обновление identities требует review, а не auto-learning.
Capture `--collect-unbound` всегда диагностический, exit2 даже при mismatch; qualification — отдельный bound ordinary run.

Mixed comparison **не требует полного равенства всех свойств**: допускаются только дополнительные/отсутствующие
SUCCESS/UNREACHABLE `.safety_check.N` в reviewed shared `std::ptr::read::<u8>` с exact function location/ID pattern.
Существующие IDs не могут менять status/metadata; failures, Unsupported, assertions, covers и root/target useful checks не exempt.
Различия сохраняются как T1b evidence. Это ослабление относительно исходного exact-inventory gate, ограниченное явным allowlist.
Оно не исправляет shared `BodyTransformation` cache и не доказывает отсутствие lost checks в общем случае.
Actual codegen AB/BA не установлен: оба CLI selector order не заменяют receipt producer order.
Есть цена сопровождения: большие golden inventories, compiler/path/location drift, parser dependency между suites,
дублирование regular/JSON наблюдений и время 11 verifier invocations. C1b исправил уже обнаруженную checkout fragility,
но upstream acceptance такого объёма и формы tests ещё не получено. Сокращать их следует без потери intended negative oracle.
Scope за раунды вырос от storage до immutable origins, generated contracts и cycle handling, затем получил новые исключения.
Этот дрейф требует отдельного review admitted domain; большая матрица regression сама по себе не фиксирует его границу.

## 9. Gates: что завершено и что не завершено

### 9.1. Gate A — полный штатный Linux regression

Первый C1 run **43514459160** дошёл до json-handler9/2; ранние suites прошли, trailing stages не выполнились.
Причина 2 наших JSON-suite failures — checkout/cwd-dependent paths; это основание C1b, не результат полного PASS C1.
Второй run **43521643425**, CI overlay `7ff2292142`, C1b: координатор сообщает 33мин и все 29 `EXIT_ZERO`.

| Часть gate | Сообщённый результат |
|---|---|
| Unit packages / build / fmt | PASS в общем полном gate; индивидуальные unit counts здесь не supplied |
| kani | 647 passed /0 failed |
| expected | 686/0 |
| ui | 168/0 |
| std-checks | 5/0 |
| cargo-kani | 72/0 |
| script-based-pre | 99/0 |
| json-handler | 11/0 |
| Остальные штатные suites | PASS по общему 29-stage сообщению: firecracker, prusti, smack, cargo-ui, coverage, cargo-coverage, kani-docs, kani-fixme |
| После compiletest | firecracker-codegen, manifest smoke, clean и warnings-denied build — EXIT_ZERO |

Источник повторного PASS — сводка координатора по stage summaries публичного [run 43521643425](https://github.com/Tiramisu-Cake/kani/actions/runs/43521643425); аудитор может сверить его напрямую.
Receipt status координатор цитирует как `COMPLETE_EXIT_ZERO_REQUIRES_REVIEW`.
Пакет `final-gate/c1b-worker14/` подтверждает source repair и bounded replay **первого** failing gate,
а не содержит независимый полный review второго run43521643425. Детальные непереданные stage counts — UNKNOWN.
Не читались/не скачивались raw gate archives. Это coordinator-reported completed regression, не независимое доказательство модели.
AArch64/macOS финального export и LLBC-specific full gate здесь не заявляются; historical runs их не подменяют.

### 9.2. Gate B — SmallSort replay,12 object bits

Std snapshot `70ba5befc617627073738e26cb1466bd4fb76e41`, library tree `6ea9d3425f6d0478cfc2517cbdd2fb7d7b32a53f`.
Test-only overlay добавляет matched raw-helper pair; production SmallSort ради зелёного replay не менялся.
Декларированный профиль по REPLAY-REQUEST/root map: ON/OFF различаются `-Z uninit-checks`, valid-value-checks OFF,
default checks/solver/slicing; ordinary `--no-assert-contracts`. PFC body selection требует отдельного binding, а не вывода из одного этого флага.
План scratch profiles включает flat48 и `MU<[T;48]>`, source prefix и offset32; geometry см. [root map](kani3300/final-gate/REPLAY-ROOT-MAP.md).

| Попытка | Run | Где остановилась / исправление |
|---|---|---|
| 1 | `43514465580` | До verifier: argparse Path превратил URL в `https:/github.com`; `432a083596` меняет тип на str. |
| 2 | `43520983660` | До replay: shell comment поглотил `--destination`; `afc273c7a2` исправляет invocation. |
| 3 | `43526151639` | Std build: не initialized `library/backtrace` submodule; `ac49cf8f62` добавляет submodule init. |
| 4 | `43533328479` | Все 12 строк завершили preparation/std build/Kani; scope-blocked результат ниже. |

| Строка run4 | Результат | Полный набор failures по coordinator summary |
|---|---|---|
| Все 6 OFF companions | PASS(expected) | Нет failures; это compatibility, не uninit proof. |
| raw-legal-on | FAILED1/387 | `select_unpredictable` Unimplemented, hint.rs:871, `<*const u64>`. |
| raw-negative-on | FAILED2/387 | Intended uninit `sort4_stable.safety_check.1`, smallsort.rs:751, source[1], плюс тот же select Unsupported. |
| sort8-boundary-on | FAILED1/589 | `select_unpredictable`; это ещё и boundary root со stub, не actual merge proof. |
| sort4-pfc-on | FAILED1/761 | fn-item comparator через `FnMut::call_mut`, function.rs:166 Unsupported. |
| merge-raw-pfc-on | FAILED1/573 | Та же fn-item comparator class. |
| merge-profile-pfc-on | FAILED1/1027 | «checks across calls through function pointers», function.rs:166. |

Источник: [run4 RESULT](kani3300/final-gate/gateb-run4/RESULT.md), публичный [run 43533328479](https://github.com/Tiramisu-Cake/kani/actions/runs/43533328479); остальные checks сообщены SUCCESS.
False-uninit в этих строках не найден, но positive ON **не SUCCESS**. Недостижимые после Unsupported effects не квалифицированы.
Negative различает unwritten source read и legal source по intended check, но не является чистым единственным-failure negative.
Root-map/REPLAY-REQUEST — pre-run планы, не самостоятельные доказательства actual effective argv/selected bodies run4.
Run4 сводка ссылается на coordinator receipts/stdout; полного их независимого review при написании не было.
Итоговый status Gate B — **BLOCKED по scope**, не очередной дефект harness infrastructure и не GO.

## 10. Центральная развилка: граница Part 1 или расширение

### 10.1. Почему это отдельное решение

U7/SEL0 и U4 были известны до финального replay, но Gate B план ошибочно требовал legal ON SUCCESS без их устранения.
Отсутствие false-uninit — полезный результат, однако не заменяет возможность пройти всю целевую программу с checks ON.
В [SEL0 DESIGN][r-sel0] уже есть статический разбор, **SEL1 не реализован** и не квалифицирован на C1b.
Важная деталь SEL0: реальный `hint` wrapper выбирает не только pointers, но и `MaybeUninit<T>` перед assume_init;
одна backend ветвь для scalar/pointer intrinsic не гарантирует успех всего wrapper/SmallSort U7.
Нужно сохранить выбранный arm, aliases обоих возможных referents и shadow false/padding, не bless обоих pointees.
Comparator fn-item и настоящий fn-pointer тоже нельзя объединить в «снять Unsupported»: требуется resolution/effect coverage,
чтобы indirect path не потерял checks/targets, уже защищённые B1. Наличие fallback body само по себе не доказательство поддержки.

### 10.2. Вариант A — ограниченный инструментальный этап сейчас

Обе конструкции явно остаются за Part 1; SEL1 и comparator-call support предлагаются отдельными дальнейшими изменениями.
Поставка содержит MU/storage/protocol/immutable/contract fixes с полным regression и малыми положительными PFC controls,
но **не обещает legal SmallSort uninit-ON verification**. Для практической цели SmallSort остаётся незакрытый downstream шаг.
Gate B можно принять лишь по **новому явно ограниченному критерию**: OFF compatibility + reached intended negative
и named Unsupported на ON positives. Нельзя переименовать это в выполнение прежнего positive-ON gate.
До подачи потребуются согласованное scope wording в docs/PR, явный ledger незакрытых целей и review границ nested aggregates/T1b.
Объём меньше варианта B: новые intrinsic/call semantics не реализуются; сложность review уже существующего пакета всё равно велика.
Риск — мейнтейнеры сочтут practical evidence недостаточным либо попросят разбиение. Преимущество — проверяемые части
не ждут ещё одной серии compiler/model изменений, а dependency chain можно обсуждать предметно.

### 10.3. Вариант B — включить недостающую поддержку в Part 1

SEL1 и/или comparator-call support реализуются, проходят matched legal/hole/alias/Move/padding и scope controls,
затем новый export freeze, полный Gate A и Gate B заново. Старые receipts не относятся к изменённому production tree.
SEL1-only может разблокировать raw helper, но не comparator PFC; comparator-only не закрывает U7.
Чтобы получить все требовавшиеся positive ON строки, вероятно понадобятся обе зависимости, а не произвольная одна.
Объём — отдельные design/implementation/qualification стадии; достоверной календарной/денежной оценки в источниках нет.
Риски: selected-arm shadow transfer, points-to alias joins, indirect/trait-call resolution, callback effects и новые S3-like regressions.
Снятие этих двух Unsupported может открыть следующий неисследованный путь; успех всего replay заранее не гарантирован.
Награда — возможность дать SmallSort положительное bounded uninit свидетельство на реальных scratch profiles,
а не только набор минимальных инструментальных tests и различающий negative.
Для upstream review пакет станет ещё шире; новые темы можно разбить на dependency PR, но это не автоматически один обзорный diff.

| Критерий | A | B |
|---|---|---|
| Production scope сейчас | Без SEL1/comparator расширения | Добавляется одна/обе зависимости |
| Малые legal PFC controls | Уже есть в export/gate | Сохраняются и перепроверяются |
| Реальный legal SmallSort ON | Не достигнут; явная последующая цель | Цель нового gate, пока NOT_RUN |
| Формулировка Gate B | Ограниченное принятие с исключениями, не исходный PASS | Повтор исходного критерия после реализации |
| Риск новой модели | Меньше новых изменений, прежние exclusions остаются | Выше; нельзя снимать guards без замены проверок |
| Reviewability | Нужна нарезка текущих 331 файлов | Нужна нарезка и новых тем/dependencies |

**Мнение координатора:** вариант A. Это предложение о границе поставки, не техническое доказательство её достаточности.
**Мнение планера:** A допустим как ограниченный upstream-инструментальный этап, если аудитор признает границу пригодной
и wording не засчитывает BLOCKED ON за положительный proof. Для исходной SmallSort цели необходим последующий B-трек.
Недокументированные публично exclusions и admitted T1b/aggregate риски следует рассмотреть до заявления готовности.
Аудитор не обязан выбирать между A/B: возможны другая нарезка, дополнительный контроль или более узкая независимая поставка.

## 11. Побочные результаты и отдельные upstream треки

- [diffblue/cbmc#9487](https://github.com/diffblue/cbmc/pull/9487): bits2expr для array zero-width elements, кандидат `9f2d01ec`.
  Это отдельный CBMC fix; C1b всё ещё pinned на CBMC6.11.0 и не включает его как dependency.
- В [kani#5085](https://github.com/model-checking/kani/issues/5085#issuecomment-6863856826) опубликован результат replay:
  base CBMC abort134 на static/const ZST-array и Tail typed-copy, patched CBMC SUCCESS; controls SUCCESS на обоих.
  Coordinator-reported run `43497661683`; это свидетельство отдельного backend трека, не закрытие Part1 Gate B.
- [kani#5159](https://github.com/model-checking/kani/pull/5159): volatile ZST fix по #5072; ready for review по хронологии 14.11.
- B1: preserved checks на unresolved calls входит в историческую Part1 цепочку, но готовится и отдельный upstream PR.
  Актуальная подготовка — `6fe484b30` на upstream `0aac16ef6`, fork `fix/kani-uninit-unresolved-call-v3`;
  Kani CI [run 43516450125](https://github.com/Tiramisu-Cake/kani/actions/runs/43516450125): все regression jobs PASS, кроме macOS 15 Intel — CBMC timeout
  в несвязанном `cargo_autoharness_multichareq_searcher` (и после повторного запуска); тот же job так же падает на upstream `main`.
  При последующем переносе Part1 нужно учесть принятую upstream версию B1, не продублировать старый diff/слепо rebase.

## 12. Вопросы аудитору — по приоритету

1. Можно ли выпускать A как ограниченный вклад в #3300 при отсутствии legal SmallSort ON, и какая точная формулировка scope/готовности честна?
2. Достаточны ли named select/comparator boundaries, или именно positive ON replay должен быть release blocker Part1?
3. При B какая минимальная последовательность SEL1/comparator изменений даст useful legal+negative без необоснованного снятия checks?
4. Не мешает ли выпуску признанная возможность missed reads у nested by-value MU aggregates? Где проходит проверяемая граница admitted domain?
5. Приемлем ли откат широкого aggregate guard и known false-positive тест, или нужен иной узкий admission/диагностический механизм?
6. Достаточны ли A3 snapshot/pairing/return0 и A1 typed masks; каких Move/false/padding/stride counterexamples всё ещё не хватает?
7. Являются ли M1/E2 provenance/masks/reset seeds корректными в admitted whole-object domain; как честно оформить subrange/relocation ограничения?
8. Достаточен ли CC1 fail-closed analysis-cycle вместо SCC, и не распространяется ли новая граница нежелательно на обычные contracts?
9. Какие рекомендации R3 остаются обязательными до подачи: marker lookup, AArch64 gate, actual producer AB/BA, другие semantic edges?
10. Приемлем ли narrow T1b allowlist, если existing IDs/status/failures exact, но часть shared SUCCESS checks появляется/исчезает?
11. Что нужно доказать дополнительно, прежде чем считать mixed-root suite свидетельством isolation, а не regression observation?
12. Как уменьшить JSON tooling и 8.2k-line manifest без потери полных per-harness negative oracles и useful reachability checks?
13. Какие C1b path normalizations чрезмерны/недостаточны; достаточно ли Gate A для их практической устойчивости?
14. Как разделить 331-file export на reviewable upstream PR: masks/storage, calls/B1, immutable seeds, S3/CC и tests — с какими зависимостями?
15. Какие подтверждения Gate A/B или дополнительные source-to-property bindings требуются для решения, учитывая coordinator-reported evidence?

## 13. Навигация и пределы этого отчёта

- Основной предыдущий материал: [R3 brief](AUDIT-BRIEF-KANI3300-PART1-R3.md), [R3 audit](AUDIT-REPORT-KANI3300-PART1-R3-RU.md).
- Исправления первого/второго аудита: [первый отчёт](AUDIT-REPORT-KANI3300-RU.md), [R2](AUDIT-REPORT-KANI3300-PART1-R2-RU.md).
- Финальный gate package: [INPUTS](kani3300/final-gate/INPUTS.md), [Gate A request](kani3300/final-gate/FULL-GATE-REQUEST.md), [Gate B result](kani3300/final-gate/gateb-run4/RESULT.md).
- Frozen source: [C1](https://github.com/Tiramisu-Cake/kani/tree/1658f4cadfa83139e41180ce3865e23f79d889aa), [C1b](https://github.com/Tiramisu-Cake/kani/tree/3f2c12f46e9e32899e8d84e89c65cb6483ba685a).
- Исторические результаты выше не пересчитаны; private/raw logs и архивы при подготовке не читались, GitHub не опрашивался.
- Source identities/diff/docs сверены локально read-only. CI PASS/вердикты происходят из названных reports/сообщений, не новых запусков автора.
- Final binding/C1b preparation материалы (`final-gate/c1b-worker14/`, `m3-final/r4-cycle-binding-worker14/`) опубликованы вместе с этим отчётом.
- Готовность этого отчёта не означает выбранный вариант, разрешение на новые CI либо публикацию Part1 PR.

[k-runtime]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/library/kani_core/src/mem_init.rs
[k-layout]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs
[k-uninit]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/transform/check_uninit/mod.rs
[k-visitor]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs
[k-operand]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/codegen_cprover_gotoc/codegen/operand.rs
[k-delayed]: https://github.com/Tiramisu-Cake/kani/tree/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub
[k-points]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs
[k-immutable]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/codegen_cprover_gotoc/context/immutable_allocations.rs
[k-static]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/codegen_cprover_gotoc/codegen/static_var.rs
[k-anonymous]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/anonymous_allocations.rs
[k-contract]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs
[k-contract-doc]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/docs/src/reference/experimental/contracts.md
[r-u0]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/1f2cde2e9d3cde683411c81cc692f1a3aadb6d57/research/challenge-8/kani-k1/kani3300/u0/RESULT-KANI3300-U0.md
[r-u2]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/4ecdcc59308cbc36db6eb7ad8e12b13c755fc059/research/challenge-8/kani-k1/kani3300/u2/RESULT-KANI3300-U2.md
[r-cmp0]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/8f3893c7e7542c5e02a87ba98c0274a86c6bbd1c/research/challenge-8/kani-k1/kani3300/cmp0/DESIGN-COMPOUND.md
[r-cmp1]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/da8e4740864af90512d84eafd662157183be4bcd/research/challenge-8/kani-k1/kani3300/cmp1/RESULT-KANI3300-CMP1.md
[r-sel0]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/898fdb62943394e227c7f9b67deb313779be1d7d/research/challenge-8/kani-k1/kani3300/sel0/DESIGN-SELECT.md
