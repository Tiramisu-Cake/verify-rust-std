# Same Independent14 — CHANGES_REQUIRED

R14-01/P1 and R14-02/P2 are **CLOSED**. New **R14-03/P2** blocks approval of the
explicitly requested lexical gate. Return one localized fix to original13, then
same14 immutable delta review. Reviewer changed no implementation.

Issued owner17:29, task taskcf40e805eb47a5f11efdf27a62b06caf2bc2adff.
Owner's explicit /new supersedes the task's reuse-context instruction. Frozen
review f5dd71722f82ac59e37152927a5f4dd9eee6ea1a supplies unchanged review facts;
this review covers only the repair delta and new lexical gate, without broad reaudit.

Reviewed package **474e0b4209554bdd69c4303410192d2d472af4a2**.
Source **bd62e54df1b4749154790aa3db3cc7978f547f75**,
tree **dc2e7a7f258719a05c65bbb9b1e2c7f1e8271ac8**,
sole parent **97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a**.
Control **0e8c836857344866564e1423ad5d8d28bbc4106b**,
tree **9f7c903f2039e6a52b19f37c5f32fbd9cc86566f**,
sole parent **9e14e033f9ee31522b571c127609dcdff76d230b**.
Request SHA256 **9d165365933b6bc117311d7d52568f834bc2f083c2272800803a84883f286717**.
Workflow SHA256 **93521eefcbd83c50218d8484b2f8bbc044ff9acd2dd2b003749fe0e316c0ea6c**.
Stock **0aac16ef62da9e9d5645782d458593e5d78143ba**,
tree **9d8bc9312bf955ef126d32b819b3cd0ed105ed2b**.
INPUTS.json contains full pins, committed input hashes and task document identities.

## R14-03/P2 — new lexical gate drops nested-parenthesized static calls

At exact control above, `ch8-s1-control/lexical_bindings.py:78-84`, call_paths
recognizes a path followed directly by arguments, or exactly one parenthesis
around the path. It has no rejection for additional callable parentheses.
At lines247-254, audit validates only the paths yielded by call_paths, so an
omitted required static call never reaches binding resolution or a fail-closed guard.

On the final committed source fixtures, add this expression at the start of
the already inventoried `sort13_weak` function, source line146:

```rust
fn sort13_weak() { ((missing_static))();
```

No declaration/import/value binds missing_static. Remove only the synthetic
request's lexical_source_sha256 map, retaining every other request field. The
actual lexical_bindings.check returns **STATIC_PASS**, still reporting77 static
calls,8 functions and11 contexts. missing_static appears in neither the static
inventory nor the dispatch-limit inventory. Direct `missing_static()` and singly
parenthesized `(missing_static)()` reject with unresolved-static-path diagnostics
in the separately executed probe. The extractor also silently omits the qualified
`((super::super::sort4_stable))(a,b,c)` form.

R14-03-DISCRIMINATOR.json records the actual full-gate result, source/request
hashes, exact mutation and function inventory. additional_checks.py reproduces
the finding with scanner controls and an actual final-object gate invocation.
This is a source-scanner finding, **not an observed Rust compiler diagnostic**.

The exact unchanged source contains no missing_static call. Its immutable source
hashes and separate correspondence policy independently reject this mutation;
this review claims no bypass of those checks. The defect is that the new lexical
gate does not meet the task's explicit requirement to resolve every required
static call or fail closed on unsupported syntax. As with frozen R14-02, byte
identity protection does not establish the semantic discrimination of the gate.

Localized repair contract: original13 handles nested-parenthesized callable paths
or rejects unsupported callable-expression syntax before silently dropping a
required static path. Add semantic discriminators for direct/single/nested
parentheses, unbound and legitimate full paths, aliases and local callable values;
resolution or a precise unsupported rejection is acceptable within the bounded
gate. Keep method/type/trait/MIR limits separate. Preserve existing source/model,
controls and caps; prepare a new immutable exact package and return only its delta
to same14. No reviewer implementation or general Rust compiler is requested.

