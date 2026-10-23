# Минимальный Cloud POC: actual insert_tail → one-cell Drop

**PROPOSAL / NOT_RUN.** Текущая миссия: Cloud budget 0, разрешённых lanes нет. Ни этот документ, ни имена ниже не регистрируют lane, account или phase. Любые compiler/extraction/proof команды выполняются только после нового поручения владельца в reviewed Cloud checkout. Runtime std, общий план и существующая инфраструктура этой миссией не меняются.

## Вопрос, hypothesis и consumer

Actual obligation: `insert_tail<T,F>` возвращает полный initialized owning range и CURRENT callback/element resources на normal и comparator-unwind exits, включая actual `CopyOnDrop::drop` и compiler glue. Consumer: actual `insertion_sort_shift_left` → default/fallback SmallSort; отдельный scratch caller `small_sort_general_with_scratch` использует insertion до своего count-n guard. Его поздний guard не защищает этот узел.

Hypothesis H: на RR development `332d945fafa14bf55c0c8390cb35ec4b0c012cff` можно admit actual helper/guard и доказать one-cell recovery через существующие resource unwind posts, без изменения Radium/translator/type rules и без ограничения safety `T: Copy/Freeze` или comparator purity/no-panic. Фальсификатор — конкретный unsupported API/source operation, невыполнимый resource interface или intended proof obligation, требующий новой trusted semantics. Отрицательный admission result полезен: прекращает POC до затрат на сортировку/CI.

Это проверка feasibility, не выполнение W3 или перенос владения миссией merge. No generic insertion caller / full Challenge credit until their actual source paths are verified. No VeriFast summary is imported as a premise.

## Замороженные inputs и предварительный G0

| Input | Предложенный pin / gate |
| --- | --- |
| Std source | base `c7ca8c467aecf10a4b53039372ee97714f854ee3`, SmallSort blob `e555fce440872898e47fd5114f32eb15401d07df`, SHA256 `32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`; helper L542–578, guard L295–309 |
| Proof/infra source | Новые полные опубликованные SHA своей будущей ветки; сейчас отсутствуют. Recipe включает точную closure источников, собственных specs и primitive correspondence certificates |
| RR | `332d945fafa14bf55c0c8390cb35ec4b0c012cff`, без патчей. Изменение commit/profile — отдельное решение; July artifact не доказывает новую unwind поддержку |
| Compiler | nightly-2026-08-28, rustc-dev/LLVM из RR toolchain. В Cloud снять `rustc -Vv`, compiler commit/target/config. Совместимость с фактическим repository source — первый gate, не предположение |
| Proof stack | Rocq 9.2.0 / stdlib 9.1.0 / Equations 1.3.2+9.2; reviewed Dune 3.23.1 / OCaml 4.14.2+flambda и dependency pins из report. Если выбран Nix, отдельно зафиксировать фактические versions из flake derivations вместо смешения с opam |
| Configuration | x86_64-unknown-linux-gnu, debug assertions/overflow settings recorded, `panic=unwind`; Radium PanicUnwind / adequacy AllowUnwind; `generate_linking_requirements=true` во всех участвующих crates |
| Dependency image | Digest и полный manifest **TBD** до dispatch. Cold preparation отдельно согласуется; mutable tag/JULY image не substitute. Source/patch/compiler/deps/platform/config должны входить в key |

G0 — без запуска: review exact source/dependency closure, всех используемых RR shims и переходов byte-value ↔ generic ownership. Сначала сформулировать actual ManuallyDrop constructor/Deref/drop-suppression contract, ptr read/copy/sub contracts и callback exceptional recovery. Каждый summary либо theorem actual callee той же source revision, либо явно reviewed primitive modeling boundary с correspondence и сохраняющими ограничения controls; подменять обычный std callee assumed `only_spec` нельзя. Нужная новая shim/семантика, невозможность закрыть admits или более сильная FnMut premise → STOP и новый trust decision, не silent implementation.

Не начинать общий core build только ради thin-pointer helper: Cloud extraction выбирает actual helper, guard, Drop body и необходимые callees, без переписывания generic signatures. Аннотации допустимы только при точном ghost-strip equality исходных bodies и сохранении MIR/layout/cleanup/source mapping. Изолированный translation unit — diagnostic actual body, не whole-core proof. Unsupported `ManuallyDrop` фиксируется как admission refusal. Unsupported slices/union уже известны: обойти их переписанным Vec caller для acceptance нельзя.

## Domain и конечные posts

Final helper contract: arbitrary initialized valid T, legal stateful `F: FnMut(&T,&T)->bool`, source-defined begin/tail safety premises, allocation/provenance/alignment/bounds and exclusive range resources. Full safety requires no sorted prefix/order premise. Domain is caller-reachable; logical indices and physical pointers are related explicitly, not by numeric inequality alone. Не вводить fixed length/cutoff для конечного theorem.

