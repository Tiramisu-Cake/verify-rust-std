# Networks experiment journal

Historical common logs remain untouched. Own phase starts 2026-10-07 at
bea62488b44f8c557e45e04cb4eb259b0173422f. Budget 1800 summed hosted job seconds.

## N9 — prepared before implementation/dispatch

Actual obligation: sort9_optimal lines426–467, 25 actual swap_if_less calls.
Hypothesis: exact call sequence composes abstract compare-exchange into a sorted
9-element prefix and permutation of occurrences. A dropped final comparator
should break sortedness; a duplicated CE output should break permutation.

Domain: arbitrary nine logical occurrences and fixed total preorder on
preserved keys; all abstract CE calls normal. Rank variables are unbounded
mathematical integers, including ties. Separate permutation component admits
arbitrary Boolean decisions and retains complete occurrence identities.
Rust T unrestricted including ZST; the abstract proof has no physical memory.
Full normal target: sorted prefix, same occurrence multiset, fixed suffix modulo
callback effects. Full Rust safety/unwind target is in SWAP-CONTRACT and SOURCE-MAP;
this deliberately pure fixture does not discharge it or claim a panic model.

Profile: unchanged official VeriFast26.09/source809de459, release archive
da1b619f...98aa; no tool patches. Binary sorting plus checked per-CE threshold
commutation/general rank theorem, separate identity-count conservation.
Pure C ghosts require no Rust MIR/refinement; Rust bridge remains OPEN.

Controls: named positive binary/rank-transfer/permutation lemma bodies return
with full declared posts and leak checks; missing-final-CE negative rejects its
marked sortedness assertion on a concrete binary counterexample; duplicated
output negative rejects marked occurrence conservation. Unknown operation,
parse/setup/unrelated helper/timeouts are INCONCLUSIVE, never intended failures.
Full generated source/logs, before/after hashes, source map, verifier command and
exit, exact negative line and summary retained in Actions artifact.

Decision: positives and intended negatives all accepted -> prepare N13 under
same frozen profile. Routine ghost syntax/generation/classification failure ->
fix within phase and NEW SHA run, preserving failure. Missing semantics -> stop
without patch. Budget bound -> checkpoint. No automatic merge.

Dispatch: smallsort-research.yml on challenge-8/networks;
proof=verifast_sort4_components, sort4_component=networks9, budget_minutes=30.
Actual network job cap10min, per proof180s; only one job/experiment.
Source SHA/run/cost pending.

### N9 first result

Proof SHA `d433216f635c58d84ed9b9cde7bcab95c2c38549`,
[run37636248489](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37636248489),
[full artifact11490266217](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37636248489/artifacts/11490266217).
Artifact ZIP SHA2565ef244a960dc58e8fb7eac5c30a925e8db194b0b62b7d7a2008fa64d914ecab0,
41,706,974bytes; original raw results/classifications preserved.
Stock console dc672335da76fe1bb06cf7ebca916185c34edb65466df0a937645a437c7f0ecc.
Complete source gate matches25 calls with lines441–465; all source hashes unchanged.

Binary PASS,0.203703s/83 statements,496 return/leak paths. Threshold exit124 at
180s: only order_at_0 visited,12142 complete path return/leak checks; no full
8-adjacency theorem. Identity exit124 at180s,207556 path return/leak checks;
no full universal-choice permutation theorem. Millions of repeated statement
paths demonstrate branch explosion from inline conditionals, not a false proof.
Both timeouts INCONCLUSIVE; successful paths do not replace whole-unit acceptance.

Sorting negative: omission of step25(5,6), input mask11 (bit i = occurrence i),
mutant output000001011; correct error88,16–18, VC`!(true) || false`.
Permutation negative: duplicate0 instead of preserving3, correct error12,55–57,
VC`((0 = 3 ? 1 : 0) + (0 = 3 ? 1 : 0)) = (0 + 1)`.
Manual intended failures established; raw automatic classifiers INCONCLUSIVE:
they demanded literal false and counted untimed diagnostic-note headers twice.
Preserve this failure; do not overwrite original results.

Full Actions log and ZIP read, all generated sources/source map and log heads,
tails, errors, named bodies and complete path counts audited. No Rust proof.
One executed job14:23:19Z–14:29:40Z = **381s**; skipped jobs consume0.
Budget381/1800,1419 remain.

## N9b — within-profile decomposition, prepared before next dispatch

