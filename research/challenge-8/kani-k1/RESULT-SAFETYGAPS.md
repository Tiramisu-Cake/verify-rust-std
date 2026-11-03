# RESULT SAFETYGAPS — six existing opt-in roots (dispatch bytes85/ZST, mutating Cell insertion N6..20) on v6 (GCB, jobs1)

Reviewed: PRE-BUILD 69769295 (GO for G1, and G2 from the same source); G2 commit 89e58019 (only receipt + RUN-REQUEST).
Branch experiment/kani-k1-safetygaps-20261103, owner k1-network; task 972d8c0b. library tree d4ec476a (v6), network.rs blob
1a85a483; source, harnesses, covers, domains unchanged. Kani 9461e07a / nightly-2026-10-12; check-tooling vs e8e238db9d87:
pool, lane files, 6 bound files ok for both. Profile k1-standard4 4 CPU/15.6 GiB, swap off, controls on, jobs 1, uninit off,
10 min/row, unwind 65 (dispatch) / 35 (Cell). G1 safetygaps-g1-measure-dispatch-bytes85-zst-20261103 (d0bd35e5…436d) →
build 46745c1e-b4a5-4dfd-9c62-915328563384 @69769295; G2 safetygaps-g2-measure-cell-insertion-n6-20-20261103
(7caeb8f1…3dc2) → build 27cc7d3f-a1b2-424c-a2f2-31e018723be9 @89e58019. T0 13:20:44Z; last finish 14:19:44Z.

| Pkt | Root (verify::network::) | Status | VT s | failed/total | unreach. | covers | CBMC row RSS |
|---|---|---|---:|---|---:|---|---:|
| G1 | dispatch_safety_stable_unstable_bytes85_n31 | SUCCESS | 184.0 | 0/370 | 9 | 3/3 | 2.68 GiB |
| G1 | dispatch_safety_stable_zst_n0_1_2_7_8_15_16_17_31_32 | FAILED | 345.9 | 4/391 | 5 | 11/11 | 6.81 GiB |
| G1 | dispatch_safety_unstable_zst_n8_9_12_13_17 | TIMEOUT | >600 | — | — | — | ≥7.97 GiB |
| G2 | mutating_insertion_safety_cell_n6_to10 | SUCCESS | 142.6 | 0/218 | 4 | 17/17 | 3.33 GiB |
| G2 | mutating_insertion_safety_cell_n11_to15 | FAILED (no data) | UNKNOWN | — | — | — | 8.47 GiB |
| G2 | mutating_insertion_safety_cell_n16_to20 | TIMEOUT | >600 | — | — | — | ≥12.29 GiB |

stable ZST failed checks (bounded summary): dereference failure — pointer NULL / pointer invalid / outside object bounds /
invalid integer address, all `@ no location`; unclassified (no property id/function/trace in bounded data). n11_to15: FAILED
after ~367 s CBMC with no check/cover data and no failed property listed; unclassified. Both reported to coordinator, no retry.
Packet peaks (per Build): G1 time -v 7.97 GiB (cbmc), kani-compiler 1.58, driver 0.92, sampled sum 8.65 GiB, wall 19:59;
G2 time -v 12.30 GiB (cbmc n16_to20), kani-compiler 1.63, driver 0.32, sampled sum 12.53 GiB, wall 19:43. OOM none_seen.
Cost: G1 $0.3645 + G2 $0.3645 = own spent $0.7290 of cap $1.65, own reserved $0; project used $87.8955, reserved $0, cap $93.96.
Gates: G1 1/3 accepted, G2 1/3 accepted (identities/profile match, SUCCESS, 0 failures, all covers incl. normal return of each
route/length). Accepted 2/6; FAILED rows kept as failures, TIMEOUT rows OPEN.

Domains added to ordinary 202 (accepted rows only credit):
- bytes85_n31: [u8;85] × N31 × stable general_with_scratch (scratch 48) and unstable small_sort_general — gap between
  ordinary bytes85 N17 and N32. ACCEPTED.
- stable ZST: () × N{0,1,2,7,8,15,16,17,31,32} × stable general_with_scratch — no ZST in ordinary. NOT credited (FAILED).
- unstable ZST: () × N{8,9,12,13,17} × unstable small_sort_network. NOT credited (TIMEOUT).
- Cell N6..10 / N11..15 / N16..20: Cell<TaggedKey> × each N × every offset 1..=N × direct insertion with mutating comparator;
  ordinary has N1..5 and N20 all offsets. N6..10 ACCEPTED; N11..19 remain OPEN.
v7 shortlist (≤300 s GCB, accepted): dispatch_safety_stable_unstable_bytes85_n31 (184.0 s), mutating_insertion_safety_cell_n6_to10
(142.6 s); GCB result only, macOS not established.
Cell split plan (not run; existing opt-in roots, no source change): N11..15 → n11_to12, n13, n14, n15_offsets{1_to4,5_to8,
9_to12,13_to15}; N16..19 → offsets{1_to4,5_to8,9_to12} each + n16 13_to16, n17 13_to15+16_to17, n18 13_to16+17_to18, n19
13_to16+17_to19. n11_to15 FAILED must first be classified (bounded evidence, coordinator) before any split dispatch. Receipts: safetygaps/{PREBUILD,g1.result,g2.result}.md.

## Addendum — bounded classification of the two FAILED rows (k1g.sh log-grep/log-lines, coordinator-authorized; no rerun)
(1) stable ZST, G1 46745c1e kani.log 2728-2742: "4 of 391 failed (5 unreachable)", "11 of 11 cover properties satisfied", then
four `Failed Checks:` lines (pointer NULL / pointer invalid / pointer outside object bounds / invalid integer address),
VERIFICATION FAILED, 345.92 s. The lane runs `--output-format=terse` (kani_k1.py 352), which prints only descriptions: no
property id, function, file or line exists anywhere in the log (grep for Location/File/Function/property ids: no match). The
summary's "@ no location" is kani_k1.py's placeholder for that (1574), not a CBMC fact. The four checks are the standard pointer-
check set of one dereference class, so a core-vs-harness/Kani-model attribution is NOT determinable from existing evidence; it
needs a non-terse run (new request/GO). Still neither real UB nor artifact; stays FAILED.
(2) Cell N11..15, G2 27cc7d3f kani.log 2733-2736: "CBMC failed with status 6", VERIFICATION FAILED, no VERIFICATION RESULT block,
no Failed Checks, no time — CBMC terminated abnormally before reporting, so this is NOT a counterexample. Not TIMEOUT (CBMC
span 814–1181 s ≈ 367 s < 600 s) and not a kernel OOM kill (dmesg none_seen; peak 8.47 GiB of 15.6 GiB). Status 6 matches the
CBMC exit-code class for internal error/exception (which also covers a caught bad_alloc "Out of memory"); a SIGABRT reading
cannot be excluded because terse output carries no CBMC message. Root cause UNKNOWN; row = RUNNER/CBMC_ABNORMAL_EXIT, OPEN.
Split plan unchanged; for N11..15 the smaller existing roots also test whether the abnormal exit is size-related.
