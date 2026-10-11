# Current localization — 2026-10-11 session

Fresh009ad1c2 /f8115f33 establishes exact physical203: postlist138/ordinal256
Goto63 afterLabel3, originalroot131, printed228,2; noEXEC203. Other equalprinted
locations202/204 execute. Source/MIR/pre/postAST all unchanged from3521.
Callback-free sameguard native&T[] VF0; addingunused nativeMU[] VF1/deadzero.
Current cause localized to frozen native MU layout/resource model, not dropped
CFG or unwind-epilogue placement. Entry array_inv introduces MU size before
body calls; exact positive-bound trigger follow-up pending. No admissible
source-specific repair yet. NativeC1 INCOMPLETE; connectedC4 NOT_RUN.
[Fresh review](FRESH-009AD1C2-REVIEW.md), [maintainer blocker](ZST-MODEL-BLOCKER.md).
The following prior-session account is preserved as historical evidence.

# Remaining precise obligations — native bound C1 session

Fresh10006623 native target reaches actual first FnMut operands1,0; CURRENT
normal and direct-unwind resource recovery and original automatic native
post/free/leak terminal traces pass, but verifierexit1 on `dead code228,2`.
No complete connected theorem. Exact runnable reproducer is native-c1-candidate.rs
(source7ebcf7cd/original7c35a7e0), full case/profile/recipe and commands in
REPRODUCTION.md; failing effective translator dccb8657, kernel37ed, proofinfra
8ec0214. Expected: one unit returning outcome and direct unwinding outcome,
complete CURRENT native storage/owners/F/thread/lifetimes, local free/leak,
all source branch/dead-code checks. Actual: resources reach terminal checks,
then dead-code refusal. Controls intendedfalse226normal/210unwind do reach
explicit full cleanup boundaries; setup/admission controls separate.

Same printed loc228,2 covers root129 Goto63 viaLabel62, root131 Goto63 viaLabel3,
root133 normalReturn, with distinct physically tracked locations. Positive
trace normal terminal paths C1/len<8 useGoto62; source145 sizezero true/Goto3
not visibly entered. Unwind epilogue placement may cause the diagnostic;
exact-node attribution remains unresolved. Final narrow CFG fix381e80eb/
eea19eda conserves allnodes/returns and moves epilogue ahead of originaltail,
with seven-statement CFG gate and independentstaticGO. Fresh result required;
it must not delete ZSTbranch or disabledeadcode/strictcut/unwind/resourcechecks.
If the same refusal remains, first next action is source-specific node/size_of
path diagnosis preserving prior refusal and all checks, not repeatedmatrix or
assumed general semantics extension. No inference/alias/MU/generalkernel rule
has been established as necessary for C1 by this session.

External boundaries unchanged: native safe refs/generic FnMut bound are entry
conditions; source4/tail/F/thread/types derive from their stock resources,
not fresh supplied raw C1. Scratch MU remains opaque; no optional-T destination,
MU inverse/new(inner(old)) identity, arbitrary ownership/separation/layout facts.
Comparison branch explicitly positive-size/nonZST and len>=8; selected actual
caller branch does not imply positive size (len8,size0). Actual external
as_mut_ptr method binding, scratch guards/inlineconst/abort/len+16 and caller
edge remain unproved. Prior checked-add reproducer identifies exporter forced
overflowoff/absence Assert-unwind, not runtimeunsafety. Generic layout/ZST peer-
owned. NativeC4 connected target NOT_RUN until fullC1PASS; oldC1→C4 priorPASS
remains separate. Strict draft/selector/C5/copy and peer unfinished patches unused.

Final fresh3521e3b3 /2e995605 repeats dead code228,2 with translator381e80eb;
CFG placement-only hypothesis is falsified. All three reached terminal paths
still check full native CURRENT posts/unit/free/leak. No complete nativeC1PASS;
C4 NOT_RUN. Originalroot131 remains a candidate, not an exact physical error
identity. Need location-disambiguating diagnostic and size_of-path analysis;
no general rule requirement established. Stock size_of has no nonzero premise,
FreezeMarker permits ZST. Session/account closed1556/3600; no further run here.
