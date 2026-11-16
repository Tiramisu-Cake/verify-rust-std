# PROF-ON-02 — one preparation stage

Source: `166a406e2203bae2fc9246ba00c00b944b364445`, tree
`460029c0d95fa7ef04eb7da0115f6fa2792c3b0b`, parent P′ `9fa2f7f977`.
The exact final control pin, payload hashes and review are in CI-REQUEST.json
and REVIEW.json. SOURCE.json/source.patch document A/B/C; BINDING-SPEC.json
predeclares fresh source/oracle/cover/dependency bindings for all 63 rows.

The paired control workflow prepares **one dispatch**: ON first, then OFF
through an explicit job dependency. OFF still runs after ON failure. The two
jobs use the same source and manifests; ON builds exact SEL1 `14bc57fdb9`,
OFF builds exact stock `0aac16ef62`. Both use the established two-cfg batch
runner, no global list, all original 62 rows plus the new merge4 leaf.

Caps are per lane: job 180 minutes, absolute setup 1800s, proof 8400s,
closeout 600s, row 600s, sampled CBMC RSS 6 GiB, group RSS at most 12 GiB
and available memory minus 2 GiB, stdout/stderr 1 MiB each per row,
export 8 MiB per row, artifact 256 MiB. Maximum active jobs/runs remains one.
Two sequential jobs have a proposed total envelope of at most 360 job minutes;
this is explicit preparation, not a reservation or permission to dispatch.

Coordinator publishes these local branches in a separately authorized stage:

- verify-rust-std: `work/ch8-profiles-pprime-w11` (source).
- Kani host: `work/ch8-prof02-w11` (reviewed CI-only control).
- g0: `experiment/kani-k1-kani3300g0-20261111` (this handoff).

All prepared commits contain `[skip ci]`. A later authorized coordinator stage
may create a deliberate trigger on `uninit-ci/ch8-prof02-a` from the reviewed
control. Verify full remote source/control identities before that action;
none of those pushes or triggers has been performed by this stage.

Use CLASSIFICATION.md: fresh lane-local source/tool/config/row/property/role/
cover/frame bindings are required. `BOUND` is not admission. New merge4
consumer needs its exact new accepted leaf, never the old general merge leaf
or the other lane's result. No historical OFF admission carries forward.

PolymorphicIter rows freeze_noncopy_n2/rejects_always_true remain present with
unchanged oracles/covers; ON status is BLOCKED_TOOL pending fresh evidence.
Changing runtime roots/iterator or adding Copy would not preserve the claim.
The actual generated factory-closure rendering and frame variable spelling
remain NOT_RUN and fail closed in the binding adapter if they differ.

No compiler code, push, CI, publication, ledger change, raw-evidence access or
local cargo/rustc/Kani/CBMC run. Compile/proof qualification NOT_RUN; independent
B1/B2 proof credit NONE. One assigned preparation/review stage only.
