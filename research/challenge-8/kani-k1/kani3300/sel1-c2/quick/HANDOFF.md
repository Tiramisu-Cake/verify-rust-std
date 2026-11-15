# SEL1-C2 worker15 — подготовка A/B/Q

Вход g0 `b216a04e107e62d40d639689d1b7afefe77feaf4`; 2026-11-15.
Задание: `research/challenge-8/kani-k1/TASK-KANI3300-SEL1-C2.md` + прямое поручение подготовить A/B/Q, пока worker14 выполняет P.
Готовы только заготовки; все новые Quick/Gate A/replay **NOT_RUN**. Cloud $0. Локальных сборок, setup, verifier, push/dispatch не было.
Source worker14 и research `port/` не изменялись; независимый review порта не входит в эту подготовительную сессию.

| Стадия | Готово | Локальный CI SHA |
| --- | --- | --- |
| A | accepted observer/lifecycle с 39bcdd7ad5, 3 платформы, 33 стадии, caps, request, receipt и overlay patch | `a634f93ded5440b60eac3025adbd97e2b7157159` |
| B | C2 B′ runner + test-only 6075e7ce17, 6 уникальных exact строк, caps/argv/oracles, receipt и overlay patch | `b759ee8d8aa93b154bf3906e452b26afe040445b` |
| Q | slice-07 43723531871, прежние 471 + 29 SEL1 selectors, S5 4/4 и F7 18 сравнений, sibling control/export, receipt и overlay patch | `ed8848daa5e2c4146603ba50d9883fd71df91c81` |

Все CI refs локальны, в одном worktree `/root/kani-fix-3300-sel1-c2-w15` (сейчас Quick).
Точные ветки/SHA/tree — `LOCAL-CI-INDEX.json`; base каждой заготовки — exact C2 `8e299aa624`.
Это CI templates поверх C2, **не overlays принятого SEL1 candidate**: после P их нужно пересоздать поверх принятого candidate,
а после Quick привязать A/B к точной freeze. Старые source identities намеренно заменены PENDING токенами.
В каждой ветке удалены stock workflows только CI-коммитом, оставлен один manual fork-only workflow с `false &&` guard.
Source/tests/docs/runtime за пределами CI unchanged. `[skip ci]`, автор/committer Tiramisu-Cake через per-command `-c`.

Готовые файлы в каждой стадии: `full-export/`, `ci-only-template.patch`, `CI-REQUEST.json`, `CI-OVERLAY.json`,
`receipt-template.json`, `TEMPLATE-INVENTORY.json`, `LOCAL-CI.json`, `CI-REQUEST.md`, `RESULT-template.md`.
`quick/validate_preparation.py` проверяет identities, coverage, caps, source-preserving diff и совпадение local CI/full-export.
Синтетика: Gate A 26, replay 29, Quick 7 checks PASS (ни один не запускает toolchain).
Gate A synthetic fixture использует искусственные SHA только во временной копии; реальный source binding не создаётся.
`VALIDATION.json` хранит результаты. Полный diff-check замечает пробельный context внутри принятого S5 patch;
non-patch diff-check PASS, исходные patch bytes сохранены и проверены hash.

Ждёт P/Quick/freeze:

1. Worker14 завершает P; worker15 делает отдельный review delta/стыков и сверяет 29 selectors, причины отказов и новые source bytes.
2. **До Quick**, после принятия P: привязать Q к candidate SHA/tree/parent; заново получить file blobs/SHA/directives,
   проверить native discovery 500 selectors и units против actual candidate (новые units допускают только review, не потерю прежних).
   Обновить manifest/inputs, source pin sensitivity, test-only input hashes и вложенные checksum bindings.
   См. `REBIND.md`. Q не ждёт freeze: именно принятый Q позволяет coordinator объявить freeze.
3. Coordinator публикует/запускает Q один раз и принимает полный результат; затем фиксирует **точные source SHA/tree**.
4. **После freeze**: заново открыть A/B source inventories, определить актуальное coverage, пересчитать каждый file/subtree hash,
   request hash, embedded constants, overlay manifest/file hashes, patch SHA и новые CI commits с parent exact freeze.
   570 paths/7 subtrees — заготовка coverage, не готовый manifest; число может измениться после source discovery.
5. Worker14 review A; coordinator review binding/workflow и доступности manual dispatch в fork.
   Disabled guards снимаются только в финальной проверенной CI-копии. Push/dispatch — только coordinator;
   отсутствие workflow на default branch не решено этой подготовкой, push trigger не добавлен.
6. Приёмка строго **P → Q → freeze → A → B**. B только после принятого A на той же freeze.
   В каждом будущем run — исходные exit/signal, caps, complete receipts, полезные checks/covers, runtime hashes;
   missing/UNKNOWN/timeout/OOM не превращаются в PASS. Любой drift требует review, без автоматического retry.

Финальный результат этой сессии — g0 research commit с этим handoff; source binding и proof credit не заявлены.