R5 target retains all valid lengths and `1 <= offset <= len`; invalid offset leads to actual abort and must be classified separately. ZST is an explicit caller path: equal `tail/v_end` skips the loop, with full resources returned. Вызов insert_tail на ZST с недоказанной strict-address premise не считается actual reachability. Fixed-width primitive diagnostics do not discharge generic/ZST safety.

Normal post N: complete initialized range with exactly one logical owner per live element, current F resources, write/share permissions and outside frame; held owner restored into final gap; temporary/guard storage and borrows closed, no unintended T payload Drop. Early return has the same ownership guarantees without tmp/guard. Sorting/old-value permutation are separate functional contracts, requiring sufficient ordering/effect premises; interior-mutating comparator safety does not promise unchanged payloads.

Unwind post U: at first comparator panic, recover intact owning range and CURRENT F/T state without a nonexistent guard. At later panic, actual cleanup executes CopyOnDrop and restores CURRENT held representation/owner to the current gap; all range cells initialized and uniquely owned, current F ownership/frame returned and temporary borrow/storage obligations closed. No sortedness or old-value restoration promised. Both posts must account for all resources, not an Iris `True` post that forgets owners. Terminal abort/double-panic classification is separate; it cannot replace ordinary comparator unwind.

## Минимальная последовательность

| Gate | Что выполняет будущий Cloud Build | PASS / следующий шаг | FAIL / решение |
| --- | --- | --- | --- |
| G1 environment/admission | Version/hash preflight; recheck one small existing foundational control in its exact dependency closure; generate source-linked actual guard/helper MIR/Radium with cleanup present; check source/layout/callee maps | Tool environment and selected body admission only; перейти к G2 | Setup error: один routine fix в будущей allowlist. Missing API, erased cleanup, compiler incompatibility, new semantics needed: checkpoint STOP |
| G2 one-cell semantic probe | Собственный contract/invariant; actual guard Drop and glue; actual helper instantiated on `[Token; 3]` with non-Copy payload, legal interior mutation and verified stateful comparator. Cases: early return, first panic, ≥1 shift then late panic, normal final cleanup | Full diagnostic N/U and controls, linked actual callees, complete assumptions report; оценить цену G3 | Intended ownership/borrow/CURRENT failure: record first causal blocker. No green by weakening contract. После одного содержательного отказа без новой evidence не повторять |
| G3 generic helper | Prove inner loop inductively for arbitrary reachable range, generic non-Copy T/F, current resource accounting and guard on both exits; complete generic layouts and relevant ZST applicability | Generic helper theorem; **still not R5**. Present evidence and measured iteration cost to owner | New alias/layout/closure semantic extension or unclosed generic premise: STOP; bounded G2 remains diagnostic |
| G4 actual consumer, separate decision | Exact actual R5 `&mut [T]`, outer invariant/arbitrary length, ZST/valid-offset/abort paths; later fallback composition | Prerequisite before migration discussion | Current Slice refusal means this gate cannot pass stock inspected frontend. Requires separately authorized model/tool work; no wrapper substitute |

G1/G2 are the minimum actionable POC; G3/G4 are explicit later boundaries, not requested executions. A built-in control with admitted/assumed external specs only demonstrates setup: it must not supply target premises or be labeled a foundational closed proof.

Token suggestion: own synthetic non-Copy struct with stable logical identity, a `Cell`-style mutable field and a verified resource-observable Drop. Avoid allocation/Vec dependencies initially. Exact field APIs and layout must be admitted without axiomatized effect summaries. Comparator mutates held field and F counter, then either returns arbitrary bool or panics at first/later invocation. All implementations are our own. A terminal unwind post is inspected directly in the logic; adding assumed `catch_unwind` is unnecessary and prohibited as a substitute. Sentinel destructive T Drop while shifting must never execute; normal caller Drop after restored ownership may execute exactly once per owner.

## Controls и intended locations

Synthetic controls are isolated alternative fixtures, never mutations of actual runtime std. They share successful admission with positive fixture before proof verdict is counted.

| Negative | Intended rejection |
| --- | --- |
| No valid source/owner token for `tail.read` | Resource precondition at actual modeled read/move, not parse failure |
| No write permission / wrong alignment / out-of-allocation read | Permission, layout or bounds predicate at corresponding typed operation; record exact MIR/Radium node |
| Byte-copy alias/overlap passed as nonoverlap | Primitive nonoverlap obligation at copy. If stock shim has no adequate check/certificate, G0 fails; do not claim a matched negative |
| Guard destination kept at old tail after shift | Resource relation or restored-range post at cleanup copy; branch must reach later panic and real Drop |
| Restore pre-comparison snapshot after legal interior mutation | CURRENT observation/post at restoration, including F state |
| Duplicate owner for bytes remaining at source | Ownership-conservation post; byte equality must not produce `T.own` |
| Suppress actual cleanup or drop tmp payload twice | Linked guard/glue resource post and verified payload Drop accounting, with source mapping intact for synthetic negative |
| Typed invalid bool/reference representation or uninitialized read | Validity/init obligation at typed decode/read; unrelated failures do not count |

