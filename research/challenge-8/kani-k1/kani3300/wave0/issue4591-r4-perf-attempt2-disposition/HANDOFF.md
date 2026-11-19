# #4591 r4 perf attempt 2: согласованная остановка повторов

**Root согласен** с решением координатора: дальнейших perf rerun и задания w15 на расследование памяти сейчас не выдавать. Рабочая классификация — вероятная нестабильность fork-runner/infrastructure; независимая корневая причина остаётся UNKNOWN. Передать владельцу факты и PR-текст для решения о публикации можно. Сама публикация ждёт команды владельца.

Native attempt 2 run44516395307 завершён FAILURE на прежнем head b301. Perf job135579130682: 13:03:03–14:18:07Z, FAILURE. Восемь successful Kani jobs в attempt2 metadata унаследованы от attempt1 (прежние execution timestamps), а не выполнены заново. Format/Deny SUCCESS и все пять OS/docs/LLBC/benchcomp SUCCESS сохранены в independently checked attempt1 intake0f758. Оба perf FAILURE сохраняются; полный r4 CI зелёным не считается.

Root проверил diff6f..b301: только шесть файлов tests/kani и tests/expected. tests/perf, compiler, library, scripts, workflows/actions, tools, Cargo.lock и rust-toolchain.toml имеют одинаковые Git objects. PERF_DIR и compiletest suite выбирают tests/perf. Это подтверждает равенство соответствующих репозиторных входов r2/r4, но не runtime VM/load/dependencies.

Ранее прошедший perf r2 — историческое подтверждение на тех же репозиторных входах; он не является успешным perf на голове b301. Сообщённая координатором статистика fork6/13 против upstream8/8 и повторяющиеся runner-loss поддерживают рабочую инфраструктурную классификацию. Они не доказывают точный механизм сбоя или отсутствие любой ресурсной чувствительности.

Testing должен явно различать успешные regression/прочие jobs r4, два perf runner-loss и исторический r2 perf PASS. Допустимо дать обе ссылки с этим пояснением. Обещание, что upstream PR CI обязательно пройдёт perf, не делается; его будущий результат оценивается отдельно. Named-property/MIR и независимая причинность по metadata не установлены.

PR-4591-DRAFT.md/публикации/source/workflow/ledger не изменены. Новых CI, worker tasks, raw logs/archives/GCS или расследования памяти не запускалось. Root не связывается с владельцем напрямую; factual handoff — координатору.
