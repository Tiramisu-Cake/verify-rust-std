# KANI3300 CLOSURE-ZST — layout repair and semantic qualification (DRAFT / NOT ISSUED)

2026-11-13. Черновик одной implementation session для будущего воркера, **не выдан**.
Это верификация корректности, не security-работа. Сейчас не создавать clone/branch, не менять код и не запускать проверки.
После отдельной выдачи локальные cargo/rustc/Kani/CBMC/Miri/builds запрещены; CI готовит/запускает координатор после своего GO.
Никаких downloads/raw-log reads, публикаций, source push, G-SC или nested subagents. Cloud $0.

## Контракт стадии и исходные данные

Цель: убрать ложный Unsupported для **sized zero-byte closure** без удаления tracking/checks и без изменения clause semantics.
Exact base: Kani `4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c`, tree `af28e22ec446b254cfa3a28b2882eafa58d5a458`.
После выдачи новый isolated clone/ветка `fix/kani-3300-closure-zst` от exact base, путь согласует координатор;
имеющиеся source clones read-only. Dirty/wrong base → STOP без reset/stash. R7/R8 carrier changes не переносить.
Research g0: `experiment/kani-k1-kani3300g0-20261111`, вход `7d695258f530eebfc7ec5c2365b011535c7a973e`.
Прочитать `PLANNER-H1-SEMANTIC-REVIEW.md`, `kani3300/h1-step1/{SEMANTIC-FINDING,RESULT-H1-STEP1,ORACLES}.md`,
`kani3300/h1-step0/RESULT-H1-STEP0.md`; использовать curated reports, не локальные raw CI captures.

Исходный P1/P2 из `kani3300/m2a/cases/` сохранить byte-for-byte:
- `scalar-pfc-legal.rs`, root `postcondition_reads_initialized_return`, SHA256 `fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b`;
- `scalar-pfc-hole.rs`, root `postcondition_reads_returned_hole`, SHA256 `61fc369a6830c6ff185887b04db36139ca529e4de097c0025ce7b29c8323f759`.
Профиль будущего probe: stock CBMC6.11/прежний solver, target/toolchain из H1; explicit object-bits12, normal slicing/checks.
CLI `--cbmc-args --object-bits 12` — два tokens; остальные Kani options перед consuming --cbmc-args.
Это уже принятая policy, **не** новое разрешение запусков. Не использовать UF/no-slice или lower bits для обхода нового semantic FAIL.
Exact replay использует frozen inputs и переданные flags. Если suite-копии требуют per-test annotation b12,
записать отдельные bytes/hash и comment-only delta; не выдавать их за byte-identical исходные H1 fixtures.

## 1. Source patch — одна узкая граница

Основной файл: `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs`, `data_bytes_for_ty`.
В ветви RigidTy::Closure с rustc layout `is_sized()` и `size.bytes()==0` вернуть пустой data-chunk list.
Не подменять ошибку layout query нулём, не выводить size из числа MIR operands/названия и не расширять shortcut на все type kinds.
Замыкание с captures размера0 тоже не имеет data bytes: допустимо при проверенном полном layout0, не при «все captures игнорируем».
Все nonzero closures и прежние coroutine/foreign/union-field/niche ограничения остаются на прежнем fail-closed пути.

Обосновать цепочку empty chunks→Sized mask[]→LAYOUT_SIZE0: существующие `is_ptr_initialized`/`set_ptr_initialized`
в `library/kani_core/src/mem_init.rs` возвращают true/no-op до чтения/изменения MEM_INIT_STATE. Не менять этот runtime.
Empty closure mask не должна bless returned payload, другой object или false witness.
Проверить влияние `PointeeInfo::from_ty` и layout compatibility callers; не вводить «layout ошибки допустимы» fallback.

Не менять S3/body_overrides, receiver/argument aliases, passes/check count, DFCC/assigns, A3 pairing/Move, immutable masks,
contract Assert/Replace policy, глобальный DEFAULT_OBJECT_BITS или допуски для MU/union в агрегатах.
Если потребовалось что-либо из этого, остановиться с доказанным препятствием и отдельным предложением.
Обязательная статическая type audit: конкретные типы size/is_sized(), match bindings и сравниваемых значений;
никаких предположений «rustfmt значит типы верны» и локального компилятора для проверки.

## 2. Контроли и честные границы

Новые expected fixtures оформить по существующему uninit framework; manifest с source/hash/root/ожидаемым property class.
Не конструировать invalid typed values до целевого read: hole хранить в valid MaybeUninit/raw storage.
Legal и hole варианты различаются только состоянием нужного байта/выбором возврата, не предположениями о результате проверки.

