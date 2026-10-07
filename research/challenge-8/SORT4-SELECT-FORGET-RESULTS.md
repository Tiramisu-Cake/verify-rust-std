## Переходный checkpoint — Git sync, повторная приёмка НЕ ВЫПОЛНЕНА

2026-10-08. В этой ветке напрямую влит закреплённый upstream cd371e03.
[UPSTREAM-SYNC](UPSTREAM-SYNC.md) фиксирует parents/SHA, исходниковые изменения,
бюджеты и два следующих задания. CI budget этой фазы0; исследования отложены.
Старые принятые результаты ниже относятся только к прежним proof SHA/tool profiles.
Новым std/nightly/VF необходима повторная проверка. S7c UNACCEPTED (пять admission
контролей незавершены); G2/A/B и девять Rust projections сохраняют прежние условные
границы в исходных ветках. Бюджеты5306/5400(94) и512/1800(1288) не сброшены.
Git merge не доказывает actual helper/merge/Challenge. Подготовленные задания
НЕ разрешают их выполнение в этой CI0-фазе.

# S7c forget — CFG repair and standalone evidence

**The identical autonomous generic body now passes the full verifier, exit0,
on the experimental CFG profile. The profile is NOT ACCEPTED:** five mandatory
pointer-drop admission controls remain unverified. Actual-call linkage and redirect
were not implemented; actual helper/sort4 remain NOT PROVEN. Existing S6v4 and all
previous proof SHAs remain unchanged. No result is attributed to VeriFast26.10.

## Established cause and repair scope

[Diagnosis37681688627](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37681688627),
checked source `32d909a7b1015a9417b882676d349bab5c80481f`, first reproduces old
plainS6v4 fullVF1, then rebuilds only temporary observational instrumentation.
Both builds execute all seven predeclared bodies/returns/leak checks and reject
solely dead code; export/decode/refinement0 and exact source/MIR/AST identity hold.
Physical-loc side registry establishes residual **id52**, label2
`ReturnStmt(unwinding)`, loc3:1–16:2: REGISTER1, EXEC0, RESIDUAL1. Normal returning
ReturnStmt is distinctid53 and executes. Three declaration observationsid49
have the same printed function span but execute and are not residual. Table
comparison, registration/deletion and final result rules were not altered.

In pinned `vf_mir_translator.ml`, MD::new identity lowering returns FnCallResult;
its normal target creates assignment+Goto. Successor inventory nevertheless adds
unwind_targets. `find_blocks` follows that inventory and includes cleanup2, which
has no incoming generated statement: its synthetic return trips dead-code gate.
This is the observed cause, established before repair, not a missing ownership
resource or a proof of ManuallyDrop's trusted semantic correspondence.

[Overlay](verifast-manuallydrop-new-cfg.patch) is separate from unchangedS6v4:
profile `experimental-manuallydrop-new-cfg-v1`. A fresh per-call marker is set only
inside existing exact `std::mem::ManuallyDrop::<T>::new` identity lowering. Only
marker+FnCallResult+normalGoto use normal targets without unwind_targets. Other
calls/variants retain their old successors. Exported MIR including cleanup is
unchanged; existing graph traversal decides AST inclusion. No general AST pruning,
line exemptions, unwind/dead-code disabling or assumptions about arbitrary callees.

The broad FnCallResult successor question remains a separate future proposal,
requiring an inventory of existing lowerings and their generated transitions.
This iteration does not implement it. ManuallyDrop identity representation,
destructor suppression and no-unwind correspondence remain **TRUSTED**.

## Hosted acceptance and exact remaining gate

[Full acceptance37683136287](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37683136287)
checked `7185d8bae4a25fa2be278424fa9f5c6a80b93956`.
[Focused continuation37684590509](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37684590509)
checked `6b63670c21bfa57d2531c4be57ac098df6111c5f`, same tool overlay, repaired
separate-clause control syntax and generic shared-cleanup fixture. No temporary
trace patch is applied in either acceptance build: Ast/verify_expr/vfconsole source
diffs are empty. Exporter/refiner/spec/kernel/check modes are unchanged.

