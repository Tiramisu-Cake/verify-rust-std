# INSERTPFC — exact pre-build packet

Worktree `/root/verify-rust-std-kani-insertpfc`; branch `experiment/kani-k1-insertpfc-20261107`.
Stable owner `k1-merge`; request IDs, stages and ledger use `insertpfc-*`.
Task `a2668aa2fadb6172d3be7cb68a9925121eaf7c61`. **No build GO yet; no dispatch.**
Library commit `a282d08c5afad32ae9abb6205bc417d95152d579`; library tree `b2482f4508126b879d1942f9c1c4e0f8bd17cec3`.
Baseline commit `4f52065504aa744f0d81775e40f52ccccbea3b5e`; baseline library tree `def2d65ddc5e73ed6ccb94df0afbb36e475d80d8`.
The library diff changes only `smallsort/verify/helper_contracts.rs` and `smallsort/verify.rs`.
Tooling equals `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; Kani pin `cd355b0bccd32300713bc2ce4f765dafa1510607`.

## Source checks and expectations

Run `python3 -B research/challenge-8/kani-k1/insertpfc/check_insertpfc.py` from this worktree.
After the authorized G2 promotion use `--active-request g2`; the default checks the G1 root request.
Reuses RENAMEMODS' lexer/expander without changing existing tooling. `check-report.json`: PASS.
All 246 previous roots and inherited conservative global identifier closures are token-identical;
552 previous expanded items are unchanged (apart from the specified import and module-map docs).
The two restored PFCs and `exercise_insertion_fixed` match `44b972435a` with only the allowed
cfg removal, import relocation, comments and six direct cover-message substitutions in `message-map.json`.
Restored dependency check uses module-local function reachability plus explicit import/path checks:
root -> exercise -> arbitrary_less -> comparison_covers. Global spelling collisions in unrelated modules
are excluded here; `closures.json` records both algorithms. These checks are source checks, not compiler resolution.
`smallsort.rs` is byte-identical to baseline. Exact byte allowlist freezes every other library edit.
Authorized rustfmt wrapper `--check --edition 2024 --config-path .../codefix/rustfmt.toml`: no diff.
Changed Rust files have no lines >100; added lines have no TIDYDOCS-forbidden vocabulary or stage codenames.
Ordinary inventory: **235 = 233 + 2**, sorted SHA256 `9758f6a907a24fc4ae823968ac65605695adcd377b9990c3993cd8c4f13bb047`.
Cfg-on inventory: **248 = 235 + 13**, sorted SHA256 `6d6cd89142e2f8242eb6f1cf6f6b065a11926af2eb16b2939492c59296eb8a61`.
Both files contain sorted full names with final newline. Compiler inventory and proof rows remain NOT_RUN.

## Requests, timing and approved deviation

Root `../RUN-REQUEST.json` is byte-identical to this directory's G1 `RUN-REQUEST.json`.
G1 `insertpfc-g1-20261107-01`, SHA256 `7812dc811e6d978d054ff2ccd09f693a69c0f5e79c6c9d8b66b527dbd63924de`.
Diagnostic; controls=true; inventory=false; jobs=1; standard4; exactly 15 rows.
Two new PFCs expect SUCCESS, 0 failed checks and 6/6 reachable covers each. Their historical
RESULT `d648179493` times are **81.02985 s** (len2) and **105.375145 s** (len3).
The 13 controls and their expect_check strings come unchanged from INTEGCHECK `controls-expected.json`;
only helper_contracts.rs's source hash and changed comparator-write coordinate are relocated.
Every control must have exactly one failed check, and that check must be the designated obligation.
Historical safety::requires diagnostics can point to the attribute opener rather than expression line:
insert_tail opener 588 / expression 589, swap opener 409 / expression 410 in unchanged smallsort.rs.
Retain that distinction; require full multiline expression binding, never accept a different failed check.

**Coordinator approval, 2026-11-07:** G1 paid timeout **105 min**, replacing task **100 min**, is authorized.
Unchanged k1g.sh calculates 15 x 5 + 30 = 105; no override or tooling change. Runner cutoff is 99 min
after validate (75 + 24); per-root timeout remains 5 min. A 12 min setup allowance leaves 87 min,
covering all 75 harness-minutes with 12 min extra slack. Actual completion remains to be measured.
G1 reserve **$1.4175** at standard4 **$0.0135/min**.
G2 `insertpfc-g2-20261107-01`, SHA256 `28a7f899e75b797d9799d15fd38cc3e2c49311d181406b363b930b3d7d6c9ed7`.
Kind inventory, controls=true, inventory=true, standard4, harnesses=[]; `--harness-timeout 44m`;
paid 74 min, runner cutoff 68 min, list max 60 min. INTEGCHECK cfg-on completed in 44 billed minutes;
8 min setup allowance leaves 60 min for compile/list. G2 reserve **$0.9990**.
Combined maximum reserve **$2.4165 <= $2.50** (coordinator explicitly accepted); remaining **$0.0835**.
Project observation: 252 builds, used **$108.4560**, reserved **$0**, cap **$118.96**;
used plus both reserves **$110.8725**. Refresh project/own budget and owner slot before each dispatch.
Maximum sequential paid time 179 min fits main 300 + closeout 30. No supplied T0; record it at execution GO.
At most two builds total, retries 0; at most one compile-error repair within own cap. If repair takes build 2,
G2 stays NOT_RUN and the result is incomplete; no further dispatch. Timeout is not a retry authorization.

## Exact source and G2 promotion boundary

The helper dispatches the pushed branch tip and permits only one build per source SHA.
The final PRE-BUILD REVIEW names the full published research packet SHA; G1 uses that exact source.
A single packet GO may cover G1 and this exact conditional G2 promotion: after full G1 acceptance,
copy the byte-identical prepared `G2-RUN-REQUEST.json` to root RUN-REQUEST.json in a new research-only
`[skip ci]` commit, together with G1 evidence/ledger/report updates. Library tree, tooling, prepared G2
request bytes and expectation files must remain unchanged. Push without force, bind the new exact source
and request hash. If GO covers only G1's source SHA, obtain a new exact PRE-BUILD REVIEW/GO for G2.
This timeout approval does not authorize dispatch of either build.

## Execution and evidence after GO

1. Confirm local/origin source SHA, library tree/tooling, owner slot, refreshed budget, GO scope and deadlines.
2. Dispatch exactly once via `research/challenge-8/kani-k1/tools/k1g.sh dispatch experiment/kani-k1-insertpfc-20261107`.
   Record source/request/build identities and reservation; call `k1g.sh watch BUILD`, then **end the turn**.
   Never poll status in a loop. Apply the same watch/end-turn rule to G2.
3. After completion, use only bounded k1g.sh status, summary, `summary BUILD 0 15`, peaks,
   `check-tooling BUILD 59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`, and `budget BUILD`.
   Save evidence under insertpfc/g1-evidence or g2-evidence. No raw logs, archives or cache reads.
4. Require G1 Cloud SUCCESS, summary COMPLETE, gate/expectations true, expected Kani exit1, both PFCs
   SUCCESS with zero failed checks and covers 6/6 each. For all controls require complete failed-check
   composition: exactly one check each matching the designated check and bound to its source expression.
   Use bounded log-grep with harness headers, failed-check counts, Failed Checks, File and VERIFICATION
   lines (max200); refine queries if saturated. Summary clipping never establishes full attribution.
5. Dispatch G2 only under approved promotion scope. Page inventory with count<=80, following reported
   next_offset; bind source/request/Kani/build/hash identities and complete nonoverlapping coverage.
   Require exactly 248 distinct names, exact set equality to cfg-on-expected.txt and its sorted hash.
6. Scan both builds with bounded log-grep `[-]> .*smallsort(/verify([/.]|$)|[.]rs)` (max200),
   refine any warning matches, and require no new smallsort/verify or smallsort.rs warnings.
7. Complete RESULT-INSERTPFC.md <=40 lines with identities, static results, two PFC rows/times/covers,
   all 13 controls' full failure composition, inventory/hash, warnings and actual expense.
   Preserve the approved 105-minute deviation. Commit/push research `[skip ci]` without force;
   finish REVIEW REQUEST <full-sha> / INSERTPFC ЗАВЕРШЁН, then stop.
