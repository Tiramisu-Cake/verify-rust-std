# Historical selector dependency closure

This records the dependency closure for the pointer-select result from Build
`f4dc1ddf-c995-4650-a4d0-896cf14ad565` (infra/proof `e2b249674cbe505f2d073e0df8da023a6e6406ce`).
It is a provenance map, not permission to reuse those hashes as pins for C4.

## Translator chain

Each listed patch changes only `src/rust_frontend/vf_mir_translator/vf_mir_translator.ml`.
The chain is ordered; each result is the next patch's parent.

| Step | Parent profile / purpose | Patch SHA-256 | Result translator SHA-256 |
| --- | --- | --- | --- |
| O26 refresh | owner/A1 literal refresh | `0a6ac67c31b785acd5b2ab5eb9eb0158e0b5603dafda05033b7c58a6ef941c54` + `ad8aa43b85a58fa4b8894fed36816aba89a9abfb0f9b80cd9547e4454ff6fb75` | `0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a` |
| R2 | wrapper rebase | `f7b74745ef088f82598b409fbba347d8671691905048c1c6ed715b9226e4830b` | `2a9d9fc989dcf5564c16dc5a4f8df90755257138a9f4cadde1ff9d7c7ae9fef5` |
| R3 | wrapper input relation | `da62de4fe2a166e15e298d7a8f333e6524267392f36e3c196b81726299a47f8a` | `34a03879b45377570eab81ee384ade01ebea9d5d216eb6223c6c742c5819dc15` |
| R3 ghost scope | exact scope diagnostic | `127143ffec8499202817f6aca5041fb6c6c5c6899cc4f5e3601d97cd0b8e29e8` | `ed8ee5ed8a7f8abb7d9c7cee3a978059b55c0a02e34f908170a80d6cc3ed4102` |
| R3 receiver | receiver binding | `284a135f0c43c0ef50a7d48cd5bc6e294415e0168fa9e11a9238c0ab9c0c6c09` | `7451dee6edcd63a4151eb45816a882f51107c7f096b047762cc482b154f61fd6` |
| R3 ghost column | ordered ghost-column routing | `7e77dcc7200a141beb0a3a48ee9f0634f0e1ef7f866f992d44d820b9d58d11f6` | `f57415ab49abef2bdc5632ca47962502be8732a1321cabd607d04501c6612a86` |
| R3 column/nested | nested proof ordering | `e4cf0424921f66bbfd0af99757b3eb9198a2f25e41bd0e8f9386d81dd53be268` | `17ea15e06cee10724022df97a34d763ddf406dd8ce7bde517f205f1741402b8d` |
| R3 FRAME | current thread-only frame | `a15489c1e9b76db3d113e1f58a5531d240db2c31e23362b3b9a8c1fb656128ca` | `a8421aac6bc2863e6df8d5ca9fc94b15251123f5203cf92d271529a595bad243` |
| R3 FRAME-shadow | selected original-input relation after wrapper shadowing | `6e49d7f7c1eb43288a0ad0e6f8dd8518e76218a57c3d9a6c7a7b6cf7a953a1ee` | `54fd5dd628d8e9dac3b0a702cb13bf4ab6d2d235d0f157eb5228082b4954adf6` |
| R3 cleanup projection | exact false-unwind pointer-drop and assume-init calls | `74694608a600bb043816f5345e3173666b5e5fd8ab9b98263f98ec05e12ff150` | `9cf8bc328a2a12c97b9ae04b359f8a4c59f1d561ae768f1e6bde4146d247a041` |

Full hashes and parent fields are in `overnight-assume-actual/O26-*-PROFILE.json`
and `O26-R3-*-TEST.json`; patch bytes are under
`overnight-assume-actual/verifast-*.patch`. The final adapter is
`cloud-build/o26-r3-frame-shadow-test.py`, which imports
`cloud-build/o26-r3-frame-test.py` for the ordered parent-chain checks. The
source preparation is `overnight-assume-actual/capture.py` plus
`prepare-wrapper-input-relation-frame-shadow.py`.

