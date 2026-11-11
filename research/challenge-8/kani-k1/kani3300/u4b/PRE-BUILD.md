# KANI3300 U4B — PRE-BUILD packet

PREPARED; Cloud NOT_RUN, proof credit NONE. Runtime Codex, one diagnostic stage.
Task: `research/challenge-8/kani-k1/TASK-KANI3300-U4B.md`.
Worktree `/root/verify-rust-std-kani3300-u4`; branch `experiment/kani-k1-kani3300u4-20261111`.
Stage `kani3300-u4b`, owner `k1-merge`; request `kani3300-u4b-uninit-20261111-01`.
Baseline `582e9e0f5a436cb40ba80f3053de112d7232104b` includes coordinator U4B task.

Exactly two harnesses appended to `library/core/src/slice/sort/shared/smallsort/verify/uninit_probe.rs`;
all prior nine harnesses byte-identical, all other library files unchanged. Both run the real sort with
N4, `[MaybeUninit::<u8>::uninit(); 20]`, `strict_less`, unwind17 and the existing panic stub.
No algorithm, model, tool, pin, trusted premise or control weakening; U2/U6/U9 remain in source.

| Root (all in `slice::sort::shared::smallsort::verify::uninit_probe::`) | Expected | Manual accounting |
|---|---|---|
| U9a `small_sort_general_scratch_written_slot_u8_n4` | SUCCESS | 0 failures; normal return and both scratch[3] byte covers (3) |
| U9b `small_sort_general_scratch_unwritten_slot_only_u8_n4` | FAILED; `Reading from an uninitialized` | Record every failure type/location and covers (4); only post-sort read is scratch[4] |
| U8 `small_sort_general_with_scratch_u8_n4` | SUCCESS | Sortedness/count assertions and normal-return cover (1) |
| U1 `pincheck_calibration_uninit_read_u8` | FAILED; `Reading from an uninitialized` | Calibration failure count/type/location and covers (3) |

U9a observes only scratch[3]; U9b observes only scratch[4]. Do not require exactly one U9b failure:
the purpose is to count distinct instrumentation failures. Substring gate is insufficient for diagnosis.
If U9a SUCCESS and U9b reproduces both U9 uninit types, report split-harness evidence supporting both
original failures from the unwritten-slot read; distinguish this from independent MIR/call-site proof.
Otherwise describe actual differences; no invented causality or SUCCESS from missing evidence.

Root request equals snapshot. Request SHA256: `53a2f3ac1453787fd74f190d838352f9a819676619c66f456c6dad8c197bd1ff`.
Production patch remains `kani3300/u4/kani-uninit.patch`, SHA256
`46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4`.
Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`, nightly-2026-10-23;
protected lane paths equal KT2 `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`.
Expected production-only applied tree `d356238999ab436ddc1dd7ffa845b0db214aa53e` (prior U4 binding;
U4B observed tree NOT_RUN). Prior U4 native CMP2 waiver is historical, not a new proof claim.

One attempt, no retries: diagnostic, standard4/jobs1, 3m per harness, controls/uninit on, inventory off.
Envelope `(4 × 3 + 30) = 42min`; reserve `$0.5670` <= stage cap `$0.60`.
Spend/reservation `$0`; no phase registration, dispatch or watcher during preparation.
Coordinator must recheck project slots/budget and approve exact final SHA before dispatch.
After GO only: `research/challenge-8/kani-k1/tools/k1g.sh dispatch experiment/kani-k1-kani3300u4-20261111`,
then task-mandated `k1g.sh watch BUILD`, end turn. Thread cwd currently `/root`; no watch armed.

After terminal: Brief first, bounded `k1g.sh summary BUILD` and `summary BUILD 0 4`, status, budget,
`check-tooling BUILD 3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`; use only permitted bounded evidence.
Check head/request/patch/pin/tooling/tree identities, completeness, every failed check and covers.
No raw logs/archives/credentials or local cargo/rustc/Kani/CBMC. Missing actual argv/detail stays UNKNOWN.
Write `RESULT-KANI3300-U4B.md` here after the build (<=20 lines): table status, failed/total, covers,
Failed Checks with location; split-read conclusion, bounded normal-return scope and cost. No result fabricated pre-build.

Static checks PASS in `static-check.json`; request validator accepted four roots; rustfmt wrapper applied;
`git diff --check` PASS. Tooling unchanged; no runner service changes requiring new service tests.
Independent review receipt follows separately; neither review nor packet integrity authorizes dispatch.

Independent Luna HIGH review PASS, no blocking findings: `INDEPENDENT-REVIEW.md`.
Reviewed semantic candidate `72c4a6fde83c659dddda4960d3cc08999efc157b`;
post-review delta contains only review metadata and checkpoint status. No dispatch authorization.
