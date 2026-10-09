# R3 actual nested Drop scheduling TEST

R3's lexical nine-body order checks the outer `select_unpredictable` before its
generic nested `DropOnPanic<T>::drop`. An outer failure can hide the nested
callee's same-version proof. This isolated TEST asks whether the exact nested
body verifies before the outer body, with both normal and unwind return/leak
paths visible in the full unfocused log. It does not repair the R3 outer proof.

Apply `verifast-r3-nested-before-outer-TEST.patch` only after the immutable R2
component-23 and R3 component-24 deltas in a disposable Cloud tool copy. The
base R3 translator is `34a03879…c15`, the TEST patch is `d7712df4…e26`, and
its statically applied translator is `85962191…6a6`; the manifest contains
full hashes. Require both R3 opt-in pairs and the additional exact-root
`SORT4_R3_NESTED_ORDER_TEST_REPO_ROOT` plus
`SORT4_R3_NESTED_ORDER_TEST=1`. A missing or partial TEST pair must not
schedule declarations. Any changed source, complete unit, nested body, nine
DefPaths, root, AST type/count/key/span, or duplicate/missing node refuses.

The only changed output is the order of top-level AST `Func` body declarations:
seven same-version prefix functions, then the nested Drop, then the outer
function. The TEST retains each full serialized AST function node, its
signature and contract, and all preceding ADT, trait, predicate and ghost
declarations. The patch prints qualified names, source locations, before/after
body-node hashes and the unchanged signature-list hash. The source is the
93da observed `a95aff14…8463` pair with complete unit `407acbae…0a92` and
body-8 `e0508d6c…eae9`; the runtime original remains
`466882d7…5a5`. Normal/readonly MIR and refinement must be the already
captured same-source R3 artifacts. The kernel, parser, memory model, specs,
exporter and refiner remain identical; only the translator and rebuilt console
may differ.

The Cloud helper copies the completed R3 tool and source into independent TEST
paths, applies the one-file delta, builds one TEST console, and runs the full
unfocused nine-body proof. A diagnostic requires seven proof headers in order,
the nested header, two nested return and leak checks from its normal/unwind
paths without any earlier source error, then the outer header. A nested header
alone earns no proof credit. Source-located, `Error:` or `Fatal error:` output
before the outer header makes the result inconclusive. A later outer failure is
recorded without weakening its normal, unwind, leak, dead-code or validity
obligation.

Default-off, partial-opt-in, source/unit/body, duplicate/missing declaration,
and wrong-order adversarial controls need independent Cloud evidence at their
intended certificate gates before any nested theorem or production profile can
be accepted. This initial scheduling TEST does not implement that full matrix;
`mutation_controls_complete=false`, `actual_nested_drop_credit=false`, and
`verification_accepted=false` even if the log shows both nested paths and the
TEST console exits zero. The unchanged R3 lexical candidate remains separate.
