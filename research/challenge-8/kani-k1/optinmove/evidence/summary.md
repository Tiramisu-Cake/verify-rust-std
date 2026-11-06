# K-1 run `optinmove-g1-20261106-01`: COMPLETE

- head `3b12f9cc0d2a11ab0a1a7df00e5aa93624c212cf`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `d283842f2e85c4a1910f63039f8b98af675e0bda182046cf1d849dfb5cdd88be`
- run 242b83e1-d9bc-46d9-a504-1cd3e929fcf0 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `inventory`, runner `gcb-e2-standard-4`, whole-job work budget 44 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg off
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS None KiB, wall None (MISSING)
- verify memory cap: MISSING, limit ?, cgroup peak incl. page cache ?, OOM kills None, swap None
- ordinary verify inventory: 233 names; names SHA-256 `7b466e9686cdf5f56c3a8359464399b13652f6ced336b479eb01cdb1e048c738`
- inventory artifact SHA-256: `21e1203a1d34be93715bf25d26caa8ddaae2ffa78cc2662ef479d13b585b5646`

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
