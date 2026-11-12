# KANI3300 M2-B/R8 — pointer-carried witness snapshot, worker 15

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна дизайн+реализация/review сессия, **Cloud $0**.
Fork CI только координатора. Это верификация корректности, не security-работа.
Worker15 — source owner;14 параллельно готовит two nonzero-offset Move/return controls по TASK-KANI3300-M2BR8-CONTROLS.md.

## Вход и база с уже импортированными R7-C tests

Читать m2br7/{DESIGN.md,MODEL-MAP.md,SOURCE-MANIFEST.json,TEST-MANIFEST.json,RESULT-KANI3300-M2BR7.md},
m2br7c/ и R6b proof limitations.
По координатору P1/P2: B0 c614dba9ca/run43283061769 —292props,11700steps,841→147VCC,>6.39GiB,killed;
B1 b4eb8294b7/run43283068930 —292props,18099steps,877→147VCC,>7.24GiB,killed; P2 так же.
R7 split/scalar-target candidate не снимает resource gate. R6-02b raw-pointer diagnostic решаем50s/1.95GB, но frameFAIL.
Это empirical representation discriminator, не установленная причина стоимости конкретного operator/SSA expression.
Текущий A3 B1 уже не хранит абсолютные source object/offset: числовой witness carrier — relative_offset плюс has_witness/value.

Base **8e01eb2aff5183c53403e1d1e73e573ce28d3095**, tree **8554b019e0eb8d2daf09e5ab70bc0c0d09917de1**,
read-only `/root/kani-fix-3300-m2br7`: B1 source + exact R7-C test delta
**fe36afc4a8de2709f00524b2d3fbd6da17919728**. Эти4 files/2selectors уже присутствуют, не cherry-pick второй раз.
Создать **/root/kani-fix-3300-m2br8**, branch **fix/kani-3300-pointer-transfer-carrier** от exact base.
Existing/dirty destination/другой pin → STOP без reset/stash. Не начинать от старого R1/R6 pointer-runtime или filtered CI tree.

## 1. Дизайн: pointer encoding, а не позднее чтение source state

Перед кодом DESIGN.md: отношение current→new model и условия metadata lemma. Сохранить A3 protocol/ABI целиком:
active/index/signature/count/written/remaining/order/layout, mandatory return0, demonic argument selection, typed masks,
no-witness отдельно от captured value=false. Ни одного new assume/default true/missing-protocol fallback/индексного усечения.
Main witness object/offset/value и M1 immutable registry/reset-completion seeds остаются прежними.

**Выбранный carrier:** в separate marked ArgumentBuffer заменить только `relative_offset:usize` на
**saved_base:*const u8** и **saved_byte:*const u8**, сохранив has_witness и captured value. Остальные protocol fields неизменны.
Постоянного numeric source ID/offset/relative в buffer больше нет; локальная арифметика в trusted models разрешена.
Raw pointer здесь — носитель metadata, не разрешение читать умерший source. Само хранение dangling raw pointer не требует dereference.

**Store, пока source жив и до Move/deinit:** existing source-match predicate сохранить; snapshot has_witness/value в locals
снять до дополнительных helper calls. Только в selected&&has_witness path вычислить исходный relative (tracked_offset-from_offset),
saved_base=from_ptr.cast::<u8>(), saved_byte=saved_base.wrapping_add(relative) в байтах. has_witness подразумевает relative<N.
Не вводить reference к uninitialized payload. В false/no-witness/zero-extent path pointers не декодировать и byte-add не выполнять;
задать безопасное fully initialized pointer payload/constructor null, но flag/value не смешивать с sentinel.

**Load, тот же source-following demonic branch:** восстановить relative только из Kani pointer_offset(saved_byte)
минус pointer_offset(saved_base), с явно выбранной target-width wrapping arithmetic и guards. Retarget **к live to_ptr**,
value=captured_value && layout[relative] как B1. Никогда не retarget к saved source pointer.
Запрещены source .read/.as_ref/.offset_from, copy_init_state_single(saved_source,...), is_allocated/object_size для codec
или повторное чтение MEM_INIT_STATE.value вместо capture. Codec inline внутри уже SKIPPED Store/Load models;
новый обычный helper может сам попасть под uninit instrumentation — такого обхода здесь не нужно.

### Metadata/round-trip lemma — обязательная часть design/review

Primary CBMC6.11 sources:
[pointer encoding](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/solvers/flattening/bv_pointers.cpp)
(:675–713), [DEAD](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-symex/symex_dead.cpp)
и [return/pop_frame](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-symex/symex_function_call.cpp)
(:387–453). Kani hooks в overrides/hooks.rs прямо создают PointerObject/PointerOffset expressions без dereference/live check.
В данном BV backend metadata — slices pointer bits; DEAD/frame cleanup удаляет local SSA names, не переписывает stored globals.
Поэтому «pointer_object/offset перебирают все объекты» не установленный механизм: эти операции сами — bit extraction;
возможная цена compound formula/других operators остаётся открыта. Actual backend/version/flags/binary identity подтвердит CI.

