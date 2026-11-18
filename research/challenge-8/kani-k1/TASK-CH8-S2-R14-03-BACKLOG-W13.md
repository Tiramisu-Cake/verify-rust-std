# W13 — isolated R14-03 gate repair for the NEXT revision

ISSUED coordinator/root after owner17:40 proposal. Use current13 context,
current model/tier, Fast OFF; no subagents. STOP only real blocker.
This gate-only backlog repair runs independently of the frozen r4-r1 GO request.
DO NOT change its source/control/worktree/request/GO packet or delay its handoff.

Frozen review e7837b0f70e235399e53f8da1b48a4a84b33f693, R14-03 OPEN:
review-batch-r4-r1/REPORT.md and R14-03-DISCRIMINATOR.json. R14-01/02 CLOSED.
Frozen source bd62e54df1b4749154790aa3db3cc7978f547f75;
control0e8c836857344866564e1423ad5d8d28bbc4106b, package474e0b4209.
The current one-run exception is separate; generic gate completeness is not approved.

Create a NEW isolated control worktree from0e8, never modify the frozen one.
Repair only lexical_bindings.call_paths/extraction guards and targeted tests:
- Recognize arbitrarily nested parentheses around already-supported static paths,
  or explicitly reject unsupported callable syntax before silently omitting it.
- Reproduce exact ((missing_static))() through the actual lexical gate with only
  the synthetic lexical-source hash guard removed. Preserve source/model fixtures.
- Distinguish direct/single/double/deeper parentheses; unbound vs legitimate
  full paths/aliases/local callable values. Unsupported callable expressions may
  fail closed precisely. Keep method/type/trait/MIR limits explicit.
- Existing lexical/alias controls and exact frozen-source acceptance must remain;
  run new discriminators plus affected tests, no need repeat all96 runner tests.

No algorithm/domain/frame/init/oracle/cfg/cap/source/tool changes. No new general
Rust parser, typechecker, executable expansion, compiler, verifier or full runner.
Deliver gate-only patch/proposed local control commit and exact test evidence in
g0 kani3300/ch8-s2/r14-03-gate-backlog/: PINS, PATCH, TESTS, REPORT, MANIFEST,HANDOFF.
State NOT_AN_EXECUTABLE_CI_PACKAGE: next integration must rebind payload/request,
ancestry and receive independent review/fresh GO. No current CI credit transfers.
Preserve old reviews/candidates; author repair is not independent finding closure.
Next: same14 gate-only delta review, no automatic integration or CI.

No CI/rerun/cancel/push/PR/issue/source publication/ledger/reservation/budget.
No local cargo/rustc/Kani/CBMC; Python/static/synthetic checks only. Ownpaths-only
commit --only, [skip ci], Tiramisu-Cake <igkharin@gmail.com>.
READY full g0/local control patch pins, actual targeted tests and remaining limits.
