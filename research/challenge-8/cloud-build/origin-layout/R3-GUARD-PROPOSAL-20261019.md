# R3: conditional guard address-taken proposal — NOT IMPLEMENTED

Owner merge; task merge-first-comparator-2026-10-19-r3. Frozen tool08d6a578,
profile82973e1e, translator2ff7b16f. This is a reviewable proposal, not an
established diagnosis of Build c78529d0 and not permission to change the tool.

## Observed target and source binding

Build c78529d0-f18b-4d13-9060-6517cde03cd5, source014c3238, fullbody
source_exact=True, exporter/decode/refinement0, verifier1. Error207:49–52:
`Taking the address of this expression is not supported.` Static pinned
preparation binds the adjacent original runtime statement after read206 to
`let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };`.
The exact failing AST operand/type and which checker branch emitted it remain
NOT_ESTABLISHED; the source message alone cannot identify the cause.
R2 CURRENT array split/open/read frontier is retained; no whole-body/read/guard
or first-panic theorem is credited. Main firstcallback prefix is separate.

## Verified frozen-source defect and conditional applicability

`src/verify_expr.ml:1557` has:

```ocaml
| MergeFractionsStmt(_, a) -> ass_mark_addr_taken a locals;
```

The surrounding CPS statement traversal uses `cont locals` to visit following
statements. This arm omits it. Existing project artifact
`research/challenge-8/verifast-address-taken.patch` gives the minimal diff:

```diff
-| MergeFractionsStmt(_, a) -> ass_mark_addr_taken a locals;
+| MergeFractionsStmt(_, a) -> ass_mark_addr_taken a locals; cont locals
```

The defect exists in the pinned source. The proof preparation and CURRENT18
marker include merge_fractions before later tmp-address use. To assign this
as the Build's cause still requires the actual AST order/storage classification:
preceding MergeFractionsStmt, later AddressOf(Var tmp), and tmp left as a value
local rather than RefType. No such trace is inferred from the error alone.

Frozen translator reference lowering at3666ff has an opt-in tracked shared
ManuallyDrop reference path; ManuallyDrop::deref is an identity translation.
The path can create `create_ref(&tmp)` and needs tmp to be addressable.
Checker verifast1.ml4982ff permits AddressOf(Var local) only for RefType or
StaticArrayType; it emits the reported error otherwise. AddressOf(Deref(...))
already has a special accepted path. A second evaluator catchall8885 can emit
the same message; it must be distinguished before claiming root cause.

## Trust scope and rejected shortcuts

Adding the continuation changes the frozen address-taken pass and therefore
which locals receive existing addressable-local storage. It is a trusted
checker/profile change even though runtime, MIR lowering, kernel ownership
rules and the physical allocation mechanism need not change. Do not apply
this existing patch to tool or source closure under R3's frozen profile.
A separate owner decision and exact new reviewed profile/patch identities
are required. Preserve the current14patch chain as historical baseline.

No ghost-resource tweak is proposed as a proven fix. An annotation placed after
an unvisited merge boundary would also be missed by this prepass. Referring to
future tmp before initialization/StorageLive, creating an ownership bridge,
assuming numeric-address equality, replacing runtime `&*tmp`, or removing any
merge/lifetime operation are not accepted workarounds.

## Required validation if separately authorized

1. Establish exact archived AST/node/type/storage order, or an expressly
   authorized minimal source-linked Cloud reproduction of that defect.
2. Positive controls: address before and after merge_fractions; physical local
   chunk and one allocation, normal/unwind lifetime/storage preserved.
3. Negative controls: unsupported AddressOf operand shapes still reject; use
   before StorageLive/after StorageDead and missing physical ownership reject
   at intended checks. No arbitrary extra addressability/admission fallback.
4. All current firstcallback/CURRENT18/HRTB/unwind/late-Cleanup/default-off/B1/
   helper/receiver/end/retirement gates; fullbody read/guard frontier under
   unchanged runtime and full normal/unwind posts. B2 remains separate.
5. Independent Luna High GO; strict source/profile/patch/18base closure, exact
   published source/config, existing coordinator, fresh authorized Cloud Build.

No local compiler/decoder/refiner/verifier or proof preparer was run. Tool
worktree remains unchanged. This proposal does not resolve the prefix214
InferredTypeExpr error in its separate wrapper function.


## v0.10 actual-AST request: retained limitation

Catalogue of **Buildc78529d0** identifies full_body/cases/
actual_three_current_full_posts/proof-ast.ml, file ID
7d457f18b4648275ca0a94b68859d4f392f468bfe2b5d791e28d96b664fe6209,
SHA2757ca2a479947a06f44a78647545d78a8f37739c146bdf227819287f709748a,
archive5d058992…/index68182b14… . It is not the old prefix AST identity.

[Exact-source-location locate request](R3-GUARD-LOCATE-20261019.json),
literal `verified/lib.rs(207,49-52)`, returned **LOCATE_WITHHELD**,
reason SENSITIVE_UNTRUSTED_OR_OVERSIZED_SOURCE_LINE, request
347e136b0db5bdebb0017dd13b228fcb2eee5addac6d631199c4ecb79e31504f.
No coordinates/text were returned; exactFalse. No alternate literal/near/window
was used to bypass withholding. This path is stopped pending administrative
safe projection of actual AddressOf operand/type, enclosing statement,
preceding MergeFractionsStmt order and tmp storage classification. Request
sent to owner. The confirmed pinned-source continuation defect remains a
**conditional proposal**, not an established cause of this Build's failure.
No tool/runtime/proof changes and no new formal credit.
