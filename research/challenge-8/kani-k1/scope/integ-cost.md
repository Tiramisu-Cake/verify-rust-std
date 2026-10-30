# INTEG scope cost note

Static arithmetic from the historical P-6 macOS harness VT table; this is not a runtime forecast.
P-6 partition source: Actions run `40748125754`, all 8 partitions. P-7 autoharness is excluded.

| Change in P1 | Names | Known P-6 macOS ΣVT, seconds |
|---|---:|---:|
| Returned to ordinary: 3 swap + 1 mutating route + 27 plain insertion | 31 | +1159.9 |
| Retired duplicate callers | 11 | −245.6 |
| New DIRECT ordinary | 12 | UNKNOWN (no P-6 macOS VT) |

DIRECT measurements from `direct/results.tsv` are GCB evidence and are reported separately below. Their elapsed seconds and RSS are not added to P-6 macOS VT.

| DIRECT class | Rows | Known historical GCB time Σ, seconds | Timeout rows | Max GCB RSS, KiB |
|---|---:|---:|---:|---:|
| expected-fail | 2 | 28.1009 | 0 | 1226520 |
| ordinary | 12 | 708.8219 | 0 | 4710364 |
| positive-direct | 10 | 2427.5576 | 0 | 9241468 |
| timeout-diagnostic | 2 | 0.0000 | 2 | 9454264 |

The expected-fail row contains historical failed-control timings, not successful proof times. The revised shared-oracle control's old GCB result used a different body; its current result awaits measurement.
No P-7 autoharness projection, division by job count, or GCB-to-Mac coefficient is applied.
