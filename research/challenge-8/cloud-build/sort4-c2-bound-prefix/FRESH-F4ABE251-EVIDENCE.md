# Fresh bounded C1+C2 evidence — f4abe251

Build `f4abe251-23f9-459e-a418-6372b6553057`, token
`dispatch-9b74bfc559bf475e8abcc6daf6b1c7db`, proof=infra
`7c8e34610a52bebc7212c6e611d1afa2e70c085b`, lane
`o26-sort4-c1-current-recovery`, pinned-objects. Config SHA256
`619dfe350798dc85d6f0d8cb2e816ddf4e4f689d7ff5b4b6333a69535f9fd4fe`.
Create `2026-10-10T02:00:53.445494900Z`; finish
`2026-10-10T02:07:47.784247Z`; SUCCESS diagnostic, charged415 seconds.
Session2131/3600,1469 remaining at this result. Previous709 closed/no carry.

Archive SHA256 `e2c500fdce968124c177dfbce638e5f812ce598c4834c87e643bc6da2c1adad4`,
full archive and text-log index/chunks independently verified by download receipt.
GCS `gs://smallsort-ci-evidence-504462351565/cloud-build/f4abe251-23f9-459e-a418-6372b6553057`.
Local read-only evidence `/tmp/c2-f4abe251-read/allprooflogs/cases/sort4-c1-current-recovery`;
raw evidence is not committed. No compiler/extractor/proof ran locally.

## Proof result and limits

Fresh raw positive exits0: **0 errors,184 statements**, helper `recover_pair`
and `join_four_owned_cells` entries before `sort4_stable`; target normal,
C1 direct-Continue unwind and C2 direct-Continue unwind each reach return and
leak check. No dead-code error or disabled check. Source/normal+readonly full
MIR/refinement gates fresh; exact two actual FnMut comparisons source190/223
(original SmallSort620/621), two independent Output=bool registrations.

Domain is the unchanged raw non-ZST source4/F/thread/type/optional-dst contract.
CURRENT source owners and F state are recovered after each callback; C1 unwind
exits before C2. Complete original normal/unwind posts retained. Projection ends
after C2 normal join227, before third comparison/select/copy suffix. No actual
caller CFG, caller→sort4 composition or whole-sort4 callable summary.
The native standalone resource lemma remains separate; no native supplied
premise is credited as derived in a completed composition.

The seven negative controls reached target and produced candidate intended
first errors. Source operand mutant refuses exact source hash before proof.
Default-off C1 full VF0 and mandatory unbound scaffold refusal are preserved.
Saved MIR/preAST mutants and live-tuple/JSON-list classifier regression are
**service replay only**, never fresh proof credit. Build5 collector failure
remains preserved with bound C2 NOT_RUN in that Build.

Allocation placement and each first VC passed independent raw/kernel review in
[FRESH-F4ABE251-REVIEW](FRESH-F4ABE251-REVIEW.md). Its deterministic AST/kernel
derivation accounts for producer registration and scope/root consumption; the
verbose2 trace does not identify each local object separately. C2 receives its
CURRENT source/F/thread resources from C1 normal recovery within this completed
bounded composition, while raw entry resources remain supplied. The original collector record
retains `accepted=false`, `bounded_theorem_admitted=false` and its pending gates;
no live evidence/classifier or profile acceptance is rewritten by documentation.
Experimental proof verdict and tool-profile acceptance remain separate.
The profile's static proposal identifier ending `NOT_YET_RUN` is preserved as
an input pin; the fresh run verdict is `C1_C2_BOUND_PREFIX_VF0`. The unbound
profile remains `C2_UNBOUND_SCAFFOLD_ONLY_NOT_PROOF` and still refuses.

## Exact identities

Cloud compiler raw `compiler-version.txt`: `rustc 1.100.0-nightly`, toolchain
`nightly-2026-09-25`, commit `f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f`,
LLVM23.1.1, host/target `x86_64-unknown-linux-gnu`. Proof Ubuntu image
`sha256:5ec03bb3441e8b0bf3b4f9cd4629a1ae763010dc3035bb8da3ae6cf026486401`.
Std base `cd371e035c7e573760c43bf934d53e8118ee3e7d`; actual SmallSort source
SHA256 `85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`.

The generic top-level package `tool_profile.scope="no proof tools executed"`,
empty tool map and patch list are stale default fields for this lane
(`package-evidence.py` fallback). They are not a description of this run.
Actual execution and tool identities come from the fresh raw stages/logs and
`c2-bound-tool-snapshot.json`, directly reviewed above; proof/infra/config/archive
identities in the package are checked. The raw manifest is retained unchanged,
and `verification_accepted=false` is not upgraded. A later classifier-only repair
must replay saved evidence first; it needs no unchanged proof rerun.

VeriFast base `f76012fb518703b1d98e243ac4f487f16877cfcb`; existing frozen strict
C1/C2 chain plus the own translator-only C2 delta. Kernel/parser/schema/exporter/
refiner/prelude/proof std hashes are unchanged across the C2 delta; full snapshot
`c2-bound-tool-snapshot.json` and complete tracked patch retained in the archive.

| Identity | SHA256 |
| --- | --- |
| C2 profile | `cc598a67e27d914f97d82222bbe90de86c13b575e3433d392c7fd300d34951d5` |
| C2 driver | `80bb7bbb69cd303c52598ed212ae9175a124abc3164a63a4a40cda39e806ef4f` |
| C2 delta | `4851c87be76630a627ff04d351ba6146879568eb877a28235a95d4cbea913925` |
| VeriFast console | `c95e016c0b1502a4edbbfe5b13dbeb224795bf8dd4bbd2605ea1dc20cc60b081` |
| Translator | `daf29b03fbb7aa10e6f580c70780a9fdc5a2eb6d3f4470e1c38673212ca3d9a3` |
| Kernel | `37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c` |
| Parser | `7bf12f1205ecf033e3bf66f11b4326c20d2876d68e19006d5db59f3e45ae91c2` |
| Schema | `f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469` |
| MIR exporter | `b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796` |
| Refinement checker | `b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28` |
| Tracked tool patch | `6e1b865ad341af735f840486efa6074e096b1e4d0a5a51836feefb94952e9c16` |
| Pre AST | `4fa7d49e420dc80681328bacdf08bb1d674dc2413001b99501da1c09b11dbb0a` |
| Post AST | `96b7dd87721cb35e3808fae4f1084e8c270078052dff93ef4fbf913190fa7ec9` |
| Positive raw log | `5842ec3c357f3a76082784d829e43464f67d5dbe61143aa3be326ae7fb3b5e05` |

Exact source/MIR pins and projection domain are in [SEMANTIC-CARD](SEMANTIC-CARD.md)
and immutable profile. All profiles remain experimental/unaccepted. This fresh
VF0 does not certify the soundness/admissibility of the patched verifier or full
sort4 correctness. No runtime std/generic signature/final contract was changed.
