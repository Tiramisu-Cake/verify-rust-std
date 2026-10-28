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
