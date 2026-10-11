# Maintainer review package: native caller-entry experiment

## Scope and candidate change

The current experiment tests the first direct `sort4_stable` call from
`library/core/src/slice/sort/shared/smallsort.rs:254`, inside
`small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T, &T) -> bool>`.
The only new translator delta is the one-symbol extension in
[`verifast-slice-as-mut-ptr.patch`](../../caller-entry/verifast-slice-as-mut-ptr.patch):
the existing exact `[T]::as_ptr` arm also recognizes the exact compiler symbol
`std::slice::<impl [T]>::as_mut_ptr`. Both use the existing typed pointer cast
lowering after checking the `T` substitution and receiver count. The candidate
was rebased from patch SHA
`f200a5812149bb2278ded1d1ccb27a104b3dec3c03c5e40c79e30409d0d06916` onto the
current C4 translator. It changes no parser, RSSpec, kernel, ownership or alias
rule.

For the pinned source, `[T]::as_mut_ptr` at `library/core/src/slice/mod.rs:778`
has body `self as *mut [T] as *mut T`. The exact body and source SHA are
admission pins. The lowering returns a pointer value; it contributes no array
cells, `T` ownership, writable scratch authority, lifetime token, pointee
initialization, provenance connection, or aliasing fact. The consumer checks
must still derive those resources from the native mutable references and must
reject a wrong pointer and a fabricated initialized-`T` view of
`MaybeUninit<T>` storage.

The route keeps the real guards and no supplied nonzero/selected-path premise.
The helper's `len < 2` return and `scratch.len() < len + 16` abort check remain
in order, followed by `v.as_mut_ptr()` and `scratch.as_mut_ptr() as *mut T`.
The source's original `size_of::<T>() <= 16 && len >= 16` choice of sort8 and
`len >= 8` direct-sort4 choice are unchanged. ZST lengths 8–15 reach the direct
boundary if this internal helper is reached without the public ZST guard.

## Pins and manifest interpretation

[`AS-MUT-PTR-BASE-RESULT-MANIFEST.json`](AS-MUT-PTR-BASE-RESULT-MANIFEST.json)
has SHA-256 `af291a3f8cb9f2e75b4ce2fccb71fdfa445495fa4bc313c00242a69892d16c06`.
It records the candidate patch, its base/result profile, and first archived
Build `a125db66-0204-47bb-964f-c3134d4b6eef`; it is an experimental tool
manifest, not profile acceptance. The recorded frozen base is VeriFast HEAD
`f76012fb518703b1d98e243ac4f487f16877cfcb`, kernel
`37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`, parser
`7bf12f1205ecf033e3bf66f11b4326c20d2876d68e19006d5db59f3e45ae91c2`, RSSpec
`d33b2a7a284557002b4f7afe3d5e63f813e51f818c588712d743b4b46f9bedaf`, and
pre-binding translator `66e266d3a36517d8c552b34ab17357b7b5d11192095e47672504533611c76124`.
The current translator is `21ca026ae3279ef7da9a8a482b5355fab4c39250dec553854509b1f8923f52c4`;
the post-binding verifier binary is `6d20c76fbd49c9ad2700ada5bf9e4ab5c218f82c5a32727daf2a3d3fb86b0ae9`.
Parser, kernel, refiner, MIR exporter, all effective RSSpec files, and frozen
proof-std inputs match their recorded base hashes. Only the translator rule
and rebuilt VeriFast console differ in the relevant component. The frozen C4,
native C1, and ZST/dead-code patches remain inherited experimental overlays;
their presence does not grant blanket admissibility.

