# Решение координатора по ревью q-пилота (2026-11-21)

Ревью `PILOT-REVIEW.md` (9a4f2af637): CHANGES_REQUIRED. Сторона std в целом верна; почти все замечания — к runner: он сам проверяет роли, features, режимы Check/Replace, compile marker, домен q и при этом ошибается (WRONG_FEATURE_SET на всех корнях, роли Check-assume как обязательные properties, конфликт FAILURE/SUCCESS у P-5a, обход compile cap, общий target dir, потеря exit на malformed export, смешанные границы времени).

Решение: **лёгкая дорожка должна быть действительно лёгкой.** Runner — это сбор сырых наблюдений, а не приёмка. Вся интерпретация (роли, covers, режимы, контроли, q-домен провайдеров) — офлайн после запуска, отдельной стадией по зафиксированному чек-листу.

## Runner (control)

Оставить: exact argv из request (без произвольных аргументов), сверку std/tool/control SHA и trees, чистоту checkout (включая untracked), по одному процессу на корень, child ≤600 с через существующий supervise (reap/cleanup), отдельный per-root `--target-dir`/temp если поддерживается пином (иначе зафиксировать и чистить фактический каталог), caps stdout 16 MiB / stderr 1 MiB / export 8 MiB, sampled RSS если уже даёт supervise, job ≤180 мин.

Записывать на корень: selector, cfg, argv, start/end, wall, exit code/signal, timeout flag, cleanup status, sha256 и путь сохранённых stdout/stderr/export (bounded), ошибку чтения export как есть. Ничего не классифицировать как PASS/MATCH. Ошибка одного корня не мешает следующим.

Убрать из runner: feature-set gate, required_contract_roles и role matching, control_match и q-domain gate, compile monitor с marker (compile входит в 600 с child), внутренние campaign/outer/step/phase reserve-расчёты (оставить job timeout и порядок корней). Синтетические тесты — только на то, что осталось: argv/cfg, identity mismatch, timeout/cutoff с сохранением exit, malformed/missing export без потери exit, NOT_RUN для оставшихся при исчерпании job-бюджета.

Артефакт: `q-pilot-raw.json` + bounded stdout/stderr/export каждого корня (все в пределах 256 MiB).

## std

- P-5a: mixed-threshold cover до вызова swap (после false-OR ensures он недостижим).
- Covers «q отсутствует во входе» в применимых positives.
- Остальное по ревью — оставить.

## Офлайн-анализ (отдельная стадия после запуска)

Чек-лист `PILOT-ANALYSIS-CHECKLIST.md`: по каждому корню из regular stdout и export — native verdict, все properties со статусами, режимы Check/Replace и verified stubs (точный набор), designated failures контролей (P-5a — ровно `swap_false_or_post`; P-5c — `P5C_CORRUPT_QPOST`), covers, U/unsupported/unwind, время; P-5b — показать, что fixed-q SUCCESS не годится провайдеру (q-domain {0} против all_u8) как правило анализа. Результат — исследовательский, proof_credit=NONE.
