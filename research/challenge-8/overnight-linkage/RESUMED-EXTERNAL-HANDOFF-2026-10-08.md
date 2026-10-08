# Resumed phase: external-limit checkpoint, 2026-10-08

GitHub-hosted research is externally blocked: the O27b source-only dispatch
from `847bd01709d4a1269ff02ef63a436dd8cacf67c2` returned
`HTTP 422: Actions has been disabled for this user`. No O27b run was created.
Authorization remains until **14:30 MSK / 11:30 UTC, 8 October 2026** with a
separate 7200 summed hosted job-seconds ceiling. This checkpoint follows the
owner's external-limit instruction; it introduces no semantic approval gate.
No local verification, build, extractor or executable research test was used.

Own branch `research/overnight-select-sort4-26.10`, worktree
`/root/verify-rust-std-select-night`. Runtime std and target signatures are
unchanged. All drafts are preserved. Main, upstream and the second agent's
branch/worktree were not modified; no PR or organizer message was sent.
This report is committed after source/preparation HEAD `847bd017`; the final
documentation checkpoint SHA is its descendant, recorded in the final handoff.

## Actual Rust results and change from O22

**Neither actual `select_unpredictable` nor actual `sort4_stable` is fully
proved. No new full actual target function is claimed in this resumed phase.**

O22's actual-owner unit passed admission but stopped at nested ghost `Not_found`;
sort4 failed source stripping before a graph existed. The confirmed changes are:

| Checkpoint | Actual integration result | First remaining obligation |
| --- | --- | --- |
| O23 | Exact nested ghost ownership repaired; the original two nested commands are retained in their source bodies | SAFE outcome/pointer ghost interface, before actual body |
| O24 | Hosted independent fixture generation, runtime restoration after ghost stripping and expected-fragment checks pass **before verifier build**; complete paired NORMAL/readonly exports and refinement pass for helper and sort4 | Helper refusing nine-body calibration; sort4 reserved unwind marker at185 |
| O25 | Exact nine-body and nested H2 gates admitted; generic drop both outcomes and local pointer transmute body verified | Missing `std::mem::transmute_neo` link inside local assume_init at117 |
| O26 | Both A1 redirects and SAFE owned-forget link admitted; local prefix callees and SAFE outcome prototype verify; **actual helper body starts** | Nominal guard owner close at198: ghost `guard` has `**Element`, expected qualified `DropOnPanic<*Element>` |

The selected actual-owner harness is pointer-specialized (`T = *const Element`,
with unrestricted implicit-Sized Element). Its explicit precondition is `thread_token(t)` with `t == currentThread`.
Its normal post returns that thread token and the pointer selected by
`condition` with `raw_ptr_own<Element>(t,result)`; its unwind post is false. It
grants no Element pointee rights. A completed proof of this contract would
still not close the original unrestricted generic select contract.

O26 full traversal stops before the helper's actual runtime forget and outer
assume_init. The actual qualified nested Drop body comes later in the unit and
has not been checked to completion. Its link/counter is not a Drop-body proof.
The old actual helper body retains its exact runtime source and resource posts;
all outer return, leak, normal/unwind and selected-value obligations remain open.

O24 actual sort4 enters its full body and first rejects
`__vf_sort4_first_unwind` at `verified/lib.rs:185`. All five real FnMut calls,
eight select calls and four copies remain in the complete graph. This preparation
result does not close full callback recovery or sorting. Earlier O16 reached a
real comparator in a different partial fixture; its unresolved full-array unwind
post is preserved as historical evidence. The current full graph has not yet
proved recovery of `array<T>(v_base,4,_)` for panic at each comparator.

## Separate accepted components and experimental results

Accepted statuses retain their own proof SHA/profile/assumptions, and do not
transfer acceptance to the twenty-component composition automatically:

* Stock+CFG26.10: `e6c02f22420ba4ff6a77e39c9610708a6096e7d7`, [run37698481357](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37698481357).
  Ordinary and shared cleanup preserved; positive, false-post and dead-code controls.
* S6 constructor/as_mut_ptr/typed intrinsics/pointer drop: `1378f0ffc8342233349fae3df5a938c4a021c8d7`,
  [run37700450091](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37700450091).
  Full eight-stage primitive matrix passes again in O26, separately from actual progress.
