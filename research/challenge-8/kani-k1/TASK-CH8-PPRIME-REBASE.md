# Координатор 2026-11-16 ~00:00Z — общая база P′ вместо 872d для всех CI на Kani 0aac

Это верификация корректности, не security-работа. Отвечай кратко.

## Находка (S1-01k, run 43775527125, attempt 1, failure)

Setup и сборка stock Kani 0aac прошли (setup 349 s, RSS 1.39 GiB). Шаг list упал на компиляции `core`
(cargo exit 101, 9 ошибок), все 23 строки NOT_RUN:

1. 8 × E0599 `no associated function debug_c_like_enum_write_str for fmt::Formatter` (derive(Debug)
   в num/error.rs, intrinsics, io/error.rs, net/*, sync/atomic.rs, `kani_core::kani_lib!(core)`).
   Причина: production std `872d5a4338` (head #752) несёт библиотеку под `nightly-2026-10-22`;
   Kani `0aac16ef62` (и upstream pin `c5e65fdfc3`) — `nightly-2026-10-23`. Upstream subtree update
   **#745** (`2887c32d39`, toolchain nightly-2026-10-23) в #752 head не входит.
   **Любой** прогон std 872d + Kani 0aac падает так же (B-01 census отменён по той же причине).
2. 1 × E0369 в нашем коде: `sorting_entry_controls.rs:32` — `post::<u8, KeyLess<u8>>>(before, &v)`
   (лишний `>`), коммит S `75a4d1ea6e`.

Evidence упаковка: в artifact попал `list/target/` (~25 MB build-каталог) — исключить.

## Общая база P′

`c5ff36ff433692140605891f646043f991db05de` (tree `1302063846873aa300f8bac64fe09e8a3ed1280f`) =
merge #752 head `872d5a4338` + upstream main `6079edcda31accaf396b883f3f38e2581d0710d7`, без
конфликтов (GitHub тоже считает #752 mergeable). Toolchain nightly-2026-10-23, tool_config pin
upstream `c5e65fdfc3`. Опубликован: `Tiramisu-Cake/verify-rust-std` ветка
`experiment/ch8-pprime-20261116`. Production #752 не меняется; P′ — только база кампаний на 0aac.

Перенос S на P′: единственный конфликт — `tool_config/kani-version.toml` (S ставит 0aac) —
разрешать в пользу S (0aac).

## Что делает каждый (одна стадия; без push/CI/ledger; без локальных cargo/rustc/Kani/CBMC)

- **13:** S′ = cherry-pick `1313f7c329`, `75a4d1ea6e` на P′ (конфликт pin → 0aac), исправить
  E0369 (`post::<u8, KeyLess<u8>>(before, &v)`), прочитать весь свой diff на подобные синтаксические
  опечатки (компилятор их больше не покажет до следующего прогона). Новый kani-host control: только
  `std_sha`/tree и исключение `target/` из upload; 23 строки/runner/caps без изменений. Review.
  Записать в `kani3300/ch8-s1/kani-host-pprime/`. Последней строкой `READY <S′> <control> <g0>`.
- **11:** profiles source (`872d..b5cf722e20`) на P′ cherry-pick, новый OFF control с новым
  source sha (и тем же исключением `target/` из upload, если upload из того же runner). Review.
  `kani3300/ch8-profiles/off-ci-pprime/`. `READY <source> <control> <g0>`.
- **14:** C controls — завершить текущую стадию, но базой std взять P′ (cherry-pick на P′ до handoff);
  CI-REQUEST ссылается на P′-based sha. B census пересадить на P′ — отдельной следующей стадией.
- **15:** PR-02 reset не затронут (только Kani). S2 пакет пересаживается на S′ позже.
