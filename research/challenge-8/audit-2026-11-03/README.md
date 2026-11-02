# SmallSort (verify-rust-std Challenge 8): audit report

**Evidence cutoff:** 2026-11-02T20:23Z (UTC). Records published after this time are not used.
**Scope:** a self-contained description of what the public SmallSort sources and published run records of the
`Tiramisu-Cake/verify-rust-std` fork establish, what they do not establish, and how to check every statement
against code without credentials. This package was produced without running any compiler, Kani, proof or CI job.

**This report does not claim that Challenge 8 is solved.** All results are bounded (fixed lengths, types,
comparators and memory layouts), and several Challenge requirements are open (Sections 1, 5 and 7).

Package contents (all next to this file):

| File | Content |
|---|---|
| [snapshots.tsv](snapshots.tsv) | every source snapshot used: role, full commit, `library/` tree, source/evidence URLs, inventory/proof/CI status |
| [harnesses.tsv](harnesses.tsv) | 453 harness rows: Part 1 v6 ordinary 202 and opt-in 182, the 54 roots added on the integrated tree, and the SPLIT31, U64-TEN-CALLER and PART2-FAST subsets on their own pins |
| [claims.tsv](claims.tsv) | 64 claim records: property, T/F/CMP, domain, raw → adapter → summary route, leaf/consumer, status, assurance, Build, result URL, code lines |
| [findings.tsv](findings.tsv) | F01–F11 and A1–A4: neutral definition, status at the v4 baseline and now, links, remaining scope |
| [resources.tsv](resources.tsv) | per-row verification time (VT) and process-specific memory, with missing fields marked |
| [check_audit_report.py](check_audit_report.py) | offline static checker (Python standard library + Git) |

## 0. Identities and vocabulary

Three different library snapshots matter. They are never combined into one proof suite in this report.

| Snapshot | Commit | `library/` tree | What it is |
|---|---|---|---|
| Part 1 v6 (`P1-V6`) | `d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097` | `d4ec476a7a001363e58f19948c188a9c2078e370` | the Part 1 submission head; one commit on upstream `c0bd09c354a50bf9fe4dcc7cc5f9c34503658479` |
| Integrated research candidate (`INTEGRATED`) | `2756f0e2a6ae0956fdb427574eda39b5b9a76e64` | `a45388ac593c809405558ea0c27599f487b17e4e` | v6 plus 54 opt-in research roots; **not** the organizer-CI-verified v6 head |
| v4 baseline (`V4-BASELINE`) | `f0ba14f97b3adea21c1c9671db6245afe7a15887` | `3c23a45984f0f7cc5e43150a566b09fb1937e7c0` | Part 1 v4, used only for the delta in Section 5 |

This documentation branch starts at `6ff24c756c28f56fcac9c0bcb6551bf692bde7d1` (the terminal inventory report of
the integrated tree), so the `library/` directory of the branch holding this file is the **integrated research
candidate**, not Part 1 v6. Every code link below names the commit it refers to. Git tree IDs appear only as
identities; they are never used as the ref of a URL. Further snapshots (separate trees for SPLIT31,
U64-TEN-CALLER, research lineages) are in [snapshots.tsv](snapshots.tsv) and [claims.tsv](claims.tsv).

Vocabulary used throughout:

- **Safety**: no failure of Kani's default checks (pointer bounds/dereference, arithmetic overflow, intrinsic
  preconditions, assertions in library code) on the executed paths. **Order**: the output is sorted under the
  comparator or under a stated model key (often `x >> 1`, so distinct values can tie). **Permutation**: for an
  independent, unconstrained probe value, the number of elements equal to the probe (full logical value, not only
  the key) is unchanged; this is the "full-value count". **Frame**: memory outside the stated write set is
  unchanged.
- **Normal return vs panic/unwind**: most safety harnesses replace `panic_on_ord_violation` by a manual stub that
  aborts, assumes `false` or cuts the path. Their results describe executions that return normally; nothing is
  claimed about panics or unwinding.
- **PFC**: a `#[kani::proof_for_contract(f)]` harness checks the contract of `f` (requires/ensures/modifies) on the
  inputs the harness constructs. **Actual-entry proof**: a plain `#[kani::proof]` that calls a real trait entry or
  helper and asserts properties after it returns.
- **Verified summary / matching leaf**: a consumer harness may replace a callee by its contract via
  `#[kani::stub_verified]`. Such a result counts as a composition only if a separate **leaf** PFC proves that
  contract on the real body for exactly the consumer's domain (type, comparator value, model, probe, length,
  backing, offset, initialization). Some records call the bridge forms "B1"/"B2"; those are architecture names,
  not assurance levels.
- **Same-Build vs cross-Build**: a leaf and its consumer run in the same Cloud Build on the same tree, or in
  different Builds (possibly different trees). Cross-Build pairings are reported as historical evidence only.
- **Inventory**: the name list printed by `kani list`; it shows compilation and harness membership, not proofs.
- **Status words**: SUCCESS/FAILED/TIMEOUT/OUT_OF_MEMORY are per-harness verifier outcomes as recorded;
  PASS/PARTIAL/FAIL are stage gates of a whole Build as recorded; OPEN = not established and not scheduled;
  NOT_RUN = no run on that tree; PENDING = run in progress without a terminal published result; UNKNOWN = the
  value is not in any record used here. A timeout is a resource cap, never a counterexample.

## 1. What Challenge 8 requires and how the code is organized

