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

## First minimal-profile result

[37441463201](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37441463201)
checked `d198907e7eec57f8bcd880304fa1345b97b0ef53`, 90min. Full logs/artifacts
inspected. Exact one-translator-file source audit, unchanged parser/prelude,
patch/output pins, paired Z3 and source byte/hash checks pass. Console SHA-256
`b1012430ca97595b5ee70e5e16778d2b7f008897dba2e910b953d3e4034ebaf6`,
build0/14.75s,RSS426,796KiB. All7readonly exporter/decode0; all7VF1 before any
caller because the common new recover_single helper fails its first close of
[first_fraction]ref_initialized(tmp_ref). Its wrapper contains two fractions
of the same precise predicate; exact fractional bookkeeping must be corrected.
The independently checked recover_pair still has18 body records; caller/call
counts0 for all cases, and strict negative classifiers reject this unrelated
failure. No new lifecycle proof or intended negative is claimed.

Six refinements pass; the positive MD case separately fails because the pinned
refiner does not support RawPtr (addr_of(tmp)), although its command dump shows
the same original/verified operation. This failure is retained. The readonly
MIR audit passes new1/deref1/read2/write1/into_inner0. VF.08s percase, refinement
.04s (.05generic), runner1:22.18,RSS585,528KiB; cold setup/build dominate.
No covers/loopbounds. Next fix same-reference recovery and use a sound,
independently checked original-provenance pointer route; all full posts remain.

## Resumed prepared-phase conclusion

The phase is closed, NO-GO for actual insert_tail integration. See
[feasibility report](PREPARED-PHASE-2026-10-06.md) and [STATUS](STATUS.md).
Run37448257248, source f0f417c, same frozen minimal profile: actual recover_single
conditional body passes16records/return/leak-check with isolated same-reference
accesses. All5 independent baseline controls pass. Both MD callers instead fail
close_full_borrow_content<T>(t,&tmp) before actual reference/helper call: immutable
local tmp has half points_to, callee needs full points_to. Positive RawPtr
refinement still fails; missing-init negative is NOT reached, no lifecycle gate.
Run37448682524 on the same source with UNCHANGED release26.09 separately passes
all5 controls and all export/decode/refinement checks. Draft remains unapplied;
no mutable tmp, post weakening, pointer substitution or tool extension was used.
