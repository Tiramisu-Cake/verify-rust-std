# Permanent Cloud Build research and evidence procedure

All SmallSort CI, proof, fixture, MIR and source-build work runs in Cloud Build.
GitHub hosts source, branches, pull requests and documentation; no GitHub Actions
dispatch or rerun is authorized without direct owner instruction. Existing
automatic workflow triggers remain unchanged and are inventoried in
[GITHUB-TRIGGERS.md](GITHUB-TRIGGERS.md). The VPS runs only this lightweight
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
retains unresolved state rather than dispatching a duplicate. One queued/running
build is enforced. A sixty-second queue envelope is reserved on top of the
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
  --infra-sha FULL_PUBLISHED_INFRA_SHA \
  --proof-sha a0cfd30e066acbaf1b5406cd9773f54388cc45be \
  --lane stock --source-mode pinned-objects --timeout 800

python3 research/challenge-8/cloud-build/control.py submit \
  --infra-sha FULL_PUBLISHED_INFRA_SHA \
  --proof-sha 1378f0ffc8342233349fae3df5a938c4a021c8d7 \
  --lane constructor --source-mode pinned-objects --timeout 1500

python3 research/challenge-8/cloud-build/control.py status BUILD_ID
python3 research/challenge-8/cloud-build/control.py download BUILD_ID \
  --output /tmp/smallsort-cloud-evidence-BUILD_ID
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
hash verification; `cancel BUILD_ID` requests cancellation only. The explicit
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
submission. All agents share the same one-queued/running-build limit and budget
ledger, so no second build may start while one is active or unresolved. A second
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
source archive plus `source-input-certificate.json` to evidence. Source restore
has not yet been validated by B/C; neither lane is accepted until its restore,
source gates, full evidence upload and independent acceptance summary pass.

ChatGPT reads bucket evidence through the connected **SmallSort CI — Read Only**
connector. The publisher currently emits the archive plus
separate `manifest.json`, `summary.json`, `files-sha256.json`,
`submitted-config.json`, `archive.sha256` and `upload-complete.json` objects.
Read the compact manifest/summary first, then retrieve only the relevant log
files. Keep any connector-readable log object at or below 8 MiB; split a larger
log into ordered chunks and include a small index with chunk names, byte lengths
and per-chunk SHA-256 values. Reassemble and verify against the uploaded
manifest/archive inventory before interpreting a truncated or chunked log. The
VPS wrapper's `download` command remains the independent full archive/hash path.
