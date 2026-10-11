# End checkpoint — Rust ZST repair session CLOSED

Owner `select-sort4`; worktree `/root/verify-rust-std-select-night`; branch
`research/night-select-sort4-cloud-2026-10-09`. Initial checkpoint
`69e8ffe5c8b7607cedd9295a4e0a3a53c0d3a38a`.
Phase `SORT4-NATIVE-C1-ZST-REPAIR-CLOUD-2026-10-11`.
Policy read `c7ca8c467aecf10a4b53039372ee97714f854ee3`.
Start 08:33:37 / main deadline 10:33:37 / finish-only ceiling 11:03:37 UTC.
Account closed `2026-10-11T10:39:30.317256Z`; final checkpoint `2026-10-11T10:42:29.632367Z`.
After the main deadline only the current Build, evidence, accounting and
checkpoint were completed. No future dispatch or automatic session is authorized.

## Model repair and native C1

Minimal [Rust size patch](rust-zst-size.patch), SHA-256
`19ee0d684e972f164f16f21926bde7d5d1edc1f9224a880c20120f9cb62f1074`, changes only
`src/verifast1.ml`: Rust struct size is nonnegative with the existing upper bound;
a complete entirely empty Rust field map has size zero. C/C++ positivity,
existing array/layout/alignment and permission rules are preserved. No type
representation, ownership, callback, kernel or solver rule was changed by the
model repair. Frozen snapshot unchanged; isolated Cloud application/build only.

Fresh model gates pass for generic guarded entry with/without unused MU scratch,
legal post-nonzero inference, concrete ZST/nonZST/MU/array/layout cases and C/C++
controls. Pre-guard positive-size assertions, reachable ZST false and missing
permission controls reject at their intended obligations. First matrix failure
was a missing existing layout lemma in the fixture; no semantic patch extension.

Fresh native C1 Build `ed016f05-c66b-4d9f-8be4-12b8c0271f8f`, exact proof/infra
`f1e139053eac06da27a4068b47b0d44cbca1cb73`: verifier exit 0, 196 statements,
reachable ZST-return mapped by source/MIR/AST/trace; full native source/tail,
opaque MU/F/thread/lifetime/type normal/direct-unwind/early/unit/free/leak posts.
Normal/unwind false controls reject at 226/210; admission/refinement/strict/
dead-code gates retained. All these prerequisites were freshly repeated in
subsequent C4 Builds, including the final run.

## Fresh native C1–C4 fragment

Capture `55f876c4` pinned the four actual comparisons and full source/MIR/AST;
its intended capture refusal was not proof. Bound candidate `d128e368` and
inventory diagnostic `310f38b5` refused before proof at the old count 282.
The diagnostic established actual body284/locals239/projections0/epilogue0/HRTB
F:T. Static index correction preserves both sizezero/len IfStmt nodes and every
root, with only callback locals relocated into four strict children.
Historical failures remain in their fresh reviews/log and are inconclusive,
not semantic negatives.

Final Build `3b7431bb-4e18-4921-b690-307e4ba7f984`, proof=infra
`8de4cda418c4772009359fbb90e7e7f34836cca0`, finished 10:33:48.564284 UTC:
verifier exit 0, zero errors, 485 statements. All 503 registered physical IDs
executed, including real ZST and len<8 return/free/leak paths. Four actual
operands (1,0), (3,2), (c,a), (d,b), sequential CURRENT, normal and all four
direct-unwind source/tail/opaque MU/F/thread/lifetime/type resources and complete
posts retained. Normal false rejects at 577; unwind false at 387/442/504/561.
Source/extrabody/malformed/mixed admissions refuse as intended. Default-off
parse refusal is not a semantic negative. Paired full MIR/refinement pass.

Archive `4e9c337e98d403d5959d0581c8739b4510cb5b94b977fae2ce0a947b35e4f6e4`;
complete controller delivery/config/input/receipt/text-log checks, plus all1053
inventory hashes independently verified. Source/pre/post AST and full observed
tool profile appear in [fresh review](FRESH-3B7431BB-REVIEW.md),
[index](FRESH-3B7431BB-INDEX.json) and [C4 base/result manifest](NATIVE-C4-BASE-RESULT-MANIFEST.json).
Combined patch `4599c1e74a60e61cc6f92c0892a1f855dbb7f163b4676bff975ef0221b902de2`;
C4 translator `66e266d3a36517d8c552b34ab17357b7b5d11192095e47672504533611c76124`.
Size file `bfbfb518fb9783afeeba9384e1431b6cd280c7da7713b9fdbfd15a8395b00207`;
kernel `37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`.

## Qualification and account closure

Profiles remain experimental/unaccepted; maintainer owns review/integration.
The guarded internal fragment retains the existing `T: FreezeMarker` domain of
`small_sort_general_with_scratch` (actual source220), not unrestricted
`sort4_stable<T>` (source606). Added research sizezero guard is not an established
actual caller guard. Full actual sort4, caller/as_mut_ptr binding, caller guards/
overflow, selector/C5/copies and generic ZST safety remain outside/unproved.
Old supplied C1→C4 PASS is separate. Legacy `native_c1_to_c4: NOT_RUN` is the
separate old driver path; the current `native_c4_bound` verifies four sequential
actual comparator expressions in one guarded native fragment.

Six terminal Builds: 339+398+428+466+430+465 = 2526/3600 conservative Cloud seconds.
All accounted, fully downloaded and integrity-verified. Unused1074 retired,
no carry. Own active/unresolved Builds and reservations: none. Ready request
withdrawn through client; coordinator schema2/own reservations0 independently
checked. Ledger CLOSED; profile cloud/dispatch disabled. No pending proof draft.
No merge, upstream publication, external messages or bounty submission.

Review packages: [model](MAINTAINER-ZST-REPAIR-REVIEW.md),
[C4](MAINTAINER-NATIVE-C4-REVIEW.md), [model rationale](ZST-REPAIR-RATIONALE.md),
[model full manifest](ZST-REPAIR-BASE-RESULT-MANIFEST.json),
[C4 rationale](NATIVE-C4-BOUND-RATIONALE.md), [ledger](BUDGET-ZST-REPAIR-2026-10-11.json).
Next step requires a new explicit session/budget. Review and integration remain
maintainer decisions; no automatic continuation is authorized.
