# B3 T1b: offline classification of run 43708572925

2026-11-15. Base t0 `21d68cc4c0a93f36c64ccfafe3a0bb79f171ebf1`.
**Итог: INCONCLUSIVE_AA для полных моделей.** Итог сравнения доступных
symbol-table dumps и точные счётчики приведены ниже. Это отдельная офлайн-классификация T1b,
не C2. Сборки, CI, SAT, push не запускались; исходный RESULT.json не изменён.

## Вход и воспроизведение

Прочитаны RUN-43708572925.md, TASK-B3-T1B.md и обязательные входы T1:
TASK-B3-T1.md, t1/DESIGN.md, t1/RUN-43701550489.md, t1/RESULT-template.md.
Анализатор использует только стандартную библиотеку Python. Артефакт — недоверенные данные;
его скрипты/команды не исполнялись, новых файлов внутри него нет.

```text
python3 -I research/challenge-8/kani-k1/kani3300/b3p/t1b/test_offline.py
python3 -I research/challenge-8/kani-k1/kani3300/b3p/t1b/offline.py \
  /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/t1b/dl/b3-t1b-43708572925-1 \
  --output research/challenge-8/kani-k1/kani3300/b3p/t1b
python3 -I research/challenge-8/kani-k1/kani3300/b3p/t1b/validate_offline.py \
  research/challenge-8/kani-k1/kani3300/b3p/t1b
```

INDEX.json содержит 131 final + 131 linked + 131 symtab, каждое с A1/A2/B1
и двумя режимами дампа: 393 логических модели, 1179 model-arm записей, 2358 raw dump files.
В каждом виде есть один control, то есть 130 perf + 1 control.
Проверяются SHA-256 raw dumps против INDEX, source index против исходного RESULT,
полный набор ключей, model input hash/path против source index, соответствие stdout/mode/input
записанной команде, оригинальные exit/state и пустой stderr. Это проверка согласованности
скачанного evidence; подпись источника и повторное хэширование отсутствующих GOTO-бинарников
не утверждаются. Tool pin и provenance T1/T1b остаются source-reported claims.

## Исправленный контроль: binding по реальному типу в дампе

Старый checker требовал `Pretty name` с суффиксом `::ArrayUnion::zst_array`;
фактическое имя — `ArrayUnion::zst_array`. Новый `check_control` не использует
Kani metadata и не выводит принадлежность обёртки из её имени/Pretty name:
он разрешает ребро component-type из **родительского union Type**.

В каждом из трёх видов дампа A1=A2, A1≠B1 и A2≠B1; изменён только Type обёртки:

```text
parent: tag-_197989860869864104961024652742313003089
Pretty name.: ArrayUnion
Type: union _197989860869864104961024652742313003089 {
  unsigned char bytes[8];
  struct _197989860869864104961024652742313003089::zst_array zst_array;
}
wrapper: tag-_197989860869864104961024652742313003089::zst_array
A: struct ...::zst_array { struct Unit zst_array[2]; unsigned long int zst_array_padding; }
B: struct ...::zst_array { struct Unit zst_array;    unsigned long int zst_array_padding; }
Unit: struct Unit { }
```

Checker требует точные реальные однострочные Type, неизменные parent/Unit,
`type` flags, неизменный inventory и весь остальной текст wrapper record.
Тип Unit пуст; массив из двух Unit имеет нулевую ширину; форма `[(); 2] -> Unit`
подтверждена на уровне таблицы типов. Padding и порядок компонентов не меняются.
Пробелы в примере выше добавлены для чтения; checker их не стирает.
Полная function-часть gate остаётся непроверенной из-за пустых dumps (§ ограничения).

## Нормализации и сохранение смысла

1. **AllocId и порядок symbol records.** First occurrence по всему дампу неверен:
   первой бывает отсортированная по временному номеру запись или initialize.
   Новый порядок идентичностей задают стабильные использования в остальных symbol records
   (сортировка по стабильному имени), затем рёбра к allocation definitions; неиспользуемые
   объекты упорядочиваются по полному содержимому их definition/type records.
   Неоднозначные неиспользуемые идентичности дают ошибку, не сливаются.
   Переименование инъективно, одной картой переписывает определения/типы/ссылки;
   сохраняет число объектов, повторные ссылки, alias-различия, byte values, offsets,
   типы, flags и locations. Литералы и комментарии не переписываются.
   Сортируются записи словаря symbol table, не инструкции функций.
