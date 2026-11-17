# S1-07 PFC component — ready for w14 review

Task: `TASK-CH8-S1-07-PFC-W15.md` at `2f3ede5ff4`; initial g0 HEAD was that task
commit, with clean worktree. Model/effort unchanged; no delegation.

Result: **22/22 source-reported Profiles v4 chains bound, 0 PENDING**. The two
activation variants have their exact predeclared sole FAILURE and effective
patch/source hash; legal companions have corresponding SUCCESS. Exact rows,
producer/source semantics, six-symbol demangling dictionary and all hashes are
in PFC.json; rationale and limits are in PFC.md.

Validation: **228 tests PASS**, including 220 rejection/mutation cases and 176
contract relation mutations below hash/inventory gates. Two subsequent replay
runs matched PFC.json byte for byte. See VALIDATION.json for exact commands,
results and code/output hashes.

Only this new accept-pfc directory is written. No artifact duplication, std/tool/
control/policy/ledger change, total qualified-count recomputation, historical
receipt edit, local cargo/rustc/Kani/CBMC, raw logs/archives, CI, push or publication.
Concurrent accept-u and s1-08 work is not consumed or staged.

Assurance: bounded source-reported Profiles v4, trusting pinned stock compiler.
Independent compiler/general/B1/B2 proof credit: NONE. Null compiler-instance
identity is preserved; exact runner invocation metadata does not strengthen it.
This is solely a PFC binding component. All other admission-root gates remain
for coordinator integration.

Next: separate w14 review of this component and its mutation suite, then
coordinator integration with other components. No new Build is needed to replay
these bindings; no dispatch is authorized here. No unresolved external/scope
blocker was encountered.