Autonomous unsafe adapter is exactly `{ let _ = ManuallyDrop::new(t); }` for
unrestricted by-value genericT. req current thread_token; ens same thread_token;
on_unwind_ens false. No Copy/Freeze/ownership restriction. Runtime source and ghost
contract matchS7b byte-for-byte. Both profiles are rebuilt sequentially and logged
separately; old plain fails and new plain passes on the same sources.

| Predeclared obligation/control | Observed outcome on new profile |
| --- | --- |
| Identical autonomous whole unit, no focus | FullVF0, all7 bodies executed, returns/leak checked, mandatory dead-code gate complete |
| NORMAL/readonly export+decode, refinement, source integrity | All5 exits0; runtime/contract hashes and complete MIR identical to old profile |
| Ordinary call to locally body-verified potentially-panicking bool callee | VF0, normal+unwind returns and leak checks; valid unwindContinue translated and checked |
| Generic MD::new(t), then potentially-panicking call | Both MIR calls target cleanup3; other predecessor keeps cleanup3 in AST; normal+unwind returns execute and leak check |
| False normal post on exact generic body | VF1 Cannot prove false at9:27–32 after body/return |
| False unwind post on ordinary caller | VF1 Cannot prove false at23:15–20; actual caller unwind return26:14–38 executes |
| Contradictory precondition, nonempty unchanged body | VF1 dead-code at function3:1–16:2, call15:13–33, operand15:31–32, return16:2; vacuous body is rejected |
| Constructor regression | 16 source/proof cases,9 MIR admission mutations,14 necessary baselines PASS |
| as_mut_ptr regression | 9 proof cases,17 admission controls PASS |
| Typed intrinsics regression | 16 proof cases,40 admission controls PASS |
| Narrow pointer drop proof regression | 2 positives+11 proof negatives PASS |
| Pointer drop admission | 8 source+9 MIR intended rejections PASS; remaining5 incomplete |

**Unverified mandatory remainder:** `mir_cfg_unwind` was interrupted before a
complete result; `mir_extra_operation`, `mir_contract`, `method_source_pin`,
`glue_source_pin` were not run. The interrupted driver has exit124 and no final
summary; it is not a negative PASS. Completed admission results use their exact
`admission-classification.json`, not an incidental lower-level diagnostic class.
No green workflow badge or positive standalone body completes this gate.

Three initial unwind fixtures in37683136287 failed parsing at ens4:1–4; scalar
shared fixture exported Continue rather than shared cleanup. These are preserved
failures, not intended negatives. Focused corrected fixtures test the actual
obligations above without a further tool/model change.

False-unwind strict classifier in focused artifacts already reports intended
negative/acceptedtrue. Aggregate summary remained INCONCLUSIVE because the driver
also required normal branch execution after failing false unwind post. Driver
correction limits that requirement to positives; saved evidence is immutable.
[Replay37685560355](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37685560355),
processor `7eea51399d570b0eba895605c5d05d0de9cf3ed1`, verifies pinned artifact,
manifest/source/stage identities, sole exact error and all8 executed functions;
writes a **separate** INTENDED_PROOF_REJECTION map. Correct obligation accepts;
wrongline/wrongpredicate/setupfailure/exit0/unknownfunction reject. All6 controls
PASS. Both original summaries remain byte-identical and keep INCONCLUSIVE. Replay
invokes no compiler/exporter/verifier and does not accept the profile.

## Immutable source/tool/evidence identities

