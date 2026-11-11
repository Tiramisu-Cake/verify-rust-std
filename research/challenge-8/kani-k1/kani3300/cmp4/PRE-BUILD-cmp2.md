# KANI3300 CMP4 — CMP2 PRE-BUILD packet

PREPARED; CMP2 Cloud NOT_RUN; proof credit NONE. Runtime Codex, diagnostic only, no repair or retries.
Task `research/challenge-8/kani-k1/TASK-KANI3300-CMP4.md`; planner `PLANNER-AFTER-CMP3-ANSWER.md` points 3–6.
Worktree /root/verify-rust-std-kani3300-cmp4; branch experiment/kani-k1-kani3300cmp4-20261111.
Stage kani3300-cmp4; owner k1-merge. This is the second/final authorized attempt, requiring separate coordinator GO.

## Exact inputs

Active root request equals reviewed cmp2/RUN-REQUEST.json: kani3300-cmp4-cmp2-20261111-01.
Request SHA256 e23db232f257a8977e1d90b15260de6295da02898e612c60333fbe19c97abd51.
Production CMP2 kani_patch: research/challenge-8/kani-k1/kani3300/u4/kani-uninit.patch.
Patch SHA256 46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4; unchanged, 100977 bytes.
Kani pin f046b70644e113be0df9c22c2e6ea44a65a57566; toolchain nightly-2026-10-23.
Expected applied tree d356238999ab436ddc1dd7ffa845b0db214aa53e is inherited static binding; actual CMP2 tree NOT_RUN.
Tooling remains equal to KT2 3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c.
Library commit 2121ff2d08d50d412c834760af925b202a1d8c01; library tree identical to clean dispatch head
9730eb7286d50bfd956b1180b1211927595283aa; no source changes after clean.
Only request_id, purpose and the approved immutable kani_patch differ between requests.
Same four roots, expectations, generated argv/RUSTFLAGS, controls and fixtures; no weakening for observed clean failures.

| Root suffix (prefix slice::sort::shared::smallsort::verify::uninit_probe::) | CMP2 expectation | Clean result |
|---|---|---|
| cmp3_index_range_len | SUCCESS, zero_to(2).len()==2, cover | SUCCESS, 0/20, cover1/1 |
| cmp4_index_range_len_runtime | SUCCESS, any_where n<=4, zero_to(n).len()==n, cover | SUCCESS, 0/26, cover1/1 |
| cmp3_manually_drop_unsized_len | SUCCESS, unchanged ManuallyDrop/deref/unsize/native len | FAILED, 1/27, cover0/2; unsupported layout |
| pincheck_calibration_uninit_read_u8 | FAILED, Reading from an uninitialized | FAILED, 1/31, cover3/3; incompatible layouts |

Kind diagnostic, uninit/controls true, inventory false; standard4/jobs1, --harness-timeout 3m.
No pre-len raw-read/AddressOf; no real-method/visibility, production patch, runner or trusted-model changes.

## Review, completed clean attempt and budget

Independent Luna HIGH review PASS covers both variant snapshots and the single appended runtime root.
Semantic candidate c39f73c8ef6a2077669d19c6a80a53ffa0751046; receipt INDEPENDENT-REVIEW.md.
Spec SHA256 011daa2bf17ca0b6b8312f62cf020bc6c297b456e062d6651e8f6db1af70d56e;
packet SHA256 f95b1fd8e7045200eb9783adce164f24f958d696bb02f6633067e8003f5cede6.
Activating the exact already-reviewed CMP2 snapshot and recording evidence are within the reviewed candidate;
no new semantic diff, model or dependency. static-cmp2-activation.json checks exact request/library/patch/flags.

Clean build a7061950-0ce5-4776-8d65-fdd686526dd1: Cloud FAILURE, summary COMPLETE, gate FAIL, Kani exit1.
Bounded summary locates ManuallyDrop unsupported [MaybeUninit<usize>;2] layout at array/iter/iter_inner.rs:48;
U1 incompatible-layout transmute at mem/mod.rs:1283. U1 expected uninit check is not established; its covers give no credit.
Native unavailable (no structured native report); Brief HTTP404. Actual argv/MIR/clean applied tree UNKNOWN.
Source-reported results and exact source/tooling/request/head checks are separate from independent proof acceptance.
See CLEAN-OBSERVATIONS.json, CLEAN-EVIDENCE-INDEX.json and bounded evidence/a7061950 receipts.

Clean attempt used1/1; cost $0.1215, outstanding reserve $0 (k1g budget receipt). No clean repeat.
CMP2 attempt0/1, envelope4*3+30=42min, planned reserve$0.5670.
Spent+next reserve$0.6885 <=stage cap$1.20; initial two-envelope reserve$1.1340 unchanged.
Coordinator/client must check current slots/project budget/deadline and exact remote SHA before GO/dispatch.
Preparation does not submit/reserve a Build or modify coordinator/ledger state. Clean GO does not authorize CMP2.

## Interpretation and stop

Actual MIR Constant vs runtime assignment remains UNKNOWN; const fn source alone does not establish it.
No new tracing/tooling or production fix in this task. Preserve unsupported/error and expected-control failures.
Same located failure clean/CMP2: pre-existing; clean SUCCESS and CMP2 FAIL: regression of this fixture;
unsupported/missing or incompatible binding for a compared root: unresolved. Do not transfer prior CMP3 results as this run.
If both direct roots fail only on CMP2, the failure is not specific to literal-bound input; this alone is not causal MIR proof.
After explicit exact-packet GO only: k1g.sh dispatch on this published branch; then k1g.sh watch BUILD and end turn.
Terminal: Brief plus bounded k1g summary/native/native-field/rows; status/budget/tooling; no raw logs/archives/credentials.
Final RESULT-KANI3300-CMP4.md <=25 lines with four paired outcomes, counts/covers/located failures, limitations,
const/runtime comparison, cost and justified next step; no B2/upstream/readiness claim from diagnostic results.
Stop now at PRE-BUILD REVIEW <full published SHA> until coordinator GO; after the second Build close the single stage.
