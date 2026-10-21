# R12 Reader coverage

Build `68d2fe9c-bb4b-494e-844d-1a779d8d9f41`; expected source
`1e33bd24e37d11cf4de4c2163be3925a6be0fbea`, submitted config
`fd11a8ee39a0238d8c9d67e6857350beb77e66bdaeee617212097a925a40b621`.
Coordinator reports terminalSUCCESS11:17:36.947706Z, all three stepsSUCCESS.
These are coordinator/source observations, not independently verified inventory.

| Query | Coverage/result |
| --- | --- |
| Default Brief, twice | CLI1; `Reader report or query route is unavailable (HTTP 404)` |
| Catalogue `upload-policy.json` | Same HTTP404; no file ID |
| Default last request11:21:24.426734Z..11:21:28.611633Z | Same exact error; no report/index/archive/request ID |
| Catalogue `manifest.json`,11:24:49.286434Z..11:24:54.469844Z | Same error, >7min after terminal |

Totals: two default Brief plus two catalogue calls (the last default row details
one of those two, not an additional query). Exact/complete/coverage flags and
file/index/archive identities were not returned. No file selector or pagination
could proceed without file IDs; no no-match was converted into absence/NOT_RUN.

Actual archive size/SHA, payload manifest, effective SDK properties, marker and
upload-only timings remain UNKNOWN through the required evidence interface.
No claim that these objects are absent; HTTP404 does not identify root cause.
No raw/full logs/archive/GCS/Cloud Logging/download fallback, no modification of
historical evidence, no download_verified. Source/config/static/local synthetic
checks do not close the Cloud publication/inventory gate or establish formal proof.

An asynchronous clarification asked for the supported indexing procedure/address;
no reply was received by final report. Required proof retry remains blocked.
