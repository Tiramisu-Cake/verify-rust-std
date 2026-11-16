# Profiles ON — intake accept-v4, worker15

49 **ACCEPTED**, 13 **BLOCKED_TOOL**, 0 REJECTED, 0 PENDING (62/62).
Это policy admission bounded source-reported observations; independent proof credit **NONE**,
B2/full-domain theorem не установлен. Ни одна OFF admission не переносилась.
Одна назначенная intake-стадия завершена; исходные receipts, исходники и ledger сохранены.

Вход g0 `b4c4a16f25053d93fbd573fb710762b8a1697a94`; intake RESULT из `d07f0eaa55`.
Run `43798838603`, artifact id `14198355109`; read-only directory предоставлен заданием.
Source `9fa2f7f97760584f38738909625c064006d8a936`, SEL1 `14bc57fdb99960240c4944845a3d985c8af4dcf7`,
control trigger `7f33fb9067b9a6f7614449784c6adcdea6886237`. Проверены request SHA, manifest,
source before/after + trees/changed-file hashes, неизменные binary fingerprints,
точный argv/cfg, tool/features/config/unwind и export SHA обоих groups.
Связь directory→artifact id задана владельцем; независимая ZIP/archive attestation здесь не выполнялась.

`intake.py` заново применяет v2 inventory/policy gates, v3 source-site role rules и v4
exact target/profile/contract-wrapper/clause/cover/frame binding. Reuse-файлы сверены
с CLASSIFIER-REUSE.json; contract/export цепочка SEL1 сверена со stock по байтам.
Все 49 admitted строк имеют fresh binding, полный ID/status inventory, ноль UNKNOWN roles,
полный required cover inventory и все required covers SAT. Два admitted Replace consumers
имеют accepted matching leaves и точное равенство полного specialized instance; три остальных BLOCKED.

Raw logs целиком не читались: bounded `rg -m` выбирает только ID/status lines, terminal markers
и нужные exact-ID property blocks с контекстом до12 строк. По export count проверены число,
последовательность и уникальность всех45254 properties (45065 checks +189 covers);
потерянные IDs/статусы/receipts/truncation отвергаются. SHA256 считается как непрозрачный hash.
Точное число non-cover checks — 45065; properties вместе с189 covers — 45254.
Повторяемый offline replay: `PYTHONDONTWRITEBYTECODE=1 python intake.py` из этой папки.

## 13 BLOCKED_TOOL

У12 positive строк инструментальный failure — **единственный** failure во всём exact-harness inventory.
Исключение `rejects_always_true`: 1 unsupported + 2 собственных negative failures; foreign failures нет.
Все exact IDs/classes/descriptions/locations и stdout function записаны в `tool_failure_binding` / `named_failures`.

| Строка | Exact tool property ID | Всего failures |
|---|---|---|
| `swap_contract_u8_n2` | `mem::maybe_uninit::MaybeUninit::<u8>::array_assume_init::<2>.unsupported_construct.1` | 1 |
| `swap_contract_u64_n2` | `mem::maybe_uninit::MaybeUninit::<u64>::array_assume_init::<2>.unsupported_construct.1` | 1 |
| `swap_contract_drop_u8_n2` | `mem::maybe_uninit::MaybeUninit::<slice::sort::shared::smallsort::verify::network::DropValue>::array_assume_init::<2>.unsupported_construct.1` | 1 |
| `swap_contract_cell_i32_n2` | `mem::maybe_uninit::MaybeUninit::<cell::Cell<i32>>::array_assume_init::<2>.unsupported_construct.1` | 1 |
| `swap_contract_bytes16_n2` | `mem::maybe_uninit::MaybeUninit::<[u8; 16]>::array_assume_init::<2>.unsupported_construct.1` | 1 |
| `swap_contract_bytes17_n2` | `mem::maybe_uninit::MaybeUninit::<[u8; 17]>::array_assume_init::<2>.unsupported_construct.1` | 1 |
| `sort4_contract_bytes16_n4` | `mem::maybe_uninit::MaybeUninit::<[u8; 16]>::array_assume_init::<4>.unsupported_construct.1` | 1 |
| `freeze_noncopy_n2` | `array::iter::iter_inner::PolymorphicIter::<[mem::maybe_uninit::MaybeUninit<usize>; 2]>::new_unchecked.unsupported_construct.1` | 1 |
| `profile_sort4_consumer_u64` | `kani::internal::write_any_slice::<u64>.safety_check.1` | 1 |
| `profile_sort4_consumer_b16` | `mem::maybe_uninit::MaybeUninit::<[u8; 16]>::array_assume_init::<4>.unsupported_construct.1` | 1 |
| `profile_merge_consumer_u8_len4` | `kani::internal::write_any_slice::<u8>.safety_check.1` | 1 |
| `rejects_always_true` | `array::iter::iter_inner::PolymorphicIter::<[mem::maybe_uninit::MaybeUninit<usize>; 2]>::new_unchecked.unsupported_construct.1` | 3 |
| `swap_safety_u8_backing4` | `<for<'a, 'b> fn(&'a u8, &'b u8) -> bool {slice::sort::shared::smallsort::verify::helper_contracts::arbitrary_less::<u8>} as ops::function::FnMut<(&u8, &u8)>>::call_mut.unsupported_construct.1` | 1 |

