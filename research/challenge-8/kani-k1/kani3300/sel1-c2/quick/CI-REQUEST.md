# Q — READY for coordinator review and one manual dispatch; NOT_RUN

Source `14bc57fdb99960240c4944845a3d985c8af4dcf7`, tree `1efb6e4dfa69d346df8e23741d11839b1932403d`,
parent C2 `8e299aa6243bc5f06a29c51e98aafa9564478220`. Independent P review PASS in ../review/REVIEW.md.
CI-only overlay `4ef74e822b090109c391ebc723c4092690679e57`, tree `0833589f2ddf801542c5ac4f5fb7fb198fbbabb1`,
parent exact source. Accepted recipe8288537e7 / run43723531871 supplies ancestry, no new runtime result.
Only coordinator publishes/dispatches; workflow_dispatch only, fork Tiramisu-Cake/kani, ubuntu-24.04,
one attempt, no retry. Review dispatch availability/default-branch workflow separately.

Separate sibling control/export checkouts; observer/artifacts outside source checkout.
Do not patch export to make tests pass. Production/tests/docs/std unchanged by overlay;
S5 performs accepted independent test/golden mutations and restores bytes/mode even on failure.

Required acceptance on this source:

- fmt/build/clippy --workspace --tests -- -D warnings and LLBC build, original exits0.
- All76 exact compiler units; targeted9 ActiveCalls +9 immutable +1 argument_size +1 marker_category +6 delayed_cache +2 delayed_scope.
- All500 unique selectors: kani50/0/3, expected402/0/6, ui17/0/0, script3/0/0, json17/0/0, std2/0/0.
  All471 inherited selectors and29 SEL1 controls mandatory, with original directives and existing ignores only.
- All29 exact SEL1 selectors/outcomes in full-export/.github/c2-slices/sel1-controls.json:
  12 intended SUCCESS,17 intended failures/refusals with original per-root goldens, useful checks and exact reasons.
  29/0 is compiletest acceptance, not29 legal proofs. Nested refusal is UnionAsField before select;
  missing/overridden fallback and unsized T are static-only.
- S5 4/4 DETECTED via completed intended native verdict/count plus golden mismatch; no setup/compile/timeout/unrelated Unsupported detection.
- F7 11 complete invocations and18 exact mixed-vs-own-isolated comparisons, unchanged source/manifest;
  original exit1 expected in7 invocations (3 isolated +4 mixed), validated against manifest.
- Exact clean source identities before/after, per-stage native names/counts, stdout/stderr and original exit/termination;
  source-owned JSON schema/validator and full failed/useful property inventories. No JSON DRIFT exception.

Caps unchanged from accepted Quick: job120min, Rust test threads2, compiletest2400s/test,
S5 process2400s/variant, structural180s/invocation, retention14d. Build/fmt/clippy/LLBC share whole-job cap;
accepted Quick has no extra RSS/artifact-byte cap. Artifacts/source-after use always(), missing artifact is an error.
No lower timeout, extra object-bits/arrays-uf/global check disables or new filters/ignores.

CI-REQUEST.json and CI-OVERLAY.json bind payload, workflow, manifest and1097 source file identities.
Native source/runtime/binary/solver outcomes remain unknown until CI. Unexpected nonzero exit, timeout/OOM,
lost runner, missing/partial receipt, source drift or unexpected failure means STOP/review.
After accepted Q only, coordinator declares this exact source freeze; A/B separate future stages.
