# KANI3300 U3 — bounded native observations

Build `14dd0792-1c06-47be-b931-94f6096a664a`, Cloud terminal FAILURE, watch wait exit 0.
Authorized exact head `2021b7cf3518fc72fee611e2a5d306e4bf5b619e`; request `kani3300-u3-native-20261111-02`.
Request SHA-256 `8cda1fa64a8b1c7dfce56c44f30fd5d84bce508e9d93cf03a426e188f9c912da`.
Patch SHA-256 `f9187933ecd69858ae03762baa8dd57f5907e456e7457db7cba73092471ae111`.
Pin `f046b70644e113be0df9c22c2e6ea44a65a57566`, applied tree `d10fbe6d3089a4d015748544963824c1053e94d4`.
Only permitted bounded summary/native, check-tooling, budget and Brief routes were used; no raw fallback.

## Summary facts

`k1g.sh summary BUILD` returned TOOL_ERROR, gate false, expectation met false; 20 native ERROR, 0 PASS.
Kani build succeeded in 264 s; compiletest build 17 s; version Kani 0.68.0 / CBMC 6.11.0.
No whole-run Kani exit/status or measured memory/time supplied. Generic summary says uninit-checks off because the
harness request has no such flags; fixtures explicitly have -Z uninit-checks. Exact native argv is not yet readable.
All 20 entries say requested native PASS did not pass; no diagnosis of the underlying Kani failures follows.
The five amended U1T negative entries additionally say required diagnostic absent from this test's own output.
Their required diagnostic begins with `Failed Checks:`. That absence is a native gate fact, not a proof of SUCCESS.

## Overlap/overwrite: requested Failed Checks

Offset 16: `maybe-uninit-review-overwrite-copy/main.rs`, ERROR, 0.917 s.
Offset 17: `maybe-uninit-review-overlap-copy/main.rs`, ERROR, 1.470 s.
Summary provides no Failed Checks lines for either. Their diagnostic column is empty.
`native BUILD 16 2` returned exit 2: `page-summary: one native record exceeds the bounded page size`.
Therefore the complete Failed Checks list for overwrite and for each overlap harness is UNAVAILABLE, not empty.
No uninit, unreachable or foreign FAILURE is established for these entries; reachability is UNKNOWN.
The coordinator waived the pre-build diagnostic-source blocker and authorized this exact build. After the build,
all actual Failed Checks still need bounded evidence; no source cause is inferred from a regular Description.

## Other diagnostic descriptions (status unestablished)

The IntoIter row contains:
`Checking memory initialization of type std::array::IntoIter<usize, 2> is not supported. Cannot determine layout for a type that contains union of type std::mem::MaybeUninit<usize> as a field.`
This identifies the listed Unsupported check, not whether it was FAILURE/UNREACHABLE or the sole failing check.
Frame row contains `Check that *outside is assignable`; no actual frame FAILURE is established yet.
No-MIR row contains `Kani does not support shadow-carrying arguments to calls without a MIR body.`
Uninit descriptions in the other rows likewise do not establish their property status or absence of additional failures.

## Reader limitation and requested data

`native BUILD 0 1`, `native BUILD 4 1`, `native BUILD 16 2` all returned exit 2:
`page-summary: one native record exceeds the bounded page size`.
`smallsort-brief BUILD` returned exit 1:
`smallsort-brief: Reader report or query route is unavailable (HTTP 404)`.
No native record or excerpt was returned by these requests. No raw archive, full logs, cached summary bypass,
Cloud Logging, gcloud builds log or direct GCS evidence was read.
Requested coordinator data: bounded errors/output_excerpt/actual Failed Checks for positive offsets 0,4,11;
all Failed Checks for overwrite offset16 and both overlap harnesses offset17, with completeness/truncation noted.
If these are insufficient, request the relevant property status/source context rather than infer the cause.
No repair candidate or retry was prepared from the missing details.

## Identity and accounting

check-tooling against `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a` PASS: pool, lane files, bound tooling hashes,
request SHA, patch specification, published patch SHA, and applied tree match the authorized head.
`k1g.sh budget BUILD` returned `1 0.1080 0.0000`: actual $0.108, reserve $0.
One 10-minute-work repair would reserve $0.540, actual+reserve $0.648 <= cap $0.90, but needs factual diagnosis and new GO.
No ledger/history/download_verified record was changed. No native acceptance, independent B1/B2 credit or upstream readiness.
