# READY_FOR_ADOPTION — v4 NOT MIGRATED

2026-10-12. Owner-authorized preparation and conditional migration; Cloud budget
**0**, no Build submit/cancel, no IAM/quota/credential/trigger/ledger change.
Portable reviewed code commit:
**3bf951e5fae4a34df48854f1e215dd881eb8658f**.
Coordinator SHA256:
**66908c8ce4c363abf463b1067f356a61955d123af0bb05a7229dafd4749543d4**.
Implementation/procedure: [PARALLEL-BUILDS-V4](../PARALLEL-BUILDS-V4.md);
source/test identities: [REVIEW.json](REVIEW.json).

## Actual state and external blockers

Live envelope remains **schema_version=3/max_active=3**. Initial snapshot empty;
later read-only snapshot contains merge reservation token
`dispatch-294183f77aa84c7497e9c24ed6c53c5e`, Build
`55f96a17-c581-4379-a207-7b3a802d363d`. These snapshots are observations, not a
reconciliation or permission to change/cancel that Build. Source snapshot stored
outside Git at `/root/refinedrust-feasibility-sources/v4-audit-20261012/LIVE-SNAPSHOT.json`.
No migration command ran; no production envelope/client was patched.

[ACKS.json](ACKS.json) records actual installed hashes and **MISSING** v4 ACKs.
The three existing clients still carry coordinator SHA256
`49464b5a1078c99f8f44ef0bba06bb285c039ca0a0ab10d104bc7b54f32cb4bc` (v3).
RefinedRust has an unregistered G1 proposal, not a provisioned reviewed dispatcher.
Consequently the four-client precondition is absent. Old v3 ACKs cannot be reused.

| Owner | Addressed own adoption target | Required external action |
| --- | --- | --- |
| select-sort4 | /root/verify-rust-std-select-night | Finish its dispatcher command, independently adopt portable files, publish own infra SHA, supply reviewed-baseline receipt + exact v4 ACK |
| merge | /root/verify-rust-std-merge-origin | Same; preserve active Build pins, current ledger and all phase registrations |
| verifast | /root/verify-rust-std-verifast-upstream-l | Same; keep maintainer control.py/recipes/pins |
| refinedrust-feasibility | Separate own actual client, not a peer alias | Provision/review existing-dispatcher-based client without granting a phase/budget; then adopt and issue its own receipt/ACK |

Delivery artifact for each owner: [ADOPTION.patch](ADOPTION.patch) and portable
commit above. This is the addressed handoff; this session has no messaging
channel to the other active owner sessions and cannot manufacture their ACKs.
Only four portable files change, **control.py is excluded**. Owners can fetch
the published commit and cherry-pick it in their own checkout, first reviewing
its four-file diff. A conflict/dirty tree requires their own resolution;
no reset/force-push or copying another owner's dispatcher.

Each owner chooses a distinct ancestor baseline containing its **byte-identical**
reviewed control.py, writes its own OWNER_REVIEWED_BASELINE receipt, publishes its
adoption SHA and invokes the read-only `ack` command in PARALLEL-BUILDS-V4.
The receipt is a human/owner attestation, not a program-generated safety proof.
AST calls are only sanity checks. ACK hash/installed source/committed baseline/
published branch tip are independently checked by the helper.

After all four ACKs: operator confirms runtime quiescence (including embedded
dispatcher loops), then runs the explicit migrate command once. The helper audits
visible control.py processes, revalidates source/ACKs under the existing flock,
reads live global API inventory using canonical project/account/configuration,
validates ID/token consistency/occupancy and atomically changes only envelope
version/capacity. Full JSON readback and each owner's tokens/Build IDs are required.
Any refusal leaves v3 intact. Do not use the historical v2→v3 helper on live v3.

## Evidence and limits

Independent built-in review localized legacy-read, origin, dispatcher-attestation,
process/API, and embedded Build ID defects; all addressed. Final changed functions
have no remaining blocking finding in that review scope. Synthetic v4 tests
**14/14 PASS**, existing v3 compatibility **4/4 PASS**; APIs mocked and all writes
under mission-prefixed TemporaryDirectory. Empty/active migration preserves all
fields; four slots, fifth refusal, duplicate owner/ledger/Build ID, unknown tokens,
corruption, stale/missing ACK/source, process conflict, API mismatch/overflow and
old-client fail-closed covered. No real four-Build overlap or live transition credit.

Read-only quota query returned Cloud Quotas API **SERVICE_DISABLED**; API was not
enabled. Actual project global Build/regional CPU capacity for four simultaneous
jobs **UNKNOWN**; public defaults are not project confirmation. This is a separate
provider gate, not a claim that the code can bypass Cloud quotas.

V4 does not authorize G1 or any new proof: separate recipe/profile/image/phase/
ledger/window/IAM permission and explicit budget are still needed. Historical
max3 owner-extension proposal in g1-minimal is superseded by this explicit v4 route.

Cleanup: removed only own infra-worktree `cloud-build/__pycache__/` files
`coordination.cpython-312.pyc`, `coordination-v4-transition.cpython-312.pyc`,
`coordination-v3-transition.cpython-312.pyc` and the empty directory after checking
no active FD/mmap. Freed **57344 bytes (56 KiB)** allocated blocks. Test temp dirs
auto-removed; foreign /tmp/shared caches/evidence/Git objects/state retained.
Before df: free2.3G/inodes20%; after: free2.2G/inodes21%, root96% used. External
cleanup receipt: `/root/refinedrust-feasibility-sources/v4-audit-20261012/CLEANUP.json`.

After own commit/push **STOP**. Current result is **READY_FOR_ADOPTION**, never
MIGRATED; required next actions are the four owner adoptions/receipts/ACKs above.