The Challenge text was read at upstream commit `c0bd09c354` ([0008-smallsort.md][ch8]). It asks to prove absence
of undefined behaviour for seven functions ([lines 19–27][ch8-ub]): the `small_sort` methods of
`StableSmallSortTypeImpl`, `UnstableSmallSortTypeImpl` and `UnstableSmallSortFreezeTypeImpl`, and
`swap_if_less`, `insertion_sort_shift_left`, `sort4_stable`, `has_efficient_in_place_swap`; to write contracts
for the three `small_sort` methods showing that they sort ([line 29][ch8-contracts]); and to verify both "for all
possible slices with arbitrary valid length" ([line 36][ch8-all]). Proofs must automatically exclude, among
others, reads of uninitialized memory and production of invalid values ([lines 41–50][ch8-list]), and follow
the general challenge rules ([line 52][ch8-rules]).

Actual dispatch at Part 1 v6 ([smallsort.rs][ss]; the runtime file differs from upstream only by a
`#[cfg(kani)] mod verify;` registration at [line 866][ss-mod]):

| Entry | Element types | Route |
|---|---|---|
| Stable, blanket impl ([line 38][ss-38]) | any `T` | `insertion_sort_shift_left(v, 1)`; threshold 16 |
| Stable, `T: FreezeMarker` ([line 56][ss-56]) | Freeze | `small_sort_general_with_scratch` with caller scratch; threshold 32 |
| Unstable, blanket ([line 82][ss-82]) | any `T` | `small_sort_fallback` (insertion) |
| Unstable, `T: FreezeMarker` ([line 97][ss-97]) | Freeze | forwards to `UnstableSmallSortFreezeTypeImpl` |
| Freeze, default ([line 124][ss-124]) | Freeze, not `Copy` | `small_sort_general` (own 48-slot stack scratch) if it fits the stack limit, else fallback |
| Freeze, `Freeze + Copy` ([line 157][ss-157]) | Freeze + Copy | `small_sort_network` if `has_efficient_in_place_swap` (size ≤ 8) and fits, else general, else fallback |

Helpers on these routes: `swap_if_less` ([380][ss-380]), `sort9_optimal`/`sort13_optimal` ([420][ss-420],
[469][ss-469]), `insert_tail` ([536][ss-536]), `insertion_sort_shift_left` ([574][ss-574]), `sort4_stable`
([606][ss-606]), `bidirectional_merge` ([754][ss-754]); general scratch length 48 = 32 + 16 ([188][ss-188]).

**Bounded Kani approach.** Each harness fixes a finite set of lengths and a concrete element type, builds inputs
with `kani::any()`, chooses a concrete comparator (a function item, a reified function pointer, a mutating or a
fully arbitrary comparator), and bounds loops by `#[kani::unwind]`. The ordinary set runs with the organizer
flags, including `--no-assert-contracts` (contracts are checked only in PFC targets). The three trait methods
have no requires/ensures; correctness of the entries is stated by harness assertions and, for N2, by three
forwarding-wrapper contracts ([verify.rs:20–31][verify-doc]).

## 2. Part 1 v6 (ordinary set)

- **Identity.** Commit `d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097`, library tree
  `d4ec476a7a001363e58f19948c188a9c2078e370`; 13 files changed relative to `c0bd09c354`: 11 verification files (`verify.rs` and 10 under `verify/`), a
  `check-cfg` entry in `library/core/Cargo.toml` and the registration in `smallsort.rs`.
- **Organizer CI.** [Run 41404150041][ci6]: workflow `Kani`, `workflow_dispatch`, attempt 1, `head_sha` = v6, all
  16 jobs concluded `success` (queried from the GitHub API at cutoff). Autoharness jobs: Ubuntu
  (`125142276276`, 07:06:42–08:35:47Z) and macOS (`125142276438`, 07:06:48–09:23:06Z). The public domain registry
  bound to v6 records that both autoharness jobs report all 202 ordinary SmallSort harnesses SUCCESSFUL
  ([registry][dom]); this report did not re-read the job logs. **Per-harness times and satisfied-cover counts for
  v6 are UNKNOWN here** (they exist only in run artifacts, not in a bounded published record); cover totals of
  earlier versions are not carried over.
- **Native inventory.** The ordinary name set of this library tree was obtained natively by MACSPLIT G1
  (`cbce904f-449c-4fe7-bb75-c14b1f70fbec`, exact 202) ([RESULT-MACSPLIT][r-macsplit]); the cfg-on set of 384 for v6
  is static only.
- **Composition of the 202** (from the integration manifest; per-row data in [harnesses.tsv](harnesses.tsv)):

| Group | Roots | Property |
|---|---:|---|
| PFC: `swap_profile` 14, `sort4_profile` 2, `insert_tail_profile` 5, `merge_profile` 12, wrappers 3 | 36 | contract on the executed domain (see below) |
| Direct general/stable entries (u8 N0..9, u64 N0..9) | 25 | key order + full-value count |
| Fallback insertion (u8/u64 N0..6) | 7 | key order + full-value count |
| Network entry correctness (u8 N0..7, 9..13; u64 N0..7, 9) | 16 | order; full-value count only for N < 9 |
| Insertion-suffix permutation (u8 N10, 11, 14; u64 N10, 14) | 5 | full-value count of the insertion suffix only |
| Safety families (routes N2..8, 16; dispatch to N32 incl. `[u8;16/17/85/86]`, `DropValue`, ZST; insertion at every offset of N15..20; mutating `Cell` comparators) | 83 | safety to normal return |
| Drop count / tag permutation; `Cell` route tag permutation | 16 | at normal return |
| Trait entries with logical-byte model (`Cell<u8>`, `DropKey`) | 6 | order + count of logical values |
| Assembly helper pairs (positive members), `has_efficient_in_place_swap` type matrix, `sort4` with arbitrary comparator | 8 | helper properties / safety + value preservation |