2. **builtin-library Location.** Меняются только Location двух shared symbols при
   Module `<built-in-library>`: `__CPROVER_malloc_is_new_array` malloc:6/calloc:8/free:11 и
   `__VERIFIER_nondet___CPROVER_bool` malloc:4/calloc:4. Их Type/Value/Flags сохраняются.
   Это место первого подхваченного объявления общей builtin-библиотеки; в A/A есть
   обе альтернативы. Другие locations, строковые числа и имена не нормализуются.
3. **vtable comment.** Только внутри точного диагностического комментария
   `Kani-internal sanity check: Correct CBMC vtable size ... Please report failures:`
   обезличиваются debug-поля `Ty { id: N` и `DefId { id: N`. Хэшированные StructTag,
   имена типов, MIR-форма, все прочие числа и assert/assume/sizeof остаются.
   Это диагностические IDs, не замена типов/условий проверок. Удаление целого
   комментария или всех hashed tags было бы более сильным и здесь не применяется.
4. **__CPROVER_initialize.** Сортируются только максимальные соседние серии прямых
   присваиваний разным const static allocation symbols. RHS должен точно совпадать
   с Value соответствующего символа и подходить под одну из двух узких грамматик:
   агрегат номерных полей с байтовыми константами и/или наблюдаемыми pointer relocations
   с нулевыми offsets; допускается многострочная печать одного такого агрегата.
   Во втором случае `byte_extract_little_endian((signed char *)((unsigned char *)&obj + 0),
   0, signed char *)` извлекает представление **значения указателя**, не читает память
   по указателю. Storage статического объекта уже существует; присваивание его
   байтов не влияет на `&obj`. Нет dereference, вызовов с эффектами, scalar loads
   или зависимых вычислений; разные прямые targets не перекрываются.
   Другие statements/labels/guards/calls/reads — барьеры; дубликат target отвергается.
   Поэтому перестановки допущенных присваиваний коммутируют. Произвольная сортировка
   initialize или функций не применяется.
5. **Короткое/полное имя одноимённых локалов.** Имя восстанавливается в пределах
   конкретной функции по её собственным thread-local symbol identities, Base name,
   точному Type и декларациям. Должны быть явно найдены все полные имена кроме одного
   и ровно подходящая short declaration; восстанавливается полная identity оставшегося
   локала. Две identity не сливаются. Строки, комментарии, `.member`/`->member` сохраняются;
   коллизии struct/union/enum tags, labels/goto приводят к отказу нормализации блока.
   В `symtab/...i48_from_i16.symtab.out` постоянны `::1::var_10::input` типа `short int`
   и `::1::var_12::input` типа `struct _20520275679870751376562531927784834073`;
   меняется только выбор получателя короткого `input`. После binding декларации,
   назначения unwrap, построение struct и последующее `.0` совпадают по identity.
   Полный census выявил **второй** такой B-display случай: `symtab/...two_byte_sequence_test.symtab.out`,
   функция `execute_round_trip`. Там два локала `::1::var_6::residual` и
   `::1::var_13::residual` имеют один Type `struct _75879619656860051086441260289154465376`.
   A печатает коротким `residual` var_6, B — var_13. Декларации полных имён однозначно
   определяют оставшийся short local даже при одинаковом Type. Ветви bb5/bb11 и их
   from_residual-вызовы после восстановления identity совпадают; локалы не сливаются.
   До снятия остальных классов этот случай скрывался в нестабильном A/A-наборе;
   непосредственно перед local-alpha обе эти модели имеют A1=A2, A1≠B1.
   **Такой swap в фактических A/A diff не обнаружен.** Это B-only display alpha-equivalence,
   доказанная binding-ом и synthetic pair; нулевой A/A-diff после политики сам по себе
   не доказывает принадлежность этого случая к эмпирически наблюдённому A/A-классу.

Для нормализации не предполагаются equality-by-content разных объектов или
безвредность zero-width wrappers. Положительный контроль проходит весь тот же pipeline
и остаётся различным. Общий довод сохранения смысла — инъективные alpha-renamings,
неизменённый семантический текст и доказанная коммутативность только разрешённых init assignments;
A/A checks и controls являются дополнительной эмпирической проверкой, не общей теоремой.

## Матрица результатов

| Последовательность политик | A/A final /131 | linked /131 | symtab /131 |
|---|---:|---:|---:|
| legacy_first_occurrence | 80 | 92 | 92 |
| builtin_location | 92 | 92 | 92 |
| vtable_comment | 92 | 92 | 92 |
| allocations | 92 | 131 | 131 |
| initialize_order | 131 | 131 | 131 |
| local_names | 131 | 131 | 131 |

