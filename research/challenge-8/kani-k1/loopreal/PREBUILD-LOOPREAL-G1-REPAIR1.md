> Historical packet approved at `dc0d792f74c437966aff93c734d43fcedc4dc7a7`.
> Repair is terminal Cloud FAILURE / COMPLETE gate false; see
> [RESULT-LOOPREAL.md](../RESULT-LOOPREAL.md). No further dispatch authorized.

# LOOPREAL G1 — one compile-error repair, awaiting exact-packet GO

Worktree `/root/verify-rust-std-kani-loopreal`, branch `experiment/kani-k1-loopreal-20261105`.
Owner `k1-network`; stage `loopreal-g1-repair1`; request `loopreal-g1-repair1-20261105-01`.
The original one-dispatch GO was consumed. No repair or G2 dispatch is authorized yet.
This packet prepares the task's one permitted compile-error repair for coordinator review.

## Observed G1

Build `69ac5245-e83e-4d87-b8b6-68acd46b0e02`, source `3a1a71036fc48708094c59e3b1c70252ce4fbf9b`:
Cloud FAILURE, bounded summary COMPILE_ERROR, Kani exit 1; all 12 roots NOT_RUN.
Five E0382 diagnostics report moving `is_less: &mut F` through `loop_modifies`, followed by
borrowing it in `insert_tail`, `insertion_sort_shift_left`, and the false cfg-copy.
No invariant base/step, expected negative failure, covers, regression or length-cost evidence
was established. This is a compile error, not unsupported `loop`/`break` or verifier timeout.
The manifest warning about the dummy package edition is recorded separately.

The bounded Cloud record binds the approved source, standard4 pool and 4680-second timeout.
`check-tooling` against `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd` passes all bindings.
Summary text says `build success`, while Cloud status says FAILURE; both are retained, with
COMPILE_ERROR and no proof credit. See `evidence/verification-report.json` and
`../RESULT-LOOPREAL.md` (33 lines). Reproduce bounded consistency checks with `verify_g1.py`.
The old request and static report are frozen in `evidence/g1-request.json` and
`evidence/g1-prebuild-check-report.json`; the original build rows are not reinterpreted using
the repair request. `rows.txt` preserves empty TSV fields, including their trailing tabs.

## Exact repair

The library commit is recorded in `RUN-LEDGER.json` under `proposed_repair.library_commit`.
Only three `loop_modifies` argument expressions change relative to the approved G1 source:

```rust
is_less  // old: moves a non-Copy &mut F when consumed by the attribute expansion
is_less as *mut F  // repair: passes a Copy raw pointer to the same comparator object
```

Two sites are in the real `smallsort.rs`, one is in the false outer cfg-copy in `loopreal.rs`.
No runtime body, signature, existing function contract, loop invariant (including the accepted
ZST disjunct), other modifies target, comparator function item, harness or domain changes.
The raw pointer targets the comparator object F, not the local storage containing `&mut F`.
Rustfmt and source-only checks pass; no local cargo/rustc/Kani/CBMC was invoked. Compilation
of the repair is not established until an authorized Cloud build tests it.

The new request differs from G1 only in request_id and purpose; all 12 exact root names,
expectations/named negative check, backing 8/32/128, five ordinary regressions, controls=true,
standard4, jobs1 and 4 minutes/root remain unchanged. The same 34 positive covers are required.
Paired consumer credit still requires the matching PFC success for each fixed backing/T/F.
ZST N16 is the no-extension boundary; N32 can enter the actual inner loop. Historical ZST
Actions v7 timings remain coordinator-reported approximate comparisons, not GCB baselines.
Body-preservation, historical baseline provenance, domains and limitations are otherwise as
in the original prebuild document and `IMPACT-LOOPREAL.md` / `ZST-REACHABILITY.md`.

## Budget and dispatch boundary

G1 actual cost **$0.1080**, reserve **$0**; remaining own cap **$1.8920**.
This repair reserves at most (12 × 4 + 30) × $0.0135 = **$1.0530**;
own spent + repair reserve = **$1.1610 <= $2.00**. No further repair is planned for G1.
Project snapshot after G1: 237 builds, used $100.4910, other reserves $0, cap $118.96;
including this proposed repair reserve gives $101.5440. Recheck at authorized dispatch.
The original window/T0 remains 2026-11-05T08:19:58.044000+00:00, main deadline
12:19:58.044000+00:00 and closeout deadline 12:49:58.044000+00:00; no extension.

New request SHA256: `92b07d04e7bf08dcfaba93c0b92601236e3ce9cf987b00b34e181797ffe0ff22`.
`request.json` is byte-identical to the lane's current `RUN-REQUEST.json`.
`check_packet.py` proves the source delta is exactly the three raw-pointer target expressions,
compares all request settings with the original source, and checks spent + reserve <= cap.
The check is static only; it does not establish that the compiler or proof obligations pass.
Tooling, Kani pin, workflows, runtime bodies and all evidence policies are unchanged.

After a new exact-packet GO, submit this repair once via `k1g.sh`, record its own build/source/
request identity and repair count, then `k1g.sh watch BUILD` and end the turn. No status loop.
On completion analyze bounded outputs separately from G1; G2 still requires coordinator GO.
