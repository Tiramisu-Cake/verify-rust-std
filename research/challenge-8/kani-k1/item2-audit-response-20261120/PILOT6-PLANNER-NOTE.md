# Кампания 6. Статистика массивов на ветке refinement

Согласен отложить слои и сначала измерить refinement на неизменном std. В roster есть одна поправка. **На закреплённом CBMC 6.11.0 `P17-REFINE` не напечатает `arrayConstraints` даже с `--show-array-constraints`.** Этот флаг считывает `get_default()`. С `--refine-arrays` фабрика выбирает `get_bv_refinement()`, а конструктор `bv_refinementt` вызывает `bv_pointerst` с параметром статистики по умолчанию `false`. Оба аргумента могут успешно пройти разбор. Отсутствие счётчиков при этом ожидаемо.

Предлагаю оставить `--show-array-constraints` у `P17-STATS`, а у `P17-REFINE` передать только `--refine-arrays`. На P17 сравнить фазы, первую CNF, сообщения refinement, RSS и итог. Счётчики `arrayWith/arrayIf/arrayEquality/Ackermann` описывают только базовую кодировку. Первую CNF refinement читать вместе с последующими итерациями, поскольку ограничения могут добавляться позднее. Для двух полноразмерных корней и общего бюджета изменений не требуется. [Задание кампании](PILOT6-IMPL-TASK.md)

Источники на теге CBMC `cbmc-6.11.0` (`820ff0f555b4`): `src/goto-checker/solver_factory.cpp:112–123,355–362,416–438,782–786`, `src/solvers/refinement/bv_refinement_loop.cpp:13–28`, `src/solvers/flattening/bv_pointers.h:19–23`.
