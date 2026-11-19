# Network-r2: coordinator publication and single trigger

Use only after this packet is sealed with GO-REQUEST.json READY and the final host Validate PASS/margin gate. Root does not publish, create the actual trigger, push, launch CI or account. No extra approval round is needed when every stated binding passes.

## Exact source publication

Repository: Tiramisu-Cake/verify-rust-std. Publish **exact commit 8faf8e62af8f82b5c46af020086f8df591b6757e** to **experiment/ch8-s4p-2-r2-20261119**. Tree must be **91f097cdb4085d30c4b94afbb843aeb34f1d3287**, sole parent **c12867b1e651a3927cbd9f169fe2c3d3728a44c3**. The local branch experiment/ch8-network-r2-offline-20261119 already points to these reviewed bytes; do not regenerate or replace the source SHA.

Equivalent coordinator command, using the authenticated fork transport:

```sh
git -C /root/verify-rust-std-ch8-s4p-2-w13 push https://github.com/Tiramisu-Cake/verify-rust-std.git 8faf8e62af8f82b5c46af020086f8df591b6757e:refs/heads/experiment/ch8-s4p-2-r2-20261119
```

Before any control push, independently read the connected remote source ref and exact commit and verify fetchability/head/tree/sole parent. The prepublication connected snapshot was404 for source/ref. Recheck destination-ref state; unexpected existing refs require coordinator reconciliation, never force. Source remains the exact request.std_sha, even if another commit has the same tree.

## New control trigger: same-tree sibling

Repository: Tiramisu-Cake/kani. Proposed ref **uninit-ci/ch8-s4p-2-r2-20261119**. Create a fresh NONSKIP commit with tree **628a9aa91c86a2e5f72efee626b58f1715ec3dbf** and sole parent **4059c900e50ba179d824a1e6f6bd7798cf343e36**. It is a sibling of reviewed local candidate **3d3fb715271e3b195c6e0eee3557d5b0a6aad00d**. Do not parent the trigger to that candidate or to old9e14. Exactly one commit4059..TRIGGER; no skip directives in its message.

The following are coordinator instructions only; root has not executed them. The task-specific variables avoid changing shell/system environment options:

```sh
network_r2_trigger=$(printf '%s\n' 'CH8 network r2 concrete calls at unchanged caps' | env GIT_AUTHOR_NAME=Tiramisu-Cake GIT_AUTHOR_EMAIL=igkharin@gmail.com GIT_COMMITTER_NAME=Tiramisu-Cake GIT_COMMITTER_EMAIL=igkharin@gmail.com git -C /root/kani-ch8-s4p-2-r1-control-w13 commit-tree 628a9aa91c86a2e5f72efee626b58f1715ec3dbf -p 4059c900e50ba179d824a1e6f6bd7798cf343e36)
python3 check_future_trigger.py --repo /root/kani-ch8-s4p-2-r1-control-w13 --head "$network_r2_trigger" --ref uninit-ci/ch8-s4p-2-r2-20261119 --out /tmp/network-r2-final-trigger-check.json
```

Run the helper from this GO packet directory. It checks full SHA/tree/sole parent/range1/NONSKIP/request/workflow/155payload/source-tool/8Original-null bindings using read-only Git objects. Its MATCH is an identity result, not a new authorization. Remote source fetchability and remote-ref absence are separate connected checks. Preserve the actual full trigger SHA and report with the coordinator dispatch record.

Create the new local branch without overwrite, check the remote destination remains unused, add the coordinator ledger row, and push **once**:

```sh
git -C /root/kani-ch8-s4p-2-r1-control-w13 branch uninit-ci/ch8-s4p-2-r2-20261119 "$network_r2_trigger"
git -C /root/kani-ch8-s4p-2-r1-control-w13 push https://github.com/Tiramisu-Cake/kani.git refs/heads/uninit-ci/ch8-s4p-2-r2-20261119:refs/heads/uninit-ci/ch8-s4p-2-r2-20261119
```

No force, amend, merge, extra commit, source/control/request/workflow change, workflow_dispatch, subset, cap escalation or rerun is covered. Capture actual GitHub run ID/attempt1/push/head/ref/workflow/job metadata after dispatch. Their values are UNKNOWN until then. The workflow branch filter is uninit-ci/ch8-s4p-*; filename ch8-s2.yml, job s3_leaf, profile ch8-s4p-2r2-network-fullbyte-concrete-calls-v1.

## Unchanged limits and postrun gate

Checkout depths are **control8/source6/tool2** for these one-generation child candidates, not the old7/5. Stock tool0aac16ef62da9e9d5645782d458593e5d78143ba is immutable. Request SHA256 fd2b608a5538779f5f0345a49e5c147646d82dc6d066fdd1e3b50d0e6bc69e39; workflow SHA256 d5dd5942297df013e625b85890fcc3884ec6b60d1f08c8e1dc51c019ce15fdfc.

Child600 includes compile180; slot720; local6GiB sampled ownedPGID; outer12GiB owned census; reserve2GiB available memory; Ceff=min(6,12,A-2); campaign6900; setup1800; job180min. All remaining timeout/output/policy bounds are unchanged. Eight-slot6180 is arithmetic, not native fit. One attempt only, no automatic retry/cancel/follow-on. Numerical budgets remain TRACKING_ONLY; root/worker do not change accounting.

After actual terminal, keep native/producer-strict/S1-source-reported/admission separate. Metadata/digest first, sole compact member group-evidence.json.gz under historical artifact prefix ch8-s3-2-RUN-ATTEMPT; no raw/full/ZIP/GCS. Complete safety/unwind/role/SAT/U/guard/location/identity/cleanup/prefix evidence is required. Old exact location exceptions do not transfer. Timeout/partial stays UNKNOWN; no automatic admission/provider/init/fullN16N32/MIR/B1B2 credit or publication.
