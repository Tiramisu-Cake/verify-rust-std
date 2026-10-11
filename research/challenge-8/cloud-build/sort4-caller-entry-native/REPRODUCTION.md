# Exact commands and evidence — recorded session, now CLOSED

These are historical dispatch commands, not authorization to dispatch again.
The account is CLOSED, unused seconds retired, and current profile disabled.
Any fresh proof execution needs a newly authorized session/phase/account and
matching admission pins; do not bypass expired guards or edit the coordinator.

Worktree `/root/verify-rust-std-select-night`, owner `select-sort4`, provider
`smallsort-ci/global`, lane `o26-sort4-c1-current-recovery`. Each dispatch used
the same exact proof and infra SHA from this table, timeout1200/reserve1260.

| Build | Exact proof/infra commit | Conservative seconds | Raw archive SHA-256 |
| --- | --- | ---: | --- |
| a125db66-0204-47bb-964f-c3134d4b6eef | 46ffa84f717d428a5da91ef2f86d9024ede90fcd | 394 | 045e43a175079115c36a309ef796bd9edd866d68ebd759b14c6cbafe663aaf1c |
| 1d2237d7-2183-48ff-8aa9-a6c8d29fcd83 | 0a61febf105b29dcb89d6fc25ec993bdcfd17e46 | 374 | 9a0aa14a804981b9fed0feca217c706827bab7bda563238bd800221d609d288c |
| d352b4a6-d86d-48b4-86ca-cdccb0af4d89 | 3ed89d79a4d0c389607fac7eb0b3909d7e7d4b28 | 389 | ae39f373baf16748479cb05c0874e5c51536a8a692bfcfd63037778b6e1e9e75 |
| 00e90a4b-b7ed-4b92-8b07-bbf168dbc820 | 4871e8a6b47d9f863d42df802233496a051a7242 | 432 | 2c3e5c6870d51c605221f875abf87d7d21e7ef814b53614d2f84fefde7782760 |

For each row, the exact command shape was (substitute only the row's SHA):

```bash
python3 research/challenge-8/cloud-build/control.py \
  --phase-id SORT4-ACTUAL-CALLER-ENTRY-CLOUD-2026-10-11 \
  --ledger /root/verify-rust-std-select-night/research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-2026-10-11.json \
  --state-dir /tmp/smallsort-cloud-sort4-caller-entry-20261011 \
  --owner select-sort4 submit \
  --infra-sha "$sort4_recorded_sha" --proof-sha "$sort4_recorded_sha" \
  --lane o26-sort4-c1-current-recovery --source-mode pinned-objects --timeout 1200
```

Evidence retrieval used the same global arguments and
`download BUILD_ID --output /tmp/caller-entry-SHORT_ID-read --text-logs`.
The client independently verifies archive/config/input/receipt/text-log
transport, records download verification, and reconciles its own Build.
Safe extraction into `/tmp/caller-entry-SHORT_ID-raw` checked the archive digest,
rejected symlinks and paths escaping the destination, then reviewers rehashed
all inventory entries and checked intended errors in complete target logs.

Persistent raw evidence root for each Build is
`gs://smallsort-ci-evidence-504462351565/cloud-build/BUILD_ID/`.
`evidence.tar.gz`, `files-sha256.json`, `submitted-config.json`, `manifest.json`,
`summary.json`, upload receipt and text-log index/chunks are preserved there.
Collector success is not proof PASS. Exact config/payload hashes and tokens
are in the ledger and PRE-DISPATCH manifests. Fresh review files give each
source/MIR/AST/log identity, target exit, intended location and profile stage.
No downloaded log, generated Rust or binary is committed as research source.
