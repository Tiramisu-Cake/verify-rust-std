# First real G1: runnable candidate, execution blocked

2026-10-12; baseline `d85bb12da89b0aa02f0c7ad6f820820da8768799`.
Собственный worktree `/root/verify-rust-std-refinedrust-feasibility-20261011`,
branch `research/refinedrust-feasibility-20261011`. Прочитаны policy/AGENTS,
WORK-POLICY, Cloud runbooks, собственный STATUS и COMPLETION-PLAN на текущем
origin/main `6e1a8e59c56669abe5e6ec2013478e45ed2cc267`. **PREPARATION ONLY**:
Cloud ceiling/charge **0/0**, своих Build/token/ledger нет. Никакого исполнения
compiler/extraction/verification, установки зависимостей или production mutations.

## Команда и границы первого опыта

Гипотеза и конечные generic safety N/U posts — [G1-MINIMAL-PLAN](G1-MINIMAL-PLAN.md).
Только frontend diagnostic actual insert_tail; потребитель — actual R5 insertion.
G2, Rocq proofs и Radium parser не входят. После отдельного разрешения dispatcher
вызывает committed infra wrapper, затем [entrypoint.sh](g1-minimal/entrypoint.sh):

```text
python3 /workspace/proof/research/challenge-8/refinedrust-feasibility/g1-minimal/run.py \
  --source /workspace/g1-source --rr /opt/refinedrust \
  --freeze /workspace/proof/research/challenge-8/refinedrust-feasibility/g1-minimal/freeze.json \
  --out /workspace/evidence/g1
```

Это Cloud-only команда, **сейчас не выполнять**, в том числе `--help` на VPS.
Обязательная внешняя среда dispatcher: `SMALLSORT_EXECUTION_PROVIDER=cloud-build`,
`CLOUD_BUILD_ID`, `SMALLSORT_DEADLINE_EPOCH`, `PROOF_IMAGE`; authorization/accounting
остаётся у существующего client. Environment guard сам по себе не авторизация.
Внутри: hash/image/compiler preflight → exact source restore → ghost-only
injection → dependency-free stock control → один target invocation:

```text
RR_CONFIG=/workspace/evidence/g1/RefinedRust.toml cargo refinedrust -- \
  --manifest-path /workspace/g1-source/library/Cargo.toml -p core \
  --locked --offline --target x86_64-unknown-linux-gnu
```

Runner вызывает sibling binary `cargo-refinedrust -- ...`, эквивалент штатного
Cargo subcommand из прежнего pinned audit; его command routing/config/export
contract подтверждён pinned frontend audit; binary/path freeze остаётся обязательным.
Source restore — GitHub exact commit + backtrace Gitlink, полный byte verification
library. Std source не заменяется sysroot или переписанным isolated helper.
Crate-wide unrelated error не считается отказом insert_tail.
[annotations.json](g1-minimal/annotations.json) содержит только register_tool/rr
и verify для helper, guard Drop и actual constructor/Deref callees; никакого unit
refinement/True unwind post/assumed summary. Инжектор прежний, manifest новый;
необходимость дополнительных ADT/spec annotations оценивается по реальному отказу.

Config generation-only: `run_check=false`, `no_verify=false`, `admit_proofs=false`,
unwind/overflow/debug/borrowck/linking включены, unsupported не пропускаются.
Pinned stdlib exports явно задаются **непустым** frozen `lib_load_paths`, а не
новыми shims. Их actual DefId applicability остаётся review/proof debt.
Все версии/commands/config snapshots, полные stdout+stderr command logs, exit/
signal/timeout/timing/RSS, source/tool/ghost receipts и generated MIR/Radium/
spec/proof skeleton/rrlib/linking output сохраняются; cache и HOME вне evidence.
`first-blocker.json` и первый error line дают **UNREVIEWED hint**, не угадывают
target attribution. Reviewer фиксирует причинный stage/symbol/span по raw log.

## Inputs и source transfer — актуализация 2026-10-12

Exact RR source recovery и независимый source/workflow/export audit завершены:
[G1-SOURCE-RECOVERY](G1-SOURCE-RECOVERY.md),
[G1-PINNED-FRONTEND-AUDIT](G1-PINNED-FRONTEND-AUDIT.md).
Local source доступен вне /tmp, commit/tree/byte receipts подтверждены;
повторный GitLab fetch и external recovery не нужны. Cloud source/image delivery,
binary/config/vendor hashes и compiler compatibility в реальном run ещё NOT_RUN.
Source transfer manifests/cold null audit fields сохранены как historical candidate,
не как утверждение об отсутствии local source. Current three gates и точный запрос:
[G1-FIRST-RUN-REQUEST](G1-FIRST-RUN-REQUEST.md); v4 отменён, только v3/max3.

Registry read-only inventory отказал: `artifactregistry.locations.list` denied
для smallsort-dispatcher@smallsort-ci.iam.gserviceaccount.com. **Image availability
UNKNOWN**, не «образов нет». Достаточно выдать известный digest/receipt или
разрешить ограниченную read-only inventory; production IAM здесь не менялся.

