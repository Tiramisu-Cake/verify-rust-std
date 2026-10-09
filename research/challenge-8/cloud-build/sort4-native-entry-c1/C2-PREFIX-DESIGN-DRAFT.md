# Bounded two-comparator prefix — draft, NOT_RUN

This is a design note only; no projection implementation is admitted from it.
Prerequisite: fresh C2 complete source/MIR/original AST diagnostic, exact ordered
call operands and Continue unwind reviewed, and structural graph inventory.

Actual obligation: source-linked sort4 first two comparison prefixes conserve
CURRENT four T owners, current F cell/F.own/thread/type resources and untouched
optional destination, with original raw outcome posts and leak checks. Domain is
the existing exact raw pre (including positive T size), every normal/direct unwind
execution of c1, and, if c1 returns, every normal/direct unwind execution of c2.
Both bool values are retained; normal traces end only after second recovery/join,
before c3. No full sort4 summary/destination initialization/order/stability claim.

Falsifiable hypothesis: two separate strict local ghost lifetime scopes suffice
for the two callbacks when their compiler reference/tuple locals are moved into
precisely their own scopes, both debts close before exit and each unwind has its
own cleanup/recover/join/original return epilogue. First direct unwind skips c2;
second direct unwind occurs after complete first recovery. Every source/MIR call
operand and compiler Output=bool clause must match its own lifetime substitution;
opaque generic const is irrelevant to this raw body and no caller guard is assumed.

Proposed structure preserves all declarations, including future tuple allocations,
in original relative order except necessary certified callback lifetime relocation.
Keep each callback normal/direct unwind switch, exact close and strict exits,
all original pre-c1/prefix operations, original tail-return expression and posts.
Only normal suffix after second join is projected away. Recursively list labels/
gotos through all blocks/branches; reject unknown containers and every retained
edge into deleted suffix. No strict-dead-code exception or failing-node deletion.

Before implementation record exact whole original AST/source/full typed MIR hashes,
callback slices/declarations/two markers/outcome switches/node locations/edges.
Independent design and implementation review required in this authorized scope.
Cloud gates: prior C1/strict matrix, same-unit recovery/join helper completed proofs,
new two-call positive full VF0 with posts/return/leak and emitted exact changed AST,
both missing-debt and join/false-post controls, operand/marker/source admission
controls. A setup/translation/wrong-helper failure is not an intended negative.

Outcome: full bounded VF0 permits following actual blocker c3/selector in the
remaining main window; missing resource localizes current-owner or scope debt;
source/MIR/AST mismatch stops this projection and allows independent native entry
work. Trust/profile acceptance remains separate. No new experiment after23:52:33.

Independent GPT-6 Sol design review (read-only) requires before implementation:

- Reconstruct all four CURRENT owners/current F after c1 join; c2 lifetime and
  refs/fractions/debt are separate. C2 recovery3/2 frames owners0/1 and current F.
- Pin c2 ref/tuple locals, StorageLive/Dead/initializer/addressTaken/drop facts;
  preserve pre-boundary allocation effects, not merely empty locals_to_free.
- Original existential optional destination post is resource conservation only.
  A claim of exact destination value preservation additionally requires a checked
  assertion of the SAME destination_before list on both outcome boundaries.
- Pin both FnMut outcome switches and Output=bool substitutions, distinct unwind
  epilogue labels, all ingress/egress. C1 direct unwind enters no C2 local scope;
  c1/c2 bool assignments remain. Both exit post/leak/strict gates are mandatory.
