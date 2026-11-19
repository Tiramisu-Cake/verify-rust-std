Recommendation: retain the small code fix and all14 semantic cases; consolidate
the five edge-shape files and shorten the new comments and PR description.
This is a completed offline source review, with no candidate changes or fresh CI.

Reviewed PR https://github.com/model-checking/kani/pull/5176 at published head
`3d9a1809388f74c62ea9fb7320e123db0b8b37fa`, tree
`cf797fd1fd0ebf0ae35d58e06da5624ee00ae1ab`, base/merge base
`0aac16ef62da9e9d5645782d458593e5d78143ba`. The17 changed files match every
pinned Git blob, SHA256 and length; source checkout is clean. Body, patch and
STYLE snapshot hashes also match. Each file/harness/helper/oracle has a named
disposition in COVERAGE-EDITS.md.

1. P2, concrete cleanup: the five `zst-union-edge-*` directories duplicate the
   same imports, source/destination construction, byte initialization, typed
   copy and success/cover oracle, with no differing flags or platform rules.
   Put their concrete types and five existing harnesses into five modules in
   `zst-union-arm/main.rs`. Preserve every existing shape-specific assertion and
   named cover. Remove those ten original source/expected files after the move.
   The bodies remain concrete; a generic copy helper or case-generating macro
   would hide the Rust type/layout under test and is unnecessary.

   Update main's expected oracle from7 to12 successfully verified harnesses,
   zero failures,12 total, and retain all five existing named SATISFIED cover
   blocks there. Do not substitute a bare `VERIFICATION:- SUCCESSFUL` match:
   expected mode uses substring matching and, by default, does not require
   successful process exit. With several harnesses, one success could otherwise
   mask a later failure. The exact complete summary supplies the all-harness
   oracle. This changes packaging, not the semantic coverage count.

2. P2, preserve a real compiler-order control: keep `recursive_arm` and
   `recursive_zst_arm` in separate source files/invocations. They exercise
   incomplete enclosing types reached through pointers, not a typed union copy.
   `ensure_struct`/`ensure_union` insert incomplete symbols before generating
   fields (goto_ctx.rs:304,332). The nonzero recursive Node arm guards the
   unchanged branch; `[Node2;0]` covers zero-sized recursion. Their direct
   inferred pointer casts and black_box calls deliberately keep union types
   reachable through the pointer graph. Do not replace them with a direct union
   initialization, a generic null helper, or a shared generic copy helper.
   Their isolation protects the first-visit setup; there is no flags-based need
   for separate directories. Move them into `zst-union-arm/recursive-arm.rs` and
   `recursive-zst-arm.rs` with same-stem `.expected` files, preserving bodies and
   covers. Each expected file can additionally require its one-success/zero-
   failure/one-total summary. No claim that merging their invocations is safe
   is needed for this cleanup. Native codegen-order confirmation remains a later
   validation item, especially if implementation changes more than their paths.

3. P3, shorten comments that narrate review history or use internal terminology.
   The new typ.rs:1319 comment can say why the representation is needed in four
   or five lines, with rustc layout and incomplete recursive GOTO types explained
   positively. Replace both recursive files' “retain ... root” prose and cover
   labels with descriptions of the pointer/null-value behavior. Replace the
   repeated “including for the nested shapes” comment in five separate files;
   readers of one concrete type do not need a statement about other files.
   Exact replacements are in CODE-COMMENT-EDITS.md. Preserve licenses and all
   unmodified upstream comments, including nearby typ.rs documentation.

4. P2, correct and reduce PR prose. The snapshot says “Each new harness includes
   a kani::cover!” but only seven edge/recursive harnesses contain covers; the
   original seven contain none. Its Testing section has a test inventory,
   platform/rerun narrative and two CI links. Keep two concrete explanatory
   paragraphs, one standard-CI reference, issue5175, the relevant user-facing
   nonzero-width limitation, license and exact AI disclosure. Remove speculative
   workaround-removal advice and stale uninit-checks observations not rechecked
   on this head. PR-EDITS.md supplies proposed text only; it changes no live PR
   or external owner draft. Existing CI/main-vs-fixed statements in the snapshot
   are source-reported claims; this reviewer has not authenticated their logs or
   rerun any native comparison.

