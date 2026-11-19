# Intermittent codegen_cache regression failure: no cache statistics were printed

`tests/script-based-pre/codegen_cache` intermittently fails with `FAIL: no cache statistics were printed.` The script runs `CACHE_STATS=1 kani fixture.rs`, captures stdout and stderr, and requires the `***CACHE STATS***` marker. A successful invocation using a debug compiler should emit cache statistics that the regression can check. The reported failure is an absent marker rather than a hit-rate assertion.

Reported occurrences in upstream merge-queue CI on 2026-11-19:

- [#5201 queue run](https://github.com/model-checking/kani/actions/runs/44590803353/job/135795963590), ubuntu-22.04.
- [#5045 queue run](https://github.com/model-checking/kani/actions/runs/44605372437/job/135847524728), macos-15-intel.

The same symptom was reported in a [fork run on ubuntu-24.04-arm](https://github.com/Tiramisu-Cake/kani/actions/runs/44633285784/job/135945260201). A separate [fork ubuntu-22.04 failure](https://github.com/Tiramisu-Cake/kani/actions/runs/44616139446/attempts/1) passed on [retry](https://github.com/Tiramisu-Cake/kani/actions/runs/44616139446/attempts/2). These results suggest an intermittent regression/statistics-output problem; they do not establish the root cause.

The instrumented cache emits statistics from its macro-generated Drop implementation when `CACHE_STATS` is set; the cache is thread-local. Investigation should distinguish compiler binary/build profile (`debug_assertions`), environment propagation, cache initialization/use, owning-thread termination/Drop, and output capture. TLS-destructor timing is only a hypothesis. There is no deterministic standalone reproducer yet. Removing the marker assertion or weakening the regression would hide the symptom.

AI assistance: this report was prepared with OpenAI Codex.
