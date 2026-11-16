# PROF-OFF-02 — acceptance v2

Одна офлайн-стадия от g0 `7a416079bbf17cdd8b64d5e01c2f10171e1baac6`.
Политика: `ACCEPTANCE-POLICY-BATCH.md`. **9 ACCEPTED / 0 PENDING / 53 UNKNOWN**:
8/53 positive relation harness и 1/9 negative control приняты по политике.
Это admission source-reported bounded observations, **proof credit NONE**;
не независимое исполнение компилятора, не B2 и не общий theorem.

Run `43784551069`, artifact `14190662926`, ZIP SHA256
`6b1f8ed210d93aae32b3e512565df7d6726d43660c19cb3c614f612f6b1a15e9`.
Source `9fa2f7f97760584f38738909625c064006d8a936`, stock tool
`0aac16ef62da9e9d5645782d458593e5d78143ba`, unchanged control
`112fcc9ada67ee2bb8e1712d47983d6717487b78`.
Проверены ZIP digest, source/tool/config/selection/unwind guards, source/binary
snapshots before/after; 62 исторических receipt snapshots воспроизведены точно.
Group exit не использован как verdict отдельной строки. Старые файлы не изменены.

## Применение политики

`classifier_v2.py` — отдельный офлайн-классификатор; runner не менялся.
Полный count/partition согласуется; неизвестный статус, missing/null/wrong-type
и потерянные свойства дают UNKNOWN. Positive требует exact-row SUCCESS.
Negative сохраняет заранее заданные named oracles; generated frame placeholder
не заменяется наблюдаемым ID и остаётся PENDING. UNKNOWN имеет приоритет над
PENDING, но все вторичные причины сохранены в JSON.

205 unsupported occurrences (180 positive + 25 negative) допущены отдельно по
15 exact property IDs, а не по непустому списку или одному status. Каждая запись
связана с `assert(false); assume(false)` через frozen source chain в
`UNSUPPORTED-LINKS.json`: stock `codegen_unimplemented_stmt`,
`kani-compiler/src/codegen_cprover_gotoc/codegen/assert.rs:278-296`, вызывает
`codegen_assert_assume` (`:129-143`), который сначала assert, затем assume.
Memory-predicate hooks используют эквивалентный `codegen_assert_assume_false`
(`:214-220`, `overrides/hooks.rs:223-240`), foreign-function path —
`codegen/foreign_function.rs:255-261`; caller_location идёт через unimplemented.
Exporter сохраняет exact ID/class/status той же property
(`kani-driver/src/frontend/schema_utils.rs:495-504`, `:768-772`).
Все 205 имеют SUCCESS и не конфликтуют с другими status buckets того же harness.
Список success IDs в схеме отсутствует: связь опирается на exact PropertyExport
и статический exporter/source chain, не на выдуманный отдельный success inventory.
Новый/неподтверждённый ID либо location/class mismatch даёт UNKNOWN; reachable
unsupported блокирует acceptance.

Все 1710 unreachable occurrences (1505 positive + 205 negative) перечислены
в ACCEPT.json с exact ID, function, location=null, ролью UNKNOWN и причиной.
Экспорт не содержит их descriptions/locations; `.assertion.N` не устанавливает
соответствие исходному assertion. Разбор семейств — `UNREACHABLE-ANALYSIS.md`.
Защитных exemptions в этом batch нет. Классификатор умеет допускать только явно
разобранную defensive branch с ID/location/target relation/reason; обязательные
postcondition/frame/relation/section блокируются. Оба пути покрыты synthetic tests.

