# KANI3300 Г1 STEP1 — stock-flag fork CI package (ISSUED 2026-11-13 → worker15, подготовка)

2026-11-13. **Выдано координатором worker15: подготовка пакета.** Владелец разрешил шаг 1 (≤10 normal CBMC invocations) в Tiramisu-Cake/kani.
Это верификация корректности, не security-работа. Подготовка идёт параллельно STEP0 и от него не зависит; анализ после CI учтёт STEP0, когда он будет.
Worker готовит пакет локально; пушит/запускает только координатор в Tiramisu-Cake/kani. Cloud $0, local compiler/verifier/builds запрещены.

## Source и invariants

Отчёт R3 @88ca9d0294f5e6f631117aa68f56ee1e3464398d, `PLANNER-R3-H1-REVIEW.md`, результат STEP0 (параллельно, может отсутствовать при подготовке).
Exact Kani **4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c**, treeaf28e22ec446b254cfa3a28b2882eafa58d5a458.
Stock **CBMC6.11.0** из kani-dependencies, прежний SAT backend; не использовать новый CBMC ZST/develop/profiler build.
Никаких Kani/CBMC source fixes, initializer skip, R7/R8 carrier/assigns, clause-policy изменений или G-SC.
P1/P2 exact files из kani3300/m2a/cases/; singleton roots:
P1 scalar-pfc-legal.rs/postcondition_reads_initialized_return, SHA256fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b;
P2 scalar-pfc-hole.rs/postcondition_reads_returned_hole, SHA25661fc369a6830c6ff185887b04db36139ca529e4de097c0025ce7b29c8323f759.
Input/source/checks/solver/target/unwind/property selection fixed; vary only listed encoding/slicing options.

Isolated local clone `/root/kani-fix-3300-h1-ci` и CI-only branch `uninit-ci/h1-resource-<id>` от4f64.
Existing dirty/другой pin → STOP без reset/stash; другие source clones read-only. Все source/test bytes неизменны,
CI-only allowlist workflow/helpers/frozen copies; export4f64 не смешивать с CI overlay. Один собственный workflow в CI-only HEAD,
без inherited workflow матрицы; branch-filtered push, CI-only commit без [skip ci]. Coordinator push только конечного CI HEAD.

## Матрица: не более10 normal CBMC invocations, singleton/job isolation

| ID | Root | object bits | Дополнительный режим | Роль |
|---|---|---:|---|---|
| C12-P1 | P1 |12|обычный slice-formula|профиль организаторов, legal oracle |
| C12-P2 | P2 |12|обычный slice-formula|negative companion |
| D10-P1 | P1 |10|обычный slice-formula|вторая scale точка |
| D10-P2 | P2 |10|обычный slice-formula|negative companion |
| B14-P1 | P1 |14|обычный slice-formula|третья scale точка |
| B14-P2 | P2 |14|обычный slice-formula|negative companion |
| A16-P1 | P1 |16|обычный slice-formula|matched candidate baseline |
| F12-P1 | P1 |12|Kani --no-slice-formula|slicing discriminator |
| H16-P1 | P1 |16|CBMC --arrays-uf-always|array-encoding discriminator |
| E8-P1 | P1 |8|обычный slice-formula, optional при вместимости|дополнительная scale точка |

Это не полный Cartesian product. Полные B–H×P1/P2 дали бы14 новых runs; в этом draft их нет.
Historical A16 reuse только при exact4f64/source tree/P1/flags/CBMC/binary/limits binding. R7 B0 со skip и R8 не такой baseline.
Если matched A16 действительно доступен и координатор до dispatch выбирает reuse, его slot можно заменить G16-P1 no-slice.
Подмена записана в CI-REQUEST до запуска; total≤10. Других плеч/повторов/P2@8/добавочного UF/no-slice нет без нового GO.
У E8 object exhaustion → OBJECT_CAPACITY_EXCEEDED/INCONCLUSIVE, не semantic FAIL и не опровержениеГ1; можно не запускать его,
если уже известна недостаточная вместимость. Уменьшение b расширяет offset bits и меняет derived max-allocation limit — записать их.

## Флаги и model identity

Общий Kani: `-Z uninit-checks -Z function-contracts -Z unstable-options`, прежние --exact/--keep-temps/edition2021/-Dwarnings.
Pinned Kani не имеет отдельного публичного object-bits поля: использовать **`--cbmc-args --object-bits N`** с двумя argv tokens,
что подавляет default16 через Args::cbmc_object_bits. Не писать --object-bits=N и не допускать дублей/unknown last-wins.
`--cbmc-args` потребляет остаток argv: Kani **--no-slice-formula поставить до него**, UF-always после него.
Normal arm явно используетN; H16 также явно16. Actual expanded backend argv должен содержать ровно одно effectiveN;
F/G не содержит --slice-formula, но simple_slice CBMC остаётся — это не «без slicing вообще».

