# Independent14 delta: APPROVE — R14-02 and R14-01 CLOSED

Owner00:33 explicit `/new14` overrides prepared current context. Task
`cd90cf0bde2d7658a2dfe690dd2887bdd72aefb6`; review of exact repaired package
`0902ad2d84e5e5c4d9bb3b01d5c7f7671e84b38d`. Both original findings are independently **CLOSED**; no blocking
or new finding remains in this bounded delta. Root GO-request only; no launch.

| Input | Exact identity |
|---|---|
| Control | `fc29b93b1e333b73e55e2872701c80d9927f3b02` |
| Control tree / sole parent | `c0368fa64ab474e4f64861aedd75a8f2639b1c29` / `9e14e033f9ee31522b571c127609dcdff76d230b` |
| Frozen source | `513341f41ce53833a279571401c924bdddddb6c8` |
| Source tree / parent | `a818efb2157d57af0c9c604f6d0ca85873b8712c` / `97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a` |
| Stock tool | `0aac16ef62da9e9d5645782d458593e5d78143ba`, tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |
| Request SHA256 | `17f7cfba45ca5e572b7e32bea25d31add90885dc2378b725783737e1a6577604` |
| Workflow SHA256 | `8d5fd03476d3d7666692cc7267d3fe598a0007c54ec6576de3538cef434ac709` |

## R14-02 / P1 — CLOSED

`s3_evidence.protected` checks the recorded worker evidence before state-specific
result handling. Local `root_outcome` and portable `collect` both call it. Source
capture errors, snapshot errors, identity drift, unreadable/malformed binaries,
explicit UNKNOWN and malformed required evidence reject. COMPLETE, FAILED,
IN_PROGRESS and INTERRUPTED cannot bypass recorded observations. Matching durable
controller E0/pre/post does not erase a worker error.

Independent campaign tests vary four states, three status labels and two errors
(24 combinations). Each stops at the third invocation with exactly two sealed
prefix roots, matching controller AFTER and six later roots NOT_RUN. Fallback
retains prefix hashes, original worker bytes, exception and exit -9. The author
regressions additionally cover missing/null/unknown states and protected fields.
Sixteen resealed portable state/error mutations reject through the shared reader.
Four actual-writer-shaped stopped campaigns (FAILED/COMPLETE × source/binary
errors) preserve original exception, error records, exit -15 and signal15 in
identical local/upload-only results, with explicit GLOBAL_STOPPED_PENDING_REVIEW.

Absence remains distinct. The existing interrupted-worker continuation regression
passes. A separate independent synthetic interruption check begins with actual
writer-shaped evidence, removes genuinely absent inner source/binary AFTER,
retains verified shutdown and matching durable controller AFTER, and updates the
bound interruption records/seal. Both local and upload-only readers agree: UNKNOWN,
original exit -15, no global stop, later roots retained. This tests reader recovery,
not an actual native process termination. Present error or malformed AFTER cannot
use this absence route. No baseline reset or blanket ESRCH exemption was added;
owned-process lifecycle code and late-publication behavior are unchanged.

## R14-01 / P2 — CLOSED

The actual S3 `_run_group` supplies request-derived std_sha/std_tree/tool_sha/
tool_tree to CompileMonitor and its group record. `source_under_test_record`
writes those same identities, current pre-overlay base_std_sha=513341 and separate
historical_patch_base_std_sha=99e845. Binding metadata copies the actual record.
The shared provenance reader compares against the request at local finalization
and replay, including interrupted sealed groups; it does not merely compare two
potentially stale copies. Actual writer execution is synthetic with native calls
substituted, rather than a fabricated corrected compilation receipt.

Independent execution of the author regressions confirms actual writers, metadata,
legacy defaults and local-finalizer rejection of corrupted writers. The additional
portable matrix mutates all four fields at compile, source_under_test and group
locations across missing/null/array/integer/stale values: 60 rejections. Metadata
artifact hashes, binding references and seals are recomputed, so rejection is the
provenance guard rather than incidental storage corruption. Existing source/target,
request/selector, rich/native-metadata, error-path and late-publication checks pass.
Legacy defaults remain bd62/0aac without added tree fields. The delta leaves all
legacy fixtures, policy and historical evidence unchanged.

## Exact inputs, preserved scope and timing

INPUT-AUDIT.json independently verifies all34 committed package files/all33
manifest hashes, source/control/tool HEAD/tree/sole parent/clean status, request
and workflow bytes, request payload/source hashes, three patch replays to exact
control tree, and audited checkout ancestry7/5/2. Original55-file e8a8 package and
19-file review610d remain exact. The six frozen source/domain/role/U maps match
byte-for-byte. Only the declared seven CONTROL paths differ from1dfc.

Source-semantic/domain/cfg/PFC/U-policy review is inherited from frozen610d by
exact source/tool/map bytes; no broad source audit or new proof claim is made.
Nine roots, full-byte domains, positive actual bodies,71 literal source sites,
44 covers, unwind bounds, disabled U proposal/reject-ALL-U and all caps remain
unchanged. Workflow bytes are identical, including Validate18min, setup1800,
job180min and checkout depths7/5/2. Existing scope gaps in610d remain OPEN.

The author's exact final Validate receipt, script and transcripts agree:
136 legacy +46 S3/repair =182 PASS; execution_count1; elapsed490.471224626s;
1080/elapsed=2.2019640414655, above1.5. Monotonic arithmetic and transcript hashes
match final fc29/request/workflow pins. This is audited author local static/
synthetic evidence, not an independently witnessed CI run. Full Validate was not
rerun; no concrete concern required it. Precursors are not relabelled as final.

Independent final review:26 targeted tests PASS/239.401749s,
plus1 recovery test PASS/10.815396s, total27 PASS. The
expanded reviewer matrix is outside the workflow Validate timing measurement.
Exact commands, timestamps, stdout/stderr and hashes are in tests/ and VALIDATION.
The old targeted.stdout/stderr are preserved as INTERRUPTED PRECURSOR with hashes;
they contribute zero final tests. A reviewer audit-helper wrong-key exception is
recorded separately; correcting the helper caused no candidate change.

## Disposition and handoff

**APPROVE; R14-02 CLOSED; R14-01 CLOSED.** This satisfies the independent delta
review gate for these exact identities. Next is root GO decision only. User
coordinator alone may separately launch/account prospective item2 attempt12/17
after root consent; this review performs no dispatch or accounting action.
Latest owner budget reference31/31+11/17=42/48 supersedes frozen author's41;
that historical metadata difference is informational and not a blocker.

Native compile, compiler expansion, Kani/CBMC, full native runner, proof/fit and
CI remain NOT_RUN. Qualified leaves0, proof obligations closed0, independent
B1/B2 credit NONE. No candidate/source edit, compiler/cargo/rustfmt, CI, push,
PR/issues, raw evidence, ledger/reservation/budget action, subagent or model/settings
change occurred. High/Fast OFF instructions were preserved.
