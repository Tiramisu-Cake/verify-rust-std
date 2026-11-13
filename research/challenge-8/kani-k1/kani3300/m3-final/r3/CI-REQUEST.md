# M3-R3 coordinator handoff

Source clone `/root/kani-fix-3300-m3r3`, branch `fix/kani-3300-m3r3`.
Source SHA `6c29e38c57fdf646bf07725c5c09008518d04255`, tree
`cdc30da3c5327e8070ee4f61a42df37c9ea30104`.
Direct baseline `aac27ed95364989bc045e5cdc227f2a97448f955`; its two new commits
are `d36cfa00c9bfbc7d71b6a0974af08b31822e0023` and the source SHA above.
Do not replay the R2 guard commits 30655f306/a221d00cf/88c532d6c.

Worker performed no push, compiler/verifier run or CI dispatch. Coordinator owns
publication and CI. Compile/proof outcomes below are requested, not observations.

1. Target `tests/expected/uninit/part1-composition/move-return-top-level.rs`:
   `top_level_move_return_reinit_legal` must succeed with returned=42 and source=23;
   `top_level_move_return_source_hole` must fail on uninitialized u8 without repair.
   Require 1 successful/1 failed harness and named negative-root failure.
2. Target the preserved tuple fixture `move-return-reinit.rs`:
   `move_return_reinit_legal` is semantically legal but currently a known false
   positive; require the supplied property
   `std::mem::transmute_neo::<std::mem::MaybeUninit<u8>, u8>.safety_check.1`,
   FAILURE and `Undefined Behavior: Reading from an uninitialized pointer of type
   `u8``. Both roots currently fail (0 successful/2 failed), with separate named
   failure summaries. This is regression characterization, never UB-detection
   or supported-domain proof credit for the legal root. The negative tuple root
   remains unchanged. No dynamic failing-call attribution is established.
3. Run unchanged B1 `tests/expected/uninit/unresolved-calls/**` and
   `tests/expected/uninit/closure-zst/**`; their sources/goldens are baseline-exact.
4. Run existing Quick on this exact source and retain complete per-root required
   checks/failures for the two new companion roots. Ordinary/pointer R2 fixtures
   and aggregate-transfer-boundary directory were not imported. No guard-related
   expected broad Unsupported is accepted.

The tuple golden's property/status/description is a consecutive group; named
summary failures and exact total constrain root outcomes. The existing expected
matcher is not a complete per-root inventory validator. Confirm detailed
attribution in CI; do not automatically learn/bless new diagnostics.

Existing M3 JSON mixed-root binding remains pending; this stage does not alter
that runner or grant AB/BA, Part 1 release, B1 or B2 proof credit.
