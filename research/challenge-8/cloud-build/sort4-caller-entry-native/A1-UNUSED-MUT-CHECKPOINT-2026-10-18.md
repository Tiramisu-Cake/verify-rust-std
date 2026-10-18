# A1 unused_mut fix checkpoint — 2026-10-18

Owner select-sort4; branch research/night-select-sort4-cloud-2026-10-09.
Started at d2444867, matching remote; no newer commits existed. Eight pre-existing
local Evidence Brief instructions/policy edits and historical checkpoints,
source patches, profiles/pins and all old ledgers are byte-preserved. Current
STATUS changed as requested; its old contents are preserved in a dated snapshot.

## Exact candidate and scope

Candidate/source implementation commit `e58a75bbdcf6704175ceebcd72a227607a92d2ae`;
release binding publication `ab803728`. Exact proof and infra both equal that
candidate SHA. [Release binding](A1-UNUSED-MUT-RELEASE-2026-10-18.json) contains
all source/tool/helper/profile/recipe/control/coordination hashes.

Profile `A1-RCG-UNUSED-MUT-PROFILE-2026-10-18.json` SHA256
`f3782dcaa2de2355739fa7134ada8c6df71a52ebf59e3e75037104fec77c5fb0`.

New full R patch `required-item-representation-unused-mut-2026-10-18.patch`
SHA256 `91fe9ad49c34d834e435605d95fb183e92e03c72f3d353e588dd7092fbeb6466`;
exporter R-after/C-before/C-after source SHA256
`c29d0d4692eab84257fe61036d6e41dbc11ee3ad999005df4ffb157bb8b463ad`.
R-before is unchanged. The patch differs from old R at exactly the approved
`let mut kind` and encode_required_clause `mut out` bindings; deny(warnings)
remains. The old patch/profile/pins are retained, not rewritten.

Tool source base `f76012fb518703b1d98e243ac4f487f16877cfcb`; compiler
nightly-2026-09-25 / `f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f`.
C patch SHA256 `e7cdc8a8504338ccaab760975c1a3f1a739211d7f8d531dd214babc2005d894e`;
R/C translator/schema and frozen kernel/model/prelude/refinement pins unchanged,
including kernel `37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`.
Runtime binary hashes are not supplied by this Brief; no successful tool receipt
is inferred from source pins.

New authorization `SORT4-A1-UNUSED-MUT-FIX-CLOUD-2026-10-18` is explicitly bound
in coordinator/entry/runner to the immutable C protocol
`SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17`. This retains C bytes/pins,
without reopening the old account. New root result records both identifiers.

Source-only validation applied43 frozen pre-R patches, old/new R and C, matched
all expected maps and proposal equivalence.13 inert helper pins/26 route closure,
10 dispatcher admission tests and4 same-Build reuse identity tests PASS.
[Source check](A1-UNUSED-MUT-SOURCE-CHECK-2026-10-18.json),
[independent Luna High review](A1-UNUSED-MUT-REVIEW-2026-10-18.md).
Committed Git closure/config preflight restored33 infra +107 proof paths from160
objects; payload504218 bytes,169/191 substitutions. No compiler/exporter/source
extraction/refinement/verifier executed on VPS. Source/synthetic PASS is no proof.

## Window, Build and account

T0 `2026-10-18T08:37:29Z`; main deadline `10:37:29Z`; finish/checkpoint absolute
cutoff `11:07:29Z`. New account960 Cloud seconds/max1 Build/timeout900+60 reserve;
old330/960 with630 retired and all earlier closed accounts untouched, no carry.

Sole Build `7c26b389-1ad9-45c8-9adf-089125476fdb` through v3 coordinator:
created09:01:41.175877758Z, started09:01:41.935008081Z,
finished09:08:53.320178Z, status **FAILURE**. Submitted config SHA256
`b54b646c52589c95e2e42a869e5c05b4f15b6ed626756ffb77e11cd735b99c41`.
Coordinator charged **433/960s**, execution432s; unused**527s retired**.
Account CLOSED_ONE_BUILD_R_ONLY_FAILURE, Build1/1, no retry/carry. Request
withdrawn and v3 schema3/max_active3 shows no reservations. No download_verified
set. [New ledger](BUDGET-A1-UNUSED-MUT-FIX-2026-10-18.json).

Owner later extended local work by1h: main11:37:29Z, finish/checkpoint12:07:29Z.
The closed CI account retains its original deadlines and actual accounting; no
new Build/raw-audit authorization. A repeated Brief check after the extension
returned the same stage failure/counts and no detailed diagnostic.

## Available ordinary evidence and first blocker

[Brief](A1-UNUSED-MUT-EVIDENCE-BRIEF-2026-10-18.md),
[index](A1-UNUSED-MUT-EVIDENCE-INDEX-2026-10-18.json) and
[processing receipt](A1-UNUSED-MUT-PROCESSING-RECEIPT-2026-10-18.json), processor0.4.0,
retrieved via existing authorized reader only; Brief/index byte SHA256 match receipt.
Archive SHA256 `4da91b4e0f81a8527bfbd45466c21e38daa1cb8cc57860648ec352c389a849ce`.
Processing VERIFIED_ARCHIVE_AND_INVENTORY,356 inventory files verified and2
metadata exceptions cross-checked.272 text entries/chunks indexed; remote chunk
bytes not checked. These integrity facts do not establish formal verification.

Source claims: NOT_ACCEPTED_AS_REPORTED, run_exit0, evidence_complete=true,
diagnostic_complete=false, verification_accepted=false. Build FAILURE is separate
from these fields; successful collector/wrapper exit does not grant proof credit.

