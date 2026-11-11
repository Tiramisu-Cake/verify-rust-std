# RESULT-KANI3300-U4B — диагностика выполнена
Build `6d1690f4-c07e-4af9-a858-d97534c4db29`: Cloud SUCCESS, summary COMPLETE, gate=true, Kani exit1; одна попытка.
Head `d3e56afbf577da0d94e82406d10e9b77c2492900`; request `kani3300-u4b-uninit-20261111-01`, SHA256 `53a2f3ac1453787fd74f190d838352f9a819676619c66f456c6dad8c197bd1ff`.
Pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; patch `46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4`; observed tree `d356238999ab436ddc1dd7ffa845b0db214aa53e`; bindings совпали, check-tooling PASS против KT2.
Standard4/jobs1/3m, controls/uninit on по summary и неизменённому tooling; literal actual argv UNKNOWN.

| Row / harness в `uninit_probe::` | Status | failed/total | covers | Failed Checks с локацией |
|---|---|---|---|---|
| U9a `small_sort_general_scratch_written_slot_u8_n4` | SUCCESS | 0/492 | 3/3 | — |
| U9b `small_sort_general_scratch_unwritten_slot_only_u8_n4` | FAILED | 2/503 | 4/4 | ``Undefined Behavior: Reading from an uninitialized pointer of type `*const u8` ``; ``Undefined Behavior: Reading from an uninitialized pointer of type `u8` `` — оба @ `/workspace/src/library/core/src/ptr/mod.rs:1769` |
| U8 `small_sort_general_with_scratch_u8_n4` | SUCCESS | 0/572 | 1/1 | — |
| U1 `pincheck_calibration_uninit_read_u8` | FAILED | 1/30 | 3/3 | ``Undefined Behavior: Reading from an uninitialized pointer of type `u8` `` @ `/workspace/src/library/core/src/mem/mod.rs:1283` |

U9a SUCCESS: записанный scratch[3] не даёт ложного uninit-отказа в этом N4 harness. U9b воспроизводит оба отказа U9: чтение scratch[4] вызывает две точки инструментирования (pointer и byte); это вывод split-harness диагностики, не независимая MIR/call-site привязка.
Все covers достигнуты агрегатно: 3/3, 4/4, 1/1, 3/3; три описания равны сумме failures3, rows4/4, next_offset=done. Unreachable checks U9a/U9b/U8=19, U1=0; новых Unsupported не сообщено.
Scope: реальный u8/N4 general scratch путь, normal returns с прежним panic stub; не общий theorem/ unwind proof, independent B1/B2 credit NONE. Старые 9 harness, production patch и tooling сохранены.
Brief exit1 HTTP404; разрешённые bounded summary/rows доступны. Property IDs/columns/call sites, individual cover records и literal actual argv остаются UNKNOWN; raw fallback не использован.
Расход $0.1485 из cap$0.60; резерв$0, неиспользовано$0.4515; повторов не было и эта стадия новых Builds не разрешает.
KANI3300 U4B ЗАВЕРШЁН
