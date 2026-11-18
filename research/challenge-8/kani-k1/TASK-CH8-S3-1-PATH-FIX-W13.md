# Fresh13 — S3-1 retry path-representation repair (package r2)

ISSUED owner01:18 /new13. High/FastOFF, no subagents/model changes; STOP only
real blocker. Read immutable intake1d8a06c8bd418de6261a1cbbb24ea0f35bae1712 at
kani3300/ch8-s3/run-44405927807/HANDOFF.md, BEFORE-DIFF.md/json, SOURCE-TRACE.json,
PREFIX-REPLAY and NATIVE. Source513341f41ce53833a279571401c924bdddddb6c8 and
stocktool0aac16ef62da9e9d5645782d458593e5d78143ba MUST remain exact.
Frozen controlfc29b93b1e333b73e55e2872701c80d9927f3b02, treec0368fa64ab474e4f64861aedd75a8f2639b1c29,
package0902/review27040/GO9929/triggerd925 remain immutable; old GO spent.

Exact cause (not physical same-file proof): controller E0/pre/post record
kani_driver/kani_compiler paths tool/target/kani/bin/..., worker BEFORE/AFTER
records /home/runner/work/kani/kani/tool/target/kani/bin/.... All recorded SHA256
match at five observations, state/shape COMPLETE; fingerprints_match compares
whole binaries dictionaries, so only path differs. Realpath/readlink/stat/
inode/size/mtime and distinct setup fingerprints were not emitted: UNKNOWN.
The native first-root FAILURE at literalS2_NEG_CHECKER_ORDER is observed, but
campaign STOPPED/prefix0/firstrowINTERRUPTED-UNKNOWN/8laterNOT_RUN and8U remain;
no admitted negative/proof or historical rewrite. Charge0 is coordinator case.

Required minimal design: normalize S3 tool input to a canonical absolute path
AT CAMPAIGN ENTRY BEFORE E0 and reuse that same path for controller capture and
worker argv/capture. Normalize std argument too if needed for equivalent
representation, with explicit narrow reasoning. Keep strict fingerprint digest,
required keys/states and path comparison. Prefer fixing producer/entry boundary
rather than allowing basename/hash-only matches or retrospective artifact
normalization. Legacy writer/reader/policies stay unchanged; do not broaden
common legacy behavior without concrete dependency returned to root.
No rebaseline after drift, blanket read-error/ESRCH ignore, disabled guard,
missing evidence acceptance or claim of new physical inode/realpath assurance.
Wrong canonical path even with same bytes must still reject; real hash drift,
unreadability/malformed/missing data/globalstop behavior remains enforced.

Authentic regression: use intake observed relative-controller/absolute-worker
shape plus the actual workflow --tool tool entry and real filesystem hashing
of bounded dummy binaries in a temporary fixture. Exercise real fingerprint
serialization/controller capture/worker argument path, replacing native verifier
calls only. Do NOT use the old common fixed /tool/<name> fingerprint mock that
masked this case. Cover relative vs absolute input, cwd/parent components,
well-defined directory symlink alias if supported, preserved absolute paths,
wrong directory/path identity, hash mutation/missing/error/state tamper, genuine
interrupted absentAFTER recovery, all-state recorded drift +portable prefix.
Show frozenfc29 workflow-shaped rejection and repaired future writer equality.
The old captured artifact remains STOPPED; a counterfactual transformed copy is
NOT accepted historical evidence. Preserve original error/exit and qualification0.
No compiler/Kani/CBMC execution for these tests.

New isolated control SIBLING soleparent9e14e033f9ee31522b571c127609dcdff76d230b,
new immutable kani3300/ch8-s3/s3-1-r2/. Rebind fullcontrol/tree/parent/request/
workflow/patch/hash/maps/closure/provenance/manifest and exact fixture regression.
Source/tool, all9roots/fullbyteT=u8F=KeyLess/domains/frame/init/unwinds/71literal
sites/44cover sites/deferred8/UproposalDISABLED+rejectALLU/resourcecaps remain
unchanged. Checkout7/5/2; perchild600includescompile180/slot720/RSS6GiBsampledPGID,
outer12+2/campaign6900/setup1800/job180/Validate18min unchanged. No new features,
assumed summary/reduced-domain proof, newtool969f/#4591 fix or CI rerun here.

Targeted meaningful regressions first, freeze actual finalcontrol then final
Validate ONCE on exactbytes with truthful timing/margin>=1.5 and sourcepreflight;
no repeated full suite absent new concrete finding. If cap change needed, exact
minimal proposal to root; no budget increase. Keep failed/precursor evidence.
Native futurecompile/proof/fit NOT_RUN; all historical classifications intact.

READY fullg0/control/tree/parent/request/workflow/tests/timing ->SAME14 delta via
TASK-CH8-S3-1-PATH-DELTA-W14.md ->new root GO only. Usercoordinator separately
launches/counts prospective12/17. Current ledger01f363...31/31+11/17=42/48,
no refund/charge/reservation by you. No CI/push/PR/issues/comments/ledger or
compiler/cargo/rustc/rustfmt/Kani/CBMC/expansion/verifier/fullrunner/rawlogs/
archives/GCS/subagents/model change. Ownpaths --only [skip ci], Tiramisu-Cake
<igkharin@gmail.com>. #4591 original15 repair+11review is independent; no reset.
