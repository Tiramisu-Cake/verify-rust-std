# U8N9 — source audit до измерений

База: `ac45675c2bdcf5629086b87b4a9a385b53df61db`.
Library commit: `2c65b6cdd94ad22ac71be1bb301d9f4109d9035c`.
Library tree: `95a25d9241f071a8c22b6c6f5edebb3a31e45100`, заморожен для G1/G2.
Машинные результаты Python-проверки: `source-audit.json`.

Единственное изменение library — 57 строк в конце `verify/merge.rs`.
Все 61353 исходных байта файла сохранены побайтно; остальные library-файлы прежние.
Семь новых имён отсутствуют в исходном модуле. Импорты и модули не добавлены;
новый macro объявлен после всех старых вызовов. Поэтому разрешение старых helper/macro
dependencies сохраняется в обеих cfg, включая probe/oracle и production call graph.
Все новые helper/macro/entry items private и gated `cfg(kani_smallsort_controls)`;
ordinary delta0, controls proof delta3. Новых controls нет; stubs отсутствуют.

Combined baseline `general_stable_direct_u8_n9` разворачивается старым
`define_general_direct_harness` в `general_route_properties::<u8, _, 9>(lt_u8)`.
Его произвольный bool `stable` исчерпывающе выбирает два случая:

| Случай combined | Новый entry | Реальный вызов | Scratch |
|---|---|---|---|
| stable=false | general_direct_u8_n9 | small_sort_general | внутренний прежний |
| stable=true | stable_direct_nonconst_u8_n9 | StableSmallSortTypeImpl::small_sort | non-const48 |
| stable=true, иной fixture | stable_direct_const_u8_n9 | StableSmallSortTypeImpl::small_sort | const48 |

Для каждой ветви совпадают arbitrary `[u8; 9]`, arbitrary full-value probe через
`set_value_probe::<u8>()`, snapshot до сортировки, исходный `lt_u8` function item
и общий `assert_sorted_and_probe_preserved::<u8, _, 9>`. `let mut cmp = lt_u8`
выводит тип function item, без closure, cast или fn-pointer annotation.
Статическое ограничение исходного helper N<=16 выполнено при N=9.
Unwind34 совпадает; после oracle расположен один unconditional cover каждой ветви.
Это те же условия достижимости, что `cover(!stable)` / `cover(stable)` после oracle
в combined. Отдельного selector в новых helper-ах нет.
Итого general + non-const stable покрывают функциональный домен combined;
stable const имеет тот же функциональный домен, с иной инициализацией fixture.
Python сверил тела двух stable helper-ов: различается только initializer.
Перестановка создания stateless function item относительно probe/input не добавляет
условий и не меняет symbolic domain. Probe используется прежним bytewise oracle.

Rustfmt заданным wrapper/config: exit0; `git diff --check`: PASS; строки Rust <=100.
Локальные rustc/cargo/Kani/CBMC не запускались. G1/G2 controls compile успешен;
targeted merge/unused/dead_code/error diagnostics не найдены. Ordinary cfg исключает
весь новый блок: исходные items/dependencies прежние, fresh ordinary compile не запускался.
Статический аудит отдельно от proof credit: G1 три новых entry SUCCESS/covers1/1,
G2 general и nonconst stable SUCCESS/covers1/1 на том же library tree.
Baseline остаётся non-const combined; соседний CONSTWAVE не переносился.
