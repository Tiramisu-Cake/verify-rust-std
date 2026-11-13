# M3-R3 preparation

Prepared source `6c29e38c57fdf646bf07725c5c09008518d04255` in the new clone
`/root/kani-fix-3300-m3r3`, branch `fix/kani-3300-m3r3`, directly from
`aac27ed95364989bc045e5cdc227f2a97448f955`. R2 guard changes are absent by
ancestry; no revert on top of their commits was used.

The new top-level `MaybeUninit<u8>` companion uses explicit custom-MIR
`Move(source)` into `relay`, keeps the source address live, repairs it to 23,
reads it through the helper, reports it through an ordinary u8 out-pointer, and
returns the initialized slot directly. The legal root retains assertions that
the returned slot contains 42 and the repaired source contains 23. The no-repair
root retains the deliberate source-hole read and returned-value assertion.
Expectations are SUCCESS/FAILURE respectively; CI has not run on this candidate.

The original tuple-return executable body and both roots are unchanged. Its
legal expectation now characterizes the known false positive authorized by the
R3 task, including the exact reported transmute property, FAILURE, uninitialized
u8 description and named legal-root failure summary. Semantically it must be
SUCCESS. The prior observation comes from the issued task and existing
`../STOP-R1.md`; no new log inspection or proof run was performed. It is not
counted as detection of UB in the legal root, nor proof of which dynamic
assume_init call failed.

User-facing experimental contracts documentation states the missing transfer
for by-value aggregates with nested MaybeUninit/union slots and explicitly gives
no guarantee that these paths fail closed. There is no compiler/runtime/model
change. No R2 ordinary/pointer fixtures were carried forward. B1 unresolved-call
and closure-zst trees and goldens, shared validator, strong-oracle and mode
suites remain baseline-exact; see `INPUTS.json` and `STATIC-CHECKS.json`.

Python identity/scope audit, Git whitespace check, authorized scratchpad
rustfmt `--edition 2021 --check` on both Move fixtures, and review-packet
integrity check pass. Independent static review is recorded in `REVIEW.md`.
No cargo/rustc/Kani/CBMC, push, CI or Cloud dispatch was performed. Compilation,
verification and Quick are NOT_RUN. This stage grants no B1/B2 or release credit;
existing JSON inventory binding/producer-order limitations remain open.
