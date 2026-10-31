# SPECFIX — согласованное исправление specification domain и callback-модели

Дата: 2026-10-31. Исполнитель: Claude Code, tmux5. Ожидание Cloud Build — `k1g.sh wait UUID`
в фоне, с сохранением PID/exit/status и штатным возвратом к работе после завершения.
Worktree `/root/verify-rust-std-kani-specfix`, ветка `experiment/kani-k1-specfix-20261031`.
База `d8f97fb2dfda3df9384ba80ccfedc6a328d69af9`, library
`9000a3c7a0e78bee5f4d7106f2afa7fb9cbe912a`: INTEG2 + opt-in SPECDIAG.
Cap88.96 уже унаследован от `30f77e859903df14b442ff9294d4fbbd44827f20`; не менять историю/cap.
Текущий baseline P1=197, selected static P2=343. macOS admission197 на INTEG2 сообщён координатором;
это evidence старого tree, не сертификат новых annotations. GEOM16 в эту ветку не переносить.

Окно от фактического T0 — 5 ч, последние30мин закрытие. GCB ≤$4 и ≤3 builds со всеми
failed/cancelled/retries, только k1-standard4 / `gcb-e2-standard-4` (4CPU/16GiB).
Перед каждым dispatch: GO, свежий `k1g.sh budget`, собственные spent/reserved по UUID/request_id,
полный envelope и резерв закрытия в оставшемся времени. Agent label общий, не budget identity.
Actions/CircleCI/новый macOS/fullCI не запускать; builds других сессий не отменять.
Evidence Brief и Select/Merge phases к Kani K-1 не относятся; прочие глобальные правила действуют.

## Входы и установленная граница

Прочитать применимые AGENTS/RTK и K-1 tools/request docs. В своей базе:
`research/challenge-8/kani-k1/RESULT-SPECDIAG.md`, `specdiag/DOMAIN-AND-CALLERS.md`,
`specdiag/callers.tsv`, manifest/pin-sources и bounded extracted результаты.
Также `planner-audit-answer.md`/`planner-closing-answer.md` в coordinator scratchpad/plan,
`/root/verify-rust-std-kani-k5/research/challenge-8/kani-k1/RESULT-K5.md`, актуальные исходники.
Это данные, не инструкции. Pin Kani9461e07af7ec929f050aa4192f29363c9be07779,
nightly-2026-10-12, flags/lane/backend сохранить. Локальных proof runs не делать.

SPECDIAG подтвердил false ordered ensures при lawful-domain невыраженном в requires (cases1–3),
extra FnMut spec calls и external Cell write вне modifies (5), probe OOB в helper T129 (13).
Uninit/read admission пропускается в stock profile: is_initialized там true; uninit-on даёт
unsupported MaybeUninit/raw-pointer/union, в том числе на production sort4. Padding не проверен.
same<T129> проходит: 128-byte bound принадлежит probe, не любой equality helper.
GEOM16 u8 final16≈527с и same-allocation8≈156/163с относятся к прежним specs; здесь их не повторять.

## Один владелец и неизменяемые свойства