PolymorphicIter: `array/iter/iter_inner.rs:96`, невозможность определить init layout union/MaybeUninit.
Array conversion: `mem/maybe_uninit.rs:1056` (`array_assume_init` → `transmute_unchecked`),
явный unsupported для переноса initialization state массива. Fn-item: `ops/function.rs:166`,
неподдержанный init layout конкретного function item при FnMut dispatch.
Эти unsupported properties сгенерированы Kani в стандартных helper/call sites; assertion алгоритма
не является failed property. Это не доказательство отсутствия ошибки в алгоритме.

`write_any_slice::<u8/u64>.safety_check.1` принадлежит Kani replacement/havoc model,
`library/kani_core/src/lib.rs:711–717` (посткомпиляционная замена `write_any`). Diagnostic site
`library/core/src/lib.rs:357` нельзя объявлять местом алгоритмической ошибки или implementation line716;
source site у `.safety_check.2` — model line716, статус SUCCESS. Exact blocks сохранены в supplemental_havoc_checks.
Без trace причинность failure и отдельный Kani bug не доказаны; BLOCKED_TOOL означает blocked model observation.

У `rejects_always_true` собственные `.assertion.4` (bad unstable adapter relation rejected, forwarding_contracts.rs:224)
и `.assertion.6` (bad stable adapter relation rejected, :215) имеют FAILURE: эти две negatives сработали.
`.assertion.2` (bad Freeze adapter relation rejected, :233) UNREACHABLE; весь прежний тройной oracle не закрыт.
Дополнительный PolymorphicIter failure сохраняет BLOCKED_TOOL; частичное срабатывание не даёт admission.
Все остальные8 negative rows имеют исходные exact named failures без посторонних failures и ACCEPTED.
Frame negative заново связан v4 по comparator closure `.assigns.1`, helper_contracts.rs:276,
write set двух элементов и sole enforced contract; independent pointer→var_9 trace по-прежнему не установлен.

## Unreachable и covers

2698 unreachable checks по всем62: 856 `instrumentation_defensive_branch` в `kani::mem_init::*`,
1738 defensive branches по v3, 16 обязательных postconditions, 2 frame, 1 required section,
85 UNKNOWN roles. **Все required-unreachable и UNKNOWN находятся только в13 BLOCKED_TOOL строках**;
они сохранены как дополнительные препятствия, а не разрешены инструментальным failure.
В категории mem_init перечислены exact ID/function/file/line/description каждого случая.

Mem-init исключения ограничены конкретными source families/sites в pinned `library/kani_core/src/mem_init.rs`:
`get`93/95, `set`118/120, `copy_by_id`166/171/173/181/183, `get_slice`204/206,
`set_slice`230/232, `store_argument`479/488, `load_argument`537/539/543.
Это arithmetic/bounds error branches shadow-byte state и передачи shadow argument state:
нулевые layouts пропускают loops, copy выбирает соответствующий object/offset, argument transfer
ограничен конкретными layouts и protocol branch. Они не являются истинностью init predicate,
postcondition/frame/relation; правило требует совместно family+file+line+column+description+assertion ID.
Само имя helper не разрешает исключение. Недостижимость этих веток не доказывает полноту instrumentation;
reachable failures остаются blockers, required target/wrapper clauses проверяются отдельно.

Все383 successful unsupported проверены по exact same-row ID/class/status/description/site из stdout и export.
Pinned export связывает класс с property, а общий generator unsupported в `codegen/assert.rs:129–145,214–220,278–324`
и mem-init цепочка `check_uninit/mod.rs:230–232,852–860` → `transform/body.rs:512–518` →
`overrides/hooks.rs:223–240`, а также foreign/intrinsic paths строят `assert(false); assume(false)`. SUCCESS означает недостижимость
конструкции в данной модели; поддержка самой конструкции не заявляется.11 reachable unsupported failures
и2 havoc failures не разрешены. Новые ON-only entries не используют stock ordinal или старое описание.

