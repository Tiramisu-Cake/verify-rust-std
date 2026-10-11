# Maintainer review — source-specific native C4 candidate

Status: experimental and unaccepted. The bounded four-call native C4 fragment
freshly reaches VF0, but no project-level C4 proof credit is awarded while the
profile is unaccepted. This note records that distinction and remaining boundary.
The separate [ZST repair review](MAINTAINER-ZST-REPAIR-REVIEW.md) covers the Rust layout
model change and its gates; this note does not duplicate that review.

## Candidate and source boundary

The candidate verifies the four actual sequential comparator calls in the
`sort4_stable` prefix captured inside the guarded
`small_sort_general_with_scratch` source target. The current `native_c4_bound`
fragment contains the C1, C2, C3 and C4 expressions together; this is distinct
from the raw result’s legacy separate `native_c1_to_c4: NOT_RUN` driver-path
field, which is not the current target path. It binds each compiler-derived
`FnMut` call and `FnOnce::Output = bool` projection using the existing per-call lifetime
and `CURRENT` recovery machinery. The four direct-unwind edges retain their
captured cleanup and full resource restoration; the normal path keeps its
assertions, recoveries, current-source splits and final posts. It does not add
generic callback, alias, ownership, `MaybeUninit` inverse, parser, kernel or
solver rules. The pinned source target already has `T: FreezeMarker` (source line 220); that
existing bound is not added by this patch. The separately named `sort4_stable`
source at line 606 has no `T` bound, so this fragment does not prove that
unrestricted generic body. The generated fragment keeps the ZST guard,
`len < 8` path, `&mut [MaybeUninit<T>]` scratch and unrestricted
`FnMut(&T, &T) -> bool` signature.

This remains an experimental source-specific translator overlay. It does not
verify the external SmallSort caller, selector/C5/copy path, or a callable
summary. The four-call fragment is not a complete proof of `small_sort_general`
or generic ZST safety. The admitted source, full MIR and original AST are
identified by the capture hashes below; a green diagnostic fixture would not
by itself discharge the remaining trust obligations.

The exact source-specific design and pins are recorded in the [bound
rationale](NATIVE-C4-BOUND-RATIONALE.md), [bound manifest](NATIVE-C4-BOUND-MANIFEST.json),
[capture manifest](NATIVE-C4-CAPTURE-MANIFEST.json), and [ZST base/result
manifest](ZST-REPAIR-BASE-RESULT-MANIFEST.json). The [C4 base/result
manifest](NATIVE-C4-BASE-RESULT-MANIFEST.json) carries the full frozen base,
fresh C1 profile and observed d128/310f/3b743 C4 tool profiles, while separating current
expected corrected hashes from builds that have actually completed. The ZST
manifest documents the separate Rust layout repair, not C4 acceptance.

## Patch chain and pins

All translator outputs use VeriFast source HEAD
`f76012fb518703b1d98e243ac4f487f16877cfcb`; kernel SHA-256 is
`37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`.
The C1 translator base is `381e80ebe9a789877ee9d0e860da386f7692f54879b39775e01267f0db6f53d6`.
The native C4 capture overlay (`native-c4-capture.patch`, SHA-256
`a67b4b11a0f4c2e3e7b3d766c47b4ddbd59d6cb46f84114ce05db82679b4d944`) yields
translator `b1faa4cd7fa1ca09b3368247e19ae525898e2c006aa7d11a9479eba67029f051`.
The d128 overlay was SHA-256 `7e52f32e7ad3c1e7a1d016fd068870af52da7f69f8b7fd044226bc9ec98e0dde`
and produced translator `0f94a83db283d5373e82e2c11c1eb6fde1f0bef300d5bf67ecd40ad8339943b7`;
its combined patch was `c04ea90f7ee5967b6a2b0ae0bec23fd764aac8adfb4086a06245ace54d6c7fda`.
The later 73669196 diagnostic kept the old root indices and expected output
`a1be12ce…`; terminal Build `310f38b5` confirmed the inventory
284/239/0/0/F:T and refused before proof at its old 282 gate. It is not a result
for the corrected candidate. The corrected bound overlay SHA-256 is
`be23d8789275ac9fe2db28d3f3e407063ae774d922908ff7c9c051e6f259155a` and yields
translator `66e266d3a36517d8c552b34ab17357b7b5d11192095e47672504533611c76124`.
Its combined patch SHA-256 is
`4599c1e74a60e61cc6f92c0892a1f855dbb7f163b4676bff975ef0221b902de2`, from C1
base `381e80eb…` to that output. Fresh Build 3b743 recorded the exact translator
output and unchanged pinned kernel/verifast1 hashes; the profile still has not
been accepted.

The source/MIR/AST certificate is unchanged across the d128 run and diagnostic
follow-up:

