# Read-only validation

334 checks PASS in VALIDATION.json. The replay loads only exact committed collector/oracle dependencies, validates request/payload/source/tree/parent identities, compact/member/native metadata hashes, fresh namespace and binary snapshots, all expected source tags and oracle coordinates, start/termination/completeness boundaries, and exact native progress metrics. The exact collector returns 11 UNKNOWN outcomes.

Run offline with python3 replay.py in this directory. It reads the retained compact member, connected metadata snapshots and pinned local Git objects, and writes only this directory. It does not call runner.main/run/execute, a compiler, verifier, CI or service tests. No runner implementation changed, so no new service regression suite was invoked. Replay-control files are exact immutable code copies with hashes bound by request, not a new runnable candidate.

Transport SHA/byte equality was checked before ZIP parsing by acquire.py. Replay verifies the retained member and its embedded bytes against that acquisition attestation; it cannot re-prove transport digest without reacquisition and does not pretend otherwise. No transport ZIP was saved. Packing integrity does not establish native/producer/proof completeness. Full property oracles are deliberately not satisfied from partial progress.

Source tracing is limited to stock entry/export/scheduler/codegen grouping, exact monitor/kill path, and source-oracle coordinates. No compiler/model audit, proof acceptance, new source-stage run, historical receipt modification, ledger mutation or settings change.
