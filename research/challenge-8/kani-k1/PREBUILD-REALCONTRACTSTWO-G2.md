# REALCONTRACTSTWO G2 — authorized exact PRE-BUILD packet

State: historical preparation packet; G2 completed with all five expectations met.
Preparation owner/hash below precede the coordinator-authorized owner-only switch recorded below.

Coordinator GO after G1 report `af0bd533ca69cb1854725ad80f2f32d208cf5c14` authorizes self-dispatch
of exactly five rows below, ten-minute limit, then k1g watch and turn end. No further GO is needed
for this described packet. Owner is `k1-merge` after SCRATCHGEOM build
`88af6889-68fc-48ae-9c20-9e8cfcff729d` finishes; an earlier-free k1-network is an authorized
alternative, not selected in this packet. No competing code/branches/diffs are read.
The gate build was watched with separate `K1_CACHE=/tmp/kani-k1-realcontractstwo-scratchgeom-gate`.
Only terminal metadata/notification for that gate is needed, not its evidence or code.

Branch `experiment/kani-k1-realcontractstwo-20261104`, library `c2bc02b1151f77d163e94b3a69abff07c4be7701`;
unchanged tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd` and Kani pin
`cd355b0bccd32300713bc2ce4f765dafa1510607`. Stage `realcontractstwo-g2`, owner `k1-merge`.
Request `realcontractstwo-g2-20261105`, file SHA-256 `cddff54bb42f40ce7a8c2a50d3e90e0eab54cd51a1a22f7ce2dacc6a74ece0d9`.
Diagnostic standard4 pool (4 vCPU / 16 GB), controls true, jobs 1, 10 minutes per harness.
Organizer flags, no-assert-contracts, object-bits and uninit/value-validity settings unchanged.
All row names below are under `slice::sort::shared::smallsort::verify::realcontracts::`.

| Row | Expected | Domain / check |
| --- | --- | --- |
| sort4_safety_u64 | SUCCESS | full u64 source4; distinct uninitialized destination4; scalar source frame; unwind16 |
| sort4_safety_bytes16 | SUCCESS | full [[u8;16];4] source; distinct uninitialized destination4; scalar byte source frame; unwind32 |
| merge_safety_u64_len2 | SUCCESS | real merge PFC, full u64 source2, disjoint destination2, arbitrary comparator, explicit panic cut |
| merge_safety_u64_len4 | SUCCESS | same at source4/destination4, separate PFC root |
| rejects_merge_overlapping_dst_u64 | FAILED, `merge_contract_regions_disjoint(v.as_ptr(), dst, v.len())` | verified stub; backing4, source[0..2], destination[1..3] |

The existing sort4_safety_u64 changes only its array equality assertion to four scalar u64
comparisons; its unwind remains 16. The [u8;16] root compares all 64 source bytes individually
(two loops of 4 and 16; unwind32) and reads the four output values on return. It uses the same
arbitrary_less function-item scheme for its own T. No sort4 contract/helper/body/signature changes.
This addresses G1's observed builtin-memcmp unwinding failure without claiming independent
trace binding of that memcmp's caller or an established performance cause.

The exact new contract on the real bidirectional_merge and its cfg(kani)-only helper are:

```rust
#[cfg(kani)]
fn merge_contract_regions_disjoint<T>(src: *const T, dst: *mut T, len: usize) -> bool {
    let Some(bytes) = size_of::<T>().checked_mul(len) else {
        return false;
    };
    bytes == 0
        || !crate::ub_checks::same_allocation(src, dst)
        || (src as usize).abs_diff(dst as usize) >= bytes
}

