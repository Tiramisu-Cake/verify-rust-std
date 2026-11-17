# TASK — w11: acceptance S1-08 (одна компактная стадия)

**PREPARED_NOT_ISSUED. Выдать только после terminal run44095954742/attempt1 и committed intake w13.**
Это верификация корректности, не security-работа. Отвечай кратко. Runtime Codex;
свежая сессия, текущая pane-модель/effort, без субагентов. Времени/объёма достаточно;
объём/контекст/«не успеваю» не blocker. В сообщении выдачи координатор добавит exact intake commit.

Входы: `kani3300/ch8-s1/s1-08-postrun/INPUTS.json`, новый `s1-08/run-44095954742/` intake,
reviewed s1-08-r1 request/ROLE-MAP, `S1-ACCEPTANCE-DECISION-2026-11-17.md`.
Переиспользовать reviewed S1-07 accept-v3 и его U/PFC functions/components, не переписывать classifier с нуля.
Большие историю/планы/full audits не перечитывать; semantic rules не переоткрывать без конкретного mismatch.

1. Проверить exact новые run/head21592884db/attempt1/std99e/tool0aac/request77ae… pins, provenance,
   полный same-run stock/rich inventory, snapshots/source/variant/native identities. Неполная группа не становится
   qualified из-за полного отдельного row. Нет evidence/unknown status — fail-closed; aggregate exit не verdict.
2. **111 новых roles:** для каждого EXACT_ROLE_LABEL в immutable ROLE-MAP найти ровно один same-row/harness
   assertion ID с exact expected_description и SUCCESS, согласованными source hash/site/context и native root.
   Missing/duplicate/wrong-role/class/status/file/harness/variant дают точный PENDING, не подбор ordinal.
   Не трактовать строки из ROLE-MAP или fixture как observed messages. Остальные16 bindings/semantic sets
   независимо перепривязать к свежему source99e/evidence; legacy_s107 IDs/coordinates — только navigation.
   Supplemental54 sites учитывать по applicability/guards; не требовать N0/N1 SUCCESS в неприменимом N
   и не расширять утверждённые127 required obligations молча.
3. **U:** применять узкие reviewed per-site source-local rules с проверкой premises на actual source/hash/site.
   Не требовать старого count187/413/9986, не разрешать все std/helper UNREACHABLE через covers.
   Новый необоснованный site — UNKNOWN; mandatory post/frame/relation UNREACHABLE блокирует admission.
4. **PFC22:** method Profiles v4 — exact manual native target, full concrete instance/type/trait/impl,
   checked_with/modifies raw-symbol/property links и source clauses/variant-specific assertions. Число closure
   не задаёт роль. Independent compiler/AST/MIR trace не добавлять как gate; caller-only подмена недопустима.
   Для8 negatives сверить fresh exact predeclared sole FAILURE, включая repaired closure spans95/101;
   прежние intended failures не менять по результату. Unsupported — только exact successful unreachable guards.
5. Сохранить113 required SAT covers и их actual-call/post-check source order/meaning; SAT не заменяет role bindings.
   Пересчитать companions и4 N0..3 unions из same-run qualified members. Не переносить14/35 qualified из S1-07
   и не hardcode35/35. Итог каждой строки: QUALIFIED либо точный remaining gate. Домен только прежний smoke N0..3,
   source-reported policy, independent B1/B2/general proof credit NONE.

Write scope: только новый `kani3300/ch8-s1/s1-08/run-44095954742/accept/`.
Выход: ACCEPTANCE.md, ACCEPT.json, replay, INPUTS.json, VALIDATION.json, HANDOFF.md.
Read-only replay по умолчанию, детерминированный receipt. Не дублировать artifacts. Compact mutation checks
только изменившихся границ: labels missing/duplicate/wrong status/root/source,16 fresh bindings/sets,
stale closure oracle, foreign namespace/component, неполное U/PFC coverage, companion/union dependency.
Reuse reviewed invariant checks; не повторять сотни неизменённых tests и не начинать новый compiler design.
Новые concrete semantic gaps оставить точно описанными; не ослаблять policy и не делать repair вне этой стадии.
В HANDOFF отметить independent review нового adapter/receipt PENDING, не объявлять его выполненным.

Без push/CI/публикаций/ledger/cargo/rustc/Kani/CBMC/rustfmt/full raw logs/archives; исторические receipts
и intake immutable. Commit только своего каталога, без git add -A/reset/rebase чужих изменений;
`[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>. Финал `READY <g0>` с verdicts/gates/tests либо реальный STOP.
