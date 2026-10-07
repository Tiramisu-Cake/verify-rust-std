# STOCK-26.10-BASELINE — отчёт и сохранённая BEFORE card

2026-10-08. **Фаза завершена: stock chain работоспособна, exact generic forget
INCONCLUSIVE на обязательном dead-code gate; карта переноса готова.**
Proof SHA `a0cfd30e066acbaf1b5406cd9773f54388cc45be`,
[run37694000195](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37694000195).
Ни один semantic patch не применён. Расход **99/1800 job seconds**, остаток1701;
старый5306/5400(94) отдельно, S7c UNACCEPTED. Документационный closeout HEAD
является последующим commit, не proof SHA. Активных запусков нет.

## Сохранённая BEFORE card

2026-10-08. Owner explicitly resumes this named phase after Git synchronization.
Own branch `research/stock-26.10-baseline`, parent
`a06cfb9d9dd95cf5a8875bd5d2f9bd85df47fadd`; included upstream/std
`cd371e035c7e573760c43bf934d53e8118ee3e7d`. Sync/source branches and main stay fixed.
Separate ceiling **1800 GitHub-hosted job seconds**, including setup and artifacts.
Old account **5306/5400, 94 remaining** is untouched; S7c **UNACCEPTED**.

## Obligation, hypothesis and frozen profile

Actual obligation advanced: `core::mem::forget<T>` at mem/mod.rs193–195,
exact body `{ let _ = ManuallyDrop::new(t); }`. It is unchanged textually from the
old experiment. This tests a minimal unsafe generic adapter with the previous
explicit contract, not a safe generic-forget summary or actual guard linkage.

Hypothesis: unmodified release26.10 supports isolated scalar/raw-pointer bodies
through export/decode/refinement/full proof; on the new compiler/std, the exact
forget adapter either passes the complete gate or reveals a fresh, diagnosable
failure. The old physical residual key52 and old CFG remedy are not presumed.

Profile `stock-26.10-baseline-v1`: VF source/tag26.10
`f76012fb518703b1d98e243ac4f487f16877cfcb`, release archive SHA256
`5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd`,
Rust nightly-2026-09-25, target x86_64-unknown-linux-gnu, Ubuntu22.04 hosted.
Effective patches **NONE**. Stock exporter, integrated decoder/translator and
refiner come from the same release; decoder wire schema comes from the exact
source pin, SHA256 `f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469`.
The release/source provenance is trusted; source components and actual binaries,
all effective stock specifications, rustc commit/sysroot are recorded on runner.
Stock specs are compared bytewise to the exact VF source. No console rebuild.

The fixture body is extracted textually from repository std; external std calls
are exported using the nightly sysroot crate metadata. This is not a build/export
of repository std. Runner records repository and rust-src hashes and their actual
agreement/difference, so this limitation cannot be hidden behind the nightly label.
Repository mem SHA256 `b86a596a58dcb21a45e8b29b33327ca8c7bde708aa6fca158d4366e51403daf2`;
ManuallyDrop `f9cce798828cc852c00feeea9a6218c225b68d92727a5edbddc7c08a731a4f25`;
SmallSort `85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`.

## Complete fixture contracts and controls

All clauses are in separate block annotations, ghost-stripped original source is
retained, and hashes are checked before/after every stage. `tid == currentThread`
is part of every precondition below. All `T` are unrestricted sized Rust types;
no Freeze/Copy/purity additions. Full normal/unwind contracts:

