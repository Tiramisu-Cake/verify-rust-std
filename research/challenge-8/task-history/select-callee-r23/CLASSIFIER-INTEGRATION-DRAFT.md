# Inactive target classifier integration

The optional seven-target path is prepared for review and future Cloud qualification, without any accepted target map. Without a map, the previous incomplete/unpinned behavior stays. With a map, the helper checks exact diagnostics and declared observation provenance, while existing stage/source/argv and pre/post snapshots stay required. The audit requires the whole matrix and map/tool/helper identities. No source/ghost/MIR pin change or proof credit is established.

Open integration issue for review: verbose verifier logs contain elapsed timestamps, so a later run may have a different full log SHA even when the sole exact diagnostic is identical. Prior-observation artifact SHA/provenance and current-stage log SHA must remain distinct; copying prior provenance onto a current log would not establish current authenticity. Keep this path unqualified until that relation is correctly handled and reviewed.

The target helper is included in the pinned infra recipe because the updated entry loads its hash even when no map is supplied. Targets remain absent; S3 observations are provisional because positive still exits1 on dead-code reports.
