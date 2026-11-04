# REALCONTRACTS — G1 и единственный compile repair
G1 `23fa5dee5f23645abea868d1370b46298d96435b`, build `841ecc9e-3696-4188-aad0-300cd6f4a35b`: COMPILE_ERROR (E0433/E0034), все 8 NOT_RUN.
Repair `7cea662d2c09be7f114aa5fe6a111648f1e5d139`, build `7420db72-52f9-4f7e-9bdf-774780d91e84`; Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`; owner `k1-merge`.
Request/hash: `realcontracts-g1-20261104` / `57bffccb99cb7e7b5db0007d3e95cb36890b1160b6016d34032d2409f28ef138`; `realcontracts-g1-compile-repair1-20261104` / `b345ecd6fb42f6a5bec12fc9c1e05274256a7dfafcc18c4b08bb2aa76d0bd4c7`.
Repair summary COMPLETE, gate false (insertion TIMEOUT); compilation прошла; оба check-tooling PASS против `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`.

Точные атрибуты (переносы строк свёрнуты; тела/сигнатуры не менялись; repair добавил только `#[cfg(kani)] use crate::kani;`):
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

| Строка verify:: | Expect | G1 → repair | Секунды до → после | Failed/total; covers |
| --- | --- | --- | --- | --- |
| realcontracts::swap_safety_u8_backing4 | SUCCESS | NOT_RUN → SUCCESS | — → 19.355654 | 0/229; 6/6 |
| realcontracts::swap_safety_u64_backing4 | SUCCESS | NOT_RUN → SUCCESS | — → 19.362135 | 0/229; 6/6 |
| realcontracts::swap_safety_bytes17_backing4 | SUCCESS | NOT_RUN → SUCCESS | — → 31.84324 | 0/402; 6/6 |
| realcontracts::insertion_safety_u64_len1_to6 | SUCCESS | NOT_RUN → TIMEOUT | — → нет (лимит 5 мин) | —; — |
| realcontracts::rejects_swap_outside_backing_u8 | FAILED | NOT_RUN → FAILED | — → 0.17645621 | 1/137; 1/3 |
| network::dispatch_safety_stable_u8_n0_1_2_7_8 | SUCCESS | NOT_RUN → SUCCESS | 11.6 → 12.086438 | 0/388; 6/6 |
| network::swap_contract_four_positions_u8 | SUCCESS | NOT_RUN → SUCCESS | 12.8 → 14.242737 | 0/326; 5/5 |
| network::insertion_safety_u64_n1_to5 | SUCCESS | NOT_RUN → SUCCESS | — → 10.211888 | 0/119; 16/16 |

Контроль: единственный failed check `crate::ub_checks::can_dereference(v_base.wrapping_add(b_pos)) &&` @ `/workspace/src/library/core/src/slice/sort/shared/smallsort.rs:404` (requires); 1/3 covers, достижимость остальных не исследована.
Insertion safe-функция приняла атрибуты, PFC не доказан: CBMC timed out, peak 14.88 GiB; whole-run peak 15609960 KiB, wall 8:45.61; OOM scan none_seen.
Регрессии SUCCESS; времена dispatch +4.2%, swap-profile +11.3%; «до» из TASK/NEWPINCAL, прежний статус/идентичность не перепроверены, причинность замедления не установлена.
Stub_verified: три bounded swap PFC (u8/u64/[u8;17], backing4, stateless nondeterministic F) и requires-контроль успешны; не переносить proof credit на иные F/домены. insert_tail/bidirectional_merge и модель ensures — следующие отдельные шаги.
Не проверены: insertion PFC/covers, порядок/перестановка, универсальный callback frame/stateful/external effects, ZST/non-Copy/Drop, panic/unwinding, uninit/value validity; 4/4/9 unreachable checks в swap PFC не равны covers (все 6/6 достигнуты).
Бюджет: G1 $0.1350 + repair $0.2295 = $0.3645, reserve $0, cap $3; G2 не запускалась, нужен новый GO; дальнейший compile repair запрещён. Остановка на REVIEW REQUEST.
