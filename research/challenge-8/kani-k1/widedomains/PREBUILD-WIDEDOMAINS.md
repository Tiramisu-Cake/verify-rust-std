# WIDEDOMAINS G1 — exact pre-build packet

PRE_BUILD_REVIEW_PENDING. No build submitted; coordinator GO is required for this exact packet.
Worktree `/root/verify-rust-std-kani-widedomains`, branch `experiment/kani-k1-widedomains-20261105`.
Task `34f69f034b`, library base `4fa6151b6a`; tooling base `59893bff1f` is unchanged.
Library commit `35667f4a956e8f24919275b745455a751df57edc` (two files, 163 added lines).
Stable owner `k1-merge`; request `widedomains-g1-20261105-01`, stage/ledger `widedomains-g1`.
Request SHA256 `cb5d05e2df44e9ff7969f319cc1f462a8a50ace3e3144b1944f68fc8ccb7a315`.
Kani pin `cd355b0bccd32300713bc2ce4f765dafa1510607`, nightly `2026-10-22` (inherited).

## Proposed run

Diagnostic, controls=true, inventory=false, jobs=1, gcb-e2-standard-4.
Full std inventory is omitted: the inherited runner notes about 49 minutes for that setup;
G1 needs compilation and proof of ten opt-in roots, with static ordinary/cfg-on inventories.
Three minutes per root (180 seconds, below the 200-second ordinary-candidate threshold).
Ten roots, 30 harness-minutes + 30 overhead = 60-minute build timeout, reservation **$0.8100**.
Own cap $4.00, project cap $118.96, G1–G3 only, no retries, one compile-error repair per build
only within own spent + reserve cap. Main window 300 minutes + closeout 30 minutes.
Ledger records window/deadlines at first authorized dispatch, following the inherited K-1 ledger.
Budget snapshot 2026-11-05 07:39 UTC: 234 builds, $99.7350 used, $0 reserved;
including G1 at most $100.5450. Recheck budget and owner slot immediately before dispatch.

All names below have prefix `slice::sort::shared::smallsort::verify::widedomains::`.
All ten request entries expect SUCCESS. Each successful root must also reach every listed cover.
TIMEOUT is an observed limit, never proof or cover acceptance; the runner gate alone is insufficient.

| Root | Role / domain | Expected covers |
| --- | --- | ---: |
| swap_safety_u8_backing32 | swap PFC, u8, arbitrary interior base and relative positions | 9 |
| swap_safety_u64_backing32 | same, u64 | 9 |
| unstable_network_safety_u8_n32_stubbed | real unstable dispatch N32, verified swap stub only | 5 |
| insert_tail_safety_u64_backing32_tail1_to4 | tail PFC, backing32, relative tail 1..4 | 8 |
| insert_tail_safety_u64_backing32_tail5_to8 | tail PFC, backing32, relative tail 5..8 | 8 |
| insert_tail_safety_u64_backing32_tail9_to12 | tail PFC, backing32, relative tail 9..12 | 8 |
| insert_tail_safety_u64_backing32_tail13_to16 | tail PFC, backing32, relative tail 13..16 | 8 |
| insert_tail_safety_u64_backing32_tail17_to19 | tail PFC, backing32, relative tail 17..19 | 8 |
| insert_tail_safety_u64_backing48_tail1_to4 | tail PFC, scratch backing48, relative tail 1..4 | 8 |
| insert_tail_safety_u64_backing48_tail5_to8 | tail PFC, scratch backing48, relative tail 5..8 | 8 |

Total expected covers **79/79**, zero unreachable. Covers include both comparator answers;
swap equal/increasing/decreasing positions, allocation base/second half/last element;
each tail partition's lower and upper ends, allocation/interior base and last allocation element;
and network N32 entry, normal return and the explicit order-violation boundary.

## Call-domain inclusion argument (conditional on PFC and consumer SUCCESS)

`F_T` means exactly this module's function item `arbitrary_less::<T>`, which reads both references
with volatile reads and returns a fresh arbitrary bool. No stateful/mutating comparator is included.
PFCs and consumer use the same function item; no substitution of another comparator's proof.

