# REALCONTRACTSTWO — итог G1
Build `6ba92a58-0136-490d-a553-4649e9ce254d`, source `15703f81d243be38e04c13c27b3e5789fec92e01`, owner `k1-network`; Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`.
Summary COMPLETE, Cloud Build FAILURE, gate/expectations false, Kani exit 1; шесть SUCCESS, ожидаемый negative FAILED и sort4 FAILED.
Check-tooling PASS: pool, source identity, все lane paths и шесть SHA-256 против `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; request SHA-256 `49e677cea73efca3d400f80ff3d58262e5225d67ea9d423eed9280d3d136401d`.
Точные новые атрибуты (свёрнуты только пробелы/переносы; первая строка — insert_tail, вторая — sort4_stable; без ensures):
```rust
#[safety::requires( begin < tail && insert_tail_contract_len(begin, tail) > 1 && crate::ub_checks::can_dereference(ptr::slice_from_raw_parts( begin, insert_tail_contract_len(begin, tail), )) && crate::ub_checks::can_write(ptr::slice_from_raw_parts_mut( begin, insert_tail_contract_len(begin, tail), )) )] #[cfg_attr( kani, crate::kani::modifies(ptr::slice_from_raw_parts_mut(begin, insert_tail_contract_len(begin, tail))) )]
#[safety::requires( crate::ub_checks::can_dereference(ptr::slice_from_raw_parts(v_base, 4)) && crate::ub_checks::can_write(ptr::slice_from_raw_parts_mut(dst, 4)) && sort4_contract_regions_disjoint(v_base, dst) )] #[cfg_attr(kani, crate::kani::modifies(ptr::slice_from_raw_parts_mut(dst, 4)))]
```
Определения cfg(kani)-helper и контекст: [PREBUILD](PREBUILD-REALCONTRACTSTWO.md); length=0 для неверной геометрии, иначе размер begin..=tail; sort4 проверяет непересечение четырёх элементов. Runtime-тела/сигнатуры сохранены, у sort4 нет Freeze-bound.

| Корень verify:: | Статус | Время, с | Failed/total | Covers |
| --- | --- | --- | --- | --- |
| realcontracts::swap_safety_u8_backing9 | SUCCESS | 17.355093 | 0/219 | 6/6 |
| realcontracts::swap_safety_u8_backing13 | SUCCESS | 17.583559 | 0/219 | 6/6 |
| realcontracts::unstable_network_safety_u8_n9_stubbed | SUCCESS | 11.660206 | 0/383 | 1/3 |
| realcontracts::unstable_network_safety_u8_n13_stubbed | SUCCESS | 13.978799 | 0/383 | 1/3 |
| realcontracts::insert_tail_safety_u64_tail1_to4_backing5 | SUCCESS | 34.020428 | 0/219 | 7/7 |
| realcontracts::rejects_insert_tail_equal_begin_u64 | FAILED | 0.20505936 | 1/205 | 1/3 |
| realcontracts::sort4_safety_u64 | FAILED | 14.53286 | 1/271 | 2/3 |
| assembly::sorted_permutation_insert_tail_u8_n2 | SUCCESS | 0.31345087 | 0/106 | 1/1 |

Negative: единственный failed check — `begin < tail && insert_tail_contract_len(begin, tail) > 1 &&` в smallsort.rs:582; ожидаемый requires подтверждён.
Sort4: единственный failed check — `unwinding assertion loop 0`, `<builtin-library-memcmp>:25`; PFC не доказан. Bounded log-grep подтверждает строки 2729–2730; caller этим не установлен.
Совпали обе пары: swap_safety_u8_backing9 ↔ unstable_network_safety_u8_n9_stubbed, backing13 ↔ n13_stubbed: T=u8, backing=N, один function-item arbitrary_less::<u8>, полный вход и произвольные позиции PFC покрывают все 25/45 call-site. Обе стороны каждой пары SUCCESS: композиция теперь ограниченно подтверждена именно на этих доменах.
Consumer covers 1/3: по исходнику callback не исполняется после stub swap, insertion при offset==len не итерирует; выполнен return cover, два callback covers недостижимы. Это интерпретация исходника и счётчиков, не отдельный универсальный proof.
Insert_tail: u64 backing5, tail1..4, произвольные решения comparator, 7/7 covers и frame после tail; sorted-prefix premise не требуется для safety. Ordinary u8 N2 исполнил настоящее тело и подтвердил sorted permutation своим strict comparator; это отдельный домен, без stub.
В ordinary-кандидаты переносим safety/modifies и соответствующие bounded PFC для stateless u8 swap N9/N13 и u64 insert_tail в указанном backing5; перенос композиции на другие backing/F/T требует совпадающего доказанного домена. Sort4-summary пока переносить нельзя.
Пределы: нет ordering ensures, универсального callback-frame, generic/Drop/ZST/panic proof; uninit/value-validity flags выключены. Covers/unreachable не добавляют proof-credit.
Whole verify wall 3:11.46, max RSS 1748140 KiB; sampled CBMC peak 1.24 GiB у insert_tail, OOM scan none_seen (не доказательство запаса RAM).
Стоимость G1 по bounded k1g budget: `1 0.1485 0.0000`; свой spent $0.1485 <= $3, резерв 0; одна primary build, compile-repair не использован, G2 не запускался.
Дальше только с новым заданием/GO: локализовать memcmp (гипотеза по исходнику: src==before сравнивает 32 байта при unwind16), согласовать целевой повтор sort4. TIMEOUT не было; разбиение insert_tail не требуется.
После G1 изменены только отчёты/ledger; проверенные library/request/tooling сохранены. Передача на review, без новой сборки.
