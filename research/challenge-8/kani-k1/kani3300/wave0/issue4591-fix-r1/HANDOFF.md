# READY for same11 delta-review; GO pending main-drift decision

Task TASK-KANI-4591-PFC-FIX-W15 at g0
0396e88e1557104fd081587cc453f6cd22bcfbe1. W15/new15, high, Fast OFF,
zero subagents and no model changes. This new immutable repair directory is
kani3300/wave0/issue4591-fix-r1/. Its delivery g0 SHA is the commit containing
this directory and is supplied in the final handoff; no circular self-pin.

| Binding | Exact value |
| --- | --- |
| Frozen g0 | bdf1bb42189257c9654eb55dfcda11b2f08a0b01 |
| Frozen review | 54ea8a918b761dc67213f7f24ae5163b7f463b42 |
| Frozen source / tree | a7bca98c91cbfa595bdc2a1bdc6bd4d0a4fa796a / 98fae98ce9e783bed0393d35657674da09c3aa31 |
| New isolated worktree | /root/kani-issue4591-fix-r1-w15 |
| New branch | fix/ordinary-stub-contracts-4591-r1-w15 |
| New source | e6aa083da3c93f3189039077795cc9a0d67d3a6d |
| New source tree | 01140856c15e161ff6fc4c1ce460fd4208a298cd |
| Sole parent / frozen main | faffcee3bca2770c03bd21c3bde89cc8f6f7a14e |
| Main tree | 09b828b47c93e90e140e8c41f9048109a2f4a786 |
| Main parent | a3c8b8610739aab7d2c864bd4021086a5e7c0d94 |
| fix.patch SHA256 | ec159a83dbe1ff897480c30ab9a142de5859c57490999fb929cdc2c2c61f5e7b |
| regression-main.patch SHA256 | ef04091ab11f9af5067fc2d634bd901f013d75f8427bb026334566fb8fd536bd |
| full-main.patch SHA256 | 4af4a997cb786fbe85b8916b98d0d8e487d770edfc088bc0b02d25d30ae6acb3 |
| CI-REQUEST.json SHA256 | cf9dad7620e7aa1045d198003ba4225eaf19dbbdb38946779988aa8b2027c176 |
| Future nonskip final head | NOT_CREATED; same-tree sibling, sole frozen-main parent, one nonskip commit in main..final |

SOURCE-PINS.json binds every test path, exact blob/SHA256, compiler file,
workflow and protected tree/file. REGRESSION-ORACLE.json binds all38 harnesses,
updated attributes and repaired path expectations to the exact source/tree.
MANIFEST.json seals every file in this directory except itself. The source
candidate is a real committed local [skip ci] object, Tiramisu-Cake
<igkharin@gmail.com>, with exactly frozen main as its sole parent. It is a
sibling of the frozen skipped candidate, never its child. Future nonskip source
publication must exclude both skipped candidates from main..final.

W11-01 source repair: replacement_contract_target now directly calls its
selected contracted_replacement(0), then calls f(kani::any()). The negative
replacement_provider_postcondition selects a dedicated identity provider with
ensures result == 0, directly calls it with 0 (postcondition passes), then
calls f(1) (copied provider result 1 violates that postcondition). Existing
bad_contract and all other original functions, safety assertions and controls
are preserved. The new expected FAILURE description is unique to this
provider; all old expected groups, named results and 2/11/13 counts remain.
Read W11-01-CLOSURE.md first for the finding-to-repair mapping and limitations.

Only the two affected .rs fixtures and the negative .expected differ from
frozen source. The three compiler files and the entire kani-compiler tree
match frozen source exactly; fix.patch also matches byte-for-byte. No routing,
reachability guard, remaining control, standard workflow/script/action/library
or toolchain/dependency file changed. The inherited source analysis and
historical INCONCLUSIVE intake remain preserved in their proper assurance scope.

Static/mock validation replays both split and full patches to the exact source
tree, checks all16 workflow inventories and native push jobs/matrices, checks
13 lexical PFC harness call inventories, and rejects original W11-01 fixtures,
failing/missing/dead/comment-only/cross-harness direct calls and passing/missing
copied calls. See VALIDATION.json for the full executed check list and
pfc_regression report. Lexical calls and Python arithmetic are not compiler
DefId resolution, MIR proof, macro expansion, typechecking or native evidence.
All new main/fixed native, compiler, cargo/rustc/rustfmt, Kani/CBMC, expansion,
fullrunner, performance and CI results remain NOT_RUN. No push, PR/issues/
comments, ledger, reservation, budget or CI action occurred.

MAIN-CHECK.json records read-only upstream main drift to
969f4648980a8e66cd0ca32fd3e714a55ac32cef. The required sole parent remains
frozen faffcee3bca2770c03bd21c3bde89cc8f6f7a14e. No fetch/rebase was performed.
Root/coordinator must decide how to handle drift before GO; the prepared
metadata gate alone does not resolve it or grant dispatch authorization.

Next: same independent11 reviewer delta-reviews this exact immutable package
and source/tree, then root resolves drift and decides exact GO. Usercoordinator
alone launches one full standard push-CI bundle on the future nonskip sibling;
owner alone publishes PR/issues/comments or pushes open-PR branches. No new
final object, custom CI, cron/enable/dispatch or publication is created here.
The three stock push workflows and all twelve native job/matrix instances stay
in the prepared request; deferred upstream PR scope stays unchanged. Reference
budget item1 30/31, item2 11/17, total41/48, zero attempts consumed; the future
single authorized bundle would reach item1 31/31 and total42/48.
