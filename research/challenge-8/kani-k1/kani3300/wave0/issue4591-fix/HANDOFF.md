# READY for independent11 review

Standalone source/test/static package for TASK-KANI-4591-FIX-W15, issued at g0
`7afd3d52d959a246df4e968e9cc8a66f029fbedf`. Fast OFF; zero subagents.
The g0 delivery commit is the commit containing this exact package; the full
delivery SHA is reported with the final handoff. All g0 changes are restricted
to `kani3300/wave0/issue4591-fix/` under the task's research directory.

| Binding | Value |
| --- | --- |
| Source worktree | `/root/kani-issue4591-fix-w15` |
| Source branch | `fix/ordinary-stub-contracts-4591-w15` |
| Local candidate | `a7bca98c91cbfa595bdc2a1bdc6bd4d0a4fa796a` |
| Candidate tree | `98fae98ce9e783bed0393d35657674da09c3aa31` |
| Single parent / stock main | `faffcee3bca2770c03bd21c3bde89cc8f6f7a14e` |
| Main tree | `09b828b47c93e90e140e8c41f9048109a2f4a786` |
| Main parent | `a3c8b8610739aab7d2c864bd4021086a5e7c0d94` |
| Future nonskip head | `NOT_CREATED`: same-tree sibling with exactly main as parent |

The candidate is local `[skip ci]`, authored by Tiramisu-Cake
<igkharin@gmail.com>. It must stay outside the future main..final pushed range.
Main was rechecked read-only with no drift; see MAIN-CHECK.json. No rebase,
compiler, cargo/rustc/rustfmt, expansion, Kani/CBMC, fullrunner, CI, push, PR,
issue/comment publication, ledger, reservation or budget action occurred.
Historical MRE/intake/clear-error/draft records are unchanged.

Read SOURCE-TRACE.md, REGRESSION-ORACLE.md and PR-DRAFT.md first. The fix records
the successfully resolved ordinary replacement source for the contract pass;
other transformations and safety instrumentation continue. Original PFC and
verified modes remain selected for their explicit targets. Contracted
replacements process their own contracts. An explicit same-target
PFC/verified-plus-ordinary overlap retains its current compilation error; a
broader contract precedence policy is deliberately left unchanged.

The eight test files in SOURCE-PINS.json cover the issue's verbatim reproducer,
our f/g MRE, requires-only/ensures-only/both cases, precondition bypass,
postcondition replacement, PFC/verified positive and negative controls,
recursion/generic/transitive/uncontracted/multiple targets and provider-target
overlaps. The issue's caller overflow is an expected counterexample, never a
fixed PASS. Every newly authored main/fix native result is NOT_RUN. The
historical intake keeps its INCONCLUSIVE classification and successful native
control observations separately.

`python3 -B validate.py` replays split and whole patches into temporary Git
indexes, checks exact trees/hashes, fixture/code-block and workflow inventories,
and exercises synthetic metadata plus real read-only rejection paths for the
future-head gate. VALIDATION.json records static/mock results, not typechecking
or verifier success. MANIFEST.json seals every package file except itself.

CI-REQUEST.json / CI-REQUEST.md prepare one full standard PUSH-CI bundle on
the eventual exact PR-branch head. All16 workflows and all scripts/actions
retain main's bytes. The three native push workflows include every job and
matrix entry. PR-only release/std/benchmark scope remains deferred to the
upstream PR as directed by the owner. Ledger reference df7a140991 is item1
30/31, item2 11/17, total41/48; zero attempts consumed here.

Next gate: **independent11 review of this exact g0 package and source/tree**.
After approval, root prepares the exact GO request. A separate owner/coordinator
command authorizes the future nonskip head and full standard push-CI; PR
publication still requires an owner command. READY is preparation status and
grants neither action.
