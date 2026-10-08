# Nine-body A1 linkage: static review of the unrun component

The proposed patch is `verifast-actual-nine-a1-26.10.patch` (SHA-256
`557e88169c2f8b5d5e617e413abdccc69e42c4f2147b8d750cbc9019f3e7e8fa`),
based **after**
the pinned 16-component chain, actual-owner-nine admission component 17,
nested H2 component 18, and SAFE-forget component 19 (SHA-256
`d6d25b9ad1b07ce62d1a21f8f1bfb1dd72658cc7e5e1a527b0be38afc7e6953f`).
It changes only `vf_mir_translator.ml`; it does not modify std runtime,
fixture source, headers, contracts, kernel or cleanup implementation. The
existing two-body `SORT4_A1_LINK_REPO_ROOT` gate and behavior remain separate.

O25 run `37761756051` compiled the first 18 components and passed the full
S6 regression. Its exact nine-body owner gate accepted. The complete verifier
then checked `checked_transmute_neo_pointer` through its full return/leak
obligations and stopped inside `checked_assume_init_pointer` at its unchanged
std call: `verified/lib.rs(117,13-35): error: No such function:
std::mem::transmute_neo`. This witnesses the first A1 linkage need; it does
not demonstrate the second outer call or a full actual helper proof.

The new `SORT4_A1_NINE_REPO_ROOT` opt-in requires the owner-nine gate to have
accepted the same root and complete decoded unit before it activates. The
owner gate pins all nine ordered DefPaths, the complete verified/original
source SHA-256 values, every decoded body hash and the whole decoded unit
hash. This component also checks its own exact verified source hash, the
two local A1 function names, source-unit identity, contracts, pointer-local
shapes and the existing typed A1 graph, then audits the outer actual
`assume_init` typed pointer substitution, sole Move input, result place,
decoded wrapper/pointer locals, normal target and **original shared Cleanup successor**. O24's NORMAL outer
graph has 42 locals/25 blocks, selected block 20, `Move(_37)` to `_0`,
target 21/cleanup 24; readonly has 31 locals/14 blocks, block 9,
`Move(_26)` to `_0`, target 10/cleanup 13. The local `transmute_neo` call
remains the previously checked direct-Continue A1 graph. Each redirect is a
`FnCallOutcome`, preserving the MIR's original normal and unwind routing.

The patch rejects simultaneous old two-body and new nine-body A1 opt-ins,
missing owner-nine/root admission, nonpointer substitutions, altered local
or outer graph, and duplicate or missing redirects. The outer local checked
callee retains `some(p)`, `MaybeUninit_pointer_own`, current thread,
`raw_ptr_own` of the same returned pointer and `on_unwind_ens false`. Neither
redirect grants `Element` pointee rights or claims a generic
`MaybeUninit<T>::assume_init` rule. The actual helper's shared cleanup and
all other call sites are unchanged.

The complete-source hash in the owner gate means a source mutation normally
fails there before the A1-specific checks; such a case is an owner admission
negative, not evidence for an A1 resource failure. The existing isolated A1
resource controls remain necessary for `some(p)`, missing pointer owner,
incorrect result identity and false unwind. For this nine-body profile,
new hosted controls should verify missing/partial opt-in refusal and exact
typed MIR mutations of each call fail at their expected admission gate;
positive proof must verify both checked local bodies before using their
summaries, then reach the actual helper's ordinary safety, cleanup and leak
obligations. A residual actual helper failure is a new barrier, not license
to weaken posts or ownership.

Static validation only: the patch applies with `git apply --check` to a
disposable copy of component 19's translator, reverses cleanly from its
edited copy, and `git diff --check` is clean. No local build, verifier,
exporter, research runner or executable test was run. The patch has no
hosted result and is **unaccepted** pending main review and a new exact-SHA
hosted run.
