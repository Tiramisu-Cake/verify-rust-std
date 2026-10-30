# ASSEMBLY — pre-build handoff

Worktree: `/root/verify-rust-std-kani-assembly`.
Branch: `experiment/kani-k1-assembly-20261031`; initial HEAD `ddcc33f837`.
Library commit `b153898c85aeeac5deba54951b9aa7f17a40332f` (pushed).
Library tree `2976c90fc67d06bfe64119828ed0c5ea12653b48`.

No builds submitted. Own spent/reserved USD0, ceiling USD3.5 and 3 builds (TASK-ASSEMBLY-NOTES).
No GO yet. Task requires ending turn after PRE-BUILD REVIEW and waiting for coordinator GO.
General N7 and stable N6/N7 are prepared but gated pending coordinator confirmation
of BACKING2 exact source/library SHA and SUCCESS/covers (NOTES p1).
C u64 N6/N7 therefore stay ordinary; N8 is retired. Static ordinary181/all463.
Do not infer the confirmation from the historical BACKING2 summary alone.

Regenerate the manifests after a library change with scope/prepare_scope.py,
scope/prepare_pr2.py, scope/check_scope.py and scope/check_helpers.py (Python only).

Only after explicit confirmation, the prepared promotion can be applied with:
`python3 research/challenge-8/kani-k1/assembly/assemble_library.py --backing2-confirmed`
Then rustfmt both changed files, audit, commit library separately, regenerate scope,
update report/rename map/checkpoint identities and obtain review on the new candidate.
All commits require `[skip ci]`; push without force.

The current RUN-REQUEST is the ordinary inventory candidate. The other two validated
requests are in this directory. Each dispatch needs fresh `k1g.sh budget`; own worst
three-build reserve USD2.97. Respect global CAP_USD73.96 and k1-standard4.
Inventory ordinary30min, controls60min, measurement five controls each10min; setup30min/build.
Keep a separate build UUID/request_id ledger; shared agent label is not a cost boundary.
Only await builds via `k1g.sh watch BUILD` and end the turn.

After GO: ordinary inventory and controls inventory as separate builds; exact-name set
comparison against scope/ordinary.txt and all manifest.tsv names, respectively.
Then measurement of the five controls. For both count controls verify summary location:
only FAILED must be the count-assert in assert_sorted_and_probe_preserved at the
actual final summary location. No other FAILED; terse absence of sortedness failure is
not an explicit sortedness SUCCESS line. Check covers. Placeholder-message alone does not establish the expected oracle failure.
Report actual locations/results after measurement; derive them on the final SHA.
Only bounded K-1 summary/peaks/inventory/log-grep/log-lines/check-tooling; no raw evidence.
No local Rust/cargo/Kani/CBMC, no lane or toolchain changes, no submission branches.

Final completion only after requested evidence, report ≤100 lines, commit + push.
Do not emit ASSEMBLY ЗАВЕРШЁН while builds/inventories/controls remain unperformed.

NOTES: combined B u64 N6/N7 are retired duplicates; historical A u64 N5..8 stay
opt-in outside P2. Recomputed P2 ordinary338/all463. B corruption control now has
a pre-failure reachability cover; oracle unchanged. After GO, freeze this library tree
for all three requests; any further library edit needs delta-review.
T0/deadline and 15min closing reserve: window.json. Recheck full next envelope before dispatch.