| Identity | SHA256 or exact pin |
| --- | --- |
| VF source | `809de4596839b739dd999f9e462242c835e3af46` |
| Compiler | `nightly-2026-02-05` |
| Unchanged S6v4 patch | `c7cc08a995bac5879901f4fe08030f09d23bdfefb1a3ab5893be12a8dd1f8fc1` |
| New CFG overlay | `89b0d80bd1e6382a9bf5be2f1ed208bae6aac5e907a21dd782c4c22307578da7` |
| Effective translator | `89b76a1aca6b54205ed4ddb73b7a259de98ada360edf4b8b0bcc95bc7e18588d` |
| Unchanged effective std specification | `70f09d294ca708424e26c68df382038e13d487e6f1eb3d63fa84b0743628c76a` |
| Exact original autonomous source | `111334d30b9bd17b22d4ad52aa53572902ac055f8313f38503201a3fc281fe64` |
| Exact verified autonomous source | `7518b013a07c8fc42ed7f12fa88b519efa317e5e2e6c8816cc4664db3b69e99d` |
| Complete NORMAL/readonly MIR binary | `1bf0d97cc332cb5f921836f53ff1acb54540a3c87139911c528c6c5cc00654e7` |
| Complete NORMAL/readonly decoded MIR | `3b08b5835f03ff152e6dae68bbf4ce05d1491d7919124f06222794f844b8553d` |
| Old AST | `172fbc51f8592fbdad092a7f0abaa1895077d72c4dd60cd887b37fa9e196aecc` |
| New AST | `b0cd6860a420751ecee9a6632f23c7636c6d9415a360db33ca96e651f715089b` |
| Acceptance binary37683136287 | `e809097131bbd9eebd2468eaebdbeadab1e9455341c6849e99de18d282f346ac` |

Trace-only patch23d77777 and binary927e0892 are recorded separately; plain old
binary799fac74 is retained with diagnosis. Detailed environment inventories hold
full schema/exporter/refiner/dependency/flag/source hashes for each build.
Plain/traced old AST equality and old/new exported cleanup2 identity are checked;
new AST excludes only orphan unwind return for the autonomous body.

Compact/full artifact IDs: diagnosis11510235246/11509725710;
acceptance11510392179/11510152397; focused11510757595/11510870158;
replay11511500191. Compact manifests894/4605/1042 included entries were read and
verified for SHA256/size/ZIP CRC; separate logs preserve whole failures. Archive
hashes respectively1388580d,db0c15d5,26836bce. Replay artifact zipSHA
fd6c568c744937eb911ece7255d90d93ea422212a21f99754026c62a284318e6.
Replay's original aggregateSHA313675ae and false-unwindSHA11384c7d match the source
artifact bytes; original and separate classifications are not overwritten.

## Boundary and budget

4752 entry +132 diagnosis +283 acceptance +131 focused +8 replay =
**5306/5400 summed hosted job seconds used,94remain**, no reset; all executable
checks GitHub-hosted, one active direction at a time, no active run at checkpoint.
The 94s remainder has no established bound for rebuilding, completing the missing
admission tail and saving evidence; no repeat is dispatched. Profile UNACCEPTED.

Checked proof SHAs are32d909a7 (diagnosis),7185d8ba (full partial acceptance),
6b63670c (focused positive/controls). Processor7eea5139 is classifier replay only.
The final documentation HEAD is **not** a proof SHA or a26.10 result.

Actual still has the oldS6v4 forget63 nominal-guard-own failure at stdspec420.
No actual-call linkage/redirect, guard ownership, Drop, assume_init, memory model,
exporter, refiner or kernel extension. No safe generic forget summary; full actual
helper/sort4 not proven. Supplement authorizes only a source comparison and
[26.10 migration plan](VERIFAST-26.10-MIGRATION.md), without rebase/merge/profile
switch or new migration CI; old evidence and budget retain their exact pins.

## Historical S7b — standalone body and admission checkpoint

**The auxiliary body theorem is NOT ACCEPTED. Actual-call linkage is NOT ACCEPTED
and was not implemented. Actual helper did not advance in S7b.** The complete
standalone verifier exits1 at the mandatory dead-code gate after the reachable
body returns and passes leak-check. Existing S6v4 components remain accepted;
full helper and sort4 are NOT PROVEN.

## Standalone whole-unit experiment