`SOURCE-MAP.json` задаёт source-file hashes и covers→obligations для всех 53
positive строк, включая macro parameters; дополнительно перечислены negative
covers. Проверены все 189 source windows, из них 179 positive; все экспортированные
covers SAT. Required IDs взяты из разбора source calls до admission, сохраняются
и при удалении cover из export: отсутствие блокирует строку. Шесть covers в трёх
four-position swap строках стоят до target call; два comparator callback covers
свидетельствуют вызов сравнения, но не target return. Эти восемь не используются
как post-target-return witnesses. У всех positive есть отдельные covers после
actual target/verified-stub call либо relation/frame/post checks. SAT — только
существование исполнения; полнота domain/ветвей/независимость assumptions не заявлена.
Статическое сопоставление source function/ordinal не является независимым
AST/MIR/codegen binding; эта граница явно отмечена в mapping.

Для PFC сравниваются полные source/export token paths, с разрешением source
module/import до fully qualified target; terminal identifier не используется
в качестве полного binding. Exact mangled contract-wrapper specialization не
установлена и явно PENDING во всех 38 PFC строках; также сохраняется граница
wrapper binding для пяти stub consumers. Original relation harness не имеют
contract wrapper: их source helper/type/call binding разобран отдельно.
Consumers оцениваются после leaf; все пять остаются заблокированы.

## Все строки

`U(n)` — n exact unreachable IDs с неустановленной ролью; каждый перечислен в JSON.
`W` — exact generated wrapper PENDING; `F` — predeclared frame oracle PENDING;
`L` — matching leaf не ACCEPTED. Другие причины указаны полностью.

