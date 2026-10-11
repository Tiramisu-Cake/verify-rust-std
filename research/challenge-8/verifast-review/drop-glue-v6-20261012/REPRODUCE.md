# Воспроизведение review, только saved-data service checks

Входы — [INPUTS.json](INPUTS.json). Source Git extraction ниже означает чтение tracked bytes, не запуск proof source extractor. Cloud budget0; compiler, exporter, decoder binary, refiner, VeriFast и Cloud runners не запускать. Scripts импортируют только inert classifier/parser modules и вызывают read-only gates; imports/entrypoints осмотрены перед исполнением. Output всегда в отдельном temporary каталоге; исходные evidence/receipts не переписывать.

Raw evidence сохранено в object storage:
`gs://smallsort-ci-evidence-504462351565/cloud-build/34485da0-911b-4c1e-9d8d-32922f154f82/`.
Локально прочитаны `/tmp/merge-glue-body-v6-evidence-34485da0` и `/tmp/merge-glue-body-v6-unpacked-34485da0`. Архив `evidence.tar.gz` SHA256 `9d6294260e96ce7d3480010a0b2ab16adfa35830a72972c2e8ccbab96d2c0bc3`; archive bytes/raw logs в review Git не копируются. [Cloud record](https://console.cloud.google.com/cloud-build/builds/34485da0-911b-4c1e-9d8d-32922f154f82?project=504462351565).

Из корня своего review checkout при наличии raw unpacked evidence:

```bash
c8_review_tmp=$(mktemp -d /tmp/c8-v6-review.XXXXXX)
mkdir -p "$c8_review_tmp/proof" "$c8_review_tmp/auditor"
git archive f8c7cb7ed80fed845c0ad11155835da4a5803340 \
  research/challenge-8/cloud-build/origin-layout/onecell-selected-drop.py \
  research/challenge-8/merge/overnight/stack-proof-ast-admission.py \
  | tar -x -C "$c8_review_tmp/proof"
git archive 420188dd1732d53f3f515690ed2ff6f53a9026ab \
  research/challenge-8/cloud-build/origin-layout/onecell-selected-drop.py \
  | tar -x -C "$c8_review_tmp/auditor"
c8_raw_cases=/tmp/merge-glue-body-v6-unpacked-34485da0/allprooflogs/checked-minimal-bridge/onecell-selected-drop
PYTHONDONTWRITEBYTECODE=1 python3 \
  research/challenge-8/verifast-review/drop-glue-v6-20261012/parser-check.py \
  "$c8_review_tmp/proof" "$c8_raw_cases/cases/positive" \
  > "$c8_review_tmp/parser.json"
PYTHONDONTWRITEBYTECODE=1 python3 \
  research/challenge-8/verifast-review/drop-glue-v6-20261012/replay-gates.py \
  "$c8_review_tmp/auditor" "$c8_raw_cases" \
  > "$c8_review_tmp/negative-replay.json"
```

Фактически выполнены те же commands с pinned trees `/tmp/review-v6-pinned` и `/tmp/review-v6-auditor420`, output — [PARSER-CHECK.json](PARSER-CHECK.json) и [NEGATIVE-GATE-REPLAY.json](NEGATIVE-GATE-REPLAY.json) в собственном новом review package. Синтетические whole-post mutations делались в памяти после parsing, исходный `proof-ast.ml` не менялся. Duplicate-arm accepted — воспроизведённое finding, а не passing negative. Остальные invalid/missing cases reject.

`replay-gates.py` проверяет source hashes, stage exit-code files/JSON и наличие всех прежних full admission flags/source immutability, переиспользует hash-bound original source/MIR/body admission receipts. Заново выполняются только `_generated_glue_proof_gate` и `_body_glue_negative_gate` на неизменённых raw logs. Старый positive сохраняет fragment PASS; шесть raw INCONCLUSIVE получают отдельные intended-negative verdicts. Это уточнение классификации старого Build, не fresh/full auditor/proof, не новый профиль и не выполнение NOT_RUN cases.

Дополнительные выполненные static commands:

```bash
git -C /root/verifast-merge-actual-glue diff \
  853fd1e2edb309101df83b93c65572a0d8d0d189 \
  e0a94e3eab17fcd69f7fad785f7a0fb316d27258 -- src/refinement_checker
git show f8c7cb7ed80fed845c0ad11155835da4a5803340:research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json | sha256sum
git show 420188dd1732d53f3f515690ed2ff6f53a9026ab:research/challenge-8/cloud-build/origin-layout/GLUE-BODY-PROFILE-V6.json | sha256sum
sha256sum /tmp/merge-glue-body-v6-evidence-34485da0/evidence.tar.gz
```

Собственный source-hash check сравнил 109 restored-path entries certificate с exact f8 Git objects, 13 ordered patch hashes и 5 compiled source pins с exact e0 Git objects. Все значения записаны в INPUTS.json. Independent inventory/index проверка записана в INDEPENDENT-REVIEW.md. Baseline profile refiner hash не заменяет actual binary receipts.