| Fixture | Domain and precondition | Normal post | Unwind post / expected obligation |
| --- | --- | --- | --- |
| u32_positive, stock_u32(x) = x | all u32 x; thread_token(tid) | same thread token, result == x | false; full verifier exit0/body/return/leak/dead-code |
| raw_positive, stock_raw(p) = *p | valid initialized u32 slot, full `*p |-> v`, thread token, pointer provenance/permissions carried by the resource | same slot/value and token, result == v | false; full verifier exit0/body/return/leak/dead-code |
| u32_false_post / raw_false_post | same respective pre and body | same resources & false instead of result equality | false; intended `Cannot prove false` at normal ens line6 |
| u32_contradictory_pre | u32 pre & false, same nonempty body | original full normal post | false; expected mandatory dead-code rejection for skipped stock_u32 body, no early frontend failure |
| forget_positive | arbitrary T by value; thread_token(tid) | same token | false; exact generic body, full gate or first blocker |
| forget_false_post | same T/pre/body | same token & false | false; intended `Cannot prove false` at ens line9 |
| forget_contradictory_pre | same T/pre & false/body | same token | false; intended dead-code rejection for skipped adapter body |
| potentially_panicking(b) | all bool b, token; panic if b | same token | same token; actual callee body checked before caller in same unit |
| ordinary_unwind | bool b, token; calls checked callee | same token | same token; actual normal/unwind ReturnStmt paths must execute |
| false_unwind | same caller domain/body | same token | false; intended `Cannot prove false` at caller unwind line23 |
| shared_cleanup<T> | bool b, arbitrary T, token; MD::new then checked potentially-panicking call | same token | same token; verify actual cleanup predecessors and both AST returns |

First scalar/raw fixtures run before forget. All eleven are isolated units; no S6
predicates/helpers are inserted. Failures do not prevent independent later units.
Each unit records NORMAL export/decode, readonly export/decode, full verifier and
refinement independently. AST-with-locs is captured by the stock console; there
is no separate standalone translator binary stage. Full proof means actual timed
body headers and body/return/leak traces, exact ordered stock-prelude functions
u32_sync/u32_share_mono/init_ref_readonly_points_to_shared plus target functions,
no focus, exit0, no dead code. Unwind positives also require observed actual AST
unwind/normal returns, not just full exit0. The old strict classifier is unchanged;
its raw classification is saved. Contradictory-pre tests have a separate explicit
mapping requiring exact body span, no target body execution, exit1 and frontend0;
they are deliberately unreachable controls, never positive proofs.

## Outcome decisions and dispatch bound

- Setup/export/decode/refinement or unrelated proof failure: record first causal
  stage, fix only a concrete harness issue; this is not an intended negative.
- Full scalar/pointer positive and intended controls: stock chain operational in
  that domain only. Continue exact adapter/independent unwind controls.
- Adapter dead code: inspect new complete MIR, AST, stock source/console diagnostic.
  State structural inference separately from physical-loc attribution. No tracing
  patch or semantic CFG change is authorized in this phase.
- Missing S6 rules: source-based migration plan, not adding predicates here.
- Semantic rejection repeats: no identical re-run. A new run needs a new
  falsifiable hypothesis or exact harness repair, plus budget and artifact reserve.

First dispatch uses existing workflow API selection
`proof=verifast_maybeuninit_new_pointer`, `forget_guard_stage=forget_generic_ast`,
`budget_minutes=30`, routed only on our new branch to job `stock-2610`.
Research trigger remains **workflow_dispatch only**. Other historical jobs skip;
a skipped job is not verification. Exact source SHA is resolved after commit and
remote equality before dispatch. Job ceiling10min=600s; inner deadline540s leaves
60s for artifacts/cancellation, fixture deadline530s. First run has1800s available;
remaining budget must be recalculated from actual job started_at/completed_at.
No actual-call redirect, ownership guard, assume_init, pointer-drop/memory/unwind
model extension or patch transfer. Deliverable is stock evidence + transfer plan.

## Run1 — setup failure and BEFORE run2

