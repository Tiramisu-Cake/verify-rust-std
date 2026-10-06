# VeriFast generic swap-size helper

This is a small, independent generic target for VeriFast 26.09 with
`nightly-2026-02-05`. It targets the live
`has_efficient_in_place_swap<T>()` at the end of
`library/core/src/slice/sort/shared/smallsort.rs` (currently the item beginning
at line 863). This helper is the seventh listed safety target in the Challenge
8 coverage map. It is called by the small-sort dispatch code at the
`has_efficient_in_place_swap::<T>()` branches in that same file.

The extractor selects the complete final item, including `#[must_use]`, using
unique exact start and body-end anchors. It fails closed if either anchor is
not unique, the function signature or `size_of::<T>() <= 8` expression changes,
or non-whitespace follows the item. The disposable original source contains
that exact live body and only a `core::mem::size_of` import for the minimal
crate shell. The verified copy adds only the contract
`req true; ens result == (std::mem::size_of::<T>() <= 8);`. Extraction metadata records
source, body and variant hashes; stripping the one ghost contract must recover
the original bytes exactly. The pinned refinement checker verifies this
ghost-only relationship.

The function is generic over unrestricted `T`; it has no runtime arguments,
pointer, slice, ownership, sortedness, or comparator premises. The result
contract states exactly that the returned boolean is the live size threshold
expression. The body performs only a type-size query and integer comparison,
so this isolated target is not intended to need an uninitialized-memory,
valid-value, or pointer-access obligation. Proving this helper would cover the
helper target only; it would not prove the dispatch callers or the other six
safety targets.

Run `run-verifast-swap-size.sh [30|60|90|120]` only on a GitHub-hosted Linux
Actions runner. The default is a single 90-minute budget covering extraction,
the pinned tool setup, VeriFast and refinement checking. Evidence is written
under `research-results/verifast-swap-size/`; the run stores source and tool
hashes, the exact extracted variants, full logs, each stage exit status and
GNU `time -v` resource reports. A passing selection requires both verifier
and refiner exit status zero, exactly one VeriFast report for
`smallsort::has_efficient_in_place_swap`, and at least one execution trace
statement in the extracted helper body. The pinned CLI source
`src/vfconsole/vfconsole.ml` at pinned tag `26.09` (commit
`809de4596839b739dd999f9e462242c835e3af46`) defines `-verbose 1` as statement-execution
verbosity; `src/verifast1.ml` prints execution contexts at verbosity level 1,
and `src/verifast.ml` emits the named `Verifying function` context. The runner
checks these positive function and body-statement records, rather than
inferring analysis from extraction metadata alone. An overall green run establishes
only this helper's stated generic result contract against the extracted live
body at that source revision.

The pinned setup script identifies VeriFast 26.09 Linux by SHA-256
`da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa` and uses
Rust `nightly-2026-02-05`. Existing proof files use
`std::mem::size_of::<T>()` in VeriFast contracts, providing repository
precedent for the size expression. The isolated crate imports the function as
`size_of` for the actual body and uses the fully qualified spelling in the
ghost contract.
