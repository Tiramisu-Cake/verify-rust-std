# Current shared Cloud interface — nightly phases

The accepted migration below stays closed. New owner-authorized phases use
independent ledgers, exact committed recipes and the global lock. The owner
approved two project-wide slots, one per agent owner/ledger, on 2026-10-09.
See [the protocol, transition and validation status](PARALLEL-BUILDS.md). Common CLI:

```bash
python3 research/challenge-8/cloud-build/control.py \
  --phase-id NIGHT-SELECT-SORT4-CLOUD-2026-10-09 \
  --ledger /root/verify-rust-std-select-night/research/challenge-8/cloud-build/night-select-sort4/BUDGET.json \
  --state-dir /tmp/smallsort-night-select-sort4 --owner select-sort4 request
```

Replace `request` with `submit --infra-sha FULL_SHA --proof-sha FULL_SHA
--lane o26 --source-mode pinned-objects --timeout 1200`, `status BUILD_ID`,
`download BUILD_ID --output NEW_DIR`, `withdraw-request`, or `cancel BUILD_ID`.
Global arguments precede the command. Each agent keeps its own ledger/worktree,
proof SHA, infra SHA, recipe/profile, state directory and owner. Account requires
phase/status=AUTHORIZED/authorization/deadline_utc/ceiling_build_seconds/
allowed_lanes/builds; timestamps determine actual conservative charge.
The select account is10800 seconds, cutoff2026-10-09T08:00:00Z. Earlier accounts
are not reset or transferred. Migration submit is refused.

`/root/smallsort-ci-coordination/lock` uses flock. Under it the client reconciles
the two active.json reservations (owner, phase, absolute ledger/state, token,
Build ID or unresolved),
checks API ongoing builds, reserves atomically before sending and records the
response. Crashes or uncertain replies keep reservations. No unique API match
means unresolved, not permission to retry. Terminal API evidence or a recorded
conclusive INVALID_ARGUMENT with no token match clears it. Never manually remove
an unresolved reservation to retry. Status reconciles a crashed foreign account
under the same lock; cancel checks explicit owner/phase/ledger. Download transfers
outside the lock and atomically updates its own account after hash checks.

Ready senders may register `request`; requests are advisory and no longer impose
turn alternation. A sender may submit when its own slot is clear and the project
has fewer than two occupied slots. Withdraw stale requests. No scheduler/service
is introduced.

New lanes register `recipes/LANE.json` in the infrastructure commit with schema
smallsort-cloud-recipe-v1, lane, entrypoint (infra shell script), sorted exact
infra_paths and proof_paths; optional baseline_sha/baseline_paths retain original
historical source separately. The committed registry, original commits/root and
ancestor trees/blobs, file modes/hashes, explicit input set and exact selected
object closure are checked before proof preparation. Every imported script,
patch, certificate/data and std input must be present. No worktree data enters.
Add only the new lane to your own allowed_lanes and publish its infra commit;
never inherit another direction's proof acceptance. Recipes route through the
existing run-proof entrypoint and preserve pinned images/--no-source/publication.

A complete diagnostic collector may finish SUCCESS with diagnostic_complete=true;
verification_accepted remains a separate false/true proof verdict and requires its
own audit. Read complete logs/source/profile and actual target checks before any
claim. No build solely to repeat migration smoke or unchanged constructor acceptance.

# Accepted migration workflow (historical commands/accounts)

# Accepted Cloud Build workflow

A/B/C migration accepted; [scope, pins, Build IDs and budget](ACCEPTANCE.md).
The tested infrastructure SHA is `30fc3b42a2fb980b49174d459ec5cfbea778379b`.
The migration commands below identify the historical runs; that phase is closed
and the client refuses further migration submissions. Newer documentation HEADs
are not new proof runs.

## Authorized phase accounts and shared two-slot gate

New submissions require explicit `--phase-id`, absolute `--ledger`, absolute
`--state-dir`, and an owner identifier before the subcommand. The selected
ledger must name an `AUTHORIZED` phase, record its owner's authorization and
deadline, and list the reviewed lanes. The 2026-10-09 select account is
`night-select-sort4/BUDGET.json`; its ceiling is 10800 seconds and its deadline
is 08:00 UTC. A separately authorized merge direction uses its own ledger and
recipe. Every new submission uses pinned Git objects and a published full
infrastructure/proof SHA. For example, after publishing those commits:

