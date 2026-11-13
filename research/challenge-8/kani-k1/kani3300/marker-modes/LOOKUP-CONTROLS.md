# Lookup controls — DEFERRED, outside the resumed stage

Coordinator accepted the section-2 STOP on 2026-11-13 and removed marker diagnostics
from this stage. See [REQUIRED-STATE.md](REQUIRED-STATE.md), retained unchanged as the
accepted design note. The existing lookup is upstream code; missing private state
remains fail-closed through frameFAIL. No new diagnostic or lookup qualification is claimed.

No compiler lookup resolver, truth-table units, fault injection, marker/state integration
or required-state plumbing is included in the resumed CI request. They belong to the
separate future note/issue and are DEFERRED, not silently accepted or verified.

The original read-only API findings remain available in research commit
`cee401ec22bd96e2b91733e6e2a275618b55f37e`. In particular, symbol-table lookup is keyed
by one mangled name; duplicate markers and ambiguous binding are distinct from duplicate
insertion into that map. No production lookup/target/static was changed.
