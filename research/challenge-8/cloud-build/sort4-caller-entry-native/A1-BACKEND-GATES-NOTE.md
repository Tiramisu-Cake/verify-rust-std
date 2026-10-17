# A1 AST and backend gate plan — source only, UNRUN

This note describes a bounded adapter design from the pinned sources. No
compiler, exporter, translator, verifier, proof, or AST dump was run. It grants
no proof credit and does not clear the A1 runner's NO-GO status.

## Actual AST dump format and extraction points

`vfconsole.ml` registers `-dump_ast_with_locs` at line 629 and, in the
`emitter_callback` around lines 666–679, writes
`Ocaml_expr_of_ast.of_list Ocaml_expr_of_ast.of_package packages` through
`Ocaml_expr_formatter.print_ocaml_expr_to_file`. The result is OCaml
constructor text with `Func (...)`, `CallExpr (...)`, `SwitchExpr (...)`,
`SwitchExprClause (...)`, and `loc "..."` nodes. It is not JSON or a verifier
trace. The existing bounded scanner in `selected-proof.py` (`_balanced_end`,
`_split_ast_fields`, `_selected_ast_inventory`, `_call_records`) already
extracts the 13 `Ast.Func` fields and six `Ast.CallExpr` fields; these are
reusable patterns, but the selected-branch inventory is hard-coded and cannot
be used as an A1 classifier unchanged.

For `Ast.Func` (`frontend/ast.ml:994`), fields are: location, kind, generic
parameters plus bounds, return type, name, parameters, nonghost flag,
function-type/prototype proof fields, optional `(pre, (result_name, post))`,
termination flag, optional body, virtual flag, overrides. A focused adapter
should require exact field count and parse the `spec` and `body` options; it
must distinguish a prototype (`body=None`) from a body definition (`Some`).
The `-emit_sexpr` path is another possible bounded format: `SExpressionEmitter`
serializes function names, parameters, generic parameter names, pre/post and
switch clauses, but omits locations and generic bounds. Prefer the existing
location-bearing OCaml AST dump for source-line and tparam-bound checks.

For the checked threshold post, `gen_contract` constructs the native
precondition and `fn_outcome` returning/unwinding post. The C transform in
`Sort4A1Contract.threshold_contract` only wraps the returning branch's native
post in a `Sep` with `16 <= result && result <= 32`. It returns the original
precondition subtree and original unwind subtree. A structural AST gate can:

1. Find exactly one common bodyless
   `StableSmallSortTypeImpl::small_sort_threshold` prototype and the two
   compiler-item-bound A1 implementation prototypes plus their corresponding
   body definitions. Bind those records to numeric `TraitImpl`/item IDs and
   source spans from the paired decoded MIR inventory; names containing
   printed IDs alone are not the identity source.
2. Parse each `spec` as `Some (pre, (outcome, SwitchExpr(...)))`; require the
   exact `fn_outcome` switch with one returning result binder and one
   zero-argument unwinding arm. In the returning arm require exactly one
   appended range conjunction over that arm's result variable. In the
   unwinding arm require no range conjunct.
3. Normalize only source locations and alpha-bound result/local names. Compare
   common prototype, both implementation prototypes, and both body contract
   ASTs so that their preconditions, native returning post after removing the
   exact range subtree, and full unwind post agree under that explicit alpha
   map. Also check the common prototype's pre/range/unwind structure directly;
   cross-comparing only the two impls would miss a shared weakening.
4. Keep this structural result separate from proof. A successful focused
   verifier run of each actual body plus its header-compatibility check is
   needed before a body/conformance attestation; AST equality alone is not
   conformance evidence.

The dump does not contain compiler DefIds for generated A1 aliases, so the
adapter must cross-bind the AST records to actual MIR `defIndex` and
`TraitImplItem.defIndex`, source certificate spans, and exact `(verified,
original)` pair. The AST's rendered lifetimes are not a substitute for
compiler region IDs; validate the `small_sort` signature and FnMut/Output
clause binder identities from R's decoded compiler representation, then
compare the AST names/types through the explicit ordered alias map. The
threshold item is `() -> usize`; its only semantic generic is the trait's
`Self`, mapped to the impl's `T`. The `small_sort` interface must preserve
`Self`, method `F`, three distinct input-borrow lifetimes, and the HRTB
FnMut/Output=bool clauses. S-expression generic names alone cannot establish
bounds or binder identity.

