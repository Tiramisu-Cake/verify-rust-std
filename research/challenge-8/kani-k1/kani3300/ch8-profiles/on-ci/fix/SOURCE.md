# Source PROF-ON-02

Source `166a406e2203bae2fc9246ba00c00b944b364445`, tree
`460029c0d95fa7ef04eb7da0115f6fa2792c3b0b`, parent P′ `9fa2f7f977`.
Branch `work/ch8-profiles-pprime-w11`. See SOURCE.json and source.patch.

A covers all eight array_assume_init failures enumerated by the coordinator
bounded run summary: six exact-two swaps, B16 sort4 leaf and consumer.
The shared sort4 change also applies to the U64 pair. Each array element is
generated independently; the B16 element's byte array still uses u8's raw-array
Arbitrary override. No new bounds, sorted assumptions or initialized output.

B replaces only sort4's frame encoding by its four thin targets. A separate
merge4_profile plus exact-length LtU8 proof leaf qualifies the len4 consumer;
the general merge_profile 2..=32 source is unchanged. Both output arrays remain
MaybeUninit. The bounded wrapper proves only len4, never the general theorem.

C uses the shared comparator factory at all matching call sites in the existing
ordinary and wide helper modules. Reading/nondeterminism/covers remain intact.
All existing oracle/covers and the fresh new leaf are in BINDING-SPEC.json.

PolymorphicIter has no equivalent harness-only workaround established for
freeze_noncopy_n2/rejects_always_true. Keep both ON rows BLOCKED_TOOL without
changing their original oracle. Runtime/compiler patches are outside this stage.

Static/synthetic preparation only. Compile/proof NOT_RUN; proof credit NONE.
