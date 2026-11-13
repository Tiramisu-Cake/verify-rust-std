# KANI3300 M3 JSON — capture, review, binding (DRAFT / NOT ISSUED)

2026-11-13. Worker15 готовит capture/review package, CI выполняет координатор. Это верификация корректности, не security-работа.
Только черновик. Без выдачи, local cargo/rustc/Kani/CBMC/Miri/builds, CI/Cloud dispatch, push и публикаций.
Preparation Cloud $0. Read-only base `aac27ed95364989bc045e5cdc227f2a97448f955` в `/root/kani-fix-3300-m3`.

## Один согласованный захват после source fix

Сейчас семь `roots.json` entries — BINDING_PENDING; обычный test.sh fail-closed до Kani. Это pre-binding gate,
не семь verification FAIL и не compiler regression. Capture следует делать на reviewed M3-R2 source после guard/fixes:
координатор передаёт exact source SHA/tree, unchanged mixed.rs SHA, checker/schema/manifest hashes и tool binary identity.
Захват на старом aac ради последующего нового compiler head потребовал бы повторения bindings; не делать лишний run.

Подготовить отдельный CI-only overlay/request, не менять source W14. Собрать pinned Kani штатным fork recipe,
на профиле mixed fixture object-bits12/jobs1, без solver/check/slicing ослаблений. Одна CI job, последовательно:
`./test.sh --collect-unbound --keep-output` в `tests/json-handler/uninit-part1-composition/`.
Runner уже содержит7 isolated invocation +2 all-root selector orders +2 cycle/legal pair orders =11 invocation;
не размножать это в матрицу11 jobs/повторные сборки. Per-invocation180s текущего runner, timeout/OOM — STOP, не retry-to-green.

CI wrapper должен:
- закрепить matching kani на PATH/`--kani`, environment/actual argv, source/export hashes, binary/toolchain/dependency versions;
- задать task-specific TMPDIR под artifact workspace до запуска, чтобы все retained temp directories были найдены;
- сохранить original script exit, stdout/stderr, `capture.json`,11 `receipt.json`,11 exports и regular outputs,
  включая полные failed properties/Unsupported inventories; hashes/manifest artifacts и после отказа (`always`);
- использовать принятые bounded caps и process-group watchdog, без grep/head потери нужных rows;
  truncation/missing/incomplete явно UNKNOWN и pre-binding STOP, без raw archive downloads для обычного review.

Ожидаемый capture outcome — exit2 **и** report status UNBOUND_CAPTURE при полном coverage11/11 и Python24/24.
Shell wrapper может классифицировать это как успешно собранный диагностический пакет, но обязан сохранить original2
и отдельный `qualification=NOT_RUN`. Не считать любой exit2/зелёный step PASS; failure до complete capture — FAIL/UNKNOWN.
Existing runner сравнивает singleton/combined inventories уже в capture; если остановится раньше — разобрать точное drift,
не отключать comparator ради получения полного PASS. Partial receipts/exports всё равно выгрузить.

## Review → binding, без auto-learn

После координаторского bounded reporting handoff review всех семи isolated roots и каждой combined selection:
root/source/hash/line, actual mode/selected body, complete checks с IDs/classes/sites/statuses,
failure kind, полная failed-property metadata и точная Unsupported inventory. Actual stdout assertion не заменяет export.
Legal roots требуют meaningful reached checks/ensures и no extra failure; immutable/PFC negatives — intended uninit-read;
cycle — точный cycle Unsupported, не arbitrary FAILED, не legal proof. Source-operation binding задать до записи inventories.
Сопоставить весь multiset isolated/combined, не только FAIL; lost/extra check или unrelated legal contamination — STOP.
Если compiler/review исправляет semantic defect — source freeze заново и новый capture на исправленной голове,
а не blessing полученного bad output. Никаких wildcard/substring goldens и автоматического копирования снимка как истины.

После review заполнить exact `expected_inventory`, `expected_failure_kind`, `expected_failures`,
`expected_unsupported_inventory`, перевести все7 bindings в REGRESSION_BOUND. Сохранить review/capture identities в research,
не возвращать research URL в export README; manifest не должен ссылаться на недоступный внешний research для работы теста.
Synthetic tests включают lost/extra/status/root/failure/Unsupported drift, source hash mismatch и pending fail-closed.

Фиксированный mixed.rs и compiler из capture + reviewed manifest/checker образуют новый export C1.
**Потом требуется обычный `./test.sh` без collect-unbound**, Quick и полный gate на exact C1; capture не заменяет этот запуск.
Изменение только ожиданий не даёт нового semantic evidence; изменение input/compiler отменяет старую привязку.
Actual producer order — отдельный receipt: CLI AB/BA не доказывает codegen AB/BA. До обоих observed orders оставить
ORDER_UNCONTROLLED / no matched-order credit, даже если обычный inventory test PASS. Не изобретать обход этого gate.

## Scope и handoff

Worker15: CI-only overlay/request, `tests/json-handler/uninit-part1-composition/roots.json` и bounded comparator tests/docs
только по review; не compiler/runtime и не Rust fixtures W14. Нужен parser/model/schema fix — отдельный STOP/review.
Research `kani3300/m3-json-bind/`: INPUTS, CAPTURE-REQUEST, ROOT/PROPERTY-BINDINGS, ORDER-STATUS,
REVIEW, CI-QUALIFICATION-REQUEST, RESULT с отдельными capture/binding/ordinary-test/Quick/full-gate статусами.
Commit/push только после отдельной выдачи и в заданных координатором границах. Сейчас **DRAFT / NOT ISSUED**.
