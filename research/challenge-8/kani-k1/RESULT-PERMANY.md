# RESULT PERMANY — u64 N8 permutation under an arbitrary read-only comparator: NOT proven (both positive rows TIMEOUT 600 s)

Reviewed PRE-BUILD e305cf2471 (GO). Branch experiment/kani-k1-permany-20261103, owner k1-network, base e0fda080f5 (v6).
Library b2cea32c40 → tree 5e107678 (network.rs append `mod permany;`, new verify/network/permany.rs; old roots unchanged).
Build 39f97957-710a-4059-99f6-d184e33fe031 @e305cf2471, request permany-g1-anyless-u64n8-20261103 (1b0ea6ca…7cc3), kind
diagnostic. Kani 9461e07af7ec; check-tooling vs e0fda080f5 ok. gcb-e2-standard-4 → k1-standard4, 4 CPU / 15.6 GiB, swap off,
controls on, jobs 1, uninit off, 10 min/row, unwind 25, T0 19:45:23Z → 20:19:18Z. Body = PERMSOLVER arbitrary-probe count
with `strict_less` → `any_less` (fresh `kani::any()`, reads no memory); no stubs/summaries/assumptions.

| Root (verify::network::permany::) | Solver | Status | VT | checks | covers | CBMC RSS |
|---|---|---|---|---|---|---|
| permany_u64_n8_default | default | TIMEOUT | 600 (UNKNOWN) | UNKNOWN | UNKNOWN | 0.16 GiB |
| permany_u64_n8_kissat | kissat | **TIMEOUT** | 600 (UNKNOWN) | UNKNOWN | UNKNOWN | 0.09 GiB (+ kissat 0.05) |
| permany_u64_n8_value_loss_control | kissat | FAILED | 6.91 s | 1/314 (18 unreachable) | 7/7 | 0.09 GiB |

Gate: row 2 expected SUCCESS with 7/7 covers → TIMEOUT, **gate not met**. Row 3 met: failed only `permany: full-value count
preserved` @ permany.rs:32 (`permany_count_u64_n8::<true>`), 7/7 covers. Row 1 (measurement): TIMEOUT, a fact.
Build peaks: max RSS 1709676 KiB (kani-compiler 1.57 GiB), wall 21:39.05, OOM none_seen. No compile error, no new warnings;
no repair/retry used (one Build per task).
Solver note (single runs): with the canonical `strict_less` the same body + kissat was SUCCESS 449.5 s (PERMSOLVER a931cf37);
with `any_less` it does not finish in 600 s. No speed-up or bound is derived from the TIMEOUT caps.
Cost: $0.4455 own spent of cap $0.90, own reserved $0; project used $91.9725, reserved $0, cap $98.96.

Conclusion: the permutation of u64 N8 on the real unstable route (network → insertion only, no merge, no
`panic_on_ord_violation`) under any read-only bool comparator is **not proven** by this run: both positive roots time out at
600 s; the value-loss control shows the assert is live and located. Route argument (insertion moves only by gap copies) is by
source, not machine-checked here.
Not proven: this claim itself; a mutating comparator; N ≥ 9 (sort9/13 + insertion, merge from N18); other types; CI fit (> 300 s).
Receipts: permany/PREBUILD.md, permany/body-diff.txt, permany/g1.request.json, permany/g1.result.md.
