# Four-owner Cloud Build coordinator: staged v4 transition

This protocol reserves at most four project-wide queued, running, or unresolved
Cloud Builds, one per stable owner and absolute ledger. The only v4 owners are
`select-sort4`, `merge`, `verifast`, and `refinedrust-feasibility`. It does not
authorize any Build, phase, budget, dispatcher command, proof claim, or change
to a client's phase registration. Until the explicit transition, the live v3
envelope remains v3 with capacity three.

## Publish and adopt before migration

1. Publish one reviewed portable infrastructure commit containing
   `coordination.py`, `coordination-v4-transition.py`,
   `coordination-v4-test.py`, and this document. Record its full commit ID and
   the SHA-256 of `coordination.py`. The coordinator reads v2, v3 and v4, but
   an ordinary reservation write retains the installed envelope version and
   capacity. Extra envelope and reservation fields, including timestamps and
   receipt data, survive updates.
2. Each owner independently adopts exactly the portable coordinator source
   in its own checkout, keeping its own `control.py`, phase registrations,
   recipes, proof tree, ledger and pins. Finish any dispatcher command before
   adoption. Commit and publish its own infrastructure revision containing
   the installed `coordination.py` and `control.py`. Select a distinct ancestor
   baseline commit with the same `authorized_phase` registration and named
   phase/deadline/lane/start constants. The RefinedRust client must first be
   provisioned with a real dispatcher and its own registration; no ACK can be
   inferred from a proof branch or another owner's dispatcher. Gate the own
   source replacement under the common `flock`: while holding it, run
   `python3 coordination-v4-transition.py audit` and replace only the own
   `coordination.py` if it reports no dispatcher. The audit reads `/proc` and
   refuses an inaccessible inventory or a `control.py` command from any
   checkout. Finish commit/publication and keep the client quiescent through
   ACK issuance. A fresh ACK is required if installed bytes or branch tip
   later change.
3. The owner independently reviews the **entire** existing dispatcher
   baseline, including helpers and owner patterns, and creates a separate
   review receipt. The transition script cannot perform this review. Its
   `authorized_phase`/coordinator-call AST checks are sanity checks only.
   The receipt contains the following exact fields; the owner supplies it
   as a file and the ACK command never invents `review_status`:

   ```json
   {"owner":"select-sort4","review_status":"OWNER_REVIEWED_BASELINE",
    "baseline_control_commit":"<40-hex-ancestor>","control_sha256":"<64-lowercase-hex>"}
   ```

   The baseline commit must be a distinct ancestor of the published adopted
   infrastructure commit, so its object is published with that branch. The
   installed `control.py`, the baseline version and the adopted version must
   be **byte-identical**. For the new RefinedRust dispatcher, independent
   owner review and an actual published baseline are prerequisites; a stub
   registration does not satisfy this human review.
4. After publishing, each owner runs this **read-only** command from the
   portable script. Use its own checkout and published branch ref, with the
   branch tip equal to the exact adopted infrastructure commit:

   ```sh
   python3 research/challenge-8/cloud-build/coordination-v4-transition.py ack \
     --owner select-sort4 --client /path/to/own/checkout \
     --baseline-control-commit <40-hex-ancestor> \
     --infra-commit <40-hex-published-tip> \
     --published-ref refs/heads/<own-branch> \
     --review-receipt /path/to/own-review.json
   ```

   Repeat independently for `merge`, `verifast`, and
   `refinedrust-feasibility`, changing owner, checkout, and exact commits.
   The command prints one JSON ACK and does not write to the client or shared
   state. Each owner may save its output as a separate ACK file and provide it
   to the migration operator. Do not fabricate or overwrite a peer's ACK.
   ACK fields are owner, installed coordinator/control SHA-256, adopted
   infrastructure commit, baseline control commit, published ref and the
   separate owner-authored review receipt.
   Validation checks installed bytes against the adopted commit, baseline
   ancestry and unchanged phase registration, required coordinator API calls,
   the project fork's `origin`, and the published branch tip. It scans `/proc`
   before and after the ACK check and refuses a live `control.py` command,
   including one outside the supplied checkout, or an unreadable process
   inventory. Git operations have five-second timeouts. The receipt is a
   human attestation, not cryptographic proof of the review; the script
   checks its exact identities and publication, not review quality. The ACK
   cannot establish a Build authorization.

## Explicit migration after four ACKs

The operator confirms that all four dispatcher commands have finished, obtains
all four real ACK files and checkouts, and confirms current API inventory and
reservation tokens. Then run the migration command once:

```sh
python3 research/challenge-8/cloud-build/coordination-v4-transition.py migrate \
  --configuration smallsort-ci \
  --account smallsort-dispatcher@smallsort-ci.iam.gserviceaccount.com \
  --project smallsort-ci \
  --client select-sort4=/path/to/select --ack select-sort4=/path/to/select-ack.json \
  --client merge=/path/to/merge --ack merge=/path/to/merge-ack.json \
  --client verifast=/path/to/verifast --ack verifast=/path/to/verifast-ack.json \
  --client refinedrust-feasibility=/path/to/refinedrust \
  --ack refinedrust-feasibility=/path/to/refinedrust-ack.json
```

The command audits `/proc` before taking the shared lock and twice under it:
before local ACK validation and immediately before replacement. It checks
all published branch tips outside the lock, snapshots the four ACK files,
then under the lock confirms unchanged ACK bytes and revalidates installed
source and committed dispatcher bytes. A live `control.py`
command or inaccessible process inventory blocks migration, including for a
checkout omitted from the four paths. While locked, it reads current ongoing
Builds through the canonical Cloud SDK configuration `smallsort-ci`, account
`smallsort-dispatcher@smallsort-ci.iam.gserviceaccount.com`, and project
`smallsort-ci` in
region `global`, with a ten-second timeout. It checks duplicate or conflicting
Build IDs/tokens and counts reservations plus unmatched live Builds. A pending
reservation occupies a slot; a matching visible Build does not consume another.
It refuses occupancy above four and makes no submit or ledger change. An API
error or unavailable account blocks migration; a stale local snapshot cannot
replace this read. The command takes the existing shared `flock` across local
ACK validation, v3 state validation and one atomic replacement. It requires an existing v3 envelope,
rejects unknown owners and malformed or duplicate reservation identities.
Legacy v2/v3 minimal records remain readable, but migration requires every
active record to have the full reconciler fields (`phase_id`, absolute
`state_dir`, `build_id`, and `item`); the item must contain matching owner,
phase and dispatch token. A Build ID may appear first in either the item or
global record during reconciliation, but two different nonempty IDs conflict.
It then changes only `schema_version` from 3 to 4 and `max_active` from 3 to 4, and
reads back the full JSON value. Existing records, tokens, Build IDs, timestamps,
receipts and other fields remain. It does not delete or edit requests, ledgers
or other coordination files. An old v3 client rejects v4; never reset the
envelope to make it run.

After migration, read back the envelope and each owner's status/ledger, then
reconcile API inventory before any separately authorized submission. A matching
reserved token and visible Build occupy one slot. An unmatched live Build or
unresolved submission occupies a slot. Duplicate or conflicting IDs/tokens
fail closed. Updates and clears select the exact token; terminal API evidence
or definitive validation refusal remains the release condition. Cancellation
alone does not free a slot. The existing phase and budget restrictions still
govern each client.

`python3 research/challenge-8/cloud-build/coordination-v4-test.py` uses only
synthetic mission-prefixed temporary state and local Git reads. Its Cloud API
responses are mocked; it makes no provider, compiler or proof calls. A local
service test is not Cloud acceptance.
