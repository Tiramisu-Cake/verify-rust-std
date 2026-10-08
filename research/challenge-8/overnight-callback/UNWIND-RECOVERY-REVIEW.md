# Callback unwind recovery component: pre-hosted review

The preceding [design boundary](UNWIND-RECOVERY-DESIGN.md) recorded the O13
problem, semantics, trust boundary and controls before this draft. This note
reviews `verifast-callback-unwind-26.10.patch` and the two source-only callback
markers. They have **not** been compiled or verified. The patch is separate
from the seven active O13 components and applies after H2a. Its SHA-256 is
`6df78294595d9e9001bc66cec85d9ddd98f4fd679534d7807b2ca08f7c97231a`.
Static `git apply --check` passes on a disposable pinned f76012fb checkout
after these exact patches in workflow order:

| Component | SHA-256 |
| --- | --- |
| S6 | `20f7d07ac9bdaca7c46f737b89925dfac3f4cef66c3f5d48aa9634ac949dbc1c` |
| CFG | `593d09405379974ffbc475c2e0b65d648d8a6913f55b765dd0c3bebdc0922781` |
| A1 assert | `b3fdae6588c5d88a5151f9b103b2f5ab6d2d58db880955a1b975a7f88ca2feb9` |
| A1 pointer transmute | `44b460e64eede02bb7776ef36c6be12eb2bed2e5a4fd37ad9b733c7b5633c8ab` |
| Tuple 2 own | `84b58b71bfb65ac2bfac1a63d181239001cf0a7ffba3f8bfb5d5b0f1d3a640da` |
| A1 linkage | `40fb77888c9b907f150d32f9d85769512cad9c57bb0b14f9c9dbd593fc44c0e7` |
| H2a | `cc29a1855d9d129d07e61a759bb7163b65f5b6e6285d62e883207c9a9e73fe00` |

## Actual obligation and target

The O13 `callback_positive` body passes real `FnMut::call_mut` and then fails
the unchanged full unwind post at `points_to<T>(left, _)`. The source creates
two real shared references to separated initialized T slots and packages
their reference ownership into stock FnMut `Args.own`. The call may mutate
interior state and panic; its stock unwind post returns the current F
storage/own and thread, while the source-cell borrow debt stays framed.

Domain: unrestricted sized T and `F: FnMut(&T, &T) -> bool`, two separated
initialized cells each with one `T.own`, F storage/own, `thread_token` equal
to `currentThread`, and type interpretations. Normal and unwind posts each
return both full initialized cells with their *current* `T.own`, current F
storage/own, thread, and type interpretations. No comparator purity, `Freeze`,
`Copy`, unchanged-value, nonpanic or ordering premise is added. The false
normal-post control retains its extra `false`; a separate false unwind-post
control is required for acceptance.

## Proposed semantics and trust

One explicit inert Rust ghost comment, placed immediately before the source
call, contains a parser-visible `__vf_callback_unwind_pair()` marker and two
source-written ghost statements in separate nested blocks. The first closes
the exact existing `comparison_debt<T>` from the two reference-initialization
fractions, close tokens and borrow-end tokens. The second calls the same
checked ordinary `recover_pair<T>(left,right)` used on normal return. The
translator consumes the marker's ghost command as a no-op; it does not execute
the two steps on the normal path. It requires the next real call to be the
two-argument `std::ops::FnMut::call_mut` with equal shared-reference T and
lifetime types, a normal successor, a direct `Continue` unwind, and the call
span beginning on the line after the marker. Only bodies named
`callback_positive` or `callback_false_post` may use this component, and each
must have exactly one marker. Malformed, missing and unmatched markers fail
translation for those fixtures. Other bodies retain stock behavior.

On the marked unwind branch, the translator emits the checked debt close and
a synthetic `GotoStmt` to a label appended outside the reconstructed Rust
block. The verifier's stock block-exit continuation restores the half
`lifetime_token` reserved by `let_lft`; at the outer label the checked
`recover_pair` can close fractions, end the lifetime, consume both borrow-end
tokens and open the current full-borrow contents. The branch then executes the
same `ReturnStmt(unwinding())` as stock. Normal call successor, all other
unwind actions, actual Rust effects and postconditions remain unchanged.

