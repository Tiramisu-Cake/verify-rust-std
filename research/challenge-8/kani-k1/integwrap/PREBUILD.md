# INTEGWRAP PRE-BUILD REVIEW packet

Task `TASK-INTEGWRAP.md` (`55ef62880a`). Base `f000cb484e0c64fffa04581a9d5e930ee736f703`
(P1-CLEAN, library tree `73e902bec8`, ordinary native 197, cfg-on native 377). Cap 88.96
inherited; pin Kani `9461e07af7`, nightly-2026-10-12; tools/workflows/flags untouched.
No local cargo/rustc/Kani: compile of both cfg settings is first established by G1 (cfg-on) / G2.

## Patch (library commit `4ef0f7984b`, library tree **`426fb74a829db04569a6e8eabed99cb78232962b`**)

- `verify/wrap.rs` (new) = WRAP-N2 `811c78777d` code byte-identical once comments and the three
  cfg lines are dropped (gate). Deltas: `#[cfg(kani_smallsort_controls)]` on `always_true`,
  `rejects_always_true`, `rejects_payload_corruption`; 4 comment rewordings drop research labels
  (`WRAP-N2:`, `SPECFIX StageA … pinned model` → `merge::specfix` profile guard, `(G1 E0502)`,
  `Plain real-body…` → `Opt-in control, plain real-body…`). Wrappers, `Model` impls, comparators,
  `canonical`/`canonical_guard`, region/count helpers and the 3 PFCs compile in both cfg.
  In cfg-off nothing becomes unused (`sorted`/`count` used by `pair_*`).
- `verify.rs`: `mod wrap;` appended after `mod types;` (no cfg, existing order unchanged) and one
  doc line after the trait-method line: `` `wrap` checks N2 forwarding contracts that run them
  for Cell<u8>, u8 and a Freeze non-Copy u8.``
- `smallsort.rs` and all other verify modules byte-identical to base (runtime bodies/signatures
  therefore identical to base, whose projection gate vs `6f3a262961` passed in P1-CLEAN).

Semantic note: WRAP-N2 passed on `6f3a262961`, where callees still carried generic contracts;
on this tree they carry none. The 3 PFC targets/specs are unchanged, but the old PASS is evidence
of the old tree only; G1 re-runs all 5 on the new tree.

## Static gate (`check_integwrap.py` → `static-check-prebuild.json`, ok 23/23)

Library delta = exactly `verify.rs` + new `wrap.rs`; smallsort.rs identical; verify.rs diff =
1 doc line + `mod wrap;`; module order; wrap.rs code = WRAP-N2; cfg-gated items exactly the 3;
no stub/research label; 15 spec clauses, 0 callback calls; both expect_check literals once, each a
literal `kani::assert` line (`wrap.rs:61`, `wrap.rs:269`); base static sets = P1-CLEAN native
lists; ordinary = 197 + 3 = **200** (`ordinary-expected.txt`, sorted-set SHA-256 `0f59670e…1e2d`);
cfg-on = 377 + 5 = **382** (`cfg-on-expected.txt`, `220453cf…b78d`); retired unchanged; PFC
targets `stable_cell`/`unstable_byte`/`freeze_noncopy`, no `stub_verified`; requests validate with
`kani_k1.validate_request`; G1 entries = WRAP-N2 `g2-retry` entries; lines ≤ 100.
rustfmt `--check` (TASK-SPECFIX wrapper) clean for both files (`rustfmt-check.txt`).
Native `names_sha256` is over `kani list` order, so G2 is compared as an exact name set.

## Requests and budget

| Build | File (sha256) | Kind / flags | Entries | Reserve |
|---|---|---|---|---|
| G1 | `g1.request.json` = `RUN-REQUEST.json` (`e23558b8…454c`) | measurement, controls, jobs 1, uninit off, 10 min | 5 | 80 min / $1.080 |
| G2 | `g2.request.json` (`60304112…0a36`) | inventory, controls false, 20 min | [] | 50 min / $0.675 |

G1 rows (`verify::wrap::`): 1 `stable_cell_n2`, 2 `unstable_byte_n2`, 3 `freeze_noncopy_n2` SUCCESS;
4 `rejects_always_true` FAILED `wrap canonical comparator required`; 5 `rejects_payload_corruption`
FAILED `wrap full-value checker rejects payload corruption`. Controls accepted only with exactly
1 failed check = that literal at its line (WRAP-N2: 1/576, 1/341). Covers 9/7/7/3/1 expected.
G2: exact 200 by names vs `ordinary-expected.txt`. cfg-on 382 is a source count only (no G3
inventory in this task); G1 compiling the whole cfg-on tree shows the 5 names exist there.

Budget at packet time: used $71.7225, reserved $0, cap $88.96 (`budget-prebuild.txt`).
Reserves G1 + G2 = $1.755 > the task's $1.5. Proposal: dispatch G2 after G1 is terminal, only
if G1 actual + $0.675 ≤ $1.5 (WRAP-N2 G2 actual $0.1755; P1-CLEAN G2 actual $0.567); both
back-to-back only on explicit coordinator GO accepting the $1.755 worst-case reserve.
G2 head = G1 head + `RUN-REQUEST.json` swapped to the G2 request (no library change).

## Risks

- First ordinary (cfg-off) compile of wrap.rs: an error makes G2 fail; G1 compiles cfg-on only.
- Callee contracts removed in P1-CLEAN change what the PFCs execute (plain bodies); VT may differ.
- No unwind/panic, stable tie order, padding, init detection or full-threshold claims (as WRAP-N2).
