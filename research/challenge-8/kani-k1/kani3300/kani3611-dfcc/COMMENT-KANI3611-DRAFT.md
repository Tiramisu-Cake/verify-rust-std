I measured `refcell.rs` on unpatched upstream Kani [`0aac16ef62`](https://github.com/model-checking/kani/commit/0aac16ef62da9e9d5645782d458593e5d78143ba), CBMC 6.11.0, default CaDiCaL, Ubuntu 24.04 ([run](https://github.com/Tiramisu-Cake/kani/actions/runs/43605710505)).

Command: `kani tests/expected/function-contract/interior-mutability/whole-struct/refcell.rs -Z function-contracts -Z unstable-options --cbmc-args --object-bits B`. All five runs verified successfully.

| B | SAT variables | Clauses | Max RSS (GB, reported) |
|---:|---:|---:|---:|
| 8 | 74,388 | 172,601 | 0.26 |
| 10 | 272,532 | 665,657 | 0.26 |
| 12 | 1,065,108 | 2,637,881 | 0.66 |
| 14 | 4,235,412 | 10,526,777 | 2.52 |
| 16 | 16,916,628 | 42,082,361 | 9.84 |

The exact fits are `V = 258·2^B + 8340` and `C = 642·2^B + 8249`, with zero residual at every point.
The coefficients match exactly two sliced 64-bit DFCC-table reads: each contributes `129·N` variables and `321·N` clauses, where `N = 2^B`.

DFCC's object-indexed [sets](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/ansi-c/library/cprover_contracts.c#L251-L278) allocate `1UL << object_bits` pointer entries, and constant-sized arrays are [bit-flattened by default](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/solvers/flattening/boolbv.cpp#L534-L552).
After a table write, the expression becomes `WITH`; [symex does not forward-propagate it](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-symex/goto_symex_can_forward_propagate.h#L44-L58), unlike the initial constant array.
The [slicer](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-symex/slice.cpp#L34-L121) can remove table definitions while [GOTO conditions are still converted](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-symex/symex_target_equation.cpp#L457-L482), leaving symbolic table bits.
For a syntactically non-constant `POINTER_OBJECT` index, [`convert_index`](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/solvers/flattening/boolbv_index.cpp#L203-L240) constructs selectors across all N entries, including work done before constant index-bit comparisons can eliminate alternatives.

Lowering object bits reduces these table widths exponentially, explaining the improvement here; the chosen value still needs enough object-ID capacity for the program. This measurement does not establish a general fix.

With `--arrays-uf-always` added to the CBMC arguments ([run](https://github.com/Tiramisu-Cake/kani/actions/runs/43606302978)), both B=12 and B=16 still verify successfully. The clause count stays at 8,247 for both; variables are 532,628 and 8,396,948. At B=16, max RSS drops from 9.84 GB to 2.41 GB and wall time from 22.4 s to 3.3 s. I only tried this one test, so this is an observation rather than a suggested default.

*Disclosure: this analysis and comment were prepared with the help of AI assistants.*
