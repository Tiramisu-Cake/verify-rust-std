# Independent raw review — C3 bounded-prefix Build3

**Verdict: PASS for the pinned C3 bounded-prefix diagnostic.** The positive
candidate and all eight target-first negative controls have the expected raw
outcomes, and the transformed AST's callback-local allocation scopes match the
fresh MIR/source map. This is still an experimental bounded-prefix candidate:
the Build stage records `proof_credit=false`, the result says
`accepted=false`, and `full_sort4_callable_summary=false`. It does not prove
the full `sort4_stable` function or admit later projection by itself.

This review covers Build `a956b0b2-4e05-4c19-90b4-408f381ba1fc`, raw archive
verification `c62db4…`, proof-input identity
`aa6e5a725f71506602903f95b1832a32fa849e50`, under
`/tmp/c3-a956b0b2-read/allprooflogs/cases/sort4-c1-current-recovery`.
The positive post-AST SHA-256 is
`9ca21fdc2e3f199ea73d3ff62f1ec8cf29e7f4f8a3e269dd433e6711c9013397`, matching
the recorded result. Its exact source, pre-AST, normal/readonly MIR and
translator hashes match the C3 profile. I read saved artifacts only; I ran no
compiler, extractor, verifier, or proof.

The positive raw log enters `sort4_stable` once, after verifying
`selected_four_limits`, `split_selected_four`, and `join_selected_four`.
The limits helper establishes source-offset bounds before the unchanged
`.add` expressions; the split and inverse-join helpers consume the array and
`foreach` ownership resources and branch on `c1`/`c2`. The C3 callback proof uses the selected
individual permissions and returns the same four CURRENT owners through the
inverse join. The source still uses the original `a`/`b`/`c`/`d` pointer
expressions, and `is_less(&*c, &*a)` remains the C3 call. The four Boolean cases
map the selected `(c,a)` offsets to `(2,0)`, `(3,0)`, `(2,1)`, `(3,1)` and the
complementary `(b,d)` offsets to `(1,3)`, `(1,2)`, `(0,3)`, `(0,2)`. The
ownership argument is the split array/`foreach` permission; pointer arithmetic
or numeric pointer equality does not create permission. The helper proof
preserves callback-current values and restores the original physical order.

The actual post-AST has 155 direct outer local declarations and the strict C1,
C2, and C3 callback blocks contain the source-mapped 8, 10, and 6 locals
respectively (`$_27..$_34`, `$_63..$_72`, and `$_124..$_129`). C3's six are
inside the sibling scope; `_123`/`c3` remains outer. The C3 tuple object is
`$_125`, the only struct-valued callback temporary there. The 12 future callback
locals (`$_135..$_140`, `$_164..$_169`) are absent, while C3 setup/close
unit-tuples and the original post/return structure remain present. This
corresponds to 179 total source callback/root declarations (155 + 8 + 10 + 6),
not the raw textual count of every nested `DeclStmt` form in the AST.

Allocation follows the frozen kernel snapshot: the C3 positive snapshot pins
`src/verifast.ml` at
`37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`. The
prior C2 kernel review established that an uninitialized struct `DeclStmt`
uses `produce_object`, non-struct uninitialized locals with `address_taken=false`
are symbolic locals without heap chunks, and lexical `BlockStmt` cleanup frees
local objects on normal exit and outward goto. Here the emitted AST places
`$_125` in the strict C3 block and leaves the tuple's five reference/pointer
neighbors symbolic; its scope closes at the source marker before recovery and
join. The raw positive log records cleanup at the C3 block close (`449,9-450,1`)
and outer-local cleanup at function exit (`468,1-2`), followed by the original
postcondition and leak checks. The log does not print each `produce_object`
operation explicitly, so producer counts are derived from the pinned kernel
rules and AST declarations, not claimed as separate trace output. The retained
outer unit structs—including later setup units—remain an intentional
produce/free burden on every bounded outcome.

The positive log ends with `0 errors found (335 statements verified)`, no
dead-code findings, and the original function postcondition/leak checks. It
verifies both normal and unwinding outcome arms; the C3 unwind arm closes debt,
recovers `(c,a)`, and calls the same inverse join before the unchanged unwind
return. All eight raw control logs enter `sort4_stable` before their first
failure:

| Control | Exit | First raw failure |
| --- | ---: | --- |
| `c1-unwind-false-assert` | 1 | False assertion at `verified/lib.rs:365` in C1 unwind epilogue |
| `c2-unwind-false-assert` | 1 | False assertion at `verified/lib.rs:398` in C2 unwind epilogue |
| `c3-normal-missing-close` | 1 | Missing `comparison_debt` chunk at helper precondition, `verified/lib.rs:68` |
| `c3-normal-omit-join` | 1 | Missing four-owner `foreach` post at `verified/lib.rs:317` |
| `c3-unwind-false-assert` | 1 | False assertion at `verified/lib.rs:447` in C3 unwind epilogue |
| `c3-unwind-missing-close` | 1 | Missing `comparison_debt` chunk at helper precondition, `verified/lib.rs:68` |
| `c3-unwind-omit-join` | 1 | Missing four-owner `foreach` post at `verified/lib.rs:324` |
| `normal-false-post` | 1 | Deliberately false normal post at `verified/lib.rs:315` |

The source mutant exits 2 with the exact refusal
`SORT4-C3-BOUND: verified source SHA256 differs` and has zero target entries.
The default-off C2 replay exits 0 with its existing 184-statement result. The
mandatory unbound-C2 replay exits 2 with
`SORT4-C2-DISCOVERY: UNBOUND_C2_LIFETIME_NOT_PROOF scaffold_AST_emitted`.
These controls confirm opt-in/default and source-binding behavior; they are not
C3 proof credit.

The saved C3 capture/bound snapshots have the same HEAD, effective RSSpecs,
proof-std inputs, non-translator critical files, and non-VeriFast binaries.
Only the intended translator hash and rebuilt `bin/verifast` differ. This
closes the frozen non-translator identity check for this Build. Exact raw
control, local-scope, and allocation review supports the C3 PASS above, while
the candidate remains `accepted=false` and outside full-function claims.
