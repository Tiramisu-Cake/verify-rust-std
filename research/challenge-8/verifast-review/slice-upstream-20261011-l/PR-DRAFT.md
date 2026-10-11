# Title

[Rust] Support slice as_mut_ptr using the existing typed cast lowering

# Body

Calls to `[T]::as_mut_ptr` currently have no exact binding in the Rust translator. Route that exact compiler-selected method through the existing `[T]::as_ptr` typed cast, matching the standard library body `self as *mut [T] as *mut T`. The lowering returns the data pointer and grants no additional element permissions or initialization facts.

Regression tests use actual calls for ordinary, empty and MaybeUninit slices, check the data pointer, and preserve generated slice resources. A negative opens MaybeUninit storage and attempts an initialized byte read without establishing the required view.

Validation: fresh clean-base missing-binding control, candidate positives (62 statements), and expected initialized-read rejection at line8 passed on candidate095ef553e92deaae063b3684ea3172128e666785. Linux make test passed with0 failed processes, including the normal Rust suite, on nightly-2026-09-25 (rustc f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f). Cloud Build34c10f8c-c6f9-49b4-a75b-124755f5d219; optional Rocq, Java AST server and private assignment models were unavailable/disabled, as recorded in receipts. Other platforms are NOT_RUN. This PR does not include the separate ManuallyDrop change or Challenge8 experimental profiles.

Draft only. No PR or upstream publication authorized/performed.
