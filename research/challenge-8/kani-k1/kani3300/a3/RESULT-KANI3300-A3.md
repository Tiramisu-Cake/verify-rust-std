# KANI3300 A3
- Выполнена только TASK-KANI3300-A3.md из 0fbd976d7f; база A2R b207847932.
- Kani final: `0b1d68ac691cac7e03dbe73f4aec139bb5389059` (локально, без push).
- Общий caller/callee predicate; явный current-call protocol; обязательный normal return0, включая ordinary union.
- In-place shadow Call(Move): снимок witness до очистки полного extent; Copy/assignment/forget и original при temp сохраняют поведение.
- Три selectors, 21 harness: ожидания 9 SUCCESS / 12 именованных FAILURE; это не измеренные outcomes.
- rustfmt wrapper --config-path rustfmt.toml --check, diff --check и static inventory PASS; clippy/-D warnings — source audit.
- Независимые Luna HIGH reviews: REVIEW-CORE-FINAL.md, REVIEW-TESTS.md, REVIEW-COVERAGE.md; initial REVIEW.md сохраняется для packet identities.
- Compilation/MIR/Kani/CBMC/Miri NOT_RUN, proof credit NONE; Cloud $0; CI выполняет только координатор.
- Scope/ограничения/точные fixture hashes: NOTES.md и TEST-MANIFEST.json; следующие стадии не выполнялись.
A3 READY 0b1d68ac691cac7e03dbe73f4aec139bb5389059
