# Fresh final verdict — Build 3521e3b3

**INCOMPLETE / verifier exit 1 / no fresh VF0 for native→actual C1.**
Independent raw review: [FRESH-3521-INDEPENDENT-REVIEW.md](FRESH-3521-INDEPENDENT-REVIEW.md).
All helper bodies verify before target. Actual first comparator uses operands
1 and0 derived from native source storage, safe native F/thread/types and
checked reference argument preparation. Original scratch MU storage/owners
remain opaque; no optional-T adapter, MU inverse or re-supplied rawC1 inputs.
One strict scope, eight compiler callback locals, compiler HRTB/Output=bool,
normal and direct-unwind branches, four native unwind cleanup blocks retained.

The positive trace reaches direct comparator unwind and normal C1 return,
plus len<8 normal return. Each reached terminal path checks CURRENT native
postconditions, unit return, all local free obligations and final leak check.
Normal/unwind false controls fail at intended source226/210 after explicit
CURRENT/source-tail/MU/F/type cleanup; these controls themselves stop before
automatic return/post/leak. Full target nevertheless fails `dead code228,2`.
No complete proof/theorem/callable summary or actual external caller claim.

Fresh CFG correction performs its intended placement but does not remove
that refusal. The unvisited source-zero-size route is Label3→originalroot131
Goto63. It is the strongest candidate for the reported dead statement:
root129 Goto63 and root133 normalReturn are visited, but all3 print228,2 with
different physical locations. Exact physical diagnostic identity and reason
size_of==0 is not visited require disambiguation. Stock size_of spec has no
nonzero requirement; generic size is uninterpreted, FreezeMarker allowsZST.
No general rule is proved necessary, no guard/path removed, no dead-code or
strict-entry/cut/escape/unwind/free/leak check disabled. No further Cloud
experiment after main deadline; native→C4 remains NOT_RUN.

Build3521e3b3-5979-4c35-b931-93c4e165176b; proof=infra
2e995605f5183907817d92db082624281665d61e.
Create2026-10-10T23:48:14.972546175Z; finish23:54:44.406774Z;
390 charged seconds /389 execution. Token dispatch-f9d33272075e4481990a02c3f462e512;
config03c27dd85bad79f48e4b7f41613fdc05b0b7d06199045d69d9d7a7ecf03c8db2;
inputd6162f7526d251c099e16ed456ad17ca402b824588e0c8dfe7cc25ccd1eb93db.
Archive9fe9e42f34e4b5c2b1fb8a4644d3b00ab398cf871181b9efa045455ac7979249,
/tmp/native-c1-bound-3521e3b3-read, integrity/text-index verified.

ToolHEADf76012fb518703b1d98e243ac4f487f16877cfcb,
translator381e80ebe9a789877ee9d0e860da386f7692f54879b39775e01267f0db6f53d6,
patcheea19eda3723a0f60970df751c7600c326f98ad476d41f61e3f39442beb88693,
kernel37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c,
consolea3069f42c3cbac1da7d46c62d7192040a559b912cacadc667020197ea6460f69.
Effective profile artifact74591fdcf9846a7e56bc8a97833803b45a8f6d69129a4bd1694a2a4ecea52351,
bound phase profile348833f3b62ef96fc7984ffe4f4d04560b0d0266f5dd7df848e8a3ae8b33a9f7;
full fresh critical/binary/prelude snapshot in FRESH-3521E3B3-TOOL.json.
Fresh native input identityb26d60f3c455d37ef872f3cfa7e76db03544ab291f2af021f90453df25dfdf21,
FRESH-3521E3B3-INPUT.json (historical baseline separately labelled in archive).

PreAST18973de5dd5ff1a9c94652fd808d42ffe2297096adb8a3cc1980f74a554ccea5;
positive postASTc5fa49a0c3cf7fdaa03cb6ba22f3fd0fcd539e9fab743ee3d724716e47755a5e;
normal-false512259e40eb6bcc11ca6397d4ea1a684de705a3889df97d4e720a61b07f98dcd;
unwind-false50c19f4e755d30e7df35130ff2bb0895297e41921bf175400dc8f0a1747aa8f0.
Positive raw verification logc578064ef24a8364f58f4d86c5985ee9d51929538269416e1f6cbd8898ea7497.
All8 paired export/decode/refinement PASS; six exact sources enforce fullMIR
8e9adccc/bde6d797 and source7ebcf7cd/original7c35a7e0; immutable pairs.
Default-off strict-entry172 refusal retained. Source-hash, extra-body, malformed
and mixed controls refuse exactly before target; admission is not semanticnegative.
Profiles remain experimental/unaccepted. Prior components/C1→C4 not rerun.
