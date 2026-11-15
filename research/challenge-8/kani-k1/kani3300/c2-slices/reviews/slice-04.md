# Slice04 STORAGE/protocol+F6 — worker15 review

**PASS_STATIC_ONLY; READY_FOR_COORDINATOR_CI.** No blocking finding in the slice04 hunks.
Native compilation, formatting, clippy, units and verification remain NOT_RUN. This is correctness review, with no formal proof credit.

Source `345cedfd67df679e326474385308349d609fc43d`, tree
`e13784fc67ec6bb1b15f30dc851ef7460738e3eb`, exact parent accepted03
`5ca51679e3f433718807a2e44add0d5abac128e7` (run43706759714).
Input g0 `7655cf9542`; reference F `ad499e41dd2db9ccd432f89721638a1f3a0bbd44`.
Read-only candidate review: no worker14 source/package changes. Worker15 writes only reviews/ and ci/.

Review covered the204 changed paths: eight production files, two docs,95 new complete fixture pairs
and four inherited entry-source updates, with existing goldens unchanged. Independent read-only
composition of owners1..4 and accepted parent reconstruction matched Git objects; all180 owner4
part hashes matched the canonical map. Six production files equal F; layout retains the pre5 Closure
fallback, and delayed/mod retains the explicitly mapped pre-F7 writer/import. Earlier parts stay
accounted for by the composition. No SEL1, R7/R8, F7 production, dependency/pin or stock-workflow
change was imported into the candidate. Docs describe current storage and F6 limitations without
claiming captured-closure or nested aggregate transfer support.

Pairing is atomic across producer/consumer/runtime/signature:

- The same `has_transfer_protocol` predicate gates caller, callee entry and Return: Item, nonforeign,
  body present; the typed-marker exclusion is exactly `KaniFunction::Hook(_)`. Unknown markers and
  Model/Intrinsic categories are not promoted to Hook. Nonpaired shadow values are refused before
  begin/snapshot/deinit; ordinary scalar Hook controls remain usable.
- Caller Begin and all StoreArgument snapshots precede every actual Move reset. Copy sources stay
  live and unchanged. Caller/callee use the same `instance.ty()` interned signature, original1-based
  argument indices and the count of shadow-bearing arguments. Return store0 and caller load0 are
  mandatory on the normal edge; abort/unwind does not consume a normal-return pair.
- Runtime Begin/Store/Load enforce active/signature/count/order/remaining and return0; missing protocol
  is not initialized fallback. A witness snapshots its Boolean while live and preserves false through
  the typed mask. Demonic unselected paths do not replace the selected false-witness obligation.
  Buffer fields remain in marked verifier-private MEM_INIT_STATE for DFCC.
- Constant `None` bytes remain false; SetStorage intersects the actual constant mask with the typed
  data mask. Raw copies preserve whole byte extents; typed copies/loads retain payload bytes and
  discard padding at the real array/slice stride. Storage assignment/transmute guards retain source
  reads and reject unsupported shapes rather than admitting broad aggregates.
- F6 resets only actual moved source places before calls and destination storage after normal return,
  including padding via `for_deinit`. Copy is preserved. The same helper covers BlackBox and ordinary
  calls. Both distinguishing negatives and the reinitialization companion are exact F fixtures;
  conservative nested false positives stay documented, not relabeled as UB.

Independent compile-seam recheck: [SEAM-VALIDATION](../ci/slice-04/SEAM-VALIDATION.json)
re-executed the reusable checker on exact parent/candidate/F objects:107 changed Rust files,
repository-wide generic checks for both changed context types, all44 explicit call contracts,
`errors=[]`. Ten checker synthetic tests passed. Manual binding review covered both7-argument
UninitInstrumenter::run callers; visitor TyCtxt lifetime/constructor/impl/imports; MemoryInitOp
producers, exhaustive helpers and dispatch; CheckRefAs address/cast; constant mask visibility;
argument_size before address/model materialization; marker lookup/SKIPPED_ITEMS and runtime macro.
Begin `(signature,count)`2, Store `(ptr,index,signature)`3, Load `(ptr,index,signature,count,mask)`5,
and typed Copy `(from,to,mask)`3 agree with builder argument order and `<LAYOUT_SIZE,T>` resolution.
Token matching does not establish Rust name/type/borrow/trait resolution or macro expansion: native
build and clippy remain required.

All99 fixture pairs were separately reviewed for premature closure5 dependencies by worker15 and
an independent Luna HIGH read-only helper. [FIXTURE-REVIEW](../ci/slice-04/FIXTURE-REVIEW.json)
records every path and source-list hash. Exactly seven changed files contain closure expressions:
one pairing-unsupported, four item-return and two tuple-MU controls. They capture no upvars and have
no requires/ensures/modifies attributes. Closure values are not shadow carriers; assignment and
nested-reset guards react specifically to UnionAsField, while baseline Closure produces
UnsupportedType; delayed entry requires Ok(Sized). Thus these closure locals do not require a mask.
The four Item bodies transfer the MU return through stage4; shim/tuple controls retain their intended
conservative refusal. No added fixture was found to require closure layout5. Unexpected native
Closure/layout Unsupported remains STOP, never a reason to weaken the golden. The helper's prose
miscounted its seven enumerated paths as six; worker15 independently recounted seven.

All47 mapped head5 fixture pairs are absent, including all eight strong S5 oracle fixtures.
Sensitivity mutations4/4 with --force-rerun are therefore **DEFERRED TO5**, not executed or credited
on4. The request preserves this explicit disposition.

Nonblocking metadata correction: slice04 TEST-MANIFEST scalar `unit_expected_count:18` is inherited
from03 and omits the two new unit filters. The CI-only inputs/request explicitly require20 units:
ActiveCalls9 + immutable9 + argument_size1 + marker_category1, with exact native names and nonzero
counts. The embedded fixture manifest remains byte-identical to worker14's package. Canonical
QUICK-PLAN discovery counts predate the slice03 fixture reassignment; exact cumulative manifest
now has413 selectors, including every154 present expected/uninit input. No test is dropped to fit an
old count. [SOURCE-VALIDATION](../ci/slice-04/SOURCE-VALIDATION.json) verifies803 manifest identities,
all inherited selections,95 additions and only the four authorized source identity replacements.

CI-only overlay `4f00e47d81da1e8849551e748ed378edbf868be1` has exact candidate parent and changes
only .github/. Accepted03 runner execution/output/source-guard logic is preserved; the only runner
delta adds two unit commands and exact-name expectations.21 isolated synthetic runner checks pass,
including success, original failure, timeout, launch error, partial/missing/null/wrong-type output,
zero selection, name/count/ignore mismatch, explicit NOT_RUN, source mismatch and new filters.
[CI-REQUEST](../ci/slice-04/CI-REQUEST.md) preserves selectors, flags, original exits and always-upload
artifacts. All source identities are guarded before/after execution.

Owner1 seven head4 obligations, owner3 nine, and18 reassigned pairs remain PENDING until explicit
per-fixture results on this exact cumulative head. Historical slice1/3 receipts are unchanged;
closure-dependent obligations remain on5. No local native tools, push, dispatch or Cloud spend.