* Local A1 pointer transmute/assume_init: `d3363d2e6525b2c27cdfc3e83006db94a04921da`,
  [run37711416854](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37711416854).
  Three full positives, twelve intended proof/resource negatives, three source rejects.
* Local H2b nominal optional-storage guard: production O19
  `a6f9d5e00cc99c06f8c49fa2e27e6a92308a1a79` and adversarial O20
  `e30bdc72d7af37222c401dd54ed50759eb840547`,
  [run37746579002](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37746579002),
  [run37748156620](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37748156620).
  Constructor, generic method and real local SAFE Drop body check both outcomes,
  consume initialized storage plus `T.own`, and return optional storage after
  destruction. Five generated-post controls distinguish outcome/resource failures.
  [Acceptance review](../overnight-guard/O20-POST-ADMISSION-REVIEW.md).
* Local exact-body generic owner-preserving unsafe forget adapter: O22
  `02945280d4f335948c6edd60feb7ac62092a0256`,
  [run37754201983](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37754201983).
  Returns the same thread and `T.own` normally, false unwind; full proof, five
  post/leak controls, dead-code and separately classified admission control.
  This is not an independent proof of SAFE/const std correspondence.
  [Acceptance review](../overnight-forget-own/RESULT-O22.md).

Local callback/HRTB progress remains experimental: O19 verifies genuine FnMut
normal/unwind recovery of current cells and owners and resolves the local
FnOnce::Output/bool interface; O20 matcher controls pass. It is not actual sort4
recovery. Local join-four O21 verifies the stock memory join and three resource
controls; single-element scratch copy has an explicit non-ZST domain. Neither
proves stable sorting or a general generic/ZST contract. SWO functional composition
remains separate from safety under arbitrary admissible comparator responses.
Historical S6 and S7c statuses are preserved; S7c is not upgraded.

## Exact O26 tool profile and trust boundary

[Machine-readable ordered manifest](O26-PROFILE-MANIFEST.json) records all twenty
patch paths and SHA-256 values, applied diff, binary/spec/parser/translator,
exporter/refiner/schema hashes and three modified production files. Base std
`cd371e035c7e573760c43bf934d53e8118ee3e7d`; VF26.10
`f76012fb518703b1d98e243ac4f487f16877cfcb`; nightly2026-09-25 compiler
`f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f`. The production kernel is unchanged.
Main20 is **EXPERIMENTAL**, not an accepted helper/sort4 profile.

The composition retains compiler layout and typed-source/MIR correspondence,
stock pointer memory/ownership and drop glue dependencies, ManuallyDrop identity/
nonunwind behavior, and the recorded refiner limitations concerning Call/Drop/
Assert unwind. These are explicit trust dependencies, not proven universal Rust
destructor/compiler semantics.

New integration components have these additional narrow obligations:

* 17 admits only the exact nine-body source/qualified ADT and whole decoded
  unit plus all bodies, preserving all thirteen ghost commands (two nested,
  eleven outer) and shared cleanup inventory. 15 reparents the exact existing
  nested commands; it does not delete, duplicate or invent proof commands.
* 18 redirects the qualified nested pointer drop to the same-unit checked
  generic drop with normal and unwind routing retained. Its nominal Drop post
  returns optional storage on both outcomes, consuming initialized cell and
  `T.own`. Final actual nested-body proof is still required.
* 19 relates exact SAFE/const std forget to the checked unsafe/non-const
  owner-preserving adapter. Its precondition still requires nominal ownership;
  it creates no owner or Element pointee permission. The one exact false-unwind
  call is projected to normal; the other nine shared cleanup predecessors remain.
* 20 relates typed pointer A1 calls to checked local transmute/assume_init.
  It retains `some(p)`, current thread, MaybeUninit ownership, result identity,
  raw-pointer ownership and false unwind. The outer original Cleanup24 remains
  in FnCallOutcome and typed MIR; its proof traversal is pending. No generic
  transmute theorem or Element pointee rights follow.

