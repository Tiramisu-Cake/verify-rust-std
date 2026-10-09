# One-cell insertion diagnostic — INCONCLUSIVE, no actual theorem

Phase `NEXT-MERGE-DROP-CALLER-CLOUD-2026-10-09`, owner `merge`.
The exact source/runtime was unchanged. The selected caller is `insert_tail`,
source lines 550–551, source SHA-256
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`,
blob `40939f922bcb6fdc7ee0d30427fa861827043827`.

The mutable guard has a different storage requirement from immutable general
`CopyOnDrop` at line 279. Saved actual MIR and new fragment MIR confirm mutable
guard storage and immutable `tmp`. This does **not** prove that canonical FBC
can be closed: none of this session's five target bodies reached that close.
The general V4 physical-half failure was not rerun or made a prerequisite.

## Fresh Cloud evidence

| Build / exact proof and infra | Result | Conservative seconds |
| --- | --- | ---: |
| `000add59-443d-4cc6-bc67-cc412e3fc9bd` / `6d138cd960b04078bbc3432782abe466cbb17c32` | Nine new cases stop before proof execution at AST serializer `MergeFractionsStmt` TODO | 359 |
| `5fddf20d-a40f-4559-ac7c-c7c304d0ca22` / `d793eaa25f5cb4de92cda44ba9fc94ea1162d296` | Serializer repaired; five target cases and four MD controls remain INCONCLUSIVE at unrelated admission errors | 318 |

Both collectors report SUCCESS / diagnostic complete, **verification accepted
false**. Both complete archives, external text-log chunks/indexes, submitted
configs and source identities were integrity verified. First archive:
`bc5362e9a01237b15be2c1c1c9552ad6e7502d8fa424fabd95e640fbb1114f11`.
Second archive:
`6c2f55a9d0ff430efc508310801cd07f5dff18f8a595b11e264e5a4695ea8e09`.
Second config:
`9d2838a3466425dd4a45a5fb014220800a7295c69e57b3cd49081ce2f267e286`;
source input:
`7feac65b5637abde582fcab35c722f57229495f24a742e8208ae442bbe6d09a6`.

Second-run target cases `positive`, `after_fbc_false`, `after_recovery_false`,
`missing_held_owner`, `double_physical_fbc`: stages export/decode/VF/refinement
`0/0/1/0`; source and MIR admission true, AST admission false, target body unseen,
copy unexecuted. All fail at `verified/lib.rs(13,5–6)`:
`List expression must not contain patterns`, on the own-predicate syntax
`[?f]*v.src`. This is a fixture admission defect, **not a resource rejection**.
Neither authority negative nor duplicate-FBC negative reached its obligation.

Tracked-MD positive, missing-init and read-permission controls fail at
`verified/lib.rs(11,38–39)` on `precreate_ref(&tmp)`:
`Taking the address of this expression is not supported.` Missing-precreation
fails at `(11,15–18)` on runtime `&*tmp`, with the same unsupported-address
error. All stages are `0/0/1/0`. These are INCONCLUSIVE, not expected negatives.
Logs do reach each MD function, but not its intended permission check or post.
The new tracked-MD profile therefore has no passing regression gate and cannot
be used as an accepted ownership/reference bridge.

Affected stock/six V3b constructor positives retain full normal post/return/leak
PASS_FRAGMENT_ONLY, and matching false controls pass in both builds. Ordinary
call normal/unwind smoke passes. Those are fresh regression results for their
existing domains; they give no target one-cell or actual Drop credit.

## Profile and replay boundaries

The opt-in profile is `experimental-merge-six-tracked-md-onecell-v1`,
**NOT_ACCEPTED**. [PROFILE.json](PROFILE.json) records the full frozen tool
identities and the reviewed rebase plus observational serializer patch.
Second console SHA-256:
`d631913a27b35331ef63325011173638e64bb81f3c4aec5def317f995cef57a5`.
The original stock/six tools remained intact. Kernel, parser, prelude,
copy model, exporter and refinement checker were unchanged.

Separately, saved first-run MIR was replayed after fixing classifier handling
of nonassignment statements. All five MIR admissions are true. This is parser
replay only: first-run VF2 cases remain INCONCLUSIVE before proof, with no new
theorem or negative credit. The same correction is present in the second
exact-SHA run. Unchanged V4, coordinator18, OR17, RESOURCE11 and native matrices
are NOT_RUN in this session. Callable actual Drop, canonical payload post,
compiler glue, normal forget and full insertion are NOT_PROVED.

## Applicability review and next decision

The fragment supplies initialized writable tail, one CURRENT T owner,
thread/type and geometry facts. Actual `tail.read → ManuallyDrop → &*tmp` is
represented by exact source bytes, but its target proof has not executed.
The first caller debt is comparator line 541 → current tail/sift owners,
F/frame/thread and closed shared borrows before read line 550. None is newly
established here. Positive-size T is a diagnostic domain premise, not a new
restriction on unrestricted actual insertion; ZST remains open.

The adapter also removes the Drop impl and immediately copies held→tail with
literal count 1. Actual execution must first copy sift→gap (557), update
`dst=sift` (558), and only then reach Drop (306). The adapter is not a reachable
actual Drop edge, and the len≥2 bulk theorem does not cover it. No unverified
actual Drop summary was installed.

Source/spec review establishes a separate **no-go for reusing this readonly
held-reference protocol as the full insertion invariant**: the later comparator
at 566 may legally mutate T through interior mutability. `init_ref_readonly`
requires that this facility is unnecessary; adding Freeze/Copy/purity is not
allowed. Real normal/unwind paths also need genuine comparator reference debts,
CURRENT owner transfer and complementary tmp storage recovery before
StorageDead. This is an applicability finding, not a matched verifier negative
or proof that mutable canonical FBC is impossible.

Recommended next single task: repair the source-linked MD/own admission using
existing supported syntax/address mechanisms, then run its isolated positive
and exact authority controls before retrying mutable construction→FBC. Preserve
the exact read/initializer, current owner and complementary fractions; do not
mint authority, change immutable storage into compiler disposal, or assume a
shared ownership bridge. If the pinned frontend cannot represent the actual
immutable local address with existing mechanisms, record that specific no-go
before proposing another semantic change. Passing this gate would still leave
the actual first-shift/dst-update/Drop edge and comparator acquisition open.

Read-only repair candidates, **NOT_RUN / not implemented**: existing scalar
syntax in `merge/overnight/copy-cases.rs:24` is `[?f](*src |-> ?v)`, so
parenthesizing the target chunk is the first fixture repair. Historical
`verifast-address-taken.patch` adds continuation after fraction-merge address
analysis; the MD cases put a fraction-merge before their tmp address. Try
precreation before that merge using the existing `req true` operation, with
corresponding missing-precreation control ordering, before considering a new
trusted traversal patch. This hypothesis requires fresh Cloud positives and
intended negatives; neither generic MD applicability nor successful recovery
follows from reading the historic patch.

Total **677/3600 conservative Cloud seconds** (359+318), 2923 unspent and closed.
Second incremental tool build 28.50s; nine-case staged group 5.37s. First runner
setup/build 168s and incremental MD build 4.64s. The remainder includes cold
setup, other controls and publication; no unsupported exact setup/verification
split is claimed. Both own builds terminal and download verified; own slot
released, ready request withdrawn. No new experiment after the minute-46
reassessment; session checkpoint completed within the main hour.
