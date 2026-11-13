# X1 before/after export map

Paths in the table are relative to the Kani source checkout. Counts are lines,
not a reduction target. The runners gained failure diagnostics and cleanup checks;
actual oracle predicates were retained even where they dominate file size.

| Path | Before → after | Change and predicate distinction |
| --- | --- | --- |
| `docs/dev/kani3300-m2bs-handoff.md` | 27 → absent | Internal historical handoff copied verbatim into research; not a user model-boundary reference. |
| `docs/dev/kani3300-m2bs2-handoff.md` | 34 → absent | Same; provenance/hashes in INPUTS. |
| `tests/json-handler/uninit-contract-oracles/README.md` | 73 → 42 | Self-contained purpose, eight expectations, profile, checks and invocation; remove historical run/worker/capture/proof bookkeeping. |
| `tests/json-handler/uninit-contract-oracles/oracles.json` | 705 → 599 | Move old base/qualification, per-binding semantic_qualification/evidence to research. All actual source/root/hash/check/operation predicates unchanged. |
| `tests/json-handler/uninit-contract-oracles/checker.py` | 263 → 238 | Remove historical evidence-presence guard and receipt-file CLI. Current source/export/regular hashes still checked using an in-memory receipt. The historical guard checked hash syntax/presence, not the current invocation's properties. |
| `tests/json-handler/uninit-contract-oracles/run.py` | 116 → 110 | TemporaryDirectory cleanup, no keep-temps, argv/rustflags receipt duplication or invocation/observation JSON files. Keep runtime hash/exit/time identity in memory; print failure reason, original exit/process error and prefixed regular output. |
| `tests/json-handler/uninit-contract-oracles/test_checker.py` | 487 → 505 | Adapt receipt inspection, retain property adversaries; add mocked timeout and real cleanup checks, remove only the relocated historical-evidence-presence mutation. |
| `tests/json-handler/uninit-contract-mode-boundaries/README.md` | 69 → 47 | Self-contained six expectations, model limits, CC5 grouping and invocation; remove research URL and organizational history. |
| `tests/json-handler/uninit-contract-mode-boundaries/roots.json` | 130 → 111 | Remove redundant unconsumed top-level mode_qualification and per-root source_semantics/observed_outcome/binding_status. Required root/mode/target/companion/expected_result/covers unchanged. Output still explicitly denies mode qualification. |
| `tests/json-handler/uninit-contract-mode-boundaries/run.py` | 91 → 106 | TemporaryDirectory cleanup; remove keep-temps, input receipt and per-root duplicate observation files. Retain ephemeral aggregate report and export/logs until diagnosis, print report before cleanup. Enforce source hash stability; preserve original exits and NOT_RUN downstream. |
| `tests/json-handler/uninit-contract-mode-boundaries/test.sh` | 7 → 7 | Drop leaking mktemp/--output wrapper; runner owns cleanup. |
| `tests/json-handler/uninit-contract-mode-boundaries/test_observe.py` | 351 → 407 | Add cleanup and malformed/null/wrong-type/partial/wrong-root/source-change/exec-error diagnostics and downstream NOT_RUN tests. |

`uninit-contract-mode-boundaries/observe.py` is byte-identical to the base,
including CC5 source cover grouping. All Rust fixture bodies, reference model
boundary documentation and files owned by W14 are unchanged. There is no new
framework, CI capture code, wildcard golden or production guard. Persistent
receipts/GOTO collection belong in a separate coordinator CI-only overlay;
the regression test does not preserve its temporary directories.
