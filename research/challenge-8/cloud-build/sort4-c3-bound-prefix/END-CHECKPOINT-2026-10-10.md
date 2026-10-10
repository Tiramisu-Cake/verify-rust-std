# End checkpoint — actual sort4 session 2026-10-10

Session **CLOSED**. Main window 2026-10-10 **10:20:59–12:20:59 UTC**;
finish-only ceiling **12:50:59 UTC**. No new experiments/Builds after main
end. Accounting closed at **2026-10-10T12:30:48Z**; final publication is documentation
and the already-started runner configuration draft only. No automatic new session.

Worktree `/root/verify-rust-std-select-night`, branch
`research/night-select-sort4-cloud-2026-10-09`, initial clean HEAD
`fafb91f0d59d070dac8b9ac72c71143a4224a78b`. Separate git-dir/index verified:
`/root/verify-rust-std/.git/worktrees/verify-rust-std-select-night` and its index.
Fork origin `https://github.com/Tiramisu-Cake/verify-rust-std.git`.
Policy read `c7ca8c467aecf10a4b53039372ee97714f854ee3`, WORK-POLICY blob
`61d4cd336a26df4925bd42d2846f9bc771263fde`; adoption/ACK retained.
No Actions, upstream publication, foreign pins/ledgers/slots changes or local
compilation/extraction/proof. Local configuration parsing/replay only.

## Completed actual prefix and applicability boundary

Fresh unified **C1→C2→C3** VF0/335 statements, then **C1→C2→C3→C4**
VF0/370 statements. C3 is actual `is_less(&*c,&*a)`; C4 is actual
`is_less(&*d,&*b)`. C5, first `select_unpredictable`, remaining selects/copy
were **NOT_RUN**, and have no new proof credit. This is an exact conditional
bounded-prefix result on experimental profiles, not whole-sort4 summary,
actual caller theorem, or acceptance of verifier semantics.

From C2 CURRENT owners, a=base+c1, b=base+!c1, c=base+2+c2,
d=base+2+!c2. In c1/c2 order FF,FT,TF,TT, C3(c,a) selects
(2,0),(3,0),(2,1),(3,1); its complementary CURRENT frame is (b,d).
C4(d,b) selects (3,1),(2,1),(3,0),(2,0), frame(a,c).
The same-version selected-four limits/split/inverse-join helpers establish
bounds, distinct cells and owner/frame partitions before target use.
Ownership/provenance comes from array/foreach resources, never numeric address
equality. Callback values are recovered CURRENT, never replaced by entry snapshots.
Compiler-derived bool casts, pointer operations and all four selection cases
are source/MIR/AST linked. Third/fourth Output=bool lifetime bindings preserve
c3/c4 and a,b,c,d in outer scope. Allocation/free correspondence was reviewed
against exact frozen producer/free rules and observed all-path frees.

Normal and every reachable **C1/C2/C3/C4 direct unwind** restore CURRENT
four owners, F/thread/type/destination resources, complete original resource
posts, unit return and leak/dead-code checks. Earlier unwinds exit before later
callbacks. Five helper proofs precede target. Independent C3 and C4 raw,
projection/allocation and intended-first-VC reviews **PASS for these exact
bounded projections**. C4 has nine intended target-first controls; source
mutant rejection is admission refusal, not a semantic negative. Default-off
C1/C2/C3 evidence and mandatory unbound refusals are retained. Raw collectors'
pending/global acceptance fields are preserved; VF0 does not admit a profile.

Native premises: entry raw source4/F/thread/types, positive T size and optional
T destination remain **supplied** to these prefixes. Earlier native typed
source/F/opaque-MaybeUninit-frame lemma and type interpretations were **proved
separately**, not linked in composition. No native→C1 or actual caller→sort4
theorem. Optional destination/MU inverse, actual scratch/inline-const guards,
actual caller CFG and generic layout/ZST remain open; ZST is merge-owned.
No assumption `new(inner(old)) == old`. Runtime std/generic signatures unchanged;
ghost-stripped source SHA-256
`3602050e45025745d80b308802be9e552310959abcee4b95bfe8c24f8ca04b72`,
std SmallSort blob `40939f922bcb6fdc7ee0d30427fa861827043827`.

## Exact fresh proof/profile identifiers

Common tool HEAD `f76012fb518703b1d98e243ac4f487f16877cfcb`,
nightly-2026-09-25. C3/C4 frozen kernel SHA-256
`37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`.
Parser `7bf12f1205ecf033e3bf66f11b4326c20d2876d68e19006d5db59f3e45ae91c2`,
exporter `b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796`,
refiner `b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28`,
effective lib.rsspec `d33b2a7a284557002b4f7afe3d5e63f813e51f818c588712d743b4b46f9bedaf`.

