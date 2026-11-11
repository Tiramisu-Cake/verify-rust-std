# KANI3300 A2
- Выполнена только A2 по заданию a9ae7b5f6c; Cloud $0.
- Pat сохраняет offset; варианты вложенного enum сравниваются локально, затем смещаются один раз.
- Добавлены nested Pat/enum controls; reverse MU-array transmute и raw_eq закрыты явным Unsupported.
- Ограничение raw_eq распространяется на std array equality при uninit-checks; прежние full-suite goldens не объявлены проходящими.
- Kani: четыре локальных коммита поверх A1, автор Tiramisu-Cake; push Kani не выполнялся.
- 6 новых selectors / 9 harnesses; исходники, diagnostics и ожидаемые counts закреплены в TEST-MANIFEST.json.
- rustfmt, git diff --check, pinned API hashes и статический source audit пройдены.
- Независимое Luna HIGH ревью: REVIEW.md; ожидаемые результаты требуют fork CI координатора.
- Компиляция/clippy, Kani/CBMC/Miri и CI NOT_RUN; proof credit отсутствует.
A2 READY 3dc0227cee87d85bed32678a2209353ebdb9d2fa
