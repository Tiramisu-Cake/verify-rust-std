# SmallSort CI Evidence Brief policy

Policy revision: 2026-10-17 (Europe/Moscow). Applies to all SmallSort agents,
worktrees, and reviewers. This policy takes precedence over conflicting ordinary
agent evidence-reading instructions elsewhere in the repository.

After a Cloud Build reaches terminal status, obtain its result with
`smallsort-brief BUILD_UUID`. The compact Evidence Brief is the default and
authoritative reporting interface for CI evidence available to ordinary agents.
Use its distinctions and limits when reporting the result.

Build status, `diagnostic_complete`, `evidence_complete`, and
`verification_accepted` are separate facts. A successful Build or completed
collector does not establish proof acceptance; NOT_RUN is not PASS. An observed
first error is not automatically an independently established causal blocker.

Ordinary agents must not read or download full Build logs, full verifier logs, raw
GCS evidence archives, Cloud Logging output, or equivalent evidence through
connectors or other alternate interfaces. This also applies to evidence already
present locally.
Do not invoke `control.py download`, `gcloud storage cp`, `gcloud logging read`, or
`gcloud builds log` for evidence review.

If the Brief is missing, incomplete, or insufficient, report that limitation.
Do not infer proof acceptance or fall back to raw evidence. Request a separately
authorized administrative audit when raw evidence is needed; that request alone
does not authorize the audit.

`VERIFIED_ARCHIVE_AND_INVENTORY` establishes archive and inventory integrity only;
it does not establish successful formal verification. Preserve the distinction
between B1 bounded evidence and B2 full target proof, and between source-reported
claims and independently established proof. Never set `download_verified` from a
Brief or rewrite historical evidence or ledger records.

Small synthetic classifier/parser service tests remain allowed under the existing
VPS exception. Do not use that exception to replay full raw evidence; raw replay
requires a separately authorized administrative audit.

Coordinator submission, status, cancellation, slot coordination, budgets, phases,
owners, and deadlines remain governed by their existing procedures. This policy
does not change backend evidence production, storage, or hash processing, nor IAM
or runtime behavior.