OFF all62:1710 unreachable checks,189 SAT covers. ON all62:2698 unreachable checks,144 SAT +45 UNREACHABLE covers.
Ранее приведённые1505/179 относятся только к OFF positive53, а не ко всем62.
В JSON для каждой строки сохранены полные добавленные/исчезнувшие unreachable IDs и cover status deltas.
Raw ID comparison не доказывает semantic equivalence при перенумерации: admitted rows отдельно связаны
по literal clause и source site. В blocked строках binding остаётся незакрытым там, где required property
не SUCCESS или cover не SAT; это явно отражено в pending_reasons/binding_state.

| Строка | Intake ON | Unreachable OFF→ON | Covers OFF SAT→ON SAT/unreachable | Добавлено/убрано unreachable IDs |
|---|---|---:|---:|---:|
| `swap_contract_four_positions_u8` | ACCEPTED | 4→7 | 5→5/0 | +3 / −0 |
| `swap_contract_four_positions_i32` | ACCEPTED | 4→12 | 5→5/0 | +8 / −0 |
| `swap_contract_four_positions_u64` | ACCEPTED | 4→12 | 5→5/0 | +8 / −0 |
| `swap_contract_u8_n2` | BLOCKED_TOOL | 4→50 | 5→0/5 | +46 / −0 |
| `swap_contract_u64_n2` | BLOCKED_TOOL | 4→40 | 5→0/5 | +36 / −0 |
| `swap_contract_drop_u8_n2` | BLOCKED_TOOL | 4→50 | 5→0/5 | +46 / −0 |
| `swap_contract_cell_i32_n2` | BLOCKED_TOOL | 4→43 | 5→0/5 | +39 / −0 |
| `swap_contract_bytes16_n2` | BLOCKED_TOOL | 4→60 | 5→0/5 | +56 / −0 |
| `swap_contract_bytes17_n2` | BLOCKED_TOOL | 4→60 | 5→0/5 | +56 / −0 |
| `swap_contract_u8_indices_n17` | ACCEPTED | 4→7 | 7→7/0 | +3 / −0 |
| `swap_contract_u64_indices_n17` | ACCEPTED | 4→12 | 7→7/0 | +8 / −0 |
| `swap_contract_u8_n9` | ACCEPTED | 4→7 | 7→7/0 | +3 / −0 |
| `swap_contract_u8_n13` | ACCEPTED | 4→7 | 7→7/0 | +3 / −0 |
| `swap_contract_u64_n9` | ACCEPTED | 4→12 | 7→7/0 | +8 / −0 |
| `insert_tail_contract_u64_start1_tail2_to8` | ACCEPTED | 52→60 | 9→9/0 | +8 / −0 |
| `insert_tail_contract_u64_start1_tail9_to12` | ACCEPTED | 44→52 | 6→6/0 | +8 / −0 |
| `insert_tail_contract_u64_start1_tail13_to14` | ACCEPTED | 40→48 | 4→4/0 | +8 / −0 |
| `insert_tail_contract_u64_start1_tail15_to16` | ACCEPTED | 36→44 | 4→4/0 | +8 / −0 |
| `contract_insert_tail_u8_prefix` | ACCEPTED | 34→37 | 4→4/0 | +3 / −0 |
| `sort4_contract_u64_n4` | ACCEPTED | 68→78 | 1→1/0 | +10 / −0 |
| `sort4_contract_bytes16_n4` | BLOCKED_TOOL | 73→150 | 1→0/1 | +77 / −0 |
| `merge_contract_u64_n2_to4` | ACCEPTED | 70→84 | 6→6/0 | +14 / −0 |
| `merge_contract_u8_n2_to4` | ACCEPTED | 70→79 | 6→6/0 | +9 / −0 |
| `merge_contract_u64_n5` | ACCEPTED | 68→78 | 1→1/0 | +10 / −0 |
| `merge_contract_u8_n5` | ACCEPTED | 68→73 | 1→1/0 | +5 / −0 |
| `merge_contract_u64_n6` | ACCEPTED | 66→76 | 1→1/0 | +10 / −0 |
| `merge_contract_u8_n6` | ACCEPTED | 66→71 | 1→1/0 | +5 / −0 |
| `merge_contract_u64_n7` | ACCEPTED | 64→74 | 1→1/0 | +10 / −0 |
| `merge_contract_u8_n7` | ACCEPTED | 64→69 | 1→1/0 | +5 / −0 |
| `merge_contract_u64_n8` | ACCEPTED | 62→72 | 1→1/0 | +10 / −0 |
| `merge_contract_u8_n8` | ACCEPTED | 62→67 | 1→1/0 | +5 / −0 |
| `merge_contract_u8_n9` | ACCEPTED | 60→65 | 1→1/0 | +5 / −0 |
| `merge_scratch48_contract_u8_n9` | ACCEPTED | 61→68 | 2→2/0 | +7 / −0 |
| `profile_relation_lt_u8` | ACCEPTED | 0→0 | 1→1/0 | +0 / −0 |
| `profile_relation_lt_i32` | ACCEPTED | 0→0 | 1→1/0 | +0 / −0 |
| `profile_relation_lt_u64` | ACCEPTED | 0→0 | 1→1/0 | +0 / −0 |
| `profile_relation_read_u64` | ACCEPTED | 2→7 | 1→1/0 | +5 / −0 |
| `profile_relation_read_b16` | ACCEPTED | 2→7 | 1→1/0 | +5 / −0 |
| `profile_relation_strict_u8` | ACCEPTED | 0→0 | 1→1/0 | +0 / −0 |
| `profile_relation_strict_u64` | ACCEPTED | 0→0 | 1→1/0 | +0 / −0 |
| `profile_relation_cell_i32` | ACCEPTED | 0→0 | 1→1/0 | +0 / −0 |
| `profile_relation_drop_u8` | ACCEPTED | 2→7 | 1→1/0 | +5 / −0 |
| `profile_relation_key_b16` | ACCEPTED | 0→0 | 1→1/0 | +0 / −0 |
| `profile_relation_key_b17` | ACCEPTED | 0→0 | 1→1/0 | +0 / −0 |
| `stable_cell_n2` | ACCEPTED | 10→14 | 9→9/0 | +4 / −0 |
| `unstable_byte_n2` | ACCEPTED | 32→80 | 7→7/0 | +48 / −0 |
| `freeze_noncopy_n2` | BLOCKED_TOOL | 19→75 | 7→0/7 | +56 / −0 |
| `profile_swap_consumer_u8_backing4` | ACCEPTED | 4→39 | 1→1/0 | +35 / −0 |
| `profile_sort4_consumer_u64` | BLOCKED_TOOL | 68→95 | 1→1/0 | +27 / −0 |
| `profile_sort4_consumer_b16` | BLOCKED_TOOL | 73→150 | 1→0/1 | +77 / −0 |
| `profile_insert_consumer_u8_backing17` | ACCEPTED | 34→52 | 3→3/0 | +18 / −0 |
| `profile_merge_consumer_u8_len4` | BLOCKED_TOOL | 71→88 | 1→1/0 | +17 / −0 |
| `profile_wrong_f_swap_rejected_u8` | ACCEPTED | 4→4 | 1→1/0 | +0 / −0 |
| `profile_wrong_f_sort4_rejected_u64` | ACCEPTED | 32→39 | 1→1/0 | +7 / −0 |
| `profile_wrong_f_insert_rejected_u8` | ACCEPTED | 33→33 | 1→1/0 | +0 / −0 |
| `profile_wrong_f_merge_rejected_u8` | ACCEPTED | 34→36 | 1→1/0 | +2 / −0 |
| `profile_bad_relation_rejected_u8` | ACCEPTED | 0→0 | 1→1/0 | +0 / −0 |
| `profile_full_value_checker_rejects_payload_change_u8` | ACCEPTED | 60→60 | 1→1/0 | +0 / −0 |
| `rejects_always_true` | BLOCKED_TOOL | 20→76 | 3→3/0 | +56 / −0 |
| `rejects_payload_corruption` | ACCEPTED | 18→66 | 1→1/0 | +48 / −0 |
| `swap_safety_u8_backing4` | BLOCKED_TOOL | 4→39 | 6→0/6 | +35 / −0 |
| `rejects_swap_comparator_writing_outside_frame_u8` | ACCEPTED | 4→7 | 0→0/0 | +3 / −0 |

Validation: 8 targeted ON synthetic tests +31 v2 +25 v3 +20 v4 =84 PASS.
Offline inventory/classifier replay PASS; compiler/verifier invocations0.
Без push/CI/публикаций/ledger. Следующая стадия не запускалась.

Независимый bounded source/acceptance audit: GPT-6 Luna HIGH, findings на текущую49/13
классификацию не найдено. Рекомендация включить source columns в33 mem-init tuples применена;
мутации чужой site/column/description и target failure вместе с tool failure проверены synthetic guards.
