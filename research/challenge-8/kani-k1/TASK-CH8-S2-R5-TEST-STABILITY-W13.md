# Original13 — deterministic escaped-child process fixture before R5 GO

ISSUED under owner21:22 request to choose and prepare GO. Root chooses(b):
stabilize the test, retain it in CI Validate. CURRENT13 context/settings,
Fast OFF, no subagents. STOP only real blocker; no runtime redesign.

Freeze approved r5-r1 package dc8d28b0117737e95ccc9b91eb470c1a3c42a635,
control d67bd1ecd555030c46a06b8462d0313ea416711a/tree
c8925e3acfd299f7eb74997c8e120873dcaab84d. Review
2ed2c8ef2f6b9d6460494b85594e3a5f08387a7f APPROVE closes01/02 but records
34targeted=33PASS/1FAIL and isolated repeatFAIL. Read its REPORT.md,
PROCESS-DIAGNOSTIC.json and diagnose_process.py. Test
test_r5.ProcessTests.test_escaped_setsid_child_found_and_reaped is included in
CI Validate by explicit `python3 -m unittest ... test_r5.py`.

The initial orphan list is a pre-poll sampled snapshot, not guaranteed to include
a child adopted after the sample. Existing fixture exits parent immediately
after Popen. Final cleanup still observes/signals/reaps and controller rejects
escaped PGID. This is a test-observation race, not permission to weaken runtime.

Make ONE tiny TEST-ONLY repair in a new immutable batch-r5-r1-stable/ packet,
isolated sibling control parent9e14e033f9ee31522b571c127609dcdff76d230b.
Logical profile/GO remains r5-r1. Preserve dc8d28/d67 and review2ed2 immutable.

Required behavior:
- Use a bounded explicit child-ready handshake after setsid (not fixed sleeps)
  before parent exit, with timeout/cleanup on every fixture failure path.
- Assert stable post-cleanup evidence: escaped child's real identity/PGID,
  observed and signalled owned child, reaped adopted child, verified containment,
  and controller's expected rejection of escaped PGID using actual supervisor
  result. Do not require a particular early snapshot to contain a late child.
  Keep coverage for early-orphan handling meaningful; if a deterministic mock
  boundary case is needed, make it narrow and preserve real-child coverage.
- Do not delete/skip/exclude the test, remove semantic cleanup checks, add retry
  until pass, hide failures, or modify production r5_runtime/campaign/collector/
  runner/packer/protected controls. No arbitrary delay as a race fix.
- Exactly test changes + necessary request payload/hash/audit/package bindings.
  Sourcebd62/tool0aac, workflow command/module list/cap11, selected9/16/5 and
  deferredgeneral32/full11/20/6, all runtime/campaign/resource caps unchanged.

Validation: bounded repeated real-child cases (record all attempts, no hidden
retry), meaningful forced scheduling/delayed-observation case, existing relevant
process and portable/cap regressions. Then run actual final Validate ONCE on
exact committed control, record full result/provenance/timing; confirm11min>=1.5x.
Only if necessary under owner's margin rule, use smallest sufficient R5 cap
with derived bindings, never increase setup aggregate/job/campaign budgets.
Prior134PASS409s remains prior-object, review33/1 and repeatFAIL stay recorded.
Static inventories/patch replays/shallow7/5/2/source invariance and exact hashes.

Output full PINS/HANDOFF/TEST-STABILITY.md+json, immutable parent patch/main delta,
validation transcripts/timings/manifest. Write g0 only new batch-r5-r1-stable/.
Ownpaths-only --only [skip ci], Tiramisu-Cake <igkharin@gmail.com>.
READY exactg0/control/tree/parent/request/workflow/testpins. SAME14 narrow delta
review then root final go-r5-r1. Root does NOT agree to dispatch oldd67 with known
flaky prebuild test; agreement is conditional on exact stable candidate approval.
No compiler/Kani/CBMC/native verifier/full runner/CI/push/PR/issues/rawarchives/
GCS/ledger/reservation/budget. Actual29/30 item1,10/17item2,total39/47 unchanged.
