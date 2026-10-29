# K-1 run `valid-b-inventory-controls`: COMPLETE

- head `cd2af83cc7ea2320a148262b74481fa43636b1b8`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `88d81bbc3f131240237549fee59be089b0e5954b734866117e6d6550a8f80d9d`
- run e489cd59-0518-41fc-bd37-4fbd0948c859 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `inventory`, runner `gcb-e2-standard-4`, whole-job work budget 60 min, harnesses in parallel 1, uninit checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS None KiB, wall None (MISSING)
- verify memory cap: MISSING, limit ?, cgroup peak incl. page cache ?, OOM kills None, swap None
- ordinary verify inventory: 423 names; names SHA-256 `4d52da0df37bcedfbf9da26666bb5c8199207cdd09e86763e032754fef7a9926`
- inventory artifact SHA-256: `ff9830c81b24e3d154efbf0b1705ac8e7f09bdddc9bcc3280812170d4baa7e53`

- memory peaks MISSING: sampled every ? s, None samples, largest sampled sum of RSS ? at ?; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- per-command memory peaks MISSING
- verify memory cap MISSING: no reason recorded
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
