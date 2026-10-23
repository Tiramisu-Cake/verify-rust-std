# N8 Docker API and actual-start admission design

Defects: N7 inherited apt Docker client selects API1.52 against daemonmax1.41.
Its admission helper also counts all submissions as cold attempts, superseded
by explicit owner update. Apply only to the new N8 account; N7 ledger/history
remain byte-identical. New budget5009s; fixed main/absolute deadlines unchanged.

Fix: export DOCKER_API_VERSION=1.41 and DOCKER_BUILDKIT=0 for the cold executor,
record `docker version` JSON before its first build and fail on an invalid client/
server API receipt. Preserve client config/credentials, exact RR/compiler/archive
pins, source transport, exit statuses and partial evidence. Use classic daemon
Dockerfile output as the start evidence; wrapper entry/context transfer is not
such evidence. Do not fabricate an execution-start marker in the wrapper.

Actual cold-start gate: each prior cold Build is separately classified STARTED,
NOT_STARTED or UNKNOWN. STARTED requires a Build/source/stage-bound Brief file/
index/archive identity+selector. EXPIRED with metadata execution0 may be classified
NOT_STARTED under the explicit owner precedent; other negative classifications
require bound Brief evidence. UNKNOWN is a pending evidence gate, never an
exhaustion claim. Infrastructure failures have no numeric submit limit beyond
budget/window and changed-config/evidence repair rules. At most2 confirmed starts;
warm at most2 attempts and requires a successful, STARTED cold image receipt.

Invariants: actual runtime std/algorithms/CFG/generic signatures, RR332d945f/tree,
compiler nightly2026-08-28, sourcecd371e0, ownership/normal/unwind/cleanup, p0 and
all controls unchanged; no frontend patches, only_spec/shims/stronger premises.
No shared coordinator/IAM/transport/foreign lane changes, no VPS actual tools.
Cold1740/1800, warm1200/1260, report240; warm by canonical registry digest only.

Controls: synthetic Docker API success/error/malformed/missing/null/wrong-type,
NOT_RUN and source-stage/build mismatch; start classifications and arbitrary
pre-start failures must not consume cold slots; unbound starts/UNKNOWN cannot
silently count0 or2; two actual starts/warm attempts enforce limits; original
error/timeout logs preserved. Independent Luna HIGH connected diff review before
submit; pins-only digest/freeze delta returns to reviewer. Proofcredit0.

Primary Docker source audit supports explicit API override bypassing negotiation
minimum (client v29.1), while compatibility remains to be exercised in Cloud.
No new daemon/client binary is installed locally or changed on the shared host.
