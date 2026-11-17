# TASK — w14: независимый review S1 components и S1-08 candidate

Это верификация корректности, не security-работа. Отвечай кратко. Runtime Codex.
Свежая независимая сессия, модель/effort оставить установленными в pane, без вложенной делегации.
Вход g0 `013f288ca5111c0587e087567d2ec4182856be1d`.

## Exact review inputs

Репозиторий `/root/verify-rust-std-kani3300-g0`, только committed candidate и pinned dependencies:
- U component `kani3300/ch8-s1/s1-07/run-43923266772/accept-u/`, commit
  `16e36c4a2c244bb23ae71c80e5aa6db5f95e5338`;
- PFC component `.../accept-pfc/`, commit `013f288ca5111c0587e087567d2ec4182856be1d`;
- S1-08 package `kani3300/ch8-s1/s1-08/`, commit `8ea1c1d370f4076eb6ed4aeaa0a96898499ce580`;
  std `/root/verify-rust-std-ch8-s1-08-w13` `99e8456d200fff1299ee5756279cddb23921dc65`,
  parent `5be85699b8826e3286c0bf89efb9affefac0acb5`;
  control `/root/kani-ch8-s1-08-w13` `9ccd882ef2460fbc97400594e7e3dfc884a4a997`,
  parent reviewed `9208b373c0a08a265fa0d7493a6529e331065271`;
  stock tool `0aac16ef62da9e9d5645782d458593e5d78143ba`.

Assurance policy: PFC bounded source-reported Profiles v4 с доверием pinned stock compiler. Independent AST/MIR
provenance не требуется и не присваивается. Это не blanket helper exemption и не caller-only подмена PFC.
Составить собственные выводы по коду/evidence: author READY/test counts и coordinator recommendations не proof.

## Review scope

1. U: доказательность exact site/function/operation rules и всех premises для arithmetic/bounds safety, включая
   shift RHS semantics и active_post loop invariants; полнота обработки, отсутствие исключений sorting relation,
   согласование с same-run inventory/source/variant. Оценить, что tests проверяют semantics ниже hash gate.
2. PFC: full symbol/instance/trait/type/impl/source clauses/producer semantics и native links, check/modifies roles,
   mode requires/ensures, exact negative variant patches/oracles, допустимая normalization. Не требовать отсутствующих
   independent compiler-origin fields как нового gate; не принять raw-symbol diagnostic pair вместо clause proof.
3. S1-08: эквивалентность всех assertion operands/evaluation order/guards/assumptions/geometry/domain/covers,
   assert-assume vs старый panic path по pinned producer; negative fixtures и oracle identities; 127 role mappings,
   111 future labels vs 16 preserved semantic bindings, supplemental conditional roles; observed/source promises
   различать. Контроль source/control/request/variant/file pins, payloads, shallow ancestry и преемственности
   runner/decoder/export/native capture/snapshot/location/checks/flags/caps. Нового admission внутри runner нет.
4. Проверить exact hashes и meaningful targeted validation. Допустимы read-only replay, small Python synthetic tests,
   Git-fixtures/demangler; не запускай compiler/rustfmt/full runner. Не повторяй broad suites без причины.

Write scope: только `kani3300/ch8-s1/review-after-07/` — REVIEW.json/md, validation/evidence anchors и HANDOFF.md.
Не исправляй код автора самостоятельно. Concrete localized findings (severity, path:line, evidence/reproducer,
минимальная нужная правка) передай координатору; он вернёт original owner. Gate по каждой части отдельно
APPROVE/CHANGES_REQUIRED с пределом assurance. Source/control runtime/CI NOT_RUN, review не dispatch GO.

W11 независимо сводит components в новый accept-v3/. Пока его committed candidate не выдан — не ревьюить
незавершённые файлы и не ждать его вместо доступного scope. Координатор при готовности передаст exact SHA
как delta того же review; при отсутствии delta закончи этот bounded review с composer NOT_REVIEWED.

Времени/объёма достаточно. Работать до результата, STOP только по реальному blocker или фактически достигнутому
установленному лимиту, не по оценке «не успеваю»/объёму/контексту. Новое рабочее окно по CORE от старта.
Без push/CI/публикаций/ledger, локальных cargo/rustc/Kani/CBMC, full raw logs/archives.
Shared g0: stage/commit только review/, не git add -A/reset/rebase чужих изменений.
Коммит `[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>.
Финал `READY <g0>` с verdicts либо `STOP <реальный blocker>`.
