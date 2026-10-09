# Internal maintainer review package — experimental

No upstream publication or consumer pin update. Developed in isolated
`/root/verifast-select-sort4-native-20261010`, detached from VeriFast
`f76012fb518703b1d98e243ac4f487f16877cfcb` plus the existing frozen O26 manifest,
refresh, strict/relocation, actual first-scope, Output-equality and debt overlays.

[Prefix patch](verifast-actual-c1-prefix-TEST.patch) applies only after assembled
translator SHA256 `4aa487b5a000aa4ee045836059bdf34793db9d752300b3d0b55299ca95bac8a1`.
Patch SHA256 `2e1621b735e9d8af1d7c73b29d09daf1cd576943307521f67096917d342130e0`;
result translator SHA256 `590483304f55d744389f294a1dcc09053ba484d682d45d81ee6520d92b06f854`.
[Profile](C1-PREFIX-PROFILE.json), [rationale](C1-PREFIX-SEMANTIC-CARD.md),
[independent review/fixes](C1-PREFIX-IMPLEMENTATION-REVIEW.md).
Static git-apply reverse/check verified exact base/result. No local tool execution.

Default-off full-target AST and contracts unchanged. Prefix-only admits exact
full source/pre-AST/MIR, one isolated runtime body, unwind/full checks enabled;
preserves all declarations and c1 normal/direct-unwind edges. Excludes normal
suffix after recovery/join before c2. Closed edge inventory rejects a goto into
removed code or unknown control container. Emits the unchanged projected AST
object separately for runtime inventory. Retains strict dead-code/refinement.

This is a bounded resource-conservation theorem, not a callable whole sort4
summary. Prefix mode may not be exported/imported as actual sort4 proof. Native
entry applicability, optional scratch/dst, runtime layout/ZST and trust/admissibility
of historical overlays remain separately stated. New profile is not accepted.
Cloud proof and causal controls, not static application, determine proof evidence.


[C2 diagnostic delta](verifast-actual-c2-discovery-TEST.patch),
[C2 profile](C2-DISCOVERY-PROFILE.json), [preimplementation rationale](C2-DISCOVERY-CARD.md)
and [independent review](C2-DISCOVERY-IMPLEMENTATION-REVIEW.md) extend only the own
translator, after the exact C1 profile. Full source ECD83, two cut bindings, original
complete AST capture and intentional refusal; never a C2 proof. This package is
internal and portable, pending Cloud compile/capture and later maintainer review.

Current C2 package supersedes the original-AST diagnostic with an explicitly
unbound declaration scaffold. See C2-UNBOUND-SCAFFOLD-CARD.md (independent design
and implementation review). Exact second source196 let_lft is parsed by the stock
declaration parser into a closed local declaration/placeholder block, and the
translator always refuses before proof/summary. No lifetime escapes into C2.
Patch2a1ffa0bb1b472869a7697eb93bc9c45d671870de930791b13e725baf67d9cc8
from590483 yields8e467ca535bfcead8555a717897ec0355261ee8ccb011f98441e2dba80b5984f.
Historical original diagnostic remains at dfe8a19/ff5d4b85; no proof upgraded.
