# Independent14 — CHANGES_REQUIRED

Reviewed package **4e2801660d89d75a1357a420c78cd435159c35b3**, task
**043f659cb6ec8512fc0215aa52357369464f4cad**, issued owner16:52.
Source **16aa3557742e1b8a8b64b3b3d49da23d988027f8**,
tree **135f4549d1e8d6f69f1935c817f4c42bb917b756**,
sole parent **97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a**.
Control **db81e62d76cfa193b1d7fe8e8ebbecead7e20ef8**,
tree **76b64915601e060fc79da7cc1410993283a6dcab**,
sole parent **9e14e033f9ee31522b571c127609dcdff76d230b**.
Request SHA256 **800fa67f8b7dcd8efdb228b72c0131f77d3676b3a1f46e1c06ba29a93cb77512**.
Full stock/workflow pins and initial identities are in INPUTS.json.

Two localized findings go to original13. Reviewer changed no implementation.
The first is a source name-resolution blocker; the second violates the required
alias/fail-closed gate behavior. No GO or dispatch follows this review.

## R14-01 — P1: copied scratch algorithm lacks the sort4_stable binding

At exact source above,
`library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs:300-301`,
`general_fault_scratch` calls bare `sort4_stable` twice. The module's explicit
imports at lines2-7 do not import it, and the module has no local declaration.
The original function exists in the grandparent smallsort module, where the
original scratch body could use its bare name. Moving the body into the child
module requires that binding to be imported or qualified.

The `len >= 8` branch still participates in Rust name resolution even though the
selected negative harness supplies length32. Therefore the copied source is not
ready to compile. This is a static source finding, **not an observed compiler
diagnostic**; native compilation remains NOT_RUN.

`s2_correspondence.check` passes because its head/body token comparison does not
establish lexical binding equivalence after relocating a function. The package's
84 Python tests and actual `check-source` also accept this exact source.
ADDITIONAL-CHECKS.json records the two call coordinates, every explicit module
import and local function, the parent declaration, and exact source delta.

Required localized repair: original13 restores the correct original callee binding
without changing the copied algorithm, assertions, domain or fault. Update the
finite correspondence import expectation and add a small static dependency check
that distinguishes this missing binding. Rebind source/control inventories,
fixtures, request, patches and final-object provenance in a new immutable package.
Do not delete the branch to satisfy the checker. Return its delta to same14.

## R14-02 — P2: chained attribute aliases silently hide an ordinary stub

At exact control above, `ch8-s1-control/cfg_pfc.py:260-267` resolves only one import
alias. `ordinary_contracts.py:117-120` then ignores any resolved path whose last
segment is not literally `stub`, even when that path is another local alias of
the Kani stub attribute. The combined PFC gate also skips it at
`cfg_pfc.py:373-377`.

Reproduction on the same source fixtures, replacing the one sort13_weak attr:

```rust
use crate::kani::stub as ordinary1;
use self::ordinary1 as ordinary2;
#[ordinary2(swap_if_less,weak_swap)]
```

Both `ordinary_contracts.check` and combined `cfg_pfc.check` return STATIC_PASS.
The ordinary inventory drops from23 to22 records and contains no sort13_weak
binding, although the alias chain names an ordinary replacement of contracted
swap_if_less. Direct spelling and a single alias correctly reject the same target.
ALIAS-DISCRIMINATOR.json contains all four actual synthetic gate results and
diagnostics; review_checks.py reproduces them without expansion or compilation.

As in the submitted mutation tests, only the two gate source-hash maps are removed
from the synthetic request, so the test exercises semantic discrimination rather
than immutable-byte rejection. The exact frozen request would reject changed
source bytes, and the batch correspondence policy also restricts its prefix.
This finding does **not** claim a bypass of those independent checks or an unsafe
ordinary target in the unchanged r4 package. It establishes that the new gate
itself does not meet the explicit full-alias/unsupported-fails-closed requirement.

Required localized repair: original13 either resolves such alias chains to full
identity with ambiguity/cycle protection or rejects unsupported alias chains
before silently discarding a potentially relevant attribute. Add distinguishing
safe-target/contracted-target chained-alias cases and fail-closed cases; preserve
the existing full-target, safety-wrapper, cfg and same-cfg PFC controls. Include
the bounded control delta and exact final tests in the immutable repair for same14.

## Source mechanism and semantic review

Frozen diagnostic **04c61ba50ae4d62caaf87ed84b90e84e958c184f** is source-supported.
Independent inspection of exact stock
**0aac16ef62da9e9d5645782d458593e5d78143ba** confirms:

- `transform/stubs.rs:46-55` substitutes the validated replacement body.
- `transform/mod.rs:115-123,152-179` places FnStubPass before
  FunctionWithContractPass, retaining the original instance through body changes.
