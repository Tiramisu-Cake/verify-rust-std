# RefinedRust 2026: feasibility для Challenge 8

Дата: 2026-10-11, Europe/Moscow. Исследование исходников и опубликованных материалов; **proof execution NOT_RUN**, Cloud charge 0. Ни один статус existing proofs не повышен.

## Решение

**CONDITIONAL — для малого отдельного исследования `insert_tail`; NO-GO для миграции Challenge 8 и Tool Application сейчас.** RefinedRust 2026 предоставляет подходящие логические механизмы для generic ownership, callback, Drop и unwind. Поэтому утверждение «RefinedRust принципиально не умеет panic cleanup» для текущих исходников неверно. Однако готового пути к доказательству actual `insert_tail<T,F>` с восстановлением CURRENT через `CopyOnDrop::drop` не установлено. На нынешнем профиле весь Challenge блокируется явным отсутствием slices и union ADTs; сама логика ресурсов не заменяет source applicability.

Рекомендация: продолжать текущую работу на VeriFast. RefinedRust имеет смысл проверять только последовательно по [gates](EXPERIMENT-PLAN.md), начиная с source/callee admission и one-cell cleanup. Не инвестировать в интеграцию CI или заявку инструмента до доказательства этого узла без новых trusted assumptions. Данных, что RefinedRust завершит Challenge быстрее или надёжнее, сейчас нет; есть основания для ограниченной проверки альтернативы, но не для смены основного подхода.

## Изоляция и точные revisions

Read-only preflight: исходное дерево `/root/verify-rust-std` было чистым, HEAD `fbc063ce609cc549358e3bbc0f8b3a12b75b3945`, branch `overnight/merge-26.10`. Проверены worktrees, local/remote branches и remotes. `git ls-remote origin` подтвердил main `c7ca8c467aecf10a4b53039372ee97714f854ee3` и research `f6c3b3cf561a75e1f5f433087c975fd1690b7e38`. Origin fetch/push: `https://github.com/Tiramisu-Cake/verify-rust-std.git`. Read-only `gh run list --repo Tiramisu-Cake/verify-rust-std --limit 8 ...` вернул `[]`; это не утверждение об отсутствии Cloud builds.

