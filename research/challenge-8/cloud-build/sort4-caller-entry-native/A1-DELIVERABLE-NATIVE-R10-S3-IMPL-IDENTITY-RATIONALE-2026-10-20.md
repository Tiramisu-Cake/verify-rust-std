# R10 original impl AST identity rationale

The source-bound R-only baseline currently rejects two compiler-inventoried
`small_sort` bodies if their printed `item_def_id` strings are equal. That is
not a safe uniqueness key: source/compiler observations establish that distinct
numeric impl/item identities can share a printed DefPath. Matching by DefPath
alone, choosing the first row, or deduplicating the records would discard that
compiler distinction.

The inventory already binds each body to numeric `impl_def_index` and
`item_def_index` values and parses its regular MIR body span. The identity
record will retain that raw full span. At the join, MIR character positions
must be converted to AST columns: the pinned translator's
`translate_char_pos` explicitly adds one (`IntAux.Uint64.try_add pos
Stdint.Uint64.one`, comment `Make it 1-based`; source anchor
`/tmp/r8-p1-base/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml:1433-1440`,
SHA-256 `9391bff0376ad008798a950d76dbaac095cacbe8fd5acf5b2ea4d336a759f33f`).
Therefore the gate compares full AST Lexed spans against a derived +1-column
view of both MIR endpoints, while preserving the raw compiler span in source
inventory and baseline output. AST locations must spell the exact canonical
`verified/lib.rs` path; a prefixed path with that suffix is not canonicalized
or accepted. The AST gate will accept a repeated DefPath
only when the compiler numeric identities and full source spans are each
distinct, and will bind each AST definition uniquely in both directions by
DefPath plus the full regular Lexed `Func` span. Existing compiler signature,
source path, positional lifetime, typed header, native precondition, normal
return, and unwind comparisons remain required.

The pinned AST printer supports compact same-line full ranges: its
`string_of_loc0` prints `-end_column` when both endpoints share a file and
line, and prints `-end_line,end_column` across lines. Source anchor:
`src/frontend/ast.ml:35-47 (git show from /root/verifast)`, commit
`f76012fb518703b1d98e243ac4f487f16877cfcb`, SHA-256
`de4dc2c13c7ba9098fefa78300debc78a2024830e93b6e6e03d9cdecd6d7bf2c`.
The parser therefore accepts both printed full-range forms and expands a
compact endpoint to the same start line; it still rejects point-only
locations.

Synthetic tests cover valid shared printed paths, duplicate numeric identity,
duplicate full spans, ambiguous AST rows, wrong source paths, and full-span
mismatch, while retaining the existing native-structure regressions. No
compiler, fixture preparation, full runner, or Cloud action is part of this
change; deployment still requires the active profile to pin the changed
helpers.
