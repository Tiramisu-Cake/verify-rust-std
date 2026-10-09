# R3 input relation and shadow binding: design only

R2 reaches the outer return, then cannot establish the unchanged normal
postcondition relating the pointer result to the original `true_val` and
`false_val` parameters. This is a missing pure relation, not permission to
change the postcondition or assume wrapper ownership. The nine-command R3
source diagnostic saves both inputs before Rust shadowing, checks both opened
payloads, both current wrapper values, both shadow wrapper values, and the
conditional wrapper value. Its first Cloud action is source/MIR/refinement
capture only. No R3 admission pins or proof verdict exist yet.

The pinned VeriFast 26.10 translator at commit
`f76012fb518703b1d98e243ac4f487f16877cfcb` constructs variable names in
`vf_mir_translator.ml` `make_var_id_name_maps` (around line 4575). The first
debug name keeps its surface spelling; a later duplicate receives `_1`.
Its own comment says ghost statements are not yet rewritten to these internal
names. `translate_local_decl_id_` (around line 1972) applies the map only to
translated MIR locals. The R2 decoded outer MIR has parameter `true_val`/`false_val`
at `_2`/`_3`, then Rust shadow wrappers with the same debug names at `_4`/`_6`.
The final intrinsic copies `_4`/`_6` into its arguments before A1 moves its
selected wrapper into the result. A late ghost spelling `true_val` can still
name the original pointer parameter, not the wrapper. This predicts a type or
lookup refusal for R3's late `MaybeUninit::inner(true_val)` and its false-side
and conditional counterparts; the exact first refusal requires Cloud proof.

The least invasive candidate is a **separate source-only revision** after the
fresh nine-command capture: keep all nine commands and their ordering, but
refer to the observed internal shadow names in only the three late
shadow-wrapper checks (`true_val_1` and `false_val_1` in R2). Early saved-input
bindings must continue to refer to the unsuffixed
parameters. Before using the revision, certify the exact decoded debug-order
map, local types, source spans, storage lifetimes, final-call operands and
generated names in both NORMAL and readonly MIR. Capture a new exact verified
source hash, unchanged ghost-stripped runtime source, full MIR/refinement,
unit/body snapshots and ghost metadata. Test both positive lookup and
same-source negative mutations that exchange original/shadow bindings or
move a check before the declaration. Failure to resolve the generated name
is setup evidence, not a failed pointer relation.

The separate draft preparer `prepare-wrapper-input-relation-shadow.py` is
layered on `prepare-wrapper-input-relation.py` and refuses before writing while
`O26-WRAPPER-INPUT-RELATION-SHADOW-DRAFT.json` has its current BLOCKED status.
After a reviewed fresh parent capture, that manifest may record the observed
parent source SHA and NORMAL/readonly internal shadow names. The preparer then
changes exactly the three late comments, records all nine resulting comment
spans and three regions, checks byte-for-byte reversibility to the captured
R3 source, and requires the same ghost-stripped runtime bytes. This is a
source generator only: it does not admit MIR, install a verifier rule, or run
a proof. R2 and the frozen first twenty components are untouched, and the
revised R3 source needs new capture and its own default-off profile.

If direct use of generated names is unsupported, a narrowly scoped frontend
rewrite could map the selected ghost AST references to the exact shadow
locals, while leaving function contracts and other bodies untouched. That
would change trusted frontend semantics. It requires a separate decision,
written trust/admissibility review, exact source/MIR gate and regression
negatives before implementation. Alpha-renaming the Rust runtime locals would
break the byte-exact actual-source obligation and is outside this profile.

R3 proof gates, after fresh capture and an explicitly reviewed profile, are:
old exact-source certificates refuse the changed source; source/unit/body
pins and ghost-call CFG are observed rather than predicted; component 17,
SAFE-forget, A1 and name-resolution negatives reach their intended checks;
the unchanged constructor, `as_mut_ptr`, pointer-drop, wrapper-select and
assume-init contracts imply each pure link without added ownership; all
same-version callees, the nested Drop, both normal/unwind paths, leak/dead,
validity and refinement checks remain active. The first payload equality,
current-wrapper equality, shadow-wrapper lookup, conditional equality and
unchanged function post are distinct possible first blockers. Reaching one
does not establish the later ones. The two-current-wrapper `some(input)`
assertions are a pointer-specialized diagnostic only: generic dropping the
unselected value can leave its storage uninitialized. No result here proves
generic `T`, a ZST case, or actual `sort4_stable`.

The admission patch point is a **new** profile derived from R2's exact-source
and ordered-ghost guard (its component-23 patch around source inventory),
typed ghost-call/cleanup graph checks, and wrapper call-site checks. It must
read the newly captured complete NORMAL and readonly records and all nine
body snapshots, retain the original full body/callee set and posts, and pin
the newly observed source, unit, body-7 and translated-tool identities.
No count, local ID, block ID or SHA from R2 is reused as an R3 prediction.
Keep the production translator/kernel/parser/spec/binaries and R2 profile
unchanged. In the isolated Cloud checkout, build the newly admitted translator
from its own committed patch, compare whole effective specs, tracked source,
all five binaries and runtime source before/after, then run the complete
verifier with both normal and cleanup paths. The old R2 certificate must
reject the new source; independent stale-source, changed-body/ghost-order,
and swapped original/shadow debug-name controls must refuse at their exact
admission or lookup gates. A refusal at setup or an earlier unrelated callee
is inconclusive. The new profile stays default-off and unaccepted until
those controls and actual proof logs have been reviewed.
