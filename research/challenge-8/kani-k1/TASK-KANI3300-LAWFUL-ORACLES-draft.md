# KANI3300 LAWFUL-ORACLES — R7-C positive and exact negative inventories (DRAFT / NOT ISSUED)

2026-11-13. Предлагаемый worker14, одна implementation/preparation session. **Не выдан.**
Это верификация корректности, не security-работа. Сейчас только черновик; не создавать ветку, не менять код, не запускать ничего.
После отдельной выдачи: local cargo/rustc/Kani/CBMC/Miri/builds запрещены; Cloud $0; CI/push/запуск — координатор после GO.
Никаких raw-log downloads, вложенных агентов, source push или публикаций.

## 1. База, результат предшественника, разделение работ

Exact source base: `ee2695e5a2c4c2d8ead7a511e0f3f6f2a9a95677`, цепочка CLOSURE-ZST `0ad35c0a9345d6dc460ef0f2ed2adea7b76d235b`
→ correction `e0340be9ff45b293a2ffd439003ce1b47122ff61` → heavy tests b12 `ee2695e5a2`.
Read-only reference `/root/kani-fix-3300-closure-zst`; после выдачи отдельный clone `/root/kani-fix-3300-lawful-oracles`,
ветка `fix/kani-3300-lawful-oracles` от exact base. Dirty/wrong base → STOP без reset/stash.
Research: g0 `experiment/kani-k1-kani3300g0-20261111`; HEAD подготовки задания `f95a821af94acb36b0875843e9499fa2bcff4b2d`.

По сообщению координатора: narrow43403281233 —18/18 closure-zst, P1 SUCCESS b12;
Quick r6 43419217261 — expected155/0, kani22/0, ui14/0, script1/0; legal_pfc_transfer SUCCESS.
Это уже положительное свидетельство; не повторять ресурсную бисекцию и не приписывать себе независимое чтение raw evidence.
Старые prep/NOT_RUN файлы не переписывать. Новая qualification точных негативов остаётся отдельной задачей.

Параллельный worker15 MARKER-MODES меняет codegen/docs/свои fixtures, не эти файлы. Здесь **tests-only**:
`tests/expected/uninit/private-transfer-frame/lawful-modifies.{rs,expected}` и
`tests/json-handler/uninit-contract-oracles/**`. Не менять compiler/runtime/macros/driver/export schema/compiletest.
Не читать/интегрировать незавершённую ветку worker15. Оба пакета можно готовить независимо от ee2695e5a2;
композицию и CI на общей голове выполняет координатор после review.

## 2. Lawful-modifies

В g0 прочитать `kani3300/m2br7c/{TEST-DELTA.patch,CONTROL-MAP.md,CI-REQUEST.md}` и
`PLANNER-H1-SEMANTIC-REVIEW.md`, `kani3300/h1-step1/SEMANTIC-FINDING.md`.
Из старого test-only пакета `fe36afc4a8de2709f00524b2d3fbd6da17919728` взять **только** lawful-modifies source/expected.
Original source SHA256 `f629b795969f197ef289061c88ebc26e08c8fe969a6f82f643897451bfbdf90f`;
не импортировать R7 production/carrier/12-field assigns или лишнюю копию P1.
Сохранить Rust body, modifies/ensures и смысл: relay/choose(MU.new(*outside),MU.new29) → value29;
разрешена только запись *out; result29/out29, outside остаётся41.
Добавить per-test b12 flags и пояснение как в принятом legal-pair/history-stub стиле; это декларированный comment-only delta.
Все Kani flags, включая `-Z unstable-options`, должны быть **до** `--cbmc-args --object-bits 12`.
Глобальный DEFAULT_OBJECT_BITS не менять; normal slicing/checks/solver сохраняются.

Root `lawful_modifies_preserves_outside`: ожидается SUCCESS полезных body/frame/ensures и harness assertions.
Actual source→emitted write *out и private state assignments должны входить в свой frame; *outside не записывается.
Не выводить Unsupported из самого факта capture: legal-pair уже содержит out capture и прошёл.
Если новый root всё же получает nonzero closure layout Unsupported, сохранить точный operation/type и STOP:
общий upvar-layout patch, изменение points-to/контракта/масок этим заданием не разрешены.

## 3. Точные оракулы через существующий JSON export

`tools/compiletest/src/runtest.rs::verify_output/contains_lines` использует вхождение строк: одни .expected
не запрещают дополнительные failures. Сохранить их как совместимость вывода; **qualification gate заменить структурной проверкой**.
Использовать имеющиеся `-Z export-json --export-json FILE`, `tests/json-handler/*/config.yml`/exec и
`scripts/validate_json_export.py`; добавить один небольшой сценарий `tests/json-handler/uninit-contract-oracles/`.
Не расширять публичный JSON schema или общий expected runner, не писать новый CI runner/CBMC interceptor.
Fixtures запускать из существующих исходников exact base/нового lawful файла; без второй расходящейся копии Rust body.

Для каждой invocation: unique temporary directory/export, точный input/hash/root, `--harness ROOT --exact`, jobs1,
regular output + JSON export; все Kani options до backend args b12. Сохранять original exit, не использовать `|| true`
как критерий успеха. Известный отрицательный verification exit принимать только вместе с полным корректным JSON outcome.
Stale/missing/INCOMPLETE export, zero/wrong harness selection, timeout/signal/codegen error → FAIL/UNKNOWN, не negative PASS.
Команда должна явно включать `-Z uninit-checks -Z function-contracts -Z export-json -Z unstable-options`,
`--export-json FILE --output-format=regular` перед последним `--cbmc-args --object-bits 12`;
edition2021/-Dwarnings передать по принятому Kani recipe. Ручной вызов Kani не читает compiletest kani-flags комментарии сам.

