# KANI3300 G1R5
Задание: `TASK-KANI3300-G1R5.md` @ research `b9457b49971807224cd1ec093712ece42919cd90`; выполнена одна стадия, Cloud $0.
Kani production: `070566e6023a0a88f25dc53d738136bc16b18882`.
Kani тесты: `bdd46381220994e06e90c5a15d30b1db564abc63`, `4914c6c2d737e068c5a30547120d15dfb56e7a15`, `8639a651fd5fef812c711ebf62c7ff2bebd7f089` (финальный кандидат после ответа координатора).
Автор всех Kani-коммитов — Tiramisu-Cake через git -c; Kani не пушился, сообщения без skip-ci.
Итоговый diff от `5b2265c41`: 6 файлов, +16/-300; production и тесты отдельными коммитами.
Нерезолвимый callee ограничен shadow-участием; base потеря target отмечена отдельно, delayed-UB golden сохранён.
Move-source clearing полностью убран с синхронной правкой emitter/model signatures; paired transfer и forget no-effect сохранены.
По ответу координатора выбран вариант 2: удалены все десять moved-from source проверок; переноса в positive нет. Negative 60 / positive 63; positive source/golden побайтно равны G1R4, Known limitation описана в NOTES.md.
Forget-array fixture теперь непустая; golden/guard прежние. CBMC134 статически не локализован: четыре исходных теста сохранены, `padding-candidate.rs` + три гипотезы в NOTES.md.
PASS: rustfmt wrapper с `--config-path rustfmt.toml` (edition=2024), 3 production + все 23 G1 test .rs + reduction candidate; git diff --check.
PASS: точный inventory source/property/summary 60/60/60 и positive 63; 11/11 SHA pinned nightly API sources, сигнатуры и unused после удаления проверены статически.
Независимое ревью: Luna HIGH; тот же reviewer проверил дельту ответа координатора — blockers нет; production неизменён и покрыт предыдущим ревью; identities/ограничения — REVIEW.md.
NOT_RUN: compiler `-D warnings`, cargo/rustc/Kani/CBMC/fork CI (прямой запрет); runtime outcomes UNKNOWN, proof credit NONE.
Никаких Cloud/build/dispatch/Actions/PR/issues/comments/raw evidence; дальнейший fork CI остаётся координатору.
