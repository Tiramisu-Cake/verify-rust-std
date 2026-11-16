# U-03 — сохранённый результат

Источник фактов о прогонах: поручение координатора `TASK-CH8-PR02-FINAL-W11.md`, g0 input `dee2b6c723b06c97b37256b650bd0a380674b4f9`. В этой стадии результаты CI независимо не перечитывались; это task-reported qualification, не новый proof credit.

- Run: https://github.com/Tiramisu-Cake/kani/actions/runs/43783429976
- Package: `80d0d98529445088db2fd2941fe9370ba6c0eaa6`.
- Source pin: `f7e89f1942fa6f671f20ec45fde98d9d736dc122`.
- PR-02 + fix: fmt/build/clippy OK; compiler units 66 passed / 0 failed; expected uninit 56 / 0 (2 ignored); function-contract 134 / 0 (4 ignored).
- Весь выбранный `script-based-pre` autoharness набор: 54 passed / 1 failed.
- Новые `autoharness_entry_reset_*`: 6 passed / 1 failed. `autoharness_entry_reset_uninit_read` завершился verification SUCCESS, exit 0 вместо ожидаемого UB: чтение padding-байта `#[repr(C)]` struct Kani не считает uninit. Это дефект фикстуры; данный прогон не устанавливает обнаружение такого чтения.
- Matched old PR-02 `932fb8395a58f8c86c0d702ba2cae835823b2962`: seed_only / argument_seed / contract_seed дали ожидаемый fatal `immutable masks: reset is absent from this model`; no_seed завершился, как ожидалось.
- Переданный результат U-01 arm B: SEL1+fix, исходный #4854 autoharness SUCCESS, 154 passed / 0 failed. Это другой source context, не прогон финального PR-02.

Решение координатора: удалить `uninit_read`; сохранить шесть прошедших фикстур байт-в-байт. Обнаружение uninit-read покрыто существующим uninit-набором. Новый CI не требуется при идентичном compiler diff и оставшихся файлах. Не утверждаем, что полный набор был повторно запущен или прошёл на финальном SHA.

Стадия выполнена без push, CI, публикаций, ledger и локальных cargo/rustc/Kani/CBMC. Исторические результаты и записи не изменялись.
