# sort4 autonomous night results — 2026-10-07

DRAFT: N11 proof repair is being prepared; this report is not a closeout yet. Owner night authorization
and frozen profiles: [phase card](SORT4-NIGHT-PHASE.md). Source, artifact identities,
full experiment hypotheses and historical failures: [journal](EXPERIMENT-LOG.md).

## Accepted components

- Exact experimental fieldless layout profile d4a12525: full existing matrix,
  metadata, classifier/span and native controls accepted in N2. The patch stayed
  SHA256 d4a12525bcdbdaa4deb82058d6cc0037c8c09fa508ad2eeb14386b2753693a14.
  This is bounded-profile acceptance, not full-model soundness or generic layout.
- Stock pure [index theorem](SORT4-INDEX-LEMMA.md): all five independent Boolean
  answers yield bounded logical indices and each original ID exactly once.
  No order/purity/coherence assumption. N4 proof and N5 saved classifier replay
  accepted; original failure evidence preserved.
- Stock [integer-rank order/stability](SORT4-ORDER-LEMMA.md): exact five-comparison
  network, arbitrary unchanged integer ranks, original IDs retained among ties.
  Equal-key instability control fails its intended assertion. The relation/rank
  transfer is a separate component, not a lift from the older concrete i32 result.
- Stock [scalar selected-cell range composition](SORT4-MEMORY-OPERATIONS.md):
  containment and per-copy separation for arbitrary nonnegative stride, including
  zero. This links exact logical source choices to destination offsets0..3;
  no pointer, resource, overflow or operation-UB theorem follows.
- Existing generic H_align remains accepted independently; it was not rerun.
  Distinct logical ZST IDs can share numerical addresses.

## Blocked, diagnostic and design boundaries

The [actual pointer-valued select callee](SORT4-SELECT-CALLEE.md) retained its
MaybeUninit/DropOnPanic/three intrinsic selections. Export/decode/refinement and
body integrity passed, but the first proof error is unresolved runtime
MaybeUninit::new at adapter21. Pointer selection/provenance/permission/frame and
normal/no-unwind posts are unproved. No T:Copy bound, runtime if replacement,
assumed summary or historical helper patch chain was introduced.

The [memory-spec audit](SORT4-MEMORY-OPERATIONS.md) distinguishes typed references,
raw-byte/typed copy and MaybeUninit ownership. Existing copy specs require an
initialized destination and do not provide the needed raw-scratch interface.
Reference/copy numerical-alignment enforcement has no accepted operation-level
negative test here. Manual alignment assertions are geometric evidence only;
this coverage gap does not invalidate independent geometry.

Future owner decisions concern (1) a reviewed source-linked constructor/union
ownership route, followed by actual intrinsic/DropOnPanic verification, and (2)
a reviewed raw-destination copy/ownership interface, including optional bytes,
padding/validity, preserved source/frame and the single eventual owner. These are
designs, not implemented trusted extensions. Actual FnMut effects, preserved keys
for functional application, all five panic resource posts and caller storage
preconditions remain necessary for a complete unrestricted sort4 safety proof.

General safety domain remains ZST/non-Copy/non-Freeze/raw scratch/legal comparator
effects and panics. Functional fixed-order/key-preservation premises are separate.
RAPx CLOSED/NO-GO; B/C NOT RUN. No other sort, tool, external publication or PR.

## Hosted run ledger

All runs manual on GitHub-hosted Linux; every failure counts. All source commits
are on challenge-8/research. Full SHAs and artifact ZIP hashes are in the journal.

| Night run | Actions evidence / source SHA | Job seconds | Outcome |
| --- | --- | ---: | --- |
| N1 | [37547307118](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37547307118),6bbd25a240ff4d2966c2dcdfed5d79936bc0638f |145| Layout harness fixed; native C++ annotation syntax failure |
| N2 | [37547890530](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37547890530),3f5c9e3126a6db0599f1b989f03146e143342d04 |154| Full layout matrix/audit accepted |
| N3 | [37548195599](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37548195599),03e23cbf56ff3d9e7d79923a0a1d8f15e88fe879 |23| Ghost include/block syntax failure |
| N4 | [37548475221](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37548475221),fa74d92a120cc6990e5f65b94b31e72f2fb50d2f |44| Index proof pass; negative classifier inconclusive, repaired by saved replay |
| N5 | [37548811698](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37548811698),6a12b4e39621eb057712f9084b809f86da6c9b77 |41| Rank order/stability and saved-index processing accepted |
| N6 | [37549040942](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37549040942),aed1d970acb656cd29149241bf6720198895adac |32| Actual callee first blocker MaybeUninit::new |
| N7 | [37549385441](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37549385441),b288370f1a1e6b34c26ef63764c73be2ced452c9 |40| Range helper integer case residual; intended negative accepted |
| N8 | [37549955948](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37549955948),9b25c410f6f69bdf5649aabf98481501824cec1e |27| Full scalar range component accepted |
| N9 | [37550139106](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37550139106),4d7aebcea01c58472e7ef03c4c1611a12d3c673d |1810| Timeout at equivalent-count sum; no full bridge/negative |
| N10 | [37553115842](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37553115842),3ea303b682b63da3237a3d543ce3229b48c2848b |323| Equality repair passes; strict-count sum timeout |

Budget so far:10/12 NEW,2639/10800 summed job-seconds;
layout repair2/2 closed. No local build/verifier/test/replay/extractor execution.
Downloaded logs/build evidence remain in /tmp, never committed. Main changes
expose only minimal manual workflow inputs; no research-history merge into main.

N9 was configured at30minutes, but upload/cleanup made actual job time1810s;
all10extra seconds are counted. Later jobs reserve120s for cleanup and use300s
per ghost fixture; incomplete proofs stay inconclusive. Pure SWO/network composition
is a prepared unverified project, not an accepted component.
