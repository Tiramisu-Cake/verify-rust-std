# Review and validation

Final source `88c532d6c19d3647ea877af6222078d760c06900`, tree `57fbba832389b448229aefa9365ad00ab68657fe`.
Independent reviewer `/root/boundary_review`: GPT-6 Luna HIGH, no nested delegation.
Static-only, no compiler/verifier/CI. No proof or compile success is established.

- Initial compiler/fixtures candidate `30655f3060f33603d94e32f39951462434447ed0`:
  reviewer returned no concrete findings. Exact packet/spec and receipt in
  REVIEW-INITIAL.md and review-packet/.
- Compiler delta `a221d00cf66b723c66a5a3a928d2ab1e29e8df44`:
  actual nested args/destination now diagnosed even if resolution fails; new
  expectations additionally require the nested-slot reason. Reviewer returned
  no findings. Spec SHA256 c7626a3d6a1e3d82ed617cf41b4095057bad54c50d86755ccb9df2bb820171a5;
  packet SHA256 6f4fea47aecf9845bbd88f4925a17aa2f51cca49f3b85a10d30ed15783eded4f.
- Main's source audit found the newly introduced positive raw aggregate read
  expectation overclaimed existing support: raw Deref emits Check(Packet), whose
  pointee mask still fails UnionAsField. Final test-only delta `88c532d6c19d3647ea877af6222078d760c06900` separates
  pointer-value admission from that existing layout Unsupported. Reference read42
  remains; the raw read remains as a distinct known-Unsupported control. The same
  reviewer checked this delta and returned no findings. This does not modify any
  pre-existing control or compiler semantics after the reviewed compiler delta.

Manual Rust-type audit: visitor traversal uses public Ty/instantiated ADT fields;
closure upvars use the same internal/stable conversion pattern as ty_layout.
Actual call operands use Operand::ty; destination/local0 use Place/local Ty;
selected FnSig inputs/output are independently validated. Classification computes
no sizes/offsets and introduces no layout unwrap or cast. Refs/raw pointers stop,
all enum variants and ZST/zero-array element types are inspected conservatively.
Worklist plus HashSet terminates repeated type visits. Existing flat protocol,
normal-edge return LoadArgument, snapshot-all before Move-source deinit and
source lifetime ordering remain unchanged.

Custom MIR has source/returned: MU<u8>, saved pointer: *mut MU<u8>, observed: u8,
observed_out: *mut u8, RET: MU<u8>. The raw scalar store is type-correct; saved
source is repaired to23 before source-read on the legal edge; actual relay return42
is returned and consumed. No-repair edge still reads moved-from source. Original
legal tuple-return source/expectation are archived unchanged with SHA256 in INPUTS.

Scratchpad rustfmt --check (compiler edition2024, fixtures edition2021): PASS.
Source git diff --check base..final: PASS. Python Git mode/blob audit: 363 protected
entries unchanged; all pre-existing paths unchanged except the three allowed
source/doc/fixture files. Existing move-return expected remains byte-identical.
All 17 new selectors and both supported Move roots: compile/proof NOT_RUN.
Existing controls are unchanged, but exact new diagnostics (especially RustCall
synthetic tuple signatures/closure captures) still require coordinator review;
no broad rejection of legal contracts or golden refresh is accepted by this review.
