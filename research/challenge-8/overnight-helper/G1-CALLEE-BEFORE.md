# G1c: independently callable generic forget body, before hosted run

The exact updated `core::mem::forget<T>` body is
`{ let _ = ManuallyDrop::new(t); }`. The O7/O11 framed positives inline this
body and do not provide a callable generic callee summary. Historical
standalone `checked_forget_generic<T>` executed its body/return/leak checks
but failed the mandatory dead-code gate on a synthetic unwind return.
The accepted 26.10 ManuallyDrop CFG repair supplies a new, falsifiable
reason to rerun **only the isolated callee**, without a caller whose own
synthetic `unwind=continue` could obscure its result.

The fresh fixture is a single public `unsafe fn checked_forget_generic<T>(t:T)`
with that exact body and no runtime arguments beyond `t`; its ghost contract
requires current `thread_token(tid)`, returns the same token, and has false
unwind. `T` has no Copy/Freeze/ownership bound. The source preparer pins the
whole updated `mem/mod.rs` and `manually_drop.rs`, the exact forget and
ManuallyDrop::new bodies, and ghost-stripped original/verified identity.
The hosted gate records complete NORMAL/readonly decoded MIR, refinement,
full VeriFast return/leak/dead-code outcomes and unchanged source hashes.
The source/MIR-to-Rust identity and destructor suppression are trusted; body
contract, token preservation and no-unwind are checked obligations.

The positive must exit zero after verifying the public callee. Controls
with a false post, lost token, duplicate token and contradictory precondition
must fail respectively at the named post, leak, post, and mandatory dead-code
obligations; a source/export/setup failure is inconclusive. The prior direct
body frame proof remains separate evidence. No SAFE `forget` call is
redirected by this experiment, no nominal guard is modeled, and the full
actual helper is not claimed. A later actual redirect needs a separately
reviewed source/typed-MIR certificate and an independently passing framed
call probe, with shared cleanup preserved.