## Original finding closure

R14-01/P1 closes: the source delta from frozen r4 is exactly one import-line
replacement adding original grandparent sort4_stable. No other source bytes
change. Both calls at300/301 bind the original smallsort declaration; the len>=8
branch and copied algorithm remain. Frozen-r4, removed/renamed/wrong-target and
cfg-disabled imports reject semantically; repaired source, legitimate qualified
path and alias pass. Foreign-basename and visibility tests also pass. The finite
copy-correspondence expectation changes only for that import. Native compile NOT_RUN.

R14-02/P2 closes: the recursive shared resolver is used by ordinary_contracts
and combined cfg_pfc. The independently rerun exact ordinary1/ordinary2 review
discriminator uses imports at module scope, preserving every function attribute.
Both gates reject contracted swap_if_less and retain the safe s2_swap_seam binding
by full identity. Three-level and module chains, function-target/replacement chains,
cycles, ambiguous imports and unresolved targets are exercised. Only the ordinary
and cfg/PFC source-hash maps are removed for these synthetic checks. Active/inactive
cfg, wrappers, full targets, foreign basenames and same-cfg PFC controls pass.
FINDING-CLOSURE.json and TARGETED-CHECKS.json give independent closure evidence.

## Bounded validation and inherited facts

The repaired package has60 files/59 hashes matching its exact commit. Frozen
review files match f5dd717 and remain unchanged. This review independently ran
**96/96 final-object Python/static/synthetic tests**; FINAL-TESTS.txt and
TEST-PROVENANCE.json record this execution, not the author's earlier transcript.
The new fail-open discriminator is additional to those passing tests.

The package validator was executed with only output writes redirected into this
review directory. Actual runner.py check-source passes and the traced prebuild
order is lexical paths → ordinary contract gate → verified same-cfg PFC, each
covering11 contexts. Workflow check-source precedes stock setup/build. All11 rows
share the pinned effective cfg. Baseline NAME-RESOLUTION-MAP matches the candidate:
six new functions plus two changed callers,77 static calls and explicit method,
macro and associated-type dispatch limits. Its completeness claim is blocked by
R14-03; a baseline map match does not repair that semantic gap.

VALIDATION.json records six exact patch/tree replays, real shallow checkout7/5/2,
request/workflow/payload inventories,23 ordinary binding records,19 original
contract stacks and326 enumerated functions. Targeted byte comparison confirms
the control delta is limited to alias resolution, necessary gate integration,
new fixtures/tests and identity metadata; runner changes only two source literals.
Protected collector/packer/diagnostic/error/B-01/B-02 bytes and workflow are unchanged.

The original source/model/contracts, operation-identical copies, domains, frames,
initialization, six exact assertion tags and positive/negative scope inherit f5
facts by the exact one-line import delta. Both general32 roots still have only
same-cfg verified original-sort8 registration, with DIAGNOSTIC_ASSUMED unchanged;
this does not establish a proved leaf or qualification. The same11 roots,20 covers,
6 negatives,3 primary probes, one group/no variants and all caps remain:
backend600s, compile900s, rootsum6600s, group7500s, internal8100s, step7560s,
setup1800s, job180min, serial1, RSS12GiB plus2GiB headroom.

Native compilation, expansion, type/method/trait/MIR resolution, verifier, full
runner, CI and causal repair NOT_RUN. Actual R3 failing unit/body UNKNOWN;
leaf/PFC qualification NOT_RUN; independent B1/B2 proof credit NONE, closed proof
obligations0. Frozen source-mechanism facts are inherited without a stock reaudit.
Reference29/29 +9/14=38/43 and r0..r3 charged0 remain references only.

No compiler/CI/push/issue/PR/ledger/reservation/budget operation, external message
or publication occurred. Current settings retained; Fast OFF per owner unchanged;
no subagents. Outputs are confined to review-batch-r4-r1. HANDOFF.md routes the
localized R14-03 repair to original13 and then same14 delta. No GO preparation
or dispatch is authorized by CHANGES_REQUIRED.
