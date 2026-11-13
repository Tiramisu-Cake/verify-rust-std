# R3 / Г1 — критическая оценка и черновой порядок

2026-11-13. Отчёт прочитан целиком: `AUDIT-REPORT-KANI3300-PART1-R3-RU.md` @88ca9d0294f5e6f631117aa68f56ee1e3464398d.
Это верификация корректности, не security-работа. **Только анализ и TASK drafts; шаги 0/1 не выданы, D1 census и CI не выполнялись.**

## С чем согласен

Г1 — сильная и дешёво проверяемая гипотеза. CBMC6.11 finite-array flattening, DFCC object tables2^b и пропуск GOTO
в dependency slicer при последующей conversion GOTO conditions подтверждаются source. Печатный program-only census
не покрывает весь converter workload. Мой прежний вывод «большой backing есть у дешёвого контраста, поэтому не объясняет OOM»
следует снять: удержанность определения способна принципиально изменить стоимость чтения того же backing.
Carrier-серия не была чистой изоляцией представления; G-SC и новые carrier rewrites сейчас не обоснованы.
Проверка штатных object-bits/slicing flags до patched converter C — правильный следующий выбор, если владелец разрешит CI.

## §2.2 — числа верны, атрибуция сильнее данных

Для qC=4259841 и qV=65600 повторный арифметический расчёт даёт:

| Run | floor(C/qC) | независимо floor(V/qV) | Остаток V | Остаток C | Остаток V,% | Остаток C,% |
|---|---:|---:|---:|---:|---:|---:|
| upstream /43253856019 |4|4|22483|33050|7.892|0.194|
| V02 /43258921276 |12|12|56829|104684|6.733|0.204|
| R5-01 /43268005490 |12|12|59280|100743|7.003|0.197|
| R6b /43276309576 |12|12|42758|55693|5.152|0.109|

Совпадение значимое, однако «точность0.2% размеров формулы» относится только к клаузам; по переменным остаток5–8%.
`k=floor(C/qC)` и отрицательный остаток приk+1 — свойства выбора k, не независимое доказательство числа чтений.
Независимый variable-based k действительно совпадает; это усиливает гипотезу, но не устанавливает owner/table/read count.
Время SSA/k — нормировка всей фазы, не измеренное время одного lookup.

Оценки стоимости условны: 64-bit words, constant-converted index, SAT has_set_to path, тип битов таблицы и cache reuse.
По source cnf::land убирает false/all-true/duplicates; нельзя применять одну цену к произвольному expression без условий.
Retained definition может оставаться guarded/symbolic; retained не означает автоматически «все биты константны».
Для новой свободной версии таблицы плата за storage64N variables возникает один раз. Если D различных free-table lookups
используют S разных свободных версий, а C читает retained/constant versions, упрощённые slopes:
**clauses ≈ (321D+65C)N; variables ≈ (64S+65D+C)N**, плюс per-read64 и прочие terms в residual.
Формула129D+C предполагает S=D. При D=S=1,C=10 отношение slopes971/139≈6.986; поэтому диапазон2.5–5 и порог<10
из §2.6 не обязательны для смеси. Их можно применять только после оценки retained share/cache sharing.

