# KANI3300 M2-B/R3 — R1 expression delta и bounded hunk-ablation, worker 15

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна аналитическая/подготовительная сессия,
**Cloud $0**. Fork CI только координатора; local compiler/verifier/сборки запрещены.
Это верификация корректности, не security-работа.

## Вход и уже измеренная граница

Читать `kani3300/m2br2/` @ **6a69089695**, прежние m2br HISTORY-MAP/FRAME-BINDINGS и M2-A inputs P1/P2.
Full researchSHA/tree/input hashes записать в INPUTS; исторические результаты/очереди не переписывать/повторять.
По координатору matched probe inventory+solver, P1/P2, watchdog CBMC RSS>6GiB:

| Source / run | GOTO / props / eloc | Symex steps / VCC before→after | Outcome |
|---|---|---|---|
| R1 **1cd96e354**, **43252928887** | 232KB / 144 / 247 | 10005 / 509→120 | >6.3–6.8GiB за10–11s, killed |
| A1 **613c188313**, **43252936014** | 239KB / 160 / 239 | 11348 / 699→186 | >8.1GiB за10s, killed |
| Upstream **bf9c58e662**, **43253856019** | 222KB / 159 / 230 | 4908 / 222→66 | watchdog не сработал; прежний run46s/1.4GB, frameFAIL |

Не переносить старые46s/1.4GB в новое измерение без receipt; per-P1/P2 split/units/timestamps сохранить либо UNKNOWN.
R1 **1cd96e354ec45346b61c245554a50a8af8cb5ce7** — один commit поверх upstream
**bf9c58e662fd65c64381ef2ac97a6397ffc0693a** (проверить parent и rev-list count1).
History bisect завершён на этом интервале; A1/A3/B1I/M1 не нужны для воспроизведения. Дальше — hunks R1, не ещё pins.
Скачок RSS при умеренном росте steps/VCC указывает на нелинейную encoding cost; huge width/object — гипотеза,
не обязательное следствие. Выделять width **и** operator/multiplicity, retained guards/path, phase и conversion growth.
Upstream frame/Unsupported всё ещё не semantic PASS; одинаковые input bytes не гарантируют эквивалентные obligations.

Worker14 и concurrent `kani3300/m2bs3/`/иные source/research changes не трогать. Seed/semantic gate отдельно; M3 HELD.

## 1. Что именно добавляет R1 — source/GOTO/props → VCC/expression

Exact source смотреть через git objects U/R1 в `/root/kani-fix-3300-m2`, **не брать dirty worktree за R1**.
Использовать existing curated goto-functions/props/type projections этих двух runs; отсутствие данных оформить узким запросом.
Нельзя статикой выдать фактически emitted VCC: каждая строка SOURCE_PREDICTED / EMITTED / RETAINED_VCC / UNKNOWN.

Создать DELTA-MAP: matched property/instance/source-op → U/R1 GOTO statement/type/guard/callsite → normalized expression
и operand/result width → VCC/SSA use, если имеется. IDs/SSA names между pins нестабильны: матчить по origin/location,
diagnostic/class/instance и форме operands, сохранять unmapped/many-to-one. 144 props и120 VCC — разные сущности;
не считать разницу totals множеством новых checks и не выводить отсутствие из no-match/partial projection.
Особенно сопоставить reached store/load, return0, writes/reads/transmute/constant storage и actual DFCC helper operations.

R1 меняет семь production files: `check_uninit/{mod.rs,relevant_instruction.rs,ty_layout.rs,ptr_uninit/mod.rs,
ptr_uninit/uninit_visitor.rs,delayed_ub/mod.rs}` и `library/kani_core/src/mem_init.rs`.
Разделить source clusters и отметить **реально достигнутые P1/P2** hunks, а не весь общий diff:

- buffer migration в marked MEM_INIT_STATE, saved pointer→object/offset, copy_by_id/bless_by_id и range arithmetic;
- mandatory selected_argument0 store и новые return-slot store/load/arg-scope producers;
- MU/flat storage recognition, SetStorage constant materialization/masks, AssignUnion effects;
- CheckRefAs/typed transmute/reference paths, layout selection и emitted Layout<N> instances;
- frame/assigns/DFCC/capture/havoc/snapshot use вокруг изменённого private object (contract.rs source не менялся).

