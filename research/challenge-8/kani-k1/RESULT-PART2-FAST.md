# RESULT PART2-FAST — eight existing opt-in roots measured on unchanged v6 library (GCB, jobs1)

Reviewed: PRE-BUILD b6d930ff (G1 GO) and d1b51766 (G2 GO). Branch experiment/kani-k1-partfast-20261102, owner k1-network.
Base MACSPLIT 4f4034527d3e; task cfac8c85c6. library tree d4ec476a7a00 = Part1 v6 d6b8caf7fe0e; network.rs blob 1a85a483
(source, roots, covers, F and domains unchanged; no library commit). Kani 9461e07af7ec / nightly-2026-10-12; check-tooling vs
frozen 30f77e859903: pool, lane files, 6 bound files ok for both builds. Profile: gcb-e2-standard-4 → k1-standard4 4 CPU/15.6 GiB,
swap off, controls on, kani_jobs 1, uninit off, 10 min/row, unwind 25. Requests: G1 partfast-g1-measure-u8net4-20261102
(42df2ee0…bb59) → build 5765f47e-81d4-4729-9bc6-76e51998bbcc @b6d930ff; G2 partfast-g2-measure-u64net3-ins1-20261102
(e46f07c2…a97a) → build 38ec4914-5a7e-4690-aa32-d8ec32d889f7 @d1b51766. T0 19:19:05Z; last finish 20:01:52Z.

| Pkt | Root (verify::network::) | Status | VT s | failed/total | unreach. | covers | CBMC row RSS |
|---|---|---|---:|---|---:|---|---:|
| G1 | network_correctness_u8_n8 | SUCCESS | 143.6 | 0/345 | 18 | 3/3 | 0.10 GiB |
| G1 | network_correctness_u8_n14 | SUCCESS | 111.5 | 0/345 | 21 | 3/3 | 0.44 GiB |
| G1 | network_correctness_u8_n15 | SUCCESS | 198.2 | 0/345 | 21 | 3/3 | 0.46 GiB |
| G1 | network_correctness_u8_n16 | SUCCESS | 311.9 | 0/345 | 21 | 3/3 | 0.51 GiB |
| G2 | network_correctness_u64_n10 | SUCCESS | 66.2 | 0/345 | 21 | 3/3 | 0.64 GiB |
| G2 | network_correctness_u64_n11 | SUCCESS | 150.6 | 0/345 | 21 | 3/3 | 0.71 GiB |
| G2 | network_correctness_u64_n12 | SUCCESS | 302.8 | 0/345 | 21 | 3/3 | 0.79 GiB |
| G2 | insertion_permutation_u8_n15 | SUCCESS | 34.9 | 0/110 | 4 | 2/2 | 0.11 GiB |

Row RSS: VmHWM of the single CBMC PID attributed `active=T0:<root>` (k1g.sh peaks; jobs 1). Unreachable counts are Kani data.
Packet peaks (per Build, not per row): G1 time -v max 1758976 KiB, kani-compiler 1.57 GiB, kani-driver 0.72 GiB, sampled
process-sum 1.68 GiB, wall 13:55; G2 time -v max 1757156 KiB, kani-compiler 1.57 GiB, kani-driver 0.44 GiB, sampled sum
1.67 GiB, wall 10:24. dmesg OOM none_seen in both.

Gates: G1 4/4 accepted, G2 4/4 accepted (identities/profile match, SUCCESS, 0 unintended failures, all original covers;
summary gate True per Build). Overall FAST PASS 8/8. N8 keeps its full-width count; N≥9 network rows prove sortedness only
(no whole-route count asserted or credited); insertion u8 N15 proves full-value count of the real suffix only (no sortedness).
Cost: G1 $0.2835 + G2 $0.2295 = own spent $0.5130 of cap $2.00, own reserved $0; project used $82.2930, reserved $0, cap $88.96.

Meaning: bounded GCB SUCCESS ≤600 s for all eight; max VT 311.9 s (u8_n16), 302.8 s (u64_n12). Source unchanged, so this
is a measurement, not a code speed-up. macOS/jobs3/600 s with 400–450 s margin stays OPEN (no conversion factor);
historical organizer partition timings are not a new Mac baseline. Not added to ordinary; no v7, organizer CI or PR here.
Audit-report candidates (all rows kept): the eight above, highest macOS risk first: u8_n16, u64_n12, u8_n15, u64_n11,
u8_n8, u8_n14, u64_n10, insertion_permutation_u8_n15. Receipts: partfast/PREBUILD.md, partfast/g1.result.md.
