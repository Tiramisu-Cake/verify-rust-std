# R11 Build3 translator type repair

Build3 reaches the translator compile gate and reports line7610 unit where Mir.basic_block expected. The placement plan exported its locally polymorphic static-error function as an ordinary tuple member. Matching that tuple monomorphizes the function; first use in require fixes result to unit, while unique-block selection needs a nonreturning branch of Mir.basic_block type.

Return only source data in the placement plan. Recreate the local nonreturning static_error helper at the translated-plan consumer, which permits local let-polymorphism at each call. No guard, diagnostic, accepted input, statement/edge placement, storage or logical state changes. Inspect all exported helpers and pattern branches in the new placement class for the same type restriction. Independent LunaHIGH review before a new exact tool/patch/profile closure and Cloud compile gate. No local compiler/proof execution and no proof credit.

Independent GPT-6 Luna HIGH r10_review GO: consumer-local fail remains polymorphic at unit/basic_block uses; no other obvious APIs/type-inference issues in placement class, no guard/placement semantics changed. Static only, compiler not run. Exact tool 5c80671711da1b43a7390f13431b7c51986b210d.