The archived tool manifests and current source admission manifest pin these
source identities: slice implementation
`e3a45814fc07497d6e85d182d6b30782711e4b77752fa817988ec6da12e2cb6f`,
SmallSort `85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`,
stable public entry source `3f2b2d8543a1cb91c9352e041bed49949a31cbd4b1030ec1a82cca1304cb22d3`,
and `SizedTypeProperties` source
`b86a596a58dcb21a45e8b29b33327ca8c7bde708aa6fca158d4366e51403daf2`.
The generated source template changes between experiments; the third-build
template pin is `fb540479a8c0e170e12af607da2b17172f9c25a3e1a952032d60ef7867e882a0`,
while the second `1d2237d7` raw records its own per-run template
`2b051cac1c58f2badb42bd5c6bede4d9b0d7c6356beee0533815aa526231f9ac`.
Those are distinct fixture identities and must not be merged or treated as one
source hash. The first archive SHA is
`045e43a175079115c36a309ef796bd9edd866d68ebd759b14c6cbafe663aaf1c`; the
later complete archive SHA is
`9a0aa14a804981b9fed0feca217c706827bab7bda563238bd800221d609d288c`.
The separate [fresh second-build manifest](AS-MUT-PTR-FRESH-1D2237D7-MANIFEST.json)
records that run's source/proof IDs. Both complete base/result snapshot objects
were independently compared with the first manifest and are identical; the
consumer fixture and permission control changed and were freshly verified.

## Evidence and separated verdicts

The first raw review, [FRESH-A125DB66-REVIEW.md](FRESH-A125DB66-REVIEW.md),
found source/tool pins and isolated positives reviewable, but the packager
rejected its audit because the root `proof-audit.json` lacked the required
typed Boolean `accepted`; process exit 0 was not evidence acceptance. Its
unfiltered prefix had a syntax failure before MIR and is only NOT RUN.

The later [FRESH-1D2237D7-REVIEW.md](FRESH-1D2237D7-REVIEW.md) independently
verified the archive and all 646 inventory entries. Its collector reports
complete diagnostic/evidence packaging, but `verification_accepted=false` and
the profile remains unaccepted. Canonical generic and MU components pass
normal/read-only support, refinement, AST and verifier gates; their 55/55
registered physical nodes execute, with full generated normal/unwind posts
and cleanup/leak checks. The isolated real-call consumer passes its paired
support, refinement, AST and verifier gates; all 65/65 registered IDs execute,
and the full post/free/leak checks pass. Wrong-pointer, missing-raw-rights,
and forbidden MU-to-initialized-T controls fail at their intended assertions.
Admission mutations and default-off controls refuse before proof. These are
component and consumer diagnostics only; the manifest and raw audits retain
`profile_accepted=false`, `actual_caller_proved=false`,
`actual_sort4_proved=false`, and `callable_summary=false`.

Both current unfiltered caller-prefix variants pass normal/read-only export,
decode, paired MIR support, and refinement on the immutable source pair. The
AST root is `small_sort_general_with_scratch<T,F>` at
`verified/lib.rs(10,1-57,2)`, with `v`, `scratch`, `is_less` and the three
translated lifetime parameters. Both variants stop at their first verifier
obligation, `verified/lib.rs(20,24-32)`, mapped to source line 230:
`scratch.len() < len + 16` after `len = v.len()` at source line 225. The
unproved VC is
`ptr_len(fn_outcome_result(outcome)) + 16 <= usize::MAX`; both verifier exits
are 1. This neither proves nor aliases the abort branch and occurs before
either pointer call. There is no native actual-caller pointer or alias credit.

## Source applicability and trust obligations

The source-level `FreezeMarker` bound does not imply nonzero size, `Copy`,
comparator purity, absence of panic, or disjointness. The stable specialization
uses a `T: FreezeMarker` implementation and threshold (SmallSort lines 49–62),
but that specialization is not proof that this helper's caller passed a
non-ZST type. The generic `sort4_stable` at line 606 has no `T: FreezeMarker`
bound.

The public stable sort checks `T::IS_ZST` and returns before its later length
and dispatch work (`stable/mod.rs:29–40`). The pinned
`SizedTypeProperties` trait defines `IS_ZST` through `SIZE == 0` in
`library/core/src/mem/mod.rs`; the existing C4 RSSpec relates
`IS_ZST::<T>()` to `size_of::<T>() == 0` (`std/lib.rsspec:395–403`). This
offers a source/spec route to nonzero size for a call that is proved to pass
that public guard. The actual path from the public guard through entry
selection, scratch creation, and this helper call has not been proved. The
native prefix starts inside the helper and so cannot inherit that fact.

