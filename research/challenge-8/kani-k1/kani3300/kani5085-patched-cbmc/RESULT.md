# KANI5085 replay — RESULT (coordinator, 2026-11-13)

Run https://github.com/Tiramisu-Cake/kani/actions/runs/43497661683 (CI-only eca29301eb on upstream Kani 0aac16ef62),
artifact downloaded to /root/kani5085-replay-ci/. Kani 0.68.0 upstream, unpatched; CBMC built from source:
base 107a1e504c (`CBMC 6.11.0 (107a1e50)`), fix 9f2d01ec (`CBMC 6.11.0 (9f2d01ec)`), same Release configuration.
Kani log of every case shows the selected CBMC version string, so the shim binding is confirmed.

| Root | base (107a1e50) | fix (9f2d01ec) |
|---|---|---|
| static_zst_arr — #5085 reproducer verbatim (`static S: ([[u8; 0]; 2], u8)`) | CBMC abort, status 134 (bits2expr invariant) | VERIFICATION:- SUCCESSFUL (0 of 7 failed) |
| const_zst_arr — same with `const` | CBMC abort, status 134 | VERIFICATION:- SUCCESSFUL |
| tail_typed_copy — typed copy of `Tail { u8, [(); 2] }` | CBMC abort, status 134 | VERIFICATION:- SUCCESSFUL |
| tail_nondet — nondeterministic bytes (lowering path) | SUCCESSFUL | SUCCESSFUL |
| runtime_control | SUCCESSFUL | SUCCESSFUL |

Note: the replay classifier labelled fix outcomes `OTHER_FAILURE` because the raw CBMC exit is 10; the only CBMC FAILURE is
Kani's own `reachability_check` instrumentation, which Kani post-processes; the Kani verdict is SUCCESSFUL. Classifier bug, not a result.
