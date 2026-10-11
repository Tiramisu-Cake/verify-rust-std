# Native C1 exact dead-node / ZST model checkpoint

Session CLOSED 2026-10-11T01:22:29Z; start00:21UTC, main allowed until02:21, finish-only02:51.
Closed after cause localization rather than unauthorized general model repair.
Owner select-sort4; worktree `/root/verify-rust-std-select-night`; current branch
`research/night-select-sort4-cloud-2026-10-09`. Initial checkpoint
`d2c739b557941875f0888eca50749fcbd6d4e9a7`. Policy revision read/adopted
`c7ca8c467aecf10a4b53039372ee97714f854ee3`; origin/main fetched, docs already
integrated. Hour progress delivered01:21UTC; continued checkpoint/push without
waiting for reply. No new session automatically starts.

## Exact node and established cause

Dead physical location/statement ID203, post-AST list138 / traversal ordinal256,
Goto63 immediately after Label3, original pre-AST root131. Printed228,2 also
belongs to visited IDs202(Goto63 viaLabel62) and204(Return afterLabel63).
203 has noEXEC; original dead-code decision/exit1 preserved. Diagnostic uses
same physical-location equality and original registration/removal/filtering,
not manufactured visits. Identity is run-local; statement/index/label/source
mapping identifies the actual AST node. [Physical review](FRESH-009AD1C2-REVIEW.md).

Source145 sizezero guard → MIR size_of bb1, bool equality/switch bb2,
false/nonzero→bb4 and true/zero→bb3 → retained pre/postAST If(_7,Goto3,Goto4)
and Label3/Goto63. No branch removed, successor inverted or unwind epilogue
relocation repeated. First zero assumption is pruned in symbolic execution.

Existing frozen model represents Rust union MaybeUninit as struct; generic
struct-size axiom in verifast1.ml6519 says size>0 for every instantiation.
Effective std lib.rsspec429 declares MU struct; automatic size_of_MaybeUninit
523–525 equates MU and T sizes. **Implicit entry array_inv autolemma** produces
scratch array-size bound and instantiates this chain before body execution.
This is separate from later explicit source169 helper call. Fresh9ae minimal
callback-free -verbose6 directly observes size_of_MaybeUninit2414 then
MaybeUninit_size_limits2415 during native scratch entry (prelude257). First
positive-T query2559 passes withMU; withoutMU firstquery2497 fails2501. Both
precede len/size_of calls. Verbose6 names triggers but does not dump substitutions;
adjacent MU<T> term, static quantified axiom/equality and diagnostic query pair
identify this instantiated cause. Native log verbosity4 has the same entry term
but not named-trigger messages. [Entry review](FRESH-9AE319B8-REVIEW.md).

Classification: localized **existing frozen MU/struct layout-model limitation**,
not source-specific binding fault or incorrect visit bookkeeping; no blanket
claim about VeriFast. Generic source array<T>/Sized alone does not prove positive
size; native MU scratch does under this model. Generic ZST support is NOT_PROVED.

## Fix, boundaries, verdicts

Implemented only diagnostic identity/statement/predecessor/visit reporting,
exact phase registration and dependency-role repairs, saved-log reader and
callback-free model probes. No semantic/model/kernel change or source-specific
target repair was applied. A binding-only repair cannot undo the model chain
while preserving native opaque MU and the real zero branch/dead-code checks.
[Minimal maintainer blocker](ZST-MODEL-BLOCKER.md) is READY; repair needs separate
VeriFast-agent scope, rationale/trust review and regression gate. No external
message/publication sent and no peer unfinished profile imported.

Native C1 **INCOMPLETE**: fresh positive reaches actual FnMut operands1,0,
normal/current recovery and direct comparator unwind/current recovery, plus
len<8 return and full automatic native source/tail/MU/F/thread/lifetime/type,
unit/free/leak checks, then verifierexit1 DEAD203. The zero path is excluded;
there is no fresh complete exit0, callable summary or full theorem. False-normal
226 / mapped false-unwind210 reach their intended post-cleanup false assertions.
Strict entry/cut, escape/unwind/free/leak/deadcode/refinement and all admission
checks remain on. Diagnostic ghost positive-size assert is not an assume or
actual-target modification. Source/F/thread/types derive from native entry.

