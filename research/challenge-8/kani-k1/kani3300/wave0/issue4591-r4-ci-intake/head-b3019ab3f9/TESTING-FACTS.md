# CI/testing facts for coordinator

Attempt 1 only; published head b3019ab3f9c83a25cd4d870e49e49121b3327bb1, push on fix/stub-contracted-function.

- Kani CI 44516395307: FAILURE. Eight of nine jobs succeeded; perf 135533377626 failed.
- Successful Kani jobs: regression on macos-15-intel, ubuntu-22.04, ubuntu-24.04, macos-15 and ubuntu-24.04-arm; documentation, benchcomp-tests and llbc-regression.
- Kani Format Check 44516395718: SUCCESS, format-check and clippy-check.
- Cargo Deny 44516395278: SUCCESS, audit.
- All standard instances: 12 terminal jobs, 11 SUCCESS, 1 FAILURE; no missing or cancelled jobs.
- Perf reason: runner communication/CPU-memory/s2n-quic is COORDINATOR_REPORTED. Independent cause UNKNOWN. No speedup/full-green claim.
- Named-harness/property results UNKNOWN; seven source declarations are five intended positives plus two expected semantic negatives.

Attempt-specific Kani result: https://github.com/Tiramisu-Cake/kani/actions/runs/44516395307/attempts/1

These are factual intake notes. Coordinator owns PR Testing text and actual link integration. Possible later retries are separate attempts and cannot replace this result. No draft, proposed PR text, rerun or publication is part of this packet.
