# READY for SAME11 single-call delta review

Task98dde2de28e13381092f20c082ba90f90ce34773, original15/high/FastOFF;
no subagents/model changes. New isolated worktree:
`/root/kani-issue4591-singlecall-r3-w15`, branch
`fix/issue4591-singlecall-r3-w15`, clean at local skipped candidate:

- Source: `f82934ca97caaa1270d5279054aa950173868be5`.
- Tree: `2ff34bc99ec3fe63579202c196f0ca288e318919`.
- Sole parent: `6fca00af805b5c62b58e3e3f29eef183d6939907`.
- Published base tree: `7a3d5c05b5d663d515c198b2bfa7c4926ae133ac`.
- Main/base parent: `969f4648980a8e66cd0ca32fd3e714a55ac32cef`.
- Main tree: `c9a832dc1647c51ac3036429e5f97e73eb717ba7`.
- CI-request SHA256: `8fb98acee9861fb9a94133d060d568fd0b7735d5840fcd9fdf7fc2fc6aacf4bc`.
- repair.patch SHA256: `0215d0d906a2fc9b4bcfdb57ec9c759d918d24fd6662d9ffcbc2f3971ad65476`.
- full-main.patch SHA256: `b0799ef2f4b96ef2e3adc84db4a61a2e4f1301c5aba30d2c60ea690fcf80056f`.

The g0 delivery commit containing this package is reported externally to avoid
a circular self-pin. MANIFEST.json seals every other package file. Only this
new owned output is committed in g0. Frozen authorad50/review0f4/GO1a32,
postrun INPUTS and all prior packages remain unchanged.

Diagnosis: both old fixtures reach the selected provider directly and through
its body copied into f, consuming the same enforced wrapper twice. Native
positive failure confirms the restriction; the negative is source-predicted
because the expected suite never ran. New caller-contract harnesses execute
one exact selected call, with the ordinary provider in Assert mode inside it.
Negative input1 passes caller post and fails the provider's ensures0.
Compiler and reachability/once guards are unchanged. DIAGNOSIS.md explains
the supported composition and explicit coverage limit.

Both affected fixtures repaired; other36 harness definitions, all expected
bytes, same-function PFC/verified controls, replacement safety, no-assert and
overlap modes, and actual issue caller-overflow remain. Offline validation
passes; three index replays reproduce the tree. Connected metadata accounts
all12 native jobs:7success/1failure/4cancelled. Full diagnostic/actual checkout
identities remain UNKNOWN. No repaired native/typecheck/MIR/compiler/rustfmt/
Kani/CBMC/fullrunner result exists: NOT_RUN. Old failed native history and
static approval history remain intact. No full-matrix green claim.

Upstream main read-only recheck matches969f; remote branch recheck matches6f at
recorded times. No rebase. Every native workflow/action/script/library/
toolchain/dependency byte matches the reviewed base. A future nonskip repair
must be a same-tree sibling with sole6fparent. Full969f..future contains exactly
old nonskip6f plus new nonskip repair, excluding the skipped candidate, so the
remote update can fast-forward. Future final head NOT_CREATED; gate source,
metadata tests and actual rejection receipts are included. No push occurred.

Next: SAME11-DELTA-REQUEST.md, exact independent delta review; return any finding
to original15 in a new immutable repair. After exactAPPROVE root prepares
GO-request HOLD_FOR_OWNER_EXTRA_ITEM1_GRANT. This package does not issue that
future GO or claim reviewer approval. Item1 remains31/31 EXHAUSTED, item2 12/17,
total43/48 as references; potential owner morning+1 is NOT_GRANTED. No repeat,
refund, accounting mutation or dispatch. Full standard future Kani all5OS and
all other jobs plus Format/Deny are prepared, PR-only scope deferred. Owner
alone publishes PR/issues/comments; S3 remains independent and untouched.

Authorized offline author work is complete. Independent SAME11 review is an
external handoff gate; author self-review cannot satisfy it. Native execution
is a separate exhausted-budget/owner-grant gate. No other offline source
repair is blocked or left unattempted within the two-fixture scope.
