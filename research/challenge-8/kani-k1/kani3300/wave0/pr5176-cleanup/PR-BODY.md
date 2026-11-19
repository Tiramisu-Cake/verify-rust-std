Typed copies of unions with zero-sized array arms can reach CBMC's zero-width-array invariant. This change represents zero-sized payloads in padded union wrappers with the existing empty unit struct, while retaining each field's logical type for projections and indexing. Rustc layout supplies the size while recursive types are still being generated. Resolves #5175.

The regression tests cover typed copies, padding, alignment, field order, nested arrays, indexing and recursive types. Nonzero-width payloads containing zero-sized arrays remain outside this fix (#5085 and diffblue/cbmc#9487).

Testing: [Existing standard CI on the original PR head](https://github.com/Tiramisu-Cake/kani/actions/runs/43605511755). Static preservation and oracle checks pass; native validation of the cleanup is pending.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
