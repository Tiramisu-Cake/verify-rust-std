# Actual nine-body guard shadow checkpoint (O26 → O27)

O26 entered the actual `select_unpredictable` body after the exact nine-body
admission, checked prefix callees, and safety prototype. The first actual-body
error at `verified/lib.rs:198` was a type mismatch at the first nominal owner
close: ghost `guard` had type `**Element`, while
`<select_unpredictable::DropOnPanic<*Element>>.own` expects the nominal guard
value. O24 MIR records the first pointer-valued `guard` as `_16` (source 188)
and the later Rust guard aggregate as `_24` (source 195). The error occurs
before VeriFast can check whether the selected cell and raw-pointer owner
actually suffice to close the predicate.

The source-only O27 candidate passes `owner_literal=True` through
`prepare-actual-owner-projection.py` → `prepare-actual-owner-linked.py` →
`prepare-actual-nested-drop.py` → `overnight-assume-actual/prepare.py`. It
replaces exactly the two conditional close arguments with the logical value
`select_unpredictable::DropOnPanic::<*Element> { inner: guard }`, where the
inner `guard` still denotes the first pointer. Both branches retain the same
`raw_ptr_own` close and the same nominal predicate. The post-forget open uses
the existing `saved_guard` witness and is unchanged. The five-body preparer
defaults to the historical source. Static inspection shows that the nine-body
preparer copies the entire actual helper suffix from the seven-body source,
and ghost stripping is checked at each preparation layer. `git diff --check`
passes. The new expression's VeriFast parsing and resource proof remain
unverified; no local executable check was run.

O27 dispatch created run37764722707, which failed before runner allocation
without steps, logs or artifacts. The subsequent source-only O27b dispatch
from 847bd01709d4a1269ff02ef63a436dd8cacf67c2 was rejected with
`HTTP 422: Actions has been disabled for this user`; no O27b run was created.
Thus neither attempt produced source, MIR, refinement or proof evidence. The O24/O26 nine-body certificate
must **not** admit the changed source. On runner recovery, capture the fresh
NORMAL and readonly exports and refinement of the exact new verified/original
pair, plus all nine complete decoded body snapshots and the complete decoded
unit with `Marshal.No_sharing`. Review their structural inventories before
updating patch17's nine-only verified source SHA, complete unit SHA, affected
body SHA values, exact reconstructed `owner` ghost block, and raw ghost
terminator list. Component20 independently pins the verified source SHA and
requires a corresponding reviewed refresh; changing component17 alone is
insufficient. Keep both historical patches and distinguish each new component. Preserve the original source pin if the fresh ghost-strip
equality confirms it; do not guess any fingerprint or relax its gate. Repeat
the source and typed-MIR admission mutants at the changed gate, then run full
proof with normal, unwind, return, leak, dead-code, and refinement checks.

The next substantive obligation, if the logical aggregate typechecks, is
closing the truthful nominal guard owner from the selected initialized slot
and its pointer-value owner while retaining the unselected slot for the real
drop. A typechecked close alone does not establish the later SAFE forget,
`assume_init`, full selected-pointer post, or generic/ZST contract.
