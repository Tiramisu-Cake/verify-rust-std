# Receiver resource ledger and falsifiable probe — 2026-10-11

Session: stable owner `merge`, worktree `/root/verify-rust-std-merge-origin`, branch
`merge/incoming-origin-20261009`, start checkpoint
`ce2bc9d67ce83b2439fb17177487b462267c36e1`. Start `08:17:34Z`, main deadline
`09:17:34Z`, finishing deadline `09:47:34Z` (11:17:34/12:17:34/12:47:34 MSK).
Fresh account 3600 Cloud seconds, no carryover; old ledger archived unchanged in
`archive/BUDGET-CLOSED-LEN1-COMPOSITION-20261011.json`. Policy revision read:
`c7ca8c467aecf10a4b53039372ee97714f854ee3`, local adoption
`1b9e3df3182d13e5adf7d2e5d04afcfbc1851f14`; current policy files match origin/main.
Frozen tool `df6b3fbfcf4192d6b442d13e35dafe8477a3fe6f`, effective base
`f76012fb518703b1d98e243ac4f487f16877cfcb` plus ordered ten patches and twelve
trusted file hashes in EFFECTIVE-SOURCE.json. Profile
`0b8cf55b0e7b5a1d0e0595b1483726459cb1d2f40264311e2014d3580ad189b8` remains
**NOT_ACCEPTED / NOT_FOR_INTEGRATION**. Domain concrete-u64/x86_64, len==1.
No trusted semantics, std source or runtime adapter change is authorized here.

## Required versus produced resources

| Item | Actual Drop requirement | Constructor/caller state | Existing rule / missing step |
| --- | --- | --- | --- |
| Thread | thread_token(_t), _t=currentThread | inherited caller token | conserved in old fresh caller |
| Receiver ownership | full CopyOnDrop_full_borrow_content(_t,self)() | full initialized src/dst/len fields, padding, nonempty own can be reclosed at physical guard g | canonical FBC definition folds fields+padding+own; old caller only opens a half FBC and conserves the rest |
| Payload | source quarter, full destination gap, CURRENT u64 owner, len1, separation | derived from actual tail.read and constructor; no standalone body entry assumption | own/FBC conversions and singleton array packaging previously checked |
| Local lifetime | lifetime_token(k) plus full_borrow(k,FBC(t,g)) if using reborrow | old source reference lifetime is distinct from a new guard borrow lifetime | begin_lifetime and borrow(k,P) can construct the package from P; do not reuse or invent tokens |
| Receiver origin | ref_origin(self)==self | physical alias guard_ptr==g only | ref_origin idempotence and numeric/address equality do not prove g is a fixedpoint |
| Return | full normal posts, CURRENT recovery, guard frame, return/free/leak | old checked helper returns effect and frame | not available through generic drop_in_place post |

Generated Drop contract: frozen translator `vf_mir_translator.ml:4585–4613`.
Actual std Drop body at smallsort.rs:295–307, dynamic copy at306;
actual read/constructor at550–551. Contract normal/unwind details remain those
in the existing source-bound cards; diagnostic below does not replace them.

## Rule applicability (including correction to the old review)

`bin/rust/aliasing.rsspec:55–58` create_ref_mut consumes *g|->v and returns
*result|->v plus opaque ref_mut_end_token(result,g). It does not return origin
fixedpoint. end_ref_mut:67–69 consumes that exact token and returned points-to,
restores *g|->v and proves no origin equality. Current Ref+Cast lowering creates
no such token, so neither assertion nor end_ref_mut is applicable on that path.

`rust_belt/lifetime_logic.rsspec:71–74,117–120` begin_lifetime/borrow can form a
keyed full borrow from the reclosed FBC. Thus absence of full_borrow in the old
fixture is NOT a fundamental inability to create that resource. open_full_borrow
and close_full_borrow:135–143 conserve the accessor token; end_lifetime and
borrow_end:122–125 recover original P after lifetime death. These nonghost-only
lemmas can be called in annotations of real functions, not arbitrary ghost lemmas.

`rust_belt/aliasing.rsspec:1–4` reborrow_ref_mut needs thread_token, full_borrow(k,
<T>.full_borrow_content(t,g)) and a positive lifetime token share; it returns FBC
at a result r with ref_origin(r)==r, but does NOT ensure r==g. The rule is a
regular function and cannot simply be called as a ghost lemma (verify_expr.ml:3137).
An arbitrary modeled result cannot be substituted for the actual method receiver.

Frozen translator:3241–3272 unconditionally uses AddressOf for mutable Ref;
3298–3300 reborrow/create branches are bypassed by that condition. Saved caller
AST155 binds reference=AddressOf(gap_guard), guard_ptr=AddressOf(Deref(reference)).
No creation call, returned reborrow receiver or token exists there. This is
source/AST binding evidence, not a new proof refusal.

## Probe before deciding impossibility

Hypothesis: the frozen rules do not prove ref_origin(guard_ptr)==guard_ptr from
the successfully derived physical frame. Add exactly that assertion after the
existing borrowed-field assertion and before the checked helper call. Preserve
all three old cases, including helper-positive, and both mandatory normal/unwind
smoke groups. No call or precondition changes. Expected first refusal must be
Cannot prove equality at this exact assertion after frame production, with
source/MIR/AST/refinement gates passing. Earlier setup/token/FBC/binding failure
is INCONCLUSIVE, not the desired receiver refusal. If the assertion passes,
record origin established for this fragment and reassess receiver/FBC handoff;
do not count an unexpected positive as an intended negative.

Diagnostic normal post remains thread_token(t), type_interp::<u64>(), initialized
*tail|->held and u64.own(t,held); caller unwind post remains thread token/type,
*tail|->unwound and owner. The probe is deliberately partial and proves no actual
method call, no compiler glue or panic cleanup. One build, timeout1200 + reserve60,
fits both main window and fresh budget. No repeat without a new causal hypothesis.

## Next source-bound edge if the probe refuses

Rust forbids explicit destructor calls (E0040); an invented `Drop::drop` runtime
edge is not a solution. Frozen Drop terminator:2917–2959 lowers to generic
std::ptr::drop_in_place(AddressOf(place)). std/lib.rsspec:597–600 consumes typed
storage+own and returns storage/thread only, with no CopyOnDrop CURRENT effect.
A real receiver and checked Drop-body dispatch/interface is required before
claiming a method call. Ask the VeriFast owner which existing source-bound rule
connects physical guard FBC to the receiver used for the actual method, or request
a separately reviewed semantic/interface proposal. No patch in this session.

## Effective-source citation qualification

Raw component checkout differs from the full effective profile; its earlier line
references above are navigation only. Reconstructed base+ordered10 patches with
reviewed Git/text-only source-replay.py in a disposable own directory; all12
expected effective hashes matched (PASS_TEXT_REPLAY_ONLY, no compiler/proof).
Effective translator citations: Drop terminator3097–3139; mutable Ref3433–3460
(the tracked-MD shared special case does not affect Mut); branch3486–3488;
generated Drop4810–4840; gen_drop_contract4737; generated FBC6169 onwards.
Unchanged aliasing/lifetime spec hashes in RECEIVER-RULE-BINDINGS-20261011.json
match the pinned base exactly. Source reconstruction is text evidence only.
