# Part 1 v7: organizer CI in the fork (2026-11-04)

Head `d1283ff22ab40adb91473ef430072172b3e21d67` (branch `submission/ch8-smallsort-part1-v7`): one commit on upstream
`233f96f66ab3785881cead133817ed5db4c76b09` (Kani `cd355b0b`, nightly-2026-10-22); library tree `32ce0c62f6` =
TRIMPART `bd7fb8196e`. Workflow files and `scripts/run-kani.sh` are upstream's, unchanged; all ten were started by
`workflow_dispatch` in the fork.

| Workflow | Run | Result |
|---|---|---|
| Kani | [41836353526](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/41836353526) | 15/16 jobs success; `Build JSON from logs (macos-latest)` never got a runner ("not acquired by Runner ... capacity constraints"), in attempt 1 and in one rerun (attempt 2) |
| Rust Tests, Flux, RAPx, KMIR, VeriFast, VeriFast (negative), GOTO Transcoder, Build Book, Testable SIMD | 41836364754, 41836376488, 41836390576, 41836402540, 41836416105, 41836428712, 41836441166, 41836453998, 41836466032 | success, attempt 1 |

Kani jobs that passed: 8 partitions (4 per OS), autoharness on ubuntu and macOS, List, Analyzer, Metrics on both OS,
Build JSON on ubuntu.

`v7-autoharness-smallsort.tsv`: the 202 `smallsort::verify` harnesses in the two autoharness job logs (status, failed
checks, satisfied covers, Verification Time), with the v6 times from run 41404150041 (pin `9461e07a`). Extracted from
the job logs with the `Thread N:` lines; the workflow itself does not check covers.

| OS | SUCCESSFUL | failed checks | covers satisfied | sum VT (v6) | max VT | > 300 s | > 200 s |
|---|---:|---:|---:|---|---|---:|---:|
| ubuntu | 202/202 | 0 | 855/855 | 8425 s (6628 s) | 374.0 s `merge::general_direct_u64_n9` | 1 | 3 |
| macOS | 202/202 | 0 | 855/855 | 9604 s (10746 s) | 306.1 s `network::dispatch_safety_stable_unstable_bytes16_n32` | 1 | 8 |

No warning in the job logs points at `smallsort/verify`.
