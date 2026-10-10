# Exact native C1 pre-AST capture — diagnostic translator delta

Before implementation,20:24UTC. Independent design review by
/root/explorer_opaque_native confirmed a separate exact native opt-in can
capture the fresh MIR-derived original declaration without changing old sort4
admission gates. This is NOT a new kernel/lifetime rule or a bound proof.

Fresh d77612a5 /86e38e3a native candidate reaches the strict lifetime declaration
at172:1–30 and refuses unresolved inference in entry outer type. Normal/readonly
full MIR and refinement pass. The ordinary AST diagnostic separately fails
Ocaml_expr_of_ast.of_body_ss with TODO, so no pre-AST artifact is obtained.
Expected issue: callback local declarations remain outer; no cause is assumed
until fresh capture identifies exact unresolved types and allocation inventory.

Only new opt-in SORT4_NATIVE_OPAQUE_C1_CAPTURE=1 is permitted for exact source
SHA7ebcf7cd435c31b3f4669ac6f31a62fd45fcb2c7fa03500bdfbc44ccaca01742,
body small_sort_general_with_scratch, exact-one runtime body, full checks and
unwind. Mutually exclusive with all old actual-sort4 capture/bound flags and
AST_SCOPE=0, strict cut=1. Old exact-one/source/preAST gates remain untouched.
Reject malformed opt-ins, wrong source, extra body, skip_specless or ignored
unwind. Require one named cmp cut, one first-unwind marker and one compiler
FnMut call with expected operand1/0/source location from pinned source/MIR.

Capture path leaves end_lft_binding as its original regular source ghost
command, as old sort4 capture does; it neither executes nor replaces the cut
with Noop. After full original declaration construction, emit native preAST
and ALWAYS refuse before helper/target proof or summary export. Preserve source
normal and unwind returns, original native automatic header/post and every
allocation/free declaration. HRTB/bound projection remains absent. This exact
capture provides no target theorem, escape exemption or proof credit.

Fresh Cloud must compile this isolated translator delta, retain paired MIR and
refinement and dump full original preAST followed by the exact capture-only
refusal. Positive capture means artifact+refusal, never VF0. Existing unbound
refusal is already fresh and must not be rerun without a new purpose. No general
VF, alias, checked arithmetic, strict-cut draft or selector patch is included.
