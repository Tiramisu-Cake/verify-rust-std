# C2 exact unbound declaration scaffold — semantic rationale, NOT_RUN

C974 full normal/read-only source/MIR/refinement passes; parsing stops before AST
at source196 second let_lft, exported as ordinary ghostStmts. Do not fabricate a
second ghostDeclBlock with the same closeBraceLoc255, which keys frontend CFG heads.

Exact source ECD83 and original runtime3602050 remain unchanged; isolated one actual
sort4 Rust body, full unwind/strict checks, actualscope1/prefix0/Outputeq0, explicit
C2 discovery1 only. Default-off must preserve C1 complete gates and fresh prefixVF0.
Before any generic ghost_stmt parse, recognize EXACT one raw annotation
/*@ let_lft 'cmp2 = cmp2_k; @*/ at verified/lib.rs196. Invoke the EXISTING ghost
declaration parser (no parser semantics change), require exactly TypeWithTypeidDecl
'cmp2 with typeid_of_lft(cmp2_k). Represent its AST information in a marked closed
local block containing the explicit unresolved placeholder command
__vf_sort4_C2_UNBOUND_LIFETIME_DECL_PLACEHOLDER, preserving the annotation span.
All other ghost statements/declarations/runtime AST translation is unchanged.

The placeholder block gives no later C2 lexical binding. This is explicitly an
UNBOUND_C2_LIFETIME_NOT_PROOF scaffold, NOT original/source-correct bound AST or a
verified theorem. No AST runtime path is removed. Emit/hash only this full scaffold
then ALWAYS refuse before kernel checking, helpers/target proof or summary export.
No proof mode accepts the unresolved placeholder. Preserve all 5 FnMut/8select/4copy
calls; exact source196 placeholder and 'cmp2 declaration must appear exactly once.
The scaffold only exposes the structure needed for a subsequent independently
reviewed two-sibling projection consuming marker/declaration into proper scopes.

Changed trust surface: exact opt-in translator binding classification/diagnostic
only; parser/kernel/prelude/memory/refiner frozen. Fresh compile plus default-off
C1 gates, both complete MIR/refinement, exact placeholder/scaffold runtime inventory,
intentional UNBOUND refusal and source mutation refusal before output required.
A failed parse/changed shape stays inconclusive; no deleting/faking a declaration,
no ghost lifetime proof, type equality, ownership bridge or disabled strict check.
Prior original-discovery profile/source artifacts remain historical at dfe8/ff5d
and exact C974 evidence. This new profile must name scaffold filename/classification
and never label it original/bound AST. No new Build after23:52:33 UTC.

Independent Sol design review approved diagnostic-only constraints. Implementation
review clarified that the placeholder is inside the closed local block; no later
annotation acquires its lifetime. Runner must count both original cmp and new cmp2
declarations by name, retaining one of each. No compiler/proof executed locally.
