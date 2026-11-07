# Kani pin check: the kani#5104 reproducer and `-Z uninit-checks`

Two questions about the organizer Kani pin `cd355b0bccd32300713bc2ce4f765dafa1510607` (nightly-2026-10-22):

1. Does the array-select reproducer from [kani#5104](https://github.com/model-checking/kani/issues/5104) still fail?
   **Yes.**
2. Can `-Z uninit-checks` check the SmallSort code paths? **Not yet:** it stops on unsupported operations before
   the target reads.

## Setup

- An earlier research tree (`53ec52ed73`) plus an opt-in module
  [`verify/pincheck.rs`](https://github.com/Tiramisu-Cake/verify-rust-std/blob/690bdea1c7e2c919161e0b3ef16c206122e885b5/library/core/src/slice/sort/shared/smallsort/verify/pincheck.rs), compiled only with `cfg(kani_smallsort_controls)`. The module is not part of the
  submission.
- Google Cloud Build, `e2-standard-4` (4 vCPU, 15.6 GiB, Ubuntu 24.04). The runner uses the repository's
  `scripts/run-kani.sh` and Kani pin unchanged.
- Build `d7302cc6-30d7-478e-9a7e-7750f034b3e4`: the reproducer with default checks. Build
  `8f59f833-267f-456c-a0f3-c5f867faca39`: the same runner with `-Z uninit-checks`.

## 1. Array-select reproducer (kani#5104)

[D1](https://github.com/Tiramisu-Cake/verify-rust-std/blob/690bdea1c7e2c919161e0b3ef16c206122e885b5/library/core/src/slice/sort/shared/smallsort/verify/pincheck.rs#L12-L30) builds `v = [x, y]` with `x, y: [u8; 1]`. It picks a pointer to `v[0]` or `v[1]` with
`hint::select_unpredictable` and reads through it with `ptr::read`. The assertion says the value read is the selected
element. D2 is the same code on `u8` elements. F5 is D1 with symbolic distinct indices for the two candidates.

| Harness (`verify::pincheck::`) | Expected | Status | Failed / total checks | Covers |
|---|---|---|---|---|
| `casefive_d1_select_read_bytes1` | FAILED | FAILED: `casefive D1: read through the selection` @ pincheck.rs:29 | 1/40 | 2/2 |
| `casefive_d2_select_read_u8` | SUCCESS | SUCCESS | 0/26 | 2/2 |
| `arrayfactor_f5_symbolic_indices_bytes1` | SUCCESS | SUCCESS | 0/52 | 4/4 |

D1 still fails on its value assertion. Both of its covers are satisfied: each branch is reached with `x[0] != y[0]`.
The scalar version D2 and the symbolic-index version F5 pass. All three rows give the same results as on Kani
`9461e07a`, where we first observed the failure.

**Consequence for the submission:** four fixtures use array-valued elements:
- `network::swap_contract_bytes16_n2`;
- `network::swap_contract_bytes17_n2`;
- `merge::sort4_contract_bytes16_n4`;
- `merge::sort4_arbitrary_comparator_bytes16_n4`.

No check fails in any of them, but their results carry this caveat about the model.

The same build also ran six negative controls of that tree. Each failed exactly its one designated check, so assertion
reporting works as expected on this pin.

## 2. `-Z uninit-checks` on the SmallSort code paths

The first two rows are a calibration pair. They differ only in whether the `MaybeUninit<u8>` slot was written before
`assume_init`. A working uninit check should fail the first row and pass the second.

| Harness (`verify::`) | Expected | Status | The only failed check | Kind |
|---|---|---|---|---|
| `pincheck::pincheck_calibration_uninit_read_u8` | FAILED | FAILED | `Transmuting between types of incompatible layouts.` @ core/src/mem/mod.rs:1283 | unsupported |
| `pincheck::pincheck_calibration_init_read_u8` | SUCCESS | FAILED | same check, same location | unsupported |
| `pincheck::raw_uninit_read_sensitivity` | FAILED | FAILED | `Interaction between raw pointers and unions is not yet supported.` @ pincheck.rs:106 | unsupported |
| `network::swap_contract_four_positions_u8` | SUCCESS | FAILED | `Kani does not support memory initialization checks across calls through function pointers.` ([kani#3300](https://github.com/model-checking/kani/issues/3300)) @ core/src/ops/function.rs:166 | unsupported |
| `assembly::sorted_permutation_insert_tail_u8_n2` | SUCCESS | SUCCESS | none (0/174) | — |
| `assembly::permutation_merge_u8_n4` | SUCCESS | FAILED | `Interaction between raw pointers and unions is not yet supported.` @ assembly.rs:83 | unsupported |

On this pin, `assume_init` goes through `transmute_neo`, which `-Z uninit-checks` rejects for
`MaybeUninit<u8> -> u8`. Both calibration rows therefore stop on the same unsupported check, and the uninitialized row
still satisfies the covers placed after its read. The SmallSort paths hit the same kinds of unsupported operation:
- `MaybeUninit` raw pointers;
- comparators called through function pointers.

The one passing row is not evidence of an uninit check, because the calibration did not work. For this reason the
submission makes no claim about reads of uninitialized memory.

## Raw evidence

- [Reproducer build summary](https://github.com/Tiramisu-Cake/verify-rust-std/blob/690bdea1c7e2c919161e0b3ef16c206122e885b5/research/challenge-8/kani-k1/pincheck/g1.summary.md)
- [`-Z uninit-checks` build summary](https://github.com/Tiramisu-Cake/verify-rust-std/blob/690bdea1c7e2c919161e0b3ef16c206122e885b5/research/challenge-8/kani-k1/pincheck/g2.summary.md)
- [Fixture source](https://github.com/Tiramisu-Cake/verify-rust-std/blob/690bdea1c7e2c919161e0b3ef16c206122e885b5/library/core/src/slice/sort/shared/smallsort/verify/pincheck.rs)
