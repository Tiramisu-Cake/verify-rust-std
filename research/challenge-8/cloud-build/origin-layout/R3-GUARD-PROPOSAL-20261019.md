# R3 guard — source-linked addressability diagnosis and proposals

Frozen tool08d6a578/profile82973e1e/translator2ff7b16f. No implementation,
proof edit or new Build. The v0.11 observations below supersede the earlier
message-only/conditional diagnosis; historical JSON responses are unchanged.

## Actual Build and AST

Buildc78529d0-f18b-4d13-9060-6517cde03cd5, executed source014c3238, fullbody
source_exact=True, exporter/decode/refinement0, verifier1. Observed error
verified/lib.rs207:49–52: Taking the address of this expression is not supported.
Original runtime guard is `CopyOnDrop { src: &*tmp, dst: tail, len: 1 }`, after
read206; R2 CURRENT array split/open is retained. This file is **R2 fullbody**,
not the old prefix AST:
file7d457f18b4648275ca0a94b68859d4f392f468bfe2b5d791e28d96b664fe6209,
SHA2757ca2a479947a06f44a78647545d78a8f37739c146bdf227819287f709748a,
archive5d058992…/index68182b14… .

| Exact archived AST | Observation |
| --- | --- |
| [424–425](R3-V011-GUARD-TMP-TYPE.json) | DeclStmt tmp:ConstTypeExpr(u64), initializer None, initial address_taken ref(false); function range117–227 |
| [710](R3-V011-GUARD-MERGE.json) | PureStmt(MergeFractionsStmt(lifetime_token(cmp_k))), source180, before guard |
| [985–987](R3-V011-GUARD-ADDRESS.json) | source207:49–52, create_ref(AddressOf(Var tmp)) inside actual fn_outcome_result assignment |
| [Complete tmp locator](R3-V011-GUARD-TMP-LOCATE.json) | Quoted tmp occurs only at424/973/979/987/1058/1167; no earlier reference before merge710 except its declaration |
| [Complete merge locator](R3-V011-GUARD-MERGE-LOCATE.json) | Merges710/800/816; fixing only the first visible caller merge would not remove all subsequent truncations |

## Frozen pass route and causal explanation

verify_expr.ml1510–1523 registers the declaration's address_taken ref by name.
mark_if_local1388–1391 is its writer; the AddressOf branch1398–1404 invokes it.
PureStmt1526 forwards the same continuation. MergeFractionsStmt1557 scans the
assertion and **omits cont locals**. The CPS sequence1566–1569 therefore stops
there. The actual merge assertion is about cmp_k, not tmp; the complete tmp
locator shows no earlier tmp address reference. Subsequent AddressOf(tmp)
987 cannot update the flag, and it stays false by this source trace.

This ref(false) in the archived AST is initial serialized state; final false
is **derived from the pinned pass and complete relevant occurrences**, not
captured runtime state. The prepass is called once (verifast.ml3538). The
separate stmt_address_taken walk only informs parameter heapy_vars and does
not repair local declaration flags. verify_block1195–1206 leaves a non-address-
taken scalar as a value type; StorageLive's scalar branch1057 does not allocate
or change the flag. Checker verifast1.ml4982–4988 then rejects AddressOf(Var tmp)
for scalar u64 with the exact observed diagnostic/location. The error's actual
operand, declared type, prior merge and missed classification route are now
source-linked, rather than inferred just from the Rust line/message.

Generic parser_input_binding=NOT_ESTABLISHED and causal_status=UNKNOWN remain;
this is a static causal explanation, not independent parser/verifier replay or
proof acceptance. No whole read/guard/fullbody theorem or B2 credit follows.

## Minimal tool proposal — NOT IMPLEMENTED

Existing project artifact verifast-address-taken.patch gives the exact fix:

```diff
-| MergeFractionsStmt(_, a) -> ass_mark_addr_taken a locals;
+| MergeFractionsStmt(_, a) -> ass_mark_addr_taken a locals; cont locals
```

This preserves assertion scanning and resumes the tail. It changes the frozen
addressability classifier and requires an explicit tool/profile decision before
implementation, new reviewed pins and independent GO; no automatic application
of this existing historical patch. Kernel allocation rules/runtime need not be
changed, but calling the patch frontend-only does not waive the trust boundary.

Controls: AddressOf after/before merge, inside its assertion, across multiple
merges, unrelated local stays unmarked; exactly one continuation/one physical
allocation; missing ownership/beforeStorageLive/afterStorageDead negatives;
unsupported operand shapes still reject. Retain full mandatory firstcallback/
CURRENT18/HRTB/unwind/late-Cleanup/default-off/B1/helper/receiver/end/retirement
matrix with full source/runtime/posts and strict closure. No local proof run.

## Possible checked proof-only alternative, not yet a candidate

A checked ghost helper could contain merge while the caller uses a normal
lemma call, allowing its own prepass to continue. No existing token-merge lemma
was found in frozen lifetime_logic.rsspec. A generic contract taking just one
fraction does **not** collect all caller chunks: normal lemma-call consumption
passes only contract resources, while MergeFractionsStmt sums all matching
chunks. Such a shortcut would not preserve the original operation.

A valid narrow helper would explicitly receive the actual finite fragments,
return their exact sum, and prove all coefficient conditions. For two actual
fragments q1/q2, consume both and return q1+q2; a full token requires a proved
q1+q2=1. Never assume this decomposition or sum from the current evidence. Each
caller merge710/800/816 must be accounted for at its real resource point; helper
must have no later address-taken locals affected by its own merge. First inspect
the caller decomposition, then verify this helper body and calls in a newly
authorized proof session. No resource removal, invented equality/owner bridge,
future-local reference or runtime rewrite. This could avoid a tool change if
checked; here it is only an alternative proposal, not a verified correction.

## v0.11 reporting result

Earlier request347e136b… returned LOCATE_WITHHELD under v0.10 and remains saved
in R3-GUARD-LOCATE-20261019.json. Under v0.11 the same source literal succeeds,
request3d175c69…; bounded nodes above are exact, content_filtered=false. The
prior administrative AST projection request is resolved for these node/type/
order fields. No quota/cache/backend/IAM change or raw fallback was made.
[Provenance](R3-V011-PROVENANCE.json); R3 remains CLOSED and Cloud0.
