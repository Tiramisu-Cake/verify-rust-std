# C2-SLICES / stage0 / worker14

Entry g0: `203c712c6b7ac3898f105c3ca89fe0d9a026baf6`. Research only; source F and B1 remain clean and pinned.
Dedicated `/root/kani-fix-3300-c2-slices-w14` is a clean detached worktree at existing B1, ready for a separately issued stage1.

Read `INPUTS.json` → `FILE-HUNK-MAP.md` / JSON → `SEAMS.md` → `DEPENDENCIES.md` / JSON.
`UPSTREAM-SNAPSHOT.json` records main=U, #5172 open/unmerged with head=B1/base=U and both fork freeze refs=F,
with UTC observation timestamps and PR/commit timestamps. No upstream drift was observed.
The PR's `merge_commit_sha` is a test-merge candidate, not evidence of merge or the extraction base.

The inventory covers **all24 changed production/source files**, **36 U→B1 hunks**, **225 B1→F hunks**;
all changed +/- lines have one owner. Embedded compiler unit tests are source-inventoried with their owning feature;
their oracle/test qualification map remains worker15's area. All368 other changed paths are tests/docs, enumerated
only for a complete path partition in INPUTS; worker14 makes no oracle/docs ownership decisions.

Original blob IDs, modes, full SHA256, exact old/new ranges, nearest preceding declaration anchors, patch and hunk/part
hashes are in JSON. Those anchors are lexical navigation, not parsed symbol/AST ownership. Mixed Git hunks have explicit
owner parts; individual +/- line parts are not independently applicable patches. Extraction must keep complete Rust
syntax/imports/callers together and obey the semantic seam notes. Raw source diffs are research baselines, not slice patches.

Two dependencies refine the initial outline:2 borrows only the exact layout qualification helpers it already calls;
4 receives projected-raw/address behavior needed by MU safety.6 retains only its edge qualification. These refinements are accepted by the variant C decision below.
F7 stays7; earlier heads use exact historical cache writes/import from PRE-F7.json, with no early fake API.

`STATIC-CHECKS.json`: all source patches reconstruct their target blobs byte-for-byte **in memory**;
B1 parent=U, B1 ancestor of F and F tree pin checked. `RESEARCH-VALIDATION.json` adds path, digest and seam checks.
`build_source_map.py` regenerates the inventory from read-only Git objects; `validate_source_map.py` checks it independently.
These are static consistency checks. No intermediate compile/proof/regression success or exact final recomposition is claimed.

Required inputs read: TASK/PLAN-C2, R4 answer14, S5 ORACLE-MAP(.md/.json), MODE-COVER-MAP,
DISCOVERY-DELETION-MAP, SENSITIVITY-MANIFEST; S6 CONTROL-MAP/DOCS-SCOPE-MAP; final Quick/Gate A/Gate B′ acceptance documents.
Historical NOT_RUN fields in old maps do not supersede later acceptance. Those acceptances qualify **F**, not future sliced heads;
this stage does not independently re-audit their CI evidence or establish formal proof credit.

NOT_RUN: local native builds (prohibited), CI, push, intermediate head Quick, source slicing, full-tree recompose.
Parallel oracle/docs map is neither modified nor accepted here. This handoff completes worker14's stage0 assignment;
the coordinator owns combined-map acceptance and issuing the next stage.

## Accepted dependency decision for stage1

TASK @`4fef62ad67`, variant C supersedes stage0 review-pending language above.
Recognition/for_storage helpers stay2; all projected-raw guards and exact V420–424 part move to4; E1 has no required production residual.
Head1 is `NO_REGRESSION`, integration `PENDING` on heads `[4,5]`: no new non-MU fixtures, no golden weakening, no early closure/storage prerequisites.
Head4 closes owner1 DAG/cycles/root-order and ordinary payload/padding; head5 closes ordinary positive/capture-free and all mapped contract/strong/mode/root obligations.
Nested Pat/enum/raw-eq-uninit integration of owner3 waits4; generated-modifies-no-shadow waits5.
Stage0 findings are static dependency observations, not failed runtime runs. Canonical updated parts are in JSON; stage0 pins remain available at bf455494e4.

Current stage1 source/patch/static result and pending integration obligations: `../slice-01/SLICE.json`. The preceding stage0 status is historical.
