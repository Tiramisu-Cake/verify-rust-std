# KANI3300 T0 — bounded trace design

Статический дизайн, 2026-11-11; Cloud $0, компиляторы/верификаторы NOT_RUN; причина UNKNOWN, independent B1/B2 credit NONE.
Контракт: TASK-KANI3300-T0; прочитаны целиком cmp4/PLANNER-AFTER-CMP3-ANSWER.md (§3–6) и PLANNER-3300-SCOPE-ANSWER.md (§6,8, путь в задании).
Ниже K = исходники Kani на b1f0105c0390fb55081e3d186fa286d23867b585; M = kani-compiler/src/kani_middle; T = research/challenge-8/kani-k1/tools на KT2 3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c.

## Наблюдения и необходимые данные
Source-reported: CMP3 step1 FAIL/step4 SUCCESS; CMP4 обе direct-проверки SUCCESS на clean и CMP2. Это разные library revisions, причинность не установлена.
Важная альтернатива (б): K:kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs:407,433,442,448 — общий transformer/cache на unit, но codegen_items и global passes вызываются отдельно для каждого harness; те же точки проверены на clean f046b70644.
K:M/codegen_order.rs:50,63 и M/transform/mod.rs:152,161,301: рейтинг прогревает cache; DumpMirPass идёт после delayed-UB. Нужны фактический порядок roots, unit/stubs, cache hit/miss, создатель/последний writer body и повторная инструментация.
K:M/transform/check_uninit/delayed_ub/mod.rs:72,108,114,124,144 — initial targets из instances, points-to от starting_items, successor closure, чтение и обновление cached-body; это механизм, не доказанная причина.
Трассировать step1 и step4 до len и внутри actual IndexRange::len: monomorphized name+mangled symbol, тип, MIR stage/body hash, bb/statement/terminator, Assign rvalue (Constant/Call/Aggregate/Copy/Move), Ref/AddressOf, destination/projections, lifetime и call/return.
Для каждого relevant/irrelevant place — resolved MemLoc, initial-target witness (origin instance/location + cast-layout/copy reason), successors/intersection, needs_get и needs_set/common-ancestor witness, выбранные/пропущенные операции и причины.
Для matched functions — changed/unchanged/skipped и причина по каждой стадии; при отсутствии отдельного len/zero_to instance (inlining/const-fold) сохранить actual caller MIR и instance_absent, не выдумывать callee/assignment.
Порядок before/after Set/Copy/Get, SetStorage/SetPadding и argument/return transfers фиксировать отдельно от порядка обхода/insertion; финальный MIR CFG нужен, чтобы восстановить execution order.
Для отказа — exact property ID, caller/callee instance, call occurrence, source→generated MIR→CBMC symbol binding, object ID+offset и диапазон/mask, tracked_object_id/offset/value(R) до/после каждой операции, результат Get.
MemLoc — абстрактная allocation-site identity (K:M/points_to/points_to_graph.rs:19), не CBMC object; связать их через concrete pointer/call-frame, не по совпадению span/номера local. Object IDs разных моделей не сравнивать как равные.

## Уже существующие средства (K, файл:строка)
M/transform/dump_mir_pass.rs:27,60,65: rustc --emit=mir включает *.kani.mir (полные transformed bodies с instance/mangled name); M/transform/mod.rs:301 подтверждает post-delayed стадию.
M/transform/check_uninit/delayed_ub/mod.rs:117 и M/points_to/points_to_graph.rs:191: тот же OutputType::Mir пишет полный points-to.dot; нет function filter, relevance reasons, runtime R или гарантии отсутствия перезаписи dot.
kani-driver/src/args/mod.rs:313 и kani-driver/src/session.rs:119: --keep-temps сохраняет временные файлы, но не делает их bounded evidence.
kani-driver/src/call_single_file.rs:298: RUSTFLAGS передаёт rustc options; кандидат --emit=mir и rustc -Zdump-mir/-Zdump-mir-dir требует проверки pinned nightly в Cloud; rustc dump не заменяет Kani transformed MIR.
kani-compiler/src/session.rs:71,86 и M/transform/check_uninit/ptr_uninit/mod.rs:55: RUSTC_LOG отдельно от KANI_LOG/--log-level; существующий trace сообщает function/transform, не решения и shadow. Полные debug dumps/logs агент не читает.
kani-driver/src/args/mod.rs:228,335 и kani-driver/src/call_cbmc.rs:282,301: --no-slice-formula и --cbmc-args --trace доступны; не включать concrete-playback, который добавляет --compact-trace и может убрать hidden steps (:286–298).
kani-driver/src/cbmc_output_parser.rs:318 хранит лишь step_type/lhs/source_location/value; richer call/object binding сейчас не гарантирован. SUCCESS обычно не имеет counterexample: runtime R шага4 тогда UNKNOWN, статический CFG доступен.

