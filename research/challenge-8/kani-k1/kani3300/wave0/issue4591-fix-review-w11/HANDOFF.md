# Independent11: REQUEST_CHANGES

Reviewed exact g0 package `bdf1bb42189257c9654eb55dfcda11b2f08a0b01`;
source `a7bca98c91cbfa595bdc2a1bdc6bd4d0a4fa796a`;
tree `98fae98ce9e783bed0393d35657674da09c3aa31`;
sole parent/main `faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`.

**W11-01, High:** `replacement_contract_target` and
`replacement_provider_postcondition` select provider PFC targets while calling
only ordinary-stubbed `f`. Copied provider closures do not satisfy Kani's exact
function-DefId reachability check. Both containing fixtures are expected to fail
compilation, invalidating their positive/semantic-negative result inventories.
This is a static finding; native executions remain NOT_RUN.

Original15 must repair the fixtures and publish a new immutable package, then
return it to the same independent11 reviewer for delta-review. Preserve a
discriminating copied-provider failure: a directly failing provider call alone
can mask the negative case. Do not weaken reachability checks or replace these
oracles with compile-error expectations. REPORT.md gives the source chain and
acceptance requirements. The original package and all source files were left
unchanged by this review.

Independent 112 static checks and author's 137 static/mock checks passed.
All21 package files/20manifest records, source cleanliness, exact pins,
protected trees and all16 workflow inventories match. Prepared full push-CI
contains the correct three workflows and twelve native job/matrix instances.
The #4591 reproducer correctly expects caller overflow. Main has no observed
drift. All38 harness oracles were inspected; two are blocked by W11-01.

**APPROVE: no. Root GO-request: withheld pending immutable repair/delta APPROVE.**
Future nonskip head NOT_CREATED; same reviewed tree/sole exact-main parent and
one-commit nonskip range remain mandatory after approval. Main/fixed native,
compiler/Cargo/rustfmt/Kani/fullrunner/CI are NOT_RUN. Budget remains30/31;
zero attempts consumed. CI dispatch and PR publication need their separate
coordinator/owner commands. No push, PR, issues, ledger, source edits, subagents
or model changes occurred.

Delivery is the local `[skip ci]` commit containing this exact immutable review
directory; its full SHA is supplied in the final response. MANIFEST.json seals
all review files except itself. inputs/INPUTS.json pins the reviewed artifacts;
evidence/ records static checks and source excerpts; tests/ records the
independent checker and all per-harness oracle conclusions.
