# U1T → U3: диагностики и точная граница

Основание: [AMEND-U1T.md](AMEND-U1T.md), сообщение координатора; build `ff0988c7-d2f2-4872-b4ea-be581d9de02f`.
Это дополнение к историческому INPUT-U1T, а не пересмотр старого evidence/ledger.

Координатор сообщает: offsets 0,1,2,3,5 имеют Kani VERIFICATION FAILED и compiletest golden mismatch.
Это исключает overall SUCCESS этих harness по сообщению координатора, но не доказывает FAILURE нужного uninit property.
Для overwrite дополнительно сообщён unsupported foreign function(1); для обеих overlap — описание internal error:
entered unreachable code. Описание само по себе не устанавливает ни FAILURE данного свойства, ни его source binding.

## Выполненные изменения

Пять golden review-{overwrite-copy,overlap-copy,repeat-local,reset-zst,argument-return} переведены с
`<harness>.safety_check` на `Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type ...`.
Типы `[u8; 2]`, `u8`, `u64`, `u64`, `u16` сохранены. Overlap сохраняет обе harness, Checking harness для каждой,
Failed Checks / VERIFICATION:- FAILED и Complete 0/2/2. Все пять selectors + review-positive включены в manifest.
Goldens — требования к будущему native run; это не новое evidence прохождения. Expected matcher ищет строки в выводе;
для overlap при разборе результата всё равно нужны собственные bounded статусы/Failed Checks обеих harness.
Padded-manually-drop снят с manifest для лимита 20 и указан NOT_RUN. Все 7 Rust sources U1T неизменны.

## Статическая трассировка (независимый explorer Luna HIGH)

Исследован Kani `8bfb7c7c908fe58668214089a0fc7d1b5ccfe378`; новая версия меняет только 5 golden.
Baseline U1 `546bcf30379b9b2894f94b1305d5277cc5b4574c`; Kani rust-toolchain: nightly-2026-10-23.

- Overlap fixture `tests/expected/uninit/maybe-uninit-review-overlap-copy/main.rs:13,23` вызывает ptr::copy,
  затем `:14,24` читает через assume_init. В library/core U1T checkout @51971120af copy ведёт в intrinsic
  (`library/core/src/ptr/mod.rs:658–674`). Совпадение этого исходника с native sysroot отдельно не установлено.
- Kani `kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs:1125–1178` кодирует Copy как memmove.
  `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs:614–642` добавляет CopyInitStateModel;
  `library/kani_core/src/mem_init.rs:105–145,361–390` содержит shadow copy. В этих участках нет unreachable!.
  Это callpath возможной инструментированной операции, не привязка observed property к её source.
- Определение переопределённого unreachable! в Kani `library/std/src/lib.rs:218–244` формирует этот текст через
  kani::panic; panic pathway — `library/kani_core/src/lib.rs:548–558`. Найден механизм сообщения, но НЕ invocation.
  Конкретный runtime file:line и причина observed overlap сообщения остаются UNKNOWN; выбирать std/patch нельзя.
- Overwrite fixture `main.rs:12` делает copy_nonoverlapping, `:13` — assume_init. Счётчик foreign function(1)
  агрегируется в `kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs:764–781`; места unsupported foreign
  calls регистрируются в `.../codegen/foreign_function.rs:231–261`. Имя callee и callsite из счётчика не следуют.
  Конкретная foreign function и её достижимость UNKNOWN; утверждать, что она недостижима, оснований нет.

Ни один production fix по догадке не внесён. Положительные overlap_copy_*_written_slot уже есть в review-positive,
сохранены в пакете; их прошлый PASS — сообщение U1T, не proof нужного отрицательного сценария.

## Координатор, вопрос — dispatch заблокирован

Пункт 3 AMEND прямо требует вопрос, если source установить нельзя. Через async запрос координатору нужны:
1. Для каждой overlap harness: статус свойства internal error: entered unreachable code + source_location/callsite
   (и call stack, если присутствует); отдельно её Failed Checks для uninit.
2. Для overwrite: foreign callee/symbol и callsite/source_location; статус/reachability, если присутствует.
Достаточны bounded фрагменты summary, которыми располагает координатор, или путь к сохранённой bounded-выборке.
Explorer сообщает, что native pages 0/1 по-прежнему отклоняются: one native record exceeds the bounded page size.
Raw logs/archives, прямой GCS и обход reader не использованы. Пакет остаётся BLOCKED_MISSING_DIAGNOSTIC_BINDING,
пока точные данные не позволят выполнить пункты 3–4 либо координатор явно не изменит эту границу.
