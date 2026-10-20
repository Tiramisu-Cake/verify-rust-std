# R8 independent obligation investigation

Read-only Luna HIGH investigation at exact tool47b80fad, no compiler/proof.
Prefix remains OPEN: exporter erases compiler PointerCoercion subtype to unit;
array3→slice needs exact Unsize discriminator, certified body/span/assignment/
local lifetime, length3 metadata and checked physical/borrow bridge. Existing
CastExpr sized-source Upcast is identity and retains metadata_none; lifetime-only
ascription does not establish the slice representation.

Minimal frontend scope: exporter lib.rs cast encoder; vf_mir.capnp CastKind;
generated decoder; translator translate_statement/translate_rvalue and exact
b2_three_from_local lhs_4/move_5/no-projection gate. Unknown subtype and all
mismatches fail closed. Checked bridge candidates: Array_to_array<u64,3>, existing
array/foreach, slice_full_borrow_content and slice_from_raw_parts_mut metadata.
Raw pointer construction alone gives no reference ownership or loan authority.

Model boundary: translate_array_ty currently rejects static-array FBC;
raw slice pointer FBC also unsupported. Before implementing a broad typeinterp
change, isolate a verifier-checked exact physical u64;3 bridge and live borrow
return on normal/unwind. If no such checked bridge exists, explicitly identify
needed model decision; never assume it. No new memory/alias/layout model,
static lifetime fallback, blanket PointerCoercion or numeric equality ownership.

BeforeLive remains INCONCLUSIVE: existing ghost address before source binding
fails unbound-local, not physical heap refusal. LocalAddrTaken is not liveness;
Rocq consumer ignores StorageLive/Dead. Relabeling an after-StorageLive uninitialized
case would not close before-StorageLive obligation. No profile qualification or
owner/Rocq credit from this investigation. Primary R8 late-rejoin target proceeds.

Read-only cleanup placement follow-up (candidate5 pending): normal source suffix
is bypassed by FnMut panic -> original Cleanup Drop -> Resume. Existing late
recovery remains before actual Drop. A future checked frontend marker must bind
the unique selected cleanup Drop by generatedbodykey/path/hash/guard, attach only
to its normal DropData.target before exacttmp retirement/Resume, retain cleanup
successors/Resume/on_unwind_ens and reject ambiguous target chains. Never attach
to Drop's own unwind_action. Existing selected_resume_targets only marks direct
UnwindResume locations for selected Drop unwind actions; it inserts no recovery.
Translator loci3402-3468/3544-3556/7198-7215/7323-7388, core return3113-3118.
No implementation, actual proof or credit from this design investigation.
