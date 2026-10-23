# Next setup decision after N7 (not executed)

**Owner update, 2026-10-24:** the admission-count interpretation in the historical
closeout below is superseded by [the cold-attempt rule](N7-COLD-ATTEMPT-OWNER-UPDATE.md).
N7 has **0 cold attempts and 2 infrastructure/setup Builds**. Continue with the
localized compatibility repair under that rule; a fresh account is needed because
the historical N7 ledger was closed with carry0, rather than because the cold
attempt allowance was consumed. The options below remain unverified.

N7 exhausted its two cold Build admissions: first EXPIRED before execution, then
one reviewed setup repair. No third cold Build is authorized by N7 even with
5009s budget remaining. Preserve both failures and close carry0; a later task
must provide a fresh account/window and attempt authorization.

The next localized defect is Docker CLI/daemon API compatibility. Exact Brief
line6 reports client API1.52 rejected by daemon maximum1.41. RR/frontend/runtime
source has not been reached, so no RR semantic patch or stronger premise follows.

An unverified candidate for a later task is an explicit Cloud-only
`DOCKER_API_VERSION=1.41`, followed by a saved `docker version` client/server/API
preflight before `docker build`. Docker documents the override and says it
disables API negotiation; minimum supported API and client feature compatibility
must still be checked. A separately pinned compatible Docker client is another
option if the installed client cannot use1.41. Neither option is tested or
admitted here. Keep modern Git/Python source transport, original error exits,
exact RR/compiler/archive pins and full cold1740/1800 + report240 envelope.

Primary reference: [Docker Engine API versioning](https://docs.docker.com/reference/api/engine/)
and [Docker CLI environment variables](https://docs.docker.com/reference/cli/docker/).
No dependency/client/daemon installation or update was done on the VPS.
