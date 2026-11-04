# REALCONTRACTSTWO G1 — exact-packet PRE-BUILD review

State: prepared, not dispatched. Stop until coordinator GO for the full published packet SHA.
Worktree `/root/verify-rust-std-kani-realcontractstwo`; branch `experiment/kani-k1-realcontractstwo-20261104`.
Task `ca4b4a00e9`, inherited library/report base `d648179493`.
Library commit `def6ad2e111e68987b040e3d3eb14a279e4aea0d`; tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`.
Kani pin `cd355b0bccd32300713bc2ce4f765dafa1510607` unchanged.
Owner `k1-merge`, required free at dispatch; its current availability is not inferred from the budget.
Stage `realcontractstwo-g1`; request `realcontractstwo-g1-20261104`;
request file SHA-256 `0b0188923d4cbe99a94d9f1698aadd67c17b01396f3eb90e4fb002676d2fc5f1`; ledger `realcontractstwo-ledger.json`.

Diagnostic standard4 pool (4 vCPU / 16 GB), controls true, jobs 1, ten minutes per harness, eight rows.
No uninitialized-memory or value-validity flags added. Existing organizer flags and object-bits stay unchanged.
Every row below has prefix `slice::sort::shared::smallsort::verify::`.

| Row | Expected | Domain / purpose |
| --- | --- | --- |
| realcontracts::swap_safety_u8_backing9 | SUCCESS | real swap PFC; full u8 backing9, arbitrary a/b in 0..9 including equality |
| realcontracts::swap_safety_u8_backing13 | SUCCESS | real swap PFC; full u8 backing13, arbitrary a/b in 0..13 including equality |
| realcontracts::unstable_network_safety_u8_n9_stubbed | SUCCESS | inherited actual Unstable consumer, same u8/backing9/F, stub_verified(swap_if_less) |
| realcontracts::unstable_network_safety_u8_n13_stubbed | SUCCESS | inherited actual Unstable consumer, same u8/backing13/F, stub_verified(swap_if_less) |
| realcontracts::insert_tail_safety_u64_tail1_to4_backing5 | SUCCESS | real insert_tail PFC; full u64 backing5, begin at 0, symbolic tail 1..=4 |
| realcontracts::rejects_insert_tail_equal_begin_u64 | FAILED, `begin < tail` | stub_verified(insert_tail), full u64 backing5, tail == begin |
| realcontracts::sort4_safety_u64 | SUCCESS | real sort4 PFC; arbitrary initialized u64 source4, separate uninitialized writable destination4 |
| assembly::sorted_permutation_insert_tail_u8_n2 | SUCCESS | unchanged ordinary root; real insert_tail, strict reading comparator, sorted permutation |

Swap and consumer use the exact same function-item `arbitrary_less::<u8>`: volatile reads of both
arguments, then a fresh nondeterministic bool per call; no callback state. PFC position domains
contain every constant network call (N9: 0..8, N13: 0..12) and equal positions as well.
Both PFC/consumer pairs must pass in this packet before claiming matched bounded composition.
The existing step-1 consumers alone did not prove the larger-allocation swap body. Matching here
covers type, allocation size and comparator, with arbitrary input values, not a universal summary.
The actual consumer route still uses the real no-op insertion call at offset == len.
No additional real/stub timing pair is requested: these eight rows prioritize matching PFCs and
current stub consumers plus all mandatory helper/control/regression rows. Optional `[u8; 16]`
sort4 PFC is deferred to keep this exact packet within eight rows.

New exact contracts and cfg(kani)-only helpers (no ensures):

```rust
#[cfg(kani)]
fn insert_tail_contract_len<T>(begin: *mut T, tail: *mut T) -> usize {
    let elem_size = size_of::<T>();
    if elem_size == 0 || begin >= tail || !crate::ub_checks::same_allocation(begin, tail) {
        return 0;
    }
    let Some(bytes) = (tail as usize).checked_sub(begin as usize) else {
        return 0;
    };
    if bytes > isize::MAX as usize || bytes % elem_size != 0 {
        return 0;
    }
    (bytes / elem_size).saturating_add(1)
}

#[safety::requires(
    begin < tail
        && insert_tail_contract_len(begin, tail) > 1
        && crate::ub_checks::can_dereference(ptr::slice_from_raw_parts(
            begin,
            insert_tail_contract_len(begin, tail),
        ))
        && crate::ub_checks::can_write(ptr::slice_from_raw_parts_mut(
            begin,
            insert_tail_contract_len(begin, tail),
        ))
)]
#[cfg_attr(
    kani,
    crate::kani::modifies(ptr::slice_from_raw_parts_mut(begin, insert_tail_contract_len(begin, tail)))
)]
// immediately on the unchanged insert_tail declaration

