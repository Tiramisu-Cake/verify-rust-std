# REALCONTRACTS — результат G1 / compile-error repair на review
G1 SHA `23fa5dee5f23645abea868d1370b46298d96435b`; library `3f0fc215587ee4b5ab4e8e9f901e49ea206f7c19`; owner `k1-merge`.
Build `841ecc9e-3696-4188-aad0-300cd6f4a35b`; Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`.
Request `realcontracts-g1-20261104`, sha256 `57bffccb99cb7e7b5db0007d3e95cb36890b1160b6016d34032d2409f28ef138`.
Bounded summary: COMPILE_ERROR; check-tooling PASS против `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`.

Точные атрибуты (переносы строк свёрнуты; тела/сигнатуры не менялись):
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

| Строка verify:: | Ожидание | G1 | До → после, с |
| --- | --- | --- | --- |
| realcontracts::swap_safety_u8_backing4 | SUCCESS | NOT_RUN | нет данных → нет |
| realcontracts::swap_safety_u64_backing4 | SUCCESS | NOT_RUN | нет данных → нет |
| realcontracts::swap_safety_bytes17_backing4 | SUCCESS | NOT_RUN | нет данных → нет |
| realcontracts::insertion_safety_u64_len1_to6 | SUCCESS | NOT_RUN | нет данных → нет |
| realcontracts::rejects_swap_outside_backing_u8 | FAILED | NOT_RUN | нет данных → нет |
| network::dispatch_safety_stable_u8_n0_1_2_7_8 | SUCCESS | NOT_RUN | 11.6 (task) → нет |
| network::swap_contract_four_positions_u8 | SUCCESS | NOT_RUN | 12.8 (task) → нет |
| network::insertion_safety_u64_n1_to5 | SUCCESS | NOT_RUN | нет данных → нет |

Диагностика: E0433, `kani` не найден в expansion requires/modifies; также E0034 в базовых числовых методах (связь с E0433 не установлена). Safe-function support не установлен.
Compile repair library `2e7f1a6db52778a1e9a9652f02b639f088fb2cd3`: только `#[cfg(kani)] use crate::kani;`; request_id `realcontracts-g1-compile-repair1-20261104`.
G1 стоил $0.135; repair reserve $0.945; сумма $1.080 ≤ $3. Новый dispatch только после exact-packet GO; G2 не запускалась.
Для stub_verified новых доказательств нет; следующий insert_tail/bidirectional_merge и модель ensures остаются отдельными шагами.
Не проверены: compile repair, PFC/frame, negative requires failure, covers, регрессионные времена; stateful/external effects, ZST/non-Copy/Drop, panic, uninit/value validity.