## Минимальный диагностический кандидат (только предложение T1)
Отдельная opt-in delta поверх неизменного production CMP2, не исправление. Новый host-only trace collector: env KANI3300_TRACE_DIR + KANI3300_TRACE_FILTER (literal qualified-name patterns); отсутствие env — никаких diagnostics/дополнительных запросов к transformer.
Точки: compiler_interface.rs:407–450 (unit/root/order); M/transform/mod.rs:152–177 (cache provenance); delayed_ub/mod.rs:72–145 и initial_target_visitor.rs:69–125 (targets/joins); instrumentation_visitor.rs:54,160–236 (parameter seed и relevance).
M/transform/check_uninit/ptr_uninit/uninit_visitor.rs:241,422–512: storage constant mask и ordinary assignment; M/transform/check_uninit/mod.rs:121–153,157 (список MemoryInitOp до reverse insertion, emitted sites/unsupported/skip).
Сохранять pre-local, post-local/pre-delayed, post-delayed bodies из уже доступных значений, включая входящий cached-body; не вычислять body заново ради trace и не менять порядок visits/HashSet/transformations.
Фильтр payload: два target roots, crate::array::kani_cmp3 adapters, PolymorphicIter len, IndexRange::{zero_to,len}; дополнительно bounded target-origin/cache-writer witnesses из других roots. Список всех roots/unit/order всегда в header.
Формат JSONL v1: {kind,unit,root,pass,instance,symbol,body_sha,bb,stmt,place,ty,rvalue,reason,targets,ops_before,ops_after}; отдельные records cache/target/relevance/MIR/op/map/footer, стабильная сортировка только копий множеств для вывода.
Пример: {"kind":"relevance","root":"…cmp3_index_range_len","instance":"…IndexRange::len","bb":0,"stmt":0,"place":"(*_1).1","needs_get":true,"witness":"target:17"}; значения здесь иллюстративны, не наблюдения MIR.
Лимит producer: 512 records/256KiB на compiler/driver invocation, aggregate≤1MiB/run, record≤2048 UTF-8 bytes; bounded arrays и отдельный footer с seen/emitted/omitted, oversize, coverage, complete. Превышение не обрезает compiler execution, но делает trace PARTIAL/причину UNKNOWN.
Никаких вставок в harness/model/MIR, новых reads/AddressOf/assume/seed, изменения R/S/P/masks/checks. Запись sidecar без panic/изменения verifier exit; IO error явно передать в diagnostic status, отсутствие footer = INCOMPLETE.
Runtime-часть — host projection существующего некомпактного CBMC JSON stream: kani-driver/src/call_cbmc.rs и cbmc_output_parser.rs; сохранить hidden assignments/call frames/property ID и исходный step ordinal, только до выбранного отказа step1.
После cap parser продолжает drain потока без накопления diagnostic payload; не завершать CBMC и не подменять его exit. Лимиты ограничивают collector, не гарантируют размер/стоимость самого CBMC counterexample.
Связать op→generated helper-call→symbol через host side-map при emission; при необходимости точки codegen_cprover_gotoc/codegen/{function.rs:94,block.rs:21,statement.rs:468}. Не добавлять labels/instructions в модель; неоднозначный match явно UNKNOWN.
Собирать все shadow dependencies выбранного counterexample независимо от function payload filter, включая reset/retarget/buffers; library/kani_core/src/mem_init.rs:34,70,94,130,234 задаёт tracked-byte model. Это не снимок всей памяти; отсутствующие значения не додумывать.

