# RESULT-DOMSIX

Updated the public English registry, TSV, README and checker for Part 1 v6; recalculated source links.
Source pin: d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097; library d4ec476a7a001363e58f19948c188a9c2078e370.
Inventory head 71d18696613bdd6b00648a0d7b44d1cd3c6da940 has the same library tree; documentation HEAD retains v5 library.
Imported the two requested ordinary inventory files: native 202 names; cfg-on 384 is statically derived, not native v6.
PFC: 38 entries (36 ordinary + 2 controls), insert_tail 5; 18 lexical sites and 22 domain records preserved.
Organizer CI status and link updated from the supplied task; no builds or CI requests were made.

`python3 -B research/challenge-8/kani-k1/domains/check_domains.py`:
```text
OK: source pin d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097 library d4ec476a7a; documentation HEAD library cbe69760c8 (distinct); 38 PFC entries / 18 lexical sites; 36 ordinary + 2 controls + 0 cfg(any()); 72 retired absent; native G1 202; static cfg-on v6 384; 22 domains; 156 source links (45 harness-name links)
Source forecast: 11 files reconciled to native ordinary and statically derived cfg-on sets.
Proof status: organizer CI run https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/41404150041; cfg-on v6 membership is statically derived, not a native inventory. This script does not verify proofs.
```
Targeted negative checks rejected an inventory tree mismatch, altered cfg provenance, and a same-count cfg-on name substitution.
Open questions: native cfg-on v6 inventory is unavailable; the existing Kani #5104 model-trust question remains open.
