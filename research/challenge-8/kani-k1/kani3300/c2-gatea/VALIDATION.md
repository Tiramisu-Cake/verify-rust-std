# Local preparation validation / NOT_RUN

Only Git, static Python/YAML/Bash parsing and synthetic shell tests are authorized. No frozen setup/regression scripts, toolchain/verifier, push, dispatch or CI executed. Cloud $0.

Initial source HEAD/tree/status and local fix ref matched exact inputs. Research HEAD f7e5b555c7; S6 curated acceptance also checked at b624253cb6. Required curated inputs and all frozen setup/dependency/script identities recorded in EXPORT-MANIFEST.json.

Initial static workflow check passed: YAML parsed with PyYAML BaseLoader; only workflow_dispatch, fork guard, contents:read, exact three matrix labels, fail-fast false/max-parallel3,360min job cap, common concurrency/cancel false, two exact checkouts, own frozen setup with OS/kani_dir, Bash syntax for every inline run step.33-stage binding file hashes and source lines verified against frozen source.

Final synthetic results, overlay parent/path/hash checks and independent review follow below when complete.

Real macOS/ARM execution, runner availability, setup/binary inventory and actual full regression load remain unvalidated until coordinator CI. Synthetic success is not Gate A evidence; Gate A NOT_RUN, formal proof credit NOT_ESTABLISHED.

Final local validation: `python3 -m unittest -v test_receipt test_lifecycle` — **26 tests passed** (14 observer,12 lifecycle),4.306s. Exact test names/results in SYNTHETIC-TESTS.txt; only synthetic results, not CI receipts. Includes actual full33-stage synthetic shell through hook/capture/parser; original nonzero/EXIT/missing/repeated/order/counts/filter/overflow; process-group timeout/signal/output cap and exited-leader descendants; setup-only fallback, source SHA/tree/dirty/untracked/unbound-file drift; missing/failed/null matrix receipts and status-only rejection; metadata cap.

Python AST/import checks, generated hook and all workflow Bash syntax, YAML guards/triggers/matrix/caps/checkouts/frozen setup/uploads,22 frozen file SHA-256 identities, bound symlinks/subtrees and33-stage source-line map PASS. Actual read-only source passed lifecycle pre-setup validation of clean HEAD/tree/files/subtrees/gitlink pins/symlinks. No setup/submodule initialization performed locally.

Final commit `e795403859f5b61e37b5bae9dce705b9a8ede8e0`, tree `42ce47f065ae6aeb3c9ad23d1b15f95d7a0e82f7`, sole direct parent `ad499e41dd2db9ccd432f89721638a1f3a0bbd44`; exactly one commit.22 changed paths, all allowed:16 stock workflow deletions, new manual workflow and5 gate-script/binding/test additions. All frozen source/deps/tests/docs and .github/actions/setup unchanged. Overlay status clean. Patch SHA-256 `85dcce641c9587f22e0bbdf94137ede2299ed0e3adec77a03cdfd0f15ea371c2`, 184542 bytes. Research remains uncommitted; source HEAD/tree/status rechecked separately.

Final reverse patch apply --check PASS without applying changes. Final research JSON/patch/per-path hashes and FULL-GATE-REQUEST overlay identity PASS. Original source still ad499e41dd2db9ccd432f89721638a1f3a0bbd44/tree9829702c1aa0ecb73c860fc0ad5451757917d6cb and clean; local overlay clean. g0 remains f7e5b555c7b0068d933ceb358846285b2288cb51 with only this research package untracked. No push/dispatch/CI. Gate A NOT_RUN.
