# KANI3300 M2-B/R6 — Hbuf: representation/lifetime против selection/reset, worker 15

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна сессия подготовки второй пары, **Cloud $0**.
Fork CI только координатора; local compiler/verifier/builds запрещены. Это верификация корректности, не security-работа.
Следуем R5 decision tree: ≤2 дополняющих варианта внутри Hbuf, тот же P1, без нового history/одиночного перебора.

**Новый handoff:** package @54252f16e4; R6-01 run43271948094 heavy, R6-02 run43271955539 ранний
Enum Unsupported на Option reset, NON_COMPARABLE. Worker15 → TASK-KANI3300-M2BR6B.md, historical m2br6 не менять.

## Вход и новые outcomes

Читать `kani3300/m2br5/` @ **c114b13fb4bfc08502529d78c45344ec724d56f2**, HUNK-MAP/STATIC-AUDIT.py,
TYPE-AUDIT, patches и manifest; U/R1 blobs только из committed objects. Historical results не менять.
По координатору probe P1:

| Candidate / run | Props / symex steps / VCC before→after | Conversion outcome |
|---|---|---|
| R5-01 **bcc1a2af3f**, **43268005490** | 145 / 11639 / 476→182 | **846480vars/51218835clauses**, ConvertSSA8.5s, дошёл до solver |
| R5-02 **899ffb5f26**, **43268011610** | 150 / 9971 / 569→120 | >6.68GiB, killed до size print |

R5-01 **bcc1a2af3fe13599b88acabc78c33e1394407dc5** = U Hbuf + exact R1 Hcopy/GLUE, конвертируемый endpoint.
R5-02 **899ffb5f26b79e89cec1b7cc537d54be494ab390** = R1 Hbuf + adapted U Hcopy + R1 GLUE.
Данные направляют следующий cut в Hbuf; Hcopy/GLUE сохраняем R1. Это не глобальная независимость факторов,
не изоляция одного VCC/hunk и не semantic PASS: retained paths/failures/phase identities связывать отдельно.
R1/V01/R4 outcomes не повторять. Selection-only V01 не помог, но selection+reset ещё отдельный совместный cut.

## 1. Контекст, две группы Hbuf и exact siblings

Frozen parent **R1 1cd96e354ec45346b61c245554a50a8af8cb5ce7**; U reference
**bf9c58e662fd65c64381ef2ac97a6397ffc0693a**. R5 clone `/root/kani-fix-3300-m2br5` read-only.
Создать **/root/kani-fix-3300-m2br6**, root branch **experiment/kani-3300-m2br6** от R1 и sibling branches
**-epoch-u** / **-repr-u**; два local diagnostic commits, каждый direct child R1. Existing/dirty destination → STOP без reset/stash.
Scope только **library/kani_core/src/mem_init.rs**. Compiler/contract.rs/macros/tests/driver/toolchain и модельные signatures
не менять. Release/M1/M2/S3/worker14 source не трогать; Kani не пушить, candidates NOT_RELEASE_CANDIDATE.

Hbuf разделить на:

- **Hrepr**: где/в какой форме хранится buffer, поля/constructor, pointer Option против captured IDs, store payload writes,
  paired load/match/layout-check/consume, lifetime и DFCC membership. Capture/consume остаются согласованными.
- **Hepoch**: store selection (`any()` против mandatory index0) и buffer invalidation в initialize_memory_initialization_state.
  Constructor inactive default относится к Hrepr; matched consumption относится к Hrepr; epoch-reset — отдельная операция.

В HBUF-MAP привязать новые subgroups к R5 atoms D01–D03,D13–D18, разрезав composite D15 только по coherent operations.
Это source-bound conceptual cross-cut с маленьким reset/type adapter, не механические50% строк.
Во всех случаях **copy/copy_by_id/bless/bless_by_id и весь Hcopy/GLUE exact R1**, проверить bytes/hashes.

### R6-01 — R1 Hrepr + U Hepoch

R1 marked main state со scalar ID/offset buffer, constructors, store capture и load полностью сохранить.
Изменить только store selection на demonic any-only (как V01) и **удалить только**
`MEM_INIT_STATE.argument_buffer_active = false` из initialize_memory_initialization_state.
Остальные tracked object/offset/value initialization и все normal matched-load clears остаются R1.
Опциональная source-form any-only через U's bool local должна быть явно учтена; никаких других hunks.
Эта пара проверяет совместный selection/reset cut, не повторяет V01. После initialize buffer может остаться active/stale;
false transfer/mandatory return/epoch guarantee потеряны диагностически, нельзя трактовать legal PASS как acceptance.

### R6-02 — U Hrepr + R1 Hepoch

Взять exact R5-01 runtime как промежуточный source template (R1 Hcopy/GLUE там уже сохранены), затем **только**:

1. U pointer-buffer store сделать mandatory index0: `selected_argument == 0 || super::any()` вместо demonic-only;
   удалить теперь ненужный should_store local, если исходная U source-form его содержит.
2. В существующем unsafe block initialize добавить **ARGUMENT_BUFFER = None** как type-correct counterpart R1 active=false.

