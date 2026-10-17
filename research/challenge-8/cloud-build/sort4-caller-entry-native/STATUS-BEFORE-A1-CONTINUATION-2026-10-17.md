# select/sort4 — A1 common trait-contract: NO-GO / checkpoint

Owner `select-sort4`; worktree `/root/verify-rust-std-select-night`; ветка
`research/night-select-sort4-cloud-2026-10-09`. Source-кандидат:
`bc2af77223428df14b61300a81eb99541c49723e`.

Разрешённый эксперимент R/C/G подготовлен как **UNRUN-кандидат**.
Threshold/interface hypothesis не подтверждена. Первый установленный blocker
запуска — отсутствует полный P1 gate: привязка `Self,F`, трёх scoped input regions,
полных clauses и native pre/returning/unwind AST исходного `small_sort` к обеим
actual impl. Проверки threshold и формы generic call этого не заменяют.
Сквозное исполнение/классификация всех 26 строк и отдельный exact-pair receipt
для N-false31 также не завершены. `run(a)` остаётся закрытым preflight;
`cloud_build_enabled=false`, proof/infra run pins не выпущены.

[Точный checkpoint](cloud-build/sort4-caller-entry-native/A1-RCG-CHECKPOINT-2026-10-17.md),
[semantic rationale/gates](cloud-build/sort4-caller-entry-native/A1-RCG-SEMANTIC-GATES-2026-10-17.md),
[независимый source review](cloud-build/sort4-caller-entry-native/A1-RCG-INDEPENDENT-REVIEW-2026-10-17.md).
R/C/G, exporter/schema/decoder, threshold bodies, generic proof, P1, negatives
и семь свежих регрессий — **NOT_RUN**. Подтверждённых Brief gates нет: Build
не запрашивался и Brief отсутствует. Raw logs/archives не читались.

Локально: **96 изолированных синтетических parser/classifier tests PASS**;
Python AST parse, последовательное применение R→C и exact SHA256 checks PASS.
Это сервисные/структурные проверки, не compilation или formal verification.
Source review проверил сохранение native envelope в C, identities в R,
запрет selected redirect, привязку focus к compiler `Body.span` и порядок receipt;
это source-reported claims, без независимого proof credit.

Сессия: 00:28:49Z–01:46:25Z, завершена NO-GO checkpoint до основного лимита
02:28:49Z (finish-only предел 02:58:49Z). [Отдельный счёт](cloud-build/sort4-caller-entry-native/BUDGET-A1-TRAIT-CONTRACT-2026-10-17.json)
закрыт без Build: **расход 0/960 Cloud секунд, Builds 0/1**, 960 неиспользованных
секунд retired, без переноса. Coordinator v3, slots и исторические ledgers не
менялись; ни Actions, ни Cloud dispatch не выполнялись.

Следующий конкретный шаг — реализовать и независимо проверить полный P1 AST
mapping/equality gate, затем связать всю матрицу и exact-pair N-false31 lifecycle.
До запуска нужны полный review, proof/infra pins, recipe closure и открытое
разрешённое окно/счёт; этот checkpoint не разрешает автоматический Build.
A1/A2 **NOT ACHIEVED**, index 15% и experimental profile **UNACCEPTED** неизменны.
Полный A1 требует последующей доказанной actual small_sort→helper передачи;
A2, ZST/resource redesign, C5/copies и sort8 остаются вне задания.

Policy read: WORK-POLICY 2026-10-10 + owner Evidence Brief 2026-10-17.
Все исходные локальные изменения инструкций Evidence Brief сохранены и не
включены в commits этой сессии. [Предыдущий STATUS](cloud-build/sort4-caller-entry-native/STATUS-BEFORE-A1-TRAIT-CONTRACT-2026-10-17.md)
сохраняет прежние run IDs, failures и закрытые бюджеты без изменений.
