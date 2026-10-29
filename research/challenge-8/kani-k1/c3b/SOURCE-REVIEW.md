# Ограниченная проверка source invariants

Проверялся diff `691dca04d6..a03456b8d9 -- library`, без запуска verifier.
Это проверка исходников, не дополнительное computational proof evidence.

- Runtime SmallSort и тела requires/ensures не менялись.
- Assertions, output assumptions и stub targets не ослаблялись.
- START1..4 / END соответствуют точному множеству `START < END < 17`;
  матрица54 исчерпывает четыре старых диапазона в `[u64;17]`.
- Для bytes16/17 исчерпаны обе ветви stable/unstable и длины15,16,17.
- N11/12 сохранены вместе со всеми offsets1..N; unwind assertions остаются.
- `proof_cover!` при default cfg вычисляет predicate как `let _ = predicate`;
  при controls вызывает прежний `kani::cover`. Coverage obligations теперь
  opt-in; default CI не устанавливает эти auxiliary existential witnesses.
- In-sort mutation witness тоже opt-in; короткий ordinary witness проверяет
  итоговые две записи в Cells. Мутирующие значения и comparator result остаются
  независимыми произвольными значениями.

Конкретных domain holes или утраченных assertions в diff не найдено.
Kissat, достаточность новых unwind и времена устанавливаются только GCB-замерами.

## Дополнение по route split 7cedf2deb9

Проверены `general_stable_stub_for_route` / `general_stub_route_harness` и
`general_route_properties_for_route` / `define_general_sortedness_route_harness`.
Фиксация stable=false/true разбивает прежний bool-домен исчерпывающе.
Произвольные полноширинные массивы, общий probe, scratch48, asserts sortedness
и multiplicity, stub targets и unwind50/34 сохранены. Correct u64 N15 controls
и прочие merge wrappers сохраняют nondeterministic bool wrapper. Новых output
assumptions нет. Это source audit; он не устанавливает достаточность unwind,
успех solver или время. Общий helper меняет IR35 merge моделей, поэтому их
старые времена не переиспользуются как окончательные.
