# K-1 run `traitpfc-g3-20261110-01`: COMPILE_ERROR

- head `55a7fd1c8ada1590ab571b040a6256219ef75e63`, Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, request sha256 `4593460dd782ee6437fd9d2b28398f46ce62a5fa62df53f54324fee4ea6faec7`
- run 9d94cb84-55e1-4cae-a55b-9597ddd81d87 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 5 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 1311268 KiB, wall 0:52.36 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 28 samples, largest sampled sum of RSS 1.30 GiB at 52 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.25 GiB (≤13 GiB), seen 4–52 s, peak sample 52 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–52 s, peak sample 38 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `kani-driver` 0.01 GiB (≤13 GiB), seen 2–52 s, peak sample 2 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–52 s, peak sample 2 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–52 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–52 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–52 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–52 s, peak sample 2 s
  - simultaneous driver RSS 0.01 GiB at 2 s
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| trait_contracts::stable_sorts_permutation_u64_len2 | SUCCESS | NOT_RUN |  |  |  |  |
| trait_contracts::stable_sorts_permutation_u64_len3 | SUCCESS | NOT_RUN |  |  |  |  |
| trait_contracts::freeze_sorts_permutation_u64_backing4 | SUCCESS | NOT_RUN |  |  |  |  |
| trait_contracts::freeze_sorts_permutation_u64_backing5 | SUCCESS | NOT_RUN |  |  |  |  |
| trait_contracts::unstable_sorts_permutation_u64_backing4 | SUCCESS | NOT_RUN |  |  |  |  |
| trait_contracts::unstable_sorts_permutation_u64_backing5 | SUCCESS | NOT_RUN |  |  |  |  |
| trait_contracts::verified_forwarding_sorts_permutation_u64_backing5 | SUCCESS | NOT_RUN |  |  |  |  |
| trait_contracts::rejects_high_bit_corruption_u64_len3 | FAILED | NOT_RUN |  |  |  |  |
| trait_contracts::rejects_changed_multiplicities_u64_len3 | FAILED | NOT_RUN |  |  |  |  |
| trait_contracts::rejects_reverse_pointer_sorted_u64_backing5 | FAILED | NOT_RUN |  |  |  |  |
| trait_contracts::rejects_function_item_sorted_u64_backing5 | FAILED | NOT_RUN |  |  |  |  |
| trait_contracts::freeze_frame_function_item_u64_backing5 | SUCCESS | NOT_RUN |  |  |  |  |
| scratch_geometry::stable_u64_min_scratch_n2 | SUCCESS | NOT_RUN |  |  |  |  |
| forwarding_contracts::unstable_byte_n2 | SUCCESS | NOT_RUN |  |  |  |  |

Error lines:
```
error[E0308]: mismatched types
   --> /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs:245:73
    |
245 |     let enabled = <() as SortModel<u64, _>>::enabled(SortEntry::Freeze, &cmp, v.len());
    |                   ----------------------------------                    ^^^^ expected `&fn(&u64, &u64) -> bool`, found `&fn(&u64, &u64) -> bool {trait_less_u64}`
    |                   |
    |                   arguments to this function are incorrect
    |
error[E0308]: mismatched types
   --> /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs:261:73
    |
261 |     let enabled = <() as SortModel<u64, _>>::enabled(SortEntry::Freeze, &cmp, v.len());
    |                   ----------------------------------                    ^^^^ expected `&fn(&u64, &u64) -> bool`, found `&fn(&u64, &u64) -> bool {trait_less_u64}`
    |                   |
    |                   arguments to this function are incorrect
    |
error: could not compile `core` (lib) due to 2 previous errors; 1 warning emitted
error: Failed to execute cargo (exit status: 101). Found 2 compilation errors.
```

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` d51f9c59823339dfd211e0e1226e6a372f4816d2ef6c86a68cce2676dc796215
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 7dca0aa5bf9467c6c4fb4323dabc12254f6372f5f01af096420583bc2b5c9ca3

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
