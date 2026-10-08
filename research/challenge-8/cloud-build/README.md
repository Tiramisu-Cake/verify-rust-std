# Explicit Cloud Build research commands

The VPS runs only this lightweight control client and evidence hash checker.
Proofs, fixture generation, MIR and source builds run inside Cloud Build.
No Docker, compiler or full research runner runs on the VPS.

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

Before submit, commit/push the migration branch and resolve the full published
infrastructure SHA. Proof input is an independent full published SHA. Choose one
lane; the historical comparison targets are fixed in the phase note:

```bash
python3 research/challenge-8/cloud-build/control.py submit \
  --infra-sha FULL_PUBLISHED_INFRA_SHA \
  --proof-sha a0cfd30e066acbaf1b5406cd9773f54388cc45be \
  --lane stock --timeout 800

python3 research/challenge-8/cloud-build/control.py submit \
  --infra-sha FULL_PUBLISHED_INFRA_SHA \
  --proof-sha 1378f0ffc8342233349fae3df5a938c4a021c8d7 \
  --lane constructor --timeout 1500

python3 research/challenge-8/cloud-build/control.py status BUILD_ID
python3 research/challenge-8/cloud-build/control.py download BUILD_ID \
  --output /tmp/smallsort-cloud-evidence-BUILD_ID
python3 research/challenge-8/cloud-build/control.py cancel BUILD_ID
```

The client refuses a timeout outside the current remaining budget. Status updates
accounting from authoritative API timestamps. Cancelling only requests cancellation;
poll until terminal status and do not assume VPS timeout stopped a build. Forced
termination may leave incomplete evidence. The ledger's active/unresolved build
must be resolved before another submission. Compact API/config/download files stay
in `/tmp`, not Git. Commit only the ledger and summaries/reports as checkpoints.

Evidence prefix:
`gs://smallsort-ci-evidence-504462351565/cloud-build/BUILD_ID/`.
Download verifies the archive SHA, complete file inventory, config and input SHAs,
external copies and upload receipt. Hash verification is independent of proof
acceptance. Managed `smoke-error` and `smoke-timeout` runs must finish FAILURE
with original42/124, even though their evidence uploads successfully. The package
and upload steps have allowFailure only to reach the independent final verdict;
a missing result, bad summary, incomplete archive or upload cannot yield PASS.

For the second direction: use this migration infrastructure SHA with its own
explicit proof SHA/profile and a separately authorized ledger/selection. Existing
lanes are the reviewed stock and historical constructor matrix only. Do not
silently load its verifier patches or extend these lanes to another semantic
profile. No merge of research histories, IAM change, cloud resource or trigger is
needed. The second agent stays suspended during this phase.

Cloud Build schema and no-source behavior were checked against official
[build configuration documentation](https://docs.cloud.google.com/build/docs/build-config-file-schema)
and [gcloud builds submit](https://docs.cloud.google.com/sdk/gcloud/reference/builds/submit).

## Prepared source-access fallback

The first B build found the public fork inaccessible anonymously: Git fetch
failed128; raw, codeload and anonymous API returned404, while authenticated API
reported PUBLIC. No GitHub credential is transferred to Cloud Build.

A credential-free alternative is prepared, pending the owner's response to the
explicit source-delivery exception request. Add `--source-mode pinned-objects`
to the submit command only after approval. The client reads selected committed
Git objects, not working-tree files, and sends a bounded gzip payload through
explicit substitutions using a [gcloud flags file](https://docs.cloud.google.com/sdk/gcloud/reference/topic/flags-file).
The receiver checks each original Git object ID, commit/root tree, selected path,
mode, SHA256 and both actual HEADs. Only required scripts, two profile patches
and source-certificate files are materialized. Partial repositories are intentional;
their unselected objects are absent. No commit is fabricated and no fixture is
generated on the VPS. The source archive and certificate enter evidence.

This preserves `--no-source` and requires no bucket write from the dispatcher,
new key, resource or IAM change. The default remains public Git fetch.
