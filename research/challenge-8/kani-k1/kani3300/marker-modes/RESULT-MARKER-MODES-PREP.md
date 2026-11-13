# MARKER-MODES preparation — worker15, 2026-11-13
Status: PREPARED_FOR_COORDINATOR_REVIEW_AND_CI (resumed scope).
Coordinator accepted §2 STOP and deferred marker diagnostics to separate work.
Design follow-up: [REQUIRED-STATE.md](REQUIRED-STATE.md), retained unchanged.
Source base: ee2695e5a2c4c2d8ead7a511e0f3f6f2a9a95677.
Source clone/branch: /root/kani-fix-3300-marker-modes, fix/kani-3300-marker-modes.
Source SHA: see INPUTS.json.source_commit.
Public docs now exclude Replace/RecursiveCheck shadow transfers from Part1 claims.
Docs explicitly defer marker diagnostics and link the accepted design note.
contract.rs and all compiler/runtime semantics remain unchanged.
Prepared Replace and RecursiveCheck fixtures, each with Assert/SimpleCheck companions.
Six roots include valid new/uninit storage, helper/return, requires/ensures paths.
Recursive root has depth 0/1, actual self-call/reentry, explicit unwind 8 and path covers.
No failure golden guessed; particular boundary SUCCESS is preserved without qualification.
JSON collector retains complete outcomes/failure sets and marks transformed binding pending.
Unsupported/frame/unreached-path gaps do not establish a semantic boundary.
13 synthetic Python tests PASS; static scope/manifest audit PASS; scratchpad rustfmt PASS.
Rust compile/typecheck and all six verifier roots: NOT_RUN; actual bindings: BINDING_PENDING.
No reproduced boundary/lawful prefix/per-root emitted property mapping claimed before CI.
Exact source changed files and read-only type/API audit: REVIEW.md / TYPE-AUDIT.md.
CI-REQUEST.md proposes six roots, unwind 8, 120s harness/180s outer caps, b12; approval pending.
Shared gate with worker14 and one agreed Quick/new suite remain coordinator-owned.
No blanket guard/exemption, private-target change or semantics rewrite; worker14 untouched.
No local cargo/rustc/Kani/CBMC/Miri/builds, push, CI or raw evidence read; Cloud $0.
