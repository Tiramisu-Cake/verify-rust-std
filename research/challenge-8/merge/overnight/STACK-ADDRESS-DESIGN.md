# Hidden stack address projection — design and review before implementation

Experimental fallback for unchanged actual bidirectional_merge, source blob
40939f922bcb6fdc7ee0d30427fa861827043827, VFf76012fb/cleanup94fe2cd6.
Run37744660894/proof6ba53993 first reaches body31executions and fails a strict
loop leak on existing Range/tuple3 stack fields/padding and func_lft. Stock
Some/body invariant+iterator/lifetime is tested separately before applying this
extension. A source-level ghost name cannot denote the unnamed compiler locals.

## Exact contract and boundary

Ghost-only expression `mir_stack_addr(N)` accepts one literal positive decimal
raw MIR local ID. Resolve that exact ID via the current body's decoded local
and translator name map, not a string prefix or guessed `$_N`. Eligibility:
hidden compiler local with no source/VDI alias; not return-place0 or a parameter;
stock translated nonparameter StructType, declaration initializer None, and
already materialized as a RefType/stack object by stock allocation rules. All
MIR local declarations use initializer None, so that fact alone is insufficient.

Rewrite ONLY this ghost expression to ordinary AST AddressOf(Var(actual_local)).
No runtime/MIR operation is replaced, inserted or deleted. No resource chunk,
ownership, lifetime, value, validity, allocation bound, provenance equality or
assumption is produced. Source annotations must carry the ordinary stock
padding and every existing field permission at the resulting address; field
options may change as the original MIR overwrites/moves temporaries. Ordinary
kernel address/type/resource/return/unwind/leak/dead/refinement rules still apply.

Every occurrence must be admitted against fresh same-SHA compiler MIR and the
exact ghost/runtime source. Reject missing/duplicate IDs, renamed/source locals,
scalar, initialized nonmaterialized value, parameter, return-place, nonliteral
or invalid arity/type arguments, and runtime occurrences. IDs can shift when
annotations change; an old numeric ID must not silently retarget a different
local. The application gate must check the expected type and source/call role
for each addressed temporary. Type checking alone does not establish that role.

## Self-review

Kernel produce_object allocates uninitialized structs as RefType regardless of
the address_taken flag. Restricting the rewrite to those already materialized
objects avoids changing stack representation when AddressOf marks the flag.
Inline AddressOf avoids the ghost-let scope problem in independent loop blocks.
Exposing an address does not provide dereference permissions: those remain the
existing exact stock chunks, consumed and reproduced by the invariant. This is
still a trusted translator/proof-AST change, separately pinned from W1/M2/C1/
cleanup and the independent usize specification; not a verified memory primitive.
No whole merge acceptance follows from address projection or len2 diagnostics.

## Hosted matrix

Positive: exact hidden Range/tuple3 address identity and already-stock materialization;
explicit complete padding/field frame across an ordinary loop and normal return;
actual bidirectional Some/body invariant with current source/F/options, iterator,
lifetime and exact compiler-temporary frame; full unchanged-source/MIR/export/
decode/refinement and function return/leak/unwind/dead gates. Repeat all affected
Rust/C/C++/G2/A/B/W1/C1/M2/cleanup boundaries before any profile admission.

Frontend admission controls: missing/high/zero/negative/nonliteral ID, scalar,
source-named/parameter target, type/role mismatch, wrong arity, and exact-name
collision; no body entry counts as a proof-negative. Proof controls: wrong address
association, forged points-to or T.own, omitted stack field/tuple frame, omitted
iterator/F owner and false callback-unwind destination stage must reach their
specific obligations. Preserve every original INCONCLUSIVE diagnostic and
calibrate exact new errors only after observing the intended target.

Compare feature on/off on identical compiler MIR: no additional runtime ops,
locals or allocation/resource production; only validated ghost AddressOf nodes.
Unknown patterns fail closed. First new binary comes from pinned fresh hosted
source build; old console cache cannot stand in for the extended profile.

## Implementation draft and admission notes

`stack-address.patch` is based only on the pinned post-cleanup translator text
with SHA-256 `0e450267e453493f894b91763ef9412bf41b7ee8d3988115f24126456ab4e025`.
It rewrites parsed body ghost expressions after MIR locals and the VDI name map
are decoded, before basic-block translation and `find_blocks`. The raw `_N`
declaration must occur exactly once at list index `N`, be after the return place
and parameters, have no VDI alias, retain the exact stock translated hidden name,
and have a `StructTypeExpr` type. Any other case raises a source-located static
error. The emitter prints the raw ID, translated name, structural type spelling,
declaration span and use span for the hosted admission certificate.

