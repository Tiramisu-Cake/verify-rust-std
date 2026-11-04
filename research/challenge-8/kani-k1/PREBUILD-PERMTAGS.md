# PERMTAGS — G1 packet

Task: `TASK-PERMTAGS.md` at `8a1655ba45b7561765aaac3b1849ec66cefcf2bd`.
Branch: `experiment/kani-k1-permtags-20261105`; worktree: `/root/verify-rust-std-kani-permtags`.
Tooling base: `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; runtime/workflows/tooling unchanged.

## Review and dispatch boundary

This packet is prepared for exact-SHA PRE-BUILD review. No build has been dispatched and no
verification result is claimed. Dispatch requires coordinator GO for the published packet.
The request selects stable owner `k1-network`; it must be free at dispatch. If a different owner
is required, revise the request and obtain review/GO for the resulting exact SHA.
Use only `tools/k1g.sh`; after dispatch, start `watch BUILD` and end the turn.

## G1 request

`permtags-g1-20261105-01`: diagnostic, controls=true, gcb-e2-standard-4, jobs=1,
10 minutes per root, default solver, seven roots under
`slice::sort::shared::smallsort::verify::permtags::`:

| Root | Expected |
| --- | --- |
| `tag_types_preserve_source_routes` | SUCCESS |
| `network_u8_n9` | SUCCESS |
| `network_u8_n13` | SUCCESS |
| `network_u8_n16` | SUCCESS |
| `general_u64_n9` | SUCCESS |
| `fallback_cell_u8_n16` | SUCCESS |
| `reject_duplicate_network_u8_n9` | FAILED: `permtags: every input tag occurs exactly once` |

Maximum reservation: (7 × 10 + 30) × $0.0135 = **$1.35**, against own cap **$2.50**.
Project cap remains **$118.96**; dispatch must pass the existing project ledger gate.
Main window: 180 minutes, closeout: 30 minutes; at most G1 and G2, with a new GO for G2
and the task's allowance of one compile-error repair per build. Any repair still consumes budget/time.

## Property and limits

Inputs are ascending distinct identity tags `0..N`; each comparison reads both arguments using
volatile reads (Cell reads its payload without mutation), then independently returns `kani::any()`.
Real trait entries run with unwind bound 34, without verified-contract stubs. The sole manual
stub covers and cuts `panic_on_ord_violation`; checks apply to normal return, excluding unwinding.
The checker asserts output-tag range and an N-bit all-ones u64 mask. With N output slots this
implies every tag appears exactly once; no u128 or full-width shift is used. The negative control
runs the same real network call as the positive N9 root, then overwrites element 1 with element 0
using `ptr::copy`, and applies the same checker.

Transfer to arbitrary values is conditional on the source-level assumption that, on the same
type-selected route, the implementation only moves whole elements and does not branch on payloads
except through comparison answers. Fresh symbolic answers include every comparator-answer sequence;
identity tags track distinct input positions even for equal payloads. This is bounded evidence,
not a machine-checked generic refinement theorem. Payload-mutating comparators, comparator panics,
sortedness and stability are outside the claim. Organizer-default checks are unchanged; no extra
uninitialized-memory, valid-value or permission checking is requested.

Tags use the source types themselves: Unstable u8 (Freeze+Copy, size 1, network predicates), Stable
u64 (Freeze, general, scratch 48), and Stable Cell<u8> (blanket insertion). A separate root checks
the applicable type bounds, dispatch predicates, sizes, scratch constant and thresholds. Threshold
alone does not distinguish network from general; the u8 predicate checks establish its size branch.

## G2 candidates, pending G1 and separate GO

Mandatory remaining roots already compile into the opt-in module: `network_u8_n17`,
`network_u8_n32`, `general_u64_n16`. Optional: `general_u64_n17`, `general_u64_n32`.
Five rows would reserve (5 × 10 + 30) × $0.0135 = $1.08, or $2.43 together with maximum G1.
Prioritize mandatory lengths and G1 TIMEOUT retries over optional lengths; consider kissat only
for a timed-out row. Recompute own/project budget and remaining window before preparing G2.

## Validation and closeout

Local validation is limited to request validation, source/diff review and tooling-base equality;
no local cargo, rustc, Kani or CBMC. Compilation and proof outcomes remain pending Cloud Build.
The request validator accepted all seven roots; whitespace checks passed and lane files equal
the tooling base. The new source was reviewed against the existing Part 1 safety stub pattern.
After each build use bounded summary/peaks and check-tooling interfaces, without opening raw logs
or credentials. Final `RESULT-PERMTAGS.md` (at most 35 lines) will bind build/commit identities,
report per-row time/checks/covers/memory, distinguish verified rows from timeouts or unrun roots,
record the transfer assumption, compare with the task's source-reported direct-proof baseline
(u8 through N9; u64 N8 with kissat), and identify SUCCESS candidates within 60 seconds.
