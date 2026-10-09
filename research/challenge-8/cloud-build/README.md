# Cloud Build: действующая процедура Challenge 8

Это общий runbook для назначенных рабочих веток. В main здесь только docs;
исполняемые clients/recipes, pins и собственный ledger берутся из явно назначенной
ветки и поручения. [WORK-POLICY](../WORK-POLICY.md) задаёт полномочия/сессии,
[AGENT-RUNBOOK](../AGENT-RUNBOOK.md) — proof/evidence loop,
[v2 protocol](PARALLEL-BUILDS.md) — неизменённый предел двух slots.
Исторические migration/night accounts и команды — в [архиве](../archive/team-procedure-2026-10-10/README-ARCHIVE.md).

## Inputs и счёт до submit

- Proof owners `select-sort4` и `merge`; свой absolute ledger и state directory.
  Maintainer использует stable owner своего конкретного задания (в прочитанном
  fullmake account — `verifast`) и собственный ledger, не alias proof-owner.
  Его Build тоже занимает один из двух общих slots; третья одновременная submission
  ждёт capacity. Это не выдаёт maintainer новый счёт/бюджет.
- Phase ID, явная authorization, статус AUTHORIZED, ещё не истёкшие main/absolute
  deadlines, ceiling/remaining seconds и reviewed allowed_lanes своего задания.
  Старый ledger AUTHORIZED после deadline не является разрешением.
- Полные опубликованные proof/infra SHAs, именованный profile и exact recipe.
  Client bytes должны соответствовать выбранному infra commit; не использовать
  SHA чужого patch commit вместо результирующего infra SHA своей ветки.
- `pinned-objects` и `--no-source`: только выбранные committed Git objects.
  Recipe связывает entrypoint и точные infra_paths/proof_paths с modes/hashes;
  restore проверяет original commit/root/tree/blob identities и selected closure.
  Все scripts/patches/certificates/std inputs присутствуют. Worktree/index/hooks
  и GitHub credentials не входят. Добавление lane/изменение recipe вне задания
  требует отдельного scope; docs не регистрируют новые lanes.

## Команды существующего client

Пример только формы; переменные заполняются из **действующего** поручения.
Не копировать phase ID, budget или deadline из архивного примера. Команды
выполняются из собственного worktree, где есть reviewed `control.py`:

```bash
python3 research/challenge-8/cloud-build/control.py \
  --phase-id "$c8_phase_id" --ledger "$c8_ledger_absolute" \
  --state-dir "$c8_state_absolute" --owner "$c8_owner" request

python3 research/challenge-8/cloud-build/control.py \
  --phase-id "$c8_phase_id" --ledger "$c8_ledger_absolute" \
  --state-dir "$c8_state_absolute" --owner "$c8_owner" submit \
  --infra-sha "$c8_infra_sha" --proof-sha "$c8_proof_sha" \
  --lane "$c8_reviewed_lane" --source-mode pinned-objects --timeout "$c8_timeout_seconds"

python3 research/challenge-8/cloud-build/control.py \
  --phase-id "$c8_phase_id" --ledger "$c8_ledger_absolute" \
  --state-dir "$c8_state_absolute" --owner "$c8_owner" status "$c8_build_id"

python3 research/challenge-8/cloud-build/control.py \
  --phase-id "$c8_phase_id" --ledger "$c8_ledger_absolute" \
  --state-dir "$c8_state_absolute" --owner "$c8_owner" download "$c8_build_id" \
  --output "$c8_new_evidence_directory" --text-logs
```

Global arguments всегда до subcommand. `withdraw-request` убирает свой stale
advisory request; `cancel BUILD_ID` требует совпадения owner/phase/ledger и только
запрашивает отмену: ждать terminal API state. Не отменять peer ради docs.
`request` не даёт авторизацию и не вводит turn alternation.

Существующий client резервирует timeout + 60 секунд queue envelope; в прочитанных
select/merge clients базовый timeout 90–1740 секунд (envelope ≤1800). Это не
общий потолок для отдельно согласованной maintainer lane: её reviewed client
может иметь более конкретный лимит, который нельзя переносить в proof lane. Сверить более строгие
lane/proof ограничения и оставшееся окно своего задания. Не обходить refusal;
новый режим сессий не меняет executable phase registrations или timeout pins.

## Coordination и стоимость

Использовать существующий client с общей `/root/smallsort-ci-coordination/lock`.
Под flock он reconcile reservations/API, допускает и атомарно резервирует submit,
сохраняет token и ответ; uncertain reply занимает slot до однозначного resolution.
[v2](PARALLEL-BUILDS.md) считает максимум два occupied project slots, один на owner
и ledger, включая untracked API builds. Не править live active.json вручную.

Ledger charges — округлённый вверх createTime→finishTime, включая queue, setup,
verification и upload; execution startTime→finishTime отдельно. Пока terminal
данных нет, reservation расходуется консервативно. Historical accounts не
сбрасывать и не переносить. Download идёт вне lock; запись собственного receipt
атомарна после hash checks. Продолжение с истёкшим счётом не разрешено.

Все gcloud вызовы client адресует явно: configuration `smallsort-ci`, account
`smallsort-dispatcher@smallsort-ci.iam.gserviceaccount.com`, project `smallsort-ci`,
region `global` для Build API; storage без region. Не менять active configuration,
IAM/resources или читать/выводить credentials. Образы и tool pins задаёт exact
infra/profile, а не копия digest в документации.

## Evidence и verdict

Prefix: `gs://smallsort-ci-evidence-504462351565/cloud-build/BUILD_ID/`.
Packaging/upload предшествуют независимому final verdict. Сохраняются submitted
config, source-input certificate, manifest, summary, file hashes, archive SHA,
upload receipt и индекс text logs. Download проверяет archive/config/input/
file inventory/receipt и выбранные external text chunks. При чтении через
read-only connector начать с compact summary/manifest, затем нужные raw logs.
Chunks ≤8MiB; восстановить порядок и проверить длины/hashes по index/inventory
до интерпретации. Не трактовать усечённый лог как полный.

`diagnostic_complete`, `evidence_complete`, `verification_accepted` и Build status
различать. SUCCESS collector может сопровождать непринятое/ошибочное proof.
Error/timeout, отсутствующий case или bad upload не дают PASS. Actual body,
full posts, refinement/nonvacuity/UB и intended negatives проверяются по полным
данным. Архивы/генерированный source/полные logs хранить вне Git; в checkpoint —
компактные receipts, identities и claims. Classifier-only replay не собирает
верификатор и не переносит evidence на иной source/profile.

Новые cache/preflight/replay lanes поставлены в [отдельном задании](../INFRASTRUCTURE-TASK.md).
Данная документация не меняет client, coordinator, pins или доказательства.
