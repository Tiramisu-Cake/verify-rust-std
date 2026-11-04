# REALCONTRACTSTWO — итог G1/G2
G1 build `6ba92a58-0136-490d-a553-4649e9ce254d`, source `15703f81d243be38e04c13c27b3e5789fec92e01`: COMPLETE, Cloud FAILURE, gate false (sort4 unwind); шесть SUCCESS и ожидаемый negative FAILED.
G2 build `1c18c183-7714-4d23-9c25-41e9786dfd5a`, source `41a524a98d6e1136716f95b0b57aaeea48ed8496`: COMPLETE, Cloud SUCCESS, gate/expectations true; четыре SUCCESS и ожидаемый negative FAILED, Kani exit 1; owner k1-network.
В обоих check-tooling PASS: pool/source identity, lane paths и шесть SHA-256 против `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`. Request hashes/полные данные: [ledger](realcontractstwo-ledger.json).
Точные новые атрибуты (свёрнуты только пробелы/переносы): insert_tail, sort4_stable, bidirectional_merge; cfg(kani)-helper/контекст: [G1](PREBUILD-REALCONTRACTSTWO.md), [G2](PREBUILD-REALCONTRACTSTWO-G2.md).
```rust
#[safety::requires( begin < tail && insert_tail_contract_len(begin, tail) > 1 && crate::ub_checks::can_dereference(ptr::slice_from_raw_parts( begin, insert_tail_contract_len(begin, tail), )) && crate::ub_checks::can_write(ptr::slice_from_raw_parts_mut( begin, insert_tail_contract_len(begin, tail), )) )] #[cfg_attr( kani, crate::kani::modifies(ptr::slice_from_raw_parts_mut(begin, insert_tail_contract_len(begin, tail))) )]
#[safety::requires( crate::ub_checks::can_dereference(ptr::slice_from_raw_parts(v_base, 4)) && crate::ub_checks::can_write(ptr::slice_from_raw_parts_mut(dst, 4)) && sort4_contract_regions_disjoint(v_base, dst) )] #[cfg_attr(kani, crate::kani::modifies(ptr::slice_from_raw_parts_mut(dst, 4)))]
#[safety::requires(v.len() >= 2)] #[safety::requires(crate::ub_checks::can_dereference(v as *const [T]))] #[safety::requires(crate::ub_checks::can_write(ptr::slice_from_raw_parts_mut(dst, v.len())))] #[safety::requires(merge_contract_regions_disjoint(v.as_ptr(), dst, v.len()))] #[cfg_attr(kani, crate::kani::modifies(ptr::slice_from_raw_parts_mut(dst, v.len())))]
```

| Этап | Корень verify:: | Статус | Время, с | Failed/total | Covers |
| --- | --- | --- | --- | --- | --- |
| G1 | realcontracts::swap_safety_u8_backing9 | SUCCESS | 17.355093 | 0/219 | 6/6 |
| G1 | realcontracts::swap_safety_u8_backing13 | SUCCESS | 17.583559 | 0/219 | 6/6 |
| G1 | realcontracts::unstable_network_safety_u8_n9_stubbed | SUCCESS | 11.660206 | 0/383 | 1/3 |
| G1 | realcontracts::unstable_network_safety_u8_n13_stubbed | SUCCESS | 13.978799 | 0/383 | 1/3 |
| G1 | realcontracts::insert_tail_safety_u64_tail1_to4_backing5 | SUCCESS | 34.020428 | 0/219 | 7/7 |
| G1 | realcontracts::rejects_insert_tail_equal_begin_u64 | FAILED | 0.20505936 | 1/205 | 1/3 |
| G1 | realcontracts::sort4_safety_u64 | FAILED | 14.53286 | 1/271 | 2/3 |
| G1 | assembly::sorted_permutation_insert_tail_u8_n2 | SUCCESS | 0.31345087 | 0/106 | 1/1 |
| G2 | realcontracts::sort4_safety_u64 | SUCCESS | 36.28767 | 0/293 | 3/3 |
| G2 | realcontracts::sort4_safety_bytes16 | SUCCESS | 73.99763 | 0/462 | 3/3 |
| G2 | realcontracts::merge_safety_u64_len2 | SUCCESS | 27.213285 | 0/284 | 4/4 |
| G2 | realcontracts::merge_safety_u64_len4 | SUCCESS | 42.305798 | 0/284 | 4/4 |
| G2 | realcontracts::rejects_merge_overlapping_dst_u64 | FAILED | 0.5439207 | 1/235 | 1/3 |

Оба negative подтверждены ровно одним requires: G1 `begin < tail && insert_tail_contract_len(begin, tail) > 1 &&` (smallsort.rs:582); G2 `merge_contract_regions_disjoint(v.as_ptr(), dst, v.len())` (:847), source[0..2]/dst[1..3] в backing4.
Композиция swap: обе пары PFC backing9 ↔ consumer N9 и backing13 ↔ N13 SUCCESS; совпали u8, backing N и function-item arbitrary_less::<u8>. Произвольные позиции PFC покрывают все 25/45 network call-site; это bounded evidence этих доменов.
Домены helper: insert u64 backing5 tail1..4; sort4 u64/[u8;16] source4 + disjoint writable dst4; merge u64 len2/4 + disjoint dst той же длины, T: FreezeMarker сохранён. Компаратор читает оба аргумента и выдаёт свежий bool; sortedness premise/ensures не добавлены.
G1 sort4 FAILED только на unwinding assertion в builtin-memcmp:25; G2 заменил array equality скалярными сравнениями при неизменном контракте/runtime, u64 unwind16 и bytes16 unwind32. G2 SUCCESS закрывает bounded PFC; точная caller/causal-привязка G1 memcmp не установлена.
Covers: swap PFC 6/6, insert 7/7, sort4 3/3, merge 4/4. Consumer 1/3 соответствует return и двум недостижимым callback covers по исходнику. Merge panic-stub: cover явного order-violation, assume(false); работа до границы проверяется, panic unwinding не доказан.
В ordinary-кандидаты переносим safety/modifies и PFC в перечисленных доменах; ordinary u8 insert N2 отдельно исполнил real body со strict comparator и подтвердил sorted permutation. Другие backing/T/F и композиции требуют совпадающего домена; нет universal callback-frame/order/Drop/ZST proof, uninit/value-validity flags выключены.
Расход G1 $0.1485 + G2 $0.1620 = $0.3105 <= $3; bounded budget: `2 0.3105 0.0000`, две primary build, без compile-repair. Verify wall/RSS: G1 3:11.46/1748140 KiB; G2 4:39.72/1815204 KiB; OOM scans none_seen не доказывают запас RAM.
После G2 изменены только отчёты/ledger; library/request/tooling сохранены. Далее review и отдельное задание для расширения доменов/ordinary интеграции; новых сборок в этой задаче не запускаем.