The new trusted premise is source annotation/MIR call and scope correspondence
in this narrowly marked frontend lowering. The checked `recover_pair` body
and stock lifetime/alias predicates are not changed. No kernel, FnMut spec,
memory/alias/prelude, exporter, decoder, refiner, leak/dead-code or validity
check is changed. This remains an experimental semantic component until
hosted source/MIR/AST/proof and negative gates pass; it establishes no actual
sort4 theorem by itself. The application chain and effective source diff
must be hash-certified, with pinned VF f76012fb, std cd371e03 and
nightly-2026-09-25.

## Hosted gates and outcome decisions

Positive: run `callback_positive` and its checked `recover_pair` with the
unchanged complete normal/unwind posts; require named body, both post edges,
return/leak/dead-code and full VF exit0. Inspect AST/proof trace for unwind
debt close, scope exit, checked recovery, then original unwinding return. Run
the unchanged `callback_false_post`; it must fail only at its false normal
post after unwind succeeds. Add false unwind post and F-owner-loss negatives;
they must fail at those exact posts. No setup/frontend failure counts.

Resource negatives, each isolated: omit one reference-init fraction, one
close-fraction token, one borrow-end token or the reserved half lifetime
token; each must fail at the matched debt close or `recover_pair` precondition.
An intentionally swapped/wrong slot cannot silently restore the other cell.
Admission negatives: missing/duplicate/malformed marker, moved marker, changed
callee, wrong tuple type/lifetime, missing normal successor and non-Continue
unwind must reject before proof. A marker in any other function also rejects
before proof. An unmarked ordinary panicking call and a
shared cleanup/Drop call must keep their original unwind AST and complete
proof. Every case needs fresh NORMAL/readonly MIR export/decode, source/ghost
strip identity, refinement, exact tool/profile hashes and full logs.

If a positive fails because `goto` does not restore the reserved lifetime
fraction or the synthetic label bypasses a real cleanup/Drop, stop this
candidate and return to architecture review. If the marker fails to parse,
repair only the precise frontend syntax while retaining the semantics. A
later resource failure can justify a source-written proof correction only
after its exact missing chunk is observed. A green partial debt post is not
the full target. Do not extend this candidate to actual sort4 calls without
independent per-call resource and real-cleanup applicability evidence.

An opt-in `probe.py --unwind-matrix` adds isolated missing, duplicate, moved
and foreign marker admission cases, plus false unwind, duplicate F owner and
duplicate left T owner post cases. Each uses the same real generic callback
body unless the admission mutation deliberately changes only its name or
ghost marker placement. The default probe still runs just the original
positive and false normal-post cases. The matrix records source pairs,
NORMAL/readonly MIR and alias audit, full VF and refinement; its classifiers
require the intended admission message or exact unwind-post line. Duplicate
owner cases remain review candidates until their full trace is inspected.
Missing fraction, close token, borrow-end token, half lifetime and altered
cleanup controls are specified above but **not yet generated**; they need the
first hosted positive/negative trace to choose a precise mutation that reaches
the intended obligation. Existing S6 ordinary panic/shared cleanup controls
can serve as unchanged-profile regression evidence only after a fresh run on
the combined profile. No two-case or partial matrix result is acceptance.

## Static self-review

The patch alters only `vf_mir_translator.ml`. Its special path is limited to
the two named fixture bodies, requires exactly one marker in each, and rejects
a marker whose decoded next call is not the required FnMut/Continue shape.
The existing runner's `callback_mir_alias_audit` independently checks both
decoded NORMAL and readonly MIR before full VF: it follows the actual ordered
FnMut tuple fields through two reference borrows to source `left`/`right`
parameters. This audit remains an external acceptance condition, not a
translator theorem. The patch does not synthesize `T.own`,
`F.own`, a reference or a lifetime token: the only injected operations are
the source-written close, the checked existing recovery call, a goto and the
original unwind return. The critical unproven fact is that the goto crosses
the reconstructed `let_lft` scope exactly as intended while preserving all
real unwind effects. The hosted trace and shared-cleanup negative must decide
that; static review is not acceptance.
