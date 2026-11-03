# RESULT CELLSPLIT — mutating Cell insertion N11..19 via 26 existing split roots on v6 (GCB, jobs1)
Reviewed PRE-BUILD 24c93e8d/d3a639c2/2f1ef6a9 (G1/G2/G3 GO); branch experiment/kani-k1-cellsplit-20261103, owner k1-network, task ea894835. library tree d4ec476a (v6),
network.rs blob 1a85a483, source/covers unchanged; Kani 9461e07a/nightly-2026-10-12; check-tooling vs e8e238db9d87 ok ×3. k1-standard4 4 CPU/15.6 GiB, swap off, controls, jobs 1,
uninit off, 10 min/row, unwind 35. Builds G1 37bbcae6-9d4c-48d8-b386-815db4c50530 (req 6abdc9be…), G2 f77274f7-4475-4748-94d3-ec9096a03d98 (4c1e9ce6…), G3 23080711-3c34-4937-9290-28558881de56 (61b78853…); T0 16:11:14Z, last finish 17:15:22Z.
| Pkt | Root (network::mutating_insertion_safety_cell_) | Status | VT s | failed/total | unreach. | covers | CBMC row RSS |
|---|---|---|---:|---|---:|---|---:|
| G1 | n11_to12 | SUCCESS | 154.6 | 0/191 | 4 | 8/8 | 3.49 GiB |
| G1 | n13 | SUCCESS | 100.4 | 0/182 | 4 | 5/5 | 2.51 GiB |
| G1 | n14 | SUCCESS | 133.8 | 0/182 | 4 | 5/5 | 3.09 GiB |
| G1 | n15_offsets1_to4 | SUCCESS | 77.3 | 0/177 | 4 | 6/6 | 1.47 GiB |
| G1 | n15_offsets5_to8 | SUCCESS | 47.5 | 0/177 | 4 | 6/6 | 1.28 GiB |
| G1 | n15_offsets9_to12 | SUCCESS | 34.7 | 0/177 | 4 | 6/6 | 0.79 GiB |
| G1 | n15_offsets13_to15 | SUCCESS | 7.3 | 0/177 | 4 | 5/5 | 0.19 GiB |
| G2 | n16_offsets1_to4 | SUCCESS | 78.0 | 0/177 | 4 | 6/6 | 1.63 GiB |
| G2 | n16_offsets5_to8 | SUCCESS | 59.3 | 0/177 | 4 | 6/6 | 1.45 GiB |
| G2 | n16_offsets9_to12 | SUCCESS | 41.8 | 0/177 | 4 | 6/6 | 0.95 GiB |
| G2 | n16_offsets13_to16 | SUCCESS | 14.4 | 0/177 | 4 | 6/6 | 0.35 GiB |
| G2 | n17_offsets1_to4 | SUCCESS | 97.7 | 0/177 | 4 | 6/6 | 1.81 GiB |
| G2 | n17_offsets5_to8 | SUCCESS | 76.4 | 0/177 | 4 | 6/6 | 1.62 GiB |
| G2 | n17_offsets9_to12 | SUCCESS | 70.0 | 0/177 | 4 | 6/6 | 1.26 GiB |
| G2 | n17_offsets13_to15 | SUCCESS | 17.4 | 0/177 | 4 | 5/5 | 0.48 GiB |
| G2 | n17_offsets16_to17 | SUCCESS | 3.6 | 0/177 | 4 | 4/4 | 0.08 GiB |
| G3 | n18_offsets1_to4 | SUCCESS | 87.7 | 0/177 | 4 | 6/6 | 2.29 GiB |
| G3 | n18_offsets5_to8 | SUCCESS | 91.5 | 0/177 | 4 | 6/6 | 1.83 GiB |
| G3 | n18_offsets9_to12 | SUCCESS | 57.8 | 0/177 | 4 | 6/6 | 1.45 GiB |
| G3 | n18_offsets13_to16 | SUCCESS | 48.4 | 0/177 | 4 | 6/6 | 0.78 GiB |
| G3 | n18_offsets17_to18 | SUCCESS | 3.3 | 0/177 | 4 | 4/4 | 0.11 GiB |
| G3 | n19_offsets1_to4 | SUCCESS | 111.1 | 0/177 | 4 | 6/6 | 2.49 GiB |
| G3 | n19_offsets5_to8 | SUCCESS | 99.8 | 0/177 | 4 | 6/6 | 2.30 GiB |
| G3 | n19_offsets9_to12 | SUCCESS | 70.4 | 0/177 | 4 | 6/6 | 1.67 GiB |
| G3 | n19_offsets13_to16 | SUCCESS | 37.2 | 0/177 | 4 | 6/6 | 1.13 GiB |
| G3 | n19_offsets17_to19 | SUCCESS | 8.4 | 0/177 | 4 | 5/5 | 0.23 GiB |
## Peaks, cost, gates, coverage
Row RSS: VmHWM of the one CBMC PID attributed direct `active=T0:<root>` (k1g.sh peaks, jobs 1). Packet peaks per Build (time -v / compiler / driver / sampled sum / wall):
G1 3.49 GiB (cbmc n11_to12) / 1.63 / 0.38 / 3.79 GiB / 10:29; G2 1.81 / 1.61 / 0.68 / 2.30 / 8:53; G3 2.49 / 1.61 / 0.81 / 3.01 / 11:25. OOM none_seen ×3; no status 6, no counterexample.
Cost G1 $0.2430 + G2 $0.2295 + G3 $0.2430 = own spent $0.7155 of cap $3.60, own reserved $0; project used $89.3130 (+$1.7550 reserved by another owner), cap $93.96.
Gates G1 7/7, G2 9/9, G3 10/10 accepted: identities/profile, SUCCESS, 0 failures, all source covers incl. "mutating comparator changes both keys"; 4 unreachable/row is Kani data.
Coverage: Cell<TaggedKey> × mutating_key_order × direct insertion_sort_shift_left, every (N, offset) with N∈11..19, offset 1..=N PROVED (groups partition 1..=N per PRE-BUILD); OPEN: none.
With ordinary N1..5/N20 and SAFETYGAPS n6_to10, N1..20 all offsets covered; wide n11_to15 (status 6) and n16_to20 (TIMEOUT) remain OPEN as rows only. Source unchanged: measurement, not speed-up.
v7 candidates (≤300 s GCB): all 26 rows (sum VT 1629.8 s, max 154.6 s n11_to12); GCB only, macOS not established. Receipts: cellsplit/{PREBUILD,g1.result,g2.result,g3.result}.md.