Run [37693718508](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37693718508),
SHA `4baed1897c1e50196e06142c957c6a2756d58132`, job113039989146
22:04:06–22:04:43UTC =37s. Artifact11515150111 digest
`13caace621e93e8b601c3b4282f4c2246af65f57b4da9ec3fe48f598dd1b7154`.
Archive/source/compiler install PASS, then audit rejects generated package file
`bin/rust/rocq/.Annotations.aux`, absent from tracked source. No fixture/stage proof
ran; all obligations NOT_RUN. This is a harness audit overreach, not stock proof
failure. Repair: hash entire Rust package inventory, compare exact stock/source
*.rsspec content AND complete inventory; record source existence/equality for all
other files without requiring generated Rocq auxiliary output to be Git source.
No runtime specification bytes, verifier flags or classifiers change. New falsifiable
hypothesis: proper effective-spec audit reaches the eleven declared fixtures.
Same full domains/posts/expected diagnostics, same stock profile/600s job ceiling
and60s artifact reserve. Used37/1800, remaining1763; old budget unchanged.

## Карта переноса — исходниковые выводы, не runtime acceptance

Это карта для отдельного следующего решения, а не разрешение применять patches.
Точные S6 rules отсутствуют в stock source f76012fb. Их старые доказательства
не переносятся на новый std/tool автоматически; S7c остаётся UNACCEPTED.

| Компонент | Что даёт stock26.10 (source analysis) | Изменение std/MIR и минимальный кандидат | Новое доверие и приёмочные ворота |
| --- | --- | --- | --- |
| Constructor | std/lib.rsspec429–440: abstract MaybeUninit/new/inner; отсутствуют MaybeUninit_pointer_own и checked close/select lemmas | maybe_uninit.rs406–408 сохраняет union value=MD::new(val), но manually_drop.rs153–158 теперь поле T вместо MaybeDangling, new180–182 — прямой initializer. Пересертифицировать constructor actual body/union и новый MIR; отдельно переносить только pointer-value constructor/defined predicate при подтверждённой необходимости | Review представления и identity/destructor correspondence; unsafe/SAFE prototype checks отдельно от тела. Полная constructor positive/negative + source/MIR/contract mutation матрица, no pointee rights, same-profile baselines |
| as_mut_ptr | Stock MaybeUninit storage/size/align lemmas, но нет S6 source-certified method redirect/own bridge | maybe_uninit.rs656–662: rustc_as_ptr, два casts self as *mut _ as *mut T. Минимум — обновлённый exact-method certificate + checked adapter и MIR gate только при установленном stock blocker | Происхождение указателя, borrow/storage и initialized cell нужны явно; pointer bits не создают slot rights. NORMAL и readonly, точные receiver/type/call/source/MIR negative controls, refiner, полная asptr9+17 матрица |
| Typed intrinsics | Нет S6 typed select_unpredictable rule и selected-pointer ownership lemma | smallsort.rs637–645 сохраняет pointer selections; source/compiler changes требуют новых fallback/intrinsic/types/call count/MIR certificates. Кандидат — узкая type-certified family, без generic intrinsic расширения | Trust intrinsic correspondence отдельно от microlemma; сохранять value/provenance/permissions и только выбранный ресурс. Intrinsics16+40 admission и baselines на едином профиле; upstream ghost projections не доказывают runtime intrinsic |
| Pointer drop | std/lib.rsspec597–600: generic drop_in_place требует token, slot, T.own; normal/unwind возвращают token+slot. Translator2952–2959 делает обычный call; нет pointer_drop_glue_identity | ptr/mod.rs843–864 теперь drop_in_place вызывает drop_glue(&mut *to_drop), lang item перенесён на drop_glue с пустым compiler-replaced body. MD теперь содержит T напрямую. Старые method/glue certificates должны fail closed; минимум — новое typed raw-pointer glue/source соответствие и отдельная resource identity lemma | Это новая узкая доверенная compiler glue specialization, не общий Drop. Проверить pointer value vs pointee права, normal/unwind/drop glue; 2 positives+11 proof negatives и полные22 admission, включая незавершённые старые mir_cfg_unwind/mir_extra_operation/mir_contract/method_source_pin/glue_source_pin |
| CFG | MD::new identity FnCallResult arg: translator2592–2598; assignment+normalGoto2721–2758, inventory targets@unwind_targets2796; UnwindResume→unwinding ReturnStmt2989–2998; find_blocks3701+ | Новый MIR/AST решает применимость. При подтверждённом orphan cleanup кандидат — только точный MD::new + FnCallResult + normalGoto successor inventory; никаких общих FnCallResult pruning. В этой фазе не реализуется | Свежая causality/loc диагностика, preserving exported MIR and reachable cleanup. Full positive/body/return/leak/dead-code, обычный unwind, общий cleanup с реальным вторым predecessor, false normal/unwind и contradictory-pre controls; regression всех S6 families только после независимого их допуска |

