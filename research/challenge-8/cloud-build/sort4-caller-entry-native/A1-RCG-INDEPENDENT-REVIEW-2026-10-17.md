# A1 R/C/G independent source review (UNRUN)

## CURRENT checkpoint — source-only final review, 2026-10-17

**NO-GO; no Cloud Build requested or run.** All 26 matrix rows, R/C/G
compiler/exporter/schema/decoder execution, verifier checks, and proof claims
remain **UNRUN**. No Brief exists and no cost was incurred. This checkpoint
supersedes stale “runner not wired” wording below where current source has
since added hooks; it does not treat those hooks as executed evidence.

Reviewed final source pins: R patch
`4c0a43a10d5e023af7c190ed801546cf9877448d8dde65b39a773d68707f5a5e`, C patch
`e7cdc8a8504338ccaab760975c1a3f1a739211d7f8d531dd214babc2005d894e`, and
integrated translator
`4e1c7e12dc67f3ea9f6305ea495f9503c170ad624612d0839dc8e8f00ae3a00d`. Source
review closes the earlier R owner/generic/scope issues and C publication-order
issue; the common native outcome envelope remains present. It establishes no
API/build correctness and no compiler or proof result.

Current source hashes are runner
`d0b6b951655d5982dfb2067b458632bb0467611e259f4230d8e67b62c6aa812a`, proof
classifier `7a2070a3132bc7d4601565aebd25e0aea682520e3fbb32a6045ccdf276142a2e`,
admission `0ac3b182a24ba3a8cfd21588dd393f652e864bf54593ac7f4a5caaa473927ad4`,
receipt `bcc55360698346f0aa2dfb3858c6b555a9104db95308116d2c16c188a9b8a7dd`,
and profile `fbdb28dc43582b9b9bb695929f0b8200148761ed66c2c7b78def0df1da7b75d0`.
The profile's 12-entry helper map matches the current helper bytes. The
separate runner entrypoint hash is listed above. Profile
`cloud_build_enabled` remains false and proof/infra pins remain null, so this
is not a dispatch-ready profile.

Other current source hashes checked: focus backend
`627de306d68790effbec95fde0a777bc8f889fcdced3afc0fdaae3ceb6de8075`, compiler
inventory `6b1cf336d7af59a92eaf023e9870b93de8b1b0b9aa74d20ceb42a636fbfd72dc`,
inventory test `22d9755aa9c11a1ee813065dcf390e6eda0735083e11763b2d6a5a95b54045a9`,
AST gates `ab0b86a8773f2300392b0ab56a00b8068df1ac78296835bcd9d3ff965f2b54b8`,
call binding `ff79dc058385a6d1476a389022aeae7a063e6238695f9046d6b709e2f49ba27d`,
and tool reconstruction helper
`31237e0a435164bd14b73f6df2c5124df31d47b074f1623b3e37326ecf9b6e09`.

The runner now has a source-only focused error-context parser. Pinned console
source prints `Verifying function '<numeric alias>'` only after the prototype
compatibility continuation returns; the classifier requires that frame at the
actual `Body.span.lo` for a negative contract case before it calls the result
an intended body-post candidate. Missing or header-only context stays
inconclusive. Synthetic context tests exist, but are unrun here and do not
validate Cloud text formatting. The runner remains a false-returning
preflight: first missing scientific stage is the full P1 `small_sort`
interface (required method and both implementations, all regions/clauses,
normal, returning, and unwind AST posts). The full 26-row runner/admission
lifecycle, receipt flow, and live negative controls are incomplete. No summary
is published; no build or proof is authorized by this checkpoint.

The main agent reports that eight isolated synthetic modules passed 96 tests
in 4.4 seconds. Subsequent whitespace cleanup was guarded by Python AST
equality checks; no behavior change is claimed. These checks provide
parser/control evidence only, not compiler, tool, verifier, fixture, or proof
evidence.

## Earlier disposition — superseded source checkpoint