#[cfg(kani)]
fn sort4_contract_regions_disjoint<T>(src: *const T, dst: *mut T) -> bool {
    let Some(bytes) = size_of::<T>().checked_mul(4) else {
        return false;
    };
    bytes == 0
        || !crate::ub_checks::same_allocation(src, dst)
        || (src as usize).abs_diff(dst as usize) >= bytes
}

#[safety::requires(
    crate::ub_checks::can_dereference(ptr::slice_from_raw_parts(v_base, 4))
        && crate::ub_checks::can_write(ptr::slice_from_raw_parts_mut(dst, 4))
        && sort4_contract_regions_disjoint(v_base, dst)
)]
#[cfg_attr(kani, crate::kani::modifies(ptr::slice_from_raw_parts_mut(dst, 4)))]
// immediately on the unchanged sort4_stable declaration
```

Insert geometry checks element size, strict pointer order, same allocation, representable and
integral element distance. The requires then check the entire inclusive range for initialized
read access and write access. The write set is precisely begin..=tail; no sorted-prefix premise
is added to this safety-only contract. The length helper never dereferences or calls unsafe
pointer-distance operations. It returns zero for equal/invalid geometry, and its checked/division
arithmetic is guarded, so even the negative consumer's modifies expression is total.
Sort4 checks four initialized reads, four writable slots and disjoint byte ranges. Its helper
accepts separate allocations or disjoint ranges in one allocation; zero-sized ranges are empty.
The existing sort4 signature has no Freeze bound, so its signature is retained. This PFC uses u64,
which is Copy/Freeze, and does not establish generic interior-mutation or callback effects.
All new helpers are cfg(kani); safety::requires is a runtime no-op, as in the existing swap contract.
Runtime bodies/signatures, existing requires, workflows, scripts, tooling and ordinary roots are unchanged.
Only the opt-in realcontracts harnesses, real-helper attributes/helpers and suite documentation change.

Positive swap PFCs request both callback answers, equal/forward/reverse positions and return (6 covers).
Insert PFC requests both callback answers, each tail offset and return (7 covers); the explicit frame
asserts values after tail are unchanged. Sort4 requests both callback answers and return (3 covers),
checks source unchanged and reads output on return. Uninitialized destination construction is a
harness input, not independent proof of initialization under disabled uninit/value-validity checks.
Stubbed networks request normal return; the two callback-answer covers are expected unreachable
because swap is stubbed and insertion performs zero iterations. Inspect covers separately from SUCCESS.
The negative control must fail its located requires containing `begin < tail`; unrelated failure is
not accepted by expect_check. The ordinary regression retains its existing assertions and return cover.
Unwind is 16 for new roots and inherited consumers; ordinary regression retains 17.

Validation: existing request validator accepts all eight roots; git diff --check passes. Source checks
compare runtime declarations and bodies byte for byte with the task base; deleting only the new
attributes and cfg(kani) helpers restores the entire original runtime file. All protected lane/tooling
paths match the full base. No local cargo/rustc/Kani/CBMC, Actions/PR/issue, credentials, raw logs or
competing code/branches/diffs were accessed. Compilation and proof outcomes remain NOT_RUN.
Specification restrictions (one T/F instantiation per PFC; pure, nonpanicking write-set expressions)
follow [Kani contracts documentation](https://model-checking.github.io/kani/crates/doc/kani/contracts/index.html).

Reserve: (8 * 10 + 30) min * $0.0135/min = $1.485; own spent $0, own cap $3.00.
One preparation k1g budget query returned 224 builds, used $94.6995, reserved $2.0925;
with this G1 at most $98.2770 < project cap $118.96. Refresh the project ledger at dispatch.
The window is main 240 + closeout 30 minutes. At most G1 and G2, with one compile-error repair
per primary build, always within actual own spent + next worst-case reserve <= $3.00.
No repair or G2 dispatch is authorized by this packet. G2 needs a new coordinator GO after G1;
if symbolic insert tail1..4 times out, the task permits separate tail roots in a reviewed G2.

Publish separate library/research commits with [skip ci], push without force and stop with
PRE-BUILD REVIEW for the full packet SHA. After exact-packet GO and free owner, dispatch this branch
using k1g.sh, immediately run k1g.sh watch BUILD, then end the turn without polling status.
After the queued completion notification: bounded K-1 summary/row evidence and check-tooling only;
report timings, exact failed requires, covers, matched domains and ordinary applicability separately.
Write RESULT-REALCONTRACTSTWO.md in <=35 lines and update the new ledger, publish with [skip ci],
then REVIEW REQUEST / REALCONTRACTSTWO ЗАВЕРШЁН and stop. These safety/frame contracts support
only the tested bounded stateless comparator domains; no ordering ensures, universal T/F frame,
non-Copy/Drop/ZST proof, panic-path proof or bidirectional_merge contract is claimed here.
