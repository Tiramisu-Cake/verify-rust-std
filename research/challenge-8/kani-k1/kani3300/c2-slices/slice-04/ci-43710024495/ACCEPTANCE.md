# Slice 04 STORAGE/protocol+F6 — ACCEPTED (run 43710024495)

2026-11-15, coordinator. Fork run [43710024495](https://github.com/Tiramisu-Cake/kani/actions/runs/43710024495),
branch `uninit-ci/c2-slices-04-w15`, overlay `4f00e47d81da1e8849551e748ed378edbf868be1` (CI-only `.github/`) on source
`345cedfd67df679e326474385308349d609fc43d` (parent slice 3 `5ca51679e3`). ubuntu-24.04, ~18 min, every step success.

| Stage | Result |
|---|---|
| fmt / build-dev / clippy `-D warnings` | exit 0 |
| units: ActiveCalls / immutable_allocations / argument_size / marker_category | 9 / 9 / 1 / 1, 0 failed |
| kani | 50 / 0 / 3 ignored |
| expected | 315 / 0 / 6 ignored |
| ui / script-based-pre / json-handler / std-checks | 17 / 3 / 17 / 2 |

Totals 404 passed / 9 pre-existing ignores = CI-REQUEST (413 selectors) + 20 units. Every stage reviewed.

Deferred obligations closed here (each `... ok` in native expected output):
- slice 1 (head 4): `points-to-cycles/{dag,self-cycle,mutual-cycle,roots-acyclic-first,roots-cycle-first}`,
  `ordinary-slots/{payload,padding}`;
- slice 3: `nested-pat-{data,padding}`, `nested-enum-{same,different}-padding`, `raw-eq-uninit`, and the 18 moved pairs
  (e.g. `promoted-allocations/direct-legal`, `mixed-promoted-allocations/eq-u8-stack-left`, `part1-edges/immutable-static-hole`);
- stage-0 decision 2: `marker-hook-calls/marked-model-{initialized,hole}`.
Still PENDING on slice 5: slice-1 head-5 obligations (`ordinary-slots/positive`, `points-to-cycles/capture-free`,
contract/mode/root fixtures), `marker-hook-calls/generated-modifies-no-shadow`, S5 sensitivity mutations 4/4.
Not Gate A, no proof credit. Next: stage 5 CLOSURE on `345cedfd67`.
