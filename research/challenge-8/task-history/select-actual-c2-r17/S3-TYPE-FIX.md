# R17 S3: typed parameter exclusion

S2 Cloud compiler diagnostic at translator:9200 observes `param_decls` as `(Ast.loc * string * Mir.ty_info) list`, while the new local-group filter expected four-tuples. The compiler has already mapped parameter declarations to three-tuples at that point. Applicability: indexed c2 candidate's exclusion of input parameters from relocatable MIR temporary cells only.

Fix the tuple destructuring to the actual three-field representation; preserve the exact parameter-ID equality exclusion and all source-span/type/count/containment checks. No runtime/CFG/post/kernel/model change. Distinguishing control remains source-bound exact30 local partition with six cells per ordered callback; malformed inventory refuses. The changed OCaml candidate must be compiled and tested only in Cloud, following independent Luna HIGH delta review. No proof credit follows from compilation.
