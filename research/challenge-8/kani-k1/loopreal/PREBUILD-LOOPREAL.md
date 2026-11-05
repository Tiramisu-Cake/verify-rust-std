# LOOPREAL corrected exact packet for coordinator review

Task `01cb5fc3cda3ecf2795939285154416f213fa7e2`, base `4b05b98a3c41c64afe79446da766430a284de83f`.
Worktree `/root/verify-rust-std-kani-loopreal`, branch `experiment/kani-k1-loopreal-20261105`.
Library commits `fc1ddf01251e12fa087cfa280161bcbb6a720cdb` and
`d79f9d306b3a771b87c4fd5f0104347adabb11b0` carry `[skip ci]`; research commits are separate.
Coordinator NO-GO on `ffda59d715b3a0bceac59276d18a03f8a61a6015` is addressed by the ZST
disjunct and the two additional ordinary regressions; this packet has no dispatch GO.
Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`; tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`.
Stable owner `k1-network`; request `loopreal-g1-20261105-02`, stage `loopreal-g1`.
No build submitted. Exact pushed packet requires coordinator PRE-BUILD review/GO.

## Source and invariants

`smallsort.rs` adds only four `cfg_attr(kani, crate::kani::loop_...)` attributes:
one invariant and one modifies on each real insertion loop. Bodies, signatures and existing
function contracts are byte-identical after stripping just those attributes. `verify.rs`
adds one controls-gated `loopreal` registration; all other existing library files are unchanged.

For the real inner `insert_tail` loop, the exact invariant is:

```rust
size_of::<T>() == 0
    || (crate::ub_checks::same_allocation(begin, sift)
        && crate::ub_checks::same_allocation(begin, gap_guard.dst)
        && begin.addr() <= sift.addr()
        && sift.addr() < gap_guard.dst.addr()
        && gap_guard.dst.addr() <= tail.addr()
        && gap_guard.dst.addr() - sift.addr() == size_of::<T>()
        && (sift.addr() - begin.addr()) % size_of::<T>() == 0)
```

The non-ZST branch describes the loop header: `sift` precedes the gap by one element
inside the inclusive prefix. The ZST branch short-circuits before address ordering/modulo;
see `ZST-REACHABILITY.md` for the existing reachable Stable unit route. Breaking paths
assign the gap to `sift` before exit; inductiveness is required on backedges. Modifies: `&sift`, `ptr::addr_of!(gap_guard.dst)`, the inclusive begin..tail slice described by
the existing `insert_tail_contract_len`, and the comparator object `is_less`.
A raw pointer selects the destination field alone rather than a whole-object reference.
The guard source/length and saved `tmp` are excluded from the write set.

For the real outer `insertion_sort_shift_left` while, the exact invariant is:

```rust
size_of::<T>() == 0
    || (crate::ub_checks::same_allocation(v_base, tail)
        && crate::ub_checks::same_allocation(v_base, v_end)
        && v_base.addr() < tail.addr()
        && tail.addr() <= v_end.addr()
        && (tail.addr() - v_base.addr()) % size_of::<T>() == 0)
```

The size-zero disjunct permits the original empty pointer loop for ZSTs without division by
zero; it does not claim a new ZST contract domain. Modifies: `&tail`, the selected slice,
and `is_less`. These are geometry/safety invariants, not sortedness/permutation invariants.
Ordinary value assertions can expose abstraction regressions; retain/report those failures.

## Twelve G1 rows

| Root under `verify::` | Expectation | Domain |
| --- | --- | --- |
| `loopreal::insert_tail_u64_backing8` | SUCCESS | real-body PFC, tail any in 1..8 |
| `loopreal::outer_loop_u64_backing8` | SUCCESS | real outer body, verified `insert_tail` stub |
| `loopreal::insert_tail_u64_backing32` | SUCCESS | real-body PFC, tail any in 1..32 |
| `loopreal::outer_loop_u64_backing32` | SUCCESS | real outer body, verified `insert_tail` stub |
| `loopreal::insert_tail_u64_backing128` | SUCCESS | real-body PFC, tail any in 1..128 |
| `loopreal::outer_loop_u64_backing128` | SUCCESS | real outer body, verified `insert_tail` stub |
| `loopreal::outer_loop_false_invariant_backing8` | FAILED on invariant-step | exact cfg-copy of real outer function; extra false conjunct |
| `realcontracts::insert_tail_safety_u64_tail1_to4_backing5` | SUCCESS | ordinary PFC; before 38.1495 s |
| `network::unstable_freeze_noncopy_bytes86_fallback_n2` | SUCCESS | ordinary fallback/value assertions; before 8.783918 s |
| `realcontracts::unstable_network_safety_u8_n9_stubbed` | SUCCESS | ordinary u8 network/empty outer suffix; before 8.316227 s |
| `assembly::safety_stable_unit_n16` | SUCCESS | ordinary ZST boundary; Actions v7 ubuntu 4.687 s / macOS 3.657 s (reported) |
| `assembly::safety_stable_unit_n32` | SUCCESS | ordinary ZST real inner loop; Actions v7 ubuntu 35.126 s / macOS 25.670 s (reported) |

All new PFCs and consumers use one `u64` comparator function item `reading_less_u64`, reading
both references and returning a fresh arbitrary bool. No callback covers are cut by a stub.
Each caller has arbitrary `1 <= len <= N`, arbitrary `1 <= offset <= len`, and one backing
allocation `[u64; N]`. Its `insert_tail` calls have begin at allocation offset zero and tail
in `1..len`, a subset of the paired PFC's exact `1..N` domain, with the same T/F/backing N.
The negative caller uses the backing8 PFC domain too. Credit a consumer only if its paired
PFC succeeds, the stub is the real helper, and no domain mismatch is observed.

