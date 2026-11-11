# KANI3300 B2 — probes для CI координатора
- Scope: только TASK-KANI3300-B2.md, research input 230fa9aa656dd90503390019a6c0d153ef93520b.
- Восстановлены десять historical cases с исходными формами и default union repr: removed-cases.md.
- Подготовлены 25 самостоятельных бинарей, Cargo без зависимостей, edition 2021, pin nightly-2026-10-23.
- Copy/assignment/Call(address-taken)/forget/reinit/field/union/MaybeUninit; original bytes читаются через pre-move raw pointer.
- EXPECTATIONS.md отделяет Reference/MIR-прогноз от будущих Miri outcomes и отмечает неоднозначное lowering.
- Независимое review: ожидается; результат будет записан перед публикацией.
- Локальных cargo/rustc/Kani/CBMC/Miri, Builds/dispatch/Actions не было; Cloud $0, Kani без изменений.
- Компиляция, фактический MIR/Miri, источник ошибки и proof credit НЕ установлены.
- Следующая стадия: exact-SHA MIR и Miri в fork CI координатора; в B2 не запускается.
