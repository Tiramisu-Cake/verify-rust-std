# R11 S3 integration review

## Decision

**GO for the bounded S3 Cloud test after the final profile pins are frozen.** The parser-shaped helper gate, active-tool receipt binding and comparison-only P1 alpha checks are now coherent. This is authorization for the experiment, not proof credit: the helper must pass in the same Build, then the caller and full 26-case matrix must satisfy their existing admission checks.

## Checked-helper gate

The fixture constructs one exact ghost block and records its inclusive source
and body intervals. The backend requires both the certificate metadata and
profile SHA pin, checks the block bytes and uniqueness in `verified/lib.rs`,
then runs a fresh `-focus` stage at the certified helper-body line. It checks
the final VeriFast binary against the tool receipt before and after the stage,
and binds the record to the Build ID, profile hash, source certificate,
verified/original source pair, command, output log and AST artifact. The runner
rechecks these identities and reselects the AST from current source and AST
bytes before it classifies caller output.

The pinned Rust parser constructs ghost `Func` rows with a point location at
the declaration name and stores the body closing-brace location separately
(`rust_parser.ml:751–777`). The helper selector now binds that exact name token
location and closing token to the certified lines, derives the effective
header-through-close interval, and rejects overlapping or duplicate
definitions. It requires exactly one same-name definition of AST kind
`Lemma(false, None)`; bare/regular, auto, triggered, malformed, duplicate,
wrong-path or wrong-location rows fail closed. The ordinary focused-body
selector also uses effective intervals for manual ghost lemma wrappers when
counting overlaps, skips unrelated source files, and still requires the
selected runtime function's raw `Func` span and close location to match the
compiler-bound `Body.span` exactly.

The backend blocks callers on failed or missing paired support, helper error,
missing AST, source/tool change, invalid metadata, or exhausted deadline; it
records zero proof credit. The explicit post-helper deadline check also leaves
caller verification unattempted when the remaining window is too short. The
helper stage is run independently for each caller case, so the gate does not
carry proof state across cases or Builds. The runner now binds the receipt's
resolved console path and binary SHA to the active selected tool path and
`tool_receipt`, and checks the helper stage argv/cwd against that active path.
Path-substitution and wrong-receipt cases fail closed.

The active profile helper pin matches the constructed block at
`cfae805f5c317e3e1d7180bd88e863c5b5f84a27fc10867dd2b762709e8bccaa`; the
helper-file, source-runner and R11-entry pins currently match their files.
Recompute/freeze this set after any further source edits and carry the exact
profile identity into the Build.

## P1 parameter-name adjustment

The source and R-only AST show the trait prototype and Freeze impl use
`scratch`, while the blanket impl intentionally uses `_scratch`. The
comparison-only parameter projection changes only this second binding label.
The common-vs-impl native comparison also alpha-renames only the bound
`Var(scratch/_scratch)` nodes and the recognized generated `_v0_`/`_v1_` fold
binders paired with both a `VarPat` and a `Var`; resource names, types, regions,
unrelated strings, and other native terms remain exact. Unknown fold indices,
missing pattern/use pairs, and resource/type/region changes are rejected. Raw
headers and native trees remain stored, and each candidate impl must still
equal the exact R-only original header and native tree for that compiler-bound
body before common-vs-impl projection. Parameter order, types,
lifetimes/regions, source spans, numeric item identity, native
preconditions/posts, body multiplicity and the mathematical criterion remain
checked. Parser-input binding and failure causality remain unestablished.

## Evidence boundary

The isolated helper-gate tests (14) and AST-gate tests (38) pass, as does
`git diff --check`. These synthetic tests exercise source/AST gate behavior;
they do not prove the real helper body. The focused helper stage must succeed
in the same Build before caller verification proceeds. Retain all 26 case
receipts and existing caller admission rules. A helper-stage success is only a
prerequisite receipt, not a Rust callsite/MIR binding or caller proof result.

The proposed timing is reasonable for a bounded first test: 1,200 seconds
total, 960 seconds work allowance, 900-second soft work target, and 240 seconds
for report/packaging. The prior S2 execution was 424.487 seconds; adding both
fresh helper-stage caps of 180 seconds gives an estimated 784.487 seconds,
below the soft target, but this remains an estimate rather than a guarantee.
The 1,260-second envelope stays under the existing 1,200-second build cap plus
the 60-second queue/envelope reserve. The stated 2,558-second remaining budget
can cover this and a subsequent 1,260-second full-matrix reserve with 38
seconds left; keep actual accounting and do not reduce existing reserves. A
timeout or partial matrix remains incomplete, not accepted.
