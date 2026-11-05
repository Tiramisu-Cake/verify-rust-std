# LOOPPIN — результат: loop-contract калибровка работает на новом pin
Build `f645e709-de9a-4b7a-a61f-69aab36f4f75`: Cloud SUCCESS, COMPLETE, gate true, Kani exit 1 (ожидаемый negative).
Source `2ed6e9c7da48d61fd362a9f90401486ef25421bc`; library `532eddb301c43d36b8b777414b59cbc09e86ed37`.
Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`; tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`, check-tooling PASS.
Request `looppin-g1-20261105-01`, owner k1-network; diagnostic, standard4, controls=true, jobs=1, 3 мин/root.
Request SHA256 `5c3908bef8e08cfa1967cd4b8d1bea82ffd918647c6b777771721a5e3e097caa`; source/request/build/pool bindings PASS.

| Root в verify::looppin:: | Статус | Проверка (failed/total) | с | CBMC peak RSS, KiB |
| --- | --- | --- | ---: | ---: |
| calibration_true | SUCCESS | 0/83; covers 3/3 | 0.17787845 | н/д* |
| calibration_false_control | FAILED (ожидаемо) | invariant step, 1/88 | 0.13606513 | н/д* |
| insert_tail_u64_tail1_to4_backing5 | SUCCESS | real-helper PFC, 0/219; covers 4/4 | 30.317678 | 1300820 |
| outer_loop_u64_symbolic_len_backing5 | SUCCESS | loop invariant + verified stub, 0/404; covers 3/3 | 121.00956 | 6227528 |

Единственный FAILED check: `Check invariant after step for loop slice::sort::shared::smallsort::verify::looppin::calibration_false_control.0`.
Location: `/workspace/src/library/core/src/slice/sort/shared/smallsort/verify/looppin.rs:38`; других failed checks нет.
Covers **10/10**, unreachable covers **0**; по 4 unreachable прочих checks у PFC и consumer не являются covers.
*Обе калибровки короче sampling-интервала 2 с; per-root RSS отсутствует, не равен нулю. Два больших CBMC peak имеют direct attribution.
Пики PFC/consumer: 1.24/5.94 GiB; machine 15.63 GiB, swap off, OOM scan none_seen; verify wall 4:16.01, сумма row 151.64118158 с.
LOOPINV (`92ded02d10`, старый pin `9461e07a`): source-reported 3/3 TIMEOUT при 600 с/root, CBMC 14.81–14.99 GiB, invariant/negative не установлены.
Здесь index-калибровка и stubbed pointer-copy отличаются от старых roots; изменение нельзя причинно приписать только pin.
Вывод: путь loop contracts на новом pin засчитан — true проходит, false отвергается нужной проверкой; copied outer loop тоже проходит.
PFC/consumer используют один reading_less_u64 function item, u64 backing5 и tail 1..4; len=any() в 1..5, offset=any() в 1..len.
Это фиксированный backing и копия цикла; runtime smallsort.rs не менялся. Произвольная длина, generic callbacks, sortedness/termination не доказаны.
Следующий шаг: отдельно обосновать перенос на настоящий внешний цикл и произвольный backing, расширить insert_tail contract/PFC за конечный домен.
Компиляция успешна; unsupported operation, compile error, TIMEOUT/память как отказ в этих четырёх roots не наблюдались.
Одна сборка, retries/repairs 0; own spent **$0.1620 / $1.20**, резерв $0; проект used $99.8970, прочие reserves $0.8100, cap $118.96.
Bounded evidence и воспроизводимая проверка: [отчёт](looppin/evidence/verification-report.json), [проверка](looppin/verify_result.py); новой независимой verifier execution нет.
