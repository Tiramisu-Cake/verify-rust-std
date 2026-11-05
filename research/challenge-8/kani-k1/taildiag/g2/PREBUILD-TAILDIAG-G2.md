# TAILDIAG G2 — matched insertion composition after successful G1 tail domains

Stable owner `k1-network`, branch `experiment/kani-k1-taildiag-20261105`.
G1 build `34500433-bd3d-4784-9a26-aaf0ba3f0492`, source
`1c99acce330d708961571bd593ecc322768f690f`: nine SUCCESS <=200 s, one TIMEOUT.
Exact bounded evidence and identity/peak validation: [G1 report](../g1/verification-report.json),
[RESULT](../../RESULT-TAILDIAG.md). The Cloud failure is the deterministic tail1..7 timeout;
there is no compile error. 45/45 covers reached for SUCCESS rows; total goal50 is unestablished.
Tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`, Kani pin
`cd355b0bccd32300713bc2ce4f765dafa1510607` unchanged; check-tooling G1 PASS.

Library-only G2 commit `eec8eb6bf0fe17e2e7206fbb651cbcf86ffd5942` adds five opt-in roots.
Every G1 root/helper is token-identical, including the comparator and all its reads/covers.
All other verify sources and the real runtime are unchanged. No local compiler or proof tools ran.
G1 source checks remain runnable against its approved historical commit/request; G2 has a
separate current-tree source checker. Saved expected-name files are source-only inventories.

## Why this combination

At fixed u64/backing17/start0/tail1..7, removing the redundant explicit suffix frame changes
182.69366 -> 31.25227 s (~5.85x), retaining the actual modifies contract. This is the largest
measured factor. The u8 change also helps (38.121933 s) but changes T; it is not needed to reach
our u64 target. Backing8/12 improve time but cannot contain tail15. Kissat with a frame needs
142.5729 s, slower than the measured no-frame/default combination; no unmeasured combination
is assumed faster. Deterministic lower-tail times out. Keep arbitrary answers and default solver.
No repeat sampling was done: hardware/order noise is not excluded, and backing32 is untested.

## Exact five rows

Prefix `slice::sort::shared::smallsort::verify::taildiag::`; unwind32, default solver, all SUCCESS.
The first row is a real `insert_tail` PFC; the other four are `insertion_sort_shift_left` PFCs
executing its real body with `stub_verified(insert_tail)`. No explicit post-call frame is added;
real callee/caller modifies contracts stay enabled. No sortedness assumptions or loop contracts.

| Root | Array / start | Domain | Covers |
| --- | --- | --- | --- |
| u64_backing17_tail8_to15_no_explicit_frame | initialized u64[17] / 0 | tail8..15 | 5 |
| insertion_stubbed_u64_backing17_len1_to4 | initialized u64[17] / 0 | slice len1..4, offset1..len | 5 |
| insertion_stubbed_u64_backing17_len5_to8 | initialized u64[17] / 0 | slice len5..8, offset1..len | 5 |
| insertion_stubbed_u64_backing17_len9_to12 | initialized u64[17] / 0 | slice len9..12, offset1..len | 5 |
| insertion_stubbed_u64_backing17_len13_to16 | initialized u64[17] / 0 | slice len13..16, offset1..len | 5 |

Matched F is the exact function-item `taildiag::arbitrary_less::<u64>` in PFC and consumer;
it makes volatile reads and fresh arbitrary decisions. Arrays have arbitrary values and
exactly 17 initialized elements. Consumer slices are prefixes of that allocation, not new
allocations of length len. Every tail call begins at backing[0], with tail offset1..15.
G1 successful PFC union already covers this entire domain: no-frame tail1..7 at31.25227 s
and explicit-frame tail8..15 at177.43237 s. Both instantiate the same real contract and F.
Thus consumer composition can use G1 even if the G2 upper-tail performance experiment times out.
All four consumers must individually succeed for len1..16 credit; no credit before their runs.
This tests bounded safety/modifies composition, not functional sortedness or permutation.

The verified tail stub cuts the callback. Consumer-only `stub(comparison_covers,
omit_comparison_covers)` omits its unreachable coverage hook, preserving F and its semantic
reads/answers. This follows the existing realcontracts consumer pattern; no manual functional
stub is introduced. Each consumer retains reachable lowest/highest len, offset1, offset=len
and return covers. Tail PFC retains true/false comparator, lowest/highest tail and return covers.
Require each exact row's five covers reachable (25/25 total), zero unreachable covers;
unreachable checks of other kinds must not be mistaken for covers.

## Packet validation and limits

`python3 -B research/challenge-8/kani-k1/taildiag/verify_g1.py`: PASS, bounded evidence only.
`python3 -B research/challenge-8/kani-k1/taildiag/check_taildiag_g2.py`: PASS, source only.
Ordinary219 unchanged; cfg-on263 ->268, all previous roots and helpers unchanged.
Rustfmt --check with existing 2024 wrapper/config, <=100 columns, git diff --check: PASS.
Existing request validator accepted five exact SUCCESS rows. Inventory=false, controls=true,
jobs1, standard4, 4 min/root. Full std inventory remains disabled per coordinator correction.
Request `taildiag-g2-20261105-01`, SHA256
`c7652b3bf9c2b8abc8896b894c80c228b619a3087917d55131cdcf19d261fdf7`.
20 harness-minutes +30 overhead =50-minute build timeout, maximum reserve **$0.6750**.
G1 spent **$0.4185**, own spent+G2 reserve **$1.0935 / $2.00**. No retry; one compile-error
repair only within own remaining cap and original task window. This is the last primary build.
Project snapshot242 builds: used **$102.6105**, others reserved **$2.0925**, with proposed G2
**$105.3780 / $118.96**. Recheck immediately before dispatch, including stable owner slot.
Existing main deadline **2026-11-05T15:41:38.904141+00:00**, closeout **16:11:38.904141+00:00**.

## Required GO and closeout

This packet does not authorize dispatch. Stop at PRE-BUILD REVIEW; after exact coordinator GO,
dispatch once, record identity and `k1g.sh watch BUILD`, then end the turn. After notification,
use only bounded K-1 summary/rows/peaks/log-grep, status, check-tooling and budget; no inventory,
raw logs/archives or credentials. Bind build/source/request/pool/Kani identities, five exact
rows, checks, covers, times and directly attributed RSS. Record timeout time as unknown.
Ordinary candidates require SUCCESS <=200 s, all their covers, and matching composition domains.
Update RESULT-TAILDIAG.md <=40 lines; separate research [skip ci] commit, push without force,
then REVIEW REQUEST <sha> / TAILDIAG ЗАВЕРШЁН. No third primary build or silent rerun.
