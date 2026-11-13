# E2 controls

All six existing immutable singleton `.expected` files are unchanged. Legal requires SUCCESS; hole requires intended uninitialized-byte read only. No expected is changed to accept an early transmute failure or a legal falseFAIL.

- immutable-static-legal/hole: unchanged sources. Required source mask [true,true,true] / [true,false,true]; hole at static offset 1. Legal compares SOURCE against identically initialized promoted storage, also exercising possible alloc_map coalescing. Both operand checks must succeed in legal; hole failure must bind only to SOURCE's None byte.
- immutable-subrange-legal/hole: four-byte parent, runtime reference at offset 1, extent 3. Hole only at parent byte 3. No whole-parent runtime reference added; right operand all initialized.
- immutable-relocation-legal/hole: three pointer-sized slots; initialized slot 0 retains relocation, hole only in slot 1; slot 2 initialized in both. No invalid &u8 is formed for the hole: it is MaybeUninit::uninit().

M1 anonymous admission, mutable-copy/reset controls, ordinary/PFC controls, eight strong oracles, cycle fail-closed, typed-data/padding controls and X1 changes retain C0 identities. They are coordinator CI controls, not locally executed evidence. Subrange/relocation legal may now expose a conservative uninitialized falseFAIL because their admission remains excluded; such a result is a release limitation, and does not qualify the hole.
