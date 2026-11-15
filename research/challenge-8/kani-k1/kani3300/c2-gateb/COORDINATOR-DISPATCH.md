# C2 Gate B′ replay — coordinator dispatch

2026-11-15. Worker15 READY `0d6282ad1a0004721447438f9b6e87fc90dd9971` / g0 `0882994411`.

Coordinator review before dispatch (against C1 overlay `0c1cc8a7d05184044d496b01f5ed41cebfde0cac`):
- overlay commit adds only `.github/workflows/kani3300-replay.yml` and `scripts/kani3300-replay/*` on top of `ad499e41dd`; no Kani source change;
- `gateb-prime-test-only.patch` SHA-256 `af2d6e7b…` equals the std diff `70ba5befc6..933b20a237` byte for byte;
- CI-REQUEST row argv unchanged except the binary placeholder C1→C2; replay.py changes are the C1→C2 identity rebinding;
- runner/caps fixed to ubuntu-24.04, 3 serial jobs, 180 min total (planner decision).

Dispatch commit `6376c3cb3f5a8c6e6e26fd36678f8517d7898a4e` = `0d6282ad1` minus the other 16 workflows (as for C1, only the replay
workflow on the dispatch branch), pushed to fork `ci/kani3300-c2-gateb-w15` → run **43683557088**.