C3 bound proof=infra `aa6e5a725f71506602903f95b1832a32fa849e50`:
translator `d2f132148d409eb9a9e27afd24603d992405ec1984849817da9e427ab070db6e`,
bound patch `d6165630a3a7e4452be49849557df2790368fd62773424c939fe98d0aec9177d`,
**dispatched profile JSON** `001a4437ed3c8df72bb24ca703f1b415d45aa3220342ecbe30c0916bf29ce29a`.
Source `087123b12072a19b0490260e509ce6773c1ed3dce0ed7c14c95991fdaf82996e`,
preAST `7dbc4ed84339a7a5f3056239d8ef67b9dc0cb7657f6d2cb2d954435ce462f35b`,
postAST `9ca21fdc2e3f199ea73d3ff62f1ec8cf29e7f4f8a3e269dd433e6711c9013397`.
[Fresh evidence](FRESH-A956B0B2-EVIDENCE.md),
[independent review](FRESH-A956B0B2-REVIEW.md), review SHA-256
`d528bfa5806376d41e36496bee390b5b1502d3e2f2d3b74b8f54524267c2ede2`.

C4 bound proof=infra `203b59258b00ccc8bc2ecc030726fafde3a57d05`:
translator `1eab6eb54fe5c23d53ca72a6d9dfcbbff09c09ffaf26c48a4f450f5068a8d313`,
bound patch `3152f51e7362817bdeba326b7840092418d5a64e85fb851c51a91f5fd156ed3e`,
**dispatched profile JSON** `2fae327bf29cb5038d059e774ba3ec46dd570adcf283daab50b57bf481cbdd2b`,
console `8d686fef29ae6fe5b6adb91a946ff9942aef682baf934b273cc61d71a625527b`.
Source `ba9e6ad3633004c3d934c590462443951ddd6dec80a5df9ffb687ec940958c6f`,
preAST `0ed31137cf55a2ed47ed624a6c61591e4aaf96371df3c2979fc10ce8d95bb222`,
postAST `2f11c68f1cc81ab23ceec03b357f2bbb35ef8dd5c012328fe3846635a3cdc396`.
Normal full MIR `af8dcfda4212ec1e1bd8fcafcb763fe0107fbeb63b6c1a65bc830e2c81bf9f80`
(141 blocks/223 locals), readonly
`aebd7d6219106ba8f6b2fd730bb0a9b0876bea141eb2f06ab7c6e3804abc23ea` (28/110).
[Fresh evidence](../sort4-c4-bound-prefix/FRESH-A5180CD7-EVIDENCE.md),
[independent review](../sort4-c4-bound-prefix/FRESH-A5180CD7-REVIEW.md), review hash
`ebd77b898cc761f4287ef84cabc68c3a03018d66a8d5045e5306031bf9835c4c`.
Later review gates/documentation do not alter the pinned Build inputs above.

## Strict-cut candidate: compiled, downstream proof NOT_RUN

Separately named production-compatible experimental profile, own isolated
VeriFast worktree `/root/verifast-select-compatible-strict-cut-20261010`.
Semantic card and independent addressed design review preceded implementation.
Exact two-file translator+src/verifast.ml delta, not a copied historical kernel:
`01f52d929a3678aed81bef8659f4e0ad6926487da1667139e7a66d6664526154`.
Base translator `4d3a190fcec695415b41162ddf8d71aec6e2826d2b69e7692df306a568add98c`,
base kernel `adbf2c3de02cba7fbdb0b8e203a864e34c1b2ab16de4f6b153477106dbba04d0`;
result translator `753166a81e886bb4e3139614706f9a9b4fb9840f546153f27db7a0a073975704`,
result kernel `7870f3eb6b2978577de54fb23bf8e8bc4daf21a4d7cad18055ee008bbfaf4608`.
No end_lft_binding Noop substitution. Intended live heap/outer type/current
bound escape checks precede rebase; chunk/term/permission conservation,
allocation/free and normal/return/unwind/outgoing-goto obligations retained.
This design/static review is not semantic acceptance.