## Bounded tooling (отдельный review и tests)
KT2:T/k1g.sh:13–17,217–251: summary — harness rows (≤80), native — compiletest rows (≤4), native-field — dotted field (≤80 units, ≤12000 bytes; T/kani_k1.py:1558–1613).
CMP3/CMP4 verify-std не имеют native report: native.json создаётся только kind=kani-tests (T/gcb-k1.sh:149, T/kani_k1.py:445). Нельзя подделать native tests для trace; существующих selectors недостаточно.
Минимальное расширение: gcb-k1.sh verify/summarize (:242,264–284) принимает строго opt-in диагностические env/args, собирает bounded compiler/driver sidecars и передаёт новый --compiler-trace в kani_k1.py summarize; embed diagnostic_trace в summary.json, не kani.log.
Новый k1g.sh trace-field BUILD FIELD [START [COUNT]] переиспользует field pager и summary-only fetch (:104–120); отдельный upload не нужен (:312–318 gcb-k1.sh). Это предлагаемый, пока НЕ существующий verb.
Envelope содержит build/head/request, library/fixture/Kani/patch/applied-tree/tooling/toolchain/actual argv hashes, trace schema/filter/hash, exact/complete/coverage/omitted и diagnostic_only; leaf≤2048 bytes, page≤20 records/12000 bytes, continuation только returned next_start.
MISSING/INVALID_JSON/OVERSIZED/timeout/identity mismatch/ambiguous binding — явные состояния; не пустой PASS/NOT_RUN. Trace не меняет status/gate/counts/original exits; отдельная trace completeness оценка, raw fallback запрещён.
До Cloud: separate tooling review + existing preflight; synthetic/service tests success/error/timeout/partial/missing/null/wrong-type/NOT_RUN, source-stage-target mismatch, cap/paging/cache identity/summary-only fetch; verdict unchanged, никаких fake native rows. Kani delta review: opt-out equivalence и opt-in MIR/GOTO equivalence на producer boundary.

## Два сопоставимых эксперимента и критерии
Один library commit 2121ff2d08d50d412c834760af925b202a1d8c01, tree 919cc3e2dc5fb19ea6e7f7be761914b949160a41; fixture uninit_probe.rs SHA256 bd6d51c7ad634644d5e8fc16b539cd84b2eedb6101d52692c4d7d0fb3545e8a6; оба набора уже в нём.
A = original CMP3 nine roots; B = CMP4 four roots; одинаковые clean pin f046b70644e113be0df9c22c2e6ea44a65a57566 + CMP2 production patch SHA256 46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4 + одна diagnostic delta/recipe. Clean-vs-CMP2 сейчас хуже: контекстный отказ не локализует.
Одинаковые nightly-2026-10-23, controls/uninit on, inventory off, standard4/jobs1/3m, trace flags/filter/caps; exact selectors в TASK-DRAFT-T1. ≤2 Builds без retries, предложенный cap $1.40: (9×3+30 + 4×3+30)×$0.0135 = $1.3365 reserve; пересчитать overhead после tooling review, cap/timeout не обходить.
(а) поддержана только если A воспроизводит step1 FAIL/B SUCCESS и связанная полная трасса показывает actual ordinary constant assignment, отсутствие нужного R write, origin-dependent delayed Get на том же object+offset/data byte и R=false, без intervening причины; проходящий step4 — contrast, не доказательство.
(а) опровергнута для этого отказа, если присваивание иное, Get относится к другому объекту либо нужный write выполнен корректно, а полный trace указывает иной transfer/reset/cache defect. Cache contamination/repeated instrumentation — отдельный результат (б).
Невоспроизведение, trace/identity/controls failure, Unsupported/timeout, неполная lineage/coverage либо только общий span → UNKNOWN; не приписывать отсутствие Get по no-match. Успех обоих не закрывает blocker; SUCCESS шага4 не выдумывает runtime trace.
T0 завершает только эти два документа, commit/push и REVIEW REQUEST; T1 draft не GO, narrow fix и дальнейшие Builds/PR/Actions вне стадии.