The caller's first unresolved obligation is the `len + 16` overflow check.
The existing Rust array invariant can yield a length/size bound for nonzero
elements, but ZSTs have no length bound from byte footprint. Proving the
public non-ZST guard reaches this check could support a later arithmetic
derivation; it does not erase the check, prove `abort`, or grant any pointer
permissions. Source `MaybeUninit<T>` size/alignment equivalence is already in
the frozen profile, but remains a layout fact: it does not make a
`MaybeUninit<T>` slice into initialized `T` ownership or writable raw
authority. The intended consumer negative specifically guards that boundary.

The trust review must assess the **whole existing experimental tool profile**
as well as this one-symbol delta. Current logs do not accept the ZST size
repair, C1/C4 overlays, or combined profile. Exact source admission and
component positives/negatives support a narrow candidate evaluation, not a
soundness conclusion. Acceptance still needs independent review of the
translator's source-symbol applicability, typed cast projection, existing
Rust layout/IS_ZST and `MaybeUninit` model, and all inherited semantic patches.
No foreign proof is imported, and no user-facing Rust signature or runtime
algorithm was changed.

## Open domain after the current first obligation

Even after proving this first `len + 16` check from the actual caller, further
source-derived facts and proof obligations remain: entry length is at least 8
for the direct-sort4 arm; for nonzero `T`, the `size_of::<T>() <= 16 && len >=
16` arm selects sort8 instead, so direct sort4 covers sizes above 16 at
lengths at least 8 and sizes 1–16 at lengths 8–15. The actual helper must
preserve native source array/owners, `MaybeUninit<T>` scratch frame, callback
`F`, thread and lifetime resources, and full normal/unwind/abort behavior.
The four-comparator C4 fragment is not the five-comparison `sort4_stable`
contract and is not an actual caller summary.

The second direct call at `smallsort.rs:255` additionally needs the
`len_div_2` offsets, valid second source and scratch windows, disjointness and
resource restoration after the first call. The size/length sort8 route at
241–251 calls nested sort4s and merge; other short-path, insertion, tail,
merge, panic and caller-frame routes remain separate. Neither this package nor
the current two builds proves the second call, sort8 route, full `sort4_stable`,
or complete sort4/SmallSort function.

## Current-phase Cloud command template

This is the reviewed command shape for the existing authorized phase, not a
new dispatch or a request to run a build. Use the current published exact
proof/infra SHAs, the assigned stable owner's ledger/state, and a lane allowed
by the active manifest. For the recorded inputs those values were phase
`SORT4-ACTUAL-CALLER-ENTRY-CLOUD-2026-10-11`, lane
`o26-sort4-c1-current-recovery`, proof SHA `0a61febf105b29dcb89d6fc25ec993bdcfd17e46`,
and infra SHA `0a61febf105b29dcb89d6fc25ec993bdcfd17e46`:

```bash
python3 research/challenge-8/cloud-build/control.py \
  --phase-id SORT4-ACTUAL-CALLER-ENTRY-CLOUD-2026-10-11 \
  --ledger "$c8_ledger_absolute" --state-dir "$c8_state_absolute" \
  --owner "$c8_owner" submit \
  --infra-sha "$c8_infra_sha" --proof-sha "$c8_proof_sha" \
  --lane o26-sort4-c1-current-recovery \
  --source-mode pinned-objects --timeout "$c8_timeout_seconds"
```

Before any submit, use the active owner ledger and v2 coordinator to reconcile
own unresolved Builds/capacity; do not copy the historical hashes if sources
or recipe change. Download and verify the complete archive, inventory, receipt
and logs before interpreting proof status.

## Third public-guard build — pending raw review

The upcoming third build is expected to add a source-bound public stable-guard
prefix. Its exact Build ID, proof/infra SHAs, archive hash, per-case stage
results, source/MIR/AST roots, first causal obligation, and whether the guard
fact transfers to the actual helper are **PENDING RAW REVIEW**. Do not infer
guard entailment from admission, collector success, or static source alone;
the proof/model/profile status remains unchanged until that package is
independently reviewed.
