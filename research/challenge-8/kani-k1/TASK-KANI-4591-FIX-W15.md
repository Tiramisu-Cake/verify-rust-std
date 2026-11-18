# W15 — support ordinary stubs of contracted targets, Resolves #4591

ISSUED owner, fresh /new15/current settings/Fast OFF, no subagents. STOP only a
real blocker. Existing issue#4591 is the duplicate: no new issue publication.
Clear-error candidate is SUPERSEDED and must not be ported into this fix.

Fresh upstream main was checked read-only: faffcee3bca2770c03bd21c3bde89cc8f6f7a14e,
tree09b828b47c93e90e140e8c41f9048109a2f4a786/parenta3c8b8610739aab7d2c864bd4021086a5e7c0d94.
Recheck before final handoff; relevant drift -> explicit update, no silent rebase.
Own isolated clean source branch from stock main, no F4/unpublished tool stack.
Read baseline AGENTS and STYLE-UPSTREAM-RULES. Owner explicitly permits public
https://github.com/model-checking/kani/issues/4591 and comments as coding inputs
and asks its reproducer; this is the narrow clean-room exception. No unrelated
third-party PRs/diffs/implementations. Derive code from upstream main + own trace.

Maintainer feliperodri July11: ordinary stub fully replaces original body; adjust
ordering/resolution so original contract closure lookup is skipped/redirected
when replacement is active. Root verified issue/comment. Analyze FnStubPass →
FunctionWithContractPass/mark_unused and original instance/body/contract modes.
Implement minimum change: for the actually ordinary-stub-replaced instance/body,
do not apply original contract instrumentation/search closures to replacement.
Guard on resolved active ordinary replacement, not name/any stub in unit/absence
of closure. Keep other transformations/safety checks on replacement. Preserve
stub_verified/proof_for_contract, unstubbed contracted calls, recursion contract
modes, generic resolution and existing conflict/cycle/error handling. Trace
overlaps/provider-target and replacement-with-contract edge cases; if a broader
policy decision is required, return exact ambiguity, do not silently weaken proof.
Do not globally suppress missing closure errors or disable contracts/stubbing.

Upstream-style minimal tests (few files/directories, standard licensing):
- #4591 ensures reproducer and our dependency-free observed MRE from
  run44380273557/author5bb7/intake75de: main exact missing f closure, controls
  native successful. Preserve actual evidence vs new tests NOT_RUN.
- requires-only and requires+ensures ordinary targets, with distinguishable
  replacement behavior; include bypass of original target precondition where
  safe replacement allows it. Check original postcondition is not enforced on
  a plain replacement. Same-function PFC and verified-stub controls retain
  intended original contract behavior; include meaningful failure controls.
- Relevant recursion/generic/uncontracted/multiple-target and overlap cases
  bounded to changed behavior, using existing tests/ style. No guessed aggregate
  check quotas; assert meaningful native outcomes/semantics.
IMPORTANT #4591 pasted stub allows i32::MAX then caller+1, a real overflow case.
Do not claim verbatim example verifies SUCCESS after this fix. Keep it as an
expected verification-counterexample regression once compilation succeeds, or
explicitly explain a bounded passing variant; never silently remove that case.
Our u8 x<8/x+1 vsx+2 fixture supplies a safe positive ordinary-stub regression.

Prepare standalone PR package g0 ONLY kani3300/wave0/issue4591-fix/: exact main/
fix head/tree/parent/patches, source trace, regression main-fail vs fixed expected
oracle, static/mock validation, PR-DRAFT.md (Resolves #4591, disclosure, no invented
fixedPASS), and CI-REQUEST for ONE full STANDARD PUSH-CI bundle on FINAL PR-branch
head. As F4: preserve all standard workflows/scripts byte-identically; derive
actual push workflows/all native jobs/matrices (kani.yml, format,deny if same
main); no custom confirmation workflow, no subset-only tests or enable cron.
PR-only release/std/bench follow owner F4 upstream-PR scope, not a fork PR.
Final nonskip head/range/tree/parent bindings explicit; current native fixed
results NOT_RUN. No local compiler/cargo/rustc/Kani/CBMC/rustfmt/expansion/fullrunner.

Owner grants +1item1: ledgerdf7a140991 current30/31, total41/48 (item2 11/17).
This authorizes preparation, not CI now. Exact READY → independent11 review →
root GO-request → separate owner/coordinator full push-CI. PR publication still
requires owner command. No CI/push/rerun/cancel/enable/PR/issues/comments/ledger/
reservation/budget. Keep all old clear-error/MRE/intake/draft records immutable;
mark duplicate/superseded status only in new package. Ownpaths --only [skip ci],
Tiramisu-Cake <igkharin@gmail.com>. READY fullg0/fix/main/tree/parent/test/CI pins.
