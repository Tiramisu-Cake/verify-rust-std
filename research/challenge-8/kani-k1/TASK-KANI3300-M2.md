# KANI3300 M2 — qualification call destinations/false transfers/PFC, worker 14

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна стадия, **Cloud $0**, без запусков.
Цель — квалификация существующих setters/transfers после M1, не предполагаемая новая setter-модель.
Это верификация корректности, не security-работа.

**CI update 2026-11-12:** M2 READY5f7f2b7364, но qualification не принята. Quick43229982767 дважды shutdown/exit143;
memprobe43232249168 (CIcc29c82bf1) выявил legal ordinary+PFC uninit `[u8;3]` falseFAIL и postcondition-hole OOM.
M2-Aea0fbb5931 probes готовы; новый handoff: TASK-KANI3300-M2B.md (14, Assert/ensures seed repair),
TASK-KANI3300-M2B-RESOURCE.md (15 после B3-CI, resource/frame diagnosis). M2 semantic/resource gates остаются открыты.
Ordinary вызывает contract-decorated target в default Assert mode; название root не является no-contract control.
Original inputs/goldens и исторические m2 results не переписывать. M3 HELD.

## Вход и pins

Прочитать M0 @ `742c77fa03`, `kani3300/m1/{SOURCE-BINDINGS.md,TEST-MANIFEST.json,REVIEW.md,CI-REQUEST.md}` @
research **1027035e6b**, `TASK-KANI3300-C1T2.md` и `M1-NOTICE-C1T2.md`.
Проверенная M1 source **5abdcf982da6aff65662e198af27a9c776830a89**, production **254ae69662b3206cd4432dae0cd44c534b1b13fb**,
tree **960a71c70b3f890b4f5cd2b53a83f6a0f8e00951**; `/root/kani-fix-3300-m1` читать, не менять.
Создать отдельный clone **/root/kani-fix-3300-m2**, ветку **experiment/kani-3300-m2-qualification** от exact M1 source.
Иной existing destination/dirty state → STOP, без reset/stash. Не ребазировать на diagnostic tree или standalone B1/B3.

По координатору Quick **43222702257**, CI **05024a2112b77da6d86d29f3d272bbc74ad5df98**: fmt/build/clippy PASS,
unit immutable_allocations 5/0, kani Uninit 22/0, expected 130/0/2 ignored, ui 14/0, script 1/0.
Два existing D0 legal теперь PASS без изменений прежних fixtures/goldens. Immutable-masks 4 и promoted-only 6 matched;
последние matched и на baseline, поэтому не являются различающим evidence M1. Это aggregate coordinator-reported facts,
не полная source/mask/runtime-binding qualification и не full regression gate. Исторические m1 results не переписывать.

**Scope update C1-T2:** baseline43225818126 → M1 43225812282: четыре u8 raw/== mixed cases различают модели,
но четыре MU inputs обеих lanes дали ранний Unsupported у `MaybeUninit<[MaybeUninit<u8>;3]>`, до raw_eq.
15 исправляет их на direct flat stack по TASK-C1T2A; эти четыре старых failures не засчитывать как intended negative.
Current scope: `[MaybeUninit<T>;N]`/slices и supported `MaybeUninit<[u8;N]>`; **nested MU-of-flat не добавлять**.
Не устранять такой fixture helper расширением layout/введением all-true mask. Контрольные target/out storage выбирать
в поддержанной форме; nested idiom записан отдельно в SCOPE-MU-OF-FLAT.md. U8 outcomes не доказывают opaque MU/ABI branches.

## 1. Карта существующих обязательств, без копирования тестов

Создать matrix existing source/harness/hash → exact semantic obligation → требуемые operand/CFG/property bindings.
Переиспользовать:

- `maybe-uninit-initialized`: два D0 [u8;4] legal, left normal-edge setter; новый setter здесь не нужен;
- `maybe-uninit-call-pairing`: selected first/middle/last с gaps обычных args, nested/repeated calls и initialized control;
- `maybe-uninit-argument-return`, `-argument-buffer`: false propagation через conditional/nested returns;
- `unresolved-calls/item-return-{initialized,uninit}-{plain,seeded}`: Item true/false pair, не Shim coverage;
- `maybe-uninit-typed-*-padding` и `-typed-transfer-data`: raw extent против typed D(T), padding discard и false-data;
- `maybe-uninit-contract-frame` / `-clause`: frame violation и requires-clause uninit negative;
- `maybe-uninit-call-move`: snapshot-before-reset normal path, не доказательство unwind semantics.

Для supported ordinary Item указать actual parameter indices/signature/count/return0, selected source-following branch,
снапшоты до Move reset, caller normal destination и existing setter. Оптимистичный destination branch текущей модели
не считать конкретным initialized state на всех ветвях; обязателен путь, сохраняющий false source byte.