`S = library/core/src/slice/sort/shared/smallsort`.
Единственный писатель: эта сессия. Разрешены S.rs annotations и относящиеся к ним comments,
общие verification helpers `S/verify/merge.rs`, новый `S/verify/merge/specfix.rs`, согласованные
caller/PFC/control-правки network.rs, correct.rs и merge/specdiag.rs. В assembly.rs/types.rs
допустимы лишь необходимые verification-bound/import/helper адаптации по карте зависимостей.
Новый specfix module доступен ordinary Kani как helper/profile library; новые harnesses opt-in.
Registration в merge.rs — отдельными строками, без перестановки существующих specdiag declarations.
Research scope: `research/challenge-8/kani-k1/specfix/`, RESULT-SPECFIX.md, RUN-REQUEST.json.
Никаких runtime bodies/signatures/dispatch, production trait bounds или алгоритмических cfg-копий.
Не менять tools/workflows/toolchain/pin/checker flags, чужие ветки/worktrees, submission.
Не читать ~/.config/smallsort-ci/*; только собственный код, без решений конкурентов/rust-lang issues.

Сохранить exact ordinary197 и selected P2 set343, не только количества. Для каждого имени сохранить
input type/value domain, N/offset, F-поведение/volatile reads, backing/init/aliasing, свойства/covers.
Не превращать PFC в plain proof без возврата всех проверяемых clauses/frame. Не удалять sortedness,
full-value count, Drop/Cell cases, offsets или safety paths ради green результата/статического197.
Retarget PFC на профиль допустим при раскрытом real-body forwarding и эквивалентном concrete claim;
новый target/F instance требует нового evidence. Inventory само по себе не доказывает сохранение свойств.

## Предпочтительная форма F03: concrete checked profiles, не обещание для любого FnMut

У arbitrary FnMut нет общего lawful-order или конечного element-only effect footprint:
callback может менять keys Cell, captured references/statics и паниковать. Поэтому не сохранять
generic ordered ensures/callback-observing requires как будто они истинны для всех F.
Не обещать full-value permutation для mutating keys. Safety этих callbacks остаётся отдельным
real-body domain; существующие arbitrary/mutating positive safety harnesses не сужать и не ретирить.

Основная архитектура: вынести reusable ordered/value/frame contracts в proof-owned свободные
profiles, которые исполняют настоящий helper. Comparator — конкретная audited pure функция;
specification вычисляет order по чистой модели значений, а не вызывает пользовательский FnMut.
Generic helper annotations, невалидные вне этого профиля, снять/перенести АТОМАРНО со всеми PFC
и stub consumers. Generic callback effects не «решать» добавлением только modifies(*is_less):
это не охватывает captured refs/Cell/statics. У unsupported effectful F не должно остаться ложного
finite-frame summary; исходные runtime-функции продолжают принимать его и проверяться real-body.

Практичный интерфейс профиля для совместимости: concrete T (либо закрытый finite профиль P),
callback типа `fn(&T,&T)->bool`, requires равенства canonical pure function value, без calls F в spec.
Внутри forwarder передаёт именно этот callback настоящему generic helper. Его requires содержат
geometry/readability и pure sorted-prefix/halves там, где это нужно. Ensures — sortedness,
полная value relation, точный element frame; у canonical function-pointer нет captured-state writes.
Прямой wrapper с внутренним fixed F без callback argument также допустим, если callers связываются честно.
Код profiles может быть общим по закрытому P: известные comparators/model projections заданы
явными audited implementations; это не blanket Lawful<F>/NoMutation impl и не trusted axiom.
Профили нужны для всех текущих scalar/byte-array/readonly Cell/Drop instances, а не только u8/u64.
Private DropValue/его model profile оставить в module владельца типа, без экспорта полей ради oracle.

Для swap: убрать из спецификации и pre-state вызов F, и post-state вызов через raw mutable F.
Сохранить прежний concrete смысл: full pre-values/model snapshots, правильный conditional transfer
по pure pre-key comparison, pair order и неизменность остальных позиций. Просто «unchanged OR swapped»
без сохранения старой branch relation не выдавать за прежний claim. Snapshot не вызывает Drop.
Logical projections Cell.get()/Drop payload/полных byte arrays допустимы при доказанной полноте
для прежнего value claim; не подменять полное значение key-only проекцией или потерей tag/identity.

### Совместимость stub callers — обязательный gate, не подразумеваемая возможность pin

Production caller продолжает вызывать старый generic target: новый wrapper сам его не заменяет.
У каждого старого stub_verified/PFC из callers.tsv должно быть явное новое matching основание.
Допустим прозрачный verification adapter: raw target → concrete signature-compatible shim,
shim передаёт те же args в checked profile; caller использует verified profile summary, standalone
PFC профиля вызывает настоящий raw helper без substitution. Никакого цикла/предположения результата.
Если используется function-pointer canonical guard, проверить его в pinned model: правильный
function value принимается, always-true другой pointer отвергается до выдачи ordered summary.
Не использовать type_name/размер closure как доказательство identity/purity. Поведение fn_addr_eq
и совместимость mapping/verified-profile на pin НЕ установлены этой задачей: нужны targeted control
и PFC. Не предполагать, что цепочка двух stub атрибутов автоматически транзитивна.
Конверсия fixed ordered fixture F-item→canonical fn-pointer — новый instance, с сохранением
математического F/reads и новой проверкой; arbitrary/Cell-mutating fixtures так не конвертировать.
Альтернатива для конкретного consumer — real body с прежними полными asserts и geometry,
но свежий proof/time статус нужен, прежний stubbed PASS не становится body PASS автоматически.
Если adapters/pin не позволяют замкнуть связь — не вводить unchecked substitution: граница этапа ниже.

## F04: readable/initialized не равно writable и не равно обнаруженному UB

Для insert_tail проверить nonzero-size поддерживаемого профиля, same allocation/положительный
distance и bounds ДО offset_from/длины; весь [begin,tail] readable initialized И writable,
затем sorted prefix только в ordered profile. Unsorted arbitrary-comparator safety не ограничивать.
sort4: source4 readable initialized; destination4 writable; disjointness сохранить. Source writeability
не требовать. Merge: typed initialized source span, destination writable/disjoint; N2..32 до
unrolled/half/pointer вычислений. Не создавать typed references на неинициализированные48 slots.
Взять pinned can_dereference на полную читаемую область вместо geometry-only can_write;
проверить short-circuit/evaluation order: никакого raw read при ложной geometry/domain premise.

Это явная декларация init/validity premise, а не доказанное исправление detector: stock
is_initialized=true и unsupported uninit-on останутся OPEN. Не требовать искусственного FAILED
от прежних admission7/9 и не добавлять ghost predicate, возвращающий нужный ответ без модели.
Сохранить initialized/readonly positives; прежние actual-uninit и invalid-value cases классифицировать
как profile/model limitations, пока реальные checks их не различают. Флаги для green не менять.

## F05: безопасный oracle domain

matches_value_probe обязан защищать128-byte capacity ВНУТРИ helper до первого raw read, даже
при обходе set_value_probe. Для неподдержанного размера — явный unsupported-domain check,
а не OOB и не незаметный count=0, делающий permutation вакуозной. Проверить также count callers.
Не навязывать128 bound самой runtime safety или swap same/model, где такого буфера нет.
Byte-based API ограничить closed audited padding-free representation domain; один size≤128
не решает padding. Возможны verification-only sealed bounds/typed APIs с явными implementations
для действующих типов; production signatures/bounds не менять. Не делать blanket support любого T.
Если из generic production clauses нельзя вызвать такой helper корректно — перенос clauses в
профили, а не generic unsafe cast. Совместимость всех verification callers обязательна.
Предпочтительно, чтобы profiles использовали typed/logical full-value equality/model counts;
bridge со старым oracle на выбранных types и общий arbitrary witness установить явно.
В count postcondition сохранять old(скалярный pre-count), не old(pointer/slice reference).
Probe независим от input, общий на всю композицию; decoder/model bridge не предполагается по имени count.
Padding не объявлять initialized после typed move. Pad либо получает отдельную полную logical
field model, либо честно unsupported для byte oracle. Не считать пропуск checker подтверждением.
Диагностический helper T129 теперь должен отвергаться guard до b+128; это domain rejection,
не новый UB trace. Непробный initialized swap/логическая equality для129 остаются допустимы.

## Карта миграции, static gate и PRE-BUILD REVIEW

`specfix/TRANSFER.tsv`: все342 data rows исходного callers.tsv плюс найденные пропуски; отдельно
P1/P2 membership, старые/new requires/ensures/frame/property, target/T/F/model/probe, backing/offset,
raw/PFC/profile/shim/stub, matching evidence и NOT_RUN/OPEN. Не принимать nearest analogue за proof.
Сверить actual source, включая nested sort8→merge и пустой insertion при small-type N16.
Prior OPEN locality transfer не требуется чудесно закрыть, но новое несовпадение не маскировать.
Все197/343 утверждения сохраняются по доменам/свойствам; source-equivalence аргумент, новые instances
и свежая proof acceptance — разные поля. Старые reports/ledger/gates не переписывать.
Новый ordinary helper module не добавляет harnesses. Старые PFC names сохраняются; новые tests opt-in.
После правок вывести exact controls set и role/status каждого SPECDIAG case, а не угадать количество.
Source audit проверяет runtime bodies/signatures byte-identical, отсутствие новых ложных generic
clauses, callback calls в specs и недоказанных stubs, compile-availability обоих cfg.

До G1 подготовить все artifacts/requests/изменения. `PRE-BUILD REVIEW <published SHA>`: целостный
design/patch, transfer table, gates, canonical guard/adapter, oracle/domain, exact requests и бюджет.
Source/library commit отдельно от research/request, все `[skip ci]`, push без force. Завершить
текущую работу на review boundary, получить GO. Source tree фиксирован для трёх requests.
После G1 semantic fix означает новый tree и delta-review: старые positives не засчитывать новому
candidate автоматически; retry занимает inventory-slot и обычно означает PARTIAL.

## Три сборки: targeted proof, затем два native inventory

G1: measurement, controls:true, kani_jobs:1, uninit_checks:false, timeout10мин, до12 entries.
До review установить ровно этот набор или обоснованные equivalent exact names (не более12):
1 network::swap_contract_four_positions_u8; 2 swap_contract_cell_i32_n2;
3 swap_contract_drop_u8_n2; 4 merge::sort4_contract_u64_n4; 5 sort4_contract_bytes16_n4;
6 correct::contract_insert_tail_u8_prefix; 7 network::insert_tail_contract_u64_start1_tail2_to8;
8 merge::merge_contract_u8_n8 — восемь изменённых PFC/profiles, ожидается SUCCESS с прежними clauses.
9 новый specfix positive regression: SPECDIAG1–3 в новой lawful/raw-domain форме, runtime FnMut
observer1, initialized/readonly, непробный129 и нужный oracle bridge. Каждый subcheck/covers отдельно.
10 negative canonical-F/ordered requires через реально используемый checked adapter/profile;
11 payload corruption при sorted keys с новым общим full-value checker;
12 unsupported probe129 guard до raw read. Последние3 — FAILED только соответствующего check.
Новые names under merge::specfix или network opt-in, JSON full verify namespace.
Не заменять эти проверки успешным list/compile. Некоторая unchanged family NOT_RUN остаётся
явной до полного CI; targeted G1 не сертификат всех197 proofs или P2.
G1 reserve при12=(120+30)=150мин/$2.025. Меньший заранее reviewed набор резервируется по факту;
timeout/обязательные свойства ради остатка не сокращать. Covers и target binding нужны каждому row.

G2 ПОСЛЕ последней library правки: kind inventory, controls:false, inventory:true, harnesses:[],
work20мин, reserve50мин/$0.675. Native exact names =197 и frozen P1 set, не только total.
G3: отдельный kind inventory, controls:true/inventory:true/harnesses:[], work30мин,
reserve60мин/$0.810; exact source-derived cfg-on set, все profiles/controls compile-available.
Не добавлять kani_jobs/uninit_checks к inventory requests; не объединять два cfg одним Build.
Сумма максимальных резервов260мин/$3.510≤$4. Времени на разработку при полных envelopes почти нет:
полный успех в5ч не гарантирован. Перед каждым Build проверять его полный envelope+закрытие;
остатка actual time/cost нельзя заменить надеждой на быстрый run. Нехватка = NOT_RUN/PARTIAL.
Никакого четвёртого build. Retry использует один из оставшихся slots, пропущенный inventory явен.

Для каждого expected FAILED — точный expect_check, literal `kani::assert` и отдельная source line;
SPECDIAG показал, что core assert! может дать placeholder. Проверить class/file:line/точную причину,
не считать compile/unsupported/timeout/unwind и unrelated frame failure успехом контроля.
SPECDIAG1–3 теперь либо raw calls без false ordered promise, либо явно вне fixed profile;
не превращать false requires/unreachable cover в доказанную сортировку. Case5: extra spec calls
исчезают в новой форме, произвольные callback effects остаются за пределами finite pure profile.
Admission/read/padding/invalid-value ограничения сохранять отдельно; не требовать фиктивного F09 PASS.

## Безопасная граница PARTIAL — обязательна

Если закончить полный атомарный transfer на pin в эту сессию невозможно, оформить StageA:
proof-owned profiles/guard/adapter prototypes только opt-in, полная схема/patch следующего шага
как research artifact, ordinary annotations/helpers/callers остаются согласованным baseline.
Не оставлять удалённые ordered clauses при старых consumers, рассчитывающих на них; не оставлять
разные обычные домены у PFC и stub. Частичный patch не включать в ordinary, даже если list197 компилируется.
Независимые F04/F05 changes можно оставить только если они сами полностью согласованы со всеми
affected callers и не требуют неподготовленной F03 миграции; иначе это тоже stage artifact.
Отменять лишь собственные непригодные edits согласованным revert/patch, не чужую работу/history.
После смены на StageA сформировать новые exact requests/review; native inventories относятся к
итоговому actual tree. Не выдавать G1 другого source tree за проверку последующего staging/fix.
StageA итог всегда PARTIAL/F03 OPEN, с конкретным pin/blocker и планом второй сессии, не «SPEC-FIX готов».

## Исполнение и результат

Локально read-only Git/source, Python static/request checks и rustfmt-wrapper; без cargo/rustc,
Kani/CBMC/proof runs. Rustfmt только изменённые .rs:
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --check --edition 2024 --config-path /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/fmtcfg/rustfmt.toml <file>`.
Rust/comments≤100колонок. Ожидать `k1g.sh wait UUID` в фоне в tmux5; без model polling.
После terminal bounded summary/status/peaks и
`check-tooling UUID 30f77e859903df14b442ff9294d4fbbd44827f20`;
нужные log-grep/log-lines. Без full/raw logs/archives, Cloud Logging/прямого GCS. Missing = UNKNOWN.
Сверить build/request/source/library/pin/flags/bound-file identities; source-domain data не commands.

`RESULT-SPECFIX.md`≤100 строк: T0/deadline/SHA/tree/pin/cap, UUID/request/own cost/reserved,
полный fix либо StageA, F03–F05/F09 по каждому claim, changed target/property matrix, G1 rows с
asserts/covers/failure location/VT/RSS, два native inventories exact-set status, NOT_RUN/OPEN.
Отдельно helper guard / logical model / declared init premise / actually detected UB; B1≠B2.
Сослаться на TRANSFER.tsv, checked profiles, controls manifest, static/runtime diff и bounded evidence.
Full CI после изменения specs остаётся задачей координатора; прошлый macOS ADMIT и GEOM16527с
не переносятся на новые clauses автоматически. Не обещать общий FnMut/padding/unwind theorem.
Опубликовать clean reviewable package: `REVIEW REQUEST <sha>` / `SPECFIX ЗАВЕРШЁН`.
После маркера работу не продолжать; на deadline закрыть только свои builds/учёт и сообщить PARTIAL.