- Verified fixture `0f92a609c898df5271cbafd04cea688bf7b46c8b4786f8313b8ff99db995e9c4`; ghost-stripped original `9628df15e3a42643d671bd1e9f5684e0bdd81162e26ab8233ce704a9657942df`.
- Normal full MIR `b0da712d2b16c76d1baac91ae69c591ddeab308a2242e196fe876fd27e35e24d`; readonly full MIR `79c16a30be7b2921ccdaa35c66aac496f236d900130fff72a36b81524e50ef86`.
- Pre-transform full AST `65b9ddf282ab3b8d123bba3725600528936ff09e236c4261841d61f66cb5ae18`.

The d128 Cloud tool retained the pinned kernel and verifast1, applied the
combined translator to `0f94a83db283d5373e82e2c11c1eb6fde1f0bef300d5bf67ecd40ad8339943b7`,
and rebuilt its console. At that point, corrected output `66e266d3…` was only
expected. Build 3b743 subsequently recorded that output and the pinned kernel
and verifast1; the current profile remains `profile_accepted: false`.

## Earlier fresh evidence and inventory blocker (superseded by the 3b743 result below)

The published source/candidate sequence is: `a0343cec1c1874d58d78a8c3d2f290541c8c4837`
captures the exact native source fragment; `0c1bd9d70635776d587489163384b8c4f25b9d1b`
records the provenance and was the proof input for capture Build
`55f876c4-c3a7-4a4f-87b4-9242a3ad660b`; `0d6e4ac0312ccddfc2daee8a973d4e12a4e707a6`
adds the C1–C4 bound candidate and controls; `70ea6f49fef34495313b98ca5192c1b99164d30b`
packages the equivalent combined overlay; and `aea868bfd3ac9519ae3a51112cd8af82d9b29171`
was the proof input for d128 Build `d128e368-9a50-4c1a-8e74-64d71c51bfa0`.
Commit `736691964dd733b67ded1a683efe5d586f5952f0` adds diagnostic inventory
printing but retains the old root indices; Build `310f38b5` completed and is
distinct from the corrected source. Current candidate commit
`8de4cda418c4772009359fbb90e7e7f34836cca0` corrects those indices and is
published. The corrected commit was used by Build `3b7431bb-4e18-4921-b690-307e4ba7f984`; its bounded-fragment result is reviewed below.

Build `d128e368-9a50-4c1a-8e74-64d71c51bfa0` used proof/infra commit
`aea868bfd3ac9519ae3a51112cd8af82d9b29171`, completed successfully as a
collector run in 466 seconds, and delivered complete evidence. The fresh model
gates and native C1 binding/control gates passed. C4 paired normal/readonly
MIR and refinement passed on the exact source pair. The C4 positive and all
five intended false controls stopped before admission and post-transform AST
with the same error:

```text
Fatal error: exception Failure("NATIVE-C4-BOUND: complete native AST/HRTB inventory")
```

Those C4 cases are inconclusive frontend/setup failures, not proof negatives.
The four source/extrabody/malformed/mixed admission controls reached their
intended refusals. Default-off remained unadmitted but failed at parsing, so
that case also gives no semantic negative. Raw evidence and the independent
review are in [FRESH-D128E368-REVIEW.md](FRESH-D128E368-REVIEW.md) and its
[index](FRESH-D128E368-INDEX.json); archive SHA-256 is
`b0628ec500d606afbe059c50855601189298075b9a8a85ac45c0ee7b457fc663`.

The prior diagnostic code commit is
`736691964dd733b67ded1a683efe5d586f5952f0`, parent
`aea868bfd3ac9519ae3a51112cd8af82d9b29171`. It prints the original AST body
length, local count, projection-statement count, unwind-epilogue count and the
actual derived HRTB `(F,T)` pairs before applying the same exact candidate
inventory predicate. It does not relax the predicate, alter source, weaken
posts, or introduce a new binding rule. Its Build `310f38b5-5f45-4d4c-bb72-cd3f48ed40c6` used the old root-count
predicate and recorded body 284 against stale expected count 282. The corrected
candidate at `8de4cda418c4772009359fbb90e7e7f34836cca0` changes AST indexing based
on the saved preAST; its fresh result is recorded below.

## Exact Cloud invocation and reproducibility

The d128 run was submitted through the authorized existing lane, pinned-object
source mode, and phase ledger:

