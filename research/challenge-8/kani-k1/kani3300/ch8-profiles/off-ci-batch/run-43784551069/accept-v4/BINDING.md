# Exact contract-wrapper binding — v4

Все references к Kani ниже относятся к stock `0aac16ef62da9e9d5645782d458593e5d78143ba`.
Replay проверяет byte equality этих source files на control `112fcc9ada`;
source algorithm/harness files читаются через Git на `9fa2f7f977`, их hashes
совпадают с принятым SOURCE-MAP.json. Никакие compiler/verifier commands не запускались.
Декодирование имён — GNU `c++filt -i -s rust` 2.42, executable SHA256 и полный
словарь raw→decoded сохранены в ACCEPT.json. Это demangler, не Rust compiler.

## Механизм

1. `library/kani_macros/src/sysroot/contracts/mod.rs:572-587`: PFC сохраняет
   target expression в harness attr. `kani-compiler/src/kani_middle/attributes.rs:253-257,767-787`
   и `resolve.rs:58-119` разрешают полный target path в родительском модуле harness;
   `codegen_units.rs:282-288` создаёт `ContractUsage::Check(target DefId)`.
2. `initialize.rs:72-90` создаёт локальные имена `__kani_check_<fn>`,
   `__kani_replace_<fn>`, `__kani_modifies_<fn>`; `bootstrap.rs:36-49,85-103`
   прикрепляет `kanitool::checked_with`, `replaced_with`, `modifies_wrapper` и
   выбирает closure по mode. Локальное имя переменной не является символом функции.
3. `check.rs:23-80,84-120,135-153`: check assumes requires, вызывает modifies
   closure с original body, затем asserts ensures с `stringify!(source clause)`.
   `replace.rs:102-159`: Replace asserts requires, havocs modifies, assumes ensures.
   В этом pin нет literal атрибута `inner_check`; соответствующая роль называется
   `modifies_wrapper` (`attributes.rs:163`), а generated closure помечена
   `is_contract_generated(wrapper)`. Нельзя искать выдуманный символ inner_check.
4. `codegen/contract.rs:19-53,98-125`: compiler берёт target instance и по
   `var_debug_info` ищет named checked_with, затем named modifies_wrapper;
   `AssignsContract.contracted_function_name = modify.mangled_name()`.
   `kani_metadata/src/harness.rs:10-19` явно документирует эту роль.
   `kani-driver/src/call_goto_instrument.rs:180-210` передаёт ровно один
   `--enforce-contract <metadata symbol>` для exact harness, без loop contracts
   в этом batch. Поэтому assigns properties в callees относятся к write set
   этого enforced contract; их ID указывает на место записи, а не на владельца.
5. `cbmc_output_parser.rs:132-139,149-227,282-305`: ID имеет fn.class.counter;
   function в ID и Location декодируется. Обычные Rust pretty names опускают local
   `core::`; DFCC properties оставляют crate prefix. Нормализуется только `core::`,
   полный module path и generic arguments сравниваются без suffix matching.
   При сравнении clause удаляется только whitespace, не токены/условия.

Данные stdout анализируются как bounded property projection существующего exact
artifact; downloads, full compilation logs, Cloud/GCS/Logging не использовались.
Сохраняются v3 marker/receipt/hash/completeness checks на каждую затронутую строку.
Для каждой PFC два DFCC properties содержат raw metadata symbol дважды и имеют
Location/ID stem равный decoded modifies-wrapper. Родительская closure содержит
exact source ensures assertions (кроме safety-only swap_if_less, у которого ensures
нет). Следовательно, цепочка role→symbol→full path→clause установлена в пределах
source-reported policy. Demangling/closure numbers сами по себе не являются
независимым AST/MIR binding или доказательством корректности toolchain.

В обычных profiles и concrete forwarders наблюдается check `{closure#3}` и
modifies `{closure#3}::{closure#2}`; у swap_if_less — `{closure#2}` и
`{closure#2}::{closure#2}`. Replace profiles имеют `{closure#2}`.
Эти suffixes — наблюдение конкретного pin; classifier не назначает роль по числу.
PFC precondition predicates находятся в source requires; они assumed, поэтому их
отсутствие среди assertions ожидаемо. `precondition_instance` у memcpy/free —
отдельные builtin checks, они не выдаются за target requires.

## По строкам

В таблице полные target instances; suffix check/modify либо Replace приведён
относительно этого instance. В ACCEPT.json сохранены raw symbol, обе полные wrapper
paths, все соответствующие exact property records, source sites и post-target covers.
Отдельные assigns properties перечислены с ID/function/description/status/site,
включая memcpy/memmove, helpers и counter negative. Все success/cover/role gates
v3 сохранены; 5 consumers зависят от соответствующего принятого leaf той же specialization.

