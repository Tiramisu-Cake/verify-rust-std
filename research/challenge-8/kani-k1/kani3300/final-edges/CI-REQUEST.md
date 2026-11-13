# E1 coordinator-only qualification request

Prepared source dc24745c68951effb702a4302e84481ca74bc51a, tree
4e17cba9a9ae0bbc625f5fc6c147ff1cca17dc04, exact parent 94c00a8859bc9e4f0f1b7db73a95dbee88f6213a.
No dispatch authorization or Cloud spend. Coordinator owns source transport, push, CI and caps.
No CI overlay is part of this source export. Check manifest/hash identities before each stage.

1. Existing coordinator build/preflight/typecheck on nightly-2026-10-23 and its pinned target.
   Run compiler unit `argument_size_tests::transfer_requires_complete_sized_storage` in CI.
   Compile all new fixtures; any E0277/ICE/preparation failure stops the affected qualification.
   Source compilation failure is not a by-value DST runtime-model guard test.
2. Tiny singleton controls, one Kani job/solver at a time, selected with `--exact --harness ROOT`.
   Inputs/roots and semantic expected complete failure sets are CONTROL-MAP.json. Run legal
   before its matched hole; constant and variable unions side by side, then raw field legal,
   neighbor/padding holes, immutable categories, by-reference and by-value DST. Use existing
   default solver/slicing/checks/resource capture; no global profile relaxation. Proposed cap
   120s/root, outer180s including compile, subject to coordinator controls and budget. Preserve
   the accepted per-test object-bits12 policy for heavy inherited PFC tests/eight oracles.
3. Capture full, consistent regular plus JSON 0.1 export inventories using existing export-json
   support/shared validator. Preserve original exit/signal/cap/RSS, source hashes before/after,
   actual argv/env/cwd, compiler/driver/sysroot/CBMC/solver identities, model/GOTO and selected
   MIR identities. Each invocation has its own fresh output. Goldens match substrings only;
   they cannot establish exact failure sets. Review all IDs/statuses/class/descriptions/locations,
   active Unsupported, successful and UNREACHABLE checks. Missing/partial/malformed inventories,
   timeout, arbitrary FAILED or an earlier unrelated Unsupported never qualify a negative.
4. Bind ordinary union Constant versus Copy and allocated masks, field-write Deref/Field/place
   type/offset and exact SetRef range, immutable carrier/referent allocation ID/provenance/offset/
   extent/masks/admission (or independently identified static initializer path), and DST by-value
   Slice/Move(Deref) argument before transfer. Verify guard ordering relative to ANY begin/load/
   store/deinit in caller and callee. Obtain bounded exact typed windows through authorized
   evidence interface; source names and root metadata alone do not establish these bindings.
5. Every legal/supported companion has zero failures and reached useful checks/assertions.
   Every hole has exactly its intended source-bound uninit failure with no additional failed
   initialized-byte reads, assertions, Unsupported or model invariants. By-value DST legal and
   hole each have only the exact unsized-transfer Unsupported, no transfer side effect; that
   diagnostic is a limitation, never proof PASS. Unrelated earlier guards leave the edge OPEN.
6. If immutable subrange/relocation/shared-static legal paths falseFAIL, retain their SUCCESS
   expectations, record the failure class and full set, mark the corresponding hole unqualified,
   and return release HELD for coordinator scope/limitation disposition. Do not seed/bless new
   origins, reseed mutable copies or change goldens to expected UB. All named statics must not
   be rejected as a category: identify independent existing paths separately.
7. After targeted acceptance/disposition, run unchanged legal PFC/ordinary companions and all
   eight strong JSON oracles (p1, ordinary, pfc, lawful-modifies, p2, postcondition-hole, frame,
   clause) using the existing scripts/bindings unchanged. Include CC1 real-cycle Unsupported,
   CC2 slots, CC3 closure/upvar layout, M1 Some(0)/None masks, S3 body selection and typed-data/
   padding/reset/transfer controls listed in CONTROL-MAP.md. Then run existing Quick on the
   exact candidate/integrated source; no new expected weakening. Preserve every regression,
   ICE, missing check or unexpected failure as STOP. M3/fullgate/replay are separate later tasks.

Actual tested source/tree, build/run identity, MIR/property binding, all failure inventories,
companion results and evidence selectors must be appended as new observations after CI by the
coordinator. Current values are NOT_RUN. Evidence Brief is the default for Cloud Build evidence;
no raw archives/full logs download or rewriting historical records/download_verified.
