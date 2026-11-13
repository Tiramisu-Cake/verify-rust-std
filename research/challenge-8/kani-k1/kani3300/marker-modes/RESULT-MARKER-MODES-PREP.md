# MARKER-MODES preparation — worker15, 2026-11-13
Status: STOP_REQUIRED_STATE_PREDICATE (task §2); not READY.
Research input: be5bdb511676c0f441662528c0b88aab9c3fe007, pull --ff-only up to date.
Source base/head: ee2695e5a2c4c2d8ead7a511e0f3f6f2a9a95677, clean.
Clone: /root/kani-fix-3300-marker-modes, fix/kani-3300-marker-modes.
Source patch/commit: none; source changed files: none.
Blocker: no established total wrapper-specific required-state fact for actual
local/delayed/transitive writes with clause/call-site/no-write/cut binding.
Global reachability/helper presence, uninit flag and failed call resolution are insufficient.
UNKNOWN was not converted to false or a blanket missing-state error.
REQUIRED-STATE.md gives exact source anchors, operation coverage and design handoff.
LOOKUP-CONTROLS.md records future resolver scenarios and read-only Rust API/type audit.
MODE-SCOPE.md records owner decision and source mode/transfer map; public text not applied.
No fixtures/goldens were staged after the prerequisite STOP.
Lookup units/integrations: NOT_RUN; mode bindings: BINDING_PENDING, verification NOT_RUN.
CI request: HOLD; exact executable roots/caps have not been approved.
No blanket guard/exemption, private target change or semantics rewrite.
No worker14 changes or dependency on its checker.
Python static audit only; not a compiler/type/model/verifier result.
No cargo/rustc/Kani/CBMC/Miri/build, CI, push or raw evidence reads; Cloud $0.
Next: establish/review bounded effect provenance and UNKNOWN policy before implementation.
