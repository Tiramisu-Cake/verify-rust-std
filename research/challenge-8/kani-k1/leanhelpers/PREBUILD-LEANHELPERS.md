# LEANHELPERS — пакет PRE-BUILD review

Ветка `experiment/kani-k1-leanhelpers-20261106`, owner `k1-merge`.
Задание `d3ea81c32f`; база library `461dac0c43902c7a929e7164492ad4a5f84a4a3b`.
Library `5c929ba094cef478efc350b3cd9d7b8fc73fe203`, tree
`ed9d8de3a0a6ad930e69646ab6001a607971ae7b`.
Dispatch не выполнен. Нужен GO координатора на exact опубликованный пакет.
Окно после GO: main 240 + closeout 30 минут; timestamps до dispatch записать в ledger.

Правки library ограничены четырьмя файлами verify и тремя пунктами задания:

- Удалены MUTANT, его const assert и две мёртвые ветки; вызов и комментарий обновлены.
- Удалён START из двух helpers; begin=1, prefix проверяется непосредственно по индексу 0.
  Сообщение assert сохранено; остальные проверки и unwind прежние.
- Три метода CopyOnDrop стали свободными generic-функциями в merge, с прежними телами.
  Вызовы и импорты обновлены в merge, scratchgeom и merge/specfix.

`smallsort.rs` побайтно неизменён. Library diff: +65/-82 строк, net -17.
Tooling/workflows/scripts не изменены относительно `59893bff1f`.

## Статическая проверка

`python3 -B research/challenge-8/kani-k1/leanhelpers/check_leanhelpers.py`
импортирует лексер/expander OPTINMOVE без изменения исходного tooling.
Целые исходные файлы сверяются с точным allowlist преобразований базы, включая комментарии.
В allowlist добавлены точные whitespace-правки rustfmt по решению координатора.
Число и набор имён: cfg-off 233; cfg-on 246 = 233 ordinary + 13 controls.
[affected-roots.json](affected-roots.json) перечисляет 13 MUTANT, 4 START и 51 helper-root:
всего 68 (66 ordinary + 2 controls); группы не пересекаются.
Для 178 остальных раскрытые roots и closures токен-идентичны базе.
Тела трёх методов token-exact после добавления generic T в сигнатуру свободной функции.
Covers сохраняют item, порядковый номер вызова и полные аргументы; сообщения assert точные.
Проверяются отсутствие строк >100/запрещённой лексики в verify, неизменность tooling и diff-check.

Resolver консервативен по идентификаторам и не является rustc name resolution.
Для графа старый impl разделяется на три метода, без изменения их тел; иначе имя generic T
создавало бы ложное глобальное ребро ко всему impl. Остальные правила inherited resolver прежние.
[cover-sites.json](cover-sites.json) содержит проверенные координаты item/call ordinal для всех roots;
строчные и абсолютные token offsets могут сдвигаться из-за разрешённых удалений.
Checker также запускает разрешённый rustfmt wrapper с `--check --edition 2024`,
конфигом `research/challenge-8/kani-k1/codefix/rustfmt.toml` от `smallsort.rs`
(с обходом всех verify-подмодулей). Exit0, stdout пуст, исходные байты не меняются.
Команда и результат: [rustfmt-check.txt](rustfmt-check.txt).
Это проверка исходников и форматирования, не compiler inventory и не новый proof credit.

## G1 и сравнение

[RUN-REQUEST.json](RUN-REQUEST.json) byte-identical верхнему RUN-REQUEST.json;
существующий validator принят. Diagnostic, controls=true, inventory=false, jobs1, standard4.
Controls включаются для компиляции cfg-on дерева; их выполнение не включено в выборку.
Семь строк, все expect SUCCESS. Выбраны быстрые представители по v8c Ubuntu:
два минимальных drop/fallback N2, general/stable u8 N2, самый быстрый PFC merge u8 N5.
probe_count — sort4 u64 N4; scratchgeom — единственный оставшийся ordinary N2;
START — предписанный самый короткий tail15_to16.

| Корень относительно verify:: | Прежнее время, с | Covers | Источник |
| --- | ---: | ---: | --- |
| merge::drop_fallback_drop_count_n2 | 0.6422159 | 2/2 | v8c Ubuntu |
| merge::drop_fallback_tag_permutation_n2 | 0.6744263 | 2/2 | v8c Ubuntu |
| merge::sort4_arbitrary_comparator_u64_n4 | 3.2531826 | 1/1 | v8c Ubuntu |
| merge::general_stable_direct_u8_n2 | 2.8596132 | 2/2 | v8c Ubuntu |
| scratchgeom::stable_u64_min_scratch_n2 | 5.838726 | 2/2 | наш VEIGHTINTEG GCB |
| merge::merge_contract_u8_n5 | 47.514442 | 1/1 | v8c Ubuntu |
| network::insert_tail_contract_u64_start1_tail15_to16 | 156.41757 | 4/4 | v8c Ubuntu |

[baseline-rows.json](baseline-rows.json) фиксирует SHA/TSV строки и excerpt нашего RESULT;
checker сверяет каждую строку с её источником. Прежние covers всего 14/14.
Сравнение source-reported; отличия runner/компилятора учитывать при разборе времени.
Рост >~25% разобрать в RESULT; новые TIMEOUT/OOM означают непринятую стадию и вопрос координатору.

8 мин/корень оставляет tail15_to16 примерно тройной запас к прежним 156–164 с.
7×8=56 мин; verify cutoff 56+24=80 мин от validate; paid timeout 56+30=86 мин.
Setup/Kani build ранее ~6–8 мин; остаток slack ~16–18 мин для cfg-on compile/instrumentation.
Фактическая сумма прежних verification times ~217.20 с; inventory отключён.
Резерв 86×$0.0135=$1.161≤$1.50, project used+reserve+G1=$108.024≤$118.96.
[prebuild-budget.txt](prebuild-budget.txt) — bounded наблюдение; обновить перед dispatch.
Одна сборка, retry0; один compile-error repair только нашей ошибки после GO и в своём cap.
Подготовленного или разрешённого G2 нет.

## После exact-packet GO

Сверить точный source SHA с GO; записать T0/deadlines и обновить budget.
Dispatch опубликованной ветки только через k1g.sh, записать UUID, затем
`research/challenge-8/kani-k1/tools/k1g.sh watch BUILD` и завершить ход.
Status в цикле не опрашивать. После уведомления читать только bounded summary/rows/peaks/log-grep.
Сверить source/request/Kani/pool identities, COMPLETE, gate, все семь SUCCESS и 14/14 covers.
check-tooling — база `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; scan verify/unused warnings.
Budget своего UUID, runtime/timing comparison и line counts внести в RESULT≤35 строк.
Завершить REVIEW REQUEST <sha> / LEANHELPERS ЗАВЕРШЁН и стоп.

## Исправление по pre-build review 4a48066ee0

Содержание принято координатором; GO до форматирования не выдан.
Library-коммит выше содержит форматирование двух assert и четырёх вызовов
`general_stable_direct_u64_n2..n5`, оставшихся после OPTINMOVE.
Токены всех verify-файлов совпадают с library `955d3384298e`; affected68/unchanged178 прежние.
Порядок ключей generated cover-sites.json стабилизирован; содержимое site mappings прежнее.
G1 request, семь строк, лимиты и бюджетные расчёты не изменены.
Новый опубликованный пакет снова ожидает exact-packet GO. Сборок не было.
