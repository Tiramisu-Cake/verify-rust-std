> **Короткий старт новых Select/Merge сессий (2026-10-21):** обязательное [CORE](agent-workflow/CORE.md) + своё CURRENT-TASK + CHECKPOINT/STATUS. Этот документ — подробный справочник: открывай нужные разделы, без полного перечитывания. Legacy active sessions сохраняют свои inputs/T0/счета. [Инструменты и порядок](agent-workflow/README.md).

# Адресное принятие общих правил всеми тремя агентами

Это инструкции переноса docs, не команда начать proof-сессию, не автоматический
merge PR и не миграция executable coordinator. Основная копия общих правил — main
нашего форка. Новая редакция принимается на следующей безопасной границе; более
конкретные действующие поручения сохраняются. Не прерывать полезный Build и не
менять его pinned inputs. До следующей сессии adoption обязателен.

## Порядок

1. Владелец/reviewer проверяет documentation draft PR к main и отдельно решает
   merge. После решения зафиксировать **полный commit принятой редакции**. Если
   владелец прямо поручил принять до merge, использовать полный reviewed PR SHA,
   не движущееся имя branch. Draft сам по себе не разрешение на proof dispatch.
2. Каждый из трёх агентов сам переносит docs в **свой назначенный worktree**.
   Порядок select → merge/insert_tail → VeriFast удобен для сверки одинаковой
   редакции; независимые docs adoption могут идти параллельно на безопасных
   границах. Не запускать чужие client commands и не редактировать чужие worktrees.
3. Каждый записывает ACK в своей существующей session card/checkpoint, с policy
   SHA, local docs commit, mission/scope, более конкретным текущим поручением,
   временем наблюдения, main/absolute deadlines, подтверждённым account state и
   следующим разрешённым шагом. Окончание main окна означает finishing-only до
   absolute deadline, не автоматическое CLOSED и не stale AUTHORIZED; закрытие
   счёта подтверждается записью владельца с точным SHA/временем. Не плодить отдельный
   общий ledger. VeriFast ACK также ссылается на scope своего review/integration
   задания и потребительские profiles; upstream publication не подразумевается.
4. Сверить три ACK и общую редакцию. Если обновление позднее текущего snapshot,
   собственный latest checkpoint остаётся фактической истиной. Следующее proof
   задание отдельно возобновляет выполнение и выдаёт окно/бюджет.

## Точный список переноса

В собственном worktree сначала `git status --short`, `git worktree list`,
`git branch --show-current`, `git rev-parse --git-dir --git-path index` и
`git remote -v`; origin должен быть `Tiramisu-Cake/verify-rust-std`.
Не делать switch/reset другого worktree. Fetch и resolve принятого commit:

```bash
git fetch origin
git rev-parse --verify "$c8_policy_commit^{commit}"
git show --stat "$c8_policy_commit"
```

`c8_policy_commit` — полный SHA принятой редакции, предоставленный reviewer,
не research HEAD. Просмотреть docs в нём через `git show SHA:path`.

**Общие файлы, которые следует принять в одинаковой редакции:**

```text
AGENTS.md
research/challenge-8/WORK-POLICY.md
research/challenge-8/AGENT-RUNBOOK.md
research/challenge-8/COMPLETION-PLAN.md
research/challenge-8/PROGRESS-REVIEW.md
research/challenge-8/PLAN.md
research/challenge-8/cloud-build/README.md
research/challenge-8/cloud-build/PARALLEL-BUILDS.md
research/challenge-8/INFRASTRUCTURE-TASK.md
research/challenge-8/ADOPTION.md
research/challenge-8/archive/team-procedure-2026-10-10/
```

Перед заменой сохранить tracked branch-local прежние версии общих документов
в собственном датированном docs archive, с полным прежним HEAD и source paths.
Особенно сохранить branch-specific AGENTS/runbook/PLAN/Cloud команды, budgets
и stop-условия как исторические. Добавить archive index: «superseded procedure;
факты только в пределах исходных identities, не полномочия». Не удалять их историю.
Uncommitted чужие изменения не включать/не перезаписывать: дождаться владельца
файла или применить согласованные docs hunks.

Затем адресно перенести только перечисленные общие файлы (например,
`git restore --source="$c8_policy_commit" --worktree -- PATH...` с **явным списком**
после просмотра diff). Если собственные постоянные правила в AGENTS не относятся
к устаревшей процедуре, сохранить их отдельным блоком со ссылкой на общий policy;
конкретный действующий assignment остаётся в своей session/phase card.
Не оставлять два противоречивых активных Cloud/Actions loop; старый блок архивировать.
Отклонения от общей редакции описать в ACK и сверить с владельцем, если они меняют
полномочия или trust boundary.

**Не переносить из main/PR:** чужие STATUS, checkpoints, coverage,
EXPERIMENT-LOG, phase cards, ledgers/BUDGET/SESSION-STATE, proof code/patches,
recipes/control/coordinator/scripts, workflows и tool pins. Не cherry-pick весь
PR: он содержит main index/snapshot и архив main истории. Не merge main/research
целиком ради правил. Новые файлы archive в списке — только исторические docs,
не research evidence или исполняемые файлы.

В своём README/index заменить лишь старый onboarding/Run/Next operating текст
ссылками на общие правила; сохранить предметный research index и run history
либо вынести старые инструкции в свой archive. Свой STATUS компактировать:
сначала сохранить прежние блоки в существующей истории/checkpoint, затем оставить
миссию, последнее проверенное обязательство, blocker, следующий шаг и evidence
links. Main STATUS/snapshot в рабочую ветку не копировать. Это docs-only и не
меняет ни pending draft implementation, ни Build inputs.

Проверить `git diff --check`, Markdown links и `git diff --name-only`: только
преднамеренные docs. Commit/push только в собственную ветку, без force-push.
Записать ACK с policy commit и local commit. Документация не требует proof run,
повторного regression или регистрации новой executable phase.

## Адресаты и точки входа на дату snapshot

| Агент | Где принимать | Что сохранить |
| --- | --- | --- |
| select/sort4 | Назначенный `/root/verify-rust-std-select-night`, `research/night-select-sort4-cloud-2026-10-09`, либо более поздний явно назначенный worktree | Latest C1 bridge checkpoint, supplied-premise debts, closed ledger, own stable owner `select-sort4` и allowlist |
| merge/insert_tail | Новейший назначенный `/root/verify-rust-std-merge-origin`, `merge/incoming-origin-20261009`; старый `/root/verify-rust-std` не переключать | Incoming-origin closeout `9da02971a162468cd06602585a0dcd4a1e8d67a1`: CLOSED владельцем в 2026-10-09T21:18:12.966107Z (774/3600; 2826 closed), prior lifetime NO-GO; main 21:16:40Z и absolute 21:46:40Z 9 октября различать, сверять время наблюдения, owner `merge`, свой учёт и tool scope |
| VeriFast maintainer | Собственный назначенный `verify-rust-std` review/infra worktree (на snapshot `/root/verify-rust-std-verifast-infra`, `infra/verifast-mdnew-cfg`) | Свой fullmake checkpoint/ledger и review packages; branch STATUS может быть старым select snapshot — сверять latest RESULT. В отдельном VeriFast repo ссылаться на принятую общую редакцию, не заменять его собственный AGENTS |

Пути выше — адреса snapshot, не вечные branch defaults. Новое назначение важнее.
Все трое принимают один policy SHA; docs task не требует отправки внешних
сообщений, merge чужих patches или публикации upstream.
