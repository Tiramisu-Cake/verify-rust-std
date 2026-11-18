**Reproduction подтверждена: DEFECT_PRESENT.** Run44177926794/attempt1 terminal; build SUCCESS, compare failure по дизайну. Exactpins, pre-extraction artifact digest, unchanged source/profile gates, seven native slots, native property oracles и read-only replay — PASS.

В обоих cfg variants initialized_control_harness отдельно SUCCESS/13 checks, paired FAILURE/20 checks: +6 SUCCESS и +1 uninitialized-read FAILURE в read_value, src/lib.rs:12. Delayed singleton/paired FAILURE/37 checks, semantic multiset неизменен. Independent uninit control intended FAILURE на control.rs:16. Все native exits согласованы с per-harness verdicts; summary не задавал outcome.

Координатору: принять bounded reproduction и определить следующую отдельно reviewed fix/CI стадию. При необходимости установить compilation order/causality нужна отдельная измерительная работа; оба направления сейчас UNKNOWN. Ни эта передача, ни PRESENT не разрешают item1 28/28. Текущие owner counters item1 27/28, item2 9/14,total36/42; ledger не менялся. S2 dispatch ждёт владельца, вне scope.

First meaningful reasons и точные missing fields — RESULT.json; exact IDs/partitions/argv/env/tools/diagnostics — result.json и PROJECTION.json; adapter/source/transport boundaries — PROVENANCE.json. Old43882466907 exact Cargo error, per-root metrics и explicit process-group shutdown остаются UNKNOWN. Нет rawlogs, нового CI, fix, PR, push, ledger changes, субагентов или смены модели.

Повторить compact replay из g0 root: `PYTHONDONTWRITEBYTECODE=1 python3 research/challenge-8/kani-k1/kani3300/wave0/f4-confirm-intake/run-44177926794/replay.py`. Скрипт только читает evidence и pinned Git objects, печатает projection; native tools не запускает.