## Call binding and the limit of dispatch traces

In AST, a `CallExpr` has six fields: location, callee name, type arguments,
predicate indices, argument patterns, and method-binding kind
(`frontend/ast.ml:513`, `Ocaml_expr_of_ast.of_expr`). For P0c require the
single source-certified observer's actual threshold call to name the original
common trait item, have type argument `T`, no value arguments, and no impl
alias. For P1 also require the original `small_sort` common item, `T` and `F`
plus the three lifetime slots, and the three original slice/comparator
operands. Reject any `default16`, Freeze, or generated implementation alias
call from those caller bodies. Pair this AST site with the raw compiler MIR
`FnDef` DefId/substitutions at the exact source location and the source
certificate; the final AST may represent late-bound lifetime arguments as
inferred/erased and cannot alone prove the three compiler binder identities.

`SORT4-A1-DISPATCH`/`SORT4-A1-CALL-AST` prints useful diagnostics, but traces
alone cannot establish the final call AST, caller source identity, or that a
verifier invocation consumed the common prototype. Require the actual dumped
AST call plus compiler MIR binding, the final opt-in/profile pins, and the
focused caller run. The current source's gate also requires an exact observer
focus, while the runner still lacks the actual export/AST/proof adapters.

## Known limits and required evidence

`-dump_ast_with_locs` is emitted from the frontend package callback; it is a
translated AST snapshot, not a kernel proof result. It can establish
structure and explicit contract preservation, but not that `EnsuresAsn`
conformance or the focused body succeeded. Conversely, a dispatch trace is
not an AST or a proof. The adapter must keep three records separate: (a)
compiler/source identity and interface-shape checks, (b) native contract
structure and actual call binding, and (c) verifier observations for each
focused implementation/caller obligation. Any missing or inconsistent stage
is `INCONCLUSIVE`, not a negative result or summary.

The current runner preflight does not yet call the exporter, decode/inventory
adapter, AST parser, focused verifier, or classifier. The full AST/native-post
and call gates above are therefore design guidance only; all remain UNRUN.

## Synthetic transport adapter source review — UNRUN

Source reviewed: `a1-synthetic-backend.py` (SHA-256
`5e97783d9cfa98388f0eae646e78432ebd35648cf79aa86ae423996dc72ad40f`). The
sibling-exporter mechanism matches the pinned frontend: `rust_fe.ml:102–129`
sets `bin_dir = Filename.dirname Sys.executable_name`, invokes the sibling
`vf-rust-mir-exporter`, and supplies the Rust toolchain sysroot/args. The adapter
copies the pinned console bytes into a disposable facade, symlinks the
unchanged support tree, and puts the replay shim only at that sibling path.
The shim accepts only `verified/lib.rs`, checks the encoded message hash, and
writes that exact Cap'n Proto payload. This is a plausible transport for
synthetic-interface negative controls; it does not edit the candidate console,
exporter, schema, or source pair. The successful return labels the result
synthetic, unclassified, without compiler/refinement provenance or summary/proof
credit, as required.

The adapter is not a complete AST gate or runner. It records an AST path but
does not require the dump to exist, parse it, classify translator exit/refusal,
or prove the real baseline's provenance; its docstring correctly delegates
baseline provenance to the outer runner. The caller must validate that
`baseline_sha256` came from the same-build paired export and bind decoded and
binary inventories to exact source/tool pins. A future focused-observation
stage must parse the AST and distinguish an intended R refusal from setup,
transport, frontend, or unrelated translation failure. `-focus ...:0` is
appropriate only for interface observation; it cannot establish body
verification or post conformance. All such gates and every mutation remain
UNRUN. No source-only review authorizes a Cloud run or proof credit.

