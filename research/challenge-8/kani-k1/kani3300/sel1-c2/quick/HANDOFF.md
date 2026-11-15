# SEL1-C2 worker15 — P review PASS, Q READY

2026-11-15. Input g0 aa9074c6f5, worker14 handoff273c619231; task sections2–3 only.
Independent read-only review: [PASS](../review/REVIEW.md), no blocking findings;
own bounded seam audit17 contracts/36 calls,34 changed Rust files, ten synthetic tests PASS.
Worker14 code and port/ unchanged. Native fmt/build/clippy/LLBC/Kani/CBMC and Q are **NOT_RUN**.
No push, dispatch, local build/setup, Cloud spend or new proof credit.

| Identity | Exact value |
| --- | --- |
| Reviewed source | `14bc57fdb99960240c4944845a3d985c8af4dcf7` |
| Source tree | `1efb6e4dfa69d346df8e23741d11839b1932403d` |
| Source parent | `8e299aa6243bc5f06a29c51e98aafa9564478220` |
| Q overlay | `4ef74e822b090109c391ebc723c4092690679e57` |
| Q overlay tree | `0833589f2ddf801542c5ac4f5fb7fb198fbbabb1` |
| Overlay parent | exact reviewed source above |

Worktree /root/kani-fix-3300-sel1-c2-w15, branch ci/kani3300-sel1-c2-quick-w15, clean.
Single CI-only commit, author/committer Tiramisu-Cake <igkharin@gmail.com>, [skip ci].
Only .github/c2-slices/ and .github/workflows/ differ from source. Stock workflows removed
only in overlay; one enabled workflow_dispatch, fork-only workflow remains.
Independent control/export sibling checkouts and external evidence preserve source/workspace boundaries.
Manual dispatch availability on fork/default branch is coordinator work; no push trigger was added.

Q uses accepted slice-07 recipe8288537e7c57b04d2462ff0c5bf1af38ab9d4451, run43723531871 as ancestry only.
All471 original selectors/directives/identities/ignores retained, plus all29 corrected SEL1 controls
(12 intended SUCCESS,17 intended failure/refusal). Static candidate discovery gives500 unique selectors:
kani53 (50+3 ignored), expected408 (402+6 ignored), ui17, script3, json17, std2.
All76 native compiler unit names independently reconstructed from candidate; targeted groups total28.
SOURCE-BINDING.json binds1097 files including source, units, fixtures/helpers/goldens, setup and pins.
Runtime source guards verify all non-CI source entries before/after. Native discovery/execution NOT_RUN.

S5 four mutation bytes/oracles unchanged; all four git apply --check PASS on actual candidate.
F7 structural source, manifest and comparison logic unchanged:11 invocations/18 exact comparisons.
Correction of inherited prose only: manifest has **7 expected exit1 invocations** (3 isolated +4 mixed),
not the five in old template/historical summary. Existing manifest/exits were not changed.
Quick caps unchanged: job120min, threads2, compiletest2400s/test, S5 2400s/variant,
structural180s/invocation, retention14d; no extra byte/RSS cap in accepted Quick.
No JSON DRIFT exceptions or added ignores/check disables. Nested refusal remains pre-select UnionAsField;
absent/overridden fallback/unsized T remain static-only. 29/0 is compiletest count, not29 legal proofs.

Package: CI-REQUEST.md/json, CI-OVERLAY.json, LOCAL-CI.json, SOURCE-BINDING.json,
receipt-template.json, TEMPLATE-INVENTORY.json and full-export/ bind these exact identities.
ci-only-template.patch keeps its legacy filename but contains the **final bound** source→overlay diff.
rebind_quick.py reconstructs candidate inputs; validate_bound.py validates committed package.
VALIDATION.json: PASS_STATIC_AND_SYNTHETIC_ONLY. Synthetic tests: Quick10, S5 13, F7 15, seam tool10.
Earlier unbound validation preserved in PREPARATION-VALIDATION.json and g0 aa9074c6f5.

Next: coordinator reviews exact workflow/binding, publishes source+overlay and runs Q once, without retry.
Missing/partial/setup/timeout/OOM/source drift/unexpected failures require STOP/review, never automatic PASS.
Only acceptance of complete Q permits declaring exact source freeze.
Gate A/B templates remain **unbound and NOT_RUN** at aa9074c6f5; not finalized in this session.
After Q acceptance/freeze: A binding/review, then B six unique rows. No A/B execution authorized here.

READY `4ef74e822b090109c391ebc723c4092690679e57`.
