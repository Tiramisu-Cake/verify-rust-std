# Бриф для аудита: регрессия памяти `proof_for_contract` + `-Z uninit-checks` в Kani #3300 Part 1

12 ноября 2026, v2. Ресурсный трек приостановлен до независимого аудита; M3 HELD. Новые эксперименты не назначены.
Нужно мнение о корректном и практически проверяемом решении либо обоснованной границе поддержки. Варианты ниже не являются выбранным планом.

## Контекст и степень готовности

Part 1 (`model-checking/kani` #3300) добавляет проверку инициализации `MaybeUninit`-storage, включая flat-слоты `[MaybeUninit<T>;N]` / `[MaybeUninit<T>]`, и перенос shadow-состояния через вызовы. Практическая цель — SmallSort scratch; допустимая ширина поддержки контрактов остаётся вопросом этого аудита.
После аудита R2 (`AUDIT-REPORT-KANI3300-PART1-R2-RU.md` @ `124a45e373`) в цепочке реализованы:

- B1: сохранение проверок при неразрешённом вызове;
- M1: immutable-allocation masks, устраняющие ложный `raw_eq` FAIL на promoted RHS;
- M2-B/S3: восстановление пропущенных setters **левого операнда** в generated body **ordinary Assert** через трамплин регистрации контракта. Это другой механизм, не M1-дефект и не установленный PFC PASS.

Кандидат `4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c`: restricted Uninit Quick PASS, run `43257528539` (CI-only `fc3bccbfff` исключал `transfer-qualification/legal-pair` и `postcondition-hole`). **M3, полный regression gate и проверка тяжёлых PFC-входов не пройдены**; ресурсный блокер — предмет этого брифа, не заявление о полной готовности остального.
Материалы стадий: `kani3300/m2a/`, `m2br*/`, `m2bs3/`; R7-C tests `fe36afc4a8` переиспользуются. Source-only review/подготовленный тест не означает проверенный solver outcome.

## Симптом и метод измерения

Полные P1/P2: `kani3300/m2a/cases/scalar-pfc-{legal,hole}.rs`. Схема:

```rust
use std::mem::MaybeUninit;
#[inline(never)]
fn select(a: MaybeUninit<u8>, b: MaybeUninit<u8>, first: bool) -> MaybeUninit<u8> {
    if first { a } else { b }
}
#[kani::ensures(|result: &MaybeUninit<u8>| unsafe { result.assume_init_read() == 17 })]
fn postcondition_target() -> MaybeUninit<u8> {
    select(MaybeUninit::new(17), MaybeUninit::uninit(), true) // P2: false
}
#[kani::proof_for_contract(postcondition_target)]
fn postcondition_reads_initialized_return() { let _unread = postcondition_target(); }
```

P1 legal → SUCCESS; P2 → uninit FAILURE именно при payload-read в `ensures`, остальные legal/frame checks не должны ложно падать. Флаги `-Z uninit-checks -Z function-contracts`, CBMC 6.11.0, Ubuntu 24.04, runner 16 GB.
Числа ниже сообщены координатором, независимо здесь не перепроверялись. По одному input/root: build → codegen/inventory (`--show-properties`, `--count-eloc`) → normal Kani/CBMC под `/usr/bin/time -v`. Сторож RSS >6 GiB имеет sampling overshoot; kill-строки — цензурированные RSS, не завершённый peak.
`skip` означает исключение **только internal initializer body** из общей uninit-самоинструментации; runtime reset исполняется. `disable_checks(pointer)` сам этого не делал. Исключение initializer не сняло OOM.

## Измерения

Счётчики — P1; P2 обычно имеет тот же outcome, но не предполагаются одинаковые counters. RSS kill-строк — GiB. Исторические peaks ~1.4 GB / 1.95 GB сохранены с исходной подписью, без пересчёта неизвестных raw units.

| Вариант / run в `Tiramisu-Cake/kani` | symex steps | VCC до (после) упрощения | CNF / RSS / время | Исход |
|---|---|---|---|---|
| upstream `bf9c58e662`, `43253856019` | 4 908 | 222 (66) | 284883 vars / 17.07M clauses; conversion 2.96 с | FAILED: frame в store_argument, Unsupported raw pointers/unions |
| R1 `1cd96e354`, `43252928887` | 10 005 | 509 (120) | >6.3–6.8 GiB, 10–11 с | убит |
| A1 `613c188313` / A2R `b207847932` / A3R `a0a2386001` | 11–14k | 699 (186) – 948 (192) | >6.4–8.1 GiB | убиты |
| V01 `51fe0993de`, `43258912765`: demonic selection для return0 **вместо mandatory store** | 11 504 | 572 (168) | >6.5 GiB | убит |
| V02 `48d10f9ff2`, `43258921276`: компилятор R1 + весь `mem_init.rs` upstream | 11 396 | 536 (191) | 844029 vars / 51.22M clauses; conversion 8.46 с | FAILED, детали не получены |
| R4 A/B/C `75090c4986` / `2983edc2a0` / `8ebc167850`: private split / arithmetic / fallback | ~10k | 509–569 (120) | >6.31–6.62 GiB | убиты |
| R5-01 `bcc1a2af3f`, `43268005490`: U Hbuf + R1 Hcopy/GLUE | 11 639 | 476 (182) | 846480 vars / 51.22M clauses; conversion 8.5 с | solver достигнут, FAILED |
| R5-02 `899ffb5f26`, `43268011610`: R1 Hbuf + U Hcopy + R1 GLUE | 9 971 | 569 (120) | >6.68 GiB | убит |
| R6-01 `25197eb23e`, `43271948094`: R1 Hrepr + U selection/reset | 11 167 | 563 (162) | >6.46 GiB | убит |
| R6-02 `258d6af1ea`, `43271955539`: U Hrepr + R1 selection/Option-reset | 1 049 | 28 (19) | 0.8 с | **несопоставим**: ранний Enum Unsupported на Option-reset |
| R6-02b `405c1f0592`, `43276309576`: то же + bootstrap skip | 9 340 | 381 (115) | 829958 vars / 51.17M clauses; 50 с / 1.95 GB | FAILED: private buffer frame, *var_17 / *var_9 |
| R1+skip `56cbc5c4a4`, `43276317655` | 8 672 | 473 (96) | >6.71 GiB | убит |
| R7 B0 `c614dba9ca`, `43283061769`: текущая цепочка + skip | 11 700 | 841 (147) | >6.39 GiB | убит |
| R7 B1 `b4eb8294b7`, `43283068930`: отдельный 12-field snapshot + scalar private targets | 18 099 | 877 (147) | >7.24 GiB | убит |
| R8 source `2bd63183d8`, +tests `0ab62c7b0c`, `43296031667`: saved_base/saved_byte + snapshot/round-trip guards | 31 794 | 1534 (395) | >8.3 / >9.1 GiB (P1/P2) | убиты |

A1/A2R/A3R runs: `43252936014` / `43249040713` / `43249047207`; R4 A/B/C: `43263641666` / `43263648365` / `43263654098`.
Upstream ~46 с / ~1.4 GB относятся к прежнему run `43244395728`, не автоматически к `43253856019`. Варианты — **производные R1**, не все прямые потомки; R7/R8 основаны на поздней цепочке. Exact parents/trees/patches — в manifests стадий; source достижим через CI-ветки `uninit-ci/*` форка. Ни job success, ни отсутствие размера CNF при kill не устанавливают verification PASS/размер завершённой формулы.

## Что установлено и что пока является гипотезой

1. Onset есть уже в единственном commit R1 поверх upstream; A3/M1 для его воспроизведения не нужны. В R5/R6 следующий различающий интервал — Hbuf (capture/consume/representation), но это не изоляция одного дорогого терма.
2. Рост **17M→51M** уже есть в V02 при **одинаковом `mem_init.rs` upstream**: это эффект компиляторной дельты R1 на этих входах. V02≈R5-01; самостоятельный вклад `copy/bless` этим не показан, его нельзя объявлять причиной такого роста или исключать все взаимодействия.
3. R1 Hbuf сохранял source object/offset; **R7 хранит relative_offset/has_witness/value + protocol fields**, не абсолютный source ID. Основной object/offset witness остаётся и в дешёвом upstream/R6-02b. Общий признак «есть usize» не объясняет OOM.
4. R8 сложнее одного saved_address: сохраняет A3 snapshot, пару pointers и дополнительные guards; рост counters/kill не опровергает все pointer-архитектуры. R4/R7 уже показывают, что простой private split не является достаточным исправлением.
5. У дешёвых сравнений есть frame/Unsupported/изменённые obligations; у killed PFC-входов нет полного semantic verdict. Подтверждённого корректного и эффективного фикса пока нет.

## Недостающие факты и другие возможные причины

- Не сняты retained expression/type widths, actual `Layout<N>` instantiations и их owners: scalar input не означает, что все служебные N=1. Число VCC/размер GOTO не ограничивают encoding cost; огромный битвектор — лишь одна гипотеза.
- Возможны symbolic array read/update, byte-extract/update, арифметика и их multiplicity; DFCC write-set/object-size/backing views, snapshots/havoc; эффект slicing/alias precision или остаточной самоинструментации helpers после skip initializer. Нужна привязка к конкретному retained терму, а не только RSS.
- Не установлена полная цепочка marker→symbol→assigns→actual write/guard/SSA: в частности, pointer-field target должен обозначать **cell в private buffer**, не pointee/user allocation. Generic frameFAIL сам не связывает *var_N с нужным объектом.
- В [BV-коде CBMC 6.11](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/solvers/flattening/bv_pointers.cpp) `pointer_object/offset` извлекают pointer bits. «Перебор всех объектов этими примитивами» не установлен; цена может возникать в окружающем кодировании.

## Возможные направления и риски

Для полной поддержки важны snapshot **до Move**, false≠no-witness, normal-return0, signature/count/original-index/order pairing, typed masks/padding и живой destination. Старый source shadow нельзя перечитывать вместо snapshot. Настоящий user out-of-frame write должен остаться FAILURE; неподдержанный путь — явный pre-effect Unsupported, не vacuous SUCCESS.
**A–G — неполный список. Аудитор не обязан выбирать из A/B/C или других наших вариантов и может предложить собственное решение, включая принципиально другую архитектуру.**

A. **Узкий fail-closed:** guarded Unsupported для PFC + нужного shadow call-transfer; ordinary/Assert/storage пути предполагается сохранить. P1/P2 не доказывают отсутствие регрессии во всей guard-области. Риски: слишком широкий guard, влияние на другие contract/stub modes и реальный scratch call graph; это решение о scope, не уже установленная совместимость.

B. **Отдельный pointer buffer + корректная DFCC-private регистрация.** R6-02b даёт ориентир, но дешевизна после exemption и сохранение A3 не установлены. Нужны pre-Move false-value snapshot, корректный return/metadata lifetime и точные private targets; риски — потерять shadow state или скрыть user writes. Решение с одним pointer не тождественно проверенному R8.

C. **Найти дорогой терм и сохранить архитектуру.** Сопоставить ограниченные pre/post-DFCC/SSA projections, widths и conversion phases, затем менять конкретный encoding/выражение. Риски: непрозрачность pipeline, дорогие диагностики и оптимизация другого набора obligations вместо исходного дефекта; полный VCC/DIMACS dump пока не снимали.

D. **Заменить глобальный канал скрытыми ghost args/return либо caller-owned shadow temporaries.** Состояние передаётся явно/локально, без общего mutable buffer. Риски: согласование всех call sites/returns, generic/trait/indirect/foreign ABI, recursion и contracts; lifetime/false snapshot всё равно нужны, это существенно более крупный compiler patch.

E. **Убрать transfer buffer инлайнингом перед instrumentation или локальным proof по call-graph slice.** Риски: recursion/непрямые вызовы, code explosion, Move/reset после преобразования и потеря modular-contract coverage. Ограничение графа требует честной границы для непокрытых вызовов.

F. **Другая shadow-модель:** SSA init-tags/передача масок вместе со значениями или per-allocation byte masks вместо одного nondet witness. Риски: alias/partial-write/padding/return soundness, размер массивов и новая стоимость solver; initializedness нельзя восстановить из одних value bits, перенос через вызов не исчезает автоматически.

G. **Другая граница DFCC/CBMC либо сдаваемого scope.** Точная маркировка synthetic shadow writes/auxiliary state вместо их обычного frame-кодирования, либо оптимизация CBMC arrays/byte-ops/slicing; риск скрыть реальные эффекты, затронуть другие режимы или лишь перенести стоимость. Отдельная возможность — storage-only/подтверждённые call forms с guard остальных или opt-in contract profile; риск разорвать нужные scratch constructor/return paths. Ни одно направление здесь не выбрано.

## Вопросы аудитору

1. Какие причинные выводы поддерживает таблица, а где changed paths/frame/Unsupported или неполные данные мешают сравнению?
2. Какое решение вы предложили бы сами, независимо от A–G? Какие обязательства и стоимость оно сохраняет/меняет?
3. Если оправдан scope cut: какая минимальная граница сохраняет цель Part 1, где нужен guard и какие сценарии доказывают отсутствие скрытого regression/пропуска проверок?
4. Для pointer/ghost/private-state решения: как сохранить pre-Move false snapshot, return и user-frame проверки; какие конкретные source/GOTO bindings и controls нужны?
5. Если нужен разбор encoding: какие минимальные bounded данные/профили/точки CBMC 6.11 различат hypotheses, прежде чем собирать большие формулы?
6. Какой минимальный semantic/resource/regression gate нужен перед подачей с учётом непройденного M3/full gate и restricted Quick?
