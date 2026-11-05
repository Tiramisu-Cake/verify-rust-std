# LOOPPIN exact packet for coordinator review

Task: `TASK-LOOPPIN.md` at `708b3a6661f40e000fe773c408ae4ef1619e292e`.
Worktree `/root/verify-rust-std-kani-looppin`, branch `experiment/kani-k1-looppin-20261105`.
Base `4fa6151b6a`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`.
Tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; lane files equal that base.
Owner `k1-network`; request/stage `looppin-g1-20261105-01` / `looppin-g1`.
Library commit `532eddb301c43d36b8b777414b59cbc09e86ed37` (`[skip ci]`).
No build submitted. Exact pushed packet requires coordinator review/GO before dispatch.

## Source and roots

The library change adds only `verify/looppin.rs` and one cfg-gated registration line in
`verify.rs`. Existing module bytes, runtime `smallsort.rs`, workflows and tooling are unchanged.
All four roots are opt-in, outside the ordinary suite.

| Root under `verify::looppin::` | Expected | Domain and purpose |
| --- | --- | --- |
| `calibration_true` | SUCCESS | `[u64; 2]`, any len 0..2; array-writing while, index <= len invariant |
| `calibration_false_control` | FAILED, invariant step | Same setup/modifies/body; extra index == 0 conjunct broken by a nonempty step |
| `insert_tail_u64_tail1_to4_backing5` | SUCCESS | Real helper contract PFC, any u64 backing5, any tail 1..4 |
| `outer_loop_u64_symbolic_len_backing5` | SUCCESS | Copy of the outer pointer loop, any len 1..5 and offset 1..len, verified insert_tail stub |

The fourth root is the PFC paired with the optional copied-loop consumer. Both use the exact
same stateless reading comparator function item `reading_less_u64`, u64 and backing5. The
consumer's possible inclusive prefix ends at backing offsets 1..4, covered by the local PFC.
The pointer invariant states same allocation, v_base < tail <= v_end and u64 alignment;
the loop modifies tail and the selected slice. The copied body calls the real helper through
`stub_verified(insert_tail)`. The comparator has no callback covers that a stub would cut.
No attributes are added to real runtime loops. No arbitrary-length safety, sortedness,
permutation, generic callback frame, uninit/value-validity or termination proof is claimed.

## Expected-check binding and acceptance

`expect_check` is `Check invariant after step for loop`, confirmed in the documentation at
the exact Kani pin (lines 79/84). The same document confirms explicit array modifies syntax.
See [pinned reference](pinned-doc-reference.json) for URL, source hash and line numbers, or
[Kani documentation at the pin](https://github.com/model-checking/kani/blob/cd355b0bccd32300713bc2ce4f765dafa1510607/docs/src/reference/experimental/loop-contracts.md).
This is a pre-build expected prefix, not an observed failed check. After the build, retain the
actual description and location from bounded rows; the negative must fail its invariant step,
with no unrelated failing checks. SUCCESS alone cannot substitute for the negative control.

Calibration works only if the true root succeeds and the false root rejects that invariant.
Require all positive covers reachable: calibration 3, PFC 4, copied loop 3 (10 total), and
zero unreachable covers. Treat copied-loop SUCCESS as supported composition only if its
paired PFC also succeeds. Report unsupported operations with exact text, compile errors,
timeouts and memory outcomes separately; record row seconds and bounded per-row RSS peaks.
The runner gate checks statuses/named failure only; cover and PFC pairing checks are additional.

## Limits and budget

Diagnostic, controls=true, jobs=1, gcb-e2-standard-4, 3 minutes per root, no inventory request.
The 3-minute timeout gives a small calibration a generous window, while stopping near the old
LOOPINV's 176..263-second memory-growth observations. It is not a replication of its 10-minute
timeout. Four roots cost at most 12 + 30 = 42 pool minutes, reserving **$0.5670**.
Own cap **$1.20**: one primary build, no retries; at most one compile-error repair if actual
own spent + new reserve <= cap. Two maximum reservations would be $1.1340; a repair still
requires a corrected published packet and applicable coordinator review/GO.
Main window 150 minutes, closeout 30; ledger window start/deadlines bind at authorized dispatch.
Project snapshot from `k1g.sh budget`: 234 builds, used $99.7350, reserved $0.0000, cap $118.96.
With this maximum reservation: $100.3020. Recheck immediately before authorized dispatch.

Request SHA256: `5c3908bef8e08cfa1967cd4b8d1bea82ffd918647c6b777771721a5e3e097caa`.
`request.json` is byte-identical to the lane's `RUN-REQUEST.json`; validation accepts four roots.
`check_packet.py` checks request/scope/roots/hashes/reservation only; it does not compile or prove.
No local cargo/rustc/Kani/CBMC or credentials were read/run; no competing PR code was opened.

## Old-pin comparison and closeout procedure

Explicitly authorized prior source: LOOPINV `92ded02d106cfa1f48475ecbd6433953be04fd92`,
`RESULT-LOOPINV.md` and `verify/network/loopinv.rs`. Old Kani `9461e07a`, build
`c151dc31-7bb8-4cfb-8b63-c685c65192a5`: source-reported 3/3 TIMEOUT at 600 seconds per root,
CBMC peaks 14.81..14.99 GiB, including trivial pointer-loop copies on `[u64; 2]`.
No successful invariant check or negative-control rejection was established there.
The new calibration uses an index loop and symbolic len; the optional pointer copy uses a
verified helper stub. These are mechanism diagnostics, not an isolated performance comparison
that can attribute a difference solely to the Kani pin.

After exact-packet GO, recheck branch/SHA, slot and budgets; dispatch once via `k1g.sh`.
Record build/source/request identities and time limits, run `k1g.sh watch BUILD`, then end
the turn. No status polling loop. On wakeup, use bounded summaries/rows/peaks/log-grep and
`check-tooling BUILD 59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; retain bounded outputs only.
Write `RESULT-LOOPPIN.md` <=30 lines with identities, status/check/time/RSS table, the old-pin
comparison and next-step conclusion. Commit/push research separately with `[skip ci]`, end
with `REVIEW REQUEST <sha>` / `LOOPPIN ЗАВЕРШЁН`, and stop. No new stage or automatic retry.