**First established blocker:** tool-reconstruction /
`a1-R-only-native-reference-build`, TERMINAL exit**2**, recorded timeout budget491s.
Processor marks stage/audit correlation CORROBORATED_SOURCE_REPORT. Audit member
SHA256 `216c3a8ce72b1e6a0bdff71e0a67f25e9eac0e9fba6930212e3a82789de593f4`;
stage member SHA256 `66620752e728d7b7f66dfe0a20704d714845afd825a1f3fe1f18123e3b0e1e90`.
The corresponding log is indexed/correlated with SHA256
`f3ba5380316c6aee2aad00bc004aaaade6af5f9d2ba75f6b0569134314c81a9b`;
the ordinary agent did not read or download it.

**Remaining uncertainty:** failure_diagnostics.messages=[]; no actual compiler /
make diagnostic or child command/status is exposed. R-only is a combined exporter
and console target. Exporter compilation alone and console completion alone are
therefore UNESTABLISHED. The report does not establish whether the old unused_mut
errors disappeared or what new/same component caused exit2. Elapsed time, an empty
message array or changed log hash cannot select that cause. Historical diagnosis
for57ea65a3 remains valid for that old Build only.

## R-only receipt, final C, P1 and all26 rows

R-only combined build **FAILED/2**. Its success receipt is downstream of the exit0
gate and was not issued by this runner according to pinned control flow; absence
of an individual receipt file was not independently audited. Final C apply/build
is downstream and **NOT_RUN by source flow**. No reference equality or compiler
identity admission is claimed. The exact two source edits are applied/static-checked;
runtime successful removal of those compiler diagnostics is not established.

The new processor explicitly reports **26 source-reported rows, NOT_RUN=26**,
with verified proof-audit member provenance. The same pinned26-row inventory
is unchanged. Each row below is NOT_RUN, not intended-negative PASS:

| Row | Reported result | Proof credit |
| --- | --- | --- |
| `N-alpha-valid` | NOT_RUN (source-reported) | none |
| `N-binder-collapse` | NOT_RUN (source-reported) | none |
| `N-binding` | NOT_RUN (source-reported) | none |
| `N-clause-redirect` | NOT_RUN (source-reported) | none |
| `N-clauses` | NOT_RUN (source-reported) | none |
| `N-default-contract` | NOT_RUN (source-reported) | none |
| `N-duplicate` | NOT_RUN (source-reported) | none |
| `N-false31` | NOT_RUN (source-reported) | none |
| `N-free-region` | NOT_RUN (source-reported) | none |
| `N-freeze-contract` | NOT_RUN (source-reported) | none |
| `N-no-F` | NOT_RUN (source-reported) | none |
| `N-region-swap` | NOT_RUN (source-reported) | none |
| `N-source` | NOT_RUN (source-reported) | none |
| `OFF` | NOT_RUN (source-reported) | none |
| `P-dispatch` | NOT_RUN (source-reported) | none |
| `P0a` | NOT_RUN (source-reported) | none |
| `P0b` | NOT_RUN (source-reported) | none |
| `P0c` | NOT_RUN (source-reported) | none |
| `P1` | NOT_RUN (source-reported) | none |
| `R1` | NOT_RUN (source-reported) | none |
| `R2` | NOT_RUN (source-reported) | none |
| `R3` | NOT_RUN (source-reported) | none |
| `R4` | NOT_RUN (source-reported) | none |
| `R5` | NOT_RUN (source-reported) | none |
| `R6` | NOT_RUN (source-reported) | none |
| `R7` | NOT_RUN (source-reported) | none |

P1 compiler→actual-AST mapping/equality gate is NOT_RUN. P0a/P0b threshold
body/conformance proofs and P0c caller are NOT_RUN. All intended negatives,
seven regressions and synthetic controls remain NOT_RUN; none receives compiler /
refinement provenance or formal credit from local service tests.

N-false31 own default and Freeze body/conformance, own receipt issuance,
threshold32/len32 admission and caller len<=31 assertion are all **not reached by
pinned source flow**, consistent with its source-reported NOT_RUN. Individual
substage receipts/results are not separately exposed. No positive-baseline
receipt was substituted or credited. [Machine result](A1-UNUSED-MUT-RESULT-2026-10-18.json)
records the basis/limits for every row and lifecycle field.

## Next concrete step and stop reason

[ADMIN-AUDIT-REQUEST](ADMIN-AUDIT-REQUEST-7c26b389-2026-10-18.md) requests separately
authorized administrative extraction of the first causal build error, command /
component/status, last confirmed substage, original marker/case provenance and
full SHA256 references. Result <=16KiB and <=30 total raw context lines. The
request itself is not raw-access authorization. No raw fallback was used.

The single permitted Build is spent and its R-only combined stage still fails;
the ordinary Brief lacks the actual error needed for an evidence-based next fix.
This is the concrete external diagnostic blocker. Further changes beyond the two
approved removals or another Build are not authorized. Stop at this checkpoint;
obtain the bounded diagnostic before proposing the next candidate.

Full A1/A2 remain NOT ACHIEVED and the threshold/interface hypothesis remains
unaccepted. Even a later complete matrix would not establish actual
small_sort→helper, A2/ZST/resource redesign, C5/copies or sort8.

## Temporary-file cleanup

Removed18 explicitly owned obsolete source/preflight scripts and redundant
report copies (931201 bytes), after comparing report duplicates with repository
records. Coordinator state directories and all unknown/foreign artifacts retained.
[Cleanup manifest](A1-UNUSED-MUT-CLEANUP-2026-10-18.json). No raw evidence was read.
