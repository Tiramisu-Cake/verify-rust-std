# Handoff — S1-05 intake

Весь новый пакет расположен в `run-43864841077/`; исходные S1-04/S1-05 preparation и ledger не изменены. Вход g0 43c470084c. Получены14 original compact artifacts (payload SHA/entry SHA в PROVENANCE.json), exact stock/properties projections, sanitized receipt projections и same-run GitHub metadata. GitHub ZIP digest сохранён как metadata; extracted ZIP digest отдельно не проверен. Самопроверка entries подтверждает целостность payload, не proof acceptance.

Replay intake: `PYTHONDONTWRITEBYTECODE=1 python3 intake.py` из любой cwd. Требует существующий immutable `/root/kani-ch8-s1-05-w13` HEAD8860d38558 и читает committed artifacts; verifier не запускает. `runner-collected.json` — результат исходного collect.py, `collected.json` добавляет raw per-row stock observations, inventory coverage, missing fields, original exits и measurements. `accept/` — отдельная офлайн-приёмка w11/policy. Не смешивать её статусы с source SUCCESS/FAILURE.

Fix candidate `/root/kani-ch8-s1-05-intake-fix-w13`, branch `uninit-ci/ch8-s1-05-intake-fix-w13`, SHA `b25dd39a46ba90b167500997d546a5f2f5bd8f3b`, parent `40b5d9cf48900ff1e227e1fbba24cb5b2edbf8d5`. `fix/control-fix.patch` — exact delta относительно executed8860; `fix/control.bundle` переносит полный candidate с prerequisite40b5d9. `fix/CI-REQUEST.json`, VALIDATION.json, DEFECT.md и REVIEW.md содержат pins/тесты/ограничения. Author Tiramisu-Cake <igkharin@gmail.com>, [skip ci]. CI-REQUEST status унаследован из старого пакета и сам по себе не разрешает dispatch.

Следующий разрешённый этап должен отдельно решить публикацию/CI. Если назначен новый run, ожидается сохранение полного inventory и явных unknown sites, но **не** автоматический PASS: отсутствие координат всё ещё блокирует completeness. Диагностические записи позволят определить exact rejected location без raw-log dump. Затем нужен source/export binding недостающих sites и прежняя офлайн-приёмка. Текущие incomplete группы нельзя восстановить из stock counters/ID, ordinal или прошлых runs; полные группы переданы отдельно.

В этой стадии: без push/CI/публикаций/ledger, без локальных cargo/rustc/Kani/CBMC и без полных raw logs. Все outputs — observations/static/synthetic; independent proof credit NONE.

Приёмка replay PASS:0 qualified /35 pending;3 exact negative observations. Все41 required covers SAT-bound;4 required-success messages exact-bound. Остальные gates и exact IDs/sites — в accept/ACCEPT.json.