- **Contract domains.** The executed domain of each PFC is listed target × tag × domain in the
  [registry][dom] and its [PFC inventory][dom-inv] (36 ordinary + 2 opt-in frame controls). Comparators are
  always the canonical **function pointer** of a profile tag; requires accept a wider domain (e.g. `merge_profile`
  and `insert_tail_profile` admit N up to 32 and same-allocation placements) than the executed fixtures (u64
  N2..8, u8 N2..9 on exact arrays; u8 N9 from a 48-slot scratch prefix; insertion u8 N2..17 and u64 N2..16 in a
  17-element backing). Only executed domains are claimed.
- **No ordinary composition.** No ordinary root uses `stub_verified`; the four `stub_verified` uses are opt-in
  wrong-comparator controls ([specfix.rs:501][sf-501]). 57 ordinary roots carry a manual `stub` of
  `panic_on_ord_violation` (abort, assume or cut), so their safety results are normal-return only.
- **Generic limitations.** No claim for arbitrary `T`, arbitrary `FnMut`, closures, other comparator
  instantiations, other lengths/backings/offsets, tie stability, uninitialized-memory detection, panic or unwind.
  `Sort4ReadU64` and `LtU64` have different canonical comparators and probes ([specfix.rs:74][sf-74],
  [:103][sf-103], [:112][sf-112]). The array-element profiles `KeyB16`, `KeyB17`, `Sort4ReadB16` carry an OPEN
  model-trust question (Section 7).

## 3. Part 2: opt-in harnesses and the integrated tree

**v6 opt-in set.** With `--cfg kani_smallsort_controls` the v6 source defines 384 roots = 202 ordinary + 182
opt-in (static). By source purpose (each root read; classification in [harnesses.tsv](harnesses.tsv)):

| Class | Roots | Meaning |
|---|---:|---|
| positive candidates (property families) | 131 | macro families proving safety/order/count on further lengths or types; expected SUCCESS; 8 measured on the v6 library tree by PART2-FAST, the rest **not run on v6** |
| intended negatives | 34 | must FAIL at one designated check (mutants, corrupted outputs, wrong comparator, deliberate UB, probe guard) |
| diagnostics | 10 | tool/model diagnostics (`specdiag` 7, CASE5 typed swap 3); no pass/fail claim |
| positive service/regression | 7 | reachability partners of controls, regression bundle, standalone `sort4` `[u8;85]` row |

Two rows are borderline: `specfix_probe_guard_rejects_t129` (a helper guard that must fail for a 129-byte type;
counted as negative) and `smoke::predicate_efficient_swap_boundaries` / `sort4_arbitrary_comparator_bytes85_n4`
(counted as service). Counting the guard as a diagnostic and one service row as a diagnostic gives the
alternative split 131/33/12/6; the 131 family count and the 182 total do not depend on this choice. The 131
are **not** 131 successful proofs and not 131 independent domains: they are 14 families, several of which repeat
one property at neighbouring lengths.

| Positive family (opt-in, v6) | Roots | Property, domain |
|---|---:|---|
| route safety, all three general routes | 23 | safety, u64 N9..15, 17..32, scratch48, arbitrary comparator |
| insertion at listed offsets / offset one | 33 | safety, u64 and mutating `Cell`, N15..20 |
| network entry correctness | 14 | order (count only N8), u8 N8, 14..17; u64 N8, 10..17 |
| fallback insertion | 13 | key order + count, u8/u64 N7..16 |
| insertion-suffix permutation | 9 | count, u8 N12, 15..17; u64 N11, 12, 15..17 |
| mutating insertion | 8 | safety, `Cell`, N6..20 groups |
| general/stable direct | 8 | key order + count, u64 N2..8, u8 N9 |
| unstable dispatch network / insertion safety / dispatch pair | 12 | safety, u64 N11..29; `[u8;16/17/85]`, `DropValue` N31 |
| aggregate-backing stable direct | 3 | key order + count, u64 N6..8 |
| trait entries | 4 | logical order + count, N7..9 |
| dispatch safety ZST, drop route | 4 | safety; drop/tag at normal return |

Four of these (general/stable direct u64 N8 and u8 N9, trait entries `Cell` N8 and `DropKey` N9) timed out at
600 s on an older tree; they remain unestablished positive candidates.

**Integrated tree.** Library commit `2756f0e2a6` copies, byte for byte, the files of five research lineages and
adds three cfg-gated module registrations; v6 runtime, ordinary roots, tooling and flags are unchanged
([SOURCE-MAP][srcmap], [check_parttwotree.py][cpt]). Expected cfg-on set 438 = 384 + 54 transferred roots
(236 opt-in). The terminal inventory Build `02b46b34-d19c-47c1-9f96-52f84d72467b` obtained the native cfg-on
set: **438 names, exactly equal to the expected list, 202/202 ordinary and 54/54 added members, no missing, extra
or duplicate names** ([RESULT-PARTTREE-INV2][r-inv2]). The earlier attempt (20-minute budget) ended with
`kani list` exit 124 and no inventory ([RESULT-PARTTWO-TREE][r-ptt]). **Formal verification of the integrated
tree is NOT_RUN**; no Build has proven any of its 54 transferred roots. The future proof matrix (A 28
SUCCESS-gate rows including 6 same-Build leaf/consumer pairs, B 17 expected-FAILED, C 10 OPEN/diagnostic) is a
plan, not 55 executed rows ([PROOF-MATRIX][pm]).