**NO-GO for Cloud dispatch; all tool build, fixture execution, proof, and
matrix rows remain UNRUN.** The historical preliminary R findings below are
not current blockers where later sections explicitly record them fixed: the
current R patch addresses the generic-parameter identity transport and
parent/method scope distinctions; the current C patch preserves the native
outcome envelope and fixes the old MD5 label. Source inspection assigns no
proof or build credit.

Current pins: R `4c0a43a10d5e023af7c190ed801546cf9877448d8dde65b39a773d68707f5a5e`,
C `16951eaf8c4d9eada7e57e5e501471553be330c443b6e78ac7fd676901a4f6d9`,
integrated translator `6cf19e4c4bbc4c856f0e6d416853f745f6128438373c321b4eb29a64a30ce8e3`,
receipt `bcc55360698346f0aa2dfb3858c6b555a9104db95308116d2c16c188a9b8a7dd`,
admission `b0703160700a799c9efba7a21a3a625aa13a68725f5a9cfcbd9a1ee7bd2b8b7d`,
runner preflight `a3a8f684b9b1bcbc00cc167bae533050c172a1576eb82834fc0236416317a43a`,
tool helper `31237e0a435164bd14b73f6df2c5124df31d47b074f1623b3e37326ecf9b6e09`,
and profile `3141dce7f83bce95b80dbfe112587d11d827ca24c03dfbf072eb4a854f49c827`.
The latest runner change statically parses `a1-contract-admission.py:MATRIX`
and checks equality with the 26 planned case IDs; this closes that inventory
drift check only. The runner remains an import-inert preflight that stops
before fixture generation, tool reconstruction, or proof execution. Required
compiler/translator observation adapters and the exact source-to-caller gate
are absent; profile proof and infra SHAs remain unset. No summary is
established and dispatch remains blocked.

Reviewed `required-item-representation.patch` and its matching tree at
`/tmp/a1-r-draft/src` against the pinned-source patch context. This is a source
review only: no schema generation, exporter, translator, compiler, verifier,
proof runner, or evidence was run or read. R, C, and G remain **UNRUN**; this
patch is not yet an executable or admissible candidate.

## R representation and transport findings

The patch keeps the ordinary type/region/clause encoders intact and introduces
local required-item encoders behind `SORT4_A1_CHECKED_TRAIT_CONTRACT=1`. The
scoped path handles the intended references, slices, tuples, ADTs, parameters,
primitive types, region outlives, trait clauses, and type projections. Unsupported
consts, binder kinds, region kinds, clauses, and type forms fail closed. For
the two current method signatures and the intended `FnMut`/`FnOnce::Output`
clauses, this is a plausibly narrow transport shape. It still requires exact
Cloud inventory confirmation and API/build validation.

**Blocker — generic use sites are not tied to generic declaration identities.**
`GenericParamDef` now transports `index` and `defIndex`, but scoped
`encode_required_ty` serializes `TyKind::Param(param)` as `param.to_string()`.
The translator decodes that string and admits `D.Param p` through `all_names`;
its declaration comparison is HIR-vs-compiler name/kind equality, and numeric
indices are only checked for uniqueness among themselves. It never proves that
each signature or clause parameter occurrence resolves to the declared HIR and
compiler binder. A same-spelling parameter from another scope/identity can
therefore pass the current name-based shape checks. Carry and validate the
actual parameter identity at every scoped `Param` use (or establish an equally
strong verified identity map); merely transporting declaration indices is not
enough. Do not claim binder-safe conformance until addressed.

The new region encoding is materially better scoped: bound-region IDs include
the owning required item, signature/clause scope, de Bruijn depth, variable
index, and compiler region kind; clause binders use their own ordinal scope.
The translator checks the expected owner/scope/index/kind spelling and uses
structural alpha correspondence between the separate FnMut and Output binders.
The elided/explicit role still derives from the compiler's printable region
classification because the native contract generator uses that role to detect
mutable input borrows. The narrow source shape and explicit three-borrow check
make that a visible constraint, but the final gate must compare the complete
native contract against OFF and verify its normal and unwind outcomes. The
current patch does not itself establish that equality.