Новый SmallSort full-file certificate отличается: marker attribute и построение
slice references через slice::from_raw_parts{,_mut} заменили raw-parts+deref в
callers (smallsort.rs285,333,358,366–370,670). Само текстуальное сохранение
sort4/select не закрепляет новый typed MIR, nominal paths, cleanup graph или spans.
MaybeUninit::assume_init использует transmute_neo; это отдельно **OUT OF SCOPE**.

Условия нового решения: каждый semantic overlay получает отдельный rationale,
source/MIR applicability, trust/admissibility review и явный regression gate ДО
implementation. Actual-call redirect/nominal guard ownership/assume_init и
расширение memory/unwind не входят ни в этот baseline, ни автоматически в
минимальный transfer. Stock микрофикстуры не доказывают whole std helper/Challenge.


## Run2 — полный stock baseline

Run [37694000195](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37694000195),
proof SHA `a0cfd30e066acbaf1b5406cd9773f54388cc45be`, job113040941877:
22:06:34–22:07:36UTC =62s. Preparation/install/audit completed, eleven isolated
units all executed; Actions success denotes evidence collection, not generic-forget
acceptance. Other six jobs skipped and supply no verification. No repeats of a
semantic failure, no retries of old proof SHA, no local executable checks.

All11 NORMAL exports,11 readonly exports,22 decodes and11 refinement invocations
exit0; all66 stage source-integrity checks pass. Every unit has exactly3 stock
prelude functions before its declared one/two target bodies, without focus or
S6 predicates. Full verifier results and actual negative locations:

| Case | Full verifier | Body/post/dead-code evidence |
| --- | ---: | --- |
| u32_positive | 0 | stock_u32 body+return+leak;39 statements, complete gate |
| raw_positive | 0 | stock_raw initialized u32 load+resources+return/leak;39 statements, complete gate |
| u32_false_post | 1 | INTENDED_NEGATIVE, Cannot prove false at6:27–32; no dead code |
| raw_false_post | 1 | INTENDED_NEGATIVE, Cannot prove false at6:40–45; no dead code |
| u32_contradictory_pre | 1 | separate INTENDED_DEAD_CODE_REJECTION: body skipped, exact function span1:1–13:2 plus load/return locations; frontend0 |
| forget_positive | 1 | INCONCLUSIVE: exact body, normal return+leak, sole3:1–16:2 dead code, no proof error |
| forget_false_post | 1 | INTENDED_NEGATIVE, Cannot prove false at9:27–32; no dead code |
| forget_contradictory_pre | 1 | separate INTENDED_DEAD_CODE_REJECTION: adapter body skipped, two physical entries printed at3:1–16:2 plus15:13–33,15:31–32,16:2; frontend0 |
| ordinary_unwind | 0 | checked callee then caller,44 statements; normal27:2 and unwind26:14–38 ReturnStmt execution, each followed by leak check |
| false_unwind | 1 | INTENDED_NEGATIVE after actual caller unwind ReturnStmt26:14–38; false unwind post23:15–20 |
| shared_cleanup | 0 | checked callee then caller,46 statements; MD::new and panicking call both export cleanup3, AST has real panicking predecessor to3; unwind15:1–28:2 and normal28:2 ReturnStmt+leak execute |

