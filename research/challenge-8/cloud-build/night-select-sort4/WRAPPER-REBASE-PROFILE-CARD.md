# O26 wrapper rebase component 23 — draft Cloud profile

This lane is a bounded experiment after the fresh, unchanged O26 refresh
capture and full proof in the same Cloud Build. It uses the actual SmallSort
`select_unpredictable` source, with only the two recorded ghost insertions that
save the prior `MaybeUninit_pointer_own` wrappers before the first storage open
and reconstruct ownership of the current wrappers after the unselected guard
Drop and SAFE forget, before the final select comment. Runtime source and
generic signature must remain identical. The actual outer contract still
requires the thread token, returns exactly the condition-selected input
pointer with `raw_ptr_own<Element>(t, result)`, and has `on_unwind_ens false`.
The insertion supplies no new pointee permission; a fingerprint or an early
verifier error is not a proof of either normal or unwind obligations.

Hypothesis: component 23's exact new source/unit/body-7 pins permit the same
owner and A1 admission only for this wrapper-rebase source. Its old eight body
pins and existing six proof gates remain in force. If the new positive case
reaches a later proof obligation, that is evidence about the rebase, not
acceptance. If it refuses at the new pin or an earlier setup stage, inspect the
full logs and do not count it as a semantic negative.

The production component-20-plus-21/22 source and canonical proof are built and
captured first. A disposable copy receives only component 23; the exact
`SORT4_WRAPPER_REBASE_REPO_ROOT` and `SORT4_WRAPPER_REBASE_ADMISSION=1` pair
selects that profile. Both must be absent for the canonical proof. The profile
manifest must have observed Cloud source/unit/body-7 and translator hashes;
placeholder values prohibit the new profile run. The positive source requires
normal and readonly MIR export/decode, refinement, ten independently hashed
Marshal snapshots, an unchanged original source, and eight canonical body
snapshots identical to the same-build baseline. The new outer typed MIR must
have exactly 44 locals and 27 blocks; its two new ghost calls occupy blocks 8
and 20. The owner negative targets the actual forget in block 15,
`Move(_33)` and cleanup 26; the A1 negative targets `Move(_39)` in block 22.
These sites come from the exact manifest, not an assumed offset from the old
42-local/25-block graph. Full proof must verify the
actual same-version callees before the outer helper and preserve all normal
and unwind obligations.

After a pinned positive case, run only the four independent component-17 owner
controls and the component-20 A1 Move/Copy negative on the new source/profile.
Each must fail at its intended obligation with source, MIR, wrapper identity,
and mutation records intact. A separate component-23-off check must refuse the
new source at the canonical old pin. The component-23 binary with the opt-in
off must also repeat the original canonical source's first verifier refusal at
`lib.rsspec(462,47-48)`, with the earlier tool profile unchanged. Do not infer
control success from a positive proof.

Outcome classification is draft diagnostic only. `verification_accepted` stays
false until all source, profile, proof, same-version callee, owner and A1 gates
pass and are reviewed. This card authorizes no semantic extension beyond the
explicit component 23 patch and no local verifier execution.
