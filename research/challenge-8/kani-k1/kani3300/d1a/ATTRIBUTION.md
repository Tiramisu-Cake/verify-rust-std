# KANI3300 D1-A — A + B-lite attribution

**Offender не найден.** Есть конкретные retained diagnostic цепочки, но нет измерения Boolean converter, cache misses, allocations или стоимости отдельного term. Это не ресурсный фикс и не semantic verdict. R1+skip и R6-02b остаются NON_COMPARABLE как корректные performance baselines; локальное сопоставление их diagnostic expressions допустимо.

## Независимый пересчёт сохранённого текста

`analyze_offline.py` читает только переданные bounded projections (<8 MiB), без Kani/CBMC/компилятора. Координаты — physical line с 1, byte offset с 0; SSA suffixes/constants сохранены, fingerprint нормализует только whitespace. Многострочные aggregate renderings склеены до fingerprint. Полный текст не включён в отчёт.

| Печатные expression records после slicing | R1+skip | R6-02b |
|---|---:|---:|
| all / ignored / retained | 5280 / 4213 / 1067 | 5865 / 4588 / 1277 |
| retained assignment-or-UNKNOWN | 496 | 643 |
| retained SHARED_WRITE | 442 | 478 |
| ASSERT / ASSUME | 96 / 33 | 115 / 41 |
| отдельно напечатанные guards | 2039 | 1961 |
| byte-extract / byte-update, all | 4 / 1 | 9 / 1 |
| byte-extract / byte-update, retained | 0 / 0 | 0 / 0 |
| WITH updates, all / retained | 85 / 0 | 90 / 13 |
| POINTER_OBJECT occurrences, all / retained | 292 / 35 | 252 / 58 |
| index text, constant / symbolic-or-UNKNOWN, all | 70 / 271 | 70 / 252 |

Все ASSERT/ASSUME в этом выводе имеют numeric marker. Это census печатного представления; SHARED_WRITE — события, не число новых converter terms. Guards не прибавлены к expression denominator; их operator occurrences сохранены отдельно. Не печатаемые categories/auxiliary expressions и actual conversion coverage остаются UNKNOWN. Никаких VCC prefix dumps здесь нет; повторные текстовые ASSERT не считаются уникальными property или DAG nodes.

Исходный D1-P parser остановился на character-work budget 200000. Его all 3191/2740 и retained 698/710 описывают префикс и сохранены отдельно в JSON; они не противоречат новому census. `textual_census_complete=true` означает классифицированный весь сохранённый printed stream, а не complete typed SSA или proof parser.

`SSA-SUMMARY.json` содержит top-30 all и retained roots по occurrence; отдельно top-30 с известной logical root width и UNKNOWN. Для равенства/ASSERT/ASSUME logical root = Boolean (1 бит), что ничего не говорит о ширине operands. Полное ранжирование **operand widths** остаётся UNKNOWN: нет typed IREP tree для всех roots. Storage layout/source-derived widths из MODEL-MAP не подменяют измерение converter bitvectors. Fingerprint occurrence ≠ unique DAG node; общих expression/cache identities нет.

## Локализованные цепочки и границы

Actual model hashes: R1 `e8d4d3e82326663aa34f912b36535cd29088adaa4fc7d3c8afe403534adc28a2`; R6 `47eaccef418b63d26413c3a310804482ba00ecdacb6ec684abf1d392dff65e55`. Все пути ниже относительно P1 root соответствующего bundle из INPUTS.json; hashes файлов и snapshots находятся там же.

1. **R1 numeric saved-object carrier.** `store_argument::<1, MaybeUninit<u8>>` сохраняет object identity в поле marked `MEM_INIT_STATE`. Retained merge equality: `invocations/cbmc-001/process/stdout.bin` line 5938, byte 634113, length 186, printed id 2016, PC 664, source `mem_init.rs:418:10`: `MEM_INIT_STATE#5..argument_buffer_saved_object_id == (guard37 ? POINTER_OBJECT(&var_3!0@1) : POINTER_OBJECT(&var_0!0@1))`. Это phi на merge/dead boundary; GOTO PC 664 — DEAD var_11, **не** исходная запись. Actual GOTO write: `actual-cbmc-show-goto-functions/stdout.bin` line1451, PC639, source `mem_init.rs:412:21`; lhs `*var_10.argument_buffer_saved_object_id`, rhs `saved_object_id`. Pointer derivation и write→merge mapping — MODEL-MAP. Поле — unsigned long int/usize, type/source-derived 64 бита на данном target; equation root — Boolean. Всего matching saved_object equality 12, retained 2; конкретный whitespace fingerprint первой retained строки встречается один раз. 56-байтовый state не означает 448-битный operand каждого field read. Цена POINTER_OBJECT, operand conversion и phi неизвестна.

