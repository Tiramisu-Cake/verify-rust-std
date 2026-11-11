# KANI3300 G1B2 — bounded result

- Build `b5e18fb8-b102-47fa-8300-644ee9348f85`: **FAILURE / RUNNER_ERROR**, gate false; source `76ffcf85e3989e8da5f1cc16c2d545237e550134`. B2 attempt 1/1 terminal (B total 2 attempts); no repair/further retry, negative unchanged.
- **0 observed native PASS, 0 observed native FAIL; all 20 selectors NOT_RUN** by bounded-diagnostic/pinned-runner-gate inference. Summary has 0 harness rows; native wall times unavailable.
- Bounded first failed stage `build`: Kani Ubuntu dependency installation failed because `archive.ubuntu.com` could not be resolved (m4/flex/bison/cmake/z3 and others). This precedes rustup/cargo and build.ok; no compiler/verifier failure inferred.
- Cloud checkout/k1/upload SUCCESS, gate FAILURE/exit1. k1 wrapper success permits upload; it does not establish Kani/compiletest success.
- Request `9b4e066d929ad0bf5e87a0de825941bac8bfba4dbf7f4db4dabcc408fa509569` and patch `c9ddce47cae76e9b9f462e8bcac94c73f70c0e8c32438f35f9ff1d7539117767` match exact published B2. Production `3d085249c9c6c49a9c2e5747e2167d629748fb70` unchanged.
- Native pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; preflight tree `8f152bac27f8ff1d7fba45f57dc6a0ebeb348867` unchanged. Completed runtime tree/version/binaries UNKNOWN; summary reports `missing/inconsistent Kani patch/tree/version/build identity` after dependency failure.
- Six summary-reported tooling hashes match source and KT2 `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`. Summary status RUNNER_ERROR is not native acceptance or independent proof.
- Build wall **199.702 s**, queue **54.923 s**. B2 spend **$0.0540** (4 rounded min); B1 **$0.0270**; cumulative B **$0.0810 ≤ $0.80**, reserved $0. Ledger `2 0.0810 0.0000`; A-family $0.4860 unchanged.
- Brief exit1 HTTP404; authorized bounded summary (exit0) + setup excerpt/metadata/budget used. Summary JSON SHA unavailable through these routes without a native report; full cached JSON/raw logs not read. Independent B1/B2 credit NONE.

| # | Selector under tests/expected/uninit | PASS/FAIL outcome | Wall s |
|---|---|---|---|
| 01 | `g1-union-pointee-unsupported-reject_bodyless_return/main.rs` | NOT_RUN (setup) | — |
| 02 | `g1-union-pointee-unsupported-reject_foreign_mutation_erased/main.rs` | NOT_RUN (setup) | — |
| 03 | `g1-union-pointee-unsupported-reject_forget_union_array/main.rs` | NOT_RUN (setup) | — |
| 04 | `maybe-uninit-transmute/main.rs` | NOT_RUN (setup) | — |
| 05 | `maybe-uninit-transfers/main.rs` | NOT_RUN (setup) | — |
| 06 | `maybe-uninit-initialized/main.rs` | NOT_RUN (setup) | — |
| 07 | `maybe-uninit-transmute-padding/main.rs` | NOT_RUN (setup) | — |
| 08 | `maybe-uninit-transmute-source-read/main.rs` | NOT_RUN (setup) | — |
| 09 | `maybe-uninit-argument-buffer/main.rs` | NOT_RUN (setup) | — |
| 10 | `maybe-uninit-contract-clause/main.rs` | NOT_RUN (setup) | — |
| 11 | `maybe-uninit-contract-frame/main.rs` | NOT_RUN (setup) | — |
| 12 | `maybe-uninit-partial-copy/main.rs` | NOT_RUN (setup) | — |
| 13 | `maybe-uninit-reset-alias/main.rs` | NOT_RUN (setup) | — |
| 14 | `maybe-uninit-argument-return/main.rs` | NOT_RUN (setup) | — |
| 15 | `maybe-uninit-overwrite-copy/main.rs` | NOT_RUN (setup) | — |
| 16 | `maybe-uninit-overlap-copy/main.rs` | NOT_RUN (setup) | — |
| 17 | `maybe-uninit-repeat-local/main.rs` | NOT_RUN (setup) | — |
| 18 | `maybe-uninit-reset-zst/main.rs` | NOT_RUN (setup) | — |
| 19 | `unions.rs` | NOT_RUN (setup) | — |
| 20 | `uninhabited-union-field/uninhabited-union-field.rs` | NOT_RUN (setup) | — |

- NOT_RUN basis: pinned `gcb-k1.sh:111` invokes `scripts/setup/ubuntu/install_deps.sh` (set -eu; apt install) before rustup/cargo/build.ok; `verify:141` requires build.ok. The build-stage DNS error therefore prevents native execution. Empty summary rows alone are not the basis.
- **Failed Checks:** unavailable; **compiletest `expected output to contain`:** unavailable; compiletest/native invocation did not run under the source-gate inference.
- Exact bounded example: `E: Failed to fetch http://archive.ubuntu.com/ubuntu/pool/universe/z/z3/z3_4.8.12-3.1build1_amd64.deb  Could not resolve 'archive.ubuntu.com'`.
- Receipts: `G1B2-BUILD-METADATA.json`, `G1B2-BOUNDED-SETUP-RECEIPT.json`, `G1B2-SUMMARY-ROWS.txt`, `G1B2-OBSERVATIONS.json`. Original B/B2 requests, patch, all goldens and B1/A3 history retained. No raw logs/archives/credentials, local compiler/verifier, source edits or ledger-history edits. Stop for coordinator review.
