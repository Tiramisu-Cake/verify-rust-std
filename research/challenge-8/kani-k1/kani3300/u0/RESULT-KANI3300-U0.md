# RESULT-KANI3300-U0

Build `51f228c7-615f-4027-8bae-d68fb293e132`, Cloud FAILURE, summary COMPLETE, gate false, Kani exit 1. Компиляция завершилась, восемь строк получены. Gate отклонил результаты с unsupported.
Head `69b3b92fc9965e3e35af4eeff80d02c650745285`. Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, без patch, nightly-2026-10-23.
Request `kani3300-u0-uninit-20261111-01`, SHA-256 `0dbce45f0859d38e56817b53e1861e4d028853418f6826caa73293adfb966056`.
Tooling base `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`, check-tooling PASS. Standard4/jobs1, controls on, inventory off, uninit checks on, timeout 3m.

| Row / harness в `uninit_probe::` | Status | failed/total | Класс | Все failed checks дословно с локацией |
|---|---|---|---|---|
| U1 `pincheck_calibration_uninit_read_u8` | FAILED | 1/31 | unsupported | `Transmuting between types of incompatible layouts.` @ `/workspace/src/library/core/src/mem/mod.rs:1283` |
| U2 `pincheck_calibration_init_read_u8` | FAILED | 1/32 | unsupported | `Transmuting between types of incompatible layouts.` @ `/workspace/src/library/core/src/mem/mod.rs:1283` |
| U3 `raw_uninit_read_sensitivity` | FAILED | 1/47 | unsupported | `Interaction between raw pointers and unions is not yet supported.` @ `/workspace/src/library/core/src/slice/sort/shared/smallsort/verify/uninit_probe.rs:47` |
| U4 `swap_contract_four_positions_u8` | FAILED | 1/454 | unsupported | `Kani does not support memory initialization checks across calls through function pointers. For more information about planned support, see https://github.com/model-checking/kani/issues/3300.` @ `/workspace/src/library/core/src/ops/function.rs:166` |
| U5 `sorted_permutation_insert_tail_u8_n2` | SUCCESS | 0/181 | SUCCESS | — |
| U6 `permutation_merge_u8_n4` | FAILED | 1/243 | unsupported | `Interaction between raw pointers and unions is not yet supported.` @ `/workspace/src/library/core/src/slice/sort/shared/smallsort/verify/uninit_probe.rs:117` |
| U7 `swap_contract_four_positions_u8_function_item` | FAILED | 1/416 | unsupported | `Interaction between raw pointers and unions is not yet supported.` @ `/workspace/src/library/core/src/hint.rs:844` |
| U8 `small_sort_general_with_scratch_u8_n4` | FAILED | 1/515 | unsupported | `Checking memory initialization of type [mem::maybe_uninit::MaybeUninit<u8>; 20] is not supported. Cannot determine layout for a type that contains union of type mem::maybe_uninit::MaybeUninit<u8> as a field.` @ `/workspace/src/library/core/src/slice/sort/shared/smallsort/verify/uninit_probe.rs:177` |

С cd355b0b статусы и классы U1–U6 совпали. Total checks U4 450→454, U5 174→181, U6 235→243, U1–U3 сохранены. U7/U8 новые.
Сравниваются полные пакеты. Помимо Kani/nightly, изменились contracts и helpers core, `assembly` перенесён, `merge::specfix` переименован в `merge::profiles`. Изолированный эффект пина не установлен.
U7 с function item прошёл за прежний fn-pointer blocker и остановился на MaybeUninit внутри `select_unpredictable`; PFC target изменён на локальный wrapper, геометрия и постусловия сохранены.
Первое наблюдаемое препятствие general scratch U8 — создание массива в строке 177 до реального вызова в строке 178. U6 имеет отдельный union output. Порядок summary не использован как порядок исполнения.
Repro-кандидат `scratch-array-layout.rs`, 18 строк, edition 2021, не запускался. Статическая цепочка и ограничения привязки изложены в `REPRO.md`.
В эталоне `/root/kani-src-f046b70644/kani-compiler/src/kani_middle/transform/check_uninit/` array recursion `ty_layout.rs:198` отвергает union в `ty_layout.rs:403`; diagnostic добавляет `ptr_uninit/uninit_visitor.rs:119`.
Все семь failed checks доступны полностью в bounded summary, по одному с локацией, маркеров clipping/truncation нет. Источники сохранены в `build.summary.md` и `build.rows.txt`, identity/status/cost/tooling рядом.
Калибровка uninit-чтения остаётся unsupported, covers после него не устанавливают чувствительность. SUCCESS U5 относится к выбранному bounded пути. TIMEOUT и иных классов отказа нет.
Расход одной сборки $0.1215 из $0.80, резерв снят, Cloud elapsed 524.008s (ledger 9 минут), verifier wall 1:28.94. Repair не потребовался.
Для патча U1 приоритетен array-of-MaybeUninit layout U8, затем отдельные raw-pointer/union пути U6/U7 и transmute U1/U2. Одного устранения fn-pointer ограничения для этих путей недостаточно.
Library scope сохранён, rustfmt PASS. Все восемь строк классифицированы по bounded evidence. Repro остаётся статически обоснованным кандидатом до отдельного запуска.