## Compiler-inventory adapter source review — source-span correction required

Reviewed `a1-compiler-inventory.py` SHA-256
`d7f4df7eed00665c128e71ab9bd26cda919772dff5bd95462cbbba6e818c3749`, its
synthetic test source SHA-256
`e696f6374659213758d103ff291c3e3f7d18a1d1ea2dc7b4f31eaaa22d5d0a54`, and
focus collector SHA-256
`eb424187959aae3ce0095a678c95850b361978751d556c529daeae0dd1a5ddf8`.
The added `defIndex`/trait-owner fields are consistent with the reviewed R
schema/exporter patch. The schema's filename nesting is also represented in the
parser: `FileName.real`, `RealFileName.localPath` or `.remapped.virtualName`,
then `Loc.file/line/col`; span endpoints are rustc `lo`/`hi`, and slicing them
as half-open is consistent with rustc `Span` endpoints. The exporter calls
`lookup_char_pos` to encode each endpoint.

There is one concrete source-span bug: `_body_map` takes `Body.span` as the
source implementation range. In the schema, `Body` has separate `span @6` and
`impSpan @7`. The exporter encodes `Body.span` from `body.span` (MIR span), but
encodes `impSpan` from `span_utils::body_imp_span`, which explicitly obtains the
HIR body expression span (`hir_body.value.span`). The source-binding check needs
the latter for the claimed implementation-body range and nesting; use
`impSpan`, not `span`. At present `span_slice`'s `body` result is also unused,
so the implementation expression itself is not checked. This must be fixed
before treating the source binding as authoritative.

The synthetic tests model local relative `verified/lib.rs` spans, but the
exporter serializes `RealFileName.localPath` directly and the source-only review
cannot establish the runtime spelling produced by the pinned compiler for the
relative CLI input. Keep the exact path check fail-closed, but confirm the
actual encoded path via the allowed paired Cloud inventory before accepting a
row; do not relax to suffix matching. `a1-focus-backend.py` remains a raw
collector only: it records focused verifier stages and AST artifact presence,
without classifying results or minting proof credit. Its focus does not filter
export/translation, matching the source behavior described in the module doc.

## Call binding, AST gate, and focus collector review — UNRUN

Reviewed current adapter pins: compiler inventory
`6b1cf336d7af59a92eaf023e9870b93de8b1b0b9aa74d20ceb42a636fbfd72dc`, call
binding `5dec59a2e0b2fa175150b9aa1268232b61940fec0a9f25fbced3eda4dca5ab29`,
AST gates `2c31644524919c9b4cd22b0b7a0e444d255a630f972ac56a53e9e93c657c0116`,
and focus collector `eb424187959aae3ce0095a678c95850b361978751d556c529daeae0dd1a5ddf8`.
The earlier `Body.impSpan` issue is fixed in the current inventory source: it
retains `mir_span` and `imp_span`, and binds the latter to the compiler body
expression range. The AST node arities/constructors used for `Func` (13),
`CallExpr` (6), `SwitchExpr` (4), and `SwitchExprClause` (4) match
`ast.ml`/`ocaml_expr_of_ast.ml`; `Func.body` is indeed `None` or `Some (stmt list,
close-brace-loc)`. `-dump_ast_with_locs` runs from the package callback in
`verifast1.ml:1234` before focused verification, so the AST is a full-package
translation snapshot, not evidence that any AST body was verified.

Three localized gaps remain before a classifier can treat these records as a
complete body/call gate:

* `a1-ast-gates.py::_threshold_header` checks return type, value-parameter
  emptiness, and safety-related flags, but never checks `Func` field 2 (generic
  parameters/bounds). `threshold_posts` also does not compare this field against
  the common prototype. R's compiler-interface checker validates compiler
  generic/clause identities, but the AST gate should still require the expected
  `Self`/method-parameter order and bounds, or compare the generated common and
  implementation AST generic lists under an explicit alpha map. Present code
  can report structural post agreement while the translated function generic
  envelope differs.