## 2. Не более шести новых test selectors первой очереди

В собственном path **tests/expected/uninit/transfer-qualification/**, не C1-T2 files. Ниже очередь gaps:
выбрать минимальное дополнение до 6 selectors с reuse/объединением совместимых positives; отложенное явно перечислить.

1. Legal no-contract/PFC pair на одном небольшом target с legal modifies: initialized transfer/read + anonymous immutable
   RHS из нового M1 пути, useful assertion/ensures. Должны пройти и полезный check, и frame; private state не даёт ложный frame.
2. Ensures/postcondition uninit negative на поддержанном return/transfer path, если существующая requires-clause пара
   этого не покрывает. Нужна reached uninit property именно в postcondition, не frame/ранний Unsupported.
3. Полезный branch-specific initialized conditional return control; existing arbitrary-bool negative переиспользовать,
   а source/value/selected branch привязать явно. Не объявлять оба arms покрытыми по одной общей FAILURE.
4. Узкая out-pointer fully written / partial-hole пара (при необходимости уложить в оставшийся лимит): изменение pointee
   не должно blessing соседних/неписанных bytes при normal return. Валидный MU storage до intended conversion/read.
5. Supported panic=abort/diverging call path: static CFG и observed panic/abort property; normal-return destination setter/
   return0 load не выполняются на abnormal edge. Настоящий unwind на этом pin не симулировать; отметить NOT_COVERED.

Лимит — до 6 selectors; legal no-contract control можно связать с existing телом, без дублирования. Если тип/контрактная
форма не supported, дать точный gap вместо framework/нового ABI. Scalar/3-byte cases предпочтительнее больших proofs.
Legal target сам устанавливает initialized data; не подменять это assume/new requires, предполагающим проверяемую initializedness.
Некорректный typed value/reference до intended read, fake Shim, лишний Unsupported или ранний frame failure не квалифицируют
целевой negative. Std == с hole в [u8] не использовать: это более ранняя validity граница; valid holes — через MU storage.

## 3. Scope source changes и приёмка

По умолчанию test-only + source/CFG audit. Локальный source repair допустим только для конкретно установленного gap
с различающим control и обоснованием; D0 setter не добавлять повторно, существующий false/typed mask/protocol не ослаблять.
Новая ABI/contract model, broad guards, blanket true, per-reference reseed, registry redesign, heap/foreign/realloc,
B3/G1/T1b/general cache work — STOP с отдельным blocker, не расширение этой стадии.

Статически проверить reset→immutable seed→user effect и private state во всех relevant ordinary/PFC/generated reset sites;
per-GotocCtx registry/полный closure сохраняются. Source presence не равен reached property: для CI готовить точные queries.
Baseline/new goldens по семантике, IDs только из наблюдений. Compile success/общий FAIL/substring match не acceptance.
Partial/missing binding — UNKNOWN; новое failure, потерянный обязательный check или unpaired transfer → STOP acceptance.

## Результат и STOP

Статика: diff --check, pinned API/-D warnings/import audit, разрешённая rustfmt-обёртка по полному пути из TASK-M1.
Один bounded Luna High review test contracts/CFG; production semantic review только при source repair, delta тому же reviewer,
без вложенной делегации. Новые compilation/runtime/property outcomes NOT_RUN, CI не запускать и не ждать.
Локальные Kani commits с нейтральными сообщениями, без [skip ci], author/committer Tiramisu-Cake <igkharin@gmail.com>;
Kani не пушить. C1-T2 ведёт 15; общие source files или interface change согласовать через координатора, не править параллельно.

g0 **kani3300/m2/**: `NOTES.md` (≤35 строк), `QUALIFICATION-MAP.json`, `TEST-MANIFEST.json`, `CFG-BINDINGS.md`,
`REVIEW.md`, `CI-REQUEST.md`, `RESULT-KANI3300-M2.md` (≤20 строк), все пути относительно research/challenge-8/kani-k1/.
Записать full base/candidate/tree и test/source deltas; pure qualification не называть новым исправлением модели.
CI request: targeted legal/PFC/frame/clause/normal-abnormal/false controls, затем existing Quick (при source repair сохранить
имеющийся шаг unit immutable_allocations); bindings через обычный
--emit=mir/property inspection при необходимости, без нового runner. M3 начинается только после приёмки результатов, не READY.
Research commit [skip ci], тот же author/committer через git -c, stage только kani3300/m2/, push g0 без force;
конкурентный update → handoff без reset/stash/force/чужих файлов.
Запрещены local cargo/rustc/Kani/CBMC/Miri/сборки, CI/Actions/Cloud dispatch/workflow edits, raw logs/archives/credentials,
PR/issue/комментарии и сторонние PR links. После reviewed handoff STOP.
Последняя строка: `READY <sha локального M2 Kani-кандидата>`.
