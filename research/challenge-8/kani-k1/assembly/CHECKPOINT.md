# ASSEMBLY — GO received, inventory dispatch

Worktree `/root/verify-rust-std-kani-assembly`, branch `experiment/kani-k1-assembly-20261031`.
Initial HEAD `ddcc33f837`; latest library commit `d4e5a0907b4d3e73b251afbc32b1bcdca58c8b18`.
Library tree `954e0becf8cb6c137ea89f94ad613d83d97235e0`.

Coordinator explicitly confirmed BACKING2 general N7 and stable N6/N7:
SUCCESS, covers1/1, checks0/407, CBMC<=0.99GiB; source30b8b975c5/libraryf28909ac02,
build33e2c5fd-27ba-4cdb-89f9-474f51a3ac39. Record: backing2-confirmation.json.
All six direct u64 N6..8 are ordinary; C u64 N6..8 are retired duplicates.
Static Part1 ordinary182/all463; pending0/retired16. Part2 ordinary339/all463.
Combined B u64 N6/N7 remain retired; historical A u64 N5..8 remain opt-in outside P2.
No Part2 micro-package. Historical results do not prove the assembled candidate tree.

All 3/3 builds submitted; no further build quota. Own ledger builds.json: full-envelope
reservation USD3.105, cap USD3.5. Refresh actual spent/reserved through k1g.sh budget UUIDs.
Coordinator GO for 74f064bad9 is recorded in go.json; library stays frozen.
Immediate next action: register k1g.sh watch for all three UUIDs and end turn.
On watcher notification, read only the completed UUID's bounded K-1 evidence.
After GO freeze this library tree for all three requests; a library edit needs delta-review.
Do not reverify positive transferred entries here; coordinator runs the full CI.

Regenerate library using assemble_library.py --backing2-confirmed; rustfmt required afterwards.
Recorded confirmation also enables that mode by default. Regenerate research using:
assembly/prepare_scope.py, scope/prepare_pr2.py, scope/check_scope.py and scope/check_helpers.py.
All commits [skip ci], library separate from research, push without force.

RUN-REQUEST is the ordinary inventory candidate. Other validated requests are in this directory.
Plan: separate ordinary30min and controls60min inventories, then five controls each10min,
measurement jobs1/controls:true; setup30min per build. Maximum own reserve USD3.105.
Inventories may be dispatched together; each build needs its own source SHA/request_id/UUID.
Fresh k1g.sh budget and remaining-window check before each dispatch. CAP_USD73.96 unchanged.
T0/deadline and closing15min reserve are in window.json; never reset the window implicitly.
If the next full envelope does not fit, report PARTIAL with exact remaining time/budget.
Only await builds via k1g.sh watch BUILD and end the turn.

Compare exact inventory name sets to scope/ordinary.txt and all manifest.tsv names.
For both count controls: exactly one FAILED at count-assert of the shared oracle,
using actual final summary location; no other FAILED. Absence of sortedness failure in
terse output is not an explicit SUCCESS line. Check all five controls' covers.
Unsorted-halves: merge_inputs_are_sorted; bounds: raw write outside whole allocation48.
Do not accept compile/unsupported/TIMEOUT as expected failures.
Bounded K-1 summary/peaks/inventory/log-grep/log-lines/check-tooling only, no raw logs.
No local Rust/cargo/Kani/CBMC, lane or toolchain changes, or submission branches.

Final completion requires inventories, controls, report <=100 lines, commit + push.
Do not emit ASSEMBLY ЗАВЕРШЁН while required evidence remains unperformed.

Submitted builds (source SHA / request_id bindings in builds.json):
- g1 inventory controls=False: 9fbe5d64-ff03-4fb4-a0d9-9ec92687e3d6
- g2 inventory controls=True: 8d168cb0-f60f-41b1-8a8b-8822a2c7a59b
- g3 measurement controls=True: b1cc9973-6a7d-4471-8e9f-6b5002a0c36f

After each watch notification: bounded summary, inventory/peaks as appropriate,
check-tooling against GO source74f064bad959b6a38369bbed43e7a11f114b81b6, warning grep.
Compare exact names for g1 ordinary182 and g2 controls463. For g3 manually inspect
all five FAILED checks/locations/covers, especially the two placeholder count failures.
Do not treat placeholder match as count-oracle acceptance; report final summary locations.
No library changes or extra builds; any needed delta goes to coordinator review.
