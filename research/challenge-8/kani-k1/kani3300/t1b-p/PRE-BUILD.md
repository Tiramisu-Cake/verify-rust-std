# KANI3300 T1b-P — PRE-BUILD
Task86cb3c464f341a02783c5960fef985964f65ceb2; Runtime Codex; exactly one preparation stage; Cloud $0.
Kani prototype 94467a24484f1d57315ebbcde7f024dd27576a00 is a separate commit directly over diagnostic 12b4137c42f3ee92f12476ea0771ea41a5cd1e8d; no Kani push.
Fresh root transformer uses identical queries/tcx/unit; ordering uses a separate discarded transformer; local/global passes and auxiliary maps inspected.
Library 919cc3e2dc5fb19ea6e7f7be761914b949160a41, flags, filters, ordering algorithm and diagnostics unchanged; no seed/CheckRef suppression/ordinary or constant transfer repair.
Combined patch is C2 plus exact prototype delta,15 deployment paths, historical tests excluded; pin f046b70644e113be0df9c22c2e6ea44a65a57566.
Deployment tree b8575e61d76709951f461b3eda70726be43d3636; patch 158274B<=4MiB; diffstat 1022B<=4096; disposable-index apply/reverse checks only.
Exactly cmp3_into_iter_next, cmp3_index_range_len, cmp3_manually_drop_unsized_len; one invocation,1m each/jobs1; original SUCCESS expectations and controls/uninit checks retained.
Acceptance: observed next→manual→index, next retains its CheckRefs, no foreign consumed body, index/manual/next SUCCESS, compare actual consumed len and caller/local MIR hashes (ACCEPTANCE.md).
Unchanged unit-scoped diagnostic last_writer can be stale when a fresh body is not rewritten; mismatched hash is not transfer evidence; unresolved strict last_writer criterion remains UNKNOWN.
Proposed stage kani3300-t1b-pilot, separate draft ledger; (3+30)×$0.0135=$0.4455, proposed new cap$0.50, margin$0.0545, historical carry$0.
No owner budget granted by this preparation; no phase/reserve registration, active request install, dispatch or Cloud access; active inputs/runner/recipe frozen.
Static validation: rustfmt with --config-path rustfmt.toml, diff --check, signatures and -D warnings source audit; check_packet.py must PASS on exact candidate.
Independent Luna HIGH review PASS for exact Kani delta and research candidate dc8e28c4cdbc92ec79b2cbaf46314c105b642781; REVIEW.md/REVIEW-IDENTITIES.json.
Compilation is NOT_RUN locally and must be checked by coordinator in fork CI; no Actions/PR/issue/comment initiated.
No new compiler/verifier/runtime evidence; B1/B2/proof credit NONE; calibration/native regressions remain outside this stage.
Stop after research commit[skip ci]/push without force; future dispatch requires new owner authorization and live ledger/slot/deadline checks.
