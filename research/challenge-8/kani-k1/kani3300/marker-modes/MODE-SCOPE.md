# Mode scope and prepared source map

Coordinator scope update, 2026-11-13: marker diagnostics are deferred to separate work;
see [REQUIRED-STATE.md](REQUIRED-STATE.md). That prerequisite STOP is accepted and does
not block this docs/fixtures stage. `contract.rs` is unchanged.

Public `docs/src/reference/experimental/contracts.md` now states that Part1 does not
claim shadow transfers in Replace (`stub_verified`) or RecursiveCheck (`recursion`
contract checking). This is not a blanket restriction of ordinary/Assert/SimpleCheck,
not a claim that every unclaimed input fails, and not an implementation Unsupported guard.
The public note also explicitly defers marker diagnostics and links the accepted design note.

All fixture paths are under `tests/json-handler/uninit-contract-mode-boundaries/`.

| File/root | Intended mode from actual metadata | Target/path |
| --- | --- | --- |
| replace.rs / replace_transfer | Proof + verified_stubs(passthrough) → Replace | input → through_helper → relay → passthrough replacement → return → conditional payload read |
| replace.rs / replace_ordinary | Proof, no stub/check target → Assert | Same target and helper/return path, actual identity body |
| replace.rs / replace_simple_check | ProofForContract(passthrough) → SimpleCheck | Same target/contract/path; wrapper has actual relay and by-value return |
| recursive.rs / recursive_check | ProofForContract(recursive_transfer) + recursion attribute → RecursiveCheck | depth 0 base body; depth 1 → relay → actual self-call → REENTRY replacement → return |
| recursive.rs / recursive_ordinary | Proof, no stub/check target → Assert | Same recursive target and bounded actual self-call with actual identity body |
| recursive.rs / recursive_simple_check | ProofForContract(bounded_transfer), no recursion attribute → SimpleCheck | Same requires/ensures; one bounded recursive step explicitly unrolled as relay(relay(value)) |

`contract_mode` in `kani_middle/transform/contracts.rs:569` establishes this source/metadata
selection. The collector checks exact root, Proof/ProofForContract metadata, verified-stub target,
unwind, and presence/absence of the recursion tracker. These checks do not establish the
transformed closure/body binding. Every actual source→emitted mode/transfer binding remains
BINDING_PENDING until coordinator CI/review; no completed outcome is invented.

## Legal source semantics, stated before execution

Inputs use `MaybeUninit::new(42)` for initialized=true and valid `MaybeUninit::uninit()` storage
for false. The same short-circuit requires/ensures clause tests payload only on the true path.
The identity body/relay preserves storage state. No invalid typed u8 is created before a target
operation; the false path transfers storage and never reads its payload. Expected companions:
SUCCESS, both paths reachable. This is a source expectation, not a measured verifier result.

Replace expansion in `library/kani_macros/src/sysroot/contracts/replace.rs` asserts requires,
havocs return with any_modifies and evaluates ensures before assuming it. Its MU Arbitrary return
can choose uninitialized storage even when initialized=true. An inserted payload uninit check may
therefore precede the assumption. Protocol failures may occur first. No exact failure/golden is
assigned from this source reading. A particular SUCCESS is retained unchanged and does not
qualify the mode generally.

RecursiveCheck expansion in `bootstrap.rs::new_recursion_closure` checks REENTRY, runs check
on initial entry and replacement on reentry. The fixture has a real recursive edge with depth
0/1, source covers before base/recursive edge, and return-consumption covers. Unwind is explicitly
8. The SimpleCheck companion unrolls the bounded step instead of testing unannotated recursion.

## Observation versus acceptance

The six fresh per-root runs retain the full JSON export, check/cover inventory and complete
failure descriptions. The collector accepts either completed boundary verdict and requires
legal companions to pass. It records Unsupported/frame/unreached-cover gaps and leaves
UNREVIEWED/BINDING_PENDING and mode_qualification=false even when collection succeeds.
It does not establish a reproduced boundary, lawful prefix or semantic acceptance. Coordinator
must map generated properties to source/clauses/helper/return and actual recursive reentry,
review the entire failure set, then set any regression golden. Early unrelated frameFAIL or
Unsupported is not a qualifying negative. No worker14 checker or shared schema change is used.

Export limitation: successful checks are counted but their individual IDs/descriptions are not
listed by this base's JSON exporter. Full successful-property mapping therefore also needs the
retained emitted/property artifacts through the coordinator evidence workflow. The collector
does not claim to supply that mapping from summary counts.
