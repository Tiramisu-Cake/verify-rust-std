# CAL2 · независимое ревью

**READY_FOR_REVIEW.** Frozen inputs, diff и локальные синтетические проверки прошли независимое ревью. `go=NOT_GRANTED` · `proof_credit=NONE`.

- Control `7393c841446064bffc9d8b1d13a4d68db83cb8f1` имеет tree `80fa0a23cac7f0dde952deea145c70e2fbba9f84` и parent `0012750e1a3bbb7977fe0149e565b6b6dcd7c3c8`. Trigger `4834030d3991ded4bbdf3f88327f2800543cddd7` имеет тот же tree и единственного parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Std overlay `043a1f19f9d36eb1666979f97b8e7e483ab41c5e` от `080a0104159fd04b6764a24f8538a97588f6612e` имеет tree `1361a0da67b9bd21fc7c77a941582d0fd17b9a8d`.
- Frozen request, bundle SHA-256 `747bed56fb2c137caf90dadc52802b42406840f9240dda3f58a370a33662a481`, bundle ref и overlay parent/tree согласованы. Layout guard принял ожидаемые CAL1 файлы и CAL2 diff только в `Cargo.toml` и N32 observer. Изменение переключает N32 на mask при CAL2 cfg, не меняя N25 и другие длины.
- Эквивалентность Mask и Below следует из формулы. Для `b = count(x < q)` маска `2^32 - 2^b` устанавливает ровно биты `i >= b`. Нулевые биты совпадают с условием `i < b` для позиций ниже `q`, включая `b=0`, `b=32` и смешанные значения. Check наблюдает фактический вывод merge.
- Прошли **78 локальных Python-тестов**. Проверены шесть последовательных Linux singleton, исходные Darwin singleton и две batch, паритет A/B, exact selectors/argv, независимость macOS от Linux cutoff, cap и latest start, partial receipts, RSS-stop/pressure/cleanup, PID churn, ограниченные PSS-пробы и native CNF при завершении и cutoff. YAML содержит независимые `ubuntu` и `macos` jobs с `contents: read`. `git diff --check`, bundle verification и layout guard прошли.
- Директива `[skip ci]` в trigger подавляет push workflow. Решение о dispatch остаётся координатору. [GitHub Actions](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs)

Запуск `run.py pins` локально без GitHub event environment завершился ожидаемой ошибкой fork/push/exact-ref guard. Guard проверен synthetic тестом. Cargo, rustc, Kani, CBMC, CI и push не запускались.
