# Actual DropGlue body-v3 — maintainer review K

Incoming `e267f9485bfe620f5570b66e63226f1d0ea6fb77`; candidate tool
`853fd1e2edb309101df83b93c65572a0d8d0d189`, profile
`experimental-merge-actual-glue-body-v3`, SHA256
`77852588b0f177eb4c7d4e4a65626f6a3648f78768da08b82458c3650e14a2a2`.
Portable `glue-body.patch` SHA256
`22619b8dbe10ab831efef57dad0302ec1a86e5f8813860e982c5509ef5727f15`.
[Exact inputs](INPUTS.json), [independent addressed review](INDEPENDENT-REVIEW.md).

**CHANGES_REQUIRED** for the package's next qualification campaign: a concrete
runner AST-admission defect is identified below. **GO for the bounded semantic
design**, subject to fresh build/extraction/refinement/proof gates; **BLOCKED for
integration**. No confirmed kernel/body-lowering unsoundness was established.
Body-v3 is STATIC_PREPARED, generated glue NOT_PROVED, new end/retirement controls
NOT_RUN. Merge retains implementation/proof ownership. This is read-only review,
not an integrated tool or accepted profile. Ready I and its historical PASS/
FAILURE/UNRUN pins remain unchanged.

## Concrete defect: valid false unwind AST cannot pass auditor

At the incoming commit, `origin-layout/onecell-selected-drop.py:485–489`,
`_body_glue_ast_evidence` compares the unwind post to `ast.Sym("False")`.
Tool853's `src/frontend/ocaml_expr_of_ast.ml:259` emits
`False l -> C("False", [of_loc l])`. The pinned parser
`merge/overnight/stack-proof-ast-admission.py:114–125` produces a `Node` for a
constructor with arguments, distinct from `Sym`. Hence proper `False(location)`
cannot satisfy that conjunct; the aggregate AST admission at lines510–514 fails.
This is a static runner defect, not a proof/refinement negative. Closure requires
structural recognition of the False node with its location, an exact revised
runner pin, isolated valid/malformed/missing-post parser controls and then fresh
same-profile generated-glue positive evidence. No code was repaired here.

## Instance → compiler body → checked method

`glue-body.patch`, exporter `collect_generated_glue` hunk (+923), collects from
exporter-owned source bodies before encoding, admits only local nongeneric
CopyOnDrop with three concrete src:*const u64/dst:*mut u64/len:usize fields, and
rejects projection/replacement. Repeated Drops of that same guard reuse one
body; another concrete instance refuses. It obtains `resolve_drop_glue`, requires
the sole type arg to be that guard, calls actual `instance_mir(instance.def)`,
checks its source instance/Runtime(Optimized) phase and exact copy/call/return
shape. It resolves the raw trait FnDef after bound-region erasure and asserts
**whole Instance equality** to Item(adt.destructor.did), args[]. The selected
source body is uniquely captured by DefId from the same owned body inventory,
with separate hash/Runtime(PostCleanup) phase; it is not claimed instantiated.
Fully-monomorphized TypingEnv is appropriate only for this admitted nongeneric
concrete generated instance; it supplies no generic dispatch theorem.

Observation-v5 Build `12a54039-11a4-4275-bfa1-0a23f80263b4`, proof/infra
`d74a50c886a8e5a19289c577a9b41fadca760630`, observer tool
`3c9d56980accd335586ca23ba6c1378a29c1819a`, establishes this binding on its own
profile. I checked all42 saved observation hashes against the archived audit
and the full archive SHA against the checkpoint receipt; no replay/compiler was
run. Raw observations retain whole glue Instance/args, raw binder, selected
Item/args[], captured source identity/phase, and no Ref/StorageDead. This is
binding evidence, not body-v3 export or generated-glue proof. The captured MIR's
64-bit DefaultHasher-of-Debug is a within-extraction identity aid, not a portable
cryptographic source certificate; archive/source/manifest SHA receipts remain
necessary. No stale/foreign capture or DefPath-only substitution qualifies.

## Export/schema/refiner: reasonable design, fresh checks outstanding

`encode_generated_body` reuses actual MIR local/block encoders instead of HIR
`encode_body`, emits a private unique key, compiler-derived input/output, no
invented Ref/StorageDead or source helper, and Body27/28/29/DropData8 tags without
renumbering older fields. `generated_raw_callee` scopes bound-region erasure to
the exact FnDef in that generated encoding context; ordinary FnDef retains
`no_bound_vars()`. Raw args remain in the descriptor and observation. Fresh
artifacts must establish that only the observed receiver binder was erased and
that original/verified typed substitutions correspond to that same raw call.

Refiner `main.ml`, `one_generated_body` / `check_generated_unit` /
`check_generated_layout` / `check_generated_shape` / `check_generated_pair`,
requires a unique tagged pair, matching same-unit checked selected method and
caller Drops, local 24-byte/alignment8 u64 guard on x86_64, four locals and exact
two blocks (_2=copy _1; Drop::drop(move _2); bb1 Return), normal bb1 and Continue
unwind. It compares span-normalized full local/CFG records and descriptors.
Hashes bind within each extraction; paths/typed structure pair corresponding
original/verified definitions across crates. Raw trait hash is retained but the
FnDef schema has no independent hash field; binding here relies on trusted
exporter whole-Instance resolution, not a standalone descriptor theorem.