Same actual source/domain/normal target/unwind boundary as N9. Hypothesis:
pure min/max/selection fixpoints with **checked-body** local threshold and
two-occurrence conservation lemmas avoid repeating branch splits across the
25-step symbolic sequence. Keep every original final ordering and occurrence
count assertion, arbitrary ghost ranks/tokens/decisions and all tool gates.
New proof abstraction, not a new trusted tool rule; no assumed or bodyless lemma.
Exact local normal lemma posts: min/max commutes with arbitrary integer threshold;
selection pair preserves count of arbitrary occurrence q for arbitrary decision.
These proofs have no runtime/unwind/memory claims.

Classifier repair uses timestamped body headers and the two observed exact
normalized negative predicates. Require exact assertion line/columns, execution,
sole error and VF1. Hosted rejection controls: unrelated line, predicate, body,
target execution, column, timeout and source change. Preserve original N9 raw
INCONCLUSIVEs; a new source requires a new run. If all original positives and
intended negatives pass, advance N13; unsupported/profile change still STOP.
Cap10min/180s proofs, within remaining1419jobseconds. Run/SHA/cost pending.

### N9b result

Source `70eaa2d9499a47d45d2c9af74de4ef643f74ed0c`,
[run37637872959](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37637872959),
[artifact11489639313](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37637872959/artifacts/11489639313),
143501bytes. Full logs/artifacts/source hashes read and audited.
Same unchanged console dc672335; exact25 source calls PASS.

Binary PASS0.256290s/83 statements/496 return-leak paths. **Arbitrary-decision
identity permutation PASS**, checked pair_count_choice body plus whole25-step
symbolic sequence,0.507588s/216 statements,3 whole normal-return/leak paths.
No ordering/purity restriction in this permutation theorem; q and all25 decisions
are arbitrary. Neither result proves ownership or callbacks in Rust.

Threshold helper body PASS two normal paths, but whole8-adjacency unit TIMEOUT
at180s: only order_at_0 entered, stops near second-pass step5 before later
assertions. Log is only27287bytes: branch explosion removed, remaining SMT
unfolding of a threshold chosen as a nested final min/max expression is expensive
(66.891/135.728s at lines181/184). General rank theorem still INCONCLUSIVE.

Both intended negatives now automatically accepted at original exact line/
columns/predicates. Original source fixtures unchanged; wrong line/predicate/
body/target execution/column/timeout/source change rejection controls7 per case
all PASS. Original N9 classifications remain unmodified.

One job14:34:54Z–14:38:07Z = **193s**; total **574/1800**,1226 remain.
No active networks run.

## N9c — universal threshold summary, prepared before dispatch

Same actual source, stock profile, domains and complete final rank-order posts.
Hypothesis: composing the projection with an independent arbitrary integer t
avoids expanding a nested network output at every CE; then a checked universal
summary can be instantiated at each final right-neighbor rank. The binary
network and independent arbitrary-decision identity theorem are retained.

Define source-bound min/max output formulas as a finite per-wire fixpoint DAG.
Check all CE transitions against that DAG. Each per-adjacency universal projection
lemma has post `(output_i>t) -> (output_i+1>t)` with unbounded arbitrary input
ranks/t. Final rank application calls these **verified same-unit** lemmas at
t=output_i+1, proving every original adjacent rank<= assertion. This is proof
decomposition, not weakening the rank-order target or adding a trusted axiom.
All body/post/return/leak gates stay enabled; no tool semantic changes.

Same intended negatives and14 rejection controls. If N9c accepts the whole unit,
advance N13 with identical scheme; otherwise inspect exact failure and reassess
within remaining1226jobseconds. Source/run/cost pending.

### N9c result and reassessment

Source `910c183c678785224074d24dbee03ca8397bee44`,
[run37638843477](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37638843477),
[artifact11490214161](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37638843477/artifacts/11490214161),
207784bytes. Full generated sources, source admission and logs read.
Stock profile unchanged. Binary, identity and both exact negatives+14controls
PASS; threshold helper PASS2paths. Universal threshold_at_0 TIMEOUT180s,
45 completed return/leak paths (47 inclhelper),7892log lines, other7projection
lemmas and general_rank_order NOT REACHED. No general-rank theorem accepted.

Independent threshold removed the giant dependent argument, but Boolean
short-circuit assignments still enumerate512 projections while carrying a
rank/DAG/threshold context. Each completed path costs seconds; increasing the
timeout alone would not scale to13. Reassess representation, not tool semantics.
Job14:41:43Z–14:44:58Z = **195s**. Total **769/1800**,1031 remain.

## N9d — reusable Boolean summary, prepared before next dispatch

