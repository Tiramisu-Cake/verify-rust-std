# Build2 source/MIR diagnostic, no proof credit

Cloud Build `e71803aa-11e1-4804-ae9c-8f901b106d5d` used exact
proof/infra SHA `eb631c2222c9070948c15693d424c631488aa86f`.
The verified receipt was unpacked at
`/tmp/native-compose-e71803aa-read/allprooflogs/cases/sort4-native-compose-c1`.
Normal and readonly MIR export/decode and refinement all exited zero.
The helper records each contain one `std::ops::FnMut::call_mut` and its
call terminator has `unwindAction = (continue = void)` with a normal target.
The readonly native record contains one call to `c1_source_prefix` with a
direct Continue unwind. This is a source/MIR diagnostic, not verification.

The first full verifier and AST diagnostic refusal is
`verified/lib.rs(226,17-23): error: Parse error: Parse error.`  The source
at that point put six consecutive assertions in a single `/*@ ... @*/`
annotation. The parser accepted its first statement and failed at the
second `assert`. For the next fresh source, each native pre/post assertion
has its own `//@` annotation, as in the existing native-entry fixture.
The pinned Build2 source/MIR hashes cannot be used as an exact frontend
transformation certificate for the changed source. Build3 must recapture
both MIR modes, refinement, AST/first refusal and the tool snapshot.

The first runner counted capitalized `Continue`; capnp text uses the exact
lowercase spelling `unwindAction = (continue = void)`. The next capture
corrects that diagnostic counter. No new frontend overlay was used or
implemented for Build2, and no verifier result was accepted.

Build3 is a deliberately partial diagnostic under the pinned production
tool plus the **existing** reviewed `SORT4_STRICT_LFT_CUT=1` and
`SORT4_HRTB_OUTPUT=1` (target `c1_source_prefix`) options only. The new
composition overlay is disabled. Its falsifiable expectation is that both
MIR modes and refinement again exit zero; parsing proceeds past the native
assertions; full verification then reaches the source marker/strict lifetime
boundary, while whole-module AST either emits the immutable original helper
AST or records the specific serializer failure. A renewed parser/setup
failure requires correcting only that source/setup defect and a fresh run.
An AST serializer failure would admit a separately reviewed capture-only
hook; an ordinary helper verification refusal would instead guide the
exact semantic patch. Every changed source is repinned in the new receipt.

The helper's runtime comparator is the pinned actual SmallSort c1 source
line 620, with operands cells 1 then 0. The native diagnostic calls this
new bounded helper under `len>=8` and positive `T` size; the actual std
native-to-sort4 control-flow edge remains outside this fixture. The next
receipt must bind exact original/verified source hashes, complete normal
and readonly helper/native MIR hashes and callback local inventory, and
the unchanged production critical-tool hashes before any frontend
transformation. Neither an old Build2 MIR hash nor the artificial native
helper call can certify the real std caller CFG.
