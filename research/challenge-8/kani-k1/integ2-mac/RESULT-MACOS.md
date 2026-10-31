# INTEG2 macOS autoharness — all candidate groups admitted

Run [41208001848](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/41208001848), workflow
395063112, head `391804160e`, library tree `b10a21505be73f26be50cd0e1c0f0c5f48773f9a` (bound before the run).
Command extracted literally from `kani.yml` (body sha256 e00605009c…), Kani checkout `9461e07a` = declared pin.
Runner: macos26 20261013.0424.1, Apple M1 (Virtual), arm64, 3 CPU, 7.0 GiB, swap 0 MB peak.

Kani exit 0, wall 5561 s (93 min, incl. Kani build and std compilation). Complete: 1943/1943 harnesses,
245/245 autoharness functions, 0 failures. SmallSort: 197/197 expected names, exactly once, all SUCCESS.
Max SmallSort VT 206.4 s (`merge::general_direct_u64_n9`); next 201.2 (`network_safety_unstable_u64_n30_to32`),
182.0, 167.3 (`network_safety_unstable_u64_n0_to17`, 380 s in the 2026-10-31 night organizer CI).
Sampler (5 s, ps): largest single cbmc 3.35 GiB; ≥3 concurrent cbmc in 435/1074 samples; ps errors 0.

Admission (threshold 300 s, every member SUCCESS, failed checks 0, source-derived covers all satisfied):
m9 206.4/150.8; start1 129.4/164.6/150.9 (covers 9/6/6); u8n9 107.9/116.1; s68const 16.7/34.5/72.2;
B u64 N2..5 const 7.2/7.3/14.2/23.7; 9 returns 3.2–26.4 s. **All 17 groups ADMIT** → no cfg demotion;
P1 = 197 ordinary (native inventory 27979544 on the same library tree), static P2 = 343.

The on-runner parser v3 reported BLOCKED (`summary.on-runner-v3.json`): two false positives of its own
checks, not of the run — 245 autoharness function blocks start with `Autoharness: Checking function`
(735 "orphan" events = 245 × 3), and std `should_panic` harnesses legitimately succeed with failed
checks. Parser v4 (this commit, tests added) recognises both; re-run on the downloaded log artifact
(gz sha256 1cd6261c…, deleted after parsing): integrity True, job_success True, 17/17 ADMIT (`summary.md`).
Single run, not the organizers' CI; a verbatim full CI with macOS remains required before submission.
