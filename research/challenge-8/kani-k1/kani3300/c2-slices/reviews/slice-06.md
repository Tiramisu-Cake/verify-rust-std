# Slice06 E1 — worker15 read-only review

PASS_STATIC_ONLY; no blocking findings. Independent reviewer worker15, source author
worker14. Candidate `3f5242bb1539fb88196d7e503b722f0905f2b46c`, tree
`fc4c2d802e8c8c61ce7fcf27c405f7dc14c9d369`, sole parent accepted5
`96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f` / coordinator run43715788377.
Review input g0 `75c4267aa8`. No source edit or stage7 extraction performed.

Read-only Git inspection confirms precisely25 changed paths:11 E1 input/golden pairs,
edge README, and outstanding hunks of the two shared docs. All25 have F's exact
blobs and modes. Entire tests/docs trees now equal F. Production, runtime, dependency
pins, stock workflows, inherited tests/goldens/directives and ignores are parent-identical;
B1 remains an ancestor. This is edge qualification, not a new production guard.

Union constants/variables use the same custom-MIR consume(Byte) call, initialized
byte0 versus empty-field union. The ordinary-union constant branch and transfer
prerequisites already belong4. Raw projected stores preserve actual Pair layout
(offsets4/8,size12), initialize only value, and distinguish untouched tail/padding.
Borrowed DST pairs read slice slot1; by-value pairs pass the dereferenced unsized
slice, requiring the same explicit size refusal for initialized and hole inputs.
All11 match final F with four SUCCESS, five uninitialized-read negatives, two
unsized-transfer negatives prescribed. E1 goldens have F's literal precision; they
do not pin exact failed-property counts or individual useful SUCCESS blocks.
Retain all source assertions and inspect native output during coordinator acceptance.

Docs preserve exact Scope A, immutable qualification and false-positive limits,
ordinary executing MIR transfer scope, marker-hook exclusion, nested aggregate
limits, Replace/RecursiveCheck/cycle limitations and explicit SmallSort exclusion.
No process links/run receipts or broader support claims enter the source export.

**Independent exact residual check:** compared head6→F against our stage0
`f7/F7-RESIDUAL.json`, SHA256
`771592442f46726dd9cda74756db8fc8f3f8cabb8ad3a17662a52973dae0d19c`.
Exactly five paths and14 hunk headers; each complete zero-context patch equals
its pinned historical ad324418cd→3b382c812a bytes and SHA256. Full residual patch
SHA256 `8e370c617017e8476ae45ed02b8c439448756d1c8cf0251ea1cbb9545fcecbe7`.
Temporary alternate-index application reconstructs exactly F's tree
`9829702c1aa0ecb73c860fc0ad5451757917d6cb`. This allows no arbitrary difference
inside compiler_interface.rs. No F7 file/API/scope wrapper was introduced, and
structural isolation remains unqualified before stage7.

Compile-seam review: zero production delta;48 call contracts inherited byte-identically
from accepted5. Fresh reusable checker audits both parent→head6 (11 Rust files) and
B1→head6 (190 files), including repo-wide generic impl inventory and99 bound calls:
PASS, no findings. Manual import/trait/impl/custom-MIR inspection of all11 fixtures
finds no new prerequisite. The three pre-F7 import/writer adaptations are unchanged
from accepted5. Static inventory does not expand macros or establish compilation.
Seam checker synthetic tests10 PASS. Native compile/fmt/clippy remain NOT_RUN.

[Source validation](../ci/slice-06/SOURCE-VALIDATION.json):919 pinned manifest file
identities; all460 previous selectors unchanged,11 new,471 cumulative,9 existing
ignores. All212 present expected/uninit selectors discovered without omissions.
Inherited strong/mode/composition oracles remain exact F and selected.
[Seam audits](../ci/slice-06/SEAM-VALIDATION.json) and cumulative companion bind
exact source/checker/contract hashes. No historical receipt or map was rewritten.

[CI request](../ci/slice-06/CI-REQUEST.md) reuses accepted5 overlay ce56d3d467/run43715788377:
runner byte-identical, compiler68 plus9/9/1/1 filters, cumulative Quick, E1/composition,
S5 mutations4/4 rerun on head6. Repaired-write classifier now accepts renumbered
permitted-write locals and requires completed SUCCESS/N0 plus the intended golden
failure mismatch. It preserves native verdict/completion checks, failure rejection,
patch/input hashes and restoration;13 sensitivity synthetic tests PASS, including
local-renumbering and wrong/missing mismatch regressions. Runner synthetic tests23 PASS.

Local Rust/Kani/CBMC builds, native tests, push and dispatch NOT_RUN. Cloud $0.
Coordinator must review exact-head native outcomes and4/4 detections; accepted5
mutation evidence is provenance, not a replacement for the requested head6 rerun.
This review establishes no Gate A, SmallSort or independent formal proof credit.
