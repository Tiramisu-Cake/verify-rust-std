# Coordinator-only CI request — KANI3300 B3R2

No dispatch is authorized in this worker session. Cloud spend is $0. Candidate is
local-only 495614a5ee331398fde83b6db7684ff201a62c39 (tree f92c801ad9a23aabaf70e2f422e0f0aa987d6351); sole parent
bf9c58e662fd65c64381ef2ac97a6397ffc0693a. Only coordinator pushes/runs Kani CI.

## Same-source targeted comparison

Production pins:
- base: bf9c58e662fd65c64381ef2ac97a6397ffc0693a
- v2: 83a413f9be2d57389c991d9f5d1250b4e4386203
- v3: 495614a5ee331398fde83b6db7684ff201a62c39

Use identical manifest-hashed A/B/new C sources on all three. `tests-on-base.patch`
and `tests-on-v2.patch` contain tests only, including the preserved seven controls
where absent and identical B sources under b3r2-probes/. Their SHA256s, complete
changed-path inventory and temporary-index result trees are in TEST-MANIFEST.json.
Both pass static apply checks against their exact pins; no existing branch was
changed. Apply in disposable CI checkouts without altering production inputs.
For v3 use committed active fixtures and byte-identical research probes copied
from probes/ to b3r2-probes/. Preserve input hashes and record actual source/tool
versions, target, environment/config, arguments and output/evidence identities.

Use the ordinary `kani file.rs` invocation with default checks, one input at a time;
no new runner/framework, unstable uninit checks or special success filtering.
A: tests/expected/zst-union-recursive-arm/main.rs and
   tests/expected/zst-union-recursive-zst-arm/main.rs.
C: all five tests/expected/zst-union-edge-*/main.rs, separate harnesses/inputs.
B: b3r2-probes/tail_bytes_first.rs, tail_first.rs, tuple_first.rs.
Old controls: tests/expected/zst-union-arm/main.rs, all seven unchanged harnesses.
Desired semantic outcome is SUCCESS for every input; no base/v2/v3 result is known.

## Required observations per harness and pin

Record setup/compiler/CBMC/verdict/cover/exit/exception separately. Preserve actual
exit code, exception and original failure stage even when workflow state differs;
setup failure, unavailable, cancelled, timeout and missing evidence are not PASS.
Do not invent property IDs/counts; collect exact emitted IDs/descriptions/results.
Each new A/B/C harness has a distinct cover description in its source/manifest;
require its own SATISFIED plus all correctness/default checks, not one global SAT.
Covers do not replace assertions, type binding or source-stage attribution.
Preserve individual original-seven results; they have no new cover properties.

For A, confirm actual retained Node/Node2-first recursive graph, union entry and
positive wrapper padding (Node small: union width minus pointer width; Link marker:
64 bits); Node width is target-dependent. Root must not pre-codegen U/Link through
values, size_of or a union-typed helper. If v2 ICE occurs, bind it to the original
source/type walk and diagnostic. If not reproduced, report retained graph/order and
UNKNOWN cause; do not declare the static hypothesis disproved without that binding.

For B, collect full observed outcomes on both Tail field orders and tuple first:
rustc union/arm widths, wrapper padding 56/0 bits, retained nested ZST, typed copy
and post-copy initialized data read path. See ASSESSMENT-B.md. Workflow success
alone is insufficient. Base PASS -> v3 FAIL/ICE is a regression blocker. If base
and v3 fail, a separate repair or measured limitation is required. If v3 passes,
active promotion/observed goldens are decided in a subsequent session.

## After targeted matrix

Run existing coordinator format-check/build/clippy/regression/verify-std jobs on
the exact candidate head, preserving platform distinctions. Record unavailable or
cancelled jobs as such. Use existing suites/options, including original seven
default controls; do not expand into the separate uninit-checks panic repair.
Return measured results with exact SHA/tree/input hashes. No old v2 CI acceptance
is inherited by the new tree, and no source-reported outcome is independent proof
credit. B3R2 worker stops at reviewed local handoff and does not wait for this CI.
