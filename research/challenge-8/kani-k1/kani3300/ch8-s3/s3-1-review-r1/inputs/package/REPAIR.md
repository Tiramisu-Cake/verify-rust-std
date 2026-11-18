# R14 controller/evidence repair

Frozen package e8a8 and review610d are immutable. Source
513341f41ce53833a279571401c924bdddddb6c8 and stock tool
0aac16ef62da9e9d5645782d458593e5d78143ba are unchanged. This is a new control
sibling fc29b93b1e333b73e55e2872701c80d9927f3b02, tree
c0368fa64ab474e4f64861aedd75a8f2639b1c29, sole parent
9e14e033f9ee31522b571c127609dcdff76d230b. Seven CONTROL paths differ from1dfc;
no source, gate policy, domains, cfg, roots, role/cover map, unwind or caps changed.

R14-02/P1: shared `s3_evidence.protected` inspects recorded protected observations
before state-specific result handling. Present source-after/before errors,
snapshot error arrays (including malformed/null), wrong request/source identity,
unreadable/incomplete/mismatched binary captures and UNKNOWN binary identity
reject in COMPLETE, FAILED, IN_PROGRESS or INTERRUPTED; unknown/malformed states
also reject. A later matching controller post cannot erase any such observation.

Absence is separate: an actual interrupted worker with negative worker exit or
identified slot cutoff and verified owned-tree shutdown may lack inner AFTER.
Required pre-evidence must match, recorded error fields must be absent, and the
separate durable controller pre/post/E0 pair must validate. Present-but-malformed
AFTER, contradictory MATCH without inner binary AFTER or explicit UNKNOWN never
becomes absence. This keeps the existing valid interruption continuation, rather
than restoring blanket R5 missing-AFTER rejection. Unknown required evidence is a
global stop; precise owned ESRCH/lifecycle machinery remains unchanged.

Local finalization and sealed replay use this same reader. Stopped replay exposes
GLOBAL_STOPPED_PENDING_REVIEW, exact stop reason, original worker protected error
records, child exit/signal and completed prefix. Later rows remain NOT_RUN. No
error is cleared, no baseline redefined, no completed prefix rewritten. The
late-publication cutoff still changes only the row; saved supervision/lifecycle/
seal facts remain identical.

R14-01/P2: S3 explicitly passes request std_sha/std_tree/tool_sha/tool_tree into
CompileMonitor. Legacy defaults remain bd62/0aac without new tree fields.
`source_under_test_record` writes the same four S3 identities, current pre-overlay
base_std_sha=513341 and a separate historical_patch_base_std_sha=99e845. It retains
variant/file/patch binding. Binding metadata copies this actual record.

Shared `s3_evidence.provenance` checks all four group/compile/source-under-test
identities, the two differently named base identities, selectors, request digest,
compile limit/state and source file/variant/patch fields against the actual
request. It runs before local sealing and during portable replay. Missing/null/
wrong-type/stale/mismatched source or tool identity cannot pass by agreeing with
another stale copy. Existing metadata/native/rich/stock/source/target/role gates
remain active; compiler-instance and property-origin gaps stay UNKNOWN.

Frozen reviewer regressions were rerun only on frozen1dfc:3 PASS reproduced the
bugs, not acceptance. Fixed targeted22 PASS /41.840s and final focused10 PASS /
30.811s cover actual writers, malformed source/tool identity matrices, corrupted
actual compile/source-under-test writers,18 state/error combinations with intact
outer snapshots, valid interrupted absence, and complete real-writer-shaped
synthetic stock/rich/native-metadata plus local/upload-only replay. Portable
identity mutations deliberately recompute metadata digests and seals, so failure
is the provenance guard, not merely hash drift. Original stop evidence is asserted
in both replays. Precommit scopes and exact final validation are distinct.

Native compilation, Kani/CBMC, proof outcome/fit, full native runner and CI remain
NOT_RUN. Registration/source/Python observations grant zero proof credit. The
nine full-byte roots, all71 literal role/cover source sites,44 covers, strict
reject-ALL-U policy/disabled U proposal and all old verdicts remain unchanged.
