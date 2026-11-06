# K-1 run `renamemods-g1-20261106-01`: COMPLETE

- head `0504202814f16c4a962687c6933a4e43b171d45b`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `4f73c163c10ec2e1f5e7737d231ba9359efb919badc9c4c0232fb4edb5eb27b5`
- run 942bc6d1-191d-4777-acc5-d0d724564fde attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `inventory`, runner `gcb-e2-standard-4`, whole-job work budget 44 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg off
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS None KiB, wall None (MISSING)
- verify memory cap: MISSING, limit ?, cgroup peak incl. page cache ?, OOM kills None, swap None
- ordinary verify inventory: 233 names; names SHA-256 `9d3dbe8fd4f352c81dfdab68ebbdd89c06e93d8968fdf37fd460f2088ac8b0e0`
- inventory artifact SHA-256: `a4ef473682e40906076159123344c3166590a2151a10227f53f439dbddae8c83`

- memory peaks MISSING: sampled every ? s, None samples, largest sampled sum of RSS ? at ?; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` ee09ed6a89e51f7ba00034176b8a2cc2eccbcab5f9400a6d96ef8248fcd35028
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 40ee88392e3e1b0af82611394f9a30df259e22cad6a623bded49ba1a0adb954c

Notes:
- per-command memory peaks MISSING
- verify memory cap MISSING: no reason recorded
