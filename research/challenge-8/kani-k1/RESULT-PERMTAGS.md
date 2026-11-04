# PERMTAGS — G1 bounded evidence

Build `d0a22e57-cd81-4f3b-b7ad-b00dba69867d`; source `c113ad679dbcd1d2dec17669e471de82b656470d`.
Library commit `04215fc2058c39298bf81a598e910ffd8c44e734`; Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`.
Request `permtags-g1-20261105-01`, SHA256 `1b2a2144716ef8ef46f73b23070203dd477fedac41eb43d2796707c8f22adfec`.
Evidence: `k1g.sh summary BUILD`, `summary BUILD 0 7`, `peaks BUILD 0 8`, `check-tooling BUILD BASE`, `budget BUILD`.
Tooling/pool/summary identities PASS against BASE `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd` (six bound tooling hashes).
Diagnostic, k1-network, standard4/15.6 GiB, jobs=1, controls=true, default solver, unwind=34, 600 s/root.
Cloud status FAILURE; summary COMPLETE, gate=false because fallback timed out. No compile error; no repair or G2 run.

| Root (`permtags::`) | Status | Time s | Failed/total checks | Unreachable | Covers | CBMC peak KiB |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| tag_types_preserve_source_routes | SUCCESS | 0.064 | 0/14 | 1 | 1/1 | unobserved |
| network_u8_n9 | SUCCESS | 13.415 | 0/539 | 18 | 1/2 | 282260 |
| network_u8_n13 | SUCCESS | 23.773 | 0/539 | 18 | 1/2 | 460872 |
| network_u8_n16 | SUCCESS | 186.136 | 0/539 | 18 | 1/2 | 623880 |
| general_u64_n9 | SUCCESS | 81.928 | 0/423 | 6 | 2/2 | 3305420 |
| fallback_cell_u8_n16 | TIMEOUT | unavailable (600 s limit) | unavailable | unavailable | unavailable | 430384 |
| reject_duplicate_network_u8_n9 | FAILED (expected) | 10.388 | 1/539 | 18 | 1/2 | 284500 |

Memory: directly attributed process VmHWM from 2 s sampling; the short route root was not observed. Whole verify RSS 3305420 KiB, wall 16:28.45; sampled simultaneous RSS peak 3740816 KiB. No OOM seen.
The mutant failed exactly `permtags: every input tag occurs exactly once` at permtags.rs:76; its corruption cover was reached.
Proved: for each SUCCESS permutation row, every bounded arbitrary comparison-answer sequence that returns normally preserves each distinct input tag exactly once (range + N-bit mask, N output slots). Normal-return covers are reachable.
Only panic_on_ord_violation is stubbed/cut. Network/control panic covers are unreachable (1/2); general N9 reaches both normal return and the panic boundary (2/2). No unwinding or comparator-panic claim.
Transfer assumption: on the same type-selected route, SmallSort moves whole elements and branches only on answers/positions/lengths/type properties, not payloads. Fresh answers cover every returning read-only comparator sequence; fixed distinct identity tags represent original positions even for equal payloads.
This source-level transfer to arbitrary values is conditional, not a machine-checked generic refinement theorem. Tags use the original u8/u64/Cell<u8> types; the separate route root checks type bounds, predicates and thresholds. Payload-mutating comparators, sortedness and stability are outside scope; extra uninit/valid-value/permission checks were not enabled.
Task-reported prior direct baseline: u8 through N9, u64 N8 only with kissat. Here the changed formulation reaches u8 N16 and u64 N9 with the default solver; no comparable timing claim or independent revalidation of the prior baseline.
Ordinary candidates (SUCCESS <=60 s): network_u8_n9, network_u8_n13, and the route root. No promotion performed; N16 network and N9 general exceed 60 s.
Unproved: fallback N16 (TIMEOUT); unrun: network N17/N32 and general N16/N17/N32. No proof credit for these roots.
Own spend: one build, $0.3105 (ledger), reservation $0; own cap $2.50. Coordinator restricted authorization to this one build; no further dispatch.
