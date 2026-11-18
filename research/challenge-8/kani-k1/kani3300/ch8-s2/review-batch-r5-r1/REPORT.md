# Independent14 combined R5-r1 delta review — APPROVE

Both **R14-R5-01 CLOSED** and **R14-R5-02 CLOSED** on exact combined package
`dc8d28b0117737e95ccc9b91eb470c1a3c42a635`, control
`d67bd1ecd555030c46a06b8462d0313ea416711a`, tree
`c8925e3acfd299f7eb74997c8e120873dcaab84d`, sole parent
`9e14e033f9ee31522b571c127609dcdff76d230b`. No blocking findings remain.
Task `taska9cc91d717751d2047e13bc7570a95305f546fa7`; owner21:10 `/new`
overrides reuse-context wording. This fresh review independently verifies the
delta and inherits unchanged full-review facts by verified invariance.

Request `f4a1eb18f3324f380973194c2b384f1a1d6d4df139620f86978e9249462dc7c2`
and workflow `4a9e90a68e4b3f977f28ee31ec2c9426e3b685f1da5616168e12756d0c64c8c6`
match committed bytes and package copies. Source
`bd62e54df1b4749154790aa3db3cc7978f547f75` and stock/tool
`0aac16ef62da9e9d5645782d458593e5d78143ba` remain exact and clean.
All **70 package files/69 manifest hashes** match; six exact Git-index patch
replays and actual shallow metadata **7/5/2** pass. Original package530 and
review022b remain immutable. See `INPUTS.json`, `INVARIANCE.json`, and
`REEXECUTED-VALIDATION.json`.

## R14-R5-01 — CLOSED

R5 Validate is exactly11 minutes; strict legacy validation remains10.
The final author execution's command equals the workflow run string, with
134 successful tests, exit0, exact control/request/workflow/source/tool provenance,
transcript hash and monotonic interval **409.026897886s**. Thus660s yields
**1.613585814065335093936654016x**, above1.5; the smallest whole-minute cap is11.
Original130PASS/403.420022367s remains **INHERITED_PRIOR_OBJECT4e97**, not a new
execution. Reviewer full Validate executions: **zero**.

Workflow commands, module list, step order and all other YAML fields are
identical. The two cap validators change only R5 cap normalization and the
derived sum. Step maxima become187min and setup-step maxima3180s; binding setup
aggregate1800s, job10800s and every campaign/resource/artifact cap are unchanged.
Those maxima grant no additional budget. Independent cap/type/order/aggregate
tests pass. Final check-source13.409119839s is inspected author evidence, with
matching identities/hash; it was not rerun. Future GitHub timing remains UNKNOWN.
See `VALIDATE-MARGIN.json` and `TARGETED-TESTS.txt`.

## R14-R5-02 — CLOSED

The portable seal now requires a versioned schema and canonical, scoped JSON
paths with SHA256 digests. `root_outcome` seals structured group evidence plus
row/worker/supervision receipts; local raw captures are recorded separately as
`LOCAL_CAPTURE_BYTES_ONLY_NOT_UPLOADED_NOT_REQUIRED_FOR_PORTABLE_REPLAY`.
The structured packer, collector, runner and protected decoders are byte-identical.
No raw log payload is added to the upload.

The reviewer reexecuted the immutable old synthetic reproduction, redirecting
only its output: original4e97 still fails archive-only seal **and collect** with
the missing stderr.log KeyError. On exact finald67 the four portable regressions
pass through real `_run_group`, receipt/seal, later failure, finalize, fallback,
packing, clean upload-only directory, deleted producer directory, seal and
public collection. Only external native execution/source/binary sampling use
fixtures. The completed first root remains byte-exact RECORDED/expected-match;
the later root stays UNKNOWN and the full inventory remains incomplete.

Additional reviewer assertions check all eight sealed structured members:
**16 omission/byte-mutation cases** reject both seal and collect, even when the
archive entry hash/length are updated. **15 malformed-seal cases** reject wrong
schema/id/type, required-member omission, absolute/traversal/noncanonical/
backslash/cross-root/non-JSON paths and bad digests. Optional local-log digest
metadata can be absent without requiring raw payload. Compact-cap omission
tests report INCOMPLETE and cannot qualify; production caps are unchanged.
See `PORTABLE-PROBE.json`, `UPLOADED-PREFIX-REPRO.json`, `TARGETED-TESTS.txt`.

## Inherited full review and validation limits

Exactly seven control paths differ from4e97; **3,874 other tree entries are
identical**. AST comparison confines service changes to `sealed`/`root_outcome`,
cap changes to `check_yaml`/`validate_yaml`, preserves all23 original R5 tests,
and confirms test_s2 only changes186 to187. Request changes are exclusively
payload hashes, entry and control reference; source maps, protected gates,
inventories, flags, budgets and R5 plan are identical. This supports inheritance
of original review022b's singleton/order/fresh binding/lifecycle/containment/
aggregate-limit/oracle/control findings. Selected9/16/5, deferred general32 pair,
full11/20/6 and sampled-PGID scope remain distinct. The seal change retains
structured request/source/binary/compile/export/property/diagnostic binding bytes.

Reviewer targeted run: **34 tests,33 PASS,1 FAIL** in30.712797523s. All four new
portable and seven cap/setup checks pass. The unchanged
`test_escaped_setsid_child_found_and_reaped` fails an early survivor-list assertion;
one isolated exact repeat also fails. This is recorded, not reported as all-PASS.
The fixture permits parent exit immediately after child Popen; `live` is sampled
before parent poll, so the early orphan list can omit a newly adopted child.
An instrumented delayed-sample reproduction confirms that exact empty-list race
while cleanup still observes, signals and reaps the escaped child and the
controller rejects its PGID via `unexpected_process_group_containment_gap`.
A synchronized setsid-before-parent-exit case independently confirms rejection.
Runtime and test are unchanged from4e97. This is a **nonblocking inherited test
timing observation**, with possible CI flakiness; it does not reopen either
repair closure. See `PROCESS-DIAGNOSTIC.json`; no process-containment proof or
future CI success is claimed.

No compiler/verifier/full runner/CI, push/PR/issues, raw real evidence/archive/
GCS access, ledger/reservation/budget changes, candidate edits or subagents.
Fast OFF/settings preserved. Native R5 NOT_RUN; independent B1/B2 credit NONE;
zero proof obligations closed. Assumed/caller-copy/source-reported restrictions
and assertion-origin/compiler-instance gaps remain. Review output is ownpaths
only. Concurrent unrelated g0 commits are outside the reviewed package.

**APPROVE prepares a coordinator GO-request only. Dispatch/publication require
separate coordinator/owner decisions.**