[Run37675513854](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37675513854)
checked source `c9c59a85807da0135a8192b1912b15d510c68028`. Its minimal crate
contains only `unsafe checked_forget_generic<T>(t:T)` with the pinned body
`{ let _ = ManuallyDrop::new(t); }`. There is no surrounding select, surrogate
guard, isolation macro or focus. Generic T has no Copy/Freeze/own restriction.
The explicit reachable contract requires current thread_token, returns the same
token and requires false on unwind. SAFE compatibility under false own is not
used as body evidence or as a safe-forget call summary.

Profile remains `experimental-source-linked-select-pointer-drop-v4`, exact patch
`c7cc08a995bac5879901f4fe08030f09d23bdfefb1a3ab5893be12a8dd1f8fc1`.
All admission flags are unset. Kernel, prelude, exporter, refiner, dead-code rules,
std runtime, signatures and target contract are unchanged. ManuallyDrop<T>→T and
ManuallyDrop::new(arg)→arg, including destructor suppression/no-unwind correspondence,
are existing TRUSTED model operations. Verifying a ghost/body prefix does not
prove their correspondence to Rust semantics and does not create memory rights.

Source preflight/regeneration, exact original/verified ghost stripping and all
before/after stage hashes PASS. NORMAL/readonly export and full decode both exit0;
readonly refinement exits0. Complete decoded MIR files are byte-identical, SHA256
`3b08b5835f03ff152e6dae68bbf4ce05d1491d7919124f06222794f844b8553d`.
Four locals are _0:unit, _1:T, _2:ManuallyDrop<T>, _3:T. BB0 moves _1 to _3 and
calls the sole typed ManuallyDrop::new<T> with Move _3, result _2, normal BB1 and
cleanup BB2. BB1 ends temporary storage, assigns unit and returns. BB2 has
cleanup=true and UnwindResume. There is no Drop terminator. The cleanup is retained;
no-unwind acceptance cannot be inferred from this syntax or failed full proof.

| Annotation or operation | verified/lib.rs coordinates |
| --- | --- |
| Adapter declaration / body | 3 / 14–16 |
| req block / statement | 5–7 / 6 |
| ens block / statement | 8–10 / 9 |
| on_unwind_ens block / statement | 11–13 / 12 |
| Runtime ManuallyDrop::new | 15 |
| MIR UnwindResume span / final dead-code diagnostic | 3:1–16:2 |

The full verifier executes exactly the seven functions declared in the BEFORE
card: u32_sync, u32_share_mono, init_ref_readonly_points_to_shared,
std::mem::close_MaybeUninit_pointer_own, std::mem::select_MaybeUninit_pointer_own,
std::ptr::pointer_drop_glue_identity, checked_forget_generic. All have execution,
return and leak-check evidence. The target trace is log219–232; log233 is the sole
`verified/lib.rs(3,1-16,2): dead code`, with no preceding proof error. Full verifier
exit1 and classification INCONCLUSIVE are retained. This is a nonvacuous body
prefix, not a successful auxiliary theorem.

## Dead-code provenance from the unchanged-profile AST diagnostic

[Run37678089113](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37678089113)
checks source `a6f077a5aa89ad25df94295320cdbe18ebe4b9d9` with only the existing
console diagnostic option `-dump_ast_with_locs verified-ast.txt`. Exact source
pairs and both complete decoded MIR files are byte-identical to37675513854;
all effective schema/tool hashes, applied patch and specification audits also
match. Export/decode/refinement exit0; full verifier again exits1 with the sole
adapter-span dead-code diagnostic. All seven bodies return/leak-check. The
classification remains INCONCLUSIVE, never PASS.

The2746-byte AST has SHA256
`172fbc51f8592fbdad092a7f0abaa1895077d72c4dd60cd887b37fa9e196aecc`.
Its topology is captured explicitly, not inferred from expected block counts:

