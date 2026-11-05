# K-1 run `loopreal-g1-20261105-02`: COMPILE_ERROR

- head `3a1a71036fc48708094c59e3b1c70252ce4fbf9b`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `8af5df8cdad82e52c3851d4caab263beb11a291ef437319feea9e2e94d9a5081`
- run 69ac5245-e83e-4d87-b8b6-68acd46b0e02 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 4 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 1290476 KiB, wall 0:43.20 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 23 samples, largest sampled sum of RSS 1.27 GiB at 42 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.22 GiB (≤13 GiB), seen 2–42 s, peak sample 42 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–42 s, peak sample 2 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `kani-driver` 0.01 GiB (≤13 GiB), seen 2–42 s, peak sample 2 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–43 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–42 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–42 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–43 s, peak sample 0 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–42 s, peak sample 2 s
  - simultaneous driver RSS 0.01 GiB at 2 s
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| loopreal::insert_tail_u64_backing8 | SUCCESS | NOT_RUN |  |  |  |  |
| loopreal::outer_loop_u64_backing8 | SUCCESS | NOT_RUN |  |  |  |  |
| loopreal::insert_tail_u64_backing32 | SUCCESS | NOT_RUN |  |  |  |  |
| loopreal::outer_loop_u64_backing32 | SUCCESS | NOT_RUN |  |  |  |  |
| loopreal::insert_tail_u64_backing128 | SUCCESS | NOT_RUN |  |  |  |  |
| loopreal::outer_loop_u64_backing128 | SUCCESS | NOT_RUN |  |  |  |  |
| loopreal::outer_loop_false_invariant_backing8 | FAILED | NOT_RUN |  |  |  |  |
| realcontracts::insert_tail_safety_u64_tail1_to4_backing5 | SUCCESS | NOT_RUN |  |  |  |  |
| network::unstable_freeze_noncopy_bytes86_fallback_n2 | SUCCESS | NOT_RUN |  |  |  |  |
| realcontracts::unstable_network_safety_u8_n9_stubbed | SUCCESS | NOT_RUN |  |  |  |  |
| assembly::safety_stable_unit_n16 | SUCCESS | NOT_RUN |  |  |  |  |
| assembly::safety_stable_unit_n32 | SUCCESS | NOT_RUN |  |  |  |  |

Error lines:
```
error[E0382]: borrow of moved value
   --> /workspace/src/library/core/src/slice/sort/shared/smallsort.rs:653:17
    |
637 |                 is_less
    |                 ------- value moved here
...
653 |             if !is_less(&tmp, &*sift) {
    |                 ^^^^^^^ value borrowed here after move
error[E0382]: borrow of moved value: `is_less`
   --> /workspace/src/library/core/src/slice/sort/shared/smallsort.rs:653:17
    |
601 | unsafe fn insert_tail<T, F: FnMut(&T, &T) -> bool>(begin: *mut T, tail: *mut T, is_less: &mut F) {
    |                                                                                 ------- move occurs because `is_less` has type `&mut F`, which does not implement the `Copy` trait
...
637 |                 is_less
    |                 ------- value moved here
error[E0382]: borrow of moved value
   --> /workspace/src/library/core/src/slice/sort/shared/smallsort.rs:700:39
    |
695 |             crate::kani::loop_modifies(&tail, ptr::slice_from_raw_parts_mut(v_base, len), is_less)
    |                                                                                           ------- value moved here
...
700 |             insert_tail(v_base, tail, is_less);
    |                                       ^^^^^^^ value borrowed here after move
error[E0382]: borrow of moved value: `is_less`
   --> /workspace/src/library/core/src/slice/sort/shared/smallsort.rs:700:39
    |
666 |     is_less: &mut F,
    |     ------- move occurs because `is_less` has type `&mut F`, which does not implement the `Copy` trait
...
695 |             crate::kani::loop_modifies(&tail, ptr::slice_from_raw_parts_mut(v_base, len), is_less)
    |                                                                                           ------- value moved here
error[E0382]: borrow of moved value: `is_less`
   --> /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/loopreal.rs:132:39
    |
 97 |     is_less: &mut F,
    |     ------- move occurs because `is_less` has type `&mut F`, which does not implement the `Copy` trait
...
127 |             crate::kani::loop_modifies(&tail, ptr::slice_from_raw_parts_mut(v_base, len), is_less)
    |                                                                                           ------- value moved here
error: could not compile `core` (lib) due to 5 previous errors; 1 warning emitted
error: Failed to execute cargo (exit status: 101). Found 5 compilation errors.
```

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` ee09ed6a89e51f7ba00034176b8a2cc2eccbcab5f9400a6d96ef8248fcd35028
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 40ee88392e3e1b0af82611394f9a30df259e22cad6a623bded49ba1a0adb954c

Notes:
- time -v max RSS 1290476 KiB exceeds the largest sampled command peak 1278800 KiB: a process grew between samples; use the time -v value as the true single-process peak
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