Fresh proof=infra `f7ff82a29b914c04181ecab4070d64555a61a58f`, dispatched
profile JSON `100abbc9314aa698622e5ae61591191e6a06a795dd1ed5f3fd1934ea6520dfa7`.
Cloud patch check/apply and compile exit0; binary
`253f9f0f283f67eb36cb986c35b40d96869a51b9cbf7e66e29443207f177f122`.
All eleven executed cases have fresh paired MIR export/decode and refinement0.
Wrong/duplicate/strict-OFF marker cases are pre-target admission refusals.
Other eight, including ordinary default-OFF, stop at translator configuration:
`SORT4_HRTB_OUTPUT requires 1 and explicit target bodies` because runner set
`SORT4_HRTB_OUTPUT=0` and empty targets. **Zero AST captures, zero target entries,
zero strict/helper/native proofs**. Outer-type/bound source cases NOT_RUN.
Runner exit0 preserved evidence; final Cloud diagnostic gate FAILURE.
[Independent raw review](../sort4-compatible-strict-cut/FRESH-31F58A87-REVIEW.md).

Finish-only two-line runner correction removes both environment variables;
static parsing and addressed frozen-guard review pass. Correction is **DRAFT,
Cloud NOT_RUN**, not in f7ff82a2 or its evidence. Current profile disabled,
dispatch_authorized=false, profile_accepted=false. Current disabled/draft profile
JSON SHA-256 `a2c7569a78d4982241a94c5ada3f36227e4a9d4c4cc4eef71a680a94a653c454`
(distinct from dispatched profile above). Full default-OFF/escape/
debt-owner-token/exit/refusal regression matrix and fresh helper/native
composition remain NOT_RUN. No downstream theorem or profile admission.

## Builds, accounting and coordinator closure

Each row has proof=infra SHA. All artifacts' archive/inventory/index hashes
verified; full C3/C4 bound and strict raw evidence inspected. External text
chunks not separately fetched. Capture-only runs/replay do not supply proof.
Setup refusals are not intended semantic negatives.

| Build ID | Proof/infra SHA | Cloud status | Charged seconds | Evidence outcome |
| --- | --- | --- | ---: | --- |
| `b38ac0e8-c818-4424-8480-8fe2386be1eb` | `3b675ffba979ce7c2af6f482459ce29549ac923f` | FAILURE | 413 | C3 setup failure; no target |
| `bdef4a7c-3a5e-4253-8fa0-65ccbbba8f89` | `b8441cb06f77cd24bc349bbbfd0d3658ecbe023f` | SUCCESS | 449 | Fresh C3 capture; target NOT_RUN |
| `a956b0b2-4e05-4c19-90b4-408f381ba1fc` | `aa6e5a725f71506602903f95b1832a32fa849e50` | SUCCESS | 461 | Fresh C1→C3 VF0,335 |
| `eb66efc6-a85f-4ffd-b20a-9382f22c5538` | `f0c7b0d0ae185cdb9c733e3aa49fd4af597bb7d9` | SUCCESS | 517 | Fresh C4 capture; target NOT_RUN |
| `a5180cd7-3ad7-4199-9b1f-56c31876cc4d` | `203b59258b00ccc8bc2ecc030726fafde3a57d05` | SUCCESS | 487 | Fresh C1→C4 VF0,370 |
| `31f58a87-9dc0-4f74-ad3a-ac4888f6ffbd` | `f7ff82a29b914c04181ecab4070d64555a61a58f` | FAILURE | 348 | Strict candidate compiled; AST/target NOT_RUN |

All six receipts, exact createTime/finishTime, dispatch tokens, submitted config,
source input and archive SHA-256 remain in [BUDGET.json](BUDGET.json).
Charge is ceil(createTime→finishTime), including setup/failures:
**2675/3600 seconds; unused 925 closed, no carry**. Earlier account is separate.
All six terminal/accounted/download_verified, active_build=null, no unresolved
Build. Terminal reservations reconciled; own v2 ready request withdrawn by
`control.py withdraw-request` (confirmed). No foreign accounting or coordinator
changes. No timeout/permission debt or pending dispatch. A pre-Build bounded
transport refusal incurred zero charge; recipe retained required pins without
changing transport limits.

## First blocker and concrete next work

Primary: actual first `select_unpredictable(c3,c,a)` needs a proved callee
contract on this exact current tool. Historical FRAME-shadow/cleanup selector
proof is on another chain and cannot transfer. [First-select next gate](../sort4-first-select/NEXT-STEP.md):
new-session same-current-tool **nine-body capture-only** with
`SORT4_NESTED_FINGERPRINT_MODE=9`, C-prefix scope flags off; capture exact actual
source/full paired MIR/preAST and qualify the callee/type-specialized contract
with its own full normal/unwind/helper proof before composing a consumer.
A new FRAME/cleanup semantic rule needs its own trust decision.

Secondary: new-session fresh strict capture-only Build with corrected absent
HRTB variables, then addressed fresh AST review, complete required trust matrix
and same-version native helper proof before native composition. Optional MU
inverse/guards/ZST do not follow automatically. No Build may use this closed
window/account. Resume requires a new user session/budget; no automatic restart.
