# Fresh Rust ZST repair gates and full native C1 fragment PASS

Build ed016f05-c66b-4d9f-8be4-12b8c0271f8f, proof=infra
f1e139053eac06da27a4068b47b0d44cbca1cb73. Cloud SUCCESS is collector status;
actual native target verifier exit0, 0errors/196statements LP64. Create
08:57:35.353058523→finish09:04:12.456245 UTC; conservative398sec.
Archive46ceca287873c8cd44c9f9b2d7e165a19c59ee70cdaa77609825c5c845bc4abc.
Independent archive inventory and controller download config/input/receipt/text
index/chunks verified. Total737/3600sec,2863remaining; both builds terminal.

## Model repair gates

Both sameguard callback-free generic bodies with/without unused native MU scratch
VF0. Both false entry-positive-size obligations refuse exactly before guard:
noMU3,41–42 /MU4,41–42 Cannotprove0<sizeof(T). Both real nonzero-branch assertions
VF0. Concrete matrix: unit, MUunit, empty Rust, reprCempty, u8/MUu8, empty arrays,
ZSTarray3 size assertions plus existing valid-layout/size_align lemma-derived
positive align/divisibility assertions VF0. No unreachable runtime branches.
Reachable unit/MUunit native entry assertfalse fails4,16–21; arbitrary rawpointer
points_to fails4,19–22 No matching heap chunks. Cnonempty and C++empty VF0.
Every Rust case fresh pairednormal/readonly export/decode/fulltargetMIR and
refinement0; synthetic MIR recorded fresh, not claimed identical to old source.
Normal posts/fullnative resources retained by automatic safe entry.

Patch unchanged19ee0d684e972f164f16f21926bde7d5d1edc1f9224a880c20120f9cb62f1074;
verifast1 resultbfbfb518fb9783afeeba9384e1431b6cd280c7da7713b9fdbfd15a8395b00207.
Frozen C4 snapshot unchanged. Effective isolated profile/source/binary/spec/std
hashes in ZST-REPAIR-BASE-RESULT-MANIFEST.json and raw effective-profile.json.
No alignment/array/provenance/permission/ownership/solver change. Profile remains
experimental/unaccepted; matrix success is not general verifier qualification.

## Native C1 target, nonvacuity and controls

Target source/original/MIR/preAST/postAST all identical3521/009/9ae:
source7ebcf7cd435c31b3f4669ac6f31a62fd45fcb2c7fa03500bdfbc44ccaca01742;
original7c35a7e01915233308d113b081f26784c4ad5aaf6f7049dc209d126e3eb326a1;
normal8e9adcccd136d3c1ee4dc1e7bd929c3cd60883f497178eab24da40f60754dee4;
readonlybde6d797d56e0e11e9837fc922f6def819c6931d1349f42c5b36d4570e2001aa;
pre18973de5dd5ff1a9c94652fd808d42ffe2297096adb8a3cc1980f74a554ccea5;
postc5fa49a0c3cf7fdaa03cb6ba22f3fd0fcd539e9fab743ee3d724716e47755a5e.
Fresh source pairs immutable, paired refinement0 before verifier; no check disabled.

Source145 guard→MIRbb1size/bb2switch(true→bb3,false→bb4)→preASTIf(_7,Goto3,Goto4)
→postLabel3/Goto63. Physical203/postlist138/ordinal256 remains run-local,
but this run has actual EXEC203 following assume(resultsize=0), raw4112;
then EXEC204/return/free at4115+/native posts/leakcheck. No manufacturedEXEC.
All205 registered physical locations visited; noDEAD. Equalprinted202/204 are
separate; identity matched by source/control-flow/AST, not by numericID alone.

Full automatic source/tail/MU/F/thread/lifetime/type CURRENT posts are consumed
on normal/direct C1unwind/len<8/sizezero paths; unit outcome/free/leak checked.
Actual comparator operands1,0 derived from native source4, MU remains opaque.
False-normal226,9–227,1 and mappedfalse-unwind210,22–93 both reach their intended
Cannotprovefalse after nativecleanup. Defaultoff strictoutertype172 refusal;
sourcehash/extra-body/malformed/mixed each intended admission refusal beforetarget.
Independent raw explorer agrees with zero-route execution and full path cleanup.

Scoped verdict: native C1 research fragment PASS on named unaccepted profile;
no callable summary/fullactualsort4/stdcaller applicability claim. Added research
sizezero guard is not proved actualcaller condition and does not prove standalone
genericZST sort4safety. Native connectedC4 still NOT_RUN at this checkpoint;
old supplied C1→C4 PASS remains independent. Next scoped step: source-pinned
native C1–C4 actual comparison prefix with sequentialCURRENT/fullnative posts,
allfour directunwind exits, without caller/as_mut_ptr/guards/overflow/C5/copies.
