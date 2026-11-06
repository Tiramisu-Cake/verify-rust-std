# K-1 run `integcheck-g2-20261106-01`: COMPLETE

- head `da620e719217707c9f8bde005abb57f8519dcabf`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `82ceb5befff1ea704280139081bbedeb04ebb103661432e540deee0aa1b62d6a`
- run d32340b9-f056-4d53-8d91-a9562f00f08b attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `inventory`, runner `gcb-e2-standard-4`, whole-job work budget 44 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS None KiB, wall None (MISSING)
- verify memory cap: MISSING, limit ?, cgroup peak incl. page cache ?, OOM kills None, swap None
- ordinary verify inventory: 246 names; names SHA-256 `d142077ebe2c76d8f6e2ffc34727f1e44be24bde7388a56233725db5d1ad110a`
- inventory artifact SHA-256: `fe248427164f5b1f38d8ff5a4b4d2a6f5b15bd0157aeac876a87a17f6bdc7d9f`

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
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
