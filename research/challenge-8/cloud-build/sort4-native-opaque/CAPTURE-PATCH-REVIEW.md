# Native C1 capture-only translator delta — implementation review, NOT_RUN

The implementation follows [NATIVE-C1-CAPTURE-CARD.md](NATIVE-C1-CAPTURE-CARD.md).
It changes only `src/rust_frontend/vf_mir_translator/vf_mir_translator.ml` in the
isolated `/root/verifast-select-sort4-opaque-20261010` worktree. The exact base
copy, saved *before* editing at `/tmp/vf-native-c1-base-1eab6eb5.ml`, has
SHA-256 `1eab6eb54fe5c23d53ca72a6d9dfcbbff09c09ffaf26c48a4f450f5068a8d313`.
The edited translator has SHA-256
`86952a6ac4a61ac854d8a9886cff98ee143a0e75ccf8148fb84e07c0a14ce544`.
The standalone [patch](native-c1-capture-only.patch) is a diff from that saved
base, **not** from tool HEAD `f76012fb...`; its SHA-256 is
`4a549366920559f7042e07bb54ad182568b5549c7c4e6dfd518312407b337def`.
`git apply --reverse --check` on the edited worktree passes. No tool was
compiled or run locally; Cloud status and verifier verdict remain **NOT_RUN**.

The new mode parses only `SORT4_NATIVE_OPAQUE_C1_CAPTURE=0/1`; any other value
fails. When on, it requires `SORT4_ACTUAL_AST_SCOPE_TEST=0`,
`SORT4_STRICT_LFT_CUT=1`, C1–C4 capture/bound/discovery modes off, HRTB and
Output equality off, strict relocation off, and all prior controls inactive.
It also rejects skipped specless checks, ignored unwind, zero/multiple runtime
bodies, or a body other than `small_sort_general_with_scratch` **before any
body translation**. The source must be exact SHA-256
`7ebcf7cd435c31b3f4669ac6f31a62fd45fcb2c7fa03500bdfbc44ccaca01742`
at `verified/lib.rs`; source lines 194, 210 and 212 must uniquely contain the
first-unwind marker, exact operand-1/0 C1 call, and `end_lft_binding` cut.

In that one native body, the parser must find exactly one `'cmp` cut at line
212 and exactly one parsed `__vf_sort4_first_unwind` marker. It leaves the
regular `end_lft_binding` ghost statement in the original stream: no new
strict-cut relocation, Noop replacement, execution or call-edge rewrite.
After the full original declaration is built, it requires exactly one
MIR-derived `FnMut::call_mut` switch with source line 210, writes
`native-c1-capture-pre-ast.ml` only if that path does not exist, checks that
serialization did not mutate the declaration, and always raises
`NATIVE-OPAQUE-C1-CAPTURE: FULL_ORIGINAL_AST_CAPTURED_NOT_PROOF`. The captured
declaration retains its generated native contract, original normal/unwind
control flow and local declaration list; the fresh Cloud artifact must be
inspected for actual contents. It cannot reach helper/target verification or
summary export through this mode.

The diff adds this opt-in path and leaves all existing C4 exact-one/source/AST
gates and target rewrites in place. With the opt-in absent or `0`, the new
source SHA and capture branches are inactive. The only new trusted behavior is
diagnostic routing to a full declaration dump followed by refusal. It does
not bind the callback lifetime, register HRTB Output equality, alter a native
alias, or accept proof. A malformed environment, source mutation, extra body,
missing marker/cut/call, or unexpected source location is an admission
failure, not a semantic negative. A fresh Cloud build is required to test
compilation, exact marker counting, AST serialization and the expected refusal;
until then every capture claim remains **DRAFT / NOT_RUN**.
