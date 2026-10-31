# WRAP-N2 final evidence reconciliation

Built G2 head aacbdf2bb78c1a03b99ca9daf2f4c755e3275500, library tree
47a9f618077d539860f6c7f2ce92d5a059e45c57. Closing commit is research-only; no library delta.
The local library tree and exact request hash match the built identities. The source gate32,
rustfmt and bounded read-only delta review preceded G2; no local proof/compiler runs were used.
K-1 check-tooling PASS for the actual pool and all lane/bound files vs30f77e8599.

All5 complete summary rows exactly match manifest names/expectations. First3 are SUCCESS with
zero failed checks; each control has exactly1 failed check and its exact expected literal and
source location. Controls' Kani exit1 is expected; lane gate/measurement/expectations are true.
Covers9/9,7/7,7/7,3/3,1/1: all27 reached. Unreachable checks10/18/8/37/18 are not missing covers.
The corruption control has no failure in the unmutated real-body sorted/full-count checks or
in sortedness after the low-bit flip. No unrelated, unwind or memory failure was reported.

RSS attribution page has exactly4 records, next_offset=done. All4 bind directly via metadata
(one match) to build/head/pin and harness. Three PFC CBMC VmHWM values are261076/267792/864924KiB;
corruption control40632KiB. Always-true control had no sampled process, RSS UNKNOWN. Sampling
is every2s and can miss short processes/growth; values are observed process VmHWM, not a full
per-harness physical-memory theorem. Whole run time-v max2253756KiB; compile+verify wall368.19s.

Own exact UUID ledger:2 builds/$0.2835/live reserve0, comprising G1$0.108 and G2$0.1755.
Final global ledger used$70.1970/reserved$2.2950 (other sessions)/cap$88.96, preserved as read.
No third build, Actions/fullCI or inventory was run. Ordinary native inventory NOT_RUN; only
cfg-off source projection is byte-identical. Old native inventory/proof statuses were not changed.
Bounded result artifacts are K-1 summary/rows/peaks/check-tooling and ledger outputs; no raw/full
log/archive or direct GCS/Cloud Logging read. No download_verified or historical ledger changed.