Native connected C4 **NOT_RUN** until complete C1 and retained paths pass.
Old supplied raw C1→C4 PASS is independent and not composition. Scratch MU stays
opaque: no reference-own inverse, optional-T adapter or copied raw premise set.
External as_mut_ptr binding/caller, guards/overflow, selector/C5/copy and general
layout/ZST extensions remain outside this task. Original std runtime code,
algorithms and signatures unchanged.

## Fresh builds and separate budget

| Build | Exact proof=infra commit | Result | Charge seconds |
| --- | --- | --- | --- |
| b05354e9-01f2-4eb7-aee8-9db0fce64bb8 | 143eec6d398095a0f4f9b5bd312f3ca02a2c177d | Setup failure: obsolete wrapper phase guard; target/probes NOT_RUN | 276 |
| 8dc2562a-d18d-439c-8916-f142ad44adab | 1286f1dc31825bb7d0affa68178e07140704daa8 | Setup failure: diagnostic dependencies only in infra role; target/probes NOT_RUN | 410 |
| 009ad1c2-119b-4598-98cf-573dcfb34c76 | f8115f33f35d745b9da9ab5e01f0ee3b7908ce56 | Diagnostic SUCCESS; nativeVF1/DEAD203; noMUcontrolVF0 vsunusedMUdead | 390 |
| 9ae319b8-7f82-4045-818c-ef654567f57f | b81f1c3ccce23e0b5e2a029350c0a6443b929747 | Diagnostic SUCCESS; entrytrigger cause confirmed; nativeVF1/DEAD203 | 354 |

Total1430/3600 create→finish Cloud seconds; unused2170 retired/no carry.
All4 terminal/accounted/evidence-download-verified, own active_buildnull,
no unresolved state, reservations[], ready request withdrawn. Coordinator
schema2/max2 preserved; own one active at a time. No Actions dispatch or trigger
changes. [Ledger](BUDGET-2026-10-11.json) records full config/payload/token/time/
archive pins. Profile cloud_enabled/dispatch_authorized nowfalse.

Archive009 SHA25648b943568293e42d56374af931963a85637fc69c2c62324f15df1ad90c5efc5d;
9aef23156ad5744bace48a0dd1c36b4eae7a2e05c672787331539644298fdc70466.
BuildGCS prefixes `gs://smallsort-ci-evidence-504462351565/cloud-build/BUILD_ID`.
Commands and Git-object role-specific closure checks in [reproduction](REPRODUCTION.md).
Native source7ebcf7cd435c31b3f4669ac6f31a62fd45fcb2c7fa03500bdfbc44ccaca01742;
original7c35a7e01915233308d113b081f26784c4ad5aaf6f7049dc209d126e3eb326a1;
normalMIR8e9adcccd136d3c1ee4dc1e7bd929c3cd60883f497178eab24da40f60754dee4;
readonlyMIRbde6d797d56e0e11e9837fc922f6def819c6931d1349f42c5b36d4570e2001aa;
preAST18973de5dd5ff1a9c94652fd808d42ffe2297096adb8a3cc1980f74a554ccea5;
postASTc5fa49a0c3cf7fdaa03cb6ba22f3fd0fcd539e9fab743ee3d724716e47755a5e.
All equal3521/009/9ae. Toolf76012fb518703b1d98e243ac4f487f16877cfcb,
nightly2026-09-25; translator381e80ebe9a789877ee9d0e860da386f7692f54879b39775e01267f0db6f53d6;
kernel37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c;
effective stdspecd33b2a7a284557002b4f7afe3d5e63f813e51f818c588712d743b4b46f9bedaf.
Complete chain/critical/exporter/refiner/prelude/proof-std pins in frozen snapshot,
NATIVE-C1-BOUND-TOOL-MANIFEST and diagnostic manifest. Diagnosticpatch
fd4510d1d82ff0a50b2d528bd8c5f4554478b617d692c8ed1210b91bac598516.

Local validation: static Python AST/fixture ordering, bash syntax, Git-object
closure role/hash/size checks, small saved/synthetic identity-reader tests and
evidence integrity review only. Heavy compilation/extraction/proof all Cloud.
No downloaded logs/build outputs/injected std committed. Independent explorer
review agrees, with explicit verbosity/substitution limits retained.
Next permitted action: evidence/documentation review; general-model implementation
or new experiments require a new separately authorized maintainer/session account.
Final documentation/profile/ledger closure is not a new proof run.
