# B3 T1b-r2 — READY package, NOT RUN

2026-11-15. Separate B3 T1b-r2 correctness task, not C2. This request supersedes
the original CI-REQUEST.md for a new capture; historical run/results are unchanged.
Research parent: `43b065bb9d0fc78cb66aef81584a8241a85f461d`.
Kani CI parent: `1a8faa3b60ee9a19534cdb57315e8887f5666301`.
Kani CI candidate: `3694410bd4650f9d3dd0f43cc49aeb963892a197`.

## Coordinator run

- Publish/trigger only `uninit-ci/b3-t1b-r2**`, workflow `.github/workflows/b3-t1b.yml`.
  The former T1b workflow file is replaced by the r2 trigger. T1 still explicitly
  excludes all `uninit-ci/b3-t1b**`; no other workflow files exist at this candidate.
- One ubuntu-24.04 job, at most 60 minutes, attempt 1 only, no retries.
- Same input: `Tiramisu-Cake/kani` run `43701550489`, artifact
  `b3-t1-43701550489-1`, outside checkout. Missing/expired input is INVALID.
- Reuse the original strict 409-record/131-final-per-arm validator, record/file
  hashes and provenance/tool/lock census. Install the same prebuilt CBMC 6.11.0;
  require the goto-instrument binary SHA256 from every arm's T1 tools.json.
  No model generation, Kani build, compiler, solver or SAT invocation.
- Capture all 393 final/linked/symtab logical models in A1/A2/B1: 1179 function
  dumps and 1179 symbol dumps. Symbol tables are recaptured with exactly the old
  verbosity 4 method so r2 is self-contained and independently pairs both displays
  with the same validated model hash; it does not depend on the previous 3.3 GB
  text artifact. Function dumps use verbosity 6.
- Upload `b3-t1b-r2-<run_id>-1`: RESULT.json, INDEX.json, source indexes/tools,
  command events and original stdout/stderr, function content/status splits,
  six repeat displays, tool/install/version output. Original stdout is never edited.

## Source check and narrowly separated status

Checked the local Git tag `cbmc-6.11.0`, commit
`820ff0f555b43fb78e0cd9332e498461bd14244b`, in `/root/cbmc-zst-prready-ci`:

| Source | Relevant behavior | Git blob content SHA256 |
|---|---|---|
| `src/goto-programs/show_goto_functions.cpp` | plain output uses `msg.status()` for each available body's separator, symbol header and `body.output()` | `5815194c0c55b6a7bd07b0a726f592201ecd4931cd39660f1dad680a97114727` |
| `src/util/message.h` | `M_STATUS=6`; level 4 suppresses status | `34f753f5fd16aea78ca03060fd7d83522aef2a12bc6cb70e322d4e78059bc189` |
| `src/goto-instrument/goto_instrument_parse_options.cpp` | `get_goto_program()` emits `Reading GOTO program from '<argv input>'`; display branch invokes `show_goto_functions` and returns | `99f91f53a59e5b3702fa1a7a17f49cb85a9d0448f30d474383a6fb825165c322` |
| `src/goto-programs/goto_program.cpp` | instruction location comments, instruction text and terminal `END_FUNCTION` | `328a4f0ba96bfdd5467236b29a1e5a492b510aeb07907699b04f762ed3b94508` |

This corrects the original DESIGN.md's claim that the function printer is
independent of verbosity. No backend binary was run locally to establish it.

At verbosity 6 the single input-path status prefix is arm-specific. The parser
requires precisely `Reading GOTO program from '<exact command input>'\n` at byte
zero, once, and saves it to `.status.txt`; the suffix is saved to `.functions.txt`.
No other path/status/comment/location/number/whitespace line is removed. Unknown
prefix, missing/wrong/repeated banner and unexpected framing fail closed.
Both derived hashes and their relation to the raw hash are independently checked
offline. This separation removes only a source-established file-read announcement,
not program text, and does not conflate the A1/A2/B1 input identities in the index.

Every primary and repeated function dump must have available-body separators,
unique nonempty symbol headers, numbered instruction-location comments and one
terminal END_FUNCTION per printed body. Empty/status-only/list-only/truncated
displays are INVALID. Every display command must exit 0 and have empty stderr.
The command event retains the original exit even when a later content check fails.
Three distinct final inputs, one per arm, repeat in both modes: six raw hashes
must match before any normalization or status separation.

