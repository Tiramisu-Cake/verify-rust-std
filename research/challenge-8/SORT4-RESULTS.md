# Actual `sort4_stable`: phase closeout, 2026-10-06

The approved phase is complete. Both independent functional theorems passed
on the actual repository body. Generic safety remains open; the existing
frozen-profile evidence supports an architecture checkpoint, not a new probe
or a semantic patch. No later phase was started.

## Exact source, run and proof domain

Approval: `68fcc98b79fc69b717d3e2ed42605cae8b4ffc05`.
Proof source: `1bc9cb718efc07315082334cded2d2362ecbbde1` on
`challenge-8/research`. [Run 37459631500](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37459631500)
was dispatched once at 11:55:16 UTC, selection `sort4_functional`, budget
90 minutes including Kani cold setup/build and both sequential proof stages.
The common workflow runner preparation precedes that runner budget. The
GitHub-hosted ubuntu-24.04 x86_64 job completed successfully at 11:59:55 UTC.

Target: [actual SmallSort source](../../library/core/src/slice/sort/shared/smallsort.rs),
Git blob `e555fce440872898e47fd5114f32eb15401d07df`, unchanged runtime and
generic signature. The hosted source audit and an independent comparison of
the downloaded artifact against this commit agree: the complete original std
file is unchanged, followed only by checked-in cfg(kani) [sort4.rs](sort4.rs).
Both harnesses call `super::sort4_stable` directly. No target stub, summary,
rewritten sorting network or imported proof is used.

| Actual-body harness | Exact theorem and assumptions | Checks / covers | CBMC verification time |
| --- | --- | --- | --- |
| `prove_sort4_values` | Four independently symbolic full-range i32 inputs; pure nonpanicking `<`; separate initialized source `[i32;4]` and destination `[0;4]`. Destination nondecreasing, exact input multiset, source unchanged. | 0/267 failed; 4 unreachable; 12/12 covers | 5.2731695 s |
| `prove_sort4_stability` | Four symbolic i32 keys; `#[repr(C)]` Copy records `{ key: i32, original_id: u8 }`, input IDs0..3; pure nonpanicking comparison of keys only; separate initialized four-record buffers. Every complete input key/ID item appears exactly once, keys nondecreasing, equal-key IDs increasing, source unchanged. | 0/233 failed; 4 unreachable; 6/6 covers | 4.0439544 s |

The i32 multiset post compares occurrence counts for every original value.
Equal array lengths make that exact, including duplicates. The tagged post
counts each complete original item once; four distinct IDs and four output
slots exclude missing, duplicate or additional items. Adjacent equal-key IDs
increase, and sorted keys make each equal-key group contiguous, establishing
stability throughout that group. Padding bytes in the eight-byte tagged layout
are not compared or claimed initialized; only its initialized fields are read.

All three explicit posts in each harness are SUCCESS. The values covers include
ascending/reverse, all-equal/mixed duplicates, MIN/MAX, the four c3/c4 patterns,
pair inversions and the final unknown-pair exchange. Tagged covers include
duplicates/all-equal, extremes, ascending/reverse and final exchange. None is
unreachable. These are representative reachability checks, not an assertion
that all 32 unconstrained decision strings arise from pure ordering.

Harnesses use unwind6 without suppressing unwinding assertions. The complete
CBMC traces show sorted/stability helper loops ending after three iterations
and count/permutation/source helpers after four, below the bound. No loop
reaches the cutoff and no unwinding-assertion property is emitted. Each log
reports exactly one successful harness, zero failures. Four non-cover
UNREACHABLE checks concern two usize abs_diff overflows, formatting shift
overflow and is_aligned_to subtraction overflow, not target posts. The three
unsupported-operation guards per harness (unallocated-pointer reasoning,
panic runtime and caller_location) are SUCCESS: their unsupported paths are
not reached. No failed unsupported check or front-end failure is hidden.

Full Actions log (4448 lines), both complete stage logs and all artifacts were
inspected. The logs contain 22 direct actual-sort4 properties per harness,
including ten reference alignment and ten invalid-pointer checks at the five
actual comparison sites. Copy alignment, overlap, readable source, writable
destination, null/dead/out-of-bounds pointer checks also pass. Compiler
edition/future-incompatibility warnings do not change this proof result.

## Frozen profile and cost

