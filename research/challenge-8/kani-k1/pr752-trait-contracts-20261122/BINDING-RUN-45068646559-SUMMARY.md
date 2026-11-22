# Run 45068646559 — #752 native binding check (coordinator first look)

Fork `Tiramisu-Cake/kani` `uninit-ci/ch8-q-pilot-v1`, trigger `bc572d7ad1b3886e06e97b1109a634e82e74f92d` (tree `0938a64902`, parent `6518a69cbe`, = reviewed control `341a719bbd`). Job `binding` success, 20:50–21:12Z (23 min). Index: `stop_reason=null`, all 13 roots `EXITED`. Artifact downloaded with `gh run download` to `/root/ch8-artifacts/run-45068646559/ch8-pr752-binding-45068646559-1/` (binding-index.json + per-root regular/native/stock-export JSON).

| Root | Regular summary | Assigned failure | Native projection |
|---|---|---|---|
| D-S | 0 of 298 failed (12 unreachable) | — | COMPLETE |
| D-U | 0 of 294 failed (12 unreachable) | — | COMPLETE |
| D-F | 0 of 497 failed (17 unreachable) | — | INCOMPLETE: truncated at 4 MiB publication cap |
| F2 | 0 of 582 failed (28 unreachable) | — | INCOMPLETE: cap |
| F3 | 0 of 638 failed (28 unreachable) | — | INCOMPLETE: cap |
| U2 | 0 of 709 failed (28 unreachable) | — | INCOMPLETE: cap |
| U3 | 0 of 765 failed (28 unreachable) | — | INCOMPLETE: cap |
| C3 | 0 of 757 failed (28 unreachable) | — | INCOMPLETE: cap |
| K1 | 1 of 73 failed | `high-bit corruption preserves sorted full values` trait_contracts.rs:234 | COMPLETE (no inspection planned) |
| K2 | 1 of 70 failed | `same set preserves full multiplicities` trait_contracts.rs:254 | COMPLETE (no inspection planned) |
| K3 | 1 of 628 failed | `reverse pointer output is sorted` trait_contracts.rs:280 | INCOMPLETE: cap |
| K4 | 1 of 542 failed | `function item output is sorted` trait_contracts.rs:315 | INCOMPLETE: cap |
| W1 | 0 of 492 failed (20 unreachable) | — | INCOMPLETE: cap |

First look only. Role acceptance (BINDING-CHECK-PLAN.md, Offline acceptance) is pending: whether the truncated projections still contain the required anchors, call edges and ordered old/havoc/post records, or a re-run with a larger per-root publication cap is needed.