2. **R6 private buffer frame check.** `store_argument` source `mem_init.rs:405` пишет 32-байтовую cell `ARGUMENT_BUFFER` через derived `var_9`, а не по pointer value, хранимому в buffer. DFCC check по адресу lhs и extent32 даёт retained chain: PC 628 `__check_lhs_assignment!0@3#2 == __CPROVER_contracts_write_set_check_assignment!0#49` (line 5818), затем PC 629 `ASSERT(guard29 ==> __check_lhs_assignment!0@3#2)` (line 5821), guard29; actual writes PC631, lines5824+. Встроенный check-result phi line5815, PC1991 — отдельный узел, не user write. Boolean check/guard имеют logical width1, extent32 = 256 storage bits — type/GOTO-derived, не measured conversion width. Каждый указанный fingerprint встречается один раз; все retained ASSERT с именем check_lhs_assignment перечислены в JSON. Это локализованный frame obligation, не установленный новый frameFAIL: normal solver NOT_RUN.

3. **R6 DFCC allocated set.** `__CPROVER_contracts_write_set_add_decl`, builtin source line664, SSA PC1947, stream line1837: retained `dynamic_object$12#2 == ARRAY_OF(NULL) WITH [(signed long int)POINTER_OBJECT(&var_0!0@1):=(const void *)&var_0!0@1]`. Вся цепочка содержит 13 retained WITH updates; R1 соответствующие printed updates sliced. Creation metadata: object_bits16, nof_objects65536 (line1628), `__contract_write_set.allocated.max_elems=65536` (line1639), elems points to dynamic_object$12. При pointer size8 logical backing estimate = 524288 bytes / 4194304 bits; это **source/type-derived capacity estimate**, не exact IREP/flattened root width, число clauses или выделенная память конвертера. Actual type/array classification/cache conversion для dynamic object не восстановлены. Само наличие большого backing на более дешёвом историческом контрасте не объясняет OOM R1.

## Проверенные гипотезы

- **Symbolic byte-extract/update:** все 5/10 видимых occurrences sliced, offsets в этих renderings — константные 0/0l/8l/16l. В retained printed terms hotspot не найден. Hidden operand rewrites/непечатные roots и converter internals не покрыты: это не глобальное исключение byte-op причины.
- **Finite-array index/update:** retained WITH есть только у R6 в этом сравнении; owner — DFCC allocated set. Symbolic-or-UNKNOWN index text — эвристика (включает casts/type brackets), не число symbolic array operations и не доказательство дорогого flattening.
- **DFCC write-set/snapshot/backing:** mapped private cell extent и retained frame check дают конкретную область для дальнейшего анализа; arbitrary havoc/private assigns и encoding не измерены. Marker→cell не разрешает pointee/user writes.
- **Повторная работа/helper instrumentation:** есть повторные bless/copy и alignment obligations, несмотря на initializer skip. Top retained repeated alignment ASSERT/ASSUME имеет по 11 occurrences на каждом pin. Это не 11 cache misses и не доминирующая цена. Общий признак usize, RSS, VCC count и длина текста не выбирают гипотезу.

## Решение и минимальные недостающие данные

Приёмочная ветвь задания — явное «offender не найден» с gaps: exact operand/root type widths и owner для всех terms; unique DAG/cache hits; allocation и inclusive/exclusive converter deltas; postponed array/pointer work; полная semantic feasibility/faithfulness. R6 содержит assume(false) abort paths в load_argument; оба symex streams предупреждают о nondeterministic arguments saturating_add/sub. Printed presence не устанавливает исполнение lawful path. Нового failure verdict и proof credit нет.

Следующий **выбор, не запуск и не задание**: отдельно одобряемый C, узкий converter profile точных сохранённых моделей с SSA/PC/model IDs, operand/result widths, origin и pre-allocation enter/exit deltas (time/RSS/vars/clauses), cache misses и postponed phases. Минимальный запрос к **уже сохранённым** данным: typed post-slicing operands для R1 SSA2016/PC664 и R6 SSA722/PC1947 (root/result width, dynamic_object$12 element type/extent), плюс имеющиеся converter/cache enter/exit records с теми же model IDs. В переданном catalogue этих полей нет; отсутствие такого сохранённого профиля означает необходимость отдельного решения о C, не разрешение на новый run/экспортёр здесь. Без них локальная оптимизация на4f64 не обоснована. Если C не принимается — отдельный proposal fail-closed scope с replay реального SmallSort graph; здесь graph/scope не менялись. M3, полный gate, PFC claim и resource fix — HELD/NOT_ESTABLISHED. STOP D1-A.