The scoped type checker rejects unsupported top-level forms, but accepts every
`D.Param _` recursively. This compounds the generic identity gap. It also
validates HIR/compiler generic declarations by rendered name/kind, not numeric
position-to-use correspondence. Several implementation assumptions remain
uncompiled (including the rustc `GenericArg`/`Term` API calls and Cap'n Proto
builder calls); these are build questions, not findings that can be resolved by
static inspection.

Schema additions use new field ordinals after existing fields, and the patch
updates the local exporter and translator reader accessors consistently in the
draft. IDs are kept distinct for required method, generic parameter, body,
trait impl, and impl item records. That is useful for distinguishing the two
generic impls even when their printed method paths both substitute `Self=T`.
However, downstream C/G code must match these numeric identities to one
compiler-produced method/body inventory and must not fall back to printed
names when an identity is absent, duplicated, or inconsistent. The R patch
alone does not implement that gate.

The `TraitImpl` collector admits only the exact root path when opted in and
explicitly panics on a qualified path ending in
`::StableSmallSortTypeImpl`; this honors the stated root-fixture scope for the
ordinary qualified case. The environment variable is only an opt-in, not a
source certificate. A caller-side source gate must still bind the exact std
bytes to the root fixture and reject a qualified or altered source before
export/dispatch. Likewise, the translator's exact root-name branch is not a
source-binding mechanism.

## C/G gates and decision

No proof-producing integration or verification was reviewed here. Before any
Cloud submission, the following remain required, including the known gates in
`A1-RCG-SEMANTIC-GATES-2026-10-17.md`:

- Fix the generic identity gap above and add a malformed/same-name binder
  negative that reaches the intended identity check.
- Wire the exact-source certificate and post-AST dispatch gate. The opt-in flag
  and root display name do not certify source bytes.
- Make summary publication contingent on both actual threshold implementation
  bodies and their trait-prototype conformance checks succeeding. Preserve the
  existing implementation-first proof ordering; a consumer must not receive an
  unverified summary through a skipped, assumed, or not-yet-checked body.
- Complete the full required positive/negative matrix, including OFF control,
  both implementation identities, both conformance obligations, caller/generic
  overflow obligations, interface and binder negatives, and native contract
  preservation. A missing case or wrong-stage negative leaves A1 UNRUN/blocked.

The semantic route remains in scope only as the previously authorized root
fixture experiment with the frozen kernel/model/prelude/refiner. Until these
representation, source, summary-ordering, and matrix gates are resolved, the
R/C/G draft is **NO-GO for Cloud dispatch** and makes no proof claim.

## First-matrix diagnostic cuts and `-focus`

The agreed first matrix explicitly permits the P0 observer's diagnostic cuts:
P0 is defined to return immediately before `small_sort` on the base path and
before the non-base continuation. P0c therefore proves only the threshold call
and guard arithmetic. P1 separately retains the original generic
`small_sort(v, scratch, is_less)` call and checks the interface/translation
shape; it does not prove that caller body. The matrix requires original default
and Freeze bodies plus the original call to remain in the full source
normal/readonly export inventory and refinement. Its requirement to connect
all actual helper dependencies applies to a **full-body proof unit** such as
later P2; it does not make P0 a helper proof or require P0 to consume helper
summaries. Diagnostic cuts must remain labeled and cannot be presented as the
full source theorem. The first unit may retain helper/insertion dependencies as
explicitly unproved diagnostic-cut bodies; the original full source dependency
inventory must still be recorded, and no P0 proof may consume a summary from
those cut bodies.

There is an important implementation constraint: the pinned exporter walks
all item-like bodies and adds the resulting MIR body list to the export
(`src/rust_frontend/vf_mir_exporter/src/lib.rs:234-291`). The translator then
maps the body list through `translate_body`
(`src/rust_frontend/vf_mir_translator/vf_mir_translator.ml:8091-8117`);
`-focus` is not an exporter or translator body filter. VeriFast documents
`-focus` as checking only the function containing the selected source line
(`src/vfconsole/vfconsole.ml:600`), and its `check_focus` gates symbolic
execution of statement ranges (`src/verify_expr.ml:154-161`). Therefore the
defensible setup is: keep the exact original bodies/call/dependencies in the
same exported and translated unit; add separate source-certified diagnostic
observer bodies with explicit cuts; use existing `-focus` only to select the
intended P0 obligation; and never let those cuts replace, summarize, or redirect
the original impl bodies or the original generic call. Helper/insertion
dependencies can be represented by labeled diagnostic cuts for P0/P1, provided
the original dependency inventory is retained and none of those cut bodies is
verified or consumed by the P0 target. If the resulting full exported unit
cannot translate/refine, P0 is blocked; the matrix does not authorize a
translator body-filter workaround. Summary availability must remain blocked
until both original threshold implementations and their conformance checks
succeed.

