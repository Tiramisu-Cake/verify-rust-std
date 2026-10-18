# Решение владельца: точный CURRENT recovery admission

Статус: APPROVED BY OWNER2026-10-18T20:02Z; implementation/review may proceed in existing window. Proposal below preserved. Независимый Luna High source review:
proof-only correction не помещается в действующий validator; требуется отдельное
разрешение изменить exact marker AST admission. Kernel/model/layout/prelude,
HRTB rules, unwind routing, runtime, posts остаются прежними.

## Установленное основание

Build `b4c78447-2c45-4548-98e9-18d00bf86132`, proof=infra251a83adc4eadcd6a1e3eb87e795124596e228c2,
tool2a5078681bf9b750d2fedb2223666df2f9baaeea, profile566457f4….
Brief+Reader index schema v6/Processor0.7.0 linked by receipt SHA.
Both prefix/fullbody: exporter/decode/refinement0,VF1; source exact, HRTB,
official-first-Continue, local-Continue and actual-first-call flagsTrue. Error:
`general.rsspec(149,51-52): No matching heap chunks: own(uint64_t_typeid)(t, head(take(1, drop(1, xs))))`.
Relevant sanitized context: fullbody verifier log SHA7283a98611c640d4c252885e7772d44b138688e85c91fba10aedc6512d4aba3a,
lines702–705 (last checked recovery statement at verified188:298–303).
Whole Build causal_status remainsUNKNOWN; normal false/true/panic unproved.
[R1-BUILD2-RESULT](R1-BUILD2-RESULT-20261018.json).

Pinned `bin/rust/rust_belt/general.rsspec:198–204`: open_full_borrow_content
returns `*l |-> ?v &*& (<T>.own)(t,v)`. The value is CURRENT, not the entry value.
Existing recovery closes own/foreach/array using entryxs. No entry/current
equality is supplied by that lemma. Creating duplicate u64 owners from their
empty representation would not establish the physical cell/array value equality
and would violate the intended provenance discipline.

Pinned `bin/rust/list.rsspec:188` provides checked `foreach_append(xs,ys)`;
`foreach_join` has no declaration in the pinned tool tree, though the old
recovery/validator require it. This is a later source defect, not a claim that
its call was reached in Build2.

## Exact proposed checked annotation sequence

Keep first_callback_close and scope-end markers unchanged. Replace ONLY recovery
body with the following ordinary checked commands (18, vs old16):

```text
assert lifetime_token(cmp_k);
end_lifetime(cmp_k);
borrow_end(cmp_k, <u64>.full_borrow_content(t, tail));
open_full_borrow_content::<u64>(t, tail);
assert *tail |-> ?current_tail;
borrow_end(cmp_k, <u64>.full_borrow_content(t, sift));
open_full_borrow_content::<u64>(t, sift);
assert *sift |-> ?current_sift;
close own::<u64>(t)(current_sift);
close own::<u64>(t)(current_tail);
close foreach(cons(current_sift, nil), own::<u64>(t));
close foreach(cons(current_tail, nil), own::<u64>(t));
close array::<u64>(sift, 1, cons(current_sift, nil));
close array::<u64>(tail, 1, cons(current_tail, nil));
array_join::<u64>(begin + 1);
array_join::<u64>(begin);
foreach_append(cons(current_sift, nil), cons(current_tail, nil));
foreach_append(take(1, xs), append(cons(current_sift, nil), cons(current_tail, nil)));
```

This is a reviewable syntax proposal, not locally extracted/generated proof
source and not yet a compiled/admitted/proved candidate. Exact parser AST and
any list-length facts must be checked before implementation/preflight. The
framed first cell remains take(1,xs); suffix becomes CURRENT sift/tail. Existing
array joins produce the matching current list. Each returned physical cell and
owner is consumed once; no old-value equality, assume/leak, extraowner or post
weakening is permitted. F/thread/type/lifetime/frame recovery stays intact.

## Required authorization and gates

Translator recover_shape currently requires exactly16commands and oldxs terms
(vf_mir_translator.ml first recovery marker validator). The proposal needs a
strict exact AST whitelist for these18ordinary proof commands, including exact
pointer/binder identity, u64 types and order; unknown expressions or mismatched
fresh value binders must fail closed. This changes trusted admission, even with
no new permission-producing rule or CFG transformation. Current task3 freezes
trusted translator semantics and requires an owner decision for new AST rules;
therefore no code/patch/pin change for this proposal has been made.

Requested narrow decision: authorize only this CURRENT value-binding/rejoin
admission correction under the existing first-comparator semantic card, with a
new tool/profile/patch/source identity and independent Luna High review. No new
HRTB/unwind/kernel/layout mechanism or proof-contract change. Existing lifetime
scope checks and first Continue/late Cleanup separation remain byte-identical.

Before any next Build: exact parser/source review; closed binder/shape rejection
tests and source-only patch/pin closure; fresh full B1/helper/smoke/admission/
default-off/receiver/end/retirement gates; exact prefix and unchanged-post fullbody;
CURRENT false/true/panic; four resource negatives, first-unwind mutant, HRTB/binder
and late-Cleanup controls at their intended checks. Lost-cell-owner control stays
after the reconstructed current array and must fail on the missing physical cell,
not an earlier setup/protocol error. No standalone reporting-only rerun.

This proposal grants no proof credit, does not closeB2, and does not authorize
another Build by itself. Existing R1 main cutoff21:04:30Z and absolute21:34:30Z
are not extended by awaiting this decision.

Owner reply: «Разрешаю эту узкую правку и review в текущем окне». Deadlines unchanged.
