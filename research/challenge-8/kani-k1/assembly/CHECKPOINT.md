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

No builds submitted. Own spent/reserved USD0, ceiling USD3.5 and 3 builds.
Coordinator GO received for 74f064bad9; go.json records authority and frozen tree.
Dispatch ordinary and controls inventories, register watch for both, then end turn.
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