Создан собственный worktree `/root/verify-rust-std-refinedrust-feasibility-20261011`, branch `research/refinedrust-feasibility-20261011`, **base/policy snapshot `c7ca8c467aecf10a4b53039372ee97714f854ee3`**. [AGENTS](https://github.com/Tiramisu-Cake/verify-rust-std/blob/c7ca8c467aecf10a4b53039372ee97714f854ee3/AGENTS.md), [WORK-POLICY](https://github.com/Tiramisu-Cake/verify-rust-std/blob/c7ca8c467aecf10a4b53039372ee97714f854ee3/research/challenge-8/WORK-POLICY.md) и runbook прочитаны в редакции, изменённой commit `5bf53668a4afa51c302e599be91a2dbc4b24042d`. Также прочитаны STATUS, COMPLETION-PLAN, PLAN, README, team checkpoint, challenge/general rules, Cloud README/v2 и relevant insertion/proof records. Assignment пользователя заменяет прежние branch/phase примеры: только подготовка, budget 0, lanes отсутствуют.

Из-за заполненного VPS собственный worktree переведён в sparse checkout; сохранены нужные docs, SmallSort и workflow definitions. Это не изменение std в Git. В `.sources/` прочитана отдельная копия инструмента и небольшой архив статьи; они исключены из commit. Чужие worktrees, processes, budgets, reservations и coordinator не менялись. Два read-only explorer исследовали независимо project blockers и library features; доказательства не выполняли.

| Identity | Значение |
| --- | --- |
| Actual source этой миссии | [smallsort.rs на base](https://github.com/Tiramisu-Cake/verify-rust-std/blob/c7ca8c467aecf10a4b53039372ee97714f854ee3/library/core/src/slice/sort/shared/smallsort.rs), Git blob `e555fce440872898e47fd5114f32eb15401d07df`, SHA256 `32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959` |
| Historical proof baseline | upstream `cd371e035c7e573760c43bf934d53e8118ee3e7d`, blob `40939f922bcb6fdc7ee0d30427fa861827043827` |
| Policy bytes | WORK-POLICY SHA256 `479c0eeb5bcb7f5dec3b5ccd526de0087a2101a1e018090389676a4dcccc0521`; AGENTS SHA256 `8ccd5c1cb6d4d1bd9691b50fd23253f790d9c0d8e85d1e0aaa6de108c70eb3a5` |
| RefinedRust development pin | [commit `332d945fafa14bf55c0c8390cb35ec4b0c012cff`](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/commit/332d945fafa14bf55c0c8390cb35ec4b0c012cff), observed main/HEAD, 2026-10-01 |
| Published 2026 artifact | [Zenodo v2, 21636474](https://zenodo.org/records/21636474), archive `artifact.tar.gz`, MD5 `29905dcfac8e796707989daf1592d965`, locally read SHA256 `34573bac60de68c3597c23136cd5221a7129f89a24b69340f8e361750f331d53` |

Base SmallSort differs from historical blob in specialization attribute and several slice-construction expressions. `insert_tail` and `CopyOnDrop` bodies match; historical proof results still retain their original source/profile identities. No result is transferred to the new blob by this textual observation.

## Что именно исследовано

[PLDI 2024](https://plv.mpi-sws.org/refinedrust/paper-refinedrust.pdf), DOI `10.1145/3656422`, introduces layout-parametric ownership verification in Coq/Iris and a simplified Vec case study. Its panic-free guarantee and missing traits/closures describe the old prototype, not the inspected development revision. [Artifact 2024 v2](https://zenodo.org/records/10912439) is a separate historical artifact; the 4.4 GB package was not downloaded.

[OOPSLA 2026](https://iris-project.org/pdfs/2026-oopsla-refinedrust2.pdf), DOI `10.1145/3839484`, extends traits, closures, iterators and recursive types, evaluating real ACE memory-management code. Sections 1/5.3 retain limitations around unsized types, GATs and trait requirements on associated types; §6 describes manual proof effort and source adaptations. This is evidence of usable foundations, not SmallSort verification.

The July [v2 artifact](https://zenodo.org/records/21636474) contains its own RefinedRust source, wiki, evaluation instructions and dependency images. Static archive reading verified metadata, README, limitations, toolchain and the function-spec record. Its `fn_params` lacks the development revision's unwind fields; the archived wiki describes a no-panic assumption for unknown code. Thus an artifact-image replay cannot validate the newer unwind implementation. No image was downloaded, installed or executed; archive source was read as data, without running extraction/proof scripts against std.

For the remainder, **all RefinedRust code links pin `332d945fafa14bf55c0c8390cb35ec4b0c012cff`**. “Present” means inspected source or checked-in proof text, not fresh successful replay. No other Challenge solution was consulted or imported.

## Возможности и ограничения

| Область | Проверенное evidence | Применимость к SmallSort |
| --- | --- | --- |
| Generic Rust/layout | [LayoutAlg/syntypes](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/theories/refinedrust/radium/syntypes.v), [generic MiniVec invariant](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/case_studies/minivec/src/lib.rs#L168) | Generic semantic types and abstract layout are available. Exact compiler layout, `repr(transparent)`, padding and std applicability require their own evidence; abstract layout is not an exact rustc-layout certificate. |
| ZST/alignment/provenance | [heap bounds, including zero-size](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/theories/refinedrust/radium/heap.v#L294), [pointer casts](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/theories/refinedrust/radium/lang.v#L503) | Explicit allocation provenance and ZST cases exist. Pointer/integer casts are deliberately stricter than Rust exposed-provenance casts. Distinct logical ZST owners need accounting even when numeric addresses coincide. No demonstrated one-cell ZST recovery theorem. |
| `MaybeUninit` | Logical `maybe_uninit T` in MiniVec; [frontend union refusal](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/rr_frontend/translation/src/types/translator.rs#L1082) | Logical uninitialized cells are supported; actual Rust `MaybeUninit<T>` union translation is not established. Union rejection is a concrete obstacle for scratch callers. A shim bypass would need separate source/trust review. |
| `ManuallyDrop` | No exported binding/proof found in inspected stdlib; [boxed comments](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/stdlib/boxed/src/lib.rs#L67) only mention it | Actual constructor/Deref and compiler suppression of payload Drop must be translated or proved at the pinned source. A transparent struct intuition is insufficient. Absence of a binding is a library/admission gap, not a theorem of impossibility. |
| Raw read/copy | [ptr specifications](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/stdlib/ptr/src/lib.rs#L47), [Radium shims](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/stdlib/ptr/theories/shims.v#L46) | `read` needs logical `Copyable`; its comment proposes moving ownership out first and reading Copyable `value_t`. This need not impose Rust `T: Copy`, but the generic byte/owner reconstruction bridge remains to prove. Copy creates byte representations, not a second `T.own`; shim has TODO safety checks and needs independent alignment/nonoverlap/source correspondence audit. |
| Traits/FnMut/closures | [closure contracts](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/stdlib/closures/src/lib.rs#L13), [FnMut inclusion proof](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/case_studies/adequacy/output/adequacy/proofs/trait_incl_main_map_closure0_FnMut_spec_subsumption_correct.v) | Stateful higher-order contracts and proof artifacts exist. FnMut interface has normal `PostMut` and pure `UnwindCondition`, without a parallel resource `UnwindPost` attribute. Recovering CURRENT F/T through panic and ended borrows needs a concrete proof; silently assuming a stronger callback contract would narrow safety. |
| Specialization | [rustc codegen resolution/FurtherSpecializable](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/rr_frontend/translation/src/traits/resolution.rs#L337) | Some resolution machinery exists. No proof of SmallSort's six specialized bodies, Freeze/CopyMarker dispatch and complete caller domain was found. Thin-pointer helper POC does not settle dispatch. |
| Drop and panic/unwind | [MIR unwind translation](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/rr_frontend/translation/src/body/mir_lowering/unwind.rs), [Drop glue translation](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/rr_frontend/translation/src/body/drop_glue_translation/tx_impl.rs), [panic examples](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/case_studies/tests/src/panic.rs) | Cleanup, resume, terminate and compiler Drop calls are represented. Missing local unwind annotations cause panic-free obligations, not permission to drop unwind checks. Generic destructor calls have virtual DropGlue assumptions that must be linked. No actual CopyOnDrop cleanup replay found. |
| Exceptional resources | [`fp_unwind_post`](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/theories/refinedrust/rust_typing/primitive/functions.v#L41), [`ensures_on_unwind` parser](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/rr_frontend/translation/src/spec_parsers/verbose_function_spec_parser.rs#L1087), [List Drop invariant](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/case_studies/linkedlist/src/lib.rs#L157) | Spatial exceptional postconditions exist, beyond `may_unwind_if(True)`. List destructor retains remaining-resource assertion on unwind. This is the most relevant new mechanism, but a list destructor is not the held-reference/gap protocol. |
| Arbitrary-length loops | [loop rules](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/theories/refinedrust/rust_typing/automation/loops.v), [VerifyThis sort proof](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/case_studies/verifythis2026/output/verifythis2026/proofs/proof_rsorted.v) | Inductive invariants, not bounded unrolling. Existing sorting case is Vec<usize> with specified wrappers; [wrappers explain missing slices](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/case_studies/verifythis2026/src/wrappers.rs#L4). It does not prove generic insert_tail. |
| Actual std/slices | [explicit Slice rejection](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/rr_frontend/translation/src/types/translator.rs#L1819), [README stdlib/interfaces](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/README.md) | This blocks actual R5 `&mut [T]` and sorting entrypoints on stock inspected frontend. `insert_tail` has thin pointers and can be isolated as a diagnostic; proving a rewritten Vec caller cannot replace actual R5. |

## Главный вопрос: `insert_tail` при panic компаратора

For raw copying, the checked-in [copy_nonoverlapping proof](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/stdlib/ptr/output/ptr/proofs/proof_copy_nonoverlapping.v) ends in `Qed` and uses separate owned source/destination arrays. The shim's TODO does not by itself establish a missing nonoverlap proof: separation preconditions may supply it. This is a proof of the modeled shim, not yet a source-correspondence or generic owner-transfer certificate for SmallSort; alignment, zero-size and intended negatives must be checked against the full contract.

[Actual body](https://github.com/Tiramisu-Cake/verify-rust-std/blob/c7ca8c467aecf10a4b53039372ee97714f854ee3/library/core/src/slice/sort/shared/smallsort.rs#L542) requires a valid initialized range and the source's strict begin/tail condition. Safety does not require a sorted prefix or lawful comparator ordering. After the first comparison, `tail.read()` transfers the owner into `ManuallyDrop`; after each shift, `gap_guard.dst` must designate the unique logical gap. The physical bytes left at the old location are not another owner. During later callbacks, `tmp` has a live shared borrow while the gap and guard invariant must remain recoverable.

Required branches are: early normal return; panic before the read/guard; arbitrary number of shifts; normal final guard Drop; late comparator panic followed by real compiler cleanup and guard Drop. Both returns must restore one initialized owner per range element, CURRENT callback/element resources, permissions, lifetimes and surrounding frame. A late callback may legally modify interior state: restoration cannot use an old byte/value snapshot. `T`'s payload must not be dropped by ManuallyDrop. Full unwind safety differs from sorting; an inconsistent comparator must remain memory-safe.

For [R5](https://github.com/Tiramisu-Cake/verify-rust-std/blob/c7ca8c467aecf10a4b53039372ee97714f854ee3/library/core/src/slice/sort/shared/smallsort.rs#L580), ZST pointer arithmetic makes `tail == v_end`, so the loop bypass requires its own caller-domain proof; forcing a synthetic ZST helper call is not proof of an actual path. No global `size_of(T)>0` restriction may be added to R5 safety. Generic ZST layout/resources and actual reachable domains remain explicit acceptance requirements.

**Answer:** the development revision can express the intended proof; there is no inspected artifact proving that it can complete it on this source/profile. The hypothesis is credible because spatial unwind posts and Drop glue are present. It remains conditional on (1) actual ManuallyDrop admission, (2) sound raw-operation/owner bridge, (3) FnMut exceptional current-state recovery, (4) nonvacuous guard invariant and compiler cleanup correspondence. These are proof and applicability tasks, not eliminated by foundational type-system soundness. Lack of slices subsequently blocks using the helper theorem in actual R5 without a separately reviewed tool extension.

## Сравнение с текущим VeriFast

Main's team STATUS is an index, not the latest merge proof. Read-only examination found the later [origin-layout checkpoint at `20548c2798115ba6f1ac0d7632aeddc11ea0e8a3`](https://github.com/Tiramisu-Cake/verify-rust-std/blob/20548c2798115ba6f1ac0d7632aeddc11ea0e8a3/research/challenge-8/cloud-build/origin-layout/FINAL-CHECKPOINT.md). Build `282324ae-a918-4bc6-b73b-e2861f2596e5`, proof/infra `a287a0f2d1b12e3a209b8d69cb66516acdd53f50`, freshly passed compiler/smokes/span controls and a bounded u64 CURRENT recovery fragment. The new guard controls did not run because ghost-fragment preparation failed. New len1/canonical interfaces and insertion caller are NOT_RUN, compiler Drop glue NOT_IMPLEMENTED, actual panic cleanup NOT_EXERCISED; profile NOT_ACCEPTED/NOT_FOR_INTEGRATION. [Len1 review](https://github.com/Tiramisu-Cake/verify-rust-std/blob/20548c2798115ba6f1ac0d7632aeddc11ea0e8a3/research/challenge-8/cloud-build/origin-layout/LEN1-INTERFACE-REVIEW-20261010.md) lists concrete admission debts. This is closer to the consumer than the October 9 summary, but not a generic theorem.

The prior [incoming-origin closeout](https://github.com/Tiramisu-Cake/verify-rust-std/blob/9da02971a162468cd06602585a0dcd4a1e8d67a1/research/challenge-8/merge/INCOMING-ORIGIN-CHECKPOINT-2026-10-09.md) keeps normal/unwind and generic/ZST extent gates open. Maintainer's [fullmake RESULT at `94cc873e6bf042d0ad2c3e7de8faa1cdf63cf136`](https://github.com/Tiramisu-Cake/verify-rust-std/blob/94cc873e6bf042d0ad2c3e7de8faa1cdf63cf136/research/challenge-8/cloud-build/verifast-mdnew-fullmake/RESULT.json) records make-test PASS, outer Cloud FAILURE and separate collector replay PASS. Neither suite nor replay supplies actual caller proof. Existing evidence was read, not independently replayed here.

| Проблема | Потенциальный выигрыш RR | Что сохраняется / цена смены |
| --- | --- | --- |
| Concrete extent/root admission debt | Layout-parametric typed storage and explicit lifetime logic may avoid VF-specific bridge patches | Need exact std layout/source correspondence, ZST branch coverage; abstract layout alone is insufficient |
| Generic own/bytes/current resources | Iris can express one-cell gap, abstract T and borrow recovery directly | Must prove resource conservation; `value_t` byte copies do not deliver ownership automatically |
| Canonical Drop interface and compiler glue | Existing Drop translator and exceptional spatial postcondition | Actual CopyOnDrop FBC/invariant applicability, normal/cleanup branches and CURRENT must still close |
| Stateful callback | Higher-order FnMut specifications and trait inclusion proofs | Exceptional resource/state contract must follow unrestricted legal callback semantics, not purity/Freeze assumptions |
| Arbitrary loop | Inductive block/loop rules and Rocq list lemmas | VF also supports invariants/induction; no established asymptotic advantage; new proofs must be written |
| Trusted tool patches | Rocq checks rule applications and automation outputs | rustc/translator, Radium semantics, shims/layout and logical axioms remain trusted; dependency closure can contain admits |
| End-to-end source and CI | Pinned Nix/opam/dependency builds and proof files | VF has working std/compiler infrastructure and existing project evidence. RR needs slices/union review, new tool admission and integration |

The fastest measured next VF obstacle is preparation repair before already-designed len1 gates; RR starts with new library and source-admission work. This favors continuing VF, without predicting that its remaining semantic obligations will be easy. RefinedRust's advantage is potentially better proof auditability and an expressive ownership foundation, not demonstrated speed. Combining RR and VF would additionally require a proved interpretation bridge between their predicates; a Rocq theorem is not automatically a VeriFast premise.

## Trust и proof engineering

Rocq checking reduces trust in tactics/type checking, not in the Rust-to-Radium translator or completeness of the semantics. [Adequacy](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/theories/refinedrust/rust_typing/typing/adequacy.v#L415) permits explicit unwind policy and treats abort as terminal divergence; it does not execute platform panic runtime. Our gate must use PanicUnwind/AllowUnwind and explicit spatial posts, not abort to avoid cleanup.

[README linking mode](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/README.md#L164) defaults to assuming callees without carrying their extra linking obligations. Enable `generate_linking_requirements = true` for every participating crate and discharge the closure. Proof text ending `Qed` is insufficient without inspecting assumptions. [Vec ghost resolution](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/stdlib/vec/extra_specs.v#L78) and [MiniVec extra specs](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/case_studies/minivec/extra_specs.v#L23) contain `Admitted`; this does not show all RR theorems unsound, but forbids unconditional reuse of those examples. `Abort.` abandons a Rocq proof and is not itself an admitted theorem. [Logical axioms](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/theories/refinedrust/rust_typing/base/axioms.v) include proof irrelevance/functional extensionality and belong in the trust ledger.

The [current validity model](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/theories/refinedrust/radium/validity.v) includes Bool/Char/Ref decoding and poisoned padding. The old paper's validity limitation must not be mechanically copied onto this revision. Nevertheless no correspondence audit here establishes all four challenge UB categories for arbitrary T, representation/layout or aliasing rules. Explicit safety posts and intended negatives are required; Iris's affine resource logic alone does not promise project-required no-loss ownership accounting.

Needed Rocq/Iris work: define generic range/gap/held-owner invariant; prove move/read/copy representation bridge and permissions; expose guard invariant at actual Drop; resolve shared held-reference and F borrow on both exits; prove indexed shift invariant/termination and CURRENT recovery; link actual callees/glue and adequacy; audit assumptions and source translation. Later R5 requires a separately accepted slice model, and scratch callers require actual MaybeUninit admission. Our own proofs must be developed; no external proof code is to be transplanted.

Planning estimate, **not measured**: with an experienced Rocq/Iris developer and existing tool image, 2–5 working days for admission/interface design, then 5–15 days for a useful non-Copy panic/guard POC and controls. Unknowns can invalidate this estimate immediately. Generic source/caller and slices/union integration have no defensible completion estimate without the early gates; full Challenge work is not included. Author benchmark timings are not our Cloud cost or a VF comparison.

## Versions и воспроизводимость

| Profile | Compiler / proof stack |
| --- | --- |
| Repository base | `rust-toolchain.toml`: nightly-2026-02-05; actual merge checkpoint above used nightly-2026-09-25, rustc `f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f`, x86_64 |
| RR development `332d945f…` | [toolchain](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/rr_frontend/rust-toolchain.toml): nightly-2026-08-28, rustc-dev/LLVM; [opam](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/theories/refinedrust.opam): Rocq core 9.2.0, stdlib 9.1.0, Equations 1.3.2+9.2, Dune ≥3.23.1; README OCaml 4.14.2+flambda |
| RR July v2 archive | Static metadata: nightly-2026-06-29; Rocq core 9.1.1, stdlib 9.0.0, Equations 1.3.1+9.1, Dune ≥3.21.0; this is not development unwind profile |

Development opam pins: stdpp `729c671ed573749588f699138e306dbae880f3e1`; Iris `4a6add171278417fec6da7c490fe487e502326f0`; iris-contrib `0ed8e45b554b2c7f7b9102818bc3ee27d8fa18b8`; lifetime logic `0a062fb1eb68f9a6ac38412347117b294fc7746b`. [flake.lock](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/flake.lock) blob `83033d4b013c0167a9b7226b14f8644753db621f`, SHA256 `eeee3f5cd5f21378c0d146d92b1dd06135b8043f25d323436ef1c26974d6bad1`. Nix and opam are alternative dependency profiles; do not mix their pins silently.

Compiler plugin uses rustc internals. Compatibility with February std and September project verifier nightly is **NOT_TESTED**; substituting its compiler is a new profile decision, not a config convenience. Prefer RR's own nightly for a separately pinned exact-source admission probe; never change the repository's global toolchain. A successful isolated compilation still would not demonstrate complete core/std integration.

CI is technically plausible via headless `cargo refinedrust` → Rocq/Dune → linking/assumption audit. [Current GitLab config](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/.gitlab-ci.yml) has pinned build paths, but ACE job is allow_failure and prunes named modules; copying its green status is not acceptance. July artifact instructions request ≥16 GB RAM for all proofs. For our isolated proposed job use ≥16 GB, preferably 32 GB, fixed jobs and stage timing; cold build cost is unknown. A digest-pinned image must be built/audited separately for the development commit, not assumed from the July archive. No image, lane, trigger or CI change was made.

At the [pinned project tools list](https://github.com/Tiramisu-Cake/verify-rust-std/blob/c7ca8c467aecf10a4b53039372ee97714f854ee3/doc/src/tools.md), RR is absent. [General rules](https://github.com/Tiramisu-Cake/verify-rust-std/blob/c7ca8c467aecf10a4b53039372ee97714f854ee3/doc/src/general-rules.md#tool-applications) require separate application and integration. A sensible future application needs actual source evidence, complete domain/UB coverage explanation, assumption ledger and reproducible automated check. This mission prepares that decision and does not initiate it.

## Условия пересмотра рекомендации

Move from CONDITIONAL to GO for further research only after an exact-source non-Copy/current-state comparator panic case proves actual guard/glue recovery with complete resources and intended negatives, under unchanged RR semantics with reviewed primitive correspondence. This still is not full Challenge GO. A generic arbitrary-length helper theorem plus an accepted actual slice-caller path and measured iteration cost are required before migration is justified. Any need for new union/slice/closure semantics returns to the owner as a new trust/scope decision. Until then the next action is review of this packet; all Cloud experiments remain proposals.


## Network N6 update — 2026-10-23

**INCONCLUSIVE: pre-dispatch setup boundary; frontend/proof NOT_RUN; Cloud0s.**
The G1 package was transferred from feasibility commit68671873 into the Network
branch and rebound to preferred std cd371e0. All seven anchors are unique; exact
selected insert_tail and CopyOnDrop bodies match the frozen source. RR stays
unpatched at332d945f with nightly-2026-08-28. No migration, frontend patch, new
trusted premise or readiness-index change is introduced.

The inherited offline cold context and registry destination are not frozen;
compatible immutable image/receipt remains unknown. Read-only registry listing
and direct lookup were denied to the dispatcher; builder access is UNKNOWN.
No Build or frontend rejection is inferred. The fresh account/recipe is
PREPARED_NOT_REGISTERED. Exact identities, observations and prerequisites are
in [RR-G1-RESULT](RR-G1-RESULT.md); independent review is recorded separately.
The original feasibility branch/report remains unchanged.


## Network N7 update — 2026-10-23 UTC

Owner clarification, 2026-10-24: [N7 cold-attempt accounting](N7-COLD-ATTEMPT-OWNER-UPDATE.md)
records **0 cold attempts and 2 infrastructure/setup Builds**. Neither reached
Dockerfile execution; the admission-limit interpretation in the historical report
below is superseded. The closed account and INCONCLUSIVE/G1 NOT_RUN verdict stand.

**INCONCLUSIVE after two authorized cold Builds; G1 frontend NOT_RUN, credit0.**
Online Artifact Registry route is implemented/reviewed. First cold Build
efd32c5f EXPIRED before execution (297s, Brief404); changed setup repair3e604123
failed at Docker API1.52 vs daemon maximum1.41, cold exit1 (94s). Exact Brief
log/status/audit identities are in [RR-G1-RESULT](RR-G1-RESULT.md). Total391s
spent,5009s retired/carry0. No image freeze, RR rejection, finite missing-spec
list or cleanup-generation result was obtained. No third cold Build withinN7.
N6 remains in N6-RR-G1-RESULT.md; original feasibility branch unchanged.
