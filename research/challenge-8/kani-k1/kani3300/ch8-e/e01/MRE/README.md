# Single-file reproducers

Ten `e_*.rs` files are byte-for-byte copies of the dispatched control tree
`3219b3f220de568a69275618944dbe26bfe2917d`, not newly executed reductions.
Their hashes match the frozen `controls-ci/CI-REQUEST.json` and all corresponding
artifact receipts. Each file contains one independent harness.

The smallest **observed** H positive here is `e_h_write_then_read.rs`:
SEL1 OFF SUCCESS **69/0**, ON FAILURE **224/2**, both failures
`assigns` at `library/kani_core/src/mem_init.rs:120`. The copy companion is
`e_h_copy_then_read.rs`: OFF 88/0, ON 270/5. See RESULT/EVIDENCE for exact rows.
`e_h_live_after_havoc.rs` retains the fixed alias/witness diagnostic.
`e_h_hole_inside_alias.rs` and `e_h_outside_false_alias.rs` are deliberately
invalid read controls, not positive reproducers.

`shadow_write_u8_candidate.rs` is an additional **NOT_RUN** reduction proposal
without unions, to expose the shared upstream loop-frame path independently of
SEL1's MaybeUninit support. It has no measured compile or verification outcome.

Reproduction recipe for a separately authorized environment (not run in this intake):

```sh
kani e_h_write_then_read.rs --harness e_h_write_then_read --exact \
  -Z unstable-options -Z loop-contracts -Z quantifiers -Z uninit-checks \
  --harness-timeout 600s --jobs 1 --cbmc-args --object-bits 12
```

Omit only `-Z uninit-checks` for OFF. For the primitive candidate, substitute its
filename and harness. For E-Q, select the corresponding file/harness, preserving
quantifiers and default checks. Exact historical argv (including export path),
exit and configuration are in the artifact receipt; these commands do not claim
to be a newly validated invocation.

`e_s_unbounded_slice.rs` intentionally preserves the dispatched E0425 error.
The source-only correction is `kani::arbitrary::any_slice_mut_unbounded::<u8>()`
at line 6. It is NOT_RUN and does not establish alloc/core binding or legal reads.

Do not add private shadow state to the user's frame, turn checks off, or supply
unchecked initialization summaries to manufacture a pass. Any compiler fix must
preserve both H negatives, sentinel/value framing, alias checks and default checks.
