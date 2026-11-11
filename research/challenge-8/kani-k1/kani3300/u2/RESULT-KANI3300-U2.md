# RESULT-KANI3300-U2

Build `6a2f4260-c343-427f-a6ef-6ed0bce50b7c`: Cloud FAILURE, summary COMPLETE, gate false, Kani exit 1. Приёмка U8/U9 НЕ выполнена.
Head `108551d92b7754d5366ec3b59bd0b652510adcef`; Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, nightly-2026-10-23.
Request `kani3300-u2-uninit-20261111-01`, SHA-256 `d025202d57d3c271f125ca9ae8dda40b677d2bb591cad6b43307c5222f67bcb3`.
Patch `306851ac5dd4f28a11778dfc49e878a5bb62fd7c35a2ad7ad0419053b9504467`; applied tree `b9c36ac5ed550e39d26e1d1d77000052e62a9bb4`; все bindings совпали.
Tooling `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`: check-tooling PASS; standard4/jobs1, controls on, inventory off, timeout 3m.
Summary сообщает uninit checks on; фактический argv bounded summary/rows не раскрывают — literal `-Z uninit-checks` в argv UNCONFIRMED; generated args не proof.

| Row / harness в `uninit_probe::` | Status | failed/total | covers | Класс | Все failed checks дословно с локацией |
|---|---|---|---|---|---|
| U1 `pincheck_calibration_uninit_read_u8` | FAILED | 1/31 | 3/3 | expected uninit-FAILED | ``Undefined Behavior: Reading from an uninitialized pointer of type `u8``` @ `/workspace/src/library/core/src/mem/mod.rs:1283` |
| U2 `pincheck_calibration_init_read_u8` | SUCCESS | 0/32 | 3/3 | SUCCESS | — |
| U3 `raw_uninit_read_sensitivity` | FAILED | 1/57 | 3/3 | expected uninit-FAILED | ``Undefined Behavior: Reading from an uninitialized pointer of type `*const u8``` @ `/workspace/src/library/core/src/ptr/mod.rs:2175` |
| U4 `swap_contract_four_positions_u8` | FAILED | 1/438 | 2/5 | unsupported | ``Kani does not support memory initialization checks across calls through function pointers. For more information about planned support, see https://github.com/model-checking/kani/issues/3300.`` @ `/workspace/src/library/core/src/ops/function.rs:166` |
| U5 `sorted_permutation_insert_tail_u8_n2` | SUCCESS | 0/178 | 1/1 | SUCCESS | — |
| U6 `permutation_merge_u8_n4` | SUCCESS | 0/230 | 1/1 | SUCCESS | — |
| U7 `swap_contract_four_positions_u8_function_item` | FAILED | 3/400 | 2/5 | unsupported + instrumentation failures | ``Check that *var_9 is assignable`` @ `library/kani_core/src/mem_init.rs:382`; ``Kani does not support reasoning about memory initialization of intrinsic `Unimplemented { name: "select_unpredictable", issue_link: "https://github.com/model-checking/kani/issues/new/choose" }`.`` @ `/workspace/src/library/core/src/hint.rs:871`; ``Check that *var_17 is assignable`` @ `library/kani_core/src/mem_init.rs:404` |
| U8 `small_sort_general_with_scratch_u8_n4` | FAILED | 2/507 | 0/1 | unsupported | ``Transmuting between types of incompatible layouts.`` @ `/workspace/src/library/core/src/array/iter.rs:77`; ``Kani does not support this assignment to MaybeUninit storage.`` @ `/workspace/src/library/core/src/array/iter.rs:77` |
| U9 `small_sort_general_scratch_unwritten_slot_u8_n4` | FAILED | 2/463 | 0/6 | unsupported; U9 acceptance blocked | ``Transmuting between types of incompatible layouts.`` @ `/workspace/src/library/core/src/array/iter.rs:77`; ``Kani does not support this assignment to MaybeUninit storage.`` @ `/workspace/src/library/core/src/array/iter.rs:77` |

С U0: U1 incompatible-layout unsupported → ожидаемый uninit; U2 → SUCCESS; U3 union unsupported → ожидаемый uninit; U4 прежний fn-pointer unsupported (454→438 checks); U5 SUCCESS (181→178); U6 union unsupported → SUCCESS (243→230); U7 union blocker → intrinsic select_unpredictable + два assignable-отказа (416→400); U8 array-layout blocker → array iterator transmute/storage blocker (515→507). U9 новая.
U9: НЕ ровно один отказ, а два unsupported в array/iter.rs:77; uninit-отказа на scratch[4] нет. Отказа на строке scratch[3] не сообщено, но успешное чтение НЕ подтверждено; covers scratch[3] НЕ достигнуты (всего 0/6). Критерий координатора не выполнен.
Статическая трассировка: smallsort.rs:267 создаёт array iterator для двух offsets; array/iter.rs:77 превращает входной массив в [MaybeUninit<T>; N]. Это исходный контекст blocker, не independently established MIR binding.
U7: intrinsic `Unimplemented { name: "select_unpredictable", issue_link: "https://github.com/model-checking/kani/issues/new/choose" }` @ hint.rs:871; оба дополнительных assignable-отказа сохранены в таблице и не объявлены дефектом std.
U8/U9 не доказали корректность general scratch-пути при uninit-checks; нормальный возврат не покрыт. U5/U6 SUCCESS ограничены их u8/N2 и u8/N4 harness и normal returns из-за panic stub. Общий theorem не закрыт.
Bounded summary/rows содержат все 10 failed checks с локациями; их число совпало с failed/total, clipping/truncation нет. TIMEOUT нет; подробности в check-report.json и build.*.
Расход $0.1215 из $0.80, резерв снят, остаток $0.6785; Cloud elapsed 515.240s (ledger 9 минут), verifier wall 1:52.63. Повтор: $0.1215 + $0.7695 = $0.8910 > cap; repair не запускался.
Следующий шаг: отдельный разрешённый tool-пакет для array-iterator transmute/storage и открытых U7 ограничений, затем повтор U8/U9. Следующий core-пакет по плану — u64 N4 через Stable trait entry с function item, затем N8/sort4.
Library/patch/pin/toolchain/tooling после review не изменены; исходная rustfmt-проверка PASS, scope сохранён. Стадия закрыта с зафиксированным blocker; proof acceptance не заявлена.