Проверены 2358 raw dumps (3324414061 байт), 2358 команд; 683 уникальных symbol dump contents.
После полного pipeline: **A1=A2 — 393/393**, включая 131/131 final.
По A1/B1 и A2/B1 в каждом виде равны 130/131; единственное различие каждого вида — control.
Вне контроля остаточных различий доступных symbol dumps **0**: все 390 perf-записей равны.
Следовательно, вспомогательный `symbol_dump_perf_status=MODELS_EQUAL`; общий статус остаётся `INCONCLUSIVE_AA`.


RESULT-OFFLINE.json хранит по каждому key/arm input/raw/stage hashes, число применений
политик, A/A/A/B результаты; residual diffs имеют короткие хэш-имена и SHA-256.
Контроль отделён от perf. Изменения отсутствующего GOTO instruction stream не классифицируются.

## Ограничение, определяющее итоговый статус

**Все 1179 goto-functions files имеют длину 0 и SHA-256 пустого файла**, хотя команды
записаны с exit 0. Например, `commands/00005.json` вызывает `--show-goto-functions ...
--verbosity 4`. Ненулевой symbol dump не заменяет body evidence: уже у final control
53 Value markers `irep("(\"compiled\")")`; у final i48_from_i16 таких 232.
Это обозначения вынесенных GOTO functions, а не их инструкции. Нет основания
отождествлять пустой вывод с отсутствием bodies, NOT_RUN или равенством моделей.

Локальный Git содержит первичный исходник **тега `cbmc-6.11.0`**,
commit `820ff0f555b43fb78e0cd9332e498461bd14244b`:

- `src/goto-programs/show_goto_functions.cpp`, line 61ff: body выводится через `msg.status()`;
  blob SHA-256 `5815194c0c55b6a7bd07b0a726f592201ecd4931cd39660f1dad680a97114727`.
- `src/util/message.h`, line 169: `M_STATUS=6`, то есть verbosity 4 подавляет этот вывод;
  blob SHA-256 `34f753f5fd16aea78ca03060fd7d83522aef2a12bc6cb70e322d4e78059bc189`.
- `src/util/byte_operators.h`, class byte_extract_exprt: binary expression над operand value
  и byte offset; blob SHA-256 `23297f5c4bc602b8542005efb1b030e16b6c77c47c4c504976fa163afe84eaca`.

Это статическая проверка source тега в `/root/cbmc-fix-zst-bits2expr`, не запуск backend
и не новое доказательство tool-binary provenance. Она объясняет потерю function output.
Существующий артефакт не содержит необходимых function bodies; Python их восстановить
из compiled markers не может. Для завершения сравнения координатору достаточно повторно
снять function dumps тех же сохранённых моделей с verbosity >=6, без пересборки моделей.
Здесь такой запуск не выполнялся.

Итоговый `INCONCLUSIVE_AA` означает, что полное A/A-равенство GOTO bodies также неизвестно,
даже если весь доступный symbol-table A/A совпал. Это не утверждение о найденном остаточном
A/A-diff и не подтверждение semantic B3 effect. MODELS_EQUAL/WRAPPER_ONLY для полных моделей
по этим данным не допускаются. SAT/B1/B2/formal proof, performance и harmlessness credit нет.

## Проверки

`validate_offline.py` независимо пересчитал AA-матрицу по сохранённым hashes,
проверил контроль A1=A2≠B1 на **каждом** шаге всех трёх видов, SHA residual diffs
и соответствие исходника normalizer его pinned SHA. В 683 уникальных raw dumps
проверено 5937 allocation-definition names: коллизий при преобразовании полного имени
в печатное C-имя **0**. Поэтому потенциальная неоднозначность этого binding в данном
корпусе исключена. `VALIDATION-OFFLINE.json` хранит checks и оба pre-local B-only keys.
Суммарно во всех плечах final содержат 196587 compiled Value markers, linked — 194364;
это дополнительно подтверждает отсутствие нужной function-части в symbol dumps.

13 synthetic tests проходят: инъективность allocation identities и сохранение bytes/alias;
сохранение AllocId-текста в литералах; допустимая перестановка records и pure init;
запрет reads/calls/dereference/дубликатов в init; точная область builtin/comment политики;
сохранение hashed type tag, type name и assertion mutations; alpha-equivalence locals
при сохранении различающих semantic mutations, members/literals и namespace collisions;
control parent edge, Unit emptiness, array length и padding; ограничение входных путей.
Два конкретных review findings (слишком широкая RHS-грамматика init и lexical namespace
коллизии locals) исправлены до итогового прохода. Дополнительное замечание о чтении памяти
byte_extract reviewer отозвал: в разрешённой форме первый operand — pointer value.