## Revised R patch review — SHA-256 `146aa2444b03ef8e50a5bb5ac45ce1f37f699b5c9f273120d9d45babaa27fb98`

This review supersedes the earlier generic-use-site finding only in part. The
new `TypeParamBinding` table carries `Self` and method type parameters in
compiler order with index and DefId index. `encode_required_ty` now derives a
wire alias from the actual `ParamTy.index`, and refuses a parameter not found
in the owning trait-plus-method type parameter list. The translator checks
`Self` at index zero, matches method binding names against HIR parameters,
matches method indices/DefIds against `GenericParamDef`, checks uniqueness,
and maps each type-use alias through that table. The revised AST order is
`Self, F, signature lifetimes`, consistently with `ast_param_order`. This
addresses the specific prior loss of `ParamTy.index` at the exporter use site;
it is still an uncompiled source claim, not verified behavior.

Region transport is also more explicit now: aliases are separate from scoped
semantic rows, the translator validates row uniqueness and binder positions,
and converts alpha-renamed wire aliases back to canonical owner/scope/depth/
index/kind IDs before AST construction. Signature regions must be the three
distinct input lifetimes in binder order; each HRTB clause validates its own
row count and binder aliases. The FnMut and Output clauses must each have two
distinct bound regions, the expected tuple of shared Self references, and the
same F; Output must be bool. The code rejects unbound type parameters, free
signature/outlives regions, repeated semantic region identities, extra scoped
region rows, missing F, and missing/duplicated FnMut or Output clauses. A
consistent alpha rename is not rejected by a literal-name allowlist. These
checks cover the listed binder-collapse, free-region, region-swap, no-F, and
HRTB/Output negatives structurally, but the required controls remain UNRUN.

**Remaining interface-shape blocker.** The A1 branch imposes the full three
input shape on `small_sort`, but does not check its output is unit. For
`small_sort_threshold`, it does not require zero inputs, zero signature
lifetimes, or a `usize` result: the generic `check_type` accepts any supported
unsigned integer and does not constrain the argument list. Both function
shapes must be exact before the native threshold contract or common
implementation contract can be attached; add explicit checks for safe
zero-argument `() -> usize` threshold and safe three-argument
`(...)->()` small_sort (plus the expected lifetime/generic counts). The source
certificate is not wired yet and cannot currently supply this missing gate.

There is also an identity-table validation boundary to keep explicit. Wire
type aliases are intentionally alpha-renamable, and actual use aliases are
generated from `ParamTy.index`; the translator then treats the binding table
as the alias-to-compiler-identity map. It does not independently encode a
numeric identity on each Cap'n Proto `Ty.Param` use or verify the alias's
owner/index spelling. This is coherent if exporter output is source-certified
and treated as one compiler-produced artifact, but a mutated serialized table
could reassign aliases while preserving uniqueness/order checks. The source
and post-AST gates must establish that the representation being consumed is
the exact compiler/exporter output for this certified unit; synthetic malformed
inputs must remain explicitly without compiler/refinement provenance. Do not
count type-use identity as independently established by these checks alone.

Static API inspection found no definite compiler API mismatch in the new
`ParamTy.index`, `ParamTy.name`, `GenericParamDef.def_id.index`, HIR generic
query, binder-kind, or Cap'n Proto builder usage against the pinned source
patterns available. This is not a compile result. R/C/G remain **UNRUN**; the
source certificate, post-AST dispatch gate, threshold summary publication
ordering, full first matrix, and native contract/outcome comparison remain
pre-Cloud blockers. Existing full-source and diagnostic-cut distinction above
continues to apply: P0/P1 cuts are admissible only as labeled unproved
dependencies, not as implementation summaries, while original bodies and call
remain in the paired inventory.

