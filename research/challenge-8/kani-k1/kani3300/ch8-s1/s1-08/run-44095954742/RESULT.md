# S1-08 intake13 — READY for separate offline acceptance

Run44095954742/attempt1 is terminal **failure**, exact head21592884db439389364b416dea1515bfa9d8018e,
reviewed tree7ba8030690596cb491d1ae4f44e32805aa25931e, request77ae11136368b592f044da3f881408c87453d9bf5f28c3fd1a5eb0fcc1431c7e.
Source99e8456d200fff1299ee5756279cddb23921dc65 and stock tool0aac16ef62da9e9d5645782d458593e5d78143ba
match pinned before/after artifact snapshots and Git identities. The approved review is e14db2d0dd;
its prepared packet's earlier PENDING labels are historical. No review/retry was awaited.

**13/14 complete groups, 33/35 complete rows**:25 source SUCCESS and8 predeclared negative FAILURE.
All13 compact ZIP GitHub digests matched before extraction; embedded bytes/SHA256, request/source/variant,
fixed three-binary before/after snapshots, shutdown, exit/exception, configuration and exact native refs passed.
The executed collector from21592884db reports33 OBSERVED/RECORDED and missing_groups=[cell-u34].
Full stock/rich records reconcile at9384 properties for these13 groups, with429 UNREACHABLE checks,
91 SAT covers and2 unreachable covers.18 location exceptions match the previously approved exact tuples;
this is diagnostic comparison, not a new exception policy or admission.299 native JSON members/2286673 bytes
are retained in binding metadata with original hashes and selector/crate pointers.

Cell is **FAILED/INCOMPLETE, not admitted**. Only immutable cell-diagnostic refs from929f21bb1f are used;
all files and its manifest match that commit and the same-run artifact identity. Both collector rows remain
status/outcome UNKNOWN. stable_default_cell has source TIMEOUT at600.031112420s with600s limit; its missing
RESULTS and unknown property inventory are preserved. unstable_default_cell has source COMPLETED/SUCCESS
at594.575884753s, but the failed group still gives it no admission. Its301-property inventory was reported
in the diagnostic, whose saved rich projection retains only8 labels, not the full301 records. No inventory
was reconstructed, no cell artifact downloaded again. Group RSS/elapsed/exits are shared observations;
per-root process exit/wall/RSS and compiler provenance gaps remain explicitly UNKNOWN/null.

LABEL-COVERAGE.json diagnoses all111 new required labels:101 found in complete groups,5 found in the
unadmitted unstable cell observation,5 stable cell labels UNKNOWN_PARTIAL. No duplicates.16 preserved
semantic bindings have fresh candidate records (13 singleton candidates and3 three-instance sets),
with historical IDs unused; exact semantics/set completeness remain for offline acceptance.

For the33 complete rows, S1-07 verdicts and property counts are unchanged. Exact rich diffs are retained:
8 IDs added/8 removed (source closure coordinates changed);14 UNREACHABLE→SUCCESS and38 SUCCESS→UNREACHABLE
records, hence checks U405→429 for the same33-row cohort. Source descriptions/coordinates also change.
These observations must be assessed by the existing offline U/role policy; they grant no qualification.
Cell changes from complete group/two source SUCCESS in S1-07 to failed group/TIMEOUT plus source SUCCESS.
9986/187/18 are not imposed as new-run inventory quotas.

TIMING-COMPARISON.json/md contains **all35 common logical row/variant pairs**,0 incompatible and0 unpaired.
The reviewed source5be→99e label/message/coordinate delta is disclosed. Mode/type/N/unwind/target/domain,
flags, cfg, limits, variant, execution groups, tool versions and measured binary identities match.
Per-harness resources.verification_time_s is used directly; no job/group/compile time substitution.

| Cohort | Rows | Completed ratio median | Ratio range |
|---|---:|---:|---:|
| SUCCESS/SUCCESS |26|1.008893573|0.585968101–1.612180418|
| intended FAILURE/FAILURE |8|0.992254580|0.688903502–1.556636863|
| TIMEOUT censored |1|UNKNOWN|conditional lower bound1.633720479|

The SUCCESS cohort includes the source-completed but unadmitted unstable cell observation:
368.802323945→594.575884753s (1.612180418x). Stable cell baseline367.259887864s→timeout600.031112420s
is censored;600/baseline gives a conditional completion-time ratio lower bound, not exact slowdown.
No changed-verdict completed pairs occur. Summaries keep all cohorts separate. These are descriptive
producer measurements, not pure solver time or evidence that labels/kani::assert caused a slowdown.
Future retry1200s is excluded.

Validation: exact structured collector/inventory/native/identity replay PASS;8 small adapter/timing tests PASS.
Admission **PENDING_OFFLINE**, independent B1/B2/general proof credit **NONE**. No source/control/policy,
retry packet, cell-diagnostic, accept, historical evidence or ledger changes; no CI/build/rerun/cancel,
compiler/verifier, push/publication or subagents.