* `a1-call-binding.py::_analyze_functions` delegates to `_selected._mir_input_shape`
  for the original caller signature. That helper checks the three mutable
  reference positions and types but only requires their region IDs to be
  strings; it does not require the `v`, `scratch`, and `is_less` input regions
  to be pairwise distinct. The source signature certificate is exact, and R
  separately checks three distinct required-method input lifetimes, but this
  caller-MIR gate should check its own three distinct compiler regions.
* `a1-focus-backend.py` writes `proof-ast.ml` in the fixture directory and
  accepts any file found there after the invocation. It does not first require
  that path to be absent or otherwise bind its post-run bytes to a newly
  produced file. On a reused fixture a stale AST could be copied after a run
  that failed before dumping. Require absence before invoking, or use a
  per-invocation output path under the fresh evidence root.

For the kernel focus semantics, `vfconsole.ml:600` parses the source path/line;
`verify_expr.ml:154–162` includes a focus when it falls in the inclusive line
interval from a construct's start to end and the root source path matches.
`verifast.ml:verify_funcs` checks the implementation header against its
prototype via `check_func_header_compat_core` before calling `verify_func`;
both the compatibility check (`verify_expr.ml:224`) and body verifier
(`verifast.ml:3335`) have their own focus interval gates. The compatibility
routine produces/consumes implementation/prototype preconditions and normal
posts, then compares exception posts (see `verify_expr.ml:194–297`).
`EnsuresAsn` carries the post continuation in both directions
(`assertions.ml:615, 1520`). Therefore focusing the declaration line can reach
both gates when the prototype is present. Still, AST presence and a zero exit
alone do not prove the intended body count or which focus interval ran: require
exactly one source-bound definition interval at that line, its compiler item
identity and prototype, and successful verifier status. Diagnostics are needed
to classify a negative at the body obligation rather than setup, header
compatibility, or an unrelated failure. The current adapters do not provide
stage telemetry sufficient for that negative classification. All gates remain
UNRUN and do not clear runner NO-GO.

## Superseding focus-line correction — use actual `Body.span.lo`

This corrects the earlier suggestion to focus the lexical declaration or
`fnSigSpan` line. In the integrated translator, `span_get body_cpn` is decoded
to `loc`, and `mk_fn_decl` stores that as `Ast.Func.loc` (around lines
8324–8359); `LocAux.get_last_col_loc loc` supplies the body close-brace
location. Native contract generation separately uses `fn_sig_loc` from
`fnSigSpan` (around line 7719). The generated implementation prototype is
also built with `mk_fn_decl contract_template None` (around lines 10751–10760),
so the alias prototype and body share the `Body.span` location.

In the pinned kernel, `verify_funcs` calls
`check_func_header_compat_core l l` when there is no prototype proof, then
calls `verify_func`; the former's `check_focus` and the latter's body
`check_focus l closeBraceLoc` both use the inclusive range rule in
`verify_expr.ml:154–162`. Consequently, the focus line that selects both
header conformance and body checking is the paired compiler inventory's
`Body.span.lo` (`mir_span.lo`). Do not substitute `fnSigSpan.lo` or a lexical
function declaration line unless paired output proves they coincide. Match AST
`Func.loc` to `Body.span`, while using `fnSigSpan` to check contract source
anchors. Before interpreting a successful focused invocation as one body plus
its native header conformance, require exactly one AST definition interval
containing that focus line, its numeric compiler item identity, the matching
prototype, and a successful verifier exit. The package AST is emitted before
focus (`verifast1.ml:1234`) and is not itself a body-count or proof result.

## Final C focus review: caller receipt ordering blocks publication

Reviewed `checked-threshold-contract.patch` SHA-256
`9bafa1589220725769ce615f7473a918200b47c2406cf313da6e6186394f800c` and
integrated translator SHA-256
`1fc8db417c9ddf1cbd57ccd0a4903e683b77c46c624195ea649840cdadb8b5ec`.
The translator's body-stage restriction is now correctly based on actual
compiler `Body.span.lo`; caller stage likewise derives `observer_body_focus`
from the actual observer `Body.span.lo` and checks the explicit CLI `-focus`
against it. The call rewrite preserves common-item identity. In caller stage,
the unproved common `small_sort` call is rejected only when
`State.body_name = "a1_guard_observer"`; the original `quicksort` body remains
available for P1 translation/interface observation.

