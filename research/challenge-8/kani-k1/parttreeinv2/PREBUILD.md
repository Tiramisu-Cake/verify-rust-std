# PARTTREE-INV2 PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO; no dispatch before GO. Runtime Claude Code, no subagents. Stable owner k1-merge.
Review SHA = published commit containing this packet (reported as `PRE-BUILD REVIEW <sha>`).
Branch `experiment/kani-k1-parttreeinv-20261102`; task `TASK-PARTTREE-INV2.md` (`b0ccb16f97`); base `28d79f2528` (PARTTWO-TREE terminal).
Library commit `2756f0e2a6ae0956fdb427574eda39b5b9a76e64`; library tree `a45388ac593c809405558ea0c27599f487b17e4e`
(HEAD:library equal; `git diff 2756f0e2a6 HEAD -- library` empty). Semantic source unchanged: prior PARTTWO-TREE review kept.
Window: T0 2026-11-02 18:50 UTC (conservative session start); main deadline 20:50, closeout 21:20.
Latest dispatch 19:10 UTC (90-min envelope + ~1 min queue + ~10 min publication reserve before 20:50); later GO -> no dispatch.

## Changes in this commit (research only, no library/tooling)

- `RUN-REQUEST.json` = `parttreeinv2/g1.request.json`, sha256 `fca8268d2d2025ad2cfba5e417ef75bddbe04223b936159e5c59324d5067d149`.
- Exact diff vs `parttwotree/g1.request.json` (e10c0993…bc4d98, kept unchanged): `request_id` →
  `parttreeinv-g1-cfgon-20261102`, `purpose` → task text, `harness_timeout_minutes` 20 → 60. Everything else equal:
  agent k1-merge, runner gcb-e2-standard-4, kind inventory, controls:true, inventory:true, harnesses:[];
  no kani_jobs/uninit_checks/worker fields. Validator exit 0 (request-validation.json); 60 = INVENTORY_MAX_MINUTES.
- New evidence files: static-check.json (re-run), request-validation.json, budget-prebuild.txt,
  check_native_inventory.py (copy of parttwotree's checker: pinned expected/added manifests with SHA-256 asserts).
- Historical PARTTWO-TREE files/ledger/G1 result untouched.

## Static (unmodified `parttwotree/check_parttwotree.py` sha256 ee828ef7…, run in a scratch detached worktree of HEAD)

PASS 50/50. ordinary 202 (= macsplit/ordinary-expected 78c4c050…, MACSPLIT native pages b721d93c…), PFC 36 /
plain 166, insert_tail PFC 5; cfg-on 438 = v6 384 + 54 added (26 PFC + 28 plain). Regenerated cfg-on-expected.txt
(sha256 `da9bcae231b35b1c42d2873976879c1209a688cc03bc25a3421f5fea7b578f1b`), opt-in-added-expected.txt (ac8c1c4a…),
roots-manifest.tsv byte-equal to committed parttwotree copies; static-check.json differs only in `head`. Expectations not edited.

## Pins, tooling, budget

Lane files equal `30f77e859903df14b442ff9294d4fbbd44827f20` (git diff empty); 6 bound files sha256 equal
(cloudbuild 73b61a35…, kani_k1.py 55d62136…, gcb-k1.sh 2547fc99…, kani.yml 587cf211…, run-kani.sh 28f1b23b…,
kani-version.toml f2f2c86a…). Kani `9461e07af7ec929f050aa4192f29363c9be07779`, nightly-2026-10-12. Pool k1-standard4.
Reserve (60+30) × $0.0135 = $1.2150 ≤ cap $1.25. Snapshot 18:56 UTC: used $81.0915, reserved $0.5400 (one foreign
unfinished 40-min build) → $82.8465 ≤ $88.96. Slots: project 1/2, k1-merge 0/1. Own: 0 builds, $0 (budget-prebuild.txt).

## After GO

Refresh budget/slots; dispatch once `k1g.sh dispatch experiment/kani-k1-parttreeinv-20261102`; `k1g.sh wait UUID` as a
background Bash task. Then bounded status/summary/inventory pages (next_offset to done)/check-tooling vs 30f77e8599/
own cost; `python3 -B parttreeinv2/check_native_inventory.py g1`; on failure bounded log-grep/log-lines only.
Gate: rc0 + bound artifact + native unique set == expected438 (missing/extra empty) → INTEGRATED + INVENTORY PASS,
PROOF NOT RUN. Timeout/no inventory/mismatch/error → exact facts, INVENTORY NOT OBTAINED/FAIL, HANDOFF; no retry/G2.
