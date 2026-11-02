# Part 2 evidence draft — opt-in compositional proofs for small-sort (Kani)

Status: draft for coordinator review. Read-only compilation of recorded results; no new Build was run for this document.
Local PARTTWO-TREE copy (2026-11-02) of `/root/smallsort-pr-drafts/PART2-EVIDENCE-DRAFT.md`: N22c updated from
RESULT-NETTEN-CALLER @`61cfba69c3`, control row N22d and totals (§4.1) added; all other rows unchanged.
Historical table of different trees, not evidence for one head and not credit for the PARTTWO-TREE integrated tree.
All evidence below is research evidence behind `--cfg kani_smallsort_controls` (opt-in). None of it is part of the
ordinary harness sets (see §6).

Common verification setup unless a row says otherwise: Kani `9461e07af7ec929f050aa4192f29363c9be07779`,
toolchain nightly-2026-10-12, tooling check against `30f77e859903df14b442ff9294d4fbbd44827f20` PASS, Cloud Build
lane in measurement mode, `jobs 1`, uninit checks **off**, unwinding assertions on, k1-standard4 (4 CPU / 16 GiB,
swap off), per-row timeout 600 s (length-wrapper builds: `timeout10`, i.e. 10 min). "VT" is Kani's printed
verification time per row; "RSS" is the sampled CBMC process peak (KiB) unless noted. "Library tree" is the
`library/` subtree hash of the stated commit (re-checked with `git rev-parse <commit>:library` for every row).

Kinds used below:

- **Theorem (PFC/direct)** — a `proof_for_contract` or plain proof over the real body, no stubs, on the exact domain stated.
- **Actual binding** — a proof of an actual library entry point in which raw helpers are replaced via
  `stub` → closed adapter → `stub_verified` summary; it is only a composition result when every summary has a
  matching independent leaf theorem on the same domain.
- **Control** — an intended-failure row (wrong comparator, corrupted output, binding guard); expected FAILED with a
  single named literal.
- **Diagnostic** — a measurement/baseline row whose purpose is comparison or cause isolation.
- **Stage gate** — the recorded overall acceptance of one Build packet (identities + all rows met expectations).

## 1. Source lineages (do not merge into one "verified head")

The records come from three separate library lineages; none of the lineage tips is an ancestor of another.
Results on one lineage say nothing about code on another, and within a lineage each row is tied to its own commit.

| Lineage | Commits (library commit → tree) | Records |
|---|---|---|
| L-M (stable merge bridge) | `b07dc219a2` → `f3bf04b5cc`; `77cb4c9773` → `b903aba7c3` (child of `b07dc219a2`) | M1–M8 |
| L-W (length wrappers) | `e4f1df6a34` → `1731596d7c`; `af8b0db75a` → `af3da15225`; `4231462d12` → `c407b96a8c` (linear, off base `e382287728`) | W1–W6 |
| L-N (unstable network) | `24d9f1d3d8` → `ac095c9d7b`; `d60b2c975d` → `a618a0bdce`; `47ed440a23` → `f9fa2945d6`; `f4d3775dc5` → `3b6d2a51da`; then three branches off `f4d3775dc5`: `fddf308321`/`497077c6cd` (u64), `4eb7e81259`/`91d4d9f77a`/`248b2725c6` (N18 leaves → merge step → direct merge4), `23ba8cfddb`/`2ebda13e14` (N10) | N1–N22 |

## 2. Claim table

Domain shorthand: T = element type; F = comparator type; CMP = comparator value; probe = independent value used by
the full-value count oracle; N = length; backing/offset = exact allocation and start; init = initialization of the
input/scratch; frame = what is proven unchanged. "fnptr" = `fn(&T,&T)->bool`. `StrictU8::CMP` / `StrictU64::CMP` are
the reified `strict_less::<T>` (ordinary `<`, full-value model). `LtU8::CMP` compares the key `x>>1`
(so ties exist between distinct bytes); its oracle is key sortedness plus full-byte count.

### 2.1 Stable merge bridge lineage (L-M)

