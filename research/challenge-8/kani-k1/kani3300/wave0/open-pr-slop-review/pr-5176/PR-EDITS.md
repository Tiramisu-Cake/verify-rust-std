Proposed title: Fix typed copies of padded unions with zero-sized fields

Proposed body after the scoped cleanup below. This text is a local suggestion;
existing CI and base/fixed observations originate in the pinned PR snapshot.
No new native validation is represented by this review. Preserve one existing
standard-CI reference and mark validation of any later cleanup pending.

---

Kani can abort CBMC while verifying a typed copy of a union containing a zero-sized array arm (`kani tests/expected/zst-union-arm/main.rs --harness array_typed_copy`). On main, the reproducer reaches CBMC's zero-width-array invariant. The change lets Kani verify its copy and field-access assertions. Resolves #5175.

Represent zero-sized payloads inside padded union wrappers with the existing empty unit struct, while retaining each field's logical type for projections and indexing. Rustc layout supplies the size while recursive types are still being generated. The regression tests cover typed copies, padding, alignment, field order, nested arrays, indexing and recursive types. Nonzero-width payloads containing zero-sized arrays remain affected by the separate backend issue tracked in #5085 and diffblue/cbmc#9487.

Testing: [Existing standard-CI run](https://github.com/Tiramisu-Cake/kani/actions/runs/43605511755). Validation of the cleanup is pending.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*

---

Before publishing, the owner must replace the Testing sentence with a truthful
result for the final candidate, retaining one standard-CI link. This review did
not inspect that run's logs. Keep the issue link, license and disclosure. Remove
the current erroneous universal-cover claim, head SHAs, harness/platform counts,
rerun narrative, second perf-comparison link, speculative workaround-removal
instruction and stale uninit-checks anecdote. No change to live PR was made.
