# PERMTAGS — G1/G2 bounded evidence

G1 build `d0a22e57-cd81-4f3b-b7ad-b00dba69867d`; source `c113ad679dbcd1d2dec17669e471de82b656470d`.
G2 build `8c10dc52-3e39-4b07-800f-0c1d3aad4888`; source `93591c28ccfc3736b597cbb827c7992f8d3a509c`.
Both use Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`; requests `permtags-g1-20261105-01` / `permtags-g2-20261105-01`.
Request SHA256 G1 `1b2a2144716ef8ef46f73b23070203dd477fedac41eb43d2796707c8f22adfec`; G2 `1e6e1389c6bbd6110ac2194932af15a151a8736282d6396d2513679714a1a4ec`.
Evidence: k1g.sh summary, bounded peaks (G1 0 8 / G2 0 8), check-tooling and budget. Both tooling/pool/summary identities PASS against BASE `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`, six bound hashes each.
Diagnostic, standard4/15.6 GiB, jobs=1, controls=true, unwind=34, 600 s/root; owners G1 k1-network / G2 k1-merge. Default solver except the separate N32 kissat root; existing roots unchanged in G2.
Both Cloud builds FAILURE; both summaries COMPLETE, gate=false due to one TIMEOUT each. Compilation succeeded; no compile repair or further build.

| Run | Root (`permtags::`) | Status | Time s | Failed/total checks | Unreachable | Covers | CBMC peak KiB |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| G1 | tag_types_preserve_source_routes | SUCCESS | 0.064 | 0/14 | 1 | 1/1 | unobserved |
| G1 | network_u8_n9 | SUCCESS | 13.415 | 0/539 | 18 | 1/2 | 282260 |
| G1 | network_u8_n13 | SUCCESS | 23.773 | 0/539 | 18 | 1/2 | 460872 |
| G1 | network_u8_n16 | SUCCESS | 186.136 | 0/539 | 18 | 1/2 | 623880 |
| G1 | general_u64_n9 | SUCCESS | 81.928 | 0/423 | 6 | 2/2 | 3305420 |
| G1 | fallback_cell_u8_n16 | TIMEOUT | unavailable (600 s limit) | unavailable | unavailable | unavailable | 430384 |
| G1 | reject_duplicate_network_u8_n9 | FAILED (expected) | 10.388 | 1/539 | 18 | 1/2 | 284500 |
| G2 | network_u8_n17 | SUCCESS | 334.623 | 0/539 | 18 | 1/2 | 653568 |
| G2 | network_u8_n32_kissat | TIMEOUT | unavailable (600 s limit) | unavailable | unavailable | unavailable | 1193880 |
| G2 | general_u64_n16 | SUCCESS | 177.458 | 0/423 | 5 | 2/2 | 6065432 |
| G2 | fallback_cell_u8_n8 | SUCCESS | 4.936 | 0/332 | 4 | 1/1 | 184236 |
| G2 | fallback_cell_u8_n12 | SUCCESS | 74.507 | 0/332 | 4 | 1/1 | 266928 |

Memory: directly attributed process VmHWM from 2 s sampling; the short route root was unobserved. N32 kissat subprocess peak 232080 KiB (separate from CBMC). Whole verify max RSS/wall: G1 3305420 KiB/16:28.45, G2 6065432 KiB/21:05.33; simultaneous sampled RSS peaks 3740816/6324976 KiB. No OOM seen.
The G1 mutant failed exactly `permtags: every input tag occurs exactly once` at its built permtags.rs:76; corruption cover reached.
Proved: for each SUCCESS permutation row, every bounded arbitrary comparison-answer sequence that returns normally preserves each distinct input tag exactly once (range + N-bit mask, N output slots). Normal-return covers are reachable.
Only panic_on_ord_violation is stubbed/cut. Successful network/control panic covers are unreachable (1/2); general N9/N16 reach normal return and panic boundary (2/2); Cell N8/N12 return covers are 1/1. No unwinding/comparator-panic claim.
Transfer assumption: on the same type-selected route, SmallSort moves whole elements and branches only on answers/positions/lengths/type properties, not payloads. Fresh answers cover every returning read-only comparator sequence; fixed distinct identity tags track original positions even for equal payloads.
Transfer to arbitrary values is conditional, not a machine-checked generic refinement theorem. Tags retain u8/u64/Cell<u8>; the route root checks type bounds, predicates and thresholds. Payload mutation, sortedness and stability are outside scope; extra uninit/valid-value/permission checks were not enabled.
Task-reported direct baseline: u8 through N9, u64 N8 only with kissat. This formulation proves selected u8 lengths through N17 and u64 N16 with the default solver, plus Cell N8/N12; no comparable timing claim or independent revalidation of the baseline.
Ordinary candidates (SUCCESS <=60 s): network_u8_n9, network_u8_n13, fallback_cell_u8_n8, and the route root. No promotion performed; all other successful permutation rows exceed 60 s.
Unproved: Cell N16 and network N32 kissat (TIMEOUT); unrun: network N32 default and general N17/N32. Network N17 has no merge (`no_merge = len < 18`); network permutation with merge remains unproved. No proof credit for timeout/unrun rows.
Own spend: G1 $0.3105 + G2 $0.3780 = $0.6885 (two-build ledger), reservation $0, cap $2.50. Both authorized builds finished; no further dispatch.
