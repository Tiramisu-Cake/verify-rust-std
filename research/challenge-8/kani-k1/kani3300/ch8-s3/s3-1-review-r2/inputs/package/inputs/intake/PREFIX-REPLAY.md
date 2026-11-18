# Authentic reader replay and minimal regression recipe

Run `python3 replay.py` in this directory. It reuses the earlier intake-helper pattern, reads pinned Git blobs, freezes their import closure in a temporary directory, verifies the sole compact payload and its36 structured members, and invokes only offline readers. It never invokes runner main, compilation, native Kani/CBMC, setup, CI or campaign execution. See254 recorded checks in VALIDATION.json.

The exact original member bytes materialized into a temporary local receipt tree reproduce `root_outcome` rejection **worker protected/provenance evidence rejected: recorded worker binary drift: before**. Request-derived provenance and the E0/pre/post controller pair pass independently. All authentic member bytes remain unchanged after replay.

| Bounded case | Frozen protected reader result |
|---|---|
| Authentic E0 + worker receipt + supervision | rejects BEFORE cross-observer comparison |
| In-memory worker copy with only driver/compiler path strings set equal to E0 in both stages | protected reader returns; no recovery, no errors ignored |
| Same diagnostic copy with one valid-format driver BEFORE hash altered | rejects BEFORE cross-observer comparison |
| Same diagnostic copy with BEFORE field removed | rejects worker binary before incomplete/malformed |

The second case isolates a necessary condition; it neither verifies same-file identity nor applies a repair. The third simulates a recorded-hash mismatch, not a real filesystem mutation. No changed record is sealed or admitted.

The exact collector using the materialized structured tree and upload-only group-evidence.json.gz produces identical **GLOBAL_STOPPED_PENDING_REVIEW**, original stop reason, first worker COMPLETE/MATCH/exit1 record, INTERRUPTED/UNKNOWN canonical first row, and eight later NOT_RUN rows. Completed prefix is empty and no completion seals exist. Consequently sealed-root validation has no root to admit; a successful collector return does not mean the protected worker passed. selected_missing_groups=[] means all selected group receipts/placeholders exist, not that roots ran. Deferred8 remain NOT_SELECTED.

This recipe is ready for original13's separately authorized regression work after root reviews the committed intake. Existing frozen guards remain unchanged. No rerun or fix is authorized by this replay.
