# G1 implementation candidate — independent review required

2026-10-11. **IMPLEMENTED CANDIDATE / FRONTEND NOT_RUN / CLOUD 0/0.** Baseline
[78063c897cfb817361b2947cbe24e49570f707df](https://github.com/Tiramisu-Cake/verify-rust-std/commit/78063c897cfb817361b2947cbe24e49570f707df).
This assignment authorizes isolated harness/recipe development only. Production
coordinator, common Cloud scripts, CI, std runtime and trusted RR semantics were
not changed. No PR/Tool Application. G1 remains frontend admission/diagnostic;
Rocq, generic CURRENT recovery and G2 remain NOT_RUN.

## Identity and actual obligation

| Input | Fixed identity / publication gate |
| --- | --- |
| Read rules | snapshot `c7ca8c467aecf10a4b53039372ee97714f854ee3`; last AGENTS/WORK-POLICY change `5bf53668a4afa51c302e599be91a2dbc4b24042d`; own index/worktree unchanged |
| Actual source | `c7ca8c467aecf10a4b53039372ee97714f854ee3`; library tree `4ae912b9caf2e477a2b0caef084fb349c878f0fd`; SmallSort blob `e555fce440872898e47fd5114f32eb15401d07df`, SHA256 `32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959` |
| RR | unpatched `332d945fafa14bf55c0c8390cb35ec4b0c012cff`; compiler nightly-2026-08-28 / `e457a7b0d326d67b4322ef0d11bd715cfaeda48f` |
| Harness/proof source | This package's published commit, reported in final answer/branch tip. It must be frozen as a full SHA in future authorization and pinned-object certificate; baseline 78063c89 contains only design docs |
| Infra | Unapplied patch baseline `ac6a1c4ebe84ee05302f4cc5829ff1075e99d822`; operational resultant infra SHA **UNASSIGNED**. No existing peer runtime has been adopted or registered |
| Image | OCI digest **UNCONFIRMED**, OS/vendor/deb context **UNFROZEN**; current nulls block execution |

Preflight found clean own branch at baseline, fork origin fetch/push and separate
index. Fetch confirmed origin/main remains c7ca8c4. Latest read merge checkpoint
[2b109b92fb9a04706fdf3acb0007c185c579d984](https://github.com/Tiramisu-Cake/verify-rust-std/blob/2b109b92fb9a04706fdf3acb0007c185c579d984/research/challenge-8/cloud-build/origin-layout/FINAL-CHECKPOINT.md)
retains actual glue exporter compile failure and unproved generic recovery.
This package neither replays nor upgrades peer evidence.

Hypothesis: unchanged RR can compile/admit exact generic insert_tail and actual
wrapper/guard/glue operations with real normal/first/late unwind paths. A compiler
mismatch, selected unsupported operation, absent callee binding or lost cleanup
falsifies the corresponding admission gate. The caller remains actual arbitrary-
length insertion; no safety premise, length cutoff, Copy/Freeze/purity/no-panic
restriction or new owner bridge is supplied. Final normal/unwind resource posts
remain those in EXPERIMENT-PLAN, not the diagnostic default specs generated here.

## Concrete diff and architecture

All edits are under this mission directory. [g1/README](g1/README.md) defines
interfaces, evidence and future command shapes.

| Component | Implemented behavior / limit |
| --- | --- |
| [inputs.json](g1/inputs.json), [verify_inputs.py](g1/verify_inputs.py) | Exact commits/trees/blobs/SHA256 anchors; pristine checkout and physical tracked-byte/mode audit of all library and RR files. Git status alone is insufficient. Reject ambient Cargo configs and unmaterialized/unfrozen Gitlinks |
| [annotations.json](g1/annotations.json), [annotate.py](g1/annotate.py) | Unique, pinned insertion anchors; core register_tool header, three ADT refinements, six actual functions; byte-offset stripping before/after writes; archive originals/annotated/stripped sources. Injector is Cloud-only and **NOT_RUN** |
| [run.py](g1/run.py), [entrypoint.sh](g1/entrypoint.sh) | Auth/pin/image/compiler gates, P0/N1/N2, native exact-core check before ghost insertion, stock RR generation; separate target caches, full logs/config/env/timing, fail-fast deadlines and collector. No dispatch, installation or Rocq commands |
| [service.py](g1/service.py), controls | P0 own trivial frontend definition; N1 own unregistered callee; N2 frozen wrong-source-SHA certificate at named source metadata gate. P1 uses actual core. Reject unrelated N1 primary errors; signals/setup/unknown target attribution do not earn negative credit |
| [correspondence.py](g1/correspondence.py) | Saved-output parser: independent ghost strip, selected MIR/Radium calls/blocks/edges, first/late/normal guard cleanup, no tmp payload Drop; seven body maps (six functions plus compiler glue), call/spec inventories. Externally reviewed hash-bound map required; no whole-file marker shortcut |
| [evidence.py](g1/evidence.py) | Per-file bytes/SHA256 inventory, required receipts, no links/extras, independent identity matching, recomputed controls/verdict; optional independently hashed map replay without mutating logs. verification_accepted=false and proof_status=NOT_RUN |
| [cloud candidates](g1/cloud/REVIEW.md) | Offline cold Dockerfile, image receipt generator, cold/warm configuration, candidate recipe and unapplied dispatcher proposal; image and registration remain absent |

A new closure finding is recorded in inputs.json: library/backtrace is a Gitlink
at **28ec93b503bf0410745bc3d571bf3dc1caac3019**, unlike ordinary stdarch/portable-simd
trees. Future Cloud restoration must materialize and verify it from pinned
.gitmodules. No submodule or extra checkout was downloaded on VPS. Core's safety
proc-macro additionally needs the locked proc-macro2/proc-macro-error/quote/syn
closure; frontend-only RR vendor cache is not automatically a complete native
core/workspace cache. Cold input context must cover both lockfiles.

## Trust boundary and unresolved gates

No code-shim or trait summary is added, no upstream proof code is imported into
our proof, and RR/kernel/translation/memory logic is unchanged. Diagnostic
`may_unwind_if("True")` permits panic; it does not assert exceptional ownership
recovery. Unit ADT refinements/default generated specs are diagnostic inputs,
not proved complete ownership contracts. Runtime equality does not alone prove
annotation-neutral MIR: source/callee/cleanup correspondence remains required.

The strict runner deliberately imports no stdlib summaries into actual core.
Pointer wrappers/FnMut bindings and recursive callee closure are **not known
closed**. Existing RR ptr models are inventory boundaries, not actual-callee
proof credit. A missing ordinary binding is LIBRARY-SPEC, distinct from an
unsupported Rust operation and from an unproved ownership lemma. Native Cargo
compiler errors can produce STOP; missing offline dependencies/timeouts are
INCONCLUSIVE. For failed RR export whose diagnostic lacks selected caller/span,
automatic classification stays INCONCLUSIVE pending independent raw-log
attribution; a confirmed selected gap is recorded as STOP in reviewed closeout.

Stock RR supplies MIR dumps and Radium definitions, but no complete machine-
readable source→Radium map. Hence even exit-0 P1 cannot receive automatic G1 PASS.
Post-Cloud independent review must freeze a `g1-reviewed-correspondence-v1` map
with body/event/local/callee/resource fields and file hashes. The parser checks
syntax/graphs; a reviewer still validates actual DefId/type substitution,
location-parameter binding and spec interpretation. Resource definitions alone
do not prove scalar↔len1 layout, CURRENT F/T, interior mutation or ownership.
Missing dependency/spec artifacts under P1 evidence keep these gates open.

The in-image receipt cannot contain its own final registry digest. Runner checks
its RR/compiler/component/binary/config relations, then requires an externally
reviewed cold registry binding. The dispatcher must independently verify the
executing step digest and submitted config/API identities; BUILD_ID or a local
JSON is not authentication or authorization. That transport is not implemented.

The isolated dispatcher proposal retains a submit rejection. It identifies
Ubuntu image, machine/disk and phase/owner hardcodes but is **not an operational
patch**. Production recipe validator currently rejects our proof-side entrypoint;
choose/review an infra wrapper or narrow transport proposal. Common packager
expects proof-shaped outputs; adapter must preserve diagnostics and set accepted
false. These are integration review blockers, not permission to apply the patch
or alter max-two/one-owner coordination.

## Validation and required review

Performed: Python AST parsing (no driver imports), JSON parsing, shell syntax,
Git/manifest hashes and unique annotation anchor checks; candidate path audit;
unapplied patch syntax/applicability check against exact ac6 bytes. **15/15
isolated service-only synthetic tests PASS**: source metadata, intended negative
classification, inventory tamper/link/extra detection, MIR/Radium graphs and
missing-map/payload-Drop rejection. Synthetic MIR is explicitly synthetic;
reading fixed source bytes for parser/hash fixtures is not an extraction run.
No injector, compiler, RR binary, Docker build, dependency installation or proof
runner was executed. Native/source admission, actual cleanup and image validity
are **NOT_RUN**. Successful service tests qualify the classifier only.

Independent reviewers must inspect ghost defaults and unchanged signatures;
actual trait/pointer/callee registration; parser/map limitations and negative
specificity; image context/loader/compiler provenance; source transport and
provider/packager integration; budget/watchdog behavior and v2 compatibility.
The practical decision remains **GO for independent implementation review;
NO-GO for Cloud authorization now**. See [dispatch gates](G1-DISPATCH-READINESS.md).
