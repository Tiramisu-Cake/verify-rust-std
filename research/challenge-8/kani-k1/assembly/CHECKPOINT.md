# ASSEMBLY — pre-build handoff

Worktree: `/root/verify-rust-std-kani-assembly`.
Branch: `experiment/kani-k1-assembly-20261031`; initial HEAD `ddcc33f837`.
Library commit `a4b4a3ca33653f5563e2cc57be6e2a6f58c493b9` (pushed).
Library tree `3548f769bc3c1c68ff7aa01c56e100ba0f27fbb7`.

No builds submitted. Own spent/reserved USD0, ceiling USD3 and 3 builds.
No GO yet. Task requires ending turn after PRE-BUILD REVIEW and waiting for coordinator GO.
Stable N6/N7 are prepared but gated pending coordinator confirmation of BACKING2 SUCCESS.
C u64 N6/N7 therefore stay ordinary; N8 is retired. Static ordinary182/all463.
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
Inventory ordinary30min, controls50min, measurement five controls each10min; setup30min/build.
Keep a separate build UUID/request_id ledger; shared agent label is not a cost boundary.
Only await builds via `k1g.sh watch BUILD` and end the turn.

After GO: ordinary inventory and controls inventory as separate builds; exact-name set
comparison against scope/ordinary.txt and all manifest.tsv names, respectively.
Then measurement of the five controls. For both count controls verify summary location:
only FAILED is count-assert merge.rs846 in assert_sorted_and_probe_preserved; sortedness844
must pass. Placeholder-message alone does not establish the expected oracle failure.
Report actual locations/results after measurement; current locations are expectations.
Only bounded K-1 summary/peaks/inventory/log-grep/log-lines/check-tooling; no raw evidence.
No local Rust/cargo/Kani/CBMC, no lane or toolchain changes, no submission branches.

Final completion only after requested evidence, report ≤100 lines, commit + push.
Do not emit ASSEMBLY ЗАВЕРШЁН while builds/inventories/controls remain unperformed.