```sh
python3 research/challenge-8/cloud-build/control.py \
  --phase-id SORT4-NATIVE-C1-ZST-REPAIR-CLOUD-2026-10-11 \
  --ledger /root/verify-rust-std-select-night/research/challenge-8/cloud-build/sort4-native-c1-bound/BUDGET-ZST-REPAIR-2026-10-11.json \
  --state-dir /tmp/smallsort-cloud-native-c1-zst-repair-20261011 \
  --owner select-sort4 submit \
  --infra-sha aea868bfd3ac9519ae3a51112cd8af82d9b29171 \
  --proof-sha aea868bfd3ac9519ae3a51112cd8af82d9b29171 \
  --lane o26-sort4-c1-current-recovery --source-mode pinned-objects --timeout 1200
```

The prior source/MIR capture Build used the same controller, phase, ledger,
state directory, owner, lane and source mode, pinned to `0c1bd9d70635776d587489163384b8c4f25b9d1b`
for both `--infra-sha` and `--proof-sha`; its Build ID is
`55f876c4-c3a7-4a4f-87b4-9242a3ad660b`. The d128 invocation above uses
`aea868bfd3ac9519ae3a51112cd8af82d9b29171` for both pins. The diagnostic
follow-up pins `736691964dd733b67ded1a683efe5d586f5952f0` for both pins; Build
310f completed with the old-count inventory refusal described above.

The terminal d128 evidence was retrieved read-only with the same phase, ledger,
state directory and owner:

```sh
python3 research/challenge-8/cloud-build/control.py \
  --phase-id SORT4-NATIVE-C1-ZST-REPAIR-CLOUD-2026-10-11 \
  --ledger /root/verify-rust-std-select-night/research/challenge-8/cloud-build/sort4-native-c1-bound/BUDGET-ZST-REPAIR-2026-10-11.json \
  --state-dir /tmp/smallsort-cloud-native-c1-zst-repair-20261011 \
  --owner select-sort4 download d128e368-9a50-4c1a-8e74-64d71c51bfa0 \
  --output /tmp/native-c4-d128-read --text-logs
```

The d128 driver recorded these isolated tool and target commands (workspace
prefix shown as present in the raw stage record):

```sh
make -C /workspace/smallsort-work/sort4-native-c4-bound-isolated-source/src \
  ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
/workspace/smallsort-work/sort4-native-c4-bound-isolated-source/bin/verifast \
  -rustc_args "--edition 2021" -verbose 4 verified/lib.rs
```

Before the verifier command, the driver required successful normal and
readonly MIR export/decode and refinement against `original/lib.rs`; each
stage and full target MIR identity is retained in the raw evidence.

Build 310f pinned the prior diagnostic commit 73669196 for both input SHAs; it
did not contain the corrected indices. The historical invocation below records
that old-count diagnostic, not the corrected candidate:

```sh
python3 research/challenge-8/cloud-build/control.py \
  --phase-id SORT4-NATIVE-C1-ZST-REPAIR-CLOUD-2026-10-11 \
  --ledger /root/verify-rust-std-select-night/research/challenge-8/cloud-build/sort4-native-c1-bound/BUDGET-ZST-REPAIR-2026-10-11.json \
  --state-dir /tmp/smallsort-cloud-native-c1-zst-repair-20261011 \
  --owner select-sort4 submit \
  --infra-sha 736691964dd733b67ded1a683efe5d586f5952f0 \
  --proof-sha 736691964dd733b67ded1a683efe5d586f5952f0 \
  --lane o26-sort4-c1-current-recovery --source-mode pinned-objects --timeout 1200
```

This records the exact published inputs and controller command, not an
authorization for another dispatch.

## Open trust obligations

The saved d128 AST has 284 top-level roots, not 282: the size-zero and
`len >= 8` branches are roots 244 and 252, and the four-call block is root 275
with 215 statements. The corrected overlay expects 284 roots and preserves
both early branches in the surrounding normal body. The full inventory still
requires 239 locals, an empty projection-statement list, an empty
callback-unwind epilogue and the sole derived `F:T` pair. A fresh build must
check these against the exact pinned AST. The correction must preserve the
complete exact-source/AST/MIR admission boundary and all four per-call
bindings. Any requirement for new
general HRTB, lifetime, ownership, callback, parser, kernel or memory-model
semantics is outside this candidate and needs separate review/authorization.

Even a successful bound fixture would remain experimental: retain complete
normal/early-return/four-direct-unwind posts, all four exact unwind false
controls and normal false control, paired source/MIR/refinement, default-off
and admission controls, dead-code/unwind/resource checks, and immutable source
identity. The caller edge, general SmallSort contract, selector/C5/copy path,
and generic ZST safety are still excluded. No current evidence supports C4
proof credit or an accepted callable summary.


## Fresh corrected-candidate result (Build 3b743)

