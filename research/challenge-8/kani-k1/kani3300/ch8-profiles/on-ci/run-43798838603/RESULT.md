# PROF-ON-01 — run 43798838603 (coordinator intake, bounded receipts only)

- Tool: SEL1 `14bc57fdb9`; source `9fa2f7f977` (P′); control `d569db0c1f` → trigger `7f33fb9067`
  (`uninit-ci/ch8-prof-on-a`). Job `profiles (on)` 03:32:59Z–04:34:53Z, conclusion failure (runner verdict
  `PENDING_INDEPENDENT_REVIEW`, credit NONE).
- Artifact `ch8-prof-on-43798838603-1` (id 14198355109, 1 065 890 B).
  Export SHA256: group-00 `3cbbdd70…af13`, group-01 `e77e28bb…8063`.
- Groups: group-00 (no cfg) compile 176 s, CBMC RSS peak 4.79 GiB; group-01 (`kani_smallsort_controls`)
  compile 43 s, peak 0.97 GiB. All 62 rows OBSERVED (no timeout/OOM/NOT_RUN).

## Raw split (failure lists from export; acceptance not yet applied)

| Class | Rows | Count |
|---|---|---|
| No failed checks (to be judged by accept-v4 classifier) | rest | 41 |
| Negatives failing on own named property | profile_bad_relation_rejected_u8, profile_full_value_checker_rejects_payload_change_u8 (assertion.3), profile_wrong_f_{insert,merge,swap}_rejected_u8, profile_wrong_f_sort4_rejected_u64, rejects_payload_corruption (assertion.5), rejects_swap_comparator_writing_outside_frame_u8 (closure assigns.1) | 8 |
| Kani uninit: `PolymorphicIter<[MaybeUninit<usize>;2]>::new_unchecked` unsupported (predicted in RISKS.md) | freeze_noncopy_n2; rejects_always_true (also its own assertion.4/.6 fail) | 2 |
| Kani uninit: "does not support checking memory initialization of transmute from [MaybeUninit<T>; N] to [T; N]" in `MaybeUninit::array_assume_init` (core maybe_uninit.rs:1056) | swap_contract_{u8,u64,bytes16,bytes17,cell_i32,drop_u8}_n2, sort4_contract_bytes16_n4, profile_sort4_consumer_b16 | 8 |
| Kani uninit: `kani::internal::write_any_slice::<T>.safety_check.1` "Reading from an uninitialized pointer of type `*mut [T]`" (kani_core lib.rs:716 havoc) | profile_merge_consumer_u8_len4, profile_sort4_consumer_u64 | 2 |
| Kani uninit: fn-item ZST layout — `<fn {arbitrary_less::<u8>} as FnMut>::call_mut.unsupported_construct.1` | swap_safety_u8_backing4 | 1 |

Total 62. Under OFF all 62 were ACCEPTED (accept-v4); every ON-only failure above is an instrumentation
construct of Kani uninit-checks, not a property of the code under proof. The array_assume_init, write_any_slice
and fn-item cases are new relative to RISKS.md.
