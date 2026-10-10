# Target helper AST capture, instrumentation only

Status: independently reviewed GO for instrumentation only, to be used if the unchanged-tool
`-dump_ast_with_locs` fails to serialize the proof-only
`recover_pair` lemma's `MergeFractionsStmt`. This file is not a semantic
overlay and does not authorize one.

The exact proof source contains `c1_source_prefix` plus checked helper lemmas
in one Rust unit. Whole-module AST dumping has historically stopped at
`MergeFractionsStmt` in the lemma even when verification without AST dumping
can proceed. The exact pre-rewrite helper `Func` AST is needed to pin a
subsequent one-call unwind overlay. Capture it at the translator's local
`original_decl` construction, before any compose transformation, when the
explicit capture opt-in is set and the function name and full verified source
SHA match the freshly saved Cloud source. Serialize that **same immutable
object** to a fixed fixture-relative file using the existing
`Ocaml_expr_of_ast.of_decl`/formatter. Compute its source and serialized
hashes, print one marker and return `original_decl` unchanged.

Admission: default off must produce byte-identical old behavior. A malformed
opt-in, wrong body, changed source, more than one target body or ambiguous
output path must refuse. The capture route keeps the complete original
normal/readonly MIR, original comparator call/Continue action and every
normal/unwind post. It cannot change parser/kernel/memory/spec/refiner,
skip verification, mask a verifier error or claim proof from AST emission.
The normal full verifier invocation remains mandatory in the same fresh
Cloud run. Archive both source/MIR/function AST/tool snapshot and any
diagnostic serializer failure. Only after the captured AST is independently
reviewed may a separately reviewed semantic overlay pin and transform it.

The independent review additionally requires the local target hook to pass
all non-target bodies, including the native function, unchanged. The global
admission must count exactly one target helper body. It must reject an
existing output path as ambiguous and leave `original_decl` unchanged; if
serializer mutation is uncertain, compare fingerprints before and after.
