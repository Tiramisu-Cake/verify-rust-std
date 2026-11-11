# A3 tooling delta
Defect: rejected sidecars lost their footer before summary coverage aggregation; old A2 data cannot be recovered.
Only diagnostic_trace.py and its isolated tests change. Kani, runner/verdict parser, upload recipe and native readers are unchanged.
Each fully read bounded sidecar gets a footer observation before JSONL/schema/counter validation.
Observation binds file + complete sidecar SHA256 + last-line SHA256; source counters are explicitly UNVALIDATED, never accepted coverage.
Allowlist: state, seen_records, emitted_records, omitted_records, optional omitted_bytes, bytes_before_footer, coverage, omission_counts.
Wrong-type fields become null with malformed_fields; unknown payload keys are discarded; missing/malformed/oversized footer is UNAVAILABLE.
Footer line <=2048 B; existing sidecar <=256 KiB/run <=1 MiB/enumeration <=128 bounds remain; no raw sidecar is archived.
Footer is embedded in summary.json, which the existing recipe copies into upload/summary even when diagnostic trace is INVALID.
Read `k1g.sh trace-field BUILD validation.footers 0 20` and `validation.errors`; continue only by returned next_start.
INVALID payload records remain withheld, with all existing identity/envelope and <=20 items/12000 B guards.
No native-field changes: that command continues to read native test records, not top-level diagnostic_trace.
Tests include real synthetic verify/summarize stages (stub compiler), original success/failure exits and persisted rejected footer.
Early invalid JSON/null row/oversized row/source-stage/context/deep JSON failures retain footer; missing/type/cap paths explicit.
Review P2: parser RecursionError now becomes INVALID; portable decoder fault injection + persisted deep-row service rejection tested.
Current Python3.12 C decoder accepts this nested row before rejecting its type; actual bounded RecursionError trigger is not established.
Reader CLI tests cover cached summaries only, footer paging/bounds, source/stage/applied-tree/env/counter mismatches and INVALID denial.
No local Rust compiler/Kani/CBMC or Cloud operation is used. Historical summaries/ledgers and active requests remain unchanged.