| AST dump line | Verified node and source span |
| --- | --- |
| 3–5 | Generic Func declaration; req6, returning ens9, unwinding false12 |
| 7–9 | Three local DeclStmt: $_0:unit, $_2:T, $_3:T, span3:1–16:2 |
| 10–11 | Label0, then $_3=t at15:31–32 |
| 12–13 | $_2=$_3, then Goto1 at15:13–33 |
| 14–15 | Label2 and ReturnStmt(unwinding()), span3:1–16:2 |
| 16–17 | Label1 and ReturnStmt(returning($_0)), span16:2 |

There is no incoming AST Goto/Switch branch to label2. Its synthetic cleanup
return remains between Goto1 and label1. NORMAL/readonly MIR retains cleanup BB2
UnwindResume with the whole-function span; this is an annotation/translation
coordinate, not proof that the Rust adapter declaration was unused. The target
body does execute. The AST contains no runtime Drop call and MDnew is lowered to
assignment; the latter remains an existing trusted model operation.

Pinned translator source explains this structure: vf_mir_translator.ml2413–2418
maps MDnew to FnCallResult;2549–2553 emits direct assignment with normal Goto;
2607–2613 nevertheless retains normal plus unwind CFG targets. The block walk
includes cleanup BB2;2775–2783 translates UnwindResume to ReturnStmt(unwinding()).
No ignore_unwind_paths option is enabled and no cleanup edge was removed from MIR.

Frozen verify_expr.ml459–467 recursively registers nontransparent statements,
including DeclStmt/ReturnStmt; labels are transparent. vfconsole.ml267–282 removes
executed keys and exits1 if a registered statement remains. Its LocHashtbl compares
loc0 with physical `==` (109–115). Thus the observed exact failing obligation is
an unexecuted registered key printed as `verified/lib.rs(3,1-16,2)`, after normal
body return/leak. The dump demonstrates an orphan synthetic cleanup return at
that same span and the source explains its retention: this is the supported
structural explanation. The dump serializes loc values, not physical identity;
we have not directly instrumented or proved which same-span loc key remains.
Do not collapse the three local declarations, Func span and cleanup return into
one key or claim an unused Rust function from the printed diagnostic alone.
The three DeclStmt locations are taken from the function loc (translator4938–4990);
cleanup gets a separately translated terminator SourceInfo loc (translate_span_data,
462ff). The raw target log has four full-span Executing-statement messages; these
are not an injective mapping to the three dumped declarations. This is another
reason to keep structural reachability evidence separate from residual-key identity.

**STOP at this frozen translation/dead-code acceptance obstacle.** No new syntax
variant, cleanup pruning, dead-code exemption or model/tool semantic change was
made. A successful complete auxiliary theorem is still absent, so no actual-call
link is designed/admitted/redirected in this iteration. Reconciliation of retained
translated cleanup with the mandatory gate requires a separate scoped decision.

## Separate classifier repair and immutable replay

[Replay37676357686](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37676357686),
processor source `dd4b0493b8411d92f61f525a3c7ef6ec0429d021`, performs no build or
verification. It replays pinned S7a run37669436220/source
`a5ce1b5f71d2f0a2ecd1f74e44063ba079683b4d`, compact artifact11503963988. Whole
inner archive SHA256 is
`12c3f3f509fc845dd1aa1bb7d8b80f8fcf70e6ab6064af3436168f0b9489dd83`.
Run/artifact/source association, archive hash and261 exact selected input files
PASS; all nine original INCONCLUSIVE classifications remain byte-for-byte intact.
New classification is separate: helper_positive and frame_positive remain
INCONCLUSIVE (exit1/dead-code); false_assert, wrong_post, thread_loss,
thread_duplication, frame_loss, frame_duplication, frame_wrong_value are
INTENDED_NEGATIVE only at their specified body/post/leak obligations. Each negative
has exactly its intended error and zero dead-code entries; positives retain their
dead-code failures. This replay does not accept the full S7 matrix.

The strict classifier counts anchored timed execution headers, ignores diagnostic
note text and enforces the predeclared ordered function inventory. Seven hosted
controls PASS: baseline; ignored note; note-only rejection; true duplicate-header
rejection; missing function; unknown function; exit1/dead-code positive rejection.
Replay artifact11506224082 SHA256
`be6bb45df5034f8be8d992906dfd08f1f0183d30b2dbf7796d389b93894f7691`.

