# Independent W14 count delta — APPROVE

**APPROVE** exact repaired candidate `9c4ce67e06a652413fa72d9678f93962da5a2e1e` for task `0414fdbdf784f07abb1ca6a7c020d1c8064c8e39`. W14-B1-01 and W14-B1-02 are independently CLOSED. No remaining findings or blockers. Owner07:26 `/new14` issues this fresh review and overrides the task's prepared/context-reuse wording. No GO or execution grant is conveyed.

| Binding | Exact identity |
|---|---|
| Repaired CONTROL | `d675ef70dc1ada13330efc0990c2e1d6b0d21a5a` |
| CONTROL tree | `6280a305cba669f59ae82119fcf5374115ecacf7` |
| CONTROL sole parent | `9e14e033f9ee31522b571c127609dcdff76d230b` |
| SOURCE | `f1bdf11902252ad1178f42403c253ae710fecbaf` |
| SOURCE tree | `f7856aae7ad610f0e89e7c54cff8062fa3c3b3f0` |
| SOURCE sole parent | `97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a` |
| Stock TOOL | `0aac16ef62da9e9d5645782d458593e5d78143ba` |
| TOOL tree | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |
| Request SHA256 | `23c137a331acb92610b3f0cf2192a0e16081dbf0815a35fc3c8d88742c0a1fa3` |
| Workflow SHA256 | `317f92181bee9470ddf65471def7154fcacbf1e6fb7913220ca1f154ca915a55` |
| Inherited full review | `4bd906e8fe1e2dc78afef74d32db8b9e14c2db7e` |

## W14-B1-01 — independently CLOSED

`s34_campaign.finalize()` calls `p.validate(request)` before reading the selected inventory. That validation checks the exact profile and seven-row order through `s34_policy.validate_request()`, including the unchanged modes, targets, flags and policy. The writer now emits `len(request['rows'])`, a genuine integer7. It never derives selection cardinality from completed seals or observed rows.

The shared `s34_campaign.collect()` validates the request, then requires a dictionary campaign metadata object, `type(selected_roots) is int`, and equality to the validated selected cardinality before calling the legacy collector. Missing/null/bool/string/float/0/6/8 reject without a default or coercion. Public local and compact-only upload dispatch both use this gate. All existing downstream terminal, identity, seal, source/stage/target, status, role, guard and lifecycle checks remain byte-exact after the inserted gate.

The independent reproducer uses the existing real Python file/hash/controller/writer/packer fixture. Only native execution, Git telemetry and resource supervision are synthetic. Baseline and repaired imports run in separate processes and assert exact worktree HEAD, cleanliness and module origins. No dummy executable, compiler or solver is run.

| Repaired scenario | Launched / completed | Writer selected | Preserved result |
|---|---:|---:|---|
| Full | 7 / 7 | int7 | Seven sealed rows accepted |
| STOPPED | 3 / 2 | int7 | Two sealed rows; interrupted third UNKNOWN; later NOT_RUN |
| SELECTED_PARTIAL | 3 / 2 | int7 | Same sealed prefix and unfinished statuses |
| STOPPED before launch | 0 / 0 | int7 | All NOT_RUN, collector outcomes UNKNOWN |
| SELECTED_PARTIAL without completion | 0 / 0 | int7 | All unfinished; no fabricated completion |

Each of these five scenarios accepts genuine7 on BOTH public local/upload-only routes and rejects all eight adverse cases on BOTH routes: **10 acceptance checks and80 rejection checks**. Upload directories contain only the packed structured member. Nonterminal structured bytes and the durable prefix are preserved across the count mutations. Six additional operations reject shortened/reversed request inventories through writer/shared/public collectors without changing terminal bytes. See `repaired.stdout`.

The independent frozen baseline reproduction still writes8 after seven launches/seals and accepts genuine7 plus every adverse variant on both routes (18 acceptances). This preserves and distinguishes the original failure; it is not relabelled a repaired result. See `baseline.stdout`.

All four added regression methods are explicitly present in exact committed `s34_validate.NEW`. The byte-exact workflow invokes `python3 s34_validate.py` in its18minute Validate step. Each new method also appears as an individual PASS in the exact final267-test receipt. This closes the omitted-from-CI regression concern.

