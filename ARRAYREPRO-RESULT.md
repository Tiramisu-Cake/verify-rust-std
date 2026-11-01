# ARRAYREPRO ЗАВЕРШЁН — наблюдение воспроизводится вне std на pin и main

REVIEW REQUEST 42ead2dba607925cd287c764014142dd0c9c14d8 — пакет принят; корректировка разрешена отдельным GO.
[Корректирующий run 41342744641](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/41342744641): push `350f0cb5cb38142be4b4b121665c1df4b92df5ae`, 2026-11-01, ubuntu-latest.
[Первый run 41342109968](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/41342109968): все 22 опыта CLI_ERROR rc=2 до proof из-за отсутствия `-Z unstable-options`; не proof evidence.
Корректирующие job SUCCESS: pin 3m43s, main 3m23s; это сборка/сбор отчёта, не SUCCESS всех proofs. Dispatch/третьего запуска нет.
Артефакты: [pin / outputs-0](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/41342744641/artifacts/13098530760), [main / outputs-1](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/41342744641/artifacts/13097852083); команды, rc, raw outputs, outcomes.json, summary.md.
Pin Kani SHA `9461e07af7ec929f050aa4192f29363c9be07779`; nightly-2026-10-12; rustc 1.101.0-nightly `080cc27146389dbb5c8772c476b1937be9c6110f` (2026-10-11).
Main Kani SHA `744b3e84d6eb68fd5456826997568666791bd355`; nightly-2026-10-23; rustc 1.101.0-nightly `7189d39d9ce936881b8132c6addeaf3e295cd455` (2026-10-22).
Оба: Kani Rust Verifier 0.68.0 (cargo plugin), CBMC `6.11.0 (cbmc-6.11.0)`, `/usr/bin/cbmc`; version probes rc=0.
Единственная коррекция: `-Z unstable-options` во всех 11 timed-командах на версию; остальные аргументы и исходник гармоник неизменны.
Help обеих версий требует этот флаг для `--harness-timeout`; остальные используемые опции его не требуют; playback имеет `-Z concrete-playback`, probe rc=0.

Колонки: status / failed checks (число/всего) / covers (satisfied/total); literal failed-check message общий для обеих версий указан слева.

| Гармоника; failed-check message | Pin | Main snapshot |
|---|---|---|
| D1; `casefive D1: read through the selection` | FAILED / 1/30 / 2/2 | FAILED / 1/30 / 2/2 |
| D2 u8, скалярный контроль; — | SUCCESS / 0/16 / 2/2 | SUCCESS / 0/16 / 2/2 |
| F2; `arrayfactor F2: read through if selection` | FAILED / 1/28 / 2/2 | FAILED / 1/28 / 2/2 |
| F5 symbolic indices; — | SUCCESS / 0/42 / 4/4 | SUCCESS / 0/42 / 4/4 |
| F7 [1]/[2]; `arrayfactor F7: first selected value` | FAILED / 1/33 / 2/2 | FAILED / 1/33 / 2/2 |
| W; `arrayrepro W: read through the selection` | FAILED / 1/32 / 2/2 | FAILED / 1/32 / 2/2 |
| C-other; `arrayrepro C-other: read through the selection` | FAILED / 1/30 / 1/1 | FAILED / 1/30 / 1/1 |
| C-neither; `arrayrepro C-neither: read through the selection` | FAILED / 1/34 / 0/1 | FAILED / 1/34 / 0/1 |

Все 22 опыта получили полные результаты: rc=1 для FAILED, rc=0 для SUCCESS; CLI/backend ERROR, unsupported, timeout и MISSING_OUTCOME отсутствуют.
D1 cadical/minisat при прочих равных: оба FAILED, только тот же literal value check, 1/30, covers 2/2 на обеих версиях; смена решателя результата не меняет.
D1 playback (отдельный опыт): assertion-вектор на обеих версиях x=[255], y=[127], c=true; FAILED 1/30, covers 2/2. print экспортирует входы any, не got.
W baseline и playback сохраняют value failure: FAILED 1/32, covers 2/2; assertion-вектор x=[255], y=[127], c=true, observed=127 на обеих версиях.
В модели отдельной W `assume(observed == got[0])` связывает got[0]=127=y[0], хотя при c=true ожидается x[0]=255; W не называется D1.
Классификация до asserts: `c && x[0]!=y[0] && got[0]==y[0]` cover 1/1; `c && x[0]!=y[0] && got[0]!=x[0] && got[0]!=y[0]` cover 0/1 на pin/main: найден другой элемент, свидетеля вне {x,y} нет в этих гармониках.
Playback print сгенерировал тесты; native replay не выполнялся. F7 падает только на first-selected assert; F2 тоже падает, F5 подавляет симптом в этом fixture.
Вывод: обычный standalone cargo-kani воспроизводит D1 на обоих SHA; на указанном main симптом сохраняется, D2 проходит.
UNKNOWN: ответственный compiler/model/backend-компонент, первопричина, обобщение на другие типы/fixtures/контексты; влияние solver за пределами проверенного D1.
Standalone использует sysroot каждой сборки Kani; результаты не отменяют in-tree FAILED и не дают общего model-trust credit.