Every positive table entry is a narrow stock-model fixture claim. Normal/unwind
returns above were bound to the actual caller Func AST and raw console trace,
not inferred from a green badge. The two contradictory-pre maps remain separate
from unchanged strict-original INCONCLUSIVE classifications in summary.json;
all earlier historical classifications/bytes are preserved. No weakenings,
allow_assume/ignore_unwind_paths/dead-code/refinement suppression or changed
annotation runtime bytes were used.

### New stock dead-code diagnosis and exact uncertainty

NORMAL and readonly **complete** forget MIR are byte-identical (604 lines,
SHA256 `f6aa0ef40489ba7497c9460b237c68846dbb521c05add2c5e6cae4bc1d0a4451`).
It contains4locals,3blocks: BB0 Move t→_3 and typed
`std::mem::ManuallyDrop::<T>::new<T>` Move_3→_2, normal target1, cleanup2;
BB1 storage kills/unit return; BB2 `unwindResume`, no statements. There is no
Drop terminator. New AST SHA256
`172fbc51f8592fbdad092a7f0abaa1895077d72c4dd60cd887b37fa9e196aecc`.
It contains3 full-function-span DeclStmt, two identity assignments, Goto1,
label2 + unwinding ReturnStmt at3:1–16:2, then label1 + normal ReturnStmt16:2.
There is **no AST incoming edge to label2**. Normal assignments/return/leak are
observed; no full-span unwind return is executed. The sole final diagnostic is
`verified/lib.rs(3,1-16,2): dead code`.

Stock source explains the structural blocker: translator2592–2598 chooses
FnCallResult identity,2721–2758 emits assignment+normal Goto,2796 retains
unwind_targets in inventory; find_blocks traverses successors and UnwindResume
2989–2998 becomes an AST return. verify_expr.ml459–467 registers nontransparent
statements; vfconsole.ml271–282 removes executed locs and rejects any residual.
LocHashtbl equality (109–115) is physical identity. This is fresh **structural
causal evidence for an orphan cleanup return**, not direct measurement of the
remaining physical key. AST serialization prints equal span values for several
objects and stock diagnostics do not expose identity. New residual numeric key,
registration/execution counts and exact same-span object attribution remain
**UNKNOWN**; old52 is not reused. No trace patch was allowed/applied. A narrowly
scoped diagnostic decision is needed before accepting any CFG transfer.

Shared-cleanup positive supplies a useful independent contrast: new MIR has two
cleanup3 edges, but AST drops the MD identity call's path while the genuine
panicking FnCallOutcome branch still goes to3 and executes unwind+leak. Ordinary
unwind likewise executes both outcomes; the false-unwind control rejects at the
postcondition. This establishes stock handling of these concrete reachable paths,
not general correctness of its unwind translation/model.

### Effective profile and std/export audit

Release/source pin/spec inventory audit PASS after run1 harness repair:17 effective
*.rsspec files match exact f76012fb content and inventory. Full stock Rust package
hashes include generated Rocq auxiliaries; these are not console specs. The stock
console loads prelude and std/lib.rsspec (translator7924–7945). Export/decode/full
console/refiner succeed together on the independent domains, providing operational
schema/decoder/translator compatibility. Integrated decoder/translator binaries
are part of the stock console; no independently built decoder was substituted.
Archive provenance→source pin remains an explicit trusted release correspondence,
not a local reproduction of the release build.