| ID | Kind | Property | Exact domain | Route | Status / checks / covers | Internal ref |
|---|---|---|---|---|---|---|
| M1 | Theorem (PFC) | `merge_profile::<LtU8>` contract (sorted merge, full-value count, dst-only frame) | T=u8, F=fnptr, CMP=`LtU8::CMP`, N=3 split 1+2; separate initialized source `[u8;3]` offset0; separate `MaybeUninit<[u8;3]>` dst offset0; independent `LtU8` probe set before call | leaf, real body, no stubs | SUCCESS, 0/566 failed (68 unreachable), covers 1/1 | BRIDGE row1 |
| M2 | Actual binding (merge level) | raw `bidirectional_merge` is replaced by the verified profile through a closed adapter; post-oracle holds | same as M1 (right pair sorted) | raw `bidirectional_merge<T,F>` → `adapter<T: FreezeMarker + MergeBridge<F>, F>` → sole u8/fnptr impl → `merge_profile::<LtU8>` (`stub_verified`); leaf = M1 | SUCCESS, 0/538 (65 unr.), covers 3/3 | BRIDGE row2 |
| M3 | Control | wrong F and unsorted halves are rejected by the summary preconditions | as M2; wrong-F keeps domain; unsorted keys `[1,0]` | as M2 | both FAILED as expected, single failure each at the canonical-comparator and sorted-halves `requires` (specfix.rs:317/:318); covers 2/3 each | BRIDGE rows3–4 |
| M4 | Diagnostic (frame calibration) | modifies-set of the target is enforced at a write outside dst | separate source3, initialized backing4, dst `[0..3)`, sentinel `[3]` | real target | positive SUCCESS 0/442 covers **2/5**; negative FAILED as expected (`assignable` check, bridge.rs:122) covers 3/5 — per-cover identities not reported | BRIDGE rows5–6 |
| M5 | Theorem (PFC) | merge leaf for the N9 scratch geometry (stable M03 and general M04 clauses) | T=u8, F=fnptr, CMP=`LtU8::CMP`; source `[MaybeUninit<u8>;48]`, offset0, prefix9 initialized / tail39 uninit, split 4+5; separate initialized dst `[u8;9]` offset0; dst9-only frame; same probe/model | leaf, real body | SUCCESS, 0/571 (57 unr.), covers 2/2 | BRIDGENINE row3 |
| M6 | Actual binding (whole entry) | `<u8 as StableSmallSortTypeImpl>::small_sort` at N9 sorts by key and preserves full-value count | T=u8, one local F=fnptr, CMP=`LtU8::CMP`; caller-owned scratch48; independent probe; no caller sortedness assume | real sort4 ×2 + insertion → raw merge → B1 adapter → verified `merge_profile<LtU8>`; leaf = M5 (same Build) | SUCCESS, 0/743 (59 unr.), covers 3/3 | BRIDGENINE B |
| M7 | Theorem (direct) + Diagnostic baseline | same property as M6 with no stubs | identical to M6 | real body throughout | SUCCESS, 0/569 (53 unr.), covers 2/2 | BRIDGENINE A |
| M8 | Control | full-value oracle detects a payload flip that preserves keys | `[p;9]`, probe=p; `v[0]^=1` after return | as M6 | FAILED as expected, sole literal `bridgenine output preserves full-value probe count` (bridge.rs:176); covers 3/3 | BRIDGENINE control |

### 2.2 Length-wrapper lineage (L-W)

Opt-in wrappers `stable_cell_len`, `unstable_byte_len`, `freeze_noncopy_len`, `stable_byte_len` with signature
`(v:*mut T, len, [scratch], cmp: fnptr, probe:u8)`; contracts: key `x>>1` sortedness, scalar full-byte count,
input-sentinel frame. Real trait bodies, **no summaries** — these are direct theorems, not compositions.

| ID | Kind | Property | Exact domain | Status / checks / covers | Internal ref |
|---|---|---|---|---|---|
| W1 | Theorem (PFC) | `stable_cell_len` contract for N∈0..3 | T=`Cell<u8>`, canonical cell fnptr; per arm backing N+2, offset1, len N; scratch backing2 borrowed 0..2, slot0 init / slot1 uninit; unrestricted values/probe/sentinels | SUCCESS, 0/328, covers 18/18 (N0 vacuous for order, N1 substantive only for count) | WONE row1 |
| W2 | Theorem (PFC) — **not established** | other three wrappers for N∈0..3 | T=u8 / private Freeze !Copy `NonCopyU8` / u8; stable u8 with separate uninit scratch48 | `unstable_byte` TIMEOUT, `freeze_noncopy` TIMEOUT, `stable_byte` OUT_OF_MEMORY | WONE rows2–4 |
| W3 | Control | canonical-comparator guard; full-value checker rejects `^=1` payload corruption after real stable u8 N3 | — | both FAILED as expected (wone.rs:58, :321), covers 1/1 each | WONE rows5–6 |
| W4 | Theorem (PFC) | three wrappers at fixed N=3 | backing5, offset1, literal len 3; otherwise as W2 | all SUCCESS, 0 failed, covers 7/7 each | WONEDIAG |
| W5 | Theorem (PFC) | three wrappers at fixed N=2 | backing4, offset1, literal len 2; otherwise as W2 | all SUCCESS, 0 failed, covers 7/7 each | WONETWO |
| W6 | Diagnostic | fixed-length PFCs fit where the N0..3 union did not | W2 vs W4 | supports a joint effect of length union/dispatch/backings; no single cause isolated | WONEDIAG |

### 2.3 Unstable network lineage (L-N)

All rows: actual unstable entry `<T as UnstableSmallSortTypeImpl>::small_sort` → Freeze+Copy path →
`small_sort_network`; unwind25 unless noted. "Exchange summary" = `swap_net9` / `swap_net13` / `swap_u64_net{9,13}`
(pair transfer/order, per-pair count invariant, frame of all other cells).

