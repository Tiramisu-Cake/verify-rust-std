# S1-08 — READY_FOR_REVIEW

Выполнено TASK-CH8-S1-08-CONTINUE-W13.md из task commit `2f3ede5ff4`.

Source оставлен на `99e8456d200fff1299ee5756279cddb23921dc65`: минимального
исправления не потребовалось. Control завершён локальным commit
`9ccd882ef2460fbc97400594e7e3dfc884a4a997` поверх reviewed9208.
Точные commit/tree/file/request/payload identities — IDENTITIES.json,
CI-REQUEST.json и PATCHES.json. SOURCE-CANDIDATE.patch от5be856;
CONTROL-CANDIDATE.patch от9208; обе patches восстанавливают exact candidate trees.
Все commits автора Tiramisu-Cake <igkharin@gmail.com>, с `[skip ci]`.

ROLE-MAP содержит 127 required success bindings: 111 новых constant root::role
labels для21 selected roots и16 прежних exact semantic bindings/sets. Исторические
semantic evidence сохранены отдельно и не выданы за S1-08 IDs. Прежний domain,
все guards/expressions/порядок вычислений/covers/negative fixtures сохранены.
Отдельно записаны54 supplemental entry sites с applicability, без требования
N0/N1 SUCCESS в другом N. Static expansion различает197 labels/25 defined roots,
включая четыре unscheduled symbolic roots; это не observed property inventory.

Проверено: equivalence23 macro sites и всего остального исходного текста,
source anchors/hashes, 35 rows/14 groups и их порядок, flags/checks/unwind/caps,
113 required covers, восемь unchanged predeclared negative oracles и обе variant
patches/source-under-test на новом base, полный CI payload, YAML и native scalar
schema, control/source Git identities и shallow behavior. Все63 small Python
static/synthetic/Git-fixture tests прошли. Missing/duplicate/wrong-role/status/
harness/source/request/tree/tool cases дают UNKNOWN в synthetic label interface;
это не production admission. Детали — VALIDATION.json и STATIC-VALIDATION.json.

AssertHook/constant-message extraction, panic termination, default reachability
prefix stripping и post-check cover reachability разобраны по pinned producer
в SEMANTICS.md; SHA файлов — PRODUCER-SOURCE.json. `kani::assert` сохраняет
assertion до assume; новые сообщения — source expectations, compiler NOT_RUN.
Количество generated properties и их IDs не прогнозируется. Independent AST/MIR
provenance и полный theorem из этих статических проверок не следуют.

Изменения control: std pins/anchors, required messages/ROLE-MAP, package tests,
необходимый checkout depth5 вместо4. Runner semantic diff — только два std pins;
collector/decoder/export/native capture/snapshots/location exceptions и flags
не менялись. Admission остаётся за offline stage. Source/model API,
sorting_model.rs, runtime algorithms и smallsort.rs attrs не менялись.

Следующий шаг: отдельный independent W14 review этого committed candidate и его
pinned dependencies. Review **NOT_RUN** и не объявлен пройденным. W11 U/PFC не
ожидались и не редактировались. После review остаются coordinator GO, адаптация
offline intake к точному ROLE-MAP и новый compatible run; подготовка не даёт GO.
Старые receipts не устанавливают успешность нового candidate.

Компиляция/cargo/rustc/Kani/CBMC/rustfmt/runtime/actual exporter/decoder/verifier:
**NOT_RUN**. CI/push/публикации/ledger/budget reservation: **NOT_RUN**.
Independent proof credit/B1/B2: **NONE**. Это smoke N0..3 в прежней fixture
geometry, не весь threshold16/32 и не общий Challenge8 proof.

Повторная проверка без compiler/CI из этого каталога:
`PYTHONDONTWRITEBYTECODE=1 python3 verify_package.py`.
Control synthetic suite: `python3 -m unittest -q test_runner.py test_package.py
 test_s104.py test_s105.py test_s107.py test_s108.py` из control/ch8-s1-control.
`prepare_package.py` предназначен для воспроизведения metadata на control base9208
с применённым patch; frozen committed candidate он не перезаписывает.
