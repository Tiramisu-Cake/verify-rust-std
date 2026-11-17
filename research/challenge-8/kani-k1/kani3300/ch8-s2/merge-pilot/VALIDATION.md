# Compact offline validation receipt

Result: **PASS_DIAGNOSTIC_ONLY**, proof credit NONE, Kani/compiler/CI NOT_RUN,
S3 qualification NONE. Machine-readable result: `validation.json`.

Reproduce from `/root/verify-rust-std-kani3300-g0`:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/challenge-8/kani-k1/kani3300/ch8-s2/merge-pilot/test_pilot.py --source-repo /root/verify-rust-std-ch8-s1-08-w13
```

Checked exact99e tree/blob/SHA256 and30 source-site anchors against read-only
Git objects. Enumerated598 sorted-half inputs at lengths2..8 over {0,1,255},
1869 paired transitions with checks at init, after up, after down and exit;
233 active pair heads had a logically exhausted half. Odd exits selected left
78 times and right150 times. Added372 deterministic fixtures over all lengths
2..32 (including all equal, separated/reversed halves and8 seeded random byte
fixtures per length). Every trace checks all256 counts and rank strengthening.
Checked34 same-allocation offset pairs numerically, plus overlap/adjacency
controls; no pointer-provenance or same-allocation Kani theorem is claimed.

| negative/definedness control | distinguishing check, with weak acceptance where relevant |
| --- | --- |
| §6 n4, [1,9,2,10], output9/2, probe0 | weak source cuts/band order/unguarded E/probe0 accept; guarded E, full counts, consumed counts, barriers and rank-output reject |
| unguarded k0 endpoint read | explicit bounds failure; guarded k0 predicate accesses no endpoint |
| exhausted reverse-left sentinel -1 | explicit bounds failure (Python negative-index wrap disabled) |
| lost9/replaced8, output still sorted | full counts/rank-output reject; order and probe0 accept |
| duplicate1/lose2, output still sorted | full counts reject; order accepts |
| swapped first two outputs | order rejects; full multiset accepts |
| write outside destination | frame/write-log rejects; sortedness/counts accept |
| source clobber | immutable source/frame check rejects |
| odd skipped write | initialization rejects before evaluating undefined output order/count loads |
| odd skipped counter | actual end equality/ord-panic check rejects |
| odd wrong source | order and full counts reject |
| down tie incorrectly selects left on [7,7] | geometry/no-double-consumption and ord-panic check reject; byte order/full counts accept |
| poison in unwritten slots (positive) | all staged predicates pass without reading poison as a byte |

These controls mutate shadow states/transitions or intentionally evaluate bad
formula reads. They do not mutate or qualify actual Rust/Kani source. No
exhaustive arbitrary-state induction, generic comparator/domain theorem,
MIR/extraction validation or solver/cost result is asserted. Open K0–K8 and
integration API/geometry are in `INVARIANT.md` / `HANDOFF.md`.

Only this package is written/staged. No subagents, local compiler/rustfmt,
full runner, solver sweep, CI, push, reservation or ledger update. Offline
dispatch cost0. No semantic blocker found; remaining formal obligations are
future integration work, not STOP conditions for the authorized offline stage.
