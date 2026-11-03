# WRAPMORE PRE-BUILD G1 (prepared; nothing dispatched)

Runtime Claude Code, executor alone, no subagents. Stable owner k1-merge, slug wrapmore. Prepared 2026-11-03.
T0 starts at the actual G1 dispatch after coordinator GO **and** PERMSOLVER terminal/accounting (same owner).
This file registers no phase and grants no dispatch.

## Identities
- Branch `experiment/kani-k1-wrapmore-20261103`; base `2104e7a596fabb058a99c8bcdf0e3f487d9a7753` (library tree
  `d4ec476a7a`, v6); task commit `483bab843d` (TASK-WRAPMORE.md sha256 4c74ebce…51de).
- Library commit `0bf64c1c32977c54c090cb4ef23aba40ba38c33c`, library tree **`b9be6513e756ad74f4f04bb3ebb8b487023bcaa7`**.
  `verify/wrap/more.rs` (new) blob `0189d5a075`, sha256 f5d1e4b6…8e50; `verify/wrap.rs` blob `5938b184` → `a2c79f35`;
  smallsort.rs sha256 78fc8fe8…ed61 (unchanged). Lane files = frozen tooling `30f77e85` (gate check). Kani pin 9461e07a.
- Request `wrapmore/g1.request.json` = `RUN-REQUEST.json` (G1 commit), id `wrapmore-g1-20261103`, sha256
  869979722e67f6d5291e8d644c87217b4906e512a5b10b2c464483031dd9eb15; `kani_k1.py validate --require-runner
  gcb-e2-standard-4 --max-total-minutes 720` OK: 3×`--harness`, `--exact`, `--harness-timeout 10m`, `--jobs=1`,
  `--output-format=terse`, rustflags `--cfg kani_smallsort_controls`.

## Semantic diff (library, vs base)
- `wrap.rs`: only appended `\n#[cfg(kani_smallsort_controls)]\nmod more;` (prefix byte-identical to base). Existing
  wrappers/helpers/PFC/controls untouched; no visibility change (child uses parent-private items via `super::`).
- `wrap/more.rs` (new, whole module opt-in): helper `freeze_scratch::<N>` (scratch length ≥ N+16, `can_write`
  scratch, disjointness exactly as `stable_region`: different allocation, or offset ≥ N / ≤ −len); wrappers
  `stable_freeze_byte`, `unstable_cell`; PFC `stable_freeze_byte_n2`, `unstable_cell_n2`; control
  `rejects_always_true_more`. Reused from parent: Model, byte_less/cell_less, canonical, canonical_guard,
  pair_region, pair_sorted, pair_count, input_covers, always_true. No stub, no cfg inside, no `pub`.

## Contracts
| Wrapper (more.rs) | requires | modifies | ensures |
|---|---|---|---|
| `stable_freeze_byte(v:*mut u8, scratch:*mut MaybeUninit<u8>, scratch_len, cmp, probe)` :30-38 | `pair_region(v) && freeze_scratch::<2>(v, scratch, scratch_len)`; `canonical(cmp, byte_less)` | `slice(v,2)`, **`slice(scratch, scratch_len)`** | `pair_sorted(v)`; `old(pair_count(v,probe)) == pair_count(v,probe)` |
| `unstable_cell(v:*mut Cell<u8>, cmp, probe)` :58-63 | `pair_region(v)`; `canonical(cmp, cell_less)` | `slice(v,2)` | same two |
Specs never call a comparator, never read scratch/uninit (helper uses only `can_write`, `same_allocation`, pointer
offset); `old()` captures only the scalar count. Body: canonical guard → `from_raw_parts_mut` → trait call. Scratch is
a raw ptr+len (not `&mut [_]`) so `modifies` names it without the &mut-capture conflict noted in wrap.rs.