## Final R revision review — SHA-256 `09330d3b2ac58e3e64acd8b6efa8d8f3f40bb9342b23d6841362e2ff2ee27b12`

The new exact signature checks close the previous shape gap: the exporter now
requires exactly the two associated functions `small_sort_threshold` and
`small_sort`, rejects other associated item kinds and duplicate/unexpected
method names, and the translator requires safe `() -> usize` for the threshold
and safe three-input `(...)->()` for `small_sort`. The exporter also serializes
trait-owner clauses separately from method clauses, and the translator checks
the source `Self: Sized` parent clause before carrying that bound into the AST.
These localized changes match the current root trait's visible source shape.

**Must-fix identity mismatch in the actual `small_sort` HRTB rows.** The
exporter encodes method clauses with owner `def_id.index` (the required method
DefId), but builds their `clause_N` `ScopedRegionBinding` row aliases using
`trait_def_id.index`. The translator's `check_binder` requires the row alias to
equal the encoded `Clause.bound_regions` alias. The FnMut and FnOnce::Output
clauses each have bound regions, so these owners differ and the intended actual
interface is rejected at binder validation. Generate those method-clause row
aliases with the method `def_id.index`. The new `parent_clause_N` encoder uses
`trait_def_id.index`, while its row generator uses method `def_id.index`; that
is the same mismatch for parent clauses with binders. The current parent
`Sized` clause has no bound region, so this second mismatch does not affect this
fixture's current parent clause, but it should use `trait_def_id.index` as well
to keep the scope identity consistent.

The final revision is therefore still **NO-GO for Cloud dispatch** pending
that localized owner correction and its review. I found no additional definite
compiler API mismatch in the revised source by static inspection. Exact source
certification, dispatch admission, body-receipt summary ordering, native
contract outcome comparison, and the complete first matrix remain separate
UNRUN gates; the corrected R transport would still make no proof claim by
itself.

## Frozen R source review — SHA-256 `3b13921e84f1399fe4bf163a1fb59015739c4c7f97ae21a8a3c653b49224e903`

The final source corrects the two scoped-region owner mismatches recorded
above. Method `clause_N` aliases are now built with the required method's
`def_id.index`, matching method-clause encoding; `parent_clause_N` aliases use
the parent trait DefId, matching parent-clause encoding and
`parent_def_index` normalization. It also separates type-parameter aliases
from region owners: `TypeParamBinding` records an alias derived from the
required method owner and `ParamTy.index`, and `encode_required_ty` uses that
stored alias even while encoding parent clauses. The parent `Self: Sized` and
`Self: StableSmallSortTypeImpl` clauses therefore refer to the same `Self`
binding as method/signature types. The exact safe signatures and closed two
method inventory remain checked. I found no remaining localized mismatch in
these fixes by source inspection. Parent clause inventory and binder details
remain **UNRUN** until Cloud confirms the compiler-exported clause sequence;
this review assigns no source/proof credit.

## C/receipt source review — `checked-threshold-contract.patch` SHA-256
`c088252c81fe85072d6b92568d5553854b23a87a7478fc0a5696b0c11603f0e2`,
`a1-summary-receipt.py` SHA-256
`e43655638ec02a286f872c7a043ddb67fb0423998040a9c4e12557bcd53dae2a`

The publication split is source-consistent: actual threshold bodies receive
the range together with their native post; their custom implementation
prototypes retain that range in both body and caller stages; the public trait
prototype receives the range only at `SORT4_A1_STAGE=caller`, after the
receipt parser validates build, proof, infra, profile, source-pair, verifier,
exporter, schema, and compiler impl/item IDs. Inventory reconciliation occurs
later in the same translation and fails before output if receipt IDs do not
name the two actual compiler items. Without the receipt, generic dispatch keeps
the original trait item and receives only the native contract. The range
transform preserves pre, returning native post, and unwind post trees and
adds the bound only to the returning branch. The runner is not wired yet, so
these orderings are not operationally established.

