# PRE-BUILD — KANI5116 KF1 repair 1

Candidate: full pushed SHA in the PRE-BUILD REVIEW marker. No repair dispatch before fresh exact-packet coordinator GO.
Branch `experiment/kani-k1-kani5116-20261110`; owner `k1-merge`; slug `kani5116`; stage `kani5116-kf1`.
Original T0 remains the coordinator GO preceding first dispatch (recorded dispatch timestamp 2026-11-10T21:34:14Z); main 360 + closeout 30 minutes from GO, no clock reset.
This is the only repair permitted by the KF1 task, a fixture compilation fix after Build 1. No scope expansion.

## Build 1 evidence and diagnosis

Build `f9143491-2674-408d-8eaf-2a0dfe8adc91`, approved source `f0fae09d78f365303beb34ac262ab0e193e8ed2b`: Cloud FAILURE, summary TOOL_ERROR, gate false. Kani built successfully.
Bounded `k1g.sh summary/native` evidence is VALIDATED: all 19 requested tests ran; 18 native PASS and one FAILED/ERROR. All ten existing regression selectors and all four new positive fixtures passed, including the original #5116 repro. No timeout/ignored outcome.
The only failing selector was `expected/function-contract/specialization_default_requires_fail.rs`; neither its golden nor the required own-output diagnostic matched, so no precondition-failure credit is claimed for Build 1.
Its own `kani_stderr` line 15 reads: `error: stub verified target `<T as Probe>::probe` does not have a corresponding `#[proof_for_contract]` harness`.
Own stderr path: `/workspace/src/k1-out/native-5/function-contract/specialization_default_requires_fail/specialization_default_requires_fail.err`; 1063 bytes, SHA-256 `300aedfbb69f202cb4806ac2c06c8a1a03cbc299c9ae413a479ec1d542c8d406`.
The excerpt is diagnostic_only, 17 selected lines / 183 omitted; all four source-match flags are false for the requested precondition diagnostic, selected_source=null. No raw-log fallback, no change to gate policy.
The pinned `kani-compiler/src/kani_middle/mod.rs` emits this exact missing-proof-harness diagnostic. The fixture alone lacked that mandatory harness; production defaultness expansion and every existing regression selector passed.
`check-tooling` against `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`: PASS for pool, all lane paths, six bound blobs, request and patch identities. Build 1 applied tree `a5782891059cd86d4129056d992819ecf25b3945` equals original preflight.
Kani/compiletest builds: 253/16 s. Cloud start 21:36:14.852869967Z, finish 21:44:28.171043Z (493.318 s). Selected-build ledger: **$0.1215 actual, $0 reserved** (9 billed minutes).

## Exact repair

Only **six lines added** to the new negative requires fixture: a comment plus `#[kani::proof_for_contract(<u16 as Probe>::probe)] fn check_contract() { <u16 as Probe>::probe(kani::any()); }`.
This proves the same default method's contract under its existing precondition. The original stubbed caller still passes zero and must fail the unchanged `value != 0` assertion.
The production macro patch, every other Rust fixture, all five new golden files, all existing golden files and all 19 manifest entries are unchanged from Build 1. No test removal or weakened expectation.
Full patch diff against Kani pin: production **3 files +52/-11**, tests **14 files +429/-0** (9 Rust + 5 golden). Incremental repair: 1 fixture +6/-0.

## Identities

- Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; nightly-2026-10-23 unchanged.
- Tooling base for KF1 remains **`c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`**; original accepted base `383fd7089550aeabac3ad92366cd7c71e2f237ee`.
- Local Kani commit `b7314d9bbfbbeae00f9c81e654bf6bf172932037`, `/root/kani-fix-5116`; no Kani push.
- Request `kani5116-kf1-repair1-20261111-02`; SHA-256 **`f951412a7c999d2c01310d9a719d1e841bc6fbdfed0dfe1774d2769b4fcc9714`**.
- Full patch path `research/challenge-8/kani-k1/kani5116/kf1/kani-fix.patch`; SHA-256 **`fd510b8a47ffff2005cc2362af6c25db790d1b579a23c0c990f6d606a983aa71`**.
- Expected applied tree **`46f37ae9abe9bb747ec7b7de33212484ed175a1b`**, equal to the local Kani commit tree. Fresh-pin preflight and full diffstat recorded in `repair1/preflight.json`; original `preflight.json` retained for Build 1.

## Manifest, checks and budget

The exact 19-selector manifest, groups, required diagnostics, edition flags and prior NOT_RUN exclusions are as listed in `PRE-BUILD-KANI5116-KF1.md`. Manifest bytes and `kani_tests` are unchanged; every expectation remains pass. Native negatives still require their concrete own-output diagnostic and their original golden; positive expected tests still use `--require-success`.
The negative requires fixture must now pass compiletest's golden check by reaching the invalid stub caller; a matching setup/compiler failure earns no credit. Both harnesses run within that same selector.
Static checks PASS: request/schema validation; fresh clean checkout apply check and indexed apply through unchanged prepare_kani; all 19 fixtures / 12 expected golden files; applied-tree equality; rustfmt zero diff on all 12 changed Rust files; git diff --check; zero diff in all tooling/lane paths against KF1 base.
The 109-test Python tooling suite passed for the unchanged tooling base; no repeat suite or local cargo/rustc/Kani/CBMC run is needed for this six-line fixture fix. No credentials, raw logs, archives or competing code read; no subagents.
Unchanged reserve: **29 work + 30 overhead = 59 paid minutes**, standard4 $0.0135/min = **$0.7965** maximum; verify cutoff at validation start + 53 min, child 180 s, outer <=210 s, one test thread.
Independent KF1 ledger: Build 1 **$0.1215** actual + repair reserve **$0.7965 = $0.9180 <= $1.50**. No other KF1 build or repair is authorized.
Cumulative branch: historical KT1 $0.3510 + KF1 $0.1215 + repair reserve $0.7965 = **$1.2690 <= $2.30**. Project and branch ledgers are rechecked atomically by dispatch.

## After fresh GO

Dispatch the exact pushed candidate, invoke `k1g.sh watch BUILD`, then end the turn; no status polling.
After wakeup, inspect bounded summary/native pages and all 19 native outcomes. Run `check-tooling BUILD c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`, compare pin/patch/request/applied-tree identities above, and obtain selected-build cost with `k1g.sh budget FIRST_BUILD REPAIR_BUILD`.
Update RESULT within 45 lines and UPSTREAM-PR-DRAFT within 10 lines, preserving Build 1's failed status. No further repair without a new coordinator decision. Then REVIEW REQUEST <sha> / KANI5116 KF1 ЗАВЕРШЁН, stop.
