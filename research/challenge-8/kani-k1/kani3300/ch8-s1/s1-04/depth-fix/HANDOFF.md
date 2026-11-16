# S1-04 depth fix — HANDOFF

Одна стадия завершена локально, independent review PASS.

- Новый control: `205b0e98c771a7e6c6b8ec28414494868bcca4e0`;
  tree `27692f2145d4faec363ba04faea9feb775cccd5f`;
  единственный parent `40b5d9cf48900ff1e227e1fbba24cb5b2edbf8d5`.
  Worktree `/root/kani-ch8-s1-04-depth-w13`, branch `work/ch8-s1-04-depth-w13`.
  Author Tiramisu-Cake <igkharin@gmail.com>; control без `[skip ci]`.
- Std `5be85699b8826e3286c0bf89efb9affefac0acb5` и tool
  `0aac16ef62da9e9d5645782d458593e5d78143ba` сохранены.
- [CI-REQUEST.json](CI-REQUEST.json) — точная копия control request;
  SHA256 `fce0e446f1506d0aebf4afc9929075843beed69c01a626391f119e18125850b7`.
  Изменены только три payload-хеша; schedule/35 rows/14 groups/4 unions сохранены.
- g0 — commit, содержащий этот HANDOFF; точный SHA дан в итоговой строке READY.

Control-depth **3** во всех4 jobs покрывает `HEAD → 40b5d9cf4 → 0aac16ef62`.
Это точная достаточная глубина для parent checks и endpoint diff; полная история
не нужна. Export/tool оставлены на2: CI identity-проверки используют HEAD/tree,
тип pinned commit и status. Полный разбор Git-команд, включая локальные
исторические validate-сравнения и overlay operations: [GIT-OPERATIONS.md](GIT-OPERATIONS.md).
От старого control `2a532e5913173d6af4490c25d74c587f7bf1a749` delta только в4 файлах:
workflow, check_package.py, test_package.py, CI-REQUEST.json. Остальные поля workflow
сравнены как типизированные документы и равны после нормализации4 depth.

Проверки: [TESTS.json](TESTS.json) — **38/38 PASS**, 137.334s; прежние36 тестов
сохранены. Новая симуляция создаёт12 настоящих shallow file:// clones по YAML depths
без alternates, вызывает реальные control()/verify_source(); depth2 воспроизводит
исходный diff exit128 при доступном HEAD^, depth1 отвергает HEAD^.
Новый YAML gate проверяет все12 depths,40 отдельных depth mutations отвергаются.
[validate.py](validate.py)/[VALIDATION.json](VALIDATION.json): PASS для графа,
identity/payload hashes, anchors, parent/author/message, scope и layout.
[REVIEW.md](REVIEW.md): независимый GPT-6 Luna HIGH, PASS для bounded delta;
[review-packet](review-packet/metadata.json) проверен на exact candidate/spec identities.

Симуляция использует синтетические истории; production shallow clone и GitHub run
не выполнялись. Прежние g0 validate-сравнения со sibling/control history остаются
локальными и не входят в CI. Локальные137.334s не измеряют GitHub runner;
прежний timeout1min synthetic-шага сохранён (предыдущий пакет локально135.724s),
CI timing остаётся непроверенным и требует наблюдения в следующей стадии.

Push/CI/публикаций/ledger и локальных cargo/rustc/Kani/CBMC не было.
Proof execution NOT_RUN; proof credit NONE. Предыдущие commits/artifacts сохранены.
Следующей стадии передан новый control; запуск остаётся за координатором в рамках
его действующих полномочий и бюджетов.