- `transform/contracts.rs:323-342,659-667` reads original FnDef contract metadata
  and looks for recursion/check/replace/assert closures in the supplied body.
- `transform/contracts.rs:711-733` requires an exact debug name and Closure type.
  `initialize.rs:72-89` constructs the original function's name family;
  `bootstrap.rs:18-49` creates the contract metadata/closures.

Thus an ordinary replacement of a contracted original can pair replacement-body
locals with original-instance metadata. This conditional mechanism does not
identify the actual R3 failing unit/body or establish a causal repair. Those
runtime facts remain UNKNOWN/NOT_RUN. All37 frozen provenance Git objects and
the diagnostic reference hashes were checked (ADDITIONAL-CHECKS.json).

The r4 semantic route otherwise satisfies the reviewed intent:

- All four r3 bindings are removed: swap in sort13_weak, sort8 in each general32
  root, and merge in general32_weak. Frozen-r3 rejection at all four sites is
  covered by the actual final-object distinguishing tests.
- Both general32 roots use original sort8's verified summary with an active exact
  same-cfg PFC registration. Registration is not a proved leaf, selected execution
  or qualification. Both assumed consumers remain DIAGNOSTIC_ASSUMED.
- Original sort8's full-byte sortedness/multiplicity, source-read and disjointness
  premises, dst8/scratch8 modifies frame, and initialized destination relation are
  retained. The shared model compares full u8 values/counts; no lower-bit shortcut
  was introduced. The original model/contract files are unchanged from r3.
- The three caller copies have identical signature/body operation tokens after
  only the declared renames. That establishes operation correspondence subject to
  correct relocated bindings, which R14-01 currently breaks. Descending13 under
  no-op swaps and [2;16][1;16] under copy-only final merge retain their order faults;
  six exact oracle tags and full postconditions remain. No unconditional false
  assertion replaces them. The two controls now cover local copies/seams rather
  than original caller/leaf identities; that limitation is explicitly recorded.
- Original smallsort bodies and contracts are byte-identical to r3, including
  swap's five preconditions, two-position frame and old-state ensures. S1/nonS2
  behavior is inherited by exact unchanged source bytes. No contracts are disabled.

## Reproducibility and integration checks

review_checks.py verifies the48-file/47-hash package before and after execution.
It independently reruns the **84 tests on final committed source/control** and
executes the reviewed package validator with only its output paths redirected to
this review directory. FINAL-TESTS.txt and CHECKS.json are this review's execution;
the author's TEST-PROVENANCE/TARGETED-TESTS remain unchanged. No precursor result
is substituted for final-object testing.

VALIDATION.json records actual final `runner.py check-source`, ordinary-then-PFC
call trace covering all11 contexts,23 ordinary records,19 original contract stacks,
326 enumerated functions, source/control/request/workflow/payload inventory checks,
six exact patch replays, and shallow ancestry checks at control7/source5/tool2.
These static passes do not invalidate the two findings.

Workflow check-source precedes both stock setup and build. Literal aliases/full
targets, active/inactive cfg_attr, wrappers/internal markers, foreign basenames,
unselected/imported targets, missing/wrong-cfg PFC and unsupported-input tests pass;
R14-02 gives an additional failing discriminator. Exact frozen forwarding-macro
file pins and the bounded all-literal-arms policy were inspected.

The same11 roots,20 covers,6 negative oracles,3 primary probes, one group and no
variants are retained. Caps remain backend600s/compile900s/rootsum6600s/group7500s/
internal8100s/step7560s/setup1800s/job180min, serial1, RSS12GiB+2GiB headroom.
Stock-relative ci_changed_paths/payload, source/variant maps and binding anchors
match the committed candidate. Source/control are sibling children of the required
parents. Protected decoder/collector/packer/error controls and workflow remain
byte-identical to r3; runner changes only two source identity literals. This
inherits reviewed B-01/B-02 behavior by exact bytes, without a new compiler audit.

## Limits and handoff

Native compile, expansion, verifier, full runner, CI and causal repair NOT_RUN.
Actual R3 failing unit/body UNKNOWN; PFC/leaf qualification NOT_RUN; B1/B2 and
independent proof credit NONE; closed proof obligations0. No compiler/CI/push/
issue/PR/ledger/reservation/budget operation or external publication occurred.
Current model/tier retained, no subagents, Fast OFF per owner without changing it.

Return R14-01 and R14-02 to original13. Preserve this review and the original r4
package; prepare an immutable bounded repair and same14 delta review. No reviewer
implementation, GO preparation, execution promise or accounting action is authorized
by CHANGES_REQUIRED. HANDOFF.md is the local routing artifact.
