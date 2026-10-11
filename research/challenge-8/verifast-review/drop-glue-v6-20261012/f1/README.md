# F1 — исправление admission outcome switch

**F1 CLOSED для подготовленного classifier patch; весь profile по-прежнему NOT_FOR_INTEGRATION / NOT_ACCEPTED.** Никакого merge или изменения active runner merge-агента. [Точные pins](INPUTS.json), [проверки](FIXED-TESTS.json), [saved replay](REPLAY.json), [независимый review](INDEPENDENT-REVIEW.md), [публикация](PUBLICATION.json), [cleanup](CLEANUP.json).

Продолжение от `ed14b2de3eb8eae65924c041efb38cd544f7505a`; старый review `7567431a7877ede692d5d523ff4756a88a2fd239` сохранён неизменным. Main policy `6e1a8e59c56669abe5e6ec2013478e45ed2cc267` и ACK `ea1551432e644812e8163a99be636dafa291cd68` сохраняются. Собственная ветка `review/verifast-drop-glue-f1-20261012`, worktree `/root/verify-rust-std-review-v6`. Сессия: start `2026-10-11T22:35:41Z`, deadline `23:35:41Z`, Cloud0, без extension. Конкретная миссия — только evidence admission/replay, не proof/transport/receiver/caller development.

## Исправление

[Portable classifier.patch](classifier.patch) — один hunk к `research/challenge-8/cloud-build/origin-layout/onecell-selected-drop.py:497–506` в exact base **`420188dd1732d53f3f515690ed2ff6f53a9026ab`**. Old runner SHA256 **`3e3e1b917a7cc301fee16074a80f7470a98ebcc4d4eb04b61781e54cbcc28a51`**; fixed runner SHA256 **`cb30a0a65e130b4bb38b99f609b3dcf929661185c3fbb9f6da6b845a0fb46d25`**. Exact tested head commit записан в publication receipt.

До формирования dict admission требует: direct outer SwitchExpr, отсутствие default, ровно два well-formed SwitchExprClause из четырёх аргументов, только returning/unwinding, оба уникальны, binders соответственно `["result"]` и `[]`, post — AST Node. После этого прежний `_literal_false_with_loc` без изменения проверяет Node False(location). Ни tool, ни contracts, runtime/proof inputs, семантика или profile/settings не изменены. Cardinality/default проверяются до dict, поэтому дубликат больше не может скрыться при overwrite.

`classifier/onecell-selected-drop.py` — изолированная копия base420 плюс этот единственный hunk; `classifier/stack-proof-ast-admission.py` — byte-identical pinned parser (SHA256 `a5f28d5feb9c3e07d2bb5ee6b19a29dc45ea782d5f51a1630f993124f20bd995`). Это review capsule для прямого вызова service entrypoints, не новая runnable hosted lane: его hosted preparation/run paths не используются. BODY_GLUE_PROFILE и вся остальная конфигурация base420 сохранены; это не свидетельство выполненного v8.

## Проверки и точный охват

Сначала, до правки, выполнен old-classifier repro через настоящий file-reading `_body_glue_ast_evidence`, с штатным OcamlAstText parser. [OLD-REPRODUCTION.json](OLD-REPRODUCTION.json): saved positive, duplicate returning и duplicate unwinding все admitted=true. Старый дефект воспроизведён не через mock parser.

Fixed tests — **15 entrypoint cases**: byte-identical saved positive сохраняется; 14 mutants (duplicate returning/unwinding, missing returning/unwinding, extra known arm, unknown arm, malformed constructor/arity, extra malformed clause, default, wrong returning/unwinding binders, malformed False post и wrapped switch) отвергаются. Для каждой мутации изменены оба равных complete contracts, их equality и `glue_contract_present=true` отдельно подтверждены. Полные AST сериализованы в собственные temporary `proof-ast.ml` и заново прочитаны настоящим entrypoint/parser; parser не подменяется. Saved raw files не изменяются. Восемь exact False/location cases переиспользованы из опубликованного `parser-check.py` и проходят. Patch application/check к exact base420 даёт byte-identical tested capsule; syntax и локальные Markdown links проверены.

На **всех семи** неизменных cases Build `34485da0-911b-4c1e-9d8d-32922f154f82`, proof/infra `f8c7cb7ed80fed845c0ad11155835da4a5803340`, tool `e0a94e3eab17fcd69f7fad785f7a0fb316d27258`, v6 profile `e97cce6325ad7f2874fccc963d43d1e9e1c0c795f813cc1bddc46a1ce9fa0081` заново исполнены:

- `_source_gate` (ghost-strip/runtime linkage);
- `_caller_ast_evidence` и **исправленный `_body_glue_ast_evidence`**, читающие original saved AST;
- refinement stage/marker/no-generated-error receipt check (не refiner execution);
- `_generated_glue_proof_gate` и `_body_glue_negative_gate` на raw logs;
- exact source hashes, все четыре stage exit-code/JSON/source-before-after receipts; все прежние raw hashes сравниваются с опубликованным scoped replay.

Переиспользованы hash-bound raw MIR identity/CFG admission, selected Drop body/effect AST admission, canonical safety_proof compatibility, compiler/refiner/verifier результаты и caller return/leak/natural-scope execution markers из исходной classification. Это **admission плюс scoped log replay**, не полный `_classify`/proof rerun. Эти границы записаны machine-readable в REPLAY.json.

Подлинный bounded normal fragment PASS сохранён. Шесть scoped intended-negative verdicts совпадают с прежним replay: after-drop false, before-call false, missing physical len field, missing source-quarter, duplicate full effect и real caller dead code. Cloud FAILURE подтверждается saved Cloud record и hash-pinned summary; шесть **raw INCONCLUSIVE** остаются неизменными. Никакого fresh proof или переноса PASS на v8.

## Команды

Из собственного checkout (output не должен переписывать raw evidence):

```bash
c8_f1_package=research/challenge-8/verifast-review/drop-glue-v6-20261012/f1
c8_f1_temp=$(mktemp -d /tmp/c8-f1-reproduce.XXXXXX)
git show 420188dd1732d53f3f515690ed2ff6f53a9026ab:research/challenge-8/cloud-build/origin-layout/onecell-selected-drop.py > "$c8_f1_temp/old.py"
c8_f1_evidence=/tmp/merge-glue-body-v6-unpacked-34485da0/allprooflogs/checked-minimal-bridge/onecell-selected-drop
PYTHONDONTWRITEBYTECODE=1 python3 "$c8_f1_package/test-admission.py" \
  --runner "$c8_f1_temp/old.py" \
  --parser "$c8_f1_package/classifier/stack-proof-ast-admission.py" \
  --case "$c8_f1_evidence/cases/positive" --mode old \
  > "$c8_f1_temp/old-repro.json"
PYTHONDONTWRITEBYTECODE=1 python3 "$c8_f1_package/test-admission.py" \
  --runner "$c8_f1_package/classifier/onecell-selected-drop.py" \
  --parser "$c8_f1_package/classifier/stack-proof-ast-admission.py" \
  --case "$c8_f1_evidence/cases/positive" --mode fixed \
  > "$c8_f1_temp/fixed-tests.json"
PYTHONDONTWRITEBYTECODE=1 python3 "$c8_f1_package/replay-admission.py" \
  --runner "$c8_f1_package/classifier/onecell-selected-drop.py" \
  --parser "$c8_f1_package/classifier/stack-proof-ast-admission.py" \
  --evidence "$c8_f1_evidence" \
  --build-record /tmp/merge-glue-body-cloud-session2-20261011/34485da0-911b-4c1e-9d8d-32922f154f82.json \
  > "$c8_f1_temp/replay.json"
```

Фактически old reproduction выполнен до изменения byte-identical capsule; fixed tests/replay — после правки с вышеуказанными arguments, outputs сохранены в этом пакете. Импорты/entrypoints осмотрены до исполнения: только inert classifier/parser, вызовов `_prepare`, `run`, proof runners, compiler/extractor/refiner/verifier нет. Не установлен ни один dependency. Temporary serialized fixtures автоматически удалены тестом. Original raw archive SHA `9d6294260e96ce7d3480010a0b2ab16adfa35830a72972c2e8ccbab96d2c0bc3`, остальные immutable bindings — в исходном [INPUTS.json](../INPUTS.json).

## Остаточные блокеры

Закрыт только F1 classifier finding. Tool I compatibility, девять official admission и четыре receiver/end/retirement controls, actual insert_tail late-panic cleanup, B1/B2 и O23 остаются отдельными OPEN/NOT_RUN обязательствами. Эта сессия их не выполняет и не повышает готовность profile. Активные файлы/worktrees/coordinator merge-агента не изменены; merge/upstream PR/profile acceptance отсутствуют. Собственный portable patch опубликован для review, его применение к активному runner здесь не выполнялось.