Source MEM_INIT_STATE — scalar fields, не huge embedded array. `usize::MAX` value не array length.
Rank до10 новых/изменённых retained expressions по actual width/operator cost с owner/use; большие declared types
без retained use — suspects, не причина. Если widths/VCC coordinates нет, дать конкретные missing projections и source candidates.

## 2. Отдельный diagnostic clone и план до четырёх вариантов

Создать **/root/kani-fix-3300-m2br3**, ветку **experiment/kani-3300-m2br3** от exact R1; U read-only reference.
Existing/dirty destination/другой pin → STOP без reset/stash. Release clones/worker14 branches не менять.
До CI подготовить ABLATION-PLAN и dependency-complete patches; допустимы local diagnostic commits V01–V04 на **отдельных
ветках от того же R1**, не накопительная цепочка. Каждый pin/tree/diff/hash и purpose в manifest. Не более4 modified variants.
Не строить cfg framework/новую ABI. Предпочесть1–2 наиболее различающих готовых варианта; остальные DRAFT/DEFERRED,
если source/binding/type audit недостаточны. DRAFT не включать как runnable в CI-request.

Предлагаемые семьи (конкретный hunk subset выбрать по DELTA-MAP, а не автоматически отключить всё):

| Family | Что изолирует / dependency boundary |
|---|---|
| Runtime group | Coherent U↔R1 mem_init representation/copy/store/load bundle при неизменном compiler emission; сначала проверить model marker/API signatures. Whole-file runtime rollback — group discriminator, **не** отдельное доказательство buffer-size причины. Старый pointer buffer/return lifetime/новый return0 semantics могут стать неполными |
| Return selection | Узкий `selected_argument == 0 || any()`→legacy demonic selection в store_argument при прочих R1 hunks; lost mandatory return0 и actual selected path явно учесть. Не объявлять source-following false сохранённым автоматически |
| Return emission/scope | Убрать только новые matched return0 producers+consumers либо отдельно реально расширенный transfers_shadow scope, оставив compatible argument indices/legacy checks. Caller/callee/normal continuation должны быть согласованы; не revert visitor отдельно от required plumbing |
| Storage/read effects | Один reached cluster SetStorage/constant materialization/for_storage или CheckRefAs/transmute, с точными producer→enum/layout→instrumenter consumers. Не смешивать оба clusters без маркировки composite; сохранить compile plumbing/tcx и enum exhaustiveness либо revert весь API dependency bundle |

Это верхняя граница четырёх variants, не требование реализовать все семьи. Если hunk не достигается input, он не кандидат первой
очереди. Runtime rollback может вернуть frame/Unsupported: это changed-obligation diagnostic, не comparable speedup.
Нужный frame-only calibration предложить **вместо** одного из четырёх, а не пятый вариант; verifier-private target не user memory.
Не удалять только copy_by_id при оставленных saved-object callers, только enum variant при оставленном producer или
только layout helper, используемый storage+transmute. Проверить все signatures/markers/calls и semantic loss до runnable SHA.

Для каждого: exact hunks, hypothesis, expected model difference, retained/lost check/transfer/frame obligations,
predicted falsifier, build risks, extra failure/Unsupported expectations и какие выводы **нельзя** сделать.
Диагностическое удаление checks/эффектов возможно только в этих isolated NOT_RELEASE_CANDIDATE variants;
никаких новых assume/bless/ослабленных goldens, никаких cherry-pick в release. Возврат памяти без retained causal use
либо из-за раннего Unsupported/frame exit не устанавливает исходную причину. Hunk interaction/non-monotonicity сохранить.

## 3. Ограниченная статистика CBMC в существующем probe

Источник declared CBMC —6.11.0; actual version/binary/solver и effective argv сверить у координатора.
Primary source: [bmc_util.h](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-checker/bmc_util.h) объявляет
`--show-vcc`; [symex-only checker](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-checker/single_path_symex_only_checker.cpp)
выводит equation без принятия solver decision. Route выбора этого checker/installed options проверить, не обещать proof verdict.
[bmc_util.cpp](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-checker/bmc_util.cpp) различает converting SSA,
convert_goals и solve: сообщение Passing problem to solver само по себе не SAT-start.

