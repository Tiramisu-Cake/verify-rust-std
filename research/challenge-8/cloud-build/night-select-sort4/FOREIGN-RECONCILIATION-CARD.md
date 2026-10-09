# Cross-worktree Cloud Build reconciliation boundary — 2026-10-09

**Observed client risk.** The current `reconcile_global()` reads the global
reservation and then calls `reconcile()` on the reservation's ledger and state
paths. A select-agent invocation can therefore write the merge agent's ledger
and `/tmp` state, and can insert a missing merge token into that ledger.
The shared reservation is an inter-agent gate, not authorization to edit a
different worktree.

**Change.** Pass the caller's explicit owner and ledger to global
reconciliation. For a foreign reservation, read the named ledger only to check
phase, owner and token identity; resolve the tag or Build ID through the
Cloud Build API; and write only the shared coordination record and an atomic
terminal receipt. A missing foreign ledger/token, zero matches without a
recorded definitive validation rejection, conflicting IDs, and API failures
remain unresolved. Never append to or account a foreign ledger or write its
state directory. An owner may still restore and account its own reserved token.

**Clearing rule.** Clear the shared active record only after an API-confirmed
terminal Build or the recorded definitive `INVALID_ARGUMENT` refusal plus a
zero-result tag lookup. Preserve token, owner, phase, ledger, Build ID, status,
timestamps and conservative charge in the shared receipt. The owner can later
reconcile its own account from the API or zero-charge rejection receipt.

**Hosted acceptance.** A new committed client requires a new Cloud Build run.
Inspect full evidence and accounting: foreign monitoring must leave foreign
ledger/state bytes unchanged, keep uncertain tokens reserved, and maintain
the one-build gate. This client change carries no proof or verifier claim.

The next actual research Build will also run the isolated Cloud-only
`coordination-regression.py` against the committed client. It substitutes
synthetic Cloud API responses while exercising the real `reconcile_global`,
`reconcile`, and `coordination.locked` functions under a private `/workspace`
coordination directory. Required cases: missing foreign ledger or token, zero-match
uncertainty, conflicting Build IDs, wrong dispatch tag, API exception, foreign
terminal receipt without foreign writes, exact own terminal charge with no
second charge, definitive validation rejection with zero-second receipt and
owner resumption, and two processes contending for one reservation. Each case
records mock API calls and observed file hashes; the summary reports
`diagnostic_complete` only when every case passes. This synthetic diagnostic
checks client behavior at the changed boundary. It does not exercise real
Cloud API consistency, transport, proof results, or a persistent service.
