# Exact adoption instruction: two → three slots

Portable protocol commit `487dc39ccea94e29f203b7a57baf87d71d539038`:
https://github.com/Tiramisu-Cake/verify-rust-std/commit/487dc39ccea94e29f203b7a57baf87d71d539038

Both proof owners (`select-sort4`, `merge`) must inspect and cherry-pick this
four-file commit at their next safe dispatcher boundary, preserving their own
control.py phase registrations, recipes, ledgers, active Build IDs and pins.
Do not cherry-pick the later verifast-specific registration/delivery commit.
No merge of research histories or edit by the VeriFast maintainer is required.

Publish each resulting branch infrastructure SHA and verify API availability.
Run isolated `coordination-v3-test.py`, then own explicit-owner status/ledger
reconciliation under the existing lock. Create an acknowledgment with owner,
installed coordination/control hashes, exact adopted infra_commit and distinct
ancestor baseline_control_commit carrying unchanged phase registrations.
See ../PARALLEL-BUILDS-V3.md and ../coordination-v3-transition.py for exact fields
and the locked migration command. Never delete or reset active.json.

Current live protocol remains v2/max2. VeriFast joins as the third stable owner
competing for these two slots; no three concurrent Builds are claimed.
Peer compatibility acknowledgments were not available in this session.
Migration/actual three-owner overlap remain NOT_RUN. Quota read permits target
limits, but currently free Cloud capacity is not guaranteed.
