# Network R4 requests: Select R21 investigation

## Decision

Recommend **adopt P1 as a narrowly scoped overlay candidate**, after the required Codex Luna HIGH review of the exact Select diff. Do not report it as built, proof, or proof credit. The prepared manifest itself says `PREPARED_UNREVIEWED_UNBUILT`; Network's older Claude review is `GO_WITH_NITS`, but it does not replace the current Select review executor.

P1 adds a `swap_if_less` body admission under `NETWORK_SWAP_IF_LESS_CALLBACK=1`. It requires the Cloud provider, the exact `verified/lib.rs` path and caller-supplied SHA-256, exactly one parsed marker, the expected source call line, marker index 1, and no previous callback marker. The existing marker count check still requires exactly one in the admitted body and zero outside an admitted fixture/body. Its body-name check prevents this opt-in from admitting another body. Exclusivity is one-way: Network mode rejects either sort4 recovery opt-in, while the existing sort4 route does not reject `NETWORK_*`; the pinned README records this, and the body-name gate prevents cross-body admission. Mutual exclusion can be added if Select chooses to require it, but is not needed for the present single-body route.

Reject P1 if its base no longer reproduces exactly or the reviewed patch changes. The patch is tied to Select commit `10e13a414a1b6f0efafdee36eea733c91df1ee6b`, profile bytes SHA-256 `d4b1b7350d9a9966bedfd0ef50e4c7f7b4cc071ca1f6c4e08d44ba85c36ed622`, and translator base SHA-256 `b5ea96a19481383a2cbc82fb8f479095d9fdabeecd531b3a2e02cb1b59ba180d`. The reproduction script pins those endpoints and reports 61 static patch-application steps; its documented run did not build or invoke a proof tool. `c14d8f8ad07b22b74a5aba45fa97fa38ec17b7ddb6e8904c32001c658d3823d7` is the **resulting translator SHA-256 prefix/value**, not a Git commit.

P1 only admits the callback-unwind marker protocol. It does not prove `select_unpredictable`, establish pointer ownership, or verify `swap_if_less`. The actual callee at `*mut T` remains P2 and must stay pending until a checked callee proof of the matching source/tool version establishes the requested conditional Boolean result and `on_unwind_ens false`. The R4 generator currently rejects any non-null `select_spec` with “P2 is not published”; do not add a summary spec by inference.

## P3 grammar recommendation

Keep P3 lower priority; the current R4 domain already requires `a_pos != b_pos`, covering the distinct logical positions used by sort9/sort13 while still allowing ZST elements. If supporting equal positions, admit one static marker at the single comparator call and branch its debt/recovery on a ghost flag derived from **logical indices**:

```rust
//@ let same_positions = (a_pos == b_pos);
/*@ {
    __vf_callback_unwind_pair_or_same();
    { if same_positions { close comparison_debt_same::<T>(t, cmp_k, left, left_ref, right_ref, left_fraction, right_fraction); }
      else { close comparison_debt::<T>(t, cmp_k, left, right, left_ref, right_ref, left_fraction, right_fraction); } }
    { if same_positions { recover_same::<T>(left); }
      else { recover_pair::<T>(left, right); } }
} @*/
```

Bind/validate that ghost flag as `a_pos == b_pos` (or make the equality explicit in the marker grammar); never infer sameness from raw pointer equality. The same branch condition must govern the contract: one owned cell for equal logical indices, two for distinct indices. The same-cell debt carries one `borrow_end_token` and both reference tokens; its recovery remains a checked lemma.

## Fixture and protocol dependencies

The R4 candidate is prepared from std blob `40939f922bcb6fdc7ee0d30427fa861827043827`, whose complete `small_sort.rs` SHA-256 is `85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`. Its extraction pins the `swap_if_less` span/signature and inventories one comparator, two `select_unpredictable` calls, one read, one `ManuallyDrop`, and the copy calls. It inserts ghost text only and checks ghost stripping restores the exact body. The callback is `is_less(&*v_b, &*v_a)`; the pair debt labels `left = v_b`, `right = v_a`, then uses the Select `comparison_debt` and checked `recover_pair` declarations. That pair protocol has two cell borrows and is valid only under distinct logical positions; the R4 fixture says equal positions are open.

The P1 line pin is generated per crate as `crate_call_line` and must be passed as `NETWORK_SWAP_IF_LESS_CALL_LINE`; the full generated crate SHA must be passed as `NETWORK_SWAP_IF_LESS_SOURCE_SHA256`. R4's source SHA, generated crate SHA, and P1's translator SHA are separate identities. W7 generates separate crate/line/SHA pins for each network body. Reproduce the Select base and re-pin the exact resulting candidate whenever Select's profile/chain changes.

## Pins

All Network files below are read from commit `c760fa3b919dbb062ca59a20355952e27c1f0983` (`challenge-8/networks`).

| Artifact | Exact identity |
| --- | --- |
| `network/r4/SELECT-REQUESTS.md` | SHA-256 `9749bbdce3ed2e93102ba923d10d6318572d75b37fe248cf0a7656dd9d8da58d` |
| `network/p1/P1-MANIFEST.json` | SHA-256 `5c4f1d1b7c53f50480e26f643a37b57fb04f3d19bc85e9ffb8dbcd896453d457` |
| `network/p1/network-swap-if-less-admission.patch` | SHA-256 `6e4dc240ec01c6f85f81ce8a5802a701983fd43910993467dcbd5b08c35c1b77` |
| `network/p1/reproduce-base.py` | SHA-256 `ee22193edd408bbb15c6170dd57b3218f58b76b4cea2d3e32e5edd1ee0ce48cb` |
| `network/p1/README.md` | SHA-256 `b7cf8cd0673c140ce7cc0af9221fabcb7a431e92528d418366e2dc2fed133a4c` |
| `network/r4/swap-if-less-body.py` | SHA-256 `5593f48a0e895ea24a09c07ce3974ba2913d1b1550dd0ae9e4acedd32ba4581d` |
| P1 resulting translator (manifest value) | SHA-256 `c14d8f8ad07b22b74a5aba45fa97fa38ec17b7ddb6e8904c32001c658d3823d7` (not a Git commit) |

The Network review record is `research/challenge-8/task-history/network-n1/review-7.json` at the same commit, SHA-256 `af6dd130076dc2b6c7b6e7ca286dad361040d6fbf0c30df0b9fe85ef9c304f98`; it records GO_WITH_NITS, a reproduced 61-step base, patch application to `b5ea96a1…`, and no build, translator execution, VeriFast run, Cloud run, or proof credit. This finding is a static investigation, not the required independent review of Select's resulting semantic diff.
