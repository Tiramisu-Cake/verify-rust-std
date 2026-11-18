# W11 independent confirmation readiness review

**APPROVE — confirmation-only readiness. Blocking findings: 0.**

Issued review task: `taskbbae71320b721ee3bb373b3b1177071266c16512`, owner 21:44 in `/new11`. The owner's issuance supersedes the task file's PREPARED_NOT_ISSUED marker. Reviewed package: `5ba4f444f6fa1882b4eb6ac6d773f76cfc9c6531`, author task `task9582039593814a2b67b3ca6377c5f165e92dfa1f`. The shared g0 starting head was `2906a5b6d3b8451e5b49417714f75e3f9a4af148`; its unrelated S2 commit was preserved. W14 and active S2/F4 paths were untouched.

## Exact inputs and isolation

- STOCK main: `faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`; tree `09b828b47c93e90e140e8c41f9048109a2f4a786`; sole parent `a3c8b8610739aab7d2c864bd4021086a5e7c0d94`.
- Control: `1253186ae87e079758ab573f50ba305a028f8963`; tree `507f9a07bc6fb4eca26706ea0fde32612731fbe2`; sole parent STOCK main. Both source/control worktrees are clean and nonshallow. The isolated temporary-index replay of `control.patch` produced the exact control tree.
- Request: `21749d215a2851d971e58f16727d7589af3468adffe086afa4a558cf026841c4`; profile: `9f230f8fac56230a468f043e294bc77a745b50d5a16a47a7857eb0be4af5cae5`; workflow: `0a537ae2e8f74f5864324237f761b2fe3b6a07982216b2e82ad9feca06d6011c`.
- Control patch: `915b02209ce2f8439c71239856b02aef6c58486236301f9e23902323b12608a4`; separate clear-error candidate: `d3221b7ed70707ae39c479eed0bccc1f89f25e5ae5215356a117a8b7f718be08`.

All 31 package files match committed bytes; all 30 manifest entries match sizes and SHA256. Source/object hashes and the request's canonical binding pass. A fresh read-only upstream main advertisement matches the frozen head. The control changes contain fixture/automation only; compiler, driver, library, toolchain and root lockfile have no delta. STOCK's script resolves its own driver; that driver resolves its sibling compiler, independently of the fixture checkout. Fix applicability was checked in a temporary index only.

## Mechanism, semantics and fixture

Independently inspected exact-main `transform/mod.rs:115–123,152–180`, `stubs.rs:46–55,145–155`, `contracts.rs:333–350,569–587,660–734`, `codegen_units.rs:244–299,316–328`, provider registration in `kani_middle/mod.rs:87–135`, and contract bootstrap/initialization. FnStubPass returns g's checked body; later passes retain f's instance. Contract mode reads f's attributes, and mark_unused looks up all four original closure names in the supplied body, starting with the recursion closure. This supports the stated conditional mechanism. It establishes neither native reproduction nor a recursion-mode execution. The precise historical S2 failing unit/body remains UNKNOWN.

`stubbing.md:19–37,159–164` documents replacement and feature coexistence. It leaves contracted-target precedence unresolved and does not document this combination as deliberately unsupported. The report correctly distinguishes those documented facts from source inference and policy recommendations. Provider registration checks existence, not proof validity; the packet additionally requires a separately successful PFC invocation.

The single standalone workspace has no dependencies. The always-present provider is compiled independently of the feature-gated verified and ordinary harnesses. Each invocation selects one exact harness, one explicit feature and a fresh target/export directory. For symbolic `u8` x under x<8, f returns x+1 while g returns x+2. The ordinary assertion cannot pass by calling f's original body. The provider must prove the x+1 postcondition; the verified control must prove f(x)==x+1. Selection/feature isolation keeps an ordinary compilation failure from suppressing those observations.

Clean-room coding inputs remain upstream main plus own analysis/automation. No third-party patch/PR code was consulted for this review. No verify-rust-std dependency, F4 tool patch or fixed compiler is included in the confirmation workflow. Provenance of the author's preparation beyond the committed materials remains a source-reported statement.

## Runner, workflow and evidence

