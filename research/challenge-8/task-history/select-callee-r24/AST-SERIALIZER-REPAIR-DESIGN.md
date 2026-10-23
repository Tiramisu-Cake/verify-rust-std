# R24 AST serializer repair candidate

Defect: Build234e58e3's additive AST stage is RAN/exit2 with no AST artifact.
Bounded Brief lines60-65 report Failure("TODO") in the AST serializer's nested
statement traversal. The exact positive annotation includes merge_fractions;
upstream f76012fb's MergeFractionsStmt arm is an unconditional TODO. Static
site mapping of the original dead-code reports remains separate and causal
status remains UNKNOWN until emitted AST evidence is obtained.

Applicability: reuse the existing R15 merge-fractions-ast-dump-r15.patch and
its manifest, only when the exact R24 runner enables its positive AST option.
The existing O26 callee chain did not apply this utility overlay. Apply it
after the parser overlay and before console compilation. Base printer898203bf,
resultf32f1a9a, patchf08f1c39; translator103a34/parser6a866a remain unchanged.

Invariant: this is constructor/field-preserving serialization only:
MergeFractionsStmt(l,e) becomes C("MergeFractionsStmt",[of_loc l;of_expr e]).
No source, ghost, raw MIR, verifier/checker/model, ownership, normal/unwind
post, call edge, default route, certificate or fingerprint changes. Existing
TODO cases remain explicit failures. Do not omit the merge node, substitute
Noop, catch-and-hide it, or infer proof credit from dump success. Keep the
ordinary proof call and all seven controls unchanged. Old R15 proof/admission
credit does not transfer.

Controls: exact patch/manifest/base/result hashes and single-file change;
static source application against f76012fb reproduces the manifest result;
recipe closure includes patch and manifest; runner gates the overlay on the
exact R24 AST route before console-build; published overlay chain and actual
profile metadata identify the added printer source. Required AST/entry/pin
controls remain active. New semantic candidate receives independent review
before its full1200 hosted Build. No local actual tools or dependencies.