Same actual source/domain/full sorted-rank and identity target. Hypothesis:
proof of Boolean model outputs on cheap Boolean-only paths can be exported as
a verified summary; applying that summary after a branch-free threshold
composition avoids repeating the rank context on512paths. Retain every original
binary/identity/final-order assertion, now add exact Boolean wire-DAG correspondence
and explicit binary sorted-output post. Define pure ce_band/ce_bor fixpoints;
their bodies are ordinary Boolean AND/OR, no trusted delta. Threshold updates
use those pure fixpoints, check both rank and Boolean model correspondence per
source step, and call the **verified same-unit** binary model lemma on original
projections. Universal threshold posts/general-rank application stay unchanged.

This is the final evidence-backed decomposition candidate before a fresh
reassessment if it again times out. No larger timeout, tool patch, weakened
posts, removed controls or zero-one-only general-order claim. Same two intended
negatives and14classifier rejection controls; exact NEW N9d run required.
Acceptance -> N13 under identical frozen profile; preserve any failure and
checkpoint within remaining1031jobseconds. Source/run/cost pending.

### N9d result: full projection bridge, final application timeout

Source `240d2ef9d8de1a0d64c2b5eec1dd683906d7a4aa`,
[run37640086725](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37640086725),
[artifact11491447574](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37640086725/artifacts/11491447574),
520445bytes. Full logs/generated sources read; source/profile/control gates
unchanged. Binary explicit sorted-output summary PASS on all Boolean inputs.
All8 universal independent-threshold lemmas PASS with full posts/return/leak
checks by33.170432s. Whole rank unit includes506complete paths (496binary,
2localCE,8projection). General_rank_order then enters; verified threshold calls
take milliseconds, but direct <= assertions take9.630/104.551s while repeatedly
expanding high-arity wire terms. Unit times out at180s after the fourth adjacency
call; general_rank_order post/return/leak not accepted. No suppressed assertion.
Identity, both intended negatives and14classifier rejection controls PASS.

New evidence localizes the remaining issue to final arithmetic application,
not the bridge or model correspondence. Generic arithmetic can be proved on
scalar formal variables and composed through a checked summary, avoiding wire
unfolding for this tautological contradiction. This is a localized fix supported
by the completed8projection bodies, rather than another speculative rewrite.
Job14:50:32Z–14:53:46Z = **194s**. Total **963/1800**,837 remain.

## N9e — scalar arithmetic application, prepared before dispatch

Same full targets and model definitions as N9d. Add checked-body ghost lemma:
`requires !(left>right) || right>right; ensures left<=right`, proving right>right
false, then not(left>right), then left<=right on arbitrary mathematical integers.
Each original final application first calls its verified universal threshold
summary at t=right output, then this scalar lemma, then retains the original
adjacent <= assertion and full general-rank sorted-output post. Its prerequisite
is established by the verified projection lemma, never assumed.

Hypothesis: scalar arithmetic proof isolates the tautological reasoning from
unnecessary min/max DAG expansion. No modified tool, kernel, trust model,
deleted obligation or weakened domain/post. Acceptance requires whole rank
unit VF0/all named bodies/return/leak, all other positives and both intended
negatives+14rejection controls. Then N13 is the next authorized step. Remaining
837jobseconds, jobcap10min; reassess/decrease cap if remaining<600 before N13.
Source/run/cost pending.

### N9e result: complete abstract network9 acceptance

Proof source `58f1680ec7951a265535f0462701511478f6efa3`,
[run37641057339](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37641057339),
[artifact11491971819](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37641057339/artifacts/11491971819),
516055bytes. Full sources/logs read, hashes independently matched to result
records. Full-file std pin and unchanged tool pins match the phase allowlist.

- Binary: PASS151statements,496 return/leak paths,1.189188s; explicit model-output sorted post.
- Threshold/rank: PASS3583statements,508 return/leak paths,25.729124s;
  all12 named bodies including all8 universal projections, local CE/scalar
  helpers, binary summary and final general_rank_order, with full sorted post.
- Identity: PASS216statements,3 return/leak paths,0.408071s; arbitrary25
  decisions and arbitrary token q, all pair-count and final-count assertions.
- Omit-final-CE sorting negative: VF1 only at line88 columns16–18,
  predicate `!(true) || false`, witness mask11/output000001011.
- Duplicate-occurrence negative: VF1 only at line12 columns55–57,
  predicate `((0 = 3 ? 1 : 0) + (0 = 3 ? 1 : 0)) = (0 + 1)`.
- All14 classifier rejection controls PASS; no disabled body/post/leak gates.

The arithmetic cut solves the localized timeout without a trusted assumption
or any deleted assertion. Thus mathematical N9 composition is accepted under
abstract CE; source sequence admission accepted. General key-order transfer is
the finite-class argument in INTEGRATION, conditioned on fixed total preorder
and preserved keys. Actual Rust helper proof remains open; no public target done.
Job14:57:38Z–14:58:19Z = **41s**. Total **1004/1800**,796 remain.

