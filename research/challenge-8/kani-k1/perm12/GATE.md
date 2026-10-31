# Gate frozen before G1

G1: measurement, jobs1, controls=true, uninit-checks off, timeout exactly10min, seven exact entries
in manifest/g1.request.json. Preserve all safety/unwinding/count assertions and movement/end covers.
Original/unpartitioned expectations are SUCCESS as schema requires; TIMEOUT is censored, unaccepted
baseline proof. Aggregate gate=false does not erase individually verified rows.

PASS requires all four cases SUCCESS, every required assertion accepted, all per-case covers
satisfied, and the negative control accepted at the sole full-value-count assertion with its
covers satisfied and no other failures. Source correspondence must be accepted at review.
Require COMPLETE, consistent row identities, actual request/source/tree/toolchain/flags binding.
Sum four case verification times <=600s. If either comparable baseline succeeds, the sum must
also be strictly below the better successful original/unpartitioned verification time.
If neither succeeds, numerical speedup=NA and <=600s is only the preselected cost ceiling.
Report sum case harness wall times, maximum case VT/wall and per-harness RSS separately.
If a required metric is missing or incomparable, gate UNKNOWN; make no savings claim.
Incomplete cases or excessive cost imply STOP; no automatic 8/16 split or domain/unwind changes.
If all proofs pass but the sum is too costly, proof COMPLETE and optimization STOP are distinct.

G1 envelope=(7*10+30)min=100min, reserve USD1.350 at USD0.0135/min.
G2 envelope=(4*10+30)min=70min, reserve USD0.945, diagnostic jobs3, same frozen library tree.
G2 only after G1 gate PASS, fresh GO applicability/global budget/own-ledger checks, <=2 builds
including retries/failed/cancelled, own spent+reserved+0.945<=USD2, and the entire envelope plus
30min closing reserve within session deadline. The two full envelopes cost USD2.295>USD2:
G2 is conditional and NOT_RUN if unaffordable; jobs1 verdict is preserved, jobs3 admission OPEN.
Record missing/exit/OOM per case and real active CBMC/driver process peaks; total peak alone
proves neither each process's peak nor the existence of three simultaneous CBMC processes.

Before every dispatch: k1g.sh budget, own selected UUID/request_id ledger, time and reserves.
Requests have separate commit SHAs/UUIDs; G2 install changes request/research only, never library.
Retry may replace G2 only in the second slot after published delta-review/GO, within same caps.
After dispatch: k1g.sh watch UUID, finish turn, wait for normal wakeup; no model polling.
After terminal: bounded status/summary/peaks, check-tooling UUID FULL_CAP_SHA and targeted
log-grep/log-lines as needed; reconcile actual identities/flags/locations before accepting rows.
No raw/full logs, direct GCS or Cloud Logging; no replacement by older evidence.