## Offline classification after artifact download

CI success means **CAPTURE_COMPLETE_OFFLINE_REQUIRED**, never model equality.
Classification is deliberately outside the job, using the same normalizer:

```sh
python3 -I research/challenge-8/kani-k1/kani3300/b3p/t1b/offline.py \
  /absolute/path/to/b3-t1b-r2-RUN-1 --r2 --output /separate/path/r2-analysis
```

Do not execute scripts/commands from the downloaded artifact. `offline.py --r2`
loads the local `offline_r2.py` and `function_dump_r2.py`; the latter is byte-for-byte
the candidate CI framing parser. The original symbol normalization implementation,
POLICIES, stages and repaired union-edge control gate are unchanged. Root offline.py
changes only its CLI dispatch; the historical RESULT-OFFLINE.json source hash
continues to identify the original script at `43b065bb9d`, not the extended CLI.
Historical results/validation receipts are not regenerated or rewritten.

The reader verifies capture completion, pinned task/CI-parent/source-CI lineage,
source run/artifact, input indexes and
model hashes, source tool hashes, exact command mode/tool/input/verbosity, exits,
stderr, raw/derived hashes, body census and the six raw repeats. These are artifact
consistency checks, not independent authentication of the source capture/binary.
The offline result starts INVALID before validation and is replaced atomically
after classification, preventing an old accepted result from surviving a failed read.

Function bodies are compared **exactly** after the exact prefix split. No new
AllocId/local-name/location/instruction-number/order normalization is guessed for
the previously unavailable function printer. New A/A body differences remain in
unified diffs and require evidence-based investigation before any new rule could
be accepted. The symbol-only equality from run 43708572925 is not reused as body
evidence. This intentionally conservative first capture may be INCONCLUSIVE_AA.

All A1/A2 comparisons complete before any A/B comparison; B_DIFF contains only
stable A/A keys. All three control stages require A1=A2≠B1, the unchanged parent
union edge and empty Unit, exactly `[Unit; 2] -> Unit` in the one wrapper Type,
and unchanged padding/other symbol text. Function control text must currently be
identical: any new function-use change fails INVALID_CONTROL for inspection,
instead of being presumed wrapper-only. Thus every accepted control difference
is exactly in the wrapper, and function changes can never silently receive credit.
Noncontrol residuals are SYMBOL_CHANGES/FUNCTION_CHANGES with diffs, conservatively
OTHER_CHANGES; no speculative WRAPPER_ONLY classification is issued.

`RESULT-OFFLINE-r2.json` includes AA_EQUAL by kind, AA_DIFF, B_PAIR_DIFFS/B_DIFF,
control gates, per-arm stage/body hashes, policy counts, parser/driver/source hashes
and residual unified diff hashes. INVALID_CONTROL, read failure or INCONCLUSIVE_AA
admits no B3 conclusion. Equality concerns this captured profile only, with no
SAT, B1/B2, formal proof, performance or harmlessness credit.

## Preparation validation

- `test_offline.py`: 13 original normalization/control-preservation tests.
- `test_runner.py` classes Validation + Commands: 11 input census and subprocess
  success/error/timeout/partial/missing/null/wrong-type/NOT_RUN/provenance tests.
  Its historical Orchestration class targets the superseded integrated classifier;
  r2 orchestration is covered separately below.
- `test_r2.py`: 7/7 PASS; synthetic full 393-model/1179-body capture and offline comparison;
  exact source prefix/body framing, malformed/empty/partial output; function
  mutations, sensitive control, missing/partial/wrong source/command/verbosity,
  failed/timeout command records, INVALID sentinel, original RESULT preservation.
- Static workflow branch isolation and Git diff whitespace/scope checks.
- Independent Luna HIGH review: PASS after fixing the pinned CI/research lineage
  validation/retention gap; delta review accepted the lineage checks and INVALID
  sentinel/atomic result replacement. No nested delegation.
- Total targeted tests: 31 PASS (13 + 11 + 7). Final r2 suite: 37.307 seconds.
  YAML parse, push-only triggers, r2 branch isolation, Python AST parse and
  unchanged original symbol-normalizer implementation checks all passed.

Preparation does not push, submit CI, create a PR/issue or run local builds/backends.
