# Static ZST reachability after coordinator NO-GO

Rejected packet: `ffda59d715b3a0bceac59276d18a03f8a61a6015`.
Scope: existing `assembly::safety_stable_unit_n*`, real helper bodies, no local proof execution.

`stable_unit_case!` constructs `[(); N]`, 48 `MaybeUninit<()>` scratch slots, and calls
`<() as StableSmallSortTypeImpl>::small_sort` with `zst_aware_less::<()>`.
Unit is Freeze, so the specialization calls `small_sort_general_with_scratch` directly.
This entry has no ZST early return. Its length/scratch guards permit all the listed N>=2.
For T=(), `size_of::<T>() <= 16`; presorted length is 8 for N>=16, 4 for 8<=N<16,
and 1 below 8. The two scratch halves are extended with `for i in presorted_len..desired_len`,
calling the real `insert_tail(dst, dst.add(i), is_less)` on each extension.

| Existing root suffix | Presorted | Desired half lengths | Real insert_tail calls on normal route | Inner loop reachable? |
| --- | ---: | --- | ---: | --- |
| `n1` | n/a | early len<2 return | 0 | no |
| `n2` | 1 | 1, 1 | 0 | no |
| `n7` | 1 | 3, 4 | 5 | yes, comparator may return true |
| `n8` | 4 | 4, 4 | 0 | no |
| `n16` | 8 | 8, 8 | 0 | no; boundary control |
| `n17` | 8 | 8, 9 | 1 | yes, comparator may return true |
| `n31` | 8 | 15, 16 | 15 | yes, comparator may return true |
| `n32` | 8 | 16, 16 | 16 | yes, comparator may return true |

For a ZST, `dst.add(i) == dst`, and `sift = tail.sub(1) == tail == begin`.
`zst_aware_less::<()>` reads with `ptr::read` and returns an arbitrary bool, so the initial
`if !is_less(...) { return; }` does not exclude entry. On the true branch the real loop
copies one zero-sized value, sets `gap_guard.dst = sift`, and exits at `sift == begin`.
Thus its old `size_of::<T>() > 0` base invariant is false on an existing reachable route.
The ordinary lane uses `--no-assert-contracts`; the real body is not cut by a verified stub.
The helper contract's strict non-ZST geometry therefore cannot justify excluding this path.

Correction: short-circuit with `size_of::<T>() == 0 || (the previous non-ZST geometry)`.
For nonzero size the prior conjunction is identical. For zero size the invariant is true
without evaluating strict-address tests or modulo zero. Runtime bodies, signatures,
function contracts and loop modifies are unchanged. This is not new ZST PFC proof credit.
G1 adds both requested existing roots: N16 checks the no-extension boundary and N32 exercises
the real ZST loop route. Dynamic safety/assigns/cover outcomes still require G1 evidence.

Source anchors: `verify/assembly.rs::stable_unit_case!`, `verify/comparators.rs::zst_aware_less`,
`smallsort.rs` Freeze stable specialization, `small_sort_general_with_scratch`, `insert_tail`.
Only the source call/count argument is established here; no Kani execution is inferred.
