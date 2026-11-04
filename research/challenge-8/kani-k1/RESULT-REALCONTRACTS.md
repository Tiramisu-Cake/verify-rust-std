# REALCONTRACTS — итог G1/G2
G1 `23fa5dee5f23645abea868d1370b46298d96435b`, build `841ecc9e-3696-4188-aad0-300cd6f4a35b`: COMPILE_ERROR E0433/E0034, все 8 NOT_RUN.
G1r `7cea662d2c09be7f114aa5fe6a111648f1e5d139`, build `7420db72-52f9-4f7e-9bdf-774780d91e84`: COMPLETE, gate false (insertion TIMEOUT).
G2 `c848fd4d0ddf5cfbb6ec3b0cccee12cfca88be1b`, build `ee952605-3d34-4831-b34d-5e84d22c2aea`: COMPLETE, gate true; Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, owner k1-merge; все check-tooling PASS против `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`. Request id/hash, checks и RSS: [ledger](realcontracts-ledger.json). Точные атрибуты (переносы свёрнуты; тела/сигнатуры неизменны; repair только `#[cfg(kani)] use crate::kani;`):
```rust
#[safety::requires( a_pos.checked_mul(size_of::<T>()).is_some_and(|offset| { offset <= isize::MAX as usize && (v_base as isize).checked_add(offset as isize).is_some() && ptr::byte_offset_does_not_wrap(v_base, offset as isize) }) )]
#[safety::requires( b_pos.checked_mul(size_of::<T>()).is_some_and(|offset| { offset <= isize::MAX as usize && (v_base as isize).checked_add(offset as isize).is_some() && ptr::byte_offset_does_not_wrap(v_base, offset as isize) }) )]
#[safety::requires( crate::ub_checks::same_allocation(v_base, v_base.wrapping_add(a_pos)) && crate::ub_checks::same_allocation(v_base, v_base.wrapping_add(b_pos)) )]
#[safety::requires( crate::ub_checks::can_dereference(v_base.wrapping_add(a_pos)) && crate::ub_checks::can_write(v_base.wrapping_add(a_pos)) )]
#[safety::requires( crate::ub_checks::can_dereference(v_base.wrapping_add(b_pos)) && crate::ub_checks::can_write(v_base.wrapping_add(b_pos)) )]
#[cfg_attr(kani, crate::kani::modifies(v_base.wrapping_add(a_pos), v_base.wrapping_add(b_pos)))]
#[safety::requires(offset != 0 && offset <= v.len())]
#[cfg_attr(kani, crate::kani::modifies(v))]
```

| Этап / verify::harness | Expect | Статус | Секунды (до → после для регрессии) | Failed/total; covers |
| --- | --- | --- | --- | --- |
| G1r / realcontracts::swap_safety_u8_backing4 | SUCCESS | SUCCESS | 19.355654 | 0/229; 6/6 |
| G1r / realcontracts::swap_safety_u64_backing4 | SUCCESS | SUCCESS | 19.362135 | 0/229; 6/6 |
| G1r / realcontracts::swap_safety_bytes17_backing4 | SUCCESS | SUCCESS | 31.84324 | 0/402; 6/6 |
| G1r / realcontracts::insertion_safety_u64_len1_to6 | SUCCESS | TIMEOUT | лимит 5 мин | —; — |
| G1r / realcontracts::rejects_swap_outside_backing_u8 | FAILED | FAILED | 0.17645621 | 1/137; 1/3 |
| G1r / network::dispatch_safety_stable_u8_n0_1_2_7_8 | SUCCESS | SUCCESS | 11.6 → 12.086438 | 0/388; 6/6 |
| G1r / network::swap_contract_four_positions_u8 | SUCCESS | SUCCESS | 12.8 → 14.242737 | 0/326; 5/5 |
| G1r / network::insertion_safety_u64_n1_to5 | SUCCESS | SUCCESS | 10.211888 | 0/119; 16/16 |
| G2 / realcontracts::insertion_safety_u64_len2 | SUCCESS | SUCCESS | 81.02985 | 0/160; 6/6 |
| G2 / realcontracts::insertion_safety_u64_len3 | SUCCESS | SUCCESS | 105.375145 | 0/160; 6/6 |
| G2 / realcontracts::unstable_network_safety_u8_n9_real | SUCCESS | SUCCESS | 6.299193 | 0/298; 3/3 |
| G2 / realcontracts::unstable_network_safety_u8_n9_stubbed | SUCCESS | SUCCESS | 8.070763 | 0/375; 1/3 |
| G2 / realcontracts::unstable_network_safety_u8_n13_real | SUCCESS | SUCCESS | 11.438447 | 0/298; 3/3 |
| G2 / realcontracts::unstable_network_safety_u8_n13_stubbed | SUCCESS | SUCCESS | 16.726189 | 0/375; 1/3 |

Контроль: единственный failed check `crate::ub_checks::can_dereference(v_base.wrapping_add(b_pos)) &&` @ `/workspace/src/library/core/src/slice/sort/shared/smallsort.rs:404` (requires). Регрессии SUCCESS: +4.2%/+11.3%; «до» из TASK/NEWPINCAL, статус/идентичность не перепроверены, причинность не установлена.
Insertion PFC осуществим для len2/3; G1 len1..6 TIMEOUT не закрыт. Stubbed N9/N13 медленнее real на 28.1%/46.2%; 1/3 covers (2 unreachable) против 3/3; callback заменён. Consumers используют summary на backing9/13, G1 swap-body PFC ограничен backing4: это не независимый универсальный proof тела на больших backing.
Не проверены порядок/перестановка, произвольный callback frame/stateful/external effects, ZST/non-Copy/Drop, panic/unwinding, uninit/value validity; insert_tail/bidirectional_merge и модель ensures остаются отдельными следующими шагами. Расход $0.1350+$0.2295+$0.1755=$0.5400 из $3, reserve $0; два primary builds + один G1 repair. REALCONTRACTS ЗАВЕРШЁН.