Domains that are explicitly open on every tree (no SUCCESS on record): u8 N13 direct proof with function-item
comparator; u64 N13 whole-entry composition; u64 N10 composition (OOM); `merge_profile` 18 → scratch32 leaf;
composed merge4 through step summaries; length wrappers N0..3 for `u8`, `NonCopyU8` and stable `u8`; the four
timed-out positive candidates above; any length outside the listed sets.

## 4. Research evidence by snapshot

The research results come from separate library lineages, none an ancestor of another; each result is tied to
its own commit and Build ([claims.tsv](claims.tsv), source compilation [PART2-EVIDENCE-DRAFT][draft]). The
integrated tree reproduces their files byte-identically, but none of these runs is credit for tree `a45388ac`.

| Lineage / record | Library commits | What is established (bounded, own tree only) | Not established |
|---|---|---|---|
| L-M stable merge bridge ([BRIDGE][r-bridge], [BRIDGENINE][r-b9]) | `b07dc219a2`, `77cb4c9773` | N3 `merge_profile<LtU8>` leaf + merge-level binding (same Build); actual Stable u8 N9 entry (one fn-pointer `LtU8::CMP`, scratch48) by direct proof M7 and by composition M6 with leaf M5 in the same Build; payload-flip control M8 | other N, types, comparators; frame calibration M4 positive has covers 2/5 |
| L-W length wrappers ([WONE][r-wone], [WONEDIAG][r-wonediag], [WONETWO][r-wonetwo]) | `e4f1df6a34`, `af8b0db75a`, `4231462d12` | `stable_cell_len` N0..3; three other wrappers at fixed N3 and N2 | N0..3 union for `u8`, `NonCopyU8`, stable `u8` (TIMEOUT/TIMEOUT/OOM) |
| L-N u8 network ([NETNINE][r-n9], [NETCOMP][r-nc], [NETCOMP2][r-nc2], [NETTEN][r-nt], [NETTEN-CALLER][r-ntc]) | `24d9f1d3d8` … `2ebda13e14` | direct u8 N9 with function-item F; exchange-summary compositions u8 N9 (same Build inside a failed calibration Build; re-run with cross-Build leaf) and u8 N13 (same Build); u8 N10 actual route through `swap_net9` + `insert_tail_profile` with one shared probe, leaves from an earlier Build | u8 N13 direct (TIMEOUT); same-Build N10 |
| L-N u64 ([U64-N9][r-u9], [U64-N13][r-u13], [U64-TEN-CALLER][r-u10]) | `fddf308321`, `497077c6cd`, `a6010df7b4` | u64 N9 composition with same-Build leaf; u64 N13 leaf; u64 N10 binding controls (gate PASS = designated FAILED rows) | u64 N13 entry (TIMEOUT); u64 N10 positive (OOM, UNKNOWN) |
| L-N N18 / merge step / merge4 ([NET18][r-n18], [MERGESTEP][r-ms], [DIRECTFOUR][r-d4]) | `4eb7e81259`, `91d4d9f77a`, `248b2725c6` | `swap_net9` leaves inside an 18-element backing; merge-step leaves; direct merge4 fixture | merge18 leaf, composed merge4 (TIMEOUT); binding controls missed declared covers |
| SPLIT31 ([RESULT][r-split]) | `b2a13747da` | bytes17 N31 dispatch safety split into Stable/Unstable roots, both SUCCESS; unsplit baseline SUCCESS | macOS fit, ordinary promotion; no sorting claim |

Rules applied to every row: a summary result is called a composition only with its matching leaf, and the leaf's
Build is stated (same-Build: M2+M1, M6+M5, N12+N11, N15+N14, N7+N5; cross-Build: N10 ← N5, N22c ← N22a/N22b).
Matching comparator semantics between a **function-item** comparator (`strict_less::<u8>` in N1 and in the
ordinary network harnesses) and a **function-pointer** comparator (`U8Cmp` = `StrictU8::CMP` in the compositions)
is not a transfer proof: they are different Rust instantiations. No row is a theorem about generic `FnMut`,
generic `T` or arbitrary layouts. Control gates passing means the designated checks FAILED as intended; that is
not a positive theorem.

## 5. Delta to the v4 baseline

The baseline is Part 1 v4 `f0ba14f97b3adea21c1c9671db6245afe7a15887`. Findings F01–F11 and the clarifications
A1–A4 are defined neutrally in [findings.tsv](findings.tsv) with links into v4 and current public code; status is
derived from that code and from the records above, not from any single green workflow. Items already addressed
at v4 are **not** counted as new closures.