| ID | Kind | Property | Exact domain | Route | Status / checks / covers | Internal ref |
|---|---|---|---|---|---|---|
| N1 | Theorem (direct) | N9 sortedness + full-value count | T=u8, **F = function-item type of `strict_less::<u8>`** (no fnptr coercion), full `any [u8;9]`, independent u8 probe, backing9/offset0 | real `sort9_optimal`, empty insertion suffix, no stubs | SUCCESS, 0/345, covers 4/4 | NETNINE |
| N2 | Control | corrupted output detected by count oracle | `[0;9]`, probe0, `v[8]=1` after sort | as N1 | FAILED as expected (network.rs:1005), covers 2/2 | NETNINE neg |
| N3 | Theorem (direct) — **not established** | N13 analogue of N1 | as N1 with N=13, function-item F | real `sort13_optimal`, zero insertions | TIMEOUT (600 s) | NETTHIRTEEN |
| N4 | Control | N13 count oracle sensitivity | `[0;13]`, `v[12]=1` | as N3 | FAILED as expected (network.rs:1055), covers 2/2 | NETTHIRTEEN neg |
| N5 | Theorem (PFC leaf) | `swap_net9` exchange summary on the real `swap_if_less` | T=u8, F=fnptr `U8Cmp`, CMP=`StrictU8::CMP`, full initialized backing9/offset0, independent probe, pair-only modifies | leaf, no stubs | SUCCESS, 0/388 (5 unr.), covers 7/7 | NETCOMP leaf9 |
| N6 | Diagnostic (direct, fnptr) — **gate not met** | N9 sortedness + count with fnptr F | as N5, whole entry | real body | SUCCESS 0/383 (22 unr.), covers **4/5** (one cover unreachable) | NETCOMP A9 |
| N7 | Actual binding | N9 entry sorted + count via exchange summaries | as N5, whole entry, full inputs | 25 raw `swap_if_less` → `adapter9` → sole u8/`U8Cmp` bridge → verified `swap_net9`; leaf = N5 | SUCCESS 0/588 (18 unr.), covers 6/6 | NETCOMP B9 |
| N8 | Control | wrong comparator rejected at the actual adapter; count oracle sensitivity | as N7 | as N7 | FAILED as expected (canonical guard netcomp.rs:122; count literal :242), covers 2/2 and 4/4 | NETCOMP controls |
| N9 | Diagnostic (direct, fnptr) — matching baseline | as N6, after a single cover move | as N6 (library `f4d3775dc5`) | real body | SUCCESS 0/383 (22 unr.), covers 4/4 | NETCOMP2 A9 |
| N10 | Actual binding | as N7 (re-run on new tree) | as N7 | as N7; leaf = **N5 reused from earlier Build** | SUCCESS 0/588, covers 6/6 | NETCOMP2 B9 |
| N11 | Theorem (PFC leaf) | `swap_net13` exchange summary | T=u8, fnptr, `StrictU8::CMP`, backing13/offset0 | leaf, no stubs | SUCCESS 0/388 (5 unr.), covers 7/7 | NETCOMP2 leaf13 |
| N12 | Actual binding | N13 entry sorted + count via exchange summaries | as N11, full `any [u8;13]` | 45 raw swaps → `adapter13` → verified `swap_net13`; leaf = N11 (same Build) | SUCCESS 0/588 (18 unr.), covers 6/6 | NETCOMP2 B13 |
| N13 | Control | count oracle (N9, N13) and wrong-cmp (N13) | concrete zero inputs; wrong-cmp reaches B13 adapter guard | as N10/N12 | FAILED as expected; single literals at netcomp.rs:242/:354/:459; covers 3/3, 2/2, 3/3; wrong-cmp9 **reused** from N8 | NETCOMP2 controls |
| N14 | Theorem (PFC leaf) | `swap_u64_net9` summary | T=u64, F=fnptr `U64Cmp`, `StrictU64::CMP`, backing9/offset0 | leaf, no stubs | SUCCESS 0/388, covers 7/7 | U64-N9 leaf |
| N15 | Actual binding | u64 N9 entry sorted + full-u64 count | full `any [u64;9]`, independent u64 probe (high-bit hit cover) | raw → `adapter_u64nine` → verified `swap_u64_net9`; leaf = N14 (same Build) | SUCCESS 0/588, covers 7/7 | U64-N9 B |
| N16 | Control | wrong-cmp guard; count control with same low 32 bits | `v[8]=1<<41`, probe `1<<40` | as N15 | FAILED as expected (:123 / :235 span), covers 2/2, 3/3 | U64-N9 controls |
| N17 | Theorem (PFC leaf) | `swap_u64_net13` summary | T=u64, fnptr, backing13/offset0 | leaf, no stubs | SUCCESS 0/388, covers 7/7 | U64-N13 leaf |
| N18 | Actual binding — **not established** | u64 N13 entry | full `any [u64;13]` | raw → `adapter_u64thirteen` → verified `swap_u64_net13` | TIMEOUT (600 s), no checks/covers | U64-N13 B13 |
| N19 | Theorem (PFC leaf) | `swap_net9` placed inside an 18-element backing (left half +0, right half +9): pair/order, active9 and whole-backing18 count, frame across the half boundary | T=u8, fnptr, `StrictU8::CMP`, unrestricted initialized `[u8;18]` | leaf, no stubs | both SUCCESS 0/409, covers 7/7 | NET18-LEAVES swap |
| N20 | Theorem (PFC leaf) — **not established** | `merge_profile::<StrictU8>` 18 → scratch32 prefix | source `[u8;18]` any, sorted halves via requires; dst `MaybeUninit<[u8;32]>` offset0; unwind34 | leaf | TIMEOUT (600 s) | NET18-LEAVES merge |
| N21a | Theorem (PFC leaf) | `up_step_u8` / `down_step_u8` contracts on real merge step helpers, incl. raw tuple = shared decoder | source `[u8;18]` any, i≠j<18; separate `MaybeUninit<[u8;32]>`, up k<32 / down 1≤k<32, init-mask any; probe any; unwind34 | leaf, no stubs | SUCCESS 0/534 covers 11/11; SUCCESS 0/546 covers 12/12 | MERGESTEP leaves |
| N21b | Actual binding — **not established** | `merge_profile::<StrictU8>` on source18[..4] → scratch32+0 via step summaries | as N21a | `merge_up`/`merge_down` → up/down adapters → verified step summaries | TIMEOUT (600 s) | MERGESTEP composed |
| N21c | Control (binding) — **gate not met** | each adapter guard fires inside its own adapter (interception of `inline(always)` helpers) | concrete | as N21b | FAILED on the intended literal only (:394, :415), but covers **2/4** and **3/4** vs declared 4/4 | MERGESTEP binding negatives |
| N21d | Control | count control runs the whole composed path on a concrete zero input | concrete | as N21b | FAILED on literal only (:576), covers 6/6 | MERGESTEP count negative |
| N21e | Theorem (direct) + Diagnostic baseline | same fixture/oracle as N21b with no stubs | identical fixture to N21b | real `bidirectional_merge`, `merge_up/down`, `panic_on_ord_violation` | SUCCESS 0/677 (67 unr.), covers 6/6 | DIRECTFOUR G2 |
| N22a | Theorem (PFC leaf) | `swap_net9` on prefix9 of backing10 (frame incl. `v[9]`) | T=u8, fnptr, `StrictU8::CMP`, any `[u8;10]`, base+0, independent probe | leaf, no stubs | SUCCESS 0/412, covers 8/8 | NETTEN-LEAVES swap |
| N22b | Theorem (PFC leaf) | `insert_tail_profile::<StrictU8>` begin0/tail9 within backing10 | probe set then any `[u8;10]`; sorted prefix9 only from `requires` | leaf, no stubs | SUCCESS 0/631 (48 unr.), covers 8/8 | NETTEN-LEAVES insert |
| N22c | Actual binding | u8 N10 entry sorted + full-value count via `swap_net9` + `insert_tail_profile` summaries | T=u8, F=fnptr `U8Cmp`, `StrictU8::CMP`, unrestricted any `[u8;10]`, exact initialized backing10/offset0; one shared independent probe (`ContextTen.probe` and `StrictU8::set_probe` set once before entry); prefix9 sortedness **asserted** before the insert (not assumed); no assume/any_where | `sort9_optimal` 25 raw swaps → `swap_adapter10` → verified `swap_net9`; insertion offset9: one raw `insert_tail(0,9)` → `insert_adapter10` → verified `insert_tail_profile`; leaves = N22a/N22b from **earlier Build** `f6fdbf06` (historical cross-Build) | SUCCESS 0/1106 (62 unr.), covers 8/8 | NETTEN-CALLER positive |
| N22d | Control | binding guards inside both actual adapters; full-value count oracle on the composed N10 route | concrete inputs | as N22c | all FAILED as expected, single literals: swap binding caller.rs:101 (covers 1/1), insert binding :162 after 25 swaps and all insert premises (1/1), count :320 span / literal :322, count(0) 10→9 (2/2) | NETTEN-CALLER controls |