Positive reachability witnesses: comparison false before read; ≥1 shift; second comparator; normal guard exit; first and late unwind; CURRENT mutation; non-Copy owner. These are source-linked paths, not merely grep markers. G3 additionally proves invariant preservation for symbolic index/length. Leak/owner loss, dead code/vacuity, initialization, validity, alias/permission, overflow and refinement/source gates remain enabled. A proof assistant accepting an inconsistent precondition is not nonvacuity evidence.

## Бюджет, configuration и stop criteria

All numbers below are **planning ceilings, not authorizations or measurements**. Charge uses createTime→finishTime, including queue/setup/upload; execution duration is reported separately. Monetary cost is not estimated without chosen provider machine/rates.

- Minimal warm-image G1/G2 campaign: propose **3600 Cloud seconds**, at most two sequential Builds. Each existing-style reservation ≤1800 seconds, e.g. timeout 1740 + queue envelope 60. One initial G1/G2 combined run, one evidence-driven repair only. Stop after G1 if unsupported API/source boundary makes G2 impossible.
- If no compatible digest-pinned development image exists, cold setup is a **separate proposed preparation account up to 7200 Cloud seconds**, with a separately reviewed timeout/lane and window. It must not consume a historical account or borrow a peer ledger. This is not a claim cold setup will finish; timeout is INCONCLUSIVE. Owner can choose a smaller admission-only run instead.
- Propose ≥16 GB RAM (prefer 32 GB), 4–8 vCPU, ≥40 GB disposable disk, `DUNE_JOBS=1` initially and bounded proof parallelism. Record actual peak RSS and timings before increasing jobs. Do not run full ACE or whole RR regression suite for this isolated target; run relevant primitive/cleanup/assumption controls.
- G3 budget is **not included**; after G2, estimate it from measured frontend/Rocq times and remaining proof design. No repeated cold builds to test documentation/classifier changes.

Before any submit, owner must name new phase, stable identity for this independent mission, own absolute ledger/state, window, ceiling and reviewed allowed lane/recipe. Suggested labels `refinedrust-admission` / `refinedrust-onecell` are descriptive only; none exists or is registered. Preserve [v2 max-two, one-per-owner/ledger](../cloud-build/PARALLEL-BUILDS.md); do not alias select-sort4, merge or verifast. Use existing dispatcher admission, reconcile unknown response without duplicate submit, record exact published proof/infra SHAs/config/certificate and independently inspect complete evidence. No direct gcloud workaround, Actions dispatch or trigger change.

STOP at: domain strengthening; no closure of actual callee/glue or assumed exceptional ownership; necessary trusted semantic patch/new model; slices/union bypass required for actual consumer; unresolved API response; OOM/timeout/insufficient evidence; exhausted ceiling/deadline; repeated causal failure without new hypothesis. Setup/frontend/unsupported-operation failure is INCONCLUSIVE for a requested proof negative, while still a feasibility blocker. Archive and checkpoint all failures; do not convert them into PASS with an auditor change.

## Acceptance и deliverables будущего запуска

G2 acceptance requires exact actual helper/guard/glue identity, complete stated N/U in the **diagnostic domain**, verified comparator/payload bodies, intended positives/negatives at recorded nodes, closed linking requirements and assumption closure without admitted resource/source bridges. Dependency axioms must be enumerated (`Print Assumptions` plus kernel check of compiled artifacts), with project approval distinct from proof status. A `Qed` file, frontend SUCCESS, collector SUCCESS or successful archive upload alone is insufficient.

Evidence: Build ID/token; tool/compiler/profile and source/proof/infra SHA; image digest/dependency manifest; source-strip/MIR/Radium maps; full proof logs; assumption/callee closure; exact negative stage/predicate/location; archive/config/input/file hashes and receipt; stage wall time/peak RSS; conservative ledger charge. Keep generated source/logs/build outputs outside Git, under the future evidence store. Commit only own specifications/proofs and concise evidence records under this research directory.

After G2, compare actual progress and engineering/Cloud cost with the VF len1/canonical checkpoint. Recommend further RR work only if source-linked CURRENT panic recovery succeeds without new trust/domain debt and the blocked actual slice-caller path has a separately reviewable solution. Tool Application remains deferred until generic/source/CI evidence is sufficient. Current authorized final action is documentation commit and ordinary push of our branch, then STOP.
