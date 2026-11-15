# Offline validation — PASS

15 Python synthetic unittest methods passed (parent run5.992s, exit0); structured
method list and exact tested code hashes are in VALIDATION.json. Cases cover child
success/intended failure, signals/group timeout with surviving descendants, stream cap,
setup-only/UNKNOWN, parser missing/partial/null/wrong-type/selector states, wrong pin/tree/
fixture, post-run drift, missing row, native/std mode mismatch, frozen RSS and bounded
artifact truncation. All executions use synthetic Python children or mocks.

The offline YAML1.2 duplicate-key/context checker, bash -n and inline Python AST checks
passed. Nine mutations were rejected: dispatch-only, actual grandparent-tree guard,
literal backslash-n output, runner in job env, shallow export, nested export, wrong setup
cwd, wrong binary prefix and duplicate YAML key. actionlint was unavailable; this is a
targeted scanner, not full upstream actionlint qualification.

Both std patches applied in temporary Git indexes to their exact bases. The overlay
from6075 yields package tree318753826afce4c952e8210b67a8b5919f646f9b; the combined
library-only patch from70ba yields library93d2f428370a2a9dbedafd6dd598305b46aac50c.
Baseline142files/118tests and SEL1572files/548tests were regenerated independently,
with9 subtree identities and3 submodule pins each. All19 CI asset hashes match the
committed package. Changed Kani paths are only control scripts and CI workflows.

Authored workflow/Python/JSON whitespace checks pass. Exact archived issue-body/fixture
EOF bytes, unified diff whitespace and historical embedded patch bytes are retained;
a full generic whitespace scan flags those data files. Exact hashes are the data check.
The std source commit's two-file diff passes git diff --check.

No local Cargo/rustc/Kani/CBMC/Miri/setup/build, push, CI dispatch or publication.
Cloud spending0; runtime results NOT_RUN; no bounded/full proof credit.