## N13 — prepared before dispatch

Actual obligation: sort13_optimal at pinned std source, len>=13, exact45 literal
swap_if_less calls (lines490–534, pairs/indices in SOURCE-MAP), first13 elements
only. Hypothesis: the identical stock proof decomposition scales to13 and
establishes all12 adjacent output orders and complete occurrence permutation.

Domain: arbitrary13 mathematical Boolean inputs for binary theorem;
unbounded arbitrary13 integer ranks plus arbitrary thresholds for general-order
bridge; arbitrary45 CE choices and arbitrary occurrence q for permutation.
Abstract CE outputs `(c?B:A,c?A:B)`; sorting additionally requires c iff
key(B)<key(A), fixed total preorder/strict-weak-order quotient on keys preserved
for every occurrence and normal callbacks. Safety for arbitrary legal T/F is a
separate open Rust obligation; no Copy/Freeze restriction or stability premise.

Full target normal post: all12 adjacent prefix keys ordered and each original
occurrence exactly once, suffix unchanged by network operations modulo legal
callback effects. Rust unwind target is the proposed effect-aware initialized
ownership post after prior completed exchanges, without current exchange or
sorting promise; this ghost-only experiment deliberately does not prove Rust
normal/unwind safety. See SWAP-CONTRACT for full actual helper posts.

Tool: unchanged official VeriFast26.09/pins above. Positive gate: exact source
admission, all named ghost bodies/full posts/normal return/leak checks VF0.
Sorting negative omits final CE and requires a concrete binary witness rejecting
its specifically marked adjacent-order assertion. Permutation negative duplicates
an occurrence and must reject its specifically marked token-count assertion.
Target line/column/predicate are recorded before each verifier invocation in
negative.json; frontend/setup/helper errors and timeouts are inconclusive.
Retain both negatives and14 independent classifier rejection controls.

Outcome mapping: all positives/negatives accepted -> document N13 composition
and integration conditions, checkpoint/commit/push without merge or public-goal
claim. Failure -> inspect first causal full evidence, preserve it, consider only
localized proof/checker correction under identical profile within remaining796s;
new trust change or insufficient budget -> checkpoint, no semantic patch.
Per-file180s/inner480s/job600s bounds; no parallel networks job.
Source/run/cost pending.

### N13 result and localized reassessment

Source `fccae976b8979105a19910f8e2181809d5d39103`,
[run37641704629](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37641704629),
[artifact11493050599](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37641704629/artifacts/11493050599),
13675667bytes. Full logs/sources read (1045251binary and1048480threshold log
lines); all source/log hashes matched results, std/tool pins unchanged.
Exact45 source calls admitted, first(0,12)line490,last(5,6)line534.

Binary PASS263statements,7633 return/leak paths,41.875257s, full sorted-output
post. Identity PASS380statements,3 return/leak paths,3.050710s. Both intended
negatives and14 rejection controls PASS. Sorting witness mask254, mutant output
0000010111111; sole error line152 columns16–18 on `!(true) || false`.
Duplicate-token sole error line12 columns55–57 on the recorded count predicate.

Threshold unit TIMEOUT180s,7639 completed return/leak paths; binary, local CE,
scalar arithmetic and threshold_at_0..2 complete, threshold_at_3 entered.
No verifier error; remaining8projection bodies and final rank theorem not
reached. No complete N13 general-order theorem accepted. The repeated45-step
projection bodies dominate cost after the binary summary; each body computes
identical rank/bit state for the same arbitrary threshold. New evidence supports
sharing this checked computation across all12 postconditions.
Job15:02:21Z–15:06:22Z = **241s**. Total **1245/1800**,555 remain.

## N13b — combined universal projection, prepared before dispatch

Same exact std sequence, domains, complete normal-order/permutation target and
open Rust normal/unwind safety boundary as N13. Unchanged stock profile.
Hypothesis: one `network13_threshold_all` body can check the identical45-step
rank/Boolean correspondence once and export ALL12 original universal threshold
posts. Final rank theorem invokes this **verified same-unit** summary at each
right output, then the verified scalar arithmetic lemma, and retains every
original <= assertion and full sorted-output post. No per-step assertion or
final-order obligation removed; N9 generator remains unchanged.

Retain binary theorem, identity theorem, both exact negatives and14classifier
controls. Whole unit VF0/all named bodies/full posts/return/leak required.
Failure remains inconclusive, inspect/reassess under actual remaining budget;
acceptance closes only abstract N13 composition/source admission, then final
documentation checkpoint/commit/push. No tool/profile extension or Rust claim.
Reduce job cap to8min and inner execution cap420s to fit remaining555s including
preparation/evidence reserve; each verifier case retains180s. Source/run pending.

