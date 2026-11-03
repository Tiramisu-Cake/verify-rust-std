# WIDTHU32 PRE-BUILD (G1 request prepared; nothing dispatched)

Runtime Claude Code, executor alone, no subagents. Owner k1-network, slug widthuthirtytwo. Prepared 2026-11-03; T0 not
started (starts at the G1 dispatch after coordinator GO). This file registers no phase and grants no dispatch.

## Identities
- Branch `experiment/kani-k1-widthuthirtytwo-20261103`; base `e0fda080f5ea479d8f4fb801f4b42adde2b3259f` (library tree
  `d4ec476a7a00…` = v6); task commit `f6274aea18` (TASK-WIDTHU32.md sha256 f1dc3e28…519a).
- Library commit **`78c413817522adc6f35dceab57fa102d17a8c8b2`**: `verify/network.rs` +3 (appends
  `#[cfg(kani_smallsort_controls)]` / `mod widthu32;`; the base file is a byte prefix, checked) and new
  `verify/network/widthu32.rs` (+79). Library diff vs base: 2 files, +82 −0. New library tree **`74039680c933…`**.
  network.rs blob 1a85a483 → 2a0dd2e1 (sha256 7d219454…ee86); widthu32.rs blob 606dbf41 (sha256 a224fb7b…6f0d, 3502 B).
  Every other library file = base, so all existing roots, helpers and the runtime are unchanged.
- Reference body: PERMSOLVER `a13389358a` `verify/network/posts/perm/solver.rs` blob ed6f56b6,
  `perm_arbitrary_kissat_u64_n8` (= POSTS8 `partposts_count_u64_n8` + kissat; RESULT-PERMSOLVER 449.48 s, Build a931cf37).
- Lane files (k1g.sh LANE_PATHS) at HEAD equal tooling base e0fda080f5; `check-tooling BUILD e0fda080f5…` after the Build.
  Kani 9461e07af7ec / nightly-2026-10-12. Kissat: same pin/image as PERMSOLVER; nothing installed here.

## Source scope / route
Child `network::widthu32` uses parent helpers `super::{strict_less, count_matching_values, prefix_unchanged}` (private
ancestor items are visible to descendants; no visibility change). No macro, stub, PFC, contract, assume, `any_where`, cut.
Route: u32 is Freeze + Copy, `has_efficient_in_place_swap::<u32>()` (size ≤ 8) → `small_sort_network`, the same branch as
u8 and u64 at N8. All roots `#[kani::proof] #[kani::unwind(25)]`, input full `[u32; 8]`, independent `probe: u32`.

## Body diff vs PERMSOLVER (`widthu32/body.diff`, sha256 7507593d…87eb; `widthu32/check_widthu32.py` exact-sequence check)
Whitespace-normalized, PERMSOLVER paths `super::super::super::` → `super::` (one module level shallower). For every root the
statement sequence must equal the PERMSOLVER body with `u64` → `u32` (4 tokens: array, probe, `strict_less::<_>`,
`<_ as UnstableSmallSortTypeImpl>`), the root name, plus exactly:
- `widthu32_perm_n8_default` (line 14): `#[kani::solver(kissat)]` removed.
- `widthu32_perm_n8_kissat` (line 37): nothing else.
- `widthu32_perm_n8_value_loss_control` (line 60): `v[0] = v[1];` right after the sort, and the count literal
  `partposts: full-value count preserved` → **`widthu32 negative: full-value count after value loss`** (designated).
- all three: two covers appended after the PERMSOLVER covers: `widthu32: probe occurs in input`
  (`count(pre, probe) > 0`) and `widthu32: probe absent from input` (`count(pre, probe) == 0`).
Assert/cover literals of roots 1–2 are byte-identical to PERMSOLVER (`partposts …`), so the copied body stays identical.

## Covers / gate
Roots 1–2: 5 covers each = PERMSOLVER 3 (`partposts count: sort moves elements` / `… sort returns normally at length 8` /
`… check reached the end`) + probe occurs / absent. Gate root 2: SUCCESS, 0 unintended failures, 5/5 covers.
Root 1: measurement (SUCCESS or TIMEOUT), not gated.
Control: the only assert is the designated count literal (literal unique in the file, not a substring of another). After the
sort v is sorted, so v0 ≤ v1; with v0 < v1 and probe = old v0, count drops by 1 → reachable failure. `v[0]`, `v[1]` are
in bounds and count ≤ 8 cannot overflow, so no other check can fail. Its 5 covers follow the assert; Kani assumes an assert
after checking it, but each cover stays satisfiable on count-preserving paths (e.g. v0 = v1, or probe = v2), so they are
reported, informational only. Gate: FAILED only at `widthu32 negative: full-value count after value loss`; any other
failure (UB, unwinding, other literal) is not counted.

## Static inventory / format (`check_widthu32.py`: imports `cleanup/source_inventory.py` on a base archive and HEAD; no report)
- Ordinary 202 → 202 (sorted-name sha256 d5d55502…42e5, unchanged). Controls-on 384 → 387; exact delta +3 −0:
  `network::widthu32::{widthu32_perm_n8_default, widthu32_perm_n8_kissat, widthu32_perm_n8_value_loss_control}`.
- PFC 36 unchanged: widthu32.rs has no `proof_for_contract`; network.rs only gains the `mod` line.
- rustfmt (TASK-DIRECT wrapper, `--edition 2024`, fmtcfg/rustfmt.toml) applied, then `--check` on network.rs and
  widthu32.rs: exit 0; no line > 100; `git diff --check` clean. All bindings used; no `_`/unused items → no new warnings
  expected (after the Build: `log-grep '[-]> .*smallsort'`). No local cargo/rustc/Kani/CBMC.
- Result: `widthu32/static-check-prebuild.json` status PASS.

## Request (`kani_k1.py validate --require-runner gcb-e2-standard-4 --max-total-minutes 720`: rc 0)
`RUN-REQUEST.json` = `widthu32/request.json`, request_id **widthuthirtytwo-g1-perm-u32n8-20261103**, sha256
**ab2a1ab9a15626e78308b93bf04a73304c6d38d05c29c452eb5b8ad6bc66ca85**. kind diagnostic, agent k1-network, runner
gcb-e2-standard-4 (k1-standard4), controls true (`--cfg kani_smallsort_controls`), kani_jobs 1, uninit_checks false,
harness_timeout_minutes 10. Rows: default SUCCESS, kissat SUCCESS, control FAILED +
expect_check `widthu32 negative: full-value count after value loss`. Solver only via the root attribute.

## Budget / slots / window (k1g.sh budget, 2026-11-03)
- Project: 211 builds, used $91.9725, reserved $0 (no unfinished), cap $98.96. + G1 reserve (3×10+30)×$0.0135 =
  **$0.810** → $92.7825 ≤ $98.96. Before dispatch I re-run `k1g.sh budget` and re-check slots (project ≤ 2 unfinished,
  k1-network ≤ 1) and spent + reserves ≤ cap.
- Own cap $0.90: one Build $0.81; no retry. A compile-error repair needs own spent + $0.81 ≤ $0.90, i.e. own spent ≤ $0.09 —
  only if the failed Build is billed that low; otherwise none.
- Window: main 150 + closeout 30 min from T0.