| Id | Issue (short) | v4 baseline | Current (P1-V6 ordinary; research separately) |
|---|---|---|---|
| F01 | no correctness contracts on the three trait methods | N2 wrapper pilot | unchanged in ordinary; opt-in wrappers N3/N2 and `stable_cell` N0..3 on other trees; OPEN |
| F02 | bounded lengths/types/properties | partial, direct to N9 | unchanged in ordinary; opt-in families not run; OPEN |
| F03 | generic comparator contracts over-claimed | fixed at v4 for concrete profiles | unchanged; not a post-v4 closure |
| F04 | init premises vs instrumentation | (a) predicates written; (b) no uninit instrumentation | (a) unchanged; (b) CI profile misses uninit reads, `-Z uninit-checks` unsupported for the code ([SPECDIAG][r-sd]); OPEN |
| F05 | bytewise oracle | substantially fixed at v4 | unchanged; probe helper guards size ≤ 128; padding unsupported |
| F06 | whole-output permutation for network N ≥ 9 | open | ordinary unchanged (count only N < 9); research: u8 N9/N10/N13 and u64 N9 compositions on separate trees; OPEN in ordinary |
| F07 | conditional composition in ordinary | removed at v4 | still none in ordinary; experimental compositions only on research trees |
| F08 | panic/unwind/ownership | open | unchanged: 57 manual panic stubs, normal-return drop checks; OPEN |
| F09 | not all UB classes checked | open | unchanged flags; OPEN |
| F10 | Part 2 on old base | incompatible | source integrated on v6 + inventory 438/438; proof NOT_RUN |
| F11 | retired scaffolding, unpublished inventory refs | 149 `cfg(any())` items | 0 at v6 ([CLEANUP][r-clean]); controls behind `cfg(kani_smallsort_controls)` |
| A1 | requires domain wider than executed PFC domain | risk | documented per target × tag in the registry; every research composition has a leaf on its own domain |
| A2 | comparator/probe agreement in each bridge | open (sort4 vs merge profiles differ) | met in each concrete research bridge (M6, N7/N10/N12, N15, N22c); general multi-stage chain OPEN; N10 shared probe counts only for its own domain |
| A3 | modifies enforcement on the pin | confirmed from Kani sources | plus a source-bound control on the pin (M4 negative FAILED at the assigns check); bounded to that target |
| A4 | process note: technical work need not wait for organizers | note | not a proof obligation and not a technical closure |

## 6. Optimizations and resources

**Ordinary count history** (each step is a separate record; counts are names, not domains):

| Step | Ordinary | Change | Record |
|---|---:|---|---|
| VALID-B (library tree `2532dc573c`) | 144 | baseline | [RESULT-VALID-B][r-vb] |
| INTEG | 176 | +12 direct roots, −11 retired duplicates (same T/F/N/body, moved to opt-in), +31 returned roots | [RESULT-INTEG][r-integ] |
| ASSEMBLY (= v2 tree `954e0becf8`) | 182 | +3 trait N8 roots, +6 aggregate u64 N6..8, −3 duplicates | [RESULT-ASSEMBLY][r-asm] |
| INTEG2 / P1-CLEAN | 197 | +16 −1 (network/insertion N10..12, route safety N3..7, N9 direct replacements, three START1 groups) | [RESULT-INTEG2][r-integ2] |
| INTEGWRAP (= v3/v4 count) | 200 | +3 N2 wrapper PFCs | [RESULT-INTEGWRAP][r-iw] |
| MACSPLIT (= v6 tree) | 202 | two slow roots each split into two halves with the same union domain (−2 +4) | [RESULT-MACSPLIT][r-macsplit] |

Net +58 names; this includes returns, duplicate retirements and splits, so it is **not** 58 new semantic domains.

**Accepted results and failures, kept apart:**

- BACKING ([record][r-backing]): aggregate `MaybeUninit<[u64;48]>` backing for stable u64 N8 accepted (CBMC RSS
  −81 %, VT −26.7 %); the same change for bytes17 N32 dispatch rejected (RSS +48 %, VT +5.6 %). Fixture change only,
  no generic-backing theorem.
- CASE5 ([record][r-case5]): a minimal fixture (`[u8;1]` element read through a `select_unpredictable`-selected
  pointer) produces a counterexample that no Rust execution can produce; the same on `u8` passes. Component and
  trigger UNKNOWN; model trust of `KeyB16`, `KeyB17`, `Sort4ReadB16` stays OPEN (in-target twins timed out).
  This is not evidence that those proofs are false, and the passing scalar diagnostic does not close it.
- GEOM16 ([record][r-geom]): three N16 scratch48 merge PFC geometries SUCCESS (one at 526.8 s), four controls
  failed at the intended locations; automated gates false, accepted by location. No caller-N16 theorem.
- WRAP-N2 ([record][r-wrap]) accepted three N2 wrappers (later ordinary); the N0..3 wrapper union failed for three
  types (W2).
- MACSPLIT: split halves measured on GCB (bytes17 max VT −52 %, sum lower; insert_tail max −28 %, sum higher). The
  macOS outcome was settled only by the full organizer CI of v6 (Section 2).
- SPLIT31 (opt-in, own tree): max VT 167.4 s vs 237.9 s (≈ −30 %), sum 280.7 s vs 237.9 s (+18 %), CBMC peak
  2.38 vs 4.00 GiB; whole-Build sampled process peaks 2.90 vs 4.45 GiB.

