# #5172 fixup — worker11

Worktree: `/root/kani-5172-fixup-w11`  
Ветка: `fix/kani-uninit-unresolved-call-v3-fixup-w11`  
Коммит: `cb0efdbe5bba20635561e5c663cd9f6c3c767578`  
Родитель: `6fe484b30043b3696b5f1ccc4bea0e42891ad012`  
Автор: `Tiramisu-Cake <igkharin@gmail.com>`.

- `resolve_call` принимает `tcx` и проверяет тело через `checked_body(tcx, instance)`, как требует `kani_middle/mod.rs`. Перенесены соответствующие изменения из PR-01 `d82752c8bc878398e672bffaa631ca6a28430acc`, включая передачу `tcx` из points-to анализа и локального visitor. Проверка явных tail calls выполняется перед преобразованием пользовательского MIR.
- Комментарии описывают проверки вызовов, перенос memory initialization state и содержимое тестов. Удалены внутренние формулировки про generated ABI, slot pairing, seeds и границы proof coverage. Перенесены правки комментариев четырёх тестов из PR-01; комментарий generated-positive дополнительно сокращён.
- Диагностика изменена: `Unsupported {kind} during memory initialization checks. For more information, see https://github.com/model-checking/kani/issues/3300.` Уточнены сообщения о недоступном MIR, LLVM intrinsic calls, переносе memory initialization state через compiler-generated shims и ошибке разрешения function item. Обновлены 18 `.expected` в `unresolved-calls` и общий `delayed-ub-unsupported-call/expected`.

Статическая проверка: PASS. `git diff --check` прошёл. Сравнение с родителем и PR-01 проверило все 41 изменённый файл: 4 compiler-файла, 18 исходников тестов с изменениями только комментариев, 19 файлов ожидаемого текста. В compiler-коде допустимая дельта ограничена переносом `checked_body`/`tcx` и строками диагностики; пробелы, комментарии и завершающие запятые нормализованы при сравнении. Код, флаги и assertions тестов сохранены; статусы, проверки и итоговые результаты в expected сохранены.

Компиляция, rustfmt, Kani/CBMC и runtime-тесты не запускались по границам задания. Результат — статически проверенный кандидат; успешный прогон новой головы не установлен. Push, CI, публикации и ledger не выполнялись. COMMENT.md — только черновик комментария.
