# VeriFast insertion probes

These are Actions-only experiments for VeriFast 26.09 and Rust
`nightly-2026-02-05`. They are not proofs of Challenge 8. The `frontend`
profile checks that the pinned frontend processes the actual generic
`insert_tail` body and reports a real safety obligation. The `range` profile
adds an initialized owned range and comparator ownership to address its first
pointer-bounds failure.

The runner `run-verifast-probe.sh` requires a GitHub-hosted Linux Actions runner.
Its arguments are a budget in minutes (default `90`) and `frontend` or `range`
(default `frontend`); the workflow must pass the selected profile explicitly.
The extraction script reads the live
`library/core/src/slice/sort/shared/smallsort.rs` and writes a disposable crate
under `research-results/verifast-probe/`. It takes these exact source spans:

1. `CopyOnDrop<T>` and its `Drop` implementation.
2. The complete generic `insert_tail` with its documentation and body.
3. The complete generic `insertion_sort_shift_left` with its documentation and body.

Each span is also saved as its own byte-exact `source-spans/*.rs` artifact with
its size and SHA-256 in `extraction.json` and `extraction.log`.

The original and verified source have identical Rust code. Both profiles add
separate `req` and `ens` ghost comments to `insert_tail`. The `range` profile
also adds one ghost lemma and invokes it before the first pointer subtraction.
A byte-for-byte check after removing every recorded ghost insertion enforces
this relationship; the manifest records each insertion's size and SHA-256.
The Actions run also
invokes the repository's pinned `refinement-checker`. Both
copies import `ManuallyDrop`, `ptr`, and `intrinsics` from `core`; those imports
are the only crate shell. There are no stand-ins for pointer operations,
comparators, guard drops, or sorting functions. The crate shell is not the
original core module tree, so resolution or frontend results from this probe
cannot alone establish a proof of the integrated std library.

The default `frontend` profile retains `req true; ens true;`. It provides no
pointer or ownership facts. Actions run
[37393312268](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37393312268)
at `8f1fc63` reached `Verifying function smallsort::insert_tail`, then failed
to prove that `tail.sub(1)` remains within pointer limits. Refinement passed.

The `range` profile has a symbolic `usize` length `n >= 2`, an initialized
exclusive range `begin[..n] |-> xs`, `tail == begin + (n - 1)`, ownership of
each generic `T` value through `foreach(xs, own::<T>(t))`, and an owned
comparator `*is_less |-> f &*& <F>.own(t, f)`, with the thread and type
interpretation resources required by the pinned model. The single range
predicate describes one pointer provenance and arbitrary representable valid
lengths; there is no fixed four-element allocation or sortedness/comparator
order assumption. The `ens true` postcondition remains deliberately weak, so
this first obligation does not establish resource restoration, sortedness or a
usable caller contract. A run must determine whether it resolves the pointer
limit and what the next actual obligation is. In particular, the range
predicate's treatment of zero-sized generic types has not been established;
do not infer full generic coverage from a successful trace.

Actions run
[37394022890](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37394022890)
at `2ba502b` accepted this generic precondition, reached the actual
`insert_tail` body, and stopped at the same first `tail.sub(1)` bound obligation;
refinement passed. An explicit `array_inv::<T>()` call before the subtraction
was accepted in Actions run
[37395348422](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37395348422)
at `6851c1a`, but VeriFast still stopped at that bound; refinement passed.

The next `range` revision adds a ghost lemma, `interior_pointer_limits`, with
the same initialized range resource and an arbitrary mathematical index with
`1 <= count` and `0 <= index <= count`. Its body opens the nonempty range,
uses the pinned `points_to_limits` lemma on its first owned cell to derive
`0 <= size_of::<T>()`, and closes the range again. It then invokes the pinned
`array_inv::<T>()` to get the base and one-past-end limits and allocation-size
bound, followed by the pinned
`mul_mono_l` to place `index * size_of::<T>()` between zero and the total
byte size. Its postcondition returns the range resource and states that the
interior pointer is within limits. The call before `tail.sub(1)` uses `n - 2`;
the existing `n >= 2` precondition establishes the helper's count and index
bounds. This
adds no new safety assumption or fixed length cap. `note` calls in the lemma
check the derived size and endpoint facts rather than assuming them. The lemma body and its
use have not yet passed Actions verification. The next result must determine
whether the arithmetic proof succeeds and whether VeriFast connects
`tail - 1` with `begin + (n - 2)`; a failure there would require another
proved equality step, not a new precondition.

