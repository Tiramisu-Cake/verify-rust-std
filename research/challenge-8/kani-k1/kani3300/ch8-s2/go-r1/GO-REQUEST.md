# S2 cfg r1 — READY_FOR_OWNER_GO

Review `e40ac8e8dd8ab071879ff9ab60f4b14149af0c11`: **APPROVE**, blockers0,
nonblocking0; S2-W14-N1 resolved. Exact package
`0a4cef493f858d0e91d3ebccfbbab0b8d32d0119`, `../batch-r1/`.
Old package/source/control/review/GO and compile-only run44264952389 stay immutable.

| Pin | Exact identity |
|---|---|
| Std / tree | `9fd558c9dab5ec26abdb1226eb5f2b9cd9ffbff6` / `64d96010b0b4b896322e26d700c253f834ba9fd6` |
| Stock Kani | `0aac16ef62da9e9d5645782d458593e5d78143ba` |
| Reviewed control / tree | `2ecf5e839f898f6bb1cd96edd6cc6bf677acb4c8` / `b04ce6fd7a2c937bf72fcda7a262eef65a9f45bb` |
| Required trigger parent | `9e14e033f9ee31522b571c127609dcdff76d230b` |
| Embedded request SHA256 | `779126ddc8aa3e5cabd9b9968f0e1cd853c4e1b60a95a21ff4eb42d5a0c7ca74` |
| Workflow SHA256 | `7dca25a36813d294548ce26c27dfe38b9b06d3f4091785eaad4f00be2a437455` |

Request: one **new r1** S2 workflow attempt. Source publication: exact std above
in Tiramisu-Cake/verify-rust-std. CI trigger: same-tree sibling with the exact parent
above in Tiramisu-Cake/kani, branch matching `uninit-ci/ch8-s2-batch3probes-*`.
The source/control checkout depths are **5/7**, stock tool2. The control preflight
checks its single parent. Actual future trigger/run/branch publication is the
coordinator's action after owner GO; this package prepares no trigger or reservation.

R1 adds only13 source lines registering sort8 PFC, without selecting it for execution.
All11 effective cfg contexts/six verified-stub uses now have matching active providers;
the new source gate runs before setup/build/verification and rejects old97ac.
58 tests,14 independent cfg fixtures,4 workflow mutations and5 exact patch replays
passed in review. Registration is no proof qualification; r1 compilation is NOT_RUN.

Scope unchanged: one serial group s2-batch3probes-u34,11 roots: actual merge32 with
sorted halves, diagnostic assumed sort13/general32, swap PFC attempt, summary witness,
six negative controls;20 required SAT covers. Assumed summaries give no formal credit.
Limits:600s/root backend,900s compile,6600s root-cap sum,7500s group child,
phase8100s/job180min,1job/max-parallel1,RSS group12GiB/headroom2GiB.
Separate model/checker/driver wall and per-root aggregate RSS remain UNKNOWN when
unmeasured; sampled comm peaks do not establish the6GiB/root target or ordinary CI fit.

Current owner ledger4076fb01d5 reports item2 **10/14**; the owner decides the failed
attempt's accounting and this repeat. No refund, new charge or next number is assumed.
Item1 27/28,total37/42 remain context only. One requested attempt, no automatic rerun.
Actual r1 proof/witness/covers/negative/cost outcomes remain NOT_RUN, proof credit NONE.
The next intake must bind the new run ID and these r1 pins; old442's0roots are not
cost/proof evidence. No push/CI/reservation/ledger action was performed here.
