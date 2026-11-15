# TASK — worker15: разбор A1-R1 и пакет A1-R3 (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

## Факты (координатор, из bounded receipts; полные логи не читались)

A1-R1 run 43772128212 (control trigger `a47d28da27`, pkg `bf81a1f14f`): все 8 matrix rows FAILURE за ~4 мин
каждая. Пример `stable_freeze_u64_n32`: `kani verify-std ... -Z uninit-checks --no-assert-contracts --harness
slice::sort::shared::smallsort::verify::wave0_a1::stable_freeze_u64_n32 --exact --jobs 1 ...`, cwd
`_temp/ch8-a1-std`, env `RUSTFLAGS=--cfg kani_smallsort_controls`, exit 1 через 20.6 s, stderr:
`error: could not compile core (lib) due to 8652 previous errors; 2 warnings emitted`.
std base `70ba5befc6` (tree `84ab170ccd`), nightly-2026-10-23 = toolchain Kani SEL1 `14bc57fdb9`;
SEL1 replay 43751703000 на той же std базе компилировался, так что это не несовпадение toolchain.
`stdout.log` (10 696 252 B, sha256 `436210c7…b71c`) удалён metadata cap артефакта (`bound-artifacts.json`
`TRUNCATED_REMOVED`) — первых ошибок нет. Ledger: A1 2 из 3 использованы; R3 — последний резерв.

Отдельно (для сравнения): S1 на std 872d + Kani 0aac упал из-за отсутствия upstream #745
(Formatter::debug_c_like_enum_write_str) — см. [TASK-CH8-PPRIME-REBASE.md](TASK-CH8-PPRIME-REBASE.md).
К A1 это, вероятно, не относится (там toolchain совпадает), но проверь.

## Что сделать

1. Статически найти причину 8652 ошибок: сравни R1 invocation/env/overlay с успешным SEL1 replay
   (RUSTFLAGS vs флаги, которые kani-driver сам передаёт cargo для verify-std; cfg
   `kani_smallsort_controls` и что он включает на 70ba5befc6 + твоём overlay; `-Z uninit-checks`;
   `--target-dir`; std_patch overlay). Если причина не устанавливается однозначно — перечисли
   гипотезы с различающим дешёвым шагом.
2. Исправить runner: сохранять bounded head+tail stdout/stderr (например 64 KiB каждый) **до**
   применения artifact metadata cap, чтобы compile-ошибки не терялись; target/ не выгружать.
3. Пакет A1-R3 = исправление причины + #5151 fixture (E0433 edition/`use core::`, из R2) +
   ранний fail-fast: если первая строка падает на компиляции core, остальные строки NOT_RUN
   без повторной сборки. Порядок строк — N32 первым, как раньше. Review.
4. g0 `kani3300/w0-a1/r3/`: TRIAGE.md, CI-REQUEST, REVIEW, HANDOFF. Коммиты `[skip ci]`, author
   `Tiramisu-Cake <igkharin@gmail.com>` в команде. Последней строкой
   `READY <pkg-sha> <g0-sha>` или `STOP <причина>`.

## Ограничения

Без push/CI/публикаций/ledger. Без локальных cargo/rustc/Kani/CBMC. Полные raw logs не читать.
