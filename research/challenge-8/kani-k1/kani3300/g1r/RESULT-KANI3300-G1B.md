# KANI3300 G1B — bounded result

- Build `8e7a82cb-3dfd-46dc-9b61-43eddf773aa0`: **FAILURE / RUNNER_ERROR (setup)**; source `6ec78732cea6f1a80b8c02574ee348f20b0563ec`. Attempt 1/1 terminal; no repair/retry; negative unchanged.
- **0 observed native PASS, 0 observed native FAIL; all 20 selectors NOT_RUN** by source-bound runner-gate inference. No native report; per-selector wall time unavailable.
- Bounded first failed stage `validate`: apt could not fetch Ubuntu packages because `archive.ubuntu.com` could not be resolved. This happened before the validation marker/Kani preparation/build/native invocation.
- Cloud steps: checkout/k1/upload SUCCESS, gate FAILURE/exit1. The k1 wrapper succeeds to permit upload; this is not Kani/compiletest build success.
- Request `faefa40aa4777ecd13a9813f26bd91d7b44b75bf35195523da254674176f45a8` and patch `c9ddce47cae76e9b9f462e8bcac94c73f70c0e8c32438f35f9ff1d7539117767` match published exact B. Production `3d085249c9c6c49a9c2e5747e2167d629748fb70` unchanged.
- Native pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; preflight tree `8f152bac27f8ff1d7fba45f57dc6a0ebeb348867` PASS. Runtime applied tree/build/binaries UNKNOWN: no summary. Local Git lane identity equals KT2 `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`; runtime bound hashes unavailable.
- Build wall **69.565 s**, queue **55.519 s**. B spend **$0.0270** (2 rounded min × $0.0135), reserved $0, separate B cap **$0.80**. A-family actual **$0.4860** remains unchanged.
- Brief exit1 HTTP404; `k1g.sh summary` exit2 reports no summary and bounded validate setup diagnostics. No raw fallback; independent B1/B2 credit NONE.

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

- NOT_RUN basis: pinned `gcb-k1.sh:46–52` installs python3/git before creating valid; apt failure exits validation. prepare/deps/build/verify require valid/build.ok. This is source/diagnostic inference, not a native result; absence of summary alone is not the basis.
- **Failed Checks:** unavailable; **compiletest `expected output to contain`:** unavailable. No compiler/verifier/assertion failure inferred from a setup/DNS failure.
- Exact bounded example: `E: Failed to fetch http://archive.ubuntu.com/ubuntu/pool/main/m/media-types/media-types_10.1.0_all.deb  Could not resolve 'archive.ubuntu.com'`.
- Receipts: `G1B-BUILD-METADATA.json`, `G1B-BOUNDED-SETUP-RECEIPT.json`, `G1B-OBSERVATIONS.json`; no raw logs/archives/credentials read. Prepared B request/patch/goldens and A/negative history preserved. Stop for coordinator review.
