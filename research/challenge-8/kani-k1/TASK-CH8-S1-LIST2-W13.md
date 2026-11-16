# TASK — worker13: S1 без глобального kani list (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Твой control `c03363b3b0` (g0 `e76136d429`, вариант (a): list timeout 1500 s) **не принят**:
у организаторов шаг `Run Kani List` на verify-rust-std main длится **73 мин**
(model-checking/verify-rust-std run 43765200249, job «Kani List», step 21:44:11–22:57:30 UTC 2026-11-15).
1500 s заведомо не хватит, а S1-03 — последняя попытка S1 без владельца.

Сделай вариант (b): убрать глобальный list; binding каждой строки — per-row из её собственного
`-Z export-json` (ровно один harness, точное `name`/module path = selector, `contract` = ожидаемая
PFC-функция для PFC-строк и null для proof-строк, `is_automatically_generated=false`,
`harness_selection.exact=true`, `matched_count=1`, `unmatched_filters=[]`). Если export не содержит
поля, нужного для прежней силы binding, — явно перечисли, что теряется, и предложи замену
(например, проверка source location `file`/`line` против exact source). Отсутствующий/невалидный
export = UNKNOWN, не PASS. Receipts list-фазы больше не нужны; оставь bounded head+tail
stdout/stderr для каждой строки (и для первой компиляции std — она теперь в первой строке, учти
~6 мин компиляции в бюджете первой строки: compile происходит внутри первой invocation —
проверь, не попадает ли он в 600 s/root; если попадает — отдельная warm-up компиляция std
(например, тем же kani с заведомо существующим дешёвым harness) с собственным лимитом и receipt,
а не повышение per-root cap).

Тот же S′ `f22f84f316`, 23 строки/oracles/caps. Synthetic tests, review.
g0 `kani3300/ch8-s1/kani-host-nolist/`. Последней строкой `READY <control> <g0>` или `STOP <причина>`.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