## Route by source (smallsort.rs)
- `stable_freeze_byte`: u8 is `Freeze` ⇒ `FreezeMarker` (shared/mod.rs:13) ⇒ specialized `impl<T: FreezeMarker>
  StableSmallSortTypeImpl` (49-62) overrides the blanket `default fn` (30-46) ⇒ `small_sort_general_with_scratch`
  (220). N2: `scratch.len() < len+16` → `abort_immediate` (230-232), hence requires ≥ 18; size 1 ≤ 16 but len < 16,
  len < 8 ⇒ copy v[0]→s[0], v[1]→s[1] (presorted 1); both inner loops empty; `bidirectional_merge(s[0..2]) → v`, 1
  iteration; guard forgotten. Writes scratch[0..2] and v. **Machine route witness** (harness assert, not spec):
  after return `scratch[0..2] == [a, b]`; the blanket insertion route never writes scratch, whose unwritten slots are
  nondeterministic, so this assert can only hold on the general route.
- `unstable_cell`: Cell<u8> contains UnsafeCell ⇒ !Freeze ⇒ no FreezeMarker; the specialized
  `impl<T: FreezeMarker> UnstableSmallSortTypeImpl` (90-101) does not apply ⇒ blanket `default fn` (75-88) ⇒
  `small_sort_fallback` (199) ⇒ `insertion_sort_shift_left(v,1)`: 1 tail, ≤ 1 shift. (Type-level argument; the
  insertion behaviour is identical to `stable_cell`, so no observable route witness exists.)
- Unwind: max loop iterations at N2 = 2 (`for offset in [0, len_div_2]`); others ≤ 1. Needed ≥ 3; `unwind(16)` as the
  three N2 wrappers (unwinding assertions stay on).

## Harnesses, covers, literals
| Row | Expect | Asserts (own) | Covers |
|---|---|---|---|
| `wrap::more::stable_freeze_byte_n2` | SUCCESS | input frame backing4 (`v[0]`,`v[3]`); route witness | 2 scratch len (18 = minimum, 19) + 6 input_covers + entry = **9** |
| `wrap::more::unstable_cell_n2` | SUCCESS | input frame backing4 | 6 input_covers + entry = **7** |
| `wrap::more::rejects_always_true_more` | FAILED `wrap canonical comparator required` | — (plain `#[kani::proof]`, real bodies) | 2 (one per nondeterministic branch, before guard) |
PFC: scratch backing `[MaybeUninit<u8>; 19]` (separate allocation), `scratch_len ∈ {18, 19}`; scratch is in `modifies`
and not frame-checked. Control: branch 1 `stable_freeze_byte(.., scratch18, always_true::<u8>)`, branch 2
`unstable_cell(.., always_true::<Cell<u8>>)`; parent `rejects_always_true` unchanged. Literal occurs once in the
tree: `wrap.rs:61` `kani::assert(ok, ...)` in `canonical_guard`. Control accepted only with exactly 1 failed check =
that literal/line, covers 2/2. Gate PFC: SUCCESS, 0 failures, all covers satisfied.

## Static delta (`check_wrapmore.py g1` → `static-check-g1.json`, ok 21/21; rustfmt `--check` clean both files)
- Ordinary unchanged **202** (= macsplit/ordinary-expected.txt; sha256 78c4c050…79e7).
- cfg-on **384 → 387**, exact added set = the 3 `wrap::more::` names above (`cfg-on-expected-g1.txt`, sha256
  66d0206e…fb75). Retired unchanged. PFC targets `stable_freeze_byte`/`unstable_cell`, no `stub_verified`.
- No local cargo/rustc/Kani: first compile of the child (cfg-on) is G1 itself.

## Budget / slots (`k1g.sh budget`, 2026-11-03, before G1)
- Project: 191 builds, used $84.3045, reserved by unfinished $1.8900 (PERMSOLVER), cap $88.96.
- G1 reserve (3×10+30)×$0.0135 = $0.810 → 84.3045 + 1.8900 + 0.810 = $87.0045 ≤ $88.96. Worst case incl. G2
  ($1.080): $88.0845 ≤ $88.96. Own spent $0; own plan $1.890 ≤ $1.95. Re-check budget immediately before submit.
