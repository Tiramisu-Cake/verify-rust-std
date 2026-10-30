# ASSEMBLY — COMPLETE, candidate ready for coordinator review

Worktree `/root/verify-rust-std-kani-assembly`, branch `experiment/kani-k1-assembly-20261031`.
Library commit `d4e5a0907b4d3e73b251afbc32b1bcdca58c8b18`.
Frozen library tree `954e0becf8cb6c137ea89f94ad613d83d97235e0`.
Coordinator GO for `74f064bad9`: go.json. No library edits after GO.
All six direct u64 N6..8 ordinary, C u64 N6..8 retired; no Part2 micro-package.
P1 ordinary182, native controls cfg463. P2 ordinary339/controls463 is a static forecast.
Retired16, pending0, expected-fail controls31; historical A-u64 remain opt-in outside P2.

All three Cloud Builds SUCCESS, summaries COMPLETE/gate true, tooling PASS against GO source.
G1 ordinary inventory: exact182-name set, no duplicates/missing/unexpected.
G2 controls inventory: exact463-name set, no duplicates/missing/unexpected.
Request/source/Kani/artifact/names hashes and complete bounded-page coverage verified.
Native inventory validation confirms enumeration, not positive verification or performance.
G1/G2 inventory memory/time fields MISSING. Targeted unused/dead_code/SmallSort warnings no match.
G3 targeted query shows only intended failure locations; old manifest/core unstable warnings remain.

G3 measurement: five intended FAILED, each exactly one check, each covers1/1.
Both count failures at merge.rs846 in assert_sorted_and_probe_preserved.
Sortedness source assert844 is not FAILED; terse output does not print explicit SUCCESS for it.
Both unsorted-halves failures: smallsort.rs842 merge_inputs_are_sorted requires.
Bounds: raw one-past-whole-allocation write, ptr/mod.rs1981; no safe indexing substituted.
Manual review and exact source binding in g3.controls-review.json.
Kani exit1 is expected for these negative controls. Uninit checks off; no full/generic proof claim.

Build / request source / UUID:
- G1 b84e992edf / 9fbe5d64-ff03-4fb4-a0d9-9ec92687e3d6
- G2 cb04aa5df6 / 8d168cb0-f60f-41b1-8a8b-8822a2c7a59b
- G3 a48fd96b6a / b1cc9973-6a7d-4471-8e9f-6b5002a0c36f
All three watches delivered; no pending build or watch, no further build quota.
Final selected-UUID ledger: spent USD1.2960, reserved USD0, budget USD3.5, builds3/3.
Individual costs: G1 USD0.5535, G2 USD0.6210, G3 USD0.1215. CAP_USD73.96 unchanged.
Original T0/deadline/closing reserve preserved; evidence review completed within the window.

Report RESULT-ASSEMBLY.md <=100 lines; final-check.json binds completed checks and report.
Not checked: native P2 inventory, macOS, jobs3 on final suite, organizers' full CI.
Positive transplanted harnesses were not reverified by these builds; full CI belongs to coordinator.
Only bounded K-1 readers used; no raw archive/log bypass, no local Rust/Kani/CBMC,
no lane/toolchain/flag changes, no submission branches, Actions or CircleCI.

No work remains for this ASSEMBLY session after final commit/push and review-request markers.
Do not resume after the final completion marker.