Прочитан [kani#3611](https://github.com/model-checking/kani/issues/3611): там действительно небольшой PFC при16 bits,
16918466 variables/42087481 clauses и >9GB. Два расчётных free-table пакета оставляют10050 variables/13367 clauses.
Это ещё один согласующийся численный след **без uninit**, но не доказательство идентичной причинной цепочки или необходимости закрыть вопрос issue-решением.

## §2.3 — полезное разбиение с ограниченной причинностью

Source/patches согласуются с14 KILL/in-frame против4 completed/out-of-frame; R6-02 исключён по early Enum Unsupported.
Но source marker/assigns construction ≠ полный emitted-target/reached-write inventory всех18 runs.
R4-A строит два whole-static targets, R7/R8 —12/13 member targets; extent/число targets тоже меняется.
У V02/R5-01 failure tails потеряны: source предсказывает out-of-frame, actual frame failure там не установлен.
Следует принять «серия не изолирует carrier cost», а не «представление/протокол не влияют» или «frame membership доказанно причина».
Сравнение interrupted RSS/time с completed peak также не измеряет slope роста памяти; режимы кодирования пока гипотеза.

## §2.6 — сделать правило решения трёхзначным

Шаг0 полезен как независимый census видимых table reads/definitions. Но guard assignments — **proxy**, не автоматически
полный список nonprinted GOTO conditions. D_proxy=0 опровергает лишь такой proxy; Г1 опровергается нулём только при доказанной coverage.
Nonsliced не означает «вообще без slicing»: simple_slice оставляет удалённый tail после последнего ASSERT.
Read counts шага0 относятся кR1/R6, а не4f64 с более богатым A3 protocol; перенос D≈12 в прогноз нового source не установлен.
Две конечные точки всегда определяют прямую; нужна хотя бы третья completed точка/независимый read census и явный residual.
KILL на12/10 не опровергает механизм, лишь прогноз завершения. Снижение числа variables при no-slice — сильный discriminator,
но не уникальная причина. Результаты: SUPPORTED / COUNTEREVIDENCE / INCONCLUSIVE, не автоматические CONFIRMED/REFUTED.
Фиксировать semantic oracle отдельно. Ранний frameFAIL/Unsupported/object exhaustion не resource relief.

Полный набор B–H для P1/P2 =14 новых normal invocations, а не≈10; с новым16-bit A —16.
В draft предлагаются **не более10**: P1/P2 при12/10/14, P1@16, P1@12 no-slice, P1@16 UF-always, optional P1@8.
Historical16 reuse допустим только при exact4f64/fixture/flags binding; R7 B0 с bootstrap-skip не такой baseline.
Если matched16 уже найден, освобождённый slot можно заранее назначить P1@16 no-slice. Никаких автоматических дополнительных плеч.

## Ответы9–12: сейчас и после Г1

**Сейчас, без source changes:** явно записать unqualified Replace/Recursive; read-only inventory и дизайны controls;
на4f64 проверить marker/assigns binding и зафиксировать условие для будущей ошибки вместо unwrap_or_default;
вести отдельные semantic gates P1/P2/lawful-frame, projected store, constant union, DST, immutable offsets/Move/M3/full export.
Не требовать статик, когда uninit выключен или relevant state действительно отсутствует; будущая диагностика должна быть conditional.

**После ресурсного эксперимента:** отдельный маленький marker diagnostic patch; tests Replace/Recursive и semantic edges;
M3, exact negative inventories, полный regression/platform gate и real SmallSort replay. Ресурсная гипотеза не закрывает ни один из них.
`*var_7 is assignable` — старый label, не переносимый oracle: нужны source/class/target binding, а не только generated number.
Property SUCCESS/presence не доказывает достижимость useful read; сохранить matched negatives/coverage и отсутствие раннего guard.

**Не принимать сейчас:** общий перевод clause asserts в assumes для Replace, blanket runtime DFCC exemption,
новый протокол или CBMC optimizer patch. Это trusted semantic changes, которым нужны отдельные repro/design/review.
Source-прогноз ложного Replace FAIL и «безвредности» saturating warnings не равен execution evidence; по сохранённым данным
нужно сверить actual extra parameter/use и callsites, а не только имена source locations.

Уменьшение b меняет object capacity, offset bits и derived max-allocation bound. Для admitted executions это может быть
корректным профилем кодирования, но вместимость/diagnostics надо подтвердить; не переносить12-bit proof на16-bit result.
Не выбирать автоматически минимальное b вместо целевого профиля12 и не объявлять весь Part1 готовым после успешного P1.
По cache report в основном прав: разные contract-usage groups имеют разные transformers; same-unit shared-body gate остаётся.

Черновики: `TASK-KANI3300-H1-STEP0-draft.md`, `TASK-KANI3300-H1-STEP1-draft.md`. Все дальнейшие выдачи/CI — отдельное решение координатора/владельца.
