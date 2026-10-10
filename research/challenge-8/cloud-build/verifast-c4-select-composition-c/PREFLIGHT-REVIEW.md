# Independent preflight review — session C

Read-only review of the prepared B2 runner changes in proof checkout
`7bc426238fa5abf69ff7e7b15d680c6efc9ff065`, with tool review inherited from
the exact B2 tool commit `e2e674f8727259ef08c68e58bb5dae1bd723cf76`. No code,
tool, or semantic changes were made for this review; no compiler, verifier, or
Cloud operation was run.

## Earlier classifier gaps and B2 transport review

The initial runner accepted selector/imported body headers by presence, which
did not prove unique headers or the dependency order. Its source and contract
admission rows shared one refusal marker, and the reducer initially accepted
any truthy mutation fingerprint. The current diff closes the order/count gap
and validates the source/contract runtime-hash distinction against the pinned
C4 source and raw preflight log digest.

The B2 translator’s transport implementation was reviewed separately at
`e2e674f8727259ef08c68e58bb5dae1bd723cf76`. Its relevant source hash is
`e8ce100375f0befe1bdce4eaec9380c7949dd34488c28f47b89108bc43ec19da` (Git blob
`b817bcf38ef223a5c1e635fab6283b90a3dfbb1d`). The typed certificate scans and
compares headers and package declarations, rejects `InferredType`, rejects
repeated mutable `Ref` identities, and refuses `WSuperMethodCall` because its
`methInfo` field is omitted by the projection. The other known projection
omissions are statement constructors that throw `TODO` during projection and
therefore fail closed. The comparator recursively checks constructors,
containers, strings, scalars, references, and locations, including nested
macro locations; it requires path changes only at exact location endpoints,
unchanged source coordinates, no endpoint strings, matching typed/raw location
counts, and reversible relocation. This is a narrow certificate for the
accepted domain; the Cloud run must still report the exact effective tool and
exporter binary pins and the fresh raw certificate log.

The reachable-unwind mutant in that same translator derives call-edge records
from the admitted body’s actual Reader, requires the unique body-7 line-194
call and baseline count 18, changes only its `Unreachable` action to
`Cleanup(38)`, then uses the same predecessor fold and unchanged expected-count
gate. The fresh raw log should show the source/unit pins, block and normal
target, old/new fingerprints, 18→19 count, and the subsequent inventory
refusal.

## Current runner diff

`run.sh` invokes `source-prepare` immediately after the existing pinned input
preflight and before package installation, downloads, compiler setup, or tool
build. The new mode imports and runs the existing source preparers against the
restored full module pack, checks the selector/C4 source pins, creates source
only regression fixtures, and records that it did not start a compiler,
extractor, or verifier. It uses a dedicated
`allprooflogs/source-preparation/` tree, leaving later proof fixtures under
`cases/integration/`. The stage is guarded by the Cloud lane and exact proof
HEAD checks already present in the runner. This is an appropriate preflight
for the prior import-time missing-module failure and does not claim proof
credit.

The producer sequence gate now requires the seven source-order helpers followed
by nested `Drop::drop` and outer `select_unpredictable`; it requires exactly one
header per target and filters the complete verifier header stream to that exact
sequence. The composition gate applies the same uniqueness and order checks,
and requires every target header before `sort4_stable`. The source MIR order
keeps outer before nested; the verifier order correctly puts nested before
outer. The existing frame audit independently checks the fixed seven-helper
prefix and nested-before-outer ordering. These checks close the earlier
presence-only classification gap.

The current reducer validates source and contract fingerprints against the
manifest’s exact C4 source SHA, validates all four digests as SHA256 strings,
requires a changed source digest, requires runtime hashes to remain equal only
for the ghost-contract mutation, and checks the recorded raw preflight-log
digest. The driver’s preflight-only flag and no-header/exit checks remain in
the reducer. This is a category-specific admission classification.

## Verdict

**GO for the Cloud source-preparation preflight and these classifier changes.**
**Conditional GO for the first B2 Cloud verification run** once the submitted
proof checkout passes the existing exact input preflight and the fresh
source-preparation stage completes with the full pinned module pack. No
semantic change is indicated by this runner diff. The producer AST remains
deliberately pinned to the old reviewed digest; a fresh B2 proof must either
match it exactly and receive raw equality review or stop before composition.
The prior B2 source-preparation failure grants no proof or transport credit.
