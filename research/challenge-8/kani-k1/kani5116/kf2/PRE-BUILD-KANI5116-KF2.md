# PRE-BUILD — KANI5116 KF2

The PRE-BUILD REVIEW marker identifies the exact pushed commit. T0 starts at coordinator GO.
Branch `experiment/kani-k1-kani5116-20261110`, slug `kani5116`, stage `kani5116-kf2`, owner `k1-merge`.
Main window 300 min plus 30 min closeout.

## Identities and reserve

- Tooling base `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`. Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`.
- KF1 patch SHA-256 `fd510b8a47ffff2005cc2362af6c25db790d1b579a23c0c990f6d606a983aa71`.
- Expected applied tree `46f37ae9abe9bb747ec7b7de33212484ed175a1b`, from KF1 with the same pin and patch bytes.
- Request `kani5116-kf2-main-20261111-01`, SHA-256 `43baae98e1f9510a91d23637ac85278df02b6ed188d1f6310730381d2e943606`.
- Patched `verify-std` diagnostic route, standard4, jobs 1, controls on, inventory off, organizer flags.
- Reserve 6 × 4 + 30 = 54 min at $0.0135/min = $0.7290 within $0.80. Published branch actual $0.5805
  through KF1 gives $1.3095 including reserve within $2.30. Dispatch rechecks branch and project ledgers.

## Library and expected rows

D1 and D2 each use `modifies(v)`. Their length guard supplies insertion offset 1, and D1 ignores
its caller scratch. D3 uses `modifies(v)` and requires
`size_of::<T>() * SMALL_SORT_GENERAL_SCRATCH_LEN > MAX_STACK_ARRAY_SIZE || v.len() <= SMALL_SORT_GENERAL_THRESHOLD`.
The general route's local scratch has 48 slots and needs `v.len() + 16` when `v.len() >= 2`.
The fallback uses the same guarded insertion as D2.

| Row | Exact suffix under `verify::default_contracts` | Expected |
|---|---|---|
| P1 | `stable_default_n2` | SUCCESS, 0 failed, 3/3 covers, D1 with empty scratch |
| P2 | `unstable_default_n2` | SUCCESS, 0 failed, 3/3 covers, D2 |
| P3 | `freeze_default_n2` | SUCCESS, 0 failed, 3/3 covers, D3 and outer frame |
| S0 | `freeze_forwarder_body_n2` | SUCCESS, real Freeze forwarder, order and outer frame |
| S1 | `freeze_forwarder_stub_frame_n2` | SUCCESS, verified stub via forwarder, outer frame and return |
| S2 | `freeze_forwarder_stub_order_n2` | FAILED, one located failure, order after stub via forwarder |

All use unwind 4. Insertion makes one N2 outer iteration and can shift once. General uses a two-item
loop over halves, an empty extension range per half, and one bidirectional merge iteration. Slice
havoc has two elements. P1–P3 record both input orders before the call and check covers after return.
P3 and S0–S2 use the same NonCopyU8 comparator function item and active slice `backing[1..3]` of
four symbolic bytes. S0–S2 assume initial order, so a skipped call cannot trigger S2's order failure.

Static checks passed: request validation, KF1 patch digest, lane parity with tooling base, Rust
scope and line lengths for added lines, rustfmt with zero diff, and 109 Python tooling tests.

## Bounded evidence after GO

Dispatch the exact pushed branch with `k1g.sh dispatch experiment/kani-k1-kani5116-20261110`.
Register `k1g.sh watch BUILD` and end the turn.
After wakeup, use `k1g.sh summary BUILD` and `k1g.sh summary BUILD 0 6` for the named rows,
counts and cover totals. Manually require S1 return cover 1/1 and exactly one S2 failure with
`KF2 S2 weak Freeze stub permits reversed output` at `verify/default_contracts.rs:102`.
The bounded renderer has no success field for a `Verified stub` target or PFC resolution trace.
If the expected rows pass, record the PFC rows and S0/S1/S2 behavior with direct target trace
`UNCONFIRMED`. Record any compilation or resolution blocker from the bounded summary as reported.
Run `k1g.sh check-tooling BUILD c98d7cee0d509b1633ab61c9a1ae989e286c8e2a` and
`k1g.sh budget BUILD`. Compare summary head, request, pin, patch and applied tree with this packet.
