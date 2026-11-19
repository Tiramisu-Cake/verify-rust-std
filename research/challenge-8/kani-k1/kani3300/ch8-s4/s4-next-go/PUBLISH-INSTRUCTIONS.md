# Coordinator handoff — S4P3 publication and one bounded attempt

These instructions become actionable only with the sealed ROOT AGREE and a PASS final Validate receipt in this directory. Root does not publish, dispatch, reserve or account.

1. Recheck reviewed package `f485968493d3512f3e719825ef4490866808d120`, exact review `507dbcfd524ef96407c742738b66abf2a2818a10`, and the final receipt. Recheck all three clean local heads/trees/sole parents. The prepared author descriptor stays historical PREPARED_NOT_RUN/count0; the root receipt records the one actual execution separately.
2. Recheck connected ref absence for source `Tiramisu-Cake/verify-rust-std:experiment/ch8-s4p-3-20261119` and control `Tiramisu-Cake/kani:uninit-ci/ch8-s4p-3-20261119`. If either now exists, inspect exact identities and existing runs rather than repeating a push or launch.
3. Publish exact reviewed source `7b31b060b90ce286e94547993f6a698c549bc5fa` from `/root/verify-rust-std-ch8-s4-next-w15` to `experiment/ch8-s4p-3-20261119` in `Tiramisu-Cake/verify-rust-std`. Expected tree `fccf3284bd678626c8f8cea72bbe6ec72964dbd9`, sole parent `8faf8e62af8f82b5c46af020086f8df591b6757e`. Preserve this exact source commit; do not substitute its parent or a later tip. Confirm connected remote head/tree/parent and actual fetchability before the trigger push.
4. Create one new NONSKIP control sibling with **tree `09938d27a127351f5c51b6c9f451602d797a1c0f` and sole parent `3d3fb715271e3b195c6e0eee3557d5b0a6aad00d`**. It is a sibling of reviewed local `65a9ea656a4b5f1e66f7b31eceffb5eefeba7541`, not its child. Do not use old parent `4059c900e5` or `9e14e033f9`. Use author/committer Tiramisu-Cake <igkharin@gmail.com>, a plain trigger message with no skip directive, and no tree/source/request/workflow changes. A commit-tree operation against these exact objects can create the sibling without resetting or editing a reviewed worktree. Root creates no trigger object or ref.
5. Before push, run the read-only gate on the actual newly created full40 SHA:

```sh
python3 /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-s4/s4-next-go/check_future_trigger.py --repo /root/kani-ch8-s4-next-control-w15 --head ACTUAL_FULL_TRIGGER_SHA --ref uninit-ci/ch8-s4p-3-20261119 --out ACTUAL_GATE_RECEIPT.json
```

Require exit0, status MATCH, errors[]; retain the gate receipt. The reviewed skipped candidate is an authentic REJECT control, retained in `trigger-gate-reviewed-candidate-negative.json`. A gate result is identity checking, not launch authority or source fetchability evidence.

6. Coordinator adds the required tracking-only item-2 ledger row under the current policy, then pushes the actual sibling once to `Tiramisu-Cake/kani:uninit-ci/ch8-s4p-3-20261119`. This is one bounded eight-root attempt, no manual rerun or automatic retry. Root GO changes no accounting totals and grants no extra numerical reservation.
7. Bind actual run/head/ref/event/attempt/workflow identities immediately after dispatch. Workflow `.github/workflows/ch8-s2.yml`, job `s3_leaf`, ubuntu-24.04; source checkout depth7, control9, stock tool2. Request SHA256 `693e12689bfee859560d5042a36fd8b80051e9fca4082fd1a612642d7e389e30`; workflow SHA256 `fc21d9f44a403b6294daaca2b25fdfcebe38d3dd7e89a927af0d289a86c177a0`. Stock tool remains `0aac16ef62da9e9d5645782d458593e5d78143ba`. Actual trigger SHA and run ID are UNKNOWN until coordinator creation/dispatch.
8. After actual terminal status, assign bounded compact intake and independent review before any admission. The intentional historical artifact prefix is `ch8-s3-2-RUN-ATTEMPT`, sole member `group-evidence.json.gz`; metadata/digest first through the authorized reporting interface. No raw logs/full archives/GCS bypass.

Scope: four unchanged negatives first, then actual network u8/KeyLess full-byte initialized V34/base1 literal N8/N9/N13/N17. Every row Original/null; four exact SUCCESS roles and six SAT covers per positive. Unwind34/34/34/36 for controls and36 for positives, checks on. No summaries, target substitution or extra input restrictions. N17 ends before final merge; N18+, other lengths/types, caller/provider/init/MIR and independent full proof stay open.

Resources remain child600 including compile180, slot720, controller180, cleanup240, campaign6900, outer7500, step7560, phase8100, setup1800, job180min, sampled-owned-PGID local6GiB, owned-census outer12GiB and available reserve2GiB (Ceff=min(6,12,A-2)). Output16MiB/1MiB/8MiB, artifact256MiB. The6180 envelope is arithmetic, not measured fit or a true kernel/cgroup peak bound.

Native cost fit and lowered unwind sufficiency are UNKNOWN at GO. Preserve ZERO_U/REJECT_ALL, unsupported guards including SUCCESS records, exact role/status/SAT/location/source/request/tool/invocation identities, structured portable prefixes and cleanup facts. Historical S1 arguments, location exceptions, role IDs and admissions do not transfer to these new invocations; any future U/model/builtin/location proposal needs its own evidence and review. No automatic qualification or provider credit.

## Exact Git operations for the coordinator, after the gates above

Source publication (once; no regenerated source commit):

```sh
git -C /root/verify-rust-std-ch8-s4-next-w15 push https://github.com/Tiramisu-Cake/verify-rust-std.git 7b31b060b90ce286e94547993f6a698c549bc5fa:refs/heads/experiment/ch8-s4p-3-20261119
```

Create the trigger object without changing the reviewed worktree or its branch:

```sh
S4P3_TRIGGER_SHA=$(git -C /root/kani-ch8-s4-next-control-w15 -c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com commit-tree 09938d27a127351f5c51b6c9f451602d797a1c0f -p 3d3fb715271e3b195c6e0eee3557d5b0a6aad00d -m 'Run bounded S4P3 full-byte network boundaries')
```

Use that actual full SHA in the read-only gate, confirm source fetchability/ref absence, and record the coordinator ledger row before this single trigger push:

```sh
git -C /root/kani-ch8-s4-next-control-w15 push https://github.com/Tiramisu-Cake/kani.git "${S4P3_TRIGGER_SHA}:refs/heads/uninit-ci/ch8-s4p-3-20261119"
```

Root prepared these operations as text only and executed none of them. Do not repeat them if dispatch or matching refs already exist.
