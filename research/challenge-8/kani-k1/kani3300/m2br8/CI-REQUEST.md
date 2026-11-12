# Coordinator handoff — R8 only, no dispatch authorization here

READY 0ab62c7b0cdecd880064b0628f995c5a5b3de9ab
Tree 4a6de5d458cf4cde1c54c8c3a7aba2469af7fa04; full tests tree
b887d2a2074e158368a6b1f04f5c971f48c69bdd. Local Kani source branch
fix/kani-3300-pointer-transfer-carrier, /root/kani-fix-3300-m2br8; unpushed.
Source commit2bd63183d88bec2efeeccb88b450b50939d120c3 plus exact reviewed R8-C
four-path delta9c8693997682e7be48230fabcf0d01f29c41f93d298bfa06898682d090efb2f2.
SOURCE.patch applies to exact base8e01eb2aff5183c53403e1d1e73e573ce28d3095;
R8C-TEST-DELTA.patch then applies on source candidate. No source import from R8-C.
Do not use old R1/R6 runtime or a filtered tree. Preserve original fixtures/goldens.

## G1, sequential resource gate

Build/fmt/clippy first; source audit/rustfmt are not compilation. Bind expanded core/std
macro, actual *const u8 field types and all -Dwarnings, no B3 E0308/E0277 shortcut.
Use existing coordinator-only fork preflight/lanes. No worker dispatch or Cloud spend.
Reuse coordinator-reported R7 B0c614dba9ca/run43283061769 and B1b4eb8294b7/
run43283068930 P1/P2 resource baselines; do not rerun historical variants. R6-02b
50s/1.95GB had frameFAIL and cannot establish acceptance or cost causality.

1. Unchanged P1 first: tests/expected/uninit/private-transfer-frame/scalar-pfc-legal.rs,
   SHA256fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b,
   root postcondition_reads_initialized_return (bind actual emitted root). Existing single
   root/solver, flags and300s/>6GiB watchdog; retain raw units/sampling/overshoot.
   All obligations SUCCESS including carrier/model/private frame. If heavy again,
   STOP for bounded formula/use diagnosis. No pointer-validity assume or hidden weakening.
2. P2: tests/expected/uninit/transfer-qualification/postcondition-hole.rs,
   SHA25661fc369a6830c6ff185887b04db36139ca529e4de097c0025ce7b29c8323f759.
   Intended first payload read in ensures must fail, no earlier model/guard/path loss.
3. R8-C tests/expected/uninit/private-transfer-pointer/{legal,hole}.rs, one root each:
   nonzero_offset_move_return_legal: all SUCCESS, useful byte values11/22/33;
   nonzero_offset_move_return_hole: first two reads lawful, intended third-byte u8
   read at hole.rs:38 FAILURE only in intended inventory. Negative golden alone
   cannot rule out extra failures. Exact hashes and selectors in TEST-MANIFEST.
4. All unchanged R7-C mapped controls from ../m2br7c/CONTROL-MAP.md and manifest:
   lawful_modifies SUCCESS, outside-frame negative actual user outside write FAILURE,
   clause negative intended read FAILURE; false/call-pairing/move/padding/return/out/
   abort/repeated/nested controls retain expectations. No private assignableFAIL may
   stand in for intended failure. P2 and old legal-pair stay required.

Each case needs full bounded failure inventory, source/tool/sysroot/argv/config/binary
identities, actual exits and phase status, steps/VCC before/after, conversion times,
variables/clauses/RSS and watchdog sampling/overshoot/raw units. Cutoff INCOMPLETE;
setup failure means solver NOT_RUN; parser/job status alone is not proof. Use Evidence
Brief and bounded source-bound catalogue queries only; no raw logs/archives/formula dump.

## Required semantic and assigns binding

Bind exact caller/model copies and model monomorphizations, not just matching source
names or property coordinates. For R8-C require actual dataflow with selected witness
relative2, three-byte extent/offsets0,1,2/no padding, source slot allocation/type/layout,
Store live capture before Call(Move)/deinit, callee parameter Load1, return Store0,
source-frame cleanup/DEAD, normal destination Load0 and actual final third read.
NoCopy and inline(never) are source hints; actual MIR/slot/deinit/frame path must bind.
Eliminated Move/death/nonzero witness leaves qualification UNKNOWN, not established.
For P1/P2 bind reset/transfer/normal load/ensures and first intended payload read.

Store guards: range, same object, base offset unchanged, nonwrapping byte offset,
exact target-width round-trip. Load guards: same object, nonwrapping offsets, r<N.
Every reached obligation must be SUCCESS; failures cannot be discarded as benchmark
relief. A guard failure on a previously admitted representable valid source is STOP
with counterexample/config; no assume/scope narrowing. Zero/no-witness does no codec;
false witnesses do. Source never reread after Move/death. Bind actual BV backend/
CBMC version/flags/object_bits/target W/O/binary to primary-source lemma; another
backend/version is not admitted by source reasoning alone.

PFC must contain both actual distinct marked globals, unchanged whole-main target and
all13 buffer member cell lvalues. For saved_base/saved_byte, emitted assigns target
address must be &ARGUMENT_BUFFER.<field>, extent sizeof(*const u8), containing object
ARGUMENT_BUFFER. Never deref/object_whole(saved pointer), source/pointee allocation,
pointer-value range or whole-buffer/padding/blanket skip. Verify actual types are
unsigned8 pointers, not void pointers; no cast rvalue. Field-set coverage is separate
from total lambda count (private14, public variable). Actual writes scalar cells only.
Unsupported/early frame/carrier guard/path loss is not a resource improvement.

## G2 and later boundary

Only after accepted G1: full Uninit Quick + immutable registry unit5 + kani Uninit +
expected + ui + mem-init-reinstrumentation. Do not exclude legal-pair/postcondition-hole
or weaken old fixtures/goldens. Retain exact external mixed16 composition request
83ceadf0485f30548c92b77c87b3c08a53f0b019/tree15d3d3ecb5d353da3ae1c51567d9b0d04cc9f5fb;
only test-only composition with exact hashes, no old production. Generated golden IDs
may change only from observed source-bound CI, no generic frameFAIL acceptance.
Full platform/tool gate and SmallSort replay later. M3 HELD through accepted G1/G2.
This handoff is SOURCE_READY/NOT_COMPILED, all gates NOT_RUN, proof credit0, Cloud$0.
