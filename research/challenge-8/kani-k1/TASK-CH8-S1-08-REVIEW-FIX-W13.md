# TASK — w13: review delta S1-08, exact closure coordinates в negative oracles

Это верификация корректности, не security-работа. Отвечай кратко. Продолжение твоей подготовительной стадии
по concrete w14 finding, модель/effort не менять, без субагентов/CI/push/ledger.

Reviewer сейчас проверяет frozen source99e8456d20/control9ccd882ef/package8ea1c1d370. Предварительный concrete finding:
два negative oracle property IDs require_active closures сохранили source coordinates100/106, тогда как после
positive macro rewrite closures находятся95/101. Exact matcher требует полный ID. Самостоятельно подтвердить
по pinned source и producer; это source-coordinate repair прежних logical failure oracles, не подбор по FAILURE.

1. Сохранить old source/control/package immutable для независимого review. Source99e менять не нужно, если
   нет отдельного конкретного finding. Использовать новый control worktree `/root/kani-ch8-s1-08-fix-w13`.
   Готовый исправленный control сделать sibling над тем же parent9208b373c0, не amend/reset9ccd и не наращивать
   ancestry без нужды: контроллерный preflight/shallow depth5 сохранять.
2. Исправить все prospective closure coordinates в exact negative IDs по фактическому source99e text/column/span;
   проверить остальные шесть oracles, source hashes/contexts, intended expressions/class/status и sole-failure
   semantics. Никакой wildcard/suffix-match/relaxation. Изменить только source-derived coordinates, прочие
   логические oracle identities сохранить. Новых результатов exporter/verifier нет.
3. Добавить meaningful fail-closed regression, которая выводит closure location из текущего source и проверяет
   заявленный полный oracle ID; старые100/106 и coherent shifted/stale source ID должны отклоняться. Не просто
   сравнение двух копий одинаковой literal строки. Включить проверку всех declared negative oracles, чтобы
   выявлять подобные source shifts до CI. Admission не переносить в runner.
4. Пересобрать request/embedded request/ROLE-MAP metadata/pins/hashes/envelope/patches и preflight/tests.
   35 roots/14 groups/127 roles/111 labels/16 preserved bindings/113 covers и previous constraints сохранять.
   Review w14 остальных inputs продолжается: если coordinator передаст дополнительные concrete findings по
   этому кандидату, включить их минимальные fixes до финального freeze. Сам scope не расширять.

Write scope в g0: только новый `kani3300/ch8-s1/s1-08-r1/`, полный corrected package с IDENTITIES,
CI-REQUEST.json/md, ROLE-MAP, exact patches, validation, REVIEW-DELTA.md и HANDOFF.md. Старый s1-08/ не переписывать.
Указать old→new logical ID spans и полный новый source/control/request SHA; source99e ожидается прежний.
Review **PENDING_DELTA_W14**, не заявлять GO или выполненный independent review. Координатор передаст fixed
committed delta тому же w14; до этого публикация/dispatch запрещены.

Времени и объёма достаточно: исправлять до результата. STOP только при реальном blocker/фактически достигнутом
установленном лимите, не по оценке «не успеваю». Без локальных cargo/rustc/Kani/CBMC/rustfmt/full raw logs.
Shared g0: только свои пути, не git add -A/reset/rebase чужих коммитов. Commits `[skip ci]`,
author Tiramisu-Cake <igkharin@gmail.com>. Финал `READY <g0> <source SHA> <fixed control SHA>` либо реальный STOP.
