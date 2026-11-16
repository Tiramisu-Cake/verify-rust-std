# A1-R1 → R3: static triage

Input: g0 `2ff42c1c8349972ec7ad60a68bbfafd32f903612`, task
`TASK-CH8-A1-R1-TRIAGE-W15.md`. One preparation stage; no push, CI, ledger or local
Rust/Kani/CBMC execution. R1 facts below are coordinator-supplied bounded receipts,
not an independently queried run or proof result.

R1 run `43772128212`, trigger `a47d28da27`, package
`bf81a1f14f9468c5b25d3ee33f7dafbf2bca131e`: all eight rows failed compiling core.
N32 example: exit 1 in 20.6s; stderr reports 8652 prior errors. The 10,696,252-byte
stdout was removed by artifact bounding (`TRUNCATED_REMOVED`); first errors are
unavailable. No raw logs were read or recovered. R2 run `43772128176` reports E0433
for both #5151 fixtures on both source pins; neither fixture has a verifier verdict.

## Definite source defect, limited causal attribution

`wave0_a1.rs:4` imported `StableSmallSortTypeImpl` and `UnstableSmallSortTypeImpl`
from `super` = `smallsort::verify`. That module contains only module declarations,
with no import/re-export of these names. Both traits are declared in `smallsort.rs`
(lines 20 and 81); siblings likewise use `super::super` for smallsort items.
The corrected import is `use super::super::{...}`. This statically establishes an
unresolved-import compile blocker, but **does not establish the cause of all 8652
diagnostics** or prove the corrected package compiles. R3 must retain the first errors.

Std fix package: `312ff625b9b3338281d899cca47d72c24d5a2539`, parent A1
`65864680a145c90c583dcba7efd1d569475519fc`. Exactly one import changes; harness
bodies, assertions, covers, unwind, stubs, domains and runtime algorithm are unchanged.

## R1 versus accepted SEL1 replay

Comparison inputs: old control `scripts/ch8-w0-a1/{a1.py,CI-REQUEST.json}`, accepted
`/root/kani-fix-3300-sel1-replay-w15/scripts/kani3300-replay/{replay.py,CI-REQUEST.json}`,
and std objects in `/root/verify-rust-std-ch8-w0-a1-w15`. The saved replay result
`../sel1-c2/replay/run-43751703000/RESULT.md` is a coordinator report of compilation
and bounded helper outcomes, not independently established proof credit here.

| Candidate cause | Static comparison and conclusion |
| --- | --- |
| RUSTFLAGS overwrites Kani flags | Both use `--cfg kani_smallsort_controls`. Pinned `kani-driver/src/call_single_file.rs:258-305` builds base flags (`--cfg=kani`, no-core extern, etc.) and appends RUSTFLAGS. `call_cargo.rs:84-125` adds local Kani flags and sends them through `pass_rustc_args(AllCrates)`; `util.rs:208-235` encodes the full vector in CARGO_ENCODED_RUSTFLAGS. No overwrite of generated flags by this RUSTFLAGS value is established. |
| controls cfg | Both enable the same existing controls/replay modules. A1 additionally enables `wave0_a1`, containing the definite bad import. |
| uninit checks | Both use ON, `--no-assert-contracts`, the same unstable features, exact harness selection, jobs1, object-bits12. A1 uses 600s rather than replay2400s and different selectors; these do not explain an early Rust name-resolution failure. |
| target-dir/cwd | Both run from a separate std checkout with `./library` and a per-row output target directory. A1 `<OUT>/target` resolves to each row's fresh directory, like replay `<OUTPUT_ROOT>/<row>/target`. No shared cache/reused row target is established. |
| std overlay | Same frozen base `70ba5befc617627073738e26cb1466bd4fb76e41`, tree `84ab170ccdcc29fba69e55e0a46e6acdf52d9704`. A1 reuses the accepted helper closure/replay changes and adds only the cfg-gated A1 module/declaration. |
| upstream #745 mismatch | Both pins use nightly-2026-10-23; the accepted replay used this same std base and Kani SEL1 `14bc57fdb99960240c4944845a3d985c8af4dcf7`. In frozen70ba, `library/core/src/fmt/mod.rs:2627` already defines `Formatter::debug_c_like_enum_write_str`. The S1 872d/0aac missing-method failure is a different pair. No P′ rebase is justified for this A1 package. |

Remaining hypotheses and distinct cheap checks within the same first R3 invocation:

| Hypothesis | Distinguishing observation |
| --- | --- |
| Further A1 type/macro/stub errors | Retained first diagnostics point to A1 code after correcting the trait import. |
| Inherited compiler/Cargo environment differs | Compare the allowlisted diagnostic environment against the row and pinned driver's flag construction; inspect wrapper/target overrides if present. |
| Unobserved toolchain/source dependency mismatch | Compare exact source/overlay validation and runtime nightly/compiler/sysroot identities against the frozen inputs. |

The cheap execution step is **one coordinator-authorized R3 first N32 invocation**:
read its bounded stdout/stderr heads/tails, exact argv/cwd, allowlisted diagnostic
environment, source/overlay/runtime identities. An E0432 at the old import supports
that defect; another diagnostic names the next blocker. No local compilation, extra
dispatch, flag sweep or full-log recovery is needed or authorized here. Missing
diagnostics remain UNKNOWN, never evidence of compilation success.

## Runner and fixture delta

Preserve four 64KiB stream windows before metadata bounding, with hashes and byte
counts. Trim actual JSON metadata rather than charging stdout for metadata debt;
protect diagnostic windows and receipts. Exclude target directories from uploaded
evidence. Removed evidence stays explicitly incomplete; excerpts alone grant no proof.
R3's eight std rows share one serial job, in the original order with three N32 first.
A confirmed core compile failure stops later rows with explicit NOT_RUN receipts;
uncertain resource/runner/incomplete failures stop separately without being called
compile failures. Original invocation codes/exceptions and receipts are preserved.

The #5151 original and companion source bytes remain unchanged, including empty Drop.
Only their standalone invocation receives `RUSTFLAGS=--edition=2021`, identically for
baseline and SEL1. R3 re-executes these two fixtures on both pins; #5020/#4854 source,
commands and historical R2 findings remain unchanged and are not re-executed by R3.
This is a fixture wiring correction, not a verification result or PR-02 reset fix.
