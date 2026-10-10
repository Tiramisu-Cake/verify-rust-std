# Fresh C3 correspondence review — bdef4a7c

**Verdict: conditional GO for designing an exact C3-prefix projection after the
selected split/inverse-join helpers are proved at this source version.** This
fresh capture itself is only `NOT_RUN`: it gives no C3 proof credit, admits no
bound profile, and does not establish an actual `sort4_stable` callable
summary. Review was read-only; no compiler, extractor, verifier, or proof was
run here.

The pinned annotated source is `087123b12072a19b0490260e509ce6773c1ed3dce0ed7c14c95991fdaf82996e`;
its ghost-stripped runtime is byte-identical to the original source
`3602050e45025745d80b308802be9e552310959abcee4b95bfe8c24f8ca04b72`. The
captured full pre-AST is `7dbc4ed84339a7a5f3056239d8ef67b9dc0cb7657f6d2cb2d954435ce462f35b`.
Normal MIR is 112 blocks/194 locals (full record SHA-256
`7582215b1e9ce56566272924c018ca31a07ad9414ea5a6f7f6dc4ccee784f101`); readonly
MIR is 28 blocks/110 locals (full record SHA-256
`9622479f50f0cafabf08523b5ea71ca46c1dd5a09c3b3fe95a287b4652e36b59`). Both
full records contain the target, complete local declarations, and basic
blocks. The five `FnMut::call_mut` calls, eight `select_unpredictable` calls,
and four `copy_nonoverlapping` calls remain present in the full runtime MIR.

The C3 runtime call at source line 447 is `is_less(&*c, &*a)` with the original
`F: FnMut(&T, &T) -> bool` shape. Normal MIR BB88 calls `FnMut::call_mut` with
receiver `_124` and tuple `_125`; that tuple is ordered from the reference to
`_87` (`c`, declared by the source expression at line 406) and then `_78`
(`a`, line 404). Its return is `_123: bool`. BB88 has `unwindAction =
(continue = void)` and normal target BB89. The earlier C1 and C2 calls are BB23
→ BB24 and BB53 → BB54 with the same direct-Continue unwind action. No cleanup
blocks exist in this capture. Thus neither earlier unwind has a CFG edge into
C3, and C3 unwind does not enter the C4 suffix. The source C3 unwind marker
must still recover `(c,a)`, join all four cells, and flow to the unchanged
original unwind post and leak checks.

The local mapping differs materially from the older `_98.._103` note:

| Source span | Fresh normal-MIR locals | Meaning for a C3 cut |
| --- | --- | --- |
| lines 417–441 | `_98.._122`, all unit tuples | Ghost-command results in the C3 setup; these are not callback temporaries. |
| line 447 | `_123` bool; `_124` receiver; `_125` tuple; `_126,_127` first-reference pair; `_128,_129` second-reference pair | Keep `_123` outside the strict callback scope as the C3 result. The six `_124.._129` callback argument/receiver temporaries are the ones whose source-derived live/dead boundaries must be moved together. |
| lines 448–451 | `_130.._133`, all unit tuples | C3 normal close, lifetime end, CURRENT pair recovery, and selected four-cell join; retain in the C3 prefix. |
| lines 452–456 | C4 callback `_134.._140`, pointer/select locals `_141.._162` | Future suffix; do not let these declarations or allocation effects enter the C3 projection. |
| lines 459–467 | C5 callback `_163.._169`, pointer/select and copy locals `_170.._193` | Future suffix; omit from the C3 projection. |

MIR places `StorageLive(_124.._129)` in BB88. In normal target BB89 it ends
`_126`, `_128`, `_125`, `_124`, `_129`, and `_127`; `_123` remains live to the
later source use and is only dead at function exit. A strict sibling scope
must therefore contain exactly the callback temporaries, while retaining the
bool result and `a`, `b`, `c`, `d`, `c1`, and `c2` outside it. The previous
`SEMANTIC-CARD.md` statement that `_98.._103` are the C3 callback temporaries
is stale and must be corrected before pinning a bound profile. The fresh
pre-AST must also be mapped against this inventory: MIR spans alone do not
prove AST declaration/allocation/free behavior.

The runtime pointer expressions are source-linked and remain unchanged:
`a = v_base.add(c1 as usize)`, `b = v_base.add(!c1 as usize)`,
`c = v_base.add(2 + c2 as usize)`, and
`d = v_base.add(2 + (!c2 as usize))` (lines 404–407). The new
`selected_four_limits(v_base,c1,c2)` ghost call is before these `.add`s (line
403), so its bounds facts are available at the pointer-arithmetic VCs. In all
four Boolean cases the selected `(c,a)` indices are respectively `(2,0)`,
`(3,0)`, `(2,1)`, `(3,1)`; the complementary `(b,d)` indices are `(1,3)`,
`(1,2)`, `(0,3)`, `(0,2)`. Each half is disjoint and all indices are in 0..3.
The argument for permission must remain the array/`foreach` split and the
resulting individual points-to plus `own` resources; address arithmetic or
numeric pointer equality alone cannot manufacture ownership. Recover fresh
CURRENT values at `(c,a)` after each callback outcome, then case-split the
inverse join to restore physical order. Do not substitute C2 entry snapshots
for callback-current values or add purity/Copy/Freeze premises.

The helper candidate is source-shaped in its current design: `split_selected_four`
starts from `base[..4]` plus `foreach`, splits real ownership, and branches on
both booleans; `join_selected_four` reorders those same resources by cases
before invoking the existing index-order join. Required proof work remains:
prove the bounds helper before relying on source `.add`, prove all four
selected points-to/`own` cases and the inverse CURRENT join, and validate the
source cast/precedence correspondence in each case. The existing post-setup
`interior_pointer_limits` annotations are redundant after the new pre-setup
limits call, but do not change runtime behavior. No C3 helper VC has been
checked by this review.