| Consumer / calls | Union of matching PFC domains | Inclusion / frame |
| --- | --- | --- |
| G1 actual unstable u8 N32 route; two real sort13 sites, base offsets 0 and 16, relative a,b in 0..12 | u8 swap backing32: arbitrary s<32 and a,b<32-s, F_u8, equal positions included | s=0/16 and a,b<=12 fit; one initialized writable [u8;32] allocation; only absolute s+a/s+b may change; explicit frame checks all other elements |
| G1 insertion/merge inside that network route | No verified insert_tail/insertion/merge stubs used | Real bodies run; no composition claim from the u64 tail PFCs. Only the explicit order-violation panic is cut with assume(false); normal-return safety, no unwinding |
| Future u64 insertion consumer on slices of backing32, len<=16 then <=20, arbitrary 1<=offset<=len | Five backing32 tail PFCs: union tail=1..19, arbitrary start<32-tail, F_u64 | For a slice at s with s+len<=32, each call has tail in offset..len-1, so s+tail<32. Whole backing initialized is one allowed outside mask. Consumer not yet implemented/proven; no current credit |
| Future u64 small_sort_general scratch48 insert_tail sites, N<=32 | G1 scratch48 union tail=1..8 only, arbitrary start<48-tail, F_u64 | Partial coverage only: actual half starts 0/floor(N/2), tails presorted_len..half_len-1 (up to 15). Tails 9..15 still need matching scratch48 PFCs before any stubbed consumer credit |

Tail fixtures use `[MaybeUninit<u64>; B]` with B exactly 32 or 48. The inclusive begin..tail
region is initialized with arbitrary values; an independent arbitrary bool for each outside slot
selects initialized arbitrary contents or uninitialized storage. Thus arbitrary extra initialized
scratch slots and fully initialized insertion allocations are included. Frame assertions read only
initialized outside slots; the contract modifies check constrains the inclusive target region.
No equality is asserted by reading an uninitialized slot. This fixture does not enable Kani's
uninitialized-memory/value-validity instrumentation or add a permission-checking theorem.
The backing32 swap PFC does not imply swap on another allocation size or scratch48.
The u64 swap PFC has no G1 stubbed consumer. Existing helpers' PFCs use other F items and are
not silently reused. Actual root domains are bounded T/F/allocation fixtures, not universal proofs.

## Validation and next actions

Source-only `check_packet.py`: ordinary 219 unchanged; cfg-on 253 -> 263; ten new gated roots;
old verify files and runtime/contracts byte-identical; only the new module and its registration
change in library; no static orphan items/imports/macro arms; tooling matches `59893bff1f`.
Rustfmt checks the two touched Rust files with the inherited codefix config; diff check is required.
Proof/times/covers/warnings are pending GCB, not established by source parsing.
No compiler inventory is requested or claimed; expected-name files are source-only.
Library and research changes are separate `[skip ci]` commits; push without force.

After exact-packet GO: verify published SHA/slot/budget, record window/deadlines and dispatch once
with `research/challenge-8/kani-k1/tools/k1g.sh dispatch experiment/kani-k1-widedomains-20261105`.
Use K1_CACHE=/tmp/widedomains-k1g-g1 for our run, record its UUID, run `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`,
then end the turn. No status polling. After wakeup use only bounded summary/rows/peaks/
log-grep and check-tooling against `59893bff1f`; require all expected covers for successful roots.
Record identity, request binding, row times/checks/covers and cost; update RESULT <=45 lines.
G2/G3 depend on G1 analysis and a new coordinator GO. If N32 times out, record that limit and
use later GO to measure a smaller real network route with matching allocation PFC coverage.
Next proof steps: finish scratch tail partitions as needed; insertion <=16 then <=20 with verified
insert_tail; merge 8 -> 16 -> 32 with exact real-call geometry. No future proof is claimed here.
No local cargo/rustc/Kani/CBMC, credentials, competing PR code, runtime or tooling changes.
