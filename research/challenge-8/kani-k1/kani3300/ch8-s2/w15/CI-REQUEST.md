# S2 CI-REQUEST worker15 — общий batch после P1

Готовый proposal для координатора, NOT_RESERVED/NOT_RUN. S2 всего1–2 dispatch
для всех workers11/13/14/15 вместе; этот пакет не создаёт свой budget/job/run.
S2-01 объединяет merge32, sort13, general32 probes и ранний merge pilot.
S2-02 только по конкретному результату и coordinator GO; infra/rerun charged.
Запуск только после P1, source integration13, review и записи exact combined
std/tree/tool/CI-control/request SHA + GO в CH8-DISPATCH-LEDGER. Ledger15 не менял.
A1 results — отдельная стадия. Push/CI в этой сессии запрещены и не выполнены.

Exact standalone source/tree/model/tool — INPUTS.json и source.patch. Source
не содержит registration, model11 или tool pin update; combined export13 должен
сохранить qualified S1 API/features/pin. Actual selectors сверять с clean0aac
list по exact match: обычный readable_name без core:: prefix; source_name в JSON
хранится отдельно. Mismatch=STOP, не substring fallback. Combined/export/control
SHA пока null намеренно: этот request не разрешает dispatch standalone SHA15.

JSON фиксирует12 roots: real merge32, base/step/exit, loop pilot, endpoint
regression, simple decreases и5 expected failures. Никаких verified/assumed
summaries; real panic_on_ord_violation и comparator сохранены. Query arbitrary
u8 не участвует в runtime. Все positives требуют complete default checks,
all covers SAT/useful return; negatives — точный property/description/stage из
JSON, а не произвольный nonzero exit. Генерируемые IDs пока UNKNOWN; failure
самого source/core/API/frontend/Unsupported/timeout не intended negative.
Положительный invariant root и negative extractor controls учитываются раздельно.

CLI как S1 integration: verify-std -Z unstable-options -Z function-contracts
-Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers
-Z stubbing --no-assert-contracts --jobs=1 --harness SELECTOR --exact
--default-unwind ROW -Z export-json --export-json OUT --output-format=terse
STD/library --cbmc-args --object-bits 12. Cfg sorting+controls; uninit/value OFF;
все default checks/unwinding assertions сохранить. Solver/slicing defaults.

Один shared ubuntu24.04 job, jobs1/max-parallel1. Workflow120min: setup/tool<=30,
verification/list<=75, receipts/upload15. Root hard600s whole process group,
aggregate concurrent RSS6291456KiB (=6GiB), sampling rawKiB и /1048576 GiB.
12 rows15 estimate1650s (UNMEASURED) + два peer probes до1200s + list300s =3150s,
остаётся1350s phase reserve. Это не измерение fit: все12*600 plus peers не
вмещаются. Watchdog не начинает root без полного600s+cleanup reserve; остальные
NOT_RUN, итог UNKNOWN. Не урезать hard cap ради остатка, не auto-rerun.
Coordinator14 сводит общую таблицу до dispatch; новые peer controls могут
изменить estimate и требуют повторного inventory/cost review.

Измерять driver/frontend/backend/process-group peak RSS и wall по фазам, если
доступны; model/checker overhead считать только по реально измеримым границам,
не приписывать backend общий wall. TERM→KILL по caps, сохранить original exit/
signal и snapshot. Output bounded, export8MiB/row, total256MiB/retention7days;
truncation/missing receipt/partial setup/UNKNOWN не PASS. Runner реализацию здесь
не меняли; использовать существующие reviewed coordinator preflight/error paths.
No new workflow/tool/backend. NOT_RUN fallback для всех не начатых строк.

P2 decision: real-body merge32 cost+correctness и отдельный invariant extraction
receipt. PASS pilot не квалифицирует actual core loop/merge summary. Если budget
не проходит, decompose через validated invariant, не повышать timeout. General32
и sort13 consumers имеют собственные leaf-qualification условия11/13. Результат
не означает S3 geometry matrix, all-T/F, extra-UB, termination или acceptance.