- Slot k1-merge: occupied by PERMSOLVER; dispatch only after its terminal/accounting and coordinator GO.
- Envelope: build timeout 60 min + finishing fits main 180 min from T0. G2 (N4 ×5) is prepared after G1 terminal.

## Risks
- First compile of contract attrs with a two-target `modifies`, a const-generic spec helper and raw scratch ptr+len:
  compile error ⇒ shared blocker; one repair only within cap rules.
- The route-witness assert is beyond the task's spec form (harness-level only); if the source reading were wrong it
  fails that PFC row, and that would be the finding.
- Scope: concrete types u8/Cell<u8>, N2 only; no generic T/F, no panic/unwind, no stable-tie-order claim.

# WRAPMORE PRE-BUILD G2 (after G1 terminal/accounting; nothing dispatched)

G1 b896b36d terminal SUCCESS, 3/3 rows accepted, cost $0.1890 (`g1.result.md`); no compile blocker ⇒ G2 runs.

## Identities
- Library commit `716e094b615484c1e0f1fac3e6f87299f14a0c49`, library tree **`7cdb7ee5eb8343ee943c9b79b2a4ecdb04fa60b8`**;
  `wrap/more.rs` blob `1f476056f0`, sha256 0510281b…ecc4. wrap.rs, smallsort.rs and all other library files unchanged
  vs G1 tree. Lane files = `30f77e85`.
- Request `wrapmore/g2.request.json` = `RUN-REQUEST.json` (G2 commit), id `wrapmore-g2-20261103`, sha256
  21dbdd87f38caaa8837994aa346d50e6852ec5643fbb239a420243524786e805; validate OK (5×`--harness`, `--exact`,
  10m, `--jobs=1`, terse; `--cfg kani_smallsort_controls`).

## Semantic diff (more.rs vs G1 library commit 0bf64c1c32)
- Module doc +1 clause; `use` lists add UnstableSmallSortFreezeTypeImpl, Model, NonCopyU8, noncopy_less,
  can_dereference. Every G1 item from `freeze_scratch` to `rejects_always_true_more` byte-identical (gate check).
- Appended child helpers: `span_region::<T,N>` (= pair_region over N), `span_sorted::<T,N>` / `span_count::<T,N>`
  (same key/full-value model as `sorted`/`count`, reading only the N input elements), `stable_region_n::<N>`
  (= `stable_region` with offset ≥ N). Five wrappers `*_n4`, five PFC `*_n4_backing6`, `n4_covers`, `ordered_pair`.
  Parent and existing wrappers/helpers/PFC untouched; no union of lengths, only fixed N4.

## Contracts (all: `canonical(cmp, <same comparator>)`; ensures `span_sorted::<_,4>(v)` and
`old(span_count::<_,4>(v,probe)) == span_count::<_,4>(v,probe)`)
| Wrapper (more.rs) | requires (region) | modifies | Trait call |
|---|---|---|---|
| `stable_cell_n4` :192 | `stable_region_n::<4>(v, scratch)` (scratch `&mut`, as parent) | `slice(v,4)` | `<Cell<u8> as Stable>` |
| `unstable_byte_n4` :213 | `span_region::<u8,4>(v)` | `slice(v,4)` | `<u8 as Unstable>` |
| `freeze_noncopy_n4` :229 | `span_region::<NonCopyU8,4>(v)` | `slice(v,4)` | `<NonCopyU8 as UnstableFreeze>` |
| `stable_freeze_byte_n4` :248 | `span_region::<u8,4>(v) && freeze_scratch::<4>(v, scratch, scratch_len)` (≥ 20) | `slice(v,4)`, **`slice(scratch, scratch_len)`** | `<u8 as Stable>` |
| `unstable_cell_n4` :273 | `span_region::<Cell<u8>,4>(v)` | `slice(v,4)` | `<Cell<u8> as Unstable>` |

