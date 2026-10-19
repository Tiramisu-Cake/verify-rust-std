> **Процесс итераций, 2026-10-19:** [ранние checks → целевой proof → полная матрица](research/challenge-8/ITERATION-PROCESS.md). Service error-path tests обязательны для затронутого runner; использовать существующий Cloud preflight. Принять на безопасной границе без изменения активных inputs/T0. Измерять закрытые proof obligations отдельно от setup-работы.

> **Evidence Reader, 2026-10-19:** [актуальный краткий guide](research/challenge-8/EVIDENCE-READER-GUIDE.md). Использовать `/usr/local/bin/smallsort-brief` (v0.8): Brief → адресные `--catalogue`/`--search` → `--file --pointer`/`--start` → отдельно разрешённый audit, только если данных всё ещё недостаточно. Запросы проекции разрешены обычному агенту; полные/raw логи и массовая выгрузка запрещены. Этот порядок заменяет старые указания сразу запрашивать audit при неполном Brief; бюджеты и closed-сессии не меняются.

# Challenge 8: постоянные инструкции команды

**Приоритетная политика отчётности CI:** [SmallSort Evidence Brief](research/challenge-8/EVIDENCE-BRIEF.md).
Она действует для всех SmallSort agents, worktrees и reviewers и переопределяет
любые противоречащие ей инструкции этого файла или иных обычных инструкций чтения
evidence.

Работаем в форке `Tiramisu-Cake/verify-rust-std`. Прямое актуальное поручение
владельца имеет приоритет. Использовать назначенные worktree и branch; сохранять
чужие изменения, не делать reset/force-push и не редактировать чужие worktrees.
GitHub-команды всегда адресовать явно нашему форку.

Перед работой прочитать:

1. [WORK-POLICY](research/challenge-8/WORK-POLICY.md): миссии, полномочия и сессии.
2. [STATUS](research/challenge-8/STATUS.md) своей ветки и самый свежий checkpoint;
   конкретное действующее поручение важнее общего snapshot.
3. [AGENT-RUNBOOK](research/challenge-8/AGENT-RUNBOOK.md): единая процедура;
   [Cloud runbook](research/challenge-8/cloud-build/README.md) для разрешённых запусков.
4. [COMPLETION-PLAN](research/challenge-8/COMPLETION-PLAN.md),
   [индекс](research/challenge-8/README.md),
   [Challenge 8](doc/src/challenges/0008-smallsort.md),
   [общие требования](doc/src/general-rules.md), actual SmallSort и относящиеся
   к выбранному обязательству specs/proofs/runner/profile.

Миссия сохраняется между сессиями; разрешение на исполнение, сроки и бюджет
учитываются отдельно. Docs, status-check и принятие правил не открывают proof-фазу.
В разрешённых границах агент сам исправляет setup и выбирает следующий полезный
шаг. Явный stop, выход за scope или новое trust-обязательство требуют решения
владельца; промежуточный PASS сам по себе не завершает миссию.

Компиляция, source extraction, proof runners и verification — только в
разрешённых Cloud Build lanes. На VPS запрещены Kani/CBMC/VeriFast, Cargo
build/check/test, rustc, bootstrap/x.py и эквивалентные subprocess/container
запуски; не устанавливать build/verifier dependencies и self-hosted runner.
Разрешены чтение/правки, Git, hashes, syntax/static parsing и малые изолированные
classifier/parser tests по [WORK-POLICY §4](research/challenge-8/WORK-POLICY.md#4-дешёвые-проверки-на-vps-разрешённое-исключение).

Использовать согласованный v3 coordinator: максимум три project-wide queued/running/unresolved
Build, один на стабильного owner и ledger. Не обходить dispatcher и не править
вручную live coordinator/чужой учёт. Actions dispatch и изменение triggers —
только по отдельному прямому поручению.

Разрабатывать свои specs/proofs. Не импортировать чужие решения и не менять
runtime std, алгоритмы или generic signatures ради proof. Эксперименты — под
`research/challenge-8`; injection/extraction — в одноразовом Cloud checkout.
Не коммитить generated/injected source, downloaded logs и build output.

Не ослаблять posts, не удалять failing assertions/resources/covers, не добавлять
Freeze/Copy/purity к unrestricted safety, не предполагать ownership bridge и
не отключать unwind/leak/dead-code/validity/uninitialized/refinement checks.
Safety и ordering premises раздельны. Pointer rewrite сохраняет provenance,
permissions и применимость к actual source. Перед использованием summary
доказать actual callee той же версии; чужой failing helper не блокирует baseline.
Negative засчитывается только на intended stage/predicate/location.

Tool pins и trusted semantics фиксированы именованным разрешённым профилем.
Узкие патчи возможны только в границах mission assignment с semantic rationale,
trust review и regression gate до реализации. Frontend/proof-AST rewrite тоже
меняет trusted semantics. Экспериментальный профиль и полнота actual theorem
имеют отдельные статусы; зелёный fixture/collector не квалифицирует инструмент.

После содержательного результата обновить компактный STATUS, существующий
EXPERIMENT-LOG и coverage/design при изменении их claims. Сохранять source/run/tool
identities, неудачи и прежние verdicts; docs не повышают proof status. В активной
сессии агент сам следит за конкретным Build. На stop/лимите — evidence, учёт,
checkpoint с активным ID и следующим разрешённым действием. Отчёты — кратко
по-русски; не обещать работу после закрытия сессии.

Draft PR в форк допустим в пределах задания. Merge, upstream PR, внешние
комментарии, tool application и bounty submission требуют отдельного поручения.
Документационные изменения не требуют proof build.

Прежние ветки, Actions-команды, бюджеты и stop-правила сохранены в
[архиве](research/challenge-8/archive/team-procedure-2026-10-10/README-ARCHIVE.md)
как история, без действующих полномочий.