Сохранить отдельный **unmarked** `Option<ArgumentBuffer>`, Clone+Copy record(index:usize,saved_address:*const (),layout_size:usize),
U capture/consume и matched clear. Никакого нового private marker/assigns extension/R4-A registration.
Store/load API по-прежнему два arguments; pointer load через copy_init_state_single→R1 copy/by-ID helpers.
Saved pointer может пережить source return slot; unmarked writes/reset могут давать frame/Unsupported/invalid-source issues.
Это известные diagnostic limitations U Hrepr, не допустимый production rollback. Reset location/frame scope подтвердить по inventory.

Проверка coverage: инверсия только Hepoch edits у R6-01 восстанавливает exact R1; у R6-02 — exact R5-01.
Hrepr U + Hepoch U даёт существующий конвертируемый R5-01; R1/R1 — heavy R1. Новых общих runtime/API glue кроме
активность↔Option reset mapping быть не должно; любой дополнительный executable delta перечислить и обосновать до review.
Не пытаться реконструировать pointer из object ID, заменять copy model или добавлять assumptions для компилируемости.

## 2. Source/type/compile audit

Проверить constructors/все field accesses/static declarations, reset/consumption coverage и правильные unsafe blocks.
Все14 existing fn_marker declarations/13 model functions, normalized generic/API signatures и arities сохранить;
model callers/markers и Hcopy/GLUE source closure по exact commits, не по рабочей копии.
TYPE-AUDIT: any() inferred bool; selected_argument/literal0 оба usize; `None` выводится из `Option<ArgumentBuffer>`;
Clone/Copy/Option reads, *const T→*const (), borrow/deref/static_mut и usize/u64/u128 boundaries проверить явно.
Rustfmt/Luna не compiler (урок B3 E0308/E0277); первые fork builds проверяют actual types/-D warnings.
Local cargo/rustc/Kani/CBMC/Miri/builds нельзя. Разрешены source/hash/Python checks, diff --check, pinned rustfmt wrapper TASK-M1.
Один bounded Luna High review dependency/coverage/type audit и outcome logic, без nested delegation/полного seed audit.

## 3. Первая и единственная CI очередь этой стадии

**Только R6-01/P1 и R6-02/P1**, sequential inventory/build→admitted solver, без P2/new baselines/retries/full matrix.
P1 source SHA256 **fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b**,
root `postcondition_reads_initialized_return`; те же bytes/actual argv/env/target/toolchain/solver/checks/PFC/uninit/object-bits/
slicing/inlining/unwind, кроме manifest deltas. Existing timeout300s/watchdog>6GiB; sampling/overshoot/PID/RSS units/exit сохранить.
Reuse R1 и R5-01 existing receipts. Build error → solver NOT_RUN, cutoff → INCOMPLETE; parser/job status не verdict.
Per candidate: source/tree/input hash, GOTO/functions/props/eloc, steps/VCC, ConvertSSA start/end/runtime,
vars/clauses если доступны, SAT-entry и bounded complete Failed Checks с IDs/location/class/coverage.
Особенно selection0 guard, buffer reset actual location, pointer-vs-ID load, marked/unmarked writes и retained DFCC targets.
No-match/cap — UNKNOWN; raw logs/archives/full equations не читать/качать. Existing bounded property/type query recipes допустимы,
новый runner/backend/export framework или broad trace не создавать. Diagnostic show-vcc не full verification.

Если только R6-01 конвертируется — следующий кандидатный interval Hepoch (joint reset/selection), не single selection.
Если только R6-02 конвертируется — Hrepr/lifetime/private-membership interval; placement vs pointer capture ещё не разделены.
Если оба/ни один — interactions/changed paths/type adaptation проверить по known endpoints, без monotonicity premise.
Любой ранний frame/Unsupported/invalid-source path меняет obligations: численная relief не автоматически causal fix.
Дальше только отдельный handoff координатора; третий вариант/production repair не готовить автоматически.

## Результат и STOP

g0 **kani3300/m2br6/**: INPUTS.json, HBUF-MAP.md, ABLATION-PLAN.md, DIAGNOSTIC-MANIFEST.json,
TYPE-AUDIT.md, patches/, STATIC-CHECKS.json, REVIEW.md, CI-REQUEST.md, RESULT-KANI3300-M2BR6.md (≤25 строк).
Source predictions/observed bindings/reported outcomes разделять. Компилируемость — audited/NOT_RUN до CI;
никакого release-ready/полной причинности или нового proof credit. M3/интеграция/тяжёлые M2 selectors пока HELD.
Local diagnostic commits без [skip ci], author/committer Tiramisu-Cake <igkharin@gmail.com>, **не push**.
Research [skip ci], тот же author/committer, stage только m2br6/, push g0 без force; concurrency → handoff без reset/stash/чужих файлов.
Без CI/Actions/Cloud dispatch/workflow edits, credentials, PR/issue/комментариев/сторонних PR links.
После двух reviewed candidates STOP. Последняя строка: `READY <sha research-коммита M2-B/R6>`.