## Route by source at N4 (smallsort.rs)
- Cell Stable: !Freeze ⇒ blanket default (30-46) ⇒ `insertion_sort_shift_left(v,1)`: 3 tails, ≤ 3 shifts each.
- u8 Unstable: Freeze ⇒ (90-101) ⇒ FreezeMarker+CopyMarker impl (142-171): size 1 ≤ 8 and 32 ≤ 4096 ⇒
  `small_sort_network` (311): 4 ≤ 32, `no_merge` (4 < 18), region v[0..4], presorted 1 (< 9) ⇒ insertion from 1, return.
- NonCopyU8: Freeze, !Copy ⇒ default Freeze impl (113-130): 48 ≤ 4096 ⇒ `small_sort_general` (205), private
  scratch48 ≥ 20 ⇒ general_with_scratch: len < 8, presorted 1: v[0]→s[0], v[2]→s[2]; each half 1 copy + 1 insert_tail;
  `bidirectional_merge` 2 iterations into v.
- u8 Stable Freeze: specialized (49-62) ⇒ the same general path with caller scratch (abort if < 20, 230-232).
  **Route witness** (harness): `scratch[0..4] == ordered_pair(a,b) ++ ordered_pair(c,d)` (stable: swap only if the
  second key is strictly less, exactly insert_tail); the insertion route would leave those slots nondeterministic.
- Cell Unstable: blanket (75-88) ⇒ `small_sort_fallback` ⇒ insertion from 1.
- Unwind: max iterations 4 (`span_count`), insertion 3 tails / ≤ 3 shifts, general 2 offsets × 1 + merge 2; need ≥ 5;
  `unwind(16)` as N2 (unwinding assertions on).

## Harnesses, covers, literals (`wrap::more::`, all expect SUCCESS, no stub)
| Row | Own asserts | Covers |
|---|---|---|
| stable_cell_n4_backing6 | frame v[0],v[5]; scratch frame (initialized slot 0, len ≤ 2) | 2 scratch + 7 n4 + entry = **10** |
| unstable_byte_n4_backing6 | frame | 7 + entry = **8** |
| freeze_noncopy_n4_backing6 | frame | **8** |
| stable_freeze_byte_n4_backing6 | frame; route witness | 2 scratch len (20, 21) + 7 + entry = **10** |
| unstable_cell_n4_backing6 | frame | **8** |
`n4_covers` = the six N2 `input_covers` on the first pair (reversed, increasing, tie, duplicate, probe hit/miss) +
`wrap N4 strictly reversed keys return` (k(a)>k(b)>k(c)>k(d): every element must move). Backing6 `[l,a,b,c,d,r]` all
`kani::any`, independent probe. Gate: SUCCESS, 0 failures, all covers satisfied. No control in G2.

## Static delta (`check_wrapmore.py g2` → `static-check-g2.json`, ok 23/23; rustfmt `--check` clean)
- Ordinary unchanged **202** (sha256 78c4c050…79e7). cfg-on **384 → 392** = base + 3 G1 + 5 G2 names, exact
  (`cfg-on-expected-g2.txt`, sha256 1dfc6d6c…4717). PFC targets = the five `*_n4` wrappers, no `stub_verified`.

## Budget / slots (`k1g.sh budget` 2026-11-03 ~11:57Z)
- Project 193 builds, used $85.1145, reserved by unfinished $0.9450 (ROUTESEF, k1-network). G2 reserve
  (5×10+30)×$0.0135 = $1.080 ⇒ 85.1145 + 0.9450 + 1.080 = **$87.1395 ≤ $88.96**. Own: $0.1890 + $1.080 = $1.269 ≤ $1.95.
- Slot k1-merge free (G1 terminal). Window: T0 11:36:24Z, main ends 14:36Z; G2 80 min envelope + closeout fits.
- Risk: N2 general-route rows took 168–202 s; N4 roughly doubles the symbolic bytes and merge steps, so
  freeze_noncopy / stable_freeze_byte N4 may TIMEOUT at 10 min — a row fact, no retry, N not reduced.
