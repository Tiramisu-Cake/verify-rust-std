# Relevant upstream-main changes and transfer assessment

Approved main969f4648980a8e66cd0ca32fd3e714a55ac32cef is a single child of
old mainfaffcee3bca2770c03bd21c3bde89cc8f6f7a14e. Its subject is
"Upgrade Rust toolchain to nightly-2026-11-18 (#5188)". This accepted main source
is the clean-room input authorized by task09840da. No unrelated unmerged PR
implementation was consulted.

| Upstream area | Accepted change | Transfer assessment |
| --- | --- | --- |
| transform/contracts.rs AnyModifiesPass::is_enabled | contains(&"function-contracts".to_string()) becomes iter().any(|arg| arg == "function-contracts") | New string-membership expression retained; our hook is in FunctionWithContractPass::transform_instance, a separate hunk. No repair adaptation. |
| kani_middle/attributes.rs attrs_by_path | Removed rustc AttributeExt import and path_matches; filters using attr_path_matches for Tool/DeriveHelper segment equality | Entire file equals new main. Original selected instance/attributes lookup is retained; no bypass of PFC target reachability or metadata checks. |
| kani_middle/attributes.rs attr_value_str | Reads value_lit().and_then(|lit| lit.kind.str()) after removal of rustc value_str | Entire helper and its callers remain accepted upstream bytes. Our patch adds no rustc attribute API calls. |
| rust-toolchain.toml | nightly-2026-11-12 to nightly-2026-11-18 | Exact new-main file; no compiler or formatter executed. |
| kani-driver/Cargo.toml, Cargo.lock and driver session | chrono removed; profiling timestamp uses std UTC conversion | Exact new-main blobs, including all lockfile removals and new session code. No dependency resolution run. |
| library/kani/src/models/mod.rs | CustomMask SIMD Clone copies the whole value after new MIR projection restriction | Exact new-main library tree; no old library files restored. |
| Other compiler API/trait/type updates | no_graphics diagnostics field, TyKind::View unsupported cases, new generic float intrinsic names, feature membership cleanup and uninit fallback handling | All upstream path blobs retained. Only contracts.rs additionally contains our original hook; normalized upstream delta equality checks its upstream hunk too. |
| Workflows/scripts/actions | No content changes in this upstream commit | Inventories freshly parsed from exact969f object bytes, not assumed from faff. All16 and every native job/matrix remain unchanged. |

The old repaired patch uses rustc_public::mir::mono::Instance, existing FnDef
and TyKind/RigidTy tests, FnStubValidator::validate and KaniAttributes mode
selection. The new-main changes do not alter those touched APIs in the patch.
The exact old full patch applies cleanly without manual resolution. Both
candidate-delta equality and upstream-delta equality retain every content line
and hunk coordinate after removing only git index blob headers. This provides
a narrow source-level basis for zero additional compiler adaptations; it does
not establish successful Rust typechecking on the new toolchain.

Range-diff is recorded verbatim. Its ! marker comes from the changed commit
message; there is no content-hunk delta. TRANSFER.json pins the compared
objects/digests and inventories all31 upstream changed paths. The test/oracle
patch remains byte-identical to repaired r1, including direct-provider-positive
and copied-provider-negative discrimination. Whole and split new-base patches
are replayed to the exact new candidate tree in temporary Git indexes.

All current-main/fixed native tests, compiler, expansion and Kani/CBMC are
NOT_RUN. Old faff MRE observations and upstream source-reported test claims do
not supply current-main proof credit. Same11 must assess W11-01 and this new-base
transfer together before root can grant GO. No unresolved design choice or
additional semantic adaptation was needed during preparation.