## 3. Identities, provenance and resources

RESULT permalinks (commit that last wrote the file = branch tip in every case, content re-checked):

[R-BRIDGE]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b7761aa50afdc2ff60a78b643397b4a765fc343f/research/challenge-8/kani-k1/RESULT-BRIDGE.md
[R-BRIDGENINE]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/8cbb26750012c51d99266fa9fbe342519345649d/research/challenge-8/kani-k1/RESULT-BRIDGENINE.md
[R-WONE]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/1c107cb12a2d214f9e8745192bc19d2d3e6df638/research/challenge-8/kani-k1/RESULT-WONE.md
[R-WONEDIAG]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b7a8db4a987c5475d371d2986eb1728e5b0a3148/research/challenge-8/kani-k1/RESULT-WONEDIAG.md
[R-WONETWO]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b21be6cd8639ba779b9badea989abe3a3e4a2c91/research/challenge-8/kani-k1/RESULT-WONETWO.md
[R-NETNINE]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/dfaba49ddcc409a04240b75908ebe25a535d19a4/research/challenge-8/kani-k1/RESULT-NETNINE.md
[R-NETTHIRTEEN]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/23751ff775363b137b3172fbd2b2abcb17309d37/research/challenge-8/kani-k1/RESULT-NETTHIRTEEN.md
[R-NETCOMP]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/763b098cd081bc8940e82a422add81ab5c2938f6/research/challenge-8/kani-k1/RESULT-NETCOMP.md
[R-NETCOMP2]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/58d464ce1ce3d3ad7e60325e3297fdf07d38db4c/research/challenge-8/kani-k1/RESULT-NETCOMP2.md
[R-U64-N9]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/9ab925b1578b9102e3009c0ec940c5c9cc0280cb/research/challenge-8/kani-k1/RESULT-U64-N9.md
[R-U64-N13]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/4b9d56c46d1be97ba981610fb0dea77e0c864f66/research/challenge-8/kani-k1/RESULT-U64-N13.md
[R-NET18]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/7d8b21728b1ccb632d67374918bd13d2c45de116/research/challenge-8/kani-k1/RESULT-NET18-LEAVES.md
[R-MERGESTEP]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/97a252bea7ee68720b097ecf83d014e0b87d5f20/research/challenge-8/kani-k1/RESULT-MERGESTEP.md
[R-DIRECTFOUR]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/e3a778017a0e057b34d6ea910fcca9d21f7dc3a3/research/challenge-8/kani-k1/RESULT-DIRECTFOUR.md
[R-NETTEN]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/9835bd00dc4bf386e68e5f7885964a17d0dda240/research/challenge-8/kani-k1/RESULT-NETTEN-LEAVES.md
[R-NETTEN-CALLER]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/61cfba69c3dac0b87324d2845c1164e08222d0a6/research/challenge-8/kani-k1/RESULT-NETTEN-CALLER.md