O26 source2/MIR2 admission controls all reject at their intended owner gates.
They do not replace A1-specific wrong-call/result/substitution/cleanup,
missing/duplicate redirect or resource controls, which remain pending.
No memory/validity/unwind/leak/dead-code/refinement check was disabled or weakened.

## Saved unverified work and next permitted steps

Source-only guard shadow correction is committed at `89cffd8b`. Exactly two
conditional nominal-owner close arguments now use the logical record
`select_unpredictable::DropOnPanic::<*Element> { inner: guard }`, where that
inner ghost name denotes the earlier pointer. It must equal the real aggregate
and close only from selected initialized storage and its pointer-value owner.
The existing saved_guard witness/post-forget open and all runtime operations
remain unchanged. No hosted source/MIR/parser/resource evidence for this new
source exists. [Guard handoff](../overnight-helper/ACTUAL-NINE-GUARD-SHADOW-HANDOFF.md).

After external Actions recovery, and only within a valid authorization window:

1. Dispatch the already narrowed SOURCE capture workflow at a fresh exact SHA.
   Hosted fixture/ghost-strip/fragments precede the console; isolate helper from
   sort4 and unrelated TEST builds. Capture fresh paired source/MIR/refinement,
   complete decoded unit and all nine bodies; do not guess their fingerprints.
2. Review source/body command ownership and graph inventories. Preserve old
   components17/20 as historical profiles and prepare a separately identified
   certificate refresh for both: both independently pin the changed verified
   source. Old gates deliberately reject it. Recheck source and typed-MIR mutants.
3. Prove the truthful nominal owner close, then actual SAFE forget/resource
   preservation, unselected drop, assume_init and complete normal/unwind posts.
   Check actual nested Drop in the same unit. Run the full relevant acceptance
   matrix, including link-specific controls, before any acceptance claim.
4. Resume actual sort4 reserved unwind-handler/callback integration and full
   four-element resource recovery without weakening the array post. Complete
   safety first, then connect existing sorting/permutation/stability under SWO.

Independent strict-lifetime CUT, exact six-temporary callback relocation and
entry tracing are preserved in `605e6bff` and related notes. They modify an
isolated TEST console only and remain outside production. The new relocation/
trace pair has no hosted execution. It is restricted to a local callback MIR;
actual sort4 has a different temporary inventory. Do not promote it to a kernel
rule or treat it as evidence for full callback/sort4. O27's planned TEST diagnostic
never executed. Keep prior inconclusive/setup classifications unchanged.

## Runs, budget and remaining external state

Main proof checkpoint O26: `c19e4c50470d32199178d5229a2819554fc6b2f1`,
[run37763468180](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37763468180),
job113265293561,10:26:27–10:29:36 UTC,189 seconds. Collector success classifies
the expected partial actual proof; it does not mean helper PASS.
Preparation/full-sort4 graph O24: `2ca66b89ed3b17c3a054c6bb5b9d1b4b3ad2348b`,
[run37760135524](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37760135524),53 seconds.

O27 `6165296266ee17ae8f91f7550034452cd0ebb0cf`,
[run37764722707](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37764722707),
was created10:37:46 UTC and completed failure10:37:51. Job113269452142 remains
queued with runner_id/runner_name null and no steps; six other jobs were skipped
without runner allocation. No logs/artifacts; GetRun/GetAttempt404. Repository
Actions is enabled, but fresh O27b dispatch explicitly reports account Actions
disabled. No executing workflow is listed; orphan queued metadata is unresolved.
No subsequent dispatch retries or new negative/proof claim were made.

[Budget ledger](../overnight/RESUMED-BUDGET.json): O18–O26 confirmed
194+232+85+172+232+254+53+185+189 = **1596 job-seconds**. O27 has no confirmed
allocated seconds; reserve **5** conservatively until metadata resolves.
**5599 available** from7200 after this reserve (5604 before it). Rejected O27b
created no job. Historical overnight3094/21600 and expired18506, S7 5306/5400,
stock99/1800 remain separate and unchanged. The deadline was not extended.

Final checks are static only: syntax parsing of edited Python/YAML, shell syntax,
patch/file hash inventory and Git whitespace checks. No such check proves the
new guard literal or any TEST semantics. The final documentation-only commit
does not replace a proof SHA or need a hosted proof run.