However, caller publication has a blocking initialization-order bug. In
`translate_vf_mir`, `translate_trait`/`translate_trait_required_fn` executes
before the A1 inventory/focus scan. Required-item translation calls
`check_publication_receipt` (~line 7228); that check reads
`observer_focus()` (~line 448), whose only assignment is later in the body
inventory scan (~line 17963). Thus `SORT4_A1_STAGE=caller` cannot validate the
receipt: it fails with “compiler observer focus not established” before the
scan computes the focus. Move a validated compiler inventory/focus prepass
(and publication-ID match) before trait translation, or equivalently stage the
receipt check until after that prepass; preserve the exact source/tool/build
and compiler-identity bindings. This is a source finding only; C/G remain
UNRUN and the runner remains NO-GO.

## C publication-order fix review — corrected source, still UNRUN

Reviewed patch SHA-256
`e7cdc8a8504338ccaab760975c1a3f1a739211d7f8d531dd214babc2005d894e` and
integrated translator SHA-256
`4e1c7e12dc67f3ea9f6305ea495f9503c170ad624612d0839dc8e8f00ae3a00d`.
The prepass now runs after `traits_cpn` and raw `bodies_cpn` are obtained but
before `translate_trait`: it resets transient observer/receipt state, resolves
the unique actual observer `Body.span` file to `verified/lib.rs`, stores its
`Body.span.lo` line, and checks the explicit focus against it. The receipt
parser therefore sees the real compiler-derived focus. The full two-impl/item
inventory and published-ID reconciliation still run after trait AST
construction but before body translation/call processing. A mismatched receipt
ID aborts the whole translation before the candidate declarations reach the
kernel or a caller can consume the stronger summary. This is a sound staged
ordering for the opt-in path; no receipt check was moved past the inventory
acceptance gate for downstream use.

The prepass does construct only a local candidate trait AST with the checked
contract before later inventory validation. Source control flow shows no body
or call translation and no kernel callback consumes that partial AST before
validation; failure aborts translation. The standard AST emitter is called
only after frontend translation completes. G remains limited as intended: in
caller stage it rejects the common `small_sort` call only inside the certified
`a1_guard_observer` body; the unmodified `quicksort` P1 body keeps its common
trait call. This review is source-only: R/C/G, receipt path, and matrix remain
UNRUN, with no proof credit or Cloud go-ahead implied.

## Region-identity transport risk — source-only, UNRUN

Pinned exporter source (`/root/verifast`, f760) shows that caller body
clauses and function inputs use different paths. `encode_body` encodes
`tcx.clauses_of(def_id)` through `encode_clause` (~1166, ~1347); trait and
projection clauses serialize binder entries from `bound_vars()`, naming
anonymous `Named(def_id)` entries using `def_id.index`. Their type arguments
then use the global type/region encoder. `Body.inputs` (~1374) also use the
global encoder through `tcx.fn_sig(def_id).skip_binder()` and `encode_ty`.

The global `encode_region` maps `ReBound(_, BoundRegionKind::Anon)` to a
string indexed by de Bruijn depth, not bound-variable index. Distinct Anon
regions at the same depth therefore collide; `ReEarlyParam` instead uses its
parameter index. The SmallSort body’s outer elided input references may be
early-bound, and its FnMut clause’s named binder entries may preserve their
distinct IDs, but source/pin inspection does not establish the actual compiler
encoding of these exact bodies or that clause argument regions match. No
actual paired export is available for this review. Treat call binding as a
fail-closed gate: a mismatch must stop before receipt publication or proof
classification. This is a conditional transport risk, not evidence of an
actual fixture failure. Extending the exporter fix from required-item
encoding to caller body transport would be a separate trust-scope decision;
R/C/G and all matrix rows remain UNRUN.
