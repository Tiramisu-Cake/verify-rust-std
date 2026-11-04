# REALCONTRACTS G1 — exact-packet review

State: historical G1 packet; build 841ecc9e-3696-4188-aad0-300cd6f4a35b ended COMPILE_ERROR.
The compile-error repair packet below requires new exact-SHA coordinator GO before dispatch.
Worktree `/root/verify-rust-std-kani-realcontracts`; branch `experiment/kani-k1-realcontracts-20261104`.
Task `3bd643ceaa`; tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`.
Library commit `3f0fc215587ee4b5ab4e8e9f901e49ea206f7c19`; owner `k1-merge`.
Stage `realcontracts-g1`; request `realcontracts-g1-20261104`; ledger `realcontracts-ledger.json`.

Only attributes were added to runtime source. Safety requires use the repository's `safety` macros,
which emit Kani contracts and are no-ops outside Kani. Modifies attributes are guarded by `cfg(kani)`.
The two offset arithmetic checks mirror this base's `ptr::add` contract, including the existing
`byte_offset_does_not_wrap` guard against Kani pointer-encoding truncation. No `a_pos != b_pos`.
The safe insertion helper keeps its existing abort check and has no sorted-prefix precondition.
No ensures were added. The complete added contract text is:

```rust
#[safety::requires(
    a_pos.checked_mul(size_of::<T>()).is_some_and(|offset| {
        offset <= isize::MAX as usize
            && (v_base as isize).checked_add(offset as isize).is_some()
            && ptr::byte_offset_does_not_wrap(v_base, offset as isize)
    })
)]
#[safety::requires(
    b_pos.checked_mul(size_of::<T>()).is_some_and(|offset| {
        offset <= isize::MAX as usize
            && (v_base as isize).checked_add(offset as isize).is_some()
            && ptr::byte_offset_does_not_wrap(v_base, offset as isize)
    })
)]
#[safety::requires(
    crate::ub_checks::same_allocation(v_base, v_base.wrapping_add(a_pos))
        && crate::ub_checks::same_allocation(v_base, v_base.wrapping_add(b_pos))
)]
#[safety::requires(
    crate::ub_checks::can_dereference(v_base.wrapping_add(a_pos))
        && crate::ub_checks::can_write(v_base.wrapping_add(a_pos))
)]
#[safety::requires(
    crate::ub_checks::can_dereference(v_base.wrapping_add(b_pos))
        && crate::ub_checks::can_write(v_base.wrapping_add(b_pos))
)]
#[cfg_attr(kani, crate::kani::modifies(v_base.wrapping_add(a_pos), v_base.wrapping_add(b_pos)))]

#[safety::requires(offset != 0 && offset <= v.len())]
#[cfg_attr(kani, crate::kani::modifies(v))]
```

G1: diagnostic, `gcb-e2-standard-4`, controls true, jobs 1, five minutes per row.
All row names below have prefix `slice::sort::shared::smallsort::verify::`.

| Row | Expected | Domain / baseline |
| --- | --- | --- |
| realcontracts::swap_safety_u8_backing4 | SUCCESS | arbitrary positions 0..4, equality included |
| realcontracts::swap_safety_u64_backing4 | SUCCESS | same |
| realcontracts::swap_safety_bytes17_backing4 | SUCCESS | same; full 17-byte values |
| realcontracts::insertion_safety_u64_len1_to6 | SUCCESS | backing6, symbolic len 1..=6 and offset 1..=len |
| realcontracts::rejects_swap_outside_backing_u8 | FAILED, `can_dereference` | stub_verified; positions 0 and 4 in backing4 |
| network::dispatch_safety_stable_u8_n0_1_2_7_8 | SUCCESS | task reports NEWPINCAL 11.6 s |
| network::swap_contract_four_positions_u8 | SUCCESS | task reports NEWPINCAL 12.8 s |
| network::insertion_safety_u64_n1_to5 | SUCCESS | prior time/build identity unavailable in task |

Positive PFCs execute real bodies with a stateless comparator that volatile-reads both arguments
and returns a fresh arbitrary bool on every invocation. Covers request both comparator answers,
equal/forward/reverse swap positions, insertion lengths 1..6, offset < len and offset == len.
Explicit asserts check unchanged elements outside the write set. Inspect cover satisfaction
separately from SUCCESS; require the negative control's located failed check to be the requires.

Validation before publication: K-1 request validator accepts all 8 rows; diff whitespace check passes;
removing precisely the inserted attributes restores the entire original runtime source verbatim;
all lane/tooling paths equal the full base SHA. No local cargo/rustc/Kani/CBMC was invoked.
The syntax follows core's `ptr/mod.rs` and existing closed-profile contracts. Kani's
[contract documentation](https://model-checking.github.io/kani/crates/doc/kani/contracts/index.html)
requires one generic instantiation per PFC; each new PFC uses one T/F pair.
Compileability, proof outcomes, covers and regression timings remain untested until G1.
Baseline times above are task-reported, not independently rechecked evidence.

Reserve: (8 * 5 + 30) min * $0.0135/min = $0.945. Own spent $0, own cap $3.
Project snapshot: 217 builds, used $93.6465, other reserved $1.4580; with G1 at most $96.0495
against $118.96. Dispatch must refresh the project budget. No G2 or repair is preauthorized
by this packet: at most two primary builds, no retry, one compile-error repair per build only
within own spent + reserve <= $3 and after the required exact-packet review.

A successful bounded PFC would support safety-only stub_verified for these proven T/F domains;
no ordering or permutation summary, generic callback frame, stateful/external callback effects,
ZST/non-Copy/Drop types, panic/unwinding, uninit/value-validity checks, insert_tail contracts or
bidirectional_merge contracts are established here. Insertion's safe-function acceptance is
itself part of the spike. G2 needs separate coordinator GO after G1 analysis. After GO use
k1g dispatch, then k1g watch and end the turn; read only bounded K-1 summaries/rows/peaks/log-grep,
check tooling against the full base, and write RESULT-REALCONTRACTS.md in at most 35 lines.

## G1 compile-error repair 1 — review packet

G1 source SHA `23fa5dee5f23645abea868d1370b46298d96435b` is bound by the bounded summary;
check-tooling passed pool, source identity and all six tooling SHA-256 checks against the base.
Every row is NOT_RUN. The bounded log-grep reports E0433 in generated requires/modifies code
and suggests `use crate::kani`; core's `ptr/mod.rs:431` already has this cfg-gated import.
Additional bounded queries expose E0034 in pre-existing numeric methods (`checked_sub`, `MAX`,
integer macro implementations). Causality is unestablished: this minimal repair addresses the
missing import only; it does not claim that all compilation errors are fixed. No unrelated
numeric code is changed.
Library repair `2e7f1a6db52778a1e9a9652f02b639f088fb2cd3` adds only:

```rust
#[cfg(kani)]
use crate::kani;
```

Contracts, helper bodies/signatures, harnesses, expectations, flags, timeouts and tooling are unchanged.
Only request_id changes to `realcontracts-g1-compile-repair1-20261104`, identifying the single
compile-error repair permitted for G1. It is not G2 or an unchanged-input retry.
G1 cost by k1g budget is $0.135; new worst-case reserve $0.945; own spent + reserve $1.080 <= $3.
No repair dispatch has occurred. No second compile-error repair for G1 is authorized.
RESULT-REALCONTRACTS.md records the observed failure and proof limitations; compile acceptance
and every requested proof/cover/regression measurement still await this repair build.
