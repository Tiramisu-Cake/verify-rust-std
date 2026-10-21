# R11 Build4 abstract AST comparison repair

Build4 compiles all seven observed milestones. Actual fullbody translator raises Invalid_argument(compare: abstract value) at line7614, where a structural list/AST comparison tests that the translated terminator is the original invariant. AST expressions contain abstract/lazy values; generic structural equality is not a safe AST identity test.

Match exactly one terminator statement and require physical identity (==) with the source-selected invariant node. The existing ghost intrinsic lowering returns the same parsed statement object from State.ghost_stmts, so this strictly binds the selected object without traversing abstract data. Keep normal edge, markers, all source/body/admission guards and logical checks unchanged. Audit remaining comparisons in the new class: string/location/empty-list/type constructors only; do not compare AST values structurally. Independent LunaHIGH review before exact new tool/patch/profile and next Cloud run. No local compile/proof; no target proof credit.

Independent GPT-6 Luna HIGH reviewer r10_review GO: plan and translated ghost terminator select the same parsed node from the same rewritten State.ghost_stmts; physical equality is exact and safe. Remaining new-class comparisons contain no AST structural equality.