The workflow checks out STOCK separately at its exact head and uses depth 2 for both checkouts. The synthetic shallow test verifies parent visibility and rejects an inadequate source checkout. Runtime snapshot gates bind heads, trees, sole parents, profile files and canonical request; tracked mutations and untracked source are rejected. Build occurs in STOCK. Native argv agrees with CI-REQUEST after path substitution; invocation identities include fixture/manifest digests, feature, target, environment and request. Built compiler/driver/tool hashes are captured before/after; tool drift is inconclusive.

Setup action outcome, compiler build process and three proof slots remain separate. The collector preserves every completed slot and continues after target/control errors. A failed build leaves proof slots NOT_RUN; finish records setup/job failure and emits a compact result. Timeouts, RSS/output caps, spawn errors, incomplete streams/diagnostics and missing evidence withhold credit. Per-process address space and sampled process-group RSS caps are 8 GiB; build is 900 seconds; each native slot is 120 seconds; setup/job are 30/60 minutes; retries are zero. RSS sampling is a bounded operational control, not a proof that transient peaks cannot exceed the cap.

Diagnostics are extracted from bounded streams independently of head/tail previews, with block digests and explicit completeness. Any exceeded stream/block/count cap makes the outcome inconclusive. Exit, signal and bounded compiler-process hints survive. Successful exports require exact selection, complete run/target, checks enabled, full successful property inventory and the distinguishing semantic assertion. An exact missing-closure error requires no export or verification inventory, complete diagnostics, and no other primary compiler error.

| Synthetic condition | Required and observed classification |
| --- | --- |
| Successful controls + exact ordinary missing closure | DEFECT_PRESENT |
| Successful controls + distinguishable ordinary assertion success | DEFECT_ABSENT for this fixture |
| Explicit unsupported diagnostic | INCONCLUSIVE with separate EXPLICIT_UNSUPPORTED behavior |
| Missing/failed provider or verified control | INCONCLUSIVE |
| Wrong target/closure, generic or additional compiler error | INCONCLUSIVE |
| Partial/malformed/oversized export, timeout/RSS/output cap, spawn failure | INCONCLUSIVE |

The compact artifact's digest can be recomputed, successful observations can be replayed, and error cases can be conservatively reclassified from diagnostics plus export inventory. Replay must inspect `export_inventory.present`: an unretained partial/invalid export must never be treated as an absent export. The first review-test attempt omitted this inventory check and failed on partial-export replay; the corrected reviewer test passes. The producer already retained the presence flag and returned INCONCLUSIVE, so this was a reviewer-test correction, not a package defect. The initial traceback is retained in `review-test-development.stderr.txt`.

## Separate fix-policy assessment

The clear-error patch is a coherent minimal restriction policy: reject contracted originals in ordinary maps before transformation, document the restriction and require the new diagnostic in an upstream UI test. It leaves verified/PFC/recursive/unstubbed algorithms and ordinary noncontracted originals unchanged. It avoids global missing-closure suppression. The patch applies cleanly to exact main, and its regression's expected main-fail/fixed-pass behavior is source-derived. Compilation, regression correctness and preservation across the required matrix remain NOT_RUN.

A support implementation needs a defined original-versus-selected-body contract policy and explicit PFC/verified overlap handling. This review approves preparation of the STOCK confirmation request only. It does not choose or approve a compiler-fix policy, fixed-branch CI or tool PR.

## Validation and handoff

`author-validation.json`: PASS, including the author's 71 counted oracle mutations, bounded Python process controls, source preflight, schema and patch checks. `independent-validation.json`: PASS, 125 checks including exact committed inventory, temporary control-tree replay, runtime request/cap parity, additional oracle rejection cases, seven three-slot artifact-replay cases and setup-finalization mocks. All execution was Git/static/Python/mock; no compiler, cargo, rustc, Kani, CBMC, native expansion or full runner was executed.

Main/fixed compilation, MIR, native MRE and CI confirmation remain **NOT_RUN**. Independent proof credit: NONE. APPROVE permits root GO-request preparation only. The thirtieth item1 confirmation still requires separate owner/coordinator GO and coordinator-owned slot/accounting. Item1 29/30, item2 10/17 and total39/47 remain unchanged references. No dispatch, publication, push, PR, issue, ledger/budget/reservation operation occurred. Settings/model/reasoning/tier and Fast OFF were preserved. No subagents were used.