Build `3b7431bb-4e18-4921-b690-307e4ba7f984` used proof/infra commit
`8de4cda418c4772009359fbb90e7e7f34836cca0`, the corrected published candidate.
It completed in 465 seconds (create `2026-10-11T10:26:03.935776892Z`, terminal
`2026-10-11T10:33:48.564284Z`); cumulative charge is 2526/3600, leaving 1074.
Archive SHA-256 is
`4e9c337e98d403d5959d0581c8739b4510cb5b94b977fae2ce0a947b35e4f6e4`; text log
index SHA-256 is `ccf48de2563412a27e8c393bc171db58189740b72370f98ff5eef3128c9be3b8`;
1053 evidence inventory hashes were independently checked. The collector run and
complete delivery succeeded, but its verification-accepted flag remains false.

All nine ZST model gates and the retained native C1 prerequisite candidate/control
gates have their expected outcomes. The raw result records
`native_c1_to_c4: NOT_RUN` for a legacy, separate C1-to-C4 driver path; this is
not the current target path. The current `native_c4_bound` target executes the
four sequential actual C1–C4 comparator expressions together in the guarded
native fragment. The separate external caller and callable summary remain
`NOT_PROVED`. C4 paired normal/readonly MIR and refinement pass with the same
source pair and AST certificate listed above. The
positive candidate passes the exact 284-root inventory and verifies with exit 0
(485 statements). The normal false control reaches assertion line 577; the four
direct-unwind false controls reach lines 387, 442, 504 and 561. Source-hash,
extra-body, malformed and mixed-environment admission controls refuse as designed.
Default-off remains unadmitted and reports a parse error, not a semantic negative.

The effective result records HEAD `f76012fb518703b1d98e243ac4f487f16877cfcb`,
translator `66e266d3a36517d8c552b34ab17357b7b5d11192095e47672504533611c76124`,
kernel `37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`,
verifast1 `bfbfb518fb9783afeeba9384e1431b6cd280c7da7713b9fdbfd15a8395b00207`,
and rebuilt console `b73d563b88727846581ab33d425a2fd57ff736fa52e580addde930da33bb01fc`.
Positive post-AST SHA-256 is
`759d08b814674869c26ec067c34c259d819cadbf7703ac76009b048e6bebf675`.
These records support the bounded four-call fragment VF0 candidate only, for
the existing `small_sort_general_with_scratch<T: FreezeMarker>` domain. They do
not establish profile acceptance, project proof credit, a callable summary, the
external caller, or the unrestricted `sort4_stable<T>` contract. The C4 base/result manifest has the full before/after profile and result
identities; see [fresh raw review](FRESH-3B7431BB-REVIEW.md) and
[index](FRESH-3B7431BB-INDEX.json).

The exact submission was through the existing authorized controller/lane with
pinned objects and the same infra/proof SHA:

```sh
python3 research/challenge-8/cloud-build/control.py \
  --phase-id SORT4-NATIVE-C1-ZST-REPAIR-CLOUD-2026-10-11 \
  --ledger /root/verify-rust-std-select-night/research/challenge-8/cloud-build/sort4-native-c1-bound/BUDGET-ZST-REPAIR-2026-10-11.json \
  --state-dir /tmp/smallsort-cloud-native-c1-zst-repair-20261011 \
  --owner select-sort4 submit \
  --infra-sha 8de4cda418c4772009359fbb90e7e7f34836cca0 \
  --proof-sha 8de4cda418c4772009359fbb90e7e7f34836cca0 \
  --lane o26-sort4-c1-current-recovery --source-mode pinned-objects --timeout 1200
```

The reviewed evidence was retrieved with the corresponding download command:

```sh
python3 research/challenge-8/cloud-build/control.py \
  --phase-id SORT4-NATIVE-C1-ZST-REPAIR-CLOUD-2026-10-11 \
  --ledger /root/verify-rust-std-select-night/research/challenge-8/cloud-build/sort4-native-c1-bound/BUDGET-ZST-REPAIR-2026-10-11.json \
  --state-dir /tmp/smallsort-cloud-native-c1-zst-repair-20261011 \
  --owner select-sort4 download 3b7431bb-4e18-4921-b690-307e4ba7f984 \
  --output /tmp/native-c4-3b743-read --text-logs
```

## Remaining trust and scope limits

The bounded fragment itself freshly reaches VF0; “no C4 proof credit” here means
the candidate/profile remains unaccepted for project credit, not that the
positive result is an inconclusive/negative run. The project profile remains
`SORT4_C1_CURRENT_RECOVERY_DIAGNOSTIC_ONLY_NOT_ACCEPTED`. The source-specific C4
overlay and Rust ZST layout model change remain experimental trust inputs; their
separate rationale, manifests and regression gates must be reviewed before any
profile acceptance. This fragment does not prove the external call site or a
callable summary, complete `small_sort_general`, selector/C5/copy path, or general
ZST safety. No further caller or architecture claim follows from the green fragment.