## W14-B1-02 — independently CLOSED

`PortableReplayTests.exercise()` now validates the inventory and compares collected rows against `len(req['rows'])`, which is seven for this profile. Its other substantive stock metadata, protected snapshot, identity, portable replay and error checks retain their original bytes.

The corrected standalone method actually passes in the author's separate1-test receipt. This reviewer independently ran that same method together with the four new count tests: **5 tests PASS**, exit0,15.829661s wrapper. See `targeted.json` and `targeted.stderr`. The standalone method remains separate from the selected267 suite; no claim is made that the original263 suite ran it.

Original review4bd remains REQUEST_CHANGES for original candidate `bcc103354d1418feeda043c6b955b38bb4393598` / CONTROL `b9e57f09775ed9db249e0b1b6f8e7e53bde5e60f`. Its isolated `7 != 9` FAIL, original263 PASS and old repro/receipts remain immutable. This approval binds only the repaired packet above.

## Invariance, identities and final timing

465 independent integrity/static assertions PASS. The exact packet contains56 committed files and55 manifest hashes. SOURCE, CONTROL and TOOL full working-tree status is clean; trees, sole parents and required ancestor availability within checkout7/5/2 match. All six packaged source/control patches independently replay through temporary Git indexes to their exact expected trees.39 source dependencies,75 committed authored dependencies,100 payload hashes and58 protected control files match their bindings. Four source-only gates PASS again; their scope remains static consistency rather than compiler/type/MIR resolution.

The complete old/new CONTROL tree comparison changes exactly five paths: request, campaign, Validate list and the two related test files. The request changes only four payload-hash entries; all other request fields and the workflow are byte-exact. Eight source/domain/cfg/oracle/resource/open-obligation maps are byte-exact to the original packet. Full original source, Cell, Original/PFC, cfg, U/location/guard/status/oracle/source-identity, lifecycle and runtime assessment is therefore inherited from4bd by object/byte invariance; this is a count delta, with no new broad source-design assessment.

Only insertion is PFC. Positive sort9, Cell fallbackN0..16 and u8 networkN0..8 remain Original/targetnull, with seven-row order, full-byte domains, modes, unwind bounds and flags unchanged. U remains REJECT_ALL/proposalDISABLED; nonempty unsupported guards remain strict, including SUCCESS. Prior ff193/f740 location cases do not transfer to future run/IDs. The count patch neither weakens the downstream gates nor changes any native runner or resource-control implementation.

The new committed final host receipt reports one full Validate: **267 PASS =136 legacy +56 S3-1 +35 S3-2 +40 bridge**, exit0. Reviewer inspection matches every ordered individual PASS, stdout result, control/request/tree binding and clean before/after identity. Wrapper632.582332670s; internal632.177610136s; `1080 /632.582332670 =1.707287643`, exceeding the required1.5 margin. Exact sourcepreflight reports one PASS in24.242099s; controlpreflight PASS in0.577142s. These are committed execution receipts, independently checked for consistency; this reviewer did not rerun full Validate or sourcepreflight. Host synthetic timing does not establish future CI speed or native fit.

Caps remain local6GiB sampledPGID/outer12GiB/reserve2GiB, Ceff=min(6,12,A-2), child600 including compile180, slot720/controller180/cleanup240, campaign6900/outer7500/step7560/phase8100/setup1800/job180min, and outputs16MiB/1MiB/8MiB/256MiB. Seven-slot5460 is only an envelope. No cap increase, eighth root or automatic rerun is introduced.

## Authority and limits

Only `bridge-1-review-r1/` review outputs are committed, with `[skip ci]`. No candidate/source/control/tool edit, subagent/model change, native execution, fullValidate rerun, CI, push, ledger change, reservation, external message or raw-evidence acquisition occurred. Item1 remains31/31 EXHAUSTED; item2 remains13/17; total44/48. Prospective14/17,total45/48 is unreserved arithmetic.

Root may now prepare an exact GO request for this approved packet. Separate user/coordinator GO, publication, dispatch and accounting of ONE attempt remain required. No admission or proof promotion: qualified new leaves0; generic Rust/type/MIR/init/B1/B2/fullS4/native proof and actual cost/fit remain unestablished or NOT_RUN. Original open obligations remain open.
