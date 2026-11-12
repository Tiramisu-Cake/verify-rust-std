# Kani #3300 Part 1 — отчёт для независимого аудитора, раунд 3

**Срез: 13 ноября 2026.** Отчёт рассчитан на знакомство с проектом с нуля. Это верификация корректности, не security-работа.

**Текущее решение владельца: реализация scope cut приостановлена до вашего ответа. На сужении scope мы не настаиваем.**
Нужна оценка корректности, практической границы Part 1 и дальнейшего пути: локальное исправление, дополнительная диагностика, иной дизайн или ограничение поддержки. G-SC — невыданный implementation draft; worker15 не начинает кодирование. G-SC-C worker14 — только инвентарь SmallSort roots/флагов/call effects, без кода. Новых сборок, solver runs или публикаций этим отчётом не запрашиваем.

## 1. Цель и связь с SmallSort

[Kani #3300 — Automatically Verify Memory Initialization](https://github.com/model-checking/kani/issues/3300) — широкий tracking issue об автоматических проверках чтения неинициализированной памяти, включая raw pointers, padding, unions и delayed UB. Наш **Part 1** — часть инструментальной поддержки Kani, а не полное решение #3300 и не завершённое доказательство SmallSort.

SmallSort использует временную scratch-память: flat `[MaybeUninit<T>; N]`/срез слотов, а также `MaybeUninit<[T; N]>` с raw/slice views. Законно читать только записанный префикс; хвост может оставаться неинициализированным. Хотим, чтобы Kani с `-Z uninit-checks` принимал такие legal paths и отклонял настоящий unwritten-byte read, сохраняя bytewise copy и корректные typed transfers.

Основной желаемый объём: поддержанные direct-MU и flat-slot layouts, записи/reset/копии, MU↔T conversions в разрешённых направлениях, обычные by-value arguments/returns, включая перенос false shadow. Не заявляем произвольные T/N, все union pointees/compound layouts, все foreign/realloc effects, полную Rust alias/move семантику или invalid-value verification.

Контракты полезны для модульных доказательств helpers и composition. Поэтому «обычный uninit-off SmallSort CI не пострадал» недостаточно для утверждения, что сохранена будущая цель PFC+uninit scratch verification. Владелец ранее выбрал сохранение flat-slot scope; отказ от raw_eq checks с оговоркой не принят как решение его зависимостей.

## 2. Ревизии и правила чтения свидетельств

| Ревизия | Роль |
|---|---|
| `bf9c58e662fd65c64381ef2ac97a6397ffc0693a` | upstream Kani base использованного исследования |
| `1cd96e354ec45346b61c245554a50a8af8cb5ce7` (R1) | первый Part 1, один commit поверх base; ранний runtime/protocol |
| `a0a2386001a15fecfe2facc2f6cd87f3dee13b60` | A1–A3R после первого аудита, до интеграции B1/M1/S3 |
| **`4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c`**, tree `af28e22ec446b254cfa3a28b2882eafa58d5a458` | нынешний семантический кандидат, к которому относятся вопросы о выпуске |
| `15276d57238f4a70b2ea5fca9141ef047cce120c` в verify-rust-std | D1-A исследовательские результаты, не Kani source-кандидат |

Kani source доступен в нашем [форке](https://github.com/Tiramisu-Cake/kani/tree/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c); research-ссылки ниже относительны каталогу этого отчёта. R7/R8 — диагностические кандидаты, **не** принятые изменения в4f64. Нельзя импортировать их source при переносе отдельных controls.

Все новые прогоны выполнял координатор в fork Actions. Здесь систематизированы его результаты и проверки прежних аудиторов; при подготовке отчёта Kani/CBMC/Miri не запускались. Ссылки на run позволяют проверить точный checkout/состав, а не присваивают независимую proof credit.
Ранние RESULT/manifest с READY/NOT_RUN часто написаны **до** последующего CI. Ниже поздние сообщения координатора выделены как такие; старые файлы не переписаны задним числом. Suite PASS у expected-negative означает совпадение oracle, не SUCCESS программы; один FAILED не исключает лишних failures.

## 3. Архитектура uninit-checks — что именно меняется

**Один символический свидетель.** Вместо полной shadow-map всех байтов runtime хранит nondet `(object_id, byte_offset)` и Boolean initializedness выбранного байта. Reset выбирает объект/смещение, `value=false`. `get` проверяет совпадение объекта/диапазона и нужность байта по layout mask; вне выбранного диапазона возвращает true. Это абстракция выбора любого плохого байта, а не разрешение считать произвольную память инициализированной. Пропущенный setter для legal объекта даёт false positive; произвольное bless может скрыть настоящий false.
Код: [state/get/set/reset](https://github.com/Tiramisu-Cake/kani/blob/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/library/kani_core/src/mem_init.rs#L33).

**Layout и перенос.** Полный rustc storage extent нужен для адресации и bytewise copy. Typed MU transfer использует data mask payload T, повторённую по rustc stride; padding, который этот typed transfer не обязан сохранять, не должен становиться инициализированным. При MU transfer false data byte остаётся false. Обычный union-value путь имеет отдельную whole-storage mask; правило D(T) не следует автоматически переносить на него или новые compound forms. Typed read игнорирует padding по своей маске, а полный byte read/raw_eq должен проверять его как байты. `Some(0)` в allocation mask — инициализированный ноль, `None` — hole, даже если backend материализует нулевые bits.
Код: [ty_layout.rs](https://github.com/Tiramisu-Cake/kani/blob/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs), [runtime copy/transfer](https://github.com/Tiramisu-Cake/kani/blob/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/library/kani_core/src/mem_init.rs#L125).

**Локальная и delayed instrumentation.** Локальный проход обнаруживает raw/union operations, reads/writes и call effects. Delayed UB анализирует targets/points-to/relevance и добавляет проверки/обновления также в обычные typed operations, через которые ранее созданное неинициализированное значение может дойти до чтения. Это важно для materialized temporaries и contract-generated bodies. Разрешить операцию на локальном уровне недостаточно, если global analysis не видит её фактический путь.
Код: [ptr_uninit](https://github.com/Tiramisu-Cake/kani/tree/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit), [delayed_ub](https://github.com/Tiramisu-Cake/kani/tree/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub), [points_to](https://github.com/Tiramisu-Cake/kani/tree/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/kani-compiler/src/kani_middle/points_to).

**Argument/return protocol A3.** На живом source caller снимает snapshot witness membership/relative offset/value для shadow-carrying аргументов; все snapshots предшествуют reset in-place Call(Move). Pairing проверяет signature/count/original indices/order/layout. Callee entry принимает состояние; return передаётся обязательным slot0, caller загружает его только на normal edge в живой destination. False ≠ отсутствие witness; нельзя перечитать умерший source вместо snapshot. Обычный поддержанный путь — bodyful nonforeign `InstanceKind::Item`; другие shadow call forms требуют явной квалификации/Unsupported.
Код: [visitor](https://github.com/Tiramisu-Cake/kani/blob/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L694), [protocol runtime](https://github.com/Tiramisu-Cake/kani/blob/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/library/kani_core/src/mem_init.rs#L425).

**M1 immutable allocations.** Registry связывает actual anonymous/promoted allocation с emitted symbol и byte mask, допускает квалифицированные immutable объекты и ставит seeds после normal reset completion. Нельзя благословить весь referent по типу ссылки: holes и padding должны оставаться false, alias/offset/overwrite/reuse требуют согласованной модели.
Код: [immutable_allocations.rs](https://github.com/Tiramisu-Cake/kani/blob/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/kani-compiler/src/codegen_cprover_gotoc/context/immutable_allocations.rs), [admission predicate](https://github.com/Tiramisu-Cake/kani/blob/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/kani-compiler/src/kani_middle/transform/check_uninit/mod.rs#L909).

**Контракты/DFCC.** Kani выбирает Original, Assert, SimpleCheck, RecursiveCheck и Replace. PFC проверяет тело контракта; stub_verified использует replacement, это другая семантика. CBMC DFCC проверяет user modifies/frame. Shadow runtime пишет auxiliary state, поэтому codegen добавляет маркированный `MEM_INIT_STATE` в assigns. Это не разрешение менять пользовательские pointees. Whole-state permission, фактические cell targets и shadow semantics replacement нужно проверять отдельно.
Код: [mode selection](https://github.com/Tiramisu-Cake/kani/blob/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/kani-compiler/src/kani_middle/transform/contracts.rs#L565), [private assigns](https://github.com/Tiramisu-Cake/kani/blob/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs#L142), [in-place DFCC driver](https://github.com/Tiramisu-Cake/kani/blob/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/kani-driver/src/call_goto_instrument.rs#L172).

## 4. Сделано после первого аудита: семантическая цепочка и CI

| Стадия / source | Изменение | Свидетельство и предел |
|---|---|---|
| R1 `1cd96e354` | MU storage/flat slots/calls | Старый run43027843249 имел успешные Ubuntu regression jobs, но последующий аудит нашёл padding P0. Старый CI не устанавливает корректность модели. |
| A1 `613c188313` (production `fc37f9021`) | Разделены storage extent и typed D(T), stride, false data | [43105165870](https://github.com/Tiramisu-Cake/kani/actions/runs/43105165870): expected85/0,2ignored. Те же новые tests на R1: [43105207965](https://github.com/Tiramisu-Cake/kani/actions/runs/43105207965)81/4; четыре padding negatives ошибочно SUCCESS на старом коде. |
| A2 `3dc0227cee` | Pat сохраняет offset; nested enum masks сравниваются локально и сдвигаются один раз | [43107071880](https://github.com/Tiramisu-Cake/kani/actions/runs/43107071880): общий gate упал из-за blanket raw_eq Unsupported (4 selectors). Layout fix не означает общий PASS. |
| A2R `b207847932`, A2R2 `585c93b2ff` | Full-range raw_eq обоих operands, затем AddressOf(*ref) перед byte-array CheckAs | [43111242922](https://github.com/Tiramisu-Cake/kani/actions/runs/43111242922), [43117585146](https://github.com/Tiramisu-Cake/kani/actions/runs/43117585146):90/1,2ignored; два false FAIL в одном legal fixture остались. |
| A3 `0b1d68ac69`, A3R `a0a2386001` | Pairing/snapshot/mandatory return0; ремонт private integer_max dependency/custom-MIR fixture | До ремонта [43116356531](https://github.com/Tiramisu-Cake/kani/actions/runs/43116356531):64/30. После [43118703581](https://github.com/Tiramisu-Cake/kani/actions/runs/43118703581):93/1,2ignored; единственный selector FAIL — raw_eq legal. |
| B1I production `cdb439b0a4`, tip `dc5f5a4067` | Сохранены накопленные checks/entry loads/Unsupported при resolver Err; один operand walk/flush; fallible seed resolver и no-body points-to guard | [43196180814](https://github.com/Tiramisu-Cake/kani/actions/runs/43196180814): expected111/7,2ignored; шесть новых fixtures неверно привязаны, плюс известный raw_eq legal. Существующие controls прошли. |
| B1I-A `6134e42dd1` | Только исправление fixture attribution: FnPtr/tuple/Item вместо вымышленного shim path | Позднее сообщение координатора: [43199156872](https://github.com/Tiramisu-Cake/kani/actions/runs/43199156872), CI`fcba2fe768`:fmt/build/clippy PASS; kani22/0, expected119/1,2ignored, ui14/0, script1/0. Единственный FAIL — D0 raw_eq. Это не proof всех shim forms. |
| M1 production `254ae69662`, tip `5abdcf982d` | Immutable allocation masks/symbol binding/reset-completion seeds | [43222702257](https://github.com/Tiramisu-Cake/kani/actions/runs/43222702257):unit5/0, kani22/0, expected130/0,2ignored, ui14/0, script1/0. D0 legal теперь PASS, прежние goldens не смягчены. |
| M1 + repaired mixed tests `83ceadf048` | Дискриминирующие stack/promoted mixed operands, обе стороны/holes | По координатору [43230532195](https://github.com/Tiramisu-Cake/kani/actions/runs/43230532195):expected138/0,2ignored, unit5/0 и остальные Quick suites PASS. Те же tests на B1I-A [43230538511](https://github.com/Tiramisu-Cake/kani/actions/runs/43230538511):127/7 (6 legal false FAIL + D0), holes совпали с negative oracle. |
| M2 `5f7f2b7364` | Test-only transfer qualification: ordinary/PFC/ensures/out/abort | Quick43229982767 дважды прерван shutdown runner; это не acceptance. Точечные probes нашли новый Assert false positive и PFC resource gate. |
| M2-B/S3 `58497d98d0`, test-only repair `4f64cc617c` | Delayed analysis следует contract registration trampoline; два const-HOLE fixtures исправлены после E0515 | [43255336861](https://github.com/Tiramisu-Cake/kani/actions/runs/43255336861):133/2 из-за двух fixture compile errors. Затем restricted Quick [43257528539](https://github.com/Tiramisu-Cake/kani/actions/runs/43257528539), CI`fc3bccbfff`:unit5/0,kani22/0,expected135/0,2ignored,ui14/0,script1/0. |

Последний restricted Quick **удалял из CI-дерева** `transfer-qualification/legal-pair` и `postcondition-hole` из-за ресурса. PFC acceptance, M3 и полный regression gate не пройдены. Аудит ресурса проверил checkout/исключения и результаты; более ранние stage files со словами «PREPARED/UNVERIFIED» не отменяют поздний ограниченный CI, но и не превращаются в full PASS.
Research: [A1](kani3300/a1/), [A2/A2R/A2R2](kani3300/a2r2/), [A3R](kani3300/a3r/), [B1I](kani3300/b1i/), [B1I-A](kani3300/b1ia/), [M1](kani3300/m1/), [C1-T2-A](kani3300/c1t2a/), [M2](kani3300/m2/), [S3](kani3300/m2bs3/).

Минимальные формы исходных семантических findings:

- **A1 padding:** `#[repr(C)] { tag:u8, value:u32 }`, extent/stride8, data offsets0,4–7, padding1–3. После заполнения физических байтов raw copy сохраняет initialized padding; typed MU assignment/argument/return не должны гарантировать этот padding. Чтение его как u8 после typed transfer — negative. Дополнительно проверены false data и slot1 массива со stride8. На старой модели четыре таких negative давали ложный SUCCESS.
- **A2 offsets:** Pat wrapper/enum внутри поля с ненулевым outer offset; variant masks надо сравнить в enum-local координатах и прибавить outer offset один раз. Исправление не добавляет поддержку разных padding masks/niches. Это layout-композиция, отдельная от последующего raw_eq false positive.
- **A3 pairing:** несколько MU аргументов с обычными аргументами между ними, одинаковые signatures/sizes в повторных/nested вызовах и MU return без MU args. Нельзя принять stale buffer или превратить выбранный false в initialized fallback из-за несовпавшего call/index. Current-call protocol и mandatory return0 закрывают именно этот класс; исходный helper `.max(1)` вызвал отдельный tool Unsupported и был удалён ремонтом.
- **B1 lost operations:** `visit_terminator` уже накопил operand reads/entry loads, затем resolution Err положил Unsupported и вернулся до общего flush. Plain case без delayed seeds терял защиту; seeded case не доказывал исправность локального pass. B1I исправляет один обход/один flush и согласует resolver/points-to. Шесть первых «shim» fixtures фактически были FnPtr, tuple-layout Unsupported или обычным Item с настоящим UB; B1I-A исправил привязки, не объявил их доказательством новых shim semantics.

## 5. Блокер raw_eq: диагностика D0 и принятая модель M1

Минимальный legal shape: записать четыре байта `MaybeUninit<[u8;4]>`, затем `assert_eq!(slot.assume_init(), [1,2,3,4])`. Есть второй legal root с partial raw copy и отдельным законным array equality. В обоих `.safety_check.2` в `SpecArrayEq` ложно падал, `.1` проходил. Сама формулировка diagnostic type не показывала, какой объект не получил shadow.

Попытки: A2 blanket Unsupported ломал штатные сравнения; A2R full-byte checks восстановили часть регрессий; A2R2 исправил synthetic reference-storage read, но false FAIL остался. Откат raw_eq был предложен как совместимость и отклонён аудитом R2: flat-slot copy теперь допускается, тогда как base её отвергал, поэтому можно открыть **новый** unchecked byte-read path. Тип ссылки не заменяет provenance диапазона.

D0-P/D0-PR, run[43209338134](https://github.com/Tiramisu-Cake/kani/actions/runs/43209338134), D0-A research`ff5cabbfca`: candidate A/B/AB/BA/D и baseline A/B/pair воспроизвели тот же FAIL, включая singleton. Порядок/shared cache **не определял именно этот сбой**. Codegen/layout/serde diagnostic infrastructure потребовала двух ремонтов; curator упёрся в caps.

D0-A установил: `.2` — **правый promoted immutable operand** (A:AllocId9,[1,2,3,4]; B:AllocId5,[9;4]), offset0/extent4/все байты Some. Его runtime shadow стартовал false и не менялся. Левый assume_init temporary получал нормальный SetRef и был true: пропущенного setter/ошибочного адреса слева здесь не было. MemLoc/constant seeds распознавали Stack/Heap/Static, но не anonymous allocations. Все12 CBMC captures были capped64MiB; четыре полных фрагмента цели восстановлены, без претензии на полноту остальных trace.

M0→M1: immutable provenance/mask registry, seeding после reset normal edge, сохранение Some(0)/None и typed masks. Unit5 и immutable-masks4 различают модель. Первые6 `promoted_*` tests проходили **и до M1**, поэтому не доказали исправление D0. C1-T2 добавил смешанные origins; первые4 MU tests упёрлись до raw_eq во внешний `MaybeUninit<[MaybeUninit<u8>;3]>`. Их переписали в поддержанный flat stack layout (C1-T2-A), после чего matched baseline/M1 показал6 legal fixes и сохранение двух promoted-hole negatives.

Это целевое подтверждение модели, не полная provenance/alias/offset/overwrite/full-composition proof. Неподдержанный nested MU-of-flat не был добавлен в scope. Полное raw_eq покрытие на финальном export остаётся частью M3/gates. Источники: [D0-A](kani3300/d0a/), [M0](kani3300/m0/), [M1](kani3300/m1/), [C1-T2-A](kani3300/c1t2a/).

## 6. Другой false positive: ordinary contract Assert, исправление S3

M2-A probe разделил обычный вызов и PFC. На M1 C03 ordinary-singleton с contract Assert падал на `[u8;3]` примерно за4s/238MB; C04 с `--no-assert-contracts` и C05/C06 без attributes проходили. На B1I-A все четыре ложно падали ещё из-за D0. Это не означало, что M1 исправил все generated contract bodies.

Probes: M1+M2[43243491671](https://github.com/Tiramisu-Cake/kani/actions/runs/43243491671), B1I-A[43244391200](https://github.com/Tiramisu-Cake/kani/actions/runs/43244391200), upstream[43244395728](https://github.com/Tiramisu-Cake/kani/actions/runs/43244395728). S3 trace[43252039413](https://github.com/Tiramisu-Cake/kani/actions/runs/43252039413) показал **левый** operand body equality, object50 byte2: last reset=false, matching setter нет; RHS immutable object20 seed исправен. Это generated ordinary Assert body; ensures ещё не достигнут, PFC PASS не установлен.

S1 (`35fab624af`) остановился без source fix: не хватало operand/object binding. S2 (`d2500db20b`), по probes43248579074/43249480111, установил left `.1` FAILURE/right `.2` SUCCESS и уже имеющийся RHS seed; trace имел340 SUCCESS/1 FAILURE/11 UNREACHABLE, но не counterexample history. Поэтому S2 тоже остался documentation-only, а не неудачным speculative seed repair. Только S3 получил witness/last-transition binding.

Причина: delayed alias analysis шёл по исходному registration body/panic, codegen использовал closure-calling trampoline. Финальный S3 заставляет analysis следовать телу регистрации, которое реально используется, и восстанавливает существующие typed setters. Seeds/DFCC/ABI не переписаны. Две ensures-hole проверки после const-HOLE compile repair прошли intended negative oracle в restricted Quick43257528539; C03 там PASS. Циклические clause/helper paths и общий semantic/resource/full gate всё ещё требуют квалификации. [S1](kani3300/m2bs/), [S2](kani3300/m2bs2/), [S3](kani3300/m2bs3/).

## 7. Главный открытый блокер: PFC + uninit resource

P1/P2 — маленькие scalar inputs, **не сортировка большого массива**. Полные frozen files: [legal](kani3300/m2a/cases/scalar-pfc-legal.rs), [hole](kani3300/m2a/cases/scalar-pfc-hole.rs). Схема P1:

```rust
use std::mem::MaybeUninit;
#[inline(never)]
fn select(a: MaybeUninit<u8>, b: MaybeUninit<u8>, first: bool) -> MaybeUninit<u8> {
    if first { a } else { b }
}
#[kani::ensures(|r: &MaybeUninit<u8>| unsafe { r.assume_init_read() == 17 })]
fn target() -> MaybeUninit<u8> {
    select(MaybeUninit::new(17), MaybeUninit::uninit(), true) // P2: false
}
#[kani::proof_for_contract(target)]
fn check() { let _unread = target(); }
```

P1 ожидает SUCCESS; P2 — intended payload-read uninit FAILURE в ensures, без лишнего frame/protocol/Unsupported. Frozen hashes P1`fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b`, P2`61fc369a6830c6ff185887b04db36139ca529e4de097c0025ce7b29c8323f759`. Source в исследовании не меняли ради covers. Запуск: singleton Kani, edition2021, `-Z uninit-checks -Z function-contracts`; actual expanded backend argv/версии определяются receipts, не этим сокращённым примером.

Первый memprobe[43232249168](https://github.com/Tiramisu-Cake/kani/actions/runs/43232249168) на16GB runner: legal-pair14:16min/maxrss≈15.07GB в прежней подписи, оба roots false FAIL; postcondition-hole убил runner. Затем roots разнесли, поставили300s и watchdog6291456KiB=6GiB. Выяснилось: Ordinary Assert false FAIL — S3, **PFC OOM возник до M1**, уже в R1.

### 7.1. Все основные ресурсные различающие попытки

Счётчики ниже P1, VCC **до→после simplification**. Указан один run/case; P2 аналогичный outcome только там, где он действительно запускался. Символ KILL означает watchdog/незавершённую Boolean conversion, не semantic FAIL. Варианты — производные R1, не все прямые потомки; R7/R8 основаны на поздней цепочке. Источники exact patches/trees: [R2](kani3300/m2br2/), [R3](kani3300/m2br3/), [R4](kani3300/m2br4/), [R5](kani3300/m2br5/), [R6](kani3300/m2br6/), [R6b](kani3300/m2br6b/), [R7](kani3300/m2br7/), [R8](kani3300/m2br8/).

| Попытка / source / run | Что меняли или сравнивали | Steps; VCC; результат |
|---|---|---|
| upstream`bf9c58e662`,43253856019 | Тот же scalar input | 4908;222→66;284883vars/17072414clauses;ConvertSSA2.96s. FAILED frame/Unsupported, не correct baseline. |
| R1`1cd96e354`,43252928887 | Первый single commit Part1 | 10005;509→120;KILL~11s,maxrss6789236KiB. Onset уже здесь. |
| A1`613c188313`,43252936014 | Проверка до A3/M1 | 11348;699→186;KILL. |
| A2R`b207847932`,43249040713; A3R`a0a2386001`,43249047207 | Проверка вклада A3 | A2R11348/699→186;A3R14420/948→192;обаKILL. A3 не необходим для onset. |
| R3 V01`51fe0993de`,43258912765 | **Demonic return selection вместо mandatory0**, диагностическое ослабление | 11504;572→168;KILL. Не исправление, в export не принято. |
| R3 V02`48d10f9ff2`,43258921276 | Compiler R1 + весь mem_init.rs upstream | 11396;536→191;844029vars/51222776clauses;Convert8.46s;solver достигнут, FAILED tail обрезан. |
| R4-A`75090c4986`,43263641666 | Отдельный buffer/private split | 9949;512→120;KILL. |
| R4-B`2983edc2a0`,43263648365 | Порядок usize arithmetic | 9975;569→120;KILL. |
| R4-C`8ebc167850`,43263654098 | Single-element copy fallback | 10101;509→120;KILL. Не изолирован весь copy semantics. |
| R5-01`bcc1a2af3f`,43268005490 | Upstream Hbuf + R1 Hcopy/GLUE | 11639;476→182;846480vars/51218835clauses;Convert8.5s;solver достигнут, FAILED. |
| R5-02`899ffb5f26`,43268011610 | R1 Hbuf + upstream Hcopy + R1 GLUE | 9971;569→120;KILL. Различающий интервал — Hbuf, не один term. |
| R6-01`25197eb23e`,43271948094 | R1 Hrepr + upstream selection/reset | 11167;563→162;KILL. |
| R6-02`258d6af1ea`,43271955539 | Upstream pointer Option-buffer + R1 selection/reset | 1049;28→19;0.8s;ранний Enum Unsupported от самоинструментации Option-reset. NON_COMPARABLE, не relief. |
| R6-02b`405c1f0592`,43276309576 | Тот же pointer-buffer + exact initializer identity исключён из uninit self-instrumentation | 9340;381→115;829958vars/51173785clauses;49.83s,maxrss1949040KiB=1.859GiB;frameFAIL var17/var9. |
| R1+same-skip`56cbc5c4a4`,43276317655 | Тот же bootstrap exclusion, runtime R1 | 8672;473→96;KILL~9.73s,maxrss6717020KiB. Сам skip недостаточен. |
| R7 B0`c614dba9ca`,43283061769 | Поздняя4f64 chain + bootstrap control | 11700;841→147;P1/P2 KILL. |
| R7 B1`b4eb8294b7`,43283068930 | Separate12-field snapshot + scalar private targets | 18099;877→147;P1/P2 KILL,P1maxrss7247504KiB=6.912GiB. Split не помог. |
| R8source`2bd63183d8`+tests`0ab62c7b0c`,43296031667 | saved_base/saved_byte вместо numeric relative, snapshots/protocol/round-trip guards | 31794;1534→395;P1/P2 KILL,maxrss8313556/9065144KiB=7.928/8.645GiB. |

R7 уже хранит **relative_offset/has_witness/value**, не R1 absolute source object ID. R8 — два pointer carriers плюс сохранённые snapshot/protocol и guards, не опыт «один простой pointer». Поэтому нельзя заключить, что всякая pointer architecture невозможна, или что одинаковое наличие usize объясняет все KILL.

### 7.2. Что эти попытки дали и чего не дали

Upstream и V02 имеют один mem_init.rs blob`37b9da8d674afb814f5024a20b77350ad5f82fd8`; рост17M→51M clauses уже даёт **compiler delta R1** на этом runtime. V02≈R5-01 не устанавливает вклад runtime copy/bless в этот рост. R6b кодирует≈51M при1.859GiB, поэтому число clauses само не причина OOM остальных вариантов.

Hbuf-bisect локализовал различие capture/consume/representation, но дешёвые версии имеют frameFAIL, Unsupported или иные obligations. Даже после достижения solver они не доказывают semantic equivalence. `pointer_object/offset` в BV CBMC извлекают bits, а не сами перечисляют все объекты; дорогой term может находиться в окружающем array/byte/DFCC/postprocessing кодировании.

**Единицы исправлены:** Linux RSS/maxrss здесь KiB; GiB=KiB/1048576. Старые подписи части таблиц ошибочно делили на1e6 и писали GiB. Исторический upstream46.14s/maxrss1405024KiB=1.340GiB относится к43244395728, не автоматически к новому inventory43253856019. Watchdog samples и time-v maxrss различны; overshoot2s poll не ранжирует стоимость завершённых proofs. У killed runs нет окончательного CNF/peak результата.

Старый diagnostic workflow выводил `grep|head -30`, не сохранял artifacts в проверенных runs и мог быть green после kill. Полные failure tails ряда вариантов потеряны, их нельзя восстановить из соседнего run. Это ограничивает причинные выводы; проблема не распространяется автоматически на restricted Quick с другим накоплением rc.

## 8. D1: штатная диагностика A+B-lite и её итог

По рекомендации PFC-resource аудитора прекратили перебор carriers. D1-P подготовил bounded capture actual pre-DFCC/post-DFCC/CBMC input, argv/tool hashes, process-group limits/rawKiB и stock `--program-only`; **без патча CBMC, SAT или normal verification**.

Run[43314208878](https://github.com/Tiramisu-Cake/kani/actions/runs/43314208878), attempt1. D1-P research`cedd1a7b5fd99c27baf9d9c07180ecaea5b92b97`; trigger`8a4664fe1d3587c8ce17790ac2d818cdb169cd25`; CI R1`1d0f1d30bfcf8ce64d63716a31a0a9bd3e06c7a0`, R6`86f9b171513de7a11eec7587bead1edc6877d950`. Exact parents: R1+skip56cbc5c4a4, R6-02b405c1f0592. Только P1 captured; P2 source сохранён, не исполнялся.

D1-A @15276d5723 проверил129/129 manifest files по bytes/SHA256 **на каждом pin**. Три model stages действительно различены: непосредственный post-DFCC не равен последующему actual CBMC input. Все invocation receipts полные; но Kani frontend rc101 из-за diagnostic stdout/parser incompatibility, top-level capture=failure/upload=PENDING. Локальная целостность переданных bundles не доказывает remote upload completion. Failure inventory NOT_RUN/UNKNOWN, proof credit0.

| Symex-only / printed census | R1+skip | R6-02b |
|---|---:|---:|
| CBMC elapsed / wait4 maxrss KiB | 0.930s /36556 | 0.886s /39364 |
| stdout bytes / dropped | 1656636 /0 | 1886396 /0 |
| printed all / ignored / retained expression records | 5280 /4213 /1067 | 5865 /4588 /1277 |
| отдельно guards | 2039 | 1961 |
| ASSERT / ASSUME | 96 /33 | 115 /41 |
| byte-extract/update all, retained | 4/1,0/0 | 9/1,0/0 |
| WITH updates retained | 0 | 13 |

Исходный parser остановился на character-work budget200000 и дал только prefix. D1-A пересчитал весь сохранённый printed stream; это не full typed SSA/converter workload. Boolean root width1 не означает узкий operand. Occurrences/fingerprints не unique IREP DAG/cache misses; categories/auxiliary expressions, не печатаемые штатным view, не восстановлены. Сам dump/symex exit0 не verification PASS.

Три конкретные локализованные цепочки (полные координаты/хэши в [MODEL-MAP](kani3300/d1a/MODEL-MAP.md), [ATTRIBUTION](kani3300/d1a/ATTRIBUTION.md)):

1. R1 `store_argument` пишет saved_object_id на GOTO PC639; retained merge equality SSA2016/PC664 имеет поле64bit и POINTER_OBJECT двух sources. PC664 — phi/DEAD boundary, **не исходная запись**. State56B не означает448bit operand каждого field read. Цена conversion неизвестна.
2. R6 buffer cell32B: DFCC check PC628 → ASSERT629 → write631; load-side var17 check околоPC559 — другой узел. Private cell address/extent не pointee saved pointer. Это новый binding frame obligation, не новый frameFAIL verdict: SAT не запускался.
3. R6 DFCC allocated set: PC1947/SSA722, retained `ARRAY_OF(NULL) WITH [...]`;13 WITH updates. При object_bits16 capacity65536 pointers ×8B=524288B/4194304bits — **type/source-derived capacity**, не measured flattened width/allocations. Большой backing есть у исторически дешёвого контраста, поэтому это не объяснение OOM R1.

Выбранные Layout0/1 соответствуют zero guard и one-byte payload mask; Layout1 — один Boolean элемент, storage1B. R1 state56B, R6 tracked24B+buffer32B — storage facts, не полный converter profile. R6 load содержит abort-on-assume(false) paths; оба symex streams предупреждают `saturating_add/sub: not enough arguments, inserting nondeterministic value`. Их влияние на faithful model/path comparison не установлено.

**Итог D1: offender не найден.** Нет exact operand-width/owner для всех terms, unique DAG/cache/allocations, inclusive/exclusive conversion deltas и postponed array/pointer attribution. Видимые byte ops sliced не исключают hidden converter rewrites. Никакая local optimization или scope cut из D1 не реализована. Отдельный capped converter profile C потребовал бы патч/сборку CBMC и сейчас не разрешён. [D1 evidence set](kani3300/d1a/).

## 9. Аудиты: что принято и что остаётся открытым

| Аудит | Findings / принятый ответ |
|---|---|
| Первый @dff05db0c8, [отчёт](AUDIT-REPORT-KANI3300-RU.md) | Приняты P0 typed padding, pairing и проверка фактического moved-from MIR, P1 Pat/enum offsets. Последовали A1–A3R с указанными controls. Старый CI не считали опровержением findings. |
| R2 @124a45e373, [отчёт](AUDIT-REPORT-KANI3300-PART1-R2-RU.md) | Принято: raw_eq rollback открывает новые unchecked flat-slot paths; B1 нужен внутри Part1; временный left/promoted диагноз надо уточнить D0; source READY не full gate. Flat scope сохранён, B1I интегрирован, D0→M1 и S3 устранили целевые false positives. Общие gates/provenance/Replace/frames/alias/recursion не объявлены закрытыми. |
| PFC-resource @ab75098224, [отчёт](AUDIT-REPORT-KANI3300-PFC-RESOURCE-RU.md) | Приняты исправления RSS units, статусов/потери tails и ограниченности causal conclusions; остановлен перебор carriers, выполнен D1 A+B-lite. Рекомендация «одна local optimization после attribution либо явный scope cut» пока не дала выбранного source-решения: offender не найден; сейчас запрашиваем альтернативную оценку, **не требуем одобрения cut**. |

R2 также требовал qualifier для exact Move/alias forms, B3 для padded ordinary union ZST claims, guard/model для foreign/realloc, actual SmallSort replay и multi-harness checks. Эти пункты нельзя считать закрытыми успехом restricted Quick. Интеграция B1 не равна blanket поддержке всех shims/indirect calls.

## 10. Отдельные границы и соседние треки

**Move.** На pinned nightly Miri probes43109689395/43109978880/43111757334 различили assignment/field Move/forget и exact in-place `Call(Move(place))`. Для последнего source становится uninitialized; Call(Copy) отличается. A3 сохраняет snapshot до clear. Это не общий proof Rust alias protectors или произвольных moved-from reads; reinit/alias/temporary forms требуют точного MIR и собственных controls. [A3R материалы](kani3300/a3r/).

**Layouts.** Reverse `[MaybeUninit<T>;N] → [T;N]` — explicit Unsupported. Nested `MaybeUninit<[MaybeUninit<T>;N]>`, by-value DST, arbitrary union pointees/compound slots, niche enums и variants с разным padding не включены молча. Поддержка matched masks/Pat offset не доказывает все layouts. Прямой `(*ptr).field=` и `addr_of_mut!(field).write()` могут иметь разный MIR; projection/setter coverage — gate.

**B1, G1, B3 — разные имена.** B1I — resolver/operation-loss fix, теперь dependency Part1; старое имя «PR-B1» также использовалось для G1 union-pointee расширения, которое здесь **не интегрировано**. B3 — отдельный ZST union codegen patch. Его последние coordinator probes base/v2/v3b43238542257/43238548798/43238557839 показали: v2 ICE на recursive arm, v3b6e9e782024 прошёл9 tests/covers; tail/tuple arm с embedded ZST-array остаётся baseline limitation. Это не CI evidence Part1 и не основание включать такой scope без composition.

**B4/realloc/foreign** остаются отдельными: pointer argument без shadow-value transfer ещё может менять отслеживаемые bytes. Нужны model/достижимый Unsupported либо явно ограниченный support claim; «resolved foreign call» не означает отсутствие memory effect.

**T1b/shared cache** — другой false-uninit трек: cached `IndexRange::len` инструментирован DelayedUbPass в контексте одного root и использован в других; C2 показал одно тело у failing index_range_len и passing manually_drop_unsized_len. Это подтверждает shared-body reuse, **не причинность FAIL**; caller/shadow state различались. Fresh-transformer causal pilot не зачтён в Part1. D0 singleton result устранил order hypothesis только для D0 raw_eq, не для всех cache cases. История T1b: [первый бриф](AUDIT-BRIEF-KANI3300.md), соседний research репозиторий t0 (Kani3300 t1b-c2). Нужен отдельный cause/repro перед глобальным cache fix.

## 11. Состояние кандидата и непройденные gates

| Gate | Сейчас |
|---|---|
| Final candidate |4f64cc617c; source A1–A3R+B1I+M1+S3, без R7/R8 и без G-SC |
| Targeted ordinary/storage |Есть Quick/matched evidence A1, B1I-A, D0/M1/mixed и S3 ordinary Assert; не универсальная proof correctness инструмента |
| Legal PFC+uninit / intended hole |P1/P2 не приняты; ресурсный предел/false private frame в контрастах; intended semantic pair gate открыт |
| DFCC private frame / Replace |Полная квалификация lawful writes, user-outside-frame negatives, clauses, stubs/recursive modes на финальном export не выполнена |
| M3 composition |Не выполнена: M1+M2+S3+mixed/alias/offset/overwrite/reset/false/Move и тяжёлые tests надо проверить вместе |
| Full regression / platforms |Нет полного финального штатного/opt-in Kani matrix для4f64; old SHA/platform results не переносятся |
| SmallSort practical replay |Нет принятого actual scratch PFC+uninit proof на финальном tool/export; read-only инвентарь в работе |
| Upstream package |Part1 ещё не представлен как готовый audited export; source/test history нужно упаковать после решения и gates, CI-only overlays исключить |

R7-C/R8-C — дополнительные **test-only** controls, подготовленные позже: [frame](kani3300/m2br7c/), [offset/Move](kani3300/m2br8c/). Их SOURCE_READY не превращать в execution evidence. На any scope cut P1/P2→Unsupported — сознательное изменение oracle/обещания, не P1 SUCCESS/P2 discovered UB; старые repro и исходная цель сохраняются в отчёте.

## 12. SmallSort scope: что известно и зачем инвентарь

В [DIRECT](https://github.com/Tiramisu-Cake/verify-rust-std/blob/4746a5d01d23ad1f562855474acfa707f63e952e/research/challenge-8/kani-k1/RESULT-DIRECT.md) Merge PFC покрывал scratch48 geometry с initialized prefix/uninit tail при **uninit off**. В [SPECDIAG](https://github.com/Tiramisu-Cake/verify-rust-std/blob/e417249e663a7b34b4148c641d062319096cb4d2/research/challenge-8/kani-k1/RESULT-SPECDIAG.md) G2 PFC+uninit выполнялся, но остановился на Unsupported до target reads. Это не свидетельство, что PFC+uninit нигде не нужен/не используется, и не положительное доказательство этого сочетания.

Задание [G-SC-C](TASK-KANI3300-G-SC-C.md) теперь **read-only inventory**, а не controls/код: exact Select/Merge repo/ref/root, proof_for_contract/stub_verified/Assert modes, flags/activation, constructors/clauses/helpers и shadow call edges, geometry и gaps. Artifact `kani3300/gscc/` на дату этого среза ещё не готов; его следует передать дополнением, не домыслить результаты сейчас.

Нужна оценка границы: исключение Check/RecursiveCheck с reachable transfer может сохранить часть ordinary storage, но блокировать modular scratch goals. Whole-harness admission шире context/path guard, поскольку включает setup; Replace отдельно. Unknown reachability не может быть доказательством отсутствия effect. Local visitor Instance сам не содержит selected PFC root context, общий body cache не должен переносить отказ между ordinary/PFC roots. Это **кандидатный дизайн для обсуждения**, не выбранная реализация.

## 13. Какие решения и отдельные issues рассмотреть

Мы готовы рассмотреть поддержку текущего scope, локальную оптимизацию, новый protocol/ghost channel, иной DFCC/CBMC encoding, дополнительную bounded диагностику или явную меньшую границу. Не требуется выбирать из прежних A/B/C. Снижение RSS через потерянный path/false frame/Unsupported не считается семантическим исправлением.

| Возможная отдельная постановка в Kani (не опубликована этим отчётом) | Что установлено / чего не следует утверждать |
|---|---|
| **“PFC with uninit shadow transfer exceeds memory limits on a scalar MaybeUninit roundtrip”** |Минимальные P1/P2, exact pins/flags/watchdog и R1 onset есть; причина DFCC/CBMC term не установлена. Стоит ли отдельный issue с ссылкой на#3300 вместо обязательства решить всё в storage patch? |
| **“Define DFCC treatment of compiler-owned memory-initialization state”** |Есть marker/assigns и mapped auxiliary writes/frame obligations. Нужны strict origin/identity/cell ranges; blanket helper exemption может скрыть user writes. Не заявляем доказанный false SUCCESS или OOM cause. |
| **“Uninit analysis of promoted allocations and contract registration bodies”** |D0/M1/S3 дают отдельные минимальные false-positive fixes и tests. Можно ли вынести implementation в отдельные patches, сохранив dependencies нового flat scope и отсутствие unchecked rollback? |
| **“Uninitializedness support for nested MaybeUninit flat-array construction”** |Внешний MU-of-flat достигает layout Unsupported до raw_eq; это support request, не доказанный false SUCCESS. Нужна ли отдельная область вместо расширения сейчас? |
| **“Retain checks when unresolved calls/seed collection fail”** |Дефект B1 был установлен и исправлен в Part1. Может иметь отдельную upstream bugfix историю; не переоткрывать его как нерешённый ресурсный диагноз. |
| **“Root-context isolation of delayed-uninit body transformations”** |T1b показывает shared mutation/reuse, причинность требует matched root/caller pilot. Отдельно от D0 и PFC OOM. |
| **Realloc/foreign effects и ZST compound union codegen** |Самостоятельные scopes с собственными repro/base controls; B3 уже имеет отдельный кандидат. Не приписывать им все симптомы Part1. |

Перед публикацией проверить существующие issues/дубли и согласовать формулировки с maintainer. Ничего не публикуется автоматически; новые runtime/ABI/backend изменения и C требуют отдельного решения. Во всех будущих PR действует строка: *Disclosure: this change and description were prepared with the help of AI assistants.*

## 14. Вопросы аудитору, по приоритету

1. Каков минимальный корректный и полезный объём Part1? Есть ли смысл **сейчас** сужать scope вообще, или лучше оставить blocker и исправить/исследовать причину? На cut не настаиваем.
2. Если сужать: какая точная граница сохраняет практически нужные SmallSort paths? Ordinary/Assert против Check/RecursiveCheck/Replace, effect-based против whole-harness admission, setup/clauses/hidden returns — где проходит честная линия?
3. Достаточны ли D1 bindings для конкретной причины/различающей гипотезы? Какие из source→GOTO→retained SSA цепочек значимы, а какие не свидетельствуют о converter cost? Не перепутаны ли Boolean root width, operand width, backing capacity и multiplicity?
4. Как трактовать saturating_add/sub nondet warnings и R6 abort paths? Нужен ли отдельный fidelity bug/repro до дальнейших ресурсных сравнений?
5. Какую минимальную следующую диагностику вы выбрали бы при отсутствии typed DAG/cache/conversion data: stock данные, bounded C patch или иной путь? Какие конкретные поля/фазы сделают эксперимент причинным?
6. Есть ли узкая оптимизация на4f64, которая сохраняет A3 pre-Move false snapshot, pairing/return0, M1 masks и S3, а также настоящий user frame failure? Или нужен другой протокол передачи/DFCC interface?
7. Если guard оправдан: как получить selected harness context, полноту transformed-effect closure и изоляцию shared cache? Как не потерять B1 diagnostics, return-only, recursive/generic/generated clauses и unknown edges?
8. Как гарантировать отказ до partial transfer/Move clear и до дорогого DFCC prefix? Достаточен ли compiler-level admission и какие последствия имеет conservative whole-harness cut?
9. Что отдельно требуется от Replace/stub_verified и private auxiliary writes? Можно ли нынешний whole-state assigns сохранить; где нужен precise cell classification и как не разрешить pointee/user writes?
10. Достаточно ли A1–A3R/B1I/M1/S3 исправляют findings R2 для заявленных форм? Какие конкретные semantic cases остаются не закрытыми targeted runs, особенно alias/offset/overwrite/projection/Move и immutable holes?
11. Какие parts стоит вынести в отдельные Kani issues/patches? Предложите точные symptom/scope формулировки; что является установленным bug, support gap, resource limitation или пока только hypothesis?
12. Какие positive/negative/mixed-root/recursive/Replace/SmallSort tests и full platform gates обязательны для окончательного export? Как трактовать expected negatives без сокрытия посторонних failures?
13. Какой порядок дальнейших шагов вы рекомендуете с нуля, без обязательства продолжать нашу последовательность R1–R8? Что можно прекратить, что является dependency выпуска, и какие решения должен принять владелец?

Просим выводы с severity, точными code/research anchors и границей установленного. Этот отчёт не утверждает готовность Part1 и не разрешает implementation G-SC до обсуждения вашего ответа.
