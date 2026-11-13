# E2 coordinator CI request

No dispatch or push authorized for worker14. No local compiler/verifier execution.

First run the six immutable static/subrange/relocation singleton fixtures. Bind exact commit/tree, actual MIR, retained raw_eq versus scalar transmute, allocation identity/offset/extent/mask, check operand identities and all failures. Static legal must SUCCESS; static hole must fail only at the None byte. Subrange/relocation must no longer fail at incompatible-layout transmute. Their legal SUCCESS remains required; a conservative legal falseFAIL is an open release limitation, not a qualified negative.

Then use the existing unchanged legal PFC/ordinary controls, immutable masks/promoted/copy/reset controls, eight strong JSON oracles, X1 and Quick matrix at C0 profile settings. Keep existing object-bits 12 for heavy cases. Any regression, ICE or lost check requires stopping qualification. No final export/M3 or proof credit is established by READY.
