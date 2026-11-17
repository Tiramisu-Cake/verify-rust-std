# W14 → coordinator

**CHANGES_REQUIRED — W14-CELL-RETRY-01 (P2).**
Reviewed package g0 `9f4c37c894e7fecee0f59321ba66b65309a87606`,
control `da8c766f957c576eafa44bccfba2c45490cef6d1`,
tree `a0e21f185de757c05397cf32547153325012469f`, parent9208;
base7c/source99e/tool0aac — exact full pins в REVIEW.json.

Вернуть W13 owner локальную правку tests: cell-only adaptations прежних двух fallback
controls. Новые17 tests не обнаруживают overwrite captured row receipt (exit42 → null);
старый preservation control обнаруживает. Нужны сохранение original outcomes,
mid-run interruption/terminal context и bounds, без расширения execution scope.
Reviewer author code не исправлял. Остальные pins/hash/delta/timeout/shallow проверки PASS.

После fixed committed candidate — delta review этого finding. Review не GO;
решение о retry только координатору после terminal S1-08 и intake. Intake11 не ждали.
CI/push/reservation/ledger/runtime proof отсутствуют. Charge8/14 неизменён;
conditional9/14 только после нового GO и принятого run.1200≠fit600, label causality UNKNOWN,
origin/profile/composition требуют явного последующего решения; same-run credit не выдан.
