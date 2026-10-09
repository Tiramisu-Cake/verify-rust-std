# Saved AST review (no new proof)

Independent read-only explorer review of integrity-verified second archive:
source-frame-positive proof-ast.ml SHA256
31aa1f1b32ff97fd2b18ec21106c2646239c4a973d2ff62b8d7a1556bcd13304.
AST180–187 maps inserted scratch-success filter (source38); AST192–200
maps retained original check (source45), AST276–278 retains abort. Boundary
assertion source58 maps to AST231–233 and both MIR ghostStmts. Runtime trace
hits both checks/boundary but never abort. Actual sort4 call is linked to complete
saved caller byte8821, not present or executed in bounded proof fragment.
AST serialization precedes verification; diagnostic exit1 is not proof PASS.
Normal MIR31BB / readonly28BB. Source spans and exact hashes are audited;
control_flow_precedence_proved=false remains an explicit limitation. Const
AST147–150 is opaque unevaluated_constant<bool>, no size expression linkage.
Full native caller theorem and actual sort4 invocation are NOT_RUN here.

Manual full-MIR CFG review: normal filter BB9 false→BB11; len<2 false→BB13;
original guard BB14 false→BB16 (v pointer), true→abort BB15. v pointer→BB17
assert→BB18 scratch pointer→BB19 sort8 const; branch continuation→BB23
len>=8 true→BB24 boundary. Readonly corresponding filter BB8→BB10→BB12,
original guard BB13 false→BB15, true→abort BB14; pointer path→BB18→BB22
len>=8 true→BB23 boundary. Boolean switch value0 is false target. Original
and inserted scratch expressions match in AST180–200, with no writes between;
continuing past filter logically forces original guard false. This is checked
manual edge/unchanged-state reasoning, not the collector's automated precedence
proof or a taken-edge trace. Separate opaque constant#0/#1 are not linked to each
other or size_of by the translator; duplicate concrete filter repairs arithmetic
without claiming that missing constant linkage. No full caller AST theorem.