Kani 0.67.0, source `152c6a8c875d9886a67e229247b4826d6105ccfd`;
Rust nightly-2026-02-05; CBMC6.10.0, CaDiCaL3.0.0. Repository default
checks through unchanged scripts/run-kani.sh, `--exact --jobs 1`,
`--object-bits 12`, repository unstable options and `--no-assert-contracts`.
There are no proof contracts/stubs here. No new suppression flags or explicit
uninit/valid-value/extra-pointer profile are used. This is a functional baseline.

Runner wall193.07s, peakRSS1810908KiB. Values stage164.64s includes cold
Kani setup/build and std compilation; stability stage28.39s includes another
24.00s std compilation. Combined CBMC verification9.3171239s; remaining
runner wall183.75s is setup/compilation/orchestration. The whole hosted job
was275s including common preparation, cache and artifact handling. All executable
work was hosted; local checks were reading/log analysis, git diff --check and
bash -n only. Documentation closeout is not a new proof run.

| Audited input/tool | SHA-256 |
| --- | --- |
| Original smallsort.rs | `32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959` |
| sort4.rs | `dc33133c822833f2b881b0f11e1c595a5873c43c08cd4e0d50b4de71beb3c477` |
| run-sort4.sh | `a3d80fc54cee2787e39c99a83563b1379a4c874e113208a3bfd0dd9283240e23` |
| scripts/run-kani.sh | `059abb4036e352b72051bd59888849a35322d89b6718190415cde71f527a4d02` |
| kani-version.toml | `b2c99f41fc652d96a37e52c1701182ebd92f5b782a734b9a4a06b3e92e4826fd` |
| rust-toolchain.toml | `20180f8307182dce745e0304bcbee56ee2a85fc7608392b2c8b266dfe533c78c` |
| Hosted kani-driver binary | `9ae446cbe90b2eb9a394506d83e26624de675c3fd0eb80f5674ff4fd2d61d842` |
| Hosted CBMC binary | `05f93fd2f2ba6247b345f2bfb3d74c38402966515c65ff69f94adf7a674593f0` |

Workflow exposure was26a43bed5b162e542a4e0cc7cbf5ce08bd4d4bee on research;
only its two workflow lines were cherry-picked onto default branch at
3d8c8c082a69dbb66c4ab566892e6be71d87a86d. No research-history merge or trigger
change occurred. Raw logs/build output remain outside the repository.

## Safety categories and next decision

| Required UB category | Result in this phase | Remaining boundary |
| --- | --- | --- |
| Dangling/misaligned access | Default reference/copy alignment and pointer/read/write/bounds checks pass in both concrete domains | Arbitrary allocations, aliasing/provenance, ZST and unrestricted generic T/F not established |
| Uninitialized reads | Source and destination fields are initialized by construction; explicit uninit instrumentation NOT RUN | No separate target uninit theorem; generic scratch/raw reads and padding semantics need applicable checking |
| Immutable-byte mutation | Destination is mutable in the chosen domain; no target detector claim | Known immutable-store detector gap in37397720683 remains |
| Invalid values | Concrete i32/u8 fields have unrestricted valid scalar bit patterns; explicit validity instrumentation NOT RUN | CopyNonOverlapping validity instrumentation unsupported in37396688760; generic validity not established |

The [full contract/caller audit](SORT4-CONTRACT.md) covers separation across
copies, single ownership, actual scratch ranges, non-Copy/non-Freeze/ZST and
callback effects/panic at each comparison. This is source analysis, not a
checked generic normal/unwind proof. The short source SAFETY comment omits
per-copy non-overlap and ownership policy; concrete callers' separation must
not silently strengthen the universal target contract.

The [generic-safety decision](SORT4-SAFETY-DECISION.md) maps the existing
tuple ownership, HRTB Output, natural-block recovery and direct-unwind evidence.
No new existing-semantics route was identified and no generic diagnostic was
dispatched. No patched VeriFast profile or semantic change was introduced.

Recommended next decision: review a narrowly specified source-derived tuple/HRTB
capability and complete normal/direct-unwind borrow-recovery route, with trust,
admissibility and positive/negative regression criteria BEFORE authorizing
implementation. Resolve the overlap/ownership contract explicitly alongside
that review. Choosing roadmap stage2 instead needs separate phase approval and
will retain the same generic callback/ownership blockers. The functional
theorems close this phase's independent work, not public generic safety or
the whole Challenge8 requirements. No active research run; insertion draft
remains unapplied and unverified.
