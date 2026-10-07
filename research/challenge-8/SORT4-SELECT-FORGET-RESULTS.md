# S7 exact local-guard forget — diagnostic closeout

**STOP: independent acceptance is blocked by the frozen global dead-code gate.**
`forget` is NOT ACCEPTED and actual redirect is NOT IMPLEMENTED. The body route
produced nonvacuous local evidence, but neither positive is a successful complete
verification. Full S7 source/MIR mutation controls, borrow-token matrix and new-profile
regressions are NOT RUN. Existing S6v4 components/classifications remain unchanged.
[Design and BEFORE cards](SORT4-SELECT-FORGET-DESIGN.md).

Latest [run37669436220](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37669436220),
proof/diagnostic source `a5ce1b5f71d2f0a2ecd1f74e44063ba079683b4d`.
Same `experimental-source-linked-select-pointer-drop-v4`, patch
`c7cc08a995bac5879901f4fe08030f09d23bdfefb1a3ab5893be12a8dd1f8fc1`.
All admission environment flags inactive; no new semantic profile or call summary.
Actual std runtime, signatures and target contract unchanged. All executable work
was GitHub-hosted, one relevant run at a time; no local compilation/verification.

## Body hypothesis and trust boundary

Pinned core::mem::forget body is `{ let _ = ManuallyDrop::new(t); }` at
mem/mod.rs162–164, file SHA256
`1db195d24508e4eef81163672d008667765c2c121f4fa70f8752742e11106273`.
Checked unsafe adapter takes exact nominal `DropOnPanic<*const Element>` and
requires only `thread_token(?tid) &*& tid == currentThread`; normal post returns
same token, unwind post false. A positive probe constructs the same guard from
an existing initialized `*cell |-> value`, calls the adapter while framing that
cell and independent `*frame |-> flag`, and returns all three resources.
No guard-own=true, no Element ownership and no permission to drop an inaccessible
slot is introduced. Wrapper/borrow tokens outside guard were part of the proposed
full acceptance, but those specific controls are NOT RUN; cell/frame evidence
must not be generalized to them.

Existing pinned translator maps ManuallyDrop<T> to T and new(arg) to arg. Its
representation, destructor suppression and operation/no-unwind correspondence
are TRUSTED existing semantics, not established by this body experiment. SAFE
compatibility with false nominal own is vacuous and supplies no body theorem.
The reachable explicit unsafe precondition, actual body execution, return/leak
and false-assert countercheck give local nonvacuous evidence separately. Complete
proof acceptance and correspondence from real safe mem::forget to this unsafe
adapter are still absent. The real guard Drop remains unchanged and unproved
here; no arbitrary-slot destruction right follows from pointer bits.

## Captured source, annotations and full typed MIR

A source-only macro module supplies helper/probe declarations at the actual guard
scope; sole macro argument is its original `DropOnPanic` identifier. Runtime body
of the adapter is exactly forget's body, without changing ManuallyDrop spelling.
Both insertion sites and all four original/verified files pass ghost-strip,
hosted preflight/regeneration and before/after stage SHA checks. NORMAL/readonly
export/decode and readonly refinement PASS independently in all nine variants.
This is diagnostic source integrity, not a completed source/MIR admission gate.

