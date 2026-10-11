# Title

[Rust] Support slice as_mut_ptr using the existing typed cast lowering

# Body

Calls to `[T]::as_mut_ptr` currently have no exact binding in the Rust translator. Route that exact compiler-selected method through the existing `[T]::as_ptr` typed cast, matching the standard library body `self as *mut [T] as *mut T`. The lowering returns the data pointer and grants no additional element permissions or initialization facts.

Regression tests use actual calls for ordinary, empty and MaybeUninit slices, check the data pointer, and preserve generated slice resources. A marked negative opens MaybeUninit storage and attempts an initialized byte read without establishing the required view.

Validation: PENDING fresh focused baseline/candidate and Linux make test (including the normal Rust suite). Exact compiler/source/build receipts and raw negative VC review will be linked in the internal review package. Other platforms are NOT_RUN. This PR does not include the separate ManuallyDrop change or Challenge8 experimental profiles.

Draft only. No PR or upstream publication authorized/performed.
