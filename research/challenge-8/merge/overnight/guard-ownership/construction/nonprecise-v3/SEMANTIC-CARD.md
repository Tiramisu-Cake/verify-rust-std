# Full-source nonprecise owner / exact construction — V3

Prepared before implementation in AFTERNOON-MERGE-GUARD-CLOUD-2026-10-09.
This replaces neither rejected V1/V2 nor their evidence. Named profile:
`copy-on-drop-source-construction-full-source-nonprecise-fragment-v3`.
No frontend/kernel/prelude/model/refinement patch is proposed; stock and the
existing six-component tool profiles remain distinct and unaccepted as a whole.

## Observed blocker and obligation

V1 precise own rejects variable source fraction; V2 supplies full source but
precise own rejects `foreach(src_values, own::<T>(t))` before any constructor
body. The immediate callee foreach is nonprecise. Independently, pinned generic
`<Self>.own : pred(thread_id_t, Self)` is nonprecise, so merely replacing foreach
with a precise recursive list wrapper would fail at generic T.own. No precision
bound on generic T is inferred or added. Current owners are still available as
linear resources in the ordinary slice FBC; precision failure is not absence
of ownership.

The source-linked obligation is the unchanged private CopyOnDrop<T> declaration
and exact physical statement279 in small_sort_general_with_scratch. Supply the
current initialized source array, writable destination and existing current
owner pool once, construct the three-field guard, and establish its complete
owner-bearing post. A matched false after construction must fail at that runtime
body location, not at precision/header. This first experiment has no Drop impl:
only a conditional source-fragment theorem can result.

## Interface and distinction from V2

Define **nonprecise** `<CopyOnDrop<T>>.own(t,v)` (no semicolon), retaining the
exact full-source V2 body: type_interp<T>, positive stride, all source/destination
pointer bounds/alignment/nonoverlap/pure facts, full initialized source array,
full writable destination array and `foreach(current_source_values, own<T>(t))`.
Keep the constructor entry resources and normal/unwind posts byte-for-byte V2;
only the precision metadata of own/FBC is different. Do not omit foreach, move
it to an unaccounted external frame, introduce opaque tokens, assume conversion,
or weaken the normal result. No generic T.own uniqueness theorem is claimed.

Pinned parser maps own without semicolon to `Right([t,v], None, body)`.
Pinned translator :6636–37 deliberately emits **nonprecise** generated FBC
when own has None; slice FBC :449–51 already carries a generic foreach this way.
Precision metadata governs usable precision inference/automatic fraction
reasoning. V3 claims no precise predicate property and must not use any rule
requiring it. A precise opaque wrapper would change the trust problem and is
excluded. Ordinary full-chunk opening/closing still consumes/produces the
complete predicate body; precision checks, separation permissions and all other
verifier checks remain enabled. No trusted semantics are changed by this syntax
choice; the new resource interpretation and its applicability are experimental.

## Conservation and caller premises

There is one existing foreach pool associated with the actual current values
of the initialized source array. Closing own consumes that pool and both arrays
exactly once. The target's proof opens the newly formed own, asserts the same
current source array and foreach plus destination permission, then recloses the
complete own before returning. This checked roundtrip exposes resource recovery;
no bytes/address/share/Freeze operation introduces a T owner. Full nonempty
positive-stride source and destination permissions remain separated. Splitting
an ordinary predicate's fraction does not grant two full points-to permissions;
V3 invokes no precision/fraction-merging lemma. It promises full resources only.

Domain remains V2: generic positive-size T, native-usize len>=2, initialized
current source, writable destination, full source permission, exact geometry,
thread token and pre-existing owner list; normal returns owner-bearing guard
and exact src/dst/len equality, unwind false. No bounds on comparator added;
this fragment has no callback. Its supplied entry state is NOT derived from
actual seed copy/sort4/sort8/insert_tail. Full-source caller applicability and
CURRENT scratch/owner handoff are separate W6 obligations; generic/ZST coverage
of whole Challenge remains open.

## Gates and refusal criteria

Separate V3 stock/six groups must be isolated from V1/V2 and unrelated helpers.
Pin full std source/blob/block, exact constructor bytes, all annotation hashes,
new profile, tool/compiler/schema/patch identities. Ghost stripping preserves
runtime bytes. MIR gate retains exact private three-field ADT, parameter-origin
aggregate at source279, one return, no Drop/call/cleanup/unwind. AST gate requires
exactly one own with **None precision**, the full two-array+foreach payload,
complete supplied pre/post, exact initializer and literal false unwind. New
roundtrip must open/close that same guard, assert source/current-pool/destination,
with no assume, axioms or alternate resource creation.

Positive must reach actual constructor statement and roundtrip, return and leak
check with full source/refinement/no-dead gates. Negative supplies the identical
pre/post and runs the same construction/roundtrip before one `assert false` at
its recorded dynamic line/columns; only that assertion counts. Any precision,
header, setup/helper, admission, unrelated error or timeout remains INCONCLUSIVE.
Do not modify classifier/return/leak/dead/source gates to accept a failure.

Success -> inspect generated nonprecise FBC and next actual type/Drop bridge.
Failure -> record the first full-log cause and make only an addressed fix.
Fragment success cannot admit canonical Drop/glue: safe Drop pre must remain
canonical FBC, self geometry must be derived from real resources, actual callee
verified same source, and complete current arrays/owners must survive generated
normal post. Generic Drop post currently returns fields/padding only; no payload
post/glue/forget rule is authorized by this card itself. A follow-up rule needs
its own rationale/review/gates under this session authorization.

## Critical self-review before implementation

Read-only Luna exploration and independent Sol review checked the pinned
precision declarations and translator branch. They found no mandatory generic
precision bound for this nonprecise own/FBC form. They rejected a precise
recursive adapter/opaque token and highlighted the canonical Drop payload-post
and self-geometry gaps. V3 exercises the already supported nonprecise interface
without pretending to prove V2's precision property. It preserves every existing
owner and target post. This reasoning supports an isolated conditional diagnostic;
tests alone do not prove tool soundness or applicability to the actual Drop type.
