# CLOUD-BUILD-MIGRATION acceptance — 2026-10-09

A/B/C are accepted within the scopes below. The cold Cloud Build execution
chain, credential-free pinned source delivery, bucket writes/reads and evidence
checks were exercised. This phase adds no actual SmallSort theorem and does not
accept the whole S6 or O26 profile. No helper/sort4/merge development follows
under this migration authorization.

Entry checkpoint: `89e0a36f8df67bb2f66cf0564f497a0a4bad4aac`.
Branch: `research/cloud-build-migration`, worktree
`/root/verify-rust-std-select-night`. The overnight branch, main/upstream, second
agent's branch/worktree and historical GitHub evidence were preserved.
Tested B/C infrastructure commit:
`30fc3b42a2fb980b49174d459ec5cfbea778379b`.
Subsequent ledger/report commits are documentation checkpoints, not new proof runs.

## Actual results

| Gate | Cloud Build ID | Final status | Charged seconds | Result |
| --- | --- | --- | ---: | --- |
| A storage | `fd0020bd-967d-4e4b-ac20-83c578733389` | SUCCESS | 47 | Small file/manifest written by builder, downloaded and hashed on VPS |
| A managed error | `63862150-33e7-4b9d-b692-1231f9c34520` | FAILURE | 54 | Original exit42 retained; uploaded evidence verified |
| A internal timeout | `6604590a-f626-4ca0-81da-71f3d9091e25` | FAILURE | 59 | Two-second internal timeout, original exit124 retained; evidence verified |
| B stock | `ce77c943-f657-47da-9dfa-4b6e16d3679e` | SUCCESS | 164 | Historical stock matrix reproduced with its classification limits |
| C constructor | `d9e4538a-c6c0-4881-b422-de6ceae72d19` | SUCCESS | 328 | Cold source build and historical constructor component accepted |

