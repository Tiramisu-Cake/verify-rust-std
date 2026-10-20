# Select R11 S2 P1 delta review

**Decision: GO for the P1 parser-gate delta.** Relative to S1 commit `5fc6f44b`, the P1 change is confined to normalizing one outer `ConstTypeExpr` around each small_sort parameter at the signature boundary. The two targeted R-only AST snapshots show this constructor around the Rust reference type. The gate checks the wrapper arity and location shape, then runs the existing strict decoder on the inner type. A second wrapper, malformed location tuple, and unsupported inner type fail closed.

The normalization does not edit the raw Func fields: the complete raw parameter field remains in `_small_sort_ast_header`, so header equality retains the wrapper and source location. The decoded signature still checks the exact three parameter names and order, reference mutability and regions, slice/`MaybeUninit`/`F` shape, then compares against compiler-derived identities and the existing baseline/source bindings. No first/last-by-order selection or leaf-name relaxation was added. The synthetic fixture exercises both the wrapped representation and the previously supported bare representation, and checks the header distinguishes them.

Evidence supports applicability at the reported failure-string and constructor level, not parser-input binding or causality. The saved Reader snapshots explicitly mark `parser_input_binding: NOT_ESTABLISHED`; the S1 Build also had an independent P0a wrapper blocker. This review gives no Build, verification, or proof credit. The same-build admission/receipts and all 26-case matrix scope are outside this parser-only delta and remain as recorded.

Validation: `test_a1_ast_gates.py` passed all 35 isolated synthetic tests. No compiler, source preparation, Cloud Build, or full runner was run. The concurrent P0c fixture changes are outside this P1 review.

## P0c S2 checked cleanup delta

**Decision: GO as the next bounded Cloud hypothesis.** The fixture now opens
the generated `Option_own` for the unchanged arbitrary parameter, matches that
same value, leaves `None` with no payload, and calls the existing checked
`drop` contract on only `Some(r)`. The pinned VeriFast enum-predicate generator
defines `Option_own` by constructor fields, so opening `None` yields `Emp` and
opening `Some(r)` yields `<&'_ T>.own(_t, r)`. The pinned `drop<T>` contract
consumes that own chunk and returns the thread token. This route preserves both
input variants and introduces no raw-reference ownership, leak, forget, or
axiom.

The edit changes generated observer cleanup only: it keeps the original
signature and source guard, places cleanup before both P0c and N-false31
returns, and appends one labeled cleanup after the unchanged P1 source prefix.
The synthetic construction controls verify both arms and all exits. They
passed 2/2. The earlier P0c S1 finding remains an observer proof failure and
does not establish a runtime leak.

I checked `'_'` against the pinned parser sources. The lexer accepts `_` as a
`PrimePrefixedIdent`; `parse_type` accepts that token after `&` and produces a
lifetime `IdentTypeExpr`, so this spelling is not rejected by the parser
grammar. The translator also recognizes lifetimes with the `'_` prefix in its
elided-lifetime contract handling. Those source paths do not establish that
this exact ghost `Option<&'_ T>` annotation resolves to the active parameter's
inferred region in the R11 effective overlay. I found no source-level proof
that it is invalid, so this is a concrete Cloud falsification point rather
than a pre-Cloud blocker. Cloud must still establish annotation resolution,
ownership of both variants, required posts and receipts; until then this
candidate has no proof credit.

### P0c lifetime typecheck re-review

**Decision for the current P0c text: NO-GO before Cloud.** The earlier
assessment that `'_'` was only an unknown Cloud falsification point relied on
the Rust parser accepting the token; that did not establish a well-typed ghost
type. At the pinned parser, `rust_parser.ml:103` turns `PrimePrefixedIdent
"_"` into `IdentTypeExpr (_, None, "'_")`. The verifier's
`verifast1.ml:2069–2138` resolves such an identifier only if it is in `tpenv`
or names a declared type; otherwise it reports “No such type parameter,
inductive datatype, class, interface, or function type.” Its
`RustRefTypeExpr` case recursively checks the lifetime expression at line 2223.
There is no `_` wildcard case there. The translator's `'_` handling at
`vf_mir_translator.ml:4283–4300` is specific to generated autocontract return
and mutable in/out classification; it does not rewrite this manually parsed
ghost annotation. The actual source's elided region is represented as a
compiler-generated name such as `'__74`, not as a declared `'_'` generic.

Therefore parser acceptance alone is insufficient, and the current annotation
has no static path to resolve its lifetime placeholder against that region.
The open/match/drop ownership argument remains sound in shape, but the candidate
must use a verifier-supported inferred type route before it is eligible for a
Cloud attempt. I did not run a compiler or verifier. This supersedes the
preceding P0c **GO as the next bounded Cloud hypothesis** assessment; the
synthetic generation test remains 2/2 and does not test type resolution.

### Final S2 P1-only release decision

The invalid P0c lifetime-placeholder experiment has been reverted: both
`a1-fixtures.py` and `test_a1_observer_checked_cleanup.py` are byte-identical
to S1 commit `5fc6f44b`. Thus the S2 candidate scope is P1 only, consisting of
the reviewed outer `ConstTypeExpr` normalization. **GO for that P1-only S2
target**, with the earlier P0c `Option_own` leak still a known failing/open
obligation and no new P0c repair claimed. The P1 review and its 35 passing
synthetic gate tests remain applicable; I did not repeat them. Refresh the
profile's numerical helper pins after integration, then verify closure before
any Build. No Build has been submitted as part of this review.