**Resources.** [resources.tsv](resources.tsv) keeps VT, CBMC, kani-driver, compiler and process-sum RSS in separate
columns with machine/jobs/flags/timeout. Three environments are never mixed: organizer CI (Ubuntu/macOS
autoharness, `--jobs=3`, 10-minute harness timeout; per-harness data UNKNOWN here), research Cloud Build (GCB
`k1-standard4`, 4 vCPU/16 GiB, swap off, jobs 1, 600 s/row), and macOS figures reported for earlier organizer runs.
A `600` entry with status "timeout cap" is the limit, not a completed VT. Notable memory facts: the u64 N10
positive was killed by the kernel while kani-driver held 15285244 KiB sampled (14.58 GiB; `time -v` 15764976 KiB),
CBMC 2711020 KiB, so CBMC was not the cause; the u8 N10 composition Build reached kani-driver VmHWM 14781664 KiB.
The inventory lane has no sampler (peaks MISSING).

## 7. Candidates for a next Part 1 version and known limitations

- **SPLIT31** is accepted opt-in evidence on its own tree `05eb97eaef` (library commit
  `b2a13747dae7458dd825f78a1d32e2ffed0b568b`); it is not a proof of the integrated head and not ordinary.
- **PART2-FAST** ([RESULT][r-fast], commit `2104e7a596fabb058a99c8bcdf0e3f487d9a7753`, library tree = v6
  `d4ec476a7a`): eight existing opt-in roots, unchanged source, all SUCCESS with full covers on GCB jobs 1 (Builds
  `5765f47e-81d4-4729-9bc6-76e51998bbcc`, `38ec4914-5a7e-4690-aa32-d8ec32d889f7`): network correctness u8 N8
  143.6 s (order + count), u8 N14 111.5 s, N15 198.2 s, N16 311.9 s, u64 N10 66.2 s, N11 150.6 s, N12 302.8 s (order
  only), insertion suffix u8 N15 34.9 s (count only). This is a measurement on the v6 tree, not organizer CI and not
  an ordinary admission; by GCB time the highest macOS risk is u8 N16 and u64 N12.
- GCB fits under 600 s do not show macOS/jobs3 readiness. A reasonable target is a 400–450 s margin per root; the
  final gate for any new Part 1 version is a separately authorized full organizer CI of that exact commit on both
  operating systems. No such version was created for this report.

Known limitations (apply to all results above):

1. **Entry contracts, lengths, types.** No contracts on the trait methods; bounded N sets; a few element types;
   requires domains wider than executed domains.
2. **Comparator identity and stability.** Results bind one concrete comparator value and Rust type (function item
   vs function pointer); no tie-stability claim beyond key order; mutating/arbitrary comparators only in safety
   families.
3. **Model trust (CASE5).** Array-element profiles have an open modelling question on the pinned Kani.
4. **Initialization, aliasing, validity.** No uninitialized-read or invalid-value instrumentation in the profile
   used; `can_dereference` premises are written but not enforced by instrumentation; aliasing beyond Kani's
   pointer checks is not modelled.
5. **Panic and unwind.** Normal-return results with manual panic stubs; no unwind-cleanup or drop-exactly-once
   proof.
6. **Trusted tools and settings.** Kani `9461e07af7ec929f050aa4192f29363c9be07779` and its CBMC, toolchain
   `nightly-2026-10-12` ([kani-version.toml][kv]), `--no-assert-contracts`, `--cbmc-args --object-bits 12`, per-root
   unwind bounds and the manual stubs are trusted; unreachable checks reported by Kani are not itemized.

## 8. Reproducing the static checks

```sh
git clone https://github.com/Tiramisu-Cake/verify-rust-std.git && cd verify-rust-std
git fetch origin '+refs/heads/*:refs/remotes/origin/*'
git remote add upstream https://github.com/model-checking/verify-rust-std.git && git fetch upstream main
git checkout <commit of this file>
python3 -B research/challenge-8/audit-2026-11-03/check_audit_report.py
```

Output at cutoff: `PASS` with 453 harness rows whose identifier appears on the declared line at the declared
commit, 64 claims, 15 findings, 12 snapshots and every GitHub source URL pinned to a full commit (counts are
printed by the script). The checker compares text and Git objects only; it does not establish AST/MIR binding,
callee identity or any proof result, and it distinguishes the documentation HEAD (library `a45388ac`) from the
target pins.

Historical checkers, run unmodified on their own inputs (each in a detached checkout of the stated commit):

| Command | Commit | Result at cutoff |
|---|---|---|
| `python3 -B research/challenge-8/kani-k1/parttwotree/check_parttwotree.py` | `6ff24c756c` | `status PASS`, 50 checks, 0 failed (rewrites only the `head` field of `static-check.json`) |
| `python3 -B research/challenge-8/kani-k1/parttreeinv2/check_native_inventory.py g1` | `6ff24c756c` | `ok: true`, total 438, ordinary 202, added 54, missing/extra/duplicates empty |
| `python3 -B research/challenge-8/kani-k1/domains/check_domains.py` | `94ae47268d` | `OK: source pin d6b8caf7fe… 38 PFC entries / 18 lexical sites; 36 ordinary + 2 controls …; 22 domains` |

Public availability of every URL commit was checked separately (online) before publication: every commit used
in a URL of this package is contained in a branch of the public fork, and the upstream commit `c0bd09c354` is on
upstream `main`.

**Pinned verifier invocations (documented, not run here).**

- Organizer CI at v6: [kani.yml autoharness step][wf-auto] (`--harness-timeout 10m`, `--default-unwind 1000`,
  `--jobs=3`) calling [run-kani.sh autoharness][rk-auto]; partition jobs call [verify-std][rk-vs]; unstable flags
  at [run-kani.sh:87][rk-87]. Commands for the SmallSort suite are documented in [verify.rs:28–31][verify-cmd].
