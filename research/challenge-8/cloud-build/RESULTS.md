# Cloud Build migration evidence

Checkpoint: 2026-10-09; phase still in progress. A is accepted for infrastructure;
B stopped at source access, and C has not run. No new actual Rust proof claim.

All evidence prefixes are
`gs://smallsort-ci-evidence-504462351565/cloud-build/<BuildID>/`.
VPS downloads verified archive SHA256, every included file, external metadata,
submitted config hash, input SHAs and upload receipt for the four available
archives below. Missing initial evidence is recorded explicitly.

| Lane | Build ID | Final / original exit | Conservative seconds |
| --- | --- | --- | ---: |
| Initial smoke setup | 7bda20f0-cef7-4ff4-8c21-697374572b34 | FAILURE; upload127, no archive | 39 |
| Storage success | fd0020bd-967d-4e4b-ac20-83c578733389 | SUCCESS /0 | 47 |
| Managed error | 63862150-33e7-4b9d-b692-1231f9c34520 | FAILURE /42 | 54 |
| Internal timeout | 6604590a-f626-4ca0-81da-71f3d9091e25 | FAILURE /124 | 59 |
| B source preparation | 3e4c62e0-744b-4278-b10e-fc74f599dbe7 | FAILURE /128 | 81 |

Total280/3600, remaining3320. Charges are ceil(createTime–finishTime), including
queue, preparation, execution and upload; API execution intervals are separate
in [the ledger](BUDGET.json). Two rejected API requests created no Build and cost
zero seconds. Historical GitHub budgets and owner setup smoke are separate.
Machine API: E2_STANDARD_2; observed nproc2, MemTotal8147688kB, Ubuntu22.04.5,
x86_64. Per-stage time/RSS files will be produced by B/C once source loading works.

| Build | Infrastructure SHA | Input proof SHA | Archive SHA256 |
| --- | --- | --- | --- |
| fd0020bd | ac74f00c27207a0f23660b6a4de2e625dbec050e | 89e0a36f8df67bb2f66cf0564f497a0a4bad4aac | dbbc6c7d8294ca6d5360e7807ec2c0c12e50b6997e4540b371b869f9620c387e |
| 63862150 | ac74f00c27207a0f23660b6a4de2e625dbec050e | 89e0a36f8df67bb2f66cf0564f497a0a4bad4aac | d7416a4a8223dfca3dc76beb6166fcf1f1a0272ed658adc1dbf326c070387ab5 |
| 6604590a | 0de62646ddfdc36a8f2254a555f9a35cba94b000 | 89e0a36f8df67bb2f66cf0564f497a0a4bad4aac | 1e103e19acedf068ed84b8ee95812fdbc2ea9e19675dbd010b1c4e81841b044c |
| 3e4c62e0 | f694acddad88d4c353850f3a170adb7adb30bdb0 | a0cfd30e066acbaf1b5406cd9773f54388cc45be | c474f40ca1209292cfafbb1f7424a8d2c58bb22e2b1fdda0e395dcf1e532b995 |

All A proof-acceptance flags are false; only the success probe has smoke_success.
The error and timeout logs preserve their causes and upload never overrides the
failed final verdict. B has incomplete proof evidence because no tools/fixtures
ran. Its full preparation stdout/stderr and original Git failure are retained.

B comparison: frozen stock fixtures at
`a0cfd30e066acbaf1b5406cd9773f54388cc45be`, historical run37694000195. Planned
matrix retains stock u32/raw pointer positives, false posts, unwind/cleanup and
dead-code controls, including historical INCONCLUSIVE generic-forget limits.

C comparison: constructor fixtures at
`1378f0ffc8342233349fae3df5a938c4a021c8d7`, historical accepted O3 run37700450091.
Historical O3 runner applies the same two patches: S6 candidate
20f7d07ac9bdaca7c46f737b89925dfac3f4cef66c3f5d48aa9634ac949dbc1c, then CFG
593d09405379974ffbc475c2e0b65d648d8a6913f55b765dd0c3bebdc0922781.
Only the constructor matrix is selected, not the whole eight-stage S6 gate:
16 source/proof cases, nine typed MIR admission mutations, ten native controls,
stock/patched false-post and pointer-frame controls. Actual callee stays NOT_RUN.

Pinned VF source f76012fb518703b1d98e243ac4f487f16877cfcb, nightly2026-09-25
compiler f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f, std base
cd371e035c7e573760c43bf934d53e8118ee3e7d. New source-built console hashes will
be recorded separately; byte identity with GitHub binaries is not assumed.

The pinned-input archive fallback is prepared pending explicit owner approval
because it changes the requested public Git fetch route. It transfers committed
source objects only, checks original commit/tree/blob identities and source-file
hashes, and needs no credential export or cloud resource changes. See
[commands and second-direction requirements](README.md).
