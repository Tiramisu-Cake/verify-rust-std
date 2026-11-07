# K-1 run `insertpfc-g2-20261107-01`: COMPLETE

- head `78d7112ea367dd9a23e588367f2b436876778c0e`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `28a7f899e75b797d9799d15fd38cc3e2c49311d181406b363b930b3d7d6c9ed7`
- run 8de198b9-953d-4b19-9eb2-76f90e5a14a4 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `inventory`, runner `gcb-e2-standard-4`, whole-job work budget 44 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS None KiB, wall None (MISSING)
- verify memory cap: MISSING, limit ?, cgroup peak incl. page cache ?, OOM kills None, swap None
- ordinary verify inventory: 248 names; names SHA-256 `e93fdc6c597fb8866b275f11f8d06f6d8a901212d949f2a1890d1caac9a3d342`
- inventory artifact SHA-256: `11ee59c3b5d9c119fc3525fccc22433ce44b6ab5582cc8e1d65eadd83aa6b9e7`

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
