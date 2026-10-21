# Tool staging into evidence: local service repair, 2026-10-21

Status: locally validated; independent Luna HIGH review GO. No Cloud Build
submitted for this repair; formal proof credit remains zero. The closed R11
account, archived R11 inputs and submitted Build identities are unchanged.

The user reported repeated packaging refusal for `synthetic-tool/.devcontainer`
and `r11-storage-placement-controls/duplicate_live/tool/.devcontainer`: tool
worktree links entered evidence, upload did not occur, and FileNotFoundError /
Reader HTTP 404 followed. This is an owner-reported infrastructure cause, not
newly retrieved Build6 proof evidence. Build6 compiler, actual and control results
remain unknown. Existing historical records are retained.

The common producer was `first-callback-admission-controls.py::_tool_tree`,
which linked every non-bin root entry and non-entrypoint bin asset into the case.
R11 replay and the verifier/refiner admission controls share this helper. Other
copies found in m2-admission-prove and or-join-liveness use disposable scratch
outside evidence and are outside this defect's path.

The helper now copies only regular `bin` assets recursively. This preserves
VeriFast's executable-relative `rust/prelude.rsspec` and `rust/std/lib.rsspec`
and sibling runtime assets. Tool root source, Git/developer configuration and
other non-bin subtrees are excluded in their entirety. No `.devcontainer`
exception is hard-coded. The caller still installs its hash-checked verifier or
refiner and exporter wrapper; all five executable-copy sites use the common
no-follow, regular-file, exclusive-destination copy helper.

Each case gets `tool-staging.json` with schema
`smallsort-tool-evidence-staging-v1`: copied relative paths, sizes and SHA-256;
excluded paths, kind and reason; symlink target text via readlink; caller-managed
entrypoints. Excluded directory entries explicitly cover the entire subtree.
Symlinks, including dangling, absolute and cyclic links, are metadata only;
their targets are never automatically copied. Special runtime entries and
invalid home/bin roots fail. Partial staging records FAILED with the error;
existing output/manifest is never overwritten. COMPLETE means asset staging
completed, not that caller execution or verification succeeded. A source symlink
at a caller-managed executable is refused by its later strict copy.

Original `LD_LIBRARY_PATH` behavior is retained: dynamic libraries may still be
loaded from the pinned original tool bin. This evidence tree is not claimed to
be a self-contained offline replay installation. Required runtime inputs must
be regular files; omitted linked runtime assets cannot establish a successful
execution. Package-wide rejection of unexpected evidence symlinks remains intact.

Local validation:

- `tool-evidence-staging-service-test.py`: 7 tests pass. Both known cases are
  represented in one synthetic result tree passed through the real packaging
  CLI, producing `evidence.tar.gz`. Every archive member is regular; inventory
  coverage and every SHA-256 match. Case sources, MIR, logs, wrappers and runtime
  specs remain byte-exact; the source tool tree remains unchanged; target
  sentinel contents do not leak into evidence.
- Error-path tests cover file/directory/dangling/cyclic/absolute symlinks, invalid
  roots, FIFO after earlier files were copied, existing destinations and source
  or destination symlinks during executable copying. Unrelated evidence links
  still make the packager refuse.
- Existing R11 placement controls: 13 tests pass; R8 freshness controls: 10 pass;
  package profile checks pass; R11 overlays: 3 pass; base pins: 3 pass.
- R11 static source/19-patch composition/provider pins/recipe closure passes;
  shell syntax and diff whitespace checks pass. No compiler/exporter/verifier
  was executed locally.

The new suite is included in the proof recipe and the existing Cloud static
preflight, before expensive setup. It tests the selected infrastructure
packager through `SMALLSORT_TEST_PACKAGER`; locally it defaults to the adjacent
package-evidence.py. The changed R11 provider source pin is updated. Historic
R11 input hashes are not restamped. Future authorized submissions must use the
new source commit; this local repair does not itself authorize a Build or reopen
any budget.

Review: `/root/r10_review`, GPT-6 Luna HIGH, read-only review of implementation,
relative runtime-spec dependencies, no-follow policy, tests, recipe and preflight
wiring; no blocker, final GO. Limitation about original LD_LIBRARY_PATH retained.
