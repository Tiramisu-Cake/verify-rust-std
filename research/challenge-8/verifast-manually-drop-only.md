# Minimal tracked ManuallyDrop reference profile

`manually_drop_only` builds pinned VeriFast 26.09 source commit
`809de4596839b739dd999f9e462242c835e3af46` with only the existing
[ManuallyDrop reference patch](verifast-manually-drop-ref.patch). The original
translator SHA-256 is
`7319d2638c3fc49a1663b50925d565ca2e10d95754933ed58e37f27239936803`,
the patch SHA-256 is
`5500204aadd0ea0a2996d63d064160185457b6d337782aa4300c11272ab450cc`,
and the statically applied translator SHA-256 is
`60ece6e90f4dd3c623a99ea31feebb3210359daa38850255332118b2316eac39`.
The builder rejects any source diff beyond
`src/rust_frontend/vf_mir_translator/vf_mir_translator.ml`, records the exact
patch and pre/post translator snapshots, and verifies that the parser and
prelude retain their pinned hashes. It preserves the hosted-only build recipe,
toolchain, exporter, refinement checker and verifier version.

The patch makes an exact immutable shared borrow of a raw `ManuallyDrop<T>`
place use the existing `create_ref` path rather than the baseline no-drop
shortcut. It does not provide `ref_precreated_token`, `ref_init_perm`,
`ref_initialized`, `T.own`, or any storage fraction. A proof must obtain these
through the real aliasing and generic sharing rules, then return its temporary
borrow before moving the value. The profile contains no tuple, HRTB,
lifetime-cut, address-taken, local-Drop, projection or verifier-kernel patch.
It is a feasibility control, not a proof of the insertion routine or its
panic cleanup. Hosted verification of this minimal combination is pending.
