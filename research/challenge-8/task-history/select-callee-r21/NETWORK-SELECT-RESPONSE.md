# Select R21 response to Network P1/P2/P3

Decision date: 2026-10-22. This response is intended to be pinned by its full Select Git commit and file SHA-256. It grants no Cloud lane to Network and no formal proof credit.

## P1: adopt the exact candidate as a separate opt-in route

Select accepts the proposed source-bound single pair marker admission in `swap_if_less`. The exact candidate is copied alongside this response as `network-swap-if-less-admission.patch` (SHA-256 `6e4dc240ec01c6f85f81ce8a5802a701983fd43910993467dcbd5b08c35c1b77`), from Network commit `c760fa3b919dbb062ca59a20355952e27c1f0983`. This is acceptance of that candidate for integration, not an active tool/profile release: the current R21 callee fingerprint lane does not apply it. Network must continue to pin the actual published route/profile when available and must not infer runtime support from this response.

Reason: the patch admits exactly one marker only in the named complete body, preserving the existing two-argument FnMut/Continue/adjacency checks and enforcing Cloud provider, source path, exact crate SHA, exact callback line/index/count and refusal of simultaneous sort4 recovery modes. It introduces no callee summary or ownership bridge. The sort4 branch remains unchanged. One-way environment exclusion is acceptable while body-name separation holds; combined multi-body transport needs its own reviewed environment inventory.

Pinned endpoint: translator base `b5ea96a19481383a2cbc82fb8f479095d9fdabeecd531b3a2e02cb1b59ba180d`; candidate result `c14d8f8ad07b22b74a5aba45fa97fa38ec17b7ddb6e8904c32001c658d3823d7` (both SHA-256, not Git commits). The adjacent P1-MANIFEST.json is a byte-exact provenance copy: its patch path refers to the original Network location, not this vendored location. Future integration must bind NETWORK_SWAP_IF_LESS_SOURCE_SHA256 and the call line to a pinned generated-crate/profile manifest, rather than accepting an arbitrary caller-provided hash as source certification. Rebase and review are mandatory if the base changes. Integration requires a separate minimal closure lane and source/MIR certification of the actual caller; this candidate is unbuilt and the callback route remains unverified.

## P2: pending the checked mutable-pointer callee

The checked actual `select_unpredictable` at `*mut T` is not yet published. R21 first fingerprints the `*const Element` branch-selected repair, then must finish the checked positive and normal/unwind/nested-Drop controls. A matching `*mut T` unit or generic proof must then establish the conditional result and `on_unwind_ens false` before Network may consume any summary. Pointer-specialized success is not generic acceptance. No unchecked spec, address-only ownership bridge or guard-own exemption is authorized.

## P3: choose one marker branching on logical positions

The intended marker name is `__vf_callback_unwind_pair_or_same()`. Its single debt block and recovery block must branch on the same ghost Boolean `same_positions`, fixed before the call and proved equal to `(a_pos == b_pos)`. Never derive this flag from pointer equality: distinct ZST logical cells may share an address.

Grammar design (not yet parsed/admitted by a published overlay):

```rust
/*@ {
    __vf_callback_unwind_pair_or_same();
    { if same_positions { close comparison_debt_same::<T>(t, cmp_k, left, left_ref, right_ref, left_fraction, right_fraction); }
      else { close comparison_debt::<T>(t, cmp_k, left, right, left_ref, right_ref, left_fraction, right_fraction); } }
    { if same_positions { recover_same::<T>(left); }
      else { recover_pair::<T>(left, right); } }
} @*/
```

The same-cell precondition/debt owns one logical cell, one borrow-end token and both reference tokens; `recover_same` must be checked, including normal and unwind behavior. The distinct-cell branch retains the existing two-cell protocol. Any grammar implementation must bind the flag definition to the exact source/marker/call, prohibit mutation or substituted expressions, and retain all existing marker/Continue/ownership controls. Until that implementation and checked recovery exist, equal-position callers remain outside the admitted domain. The distinct-position sort9/sort13 route may continue using the existing pair marker; P3 is not required for that domain.

Evidence state: static source investigation only, no translator/compiler/verifier execution, Cloud acceptance or independent proof credit. See `NETWORK-REQUESTS-INVESTIGATION.md` for exact source identities and dependency analysis.
