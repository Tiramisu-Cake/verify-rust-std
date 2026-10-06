# VeriFast insertion frontend probe

This is an Actions-only feasibility experiment for VeriFast 26.09 and Rust
`nightly-2026-02-05`. It is not a proof of Challenge 8. Its question is whether
the pinned VeriFast frontend can process the actual generic `insert_tail`
function and report a real safety obligation from its body. A failed verification
is an expected, useful result if it reaches the first missing ownership fact.

The runner `run-verifast-probe.sh` requires a GitHub-hosted Linux Actions runner.
The extraction script reads the live
`library/core/src/slice/sort/shared/smallsort.rs` and writes a disposable crate
under `research-results/verifast-probe/`. It takes these exact source spans:

1. `CopyOnDrop<T>` and its `Drop` implementation.
2. The complete generic `insert_tail` with its documentation and body.
3. The complete generic `insertion_sort_shift_left` with its documentation and body.

Each span is also saved as its own byte-exact `source-spans/*.rs` artifact with
its size and SHA-256 in `extraction.json` and `extraction.log`.

The original and verified source have identical Rust code. The verified copy
adds only the separate ghost comments `/*@ req true; @*/` and
`/*@ ens true; @*/` to `insert_tail`. A byte-for-byte check after removing
these comments enforces this relationship. The Actions run also invokes the
repository's pinned `refinement-checker`. Both
copies import `ManuallyDrop`, `ptr`, and `intrinsics` from `core`; those imports
are the only crate shell. There are no stand-ins for pointer operations,
comparators, guard drops, or sorting functions. The crate shell is not the
original core module tree, so resolution or frontend results from this probe
cannot alone establish a proof of the integrated std library.

`req true; ens true;` is deliberately weak. It describes no valid pointer,
initialized cell, exclusive ownership, ordering, or comparator behavior.
Because `insert_tail` is unsafe, this precondition is insufficient for its
first dereference; a verifier should reject the body. We have not guessed a
generic VeriFast ownership predicate for this call boundary. A future proof
must supply one for the entire initialized `[begin, tail]` range and address
the temporary gap, `CopyOnDrop` restoration, comparator unwind, and generic
`T`/`F` ownership. The current run does not verify the extracted `CopyOnDrop`
or outer function: `-skip_specless_fns` skips these unspecified functions. It
must never be counted as a three-function proof. The expected number of
specified target bodies is exactly one: `insert_tail`. Any reported success
requires checking that at least this target body was actually analyzed; a
process exit code or positive statement count alone cannot establish that.

The probe does not use `-ignore_unwind_paths`, `-allow_assume`,
`assume_correct`, or any assertion suppression. It runs VeriFast and the
refinement checker separately so both failure modes are preserved. A frontend
error on `ManuallyDrop::new`, `ptr::copy_nonoverlapping`, `Drop`, generic
`FnMut`, `intrinsics::abort`, or the detached module imports is an unsupported
model result to diagnose from the log; it is not a safety counterexample or
successful verification. The first completed run should record which function
VeriFast says it verified, the first diagnostic, and whether the checker
accepted the ghost-only refinement. If VeriFast reports success, inspect its
function count and checked paths before drawing any conclusion; with this
precondition, a success could mean the target was not analyzed.

The CLI spelling is pinned to VeriFast tag `26.09`: its `vfconsole.ml` registers
`-rustc_args` and `-skip_specless_fns`, while `refinement_checker/main.ml`
parses `--rustc-args`. The installed `bin/VERSION` file, which VeriFast itself
reads for its banner, is captured instead of relying on an unsupported
`-version` flag.

The artifact contains `environment.txt` (source commit, hashes, tool pin,
installed Rust compiler version, VeriFast release `bin/VERSION` when present,
and runner),
`extraction.json` and `extraction.log` (per-span hashes and sizes), the separate
source spans, both source copies, VeriFast and
refinement logs and statuses, a combined execution log, GNU time resources,
and the overall exit status. The budget includes downloading/installing the
pinned toolchain. The workflow should dispatch this selection manually and
upload `research-results/` even on failure, as with the Kani experiments.

No local compilation or verification is permitted; editing and static inspection
of these scripts is the only server-side preparation.

## Pinned API evidence for follow-up (not a proof)

Read-only inspection of VeriFast tag 26.09, source commit
`809de4596839b739dd999f9e462242c835e3af46`, found:

| Operation | Pinned model / relevant obligation |
| --- | --- |
| `FnMut::call_mut` | `bin/rust/std/lib.rsspec` requires thread token, owned receiver and owned argument tuple; has normal and unwind postconditions |
| `ptr::copy_nonoverlapping` | Same spec requires initialized source range and writable destination range, preserving source and initializing destination |
| Initialized generic range | `bin/rust/prelude_core.rsspec` defines `array` / `p[..n]` plus split/join lemmas; element ownership is separate from initialized bytes |
| `ptr::read`, pointer add/sub, `ManuallyDrop` | Frontend translator models these operations; reaching them still needs an actual Actions result |
| Guard destruction | Generic `drop_in_place` summary requires the guard's `.own` predicate; the actual `CopyOnDrop::drop` body is currently unspecified/skipped |

The next ownership contract can start from a mathematical list of initialized
cells, `n >= 2`, `tail == begin + n - 1`, comparator ownership and the thread
token, plus ownership of each logical `T`. This is an API-grounded sketch, not
a syntax-tested contract. An actual proof must specify and verify
`CopyOnDrop::drop` and tie its ownership predicate to the initialized held source
and writable gap; using only a generic drop summary would leave restoration
unproved. Keep comparator unwind paths enabled. A concrete closure harness is
another frontend risk: the pinned translator contains an unsupported closure
aggregate case. The extracted generic target itself constructs no closure.
