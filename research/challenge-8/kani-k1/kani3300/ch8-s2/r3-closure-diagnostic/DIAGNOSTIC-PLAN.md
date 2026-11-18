# Smallest discriminating follow-up — review14 / separate GO

**NOT_APPLIED / NOT_RUN.** The machine-readable recipes, exact edit strings, inherited pins/flags, and recipe SHA256s are in DIAGNOSTIC-PLAN.json. Recipe hashes identify proposals, not executed source commits. Current task authorizes no compiler, runner, CI, source/tool patch, request change, reservation or ledger update.

First pair: **V-W** selects only `sorting_s2_batch::sort13_weak` on exact S2/stock tool, retaining all compiled providers. **V-R** selects the same root and removes only `#[kani::stub(swap_if_less,weak_swap)]` at batch.rs:143. No contract/old/domain/frame/body/fixture change. The observed full11 R3 compile failure remains the owner-reported baseline; do not spend a broad rerun to rediscover it.

| Observation | Interpretation / next boundary |
|---|---|
| W same swap recursion miss, R gets past swap lookup | ordinary replacement is necessary for this reproducer; strongest source-supported explanation is original attrs + weak body. Bounded V-I may establish the actual event and distinguish any stub-induced metadata effect. Stop here; no old-free sweep. |
| W and R same miss, confirmed original-body identity in R | ordinary stub mismatch cannot explain R; investigate original body with PFC V-P and conditional V-O. |
| W compiles or no swap instance visited | full batch failure not isolated by W; root/provider/instance identity UNKNOWN. Select V-P or obtain V-I under new review/GO; do not call normalization fixed. |
| a different closure/function fails | record it separately; do not merge it with swap. general32_weak has merge and sort8 analogues; general32_assumed also ordinarily stubs the S2-contracted sort8. |
| any variant times out, diagnostic truncates, or reaches first root | stop branch; UNKNOWN or execution result as observed, accounting decision required. |

**V-P** is exact S2 `swap_pfc` alone, no source edits, no ordinary swap stub, SimpleCheck expected. **V-O** changes only its swap ensures `old(capture(...))` to `capture(...)`. This is an intentionally weaker relation for diagnosis, with existing harness-owned entry snapshot/exact-transfer and frame assertions preserved. It cannot replace reusable old-state contract or qualify assumed consumers. P fail/O pass supports an old-sensitive metadata interaction, but neither says which Rust MIR pass caused it. P/O same failure makes old unnecessary for this reproducer. Never test V-O first in the weak-stub configuration: Hstub predicts failure with or without old and the test would not discriminate.

**S1 anchor V-A / S2 anchor V-B:** same existing `helper_contracts::swap_safety_u8_backing13`, whose entire file bytes match at A/S. Both select one PFC with arbitrary_less fn-item, initialized13 backing, same flags/cfg and stock tool. Pair relation specialization is inactive for that F on S2. This avoids pretending S2-only `swap_pfc` exists on S1. These are revision baselines with multiple deltas, explicitly **not** an old-only causal pair. Use only if the first pair/original-body diagnostic leaves S1-vs-S2 or active-vs-inactive model dependence material. Acceptance of S1 at another configuration is not a compile observation here.

## Root/provider minimum

The smallest non-mutating reproducer uses **one exact selected root**, its transitive model/comparator dependencies, and all existing provider declarations unchanged. `--exact` filtering does not stop other declarations being parsed/attribute-checked, but stock selection and reachability do not automatically transform every provider. PFC/verified registration is not proof credit. Need no provider pruning to test ordinary-stub pass precedence.

If declaration checking itself blocks that pair, prepare a separate **one-root/one-provider cfg fixture** only after review of this finding: retain actual swap's exact signature/body, all five safety predicates and two-address modifies, exact active/inactive pair facade, KeyLess dependency where needed, and one matching PFC registration. Gate all other harness declarations rather than deleting requirements or model branches. Validate extraction bytes, matching actual body and cfg/host identities before proposing execution. Source/provider minimization is its own factor, not bundled with old removal. This fallback has no materialized identity or GO; stop at its preparation/review boundary. Removing controls for minimization never admits a production result.

## Necessary bounded observations

Existing source trace points identify function/mode/stub selection (`contracts.rs:324`, `stubs.rs:53`, `contracts.rs:458`), but do not print the debug entries needed for a causal claim. If available stock traces are insufficient, V-I proposes observation-only instrumentation: preserve all code/error paths; record at most4 target events/8192 bytes,16 exact-name matches and8 nearby names. Include request/source/tool identities, selected unit harnesses/stub map, original and replacement instance identities/generic args, expected names/mode, pre/post FnStub body provenance and relevant var_debug_info (name, Place/Const, resolved type/ClosureDef/scope). Do not print a full MIR/log. Mark overflow/truncation UNKNOWN.

A paired pre/post body observation distinguishes: (Hstub) original debug closure exists but substituted body lacks it while original attrs persist; (Hname/type) same-name entries exist but are not Closure typed; (Hbody) expected entry is only in another owner/scope; (Hmir) entry is already missing before ordinary substitution. Hmir still does not identify an optimizer or prove source-generation omission. No reported source expands to observed MIR without this new evidence. All instrumentation is future DESIGN DATA; no tool edits or executable expansion here.

## Factors excluded until motivated

Modifies is identical A/S; its role in Check wrapper and Replace havoc is traced, but deleting it would weaken frame checks and is not needed to distinguish Hstub. Generic T/F and unsafe fn are also identical; stock naming/bootstrap has no conditional branch on them. No Cartesian matrix, unsafe removal, T/F monomorphization rewrite, optimization flag sweep, or broad solver sweep is justified now. Such a next factor requires fresh bounded evidence identifying the relevant body/type stage, a one-factor diff and new review/GO.

## Controls, caps, charging and stop conditions

Each execution needs independent review14 of full candidate source/tool/config/request hashes and **separate GO**. Max1 in flight, no retry, at most7 conditional executions total in this design; normally stop after the first discriminating pair. Inherit compile cap900s and RSS6291456KiB; diagnostic output8192 bytes. No current budget is reserved or spent. Stop before proof roots using an independently reviewed compile-only stage if supported. Do not invent a Kani compile-only command or silently modify runner to obtain this. If that stage cannot enforce stop, GO must first decide root-start accounting and its execution cap; current no-run authority stays intact.

Only **confirmed compile failure before first root** may qualify0. Compile success/stage-stop, timeout, partial/unknown root status or root start is not promised free. Preserve real time/cost regardless of charge; current ledger remains untouched. Compilation success only removes a setup obstruction; it is not a PFC PASS or root proof. Any future production remedy requires full exact-transfer/frame/init/domain/negative-control validation, preserved S1/nonS2 behavior and root-qualified evidence before admission. Do not remove weak negative roots to claim all11 started. R1 diagnostic remains UNKNOWN.