Если compatible image не найден: [cold.recipe.candidate.json](g1-minimal/cold.recipe.candidate.json)
переиспользует существующий Dockerfile и exact Rust archives/frontend Cargo.lock.
Требует frozen OS .deb snapshot/versions, union vendor closure frontend+core,
Cargo config, RR bundle/context URI+generation+hash, approved registry destination
и committed/export inventory. Эти зависимости **не выдуманы, сейчас null**.
Cold dispatcher/docker-builder integration отдельно reviewed; manifest пока не
является submit-ready Cloud config. [cold-jobs.proposal.patch](g1-minimal/cold-jobs.proposal.patch)
добавляет jobs=1 в прежний Dockerfile; не применён. Rocq/Dune не нужны для
generation-only при наличии проверенных готовых exports; если их нет — сначала
отдельное решение о setup, без скрытой proof сборки.

## Минимальный infrastructure diff / approval

Точный proposal base **454d8a17e9c7989cbfebf24c4cdd31fea629abb0**; его coordinator
SHA256 `49464b5a1078c99f8f44ef0bba06bb285c039ca0a0ab10d104bc7b54f32cb4bc`.
Все patches находятся только в own candidate directory, **NOT APPLIED**:

- [coordinator-owner.proposal.patch](g1-minimal/coordinator-owner.proposal.patch):
  добавить refinedrust-feasibility к V3_OWNERS, сохранив PROTOCOLS[3]=3/max3.
- [dispatcher.proposal.patch](g1-minimal/dispatcher.proposal.patch): узкий lane/
  image/phase/input/window freeze, single warm attempt, disk 100 GB и infra wrapper;
  [warm.recipe.candidate.json](g1-minimal/warm.recipe.candidate.json) связывает exact
  infra/proof paths. `source-input.py`/transport/run-proof/upload/download остаются
  прежними. Packager получает только RR-specific metadata branch; accepted gate
  и независимая config/input/archive/upload проверка сохранены.

Read-only live state: schema_version=3/max_active=3, присутствовал merge token
dispatch-9b927166ce6b4db9a6fb424b761c5ffd / Build
a9613c24-8f42-4008-981b-4df6b1e9206d; это snapshot reservation, **не live API
capacity audit**. Трёх-owner ACK/migration уже состоялись; rerun v2→v3 transition
запрещён/не нужен. Все текущие clients должны согласованно принять новое allowlist
и записать fresh exact-byte ACK до первой RR reservation: старый client отвергнет
неизвестного owner. Не менять peers сейчас и не увеличивать max_active.

Source/workflow audit закрыт. Следующее отдельное разрешение должно закрыть image freeze, owner adoption
и candidate integration review; затем freeze published proof/infra SHAs, phase,
start/main/absolute window, собственные ledger/state и permissions существующего
submit/read/log/evidence-upload. Null G1_FREEZE в patch намеренно fail-closed.
Infra SHA связывается approved ledger + existing committed-client byte checks,
не self-referential константой собственного commit. Cold дополнительно требует
builder/context/registry-write approval; готовый digest позволяет избежать cold.

Warm proposal: E2_STANDARD_2, jobs=1, disk 100 GB, timeout **1200 s**, ledger
ceiling **1260 s** (+60 queue; ≥70 packaging внутри timeout). Cold отдельно
timeout **1740 s**, ceiling **1800 s**. RAM/runtime не измерены, guarantees нет.
Charge ceil(createTime→finishTime), включая queue/setup/upload; один на owner/
ledger, максимум три occupied project slots, unknown submit удерживает slot.
Один warm attempt, никаких retries/borrowed closed budgets. Current budget=0.

## Verdict и stop

**PASS_DIAGNOSTIC (manual)**: correct stock control, выбранные actual code/spec
и reviewed source/callee/normal+unwind evidence, verified complete external archive.
Это frontend admission/collection, **verification_accepted=false, proof NOT_RUN**;
CURRENT recovery, ownership/copy/shape/glue/leak и generic safety не доказаны.
Runner автоматически выдаёт только INCONCLUSIVE/MANUAL_REVIEW_REQUIRED.
Его diagnostic_complete означает полноту сбора команды, а не admission PASS.

**INCONCLUSIVE**: compiler/setup/compatibility, unrelated whole-core failure,
missing target/artifacts/bindings, timeout/OOM, incomplete upload/correspondence.
Missing ordinary callee spec отмечать LIBRARY-SPEC, не unsupported semantics;
proof resource obligation — отдельный UNPROVED, не compiler error.

**STOP**: mismatch pins/runtime source, selected unsupported feature, необходимость
новых trusted semantics/assumed bridge/restrictions, exhausted deadline/ceiling,
unknown submission или недостаточное evidence. Сохранить raw failure, не retry.
После этой подготовки/публикации STOP до отдельного Cloud решения.

Validation: Python3.10 AST/JSON, bash -n, actual Git-object anchor/allowed ghost
checks, recipe proof closure, git apply --check **только на temporary copies**;
patched dispatcher/coordinator только AST, не запускались. Четыре pure synthetic
service tests PASS; existing packager с proposed metadata branch на synthetic
saved evidence PASS: frontend error collection остаётся non-proof, missing stage
отклоняет completeness, RR tool/compiler identities сохраняются. Реальные source
restore/injector/frontend/watchdog/image/verification **NOT_RUN**.
