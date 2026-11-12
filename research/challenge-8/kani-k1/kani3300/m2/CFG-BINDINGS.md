# M2 source/CFG bindings — static only

Base `5abdcf982da6aff65662e198af27a9c776830a89`, tree `960a71c70b3f890b4f5cd2b53a83f6a0f8e00951`.
Candidate `5f7f2b7364135a0a8b7cfd86c43b4491a8911bac`, tree `b2bbb7366a9fbac33398fb01be7300f83a1d27bd`.
All paths below are relative to the Kani clone. Hashes are in TEST-MANIFEST.json; no production bytes changed.
Coordinates describe source rules and required joins, not observed generated MIR/CFG or reached properties.

## Existing normal destinations and false protocol

- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs:122`
  computes needs_get and common-ancestor needs_set, then mutating relevant places get SetRef(true, After).
  This includes the existing D0 left normal call destination; M2 adds no duplicate setter.
- `.../ptr_uninit/uninit_visitor.rs:1145` admits protocol only for bodyful nonforeign InstanceKind::Item.
  Resolution/unsupported guards precede call-specific effects; closure FnOnce source syntax proves no Shim coverage.
- `.../ptr_uninit/uninit_visitor.rs:47` enumerates original argument locals starting at1; count is shadow-argument count.
  Entry loads occur before user effects. `:493` creates caller shadow return LoadArgument(index0,count0,After).
  `:696` begins/stores original indices before **all** Move SetRef(false) operations; `:766` stores return0 before Return.
- `.../check_uninit/mod.rs:691` passes argument index and `function.to_index()` as usize signature; loads additionally
  receive count and transfer mask. Concrete model-dependent signatures remain UNKNOWN; must match within each pair.
- `library/kani_core/src/mem_init.rs:431` initializes fresh protocol; `:449` snapshots live object/offset/value before reset;
  `:501` checks active/signature/count/order/size and mandatory return0. Selected source-following branch assigns
  `buffer_value && layout[relative_offset]`; optimistic alternative sets destination data true. Neither branch is omitted.
  A hole control must reach the false source-following path; the optimistic branch is not exact initialized state on every path.

| Source callee | Original shadow indices / count | Normal return | Required selected path |
| --- | --- | --- | --- |
| call-pairing select(MU,u32,MU,u64,MU,u8) | 1,3,5 /3; gaps2,4; which6 ordinary | 0 /0 | which0/1/2 -> indices1/3/5 false; positive first11 and repeated third61 |
| nested_select(MU,u32,MU,u64,MU) | 1,3,5 /3 | 0 /0 | outer third -> inner select third, first initialized31 then false |
| argument-return select(MU,MU,bool) | 1,2 /2; bool3 ordinary | 0 /0 | false -> b false; arbitrary-bool failure covers only this branch |
| argument-buffer nested_return/return_second | 1,2 /2 at both boundaries | 0 /0 per function signature | b false through inner then outer return |
| invoke_once(captureless F) and actual closure Item | wrapper has no shadow args /0; actual lowered closure args UNKNOWN | 0 /0 for each MU return | plain/seeded true7 vs false; bind resolved Item, never relabel Shim |
| typed roundtrip(MU<Padded>) | 1 /1 | 0 /0 | data preserved, padding discarded |
| read_argument(MU<Padded>); return_slot() | 1 /1; none /0 respectively | ordinary u8; MU return0 /0 respectively | source padding pre-read SUCCESS; post-transfer padding false |
| consume/consume_and_write/consume_noncopy/consume_union/consume_padded | 1 /1 | ordinary u8, no shadow return0 | snapshot then in-place Move reset vs Copy preservation |
| union_roundtrip(Byte) | 1 /1 | 0 /0 | true and false byte pair |
| contract choose/relay(MU,MU) | 1,2 /2 at both boundaries | 0 /0 | initialized29 frame case vs false requires case |

Full source/harness/hash matrix, including all 13 call-move harnesses, is QUALIFICATION-MAP.json.
Generated wrapper/closure signatures and all concrete property IDs/operands/normal blocks remain UNKNOWN until observed.

## Raw extent, typed masks and out-pointer

- `.../check_uninit/ty_layout.rs:143` computes typed MU storage D(payload) at rustc stride; `:171` raw storage full extent;
  `:132` Move deinit covers whole sized storage. Padded fixtures assert size8, value offset4, stride8;
  D(Padded) is `[T,F,F,F,T,T,T,T]` on that asserted layout. Raw extent8/16 preserves padding, typed operations discard it.
- `.../check_uninit/mod.rs:659,760,837` separates raw copy from typed union/storage transfer and typed preserve mask.
  `mem_init.rs:148` source-following copy ANDs existing value with mask; it cannot turn false data true on that path.
- New out-pointer helper has ordinary `(*mut u8,bool)->()` arguments, no shadow payload/return0.
  Returning an initialized pointer/unit does not justify initializing its pointee. Full writes offsets0,2,1;
  partial writes0,2 only. Require actual setters to match exactly these bytes, successful endpoint reads and false middle read.
  MU<[u8;3]> stays valid until intended partial raw read; no hole array assume_init or &[u8] is formed.

## Normal and abnormal edges

- `.../transform/body.rs:307` split_bb_after rewires a terminator's normal target only; get_mut_target_ref `:674`
  accepts Call{target:Some}, not abnormal edges. After instrumentation does not imply execution after a diverging call.
- New return_or_abort(bool)->MU<u8> has an ordinary caller normal target. False returns initialized7 through return0;
  true reaches panic and no callee Return. Require the reached panic property, static true-path CFG and absence of executed
  return0 store/load/destination setter on that path. The normal read/assertion must independently succeed.
- `kani-compiler/src/kani_compiler.rs:98` pins panic=abort; compiler_interface.rs:658 rejects other strategy.
  Existing custom-MIR UnwindUnreachable controls qualify normal Move ordering only. Real unwind/cleanup NOT_COVERED.

## Reset -> immutable seed -> first effect and private state

- `.../ptr_uninit/mod.rs:54,82,101` identifies explicit proof and proof_for_contract roots and inserts the reset call
  before their first statement/terminator. `mem_init.rs:240` resets nondet object/offset, false value, buffer active,
  selected index and has-witness. Other buffer fields are reset at protocol begin, before any loads.
- `library/kani_macros/src/sysroot/contracts/mod.rs:570` generates manual PFC entry clause-depth reset then init_contracts.
  The later UninitPass prepends memory reset; its normal completion seeds before those user/contract entry effects.
- `.../transform/automatic.rs:2447` separately generates clause-depth reset before init_contracts for automatic contract
  roots. It is not a second memory-reset implementation. Actual generated root attributes, pass traversal and retained
  entry order are UNKNOWN; explicit new harnesses do not establish automatic-harness coverage by source presence alone.
- `.../context/goto_ctx.rs:80,133` owns/default-constructs immutable registry per GotocCtx.
  `compiler_interface.rs:137..204` prepares after recollection, emits items and check-contract machinery, handles quantifiers,
  then finalizes before metadata/export. No registry lifetime/closure or transformation cache change in M2.
- `.../context/immutable_allocations.rs:162` seals the registry, qualifies/comparers descriptors and validates canonical layout;
  `:210` resolves the single reset marker definition and unique private state. `:308,326` seeds every normal Return
  recursively including labels/branches/loops. Original reset statements are retained before seeds; no per-use/call-return seed.
- `.../codegen/contract.rs:129..176` places marked MEM_INIT_STATE in verifier-private assigns, including buffer fields.
  `library/kani_core/src/lib.rs:790..805` marks clause-depth internal storage; check_uninit/mod.rs:59..98 skips its helpers.
  New legal PFC must retain useful ensures plus frame SUCCESS; existing outside-user-write frame negative must still fail.
- No other source sites invoking/defining InitializeMemoryInitializationState were found in kani-compiler/src and library;
  this source search is not completeness evidence for exported/generated roots. For every actual ordinary/PFC/generated
  reset instance, coordinator must join reset body -> completed false/buffer resets -> canonical seed -> first effect.
  Missing reset/private symbol, late registry admission, intervening effect or partial binding blocks acceptance.

No new compilation/runtime/property evidence; source audit does not close M1 release blockers, B1 or B2.