| Actual component | SHA256 |
| --- | --- |
| verifast (integrated decoder/translator) | 9b7650ad3ab0dad3b8974ae9ba1c662ab2cd897ce1dd07215dedcbe460249ee1 |
| vf-rust-mir-exporter | b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796 |
| refinement-checker | b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28 |
| stock std/lib.rsspec | 2da7acfb6596f8abec90c103ef7f294152c18f974b88124669882fc051272999 |
| schema | f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469 |
| libz3.so (ldd resolves release copy) | 1837668dc531d14b3a4fffc0b690b77929d29c41868f98a89686f5ff64da95ea |
| full stock-spec-hashes.json | e420e8651ab4ba75d7ace9e75dbe4eb026710a2bc0a228ec8b31d8729a6f9957 |
| source-component-hashes.json | 7a6568b2d06931a8169b7bd614780c56ec3b9e2e926a9a77e3f1e0026d943cbd |
| binary-hashes.json | 0061cf859e3c1e5096915de4ea1b22d0b6e1c5b6441201735256cf9474df05ab |

Actual rustc1.100.0-nightly commit
`f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f`, LLVM23.1.1;
Cap'nProto0.8.0. Rust std metadata uses that nightly sysroot. Repository
ManuallyDrop, MaybeUninit and SmallSort files match its rust-src bytewise.
Repository mem/mod.rs and ptr/mod.rs whole files differ: sysroot hashes respectively
`623583b0ec51b865009470016276fb297ba94af2b47caa901127009d8c3799ba`
and `1d11fc57101369e1ffb5a15e5b7ee08da3a8ee72bd563995798c30a2be2b71f5`.
Read-only download from rust-lang/rust at the actual rustc commit reproduces both
hashes. Full diffs show repository Kani/RAPx/safety annotations, cfg-gated helper/
test additions and docs; **forget and drop_in_place/drop_glue bodies have no diff**.
This source audit narrows the mismatch; it is not repository std build verification.
Actual stock MD identity/no-unwind/destructor suppression stays TRUSTED.

Refiner source still has unwind correspondence TODOs: Call unwindAction2548,
Drop unwind2559 and Assert unwind2568. A green refinement result does not discharge
that general trust boundary. Full console unwind traces, exact ghost-strip and
identical runtime MIR are separate evidence; model/refiner expansion is outside
this phase. Constructor/asptr/intrinsic/drop source-linked fixture matrices were
**NOT RUN** on stock/new source; table transfer proposals for those families are
source analysis only. CFG baseline/ordinary/shared controls are runtime-tested,
but no patched candidate or physical-loc instrumentation was tested.

### Evidence, budget and next decision

Artifact [11515215378](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37694000195/artifacts/11515215378)
has ZIP SHA256 `18f1796c2be90f483402db00d2aacb868e8229a8ca2d490e8248bdc2c38be91f`;
325 entries read, CRC audit PASS; raw logs, complete MIR, AST, source pairs,
stage argv/status/resources and all identities inspected. Downloaded logs/artifacts
are outside Git; artifact retention90days. Older run1 evidence retained separately.

| Account/run | Hosted job seconds | Used / remaining |
| --- | ---: | --- |
| Old S7 account (untouched) | — | 5306/5400 /94 |
| STOCK run1 setup-only | 37 | 37/1800 /1763 |
| STOCK run2 eleven independent units+artifacts | 62 | **99/1800 /1701** |

No active run; no semantic draft. Phase is CLOSED with stock forget INCONCLUSIVE,
no actual linkage, no S6 transfer, old profiles/patches/certificates preserved.
Next recommended decision: authorize **CFG26.10-DIAGNOSIS** with a specifically
reviewed nonsemantic physical-loc diagnostic and its removal gate, then decide
whether the confirmed exact MD::new successor inventory mismatch merits its own
semantic overlay/trust review. That future gate must preserve exported cleanup,
full posts, dead-code/refinement, ordinary unwind, shared cleanup and intended
negatives. Only after a CFG candidate gate should separately scoped constructor,
asptr, typed-intrinsics and new raw-pointer glue transfers be considered, with
full new-source admission/regression. No general FnCallResult repair, actual
redirect/guard-own/assume_init/memory-unwind extension follows from this report.