One concrete digest-label error remains in the C patch: two capture messages
were renamed from `original_md5` to `original_sha256`, but still compute
`Digest.to_hex (Digest.string before)`. OCaml `Digest` is MD5, so these messages
would report a 32-hex MD5 value under a SHA-256 label. Restore the MD5 label or
use the runner's actual SHA-256 helper before relying on those capture records.

The receipt also does not carry the generated fixture/case `unit_id` or the
matrix target ID. It hashes the `verified/lib.rs` and `original/lib.rs` pair,
but the same std pair is used for multiple generated units, including
diagnostic and negative callers. Thus the receipt alone does not bind a caller
invocation to the exact source-certified P0c/P1 case; the not-yet-wired runner
must independently validate the complete fixture certificate/unit before
setting caller stage, or the receipt should include and the translator check a
fixture/manifest identity. This is the concrete source-admission boundary, not
a proof defect in the receipt's runner-reported body claim.

The receipt producer accepts caller-supplied hash values and the consumer
re-hashes fixed relative paths plus an executable-relative exporter/schema
path. The runner must calculate the producer hashes from precisely those same
files and execute from the workspace root; otherwise the consumer fails closed.
The profile hash is compared to the caller environment, while its content is
covered only by the pinned runner/profile setup. `write_cloud_receipt` checks
Cloud provider, phase, workspace path, and exclusive creation; the consumer
checks current Build ID and run pins. Build terminal success is not required
before receipt creation, which is necessary for a later caller stage in the
same build; the runner must nevertheless sequence receipt creation strictly
after both implementation body and native-envelope-conformance records pass.
The Python service intentionally validates attestations rather than proof
truth, so this sequencing belongs to the trusted Cloud runner and remains
UNRUN.

## Cloud runner integration audit — source-only, UNRUN

The established integration path is
`run-o26-refresh.sh`'s `o26-sort4-c1-current-recovery` branch (around line 741),
which calls `run-sort4-c1-current-recovery.sh`; the latter enforces the Cloud
phase/lane and currently dispatches
`sort4-caller-entry-native/driver.py`. The smallest in-scope route is a new
A1 driver behind that same guarded lane branch, with the exact A1 phase ID,
proof SHA, source/tool pins, and deadline carried into the runner. Do not reuse
the old caller `phase_gate` values as A1 authorization.

The reusable primitives are in `selected-runtime.py`: `stage` records bounded
Cloud subprocess stages; `clean_env` pins the preinstalled deps and toolchain;
`source_support` runs normal and readonly MIR export, `capnp decode ... VfMir`,
extracts a complete target record through
`overnight-sort4/capture.py:complete_function_record`, and runs paired
refinement; `verify_case` captures `-dump_ast_with_locs` then invokes
`verifast`. `driver.py:classify` and `selected-proof.py:classify_selected`
provide examples of stage, source-line, and intended-predicate classification.
No existing function accepts a focus line: `verify_case` currently invokes
the verifier without `-focus`. A1 must add exact focus selection for the
target body while retaining complete normal/readonly exports, full source
inventory, and refinement. `-focus` selects symbolic checking of a function;
it does not filter translation or exported bodies.

The A1 row map is explicit in `a1-contract-admission.py:MATRIX`; existing R
cases map to the current canonical controls: R1 generic `T` cast, R2
`MaybeUninit<T>` cast, R3 positive native consumer, R4 wrong pointer, R5
missing raw rights, R6 forbidden initialized-`T` cast, and R7 selected
threshold body. New matrix records need runner-side constructors that bind
case/source/unit IDs to generated immutable source, actual compiler item IDs,
run pins, verifier stage and intended location. `A1Admission` is expressly a
record validator, not a proof checker. Therefore a runner must derive records
from each observed verifier/AST/MIR stage and cannot infer body success,
conformance, or caller-summary availability from receipts, traces, or a
declared classification.