Tagged bodies always take `check_body_refines_body` after that structural gate,
bypassing source-snippet equality; a missing private verified body refuses.
Generated spans are not added as checked source ranges. V3's two old synthetic
Drop literals receive empty qualification strings/key and false flags; synthetic
body descriptors are disabled/empty. They grant no selection/generated credit
and leave original place/target/unwind operations intact. These defaults address
the V2 refiner compile failure, but ordinary synthetic Drop behavior still needs
fresh regression evidence. Old refiner binary `b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28`
is a baseline pin. New refiner sources0775c7cc/b6bb66ea require their own Cloud
build receipt and binary hash; V2's four successful build stages do not supply it.

## Contract, linear receiver, normal versus panic cleanup

Translator generated-Fn branch (+5709) constructs a function **with a body**,
reusing the selected strong req and complete normal/unwind post AST. It requires
the selected safety-proof clause and literal false unwind, omits only that clause
on private glue, and leaves the actual method on the ordinary safety-compatibility path.
The pattern checks clause presence, not its canonical content; fresh same-unit
verification must establish the actual canonical safety proof.
It checks the method's one receiver lifetime binder and transfers it to the
private signature; final typed AST must confirm this is erased-region naming,
not extra lifetime/alias authority. Generated raw-call lowering bypasses the
clause-ignoring generic matcher only after exact guard/trait/arity admission.
Every actual method and private body must be verified in the unit; declaration
presence alone is not summary proof.

Caller Drop still packs physical g, creates mutable receiver r plus exact
ref_mut_end_token(r,g), opens r, calls private glue, closes r, consumes end token,
and reopens g before StorageDead/free. Existing aliasing.rsspec:55–69 gives this
linear storage transfer; it provides no authority from address equality or origin
fixedpoint. The generated MIR creates neither receiver nor end token. Required
future omitted-end control must retain the token and fail physical recovery;
wrong-end must fail the exact token at end_ref_mut; post-retirement replay must
use stale retired state with no recreated resources. Simultaneous second full
effect, missing receiver/source permissions and before/after false controls must
reach their intended resource/VC, not setup or unrelated dead code. None of the
new end/retirement controls was executed at this checkpoint.

Continue/DummyLoc handling is restricted to generated continuation or the
predecessor's qualified statement-free Resume cleanup. Outcome expressions and
MIR successors remain. Require real source dead-code rejection and AST/CFG
provenance checks; synthetic locations cannot justify deleting source statements.
The glue's false unwind makes its own unwinding result unreachable if proved.
Syntactically retaining caller outcome arms and ordinary unwind smokes does not
establish reachable late comparator-panic cleanup. Refiner core still has general
Call/Drop unwind TODOs (around2586/2599); the new exact generated CFG gate covers
this glue only, not general caller cleanup refinement. Actual callback cleanup
needs separate exact edge/resource/refinement evidence before that claim.

## Minimum gates and future I compatibility

| Gate before integration | Current status / closure |
| --- | --- |
| Build/source identity | V3 NOT_CLOUD_BUILT; fresh exporter/schema/decoder/translator/console/refiner receipts with exact source/binary/compiler/target/profile identities |
| Generated binding/refinement | Fresh original+verified tagged bodies, selected capture/Instance/args, strict CFG/unwind; negatives for absent/duplicate/foreign body, wrong instance/method/substitutions/edge, no snippet shortcut |
| Checked bodies/resources | Private glue and actual dynamic self.len method, canonical safety proof, unchanged req/CURRENT/full posts; caller return/free/leak and nonvacuity |
| Receiver protocol | One caller creation and one exact end per permitted outcome; missing permissions, omitted/wrong end, duplication and retired replay at intended predicates |
| Ordinary behavior | Default-off/unqualified/foreign/generic/projected/replacement Drop, old synthetic Drop records, normal/unwind smokes and real source dead code |
| Caller cleanup/applicability | OPEN/NOT_RUN; late-panic CURRENT recovery, actual entry-premise provenance and multi-cell witness before insert_tail claims |

Body mode checks environment-variable **presence**, so value0 also enables it;
pinned runner sets1. Future profile admission must bind exact settings/inputs
and prove default-off/isolation behavior, rather than treating a boolean as
compiler evidence. This is a documented configuration boundary, not a proven
V3 semantic defect for the pinned settings.

The body delta affects exporter/schema/derived decoder, translator and official
refiner. Its thirteen-patch dependency profile also differs from I in kernel/
model/frontend/contract-support components; body-v3 itself does not change that
frozen merge kernel. I lacks the predecessor selected-Drop metadata/interface.
Any future minimal port needs explicit dependency/diff review, preserving I's
kernel/posts/CURRENT, strict lifetime/FRAME/cleanup/ZST/native/Bool semantics,
and affected fresh compatibility/regression checks on one new effective tool.
Neither the merge chain nor PASS from different tools is imported wholesale.
No integration, code edits or acceptance occurred here.

Domain remains **concrete-u64/x86_64, guard len1, explicit bounded entry premises**.
Guard length is not backing-array length. Bounded selected-method PASS proves
neither panic cleanup nor actual insert_tail. Generic T/ZST, general O23 and
inherited assumptions remain open. Next useful action is merge-owned
runner admission repair, then merge-owned fresh V3 build/generated-body gates
under its separately authorized session; this review authorizes no Cloud run.
