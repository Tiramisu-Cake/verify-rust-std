# K-1 run `kani3300-t1b-a-20261111-01`: RUNNER_ERROR

- head `0f399a76b758de89d9ddd60cfea1f4f22d0904c6`, Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, request sha256 `b4bdf24b8808c48c366974bd0acb3740f129f21c4fb209c9ea5dc4177dc54398`
- run c2bec5fd-c0dd-4749-bdb0-99ac0c81a59c attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build failure
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 3 min, harnesses in parallel 1, uninit checks on, valid-value checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit None
- whole run, including compilation: max RSS None KiB, wall None (MISSING)
- verify memory cap: not tracked by this lane

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|

Inconsistencies:
- missing/inconsistent Kani patch/tree/version/build identity

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` d51f9c59823339dfd211e0e1226e6a372f4816d2ef6c86a68cce2676dc796215
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/diagnostic_trace.py` 0fe9ba94febceb919beab22da4f29fd8057765941c9d1f23b0222234fd73b49e
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` e45ccf9a2b4fddadeb78037293468f7e537865303abf7f7ec72fbe897a270246
- `research/challenge-8/kani-k1/tools/k1g.sh` 52612fefa011f88a42bbc3f5f7c29e6b79f6de73f72a205c1592185afadf64a2
- `research/challenge-8/kani-k1/tools/kani_k1.py` 707a8ca8ddcbcfd3127598a7c4b30ccde72b3454d6e1526bbd16c4bacce4b573
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 7dca0aa5bf9467c6c4fb4323dabc12254f6372f5f01af096420583bc2b5c9ca3