The capture result records `FRESH_C3_SOURCE_MIR_PREAST_CAPTURED_REFUSED_NOT_PROOF`,
`accepted=false`, `proof_credit=false`, and `target_proof=NOT_RUN`; the refusal
is the intentional `FULL_ORIGINAL_AST_CAPTURED_NOT_PROOF`. Refinement exited
zero only as the source/runtime correspondence check. The default-off C2 replay
exited zero, and the mandatory unbound-C2 control refused as intended with
exit 2; neither is C3 proof evidence.

The saved C2-bound and C3-capture snapshots have the same repository HEAD
`f76012fb518703b1d98e243ac4f487f16877cfcb`. Their only differences are the
intended C3 translator hash and the rebuilt `bin/verifast`; all other critical
files, all non-VeriFast binaries, all effective RSSpecs, and proof-std inputs
match exactly. This supports the frozen non-translator boundary for this
capture; it does not itself admit the next transformed profile.

Before any bound C3 admission, correct the stale local map, map the fresh
pre-AST declarations and object allocation/free effects, and pin this source,
both complete MIR records, and pre-AST. Separately prove the helper lemmas at
this exact source version. Then the C3 cut may be reviewed as a prefix through
line 451 with original full normal/unwind posts, unit return, leak and dead-code
checks preserved. C3 normal/unwind missing-close and omitted-join controls must
fail at the intended debt/recovery or four-owner post; reachable false-post
controls must fail at their respective post. Capture and helper success alone
do not establish those results.

## Exact bound-delta review

The new bound profile pins this exact capture: source, pre-AST, and both full
MIR hashes above; `normal_mir_blocks=112`, `normal_mir_locals=194`,
`readonly_mir_blocks=28`, and `readonly_mir_locals=110`. It remains
`profile_accepted=false`, `actual_sort4_callable_summary=false`, and
`bounded_fnmut_calls=3` of the original five. The patch is incremental from the
capture translator `c7692ab6f4f70ad12a0f3bea886834bd072667ed4dc5ba6a314607f5b8b38a76`,
patch SHA-256 `d6165630a3a7e4452be49849557df2790368fd62773424c939fe98d0aec9177d`,
and pinned output `d2f132148d409eb9a9e27afd24603d992405ec1984849817da9e427ab070db6e`.
It edits only the existing translator file. Its opt-in defaults off, rejects
conflicting C1/C2/C3 modes, checks exact source and full pre-AST hashes plus
complete MIR/AST counts, consumes the parsed `cmp3` declaration once, and
requires ordered cuts `'cmp`, `'cmp2`, `'cmp3`.

I matched the pinned AST indices against the captured formatter output. The
original function has 198 body statements; the original single C1 block is
root 195 with 196 statements. The prefix guards match `c1`/`c2`/`c3` at roots
23/59/120, `a`/`b`/`c`/`d` at 75/79/84/89, and the C3 named binding, unwind
marker, call, end-binding, recovery, and join at source lines 417–451. The
callback declaration slices contain 8/10/6 locals respectively: C1 `$_27..$_34`, C2
`$_63..$_72`, C3 `$_124..$_129`; the live bool results `c1`, `c2`, and `c3`
stay in the outer declaration list. The two omitted future-call slices match
C4 `$_135..$_140` and C5 `$_164..$_169`; the fresh AST confirms those names at
the pinned declaration indices. This corrects the older card's stale C3
`_98.._103` mapping.

The transformation places each callback's argument/receiver locals in its own
sibling block, registers `FnOnce::Output = bool` at the call, and retains each
normal close and strict cut. The C3 unwind edge goes to a distinct epilogue
that closes debt, recovers `(c,a)`, rejoins the four CURRENT owners, and then
returns through the original unwind contract. The source body retained inside
the normal wrapper ends after C3 recovery/join, before C4. Its original
contract is carried through unchanged in the ordinary candidate; the
`normal-false-post` control deliberately mutates only the returning outcome.
The C1/C2/C3 false-assert controls are placed on their corresponding unwind
epilogues. The eight listed proof controls are reachable-path negatives; their
first VCs still need raw-result review.

Only callback temporaries are hoisted as closed strict-scope locals. The other
future source variables and pointer/select temporaries remain as their original
uninitialized declarations, while the statements that initialize/use them
after C3 are removed from the projected body. This keeps `c3` and `a,b,c,d`
outer as required and adds no initialized future value or pointer permission.
The bound result field `allocation_review` appropriately remains pending until
the Cloud positive's transformed AST and full leak/dead-code diagnostics are
inspected: static pre-AST correspondence does not prove verifier object
allocation/free behavior.

**Independent decision: conditional GO for the first bounded C3 Cloud
diagnostic** under this pinned profile and assigned lane. Preconditions are
that `selected_four_limits`, `split_selected_four`, and `join_selected_four`
are included before `sort4_stable` and verified before the target; any helper
failure is a blocker, never C3 success. Preserve the unchanged original normal
and unwind posts, unit return, leak checks, and all admissible bool cases. Keep
the source-mutant refusal and all C1/C2 defaults/unbound refusals. A positive
candidate needs zero errors and dead-code findings, three comparator output
registrations, helper-before-target evidence, full post/leak checks, and raw
review of the normal/unwind controls before any C3 credit. A changed pin or
unmapped local/allocation effect is NO-GO until re-reviewed.
