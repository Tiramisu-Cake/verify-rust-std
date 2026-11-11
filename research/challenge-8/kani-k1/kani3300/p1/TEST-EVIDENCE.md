# Selected fixtures and prior native evidence

All paths are below `tests/expected/uninit/`. PASS means native expected-mode PASS, not that negative UB verified successfully.
The table binds prior native outcomes, not a new run of the packaged goldens/context.
U3-repair1 observations: `../u3/repair1/SELECTOR-OBSERVATIONS.json`; U3B: `../u3b/POST-BUILD-OBSERVATIONS.json`;
U1: `../../RESULT-KANI3300-U1.md`. Exact source, heads and selector offsets are in `TEST-MANIFEST.json`.
All selected Rust sources are byte-equal to final v2 after the requested rustfmt; initialized also equals its original U1 patch.

| Fixture | Historical native PASS build(s), zero-based offset | Expected behavior |
|---|---|---|
| `maybe-uninit-wrap-u3-positive/main.rs` | U3-repair1 `45287677-98cb-4dc4-b98d-7ccae4782f5f` #0; U3B `9f964706-4b89-4340-a1ee-022aa23ecbe9` #5 | require-success |
| `maybe-uninit-review-positive/main.rs` | U3-repair1 `45287677-98cb-4dc4-b98d-7ccae4782f5f` #11; U3B `9f964706-4b89-4340-a1ee-022aa23ecbe9` #7 | require-success |
| `maybe-uninit-initialized/main.rs` | U1-repair1 `d5d15c41-1c07-4f9f-a6ff-16c25fae00e1` | require-success |
| `maybe-uninit-wrap-u3-padding/main.rs` | U3-repair1 `45287677-98cb-4dc4-b98d-7ccae4782f5f` #1 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u8` |
| `maybe-uninit-wrap-u3-source-read/main.rs` | U3-repair1 `45287677-98cb-4dc4-b98d-7ccae4782f5f` #2 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u64` |
| `maybe-uninit-buffer-u3-plain-negative/main.rs` | U3-repair1 `45287677-98cb-4dc4-b98d-7ccae4782f5f` #5; U3B `9f964706-4b89-4340-a1ee-022aa23ecbe9` #6 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u16` |
| `maybe-uninit-buffer-u3-clause-pfc-negative/main.rs` | U3-repair1 `45287677-98cb-4dc4-b98d-7ccae4782f5f` #8 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u16` |
| `maybe-uninit-buffer-u3-frame-negative/main.rs` | U3B `9f964706-4b89-4340-a1ee-022aa23ecbe9` #4 | Failed Checks: Check that *var_7 is assignable |
| `maybe-uninit-partial-copy/main.rs` | U3-repair1 `45287677-98cb-4dc4-b98d-7ccae4782f5f` #14 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `[u8; 4]` |
| `maybe-uninit-reset-alias/main.rs` | U3-repair1 `45287677-98cb-4dc4-b98d-7ccae4782f5f` #15 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u8` |
| `maybe-uninit-review-argument-return/main.rs` | U3-repair1 `45287677-98cb-4dc4-b98d-7ccae4782f5f` #12 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u16` |
| `maybe-uninit-review-overwrite-copy/main.rs` | U3-repair1 `45287677-98cb-4dc4-b98d-7ccae4782f5f` #16; U3B `9f964706-4b89-4340-a1ee-022aa23ecbe9` #8 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `[u8; 2]` |
| `maybe-uninit-review-overlap-copy/main.rs` | U3-repair1 `45287677-98cb-4dc4-b98d-7ccae4782f5f` #17 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u8` |
| `maybe-uninit-review-repeat-local/main.rs` | U3-repair1 `45287677-98cb-4dc4-b98d-7ccae4782f5f` #18 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u64` |
| `maybe-uninit-review-reset-zst/main.rs` | U3-repair1 `45287677-98cb-4dc4-b98d-7ccae4782f5f` #19 | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u64` |

Six new Failed Checks goldens have NOT_RUN status. Existing passed goldens for all five adversarial controls and the frame control are retained.
The frame golden checks both assigns failure and the actual user write at line 22.
The initialized fixture passed only under older U1 production; final-v2 acceptance of this selected fixture awaits the prepared gate.
U3/U3B native PASS positives are tied to exact require-success/golden counts; full literal failure lists for passed selectors were not retained.
No independent B1/B2 or general proof credit is asserted. All OOM and UNKNOWN roots are excluded from this gate.
