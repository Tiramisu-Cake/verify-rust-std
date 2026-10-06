# RAPx applicability and detector coverage: results

Execution checkpoint: gate A dispatched; outcome pending. The owner resumed
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
  budget90min; created 2026-10-06T16:04:30Z. Job began 16:04:37Z on a
  GitHub-hosted ubuntu-24.04 runner. All builds and executable diagnostics run
  there; server validation was `bash -n`, `git diff --check` and static reads.
- One run used out of four; B/C and the shared correction slot unused.
  Direct research-ref dispatch accepted the selection; no main-branch update.
- Frozen package RAPx exactly '=0.7.50', installation --locked; explicit
  nightly-2026-02-05 for installation and analysis. Reviewed upstream
  `7d61d9377033c48a4df8954f34cc076e97a93816`; package archive SHA256
  `e210328ce0e6c417ecf0498118ca0738f80851e9f2d204432a095ad703f8c0b8`.
  The read-only downloaded package VCS metadata names that commit and path rapx.
  Hosted installed-source/version/lock/sysroot audit is pending.
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
are individually selected. The ZST is `#[repr(align(8))] struct Z;`. A layout-only
binary reports size/alignment without executing invalid fixtures. ZST negatives
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

Pending hosted evidence inspection. B and C: NOT RUN, pending gate A.
