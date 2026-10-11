# Static source-bound pointer rule review — before Cloud submission

Reviewed 2026-10-11 by the primary agent and independent layout_review agent.
The slice method at slice/mod.rs:778 has the exact runtime cast sequence
`self as *mut [T] as *mut T`. The historical one-symbol patch adds only
`std::slice::<impl [T]>::as_mut_ptr` to the existing as_ptr typed-cast arm.
Its own patch hash is f200a5812149bb2278ded1d1ccb27a104b3dec3c03c5e40c79e30409d0d06916.

No ownership, provenance transfer, permissions, lifetime, array cells or alias
facts are created by this projection. Mutable receiver resources must be
retained and restored through native reference semantics. The MU-to-T pointer
cast is a separate operation and supplies no initialized T resource. Fresh
canonical native operations precede method consumers; source/MIR/body identities
and rejection controls remain admission requirements. The copied component
proves only its operations unless those source applicability checks also hold.

The historical whole O26 profile and unrelated MU method lowering are excluded.
The current ZST/C1/C4 base remains experimental/unaccepted. Original caller
overflow/abort obligations may stop verification before pointer uses and are
classified OPEN. No static review result upgrades proof or model acceptance.