Harness frame assertions select an arbitrary probe instead of scanning all N elements;
there are no growing harness loops. All new roots use the same unwind 16, independent of N.
The selected real loops must be contracted; SUCCESS under disabled unwinding assertions by
itself does not prove this. Inspect bounded check/diagnostic output for actual invariant
base/step/assigns evidence; record any lack of observability without inventing proof credit.

The negative is a controls-gated copy of the complete real outer signature/body/modifies,
with the name changed and `tail == v_base.wrapping_add(offset)` appended to the invariant.
That conjunct holds at entry and fails after a nonempty step. It is not a standalone index
calibration. The expected check prefix binds `loopreal::insertion_sort_shift_left_false`;
after G1 require the observed invariant-step description and source location inside this copy,
with no unrelated failed checks. The pinned Kani documentation supports `while`, `loop`,
and a break example: [reference](https://github.com/model-checking/kani/blob/cd355b0bccd32300713bc2ce4f765dafa1510607/docs/src/reference/experimental/loop-contracts.md).
Actual acceptance of attributes/breaks remains subject to compilation and G1 evidence.
If the inner loop is unsupported without a body rewrite, record its exact reason and take
the task's allowed outer-only fallback through a corrected, reviewed packet.

Static call-path review, broader ordinary families, external sort/select entry points and
historical source bindings are in `IMPACT-LOOPREAL.md` and `regression-baselines.json`.
The three original baselines have bounded K-1 rows. The two ZST times come from the
coordinator: full organizer Actions CI v7, revision `d1283ff22a`, same Kani pin `cd355b0b`.
They are verification times on ubuntu/macOS, not GCB standard4 measurements; comparison
with G1 is approximate across platform and revision. `actions-v7-timing-source.json`
records this supplied provenance. No historical K-1 rows or Actions run IDs were supplied
for ZST, and Actions was not accessed; no independent status/check/cover claim is inferred.
The u8 network N9 row reaches the annotated outer loop with offset=len, checking its
establishment/exit for another T/F; the first two regressions exercise loop-body steps.
The added ZST N16 root skips scratch insertion; N32 can enter the actual inner loop with
zero-sized values. The disjunct fixes its base invariant; assigns/safety/return covers still
require the requested G1 regression rather than a source-only pass claim. No external
stdlib regression execution or complete ordinary regression matrix is claimed. The unchanged K-1 validator accepts only
SmallSort verify root names; no tooling expansion is part of this packet.

## Acceptance, budgets and next authorized step

Require all 11 positive rows SUCCESS, the located negative invariant-step failure only, and
all 34 positive covers reachable (3 PFC + 4 caller per backing, plus 7/3/1/1/1 regressions).
Record statuses, failed/total checks, seconds and per-root CBMC peak RSS; missing sampling is
missing data, not zero. Compare PFC and consumer timings separately at N=8/32/128 and report
ratios only where both rows complete. Full backing storage still grows with N; near-flat time
would support the approach, not establish arbitrary-length proof or causality by itself.
Generic T/F, merge, other loops, sortedness/whole-value guarantees after abstraction,
uninit/value-validity and termination remain outside new proof credit.

Diagnostic, controls=true, jobs1, standard4, 4 minutes/root; 12 rows + 30 minutes lane overhead
reserve at most 78 pool minutes × $0.0135 = **$1.0530**, within the **$2.00** own cap.
The unchanged 4-minute per-root limit allows twice the old backing5 consumer's 121-second
cost. Two 12-row maximum reservations would cost $2.1060 and are not authorized by this cap.
If G1 consumed its entire maximum, $0.9470 would remain; size any G2/repair against actual
spent and remaining budget rather than reusing G1's maximum automatically.
At most G1/G2; no retries. G2 requires analysis of G1 and a separate coordinator GO.
One compile-error repair per build is allowed only if own actual spent + new reserve <= cap;
recheck the full task count/budget and corrected exact-packet authorization before any repair.
Main 240 + closeout 30 minutes; absolute window/deadlines bind with dispatch authorization.
Budget preparation snapshot: 236 builds, used $99.8970, other reserves $0.8100, project cap
$118.96. Adding G1 maximum gives $101.7600; this snapshot is not a slot or reservation.

`check_packet.py` checks byte-preserved bodies/contracts, the exact negative copy, request,
root count, ordinary inventory/baseline provenance, cover expectations, tooling equality
and budget. It validates preservation of supplied Actions values, not their independent truth.
Pinned standalone rustfmt passes for `smallsort.rs` and the new module. No local compiler,
cargo/Kani/CBMC, raw evidence, credentials or competing PR code was accessed.

After exact-packet GO: recheck published SHA, task/slot/window/budget; dispatch only through
`k1g.sh`, record build/source/request identities, then `k1g.sh watch BUILD` and end the turn.
On wakeup use bounded summaries/rows/peaks/log-grep and `check-tooling BUILD` against the full
base SHA above. Write `RESULT-LOOPREAL.md` <=40 lines with actual invariants, backing table,
length-cost analysis, before/after regression and limitations. Commit/push research with
`[skip ci]`, then `REVIEW REQUEST <sha>` / `LOOPREAL ЗАВЕРШЁН`, and stop as directed.