The marker is accepted only as a static call with one positive,
unsuffixed decimal literal argument and no type arguments or predicate indices.
Supported ghost statements and expressions are traversed structurally; the
number of rewritten calls must equal the marker occurrences in the original
body ghost annotations and loop-spec starts. This check rejects unhandled AST
contexts rather than allowing an unresolved marker to reach verification.
Contract and ghost-declaration markers, and markers in assumed-false bodies,
are rejected. The marker's expansion is only `AddressOf(Var(existing_local))`.

`stack-address-cases.rs` contains translator-admission diagnostics for syntax
and missing IDs. They have no claimed error counts or accepted negative status.
Positive resource probes, exact Range/tuple3 IDs and role-sensitive controls
remain pending fresh hosted MIR inspection. For each active ID, admission must
match the printed declaration span and type to the expected Range/tuple3 call
role; this is outside the translator's structural eligibility check.

## Normal-preprocess MIR admission

The old `decode.out` is **not** the MIR consumed by VeriFast. The separate
read-only exporter passed `--vf-rust-mir-exporter:preprocess-readonly`; VeriFast
invokes the same exporter in normal mode, where the preprocessor inserts ghost
command calls into the in-memory source. Run 37746828112 demonstrates different
local IDs despite unchanged on-disk source hashes: read-only MIR has Range
`_33/_34` and tuple results `_48/_60`, whereas VeriFast's proof AST has
Range `$_34/$_35` and tuple results `$_53/$_65`. Using the old decoded output to
approve numeric markers would bind them to the wrong locals.

`stack-address-admission.py` therefore accepts only a newly captured normal
export with exactly the exporter arguments VeriFast passes. Its provenance JSON
must contain `normal_preprocess: true`, `command`, `source_sha256`,
`source_unchanged: true`, `mir_sha256`, and `decoded_sha256`. The hosted pipeline
supplies `--decoded-normal`, `--mir`, `--source`, `--provenance`,
`--expected-source-sha256`, and `--output`. The decoded text is parsed to the
end with duplicate fields and unknown syntax rejected. The pipeline must run
`capnp decode` on the captured normal-export MIR and record both hashes; the
script checks those hashes and the exact source SHA. It cannot independently
prove that a decoded text file was generated from a binary whose bytes it also
receives, so that producer relation remains an orchestrator gate.

The script discovers the four IDs from unique MIR call destinations/operands,
checks exact Range and `(raw *T, raw *T, raw *mut T)` types, declaration-index
identity, lack of VDI aliases, unchanged source call spans, continue-unwind,
construction of the range at the loop, movement to the source iterator, and
tuple field flow to the six source-named cursors. On the final source it also
requires all 14 marker occurrences on the single loop-body invariant line,
with the discovered IDs repeated 3/3/4/4 times. Run once to discover roles,
insert annotations, re-export the *final* source, and require the final IDs to
match its own markers. Compare the VeriFast proof AST's four local declarations,
types, calls and source spans to that final certificate before treating a proof
result as admissible. This is a read-only certificate, not a proof of memory
ownership, a verifier semantic change, or an accepted whole-function result.

The admission script itself is restricted to GitHub-hosted execution on the
owned `overnight/merge-26.10` branch and writes a new certificate with exclusive
creation; an existing output is never overwritten. Discovery output reports
the raw IDs and spans but has `status: discovery`, and `--require-final` rejects
it. Final output includes the observed marker count and the exact final source,
normal MIR and decoded-text SHA-256 values. A mismatch reports both expected
and observed IDs/counts. In-memory negative controls must reject a destination
swap, changed tuple type, VDI alias, wrong tuple field, changed unwind, malformed
marker, and wrong MIR/source/decoded provenance hashes at the admission gate.

The current script deliberately does not parse or certify VeriFast's OCaml
`proof-ast.ml`: no stable complete schema or AST rewrite artifact for the new
marker exists yet. A separate hosted comparison of the final proof AST's
four declarations, types, call-result assignments and source locations against
the final normal-MIR certificate, plus all fourteen ghost-only address rewrites,
is required before calling the result accepted. The script's `final` status
means the MIR/source role check passed; it does not assert that AST comparison
or whole-function verification passed.

First integration uses IDs34/35/53/65 only on the existing one-line invariant;
no extra in-body ghost command is introduced there. Fresh normal MIR role
admission must validate those IDs and all14uses; a mismatch is INCONCLUSIVE.
The address-rewritten AST is not yet available for independent correspondence
review, so its separate acceptance gate is explicitly OPEN/125 and the actual
bidir result cannot classify PASS even if the diagnostic body verifies. This
first capture enables that review; it neither asserts a missing certificate
nor invokes a nonexistent certificate option. All mandatory old gates remain.
