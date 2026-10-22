# Inactive R21 actual-body transport candidate

This candidate copies the R17 full actual-body transport path and the R19
source/tool/profile bounds into a route-specific R21 bundle. It is inactive:
the profile has `cloud_build_enabled: false`, the entry requires it to be true
before dispatch, and no body-lane client or recipe is included. CURRENT-TASK
step 3 authorizes preparing separate minimal routes. The draft stays disabled
until the main agent registers the exact new lane in the existing R21
ledger/client after review, within that phase's current window and budget. This
does not create a new T0, budget, or owner authorization.

Fresh execution identity is `SORT4_R21_BODY_PHASE_ID=
SORT4-ACTUAL-SELECT-2026-10-23-R21` with lane `o26-sort4-body-r21`,
Cloud Build provider and Build ID, and no GitHub Actions environment. Entry,
runner, body, and tool each enforce these conditions. Only after the entry has
passed that fresh route and exact-profile gate does it install the old R17
authorization and A1 phase identifiers as protocol values for the pinned
backend helpers. The profile keeps R17 as `authorization_phase_id` and the A1
identifier as both `phase_id` and `experiment_protocol_phase_id`; neither is
the new route's execution authority.

The new body replaces the only full-body-path use of the 254 KB generic
`a1-runner.py` with the independently pinned 6.6 KB
`a1-cleanup-helper.py`. It still calls the exact
`select_checked_cleanup_helper_lemma` checks and loads the R21 source tool.
The generated full-body source identity, five `is_less(` calls, eight
`hint::select_unpredictable(` calls, four `copy_nonoverlapping` calls,
ghost-stripped runtime equality, normal/unwind ownership posts, source-pair
identity, selected-body gates, checked copy components, reference-own probe,
resource/leak controls, and no-proof-credit classifications remain from R17.
This adds no proof or callee summary and makes no fractional-forget changes.

`a1-tool-r21.py` retains the R17 tool's reconstruction, source overlays, and
control functions verbatim except for a fresh R21 route gate and focus-receipt
routing to the one R21 profile. The old multi-profile fallback was removed.
The R19 profile's std source hashes, compiler/toolchain/model pins, translator
identity, patch/manifest bounds, and source annotation controls remain
unchanged. The new profile changes only route identity, transport module pins,
and inactive-session metadata; it records R19's exact profile hash as its
transport parent.

## Exact pins

The inactive R21 profile SHA-256 is
`d1e0d2ddf6cd8eba5dab5a7b2a68a7530595f9b7745c6f8276f20f155b0f546d`.

| Module | SHA-256 |
| --- | --- |
| `a1-entry-r21.py` | `31f6e6cc56aed85c01286d005bb516605298a990c214fb3f4032f95eada62e99` |
| `a1-runner-r21.py` | `b3ff75b1b24c1119561c41048a395aabac8fd845fa64fd4aa8c030176d324b1b` |
| `a1-actual-body-r21.py` | `ae8c57e0549e3a900ad3660ddd302e0d4029293aa074b6accc132f003b655c16` |
| `a1-tool-r21.py` | `89144fc137403432dbfaa94f75ca5c82d53252caab1a30f4273e7935eb202078` |
| `a1-cleanup-helper.py` | `9af1324a6479896fd43eac8b8ccc3af3a254f28f672ffd4f99f0292cafaf3c45` |
| R19 parent profile | `d4b1b7350d9a9966bedfd0ef50e4c7f7b4cc071ca1f6c4e08d44ba85c36ed622` |

## Validation

Ran `python3 -m unittest -v test_a1_r21_body_transport.py` from
`cloud-build/sort4-caller-entry-native`; all 7 synthetic tests passed. The
tests cover exact module pins, fresh marker/provider/lane refusal, stale R17
authority refusal, profile and backend protocol mismatches, inactive profile
refusal, workspace path refusal, preserved R19 pins, R13 body inventory and
contract text, and verbatim R17 tool reconstruction/overlay/control functions.
The tests import definitions and use synthetic environment/profile objects;
they do not call `main`, `reconstruct`, preparation, compiler, exporter,
verifier, or Cloud services. No proof credit is claimed.

The route gate's 15 synthetic tests also pass from `cloud-build`. They build
separate proof and infra source trees and check that missing or mismatched
infra entry/runner/driver pins fail even when a same-path copy exists in the
proof tree; proof-role helper tampering fails independently. Both preflight
and terminal audit receive `--infra-root` from the isolated runner.

## Integration still required

1. After review, register the exact `o26-sort4-body-r21` lane in the existing
   R21 ledger and client, within the existing phase window and budget.
2. Derive and review an exact proof/infra recipe for this route, including the
   selected profile, R21 entry/runner/body/tool/helper, and all retained
   source/tool/overlay/read dependencies. Do not include the generic runner
   unless a route read-set audit finds a remaining dependency.
3. Wire the new lane's client/config and profile SHA in a reviewed candidate.
   Activate `cloud_build_enabled` only as part of that separately authorized
   registration; recompute the profile SHA and client pin afterward.
4. Run the coordinator's exact-phase admission and independent review before
   any submission. The R21 R17 backend identity is protocol compatibility,
   not permission to spend the R21 body budget.

The preflight validates proof and infra trees by role. Route entry, runner,
and caller driver pins are checked against `infra_root`, where the client
packages them; body, tool, cleanup helper, grammar, fixtures, AST helpers,
probe, capture, std sources, and profile remain checked against `proof_root`.
The shell passes both roots to source preflight and terminal audit. A matching
copy in the wrong tree does not satisfy a pin.

No recipe/client/legacy file was changed and no submission was attempted.
