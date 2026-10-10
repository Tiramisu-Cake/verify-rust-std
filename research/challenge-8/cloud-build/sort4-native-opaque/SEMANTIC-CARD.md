# Native resources and opaque scratch boundary

New user assignment, session start 2026-10-10 19:27:14UTC, main21:27:14,
absolute21:57:14; separate3600sec. Initial clean e5f3f1aec688b944482e6c450b6d12f75ad6fc69,
correct branch and own git-dir/index verified. Policy c7ca8c467aecf10a4b53039372ee97714f854ee3;
existing adoption/ACK preserved. No old account reset or carry.

## Actual transfer map

| Resource / fact | Origin and operation | Status before new Cloud proof |
| --- | --- | --- |
| current thread + thread token | automatic native safe-reference contract | Derived in prior separate native component |
| full source array + foreach T owners | native `&mut [T]`; split at4 transfers actual permission/owners | Prior native component; new split/rejoin interface candidate |
| F cell + F owner | native `&mut F`; callback must return CURRENT comparator | Derived separately; no callback transition credit yet |
| T/F type interpretation | stock produce_type_interp, explicitly disposed | Proved producers, not ownership assumptions |
| full MU storage + foreach MU owners | native scratch `&mut [MaybeUninit<T>]` | Retain opaque through prefix; no open/close or optional-T bridge |
| first four CURRENT source + source tail | checked split/recover lemmas, no snapshots in recover pre | New helper bodies must be proved before use |
| base pointer values | exact slice method implementation casts | New fixed expression component; external method binding absent |
| len >=8 / selected sort4 path | actual earlier caller guard/inline-const selection | External to internal resource component; ghost branch is not actual selection proof |
| positive T size | separate conditional internal boundary | Supplied/excluded ZST, not implied by selected branch (len8,size0) |
| scratch len guard `len+16` | actual checked Rust addition and Assert/panic | Earlier proof refusal; new minimal usize reproducer must retain panic |

Actual C1–C4 do not access destination; the first destination writes are after
C5 at SmallSort647–650. No MU inverse or CURRENT MU owner adapter is necessary
for the resource interface of this prefix. Retaining opaque MU does not prove
scratch binding or the full actual caller, second sort4 call, C5/select/copy.

## Hypothesis / falsifiable cases

On exactly frozen C4 tool f76012fb + existing chain (snapshot retained), the
source-linked fixed pointer expression and native early-return resource
component should pass full automatic posts. New split/CURRENT rejoin helpers
should verify their complete contracts with opaque MU frame; then native safe
wrapper should transfer its real resources to these proved helpers and close
normal/unwind automatic posts/unit return/leak. False post mutant must fail
at native_current_rejoin_with_opaque_frame post, after helper body, not setup.
These cases do not call or replace truncated C4.

The minimal unbounded usize `len+16` should capture checked MIR plus Assert
and fail at its precise verifier arithmetic obligation. Successful checked
panic is safe runtime behavior; inability to verify it is a model limitation.
No arbitrary len bound, ignore_unwind or deletion of panic is permitted.

Existing C4 exact-one-body/source/preAST gates stay unchanged and retain prior
fresh refusals (3584fb04 / 285220a3). They are admission restrictions, not
semantic negatives. User permits a new narrow connected target with separate
fresh capture and independent review; a new hash alone cannot establish it.

## Independent address review (before dispatch)

Explorer /root/explorer_opaque_native reviewed cases.rs split/rejoin/MU frame
and actual SmallSort606–650. `native_prefix_recover_current` accepts arbitrary
CURRENT four owners; `native_current_rejoin_with_opaque_frame` preserves CURRENT
F, thread/types and full MU storage/own through separation frame. No additional
trusted semantics or optional-T ownership bridge appears. Identity wrapper
alone is not callback proof. Static GO only for isolated diagnostic; fresh
source/MIR/refinement/helper-before-consumer/full posts/return/leak review needed.

## First-30-minute dependency decision (19:35 UTC static review)

Literal full caller needs missing external as_mut_ptr binding and faithful
checked-add overflow handling; those general rules are assigned to VeriFast
agent, not changed here. The internal non-ZST native C1 candidate avoids both
earlier operations by a stated helper boundary and can retain MU opaque, so
neither general rule is proved necessary for that smaller helper. Its first
remaining dependency is NEW source-specific callback/lifetime/Output binding
(the old binding accepts only exact sort4_stable). This narrow change IS within
user authorization, subject to independent review/fresh capture; it is not a
new general kernel rule. Native-C1 unbound capture is batched once to capture
the real new MIR/refinement and first admission stage, with no proof credit.
No repeated old admission experiment or inverse adapter is needed.

## Follow-up after fresh1ba7fdb3 / 9b86096e

Fresh opaque interface VF0 (four helper bodies proved before native consumer),
normal/full automatic native return/leak, false-CURRENT-rejoin-post intended
refusal; native earlyreturn VF0/81. No callback theorem. Do not repeat those
unchanged proofs. Pointer/candidate parse the first command in a bare multi-
statement ghost annotation and refuse the second (`assert`/F producer).
Rust_parser.parse_stmt accepts one statement per annotation: wrap the pointer
assertion group in one `{...}`; split C1 preparation into individual `//@`
statements so cmp_k and other witnesses remain visible at the callback.
This is harness syntax repair, not a parser semantics change. No removed
assertion, post, marker or cut. Fresh paired capture/proof is needed.

Stock exporter source lib.rs:69 unconditionally appends overflow_checks=off;
source SHA11f1e10bb8e52a4950611f874b1123c11e2c87cbb1378c3f5060992f74425f00.
Fresh minimum normal/readonly MIR therefore contains binaryOp/add and no
checked overflow Assert, then AST arithmetic checking refuses at3:17–25.
Next capture adds ONLY a diagnostic direct invocation of the same pinned
rustc with --emit=mir, overflow-checks=on, panic=unwind, opt-level0/mir-opt-level0.
Record checked tuple/Assert/success/unwind edges versus exported unchecked
capture. It supplies no new compiler/verifier rule or proof credit.

Freshd776/86e38e3a: fixed pointer implementation-expression VF0/90 fullnative
normalposts/return/leak; no externalmethod binding. ActualC1 candidate parser
now passes, reaches source4 split/start lifetime, then strictentry refuses
unresolved outertype inference172:1–30 beforecallback. New exact capture-only
card/profile preservesoldgates, produces no proof. Preparedresource component
will test entry/borrow/undo separately, without removing assertions/debt/cut.
Minimal checkedrustc capture confirms AddWithOverflow+Assert(successbb1,
unwindcontinue); standard exporter overflowoff removesboth, so current ordinary
Add refusal is a tool modeling gap, not runtimeunsafety. Rawreview FRESH-D776-REVIEW.md.