No concrete correctness defect was found in the13-line code change. union_size
and padding are measured in bits from rustc layout; within padding>0, equality
means the logical field size is zero. Zero-sized arms get the existing empty
unit struct as the wrapper payload while retaining the original logical arm
type in DatatypeComponent::UnionField. Nonzero arms keep ty.clone(); padding==0
still bypasses the wrapper. The logical type is returned by field lookup, and
the physical padded type is serialized to Irep (cprover_bindings typ.rs:102,124,
154,162,212; to_irep.rs:142). codegen_ty_unit:557 reuses ensure_struct and does
not recursively inspect the unfinished arm type. Static reading supports the
implementation and the recursive controls; it establishes no backend execution
result or model equivalence.

The14 harnesses are not an arbitrary cross-product. The original seven cover
the reproducing typed copy, real payload padding under two union layout policies,
an aligned scalar ZST, offset/prefix preservation, the padding==0 all-ZST path,
and logical array indexing with a nondeterministic valid index. Five edge cases
add field declaration order, nested unit arrays, nested empty byte arrays,
aligned arrays and an aggregate wrapping a zero-width array. The two recursive
tests cover complete-size decisions while types are incomplete. These differences
justify retaining all14 now. The eight-to-three invocation reduction above is
a packaging recommendation supported by discovery/flags, not a harness quota
or a measured performance claim.

The original `array_typed_copy` is the primary regression to preserve verbatim:
byte initialization, ptr::read/ptr::write, logical projection and all-eight-byte
equality remain. On base, the committed PR narrative reports the CBMC bits2expr
invariant abort; fixed expected output requires successful verification. Current
goldens contain no invariant, panic, signal134 or internal-error acceptance.
Keep this stable intended result and never replace the regression with an
expected abort or a mere process-failure check. Later implementation must rerun
the original reproducer against base and candidate plus the standard suites.

Discovery and oracle reasoning are from tools/compiletest/src/main.rs:487
(every .rs recursively becomes a test), runtest.rs:349 (file-local flags and
Kani invocation), :488 (.expected before legacy expected fallback), :528 and
:564 (substring/consecutive-line matching), common.rs:156 (require-success).
No new source has flags, ignores, unstable-mode requirements or cbmc object-bits
settings. Multiple files in one directory are supported: each needs its own
same-stem expected file. Existing nested proof modules are visible in
tests/expected/MemPredicates/thin_ptr_validity.rs, supporting small concrete
modules for the five colliding `Edge` types.

Upstream baselines were inspected, not assumed to replace this regression:
tests/kani/Array/array-zst.rs::check_zero_elems/check_zst_elem/check_zst_enum check
plain arrays/enums; tests/kani/Unit/main.rs::main checks a padded unit union arm;
tests/expected/union/union_transmute.rs::main checks a nonzero smaller arm;
tests/expected/uninit/unions.rs uses -Z uninit-checks with distinct initialized/
uninitialized oracles; tests/expected/valid-value-checks/maybe_uninit.rs has valid-
value mode and a deliberate invalid-value failure. None covers the same default-
mode typed padded-union copy with a zero-width array, logical projection and full
byte comparison. None justifies deleting a new harness or importing its flags.

Remaining genuine gaps: no fresh confirmation of the old abort, fixed native
results, portability, merged test discovery/output, or recursive type traversal;
the nonzero-width payload containing a ZST array remains the documented separate
backend limitation; uninit-checks is outside this default-mode change. These are
later validation/scope items, not grounds for new internal-error goldens or broader
model/compiler redesign. No semantic test removal, ignore widening, assumption
strengthening or check suppression is recommended.