| Строка | Полный target instance | check / modifies или Replace | Post assertions |
|---|---|---|---|
| `swap_contract_four_positions_u8` | `core::slice::sort::shared::smallsort::verify::merge::profiles::swap_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU8>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `swap_contract_four_positions_i32` | `core::slice::sort::shared::smallsort::verify::merge::profiles::swap_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtI32>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `swap_contract_four_positions_u64` | `core::slice::sort::shared::smallsort::verify::merge::profiles::swap_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU64>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `swap_contract_u8_n2` | `core::slice::sort::shared::smallsort::verify::merge::profiles::swap_profile::<core::slice::sort::shared::smallsort::verify::network::StrictU8>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `swap_contract_u64_n2` | `core::slice::sort::shared::smallsort::verify::merge::profiles::swap_profile::<core::slice::sort::shared::smallsort::verify::network::StrictU64>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `swap_contract_drop_u8_n2` | `core::slice::sort::shared::smallsort::verify::merge::profiles::swap_profile::<core::slice::sort::shared::smallsort::verify::network::DropU8>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `swap_contract_cell_i32_n2` | `core::slice::sort::shared::smallsort::verify::merge::profiles::swap_profile::<core::slice::sort::shared::smallsort::verify::network::CellI32>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `swap_contract_bytes16_n2` | `core::slice::sort::shared::smallsort::verify::merge::profiles::swap_profile::<core::slice::sort::shared::smallsort::verify::network::KeyB16>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `swap_contract_bytes17_n2` | `core::slice::sort::shared::smallsort::verify::merge::profiles::swap_profile::<core::slice::sort::shared::smallsort::verify::network::KeyB17>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `swap_contract_u8_indices_n17` | `core::slice::sort::shared::smallsort::verify::merge::profiles::swap_profile::<core::slice::sort::shared::smallsort::verify::network::StrictU8>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `swap_contract_u64_indices_n17` | `core::slice::sort::shared::smallsort::verify::merge::profiles::swap_profile::<core::slice::sort::shared::smallsort::verify::network::StrictU64>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `swap_contract_u8_n9` | `core::slice::sort::shared::smallsort::verify::merge::profiles::swap_profile::<core::slice::sort::shared::smallsort::verify::network::StrictU8>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `swap_contract_u8_n13` | `core::slice::sort::shared::smallsort::verify::merge::profiles::swap_profile::<core::slice::sort::shared::smallsort::verify::network::StrictU8>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `swap_contract_u64_n9` | `core::slice::sort::shared::smallsort::verify::merge::profiles::swap_profile::<core::slice::sort::shared::smallsort::verify::network::StrictU64>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `insert_tail_contract_u64_start1_tail2_to8` | `core::slice::sort::shared::smallsort::verify::merge::profiles::insert_tail_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU64>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 2, 3 |
| `insert_tail_contract_u64_start1_tail9_to12` | `core::slice::sort::shared::smallsort::verify::merge::profiles::insert_tail_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU64>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 2, 3 |
| `insert_tail_contract_u64_start1_tail13_to14` | `core::slice::sort::shared::smallsort::verify::merge::profiles::insert_tail_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU64>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 2, 3 |
| `insert_tail_contract_u64_start1_tail15_to16` | `core::slice::sort::shared::smallsort::verify::merge::profiles::insert_tail_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU64>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 2, 3 |
| `contract_insert_tail_u8_prefix` | `core::slice::sort::shared::smallsort::verify::merge::profiles::insert_tail_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU8>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 2, 3 |
| `sort4_contract_u64_n4` | `core::slice::sort::shared::smallsort::verify::merge::profiles::sort4_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::Sort4ReadU64>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `sort4_contract_bytes16_n4` | `core::slice::sort::shared::smallsort::verify::merge::profiles::sort4_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::Sort4ReadB16>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `merge_contract_u64_n2_to4` | `core::slice::sort::shared::smallsort::verify::merge::profiles::merge_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU64>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `merge_contract_u8_n2_to4` | `core::slice::sort::shared::smallsort::verify::merge::profiles::merge_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU8>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `merge_contract_u64_n5` | `core::slice::sort::shared::smallsort::verify::merge::profiles::merge_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU64>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `merge_contract_u8_n5` | `core::slice::sort::shared::smallsort::verify::merge::profiles::merge_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU8>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `merge_contract_u64_n6` | `core::slice::sort::shared::smallsort::verify::merge::profiles::merge_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU64>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `merge_contract_u8_n6` | `core::slice::sort::shared::smallsort::verify::merge::profiles::merge_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU8>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `merge_contract_u64_n7` | `core::slice::sort::shared::smallsort::verify::merge::profiles::merge_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU64>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `merge_contract_u8_n7` | `core::slice::sort::shared::smallsort::verify::merge::profiles::merge_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU8>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `merge_contract_u64_n8` | `core::slice::sort::shared::smallsort::verify::merge::profiles::merge_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU64>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `merge_contract_u8_n8` | `core::slice::sort::shared::smallsort::verify::merge::profiles::merge_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU8>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `merge_contract_u8_n9` | `core::slice::sort::shared::smallsort::verify::merge::profiles::merge_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU8>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `merge_scratch48_contract_u8_n9` | `core::slice::sort::shared::smallsort::verify::merge::profiles::merge_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU8>` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `stable_cell_n2` | `core::slice::sort::shared::smallsort::verify::forwarding_contracts::stable_cell` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `unstable_byte_n2` | `core::slice::sort::shared::smallsort::verify::forwarding_contracts::unstable_byte` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `freeze_noncopy_n2` | `core::slice::sort::shared::smallsort::verify::forwarding_contracts::freeze_noncopy` | `::{closure#3} / ::{closure#3}::{closure#2}` | 1, 2 |
| `profile_swap_consumer_u8_backing4` | `core::slice::sort::shared::smallsort::verify::merge::profiles::swap_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU8>` | `Replace ::{closure#2}` | assumed; accepted leaf |
| `profile_sort4_consumer_u64` | `core::slice::sort::shared::smallsort::verify::merge::profiles::sort4_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::Sort4ReadU64>` | `Replace ::{closure#2}` | assumed; accepted leaf |
| `profile_sort4_consumer_b16` | `core::slice::sort::shared::smallsort::verify::merge::profiles::sort4_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::Sort4ReadB16>` | `Replace ::{closure#2}` | assumed; accepted leaf |
| `profile_insert_consumer_u8_backing17` | `core::slice::sort::shared::smallsort::verify::merge::profiles::insert_tail_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU8>` | `Replace ::{closure#2}` | assumed; accepted leaf |
| `profile_merge_consumer_u8_len4` | `core::slice::sort::shared::smallsort::verify::merge::profiles::merge_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU8>` | `Replace ::{closure#2}` | assumed; accepted leaf |
| `swap_safety_u8_backing4` | `core::slice::sort::shared::smallsort::swap_if_less::<u8, core::slice::sort::shared::smallsort::verify::helper_contracts::arbitrary_less<u8>>` | `::{closure#2} / ::{closure#2}::{closure#2}` | нет ensures |
| `rejects_swap_comparator_writing_outside_frame_u8` | `core::slice::sort::shared::smallsort::swap_if_less::<u8, core::slice::sort::shared::smallsort::verify::helper_contracts::rejects_swap_comparator_writing_outside_frame_u8::{closure#0}>` | `::{closure#2} / ::{closure#2}::{closure#2}` | нет ensures |

