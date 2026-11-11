# Check initialization when extracting MaybeUninit values

With `-Z uninit-checks`, initialized `MaybeUninit<T>` values could fail layout
checks while raw slot and scratch-array access remained unsupported.
Check the source byte state against T's data mask before extraction or transmute.
Preserve shadow through copies and clear the full slot when it is reset.
Track field writes, flat arrays, constant-length repeats, and slice offsets.

Validated on pinned Kani with 20 native selectors, including nine new negative
tests with uninitialized-read diagnostics and the existing regression goldens.
The direct select_unpredictable path remains unverified; general nested unions
and function-pointer calls remain unsupported.
