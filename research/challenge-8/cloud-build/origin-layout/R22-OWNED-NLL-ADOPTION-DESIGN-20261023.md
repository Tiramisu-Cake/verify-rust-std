# R22 owned-NLL diagnostic adoption

This adds one exact diagnostic-only profile on top of the active R22 compile-fix profile. The source candidate is tool commit `419ff27dcee1a31a9f62e8db69049adb725bdbe2`; the active R22 compile tuple `65f0bb35e4f188cf8ce405a67253127173c5c3a1` and the historical tool578/profile9496 tuple remain separate accepted registrations.

The new `r22_owned_nll_registration` is an exact extension of the current compile profile. Its rollback restores the exporter, schema, refiner core, effective tool, cumulative patch, and chain hash to the byte-exact compile profile before the existing R22 compile-fix validator reverses to profile9496/R20. The compile-fix registration remains unchanged. The public runtime profile stays `experimental-merge-label-storage-r11-v1`; the provider uses a private exact NLL selector only to choose its pins.

The NLL capture is enabled only for actual callback source cases after the exact owned-NLL profile has passed admission. The per-case environment is copied, the NLL flag is removed from inherited environments for every invocation, and `VF_EXPORT_OWNED_NLL_FACTS=1` is inserted only for an admitted owned-NLL profile and an actual callback case. Prefix, unrelated, and non-NLL executions do not receive it. Executor values and exceptions pass through unchanged.

Captured NLL facts are diagnostic. The current candidate does not establish cross-stage mapping; derived origin remains unavailable. No ownership consumer, proof-credit rule, model rule, CFG change, normal-unwind change, runtime change, or source-control change is registered. Compile/refinement success alone is not proof credit. This integration does not run a compiler, exporter, MIR preparation, or verifier locally.

The provider maintains separate exact profile selections for the current compile candidate and NLL candidate, both pinning the reviewed `prove.py` bytes required by the respective profile route. R11 historical pins remain intact. Profile, patch, provider, and source pins are enforced by the R22 client and actual proof dispatcher; malformed, partial, null, wrong-type, off-by-one, and unrelated profile deltas fail closed.
