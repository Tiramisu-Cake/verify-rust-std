# Independent C2 discovery implementation review

Rationale was committed in C2-DISCOVERY-CARD before implementation. Main owner
implemented only the translator delta in the isolated absolute VeriFast worktree;
GPT-6 Sol independently inspected the complete delta and runner read-only.

Exact ECD83 annotated source SHA is checked before ghost parsing/AST output.
Explicit global/per-body opt-in requires one actual sort4 body, unwind/full checks,
strict lifetime cuts and prefix/output-equality disabled. Default-off code keeps
historical C1 behavior. Only the exact two ordered cut markers192/cmp and225/cmp2
are accepted. The complete original declaration is serialized before any scope
projection; every discovery execution then intentionally refuses. No callable
summary, verification success or kernel/memory change is produced.

Reviewer found no static unexpected proof path. Unix process linkage is a Cloud
compilation gate, not locally tested. Source hash protects fixed marker lines.
Fresh AST must be removed before capture, copied/hash-checked in the same call,
and source mutation must fail before AST/proof entry. The runner newline splice
bug was corrected and pure saved-byte test now exactly reproduces ECD83 with
runtime bytes unchanged. Full graph capture is support for subsequent raw review:
C2 ordered operands/Continue unwind correspondence remains UNREVIEWED until
inspected; constant graph inventory counts alone do not establish it.

The portable delta applies after C1 translator59048330; patchd9ac74e0 and resulting
translatorb33ca54a are fully pinned in C2-DISCOVERY-PROFILE. Both profiles remain
unaccepted. Cloud gates rebuild, frozen critical/spec/library checks, default-off
C1 prefix VF0, complete MIR/refinement capture, original AST inventory and exact
source-hash refusal. No new projection or C2 proof authorized by discovery output.