The existing `verify_case` path performs two exports/decode stages, paired
refinement, AST dump, and a verifier invocation per case; each proof stage has
a 240-second cap. This source does not establish that 26 naïvely repeated
pipelines fit the one-Build 900-second cap. Reuse paired support only for
byte-identical verified/original source pairs, retain separate proof records
for each target, and never reuse it across source mutations. Synthetic decoded
input controls must remain structural-only and receive no compiler or
refinement provenance. The fixture plan permits P0 diagnostic cuts before
helper continuation and before `small_sort` only when those cut bodies remain
explicitly unproved and ineligible as summaries; the paired inventory still
contains the original two impl bodies and P1 generic call. P0 is not a P2
full-caller proof.

## Final C/R source pins — review remains source-only

Parent supplied integrated translator SHA-256
`6cf19e4c4bbc4c856f0e6d416853f745f6128438373c321b4eb29a64a30ce8e3` and C
patch SHA-256
`16951eaf8c4d9eada7e57e5e501471553be330c443b6e78ac7fd676901a4f6d9` for the
current review target. R is reported frozen at
`4c0a43a10d5e023af7c190ed801546cf9877448d8dde65b39a773d68707f5a5e`.
These pins and the runner/service still require independent source review and
Cloud execution; they establish no compiler, conformance, caller, or proof
result. The A1 runner is not yet wired, and all 26 matrix rows remain UNRUN.

## Current R/C/G, service, and tool source checkpoint

Reviewed the current pinned inputs: R patch `4c0a43a10d5e023af7c190ed801546cf9877448d8dde65b39a773d68707f5a5e`, C patch `16951eaf8c4d9eada7e57e5e501471553be330c443b6e78ac7fd676901a4f6d9`, integrated translator `6cf19e4c4bbc4c856f0e6d416853f745f6128438373c321b4eb29a64a30ce8e3`, receipt module `bcc55360698346f0aa2dfb3858c6b555a9104db95308116d2c16c188a9b8a7dd`, admission module `b0703160700a799c9efba7a21a3a625aa13a68725f5a9cfcbd9a1ee7bd2b8b7d`, runner preflight `a3a8f684b9b1bcbc00cc167bae533050c172a1576eb82834fc0236416317a43a`, tool reconstruction helper `31237e0a435164bd14b73f6df2c5124df31d47b074f1623b3e37326ecf9b6e09`, and profile `3141dce7f83bce95b80dbfe112587d11d827ca24c03dfbf072eb4a854f49c827`.

For these R/C source revisions I found no additional localized representation
or AST-construction defect by inspection. The R path keeps separate method
and parent-clause scopes/DefIds, encodes compiler parameter identities, and
closes the exact two required-method and impl-item inventories; the root-only
trait-name gate refuses qualified suffix matches rather than silently
falling through. The C path retains precondition and both generated outcome
posts while adding the 16–32 returning range, gives both actual threshold
bodies and synthesized impl conformance prototypes the same common range,
keeps the public trait prototype native-only before receipt, and only adds the
public range in caller stage after exact tool/source/build/profile and numeric
impl/item receipt checks. The previously recorded mislabeled MD5 capture
messages are fixed in this C revision: they again say `original_md5`.

This is a source-candidate review, not interface or proof validation. I found
no source path that itself constructs a verifier result or proves that the
receipt's body/conformance attestations are true. That trust remains with the
Cloud runner. In particular, the current `a1-runner.py` explicitly stops at
`BLOCKED_UNIMPLEMENTED_STAGE` before fixture generation, tool reconstruction,
or proof execution; its `MISSING_BACKEND_HOOKS` list still includes compiler
impl/item extraction, required-item/native-post inspection, exact focused body
and conformance execution, source-bound caller dispatch inspection, actual
decoded-MIR synthetic injection, and the 26-row classifier. Thus there is no
complete backend adapter and no working source-certificate-to-call gate yet.
The trait/interface and threshold-body fixtures are ungenerated, receipt
publication/order has not been exercised, the admission module is still being
revised, and the A1 tool/profile do not identify a proof/infra SHA. Dispatch
remains **NO-GO**. All R/C/G, build, body/conformance positives, intended
negative predicates, regression rows, and matrix classification remain
**UNRUN**; this review assigns no proof credit.
