# First Network Cloud session follow-up

The N3 prepared ledger at `BUDGET-N13-20261023-N3.json` is Network's first
Cloud ledger. Before the next Network session, the workflow owners must add
`network` to `FIRST_SESSION_OWNERS` and `CLOUD_HISTORY_OWNERS`, then review the
follow-on task preparation path against this ledger. This task records the
follow-up; it does not edit the shared workflow package or coordinator.

The ledger is a fresh 3600-second account for phase
`NETWORK-N13-EXACT-2026-10-23-N3`, with no previous ledger. It is prepared
locally and remains subject to the Network client phase registration and
independent candidate review before any Cloud operation.

## Preparation lineage

The task assignment baseline was `a9cf1678`. The worktree's initial HEAD for the
assigned task was `924c1dd39aa36f591033877d5812465a41325b44`; the preparation
bundle uses the implementation baseline containing the pinned Network profile
and recipe. These are separate source identities: neither changes the pinned
Rust source (`cd371e035c7e573760c43bf934d53e8118ee3e7d`) or stock VeriFast
identity (`809de...`). The session preparation baseline is recorded in the
bundle's `spec.json` and `ledger.json`.

The recipe's infra closure names the prepared ledger path so first-session
bundle validation can include its pending bytes. Cloud submission still uses
the selected live ledger passed to the client, rather than treating the
committed source snapshot as the active budget account.
