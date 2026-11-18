**DEFECT_PRESENT — reproduction подтверждена для наблюдённого fixture.**

Run `44177926794`, attempt `1`, Tiramisu-Cake/kani, branch `f4-confirm-ci/main-20261118`: completed/failure. Build SUCCESS; compare failure соответствует точному workflow exit 1 для DEFECT_PRESENT. Результат пересчитан через exact executed reviewed oracle; summary не использован как доказательство.

Exact trigger `bbbe2d18d2f6e1be7fd410e1d6f746c98bb92b79` → control `1ec3318f5e2c39afb701aa7a5578d4ea0a721224` → upstream main `faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`. Trigger/control tree `34a402bd4ebbabf3ec611327097475c8cb46cfba`; main tree `09b828b47c93e90e140e8c41f9048109a2f4a786`. Remote commit metadata совпало с локальными Git objects. Compiler fix отсутствует в полном tree delta. Reviewed package g0 `1bd7d58e6cafc64c36c4012651751c038d3e9c64`, review `8c37ad792ead0ac22161e2e2d10d8dadcd2837e1` APPROVE.

Единственный compact artifact `f4-confirm-44177926794-1`, ID `14369704819`: 14719 bytes; GitHub SHA256 `31ded0b6f857536d41b5e25ce07a198193fe6f0c45557a9d4654b15c04e595ed` совпал до extraction. Единственный member `result.json`, 226672 bytes. ZIP не сохранялся. Source/profile/workflow/payload hashes совпали; profile SHA256 `2e6a6cf8ba9b698c95a857bddfc7dd6e5c98391f6c66062f915a8784022e0568`. Preflight/service steps SUCCESS, три source snapshots неизменны, problems=[]; source-run сохраняет native tool paths/hashes.

| Slot | Native exit | Per-harness verdict/checks | Measured elapsed s |
| --- | --- | --- | --- |
| uninitialized_control | 1 | uninitialized_control: FAILURE 32/33 success | 0.717 |
| delayed_first/delayed_alone | 1 | delayed_harness: FAILURE 36/37 success | 0.465 |
| delayed_first/control_alone | 0 | initialized_control_harness: SUCCESS 13/13 success | 0.315 |
| delayed_first/paired | 1 | delayed_harness: FAILURE 36/37 success; initialized_control_harness: FAILURE 19/20 success | 0.616 |
| control_first/delayed_alone | 1 | delayed_harness: FAILURE 36/37 success | 0.415 |
| control_first/control_alone | 0 | initialized_control_harness: SUCCESS 13/13 success | 0.315 |
| control_first/paired | 1 | delayed_harness: FAILURE 36/37 success; initialized_control_harness: FAILURE 19/20 success | 0.616 |

Все 7 slots завершены EXITED, signal=null, timeout/spawn/build failure не наблюдались; build elapsed 75.772 s, exit 0. Сохранены 247 property instances в 9 harness results, 7 failed instances. Полные native IDs/status/description/location/multiplicity, failure partitions, exact argv/env/toolpaths и bounded stderr head/tail доступны в `result.json` и `PROJECTION.json`.

Для каждого из пяти native slots с exit 1 first meaningful retained reason — safety_check Undefined Behavior: Reading from an uninitialized pointer. Independent control: `uninitialized_control.safety_check.2`, control.rs:16, type *const u8. Оба delayed singleton и оба paired slots: `read_value.safety_check.1`, src/lib.rs:12, type u64. В paired эта ошибка присутствует отдельно у каждого harness. Source stage: native property verification после успешного build; stderr сохраняет warnings/compilation progress, отдельной Cargo error в нём нет. Exact per-slot failure records и missing fields перечислены в RESULT.json.

В обеих cfg variants initialized_control_harness меняется SUCCESS→FAILURE; 13→20 properties, добавлено 6 SUCCESS и 1 FAILURE, удалений нет. Delayed harness: 37 checks, FAILURE, semantic multiset неизменен. Именно per-harness verdict и multiset устанавливают PRESENT; aggregate pair exit 1 этого не устанавливает. Independent unsupported-class entry имеет SUCCESS и совпадает с полной native property identity/status/description; reachable/unresolved unsupported отсутствуют.

`delayed_first` означает feature delayed-first: delayed вызывает read_indirect→read_value, initialized вызывает read_value. `control_first` означает отсутствие feature: delayed вызывает read_value, initialized — read_indirect→read_value. Это cfg routing, фактический compilation order и покрытие обоих порядков — UNKNOWN. Cache source trace остаётся hypothesis; runtime causal proof отсутствует.

Replay read-only: из exact trigger AST выбраны только чистые parser/oracle функции, entrypoints runner/service/native tools не выполнялись. Retained compact properties/partitions/selection/config/exit перепроверены; summary-independence и 8 corruption cases PASS. Compact-to-parser adapter явно синтезирует только отброшенные envelope/kind/cover flags, ранее проверенные reviewed producer; они не являются вновь полученными native evidence. Raw export/stdout/stderr hashes сохранены как producer-attested, повторно по raw bytes не вычислялись. Archive/member hashes проверены независимо.

UNKNOWN: old run43882466907 exact Cargo error; explicit process-group/descendant shutdown confirmation; per-root timings/RSS; underlying cargo/rustc binary hashes (recorded paths resolve to rustup proxies); post-run binary rehash; actual compilation order/causality. Native rustc version `1.102.0-nightly (3ef0c22cd 2026-11-11)`, CBMC `6.11.0`, Kani `0.68.0`; requested toolchain nightly-2026-11-12, target x86_64-unknown-linux-gnu, edition 2021. Доступные измерения — per-invocation elapsed_seconds. Formal proof credit NONE, только bounded fixture reproduction; download_verified не выставлялся.

Item1 27/28, item2 9/14, total 36/42 — user/owner reference; ledger неизменён. Новые CI/fix/PR/push/reservation не выполнялись. Субагентов и смены модели не было. S2 ждёт владельца и вне scope. Координатору передаётся подтверждённое reproduction для решения о следующей отдельно reviewed стадии.
