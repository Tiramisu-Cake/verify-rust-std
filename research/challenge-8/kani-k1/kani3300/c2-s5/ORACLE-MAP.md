# S5 semantic oracle map

ORACLE-MAP.json maps all 21 previous cases/roots: old source/JSON pointer/condition,
unchanged operation/contract/mode, replacement selector, exact N and every required
failure, useful assertion, permitted write and source cover. The map precedes deletion.

Exact-base observations supplied by the owner at g0 d9a2a40c93, run43630584079, close
strong p2/postcondition-hole with N=3: both read instrumentation failures (`*const u8`,
`u8`) plus exact outer ensures17 FAILURE. Replace has N=2, only those two reads,
no Unsupported, and both return covers SATISFIED in the original input. Hashes/argv/exit
references are in INPUTS.json and the rows. Observed property totals326/250 do not
become golden pins; only exact failure N is anchored to the check summary.

Current S4 capture43621476331 supplies composition N: immutable legal0/hole2,
ordinary ensures0, PFC legal0/negative3, cycle1, unrelated legal0. This is current S4,
not the stale C1b inventory. Each portable split retains actual target/contracts,
initialized/hole values, Move/return behavior and needed helpers. Independent existing
expected controls remain. legal-pair is replaced by two files, one harness each.

Useful blocks require consecutive function/root prefix, Status and exact Description.
Prefix-only generated-function IDs avoid ephemeral closure paths; the exact own
Description disambiguates body assertions from ensures. Frame checks retain user
outside/write roles, not verifier-private checks. All fixtures use regular output,
object-bits12, anchored SUMMARY + ** N of, final verdict and one-harness completion.
No negative root or copied helper retains covers. Only pure true observation hooks
are removed; payload reads/assertions stay. Positive mode companions retain the
SATISFIED witnesses for initialized/uninitialized and base/unrolled paths. Nondet
branch covers are not replaced with universally quantified assertions.

Full inventory/mixed isolation/schema/selector-order relations are explicitly outside
this expected representation: see MIXED-ISOLATION-DISPOSITION.md and REVIEW.md.
Portable-candidate execution, native compiletest sensitivity and three-host portability
remain NOT_RUN; base observations are not new independent proof credit.

## CI43636027466 correction: source-harness exception

Two Replace inputs require an in-crate `#[proof_for_contract(passthrough)]` companion
for `stub_verified` validation. Each now contains the original caller plus the full-domain
`replace_simple_check` companion, but `kani-flags --harness <caller> --exact` selects
exactly one caller (before --cbmc-args). This explicitly authorized exception changes
source harness count to two in these files, and preserves one selected root per oracle.
The separate replace-simple-check.rs fixture still executes the PFC oracle. Companion
presence does not constitute proof execution or mode qualification.

No goldens or intended native counts changed: Replace N2, false-return partition N0.
Only the selected caller emits the verification summary, with its own Checking harness,
consecutive SUMMARY / ** N of, verdict and Complete1total. Cover counts cannot satisfy
the anchored check-summary requirement. See fix-43636027466/REVIEW.md for source tracing.
Native verification of this correction remains NOT_RUN.
