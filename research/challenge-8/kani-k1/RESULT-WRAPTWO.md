# WRAP-N2 — PASS, bounded concrete forwarding contracts (not integrated PASS)

Worktree /root/verify-rust-std-kani-wraptwo, branch experiment/kani-k1-wraptwo-20261031.
G2 built head aacbdf2bb78c1a03b99ca9daf2f4c755e3275500; source811c78777d;
library47a9f618077d539860f6c7f2ce92d5a059e45c57, unchanged by research-only closing commit.
Kani9461e07af7ec929f050aa4192f29363c9be07779/nightly-2026-10-12, flags/cap88.96 unchanged.
G1 UUID7d5d04ec-f1da-493d-8be2-7ce36de3624b, request wraptwo-g1-20261031: COMPILE_ERROR,
all5 NOT_RUN; E0502 built wrap.rs:84/103/118 at old(count) with &mut inputs; cost$0.108.
G2 UUID670466ce-2615-4b5c-9373-1fcb60b06aef, request wraptwo-g2-retry-20261031: COMPLETE,
gate/expectations/measurement TRUE; Kani exit1 from exactly2 expected negative assertions.
Head/pin/request hash match; check-tooling vs30f77e8599 PASS for both builds.

Real dispatch (confirmed in source, no leaf/panic/verified stubs): Stable Cell<u8> !Freeze
blanket fallback insertion; Unstable u8 → Freeze/Copy network (N2 insertion, no sort9/sort13);
Freeze local repr(transparent) NonCopyU8 !Copy/!Drop → default general, singleton copies/merge.
Three checked concrete forwarding contracts, not literal trait-method annotations.

Requires: initialized/readable/writable raw span exactly2, canonical typed fn value; Stable
scratch disjoint from input (empty/other allocation/nonoverlapping ranges). Body constructs
&mut pair and forwards supplied F to real qualified entry. Ensures pure sortedness by >>1
and scalar old(pair_count(v,probe)) == pair_count(v,probe); modifies exactly the input pair.
Full models u8/Cell.get()/inner u8; independent unconstrained u8 probe shared by value pre/post.
No byte oracle/shared statics/F calls in specs. Raw-pair G2 fixes the measured G1 capture issue.
Backing4 active[1..3], symbolic outside sentinels; Stable scratch backing2 exposed len0..2,
slot0 initialized/checked unchanged, uninit slot1 never read. All harnesses use unwind16.

| Harness (wrap::) | Status | VT s | cbmc KiB¹ | Fail/total | Covers | Unreachable checks |
|---|---|---|---|---|---|---|
| stable_cell_n2 | SUCCESS | 39.805294 | 261076 | 0/304 | 9/9 | 10 |
| unstable_byte_n2 | SUCCESS | 31.517094 | 267792 | 0/497 | 7/7 | 18 |
| freeze_noncopy_n2 | SUCCESS | 178.131130 | 864924 | 0/473 | 7/7 | 8 |
| rejects_always_true | FAILED = expected | 0.501905 | UNKNOWN | 1/576 | 3/3 | 37 |
| rejects_payload_corruption | FAILED = expected | 0.661972 | 40632 | 1/341 | 1/1 | 18 |

¹ observed CBMC VmHWM, sampled2s, direct metadata binding; short processes/growth may be missed.
Only failed assertions: `wrap canonical comparator required` at wrap.rs:61 and
`wrap full-value checker rejects payload corruption` at wrap.rs:266 (literal kani::assert).
Always-true control reaches each wrapper guard. Separate plain real-body corruption control
passes sorted/full-count before mutation and key-order after XOR1; only final full-value fails.
All27 covers reached; unreachable checks above are not unreachable covers. No unwind/UB failure.
Whole compile+verify wall368.19s, max RSS2253756KiB (compiler); largest CBMC864924KiB.

Own2/2 builds: G1$0.108 + G2$0.1755 = $0.2835≤$2, live reserve0; no third build.
Final project ledger used$70.1970/reserved$2.2950 other sessions/cap$88.96; no ledger changed.
Native ordinary inventory NOT_RUN; cfg-off library projection byte-identical to base6f3a262961
is a source argument only. Static32/request/rustfmt checks passed before G2; no later code delta.
N7/N8 remain NOT_RUN: longer insertion, general half preparation/merge need new proofs/resources.
Three selected paths do not cover all implementations/thresholds; F03 ordinary migration OPEN.
No general FnMut, stable-tie-order, padding, init detector or unwind theorem; integrated tree
requires fresh exact-tree validation. This result closes the requested N2 interface/PFC gate.
Artifacts: wraptwo/g1.* and g2.* bounded evidence, FINAL-CHECKS.md, exact requests/reviews.
WRAP-N2 ЗАВЕРШЁН
