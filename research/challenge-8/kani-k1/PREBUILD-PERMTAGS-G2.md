# PERMTAGS — G2 packet

Coordinator GO after review of G1 result `c59410d2421da3fc01e2cade145b4a30c83d0064` authorizes
this exact five-row request without another PRE-BUILD review, after the k1-merge slot is free.
Request `permtags-g2-20261105-01`: diagnostic, agent=k1-merge, controls=true,
gcb-e2-standard-4, kani_jobs=1, harness_timeout_minutes=10, all rows expect SUCCESS:

| Root (`slice::sort::shared::smallsort::verify::permtags::`) | Solver |
| --- | --- |
| network_u8_n17 | default |
| network_u8_n32_kissat | kissat |
| general_u64_n16 | default |
| fallback_cell_u8_n8 | default |
| fallback_cell_u8_n12 | default |

Source correction: `small_sort_network` has `no_merge = len < 18`. N17 still uses no merge;
the requested N32 row exercises merge. The lengths above follow the coordinator's exact GO.
The macro gains optional attributes, preserving every existing invocation and generated body.
Three new roots use that same macro: a separate kissat N32 variant and Cell N8/N12.
Existing roots, the tag checker, comparator bodies, stub, unwind bound and runtime are unchanged.

Slot: watch SCRATCHGEOM `88af6889-68fc-48ae-9c20-9e8cfcff729d` with a separate K1_CACHE,
then end the turn. On completion dispatch as k1-merge, watch the new build and end the turn.
No status polling, local cargo/rustc/Kani/CBMC, credentials or raw-log reads.
G2 maximum reservation: (5 × 10 + 30) × $0.0135 = $1.08; plus G1 actual $0.3105 = $1.3905,
within own cap $2.50. Dispatch must pass the existing project ledger gate (cap $118.96).
Tooling base remains `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; no lane changes.
After completion update RESULT-PERMTAGS.md (<=35 lines) with both builds, explicit proof limits,
time/checks/covers/memory, unproved rows, comparison, ordinary candidates and combined cost.
