P1G PASS; build `1b59f625-fc99-41fb-8d07-d9c0e749da7b`; head `80463b613c4054e82bcb3bae1d18c525bca4dc0d`; pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; tree `10c032ab8e3c5a38a3fa639c4b0004d61b7c2ffe`; KT2 `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`; request SHA256 `ad96f7d0ada18cbbfe9345a2a7c06cdfbce0589924fd4255b9d5374fb8ffdaac`; patch SHA256 `b30758e575bb0bfabab186d615e8b28871543efb0703028aa721a8622ef28c40`.
15/15 native PASS; 3 positives --require-success, 12 negatives own diagnostic + full golden; ledger $0.1485/$0.80, reserve $0; one build/no repair. PFC limitations unchanged; no main compatibility/general proof credit. Evidence: P1G-OBSERVATIONS.json.

| Selector (uninit/…/main.rs) | Native | Wall s |
|---|---|---|
| maybe-uninit-wrap-u3-positive | PASS | 5.734 |
| maybe-uninit-review-positive | PASS | 10.098 |
| maybe-uninit-initialized | PASS | 10.349 |
| maybe-uninit-wrap-u3-padding | PASS | 0.918 |
| maybe-uninit-wrap-u3-source-read | PASS | 1.269 |
| maybe-uninit-buffer-u3-plain-negative | PASS | 1.57 |
| maybe-uninit-buffer-u3-clause-pfc-negative | PASS | 2.272 |
| maybe-uninit-buffer-u3-frame-negative | PASS | 120.548 |
| maybe-uninit-partial-copy | PASS | 2.925 |
| maybe-uninit-reset-alias | PASS | 1.469 |
| maybe-uninit-review-argument-return | PASS | 1.419 |
| maybe-uninit-review-overwrite-copy | PASS | 3.13 |
| maybe-uninit-review-overlap-copy | PASS | 6.903 |
| maybe-uninit-review-repeat-local | PASS | 3.384 |
| maybe-uninit-review-reset-zst | PASS | 4.138 |
