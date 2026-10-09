# MIR lifetime origin repair phase

Start20:16:40UTC, main cutoff21:16:40UTC, finishing cutoff21:46:40UTC.
Exact starting checkpoint a74d612731f41969e688326456b34b55a880c5a7; publication fbc063ce609cc549358e3bbc0f8b3a12b75b3945. Policy1fcd91eff1507fe0bd0620a23b578edb454f1c3e read from checkpoint.
Project worktree /root/verify-rust-std-merge-origin, branch merge/incoming-origin-20261009, starting HEADfbc063ce, git-dir /root/verify-rust-std/.git/worktrees/verify-rust-std-merge-origin. Tool worktree /root/verifast-merge-incoming-span, branch merge/incoming-span-lifetime-20261009, starting HEAD75099c958eb6a6d46016babf0a845a624f77d9ab; clean status confirmed by code owner.

Design: replace ordinary CallExpr lifecycle interception with internal AST storage statements emitted exclusively by trusted MIR StorageLive/StorageDead lowering. Store source location, original MIR local identity and translated local name; kernel resolves against translated declaration context. No source/ghost parser syntax constructs these nodes. Ordinary source calls use normal function resolution and diverging contract/terminator processing. Renaming markers is insufficient. Preserve path-local address epochs, resource cleanup and same-entry-Chunk authority; generic geometry remains disabled.

Actual obligation: unchanged generic CopyOnDrop tmp->tail span at diagnostic line69, caller insert_tail in actual SmallSort. Origin repair alone cannot remove the size/domain separation refusal, so do not rerun actual with only this repair. After origin, investigate exact runtime layout and concrete unit; prepare missing-rule/minimal reproducer if no sound patch is available. No supplied separation premise.

Validation: fresh Cloud source build, prior six controls with MIR/AST binding adapted to internal event shape; extern prototype/diverging route recorded separately as frontend rejection or verified ordinary-call semantic behavior; ghost/source forgery and targeted cleanup/normal/unwind cases. Frontend/setup failures earn no semantic negative credit. Existing proof outcomes are historical; replay creates no new proof. Independent implementation review remains necessary before integration. Own3600-second Cloud ledger; v2 coordinator/max2 unchanged, owner merge.

## Fresh first-build findings and exact MIR origin capture

Build6cf7f205 on01c832b2 compiled the profile and verified five of six controls;
retirement was INCONCLUSIVE because standalone exporter used preprocess-readonly
and verifier used default in-memory ghost preprocessing. Its MIR raw IDs differ
(_7 vs _12 for tmp1). Do not equate raw local IDs across those two MIR artifacts.
Next pipeline mirrors verifier's default exporter preprocessing so the origin
auditor checks actual AST events against the matching compiler input. FileLoader
returns transformed source in memory; it never writes source files (lib.rs
source fingerprints remain checked at every stage). Original readonly evidence
and classifications remain immutable; no old proof is promoted without replay.
Native C test verified both ordinary calls, then link failed because cached source
profile has no crt.dll.vfmanifest; next targeted verification uses documented -c.
Extern fixtures had incorrectly positioned req/ens inside Rust extern blocks
and failed frontend parsing; they provide no semantic negative or proof of an
extern-prototype rejection rule. Source/contract positioning is repaired before
next run. Concrete unit ghost and runtime-result assertions both failed at their
marked obligations, confirming that modeled extent cannot be used as actual
unit layout. The exact generic runtime rule remains missing.
