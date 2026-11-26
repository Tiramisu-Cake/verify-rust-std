# Проверка двух upstream-issue перед публикацией · минимальный прогон

Задание для **w11**, новая короткая стадия. Владелец разрешил один дешёвый прогон перед публикацией двух issue. Нужно точно воспроизвести их тексты, вплоть до файлов и команд. Черновики:
- `/root/smallsort-pr-drafts/ISSUE-KANI-BOOL-ORDER-DRAFT.md`
- `/root/smallsort-pr-drafts/ISSUE-KANI-VV-ARRAY-ELEM-CAST-DRAFT.md`

Основание — run 45886041869, пробы в фазе A пакета валидности.

## Что запустить

Один job `ubuntu-24.04` в fork `Tiramisu-Cake/kani`. Ограничение — 45 мин на весь job.

1. Сборка Kani — **stock upstream `main` 8c6dba5935e8b37a905145c57572d1b67489bae2**:
   - собственный `rust-toolchain.toml` (nightly-2026-11-23), без подмены toolchain;
   - submodules;
   - штатная установка зависимостей и `cargo build-dev`, как в фазе 0 пакета валидности, только без замены toolchain.
2. Файлы для запуска:
   - `bool_order.rs` и `cast.rs` — **побайтно** блоки кода из черновиков;
   - сохрани их SHA-256 и сверь с текстом черновика скриптом.
3. Команды, каждая отдельным процессом. Захвати полный stdout и stderr: они маленькие, но всё равно ограничь размер, например 1 MiB на поток. Запиши exit code.
   - `kani bool_order.rs --harness bool_order_probe --exact` — ожидается `VERIFICATION:- FAILED`, единственный failed check `bool_order_probe.assertion.1`;
   - `kani bool_order.rs --harness bool_order_u8_control --exact` — ожидается `SUCCESSFUL`;
   - `kani cast.rs -Z valid-value-checks --harness array_elem_cast_nonzero --exact` — ожидается FAILED, ровно одно `unsupported_construct` с текстом ``Kani currently doesn't support checking validity of `mutable cast` for `*mut [std::num::NonZero<u8>; 4]` ``, cover UNREACHABLE;
   - `kani cast.rs -Z valid-value-checks --harness array_elem_cast_u8_control --exact` — SUCCESSFUL;
   - `kani cast.rs --harness array_elem_cast_nonzero --exact` (без флага) — SUCCESSFUL;
   - `kani bool_order.rs --harness bool_order_probe --exact --cbmc-args --verbosity 9`, только для поиска строки `warning: ignoring`. Опубликуй число таких строк и первые три целиком, но не весь лог.

   Лишних флагов не добавляй: ни `--unwind`, ни object-bits.
4. Артефакт: `SUMMARY.md` с таблицей «команда → exit, terminal, failed checks, ожидание MATCH/MISMATCH», полные stdout пяти основных команд, сведения о версиях (`kani --version`, `cbmc --version`, rustc).

## Гейт и процесс

- Отдельная независимая Actions variable `CH8_ISSUE_REPRO_TRIGGER_TREE`. Гейт как в прежних пакетах: fork, событие push на `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, tree равен переменной, единственный родитель `467af9cb8dba0e3be78a8d7d07672a1943c4806b`.
- Control на ветке `work/issue-repro-control-w11` в отдельном worktree. Workflow минимальный, секреты и токены не используются.
- Локально: YAML, `bash -n`, сверка SHA файлов с черновиками. Cargo, rustc, Kani, CBMC, CI, push и Actions variables не трогать.
- Коммиты через `git -c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com`, с `[skip ci]` (кроме будущего trigger, его создаёт координатор), без знака решётки перед цифрой.
- Сдай `issue-repro-20261126/HANDOFF.md` в g0: control commit/tree, локальный review-trigger, значение переменной, SHA файлов. Статус `READY_FOR_REVIEW`. Остановись.
