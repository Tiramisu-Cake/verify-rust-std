# TIDYDOCS: пакет до GO

Работа по TASK-TIDYDOCS.md, одна стадия. Ветка `experiment/kani-k1-tidydocs-20261106`, owner `k1-merge`.
Основа library — `44b972435aeff6ea88cd01e64ccea3727a98294e` (v8c); tooling — `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`.
Library `6443b4d99da9ff7d9bf33dee92bb035dbe66e838`, tree `6062452294ae749722ab3734993d9ef1af830dde`.
Request SHA256 `b35b328679111b715eeb0195c3686ff384cef8ea3e92c647dacce6157cc7bbce`. Хеши исходников — в `check-report.json`; финальный packet SHA выдаётся маркером PRE-BUILD REVIEW.

## Изменения

Комментарии очищены от истории этапов и неверных утверждений об отсутствии контрактов.
Карта модулей, реальные домены и общие ограничения собраны в `verify.rs`. Обоснования SAFETY,
независимости оракулов, допустимости заглушек и согласования leaf/consumer сохранены.
В `smallsort.rs` добавлены только девять строк комментариев у пяти контрактов.
В `realcontracts.rs` заменены 20 строковых сообщений; добавлен ровно один opt-in PFC-контроль.
Остальные атрибуты, проверки, covers, типы, длины, имена и тела не менялись.
Наблюдение о ZST read_volatile и неизвестной причине pointer-check failures оставлено без изменений.

Причины минимальности чисел unwind и превосходства Cadical не установлены. Комментарии описывают
учитываемые циклы и модель; минимальность и сравнительное преимущество не заявлены.
Для Kissat результат CITRIM измерял совместное изменение solver/unwind, а не отдельные эффекты.

## Статика

Команда: `python3 -B research/challenge-8/kani-k1/tidydocs/check_tidydocs.py`.
Lexer и macro expander переиспользуются из существующего `codefix/trimpart_static.py`, tooling не меняется.
Проверяются все 15 файлов дерева verify и smallsort.rs относительно v8c:
byte equality некомментарийных строк smallsort.rs; token equality verify после исключения только
прямых message literals в assert!/kani::assert/kani::cover и точного нового контрольного item.
Во всех строках verify.rs и verify/** длина ≤100; в smallsort.rs нет новых строк >100.
Граница 100/101 проверяется отдельно; прежние длинные строки smallsort.rs не меняются.
Normalizer имеет проверки, что predicate, unwind, сторонние literals и инверсия cover не скрываются.
Имена: ordinary 233 без изменений; cfg-on 268 = 233 + 12 прежних controls + 22 прочих opt-in + 1 новый.
У всех 233 ordinary-корней и их консервативных dependency closures совпали структура и число cover sites.
966 — число runtime covers из задания/v8c, а не повторный локальный замер; compiler inventory здесь не запускается.
Поиск запрещённой лексики в комментариях и messages пуст; идентификаторы исключены из текстового поиска.
Результаты и число строк комментариев по всем файлам: `check-report.json`, `comment-lines.tsv`.

## G1

`RUN-REQUEST.json`: diagnostic, controls=true, inventory=false, jobs=1, standard4, 5 мин/корень.
Только realcontracts.rs меняет сообщения; два обязательных positive roots уже представляют этот файл.
Добавлен ещё один короткий ordinary sort4, чтобы отдельно проверить сообщения выходного frame/covers.

| Корень realcontracts:: | Expect | Прежнее время, с | Ожидаемые covers |
| --- | --- | ---: | ---: |
| rejects_swap_comparator_writing_outside_frame_u8 | FAILED | новый | 0 |
| swap_safety_u8_backing9 | SUCCESS | 18.622524 | 6 |
| unstable_network_safety_u8_n9_stubbed | SUCCESS | 8.316227 | 1 |
| sort4_safety_u64 | SUCCESS | 35.744152 | 3 |

Времена — собственный RESULT-VEIGHTINTEG.md и bounded rows, не новый замер и не обещание времени.
Контроль использует [u8;4], in-bounds позиции 0/1, lawful `*a < *b` и захваченный u8-счётчик с wrapping_add.
`expect_check: assignable` — предварительная подстрока write-set diagnostic; точное описание неизвестно до G1.
Форма сообщения основана на [документации Kani](https://model-checking.github.io/kani/reference/experimental/loop-contracts.html),
а применимость к этому function-contract check — ожидание, подлежащее калибровке.
Gate helper проверяет наличие хотя бы одного подходящего failed check. Поэтому его PASS недостаточен:
принять контроль только если ВСЕ failed checks — assigns/modifies на записи comparisons.
Любое requires/dereference/overflow или иной failure означает некалиброванный контроль, не успех.

## Время и бюджет

Helper фиксирован: 4 × 5 + 30 = **50 минут**, reserve **$0.6750** ($0.0135/мин).
Verify cutoff — 44 минуты после validate. Tooling не меняется, отдельного request-поля для compilation timeout нет.
Из собственных diagnostic без inventory: setup до verify 348 с; compiler в CITRIM G1 был активен до 66 с,
первый CBMC — на 76 с (`veightrows/prebuild-evidence/citrim-g1-peaks.txt`).
Оценка cfg-on compilation — до 5 минут с запасом относительно cfg-off; это оценка, не измеренный cfg-on bound.
Setup ~6 + cfg-on compilation до5 + roots максимум20 = ~31 мин до summary, меньше cutoff44;
30-минутный overhead helper включает setup/compilation и запас. Inventory с его ~47 мин исключён.
Снимок budget: 246 builds, spent $106.1475, reserve $0; с нашим резервом $106.8225 < $118.96.
Собственный cap $1.50; spent $0, build count 0/2. Перед dispatch повторить budget после exact-packet GO.
G2 допустима только для нашей ошибки G1 и только после нового GO; retries нет, compile-error repair ≤1 на build.

## Уточнение после review 91d5d7543d

Перенесены четыре длинные строки комментариев; ограничения разбиты на Conventions и Not covered.
Добавлена и выполнена статическая проверка длины строк. Относительно reviewed packet код и сообщения
совпадают по токенам без комментариев; smallsort.rs и оба RUN-REQUEST.json побайтно не изменились.
Request SHA256, параметры G1 и бюджет сохранены. Это новый пакет для PRE-BUILD review; GO ещё не получен.

## После GO

Один dispatch опубликованной ветки; записать build UUID и exact source/request bindings в ledger.
Сразу `k1g.sh watch BUILD`, затем завершить ход. Не опрашивать status в цикле.
По пробуждении — только bounded summary/rows/peaks/log-grep, check-tooling с указанной базой,
полный состав failed checks контроля, covers позитивных строк и итоговые расходы.
RESULT-TIDYDOCS.md ≤40 строк, затем REVIEW REQUEST с полным SHA и TIDYDOCS ЗАВЕРШЁН.
