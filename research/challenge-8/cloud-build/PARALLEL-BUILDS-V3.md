# Three-owner Cloud Build coordinator: staged transition

This is a portable protocol change for stable owners `select-sort4`, `merge`,
and `verifast`. It permits at most three project-wide queued, running, or
unresolved Builds and at most one reservation per owner and absolute ledger.
It does not grant a phase, budget, Build submission, or proof credit. The
existing v2 envelope remains the default until an explicit migration.

## Adoption order

1. Publish the portable protocol commit **`<PORTABLE_PROTOCOL_COMMIT>`**.
   Cherry-pick only `coordination.py`, `coordination-v3-transition.py`,
   `coordination-v3-test.py`, and this document into each proof client.
   Do not replace a peer's `control.py`: select, merge, and verifast have
   different phase registrations and dispatch rules. Preserve each client's
   phase constants, `authorized_phase`, recipes, proof tree, ledger and pin.
2. In each client checkout, finish any in-flight dispatcher command. Adopt
   the matching coordination source in that client's committed infrastructure
   revision. Record its exact `coordination.py` SHA-256 and current `control.py`
   SHA-256 and the exact infrastructure commit containing both files. Record
   a full baseline commit whose `control.py` has the same phase
   registrations as the adopted dispatcher. It must be an ancestor of, and
   distinct from, the adoption commit. Use the commit after phase registration
   and before dispatcher-only edits.
3. Each stable owner acknowledges its installed source with a JSON file:

   ```json
   {"owner":"select-sort4","coordination_sha256":"<64 lowercase hex>","control_sha256":"<64 lowercase hex>","infra_commit":"<40 lowercase hex>","baseline_control_commit":"<40 lowercase hex>"}
   ```

   Repeat for `merge` and `verifast`. The transition command verifies the
   installed source bytes, dispatcher bytes, committed infrastructure source,
   coordinator API calls, and phase
   registration AST against each baseline commit. Its source hash must match
   the helper's own `coordination.py` bytes. Acknowledgments are explicit
   adoption evidence, not authority to dispatch.
4. With all three client checkouts and acknowledgments available, run
   `coordination-v3-transition.py --client select-sort4=<checkout> --client
   merge=<checkout> --client verifast=<checkout> --ack select-sort4=<json>
   --ack merge=<json> --ack verifast=<json>`. It takes the existing shared
   flock, rejects absent/legacy/already-v3 state, validates all active v2
   reservations, and atomically writes the v3 envelope. It preserves active
   records losslessly as JSON values, including dispatch tokens and Build
   IDs. It never deletes `active.json`, receipts, requests, or ledgers.
5. Read back `schema_version: 3`, `max_active: 3`, active tokens, and each
   owner's status/ledger. Only then may a separately authorized phase submit
   against that client's exact published infrastructure SHA.

`coordination.py` reads both v2 and v3 envelopes. Every reservation mutation
preserves the active envelope's version and capacity. Unknown versions or
capacity mismatches fail closed. A v2 client rejects the v3 envelope; do not
delete or reset `active.json` to let it proceed. Admission counts active
reservations plus unmatched live project Builds. A visible Build carrying a
reserved token consumes that reservation's slot once; conflicting tokens or
IDs fail closed. An unresolved submission still occupies its slot. Updates and
clear operations select one exact dispatch token and preserve peer records.
Terminal API evidence or definitive validation rejection remains the release
condition; cancellation alone does not free a slot.

Run `python3 coordination-v3-test.py` only against its disposable temporary
state. It makes no Cloud API calls. Full Cloud regression and operational v3
acceptance remain **NOT_RUN** until an explicitly authorized Cloud phase.