```bash
python3 research/challenge-8/cloud-build/control.py \
  --phase-id NIGHT-SELECT-SORT4-CLOUD-2026-10-09 \
  --ledger /root/verify-rust-std-select-night/research/challenge-8/cloud-build/night-select-sort4/BUDGET.json \
  --state-dir /tmp/smallsort-select-cloud --owner select-agent request

python3 research/challenge-8/cloud-build/control.py \
  --phase-id NIGHT-SELECT-SORT4-CLOUD-2026-10-09 \
  --ledger /root/verify-rust-std-select-night/research/challenge-8/cloud-build/night-select-sort4/BUDGET.json \
  --state-dir /tmp/smallsort-select-cloud --owner select-agent submit \
  --infra-sha PUBLISHED_INFRA_SHA --proof-sha PUBLISHED_PROOF_SHA \
  --lane o26 --source-mode pinned-objects --timeout 1500
```

The client holds `/root/smallsort-ci-coordination/lock` while reconciling the
reservations and submitting. The v2 `active.json` retains each token, owner,
phase, ledger and build ID through crashes and uncertain API responses. A missing
build ID blocks that owner's retry until its token resolves; only terminal API
status or definitive API validation rejection clears the reservation. At most
two project builds are allowed across worktrees, one per owner/ledger. Untracked
API builds also consume capacity. Requests are advisory.
`status`, `download`, and `cancel` use the same phase
arguments; cancellation additionally requires the matching owner and active
build ID. Download and hashing release the shared lock while they run.

The VPS runs only this lightweight
control client and evidence hash checker. No Docker, compiler, executable test
or full research runner runs on the VPS.

Every gcloud invocation uses configuration `smallsort-ci`, account
`smallsort-dispatcher@smallsort-ci.iam.gserviceaccount.com`, project `smallsort-ci`
and region `global` for build operations. Storage operations have no region flag.
No active shared gcloud configuration is changed. Credentials are never read,
printed or copied by these scripts.

The control client submits `--no-source --async`; it captures the exact config
file bytes/hash and sends them as explicit substitutions alongside infrastructure
SHA and proof SHA. It looks up a dispatch token after an uncertain response and
retains unresolved state rather than dispatching a duplicate. Two project-wide
slots and one slot per owner/ledger are enforced. A sixty-second queue envelope is reserved on top of the
requested timeout; timeout is at most1740s, keeping the envelope within1800s.
The phase ledger charges the conservative rounded createTime–finishTime interval,
including queue, preparation, execution and upload. Execution startTime–finishTime
is separately recorded. Prior owner setup smoke and historical budgets stay separate.

Proof step image is pinned Ubuntu22.04 x86_64:
`ubuntu@sha256:5ec03bb3441e8b0bf3b4f9cd4629a1ae763010dc3035bb8da3ae6cf026486401`.
The digest is the actual buildStepImages identity of the owner's successful
Ubuntu22.04 setup build. Upload/verdict use pinned Google Cloud CLI stable:
`gcr.io/google.com/cloudsdktool/google-cloud-cli@sha256:c631b05e8121048b29c9917bdc0a9fadd76d012f04f180a4409ec2ee534e832e`.
Files shared between steps live in `/workspace`; no filesystem outside it is
assumed to persist. First proofs use cold installs/builds without a cache.

Before submit, publish the infrastructure source and resolve its full SHA.
Proof input is an independent full committed SHA. The approved
`pinned-objects` mode packs only selected Git objects from those commits; it
reads no working-tree/index/config/hook data and transfers no GitHub credential.
Cloud restore verifies the original commit/root-tree/blob identities, selected
paths, modes and bytes, then sets each repository HEAD to the original commit.
The restored repositories are intentionally partial and no commit is invented.
Pick the reviewed lane and use the historical proof SHA:

```bash
python3 research/challenge-8/cloud-build/control.py submit \
  --infra-sha 30fc3b42a2fb980b49174d459ec5cfbea778379b \
  --proof-sha a0cfd30e066acbaf1b5406cd9773f54388cc45be \
  --lane stock --source-mode pinned-objects --timeout 800

python3 research/challenge-8/cloud-build/control.py submit \
  --infra-sha 30fc3b42a2fb980b49174d459ec5cfbea778379b \
  --proof-sha 1378f0ffc8342233349fae3df5a938c4a021c8d7 \
  --lane constructor --source-mode pinned-objects --timeout 1500

python3 research/challenge-8/cloud-build/control.py status BUILD_ID
python3 research/challenge-8/cloud-build/control.py download BUILD_ID \
  --output /tmp/smallsort-cloud-evidence-BUILD_ID --text-logs
python3 research/challenge-8/cloud-build/control.py cancel BUILD_ID
(cd /tmp/smallsort-cloud-evidence-BUILD_ID && sha256sum --check archive.sha256)
```

