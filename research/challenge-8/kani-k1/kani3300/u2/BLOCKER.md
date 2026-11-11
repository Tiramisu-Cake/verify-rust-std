# KANI3300 U2 scratch blocker

Observed in COMPLETE build `6a2f4260-c343-427f-a6ef-6ed0bce50b7c` at reviewed head
`108551d92b7754d5366ec3b59bd0b652510adcef`, exact U1 patch `306851ac…4467`.

U8: FAILED 2/507, covers 0/1. U9: FAILED 2/463, covers 0/6.
Both have exactly these located failures at `/workspace/src/library/core/src/array/iter.rs:77`:

- Transmuting between types of incompatible layouts.
- Kani does not support this assignment to MaybeUninit storage.

The built source's N4 general route iterates an array of two offsets at `smallsort.rs:267`.
Array `IntoIterator::into_iter` converts the input array to `[MaybeUninit<T>; N]` with
`transmute_unchecked` at `array/iter.rs:77`. Source analysis therefore suggests the conversion
from an initialized offset array to MaybeUninit-array storage is the next tool-model gap.
The mandated patch's `maybe_uninit_transmute` handles conversion out of a MaybeUninit wrapper;
its storage-assignment fallback reports the second diagnostic above. This is a static explanation
consistent with the bounded failures; exact instantiated MIR/cause binding was not exposed.
The earlier U0 scratch allocation diagnostic is no longer the reported blocker.

The required U9 observations are absent: no uninit failure at scratch[4], no demonstrated successful
scratch[3] read, and no reached scratch[3] covers. No reported failure at its call site does not
establish success when all six covers are unsatisfied. No scratch safety/sorting proof is credited.

Separately U7 exposes the forecast select_unpredictable Unimplemented operation at hint.rs:871,
plus two `Check that *var_* is assignable` failures in kani_core mem_init; all three are preserved
verbatim in RESULT and check-report. Their cause is not independently established as a std defect.

No fix here: the exact patch, core, tooling, pin and existing eight harnesses are frozen by TASK.
Same-nine-row retry would cost/reserve $0.1215 + $0.7695 = $0.8910 > $0.80. No repair dispatched.
Next tool task should cover this initialized-array conversion with checked positive/negative
sensitivity, retain validity/data-padding checks and existing controls, then rerun real U8/U9.
The core package progression remains u64/N4 through Stable/function item, followed by N8/sort4.
