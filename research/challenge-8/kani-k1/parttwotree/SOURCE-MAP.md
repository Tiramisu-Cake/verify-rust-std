# PARTTWO-TREE source map

Base library: Part 1 v6 `d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097`, library tree `d4ec476a7a001363e58f19948c188a9c2078e370`.
Branch base (coordinator clarification): MACSPLIT head `4f4034527d3e3a26e4cd94e12ba6922e2b5e80e4`, library tree equal to v6 (checked).
Candidate library commit `2756f0e2a6ae0956fdb427574eda39b5b9a76e64`, library tree `a45388ac593c809405558ea0c27599f487b17e4e`.
All identities and byte relations below are checked by `check_parttwotree.py` (report `static-check.json`, 50/50 PASS).
Paths are relative to `library/core/src/slice/sort/shared/smallsort/verify/`.

## Frozen inputs (all objects present; no UNKNOWN)

| Line | Report tip | Library commit → tree | Prerequisite history (library → tree) | Lineage base |
|---|---|---|---|---|
| L-M bridge incl. N9 | `8cbb267500` | `77cb4c9773` → `b903aba7c3` | BRIDGE `b07dc219a2` → `f3bf04b5cc` | `9dcf313fb4` (v4 tree `3c23a45984`, pre-CLEANUP) |
| L-W wrappers incl. WONETWO | `b21be6cd86` | `4231462d12` → `c407b96a8c` | `e4f1df6a34` → `1731596d7c`; `af8b0db75a` → `af3da15225` | `dd0f293f00` (v5 tree `cbe69760c8`) |
| L-N u8 network + N10 | `61cfba69c3` | `2ebda13e14` → `40d3b22c82` | NETCOMP2 `f4d3775dc5` → `3b6d2a51da`; NETTEN `23ba8cfddb` → `74e42aaa19` | `dd0f293f00` |
| L-N u64 N9 + N13 | `4b9d56c46d` | `497077c6cd` → `90a3889318` | U64-N9 report `9ab925b157`, library `fddf308321` → `d22566ab5a` | `dd0f293f00` |
| L-N N18/MERGESTEP/merge4 | `e3a778017a` | `248b2725c6` → `7996f9c151` | NET18 `7d8b21728b` (lib `4eb7e81259` → `1fa41b3a5f`); MERGESTEP `97a252bea7` (lib `91d4d9f77a` → `dc7c79bb9b`); `813a03db4a` → `334b3a2912` | `dd0f293f00` |

The three L-N rows are independent descendants of NETCOMP2 `f4d3775dc5`; none is merged or cherry-picked.
Parallel U64-TEN-LEAVES is not an input.

## Transferred files (new; exact pinned blobs)

| New path | Source commit:path | SHA-256 (prefix) | Relation |
|---|---|---|---|
| `bridge.rs` | `77cb4c9773`:same | `c23c98ab02395b36` | byte-identical (BRIDGE b07dc219a2 rows + BRIDGENINE +55/-2) |
| `wrap/wone.rs` | `4231462d12`:same | `5eea4aa0a1d4274f` | byte-identical (WONE + WONEDIAG N3 + WONETWO N2) |
| `network/netcomp.rs` | `f4d3775dc5`:same + 2 appended blocks | `be32ff1cf425398f` | = NETCOMP2 blob + `mod netten` block of `2ebda13e14` + `mod neteighteen`/`mod mergestep` block of `248b2725c6`; each lineage's own netcomp.rs is reproduced exactly by dropping the other block; u64 lineage netcomp.rs = NETCOMP2 blob |
| `network/netcomp/netten.rs` | `2ebda13e14`:same | `695023a6f02359da` | byte-identical (NETTEN-LEAVES `23ba8cfddb` + `mod caller`) |
| `network/netcomp/netten/caller.rs` | `2ebda13e14`:same | `1553847604e9cb66` | byte-identical |
| `network/netcomp/neteighteen.rs` | `248b2725c6`:same | `6c6281e9d41825fc` | byte-identical (unchanged since `4eb7e81259`) |
| `network/netcomp/mergestep.rs` | `248b2725c6`:same | `2ae7e36dbcd2828e` | byte-identical (`91d4d9f77a` + `mod directfour` of `813a03db4a`) |
| `network/netcomp/mergestep/directfour.rs` | `248b2725c6`:same | `d8f694728de2393e` | byte-identical (`813a03db4a` + Profile import fix `248b2725c6`) |
| `network/u64nine.rs` | `497077c6cd`:same | `fd27513298a12d77` | byte-identical (`fddf308321` + `mod uthirteen`) |
| `network/u64nine/uthirteen.rs` | `497077c6cd`:same | `330732a2df9aec04` | byte-identical |

Because blobs are unchanged, every target/contract/real body, ghost context static, probe, adapter, bridge
impl, assertion, cover and annotation is unchanged with the same symbol and module path as on its lineage.
Separate context statics stay separate: `CONTEXT9`, `CONTEXT13`, `CONTEXT_TEN`, `STEP_CONTEXT`,
`CONTEXT_U64_NINE`, `CONTEXT_U64_THIRTEEN`. No shared u8/u64 framework was introduced; no symbol renamed.

Symbols per file (targets first, then helpers/bridges/roots), new path = old path:

- `bridge.rs`: targets `frame_target`; uses `merge::specfix::merge_profile` (v6, ordinary). Bridge `MergeBridge<F>`
  (sole impl u8/fnptr), `adapter`, `caller`, `always_true`, `frame_case`, `bridgenine_stable_caller`; 9 roots.
- `wrap/wone.rs`: targets `stable_cell_len`, `unstable_byte_len`, `freeze_noncopy_len`, `stable_byte_len`; helpers
  `region`, `separate_scratch`, `sorted`, `count`, `region_sorted`, `region_count`, `canonical_guard`, `input_frame`,
  `input_covers{,_n3,_n2}`; 12 roots.
- `network/netcomp.rs`: targets `swap_net9`, `swap_net13`; `U8Cmp`, `canonical`, `region9/13`, `count9/13`,
  `Context9/13` + statics, `register9/13`, `SwapBridge9/13` (sole impl u8/U8Cmp), `adapter9/13`, `check_context9/13`,
  `run9/13`, `positive9/13`, `always_true_u8`; 9 roots.
- `netcomp/netten.rs`: `sorted10`; 2 leaf roots (targets `swap_net9`, `specfix::insert_tail_profile`).
- `netcomp/netten/caller.rs`: `ContextTen` + static, `context10`, `backing10`, `register10`, `SwapBridge10`,
  `swap_adapter10`, `InsertBridge10`, `insert_adapter10`, `check_context10`, `run10`, `check_final10`; 4 roots.
- `netcomp/neteighteen.rs`: `swap_leaf18`; 3 roots (targets `swap_net9`, `specfix::merge_profile`).
- `netcomp/mergestep.rs`: targets `up_step_u8`, `down_step_u8`; `RawStep`, decoders/geometry/selection helpers,
  `StepContext` + static, ledgers, `MergeStepBridge`, `up_adapter`, `down_adapter`, `prefix4_sorted`, `check_merge4`,
  `control_merge4`; 6 roots. `directfour.rs`: 1 root (target `specfix::merge_profile`).
- `network/u64nine.rs`: target `swap_u64_net9`; `U64Cmp`, `canonical`, `region9_u64`, `count9_u64`, context,
  `SwapBridgeU64Nine`, `adapter_u64nine`, `check_context`, `run9`, `always_true_u64`; 4 roots.
- `network/u64nine/uthirteen.rs`: target `swap_u64_net13`; N13 analogues; 4 roots.

## Parent edits (insert-only; no other line of v6 changed)

| File | v6 SHA-256 → new | Inserted lines | Reason |
|---|---|---|---|
| `../verify.rs` | `5791fee0819b1677` → `29de9ac9d0836865` | `#[cfg(kani_smallsort_controls)]` `mod bridge;` at end | lineage had an un-gated `mod bridge;` with inner `#![cfg]`; the task requires a cfg-gated registration; inner attribute kept (byte copy) |
| `network.rs` | `d3d0047bf9b08aca` → `2233268e84e4ac63` | `#[cfg(kani_smallsort_controls)] mod netcomp;` after the `use` block (lineage position); same for `mod u64nine;` at end | the two network children of NETCOMP2 / U64-N9 |
| `wrap.rs` | `d829b2539e76d709` → `4bdbae717cc3a212` | `#[cfg(kani_smallsort_controls)] mod wone;` at end | WONE child |

`verify/merge.rs` needed no edit (no transferred item lives there). Runtime `shared/smallsort.rs`, all other v6
files, tooling, workflows, pin and flags are unchanged (`library_changed_paths_exact`: 3 M + 10 A only).

## Dependencies on v6 items (no helper moved)

- L-W/L-N: `smallsort.rs`, `merge.rs`, `merge/specfix.rs`, `types.rs`, `comparators.rs` are byte-identical to
  each lineage library; `wrap.rs` equals the WONE lineage except the registration. Network imports
  (`StrictU8`, `StrictU64`, `count_matching_values`, `is_sorted_by`, `prefix_unchanged`) are unchanged v6 items.
- L-M: `merge.rs`/`specfix.rs` at `77cb4c9773` equal v4 `9dcf313fb4`; v4→v6 difference on them is exactly
  CLEANUP `dd0f293f00` (removal of `cfg(any())` items; RESULT-CLEANUP: active bodies/signatures unchanged).
  Used items `merge_length_body`, `LtU8`, `Profile`, `merge_halves_sorted`, `merge_profile`, `merge_regions`,
  `model_count`, `model_sorted` are active in v6. Leaf for `bridgenine_caller_u8_n9` is the existing ordinary
  `merge::merge_scratch48_contract_u8_n9` (unchanged v6 root; no copy).
- No retired source (`correct.rs`, `cfg(any())` fragments) is restored or needed.

## Not transferred (explicit)

L-N lineage `network.rs` also carries NETNINE/NETTHIRTEEN direct roots `netnine_full_value_count_u8_n9{,_negative}`
and `netthirteen_full_value_count_u8_n13{,_negative}` (records N1–N4, function-item F) plus a reworded comment in
the ordinary `network_correctness_fixed` body. They are outside the task's file scope (network.rs: registrations
and dependencies only) and are not dependencies of any transferred file, so they stay historical; the ordinary
comment edit would change a v6 ordinary source. The fnptr direct baseline `netcomp_direct_u8_n9` is transferred.
`check_parttwotree.py` confirms these four are the only lineage roots not carried over.