The client refuses a timeout outside the current remaining budget. Status updates
accounting from authoritative API timestamps. Cancelling only requests cancellation;
poll until terminal status and do not assume VPS timeout stopped a build. Forced
termination may leave incomplete evidence. The ledger's active/unresolved build
must be resolved before another submission. Compact API/config/download files stay
in `/tmp`, not Git. Commit only the ledger and summaries/reports as checkpoints.
These are the wrapper's exact command forms: `status BUILD_ID` takes a positional
build ID; `download BUILD_ID --output DIR` performs its own manifest/input/archive
hash verification; add `--text-logs` to download and check all separately
published chunks as well. `cancel BUILD_ID` requests cancellation only. The explicit
`sha256sum --check` command independently rechecks the downloaded evidence archive.

Evidence prefix:
`gs://smallsort-ci-evidence-504462351565/cloud-build/BUILD_ID/`.
Download verifies the archive SHA, complete file inventory, config and input SHAs,
external copies and upload receipt. Hash verification is independent of proof
acceptance. Managed `smoke-error` and `smoke-timeout` runs must finish FAILURE
with original42/124, even though their evidence uploads successfully. The package
and upload steps have allowFailure only to reach the independent final verdict;
a missing result, bad summary, incomplete archive or upload cannot yield PASS.

For a separately authorized second direction or agent, preserve that agent's own
proof SHA and reviewed profile, and record a separately authorized budget before
submission. All agents share the project-level two-slot limit enforced by the client API
check, with at most one queued/running/unresolved build per owner and ledger. Keep each phase account separately in
the ledger; never reset historical usage or spend another phase's budget. An independent owner's second build may start while the first is active or
unresolved; a third build or same-owner retry must wait. A second
agent must not edit this worktree or silently use another branch's sources.
Existing lanes remain stock and historical constructor only; do not merge
research histories, load other patches, or extend the semantic profile.

Cloud Build schema and no-source behavior were checked against official
[build configuration documentation](https://docs.cloud.google.com/build/docs/build-config-file-schema)
and [gcloud builds submit](https://docs.cloud.google.com/sdk/gcloud/reference/builds/submit).

## Approved pinned-source delivery

The owner approved credential-free source delivery by pinned Git objects. The
public Git transport failure and approval are historical context; this mode is
now the permanent source path for these reviewed builds. It preserves
`--no-source`, requires no dispatcher bucket write, new key, resource or IAM
change, and carries only selected committed objects in a bounded gzip payload.
The restore module is separately embedded in the build config, verifies the
explicit `LANE`, `INFRA_SHA` and `PROOF_SHA` environment values, and writes its
source archive plus `source-input-certificate.json` to evidence. B validated
source restore: both original HEADs, selected object closure and path/blob hashes
passed; all11 stock cases retained their historical outcomes. C validated the
cold console source build and complete constructor component matrix. Both
complete archives and all separately
published text files were downloaded and checked on VPS. This accepts only
the documented stock and constructor scopes, not new actual-callee proofs.

ChatGPT reads bucket evidence through the connected **SmallSort CI — Read Only**
connector. The publisher currently emits the archive plus
separate `manifest.json`, `summary.json`, `files-sha256.json`,
`submitted-config.json`, `archive.sha256` and `upload-complete.json` objects.
The publisher also emits `text-logs-index.json` and `text-logs/*.txt` chunks.
The index maps original log paths to ordered chunk names, lengths and SHA256;
all published metadata and log chunks are capped at8MiB.
Read the compact manifest/summary first, then retrieve only the relevant log
files. Keep any connector-readable log object at or below 8 MiB; split a larger
log into ordered chunks and include a small index with chunk names, byte lengths
and per-chunk SHA-256 values. Reassemble and verify against the uploaded
manifest/archive inventory before interpreting a truncated or chunked log. The
VPS wrapper's `download` command remains the independent full archive/hash path.
