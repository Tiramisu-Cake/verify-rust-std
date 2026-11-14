# Targeted CI request — QUALIFICATION_PENDING

Candidate source `61eb057b46e2ffd62df28c3e956cd8031ed84748`, tree `712b560e63097fc36e4866572aa22af347a100c0`.

Exact source SHA/tree + file hashes: parent C2-FREEZE.json / EXPORT-MANIFEST.json.
No worker local builds/formatter/proofs, push, PR, CI or dispatch. Use existing bounded
Linux infrastructure and fixed nightly/CBMC/Kissat/deps, all normal checks and fixture
object-bits12. No full kani-regression.sh, new workflow, Gate A or SmallSort/SEL1 replay.

1. fmt/build/clippy on exact candidate; new typed_marker_categories_remain_distinct
   unit; existing S2 registration9, S4 delayed_cache6/delayed_scope2 units.
2. Matched baseline8d + candidate observations of SAME exported ordinary-hook-return.rs
   and fn-item-shadow-return.rs. New useful assertions differ from historical repros.
   Kani flags and --keep-temps BEFORE --cbmc-args; --emit mir in observation RUSTFLAGS.
   Record input/tool/source/tree/argv identities, actual instance kind/body/FnAbi,
   normal call target, complete failures, own useful SUCCESS and exits. Baseline hook
   must reproduce sole internal load_argument placeholder N1; candidate must replace
   with sole explicit pairing Unsupported N1. FnDef plain N0/shadow N1 must retain
   actual FnOnce call_once shim, not optimized Item, tuple/layout or pointer path.
3. All17 new expected selectors in DISCOVERY-INVENTORY.json; native compiletest
   --force-rerun for repeats. Exact failure N/named function/status/description,
   useful SUCCESS, summary and selected root completion must match. No bless,
   --fix-expected, skipped selectors or check-disable workaround. Actual scalar hook
   must reach destination37/source37; generated modifies(out) is only legal noncarrier.
   Actual Model and unknown-marker true/hole pairs must preserve ordinary protocol.
4. Bounded MIR/operation review on candidate: hooked MU call has explicit refusal
   before Begin/Store/return LoadArgument, no snapshots/deinit; operand checks and B1
   flush preserved. Ordinary paired companions retain caller stores/load, callee
   entry loads/return store. Copy both operands SAME place and Copy, distinct indices;
   original-source preservation. Padded actual stride/offset, cross-slot extent and
   intended final DATA byte through borrowed/raw slice, never invalid &[Padded].
5. Ordinary/PFC/contracts generation/helpers, quantifier/arbitrary, existing Uninit
   kani/expected/ui/script, S2/S3/S4 controls, all remaining upstream JSON-handler,
   then SAME existing bounded Linux Quick. S5 totals kani24/expected228/ui17/script2/
   json17 are historical only; preserve two pre-existing ignored fixmes, no new skips.
6. Revalidate four unchanged S5 sensitivity patches using c2-s5/SENSITIVITY-MANIFEST.json
   and c2-s5/sensitivity (sibling research package). Actual --force-rerun, separate
   mutation outputs, same built tools. Compile/setup errors, cached/ignored runs or
   unrelated Unsupported are INVALID sensitivity evidence.

New admitted-path regression, non-discriminating control, unexpected failure/count,
missing useful success or unexplained failure => STOP with exact repro; no new boundary
blessing. Capture receipts against exact immutable SHA. Prior S5 CI does not qualify
this predicate delta. Gate A3-platform is NOT_RUN, separate coordinator step.
