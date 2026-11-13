# Независимый аудит: CBMC `bits2expr` и массивы элементов нулевой ширины

2026-11-13. Ответ на [бриф][brief] (`ba07a1f2`). Предмет: кандидат [`cd41a5c74b`][fix] поверх develop [`107a1e504c`][base] и тексты issue/PR рядом с брифом.

Метод: чтение исходников на закреплённых ревизиях и записей координатора. Сборок и запусков CBMC или Kani не было, CI я не запускал, журналы CI форков мне недоступны. Все цифры прогонов взяты из записей и мной не перепроверены. Выводы о том, каким путём идёт symex, сделаны по чтению кода; такие места помечены «по чтению».

## 1. Итог

**Правка верна и минимальна.** Возражений по семантике нет (вопросы 1–3).

**Пакет вокруг неё отправлять в upstream рано.** Претензии не к коду, а к оформлению и к тому, что именно доказано:

| № | Срочность | Суть | Что сделать |
|---|---|---|---|
| З1 | до публикации | 13 каталогов регрессий на замену одного символа. `count-2` побайтно равен `deref`, ещё шесть отличаются от него одной-двумя строками, 12 дескрипторов одинаковы. В upstream на такое исправление приходит один каталог | Оставить один каталог (§3) |
| З2 | до публикации | В 14 новых файлах стоит строка `// Author:` с личным e-mail. В `regression/cbmc` её нет ни в одном из 1100 файлов `.c` | Убрать |
| З3 | до публикации | `unit/util/zst_bits2expr.cpp` не внесён в `unit/Makefile`. В Make-сборках upstream он молча не компилируется и не запускается | Перенести случаи в `unit/util/simplify_expr.cpp` |
| З4 | до публикации | Контроль с `memcpy` проходит по причине, не связанной с дефектом, и общего вывода не даёт | Убрать из PR и из текстов |
| З5 | до публикации | Тексты issue и PR пересказывают внутренний процесс форка; версия в issue названа одна, а команда взята из прогона другой; чек-лист не совпадает с шаблоном | Переписать (вопрос 11) |
| З6 | до публикации | Новые тесты исполнялись в одном из пяти профилей `regression/cbmc`. `negative` доходит до решателя наверняка; если дойдёт и `zero-length-inner`, в `--cprover-smt2` вероятен отказ, родственный известному upstream (#9370) | Прогнать штатные workflow upstream внутри форка |
| З7 | к сведению | Огромное число элементов нулевой ширины теперь даёт O(N) операндов вместо мгновенного отказа | Ничего; иметь готовый ответ ревьюеру |
| З8 | к сведению | В lowering остаётся родственный инвариант для структур с битовым полем (по чтению) | Вне этого PR |

Остальное коротко. Два оставшихся отказа unit-тестов вызваны обвязкой follow-up, а не кодом (вопрос 8). Прогон Kani для PR в CBMC не нужен (вопрос 9). Дублей в CBMC нет, отдельный issue не нужен (вопрос 12).

**Решения за владельцем:** состав тестов для upstream (З1, З4); прогон workflow upstream в форке (З6), это новый CI, которого бриф не разрешает; комментарий в kani#5085 после открытия PR (вопрос 12).

## 2. Ответы на вопросы брифа

### 1. Верна ли граница `>= bitst{0}` для массивов

Да. [Входная проверка][entry] даёт не-union типу ровно `pointer_offset_bits(type)` бит. Для массива элементов нулевой ширины это ноль при любом числе элементов, то есть пустая строка. [Цикл][array] берёт `std::string(bits, i * 0, 0)`, корректный пустой срез, рекурсивно строит элемент и кладёт ровно N операндов в `array_exprt` исходного типа. Теги восстанавливает ветка `struct_tag`. Соседние поля не страдают: [ветка struct][struct] сдвигает смещение на ширину компонента, здесь на ноль.

Новое условие дословно повторяет то, что уже стоит в ветке struct (L305). Оно согласуется и с остальным кодом, где нулевая ширина разрешена давно: бэкенд ([e021eef4a0][c-e02], 2022) и lowering ([a53fa0fd20][c-a53], 2022; [8749eae331][c-874], октябрь 2026). Альтернативы хуже. Отдельная ранняя ветка дублировала бы цикл. Результат в виде `array_of` сломал бы обратимость: [`expr2bits`][expr2bits] такого выражения не знает.

### 2. Достаточны ли остальные проверки, не открыт ли новый инвариант

Достаточны. Неизвестная ширина и неконстантный размер отсекаются на входе: [`pointer_offset_bits`][width] возвращает «нет значения», и функция выходит до `PRECONDITION` в L339.

Типы нулевой ширины, которые могут оказаться элементом массива:

- пустая struct или struct из полей нулевой ширины: ветка struct, результат есть;
- пустой union: [L269–L270][union-branch];
- массив нулевой длины или массив таких элементов: эта же ветка, рекурсивно;
- `ID_code` (ширина 0 по [L211–L214][width]): подходящей ветки нет, функция возвращает «нет результата», вызывающий оставляет выражение как было. Раньше здесь был abort.

Проверки `> bitst{0}` для [vector и complex][vector-complex] правильно оставлены: ни C, ни Rust через Kani не дают такого элемента нулевой ширины, тестом это не закрыть.

Новых инвариантов правка не открывает. Преобразование числа элементов в `size_t` (L341–L342) стоит до изменённой проверки. Отрицательный или слишком большой размер падает одинаково на базе и на кандидате; с разбором в [REVIEW.md][review] согласен.

Меняется одно (З7). Если число элементов помещается в `size_t`, база падала сразу, а кандидат выполняет `reserve_operands(N)` и N рекурсий, причём N не ограничено длиной входа. Для `struct E z[1u << 30]` или Rust `[(); usize::MAX]` это отказ при выделении памяти или долгая работа. В lowering [`bv_to_array_expr`][lower-array] ведёт себя так же. Условием публикации не считаю.

### 3. Другие вызывающие

Прямых вызовов шесть: [`byte_extract`, ветка `array_of`][be-arrayof] и [общая ветка константы][be-const], [`byte_update`][bu-const], [член константного union][member-union], [`extractbits`][extractbits], [`bitreverse`][bitreverse]. Последние два передают только битовые векторы, ветка массивов для них недостижима.

Неверного выражения не получит никто. Срезы для полей ненулевой ширины считает прежний код, поля нулевой ширины информации не несут, а там, где раньше был abort, теперь значение. Выбор ветви union для непустого входа не меняется: ветвь нулевой ширины отсекает входная проверка.

Покрытие (по чтению). Все типизированные чтения в тестах приходят из одной точки, общей ветки константы. Symex хранит массивы до 64 элементов поэлементно ([чтение][fs-read], [порог][magic]), поэтому операнд здесь `array_exprt` из констант, а не `array_of`. Ветка `array_of`, `byte_update` и член union регрессиями не затронуты. Пробелом это не считаю: контракт `bits2expr` от вызывающего не зависит, и unit-тесты проверяют саму функцию. Круговых преобразований на уровне unit и одной сквозной регрессии достаточно.

Одно наблюдение (по чтению). У `simplify_member` нет защиты от цели нулевой ширины, которая есть у `byte_extract` ([L1905–L1908][be-zero]). Чтение члена-массива ZST из константного union приводит к `bits2expr("", …)` и на базе падает там же. Это ещё один путь к тому же инварианту, не новая проблема.

### 4. Корректен ли C-воспроизводитель, не пусты ли проверки

В модели CBMC корректен. Пустая struct размера 0 — расширение GNU C, CBMC его поддерживает намеренно (так сказано в [e021eef4a0][c-e02]). Выравнивание `struct W` равно 1. Чтение `unsigned char[8]` через `struct W *` нарушает правило эффективного типа ISO C, но CBMC его не моделирует и трактует чтение как побайтовое. В тексте для upstream достаточно слов «GNU C»; про ISO C ничего утверждать не нужно. Union ради выравнивания в `interior` для CBMC лишний, но безвреден.

Проверки не пусты. По чтению, пользовательские утверждения сворачиваются в константы, а значения берутся из восстановленной константы: потерянные байты дали бы FAILED. Слабость одна: заполнение одним байтом `0x5a` не отличит перестановку целых байтов. Это закрывает третий unit-случай: разные значения, оба порядка байтов, точное сравнение выражений. Unit-тесты устанавливают семантику функции независимо от фронтенда C.

**Контроль с `memcpy` не контролирует то, что о нём написано (З4, по чтению).** Запись `memcpy(&w, buf, 8)` становится присваиванием в `byte_extract(w, 0, unsigned char[8])`. Перед присваиванием symex [переименовывает тип левой части и упрощает её][symex-lhs], и упрощатель [сужает её до члена][be-narrow] `w.pad`, потому что `pad` в точности покрывает эти 8 байт ([выбор члена][subexpr]). Поле `z` в операции не участвует, структурная константа не строится. Тест проходит до правки и после неё и о пути без типизированного чтения ничего не говорит.

Для раскладки с двумя ненулевыми полями, как в `position-first`, сужение невозможно. Запись пойдёт через правило [«обновление всего объекта»][bu-full] в ту же общую ветку константы, и `memcpy` на базе должен упасть на том же инварианте. Запуском это не проверено. Следствие: фраза «A `memcpy` version of the same copy verifies» верна только для этой раскладки, и байтовая копия сама по себе от дефекта не защищает.

### 5. Достаточно ли тестов, чего не хватает, сокращать ли

Для upstream их слишком много (З1). Ориентир — пять недавних исправлений в develop, у каждого один новый каталог и 34–61 добавленная строка. Ближайший аналог, [8749eae331][c-874], ослабляет одно условие для массивов нулевой длины в lowering: три файла, +46/−1. У кандидата 28 файлов и +629/−1.

Недостающих граней, обязательных до публикации, нет:

- теговые элементы, вложенность, счётчики 0/1/2, порядок ветвей union покрыты unit-тестами;
- отрицательную и неизвестную ширину валидным C не построить, неизвестная ширина до ветки не доходит;
- очень большие счётчики тестировать не нужно (З7).

Что оставить, описано в §3.

### 6. Точен ли отрицательный оракул, держится ли дифференциальный вывод

[Дескриптор `negative`][desc-negative] сам по себе не требует, чтобы отказ был единственным: строки вида `^\*\* 1 of \d+ failed` в нём нет (шаблон «N of M failed» используют 71 дескриптор в `regression/cbmc`). Обвязка форка проверяла это снаружи, upstream увидит только `test.desc`.

Предлагаю в upstream его не нести. Его задачу, показать, что проверки не пусты, решает сам факт: регрессия падает без правки. К тому же это единственный тест, которому решатель нужен наверняка, то есть единственный, чей исход заведомо зависит от профиля (вопрос 7). Если нести, то со строкой про единственный отказ.

Дифференциальный вывод «12 из 13 упираются в инвариант массива» записями поддержан. [Классификатор обвязки][harness-classify] ставит статус `ZST_ARRAY_INVARIANT` только при `Invariant check failed`, `bits2expr` и `el_size_opt` в выводе, а деревья двух заданий различаются одной строкой. Самих статусов по случаям я не видел. Тринадцатый случай, `memcpy`, в различии не участвует (вопрос 4).

### 7. Какие прогоны нужны до PR

Обязательно:

1. Парный прогон (база и правка) итогового набора тестов. Если состав изменится, как предложено, запись r2 перестанет относиться к отправляемым файлам.
2. Итоговые тесты во всех пяти профилях `regression/cbmc` ([Makefile][regr-makefile], [CMake][regr-cmake]): SAT с валидацией, `--paths lifo`, `--cprover-smt2`, `--z3`, инкрементальный SMT2. Обвязка форка исполняла только первый. Новый тест, красный в CI upstream, блокирует PR, поэтому это требование, а не пожелание (З6).
3. Проверка форматирования для итогового коммита. Для текущего кандидата она есть: clang-format 18.1.8 чист по записи r2, cpplint из репозитория на двух изменённых C++-файлах даёт 0 замечаний (запускал я, это статический линтер).
4. Перенос на текущий develop. Он ушёл на два коммита (`37a17adc07`), пути не пересекаются, слияние чистое.

Почему профили важны (по чтению). Тест `negative` доходит до решателя наверняка: ложное утверждение остаётся в уравнении. В позитивных тестах пользовательские утверждения сворачиваются, и неконстантной остаётся одна встроенная проверка. Когда локальный массив модели `memset` выходит из области видимости, в `__CPROVER_dead_object` [попадает недетерминированное значение][dead-update], и следующее разыменование указателя на локальный объект [сверяется с ним][dead-check]. У symex есть правило, которое должно свернуть и её, [по value set][vs-simplify]. Если так, позитивные тесты до решателя не доходят и от профиля не зависят.

Но это цепочка выводов по коду, и цена ошибки известна. `--cprover-smt2` [кодирует struct конкатенацией][smt2-struct] и пропускает только те члены, которые [`is_zero_width`][is-zero-width] считает нулевыми. Массив нулевой длины из ненулевых элементов к ним не относится. Отказ на структуре с членом `char e[0]` у upstream уже записан: [#9370][cbmc-9370], пункт 2 ([проверка в `flatten_array`][smt2-flatten]). Член `unsigned char z[2][0]` из `zero-length-inner` — родственная форма. Если её уравнение всё же дойдёт до этого бэкенда, отказ вероятен. Каталоги с массивами пустых struct под это правило не попадают. Профили надёжнее прогнать, чем вывести.

Проще всего закрыть пункт 2 штатными workflow upstream: открыть PR из ветки с чистым кандидатом в `develop` форка. `develop` форка сейчас равен базе, так что разница PR совпадёт с кандидатом. Запустятся те же 13 workflow, что и в upstream: пять профилей, unit-тесты в сборках Make и CMake, 32-бит, ARM, macOS, Windows, clang-format и cpplint. Секрет нужен только загрузке покрытия, её отказ в форке ожидаем. Сам push ветки без PR запустит одну сборку документации. Половину пункта 1, падение на базе, даст существующая обвязка.

Не нужны: парный baseline для util (вопрос 8), прогон Kani (вопрос 9), регрессии на других вызывающих (вопрос 3). Остальные платформы достанутся даром с тем же прогоном.

### 8. Два оставшихся отказа unit-тестов

Парный baseline не нужен, упоминать их в PR тоже не нужно. Причина в обвязке follow-up, а именно в ключе `--reporter xml`.

- В r2 unit-бинарь запускался без ключей, с консольным репортёром. По записи оба теста тогда прошли на том же исходнике: из 212 упали ровно семь, и все семь зависят от z3.
- В follow-up добавлены `--reporter xml --order lex`, а stdout стал каналом.
- XML-репортёр Catch [включает перенаправление потоков][catch-xml]: на время теста `std::cout` и `std::cerr` [пишут в память][catch-redirect]. Дочерний процесс после `fork` это наследует.
- `piped_process.cpp:72` ждёт текст «Launching abcde failed», который дочерний процесс [пишет в `std::cerr`][pp-child]. При XML-репортёре текст остаётся в памяти дочернего процесса и до родителя не доходит. Это объяснение полное.
- `run.cpp:45` получил 0, потому что `run()` [возвращает `WEXITSTATUS` без проверки `WIFEXITED`][run-status]. Ноль означает, что дочерний процесс не завершился кодом 1 из [`exit(1)`][run-child]. Аварийное завершение в `exit()` при перенаправленных потоках правдоподобно, но мной не установлено.

Проверить дёшево: та же выборка с консольным репортёром и установленным z3 должна дать 212 из 212. Штатный workflow upstream запускает unit-тесты именно так.

### 9. Нужен ли прогон Kani

Для PR в CBMC не нужен: мейнтейнерам CBMC достаточно C-воспроизводителя. Он нужен, чтобы утверждать, что исправлены B3 или #5085, и чтобы снимать обходной путь в Kani.

Минимальный набор, с CBMC, собранным из ветки PR, и с откатанным [обходом B3][kani-b3]:

1. воспроизводитель из [#5085][kani-5085] дословно и его вариант с `const`;
2. типизированная копия `Tail { u8, [(); 2] }`, то есть случай, который обход не покрывает;
3. два теста из коммита обхода: `zst-union-edge-array-first` и `zst-union-arm`;
4. один вариант с неконстантными байтами (`kani::any()`). Он идёт через lowering, а не через сворачивание констант; lowering правка не трогает (З8).

Два замечания к стороне Kani. Kani [закрепляет CBMC 6.11.0][kani-deps], так что исправление дойдёт до пользователей только с новым выпуском CBMC и обновлением этого файла; до тех пор обход нужен. И комментарий в обходе называет причиной lowering, а падает сворачивание констант в `bits2expr`. Lowering эти типы обрабатывает ([L1355–L1402][lower-extract-struct], по чтению). Перед PR в Kani формулировку стоит поправить.

### 10. Один коммит, тело, форматирование, документация, чек-лист

Один коммит с исправлением и тестами соответствует [шаблону PR][pr-template]. Тело непустое и по существу верное; третий абзац после сокращения тестов ужмётся до одной фразы. Руководство пользователя править не нужно. Форматирование чисто (вопрос 7).

Что не соответствует правилам и обычаям репозитория:

- **Unit-файл (З3).** [`unit/Makefile`][unit-makefile] перечисляет источники явно, [CMake][unit-cmake] берёт их по маске. Новый файл — единственный, который CMake собирает, а Makefile нет. Сборки Make (Ubuntu make-gcc и make-clang, macOS, VS 2022, BSD) его не увидят. Проще всего перенести три `TEST_CASE` в `unit/util/simplify_expr.cpp`, сразу за [существующим тестом `bits2expr`][unit-existing]: нужные заголовки там подключены, так же поступил upstream в [7b2dcad6bc][c-7b2]. Заодно отпадают вопросы о заголовке файла и тегах.
- **Заголовок и теги**, если файл всё же остаётся. [Стандарт][coding-header] требует блок автора по образцу существующих файлов: в `unit/util` блочный заголовок у 64 файлов из 78, строка `// Author` у пяти. [Теги][coding-unit] должны называть функцию: `[bits2expr]`, а не `[zst-bits2expr]`.
- **Строки `// Author` в `main.c` (З2).** cpplint файлы `.c` не проверяет, так что строка там ничего не решает, а личный адрес в текст чужого репозитория вносит. В поле автора коммита адрес останется, как и в прочих публичных коммитах владельца; это упоминаю только для полноты.
- **Дескрипторы.** `--gcc` действует только при `os == "windows"` ([config.cpp][config-gcc]) и ни в одном дескрипторе upstream не встречается. `--64` и `--little-endian` для байтовых проверок не нужны. Пояснительной секции после второго `--` нет, а у исправлений дефектов она принята (см. `empty_compound_type2–4`).
- **Имена каталогов.** «ZST» — термин Rust. Соседи называются `empty_compound_type4`, `byte_update_flexible_array_bitfield`.

Строка Disclosure уместна. В upstream 171 из последних 300 не-merge коммитов develop несут трейлер `Co-authored-by` с ИИ-ассистентом, включая [8749eae331][c-874].

### 11. Точны ли тексты issue и PR

[Черновик issue][issue-draft]:

- **Версия и команда не сходятся.** Названа версия 6.11.0, а команда с шестью флагами запускалась на develop. На 6.11.0, судя по [исходной записи][origin], запускалось `cbmc test.c`. Шаблон просит точную команду. К тому же `--gcc` вне Windows ничего не делает, а `--c11`, `--64` и `--little-endian` на Linux x86_64 совпадают с умолчаниями. Нужна пара «версия и команда» из одного и того же журнала.
- **Вместо пересказа нужен блок сообщения** (`Invariant check failed`, `File:`, `Condition:`), как в #5085.
- **Абзац про CI форка лишний целиком.** «12 of 13 focused cases», «fixed-case oracles», ссылка на Actions форка — это описание исправления и внутренний словарь. Ссылка к тому же протухнет.
- **Фразу про `memcpy` убрать** (вопрос 4), «in our focused cases» тоже.
- «no actual Kani/Rust replay is claimed here» — оборонительная фраза для внутреннего употребления. Хватит ссылки: тот же инвариант для Rust в model-checking/kani#5085.

[Черновик PR][pr-draft]:

- **Раздел Testing** написан тем же словарём. «Literal C reproducer» и «Kani-like C fixture» в PR не входят, читателю upstream они неизвестны. Хватит двух фраз: новая регрессия падает на develop с этим инвариантом и проходит с правкой; что запускалось сверх того.
- **«a `memcpy` control»** и перечень из 13 тестов уйдут вместе с тестами.
- **Чек-лист** пересказан своими словами. Нужен текст [шаблона][pr-template] дословно, с пометкой «n/a» у неприменимых пунктов.
- **Ссылки на #5085 нет**, хотя это главная мотивация. Добавить без слов «Fixes» или «Closes»: проблему в Kani PR не закрывает до нового выпуска CBMC.
- Полезна одна фраза о прецедентах: ветка struct и lowering уже принимают нулевую ширину.

Утверждений о полном прохождении наборов в черновиках нет, оговорка о непроведённых проверках честная. Поддержка GNU C описана верно.

### 12. Отдельный issue или сразу PR, дубли

Сразу PR, с воспроизводителем в описании и со ссылкой на model-checking/kani#5085. Шаблон PR issue не требует, исправление в одну строку объясняет себя само, а второй тред только добавит переписки. Отдельный issue оправдан в одном случае: если PR откладывается надолго, а проблему хочется зафиксировать.

Откладывать не советую. [#5085][kani-5085] открыт 2026-10-27, с 2026-10-30 назначен участнику команды Kani, комментариев и связанных PR нет. Мейнтейнер CBMC месяц назад сам исправил родственный дефект в соседнем коде ([8749eae331][c-874]); такой же правки для этого места можно ждать в любой момент. Небольшой чистый PR сейчас ценнее безупречного пакета через неделю.

Дубли, проверено 2026-11-13:

- поиск по diffblue/cbmc: issue со словом `bits2expr` нет; PR восемь, все закрыты в 2018–2021;
- открытые issue о типах нулевого размера: [#8284][cbmc-8284] (shadow memory) и [#9370][cbmc-9370] (SMT2-бэкенды), другие механизмы;
- головы PR #8400–#9474, не влитые в develop (421 из 804): файл меняют #8451, #8878, #9014, #9429, проверка массива у всех прежняя. С #9429 кандидат сливается без конфликта;
- в model-checking/kani PR со словом `bits2expr` нет.

Вопросов к мейнтейнерам до PR не нужно. По [CODEOWNERS][codeowners] файл относится к общим владельцам, отзыв ожидается в пределах двух недель. После открытия PR полезен короткий комментарий в #5085 со ссылкой, чтобы исполнитель не делал ту же работу. Внешний комментарий требует отдельного поручения.

## 3. Что предлагаю отправить

Эскиз. Не собирался и не запускался; до публикации нужен парный прогон (вопрос 7).

**Коммит:** одна строка в `simplify_utils.cpp`, один каталог регрессии, unit-случаи в существующем файле.

**Регрессия.** Форма взята из каталога `position-middle`, который по записи r2 падает на базе и проходит с правкой в профиле SAT.

```c
#include <string.h>

// GNU C: an empty struct, and any array of it, has size zero.
struct empty
{
};

struct with_empty_structs
{
  unsigned char a[4];
  struct empty z[2];
  unsigned char b[4];
};

int main(void)
{
  unsigned char buf[8];
  memset(buf, 0x5a, sizeof(buf));

  struct with_empty_structs s = *(struct with_empty_structs *)buf;

  for(unsigned i = 0; i < 4; ++i)
  {
    __CPROVER_assert(s.a[i] == 0x5a, "bytes before the empty structs");
    __CPROVER_assert(s.b[i] == 0x5a, "bytes after the empty structs");
  }

  return 0;
}
```

```
CORE gcc-only
main.c

^EXIT=0$
^SIGNAL=0$
^VERIFICATION SUCCESSFUL$
--
^warning: ignoring
Invariant check failed
--
bits2expr used to fail an invariant for arrays whose element type has zero
width, such as arrays of GNU C empty structs, although its struct branch
accepts zero-width components. A typed read of constant bytes reaches it via
byte_extract simplification.
```

Два замечания к регрессии.

- Тип из #5085, `unsigned char z[2][0]`, покрыт вторым unit-случаем. В C-регрессию его стоит добавлять, только если прогон профилей зелёный (вопрос 7).
- Вариант с инициализатором `{1, 2, 3, 4, 5, 6, 7, 8}` вместо `memset` даёт различимые байты. Он к тому же не зависит от проверки с `__CPROVER_dead_object` (вопрос 7): без `memset` в неё попадает константа. Но это другой вход: и падение на базе, и прохождение с правкой нужно подтвердить прогоном.

**Unit-тесты:** три существующих `TEST_CASE` перенести как есть, теги `[core][util]`, как у соседей.

**Тело коммита:** первые два абзаца оставить, третий заменить одной фразой о регрессии и unit-случаях.

**Описание PR**, скелет:

```
bits2expr fails an invariant when it has to rebuild an array whose element
type has zero width, such as an array of GNU C empty structs or of
zero-length arrays, inside a larger aggregate:

    <the reproducer>
    <the "Invariant check failed" block, copied from an actual run>

The struct branch of bits2expr already accepts zero-width components, and
byte-operator lowering already admits zero-width members and zero-length
arrays (a53fa0fd20, 8749eae331). With a zero element width the existing loop
takes empty slices and still produces one operand per element, so the only
change is to accept a width of zero.

Kani hits the same invariant for Rust input: model-checking/kani#5085.

Testing: the new regression test fails on develop with the invariant above
and passes with this change. <what else was actually run>

<the checklist from the PR template, verbatim>

Disclosure: ...
```

## 4. К сведению: родственный инвариант в lowering (З8)

По чтению, запуском не проверено. Когда `lower_byte_extract` не может разобрать struct по полям, например из-за битового поля, он собирает битовый вектор и вызывает `bv_to_struct_expr`. Тот для компонента нулевой ширины [передаёт дальше весь вектор][lower-struct]. Для массива из двух пустых struct [инвариант в `bv_to_array_expr`][lower-array] требует `0 * 2 == ширина вектора` и не выполняется. Октябрьская правка upstream ослабила его только для нулевого числа элементов.

Это отдельный дефект. Кандидат его не трогает и не открывает: неконстантные данные шли этим путём и раньше. Из Rust он вряд ли достижим, битовых полей там нет. В этот PR его включать не нужно; при желании это тема следующего.

## 5. Что сделано и чего не делал

Сделано:

- прочитаны кандидат, база, тег `cbmc-6.11.0`, текущий develop, все файлы рядом с брифом, коммит обхода в Kani;
- проверена сливаемость кандидата с develop `37a17adc07` и с PR #9429 (`git merge-tree`, конфликтов нет);
- запущен cpplint из репозитория CBMC на двух изменённых C++-файлах;
- дубли искал поиском GitHub и по головам PR #8400–#9474; состояние #5085 сверено сегодня.

Не делал:

- не собирал и не запускал CBMC и Kani, не запускал CI;
- не читал журналы CI форков: доступа нет, цифры r2 и follow-up взяты из [записи координатора][ci-result];
- не проверял запуском выводы, помеченные «по чтению»: через какую точку упрощателя идут тесты (вопрос 3); почему проходит `memcpy` и что он упадёт на раскладке с двумя полями (вопрос 4); что решатель нужен только тесту `negative` и что `--cprover-smt2` споткнётся о `zero-length-inner`, если уравнение до него дойдёт (вопрос 7); причину отказа `run.cpp:45` (вопрос 8); что lowering обрабатывает типы из обхода Kani (вопрос 9); поведение варианта с инициализатором (§3); инвариант в lowering (§4).

[brief]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/ba07a1f2fc2fab36118c0ecd2161dddbdd705cdd/research/challenge-8/kani-k1/kani3300/cbmc-zst-bits2expr/AUDIT-BRIEF-CBMC-ZST-BITS2EXPR.md
[review]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/ba07a1f2fc2fab36118c0ecd2161dddbdd705cdd/research/challenge-8/kani-k1/kani3300/cbmc-zst-bits2expr/REVIEW.md
[ci-result]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/ba07a1f2fc2fab36118c0ecd2161dddbdd705cdd/research/challenge-8/kani-k1/kani3300/cbmc-zst-bits2expr/CI-RESULT-R2.md
[issue-draft]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/ba07a1f2fc2fab36118c0ecd2161dddbdd705cdd/research/challenge-8/kani-k1/kani3300/cbmc-zst-bits2expr/ISSUE-CBMC-ZST-BITS2EXPR-DRAFT.md
[pr-draft]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/ba07a1f2fc2fab36118c0ecd2161dddbdd705cdd/research/challenge-8/kani-k1/kani3300/cbmc-zst-bits2expr/PR-CBMC-ZST-BITS2EXPR-DRAFT.md
[origin]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/ba07a1f2fc2fab36118c0ecd2161dddbdd705cdd/research/challenge-8/kani-k1/kani3300/b3p/ISSUE-DRAFTS.md#L65
[harness-classify]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/ba07a1f2fc2fab36118c0ecd2161dddbdd705cdd/research/challenge-8/kani-k1/kani3300/cbmc-zst-bits2expr/r1-ci-only.patch#L3661-L3676
[fix]: https://github.com/Tiramisu-Cake/cbmc/commit/cd41a5c74b0c42edf4f08834b3e2808dd3344cab
[base]: https://github.com/diffblue/cbmc/commit/107a1e504cd69a2f3483717c8bcfcfa59814c557
[entry]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_utils.cpp#L203-L213
[union-branch]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_utils.cpp#L263-L280
[struct]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_utils.cpp#L293-L321
[array]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_utils.cpp#L334-L363
[vector-complex]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_utils.cpp#L364-L408
[expr2bits]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_utils.cpp#L413-L486
[width]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/pointer_offset_size.cpp#L103-L221
[subexpr]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/pointer_offset_size.cpp#L623-L658
[be-zero]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_expr.cpp#L1905-L1908
[be-arrayof]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_expr.cpp#L1910-L1945
[be-const]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_expr.cpp#L1960-L2006
[be-narrow]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_expr.cpp#L2125-L2129
[bu-full]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_expr.cpp#L2197-L2210
[bu-const]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_expr.cpp#L2212-L2246
[member-union]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_expr_struct.cpp#L188-L215
[extractbits]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_expr_int.cpp#L1219-L1235
[bitreverse]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/simplify_expr_int.cpp#L2105-L2127
[symex-lhs]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/goto-symex/goto_symex.cpp#L64-L69
[fs-read]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/goto-symex/field_sensitivity.cpp#L343-L380
[magic]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/magic.h#L21
[lower-struct]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/lower_byte_operators.cpp#L99-L104
[lower-array]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/lower_byte_operators.cpp#L193-L200
[lower-extract-struct]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/lower_byte_operators.cpp#L1355-L1402
[desc-negative]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/regression/cbmc/zst-bits2expr-negative/test.desc
[regr-makefile]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/regression/cbmc/Makefile#L12-L35
[regr-cmake]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/regression/cbmc/CMakeLists.txt#L9-L37
[unit-makefile]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/unit/Makefile#L206-L210
[unit-cmake]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/unit/CMakeLists.txt#L12
[unit-existing]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/unit/util/simplify_expr.cpp#L66-L111
[catch-xml]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/unit/catch/catch.hpp#L17221-L17227
[catch-redirect]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/unit/catch/catch.hpp#L12978-L12983
[pp-child]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/piped_process.cpp#L314-L319
[run-child]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/run.cpp#L386-L390
[run-status]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/run.cpp#L431
[config-gcc]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/config.cpp#L1030-L1051
[coding-header]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/CODING_STANDARD.md#L64-L72
[coding-unit]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/CODING_STANDARD.md#L263-L279
[pr-template]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/.github/pull_request_template.md
[codeowners]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/CODEOWNERS#L1-L5
[c-874]: https://github.com/diffblue/cbmc/commit/8749eae33122071c98a9672f5966cecf9642d0fd
[c-a53]: https://github.com/diffblue/cbmc/commit/a53fa0fd208f14382b187f09069b8f8d24610ee5
[c-e02]: https://github.com/diffblue/cbmc/commit/e021eef4a0b262de0e52884279ec62f45e010070
[c-7b2]: https://github.com/diffblue/cbmc/commit/7b2dcad6bc45f1321c6e5935c02a17e5696680a3
[dead-update]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/ansi-c/goto-conversion/goto_check_c.cpp#L2265-L2287
[dead-check]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/ansi-c/goto-conversion/goto_check_c.cpp#L2389-L2396
[vs-simplify]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/goto-symex/simplify_expr_with_value_set.cpp#L158-L228
[is-zero-width]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/util/pointer_offset_size.cpp#L503-L536
[smt2-struct]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/solvers/smt2/smt2_conv.cpp#L3811-L3844
[smt2-flatten]: https://github.com/Tiramisu-Cake/cbmc/blob/cd41a5c74b0c42edf4f08834b3e2808dd3344cab/src/solvers/smt2/smt2_conv.cpp#L3848-L3864
[cbmc-8284]: https://github.com/diffblue/cbmc/issues/8284
[cbmc-9370]: https://github.com/diffblue/cbmc/issues/9370
[kani-5085]: https://github.com/model-checking/kani/issues/5085
[kani-b3]: https://github.com/Tiramisu-Cake/kani/commit/6e9e782024a19f93bf3b89ede89960bf2d9419cc
[kani-deps]: https://github.com/Tiramisu-Cake/kani/blob/6e9e782024a19f93bf3b89ede89960bf2d9419cc/kani-dependencies#L1-L3