### N13b publication / dispatch infrastructure checkpoint

Normal git pushes repeatedly rejected by remote Internal Server Error from
15:09:49Z onward. Remote ref remained fccae976; no Actions run was created.
Used authorized Git Data API to upload the exact tree
`f88bd1930c08c7fc4f0d0a5ef18860846ab7d5e1` and commit, then update ONLY
refs/heads/challenge-8/networks with force=false. Final local/remote proof commit
`a2be90886dc1e61c43b29d7ddc1cb95e028bd569` matches exactly. Unpublished original
4ed252e was amended only in metadata; no experiment used it. Intermediate API
object e5ac261 lacked terminal LF in its commit message and was never assigned
to a branch. Preserve exact source SHA a2be908 as the prepared candidate.

Workflow dispatch through gh workflow run and direct API by ID/name repeatedly
returns HTTP500 (one response explicitly Content-Length0, not a proof error).
Specific branch run list still ends at completed37641704629; no N13b run exists.
No duplicate run, local verification fallback or budget spend. N13b remains
UNVERIFIED as a whole rank unit. Final checkpoint/results distinguish accepted
N13 Boolean+identity results and written general-order transfer from pending
complete machine-checked rank application. Remaining555s and8min job cap retained.

Local infrastructure note: server disk was full before the separate checkout.
Existing pip/go-build caches were preserved by relocation to
/dev/shm/challenge8-preserved-pip-cache and
/dev/shm/challenge8-preserved-go-build-cache, with symlinks at their original
/root/.cache locations; nothing deleted or installed. Downloaded evidence stays
outside the repository in /dev/shm. No local compiler/verifier/test ran.

### N13b hosted continuation accepted after recovery

Ordinary documentation-checkpoint push succeeded. Remote/local source confirmed
`6851001f78b02144e25037c55d55644fa34b30de`, an unchanged-proof documentation
descendant of a2be908. After branch list showed no new run, one dispatch was
accepted: [run37642585521](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37642585521),
created15:17:26Z. This is the only active networks run; remaining555s before it,
jobcap8min/inner420s/percase180s. HTTP500 history above remains preserved.

### N13b result: complete abstract network13 acceptance

Proof source `6851001f78b02144e25037c55d55644fa34b30de`,
[run37642585521](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37642585521),
[artifact11492478839](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37642585521/artifacts/11492478839),
14053017bytes, ZIP SHA256
`70575120a310e448bc45af234bd4ebe7c5442baec7bd865a5e0be96ec641aea0`.
Full ZIP/source/log evidence inspected, streaming every line of the1045251-line
binary and1046209-line rank logs. All source/log hashes matched results; exact
std admission/pins and stock tool source/archive/console unchanged.
Generator SHA256994afa65a24c1deb73fd120ac88c96fa5d86eb971f58adba678c850a1153d0c4;
runner SHA256672b0f12d7e8491592acae1ddad37a7050a83cf73d1865db19b47f1427f7d172.

- Binary PASS263statements,7633 return/leak paths,78.411524s.
- Full threshold/rank PASS1126statements,7638 return/leak paths,154.095956s.
  All5 named bodies checked: binary, threshold_ce, rank_from_threshold,
  threshold_all, general_rank_order. Universal projection body/all12 posts
  complete by135.684067s; final rank application/full sorted-output post and
  normal return/leak complete at154.095956s.45 local bridge calls,12 summary
  applications,12 scalar arithmetic calls and every original final assertion.
- Identity PASS380statements,3 return/leak paths,5.246296s; all45 arbitrary
  decisions and arbitrary q, checked local pair/final total counts.
- Sorting negative VF1 sole error line152 columns16–18, exact predicate
  `!(true) || false`, mask254/output0000010111111, inverted positions5,6.
- Duplication negative VF1 sole error line12 columns55–57 on the exact token
  count predicate recorded in N13. Both bodies/target statements reached.
- All14 classifier rejection controls PASS. No missing posts/assertions,
  unproved assumptions, tool patches or suppressed return/leak gates.

N13 binary/identity and complete unbounded-rank composition accepted. The
written finite-class transfer supplies the conditional general-key theorem;
actual Rust helper/normal/unwind safety and public Challenge goals remain OPEN.
Job15:17:31Z–15:21:45Z = **254s**. Total **1499/1800**,301unused. No active
networks run. Completed phase checkpoint is documentation-only: no rerun needed.
