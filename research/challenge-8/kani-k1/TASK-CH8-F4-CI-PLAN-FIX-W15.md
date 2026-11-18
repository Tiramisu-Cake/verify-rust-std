# W15 — F4-R14-1: CI plan only

Это верификация корректности, не security-работа. Отвечай кратко. Fresh session
после /new, текущие model+/fast сохранить, без субагентов. STOP только реальный
blocker с evidence, не объём/контекст. Относительные пути от
`/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/`.

Exact old package `7485bbb27a72dd463d4a9628c8627689d30e7e56`, review
`cbfd888f274a0666f09af79d98ef4b8b8061f497`, finding **F4-R14-1 (P2)**.
Прочитать `kani3300/wave0/f4-fix-review/REVIEW.md` и HANDOFF. Source
`cab66681c912a3e5ee01a106faaeee5237ca0232`, tree
`8585336ed35a14fe0fc157a7ca4e0d52075c0e49`, parentmainfaff immutable.
**Compiler fix, regression code, all16 workflows и scripts не трогать.**

Исправить единственный blocker в новом package: добавить release.yml в structured
standard_pr_workflows, перечислить четыре actual bundle build jobs и оба полных
пяти-OS matrices test_bundle/test-use-local-toolchain (14 PR build/test instances).
Использовать точные job IDs/matrix значения из frozen source, не display-name догадки.
Сохранить шесть уже заявленных PR workflows. Только tag-gated kani_release и зависимая
Docker publication намеренно skip на PR; их skip не скрывает требуемые bundle jobs.

CI-REQUEST.md/json и все затронутые manifest/hash/validation/handoff обновить.
Узкий static plan gate: все семь applicable PR workflows и14 release PR instances
должны совпасть с frozen YAML; remove release/build/OS-entry mutations отклоняются.
Не менять YAML, trigger conditions или code, чтобы подогнать plan. Runtime NOT_RUN.
Из REVIEW.md перенести operational gates полного GO request: exact final PR branch
HEAD/source/trigger/tree/base и actual merge-ref checkout; оба benchmark labels и
подходящий native event; skip-ci в HEAD/pushed range; отсутствие workflow_dispatch
у этих семи workflows; feature-push сам не full PR coverage. Никаких реальных label/
event/PR/branch/CI actions. Owner выбирает допустимую choreography и accounting.

Новый g0 output только `kani3300/wave0/f4-fix-plan-r1/`. Сохранить неизменённый source
patch/test bytes по immutable refs или exact mirror; source commit/tree остаются cab/
858533, новый Kani commit не нужен. Old748/cbfd не amend/overwrite. HANDOFF должен
содержать exact old→new metadata diff и hashes, READY_FOR_DELTA_REVIEW14, finding
закрывает reviewer. Код уже без findings, full source audit не повторять.

После exact READY тот же14 проверит только plan delta, затем coordinator GO-request
на full standard CI final PR-head, последний item1 28/28. Сейчас27/28; S2r1 ждет
владельца, вне scope. Нет CI/rerun/cancel/push/PR/публикаций/reservation/ledger/
local compiler/verifier/full runner. Stage exact own paths, commit --only,
`[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>. Финал `READY <full g0 SHA>`.
