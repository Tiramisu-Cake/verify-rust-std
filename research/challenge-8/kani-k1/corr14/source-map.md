# CORR14 — статическая карта доменов до сборки

Исходная combined-гармоника и весь старый correct.rs сохранены побайтово.
`static_check.py` проверяет это, одинаковые setup, общий checker, cfg, targets и параметры.
Private opt-in corr14_check_u8_n14 содержит прежний oracle: сначала sortedness,
затем probe_count_unrolled. Все четыре positive и corruption вызывают его с тем же lt_u8.
После подстановки checker body вместо пяти вызовов код совпадает с предыдущим review
92370c188b (кроме поясняющего комментария); adapter/bounds/request не изменены.
Это проверка текста; ни Rust-компиляция, ни AST/MIR equivalence ею не установлены.

| Entry (correct::) | Маршрут / scratch | Соответствие |
|---|---|---|
| sorted_permutation_general_stable_u8_n14 | symbolic bool / старый | baseline без правок |
| sorted_permutation_general_u8_n14 | general / внутренний holder48 | прежняя ветвь stable=false |
| sorted_permutation_stable_nonconst_u8_n14 | stable / non-const array48 | прежняя ветвь stable=true |
| sorted_permutation_stable_const_u8_n14 | stable / const array48 | меняется только инициализатор |
| sorted_permutation_stable_aggregate_u8_n14 | stable / aggregate holder48 | другая backing-геометрия |

Во всех пяти T=u8, N=14, F — function item merge::lt_u8; произвольный input [u8;14],
set_value_probe::<u8>() до input, тот же полный probe_count_unrolled и sortedness.
В старом helper F передаётся аргументом, в новых связывается как `let mut cmp = lt_u8`:
тип function item тот же; новых closure/comparator нет. General вызывает тот же
small_sort_general; stable — тот же Freeze impl StableSmallSortTypeImpl::small_sort.
SMALL_SORT_GENERAL_SCRATCH_LEN = 32+16 = 48, проверено по frozen source.
Положительные helpers не содержат selector, assume или ограничения input/probe.
Оба stub_verified targets, cadical и unwind50 одинаковы. Sort4 остаётся реальным.

Объединение двух fixed-route return covers представляет оба прежних маршрута;
отдельный fixed-route cover не обязан показывать противоположную ветвь.
Положительные covers стоят после общего checker. У corruption cover — после sort,
до mutation/checker; младший payload-бит не участвует в lt_u8 (x >> 1).
Ожидается ровно один count FAILED; placeholder недостаточен без ручной location.
Bounds control берёт pointer из того же adapter и делает raw write по offset48,
за всей allocation [u8;48], без safe indexing, assume_init и чтения uninit T.
Фактические FAILED location/checks/covers сверяются только после измерения.

Adapter возвращает только &mut [MaybeUninit<T>]. Borrow holder задаёт provenance,
exclusivity и lifetime; layout массивов/MaybeUninit сохраняет alignment и extent48.
Aggregate не доказывает старую array-backed fixture, произвольный backing или transfer.

Caller остаётся conditional на insert_tail/merge callee premises соответствующих доменов.
Даже ускорение и SUCCESS всех callers этого не снимают. Возможный G2 проверяет листья
на своих fixtures (insert scratch48, merge N14), без transfer к scratch48 caller.
Новые items private opt-in; ordinary cfg не получает новых items/imports.
Без локальной компиляции отсутствие новых предупреждений обеих cfg ещё не установлено.
