# KANI3300 B1 static review

- Candidate: `835cb4a09c4e94ac6b531d20e68f9deee7262ce1`; tree: `4b426d96a0dc2f5b87bdbfe1c32f0e492e8461f3`.
- Base: `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`.
- Spec SHA256: `81b9d66c74564d28f8d7e499cd60630e0970cc45662731f634cbad44b48d9e87`; diff SHA256: `393f826b0f4d8552e3ec12cc4938aa43a2e774ee4b55d0ec1a28031b9dddf8b5`.
- Packet inventory hashes: all 14 listed files matched. `git diff --check` passed.

## Findings

None in the reviewed scope. In `uninit_visitor.rs:263-272`, each Call invokes `super_terminator` once; resolution errors append Unsupported and fall through to the common target publication at line 457, preserving operand operations and empty-block entry loads. The `InstanceKind` match at lines 274-413 explicitly handles Intrinsic, Item, Virtual, Shim, and LlvmIntrinsic. Virtual and unsupported non-Item cases receive a local Unsupported diagnosis. In `delayed_ub/instrumentation_visitor.rs:94-110`, the duplicate unsupported-call diagnosis is removed, leaving the local uninit visitor as the owner independent of delayed-UB targets.

Regression sources cover direct positive calls, empty-entry initialized/partial union controls, pending dereference checks, FnPtr/erased/wrapped pointers, virtual calls, global escaped pointers, and Shim calls, with plain and seeded variants for each group. Expected outcomes distinguish initialized reads (SUCCESS) from partial/uninitialized reads (FAILURE), while unresolved calls report the intended Unsupported diagnostic. The legacy `delayed-ub-unsupported-call` golden is unchanged. The changed Rust and test sources contain `-D warnings` compile flags; static inspection found no evident warning hazard.

## Verdict and limits

**PASS — static review of the stated B1 scope.** No local cargo/rustc/Kani/CBMC or builds were run. Expected files were reviewed as expectations only; no runtime outcomes, test execution, or proof credit are claimed.
