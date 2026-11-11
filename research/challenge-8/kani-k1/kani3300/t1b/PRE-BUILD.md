# KANI3300 T1b — PRE-BUILD REVIEW packet
Cloud $0; spend/reserve0, builds/dispatch NOT_RUN; separate independent Kani/tooling reviews PASS.
Worktree /root/verify-rust-std-kani3300-t0; branch experiment/kani-k1-kani3300t0-20261111; task base3a780c05130440340197e98eda602ee705e80d8e.
kind diagnostic; slug kani3300; stage kani3300-t1b; owner k1-merge; A9 roots/B4 roots unchanged expectations.
Library tree919cc3e2dc5fb19ea6e7f7be761914b949160a41; fixture bd6d51c7ad634644d5e8fc16b539cd84b2eedb6101d52692c4d7d0fb3545e8a6.
Kani pinf046b70644e113be0df9c22c2e6ea44a65a57566; nightly-2026-10-23; pinned Rust7189d39d9ce936881b8132c6addeaf3e295cd455.
CMP2 b1f0105c0390fb55081e3d186fa286d23867b585; unchanged production patch SHA256 46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4.
Diagnostic commit 51848f3fc7c432ae334aa4aa1c0bd607dedbcfc0 (local clone diag/kani-3300-t1; no push).
Diagnostic patch SHA256 211a036bc685ef2df5ef1d37b9f25d43d7d48595d08c9e3783d032718bb6dc14.
Combined patch SHA256 8bfd47ae78d0ff8a1a9a0b9879719400b15cc463bef11e1fe03e340b6bc55545.
Expected combined applied tree a88f60c9559879ed29443d52d8a8013da7bee9c5; static index only; production restored by reverse delta.
Tooling base 3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c; commit c3468b3bd84f4a91a2ea99fa0fcea317bd98e681.
Tooling tree 6446f4d16bf0dad3a7e38a00347835b986694e66; extension SHA256 55aeeefe592b87f46059db08c5abfb5578a58be0b3c644dda764dfecf7361de0.
Cloud recipe SHA256 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81; unchanged; other recipe hashes TOOLING-BINDING.json.
A request SHA256 b4bdf24b8808c48c366974bd0acb3740f129f21c4fb209c9ea5dc4177dc54398; kani3300-t1b-a-20261111-01.
B request SHA256 e35b5ce3e85683c8932aaedaf443cff7b16e960e5ca4457ddd7f7a824ad8e8f6; kani3300-t1b-b-20261111-01; separate GO after A analysis.
Effective runner argv: scripts/run-kani.sh --path /workspace/src --kani-args + kani-A.args/kani-B.args (unchanged baseline bytes).
Uninit/controls on, inventory off, standard4/jobs1/3m; RUSTFLAGS=--cfg kani_smallsort_controls.
KANI3300_TRACE_DIR=/workspace/src/k1-out/trace; FILTER literals in requests/EFFECTIVE-INVOCATION.json; no runtime trace flags.
KANI3300_TRACE_ID=exact request SHA256 above; KANI3300_TRACE_STAGE=kani3300-t1b; other compiler/rustc/CBMC argv UNKNOWN.
Actual runner argv/relevant env captured at Cloud boundary only; current effective invocation artifact is a static expectation, NOT_RUN.
A planned envelope57min; (9*3+30)*0.0135=$0.7695 <=cap$0.80; no reservation/phase activation in prep.
B planned envelope42min; (4*3+30)*0.0135=$0.5670; same immutable diagnostic/tooling/library; no automatic B/retries.
30min overhead preserved; diagnostic compile cost unmeasured; live budget/slots/deadline and existing Cloud preflight remain later gates.
Active lane-root request remains T1a by authorized write scope; coordinator must promote A bytes, bind final head and give exact-packet GO before dispatch.
Reviews: separate Luna HIGH Kani/tooling PASS receipts; no semantic acceptance from packet integrity or tests alone.
Before B: verify A identities/required trace coverage/controls and original failure reproduction; missing/partial/broken trace or changed checks =>stop UNKNOWN.
Checks: STATIC-CHECK.json29 PASS, Python96+9+11 PASS, rustfmt/diff/license/shell syntax; compiler/-D warnings NOT_RUN.
Concrete object/offset/R/runtime causality UNKNOWN; proof credit NONE. PRE-BUILD REVIEW is the stop boundary.