| Группа | Что проверить | Значение для этой стадии |
|---|---|---|
| Exact P1/P2 | Capture-free ensures после MU transfer | Обязательная различающая semantic пара |
| Zero-size capture | Closure с захваченным `()` или aligned ZST, полный layout0, legal/hole callback argument | Пустая маска окружения не bless-ит payload; подтвердить, что целевой layout path действительно вызван |
| Captured scalar/padded aggregate | Initialized by-value capture с nonzero rustc layout | Только при подтверждённом запросе closure layout ожидается explicit Unsupported; не обнулять padding/data целиком |
| Captured reference/raw pointer | Valid capture указывает на initialized/hole payload; есть mutation/alias use | Не удалять receiver/CheckRef; если closure layout не поддержан, это boundary result, не payload-proof credit |
| Captured MU/ordinary union by value | Valid MU::new/uninit и корректно созданный union, полный closure layout ненулевой | При подтверждённом запросе layout не превращать UnionAsField/nonzero Unsupported в empty mask или все-true; зафиксировать границу |

Для nonzero групп raw-pointer read/copy самого closure может явно запросить его layout; использовать такой законный вход,
если обычный callback не достигает layout. SOURCE_ONLY ожидаемое значение не выдавать за выполненный тест.
Если запрос layout не достигнут, это nondiscriminating control: отметить и не считать подтверждением guard.
Для captured reference/MU/union дать разные by-value/by-reference строки; pointer bytes ≠ pointee bytes.
Полная semantic квалификация nonzero captures не входит в узкий patch. Нельзя объявить успешное принятие expected Unsupported
доказательством работоспособности captures; нужный legal captured PFC на этом пути остаётся release blocker.
Сохранить существующие frame/clause/argument-transfer/false negatives и их входы; новых guessed property IDs/goldens по общему FAILED не делать.

## 3. Оракулы P1/P2 — отдельно от ресурсного итога

P1: все нужные проверки успешны; outer `postcondition_target::{closure#2}.assertion` достигнут и SUCCESS,
callback прочёл initialized17, нет Unsupported/раннего frame/protocol/invalid-value отказа или assume, скрывающего полезный хвост.
Сохранить source/callsite binding и полный bounded property inventory, а не только итоговый SUCCESS.

P2: после lawful body/return отклоняется первый payload read в ensures. На4f64 это **два разных свойства одного bad read**:
local Check (`*const u8` в description) и delayed CheckRef (`u8`), оба проверяют pointee initialization.
Новый oracle сохраняет оба ожидаемых обязательства и запрещает все посторонние failures, включая apply_closure Unsupported.
Не требовать literal «ровно один FAIL», не принимать просто `>=1`, не удалять один check ради счётчика.
Generated IDs перепривязать к source/read/operation, не копировать `.1/.4` без подтверждения новой головы.
Изменение числа/класса checks → STOP с точным MIR/source mapping; самостоятельная deduplication не разрешена.
В P2 outer assertion может быть UNREACHABLE после failed-read guard; это отличается от такого же исхода у legal P1.
Достигнутость checks и полезного callback — отдельные поля. Старые H1 inventories/ORACLES/results не переписывать.

## 4. Передача координатору и STOP

После выдачи подготовить CI-REQUEST для targeted semantic probe, не запускать его. Новые runs требуют отдельного GO:
старый H1 пакет≤10 завершён, его разрешение не переносится на этот patch.
Начать с exact P1/P2 на b12; затем boundary controls. Propose прежние per-case300s/6GiB limits,
но лимиты/число roots фиксирует координатор до запуска. Один solver одновременно; не повторять H1 matrix.
Не переносить13s/1.8GiB с failing4f64 на исправленную программу: новый callback return/outer assertion меняет workload.
CI должен сохранить build/source→binary binding, actual argv/GOTO/binary hashes, bounded полный inventory и исходные exit/signal/RSS KiB.
Не заводить новый tracing framework; при недостаточности существующего quick — конкретный bounded request и STOP.

В research `kani3300/closure-zst/`: INPUTS.json, TYPE-AUDIT.md, TEST-MANIFEST.json, CONTROL-MAP.md,
REVIEW.md, CI-REQUEST.md, RESULT-CLOSURE-ZST-PREP.md (≤35 строк); static-only и NOT_RUN обозначить явно.
Source diff только узкий layout repair и fixtures; всё остальное read-only. Один source commit от4f64,
автор через `git -c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com`; без source push/CI overlays.
Research commit `[skip ci]`, тот же автор, stage только результаты этой стадии; без push/выдачи дальнейших стадий.
Для последующего общего gate нужны legal-pair/postcondition-hole и R7-C lawful-modifies: captures `out` могут потребовать
отдельного upvar-layout patch с реальными offsets/recursive masks. Это handoff, не неявное расширение этого задания.
Готовность source package не равна P1 SUCCESS или принятию Part1. После будущей выдачи финал `READY <source-sha>`;
сейчас **DRAFT / NOT ISSUED**.
