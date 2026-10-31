# CASE5 — диагностика расхождения настоящего `swap_if_less` с ожиданием (closure, `[u8; M]`)

Исполнитель: Claude Code, свежий контекст, tmux 5. Worktree `/root/verify-rust-std-kani-casefive`, ветка
`experiment/kani-k1-casefive-20261101` (создана координатором) от `f000cb484e` (итог P1-CLEAN, library
tree `73e902bec8`). Cap 88.96 унаследован. Ожидание Build — `k1g.sh wait UUID` в фоне.
Evidence Brief / Select-Merge к K-1 не относятся.

Прочитать: `RESULT-PONECLEAN.md` (раздел Case5), `poneclean/g1.case5-extract.txt`, `TASK-SPECFIX.md`
(запреты, логи, rustfmt, expect_check — действуют), источник `case5_typed_swap!` в
`verify/merge/specfix.rs`, `swap_if_less` в `smallsort.rs`, `swap_contract_fixed`/`swap_profile`
(прошедший `swap_contract_bytes17_n2` использует тот же настоящий swap через fn pointer).

## Что известно

Real `swap_if_less(v.as_mut_ptr(), 0, 1, &mut |a, b| a[0] < b[0])` на `[[u8; M]; 2]` из `kani::any()`,
ожидание `taken = y[0] < x[0]` → `(y, x)`, иначе `(x, y)`. При M = 17/128/129: падают обе
покомпонентные проверки, `==` не среди упавших, 1 из 2 branch covers не достигнут. Не зависит от
размера. Гипотеза (не проверена): после упавшего `kani::assert` путь продолжается с assume условия,
поэтому одна ветвь целиком расходится с ожиданием и её cover недостижим.

## Цель

Одной сборкой установить: какая ветвь расходится; зависит ли это от closure vs fn pointer, от M,
от формы проверки; это ошибка гармоники, особенность модели Kani или поведение библиотеки.
Library runtime не менять. Только новый opt-in модуль `verify/merge/casefive.rs` (или раздел в
specfix.rs под `kani_smallsort_controls`) и одна строка регистрации; P1 ordinary 197 не трогать.

## Матрица (все opt-in, M = 17, если не указано; literal `kani::assert` с уникальными сообщениями)

Assert→assume на pin уже установлен исходником (kani-compiler codegen/assert.rs): он объясняет отсечение
поздних checks/covers, но не первый неверный результат. Отсутствие `==` среди упавших не доказывает
его PASS. Каждый вариант меняет РОВНО один фактор относительно R0. Witness-ы не фиксировать нулями —
исходный `kani::any()` domain с различимыми значениями и обоими направлениями.

1. R0 — точная копия case5 (контроль воспроизведения).
2. R1 — `kani::assume(taken)` сразу после pre-decision, ДО вызова; cover выбранного пути после вызова,
   ДО первого assert (противоположный cover закономерно UNSAT — его не ставить).
3. R2 — то же с `assume(!taken)`. (G2 при необходимости: разделить `x[0] < y[0]` и `x[0] == y[0]`.)
4. R3 — fn pointer: `let mut cmp: fn(&[u8; 17], &[u8; 17]) -> bool = named;` (именно pointer;
   `let mut cmp = named` даёт function-item — это уточнение для G2, если pointer и closure разойдутся).
5. R4 — R0 на `[u8; 1]` (размерный discriminator; PASS не доказывает независимость от M).
6. R5 — все component booleans вычислить без assert, затем оба branch covers, затем ОДИН исполняемый
   assert: `if taken { assert(ok_taken, "...TAKEN") } else { assert(ok_not_taken, "...NOT_TAKEN") }`.
7. R6 — ожидание из снимка `let pre = v;` (семантически = R0; проверка encoding/snapshot/MIR-copy).
8. R7 — reference: тот же fixture/oracle, но вместо `swap_if_less` — `if taken { ptr::swap(a, b) }`.
   Reference PASS + actual FAIL локализует различие исполнения/модели; оба FAIL → fixture/oracle.
Expect каждого — по предсказанию в PRE-BUILD REVIEW; COMPLETE не требует совпадения всех ожиданий:
сохранить actual rows, различённые гипотезы и оставшийся UNKNOWN. Profile `swap_contract_bytes17_n2`
— не matched raw baseline (wrapper/PFC/old-model/requires различаются); raw baseline даёт R3.
Trace/playback schema не принимает — без обходов через raw logs.

## Сборки (≤ 2 builds, ≤ $1.26 reserve; ожидаемая actual ≈ $0.2)

G1 kind diagnostic, controls:true, kani_jobs 1, uninit off, timeout 3 мин, 8 rows → 54 мин / $0.729.
G2 условный, ≤ 3 rows → 39 мин / $0.5265, только с отдельным GO координатора по итогам G1.
Timeout/compile error не считаются содержательным FAILED. PRE-BUILD REVIEW → GO → build.
Inventory не нужен (ordinary не меняется; проверить статически). Library commit отдельно от research,
`[skip ci]`, без force.

## Итог

`RESULT-CASEFIVE.md` ≤ 60 строк: таблица rows/status/failed checks/covers, какая ветвь расходится,
вывод по классу (гармоника / модель Kani / библиотека / UNKNOWN) с аргументом, влияние на P1
(свернуть ли раздел case5 в P1, можно ли вернуть проверку в Part 1 и в какой форме).
Если указывает на дефект Kani — минимальный reproducer в отчёте; никаких внешних публикаций.
Маркеры `REVIEW REQUEST <sha>` / `CASEFIVE ЗАВЕРШЁН`.
