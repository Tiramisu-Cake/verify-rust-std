# KANI3300 C1-P — подготовить контроли flat/raw_eq и ABI gaps, worker 15

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна сессия подготовки, **Cloud $0**, без запусков.
Воркер 14 продолжает D0-P. До D0-A/M0 разрешены матрица, source/spec binding и test-only заготовки;
активация новых тестов в Kani suites, production guards и модель — следующие задания после design gate.
Решение B в силе: flat scratch сохраняется, raw_eq model обязательна; direct-MU сужение и откат исключены.
Это верификация корректности, не security-работа.

## Вход и текущие факты

Прочитать `PLAN-KANI3300-PART1-B.md`, аудит `AUDIT-REPORT-KANI3300-PART1-R2-RU.md` @ `124a45e373`
(ответы 2–5,8,11–13), R0 `kani3300/r0/` @ `8ad13e016e` и
`kani3300/b1ia/{TEST-MANIFEST.json,COVERAGE-GAPS.md,RESULT-KANI3300-B1IA.md}` @ research `e3e1125988`.
Source **`6134e42dd1c65dc980336e7d9455aba02d423edf`**, `/root/kani-fix-3300-p1b1` — только чтение;
production как в `dc5f5a406749a73f1c3192e0b5338441e79508bb`. Проверить SHA/clean status; не checkout/fetch/edit source.

По сообщению координатора Quick **`43199156872`**, CI **`fcba2fe76883c3441182bb6c7506ca8565c62797`**
(parent source, diff workflow-only): fmt/build/clippy PASS; kani Uninit 22/0; expected uninit **119/1/2 ignored**;
ui 14/0; script 1/0. Единственный FAIL — прежний `maybe-uninit-initialized` raw_eq legal failure.
Это aggregate source-reported evidence; не whole-Quick PASS, не фактическая проверка всех named properties/ABI gaps.
Бывшие shim sources проверяют FnPtr, tuple Unsupported и Item return; не приписывать им недостигнутый Shim guard.

## 1. Матрица контролей без повторения существующих тестов

Создать `CONTROL-MATRIX.json`: obligation → existing pinned fixture/harness или новый draft/spec → semantic expected
property/observable → требуемый MIR/Instance/AllocId/runtime binding → lowering risk/неизвестное → stage owner.
Раздельные поля observed (с точным source/run/provenance) и expected; новые inputs всегда **NOT_RUN**.
Property ID, kind/body, retained raw_eq, branch reachability и отсутствие setters не выводить из source spelling.
Переиспользовать существующие raw-eq-uninit, typed-transfer/padding, Item-return pairs, reset/overlap и PFC controls,
давая точные ссылки/хэши вместо копирования тел или новых тестов, повторяющих реализацию.

Покрыть обязательства:

- anonymous/promoted immutable referent с полной и частичной init mask, direct reference и передача через helper;
- динамический выбор promoted/local объекта, allocation coalescing/alias/offset и оба raw_eq operands;
- flat `[MU<T>;N]` bytewise copy через pointer на **весь** массив слотов, fully written и unwritten-byte companions;
- flat slice/subrange, source/destination offset и overwrite/reset false→true/true→false; typed D(T) против raw extent;
- обычный call destination/normal edge и shadow return с сохранением false; padding не bless, unwind/abort не normal;
- nonzero/zero extent и ZST; непустой negative обязателен, empty control не заменяет его;
- legal no-contract/PFC + legal modifies, отдельные frame/clause negatives, shared specialization/root-order controls;
- границы by-value DST, ordinary-union constant, hook/DFCC/shim и resolver Err — поддержка/Unsupported/UNKNOWN отдельно.

## 2. Небольшой пакет source-level drafts

В `fixtures/` подготовить **не более 10 новых harness** первой очереди. Приоритет — недостающие promoted legal/mask-hole
controls (holes слева/справа) и flat whole-array-copy legal/hole. Остальные строки матрицы можно связать с существующим
тестом либо оставить точным spec на C1 после M0. Все drafts остаются в research, не в активных Kani suites.

Для raw_eq retained-intrinsic controls использовать размер/форму, устойчивые к известному InstSimplify (например 3 bytes;
padding fixture 12 bytes уже существует), но фактическое lowering остаётся NOT_RUN. Не править два D0 harness.
У negative ссылки должны быть допустимы до проверяемого byte read: например `[MaybeUninit<u8>;3]` с hole;
не создавать иной ранний UB/unsupported tuple, который замаскирует нужную проверку. Immutable promoted mask-hole не
получать записью в constant memory; referent с Some/None — гипотеза source lowering до MIR/AllocId подтверждения.
У каждой копии/offset/overwrite пары иметь наблюдаемый initialized positive и самостоятельный negative без раннего
Unsupported; не добавлять assume initializedness, отключение checks или blanket `should_panic`.
Draft содержит license header, proposed flags, смысл legal/negative и требуемый observable, без выдуманного golden.
Scalar companions предпочтительнее случайного array equality, если raw_eq не является проверяемой операцией.

## 3. Точные compiler-input specifications для оставшихся ABI gaps

Уточнить четыре specs B1I-A: genuine FnDef resolver Err; bodyless/generated Shim/LlvmIntrinsic/Item;
bodyful Shim direct-shadow argument-only; bodyful Shim shadow-return-only. Отдельно добавить boundary specs
by-value DST, retained ordinary-union constant и backend-hook intercepted return.
Для каждого указать нужный actual kind/body/ABI, operand/destination types, local/seed/points-to/reachability путь,
entry loads→operand checks→Unsupported и что именно доказывает исполняемый control. Проверить по pinned API source,
можно ли получить форму в legal MIR; если нет — записать ограничение/UNKNOWN, не конструировать заведомо невозможный
Instance для фиктивного coverage. Source FnOnce example и specification не равны выполненному compiler test.
Не реализовывать новый framework/visitor mock, не расширять shim ABI и не менять resolver/guards здесь.

## Результат и STOP

Только g0 `research/challenge-8/kani-k1/kani3300/c1p/`: `CONTROL-MATRIX.json`, `fixtures/`,
`COMPILER-CONTROLS.md` (specs/достижимость/unknowns), `HANDOFF-M0.md` (≤30 строк: requirements и очередность для model owner),
`RESULT-KANI3300-C1P.md` (≤15 строк). Без source edits и Kani commits, CI workflows, диагностических hooks или записи в `d0/`.
Статика: JSON/schema/хэши и source API review; разрешённая rustfmt-обёртка для draft .rs, `git diff --check`.
Неисполненные snippets не называть compile-ready. Старые b1i/b1ia/r0 results не переписывать и proof credit не присваивать.
Research commit `[skip ci]`, author/committer `Tiramisu-Cake <igkharin@gmail.com>` через `git -c`,
stage только `kani3300/c1p/`, push g0 без force. D0 активно: не включать его файлы/чужой staged diff;
при concurrent/non-fast-forward — handoff координатору, без reset/stash/force.

Никаких локальных cargo/rustc/Kani/CBMC/Miri/сборок, реальных proof tests, Actions/Cloud dispatch, raw logs/archives/credentials,
PR/issue/комментариев и ссылок на сторонние PR. Python/чтение Git и разрешённая rustfmt-обёртка допустимы.
STOP после пакета до D0-A/M0; C1 implementation/CI выдаются отдельно. Не начинать M0/model/guards самостоятельно.
Последняя строка ответа: `READY <sha research-коммита C1-P>`. Это подготовленные inputs, не runtime coverage или PASS.
