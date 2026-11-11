# RESULT-KANI3300-U4 — COMPLETE; строгая приёмка NOT_MET
Build `6a2c009d-95f5-4cb6-800b-48dde18e2372`: Cloud SUCCESS, summary COMPLETE, diagnostic gate=true, Kani exit1; gate не проверяет ровно один отказ U9.
Exact head `e1ed2374b72bd4be72c283c4fba5c88c7cbe7374`; request `kani3300-u4-uninit-20261111-01`, SHA256 `778b2ef2a1f148dd8c8e3e7b98f3da8cf99c7b48a805ef2cde38a6c9f21cf381`.
Pin `f046b70644e113be0df9c22c2e6ea44a65a57566`, nightly-2026-10-23; patch `46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4`, observed tree `d356238999ab436ddc1dd7ffa845b0db214aa53e`; bindings совпали.
Check-tooling PASS против `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`; standard4/jobs1/3m, controls/uninit on по summary и unchanged lane binding; literal actual argv `-Z uninit-checks` UNKNOWN.
GO: координатор явно снял невыполненный gate «CMP2 native PASS» только для этой сборки; это не утверждение CMP2 PASS.
Основание GO: CMP3 `ddcd43e2-f48e-4b1f-b688-931250adf78e`, RESULT в `/root/verify-rust-std-kani3300-cmp3` @ `5e8bf28b11cac1a061189312caab3cffcfcbdbaa`: тот же production patch, U8 0/550 SUCCESS и into_iter len/next SUCCESS; прямой IndexRange::zero_to(2).len() остаётся failing; причина не доказана.

| Row / harness в `uninit_probe::` | Status | failed/total | covers | Класс | Failed Checks дословно с локацией |
|---|---|---|---|---|---|
| U1 `pincheck_calibration_uninit_read_u8` | FAILED | 1/30 | 3/3 | expected uninit | ``Undefined Behavior: Reading from an uninitialized pointer of type `u8` `` @ `/workspace/src/library/core/src/mem/mod.rs:1283` |
| U2 `pincheck_calibration_init_read_u8` | SUCCESS | 0/31 | 3/3 | calibration SUCCESS | — |
| U6 `permutation_merge_u8_n4` | SUCCESS | 0/229 | 1/1 | regression SUCCESS | — |
| U8 `small_sort_general_with_scratch_u8_n4` | SUCCESS | 0/550 | 1/1 | bounded positive SUCCESS | — |
| U9 `small_sort_general_scratch_unwritten_slot_u8_n4` | FAILED | 2/504 | 6/6 | uninit; exact-one requirement NOT_MET | ``Undefined Behavior: Reading from an uninitialized pointer of type `*const u8` `` @ `/workspace/src/library/core/src/ptr/mod.rs:1769`; ``Undefined Behavior: Reading from an uninitialized pointer of type `u8` `` @ `/workspace/src/library/core/src/ptr/mod.rs:1769` |

U9: все6 covers достигнуты агрегатно, включая нормальный возврат и наблюдения written-byte; однако covers не доказывают отсутствие failing assertion на scratch[3].
Два отказа вместо одного; общий span ptr::read/read_via_copy не связывает их с вызовами scratch[3] (`uninit_probe.rs:198`) или scratch[4] (`:204`). Отсутствие отказа scratch[3] и единственный отказ scratch[4] UNCONFIRMED; не объявлять U9 принятой.
С U2: U1 ожидаемо FAILED и U2/U6 SUCCESS сохранены (31→30, 32→31, 230→229 checks); U8 2/507, covers0/1 → SUCCESS0/550, covers1/1; U9 два array-iterator Unsupported, covers0/6 → два uninit-отказа, covers6/6. Новых Unsupported не сообщено.
U8 даёт Kani-reported bounded SUCCESS проверок sortedness/count и нормального возврата реального general scratch-пути u8/N4 при заявленных uninit-checks. Только normal returns с прежним panic stub; не общий theorem для иных типов/длин, не unwind proof и не независимый B1/B2 credit.
Полнота: три приведённых описания = сумма failed checks3; summary без truncation markers, rows5/5, next_offset=done. Property IDs/columns/call sites и individual cover records недоступны.
`smallsort-brief`: exit1 HTTP404; `native`: exit2 `page-summary: no structured native report`; `native-field`: exit2 `page-native-field: no structured native report`; actual argv и более точная привязка остаются UNKNOWN, raw fallback не использован.
Unreachable checks: U6=4, U8/U9=19; covers U8/U9 достигнуты, это не одно и то же. Library/9 harnesses, patch/pin/toolchain/KT2 не изменены.
Расход $0.1215 из cap$0.80, резерв$0, остаток$0.6785; одна попытка использована, repair не запускался и требует нового GO.
Следующий шаг: отдельно согласовать bounded property/call-site/argv evidence и локализовать лишний pointer-uninit отказ U9, различив scratch[3]/scratch[4]; не ослаблять exact-one/control и не считать зелёный gate приёмкой.
Подробности и SHA receipts: `POST-BUILD-OBSERVATIONS.json`, `EVIDENCE-INDEX.json`, `build.*`; independent proof credit NONE.
KANI3300 U4 ЗАВЕРШЁН — стадия закрыта с blocker, proof acceptance NOT_MET.
