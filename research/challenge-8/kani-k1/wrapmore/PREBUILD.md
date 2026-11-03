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
