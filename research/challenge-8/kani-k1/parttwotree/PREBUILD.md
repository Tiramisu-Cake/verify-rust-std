# PARTTWO-TREE PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO; no dispatch authorized before that GO. Runtime Claude Code, no subagents.
Review SHA = the published commit containing this packet (reported with `PRE-BUILD REVIEW <sha>`).
Branch `experiment/kani-k1-parttree-20261102`; task `TASK-PARTTWO-TREE.md` (`16090a4f22`); stable owner k1-merge.
Branch base MACSPLIT head `4f4034527d` (coordinator clarification): its library tree `d4ec476a7a001363e58f19948c188a9c2078e370`
= Part 1 v6 `d6b8caf7fe` library tree (checked byte-for-byte via tree hash). MACSPLIT report `71d1869661`: same tree.
Library commit `2756f0e2a6ae0956fdb427574eda39b5b9a76e64`; library tree `a45388ac593c809405558ea0c27599f487b17e4e`.

## Patch (details: SOURCE-MAP.md)

10 new files = exact pinned blobs from `77cb4c9773` (bridge), `4231462d12` (wone), `2ebda13e14` (netten, caller),
`248b2725c6` (neteighteen, mergestep, directfour), `497077c6cd` (u64nine, uthirteen); `netcomp.rs` = NETCOMP2
`f4d3775dc5` blob + the netten block of `2ebda13e14` + the neteighteen/mergestep block of `248b2725c6`.
Parent edits, insert-only: `#[cfg(kani_smallsort_controls)] mod bridge;` (verify.rs), `mod netcomp;`/`mod u64nine;`
(network.rs), `mod wone;` (wrap.rs). merge.rs, runtime smallsort.rs, all other v6 files, tooling unchanged.
No whole-merge/cherry-pick; no retired correct.rs/cfg(any()); no renamed symbol; context statics separate.
Not transferred: NETNINE/NETTHIRTEEN direct roots (N1–N4) and an ordinary comment edit in L-N network.rs
(outside file scope, not dependencies). **Coordinator decision point** if they should be included.

## Static evidence (`python3 -B research/challenge-8/kani-k1/parttwotree/check_parttwotree.py`: PASS, 50/50 checks)

- Identities of all 5 report tips/library commits/prerequisites present; no UNKNOWN. Lineage cfg-on statics
  reproduce recorded values 391 (L-M), 394 (L-W), 401 (N10); transferred roots are opt-in on every lineage.
- Ordinary static set = 202 = `macsplit/ordinary-expected.txt` (sha256 `78c4c050…`) = MACSPLIT native G1 pages
  (names_sha256 `b721d93c…`); equals v6 static; PFC 36, insert_tail PFC 5; v6 split names present; retired
  unsplit names, `correct::` and N1–N4 roots absent. v6 roots' gates/annotations/origins unchanged.
- Expected cfg-on = v6 cfg-on 384 ∪ transferred lineage roots 54 = **438**; `cfg-on-expected.txt`
  sha256 `da9bcae231b35b1c42d2873976879c1209a688cc03bc25a3421f5fea7b578f1b`; added set `opt-in-added-expected.txt`
  sha256 `ac8c1c4a0509480dae614c36471e32a84b6b7ae93c8b9d081a2c02d1ae474230` (26 PFC + 28 plain, all controls-gated via
  module registration; bridge also via its inner `#![cfg]`). Annotations (PFC target, unwind, stub, stub_verified)
  equal those on each lineage. Per-root manifest: `roots-manifest.tsv` (438 rows, ordinary/opt-in, provenance).
- Shared dependencies: runtime/merge/specfix/types/comparators byte-identical to L-W/L-N libraries; for L-M
  merge.rs/specfix.rs differ exactly by CLEANUP `dd0f293f00`; all used items are active v6 items.
- `pfc_order.py`: 42 lexical sites, bad 0 (16 ordinary + 26 opt-in; heuristic only), see pfc-order.txt.
- rustfmt wrapper --check exit 0 on 13 changed files; `git diff --check` clean; ≤100 columns.
- No local cargo/rustc/Kani/CBMC/proofs; no competing PR code read.

## Exact request and budget

`RUN-REQUEST.json` = `parttwotree/g1.request.json`, sha256 `e10c0993162ee8e8b22a3f1e57470a652aa8e76506c3222b4eaf40b0e1bc4d98`,
request `parttwotree-g1-inventory-cfgon-20261102`, kind inventory, controls:true, inventory:true, harnesses:[],
timeout 20 min, runner gcb-e2-standard-4 (standard4 4CPU/16GiB, swap off); no jobs/uninit/worker fields.
Validator exit 0 (request-validation.json). Lane files equal `30f77e8599` locally; 6 bound files equal;
Kani `9461e07af7ec929f050aa4192f29363c9be07779`, nightly-2026-10-12.
Reserve 50 min × $0.0135 = $0.6750 ≤ $0.70. Snapshot: used $79.8900, reserved $0.5400 (1 foreign unfinished
build), cap $88.96 → $81.1050 after reserve. Slots: project 1/2, k1-merge 0/1 (budget-prebuild.txt).

## Continuation after GO

Refresh budget/slots; dispatch once from the reviewed SHA (`k1g.sh dispatch experiment/kani-k1-parttree-20261102`);
wait with `k1g.sh wait UUID` as a background Bash task. Then bounded summary, status, inventory pages, peaks,
`check-tooling UUID 30f77e859903df14b442ff9294d4fbbd44827f20`, own-UUID cost; `check_native_inventory.py g1`
against `cfg-on-expected.txt` (no missing/extra; ordinary 202 and added 54 members).
Gate: INTEGRATED + INVENTORY PASS, PROOF NOT RUN. Compile error/OOM/timeout/mismatch → bounded facts, stop.
No G2, retries, highmem, Actions or next stage. Proof matrix: PROOF-MATRIX.md / proof-matrix.tsv (NOT_RUN).
Evidence draft copy: PART2-EVIDENCE-DRAFT.md (N22c from RESULT-NETTEN-CALLER; shared draft not overwritten).