- Research Cloud Build lane (frozen tooling `30f77e8599`): request → [`kani_args`][k1-args]
  (`--harness <name>`… `--exact --harness-timeout <m>m --jobs=<n> --output-format=terse`, optional
  `-Z uninit-checks`), controls via `RUSTFLAGS="--cfg kani_smallsort_controls"` ([kani_k1.py:1726][k1-rf],
  [gcb-k1.sh:164][gcb-rf]), executed as `scripts/run-kani.sh --path "$PWD" --kani-args …` ([gcb-k1.sh:188][gcb-run]),
  which runs `kani verify-std … --no-assert-contracts … --cbmc-args --object-bits 12` ([run-kani.sh:313–317][rk-sel]).

## 9. Unresolved evidence and link issues

- v6 per-harness VT and satisfied-cover counts: UNKNOWN (artifacts only).
- Two MACSPLIT Build IDs are published only as prefixes (`78bdbbf9`, `3f1f39be`).
- Inventory Builds record no memory peaks and no `kani list` duration.
- The opt-in classification has two boundary rows (Section 3); both splits are stated.
- Leaf reuse across Builds (N10, N22c) and the NETCOMP calibration Build with gate FAIL remain historical.
- PART2-FAST rows are opt-in GCB measurements; their macOS/jobs3 behaviour is UNKNOWN.

