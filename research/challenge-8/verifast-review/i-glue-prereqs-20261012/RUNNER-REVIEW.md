# Independent pre-dispatch review — C0–C2 Cloud runner

Status: **GO for the first authorized C0–C2 Cloud dispatch; all proof results
remain raw/pending until full-log review.** This reviews the final recipe,
`run.sh`, `runner.py`, fixture manifest/matrix, `control.py` phase addition, and
current source fixtures. It is static review, not a Cloud or proof result.

## Confirmed bootstrap closure

The compressed I patch SHA-256, decompressed patch SHA-256, and all seven I
effective source hashes in `manifest.json` match the pinned `b6cb276a` tool.
The patch changes six files; the seventh pinned schema is unchanged stock.
`run.sh` checks the exact stock checkout and schema, pins the rustc commit, applies
the I patch before the additive patch, builds the exporter, console, and official
refiner, and records changed source and binary hashes. The recipe names the
runner, entrypoint, manifest, fixture pairs, and both patch deliveries. All 11
fixture source-pair hashes currently match `fixture-admission.json`.

The audit path is correct: `runner.py` writes `allprooflogs/proof-audit.json`,
which `package-evidence.py` explicitly accepts. The new `control.py` phase is
limited to owner `verifast`, the exact lane, 3600-second account, and session
window; it does not open another lane.

## Earlier findings and final closure

1. **Overlap fixture syntax — resolved.** Both runtime sources now cast
   `&*tmp as *const u64 as *mut u64`; paired digests were repinned. The Cloud
   first diagnostic still decides whether this reaches the intended assertion.

2. **C0 setting coverage — resolved in the runner.** It now executes profile
   off, invalid zero/empty, partial setting, four actual native modes,
   selector and generated-glue zero/presence controls. Each setting negative
   requires its exact first refusal at the settings gate.

3. **C2 metadata/binding controls — resolved in the runner.** The final loop
   executes eleven layout/compiler/source/field mutations and both wrong
   MIR/local binding modes against the unchanged positive source pair. Their
   mode markers plus exact first diagnostic are required; generic digest
   refusal earns no credit.

4. **Read-only destination negative — classified.** This is a checked
   `safety_proof` permission-refusal control: quarter destination permission
   cannot close the full destination array before `call()`. It does not claim
   a method-body copy-write failure; the exact first diagnostic remains the
   Cloud acceptance criterion.

5. **Positive and negative qualification.** The runner correctly labels raw
   outputs pending review and grants no negative credit. Its provisional C2
   positive condition is only verifier exit zero, printed zero errors, and no
   matched dead-code line. Before a final verdict, inspect the actual target
   execution count, method body and `safety_proof` entry, normal/unwind posts,
   lifetime/leak checks, paired official refinement, and first diagnostic of
   every negative. A capture/refiner failure before proof remains a setup or
   admission result, never the intended proof negative.

The final manifest pins tool commit `059687f190dc528338ea854566f0c1dc57375888`,
tree `f299edd9b8c4e1283cb377b50681697de90d8a60`, additive patch SHA-256
`dc9950d5d5500dfbfae70b1c0ccd86b3e752b05294559e6b74acc4a8ecbc34de`
and eleven effective file hashes. The patch and tree values independently match
the reviewed tool repository. `tool_head` remains a provenance label; effective
bytes and executable hashes are checked independently by the runner. No Cloud
build, verifier or proof was run locally.