## Actual-call linkage and actual helper

No S7 actual redirect, broad forget summary, guard-own=true, new ownership/Drop
model or pointer-derived slot rights were introduced. Full source/MIR nominal
admission, unsafe-adapter/SAFE-call correspondence, thread/cell/frame/borrow controls,
mutation controls and new-profile S6v4 regressions remain NOT RUN. They cannot be
accepted before a successful complete standalone theorem. No claim is made that
an external same-shaped guard supplies nominal identity or that one path proves
all helper branches.

Last actual evidence is accepted S6v4 run37656621026/source
`75681fbc57bda633f59096cdc28f0c1aa61daef8`: initialized selected cell from the two
constructors/stock opens supplies retained pointer drop60; closes61/62 pass. It
stops at forget63, std/lib.rsspec420 requiring
`<DropOnPanic<*const Element>>.own(t, guard)`, absent from current resources.
assume_init was not reached and remains outside authorization. The S5j historical
refinement failure remains recorded, never reclassified as a success.

## Continuing budget and evidence

Entry4411/5400 used989remaining; standalone178s + replay12s + AST diagnostic151s
=> **4752/5400 used648remaining**. No active run; this iteration totals341s.
No new budget. Generic compact11507342250/full11506168168, inner archive SHA256
`4f446d1d199aa2bae9a37f9e4df4a68c2515dd217d2bee9a02e2c885ab357479`;
852/852 entries pass SHA/CRC/size audit. Raw console and full evidence inspected.
AST diagnostic compact11507826485/full11507796366, inner SHA256
`13bc43d3fe0e095b4aed890760fa4759965205e75963722923c829e556d2be47`;
853/853 entries pass SHA/CRC/size audit. Raw console and full evidence inspected.
It does not change the failed theorem or enable actual admission. Checked proof/
diagnostic SHA values above are separate from the final documentation-only HEAD;
no proof was run on the documentation closeout.

---

# Historical S7a exact local-guard forget — diagnostic closeout

**STOP: independent acceptance is blocked by the frozen global dead-code gate.**
`forget` is NOT ACCEPTED and actual redirect is NOT IMPLEMENTED. The body route
produced nonvacuous local evidence, but neither positive is a successful complete
verification. Full S7 source/MIR mutation controls, borrow-token matrix and new-profile
regressions are NOT RUN. Existing S6v4 components/classifications remain unchanged.
[Design and BEFORE cards](SORT4-SELECT-FORGET-DESIGN.md).

Latest [run37669436220](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37669436220),
proof/diagnostic source `a5ce1b5f71d2f0a2ecd1f74e44063ba079683b4d`.
Same `experimental-source-linked-select-pointer-drop-v4`, patch
`c7cc08a995bac5879901f4fe08030f09d23bdfefb1a3ab5893be12a8dd1f8fc1`.
All admission environment flags inactive; no new semantic profile or call summary.
Actual std runtime, signatures and target contract unchanged. All executable work
was GitHub-hosted, one relevant run at a time; no local compilation/verification.

## Body hypothesis and trust boundary

Pinned core::mem::forget body is `{ let _ = ManuallyDrop::new(t); }` at
mem/mod.rs162–164, file SHA256
`1db195d24508e4eef81163672d008667765c2c121f4fa70f8752742e11106273`.
Checked unsafe adapter takes exact nominal `DropOnPanic<*const Element>` and
requires only `thread_token(?tid) &*& tid == currentThread`; normal post returns
same token, unwind post false. A positive probe constructs the same guard from
an existing initialized `*cell |-> value`, calls the adapter while framing that
cell and independent `*frame |-> flag`, and returns all three resources.
No guard-own=true, no Element ownership and no permission to drop an inaccessible
slot is introduced. Wrapper/borrow tokens outside guard were part of the proposed
full acceptance, but those specific controls are NOT RUN; cell/frame evidence
must not be generalized to them.