[ch8]: https://github.com/model-checking/verify-rust-std/blob/c0bd09c354a50bf9fe4dcc7cc5f9c34503658479/doc/src/challenges/0008-smallsort.md
[ch8-ub]: https://github.com/model-checking/verify-rust-std/blob/c0bd09c354a50bf9fe4dcc7cc5f9c34503658479/doc/src/challenges/0008-smallsort.md#L19-L27
[ch8-contracts]: https://github.com/model-checking/verify-rust-std/blob/c0bd09c354a50bf9fe4dcc7cc5f9c34503658479/doc/src/challenges/0008-smallsort.md#L29
[ch8-all]: https://github.com/model-checking/verify-rust-std/blob/c0bd09c354a50bf9fe4dcc7cc5f9c34503658479/doc/src/challenges/0008-smallsort.md#L36
[ch8-list]: https://github.com/model-checking/verify-rust-std/blob/c0bd09c354a50bf9fe4dcc7cc5f9c34503658479/doc/src/challenges/0008-smallsort.md#L41-L50
[ch8-rules]: https://github.com/model-checking/verify-rust-std/blob/c0bd09c354a50bf9fe4dcc7cc5f9c34503658479/doc/src/challenges/0008-smallsort.md#L52
[ss]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort.rs
[ss-mod]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort.rs#L866
[ss-38]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort.rs#L38
[ss-56]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort.rs#L56
[ss-82]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort.rs#L82
[ss-97]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort.rs#L97
[ss-124]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort.rs#L124
[ss-157]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort.rs#L157
[ss-188]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort.rs#L188
[ss-380]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort.rs#L380
[ss-420]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort.rs#L420
[ss-469]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort.rs#L469
[ss-536]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort.rs#L536
[ss-574]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort.rs#L574
[ss-606]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort.rs#L606
[ss-754]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort.rs#L754
[verify-doc]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort/verify.rs#L20-L31
[verify-cmd]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort/verify.rs#L28-L31
[sf-74]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort/verify/merge/specfix.rs#L74
[sf-103]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort/verify/merge/specfix.rs#L103
[sf-112]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort/verify/merge/specfix.rs#L112
[sf-501]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/library/core/src/slice/sort/shared/smallsort/verify/merge/specfix.rs#L501
[kv]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/tool_config/kani-version.toml
[wf-auto]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/.github/workflows/kani.yml#L109-L219
[rk-auto]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/scripts/run-kani.sh#L319-L327
[rk-vs]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/scripts/run-kani.sh#L229-L236
[rk-87]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/scripts/run-kani.sh#L87
[rk-sel]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097/scripts/run-kani.sh#L313-L317
[k1-args]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/30f77e859903df14b442ff9294d4fbbd44827f20/research/challenge-8/kani-k1/tools/kani_k1.py#L343-L353
[k1-rf]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/30f77e859903df14b442ff9294d4fbbd44827f20/research/challenge-8/kani-k1/tools/kani_k1.py#L1726
[gcb-rf]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/30f77e859903df14b442ff9294d4fbbd44827f20/research/challenge-8/kani-k1/tools/gcb-k1.sh#L164
[gcb-run]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/30f77e859903df14b442ff9294d4fbbd44827f20/research/challenge-8/kani-k1/tools/gcb-k1.sh#L188
[ci6]: https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/41404150041
[dom]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/94ae47268d3957e1077c43313c82dabcaf606855/research/challenge-8/kani-k1/SMALLSORT-CONTRACT-DOMAINS.md
[dom-inv]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/94ae47268d3957e1077c43313c82dabcaf606855/research/challenge-8/kani-k1/domains/pfc-inventory.tsv
[srcmap]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/28d79f25282c448e83a399aa42826db895816d1b/research/challenge-8/kani-k1/parttwotree/SOURCE-MAP.md
[cpt]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/28d79f25282c448e83a399aa42826db895816d1b/research/challenge-8/kani-k1/parttwotree/check_parttwotree.py
[pm]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/28d79f25282c448e83a399aa42826db895816d1b/research/challenge-8/kani-k1/parttwotree/PROOF-MATRIX.md
[draft]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/28d79f25282c448e83a399aa42826db895816d1b/research/challenge-8/kani-k1/parttwotree/PART2-EVIDENCE-DRAFT.md
[r-inv2]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/6ff24c756c28f56fcac9c0bcb6551bf692bde7d1/research/challenge-8/kani-k1/RESULT-PARTTREE-INV2.md
[r-ptt]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/28d79f25282c448e83a399aa42826db895816d1b/research/challenge-8/kani-k1/RESULT-PARTTWO-TREE.md
[r-macsplit]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/4f4034527d3e3a26e4cd94e12ba6922e2b5e80e4/research/challenge-8/kani-k1/RESULT-MACSPLIT.md
[r-split]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/7d5730ad9d73b53042341e055251fef16fc64289/research/challenge-8/kani-k1/RESULT-PART2-SPLIT31.md
[r-u10]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/5737fa738bac360f19dd0113b2b8640f16bea5f5/research/challenge-8/kani-k1/RESULT-U64-TEN-CALLER.md
[r-bridge]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b7761aa50afdc2ff60a78b643397b4a765fc343f/research/challenge-8/kani-k1/RESULT-BRIDGE.md
[r-b9]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/8cbb26750012c51d99266fa9fbe342519345649d/research/challenge-8/kani-k1/RESULT-BRIDGENINE.md
[r-wone]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/1c107cb12a2d214f9e8745192bc19d2d3e6df638/research/challenge-8/kani-k1/RESULT-WONE.md
[r-wonediag]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b7a8db4a987c5475d371d2986eb1728e5b0a3148/research/challenge-8/kani-k1/RESULT-WONEDIAG.md
[r-wonetwo]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b21be6cd8639ba779b9badea989abe3a3e4a2c91/research/challenge-8/kani-k1/RESULT-WONETWO.md
[r-n9]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/dfaba49ddcc409a04240b75908ebe25a535d19a4/research/challenge-8/kani-k1/RESULT-NETNINE.md
[r-nc]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/763b098cd081bc8940e82a422add81ab5c2938f6/research/challenge-8/kani-k1/RESULT-NETCOMP.md
[r-nc2]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/58d464ce1ce3d3ad7e60325e3297fdf07d38db4c/research/challenge-8/kani-k1/RESULT-NETCOMP2.md
[r-nt]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/9835bd00dc4bf386e68e5f7885964a17d0dda240/research/challenge-8/kani-k1/RESULT-NETTEN-LEAVES.md
[r-ntc]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/61cfba69c3dac0b87324d2845c1164e08222d0a6/research/challenge-8/kani-k1/RESULT-NETTEN-CALLER.md
[r-u9]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/9ab925b1578b9102e3009c0ec940c5c9cc0280cb/research/challenge-8/kani-k1/RESULT-U64-N9.md
[r-u13]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/4b9d56c46d1be97ba981610fb0dea77e0c864f66/research/challenge-8/kani-k1/RESULT-U64-N13.md
[r-n18]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/7d8b21728b1ccb632d67374918bd13d2c45de116/research/challenge-8/kani-k1/RESULT-NET18-LEAVES.md
[r-ms]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/97a252bea7ee68720b097ecf83d014e0b87d5f20/research/challenge-8/kani-k1/RESULT-MERGESTEP.md
[r-d4]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/e3a778017a0e057b34d6ea910fcca9d21f7dc3a3/research/challenge-8/kani-k1/RESULT-DIRECTFOUR.md
[r-sd]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/e417249e663a7b34b4148c641d062319096cb4d2/research/challenge-8/kani-k1/RESULT-SPECDIAG.md
[r-clean]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/e382287728b9745be3f003f286ababa31db9a9de/research/challenge-8/kani-k1/RESULT-CLEANUP.md
[r-vb]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/6ff24c756c28f56fcac9c0bcb6551bf692bde7d1/research/challenge-8/kani-k1/RESULT-VALID-B.md
[r-integ]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/6ff24c756c28f56fcac9c0bcb6551bf692bde7d1/research/challenge-8/kani-k1/RESULT-INTEG.md
[r-asm]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/6ff24c756c28f56fcac9c0bcb6551bf692bde7d1/research/challenge-8/kani-k1/RESULT-ASSEMBLY.md
[r-integ2]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/6ff24c756c28f56fcac9c0bcb6551bf692bde7d1/research/challenge-8/kani-k1/RESULT-INTEG2.md
[r-iw]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/6ff24c756c28f56fcac9c0bcb6551bf692bde7d1/research/challenge-8/kani-k1/RESULT-INTEGWRAP.md
[r-backing]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/945db634c1eb5938dc6fe51112b0a16aa52e21a1/research/challenge-8/kani-k1/RESULT-BACKING.md
[r-case5]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/a1e56b61cdaee512ca646728a1dbac098cf7be93/research/challenge-8/kani-k1/RESULT-CASEFIVE.md
[r-geom]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/1b43b51efb38e53fd70224652e9c9032aa87fdb4/research/challenge-8/kani-k1/RESULT-GEOM16.md
[r-fast]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/2104e7a596fabb058a99c8bcdf0e3f487d9a7753/research/challenge-8/kani-k1/RESULT-PART2-FAST.md
[r-wrap]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/73336711b053ed9b5ca79ac6ec2cd8ccd9e4ffad/research/challenge-8/kani-k1/RESULT-WRAPTWO.md