Сохранить actual source/CI/test/toolchain/compiler/CBMC/solver/binary identities, flags и effective object/offset bits,
root/unit, GOTO на реальном CBMC spawn, hash и небольшой selected table dimension projection, если штатно доступна.
Связать private marker→actual symbol/assigns с relevant state writes; missing binding или ранний private frameFAIL — semantic gap.
Не выполнять лишние solver replay ради argv; не выбирать произвольный *.goto через find/head.
Предпочтительно одна build точногоKani и неизменные input/root paths; не менять состав harness между настройками.
Если model hashes различны, отличить intended backend dimensions от unrelated compile/session signatures; ничего не нормализовать в proof input.
Можно использовать exact prepared GOTO с прямым stock CBMC только при доказанной идентичности нормальному Kani argv/checks/entrypoint,
без дополнительных transforms и без baked16 tables; иначе normal singleton Kani для каждого case.

## Ограничения, outcomes и capture

Один CBMC одновременно, jobs1, max-parallel1/fail-fastfalse; case300s и watchdog6291456KiB с прежним2s sampling.
Own process-group cleanup, original exit/signal/Kani/parser/watchdog statuses отдельно; root-specific bounded stdout/stderr/receipts,
начальные phase counters и хвост/final outcome независимо, artifacts always даже при kill. Не head/grep-only и не swallowed exit.
Full bounded property inventory: IDs/class/source/description/status; complete/truncated/UNKNOWN, raw RSS KiB и time-v maxrss отдельно.
Symex steps, VCC before→after, ConvertSSA start/end/time, first CNF vars/clauses и все последующие solver rounds с номером;
не путать их с одним добавочным counter. Measurement for fit — одинаковый stage/первое законченное conversion.
Missing CNF при kill — censored observation, не0/51M из соседнего case. No repeat/adaptive retries.
Run/build/phase caps и bounded logs записать в CI-REQUEST; build error означает verification NOT_RUN.
Максимум normal CBMC wall budget10×300s=50min плюс setup/build/capture; предложить job cap150min и отдельный setup cap,
но финальные limits утверждает координатор/владелец **до** запуска. Это оценка верхней границы, не разрешение расхода.
Нормальная source4f64 build в CI, никаких local cargo/rustc/Kani/CBMC/Miri/builds/CI dispatch при подготовке.

Resource и semantics раздельны. P1 expected SUCCESS; P2 intended **payload read in ensures** FAILURE, без иных failures.
Не привязывать oracle только к var_N/суммарномуFAILED; source/class/callsite binding, отсутствие early Unsupported/frame/protocol/invalid-value.
UNREACHABLE/SUCCESS property само по себе не доказывает useful read; matched P1/P2/source-path binding обязателен.
У UF arm Unsupported/backend rejection — режим не квалифицирован, не resource fix. У всех arms capacity/model error не облегчение.
Unexpected semantic result фиксировать как отдельный blocker; не исправлять source/goldens/assumes или менять solver в этом пакете.

## Анализ/правило решения после CI — трёхзначно

Для каждого root отдельно строить зависимость first-CNF C/V отN=2^b; не смешивать P1 и P2.
Две completed точки всегда задают прямую: третья и independently counted read classes нужны для проверки, а не tautological fit.
Проверить slopes/intercepts/residuals и uncertainty; при free-version sharing использовать S,D,C изSTEP0/выводов, не универсальныйC/V<10.
STEP0 измеряетR1/R6: его D/S/C нельзя присвоить4f64 напрямую. Для4f64 counts пока UNKNOWN; fit/новые receipts квалифицируют их отдельно.
Если read classes/CFG/property set меняются, отметить piecewise workload и не выдавать один slope за постоянную модель.
No-slice уменьшает V при сохранённых useful properties → сильное подтверждение sliced-definition механизма, не уникальная causal proof.
UF response и понижение b поддерживают общий array encoding hotspot; сами не устанавливают owner/read chain.
KILL на12/10 опровергает только completion prediction; ёмкость/timeout/другие terms могут скрывать тот же механизм.
Dproxy=0 со Step0 UNKNOWN coverage не опровержение. Решение: SUPPORTED / COUNTEREVIDENCE / INCONCLUSIVE с перечислением условий.
Не объявлять после этого A3/Part1/Replace/M3 soundness доказанной и не переносить lower-bits outcome на16-bit support.
Применение12-bit профиля к реальным SmallSort roots требует отдельной вместимости/semantic/replay qualification.

## Deliverables

В `kani3300/h1-step1/`: INPUTS.json, MATRIX.json (ровно выбранные≤10 cases), CI-MANIFEST.json,
ORACLES.md, CI-REQUEST.md (caps/commands/coordinator trigger), REVIEW.md и RESULT-H1-STEP1-PREP.md (≤30 строк).
Один bounded Luna High source-only review flags/identity/oracles/budget; synthetic runner error/cap/status checks, без nested delegation.
Source diff4f64=none; local CI-only commit neutral/no-skip-ci, Tiramisu-Cake <igkharin@gmail.com>, не push/dispatch.
Research [skip ci], stage только h1-step1/, локально. Владельцу передать exact maximum normal invocations и setup/timeout budget до GO.
G-SC/новые carriers/exemption/profiler C/Replace semantic rewrite не выдаются этим файлом.
Подготовка заканчивается `READY <sha CI-only commit>`; финальные caps утверждает координатор до push.
