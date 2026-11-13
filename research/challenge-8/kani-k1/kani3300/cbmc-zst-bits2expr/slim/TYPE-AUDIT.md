# Static type/API audit

Candidate: fb9c8d53d4f5e109324d8b17fd8794ed4776b43e; BASE 37a17adc07f29e1127f100debf1d8eea00532a24.

- `pointer_offset_bits` returns `std::optional<bitst>`; `bitst` is `named_mp_integert<bits_tagt>` (an arbitrary-precision integer with a bit-unit tag), so the explicit nonnegative comparison remains meaningful. The array predicate retains `has_value()` before dereference and compares to `bitst{0}`, matching the existing struct branch. No integer zero/implicit signed conversion is introduced.
- Entry whole-type width/union checks and array constant-size/count conversion are byte-identical to BASE. For element width 0, `numeric_cast_v<std::size_t>` returns 0 and `std::string(bits, i*0, 0)` is an empty slice. The loop still runs N times, recursively reconstructs each element, and produces `array_exprt` of the original array type with N operands. Missing recursive result remains a failure to simplify.
- `struct_tag` resolution reconstructs with the original tagged type. Empty structs/unions and nested zero-length arrays have existing reconstruction paths. Unsupported types still return no result; vector and complex guards stay strictly positive. Huge representable counts retain O(N) allocation/recursion; no new bound or semantic premise is added.
- The three TEST_CASE bodies are retained from `33235a4ef1:unit/util/zst_bits2expr.cpp` (only tags and formatting differ). Counts 0/1/2, nested 3/0 element rows, both endian values, nonempty-bit rejection, tagged elements, 48-bit nonzero siblings and union/roundtrip assertions remain.
- `arith_tools`, `bitvector_types`, `c_types`, `cmdline`, `config`, `namespace`, `simplify_utils`, `std_expr`, `symbol_table`, empty_namespace and Catch were already included. `std_expr.h` includes `std_types.h`; existing constructors accept the original initializer operands/types. No include duplication or new headers.
- Explicit `unit/Makefile:208` already registers `util/simplify_expr.cpp`; `unit/CMakeLists.txt:12` recursively globs unit sources. No Makefile/CMakeLists change. Original unit file header is unchanged.

Assurance: STATIC_SOURCE_ONLY. Compilation, linking, executable discovery and CBMC verdicts: NOT_RUN locally. Formatter18.1.8 unavailable locally; final diff format remains NOT_RUN. Project Python cpplint passes on both changed C++ files (0 errors; Python deprecation warnings only).
