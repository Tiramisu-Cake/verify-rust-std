# Replace: historical five failures versus current two

Exact base3b382c812a, owner-supplied run43630584079, reports N=2/250 FAILED,
only ptr::read::<u8> safety_check.1 (*const u8) and .4 (u8), Unsupported empty.
Both original covers are SATISFIED. The caller payload assertion is SUCCESS;
requires `!initialized || payload_is_42(&value)` is SUCCESS. Generated bool/&bool
initialization checks are present and SUCCESS, not deleted or waived.
INPUTS/ORACLE-MAP pin the supplied files and argv; new portable fixtures remain NOT_RUN.

The older `mode-findings/FINDINGS.md` describes five failures on the earlier tool:
these same two payload reads, two bool/&bool capture initialization failures and a
nonzero closure-layout Unsupported. It is not current-base evidence. Current source
explains the changed classes without inventing a new runtime observation:

- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs`,
  TargetFinder::find_all, entry ordinary argument-slot SetRef: valid ordinary sized
  non-union arguments initialize their own data bytes. Pointer/reference slots do not
  imply initializing their referents; MU/union keeps its transfer rules. Assignment
  handling in the same visitor tracks initialized ordinary slots/copies. This is the
  source mechanism addressing valid bool/reference/capture slots that formerly lacked
  initialization shadow. The new report confirms these checks succeed.
- `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs`, data_bytes_for_ty,
  RigidTy::Closure arm: nonzero environments now obtain actual monomorphized upvar types
  and field offsets from their closure layout. The old blanket nonzero-closure refusal
  described in FINDINGS no longer applies to this capture. This matches no Unsupported
  in the current run; it is not a general claim that every closure layout is supported.
- `library/kani_macros/src/sysroot/contracts/replace.rs` produces an `any_modifies`
  return before `kani::assume` of ensures. `library/kani_core/src/arbitrary.rs`
  Arbitrary for MaybeUninit permits uninitialized payload storage. With initialized=true,
  the unsafe predicate reads that havoc result while evaluating the assumption; the
  contract's legal concrete identity implementation does not ensure the predicate is
  total over the havoc domain. The two read instrumentation failures therefore remain
  a bounded regression observation; no general Replace mode qualification follows.

These are reviewed source mechanisms consistent with the supplied observations.
No per-instruction dynamic trace or independent causal source→GOTO proof is asserted,
and no compiler/runtime change is made in S5. F7 restoration is unchanged; the old
five is not attributed to S4 cache isolation by conjecture.