Проверка для каждого harness отдельно:
- Run `run_state=COMPLETE`, completed outcome, совпадают requested/matched filters, ровно выбранный root/input.
- В harness outcome тоже COMPLETED; verdict, n_failed, failed_properties и checks.failure согласованы.
  Проверить counts/partition n_properties=checks.total+covers.total; reject null/unknown/error/undetermined outcomes.
- Сравнить **полное множество/мультимножество failures**, не substring/«хотя бы1»/общий FAILED.
  Проверять id uniqueness, status, class, exact description/type и привязку к source/callsite.
  Нормализовать только известный absolute build prefix; не стирать line/type/function или все var_N.
- Ни одного постороннего reached Unsupported/private-frame/protocol/validity failure. Unreachable служебные ветви
  не объявлять ошибкой автоматически; полезное утверждение positive root не может быть UNREACHABLE.
- JSON0.1 экспортирует успешные checks числом, а не полным списком IDs/source/function. Поэтому полезный positive assertion
  и target binding дополнить selected complete regular/GOTO evidence той же invocation через текущий CI capture;
  отсутствие поля не выдавать за наличие/достижимость. Failed PropertyExport не содержит function отдельным полем:
  использовать существующий id и источник, не придумывать новое поле schema.

## 4. Обязательная карта cases

| Case/input | Root | Обязательный oracle |
|---|---|---|
| closure-zst/scalar-pfc-legal.rs | postcondition_reads_initialized_return | SUCCESS, нет failed checks; outer useful ensures достигнут |
| transfer-qualification/legal-pair.rs | legal_ordinary_transfer | SUCCESS; ordinary companion отдельно от PFC |
| тот же legal-pair | legal_pfc_transfer | SUCCESS; полезные ensures/out checks, нет private frame failures |
| новый lawful-modifies | lawful_modifies_preserves_outside | SUCCESS; result29/out29/outside41, lawful private writes |
| closure-zst/scalar-pfc-hole.rs (P2) | postcondition_reads_returned_hole | Полный набор двух uninit checks одного payload read: local Check и delayed CheckRef; никаких иных FAIL |
| transfer-qualification/postcondition-hole.rs | postcondition_reads_returned_hole | Независимый inventory именно этого input; intended ensures read после lawful return, без посторонних FAIL |
| maybe-uninit-contract-frame/main.rs | frame_negative | Только assigns failure пользовательской записи *outside на исходной строке22; не shadow write/ранний uninit |
| maybe-uninit-contract-clause/main.rs | clause_pfc_negative | Только source-bound u16 read в requires helper; не frame/protocol/Unsupported |

Postcondition-hole может иметь те же два generated checks, но не копировать количество/IDs молча из P2:
предварительно зафиксировать source operation map, после CI сверить полный inventory и оба instrumentation слоя.
Два свойства одного bad read допустимы и сохраняются. Считать разные inputs/root с одинаковым именем разными cases.
Outer assertion отрицательного read-root может быть UNREACHABLE после guard; для legal P1 такое запрещено.
`var_7` из старого frame expected — только историческое имя. Bind его к *outside по реальному target/property/source;
не принимать любой assigns и не делать wildcard по всем generated temporaries. Новые numeric IDs не угадывать.
Если точной привязки пока нет, manifest помечает BINDING_PENDING, CI-request требует конкретные selected fields;
такой case не получает qualification только потому, что старый .expected совпал.

## 5. Проверки, handoff и STOP

Локально после выдачи допустимы только static/Python/shell parsing и synthetic oracle tests, без компилятора/verifier.
Обязательные synthetic cases: extra FAIL, missing/duplicate root, same root in wrong input, swapped frame target,
one-of-two missing check, extra Unsupported, truncated/INCOMPLETE/stale JSON, counters mismatch, signal/nonverification error.
Эти тесты проверяют checker; не mirror implementation и не заменяют actual semantic CI.

CI-REQUEST: сначала fmt/build/checker tests, затем ровно8 roots таблицы при b12; singleton solver, proposed300s/6GiB,
actual caps/build budget утверждает координатор отдельно. Никакого переноса старого разрешения H1≤10.
Quick сейчас не включает новый сценарий автоматически: указать отдельный selected `json-handler exec` invocation,
иначе сильный gate NOT_RUN при зелёном expected. После композиции с MARKER-MODES — один согласованный Quick + новые selected gates;
не выполнять полный platform/M3/SmallSort gate и не угадывать новое общее число тестов.

В research `kani3300/lawful-oracles/`: INPUTS.json, ORACLES.json, CONTROL-MAP.md, CHECKER-TESTS.md,
CI-REQUEST.md, REVIEW.md, RESULT-LAWFUL-ORACLES-PREP.md≤35строк. Actual outcomes до CI — NOT_RUN.
Показать diff/hash lawful source, список strong gates и явно оставшиеся binding gaps.
Source test-only commit от ee2695e5a2, author/committer через -c Tiramisu-Cake <igkharin@gmail.com>, без push/CI-only overlay;
research [skip ci], stage только свой results directory, без push. Ни worker15, ни следующие стадии не выдавать.
После будущей выдачи финал `READY <source-sha>`; сейчас **DRAFT / NOT ISSUED**.