Positive macro file coordinates (columns in Cap'n Proto are zero-based):

| Annotation/item | Exact source coordinates |
| --- | --- |
| Helper declaration/body | forget-items.rs3, body14–16 |
| Helper req / ens / unwind | blocks5–7 / 8–10 / 11–13; statements6 / 9 / 12 |
| Exact ManuallyDrop::new | forget-items.rs15 |
| Probe declaration/body | forget-items.rs17, body28–31 |
| Probe req / ens / unwind | blocks19–21 / 22–24 / 25–27; statements20 / 23 / 26 |
| Guard construction / checked call | forget-items.rs29 / 30 |

NORMAL and readonly decoded **complete body records**, from `defPath` through
`loopSpecBlocks = [] )`, are byte-identical for the positive helper and probe:
helper SHA `1b8cc3db49014ec955cd646b0cca6a39e72ddaba21e32f6191d8faa53dfb21d5`,
probe SHA `173ad123bc3434130db228b7a8fedbe493a375f290758dced68e1dd1894a0e61`.
Helper has4locals/3blocks; probe7locals/3blocks; both `isFromExpansion=true`.
No global expansion allowance was added to v4. Actual parent still has36/19 NORMAL
versus31/14 readonly, corresponding to the existing five stock projection ghosts;
macro/module declaration does not create a runtime call in the actual body.
Full S7 parent/source/expansion mutation admission remains NOT RUN.

Helper NORMAL-MIR artifact coordinates: defPath5535, nominal ADT5621,
ManuallyDrop callee5876, cleanup edge5921. Name is
`select_unpredictable::checked_forget_guard`, not a same-shaped external guard.
Parameter/temporary ADT is exactly `select_unpredictable::DropOnPanic` with
substitution `*const Element`. Locals: _0 unit result, _1 input guard, _2
ManuallyDrop<exactguard>, _3 moved guard. BB0 has storage operations, Move _1→_3,
sole typed `std::mem::ManuallyDrop::<T>::new<exactguard>` call with Move _3→_2;
normal BB1 kills temporary storage, assigns unit and returns; cleanup BB2 resumes
unwind. There is NO Drop terminator in helper. Retained cleanup is NOT evidence
that unwind is impossible; the existing identity lowering is the trust boundary.
Actual parent runtime drop/forget and guard-cleanup edges remain in captured MIR.

## Independent nine-case evidence, without classifier rewrite

Every original automatic classification is **INCONCLUSIVE**. Positives have no
proof error and execute to return/leak but exit1 on mandatory dead-code reporting.
Seven negatives reach their exact intended first-error obligation. Their classifier
also counts the repeated `note: Verifying function` as a second header, so does
not accept them. No classifier correction/replay or semantic change was mixed
into this result; raw classifications and all logs retained. Below are raw
observations, not an accepted full matrix.

| Case | First causal outcome in verified/forget-items.rs |
| --- | --- |
| helper_positive | body/return/leak, then global dead-code exit1 |
| frame_positive | guard construction/call/frame post/return/leak, then global dead-code exit1 |
| false_assert | line16: Cannot prove false |
| wrong_post | ens9: Cannot prove false |
| thread_loss | return16: Function leaks heap chunks: thread_token(tid) |
| thread_duplication | ens9: No matching heap chunks: thread_token(tid) |
| frame_loss | return31: Function leaks heap chunks: points_to<bool>(frame, flag) |
| frame_duplication | ens23: No matching heap chunks: points_to<bool>(frame, flag) |
| frame_wrong_value | ens23: Cannot prove false == true |

## Precise next blocker and actual result

Frozen console `src/vfconsole/vfconsole.ml265–282` registers statements globally
and exits1 if any remain unexecuted. `verify_expr.ml154–162` focus only selects
function/prototype execution; it does not restrict that global inventory.
Helper-positive log1–16 executes body/return/leak; log17 first dead-code entry is
`verified/forget-items.rs(3,1-16,2)`, followed by skipped sibling/actual parent
`verified/lib.rs(10,1-74,2)` and prelude obligations. Probe-positive log1–22 likewise
reaches return/leak, then fails the same gate. No missing guard-own resource was
established in these checked bodies.

Independent exact-nominal positive acceptance with this isolation is therefore
unavailable at the frozen profile. `-allow_dead_code`, scoped suppressions,
dropping unrelated bodies or changing global callback/focus semantics would
weaken/change the required gate; none was done. Nonfocused actual redirect to
make the parent live before standalone acceptance would reverse the required
callee-before-caller order. A separate design resolving independent acceptance
while preserving global reachability/source/nominal gates is needed before any
new admission; this closeout does not authorize a general frontend/guard model.

Actual integration was NOT rerun in S7. Last admitted S6 prefix, run37656621026,
still passes actual pointer drop60 and closes61/62 and stops at forget63:
std/lib.rsspec420 requires `<DropOnPanic<*const Element>>.own(t, guard)`, absent.
S7 has not bypassed/discharged it. No next actual assume_init obligation has been
reached, and no whole helper branch/return/unwind/sort4 theorem is claimed.

## Evidence and continuing budget

| Run | Source SHA | Job seconds | Used / remaining |
| --- | --- | ---: | ---: |
| Entry ffa370a | S6 proof75681fbc | — | 3954 / 1446 |
| [37665233357](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37665233357) | 2ba63774e964e2ca76b3b1639e550cb93e70769e | 133 | 4087 / 1313 |
| [37666273705](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37666273705) | 3a4b0e9d375e8871b541ed18e6b340cf152734be | 122 | 4209 / 1191 |
| [37667942855](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37667942855) | f101203bfe5e6100ee2ae60fc0cae62ef7c6149b | 99 | 4308 / 1092 |
| [37669436220](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37669436220) | a5ce1b5f71d2f0a2ecd1f74e44063ba079683b4d | 103 | **4411 / 989** |

Same5400 summed hosted jobseconds, no reset. Latest18:46:51–18:48:34UTC.
No active run. S7 spent457s including setup/build/packaging; first9 construction
failures, next9 compiler failures and third9 incomplete_include failures remain
historical evidence, never intended proof negatives.

Latest compact artifact11503963988/full11503793868; inner archive SHA256
`12c3f3f509fc845dd1aa1bb7d8b80f8fcf70e6ab6064af3436168f0b9489dd83`,
manifest1135/1135 SHA/CRC/size PASS. Prior compact11503762679/full11502754044:
inner `a3e1ce82a09bca102434d5c266fd5602f7ff673e06f74824a73dc809e98807dd`,
1099/1099 PASS. Earlier identifiers/hashes in EXPERIMENT-LOG retained.
Green Actions badges mean diagnostic collection completed, not proof acceptance.