## Covers и обнаруженные уточнения

168/168 cover records затронутых positive строк имеют SATISFIED; 147 обычных
source sites совпали с принятым mapping, 21 macro cover использует invocation span
(15 insert-tail, 6 merge). Source template и invocation сохраняются раздельно.
Insert-tail macro literal description сверяется с заданным tail, не только ordinal.
У merge len2..4 observed cover ordinals обратны lexical source order: ID1→length4,
ID2→length3, ID3→length2. В exact_binding_v4/covers записаны corrected source_line,
source_expression/indirect_target_call_chain и v3_mapping_source_line; старые receipts
не исправлялись. Проверка source_description/site связывает cover с возвратом
конкретного target. SAT означает существование исполнения после assumptions,
а не полноту всех путей или independent universal proof.

## Frame negative

Pre-run manifest на control `112fcc9ada` заранее требует generated modifies failure
для captured comparisons. Source `helper_contracts.rs:269-280` фиксирует законное
сравнение и единственную постороннюю запись line276. `smallsort.rs:413` разрешает
только `v_base[a_pos]` и `v_base[b_pos]`, source call line280 передаёт 0,1; counter
является другой local allocation, захваченной comparator closure.
Decoded metadata instance содержит F = exact full harness `{closure#0}`; его
modifies-wrapper suffix `{closure#2}::{closure#2}` совпадает с двумя DFCC raw-symbol
checks. Единственный FAILURE:

- ID `slice::sort::shared::smallsort::verify::helper_contracts::rejects_swap_comparator_writing_outside_frame_u8::{closure#0}.assigns.1`;
- description `Check that *var_9 is assignable`, exact class assigns;
- Location `library/core/src/slice/sort/shared/smallsort/verify/helper_contracts.rs:276:9`,
  function — exact comparator closure, та же F у target.

Отсюда принимается заранее заданный frame oracle, а не произвольный failure по
подобранному тексту. Generated var_9 spelling закреплён только за этим artifact;
source semantic criterion выбран до run. Нет посторонних failures. Независимый
trace object identity var_9→counter и independent compiler correctness не заявляются.
Manifest placeholder и исторический runner verdict остаются неизменными.

## Следующий export (не требуется новый run для текущего admission)

Достаточных данных для всех текущих policy bindings в artifact хватает; runner и
export не менялись, CI не выполнялся. Чтобы следующий анализ не зависел от regular
stdout, минимально добавить в JSON полный property inventory (id/class/status,
source_location.function/file/line/column/description), включая SUCCESS; сейчас
checks.success — только счётчик. Плюс demangled contract symbol и resolved target
instance, check/replace/modifies-wrapper symbols/roles из compiler metadata.
Для усиленного independent MIR/DFCC audit понадобятся source span/DefId/instance
и связь property→enforced-contract symbol (у assigns отдельные write-site и owner),
а для frame negative — trace object/lvalue correspondence. Эти данные не подменяются
closure ordinal, terminal fn name, hashes или общим PASS. Это предложение следующего
экспорта, не выполненный runner change и не authorization на CI.
