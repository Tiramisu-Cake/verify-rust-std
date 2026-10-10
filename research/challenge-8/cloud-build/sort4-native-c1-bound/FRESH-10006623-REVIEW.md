# Fresh bound C1 review — 10006623

Build10006623-3880-4a5a-b3d2-7d40274b7629, proof=infra8ec0214fc8a1f3a36f63c6fdd8fca4e275020b24.
create2026-10-10T23:09:30.137885406Z → finish23:16:26.562682Z;
417 charged seconds (416 execution). Cumulative1166/3600; no carry.
Token dispatch-d3739a9d20694266840299561dbe194c; config
ba594f37354aff00c0609814c74367f346cbc927dc834aaed38afa2c07b53b9f;
input9b6e806492f6e39240194995cb3e30749f9dceb8b26a125248c12a5a99eaa6f6.
Canonical archive5b0b69c1f543069fae1d8c5a4c33bf0d727afd99c083cad32245e25bb794cb82,
/tmp/native-c1-bound-10006623-read; download integrity and text-log index verified.

Translator dccb86574c32d88f9bfb41660393ea9334238a392e71b4dbe6c96bf0f4083918;
console fea430af4f23b5270f5fb880557074a43c09300fee7899e2a34b54d72d3ce547;
kernel37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c;
effective-profile4703b41f6d87fce578cfe388b56bec168a93fd15dbe5ec55dc45901f67fd1c58.

All8 paired source/export/decode/refinement gates PASS. Six exact-source MIR
fingerprints match8e9adccc/bde6d797 and source7ebcf7cd/original7c35a7e0;
all source pairs immutable. Bound admission now retains original preAST
18973de5dd5ff1a9c94652fd808d42ffe2297096adb8a3cc1980f74a554ccea5.
Positive postASTfdd11c3f7933d36e2487c30ed08ec31977c3b19b70e946654376b11ef59fb34e.
Source, extra body, malformed and mixed controls refuse exactly before target;
default-off retains strict-entry outer-type refusal172.

Actual comparator and CURRENT recovery, normal full-native cleanup and direct
comparator-unwind four cleanup blocks are reached. False normal226 and false
unwind210 both refuse intended assertion after respective cleanup, rather than
setup. Positive nonetheless exits1 on `verified/lib.rs(228,2): dead code`.
No fresh complete VF0/native→C1 theorem claimed; native→C4 NOT_RUN.
Fresh normal/unwind resource-path evidence is partial until dead-code obligation
and independent final AST/control-flow review close. Dead-code check stays on.
Narrow source-specific translated-CFG diagnosis underway; no general rule,
MU inverse, optional destination or new raw C1 premise introduced.

Independent fresh postAST/raw-path review: normal source214–226 restores
CURRENT source cells plus untouched tail, opaque MU owners/storage, F/thread,
then original normal return228 and full automatic post/free/leak; direct
unwind source196–208 performs four cleanup blocks then original unwinding()
return210 and full automatic post/free/leak. No resource-path refusal seen.
Exact first refusal is closing-brace dead code228,2: synthetic unwind epilogue
appended after original Label63/normal-return chain. Proposed source-specific
CFG correction places unwind epilogue before the original final normal label/
return, guarded so normal Goto skips it. Keep both returns/all original posts,
dead-code enabled and fresh proof mandatory. Shared classifier-only dead-code
recognition replayed on all8 saved logs; previous seven outcomes unchanged.

False controls are after explicit source CURRENT/MU/F assertions and type_interp
leaks, BEFORE automatic return/post/final leak check. They establish reachability
of explicit cleanup boundary; positive trace independently reaches automatic
post/free/final leak on direct unwind and normal terminal paths. Neither gives
VF0 credit until the remaining dead-code refusal closes on fresh corrected run.
