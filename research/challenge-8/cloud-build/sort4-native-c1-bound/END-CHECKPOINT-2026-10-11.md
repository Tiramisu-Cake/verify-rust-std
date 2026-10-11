# Native resources → actual C1 — final session checkpoint

**CLOSED; native→actual C1 INCOMPLETE, native→actual C4 NOT_RUN.**
Final fresh verifier exit 1: `verified/lib.rs(228,2): dead code`.
No complete connected theorem or callable summary is accepted.

Owner `select-sort4`; worktree `/root/verify-rust-std-select-night`; branch
`research/night-select-sort4-cloud-2026-10-09`. Initial checkpoint
`93f902c27ca74011e28c9a84c4ce4e3e6e5a7a9f`. Factual start
2026-10-10 21:49:42 UTC; main deadline 23:49:42 UTC; finish-only limit
2026-10-11 00:19:42 UTC. First-hour update delivered at 22:49 UTC.
Policy revision `c7ca8c467aecf10a4b53039372ee97714f854ee3` read;
adoption/ACK retained. Own separate Git-dir/index and initial clean state checked;
no reset or foreign worktree/profile/pin/account changes.

## Fresh outcomes and resource transfer

The corrected prepared diagnostic was the first useful Cloud run. It passes
strict entry and derives source4/tail, F/thread/types, opaque scratch MU and
reference argument `Args.own` from native safe-reference resources. Its positive
undo diagnostic refuses the reverse reference-own opening at 198; intended
false-Args control fails at 190. This partial diagnostic is not a full native
normal theorem. The actual callback consumes `Args.own` directly, so that
unused inverse is unnecessary for the connected C1 target.

The source-specific C1 binding admits the actual first comparator, operands
1 and 0. Callback lifetime and Output=bool come from compiler types. Eight
compiler callback locals move into the checked strict comparison scope with
allocation/free/debt obligations preserved; c1 remains outside. Original native
scratch `MaybeUninit<T>` storage and ownership remain an opaque frame. Source4
and its tail, F/thread and type resources come from native entry and checked
helper bodies; no raw C1 ownership is supplied afresh. No optional-T adapter,
MU inverse, `new(inner(old)) == old` assumption, or layout/separation axiom.

In the final fresh positive trace, actual C1 normal return, direct comparator
unwind and len<8 normal return each reach full CURRENT native posts, unit
return, function-local free and final leak checks. Recovery uses CURRENT values,
joins four cells, restores the native tail/full source, retains opaque MU and
restores F/thread/types. Helpers `interior_pointer_limits`,
`split_four_owned_cells`, `recover_pair`, `join_four_owned_cells` verify before
use. The positive target still exits 1 on dead code, so these reached checks
are partial evidence, not fresh native→C1 PASS.

Normal/unwind false controls reach intended assertions at 226/210 after explicit
CURRENT cleanup; they stop before automatic return/post/leak checks. All eight
paired export/decode/refinement controls pass. Six exact full source/MIR pairs
remain immutable. Default-off strict-entry refusal at 172 and source-hash,
extra-body, malformed and mixed admission refusals are retained. Admission/setup
refusal is not a semantic negative. Strict entry/cut, escape, unwind, resource,
allocation/free, leak and dead-code checks stay enabled.

## Runs and exact accounting

| Build | Exact proof = infra SHA | create→finish charge | Fresh result |
| --- | --- | ---: | --- |
| 34bddbf7-e536-4ef0-bb7f-82e07ef439fc | 16bbfa6c7f4340e0643426560c4ff33531aff370 | 362 s | Prepared Args boundary; undo failure 198 |
| 7456e9be-368f-46b5-80df-afd9d7fb84ef | e7290456d53e47f9e22e25e52247d1823a14a540 | 387 s | Pre-AST setup refusal; no semantic credit |
| 10006623-3880-4a5a-b3d2-7d40274b7629 | 8ec0214fc8a1f3a36f63c6fdd8fca4e275020b24 | 417 s | Actual C1 reached; dead code 228,2 |
| 3521e3b3-5979-4c35-b931-93c4e165176b | 2e995605f5183907817d92db082624281665d61e | 390 s | Same refusal after CFG placement correction |

All four Builds terminal/accounted/download-verified. **1556/3600 Cloud seconds**
charged; **2044 unused closed without carry**. Collector SUCCESS is not verifier
PASS. `active_build=null`, own coordinator reservations absent, ready request
withdrawn, unresolved=[]; v2/max2/one-own protocol respected. Exact create/finish,
config/input/dispatch tokens and archive hashes: [closed ledger](BUDGET.json).
No new experiment or Build after main deadline; final Build started at
23:48:14.972546175 UTC and finished at 23:54:44.406774 UTC. Evidence/review and
accounting only afterwards. No automatic new session.

## Effective experimental profile and reproduction