The pinned [Rust annotation type reference](https://github.com/verifast/verifast/blob/26.09/docs/rust-reference/src/types.md)
defines every integer type in ghost declarations and annotations as the
mathematical integers. Thus the `i32` formal parameters of `mul_mono_l` (and
the pinned `array_split` lemma) do not impose an `i32::MAX` cap on a runtime
`usize` length. This does not itself prove the calls' arithmetic and resource
preconditions; the Actions run must check those obligations.

Actions run
[37396479423](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37396479423)
at `da5f16e` checked the first version of this helper and failed at the first
`mul_mono_l` call because `0 <= size_of::<T>()` did not follow from endpoint
facts alone. Refinement passed. The revised helper derives nonnegativity from
the owned first cell. Actions run
[37397404058](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37397404058)
at `91392b6` passed that helper and `tail.sub(1)`, then stopped at the first
`&*tail`: the frontend required a `ref_precreated_token<T>(tail, _)`.
Refinement passed.

The next staged `range` revision isolates the final two cells and their
generic `T` ownership using the pinned `array_split` and `foreach_split`
lemmas at symbolic offsets `n - 2` and `1`. It closes each cell's full-borrow
content, starts a short lifetime, creates two full borrows, turns them into
shared borrows, and uses `precreate_ref` plus `init_ref_share` to prepare
the two actual `&*` expressions. Fractional `ref_initialized` resources and
`<&T>.own` resources are prepared before the comparator call. The existing
`unsafe` block starts with a ghost `let_lft 'cmp = cmp_k` declaration, and the
call carries a ghost lifetime argument. All of these are comments in the
verified copy; no Rust statement or signature changes. The old precondition
is unchanged, including support for symbolic lengths and generic types.
This preparation is not yet verified. In particular, the Actions run must
test whether the frontend accepts lifetime arguments on the desugared
`FnMut` call and connects the split cells to `sift` and `tail`.

Actions run
[37398670146](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37398670146)
at `6540b15` accepted extraction, refinement, and the lifetime declarations,
then stopped at a parse error on the second command in the comparison's
multi-command `/*@ ... @*/` annotation. The pinned
[function-body annotation syntax](https://github.com/verifast/verifast/blob/26.09/docs/rust-reference/src/func-body-annots.md)
allows one ghost command per annotation unless commands are grouped in an
explicit ghost block. The corrected probe gives each command its own `//@`
annotation. Actions run
[37398942673](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37398942673)
at `d1bd9d6` passed parsing, the symbolic array and ownership split, the two
full borrows, and reference initialization. It stopped when the second
`open_frac_borrow(..., 1/2)` could not match another half of the comparison
lifetime token.

The pinned `begin_lifetime` returns a full `lifetime_token(k)`. Both
`share_full_borrow` and `init_ref_share` require `[q]lifetime_token(k)` and
return the same `[q]` fraction, so preparation preserves the full token in
total. The revised probe invokes the pinned parser's `merge_fractions`
command on this token before opening the two references, to combine any
separate chunks left by those calls. Each simultaneous access then requests
one half. This is an explicit redistribution of existing ownership, not a
new precondition or assumption. The next Actions result must confirm the
resource match; cleanup still needs to close both fractional borrows before
ending the lifetime.

This stage deliberately stops at the first comparison. Ending its lifetime,
recovering potentially changed `T` values after comparator interior mutation,
and restoring ownership on the early-return, normal, and unwind paths remain
proof obligations. No result from this stage should be reported as a complete
`insert_tail` proof, even if the first comparison passes.

Both profiles leave the extracted `CopyOnDrop` and outer function unverified:
`-skip_specless_fns` skips these unspecified functions. The experiment
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
function count and checked paths before drawing any conclusion; with these
preconditions, a success could mean the target was not analyzed or that the
guard's unverified generic drop summary hid its restoration obligation.

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
