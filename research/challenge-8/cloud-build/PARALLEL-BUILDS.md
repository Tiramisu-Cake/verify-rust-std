# Two Cloud Build slots

Owner decision: 2026-10-09, 13:52 MSK. Allow at most **two** project builds,
with at most **one queued, running or unresolved submission per agent owner**.
The same ledger cannot occupy two slots under different owner names. This
supersedes the shared single-slot rule and ready-request alternation, including
those in current phase documents. It changes no phase deadline, proof scope,
Cloud budget, IAM setting, machine type or execution-provider restriction.

## Protocol

`coordination.py` and `control.py` retain the shared
`/root/smallsort-ci-coordination/lock`. It protects short client transactions
(reconciliation, admission, reservation, asynchronous submission and accounting),
not the lifetime of the Cloud builds. The two builds execute independently.

`active.json` now contains a version-2 envelope with `schema_version: 2`,
`max_active: 2` and a `reservations` list. Each record retains its owner, phase,
absolute ledger/state paths, dispatch token, item and optional Build ID.
Reservation updates and removals select the exact token and preserve the peer.
Only terminal API evidence or a definitive validation rejection releases a slot.
An uncertain response consumes its owner's slot; it does not consume both slots.

Admission counts reservations plus live project builds not represented by those
reservations. IDs/tokens prevent double counting; inconsistent or duplicate
matches fail closed. Untracked builds also consume capacity. All cooperating
dispatchers must use the same lock and state directory. Do not submit around
the dispatcher or use an owner alias to obtain another slot.

`request` and `withdraw-request` remain compatible, but requests are advisory.
A pending or idle peer no longer blocks an otherwise available slot. Separate
phase budgets, exact committed inputs, source identity checks, foreign-ledger
read-only reconciliation, evidence receipts and owner-only cancellation remain.
No budget transfer or extension is implicit in parallel execution.

## Transition on the VPS

The repository change does not hot-update processes or files in existing agent
worktrees. Apply the same coordinator protocol to **both** clients before their
next submissions. Preserve each branch's `authorized_phase` implementation,
phase-specific constants, current recipes, ledgers and proof changes. In
particular, select and merge currently have different day-phase registrations;
do not replace one branch's complete `control.py` with the other branch's copy.
Transfer the coordinator commit with `git cherry-pick` after inspecting its diff,
or apply only its relevant hunks if local changes overlap. Resolve conflicts
without resetting either worktree or merging their research histories.

For both agents:

1. Let any in-flight client command finish; preserve active Cloud Build IDs and
   reservations. Apply the code and instruction changes in each worktree and
   publish that branch's resulting infrastructure commit.
2. Run the existing `status` command with that agent's explicit owner, phase,
   ledger and state arguments using the updated client. Inspect reconciliation
   and remaining budget. Keep the stable owners `select-sort4` and `merge`.
3. Submit only within a still-authorized phase using the resulting exact
   infrastructure SHA. The existing client checks its own bytes against it;
   the shared patch commit from another branch is not that branch's infra SHA.

Legacy `active.json` is read losslessly as one reservation. The first mutation
atomically writes the v2 envelope under the existing flock. A crash therefore
leaves either the old record or the complete new state. The empty envelope is
retained permanently: old single-slot clients fail closed on v2 rather than
silently permitting extra builds. **Do not delete or reset `active.json`** to
unblock an old client. Update that client instead. Downgrading requires draining
and reconciling all reservations and a separately reviewed migration; do not
simply revert the Python files during active use.

## Validation

The Cloud-only regression retains the previous reconciliation/accounting cases
and adds: three racing processes competing for two slots, independent owners,
same-owner and same-ledger refusals, unresolved and untracked capacity, token
deduplication, peer-preserving updates/releases, live legacy-state migration,
old-client exclusion, and cancellation of only the selected owner's build.
Tests use synthetic APIs and disposable `/workspace` state, never production
coordination files or real cancellation/submission calls.

An isolated `coordination-regression` recipe runs this suite without installing
or building a verifier. It uses the existing pinned source and evidence pipeline.
Choose this lane only in an explicitly authorized infrastructure-check account;
do not add it to a proof phase or reuse an expired account by assumption. The
suite can also run through the existing `o26-independent-tests` recipe, which
includes other diagnostics and is not needed just to check coordination.

At preparation: Python AST parsing, shell syntax and JSON structure were checked.
**Executable regression and live two-build operation have not been run by the
author of this patch.** The available session has GitHub and read-only evidence
access, not a Cloud Build dispatcher connection. Cloud-only validation remains
required before treating the protocol as operationally verified.
