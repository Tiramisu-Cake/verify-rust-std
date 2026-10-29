# K-1 run `valid-b-inventory-ordinary`: COMPLETE

- head `6ba5e109ea75c6301d7cbbe5ae0dd94f2d272451`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `aaffe536ce3dee61d72e70c4a68c74e40386565dad45397a3385f0ab00ab34e1`
- run bb71a182-76ec-4e8d-a6db-939c125a66f5 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `inventory`, runner `gcb-e2-standard-4`, whole-job work budget 60 min, harnesses in parallel 1, uninit checks off, controls cfg off
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS None KiB, wall None (MISSING)
- verify memory cap: MISSING, limit ?, cgroup peak incl. page cache ?, OOM kills None, swap None
- ordinary verify inventory: 144 names; names SHA-256 `1a69bde3cc13e9dc7927935f7e48ede702c87809b97167c87235233d89282d7a`
- inventory artifact SHA-256: `0f8feb4e26ec6ecce4df119a273cd394a9f5e46932fb124c099146d2dd65dec1`

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
