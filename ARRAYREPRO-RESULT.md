# ARRAYREPRO — единственный разрешённый запуск завершён; CLI ERROR

REVIEW REQUEST 42ead2dba607925cd287c764014142dd0c9c14d8 — принят координатором до push.
[Run 41342109968](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/41342109968): push `42ead2dba6`, ubuntu-latest, 2026-11-01; без dispatch/повторов.
Оба job SUCCESS (pin 3m43s, main 3m37s): Kani собран, отчёт сохранён; это не успешная проверка гармоник.
Артефакты: [pin / outputs-0](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/41342109968/artifacts/13097886247), [main / outputs-1](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/41342109968/artifacts/13098231172); commands/rc/raw output/outcomes.json/summary.md.
Pin Kani SHA `9461e07af7ec929f050aa4192f29363c9be07779`; nightly-2026-10-12; rustc 1.101.0-nightly `080cc27146389dbb5c8772c476b1937be9c6110f` (2026-10-11).
Main Kani SHA `744b3e84d6eb68fd5456826997568666791bd355`; nightly-2026-10-23; rustc 1.101.0-nightly `7189d39d9ce936881b8132c6addeaf3e295cd455` (2026-10-22).
Обе версии: Kani Rust Verifier 0.68.0 (cargo plugin), CBMC `6.11.0 (cbmc-6.11.0)`, `/usr/bin/cbmc`; version probes rc=0.
Все 22 опытных вызова cargo-kani (8 гармоник + minisat + 2 playback на версию) отклонены до компиляции/верификации: CLI rc=2, требуется `-Z unstable-options` для `--harness-timeout`.
Это ошибка подготовленной команды, не наблюдение D1 и не инфраструктурный сбой; верификатор/решатели не запускались.
В таблице: status / failed checks / covers; MISSING означает отсутствие результата, не ноль и не PASS.

| Гармоника | Pin | Main snapshot |
|---|---|---|
| D1 [u8;1] | CLI_ERROR(rc=2) / MISSING / MISSING | CLI_ERROR(rc=2) / MISSING / MISSING |
| D2 u8, скалярный контроль | CLI_ERROR(rc=2) / MISSING / MISSING | CLI_ERROR(rc=2) / MISSING / MISSING |
| F2 if | CLI_ERROR(rc=2) / MISSING / MISSING | CLI_ERROR(rc=2) / MISSING / MISSING |
| F5 symbolic indices | CLI_ERROR(rc=2) / MISSING / MISSING | CLI_ERROR(rc=2) / MISSING / MISSING |
| F7 x=[1], y=[2] | CLI_ERROR(rc=2) / MISSING / MISSING | CLI_ERROR(rc=2) / MISSING / MISSING |
| W observed | CLI_ERROR(rc=2) / MISSING / MISSING | CLI_ERROR(rc=2) / MISSING / MISSING |
| C-other, одна cover | CLI_ERROR(rc=2) / MISSING / MISSING | CLI_ERROR(rc=2) / MISSING / MISSING |
| C-neither, одна cover | CLI_ERROR(rc=2) / MISSING / MISSING | CLI_ERROR(rc=2) / MISSING / MISSING |

D1 cadical/minisat: оба CLI_ERROR rc=2 на обеих версиях; остальные флаги совпадают; влияние решателя UNKNOWN.
D1 playback: CLI_ERROR rc=2 на обеих версиях; конкретные x/y/c UNKNOWN, `got` print сам по себе не экспортирует.
W playback: CLI_ERROR rc=2 на обеих версиях; observed/got UNKNOWN, сохранение сбоя D1 в W UNKNOWN.
Probe `-Z concrete-playback --help`: rc=0, опция print присутствует на pin/main; полноценный playback блокирован timeout-флагом.
Вывод: воспроизводимость вне std и поведение на main UNKNOWN; значений, failed checks или covers для сравнения нет.
Standalone использует sysroot сборки Kani; этот запуск не меняет in-tree FAILED и не даёт model-trust credit.
Известная необходимая коррекция команд: добавить `-Z unstable-options`; новый прогон не разрешён этим отчётом и не запускался.
ARRAYREPRO ЗАВЕРШЁН — отчёт о единственном запуске; экспериментальные выводы UNKNOWN.
