# Status-only Build metadata snapshot

Defect: one `control.py status` invocation can call `gcloud builds describe`
for the same Build during global reconciliation, local reconciliation, and
the final status summary. The watcher has a 20-second operation timeout, and
the repeated read can exceed it even when each individual read succeeds.

Applicability: only the synchronous main status command. During that command,
the client may reuse successful JSON responses for an exact read-only
`builds describe BUILD --region=global --format=json` argument vector. Cache
scope is one invocation and one active context.

Invariant: retain all reconciliation, account, owner, ledger, dispatch-token,
and status checks, as well as original errors and exceptions. Do not cache
mutating requests, list queries, exceptions, or results across commands.
Consumers receive independent deep copies; failed commands and JSON decoding
failures remain retryable. The context is restored in `finally`, including
when status processing raises.

Controls: isolated tests cover exact-query matching, distinct Build IDs and
arguments, copy isolation, fresh and disabled contexts, error/timeout/JSON
decode retries, context restoration after errors, and mutation calls. An
integrated fake status path exercises the same Build through global
reconciliation, local reconciliation, and final status output while asserting
one underlying describe call. No Cloud API or proof command is used.
