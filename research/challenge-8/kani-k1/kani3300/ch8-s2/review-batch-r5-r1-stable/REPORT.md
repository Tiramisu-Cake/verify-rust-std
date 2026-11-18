# W14 fresh narrow stability review — APPROVE

No blocking findings on exact package `2906a5b6d3b8451e5b49417714f75e3f9a4af148`,
control `63535098ab85c70c8707eee0afd65f53c9ef566a`, tree
`20f53f18eaafe276a3f1ea74102cbc7c6f3985ac`, sole parent
`9e14e033f9ee31522b571c127609dcdff76d230b`.
Owner21:46 explicitly requested `/new`; this fresh review overrides the prepared
reuse-context wording. Task `task6d7c4739def196654459faf05b7e1c36ace03e93`.
Fast OFF/settings preserved; no subagents.

Request SHA256 `d87434d250a1a430c565d8e0612e5a3987f7a811b6cfd9091c268865ff3498b1`
and workflow SHA256 `80d1273b9564a16eb4619089db5604ccccdfaa1cb7a155e9703d169c14b58c90`
match committed bytes, working trees and package copies. Source
`bd62e54df1b4749154790aa3db3cc7978f547f75` and tool
`0aac16ef62da9e9d5645782d458593e5d78143ba` match clean exact pins.
All 84 package files/83 manifest hashes, six exact temporary-index patch replays
and actual shallow metadata 7/5/2 pass. `INPUTS.json` records every package hash.

The delta has exactly six paths: test_r5.py, workflow cap, check_package.py,
r5_profile.py, test_s2.py and request bindings. The other 3,875 Git tree entries
are identical to approved d67. Production containment/runtime/campaign, runner,
collector, packer, protected gates, source/tool, workflow commands/module list,
ordering and runtime/resource caps are unchanged. AST comparison finds only the
existing escaped-child test changed, with its new helper/assertion and two added
tests; all other existing methods remain identical. No skip, exclusion, sleep,
retry-until-pass or loss of semantic cleanup coverage is introduced.

The child calls setsid, arms a bounded alarm and publishes PID/PGID/start ticks
through an inherited pipe. The worker waits at most two seconds for that identity
before exiting. Final assertions require the same real identity observed and
signalled, adopted child reaped, containment verified, PID absent, successful
worker exit without cutoff/error, and actual controller rejection with
unexpected_process_group_containment_gap. The timing-dependent early snapshot
is no longer used to prove final cleanup. A socket/pidfd barrier creates the
child after the first live sample and waits for worker exit before returning
that stale sample: early orphan[] is required and the final checks still pass.
The separate valid-owned-identity/nonempty-early-orphan boundary still rejects
with exactly global_supervisor_failure through the real controller.

Failure-path inspection covers errors before child creation, readiness timeout,
EOF/malformed identity, identity mismatch, ready-file/socket failures and
supervisor callback failures. Worker finally closes control; pipe ends are
closed along their normal/error paths, and process exit releases any descriptor
left by failed spawn. Every incomplete spawned child takes terminate/wait then
kill/wait on timeout. Supervisor finally resamples/reaps owned descendants and
restores subreaper state; the child alarm adds a bounded fallback. The outer
fixture closes its listener and temporary directory. Failure is surfaced rather
than converted to success. This is scoped fixture review, not a general kernel
containment proof or a guarantee under arbitrary host scheduling delays.

Reviewer targeted execution: **28 PASS in 14.943931344s**, consisting of exactly
three normal and three forced-early-empty repetitions plus 22 relevant tests.
Every repetition and real supervision result is retained. Process, portable
prefix, identity rejection, caps/types/legacy/order/setup aggregate checks pass.
Additional subcases force ready EOF, wrong identity and missing-ready with
SIGTERM ignored; all fail the worker as expected, verify cleanup and leave the
recorded child PID absent. The last case exercises kill escalation. The original
missing-ready timeout test also passes. See TARGETED-TESTS.json/txt and the
immutable run_targeted.py. No further runs or hidden retries occurred.

**R14-R5-01 remains CLOSED with the authorized necessary cap delta.** The stable
precursor's actual 136 PASS/440.727425928s remains recorded with failed 11-minute
margin (about 1.498x). Exact final author evidence records 136 PASS,
exit0, workflow-identical command, matching identities/transcript and monotonic
duration **446.377637895s**. Thus 720s / duration = **1.612984027146456926344455403x**;
ceil(1.5 * duration / 60) = **12 minutes**, the smallest sufficient integer cap.
Check-source PASS/14.229315844s has matching final provenance. These are inspected
author executions, not new reviewer full runs. Strict legacy stays 10min;
step maxima188min/setup maxima3240s are not budget grants. Setup aggregate1800s,
job180min and campaign6900s are unchanged. Future CI duration remains UNKNOWN.

**R14-R5-02 remains CLOSED by exact production invariance** from review
`2ed2c8ef2f6b9d6460494b85594e3a5f08387a7f`; all four portable regressions also pass
on exact final control. Prior package dc8 and review2ed committed bytes are
unchanged. Prior 134 PASS/409.026897886s belongs to d67. Original reviewer
33 PASS/1 FAIL and isolated repeat FAIL remain immutable and explicitly retained;
the old runs are not relabeled. Selected9/16/5, deferred general32 pair/full11/20/6,
source-reported restrictions and previous proof limitations remain.

APPROVE permits handoff to root for the **exact final GO-request only**. Root's
805dfa HOLD packet is untouched and must be finalized separately; this review
does not issue GO or authorize dispatch. No compiler/verifier/full runner/CI,
push/PR/issues, raw archives/GCS, ledger/reservation/budget edits or candidate
edits. Reviewer full Validate/check-source executions: zero. W11 work untouched.
Proof credit NONE; native R5 NOT_RUN; no proof obligations closed.