Tool HEAD `f76012fb518703b1d98e243ac4f487f16877cfcb`, nightly `2026-09-25`.
Effective chain: frozen C4 snapshot → capture translator
`86952a6ac4a61ac854d8a9886cff98ee143a0e75ccf8148fb84e07c0a14ce544`
→ separately reviewed native C1-bound patch. Final translator SHA256
`381e80ebe9a789877ee9d0e860da386f7692f54879b39775e01267f0db6f53d6`;
patch `eea19eda3723a0f60970df751c7600c326f98ad476d41f61e3f39442beb88693`;
unchanged kernel `37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`.
Only own isolated translator at `/root/verifast-select-native-c1-bound-20261010`
changed. Nontranslator exporter/refiner/parser/schema/prelude pins preserved.
Profile experimental and unaccepted; tool HEAD alone is insufficient.

Final effective-profile artifact SHA256
`74591fdcf9846a7e56bc8a97833803b45a8f6d69129a4bd1694a2a4ecea52351`;
bound profile `348833f3b62ef96fc7984ffe4f4d04560b0d0266f5dd7df848e8a3ae8b33a9f7`.
Original pre-AST `18973de5dd5ff1a9c94652fd808d42ffe2297096adb8a3cc1980f74a554ccea5`;
final positive post-AST `c5fa49a0c3cf7fdaa03cb6ba22f3fd0fcd539e9fab743ee3d724716e47755a5e`.
The full source/MIR hashes, exact commands and recipe are in
[reproduction](REPRODUCTION.md), [tool manifest](NATIVE-C1-BOUND-TOOL-MANIFEST.json),
[fresh tool snapshot](FRESH-3521E3B3-TOOL.json) and
[fresh native input identity](FRESH-3521E3B3-INPUT.json).

Final archive SHA256
`9fe9e42f34e4b5c2b1fb8a4644d3b00ab398cf871181b9efa045455ac7979249`;
canonical location `gs://smallsort-ci-evidence-504462351565/cloud-build/3521e3b3-5979-4c35-b931-93c4e165176b/`.
[Raw review](FRESH-3521E3B3-REVIEW.md),
[independent review](FRESH-3521-INDEPENDENT-REVIEW.md),
[full result index](FRESH-3521E3B3-INDEX.json).

Classifier-only saved10006623 replay: all eight cases PASS; dead-code first-error
classification added without changing proof acceptance. Exact Git-object recipe
closure: 76 proof /16 infra files; final package 561577 gzip bytes /188 parts.
Earlier 192>191 transport and occupied-global-slots refusals occurred before
API dispatch and incurred no Build/reservation/charge. Four unused caller-entry
files read only by skipped native_cases were pruned; no transport/gate relaxation.
No local compilation/extraction/proof, toolchain install or research Actions.

## First blocker, next step and remaining scope

Reviewed CFG placement correction moves the unwind epilogue before the original
normal-return tail, conserving source branches/returns. Fresh final run repeats
the refusal, falsifying the placement-only hypothesis. Strongest unvisited
candidate is original root131 Goto63 after Label3, entered only by the
`size_of::<T>() == 0` route. Root129 Goto63 and root133 normal Return are visited;
all three share printed 228,2 but have distinct physical locations. Exact
physical error-node identity and reason for the missing zero-size path remain
unresolved. Stock size_of has no nonzero premise; FreezeMarker allows ZST.
No general VeriFast rule is established as necessary.

Next concrete experiment, only in a new authorized session: source-specific
location-disambiguating diagnostic on these pinned inputs, then trace the
size_of/array constraints and zero-size branch. Preserve prior refusal, every
branch and strict/dead-code/resource/unwind check. Do not repeat the historical
matrix or delete the ZST branch. See [precise blockers](REMAINING-BLOCKERS.md).

Native→actual C1: **fresh INCOMPLETE**. Native→actual C4: **NOT_RUN** until C1
fully passes. Old raw C1→C4 VF0/370 (a5180cd7, proof/infra203b59258b00ccc8bc2ecc030726fafde3a57d05),
normal and all four direct unwinds, remains a separate **prior PASS**, supplied
raw inputs/positive size/optional destination; it is not native composition or
whole-sort4 proof. No C2–C5/select/copy newly proved together here. Native lemma,
opaque frame/early-return/pointer-expression, MU forward/inner and guard results
remain separate prior PASS, not new composition credit.

Remaining supplied native boundary: safe entry source/scratch/F references,
thread/generic types and FnMut/Freeze contract. Selected internal comparison
boundary explicitly requires positive T size/nonZST and len>=8. Caller selection
alone does not establish positive size (len=8, size=0). Actual external
as_mut_ptr method binding, actual caller→sort4 call edge, scratch/inline-const/
abort/len+16 guards and generic layout/ZST remain unproved. Pointer-expression
prior PASS is not external method binding. Prior checked-add reproducer shows
MIR AddWithOverflow+Assert/unwind vs frozen exporter overflow-off lowering;
that tool-model gap is not runtime unsafety or permission to assume a len bound.
Retained primitive ptr_len/Add lowering does not supply fresh nonpanic proof.
General inference/alias/arithmetic/MU/kernel rules remain peer-owned. Strict-cut
draft NOT_USED; selector/C5/copy and unfinished peer patches NOT_USED.
