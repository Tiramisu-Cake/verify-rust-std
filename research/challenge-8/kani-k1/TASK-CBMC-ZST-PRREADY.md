# CBMC ZST PRREADY — z3 environment и util follow-up, worker 15

**2026-11-13, одна CI-only подготовительная сессия, Cloud $0.** Это верификация корректности, не security-работа.
Цель — закрыть семь dependency failures, не расширять source fix и не задерживать показ владельцу PR-кандидата.
Никаких local compiler/CBMC builds/tests, worker push/dispatch, issue/PR публикаций. CI — только координатор в Tiramisu-Cake/cbmc.

## База и результаты, которые не надо повторять

Читать `kani3300/cbmc-zst-bits2expr/{CI-RESULT-R2.md,PR-READINESS.md,CI-REQUEST.md}` и PR/issue drafts рядом.
Source **cd41a5c74b0c42edf4f08834b3e2808dd3344cab**, parent107a1e504cd69a2f3483717c8bcfcfa59814c557.
Source/test bytes и clean source commit **не менять**; никакого rebase/tag cleanup/runtime/optimizations в этой стадии.
CI r2 **91062c7dba9da7541c0e607a3735482e38d28d36**, run43334186094. Read-only clone `/root/cbmc-fix-zst-bits2expr`
сейчас может стоять на33235a4ef1: **не** брать его старую обвязку вместо двух исправлений координатора в91062.
Fork refs можно fetch для чтения, без dispatch/push. Работать в отдельном local clone/worktree `/root/cbmc-zst-prready-ci`,
branch `ci/zst-bits2expr-util-z3-<id>` от exact91062; dirty/неверный existing destination → STOP без reset/stash.

R2 уже подтвердил baseline12/13 crash+memcpy PASS; fix13/13 focused,13 neighbours,3/3 focused units.
Selected remaining util205/212:7 piped_process failures, z3 отсутствует. Последние owner-literal/kani-like C outcomes
по сообщению координатора — baseline invariant/fix VERIFIED; ранний CI-RESULT оставил их summary pending.
Ни parser/job status, ни сообщение о z3 не дают права записать новый PASS без rerun.

## CI-only изменение

Сохранить r2 fixes: без RLIMIT_FSIZE на configure/build/ar/link и empty formatter diff считается clean.
Добавить z3 в dependency install, сохранить package/binary path+version, проверить `command -v z3`, `z3 --version`
и минимальный `(check-sat)` через `z3 -in` как CI preflight. Не менять код/expected piped_process tests и не исключать .z3 тег.
Основная повторная выборка — **та же** `[util]~[zst-bits2expr]`, а не молча другая `[util]` с иным denominator.
Предварительно записать exact unit selection/list/count; ожидаемый r2 denominator212, но actual count сообщать, не подгонять.
Результат — все выбранные cases passed; failures должны содержать names/source/assertions/exit, не одно число totals.
Если z3 preflight плохой, tests NOT_RUN и setup failure; если preflight PASS, а семь failures остались — STOP с фактами,
не утверждать, что они «точно не относятся к patch» без дальнейшего разбора.

Один workflow ubuntu-24.04, только fix configuration: baseline/repro/13+13 regression не гонять автоматически заново.
Не применять прежний paired comparison oracle к fix-only follow-up: baseline/прочие selections здесь REUSED или NOT_RUN
с отдельной ссылкой наr2, не вымышленные новые ORACLES_MET. Отчёт явно предназначен для environment/util gap.
Бинарник unit из r2 можно использовать лишь если координатор имеет сохранённый артефакт с exact hash/source/config receipt;
не скачивать raw archives/logs и не брать произвольный release/local binary. Если такого binary artifact нет — штатная
CI-сборка exactcd41 с прежними compiler/CMake flags, target **unit**, без source изменения; новый binary hash записать.
Три новых focused unit cases повторить для этой newly-built unit binary как sanity; полный CBMC/ctest/platform matrix не запускать.
Если используем exact сохранённый бинарник, достаточно повторной проблемной selection; прежние результаты явно reuse, не новые runs.

Из CI-only HEAD оставить ровно один наш workflow, без inherited .github/workflows. Source commit остаётся clean;
CI-only deletions никогда не входят в будущий PR. Branch-filtered push trigger, no [skip ci] у CI-only commit;
пушит **сразу CI-only HEAD** координатор. Новый workflow_dispatch-only файл вне default не считать доступным trigger.
Job/workflow max120min, compiler parallelism2, util invocation300s; bounded output, rawKiB/exit/signal/time, artifact upload always().
Не возвращать file-size лимит на build ради cap логов; logs bounded с continued drain/overflow receipt, не SIGPIPE producer.
Полнота parsed records/exit отдельно от overall job green. Не менять historical run/results/ledger и не смешивать receipts разных SHA.

## Дополнительная проверка текстов — без новых тестов

Источник PR — clean cd41, один bugfix commit с body/fix+tests; не33235/91062 CI-only tree.
Сверить чеклист pinned PR template, новые regression paths и истинные counts (focused13 содержит intended negative;
neighbour13 directories/14 descriptors, focusedunit3 отдельно от212 remaining util).
Develop при planner read уже37a17adc07f29e1127f100debf1d8eea00532a24; его compiler/tests diff не касается simplify_utils.
Записать actual upstream/base/mergeability source-only observation; source не менять и новый develop CI PASS не выводить.
Обнаруженный новый overlap/исправление upstream → handoff, не скрытый rebase/второй fix.
Kani/macOS/full-regression replay не часть задания. Kani-like C остаётся C test, закрытие Kani#5085/B3 не заявлять.

## Deliverables и STOP

В t0 **kani3300/cbmc-zst-bits2expr/prready/**: INPUTS.json, CI-MANIFEST.json, CI-REQUEST.md,
CHECKLIST.md, REVIEW.md, RESULT-CBMC-ZST-PRREADY.md (≤25 строк), CI-only patch/commit SHA и source-unchanged hashes.
Static Git/hash/source/Python/shell syntax checks разрешены; никаких local C/C++/Kani/CBMC compilation/verification.
Один bounded Luna High review environment/status/selection/CI isolation, без nested delegation; исправить конкретные findings.
Local CI-only commit author/committer Tiramisu-Cake <igkharin@gmail.com>, без [skip ci], **не push**.
Research [skip ci], тот же author/committer, stage только prready/, локально; coordinator решает транспорт/запуск.
Issue/PR drafts main planner уже подготовил; если обновлять — только по source или новым curated coordinator receipts,
никаких выдуманных212/212, performance claims/full CI PASS. Новая disclosure сохраняется дословно.
После reviewed package STOP. Последняя строка: `READY <sha локального CI-only PRREADY commit>`.