Build details: [B](https://console.cloud.google.com/cloud-build/builds/ce77c943-f657-47da-9dfa-4b6e16d3679e?project=smallsort-ci),
[C](https://console.cloud.google.com/cloud-build/builds/d9e4538a-c6c0-4881-b422-de6ceae72d19?project=smallsort-ci).
Successful uploads did not change managed failure/timeout builds into success.
Their `verification_accepted` flags are false; A success is a storage smoke test.

Two additional charged failures remain in the ledger:
`7bda20f0-cef7-4ff4-8c21-697374572b34`,39s, uploader Python-path setup failure
with **incomplete evidence/no archive**; and
`3e4c62e0-744b-4278-b10e-fc74f599dbe7`,81s, anonymous repository fetch failure
with original128 and a verified archive, before any proof tool. Neither is a
proof-negative. Two API validation refusals created no builds and cost0s.
The owner's earlier setup build is separate. A was not repeated after acceptance.

### B: unchanged stock baseline

Original proof SHA: `a0cfd30e066acbaf1b5406cd9773f54388cc45be`.
Historical comparison: [GitHub run37694000195](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37694000195).
Cloud classifier: `STOCK_CHAIN_OPERATIONAL_WITH_HISTORICAL_LIMITS`.

All11 cases retain source integrity, normal/readonly export, decode and refinement
success. Four positives (u32, raw pointer, ordinary unwind, shared cleanup) verify
their exact function/body/return/leak/unwind gates with zero errors. Four false
postcondition/unwind controls fail at their intended obligations. Two
contradictory-precondition controls have the exact raw dead-code rejection;
their historical strict INCONCLUSIVE classifications remain visible. The
generic `forget_positive` is still INCONCLUSIVE with its original dead-code
limitation; this migration does not prove generic forget.

All17 effective stock RSSpec files are byte-identical to the pinned VeriFast
source. Provider overlays change only execution-environment guards. Fixtures,
contracts, expected obligations and classifiers were not weakened.
The fixture body comes from pinned repository source, while external std metadata
comes from the nightly sysroot. Repository `mem/mod.rs` and `ptr/mod.rs` differ
from that sysroot; this is the retained historical boundary, not a rebuilt
repository std theorem.

### C: previously accepted constructor component

Original proof SHA: `1378f0ffc8342233349fae3df5a938c4a021c8d7`.
Historical comparison: [O3/run37700450091](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37700450091).
Cloud classifier: `CONSTRUCTOR_COMPONENT_ACCEPTED`.

The cold chain downloads pinned dependencies, checks/applies the exact historical
patches, builds the console from source and runs the complete selected component
matrix:16 source/proof cases,9 typed MIR admission mutations,10 native controls
(5 stock/5 patched),4 false-post/frame controls. Source and MIR admission refusals
occur at the named expected boundaries, not setup failures. Export/decode/refinement,
positive body checks, return/leak and pointer-option paths are preserved.
Independent artifact review confirmed these results and the patch/profile identity.

Patch order and SHA-256:

1. `overnight-s6/verifast-s6-26.10-candidate.patch`:
   `20f7d07ac9bdaca7c46f737b89925dfac3f4cef66c3f5d48aa9634ac949dbc1c`.
2. `verifast-manuallydrop-new-cfg-2610.patch`:
   `593d09405379974ffbc475c2e0b65d648d8a6913f55b765dd0c3bebdc0922781`.

Effective applied diff SHA-256:
`b47fc7c4b4a64dea0dffa97cdd59b012364d26ce223914abc0130b3cfdac87ab`.
Only `bin/rust/std/lib.rsspec` and
`src/rust_frontend/vf_mir_translator/vf_mir_translator.ml` differ from base.
The migration adds no verifier/kernel/parser/runtime semantics or ghost contracts.
The exporter, refinement checker, C++ exporter and Z3 match stock bytewise;
16/17 effective RSSpecs match, with the one expected patched lib specification.
New source-built console SHA-256:
`f0d3c92651d98d91ceed57d58d93087bee0106a094b7efc1e956820c46132642`.
Binary identity with a historical GitHub build is not assumed.

Scope is the certified local-copy, pointer-specialized constructor and preserved
nonpointer controls. Applicability includes a typed full graph, the external
MaybeUninit constructor redirect, prototype and ownership lemma/body. The
source/MIR correspondence uses reviewed source certificates and def-path strings;
it does **not** establish actual DefId equality. `actual_callee_status=NOT_RUN`.
This is not a generic/ZST theorem or acceptance of the whole S6, O26, helper,
sort4 or merge. Safety and functional SWO sorting obligations are unchanged.

## Pins and source transport

Both B/C use:

- VeriFast base `f76012fb518703b1d98e243ac4f487f16877cfcb`.
- Rust `nightly-2026-09-25`, compiler
  `f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f`.
- std base `cd371e035c7e573760c43bf934d53e8118ee3e7d`.
- Ubuntu22.04 x86_64 proof image
  `ubuntu@sha256:5ec03bb3441e8b0bf3b4f9cd4629a1ae763010dc3035bb8da3ae6cf026486401`.
- Upload/verdict image
  `gcr.io/google.com/cloudsdktool/google-cloud-cli@sha256:c631b05e8121048b29c9917bdc0a9fadd76d012f04f180a4409ec2ee534e832e`.

Owner-approved `pinned-objects` delivery preserves `--no-source`. A narrow
committed-path allowlist supplies original commit/root-tree/ancestor-tree/blob
objects and run data in the explicit build configuration. No working tree,
uncommitted data, Git config/hooks, home, keys or credentials are included.
Cloud checks transport SHA-256, raw object IDs, complete selected object closure,
paths/modes/file hashes and both original checkout HEADs before proof preparation.
The repositories are intentionally partial, have no configured origin, and do not
fabricate replacement commits or download missing blobs. This was exercised
successfully in both B and C. Other public upstream tool downloads remain pinned.

| Identity | B SHA-256 | C SHA-256 |
| --- | --- | --- |
| Submitted config | `f532b8cccd907fef8076a02ba80c7cd4784d8a312825870b6180afcff59d55e0` | `15db37f3bb8b331e06f747c51078d0430e17ecba827ef28c9aeec8269e83fc99` |
| Source bundle | `a1ab7bad2340b84cc556eecb08d5bf99ee658e4f86523f6720cac880de584b3f` | `5a36ec008dbc0db57bcf69efe616057bc93c54c82cb8d97a2e9500344bf78b1c` |
| Evidence archive | `dac3492bb16ff5501403449ddad5a404c989e928259360dac5f20f9c305d4ad6` | `d2ef48f11744fd622520524e2ab859c479a400e17385ddcf982546b0f885d18c` |
| Text index | `6a62d9809e31d62b43235a3a12aaa063ab435287407f3ba1603174dd0ceb4d28` | `72007409313e1d94691b7e465ee214451ceb6d52391aa5d0bd576b30f6136f15` |

## Evidence availability and VPS checks

Archives:

- `gs://smallsort-ci-evidence-504462351565/cloud-build/ce77c943-f657-47da-9dfa-4b6e16d3679e/evidence.tar.gz`
- `gs://smallsort-ci-evidence-504462351565/cloud-build/d9e4538a-c6c0-4881-b422-de6ceae72d19/evidence.tar.gz`

Each prefix also publishes `manifest.json`, `summary.json`, `submitted-config.json`,
`files-sha256.json`, `archive.sha256`, `text-logs-index.json`,
`upload-complete.json`, and indexed full `text-logs/*.txt` objects separately.
ChatGPT already has bucket read access through **SmallSort CI — Read Only**.
The connector was not exposed in this Codex session; VPS dispatcher reads were
actually exercised. No IAM, bucket publicity, credentials or resources changed.

Both complete archives, metadata and **all204 B /482 C separate text files** were
downloaded on VPS into `/tmp/smallsort-cloud-evidence-<BUILD_ID>` and verified:
archive SHA-256, included-file inventory, config/source identities, external
metadata copies, upload receipt, each text chunk and lossless reconstruction.
B archive592869bytes; C archive1218174bytes. Largest separate text object was
63190bytes in B and149690bytes in C. The publisher caps MCP objects at8MiB and
indexes lossless chunks for larger logs; these runs did not need a >8MiB log.

All relevant stdout/stderr, MIR text/binaries, source fixtures, exit codes,
classifications, tool/profile hashes, resources and unknown diagnostics remain.
C omits only duplicate `mutation-profile/bin/**` trees permitted by the historical
component review:810 excluded entries are individually recorded with hashes.
Mutation wrappers/records, canonical and mutated MIR, classifications and logs
remain available. No home, credential or entire toolchain archive is uploaded.
Missing status/archive, packaging error or upload error cannot produce PASS.
Hard executor termination can still leave incomplete evidence; no guarantee is
claimed after forced cancellation or infrastructure loss.

## Budget and measured resources

Charged time is conservative ceil(createTime–finishTime), including queue,
preparation, failures and upload. Execution intervals are recorded separately.
Total **772/3600 seconds**, remainder **2828**:
`39+47+54+59+81+164+328`. Previous reported280 at resumption was retained.
The managed-error charge54 includes queue (execution53); no historical budget is
reset. [Ledger](BUDGET.json) preserves prior accounts and all dispatch attempts.
No build is active or queued at completion. No new phase work is dispatched.

Machine `E2_STANDARD_2`, observed2 CPUs and `MemTotal=8147688KiB`, Ubuntu22.04.5
x86_64, CLOUD_LOGGING_ONLY. Both proof runs were cold and cache-independent.
Measured stage maximum RSS: B toolchain543236KiB, C toolchain546084KiB.
C console compile53.49s,398136KiB maximum RSS,185%CPU; decoder6.30s/337572KiB;
constructor matrix17.09s/95268KiB. B matrix5.04s/96020KiB.
These are per-stage measurements, not a whole-build cgroup peak.

## Permanent workflow and second-direction handoff

Cloud Build performs CI/heavy checks. GitHub stores source, branches, PRs and
documentation; no Actions runs without a separate explicit owner instruction.
VPS editing/orchestration/hash checks/result analysis only. Existing automatic
Actions events were not changed and are listed separately in
[GITHUB-TRIGGERS.md](GITHUB-TRIGGERS.md). No triggers, persistent CI service,
new pool/VM, IAM changes or upstream publication were added.

[README.md](README.md) gives exact tested submit/status/download/hash/cancel
commands, including infrastructure30fc3b42 and each original proof SHA. The
lightweight `control.py` retains explicit gcloud configuration/account/project/
region, detects uncertain dispatches, charges actual timestamps and refuses an
additional queued/running build. Download with `--text-logs` verifies all separately
published logs as well as the archive. VPS timeout does not cancel Cloud Build.

The second direction can use the provider/transport/evidence interface while
preserving its own original proof SHA, patches, pins, expected obligations and
separate authorized budget/account. Its recipe must be reviewed and explicitly
selected; the current two lanes intentionally reject unrelated proof checkpoints.
It must not inherit constructor acceptance or merge research profiles implicitly.
Share the one-build project gate, keep unresolved dispatch state until reconciled,
and never edit the other agent's worktree. The second agent remained paused during
this phase. No new credential or administrative setup is required for the tested
stock/constructor commands.
