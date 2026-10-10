# Fresh frozen-profile diagnostics d5a0f8da

Buildd5a0f8da-a2ed-416c-9eac-a9ffff926c87, proof=infra
e12df71d57923d346ba0640b9bd0ea23d2835365. Cloud FAILURE because collector
expected the wrong admission marker; run exit0, complete evidence, no tool
setup failure. Create13:59:41.174458427 finish14:07:02.010745UTC, charged441sec.
Archive3ee661942dda4a67c7d29f4574f252607c460c19054540471d1e167ac115819b,
every payload/inventory/index verified by canonical download. New account783/3600.

Fresh binary8d686fef29ae6fe5b6adb91a946ff9942aef682baf934b273cc61d71a625527b
matches prior C4 console as well as all effective source/kernel/spec/non-console
pins. Tool snapshot004dab0f90e2abf75a422c83302015f593ec9273a78fc72d0e09ef71c1a2432b.
No native slice alias, new strict draft, selector patch or trusted delta applied.

| Case | Fresh result and exact scope |
| --- | --- |
| C4 bounded actual C1→C4 | VF0/370, exact original source/MIR/preAST pins, normal and all four direct unwind CURRENT recovery, four-cell joins, full original memory posts/unitreturn/leak. Conditional raw entry remains supplied. |
| normal false post | VF1 at315, Cannot prove false, after target entry. |
| C1/C2/C3/C4 direct-unwind false asserts | VF1 at365/398/447/482 respectively, Cannot prove false, after target entry. No changed source or imported snapshot values. |
| native-before-pointer positive | VF0/78, checked typed identity helper before native function. All safe native entry resources, source4 split/owners, comparator/F/thread, stock T/F producers, opaque MU frame, native automatic posts, both normal ghost branches, locals freed and leak checks. No actual as_mut_ptr, caller guards or callbacks. |
| before-pointer missing T / missing F | VF1 at helper pre11:25 /11:48, matching missing type_interp<T/F>; helper proved before native entry, then helper call reached. Intended producer controls. |
| unchanged typed native positive/missing T/missing F | All VF1 at26:18, No such function std::slice::<impl [T]>::as_mut_ptr. Paired MIR/refinement0. Missing-producer targets NOT_RUN, not semantic negatives. |
| MU forward | VF0/51, checked one-cell storage open only. |
| MU roundtrip inner | VF0/52, checked one-cell storage open/close with CURRENT.inner==old.inner only. No owner restoration or exact inverse credit. |
| MU exact old | VF1 at10:15, cannot prove new_maybe_uninit(inner(old))==old. Reached the intended assertion; no failed helper used. |
| guard prefix / selected guard lemma | VF parser refusals at13:20/7:20 on C-style ternary `?`. Guard semantics, inline-const and ZST witness NOT_RUN. Same proposition rewritten as disjunction for fresh follow-up. |
| extra runtime body | Paired MIR/refinement0; VF2 exact-one-body admission refusal before any sort4 target. The original source-SHA-first hypothesis was false. No semantic-negative credit. |

Raw review reads full verification logs, immutable source pairs and AST artifacts,
checks helper-before-consumer order and exact first errors, and checks C4 return,
CURRENT post consumption and leak traces. Existing C4 capture-only refusal also
remains before bounded target admission; it is not a semantic proofnegative.
The pure classifier correction is tested first on the saved verified admission
log in SAVED-ADMISSION-REPLAY-D5.json; it changes no raw Build/proof verdict.

Follow-up rebuilds the SAME effective frozen tool, repairs only equivalent guard
syntax, tests CURRENT MU owner restoration and the actual slice implementation
expression, and separately tests extra-body versus comment-only source gates.
Already fresh C4/controls and native alias failure are NOT_RUN in that follow-up,
with exact d5 provenance retained. No historical matrix repetition or acceptance
upgrade. Native→C1/native→C4/actualcaller→sort4 remain NOT_PROVED.