#[safety::requires(v.len() >= 2)]
#[safety::requires(crate::ub_checks::can_dereference(v as *const [T]))]
#[safety::requires(crate::ub_checks::can_write(ptr::slice_from_raw_parts_mut(dst, v.len())))]
#[safety::requires(merge_contract_regions_disjoint(v.as_ptr(), dst, v.len()))]
#[cfg_attr(kani, crate::kani::modifies(ptr::slice_from_raw_parts_mut(dst, v.len())))]
```

The safe source slice already supplies readable initialized data; the explicit source predicate
records that premise alongside len>=2. Destination has v.len() writable aligned slots and is
disjoint in bytes from the source; the helper permits separate allocations or separated ranges
in one allocation, with checked byte-size arithmetic and no unsafe pointer subtraction. It is
pure and total, including for the negative control. Modifies contains exactly dst[..v.len()].
The original T: FreezeMarker signature remains unchanged. No sorted-halves premise or ordering
ensures is added: this is the memory-safety contract with stateless reading arbitrary callbacks.

Each PFC uses one T/F instantiation and full kani::any source elements. Merge roots are distinct
len2/len4 PFCs, both unwind16, with no sortedness assumption or verified helper stub. Their manual
panic_on_ord_violation stub matches the ordinary safety family: cover the explicit order-violation
boundary, assume(false), unreachable. Real merge_up/merge_down and all work before that boundary
execute; only the abort path is cut. This does not prove panic unwinding or a lawful comparator.
Merge source frames compare u64 scalars, then read outputs on normal return. Covers request both
comparator answers, the order-violation boundary and normal return (four). Sort4 requests both
comparator answers and normal return (three). Inspect actual covers separately from SUCCESS.
No independent uninitialized-memory/value-validity proof is claimed under disabled extra checks.

Negative source is the first two initialized u64 elements of backing4. Its destination starts at
index1 and has two writable in-bounds slots, so len/readability/writability are valid while the
regions overlap at index1. stub_verified(bidirectional_merge) must fail the named disjointness
requires. The request binds expect_check to its exact helper expression; unrelated failure does
not satisfy the control. No real-body unsafe overlapping copy is the intended check.

Validation before publication: five-row request accepted by the existing validator; git diff
whitespace check passes. Removing only the new merge helper/attributes restores the entire G1
runtime source byte for byte, including sort4's complete unchanged contract. All five roots are
present, no full-array source-frame equality remains in the changed roots, and all protected lane
paths match the full tooling base. No local cargo/rustc/Kani/CBMC, credentials, raw logs or
competing code have been accessed. No tooling, workflows or ordinary roots are changed.

Reserve: (5*10+30) min * $0.0135/min = $1.0800. Own G1 spent $0.1485, plus reserve $1.2285
<= $3.00. Preparation k1g budget snapshot: 226 builds, used $95.4825, reserved $2.4300;
with G2 at most $98.9925 < project cap $118.96. Dispatcher refreshes the ledger before submission.
This is primary G2 of at most two, with at most one compile-error repair for G2 if needed within
the same cap and review rules. No third primary build or unchanged-input retry is authorized.

Publish separate library/research [skip ci] commits and push without force. Gate owner release
via the registered watch notification (or one bounded readiness status; no status polling loop).
After SCRATCHGEOM's terminal state, self-dispatch exactly this packet on the selected k1-merge
owner under the existing GO, then immediately k1g watch the new BUILD and end the turn.
On completion use bounded K-1 summary/rows, tooling check and needed bounded diagnostics; update
RESULT-REALCONTRACTSTWO.md in <=35 lines and the ledger with G1+G2 outcomes, costs and proof limits.
Publish the result, REVIEW REQUEST / REALCONTRACTSTWO ЗАВЕРШЁН, then stop.


## Observed G2 outcome / final review handoff

The one readiness status on SCRATCHGEOM was WORKING, so the prepared packet was published and
left waiting on its isolated-cache watch. The coordinator then explicitly declared k1-network
free after PERMTAGS and directed immediate dispatch using that owner. The authorized alternative
was selected; SCRATCHGEOM completion was no longer the dispatch gate. No dependency evidence,
code, branch or diff was read. Owner-only [skip ci] commit `41a524a98d6e1136716f95b0b57aaeea48ed8496` changes exactly one
request line from k1-merge to k1-network. Actual request SHA-256 is `30b505e3375bd51b6333ba958be9847a92f859bfb170615c455da38cbc69c05e`.

Published source dispatched as build `1c18c183-7714-4d23-9c25-41e9786dfd5a` and was watched with k1g.sh; its queued
completion notification was SUCCESS. Bounded summary COMPLETE, gate true, expectations true.
Kani exit 1 is consistent with the expected failing overlap control. Check-tooling passed
expected standard4 pool, source binding, protected lane paths and all six hashes against the
full tooling base. The five-row page binds the exact request/build/source and next_offset=done.

| G2 root | Status | Time s | Failed/total | Covers |
| --- | --- | --- | --- | --- |
| sort4_safety_u64 | SUCCESS | 36.28767 | 0/293 | 3/3 |
| sort4_safety_bytes16 | SUCCESS | 73.99763 | 0/462 | 3/3 |
| merge_safety_u64_len2 | SUCCESS | 27.213285 | 0/284 | 4/4 |
| merge_safety_u64_len4 | SUCCESS | 42.305798 | 0/284 | 4/4 |
| rejects_merge_overlapping_dst_u64 | FAILED | 0.5439207 | 1/235 | 1/3 |

The negative control's only failed check is the expected disjointness requires at smallsort.rs:847;
bounded log-grep lines 2718–2719 independently locate it. All positive covers are satisfied:
sort4 3/3 each; merge 4/4 each, including the order-violation boundary and normal return. The
negative's 1/3 covers reflect its reached call and unexecuted comparator, not a failed positive
reachability check. Unreachable properties are recorded separately in the ledger and do not
add independent proof credit.

The unchanged sort4 contract now proves in bounded u64 and [u8;16] source4/disjoint dst4 domains;
source frame comparisons are scalar. This is a successful follow-up to G1's memcmp unwind
failure, without claiming independent trace binding of the historical memcmp caller or cause.
Real merge PFCs execute at exact u64 lengths 2 and 4 with arbitrary reading callbacks and only
the explicit panic boundary cut. No ordering ensures, generic callback frame, panic unwinding,
Drop/ZST proof, uninit/value-validity proof or larger merge composition is inferred.

G2 verify wall 4:39.72, max RSS 1815204 KiB; per-CBMC peak 0.91 GiB, attributed to bytes16
sort4. OOM scan none_seen does not prove memory headroom. Combined bounded budget for G1/G2
is `2 0.3105 0.0000`; G2 cost $0.1620 = total $0.3105 less G1 $0.1485. Both primary builds
are consumed; no compile-error repair or additional build was run. Actual own spent is under
$3.00 with reserve zero. G2 dispatch project maximum was $97.9530 of the $118.96 cap.

RESULT-REALCONTRACTSTWO.md contains all 13 historical/current rows and exact added contracts in
35 lines; the ledger preserves identities, owner authorization, controls, timings, covers and
limits. Only these reporting files change after G2. Publish final [skip ci] report, REVIEW REQUEST
and REALCONTRACTSTWO ЗАВЕРШЁН, then stop. No further implementation or dispatch in this task.
