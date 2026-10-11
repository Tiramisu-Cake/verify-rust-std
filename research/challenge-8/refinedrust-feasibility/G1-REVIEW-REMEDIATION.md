# G1 review remediation — Phase 1

2026-10-11, Europe/Moscow. Baseline:
`619cd100eed3ef5806f1c37ced79995358bc6ceb`.
Независимый review:
[07f0180d146ed1e1ce1d89ddba7102d5f4bb882d](https://github.com/Tiramisu-Cake/verify-rust-std/blob/07f0180d146ed1e1ce1d89ddba7102d5f4bb882d/research/challenge-8/refinedrust-feasibility/G1-INDEPENDENT-REVIEW.md).

**Готов к повторному независимому review как ограниченный remediation candidate.
R2/R9 не закрыты: точный RR output contract остаётся UNKNOWN.** Удалены
ложноположительные callee/unwind observations, но положительный разбор реальных
Radium continuation roles не реализован без подтверждённого исходника writer.
Этот пакет не объявляется готовым к Cloud-интеграции или запуску.

Авторизация — только собственные harness/parser/collector/service tests.
Cloud budget/charge **0/0**, Build/token **NONE**. Компилятор, RR, extraction,
proof, Docker и Cloud не запускались; dependencies не устанавливались.
R4–R8, runtime std, trusted semantics, production coordinator, review-ветка и
чужие worktrees не изменены. PR и Tool Application не создавались.

## Результат по review items

| Item | Исправление | Tests / проверка | Результат | Остаточные риски |
| --- | --- | --- | --- | --- |
| R1 | Event detection и inventory используют один CallS scanner: nested comments/strings исключены, terms сбалансированы, inline calls и calls вне recognized blocks учтены. Отсутствующий binding/неизвестная форма отклоняются. Definition existence больше не подтверждает linkage. | Fixture: 6 calls / 4 distinct bindings; inline/event agreement; comments/string markers; complex/unknown/unbalanced call; missing binding; unrelated Definition; call outside blocks. | Service defect исправлен. Положительный actual callee resolver **UNKNOWN**, candidate definitions не получают OBSERVED. | Реальные DefId/type substitutions/linking output не наблюдались. Нельзя заменить их guessed map. |
| R2 | Удалён вывод unwind roles из произвольного Goto и отсутствия UnwindFreeAnnot. Добавлен непереопределяемый map-файлом UNKNOWN gate для RR output contract. MIR cleanup учитывает все exits, missing blocks, cycles; payload projection Drop тоже STOP. | Swapped continuations, normal-only cleanup, bypass Drop и подмена map не дают OBSERVED/PASS на Radium gate. Missing DropGlue — NOT_OBSERVED event; missing MIR guard Drop / лишний payload Drop — STOP; неизвестная ветвь/цикл — незакрытый cleanup. | **PARTIAL / UNKNOWN**. Небезопасный положительный gate устранён. Positive Radium normal/unwind role parser пока **NOT_IMPLEMENTED**, не выведен из fixture. | Требуется read-only получение exact pinned writer и статическое подтверждение syntax/roles. Эти mutation tests проверяют отказ при неизвестном contract, а не корректность реализованного role parser. |
| R3 | Signals/timeouts исключены из controls и stages; raw records/controls пересчитываются collector. Timeout всегда завершает оставшуюся process group через TERM/KILL с bounded waits, даже если parent уже вышел. | Signal exits, shell signal codes, timeout с code 0/1, interrupted native/P1, partial P0 definition. Runner проверен статически, не импортирован/исполнен tests. | Classifier/service gates исправлены; process-tree fix статически проверен. | Реальный process-tree/watchdog test **NOT_RUN**, только в будущей разрешённой Cloud-сессии. Независимого исполнения compiler/RR нет. |
| R10 | Required artifacts зависят от attempted stages. Проверяются command records, raw log hashes/lengths, environment/effective config, image receipt, source archives и archived N2; flags не заменяют raw evidence. Разделены local inventory, diagnostic и external completeness. | Удаление/reseal и substitution required artifacts; record/log/config/environment mismatches; missing stage/N2; interrupted commands; source/image receipt completeness. | `local_inventory_valid` означает проверенный локальный archive contract; `diagnostic_complete` отдельно. `evidence_complete=false` до внешнего protocol verification. | Это внутренняя целостность, не аутентификация исполнения. Package/upload/API/OCI остаются R4–R8 вне Phase 1. |
| R9 | Попытка независимо прочитать RR `332d945fafa14bf55c0c8390cb35ec4b0c012cff`; не заменяли RR source и не квалифицировали формат по fixture. | GitLab exact raw/API/blob недоступны; локальная копия не найдена. Pin/hash manifest и текущая собственная configuration прочитаны, но это не проверка source semantics. | **UNKNOWN / NOT_RUN** для generator/annotations/config/wrapper behavior и actual outputs. | `refined_by` для generic ADT, `?Sized`, ManuallyDrop/MaybeDangling, `verify`/unwind attributes, run_check/no_verify/admit_proofs и generated resource forms требуют exact source audit. |

## Границы parser после исправления

CallS scanner — служебный lexical inventory сохранённого текста. Он не
приписывает balanced arguments типы или normal/unwind роли и не исполняет Coq.
Историческая synthetic fixture продолжает проверять конкретный дефект inline
inventory. Она не становится примером подтверждённого RR output.

Наличие hash-bound Definition не связывает её с location parameter, actual
DefId или generic substitution. Поэтому даже полный inventory со всеми
candidate definitions остаётся UNKNOWN до статического определения реально
выводимой linkage relation. Unrelated definition не может разрешить admission.
Map hash удостоверяет выбор reviewed файла, а не неизвестную grammar/семантику.

`radium_output_contract=UNKNOWN` установлен в коде auditor. Source receipt,
reviewed map и command returncode не могут его повысить. Ни исходная fixture,
ни swapped continuations не дают положительного Radium cleanup verdict.
В этой ревизии полный actual-output admission PASS недоступен; это явно
незакрытое обязательство, не скрытый unsupported case и не proof acceptance.

MIR cleanup отдельно отслеживает guard Drop на каждом resume/terminate пути.
Missing blocks, циклы и неизвестные terminals не исчезают из множества outcomes.
Наблюдаемый resume без guard на late unwind остаётся STOP. Payload Drop,
включая проекцию временного `_tmp`, остаётся STOP. Достижимость одного good
пути не квалифицирует другой непроверенный путь.

## Evidence и failure handling

Сохранённые stage command records связаны с execution.json и raw logs/config/
environment. Collector не читает исходные Cloud paths: он проверяет сохранённые
bytes и их внутренние связи в downloaded archive. Image/Cargo receipt проверяет
локальную pin/config relation, но не registry/actual OCI execution. Archived N2
должен byte-match reviewed control и классифицируется именно архивная копия.

`local_inventory_valid`, `diagnostic_complete`, `evidence_complete` не синонимы.
Локальная completeness schema может подтвердить сохранение interrupted attempt
и всё равно оставить diagnostic незавершённым. Полная external evidence
completeness остаётся false: transport/package/upload verification не
реализуется этим заданием. `verification_accepted=false`, proof **NOT_RUN**.

Timeout/signals не засчитываются даже при наличии частичного P0/Radium output
или intended N1 error. Process-group fix всегда пробует SIGKILL после bounded
TERM wait; parent exit не означает исчезновение descendants. Реальную проверку
этого свойства не выполняли на VPS. Timeout остаётся INCONCLUSIVE и сохраняет
логи/command metadata для последующего анализа.

## Validation и identities

Прочитаны актуальные AGENTS/WORK-POLICY/AGENT-RUNBOOK, собственный STATUS,
полный independent review, Cloud runbooks, roadmap/requirements и actual target
source. Policy revision прочитана:
`5bf53668a4afa51c302e599be91a2dbc4b24042d`, редакция 2026-10-10.
Собственный worktree/branch чисты на baseline до начала изменений; origin —
`Tiramisu-Cake/verify-rust-std`, fetch выполнен. Review-ветка не изменялась.

Service tests импортируют только stdlib и собственные service/auditor modules;
runner/injector/compiler/Cloud clients не импортируются. Используются временные
synthetic archives, не реальные evidence/coordinator. Команда:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s research/challenge-8/refinedrust-feasibility/g1 -p 'test_*.py' -v
```

Integration validation: **30/30 service/parser tests PASS**, 34.589 s.
Python AST parsing с grammar 3.10, JSON parsing, `bash -n` entrypoint и
`git diff --check` PASS; scope проверен. Проверки не исполняют runner. Ни одна service проверка не считается proof или actual RR replay.
Sources/pins, compiler и unpatched RR profile остаются исходными; recipe/image/
authorization templates и shared Cloud runtime не меняются.

## Следующий разрешённый шаг

Повторный independent review опубликованного Phase 1 commit, с явным остатком
R2/R9 и callee linkage UNKNOWN. До Cloud-интеграции необходимо получить и
проверить exact writer/parser/config/wrapper sources, определить подтверждённые
continuation/linkage forms и реализовать positive gates с соответствующими
mutation controls. Доступность исходника сама по себе не разрешает RR execution.
R4–R8 и Cloud authorization — отдельные решения владельца, без переноса budget.

После собственного commit/push — **STOP**. Build/token NONE, Cloud 0/0;
runtime source, proof status и чужой учёт не изменены.

## Предыдущий checkpoint

Ниже сохраняется прежний STATUS на baseline 619cd100, без повышения его claims.

```text
# RefinedRust feasibility — G1 IMPLEMENTATION PREPARATION CLOSED

2026-10-11, Europe/Moscow. **CANDIDATE READY FOR INDEPENDENT REVIEW / NOT DISPATCH READY.** Cloud budget/charge **0/0**; own lane/ledger/phase not registered, Build/token **NONE**. No compiler/extraction/proof/install/image/Cloud execution; production coordinator/CI/std/semantics unchanged.

- Own worktree `/root/verify-rust-std-refinedrust-feasibility-20261011`, branch `research/refinedrust-feasibility-20261011`, origin `https://github.com/Tiramisu-Cake/verify-rust-std.git`; separate index `/root/verify-rust-std/.git/worktrees/verify-rust-std-refinedrust-feasibility-20261011/index`.
- Baseline/read prior checkpoint `78063c897cfb817361b2947cbe24e49570f707df`; source/policy snapshot `c7ca8c467aecf10a4b53039372ee97714f854ee3`; policy-change `5bf53668a4afa51c302e599be91a2dbc4b24042d`. Main unchanged after fetch.
- SmallSort blob `e555fce440872898e47fd5114f32eb15401d07df`; RR `332d945fafa14bf55c0c8390cb35ec4b0c012cff`; compiler `e457a7b0d326d67b4322ef0d11bd715cfaeda48f` (nightly-2026-08-28).
- Candidate dispatcher patch base `ac6a1c4ebe84ee05302f4cc5829ff1075e99d822`, unapplied. Operational infra SHA/image digest **UNASSIGNED/UNCONFIRMED**. Harness SHA is this package's published branch tip; freeze it before any future authorization.

Implemented [harness](g1/README.md): exact manifests/physical-byte checks, ghost injector/strip receipts, source/MIR/Radium saved-output parser, controls, evidence collector and cold/warm candidates. [Implementation review](G1-IMPLEMENTATION-REVIEW.md), [dispatch readiness](G1-DISPATCH-READINESS.md). Previous G0/G1 design evidence retained; ownership recovery remains PROOF REQUIRED/UNKNOWN. Latest read [merge checkpoint 2b109b92fb9a04706fdf3acb0007c185c579d984](https://github.com/Tiramisu-Cake/verify-rust-std/blob/2b109b92fb9a04706fdf3acb0007c185c579d984/research/challenge-8/cloud-build/origin-layout/FINAL-CHECKPOINT.md), no peer replay/changes.

Validation: AST/JSON/shell/Git/hash/anchor checks and **15/15 service-only synthetic tests PASS**. Injector, exact native core, RR export, actual cleanup and image all **NOT_RUN**. Proof acceptance always false. Full admission requires independent artifact mapping and actual callee/binding review; no automatic PASS from exit status/markers.

Main blocker: image/context and shared auth/recipe/provider/packager integration still unreviewed; proof-side entrypoint currently rejected by existing transport. Pinned backtrace Gitlink and union offline dependencies must be restored in Cloud. Proposed warm 1200/1260 s, separately approved cold 1740/1800 s; no retries or G2.

**STOP after own commit/push.** Next decision is independent review, then separately approved infrastructure integration/freeze and budget/session. No PR, Tool Application or Cloud dispatch.
```
