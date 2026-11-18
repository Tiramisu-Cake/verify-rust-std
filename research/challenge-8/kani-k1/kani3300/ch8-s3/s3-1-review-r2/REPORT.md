# SAME14 path delta: APPROVE

Review of exact package `008fcb7705e658643582668ebfabb5f2e340e95d` under task
`e2ea94d04c9d9977ac9cde891c13a73ee65f2ec4`, TASK-CH8-S3-1-PATH-DELTA-W14.md.
No blocking or new finding remains within this path representation delta.
This disposition permits the separate root decision about a **new GO only**;
it neither issues GO nor authorizes a launch. Old GO9929 remains spent.

| Input | Exact identity |
|---|---|
| Control | `cb63033ffcde918f4341146e56373476b8eeb569` |
| Control tree / sole parent | `287ebfc7b0bf95428a07cfe1b89ba1608aef3ff7` / `9e14e033f9ee31522b571c127609dcdff76d230b` |
| Frozen source | `513341f41ce53833a279571401c924bdddddb6c8` |
| Source tree / sole parent | `a818efb2157d57af0c9c604f6d0ca85873b8712c` / `97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a` |
| Stock tool | `0aac16ef62da9e9d5645782d458593e5d78143ba` |
| Tool tree / sole parent | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` / `3e095c22a231de1d7acd2410b71f0fc8e6970c19` |
| Request SHA256 | `efbc150280f5f9641c9e8b48fb4486122ae8c3cfa318f78a42486394e1de7656` |
| Workflow SHA256 | `8d5fd03476d3d7666692cc7267d3fe598a0007c54ec6576de3538cef434ac709` |

## Producer boundary and strict evidence handling

`s3_campaign.run_campaign` resolves the tool input once at campaign entry,
before E0. That Path supplies E0, every controller pre/post capture and the
invoker. `invoke` serializes that exact path into worker argv rather than
independently resolving the original relative input. The workflow still supplies
`--tool tool --std export`. The repaired producer therefore writes the same
absolute tool paths on both sides of the exact dictionary comparison.

The independent intake binds the defect to relative controller versus absolute
worker kani_driver/kani_compiler path strings with equal recorded hashes. This
review does not establish historical physical identity, installation/rebuild
causality, inode/device/stat/readlink/mtime, or absence of unobserved changes.
Those remain UNKNOWN. Canonicalization concerns future writer inputs only.

The four changed paths are CI-REQUEST.json, s3_campaign.py, s3_validate.py and
new test_s3_paths.py. The request changes only payload hashes/test inventory and
the path precursor reference; s3_validate adds the test module without removing
legacy tests. Every other frozen control byte, including runner.py,
s3_evidence.py, s3_snapshots.py, source policy, process lifecycle, legacy writers,
readers and policies, is unchanged. Whole binaries dictionaries still compare
paths and digests. Required keys/hash syntax, malformed/unreadable/missing
snapshots, recorded errors, state guards and verified shutdown remain enforced.
No basename/hash-only allowlist, guard bypass, rebaseline, retrospective artifact
normalization or error suppression was added.

Leaving std entry representation unchanged is justified: verify_source returns
pinned source/tool identities and changed-file hashes, without its directory
argument. invoke already resolves std for worker argv. The real-file fixture
exercises relative export through actual source validation and the existing worker
resolution. No common legacy behavior needs changing for this defect.

## Independent execution

23 targeted tests PASS in 75.238600s: the ten new author path tests, ten inherited
repair tests and three independent tests. Exact argv, timestamps, exits and
transcript hashes are in tests/candidate-execution.json. These are static and
synthetic service checks; dummy Kani/CBMC files are hashed and never executed.
Source checking, filesystem hashing, snapshots, worker argv, worker receipt
writers, compilation provenance writers, protected readers and portable collection
are exercised; fixture Git identities, telemetry and native execution are mocked.

The actual workflow relative input passes the repaired real-writer path and
local/upload-only replay. Absolute, dot/parent and directory symlink inputs pass.
The same workflow test, with the exact frozen fc29 import closure reconstructed
from Git and only the identical new test file added, exits1 with the expected
`recorded worker binary drift: before`. tests/frozen-closure.json binds every
frozen file. The failure is a distinguishing control, not a candidate failure or
transformed historical admission.

Independent tests retarget the input directory alias immediately after E0.
All19 E0/pre/post calls and worker commands retain the original canonical
directory; the campaign and portable replay pass. A separate matrix makes48
same-SHA path changes across both stages, all three binaries and all four valid
worker states: every mutation rejects as recorded drift. Twelve additional
required-shape/error/state mutations reject. Original on-disk worker bytes remain
untouched. A missing binary at entry yields baseline_snapshot_incomplete, zero
worker launches and all rows NOT_RUN.

The executed author controls additionally cover a different directory containing
equal bytes, real file mutation, missing files, EACCES at file open, recorded
drift across COMPLETE/FAILED/IN_PROGRESS/INTERRUPTED/null/UNKNOWN, malformed/error
records, original reasons/exits, two-root prefix/global stop and portable replay.
Request-derived source/compile provenance repair controls remain passing.

The actual forked Python worker stops at the mocked native boundary after real
BEFORE publication, is SIGKILLed and reaped. Its untouched receipt genuinely
lacks AFTER/source_after/binary_identity. Recovery accepts only the verified
interruption and rejects success/unverified shutdown. A separate synthetic
campaign-interruption check preserves original exit-15/signal15/exception and
UNKNOWN qualification. These two assurance levels remain distinct; neither
qualifies a native campaign. No present error is erased to enable recovery.

## Input closure, source scope and final Validate

INPUT-AUDIT.json verifies all65 committed package files/all64 manifest hashes,
all18 dependency commit/blob/length/hash/copy bindings, exact control/source/tool
HEAD/tree/sole-parent/clean identities, request/workflow/source/dependency hashes,
four patch replays to the exact control/source trees and ancestry7/5/2. Package0902
(34 files), review27040 (70 files), and intake1d8a (28 files) remain exact. Inputs
are copied with their original directory structure under inputs/package/.

The six source/domain/role/U maps match0902 byte-for-byte; the unchanged request
fields and source513/tool0aac bind inherited source semantic review and the prior
R14-01/R14-02 closures from27040. This is no new broad semantic proof. Nine roots,
full-byte u8/KeyLess bodies/domains/frame/init premises, unwind bounds,71 literal
sites,44 covers, deferred8, disabled U proposal/reject-ALL-U and inherited general
proof gaps remain unchanged. The existing static source preflight independently
passes in19.723640s (tests/source-preflight.json); no compiler is involved.

Workflow bytes and resource caps remain exact: checkout7/5/2; child600 including
compile180; slot720; local6GiB sampled PGID with its existing qualification;
outer12GiB plus2GiB headroom; campaign6900; setup1800; job180min; Validate18min.

The exact author final Validate record, script, stdout/stderr, all3887 tracked
file hashes and final request/workflow/tree agree:136 legacy +56 S3 =192 PASS,
recorded execution_count1, elapsed534.581739554s;1080/elapsed=2.0202710270295445,
above1.5. Monotonic arithmetic and transcript summaries match. This is audited
author local static/synthetic evidence, not an independently witnessed execution
or native/CI fit. Full Validate was not rerun; no concern justified doing so.
Author precursor failures remain preserved and are not counted as final evidence.

## Historical limits and disposition

Frozenfc29/package0902/review27040/GO9929/triggerd925 and intake1d8a remain
immutable. The authentic campaign remains STOPPED/prefix0/first row
INTERRUPTED-UNKNOWN/later8 NOT_RUN/deferred8 NOT_SELECTED. The source-reported
native FAILURE supports the literal S2_NEG_CHECKER_ORDER observation only;
driver exit1, worker exit0 and eight UNREACHABLE checks remain recorded.
No negative admission, U waiver, proof credit or historical rewrite follows.
Physical identity remains UNKNOWN. Coordinator charge0 is the existing case
decision;31/31+11/17=42/48 is unchanged. No accounting action occurred.

**APPROVE, zero blockers within this delta.** Next: root may decide a new GO for
these exact identities. The user coordinator separately owns prospective12/17
dispatch/accounting after root consent. This review issues no GO and performs
no launch. Native compile/proof/fit, full native runner and CI remain NOT_RUN;
qualification0, proof obligations closed0, independent B1/B2 credit NONE.

High/FastOFF and no-subagent instructions were preserved without model/settings
changes. No candidate/source edits, compiler/Cargo/rustc/rustfmt/Kani/CBMC,
expansion/verifier, push, PR/issues/comments, raw evidence/GCS, ledger, budget or
reservation action occurred. Only the new review directory is committed with
`[skip ci]`.