Existing pinned translator maps ManuallyDrop<T> to T and new(arg) to arg. Its
representation, destructor suppression and operation/no-unwind correspondence
are TRUSTED existing semantics, not established by this body experiment. SAFE
compatibility with false nominal own is vacuous and supplies no body theorem.
The reachable explicit unsafe precondition, actual body execution, return/leak
and false-assert countercheck give local nonvacuous evidence separately. Complete
proof acceptance and correspondence from real safe mem::forget to this unsafe
adapter are still absent. The real guard Drop remains unchanged and unproved
here; no arbitrary-slot destruction right follows from pointer bits.

## Captured source, annotations and full typed MIR

A source-only macro module supplies helper/probe declarations at the actual guard
scope; sole macro argument is its original `DropOnPanic` identifier. Runtime body
of the adapter is exactly forget's body, without changing ManuallyDrop spelling.
Both insertion sites and all four original/verified files pass ghost-strip,
hosted preflight/regeneration and before/after stage SHA checks. NORMAL/readonly
export/decode and readonly refinement PASS independently in all nine variants.
This is diagnostic source integrity, not a completed source/MIR admission gate.

Positive macro file coordinates (columns in Cap'n Proto are zero-based):

| Annotation/item | Exact source coordinates |
| --- | --- |
| Helper declaration/body | forget-items.rs3, body14–16 |
| Helper req / ens / unwind | blocks5–7 / 8–10 / 11–13; statements6 / 9 / 12 |
| Exact ManuallyDrop::new | forget-items.rs15 |
| Probe declaration/body | forget-items.rs17, body28–31 |
| Probe req / ens / unwind | blocks19–21 / 22–24 / 25–27; statements20 / 23 / 26 |
| Guard construction / checked call | forget-items.rs29 / 30 |

NORMAL and readonly decoded **complete body records**, from `defPath` through
`loopSpecBlocks = [] )`, are byte-identical for the positive helper and probe:
helper SHA `1b8cc3db49014ec955cd646b0cca6a39e72ddaba21e32f6191d8faa53dfb21d5`,
probe SHA `173ad123bc3434130db228b7a8fedbe493a375f290758dced68e1dd1894a0e61`.
Helper has4locals/3blocks; probe7locals/3blocks; both `isFromExpansion=true`.
No global expansion allowance was added to v4. Actual parent still has36/19 NORMAL
versus31/14 readonly, corresponding to the existing five stock projection ghosts;
macro/module declaration does not create a runtime call in the actual body.
Full S7 parent/source/expansion mutation admission remains NOT RUN.

Helper NORMAL-MIR artifact coordinates: defPath5535, nominal ADT5621,
ManuallyDrop callee5876, cleanup edge5921. Name is
`select_unpredictable::checked_forget_guard`, not a same-shaped external guard.
Parameter/temporary ADT is exactly `select_unpredictable::DropOnPanic` with
substitution `*const Element`. Locals: _0 unit result, _1 input guard, _2
ManuallyDrop<exactguard>, _3 moved guard. BB0 has storage operations, Move _1→_3,
sole typed `std::mem::ManuallyDrop::<T>::new<exactguard>` call with Move _3→_2;
normal BB1 kills temporary storage, assigns unit and returns; cleanup BB2 resumes
unwind. There is NO Drop terminator in helper. Retained cleanup is NOT evidence
that unwind is impossible; the existing identity lowering is the trust boundary.
Actual parent runtime drop/forget and guard-cleanup edges remain in captured MIR.

## Independent nine-case evidence, without classifier rewrite

Every original automatic classification is **INCONCLUSIVE**. Positives have no
proof error and execute to return/leak but exit1 on mandatory dead-code reporting.
Seven negatives reach their exact intended first-error obligation. Their classifier
also counts the repeated `note: Verifying function` as a second header, so does
not accept them. No classifier correction/replay or semantic change was mixed
into this result; raw classifications and all logs retained. Below are raw
observations, not an accepted full matrix.

| Case | First causal outcome in verified/forget-items.rs |
| --- | --- |
| helper_positive | body/return/leak, then global dead-code exit1 |
| frame_positive | guard construction/call/frame post/return/leak, then global dead-code exit1 |
| false_assert | line16: Cannot prove false |
| wrong_post | ens9: Cannot prove false |
| thread_loss | return16: Function leaks heap chunks: thread_token(tid) |
| thread_duplication | ens9: No matching heap chunks: thread_token(tid) |
| frame_loss | return31: Function leaks heap chunks: points_to<bool>(frame, flag) |
| frame_duplication | ens23: No matching heap chunks: points_to<bool>(frame, flag) |
| frame_wrong_value | ens23: Cannot prove false == true |

## Precise next blocker and actual result

Frozen console `src/vfconsole/vfconsole.ml265–282` registers statements globally
and exits1 if any remain unexecuted. `verify_expr.ml154–162` focus only selects
function/prototype execution; it does not restrict that global inventory.
Helper-positive log1–16 executes body/return/leak; log17 first dead-code entry is
`verified/forget-items.rs(3,1-16,2)`, followed by skipped sibling/actual parent
`verified/lib.rs(10,1-74,2)` and prelude obligations. Probe-positive log1–22 likewise
reaches return/leak, then fails the same gate. No missing guard-own resource was
established in these checked bodies.

Independent exact-nominal positive acceptance with this isolation is therefore
unavailable at the frozen profile. `-allow_dead_code`, scoped suppressions,
dropping unrelated bodies or changing global callback/focus semantics would
weaken/change the required gate; none was done. Nonfocused actual redirect to
make the parent live before standalone acceptance would reverse the required
callee-before-caller order. A separate design resolving independent acceptance
while preserving global reachability/source/nominal gates is needed before any
new admission; this closeout does not authorize a general frontend/guard model.

Actual integration was NOT rerun in S7. Last admitted S6 prefix, run37656621026,
still passes actual pointer drop60 and closes61/62 and stops at forget63:
std/lib.rsspec420 requires `<DropOnPanic<*const Element>>.own(t, guard)`, absent.
S7 has not bypassed/discharged it. No next actual assume_init obligation has been
reached, and no whole helper branch/return/unwind/sort4 theorem is claimed.

## Evidence and continuing budget

| Run | Source SHA | Job seconds | Used / remaining |
| --- | --- | ---: | ---: |
| Entry ffa370a | S6 proof75681fbc | — | 3954 / 1446 |
| [37665233357](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37665233357) | 2ba63774e964e2ca76b3b1639e550cb93e70769e | 133 | 4087 / 1313 |
| [37666273705](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37666273705) | 3a4b0e9d375e8871b541ed18e6b340cf152734be | 122 | 4209 / 1191 |
| [37667942855](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37667942855) | f101203bfe5e6100ee2ae60fc0cae62ef7c6149b | 99 | 4308 / 1092 |
| [37669436220](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37669436220) | a5ce1b5f71d2f0a2ecd1f74e44063ba079683b4d | 103 | **4411 / 989** |

Same5400 summed hosted jobseconds, no reset. Latest18:46:51–18:48:34UTC.
No active run. S7 spent457s including setup/build/packaging; first9 construction
failures, next9 compiler failures and third9 incomplete_include failures remain
historical evidence, never intended proof negatives.

Latest compact artifact11503963988/full11503793868; inner archive SHA256
`12c3f3f509fc845dd1aa1bb7d8b80f8fcf70e6ab6064af3436168f0b9489dd83`,
manifest1135/1135 SHA/CRC/size PASS. Prior compact11503762679/full11502754044:
inner `a3e1ce82a09bca102434d5c266fd5602f7ff673e06f74824a73dc809e98807dd`,
1099/1099 PASS. Earlier identifiers/hashes in EXPERIMENT-LOG retained.
Green Actions badges mean diagnostic collection completed, not proof acceptance.
