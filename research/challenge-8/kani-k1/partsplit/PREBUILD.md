# PART2-SPLIT31 PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO (G1). No dispatch before exact-packet GO; G2 gets its own PRE-BUILD REVIEW.
Runtime Claude Code; owner **k1-network**; branch `experiment/kani-k1-partsplit-20261102`; task `TASK-PART2-SPLIT31.md` (eb577e75bd).
Base MACSPLIT `4f4034527d3e3a26e4cd94e12ba6922e2b5e80e4`, library tree `d4ec476a7a001363e58f19948c188a9c2078e370`.
Library commit `b2a13747dae7458dd825f78a1d32e2ffed0b568b`; candidate library tree `05eb97eaef01dc4015e659d46256b2d910750d58`
(frozen for G1 and G2). Review SHA = published research commit reported with PRE-BUILD REVIEW.
T0 conservatively 2026-11-02T18:15Z: main deadline 21:15Z, closeout 21:45Z.

## Diff (library, only `verify/network.rs`, +4/−0)

After the unchanged `#[cfg(kani_smallsort_controls)] dispatch_pair_safety_cases!(dispatch_safety_stable_unstable_bytes17_n31, [u8; 17], [31]);`:
```
#[cfg(kani_smallsort_controls)]
dispatch_safety_cases!(dispatch_safety_stable_bytes17_n31, [u8; 17], true, [31]);
#[cfg(kani_smallsort_controls)]
dispatch_safety_cases!(dispatch_safety_unstable_bytes17_n31, [u8; 17], false, [31]);
```
No macro/helper/`dispatch_safety_fixed`/runtime change; runtime `smallsort.rs` byte-identical; no stubs/contracts/assumptions added.

## Domain union

Old pair: `len = any_where(len ∈ {31})`, `stable: bool = any()`; `stable` → `dispatch_safety_fixed::<[u8;17],31,true>()`,
else `::<[u8;17],31,false>()`. The fixed body draws its own input (`array::from_fn(|_| kani::any())`, 31 initialized
`[u8;17]`, all 17 bytes full-any, local array → offset 0), independent of `stable`. New Stable root = pair restricted to
`stable=true`, new Unstable root = pair restricted to `stable=false`; same input/comparator domain each. Union = old domain;
the `_ => {}` arm is unreachable in all three. Covers are the only post-match statements and add no assertions.
Both macros carry identical `#[kani::stub(panic_on_ord_violation, assume_order_violation)]` and `#[kani::unwind(65)]`
(unwinding assertions from the lane, unchanged); safety scope = normal return with panic cut, no sort/permutation/drop claim.

## Dispatch map for `[u8; 17]` (smallsort.rs, unchanged)

`[u8;17]` is Freeze + Copy, size 17 > 8 ⇒ `has_efficient_in_place_swap` false; 17×48 = 816 ≤ MAX_STACK_ARRAY_SIZE 4096.
- Stable: `impl<T: FreezeMarker> StableSmallSortTypeImpl` → `small_sort_general_with_scratch(v, scratch, is_less)`
  with harness scratch exact 48 `MaybeUninit<[u8;17]>` (48 ≥ 31+16).
- Unstable: `UnstableSmallSortTypeImpl` (Freeze) → `UnstableSmallSortFreezeTypeImpl` (Freeze+Copy specialization) →
  not network (swap check false) → `small_sort_general` (internal stack scratch 48) → `small_sort_general_with_scratch`.
Unstable case is the general route, not network despite module name. Dispatch is the actual trait entry, not a direct call.
F = inferred function item `volatile_reading_less::<[u8;17]>` (`&mut` to fn item, not fn-pointer coercion, not ordered):
volatile reads of both arguments, returns `kani::any()` bool.

## Roots / annotations / covers

| Root (network::) | Gate | Stub / unwind | Required covers |
|---|---|---|---|
| dispatch_safety_stable_bytes17_n31 (new) | controls | assume_order_violation / 65 | 2/2: "dispatch route returns normally at 31", "dispatch safety family reached the end" |
| dispatch_safety_unstable_bytes17_n31 (new) | controls | same | 2/2: same two |
| dispatch_safety_stable_unstable_bytes17_n31 (old, unchanged) | controls | same | 3/3: stable return 31, unstable return 31, "dispatch family reached the end" |

## Static evidence (`partsplit/static_check.py`, report `static-check-prebuild.json`; source forecast, not native inventory)

- Ordinary 202 → 202, added/removed none; set-equal to native MACSPLIT reference `macsplit/ordinary-expected.txt`.
- cfg-on 384 → 386, exact delta +2 = the two new names, removed none; opt-in 182 → 184. New roots gated only by controls.
- PFC 36 unchanged (diff adds only `#[kani::proof]` roots); `pfc_order.py`: 16 sites, bad 0 (`pfc-order.txt`).
- N32 split roots and all ordinary bodies/annotations untouched (library diff is the 4 lines above).
- rustfmt wrapper `--check --edition 2024` exit 0; `git diff --check` clean; ≤100 columns (`rustfmt-check.txt`).
- Lane files (.circleci, workflows, kani-k1/tools, gcb, run-kani.sh, kani-version.toml, rust-toolchain, .cargo, Cargo.*) equal
  tooling `30f77e859903df14b442ff9294d4fbbd44827f20`; Kani `9461e07af7ec929f050aa4192f29363c9be07779`; nightly-2026-10-12.
- No local cargo/rustc/Kani/CBMC; competing PR code not opened.

## Requests (measurement, gcb-e2-standard-4 → k1-standard4, controls true, kani_jobs 1, uninit_checks false, 10 min/row)

| Pkg | request_id | Rows | SHA-256 | Envelope / reserve |
|---|---|---|---|---|
| G1 | partsplit-g1-measure-bytes17-n31-split-20261102 | stable_bytes17_n31, unstable_bytes17_n31 | 57bf18242dce756a64ab3eea605efc9424f986cf588add2b1fea447962e50b22 | 50 min / $0.675 |
| G2 | partsplit-g2-measure-bytes17-n31-pair-20261102 | stable_unstable_bytes17_n31 | 2b516f70c703c7e6d3ee02ac3b47f7cb61e1ac6ceb968d9f3aa9ced0b7e74ec6 | 40 min / $0.540 |

`RUN-REQUEST.json` = `partsplit/g1.request.json`; both pass `kani_k1.py validate --require-runner gcb-e2-standard-4`.

## Budget / slots / window (`budget-prebuild.txt`)

Project used $80.3085 + reserved $0.675 (one unfinished 50-min build, attributed by coordinator note to k1-merge PARTTWO-TREE);
cap $88.96, headroom $7.9765. Own: 0 builds, $0 spent/reserved; G1+G2 $1.215, all four $2.430 ≤ $2.50.
Slots: project 1 unfinished < 2; k1-network 0 unfinished. Re-check budget/slots immediately before each dispatch.
G1 50 min then G2 40 min sequential fit before 21:15Z if G1 GO arrives by ~19:35Z; otherwise G2 is NOT_RUN by window.

## After GO

Dispatch G1 from the reviewed SHA; `k1g.sh wait UUID` in background. Read bounded summary/peaks, check-tooling vs 30f77e85.
Then switch RUN-REQUEST.json to g2.request.json (library tree unchanged), new PRE-BUILD REVIEW, await GO for G2.