| IDs | Library commit / tree | Build UUID | RESULT | Reuse provenance | VT s (row) | CBMC RSS KiB (row) |
|---|---|---|---|---|---|---|
| M1–M4 | `b07dc219a27af35e9832335c129bb8759926b7ca` / `f3bf04b5cc` | `642e7d4e-60e8-429b-8aed-1817ecd233d9` | [R-BRIDGE] | none | M1 24.66; M2 2.86; M3 0.90/0.78; M4 11.22/20.02 | sampled peak 0.51 GiB (whole run); compiler 1.72 GiB |
| M5–M8 | `77cb4c97733d24c1f03f11dc803a2a7676bfc4d5` / `b903aba7c3` | `b457683e-137b-485b-96a2-6d6fcf54e217` | [R-BRIDGENINE] | none (no transfer from M1's N3 domain) | M5 154.86; M6 25.56; M7 217.60; M8 19.98 | M5 1323280; M6 347688; M7 426800; M8 350956 |
| W1–W3 | `e4f1df6a348fe67277250f84e5a6aa83638a7892` / `1731596d7c` | `19e85ac8-ab3d-4e47-9fe7-a73547326ae0` | [R-WONE] | none | W1 147.90; W2 UNKNOWN; W3 0.22/3.61 | W1 968156; W2 2101724 / 15585836 / 15679436 (OOM) |
| W4 | `af8b0db75a78f737772c8fe86ed7d5cdff109e11` / `af3da15225` | `b9e00fd2-b4a6-42fa-986b-f74db31a2f12` | [R-WONEDIAG] | none; W3 controls not rerun | 59.78 / 272.54 / 286.15 | 416160 / 1161416 / 1156924 |
| W5 | `4231462d124b8c69bfaa55dd0eb956717308f1be` / `c407b96a8c` | `84ff0a05-c37c-4628-8675-28241997093d` | [R-WONETWO] | N3/cell rows in its table are copied from W1/W4, not rerun | 31.01 / 193.37 / 181.04 | 227280 / 814568 / 808972 |
| N1–N2 | `24d9f1d3d8f1ff03f2c3dbe891d1e8f6f30a4d13` / `ac095c9d7b` | `15e9cc87-6e89-4b44-b839-e43161af6a31` | [R-NETNINE] | none | 261.05 / 7.94 | 265272 / 199624 |
| N3–N4 | `d60b2c975d18ef8f69234f0269c5cf89faa2fa24` / `a618a0bdce` | `beefc7a4-f532-4bc2-ac48-42b393cb42eb` | [R-NETTHIRTEEN] | none | UNKNOWN (>600) / 16.03 | 462300 (at timeout) / 345172 |
| N5–N8 | `47ed440a23641545fba1eedd279a0ebabe6edf02` / `f9fa2945d6` | `b3e257d1-eaf9-4323-a8f1-f4648798cbd9` | [R-NETCOMP] | none | N5 49.67; N6 260.72; N7 111.43; N8 0.53/67.80 | 314920; 275776; 988628; UNKNOWN/971680 |
| N9–N13 | `f4d3775dc505ef26e30158cfa7e78f120cd3c30e` / `3b6d2a51da` | `44af7732-80e7-4cc3-b3ec-26f5af0d2d40` | [R-NETCOMP2] | **N10 depends on leaf N5 and N13 includes wrong-cmp9, both from Build `b3e257d1` (library `47ed440a23`)**; equivalence argued by a static source comparison (only one cover moved), not by re-running | N9 242.87; N10 93.44; N11 52.95; N12 268.84; N13 59.14/0.55/138.29 | 275236; 989648; 334712; 2156824; 945832/UNKNOWN/1907928 |
| N14–N16 | `fddf308321046a8cd8f5526622a5e2353d79830e` / `d22566ab5a` | `62bb5025-ed9a-4116-a868-610c993af026` | [R-U64-N9] | none (leaf and B in same Build) | 76.42; 148.29; 0.77/82.19 | 359428; 1345528; UNKNOWN/1004240 |
| N17–N18 | `497077c6cd14fdbcc439807c0cdc186860cb00ce` / `90a3889318` | `f11489dc-97ed-4470-8ed1-d782ea1f8a0f` | [R-U64-N13] | none | 180.08; UNKNOWN (>600); controls 1.03/169.43 | 411696; 3390464 (at timeout); UNKNOWN/2032700 |
| N19–N20 | `4eb7e81259f843da6517a8de97c68e23b584eb76` / `1fa41b3a5f` | `b05d30cc-f789-4946-b0c7-e1cbad944aae` | [R-NET18] | none | 63.21 / 71.62; UNKNOWN (>600) | 388296 / 354188; 3245732 (sampled, time-bound) |
| N21a–d | `91d4d9f77a5a6e7f27b151839e6ac42114523a89` / `dc7c79bb9b` | `1e9c0ac0-ce89-498f-bc5b-d25c70af2279` | [R-MERGESTEP] | none | 68.25 / 61.10; UNKNOWN (>600); 1.05 / 2.95 / 20.12 | 440604 / 407980; 2607368; UNKNOWN×2 / 242468 |
| N21e | `248b2725c6cd528a6d87aa5928e362dc11e74522` / `7996f9c151` | `9a000cec-dbd7-4b81-ab81-54da258f9d83` (earlier `37d72ac9-af24-4969-8754-e1e01ef6be88`: compile error, row NOT_RUN) | [R-DIRECTFOUR] | none | 207.98 | 894860 |
| N22a–b | `23ba8cfddbce1cf0313ab402fd6376d157a0f845` / `74e42aaa19` | `f6fdbf06-58fa-4c1d-9692-c8236cc38892` | [R-NETTEN] | none | 77.11 / 59.59 | 355216 / 1013808 |
| N22c–d | `2ebda13e1445186f53a12b69a4419aafe4f17e1b` / `40d3b22c82` (GO for `d6947d4767`) | `ea3fee3a-98aa-47f2-aa6e-d13c5cb546a0` | [R-NETTEN-CALLER] | **leaves N22a/N22b reused from Build `f6fdbf06`** (source `1914e42274`, dependencies byte-identical per reuse-dependencies.md), historical cross-Build; VT(B10)+77.10969+59.589855 = 469.628505 s is a **mixed-run estimate only**, no direct A10, no speedup claim | N22c 332.93; N22d 1.90 / 123.02 / 267.90 | 2362004; 39772 (1 sample, hint-only) / 1344460 / 2077184; compiler VmHWM 2376040; kani-driver VmHWM 14781664 (≈14.10 GiB, near 16 GB); process-sum 14.11 GiB |

## 4. Stage gates (overall acceptance per Build)

| Build | Gate | Why |
|---|---|---|
| `642e7d4e` (B1 merge smoke, N3) | accepted (SUCCESS) | all six rows met expectations; M4 positive covers 2/5 accepted with a recorded cover limitation |
| `b457683e` (stable u8 N9) | PASS | all four rows met expectations |
| `19e85ac8` (wrappers N0..3) | FAIL / PARTIAL | 1/4 PFC SUCCESS; two TIMEOUT, one OOM |
| `b9e00fd2` (wrappers N3) | PASS | 3/3 |
| `84ff0a05` (wrappers N2) | PASS | 3/3 |
| `15e9cc87` (direct u8 N9, function-item F) | PASS | 2/2 |
| `beefc7a4` (direct u8 N13, function-item F) | FAIL | positive TIMEOUT |
| `b3e257d1` (u8 N9 composition calibration) | FAIL / PARTIAL | direct baseline covers 4/5; no cover waived |
| `44af7732` (u8 N9 recalibration + N13 composition) | PASS | all seven rows met expectations (with two reused historical rows outside this Build) |
| `62bb5025` (u64 N9) | PASS | 4/4 |
| `f11489dc` (u64 N13) | FAIL / PARTIAL | composed B13 TIMEOUT |
| `b05d30cc` (N18 leaves) | FAIL / PARTIAL | merge18 leaf TIMEOUT |
| `1e9c0ac0` (merge step) | FAIL | composed merge4 TIMEOUT; binding controls missed declared covers (2/4, 3/4) |
| `9a000cec` (direct merge4) | PASS | 1/1, covers 6/6 |
| `f6fdbf06` (N10 leaves) | PASS | 2/2 |
| `ea3fee3a` (actual u8 N10 composition) | PASS | positive SUCCESS 8/8; controls only designated literals, covers 1/1, 1/1, 2/2 (leaves from `f6fdbf06`, cross-Build) |

### 4.1 Totals (recounted after adding N22c result and N22d)

- Claim rows: 43 (L-M 8, L-W 6, L-N 29 = N1–N20, N21a–e, N22a–d).
- Rows marked **not established** / **gate not met**: 7 (W2, N3, N18, N20, N21b not established; N6, N21c gate not met).
  Pending rows: 0 (was 1: N22c). Remaining 36 rows carry their recorded status on their own commit only.
- Recorded Builds in §4: 16; PASS/accepted 10 (`642e7d4e`, `b457683e`, `b9e00fd2`, `84ff0a05`, `15e9cc87`,
  `44af7732`, `62bb5025`, `9a000cec`, `f6fdbf06`, `ea3fee3a`); FAIL/PARTIAL 6 (`19e85ac8`, `beefc7a4`, `b3e257d1`,
  `f11489dc`, `b05d30cc`, `1e9c0ac0`).
- Actual-route compositions with matching leaves: same-Build 5 (M2+M1, M6+M5, N12+N11, N15+N14; N7+N5 inside the
  FAIL/PARTIAL calibration Build `b3e257d1`);
  with cross-Build leaves 2 (N10 ← N5 from `b3e257d1`; N22c ← N22a/b from `f6fdbf06`).

## 5. What the opt-in evidence establishes (and what it does not)

Established, each only on its exact domain and its own commit:

1. **Stable u8 N9 (L-M):** the actual stable small-sort entry at N9 (fnptr F, `LtU8` key comparator, scratch48) sorts by
   key and preserves the full-value count, both by a direct real-body proof (M7) and by an actual-route composition
   through a verified merge summary with a matching leaf in the same Build (M5+M6). Payload-flip control (M8) shows the
   oracle is not key-only.
2. **Unstable u8 N9 and N13 (L-N):** actual-route composition through verified exchange summaries with matching
   independent leaves (N7/N10 with N5; N12 with N11). N13 composition is the only N13 whole-entry result on record;
   the direct N13 proof with function-item F timed out (N3).
3. **Unstable u64 N9:** actual-route composition with matching leaf in one Build (N14+N15).
4. **Leaf theorems without a whole-entry result:** u64 N13 exchange leaf (N17); `swap_net9` at backing18 offsets 0/9 (N19);
   merge step helpers (N21a). These are building blocks only; they are not whole-network theorems.
4a. **Unstable u8 N10 (L-N):** actual-route composition (N22c) through `swap_net9` prefix9/backing10 and
   `insert_tail_profile` begin0/tail9 summaries with matching leaves N22a/b, but the leaves come from an earlier Build
   (`f6fdbf06`), so this is a historical cross-Build pairing; controls N22d met.
5. **Direct theorems:** u8 N9 with function-item F (N1); merge4 fixture with no stubs (N21e); length wrappers
   (W1 N0..3 cell; W4 N3; W5 N2).
6. **Binding mechanism facts:** on this Kani pin, `stub` to a closed adapter plus `stub_verified` of the summary
   intercepts the raw helpers on the actual route (M2, M6, N7/N10/N12/N15; adapter guards fire in N8/N13/N16/N21c),
   including `inline(always)` merge step helpers (N21c, binding observed even though the control gate failed).

Performance statements that are supported:

- **Stable u8 N9, same Build, matching F/domain:** VT(M6)+VT(M5) = 180.42 s vs direct M7 = 217.60 s (17.09 % less),
  while CBMC peak memory is 3.10× higher (1323280 vs 426800 KiB). One run; no broader speedup claim.
- **Unstable u8 N9:** the only matching direct baseline with full covers is N9 (fnptr). Composed B9 alone is 93.44 s vs
  242.87 s; including the leaf is a **mixed-run estimate** (leaf from an earlier Build: 143.11 s, 41.08 % less), not a
  same-build measurement; memory ≈3.6× higher. The earlier 38.2 % figure (N5+N7 vs N6) was observed under a failed
  calibration gate and is not an accepted measurement.
- **No speedup claim** for u8 N13 (direct baseline uses function-item F and timed out), u64 N9/N13 (no direct u64
  baseline), merge4 (composed side timed out; the direct side succeeded in 208 s, so the composition bundle as a whole
  is the slower formulation on that fixture, with the cause not separated).

## 6. Opt-in status and what Part 2 would need

All rows above live under `cfg(kani_smallsort_controls)`. They do not change and are not counted in either
ordinary harness set:

- the **Part 1 v6 ordinary set (202 harnesses)**, and
- the **research-branch ordinary set (exact 200)**, which every Build here verified statically as unchanged
  (the cfg-on inventory grew only by opt-in names, per lineage: e.g. 382 at the shared cleanup base, 391 at the
  stable N9 tip, 394 at the N2 wrapper tip, 405 at the merge4 tip). Static counts are not proofs.

These two sets are different trees and must not be combined or cross-credited.

For Part 2 credit, each claim would need to be moved onto the Part 2 tree and re-verified there in an exact-tree CI run:

1. Port the targets, contracts, adapters/bridges, and roots from their own lineage commit; the three lineages are
   independent and would have to be integrated deliberately (no single existing commit contains all three).
2. Re-run every leaf and its consumer in the **same** CI run on the **same** tree; cross-Build leaf reuse
   (N10/N13 ← Build `b3e257d1`; N22c ← `f6fdbf06`) is not acceptable for a final record.
3. Decide whether these harnesses run under the ordinary profile (no `kani_smallsort_controls`) or stay opt-in;
   controls must stay out of the ordinary set because they are expected failures.
4. Fit within the CI resource envelope: several successful rows need ~1–2.1 GiB CBMC and 200–290 s on 4 CPU/16 GiB;
   rows that timed out here (N3, N18, N20, N21b, W2) are not available for Part 2 without reformulation.
5. Re-check with uninit detection on, if that is part of the Part 2 profile (all evidence here ran with it off).

## 7. Open limitations (keep in any external text)

- **Bounded domains only:** fixed N (2, 3, 9, 10, 13, 18, merge4), fixed backings and offsets (mostly offset 0; wrappers
  offset 1), fixed scratch sizes (3, 32, 48). No claim for other N (in particular N16/N32/full small-sort range),
  backings, offsets, or scratch geometries.
- **Comparator form:** all compositions use a reified **function-pointer** F (`fn(&T,&T)->bool`) with one canonical
  value per type; the bridges have no blanket impl. No claim for generic `T`, generic `F: FnMut`, closures, or the
  actual **function-item** comparator type; transfer from fnptr results to function-item F is not established
  (N1/N3 are the only function-item rows and they are direct proofs).
- **Types:** u8 and u64 (L-N), u8 with key comparator (L-M), `Cell<u8>`/`NonCopyU8`/u8 (L-W). No trait-level PFC.
- **Semantics not covered:** tie stability (beyond what key sortedness implies), initialization detection (uninit
  checks off), full alias-validity, unwinding/panic behavior beyond unwinding assertions, comparator panics.
- **Coverage notes:** several rows report unreachable checks (up to 71) that the terse output does not itemize.
  M4 positive has 2/5 covers with per-cover identities unknown. N21c binding controls missed declared covers
  because a failed `kani::assert` cuts the path (inferred; covers not named in the log).
- **Not established:** N13 direct (function-item F), u64 N13 whole entry, merge18 leaf, actual N18 composition,
  composed merge4, wrappers N0..3 for three of four types. N10 composition (N22c) exists only with cross-Build leaves;
  no direct N10 baseline and no N10 speedup claim (469.628505 s is a mixed-run estimate).
- **Resource dependence:** VT/RSS are single-run numbers on one machine type; jobs1; sampled RSS can miss short CBMC
  processes (several UNKNOWN).

## 8. Source inconsistencies / items needing review

1. **M4 positive covers 2/5** with SUCCESS: accepted at the time with a recorded limitation; should not be presented as
   full-cover evidence.
2. **NETCOMP → NETCOMP2 cover totals changed** (A9 5→4, count-negative9 4/4→3/3) because one cover was moved between
   source commits `47ed440a23` and `f4d3775dc5`; the earlier PARTIAL remains the historical record.
3. **Cross-Build reuse in NETCOMP2:** leaf9 and wrong-cmp9 come from Build `b3e257d1` on a different library tree;
   equivalence is by static comparison only. The NETCOMP2 gate PASS includes these rows.
4. **u64 N9 dispatch alias:** dispatched via an alias branch with the same SHA (digit-free slug); NET18 also used an alias.
   Identity match is recorded, but the Build's branch name differs from the RESULT branch.
5. **Library tree in RESULT text** is the `library/` subtree hash, not the commit root tree; verified for all rows.
6. **NETTEN-CALLER**: resolved in this copy — RESULT @`61cfba69c3`, Build `ea3fee3a` PASS (N22c/N22d). Its leaves
   remain from Build `f6fdbf06` (cross-Build, historical).
