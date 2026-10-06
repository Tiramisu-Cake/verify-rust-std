# Sort4 no-patch feasibility assessment

2026-10-06; bounded [owner-authorized phase](SORT4-NO-PATCH-PHASE.md), entry
`11e8ead9389cc95fc7d13a24d0c28d7d2d6ba3c5`. **Source review has not identified an
evidence-backed no-patch route to the requested unrestricted safety contract.**
This is a decision about the considered candidates, not proof that every
unmodified-verifier approach is impossible. No new verifier experiment has run.
The historical patched proposal is preserved and remains unauthorized.

## Target, acceptance and evidence vocabulary

Actual [sort4_stable](https://github.com/Tiramisu-Cake/verify-rust-std/blob/11e8ead9389cc95fc7d13a24d0c28d7d2d6ba3c5/library/core/src/slice/sort/shared/smallsort.rs#L612-L658),
std blob `e555fce440872898e47fd5114f32eb15401d07df`, and actual
[selection helper](https://github.com/Tiramisu-Cake/verify-rust-std/blob/11e8ead9389cc95fc7d13a24d0c28d7d2d6ba3c5/library/core/src/hint.rs#L836-L884),
blob `fe59166363b9cc049c0d48f4349f4dc9c0e458b8`, stay unchanged.
[Challenge 8](../../doc/src/challenges/0008-smallsort.md) requires all valid types/
slices and four UB categories; [general rules](../../doc/src/general-rules.md)
require approved, already integrated tools and unchanged runtime logic.
[Full research contract](SORT4-CONTRACT.md) distinguishes sufficient range
separation, raw scratch, one ownership sequence and unrestricted callback
safety from purity/order premises for functionality. Its public-target
admissibility is still an open clarification, not an accepted stronger premise.

**Observed** below means a recorded hosted result in its exact domain or a
statically inspected source fact. **Inference** means applicability argued from
that evidence. **Unknown** means not established by an actual generic target
proof. No run of VeriFast on complete actual sort4 exists. Historical patched
results identify gaps and cannot be used as evidence for unchanged tools.

The first required capability corresponds to actual c1, smallsort.rs:626:
`let c1 = is_less(&*v_base.add(1), &*v_base);`. It borrows source slots1/0,
passes the pair through generic `FnMut::call_mut`, and can panic before any
sort4 write. Four initialized source cells, separate uninitialized four-slot
scratch, F and frame must return as full **current** resources on both paths;
normal additionally returns the actual Boolean. Callback state/interior effects
survive; scratch/frame are unchanged only where inaccessible to the callback.
There must be no local borrow debt or second independent droppable ownership.
[Contract panic table](SORT4-CONTRACT.md#all-five-panic-posts) records every
c1..c5 exit. Prior insertion MIR and unchanged translator establish the shared
call/unwind mechanism; a future c1 fixture would still require its own exported
MIR/CFG/refinement audit. No such audit/proof is claimed in this review.

## Compact obstacle matrix

| Obligation | Observed evidence, exact scope | Inference for actual sort4 / unknown |
| --- | --- | --- |
| Tuple-2 argument ownership for FnMut | Unchanged26.09 [37400422055](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37400422055) reaches actual generic insert_tail callback and cannot supply `Args.own`. [Tuple note](verifast-tuple-parser.md), runs37401357731/37401753468/37402093844/37402802085 record missing instance/namespace/name clash/duplicate alias. Baseline parser generates opaque generic tuple own; prelude supplies tuple2 share but no tuple2 close/open own lemma. | Same reference-pair call shape at sort4 c1 needs the resource. Packaging references/debt does not prove opaque tuple ownership. A proved supported field-to-own route is unidentified; this is not an executed sort4 failure. |
| HRTB FnOnce::Output=bool | Compiler MIR [37408278446](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37408278446) records two bound regions. Tuple-patched-only [37407173581](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37407173581) reaches Output/bool mismatch. [HRTB note](verifast-fnmut-hrtb.md): targeted translator patch advances in37409198258;8 matcher cases37410979109 test guards, not callback proofs. | Unchanged translator filters higher-ranked projections; changing spelling of the trait name does not instantiate the lost equality. Actual sort4 export on26.10 remains untested; no supported checked annotation derivation was found. |
| Full normal recovery | Unchanged26.09 [37437514808](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37437514808) and [37448682524](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37448682524) prove checked recover_pair plus generic/i32 callers and3 intended resource/false-post negatives in a natural block. | This supports ordinary explicit recovery after a real scope. It includes no FnMut and no source-exact five-call composition. Four-cell helper/call/resource-effect proof would still be required. |
| Full direct unwind recovery | [BORROW-RECOVERY-DESIGN](BORROW-RECOVERY-DESIGN.md): Continue becomes immediate unwinding ReturnStmt; block return returns reserved token/frees locals but skips trailing helper. Auto recovery conflicts with nonghost_callers_only APIs. Patched strict-cut37414755368 returned borrow debt on unwind, not full cells. | No checked recovery continuation on actual direct panic was identified. This rules out the reviewed trailing-helper/auto-lemma proposals, not every conceivable proof organization. Full current F/frame/cells/scratch must never be replaced by debt or rollback. |
| Copy into uninitialized scratch | Baseline typed copy_nonoverlapping requires initialized dst `|->`; `points_to` means `some(T)`. Actual callers use MaybeUninit scratch. Patched Drop37419989766 used initialized dst. Source fact, not an executed raw-scratch failure. | Cannot conjure some(T) from none or two owners from copied bytes. General byte/typed initialization transport, padding and destination prior-resource disposition remain unproved under the reviewed specifications. |
| Actual select_unpredictable | Actual hint836..884 wraps values in MaybeUninit, selects pointers, drops unselected value with DropOnPanic guard and uses intrinsic selection. No named helper/intrinsic support identified in inspected VF specs/translator. | Must verify actual pointer instantiation at matching source, including provenance, before summary use. Replacing it with an assumed if is not admissible. Pointer values have no T destructor, but that does not itself prove the actual helper or exporter support. |
| Five-call composition | Actual c1/c2,c3/c4,c5 precede copies; [contract](SORT4-CONTRACT.md) maps calls and32 Boolean index possibilities statically. No generic five-call proof. | Shared borrows may coexist; full recovery is required at normal exit and each panic. Repeated sharing/current callback effects and index-selected permission routing remain unknown. |
| Copied representations / provenance / ZST / padding | Actual-body Kani [37459631500](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37459631500) covers i32 and Copy tagged records; padding is not asserted initialized. Contract diagnostics [37466906281](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37466906281) distinguish coincident-copy UB from shifted i32 multiset loss. | Neither establishes universal generic validity or single-owner Shadow transport. Numeric pointer equality is insufficient permission evidence. ZST may share addresses while carrying four ownership occurrences; padding may be uninitialized and must be byte-copied legally. All remain explicit proof gates. |

## Unchanged 26.09: alternative annotation organization

Exact source `809de4596839b739dd999f9e462242c835e3af46`; Linux official artifact
`verifast-26.09-linux.tar.gz`, SHA256
`da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa`,
Rust nightly-2026-02-05, as pinned in
[setup](../../verifast-proofs/setup-verifast-home). A clean existing source
checkout at that exact commit was inspected read-only; no patch/build/execution.

Official immutable source locations:

- [Tuple declarations/available lemmas](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/bin/rust/prelude.rsspec#L12-L43), [opaque RSSPEC struct ownership generation](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/rust_frontend/vf_mir_translator/rust_parser.ml#L1135-L1150).
- [FnMut normal/unwind contract](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/bin/rust/std/lib.rsspec#L44-L50), [HRTB filter](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml#L4793-L4803).
- [Direct Continue translation](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml#L2473-L2493), [block return continuation](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/verifast.ml#L2665-L2681), [nonghost-only recovery APIs](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/bin/rust/rust_belt/lifetime_logic.rsspec#L275-L283), [auto-lemma restriction](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/verify_expr.ml#L381-L386).
- [Typed copy contract](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/bin/rust/std/lib.rsspec#L545-L549), [optional vs initialized cells/arrays](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/bin/rust/prelude_core.rsspec#L212-L248).

The useful alternative is ordinary verified recovery with real lifetime tokens,
as demonstrated by recover_pair. It does not address tuple ownership or HRTB,
and trailing normal proof statements are skipped on direct unwind. Moving lemma
placement cannot give a body to an opaque tuple predicate. Tuple4 trusted close
lemmas do not supply a checked tuple4-to-tuple2 ownership conversion. Supplying a
new bodyless tuple bridge, assuming tuple ownership in the public precondition,
or selecting a different callback wrapper would replace the obligation or change
the generic/runtime target. Prior naming/overlay attempts already tested those
relevant failure mechanisms; there is no new reason to repeat them.

The internal [projection registration statement](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/verifast.ml#L559-L565)
asserts an equality into the symbolic context. Manually inserting that statement
is not a proved lemma deriving the compiler's higher-ranked instance. This phase
allows checked annotations, not a new unverified translation/equality assumption.
A byte-oriented resource wrapper could be useful later, but the actual runtime
call remains `copy_nonoverlapping::<T>` with its typed contract; the separate
`ptr::copy` byte specification cannot be substituted for that call by rearranging
annotations. No checked optional-to-initialized conversion for arbitrary T was
identified. Verifying a more general actual callee is a possible future research
question, not a demonstrated capability or a cure for the earlier c1 blockers.
There is likewise no justification for an automatic lemma to invoke forbidden
nonghost-only recovery APIs. No supported alternative closing all these first-call
obligations was identified. These are source/evidence deductions, not exhaustive
elimination of all mathematical proof strategies.

## Official 26.10 comparison

The released [26.10](https://github.com/verifast/verifast/releases/tag/26.10),
published 2026-10-05T06:46:32Z, resolves to
`f76012fb518703b1d98e243ac4f487f16877cfcb`. Official
[Linux artifact](https://github.com/verifast/verifast/releases/download/26.10/verifast-26.10-linux.tar.gz):
`verifast-26.10-linux.tar.gz`, asset611766606, 97,804,993 bytes,
SHA256 `5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd`.
Digest/size are GitHub release API metadata, not a hash of a locally downloaded
binary; the release binary was not installed or run. The
[Rust frontend](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/src/rust_frontend/rust_fe.ml#L105)
pins nightly-2026-09-25. This is a possible isolated official profile, **not** a
change to the repository's26.09/nightly-2026-02-05 pin.

Comparison used official source trees at both exact commits, not only the release
changelog. The release changelog starts from26.09.20, so comparing it alone would
also miss differences since our26.09 pin.

| Mechanism | 26.10 source observation versus pinned26.09 | Consequence |
| --- | --- | --- |
| Tuple arguments | [prelude](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/bin/rust/prelude.rsspec#L12-L43) is byte-identical, SHA256 `d7058d43557a2b5147eb1377e85bb67d04b94c83594b6c1c27650c9c571841b5`; [struct parser](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/src/rust_frontend/vf_mir_translator/rust_parser.ml) retains opaque generated own. Relevant [FnMut specification](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/bin/rust/std/lib.rsspec#L44-L50) unchanged. | No field-to-tuple2 owned-argument mechanism added. |
| Output projection | [Trait-name canonicalization](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml#L4870-L4874) fixes core/std naming; [projection filter](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml#L5010-L5019) still accepts only empty bound_regions. | Useful for non-HRTB projections; does not instantiate our compiler's two-region Output=bool bound. |
| Direct panic | [Continue](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml#L2653-L2676) remains immediate unwinding ReturnStmt. | Trailing ordinary recovery still has no direct-panic continuation. Full-resource panic success has not been tested. |
| Scratch copy | [copy_nonoverlapping](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/bin/rust/std/lib.rsspec#L576-L580) still needs initialized typed dst; [optional-cell model](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/bin/rust/prelude_core.rsspec) keeps optional and initialized resources distinct. | No ready raw-MaybeUninit destination case for actual copies. This contract returns cells, not a second independent T.own sequence. |
| Actual selection | No named select_unpredictable support identified in source/spec searches. | Actual helper and intrinsic proof remain prerequisites; absence of a name alone is not proof of impossibility. |
| Other nearby changes | Address-taken locals with projection clauses and generated in-out mutable-slice contracts changed; release links PRs1023/1027. | Those changes address neither shared-reference tuple ownership nor bound-region instantiation or Continue recovery. |

Source comparison fingerprints (SHA256):26.10 std/lib.rsspec
`2da7acfb6596f8abec90c103ef7f294152c18f974b88124669882fc051272999`,
prelude_core.rsspec `435146cd4632541241563ae45b146704c14f6f7cdd3b5d404837617f08bc91b8`,
rust_parser.ml `b26422aff8a6091181485a1355fc60e3a2afde5c8bff2bbe5176fdee07b08622`,
vf_mir_translator.ml `c1eb897673f88b0b8dc50798deca603bdad2c60818b6d5380ccf1dda055fe445`.
These identify reviewed source, not verified binaries or proof results.

Static source/signature mapping remains applicable: the unchanged sort4 c1 is
still a generic reference-pair FnMut call, followed by other comparisons and
copies. Export/compilation of this exact std body on nightly-2026-09-25 and its
annotated-to-original refinement audit are **NOT RUN / unknown**. Schema/exporter
changes across toolchains mean old MIR/refinement artifacts cannot certify a26.10
fixture. The actual hint helper's const Destruct/MaybeUninit/Drop implementation
also needs a fresh exact-source compatibility audit. This is an untested gate,
not an observed compiler incompatibility. We did not spend a run merely on a
compiler-version change when independent first-call blockers persisted in source.

## One integrated alternative: Kani

Selected because it has the strongest existing exact-body integration/evidence
for this target: [approved tools](../../doc/src/tools.md),
[scripts/run-kani.sh](../../scripts/run-kani.sh),
[research workflow](../../.github/workflows/smallsort-research.yml),
[run-sort4.sh](run-sort4.sh) and [functional results](SORT4-RESULTS.md).
No other alternative received detailed comparison and no alternative was
installed, integrated or executed in this phase.

Pin [tool_config/kani-version.toml](../../tool_config/kani-version.toml):
`152c6a8c875d9886a67e229247b4826d6105ccfd`, Kani0.67.0,
[Rust nightly-2026-02-05](https://github.com/model-checking/kani/blob/152c6a8c875d9886a67e229247b4826d6105ccfd/rust-toolchain.toml).
The official [contract RFC](https://github.com/model-checking/kani/blob/152c6a8c875d9886a67e229247b4826d6105ccfd/rfc/src/rfcs/0009-function-contracts.md)
describes contract checks over monomorphized instances. Selecting more concrete
T/F instances does not prove all types or a parametric resource theorem. Four
cells are the complete sort4 arity, but that does not eliminate type/allocation/
callback domains. A verified concrete callee summary remains concrete.

The existing normal functional proofs have pure nonpanicking comparison and
initialized Copy destinations. They do not exercise callback-panic recovery.
[Validity instrumentation](https://github.com/model-checking/kani/blob/152c6a8c875d9886a67e229247b4826d6105ccfd/kani-compiler/src/kani_middle/transform/check_values.rs#L387-L393)
rejects CopyNonOverlapping in the measured stronger-check run37396688760;
[uninit instrumentation](https://github.com/model-checking/kani/blob/152c6a8c875d9886a67e229247b4826d6105ccfd/kani-compiler/src/kani_middle/transform/check_uninit/mod.rs)
and the measured immutable-write detector gap37397720683 are documented in
[ub-checks](ub-checks.md). Those runs were not generic sort4 failures; they are
material limits on reusing the pinned instrumentation for the required claim.

Kani remains useful for concrete actual-body counterexamples/diagnostics. Current
evidence does not provide the universal T/F abstraction, full ownership/frame/
callback effects on direct unwind, and required UB coverage for a general safety
route. Whether an independently justified parametric abstraction could meet all
requirements is unknown; designing/integrating one is outside this phase. No
claim about every version or every possible Kani architecture follows.

## Experiment decision and remaining decision

**NO EXPERIMENT: no new falsifiable candidate passed the first-call gate.**
No fixture, harness, runner, workflow selection or verifier change was implemented;
no dispatch, retry, local executable verification or dependency installation.
Run budget used:0 of2. New-run URL: none. Main and runtime source remain unchanged.

Decision map used before implementation: a documented supported mechanism for
both tuple/HRTB and full normal/direct-unwind recovery would justify one c1
fixture with the full phase posts and predeclared controls/negatives. A changelog
fix for only trait names, a normal-only helper, borrowed-debt unwind success, or
a concrete monomorphization does not pass that gate. The actual source review
produced the latter findings, so the permitted action is assessment/closeout.
No setup/unsupported/frontend failure is being counted as an intended negative;
there is no new negative test result at all. Historical positives and negatives
are preserved, not rerun or removed to manufacture a new green result.

**Checked:** current fork/heads/clean entry tree/no active Actions; unchanged std
blobs; prior experiment domains and failures; official26.09/26.10 source and
release identity comparison; Kani integration/pin and official contract/memory
instrumentation evidence. Local validation is documentation/link/static diff
review only, not a proof run. Generic coverage is unchanged.

**Unknown:** a different supported no-patch proof organization not found here;
26.10 exact-source export/refinement compatibility; full current-resource
callback restoration, all five calls, raw scratch copy, actual selection proof,
non-Copy/non-Freeze ownership/provenance/ZST/padding. No result establishes all
required UB categories for generic sort4. These unknowns cannot be discharged
by the source comparison or the earlier concrete Kani theorem.

**One recommended next task:** owner review and clarify the full safety contract
for actual sort4, specifically admissible range separation and the single-owner,
nondropped scratch representation protocol in SORT4-CONTRACT. This addresses
the measured mismatch between the short SAFETY comment and actual copies before
choosing any proof implementation architecture. Decision needed: authorize that
bounded contract/admissibility review or keep proof work stopped. No verifier
extension is selected or implicitly authorized by this recommendation.

Questions requiring external clarification are recorded here only: whether the
sufficient separated-range/single-owner contract is acceptable for the public
challenge target; which source-matched owned/scratch-access protocol callers
must expose. If a later no-patch mechanism is supplied, its checked tuple/HRTB
and direct-panic route must first justify a new c1 experiment. If the owner ever
chooses custom verifier work, it needs a separate explicit trust/design decision;
the preserved patched proposal does not acquire authorization from this phase.
Phase closes here; no automatic advancement to any other function or route.