FRAME-shadow requires the prior FRAME profile and opt-in. FRAME requires R2/R3,
scope, receiver, column, nested ordering, plus the owner/A1/nested/forget and
wrapper admission pairs. Thus the smallest historical *tail* is FRAME-shadow
then cleanup projection; reproducing or adapting the proof requires the whole
chain and its parent evidence. The no-duplicate-transport cleanup change at
`e2b24967` replaces the repeated typed CFG payload with its canonical hash in
`O26-R3-CLEANUP-PROJECTION-TEST.json` and changes the adapter comparison. It
does not remove the full CFG dependency: hash
`92f942a44944bd4eba4da22ccc4fbbe10901b3e9e64072d2478edbc930049c35` is still
checked against the FRAME parent graph.

## Unit and result boundary

The historical target is a nine-body source unit ending in
`select_unpredictable` and its nested `DropOnPanic::drop`; verified source SHA is
`7ec86f52b362f7f8b2ed26e3fa108212eb3d6288820bab9c6db3fa37bf8cabe0`, unit SHA
`203989644124ecd20473efc286cb43a148de4f196c10b4a037f4bdb04cd2d098`, nested
body 8 SHA `e0508d6cfb436bc1bcd04737ad74e37b357d17e9ec3c2a226ee961f7036eae9a`. The cleanup
graph is the exact 39-block / 56-local outer unit: pointer drop at bb16,
`assume_init` at bb34, shared cleanup at bb38. The final cleanup patch retains
the original complete MIR identity while projecting only the two exact
same-unit calls proven false-unwind.

Build `f4dc1ddf` recorded raw proof exit 0 but Cloud status FAILURE because the
collector used stale expectations; immutable evidence replay reclassified the
conditional pointer contract as complete. The result remains experimental and
unaccepted: profile admission open, no unrestricted generic `T`/ZST proof, and
no actual sort4 composition. See `next-select-frame-caller/END-CHECKPOINT-2026-10-09.md`
and `FINAL-TEST-RESULT.json`.

## C4 and ManuallyDrop separation

C4 at checkpoint `9240f9d4` is a different proof unit/profile. Its C4 prefix
pins source SHA `ba9e6ad3633004c3d934c590462443951ddd6dec80a5df9ffb687ec940958c6f`,
normal MIR SHA `af8dcfda4212ec1e1bd8fcafcb763fe0107fbeb63b6c1a65bc830e2c81bf9f80`
(141 blocks, 223 locals), and read-only MIR SHA
`aebd7d6219106ba8f6b2fd730bb0a9b0876bea141eb2f06ab7c6e3804abc23ea`; it ends after four comparator calls and
excludes selector/copy. Its C4 translator profile at `203b5925` is independently
pinned from `7361f1c26af1db68d3f172e9124d3a74c2d5ea8415a7edcc4164d43ffdcfc5b8`
through patch `3152f51e7362817bdeba326b7840092418d5a64e85fb851c51a91f5fd156ed3e`
to `1eab6eb54fe5c23d53ca72a6d9dfcbbff09c09ffaf26c48a4f450f5068a8d313`.
Do not use old
selector source/MIR/CFG numbers as C4 admission evidence.

The current phase card separately pins the strict-lifetime kernel at
`37ed2550…`; keep it and the effective strict-lifetime `src/verifast.ml`
unchanged. The historical selector tail is translator-only. The R3 ghost-scope
patch and strict-cut translation both edit `translate_body`'s ghost-statement
handling, so that part needs a reviewed port/merge; applying the old patch
verbatim is not justified by its old context.

The ManuallyDrop candidate `bf63b7dff2e053eea8541996d856fac4be11f6f1` changes
the translator call-lowering helper and successor inventory: it adds an
exact-name identity flag for `ManuallyDrop::<T>::new`, then omits the synthetic
unwind target only when that identity result is emitted with a normal goto.
Historical cleanup projection also modifies the same `targets @ unwind_targets`
decision, adding its own narrowly checked false-unwind predicate. Preserve the
existing MDnew flag and merge the two predicates once; do not widen either
predicate. The current std selector uses `MaybeUninit`, so MDnew is a retained
regression, not selector proof input.

Review `a06d3a90` records independent review as nonblocking and Linux `make test`
as PASS (663.71 s, zero failed processes), while the external Cloud status
remained FAILURE from the obsolete collector. The exact publication packet is
still `READY_FOR_USER_APPROVAL`; no upstream publication or user approval is
recorded. No claim about candidate acceptance follows here.
