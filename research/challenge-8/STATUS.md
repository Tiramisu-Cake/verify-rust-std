# Challenge 8: current checkpoint

Updated 2026-10-07. **CLOSED at6/6 NEW runs: stock generic PASS; experimental
fieldless-layout acceptance INCONCLUSIVE.** No active experiment; STOP.
Entry checkpoint e170656b7ff00e8de8ac9d5ebc949d2dbf3cfd75, correct fork/branch,
clean matching heads. Budget used **6/6 /653 of10800 summed job-seconds (10m53s)**,
including every job's preparation/build/upload. Unused time does not grant runs.

**Stock generic const/mut PASS independently** on unchanged official VeriFast26.09
/source809de459/nightly-2026-02-05: [run37540829027](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37540829027),
source/head968c073983e0fa27112c5d8a4e10a36b05828323. Both VF0, export/decode/
refinement0,72 statements each; resources/posts/dead-code/leak/integrity intact.
Stock concrete Z remains INCONCLUSIVE; original negatives/replay pass separately.

**Experimental-rust-fieldless-layout-v1** built and full matrix attempted in final
[run37544574703](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37544574703),
source/head e472aa27a93b15904c702a2484d9e2fdf6f5554a, exact pushed/head_sha match.
Job112545369857,23:05:34–23:08:00Z on2026-10-06,146s, FAILURE.
Patch SHA256 d4a12525bcdbdaa4deb82058d6cc0037c8c09fa508ad2eeb14386b2753693a14.
Original experimental six pass expected gates; extra9 positives/4 intended negatives/
5 unsupported-layout cases pass. Z size0/align8, const/mut zero-strideadd i0..3 and
checked generic calls Z/u64 verified. Metadata5/7 gates pass; absent/source-span
remain classifier INCONCLUSIVE despite intended raw VF failures. Existing Rust/C/C++
regressions pass both profiles; new C/C++ smoke fixtures parse-fail both profiles.
Classifier selfchecks12/12 PASS. Full logs/artifact11450580233 inspected; raw unchanged.
**Full acceptance remains INCONCLUSIVE; no checker/fixture fix applied after run6.**

Exact layout domain: local concrete original-fieldless nongeneric Sized Rust structs,
reprRust/C with optional align. Compiler-backed optional size/ABIalignment and type/
source/target binding; Rust-only >=0 bound, C/C++ >0 retained. Exact fielded/generic/
packed/transparent/enum/union/DST facts and offset/ownership/alias changes excluded.
All executable work hosted; stock profile separate. No full model-soundness,
automatic-copy UB, ownership/callback/five-unwind or whole-sort4 theorem follows.

Next proposed decision: narrowly repair evidence processing for named caller/full
nested span and split C/C++ contract annotation blocks, retaining all requirements;
NEW bounded hosted matrix run at unchanged patch. **NOT AUTHORIZED / NOT RUN.**
No demonstrated need for further model semantics at this checkpoint.
[Closeout and exact run/source identities](SORT4-ALIGNMENT-RESULTS.md#fieldless-layout-prototype-closeout),
[phase](SORT4-ALIGNMENT-PHASE.md#stock-generic-and-fieldless-layout-prototype--2026-10-07),
[patch provenance](verifast-rust-fieldless-layout.md), [journal](EXPERIMENT-LOG.md),
[previous checkpoint/history](STATUS-HISTORY-2026-10-07.md).
RAPx CLOSED / NO-GO; B/C NOT RUN; ZST retained in contract. Historical FnMut/Drop,
full sort4 and external issues/PR/messages remain outside this stage.
