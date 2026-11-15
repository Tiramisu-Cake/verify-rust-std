# Test-only correction after CI43653703859

Input source61eb057b46e2ffd62df28c3e956cd8031ed84748, research019177d852.
No native builds/proofs/formatter, push or CI run. Production unchanged.

## Same intended byte, two checks

Padded hole source is UNCHANGED. For each raw/borrowed fixture:
- stride = size_of::<Padded>(), offset = offset_of!(Padded,value).
- initialized_prefix = stride + offset + size_of::<u32>() -1 = stride+offset+3.
- write_bytes initializes [0,initialized_prefix), leaving byte initialized_prefix unwritten.
- only std::ptr::read::<u8> invocation reads slot1 offset+3, exactly that first unwritten
  DATA byte (fourth byte of the u32 field), not padding or an out-of-bounds address.
- slot0 value and slot1 offset+2 use read_volatile, with useful own assertions SUCCESS.
- Actual complete failure list is precisely read::<u8>.safety_check.1 (*const u8)
  and read::<u8>.safety_check.4 (u8), both at the same read function/source location.
  Alignment and pointer-validity checks there SUCCESS; all volatile checks SUCCESS.

The pointer-typed description does NOT prove the pointer value uninitialized. In
check_uninit/mod.rs build_get the diagnostic uses operand.ty() for MemoryInitOp::Check,
but relevant_instruction.rs mk_operand passes that pointer value to the pointee-region
initialization query. visit_place generates this check at raw dereference. The scalar
check is the payload initialization check through the same single read. Thus both native
failures originate from the intended data-byte load; there is no independent second
bad read in this harness. This is source reasoning plus the supplied native check list,
not an independently captured MIR/trace causality proof.

Goldens now require exactly N2, BOTH complete function/status/description triples,
BOTH named Failed Checks, both useful own SUCCESS triples and Complete1total. They
cannot accept an arbitrary second failure. No std file/line/nightly/full inventory pins.
Assertions use function assertion prefix plus exact description, avoiding erroneous
assumed numbering (native .4/.6 in hole, .5/.6 initialized; arithmetic checks occupy
other assertion numbers). Initialized variants retain N0 and both useful assertions.

## Same-place Copy controls

Changed only Copy(source),Copy(source) syntax to source,source in each custom MIR Call.
Copy operands are bare places; explicit Move of result/original/RET remains intact.
No domain, target argument index, selected read, source-preservation witness or flags changed.
Four sources previously failed E0423 before verification; no corrected-copy native outcome
is claimed. Both hole callees still use std::ptr::read::<u32>, so goldens prescribe the same
generic raw-pointee/payload pair (*const u32/u32), exactly N2, rather than the earlier N1
source guess. This expectation is SOURCE-DERIVED from that unchanged read implementation
and the observed u8 pair, NOT an observed u32 result; coordinator targeted rerun must
confirm it. Initialized companions remain N0 with selected/original-after-call witnesses.

## Validation

- Python replay of compiletest contains_lines against ONLY saved native stdout, excluding
  the old failing expected patterns printed by compiletest:4/4 padded goldens PASS.
- 18 synthetic wrong-count/type/function/missing-useful-witness inputs rejected.
- Source comparisons: four padded .rs byte-identical; four Copy .rs differ solely by
  removing Copy(...) wrappers. All geometry/checks/flags/pins preserved.
- git diff --check PASS; source delta confined to10 files in these two test directories.
- Hook production,9 marker controls, docs, compiler/runtime/driver/runner untouched.

New-head native fmt/targeted qualification pending. Existing61eb hook observations,
units/kani/ui/script/json, marker9 and4 mutation results are historical CI input; no
claim of new-head full acceptance or three-platform Gate A. Gate A remains NOT_RUN.
