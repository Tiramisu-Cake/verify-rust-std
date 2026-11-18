# Offline validation

Final candidate `b678fb6cdd5edf69a4e952167422f36a45a3d6cb` / tree `beb2346615ffbb7027b2f1ea8ea33a149952aa0b`: **29/29 PASS** on the final code,
command and exact transcript in VALIDATION.json and TARGETED-TESTS.txt. Python
fixture children only; no compiler, Kani, CBMC, full runner, or CI.

The preceding expanded static/service selection passed 69/69 before final
rich-parser/diagnostic-I/O error-path hardening; INTERMEDIATE-TESTS.txt identifies
that stage. The final 29 tests cover all changed execution, compile, finalization,
packing and fallback paths, plus both new hardening regressions. An earlier
68-test attempt exposed a preview snapshot race; its failure is retained in
RESOLVED-PREVIEW-RACE.txt. Preview updates now precede diagnostic persistence.

The regression deliberately places two stdout errors in the omitted middle of
168KB of text and an ANSI stderr error outside its 2KB previews. It asserts
absence in old captures and exact retention of multiline context/byte offsets
in diagnostic receipts and compact group evidence. Additional tests exercise
one-byte headers/UTF-8/ANSI, no-newline EOF, producer count gaps/suppression,
observed dropped byte/block counts, timeout/signal/output caps, spawn/read/write
failures, missing/null/wrong-type/NOT_RUN data, fallback interruption and compact
cap projection without rewriting source receipts. Existing service controls
retain original exits, exceptions, snapshots, UNKNOWN/NOT_RUN and proof credit.

`python validate_package.py` checks exact clean control/source/tool identities,
request binding and immutable matrix/caps, payload hashes, static source/PFC,
offline control preflight, and all three patches replaying to the exact tree.
It submits no work. PACKAGE-CHECK.json records the result.

Production retention is **NOT_RUN**; historical compile cause remains **UNKNOWN**.
No proof credit or budget/accounting change.