В lemma связать live formation→same-object base/byte→точный relative→stable stored pointer values через Move/return→decode.
Source death не даёт права читать source bytes/shadow. Pointer-offset encoding width может быть меньше usize width:
не считать wrapping_add автоматически lossless. Нужны non-vacuous store round-trip/same-object checks и load same-object/
relative<N invariants, **не assumes**; ложный guard не превращать в no-witness/bless. Не добавлять N≤32/u32 truncation.
Показать, что existing backend-admitted valid source extents удовлетворяют carrier relation; новый отказ на прежде допустимом
representable valid case — blocker, а не скрытое narrowing Part1 scope. Zero extent не декодирует saved carrier pointers;
ненужные live-source metadata operations можно исключить только с обоснованием same no-witness/protocol outcome.
Отношение: old/new has_witness/value и protocol одинаковы; на selected&&has_witness old.relative_offset=decode(new pair).
Inactive/no-witness pointer payload не наблюдается. Pointer metadata на иных backend/version не объявлять доказанной без binding.
Если lemma не удаётся установить по pinned implementation/guards, STOP с точным counterexample/proof gap и дешёвым
альтернативным encoding proposal; не переносить legacy pointer-copy algorithm ради benchmark PASS.

## 2. Private state/frame boundary и scope

Разрешённые source sites — **mem_init.rs** и **codegen_cprover_gotoc/codegen/contract.rs**: update new field types/list.
Bootstrap skip/B1 private markers/partial epoch reset/caller instrumentation и source S3 fixes сохранить; M1 finalizer unchanged.
Main marker unique, buffer marker distinct, оба actual globals обязательны в relevant PFC model.
R7 field-target policy сохранить: заменить один numeric field target двумя pointer-field **cell lvalues**.
Тarget относится к cell в ARGUMENT_BUFFER, **не** к pointee/source allocation. Никакого deref/object_whole(saved_pointer),
pointer-value range exemption, user-memory target или blanket frame skip. Подтвердить emitted target address/extent/object.
Expected set теперь13 buffer fields; число lambdas не2. Проверить actual *const u8 IR type, не подставлять void-pointer type
по аналогии с hook's local cast и не превращать target lvalue cast-ом в rvalue.
Конструктор null payload, store/clear/reset fields и all ordering checks source-audit; pointers можно оставлять inactive,
но любые reads только под выбранным valid witness. Scope не расширять на ABI/layout/alias/Move/DFCC backend/core-witness rewrite.

## 3. Controls, CI и условие перехода к M3

R7-C reuse без изменений: existing scalar P1, lawful_modifies, existing P2/postcondition-hole и mapped frame/clause/false controls.
Worker14 добавляет только2 ordinary nonzero-offset NoCopy MU controls. Импортировать его exact new-path-only test delta,
не source base; если ещё не READY — composition request, без дублирования/ожидания его сессии.
Не сохранять новый numeric ghost relative в release buffer ради тестов: это вернёт исследуемое представление.

G1 coordinator: build/fmt/clippy → unchanged P1 first (hash fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b),
one root/solver, existing300s/>6GiB watchdog. B0/B1 baseline receipts reuse, не новые variants/исторические reruns.
Если P1 опять heavy — STOP, bounded formula/use diagnosis; никаких pointer-validity assumptions/дальнейшего скрытого weakening.
После P1 — P2(hash61fc369a6830c6ff185887b04db36139ca529e4de097c0025ce7b29c8323f759), R8-C legal/hole, lawful/frame/clause,
existing call-pairing/move/padding/false controls. Round-trip/model guards должны быть SUCCESS, legal all SUCCESS,
P2/ordinary-hole — intended payload read FAILURE, frame-negative — user outside write, no private assignableFAIL.
Actual before-Move capture/return-death/normal load/ensures path и pointer **cell** assigns binding обязательны;
VCC presence/source predictions не полное reachability/semantics evidence. Early Unsupported/model-guard/frame/path loss не relief.
Per case полный bounded failure inventory, source/tool/argv/config identities, steps/VCC/conversion/vars/clauses/RSS/exit,
sampling/overshoot/raw units. Cutoff INCOMPLETE, setup fail NOT_RUN solver, parser/job status не proof.
G2 только после accepted G1: полный Uninit Quick +unit5/kani Uninit/expected/ui/reinstrumentation,
**без исключения legal-pair/postcondition-hole**. Existing fixtures/goldens не смягчать. Full tool/platform gate/SmallSort replay позже.
Смена generated IDs в старых goldens — только observed source-bound update после CI, не generic frameFAIL acceptance.

## Review, результаты и STOP

TYPE-AUDIT: source pointer cast/wrapping_add, hook usize vs backend ssize_t/offset bits, guards and arithmetic,
null const construction, borrow/unsafe/model signatures, pointer field IR types/targets. B3 E0308/E0277: rustfmt/Luna не compiler.
Один bounded Luna High review relation/metadata lemma/false propagation/lifetime/frame cells; concrete findings исправить,
без nested delegation. Пinned rustfmt TASK-M1, diff/source/hash/Python checks разрешены, local cargo/rustc/Kani/CBMC/Miri/builds нельзя.
g0 **kani3300/m2br8/**: INPUTS.json, DESIGN.md, CARRIER-LEMMA.md, MODEL-MAP.md, TYPE-AUDIT.md,
SOURCE-MANIFEST.json, TEST-MANIFEST.json, REVIEW.md, CI-REQUEST.md, RESULT-KANI3300-M2BR8.md (≤25 строк).
Source-ready ≠ compiled/proved/дешевле; source-reported outcomes и independent bindings отдельно, proof credit0, M3 HELD до G1/G2.
Local Kani commits нейтральные, без [skip ci], author/committer Tiramisu-Cake <igkharin@gmail.com>, **не push**.
Research [skip ci], тот же author/committer, stage только m2br8/, push g0 без force; concurrency → handoff без reset/stash/чужих файлов.
Без CI/Actions/Cloud dispatch/workflow/runner edits, raw logs/archives/credentials, PR/issue/комментариев/сторонних PR links.
После reviewed candidate/composition STOP. Последняя строка: `READY <sha локального R8 source-кандидата>`.
