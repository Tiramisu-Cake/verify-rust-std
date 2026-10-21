# R16 registration design — 2026-10-21

R16 needs a new phase account because its owner, time window, source baseline,
and budget are independent of the closed R15 session. Registration will bind
only `MERGE-CALLER-CURRENT-PROOF-R16-2026-10-21` to the R16 ledger, owner
`merge`, lane `merge`, the authorized UTC window, 3600-second ceiling, and
1200-second maximum timeout. Submit remains pinned-object only, with identical
infra/proof source SHA and a timeout plus queue reserve that fits the absolute
deadline.

The source preflight will compare the selected recipe against baseline
`a89d091c95e50d3aab961654f54668e0f631e3be`, require the exact R16 ledger
addition, and verify every selected runtime path by Git mode/blob identity and
worktree bytes. It will preserve the accepted R14 publication gate and all
prior budget records, including R15, byte-for-byte. The local preflight and
synthetic service tests stay outside the runtime recipe; no historical test
payload is added back.

The publisher change is limited to routing R16 through the existing upload
guard. Its environment/config generation and upload-shell bytes remain pinned
to the accepted R14 behavior, and the existing R15 registration remains
separately authorized. The execute budget is derived from the selected timeout
with a 420-second publication reserve and a 15-second earlier soft deadline.

Validation will use isolated synthetic service tests for valid R16 registration
and fail-closed wrong phase, deadline, budget, owner, source mode, source/blob,
publisher, and execute-budget cases. No compiler, proof, extraction, or Cloud
operation is part of this registration task.
