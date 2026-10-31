# WRAP-N2 — пилот checked wrappers для трёх `small_sort` (N2, real body, без leaf stubs)

Исполнитель: Codex, свежая сессия, tmux 4. Worktree `/root/verify-rust-std-kani-wraptwo`, ветка
`experiment/kani-k1-wraptwo-20261031` (создана координатором) от `6f3a2629615cc7184b840d3c21aaea54b129267e`. Cap 88.96
унаследован. Ожидание Build — `k1g.sh watch UUID` и завершить ход (не опрашивать статус).
Evidence Brief / Select-Merge к K-1 не относятся.

Прочитать: `TASK-SPECFIX.md` (неизменяемые свойства/запреты/логи/rustfmt действуют),
`RESULT-SPECFIX.md` (StageA + A2: профили и canonical guard работают на pin),
`/root/verify-rust-std-kani-k5/research/challenge-8/kani-k1/RESULT-K5.md` (раздел free_wrapper_cell:
что уже пробовали и где упёрлось — memcmp unwind 6), `planner-closing-answer.md` п.2.

## Цель (F01)

Первые проверенные correctness-контракты на уровне трёх entry points в форме «checked concrete
forwarding contract»: свободная proof-owned функция с фиксированным T и canonical pure comparator,
которая исполняет НАСТОЯЩИЙ trait entry:
- `<T as StableSmallSortTypeImpl>::small_sort(v, scratch, is_less)`;
- `<T as UnstableSmallSortTypeImpl>::small_sort(v, is_less)`;
- `<T as UnstableSmallSortFreezeTypeImpl>::small_sort(v, is_less)`.
Типы (выбраны заранее, три различимых specialization paths — подтвердить по source dispatch):
- Stable: `Cell<u8>` → default fallback; scratch игнорируется (можно пустой), modifies только input.
  (Если всё же stable u8 — scratch ≥ N+16 и он меняется: не обещать untouched scratch целиком.)
- Unstable: `u8` → Freeze/Copy network route (на N2 исполняется insertion, не sort9/sort13).
- Freeze: локальный `#[repr(transparent)] NonCopyU8(u8)` без Copy/Drop → default Freeze general.
  Существующий private `WrappedU64` соседнего модуля не импортировать, visibility не расширять.
Model: полный u8 / `get()` / inner u8; key = значение `>> 1`, чтобы flip младшего бита проверял
full-value oracle. requires: N=2, geometry/init; ensures: sortedness по pure model + полная value
relation (scalar `old(count)`, независимый probe, общий на pre/post), frame — по реально разрешённым
writes, uninit tail не читать. Wrapper принимает typed fn pointer, requires — его canonical value,
передаёт его в настоящий trait call; ensures используют pure model и не зовут F.
Собственные model/count/probe/comparators в `wrap.rs`; без `merge::specfix` API и shared statics
(тогда зависимость только от неизменяемых runtime bodies). PFC на каждый wrapper, без stub_verified.
N2 — gate интерфейса/PFC/controls; полного threshold claim нет, три имени не покрывают все реализации.
Не повторять лишний K5 preamble; достаточный unwind или компонентный oracle, unwinding assertions не
отключать. Наследуемые из TASK-SPECFIX запреты на runtime/signatures действуют; entry wrappers здесь —
явная цель, а не запрет.

Controls (opt-in, literal `kani::assert`, точный expect_check):
1) always-true fn pointer → отвергается requires/guard wrapper-а;
2) порча значения при сохранённом порядке ключей — отдельная plain real-body проверка с тем же
   checker (не дефект самого wrapper).

## Сборки (≤ $2, ≤ 2 builds)

G1 measurement, controls:true, kani_jobs 1, uninit off, timeout 10 мин: 3 PFC + 2 controls.
G2 — только если после G1 была semantic/compile правка: ПОВТОР тех же 3 PFC + 2 controls на новом tree
(actual + reserve ≤ $2, иначе PARTIAL). Inventory controls:false wrap не видит — его ставить только
для семантически неизменённого tree (work 20 мин, $0.675); если G1 прошёл и ordinary projection
byte-identical, inventory можно пропустить с честным NOT_RUN.
PRE-BUILD REVIEW → GO координатора → build. Регистрация — `#[cfg(kani_smallsort_controls)] mod wrap;`
в конце verify.rs. Library commit отдельно от research, `[skip ci]`, без force.
Результат ветки — не integrated PASS: после интеграции exact tree проверяется заново.

## Не делать

N7/N8, N16, миграцию PFC, правки smallsort.rs и чужих verify-модулей (только новый
`verify/wrap.rs` + одна строка регистрации), adapters/stub chains, Actions/fullCI.

## Итог

`RESULT-WRAPTWO.md` ≤ 60 строк: какие реализации исполняются, clauses, rows/VT/RSS/covers/failure,
что ограничивает расширение до N7/N8. Маркеры `REVIEW REQUEST <sha>` / `WRAP-N2 ЗАВЕРШЁН`.
