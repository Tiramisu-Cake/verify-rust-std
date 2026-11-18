# Timeout audit — r4-r2 approved-gate integration candidate

Final Validate: **PASS**, 380.011575s monotonic, 107 tests; command executed ONCE on committed control `d33a0900da19d865f20ccaa76e1ee27065c5a671`.
Actual check-source: **PASS**, 13.638509s monotonic, executed ONCE. These are this machine's measurements; future GitHub elapsed/timeout outcome UNKNOWN.

| Step | cap seconds (old -> new) | local elapsed seconds | decision |
|---|---:|---:|---|
| Begin setup budget | 60 -> 60 | UNKNOWN | Keep: one timestamp write; no enlarged workload. Origin is time.time() written inside this step, after runner/job initialization. |
| Checkout CI control | 120 -> 120 | UNKNOWN | Keep: same immutable control checkout at depth7; no measured checkout evidence justifies enlargement. |
| Validate control and synthetic wrapper | 60 -> 600 | 380.011575071 | Change 1 -> 10min: owner-authorized after run44328364855/1 step4 native FAILURE72s (PREBUILD_VALIDATION_TIMEOUT). Full offline final command measured separately; old partial tests are not suitePASS. |
| Read immutable export pins | 60 -> 60 | UNKNOWN | Keep: same READY request parse and two output pins; workload unchanged. |
| Checkout production model export | 300 -> 300 | UNKNOWN | Keep: unchanged source SHA/tree, checkout depth5, submodules; CI stage was SKIPPED, elapsed UNKNOWN. |
| Checkout immutable upstream tool | 120 -> 120 | UNKNOWN | Keep: unchanged stock tool SHA/tree, depth2; CI stage was SKIPPED, elapsed UNKNOWN. |
| Check all source identities | 60 -> 60 | 13.63850858 | Keep 1min: actual final check-source measured on this machine below60s, unchanged source and gates. GitHub time UNKNOWN; no evidence for increase. |
| Setup exact stock tool | 900 -> 900 | UNKNOWN | Keep15min: unchanged composite setup installs pinned rustup/dependencies and shallow submodules. No compiler/setup action executed locally; duration UNKNOWN. |
| Build exact stock tool once | 900 -> 900 | UNKNOWN | Keep15min: unchanged build wrapper limits execute to min(900,int(1800 - elapsed_from_epoch)); requires positive remainder and total<=1800, preserving aggregate gate. |
| Run S2 batch3probes with bounded observations | 7560 -> 7560 | UNKNOWN | Keep126min: proof step7560s and backend/group/RSS/resource caps unchanged. NOT_RUN. |
| Materialize bounded fallback | 120 -> 120 | UNKNOWN | Keep2min: protected fallback/packer unchanged, always(); no measured evidence for increase. |
| Upload bounded evidence | 360 -> 360 | UNKNOWN | Keep6min: bounded upload unchanged, always(); no measured evidence for increase. |

Aggregate setup remains1800s from the epoch written in Begin setup budget, including all following setup until build completion. Each actual preceding duration reduces build remainder; the wrapper permits at most min(900,int(1800-elapsed)). Start remainder<=0 or total>1800 fails. All other durations and actual CI remainder are UNKNOWN. Setup maxima sum3120s and all maxima sum186min are not actual elapsed or budget grants. Job remains180min; protected proof/resource caps remain unchanged.

Measured command sum 393.650084s; 1800 minus that sum is 1406.349916s only in a hypothetical zero-other-overhead replay, not CI remaining budget.

The unchanged composite tool setup installs Rust/dependencies and updates shallow submodules; inspected only. No evidence supports increasing its15min or build15min caps. No compiler, tool build, full runner or CI executed.

Old run44328364855/1 remains PREBUILD_VALIDATION_TIMEOUT (native step4 FAILURE72s), later source/build/run SKIPPED,0roots, charge0 (ledger a487 reference only). Partial tests do not establish suitePASS.

R14-03 CLOSED in exact gate-only ccb6 review; approved gate bytes integrated and explicit CI module wired. Final combined delta review PENDING. Previous GO exception is spent. SAME14 final delta review must precede a separate root GO request; no exception transfer from prior one-run GO.
