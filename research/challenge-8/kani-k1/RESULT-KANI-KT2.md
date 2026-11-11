# RESULT KANI KT2
Tooling base: `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c` (author Tiramisu-Cake; [skip ci]).
Diff: failed-check lines precede error/tail; terse + File and regular Check/FAILURE/Description/Location.
Preserved source order/clipping; added failed_check_line_count and omitted_failed_check_line_count.
New command: `k1g.sh native-field BUILD OFFSET FIELD [START [COUNT]]` (dotted keys/list indices).
Field pages: arrays, object entries, Unicode codepoints, scalars; build/offset/file + summary path/SHA; next_start.
Unknown fields/bounds, missing/malformed/null/wrong-type reports and oversized units return bounded-style errors (exit 2).
Tests: `python3 -B -m unittest discover -s research/challenge-8/kani-k1/tools` — PASS, 117 tests.
Includes failed-check priority/omissions/Unicode/long lines, no gate-credit, field pagination, service error paths.
Targeted `test_gcb_native.py` — PASS, 9 tests; `bash -n` and `git diff --check` — PASS.
Retro CLI U1T ff0988c7-d2f2-4872-b4ea-be581d9de02f, offset 1, output_excerpt.records, COUNT=2:
START=0 → count=2,next_start=2,1131 bytes; START=2 → count=2,next_start=4,1117 bytes; PASS.
U1T summary SHA256: 76a9b685ebe8554502f8a737f030c92575b8d32d5c929f9af8e47e1b682f448a.
Retro CLI U3 14dd0792-1c06-47be-b931-94f6096a664a: offset 1, same field, START 0/2 → next 2/4; PASS.
U3 summary SHA256: d9a45dc19dfe3d1d4959864ab3c04c3af991a5782df7cee700b1f31b42b4083b.
Retro used existing cached summary.json only, fake auth; no raw output read or retrospective excerpt run.
Unchanged: gate/provenance (diagnostic_only), 60 lines/4096-byte excerpt, 220-char/260-byte clipping, 12000-byte pages.
Unchanged: lanes/workflows/GCB YAML, Kani pin/toolchain; no Cloud/dispatch or local proof tools ($0).
Independent Luna HIGH review: ACCEPTED candidate 3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c; no blocking findings; 14 targeted tests PASS.
Review spec SHA256: 7fb7af5fb910c2f2493a04650cdeddbfa59188d1baa898a5fc226f79314ee6f8.
Review packet SHA256: d014b4640244456c6d593b0bf60e4cf4b6ba5ebf8fe8749bd0929a6f416771de; no formal proof credit.
REVIEW REQUEST 3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c
KANI KT2 ЗАВЕРШЁН