Kani `call_cbmc.rs::cbmc_flags` добавляет `--verbosity 9` **после** --cbmc-args; не считать override через pass-through
сработавшим без проверки итогового argv/CLI precedence. `--cbmc-args` последний Kani flag, требует -Zunstable-options;
regular mode добавляет JSON UI, поэтому non-verifying/show-vcc output может не соответствовать Kani result parser.
Подготовить version-validated recipe для **координатора** поверх того же saved post-DFCC model и expanded backend argv,
без release-driver patch/нового runner. Verbosity сначала9,10 только если source показывает нужную дополнительную статистику.

Запросить existing milestones/time/RSS: symex/postprocess, convert SSA/assignments/assertions/goals, conversion end,
observed Boolean literals/variables/clauses и SAT-entry; unavailable counts UNKNOWN, не выдумывать --formula-size flag.
`--show-vcc` — отдельный **non-solving diagnostic**, не измерение CNF/bit-blasted size и не successful verification.
Сначала2–3 mapped suspect property IDs U/R1, property-filtered diagnostic отмечать как изменённую equation без full proof credit.
Только bounded projection: ≤20 VCC/expression rows, IDs/source/operator/type/width и aggregate counts; огромные expressions
с truncation/hash/coverage, не full formula/log. Output/time/RSS cap существующего probe сохранять; не читать/качать raw dumps.
Не останавливать verification pipe head/SIGPIPE и не принимать его exit за verifier outcome. Если existing curated path не может
выдать projection, вернуть precise limitation/query recipe; без нового backend/trace/export framework в этой стадии.

## 4. CI очередь, проверка типов и результат

CI-request — максимум4 **runnable modified variants**, P1 первым, один root/process за раз. Immutable P1 SHA256
fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b, P2
61fc369a6830c6ff185887b04db36139ca529e4de097c0025ce7b29c8323f759; exact roots/flags из m2br CI-REQUEST.
U/R1 baseline reuse43253856019/43252928887; только недостающие mapped diagnostic observations, не новые history rebuilds.
Первый batch — inventories/build и P1 на1–2 лучших variants; P2/оставшиеся варианты только после отдельного handoff/admission,
не полный variants×P1×P2 product. Existing timeout300s/watchdog>6GiB, sampling/overshoot/raw units/PID/exit/phase record.
Checks/target/solver/object-bits/slicing/inlining/unwind/input bytes одинаковы вне manifest's explicit diagnostic delta.
Build failure — NOT_RUN solver; cutoff — INCOMPLETE; parser/job success не semantic PASS. Изменённые obligations перечислять.

Обязательный **TYPE-AUDIT.md** каждого Rust delta: operand/result/API types, обе стороны arithmetic/comparison,
usize/u64/u128/deref/mutability и conversion bounds, enum/call/marker completeness. Учесть B3 E0308/E0277:
rustfmt/Luna не compiler, первый fork build проверяет типы. Local cargo/rustc/Kani/CBMC/Miri/builds запрещены.
Разрешены source/hash/Python/diff --check и pinned rustfmt-обёртка из TASK-M1; independent bounded Luna High review
dependency-complete patches и lost-obligation logic, без nested delegation/полного seed audit.

g0 **kani3300/m2br3/**: INPUTS.json, DELTA-MAP.md, ABLATION-PLAN.md, DIAGNOSTIC-MANIFEST.json,
TYPE-AUDIT.md, CBMC-RECIPE.md, CI-REQUEST.md, REVIEW.md, RESULT-KANI3300-M2BR3.md (≤25 строк).
Ready candidate/patch ≠ compiled; predicted vs observed отдельно. Если runtime/VCC evidence отсутствует, не заявлять causality:
дать reviewed runnable/request package, затем STOP до fork CI координатора. M3/release gates остаются HELD, proof credit0.
Diagnostic Kani commits нейтральные, без [skip ci], author/committer Tiramisu-Cake <igkharin@gmail.com>, **не push**.
Research [skip ci], тот же author/committer, stage только m2br3/, push g0 без force; concurrency → handoff без reset/stash/чужих файлов.
Без CI/Actions/Cloud dispatch/workflow edits, raw archives/full logs/credentials, PR/issue/комментариев/сторонних PR links.
Последняя строка после reviewed package: `READY <sha research-коммита M2-B/R3>`.