| Строка | Verdict | Policy | Причины |
|---|---|---|---|
| `swap_contract_four_positions_u8` | SUCCESS | UNKNOWN | U(4), W |
| `swap_contract_four_positions_i32` | SUCCESS | UNKNOWN | U(4), W |
| `swap_contract_four_positions_u64` | SUCCESS | UNKNOWN | U(4), W |
| `swap_contract_u8_n2` | SUCCESS | UNKNOWN | U(4), W |
| `swap_contract_u64_n2` | SUCCESS | UNKNOWN | U(4), W |
| `swap_contract_drop_u8_n2` | SUCCESS | UNKNOWN | U(4), W |
| `swap_contract_cell_i32_n2` | SUCCESS | UNKNOWN | U(4), W |
| `swap_contract_bytes16_n2` | SUCCESS | UNKNOWN | U(4), W |
| `swap_contract_bytes17_n2` | SUCCESS | UNKNOWN | U(4), W |
| `swap_contract_u8_indices_n17` | SUCCESS | UNKNOWN | U(4), W |
| `swap_contract_u64_indices_n17` | SUCCESS | UNKNOWN | U(4), W |
| `swap_contract_u8_n9` | SUCCESS | UNKNOWN | U(4), W |
| `swap_contract_u8_n13` | SUCCESS | UNKNOWN | U(4), W |
| `swap_contract_u64_n9` | SUCCESS | UNKNOWN | U(4), W |
| `insert_tail_contract_u64_start1_tail2_to8` | SUCCESS | UNKNOWN | U(52), W |
| `insert_tail_contract_u64_start1_tail9_to12` | SUCCESS | UNKNOWN | U(44), W |
| `insert_tail_contract_u64_start1_tail13_to14` | SUCCESS | UNKNOWN | U(40), W |
| `insert_tail_contract_u64_start1_tail15_to16` | SUCCESS | UNKNOWN | U(36), W |
| `contract_insert_tail_u8_prefix` | SUCCESS | UNKNOWN | U(34), W |
| `sort4_contract_u64_n4` | SUCCESS | UNKNOWN | U(68), W |
| `sort4_contract_bytes16_n4` | SUCCESS | UNKNOWN | U(73), W |
| `merge_contract_u64_n2_to4` | SUCCESS | UNKNOWN | U(70), W |
| `merge_contract_u8_n2_to4` | SUCCESS | UNKNOWN | U(70), W |
| `merge_contract_u64_n5` | SUCCESS | UNKNOWN | U(68), W |
| `merge_contract_u8_n5` | SUCCESS | UNKNOWN | U(68), W |
| `merge_contract_u64_n6` | SUCCESS | UNKNOWN | U(66), W |
| `merge_contract_u8_n6` | SUCCESS | UNKNOWN | U(66), W |
| `merge_contract_u64_n7` | SUCCESS | UNKNOWN | U(64), W |
| `merge_contract_u8_n7` | SUCCESS | UNKNOWN | U(64), W |
| `merge_contract_u64_n8` | SUCCESS | UNKNOWN | U(62), W |
| `merge_contract_u8_n8` | SUCCESS | UNKNOWN | U(62), W |
| `merge_contract_u8_n9` | SUCCESS | UNKNOWN | U(60), W |
| `merge_scratch48_contract_u8_n9` | SUCCESS | UNKNOWN | U(61), W |
| `profile_relation_lt_u8` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `profile_relation_lt_i32` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `profile_relation_lt_u64` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `profile_relation_read_u64` | SUCCESS | UNKNOWN | U(2) |
| `profile_relation_read_b16` | SUCCESS | UNKNOWN | U(2) |
| `profile_relation_strict_u8` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `profile_relation_strict_u64` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `profile_relation_cell_i32` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `profile_relation_drop_u8` | SUCCESS | UNKNOWN | U(2) |
| `profile_relation_key_b16` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `profile_relation_key_b17` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `stable_cell_n2` | SUCCESS | UNKNOWN | U(10), W |
| `unstable_byte_n2` | SUCCESS | UNKNOWN | U(32), W |
| `freeze_noncopy_n2` | SUCCESS | UNKNOWN | U(19), W |
| `profile_swap_consumer_u8_backing4` | SUCCESS | UNKNOWN | U(4), W, L |
| `profile_sort4_consumer_u64` | SUCCESS | UNKNOWN | U(68), W, L |
| `profile_sort4_consumer_b16` | SUCCESS | UNKNOWN | U(73), W, L |
| `profile_insert_consumer_u8_backing17` | SUCCESS | UNKNOWN | U(34), W, L |
| `profile_merge_consumer_u8_len4` | SUCCESS | UNKNOWN | U(71), W, L |
| `profile_wrong_f_swap_rejected_u8` | FAILURE | UNKNOWN | U(4) |
| `profile_wrong_f_sort4_rejected_u64` | FAILURE | UNKNOWN | U(32) |
| `profile_wrong_f_insert_rejected_u8` | FAILURE | UNKNOWN | U(33) |
| `profile_wrong_f_merge_rejected_u8` | FAILURE | UNKNOWN | U(34) |
| `profile_bad_relation_rejected_u8` | FAILURE | ACCEPTED | Все применимые gates пройдены |
| `profile_full_value_checker_rejects_payload_change_u8` | FAILURE | UNKNOWN | U(60) |
| `rejects_always_true` | FAILURE | UNKNOWN | U(20) |
| `rejects_payload_corruption` | FAILURE | UNKNOWN | U(18) |
| `swap_safety_u8_backing4` | SUCCESS | UNKNOWN | U(4), W |
| `rejects_swap_comparator_writing_outside_frame_u8` | FAILURE | UNKNOWN | U(4), F, W |

## Валидация и оставшаяся граница

31 новый synthetic test PASS; 42 прежних runner/service tests PASS. Проверены
unsupported exact-ID/status/source mismatch, required/defensive/unknown unreachable,
missing/unsatisfied/pre-call/unmapped cover, full target/stub mismatch, wrapper
PENDING, сохранение negative oracle, ошибки inventory и consumer leaf gates.
Offline replay читает только JSON из того же ZIP; evidence argv не исполняются.

Для продвижения 53 UNKNOWN нужны точные source-condition/location bindings
unreachable properties; для PFC — независимый exact generated-wrapper binding;
для frame negative — независимый заранее заданный oracle binding. Эти пробелы
не заполнялись предположениями, изменением stock tool или новым запуском.
Independent Luna HIGH review: GO, без замечаний (REVIEW.json). READY относится к завершению этой стадии,
а не к принятию всего batch.

Push / CI / публикаций / ledger writes / local cargo-rustc-Kani-CBMC: 0.
