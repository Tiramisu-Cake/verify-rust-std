# RAPx applicability and detector coverage: results

## Current gate-A continuation (new authorization)

IN PROGRESS from `1fc89566800f8152d218de7f9a757f665626f220`, owner-authorized
on 2026-10-06: preparation and six gate-A controls only; stop before B/C.
Separate budget 0/4 NEW hosted runs, each at most 90 minutes including setup,
one active. Ordinary runner/setup/classifier repairs are autonomous within
this budget. The old two attempts and one-correction allocation below remain
historical; the new authorization supersedes only their continuation stop.
No new detector result yet. Full scope/card: [phase](RAPX-APPLICABILITY-PHASE.md#current-gate-a-continuation)
and [experiment log](EXPERIMENT-LOG.md).

## Historical initial-session closeout

**INCONCLUSIVE — gate A stopped at setup, no detector hypothesis tested.**
The owner resumed
[the approved phase](RAPX-APPLICABILITY-PHASE.md) on 2026-10-06 from documentation
commit `ad54f67d655c4106762016fba47534c58601f3ec`. This report distinguishes
source review, actual detector observations and unexecuted target obligations.

## Source, profile and execution

- Fork Tiramisu-Cake/verify-rust-std, branch challenge-8/research. Entry tree
  clean, origin verified, fast-forward to the requested documentation commit;
  no queued/in-progress Actions. No unrelated changes were present.
- Actual target: `library/core/src/slice/sort/shared/smallsort.rs`, std blob
  `e555fce440872898e47fd5114f32eb15401d07df`, unchanged. The gate tests the
  alignment obligation needed at sort4's four copies, not the whole body.
- Diagnostic source `b55ae850d1cef67ddbcd02d8d97b4763c9c4a9f1`;
  [run37492790456](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37492790456),
  workflow smallsort-research.yml, proof rapx_applicability, rapx_gate A,
  budget 90 min; created 2026-10-06T16:04:30Z. Job began 16:04:37Z on a
  GitHub-hosted ubuntu-24.04 runner. All builds and executable diagnostics run
  there; server validation was `bash -n`, `git diff --check` and static reads.
- Two runs used out of four; the shared technical correction consumed; B/C
  unused and gated.
  Direct research-ref dispatch accepted the selection; no main-branch update.
- Frozen package RAPx exactly '=0.7.50', installation --locked; explicit
  nightly-2026-02-05 for installation and analysis. Reviewed upstream
  `7d61d9377033c48a4df8954f34cc076e97a93816`; package archive SHA256
  `e210328ce0e6c417ecf0498118ca0738f80851e9f2d204432a095ad703f8c0b8`.
  The read-only downloaded package VCS metadata names that commit and path rapx.
  The first hosted run obtained the archive/lock/sysroot evidence but stopped
  before executable-version/installed-source checks; the correction run audit
  did not complete.
- Diagnostic flags: --mode targeted, --crate rapx-applicability, one module per
  case, --postfix-repeat auto, --debug-contracts, -- --lib; prepare-targets
  precedes analyses. RAPX_LOG=debug, --cfg=rapx, -Zdump-mir=all. No checker,
  model, contract, kernel or std semantic changes; no skip-invariant flag.
  The fixtures call pinned toolchain core, not the repository core build.

## Experiment card and semantic boundary

Gate A hypothesis: RAPx emits source/destination Align obligations at
copy_nonoverlapping and distinguishes aligned pointers from misaligned pointers,
including a concrete size-zero type with alignment eight. The source-review
shortcut in check_align was only a candidate miss before execution.

Six functions in the checked-in [fixture crate](rapx-applicability/src/lib.rs)
are designed for individual selection; actual preparation/selection did not run. The ZST is `#[repr(align(8))] struct Z;`. A layout-only
binary is designed to report size/alignment without executing invalid fixtures;
it was not run. ZST negatives
use wrapping byte offset one from an aligned local raw pointer; no invalid
reference is formed. Since an aligned address is 8*n, its offset-one address
is 8*n+1, including wrapping arithmetic. Count one copies zero bytes; empty
ranges do not create an overlap violation. The intended defect is alignment.

The u64 negatives use distinct initialized [u64;2] backing arrays; the tested
pointer alone is offset one byte and the other remains aligned. The eight-byte
ranges fit within separate sixteen-byte allocations. No dangling, overlap,
invalid scalar or uninitialized-read defect precedes the copy. The aligned
ordinary control uses separate initialized one-element u64 arrays.

These concrete microfixtures test automatic unsafe-operation contracts. They
add no independent manual alignment assertion and do not assume the negative
property as a precondition. Expected positives: analyzed named body SOUND with
actual copy checkpoint and both Align obligations proved. Expected negatives:
the tested Align predicate fails at the copy, while the other remains proved;
Unknown, unsupported, skipped/missing checkpoint and setup are separate results.
An adverse detector result can coexist with a successful evidence-capture job.

Full target yardstick remains [SORT4-CONTRACT](SORT4-CONTRACT.md): unrestricted
valid T/F, initialized four-position source and possibly uninitialized writable
separated scratch, legal provenance/permissions/borrows and exactly one logical
ownership sequence. Normal return retains current V5 and initializes scratch
replicas pi(V5), with current callback/frame and full storage resources and no
borrow debt. For each panic k=1..5, recover current Vk/Qk/Hk after legal callback
effects, source ownership and raw scratch with its actual initialization state,
no sort4 writes, rollback or leaked resources. Ordering assumes preserved keys
and a fixed strict weak order separately; safety has no Copy/Freeze/purity or
no-panic restriction. Gate A proves none of those full posts or generic domains.

Decision map: critical reproduced miss or essential missing semantics -> NO-GO
and stop B/C; setup/unknown/ambiguous coverage -> INCONCLUSIVE or one permitted
technical correction supported by evidence; sufficient A pass -> gate B only.
Even all gates passing would stop before a full sort4 proof or tool changes.

## Observations

First run37492790456: **INCONCLUSIVE / setup failure**, job 221 s
(16:04:37–16:08:18 UTC). Exact package compilation/install succeeded (reported
1m 24s release build); pinned rustc is 1.95.0-nightly, commit
`db3e99bbab28c6ca778b13222becdea54533d908`, LLVM 22.1.0,
host x86_64-unknown-linux-gnu. The runner's direct `rapx --version` exited 2 and
printed usage: the direct driver parses RAPXFLAGS rather than argv. No installed
source comparison, layout, preparation, target, MIR or negative executed.
This result says nothing about alignment. Noncausal warnings: Actions Node.js
deprecation and git default-branch hints.

Before correction, the experiment card recorded the unchanged full target and
six-case domain, expected executable-version checkpoint and result-to-decision
mapping. The sole code change is `RAPXFLAGS=--version rapx`. Correction source
`772def3ce7e5e3585ac0c9a909f97afbcdb9a821`,
[run37493697524](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37493697524),
created 16:11:16 UTC, same selection/gate/budget. Both full logs and all
artifacts were inspected after completion; results below. No further gate-A
technical retries; B and C: NOT RUN because A did not pass.

First full Actions log SHA256:
`3e3fb0dc237c6724c083774524fb18996f712d8dfdf8da6a0e7f5d30800b03db`.
[Artifact11426930280](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37492790456/artifacts/11426930280),
10 files, zip digest
`a149d4858471a0f6ac58de351120abeb452303916cc76d8b51280c0b70d1122d`.
Artifacts downloaded outside the repository and all files/full log inspected.
Package Cargo.lock SHA256
`23822a0ee3ecb55aadb77fbf3d6c36d6f4ef16b037233c42c08c98ff9e8ef76c`.


## Final correction-run result

Run37493697524: **INCONCLUSIVE / setup failure**, raw runner exit 1,
job 16:11:22–16:18:02 UTC,400 s. The earlier version-query correction worked:
`RAPXFLAGS=--version rapx` and `cargo +nightly-2026-02-05 rapx --version` both
report 0.7.50; `cargo install --list` lists only that package and its two binaries.

First causal failure, at 16:17:58.205 UTC:

```text
FileNotFoundError: [Errno 2] No such file or directory:
'/home/runner/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/rapx-0.7.50/.cargo-checksum.json'
```

The runner incorrectly requires this metadata file. The registry source
directory was found, but the checksum lookup fails before the upstream fetch
and installed-source comparison. This is a diagnostic-runner preparation error,
not a verifier rejection, profile mismatch, unsupported memory operation,
Unknown obligation or a reproduced UB miss. No additional correction was applied:
the single shared technical correction is consumed, and the unspent B/C slots
are not authorized as more attempts at A. There is no active run or applied draft.

| Gate / case | Intended checkpoint | Observed result |
| --- | --- | --- |
| A: zst::aligned::copy | Both Align at copy, valid control | NOT RUN |
| A: zst::source_misaligned::copy | Source Align fails at copy | NOT RUN |
| A: zst::destination_misaligned::copy | Destination Align fails at copy | NOT RUN |
| A: u64_controls::aligned::copy | Both Align at copy, valid control | NOT RUN |
| A: u64_controls::source_misaligned::copy | Source Align fails at copy | NOT RUN |
| A: u64_controls::destination_misaligned::copy | Destination Align fails at copy | NOT RUN |
| B: generic copy/initialization/four UB categories | Prior A pass required | NOT RUN |
| C: actual c1 normal/direct panic and synthetic cleanup | Prior B pass required | NOT RUN |

Analyzed fixture functions 0; prepared fixture targets 0; measured fixture paths 0;
checked fixture obligations 0. No SOUND, UNSOUND, Failed or Unknown target result.
No actual unsupported operation was reached. No concrete layout measurements,
MIR, callback shape, cleanup path or executable classifier/control test was
produced. The declared ZST/u64 sizes and alignment remain the fixture design;
the layout-only binary was not compiled/run. The source-level ZST alignment
shortcut remains a suspicion, not an end-to-end reproduced false pass.

## Identity evidence and its limits

Both runs used x86_64-unknown-linux-gnu, nightly-2026-02-05 sysroot. Rustc
1.95.0-nightly commit `db3e99bbab28c6ca778b13222becdea54533d908`,
LLVM 22.1.0; Cargo 1.95.0-nightly (fe2f314ae 2026-01-30). Native dependencies
recorded: libz3-dev 4.8.12-3.1build1 (pkg-config 4.8.12.0),
libclang-dev 1:18.0-59~exp2, pkg-config 1.8.1-2build1. No dependency installation
was performed on the editing server.

Package archive SHA256 matches the frozen requirement in both runs; its
VCS metadata is the reviewed commit. Cargo.lock version 4 has 154 package entries.
All 104 compiled name/version rows in the second cargo-install.log match that
lock; no lock-update warning or evidence of dependency drift. This is a
read-only audit of saved build evidence, not a local compiler/verifier test.
The log retains every resolved compilation version.

Installed executable SHA256 in run37493697524:

| Binary | SHA256 |
| --- | --- |
| rapx | 39afc1cbd1e22bbda19444233c90fcc32d2fe0b22af1fe3e7b65cc97a4883f52 |
| cargo-rapx | b357ca2faf83ecbcb69acdf7ee6d1c0c213545674919934cf26cfcded1036382 |

The downloaded archive's relevant sources were compared read-only with the
reviewed upstream source before dispatch. However, the hosted audit linking
installed registry sources/checker/call/contract files to that source did NOT
complete. No claim that the complete executable/source audit passed. The native
profile is identified as far as the saved artifacts permit, without treating
missing metadata as an observed checksum discrepancy.

The sysroot ptr/intrinsics hash manifest has SHA256
`970c212bc73d318baab64efe264f83c82ca94f7919737731029c8226f6a6ed5f`.
It identifies toolchain core sources, but the verifier never analyzed them in
these experiments. Repository target SHA256 in both environment records is
`32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`;
std blob remains `e555fce440872898e47fd5114f32eb15401d07df`. There is no
repository-body or generic-safety result.

## Evidence, costs and next decision

Second full Actions log SHA256:
`c4ee3f87c3d2f4e7bc0b508ca3186f539baf49e4e5c8b62b8e4edcbe0f0ea86f`.
[Artifact11426617314](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37493697524/artifacts/11426617314),
11 files, 16,573 bytes, zip SHA256
`314f42868159afb7ce54b0197c56a8d8d0d4a4a29b3bdde56e985f13cc36ac20`.
Core record hashes:

| Artifact file | SHA256 |
| --- | --- |
| cargo-install.log | 21ffd82b9cfad2f280d263b6715533f2a59d8767c34acd3484ad5b1a8eb10972 |
| experiment-environment.txt | f050db4afcea5e50b017e7f81f632583a4559e59e4c8b8a188f0d2f7ee19fe8c |
| installed-package-Cargo.toml | 83bbcea83043db2da4a14abbf4fbd9975c9dcaef0c3b4f09edd6aef238eee850 |
| installed-package-Cargo.lock | 23822a0ee3ecb55aadb77fbf3d6c36d6f4ef16b037233c42c08c98ff9e8ef76c |
| package-vcs-info.json | 5625f0c14aaf643dd14f95e3bf080a6642110a0e2534b3fab25545215ba5f4b0 |
| rapx-version.txt | 160b57633e4e1197377f745808edbe4455f866dd6f7c28e3747aea77730aa731 |
| cargo-install-list.txt | f6185ad9ac55622b71e548984e8aa2ac428c8ec6a6feef8b92ed0a451fce94e4 |
| rustc-version.txt | 7fcaf1436fa62824527ec1ead2712e804a1e8bf1fb9669b0f4602b1d1111bc4f |
| sysroot-core-source-hashes.txt | 970c212bc73d318baab64efe264f83c82ca94f7919737731029c8226f6a6ed5f |
| sysroot-path.txt | 1f29118e5116fefa88eb2d9ee8ef698da52bbb347d6ce7286fa7915b7cc43f57 |
| target-libdir.txt | 7ea31b33565253e9fbca6ea2ec81204dd3c78cca48dafab7abeedeab7f2ef991 |

Both full logs and all 21 artifact files were inspected outside the repository;
no downloaded logs, generated source, build output or archives are committed.
Noncausal warnings in the second run: Actions cache/upload Node.js
punycode/url.parse deprecations and Node 20 forced to 24; git default-branch hints.
No fixture unsupported warning, skipped-target warning or semantic failure exists
because the analysis stage was never reached.

| Run | Job elapsed | Relevant setup cost | Verification cost |
| --- | --- | --- | --- |
| 37492790456 | 221 s | RAPx release build 1m 24s, plus runner/nightly setup | 0, NOT RUN |
| 37493697524 | 400 s | Prepare runner306 s; install/identity step 81 s, including RAPx build 1m 04s | 0, NOT RUN |

Neither run approaches the 90 min limit; no timeout/OOM. Per-case wall time/RSS
files are absent because no case ran. Used 2/4 runs: planned A and shared
correction. Planned B/C remain unused and conditional, not a retry reserve.

**Stop: INCONCLUSIVE.** No generic coverage was gained and no critical detector
miss was confirmed. The bounded phase closes before A's applicability decision;
B/C/full sort4 proof and verifier patches/upgrades remain unexecuted and
unauthorized. The public-contract admissibility question is still independent.

A next owner decision could authorize one newly bounded setup-and-gate-A retry:
replace reliance on optional Cargo checksum metadata with an archive-to-installed
source byte comparison, retaining exact archive/VCS/lock/executable identities
and the original frozen profile, then execute the same six controls. That is
a proposed preparation correction, not an applied patch or a permission to
reuse B/C slots. No next run is dispatched or promised.
