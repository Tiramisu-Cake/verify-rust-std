# Independent C/C++ supplemental raw review — Build 15f28723

Read-only review of `/tmp/verifast-native-h-15f28723-raw/allprooflogs` for
Build `15f28723-2e2a-46b0-9b39-145dbb1787fa`, proof/infra
`491a98e35e5dd3caab257d91074f4aacb06415d4`. This run supplements the
inconclusive C/C++ controls in baseline Build
`47ee47d9-274b-4b13-84e2-167ba88ff770` (proof/infra
`03c2f4e134473253045d716a9779cc1b8530d0bb`). The baseline manifest,
native result, integration result, audit, and prepared-source SHA-256 pins
recorded in the supplemental result match the exact baseline files I read.

The supplemental native preparation hash is
`e6c7dae4c528b1f7259476467fbd266ece9b8293682a988db3e13ba11f5612ad`,
identical to Build 47. Its C source is a one-byte `struct CNonempty` with a
`sizeof >= 1` assertion and postcondition; its C++ source is an empty
`struct CppEmpty` with the same assertion and postcondition. Their fresh
source SHA-256 values match Build 47 and the source preparation certificate:
`0795cf5af0aca963af2f5656e42d5a899fa31c19866f1cfbbfcc05e1227dfb3a`
and `b9d0c398d00bb5b62277a1a5566a0d7bf53f8541bc6654e75d0dc108af93e361`.

Both stage JSON files invoke the rebuilt `bin/verifast` with `-shared` and the
corresponding unchanged source basename from its prepared directory. Each
stage exits 0. Each complete log says `0 errors found (1 statements verified)`
then `Program linked successfully.` Both log SHA-256 values are
`99a2f01f5b0916b9ff883d31de83aa23a52a1418f11968a40b2340f005b6dc25`.
The prior Build 47 logs reached the same assertion but failed at the missing
`main` link obligation. `-shared` removes that application-entry requirement;
the assertion and postcondition remain verified.

The supplemental effective-hashes record has `exact=true`. Its seven pinned
tool/spec file hashes equal Build 47's native result; the rebuilt
`bin/verifast` SHA-256 is
`6b73208f02f9b1c0d2e84b1b43bf53a70797c9d1953e818c6626ee4c99ee376d`,
also equal to Build 47 and both supplemental console seals. The kernel
`src/verifast.ml` remains
`37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`,
and the ZST size file `src/verifast1.ml` remains
`bfbfb518fb9783afeeba9384e1431b6cd280c7da7713b9fdbfd15a8395b00207`.
The supplemental result SHA-256
`90041ae4738a60eefd18ec099db4be4a1e467f7496347d7038aa7bcc3a63a822`
matches its proof-audit reference.

**Verdict: GO for the two affected C/C++ preservation controls on this exact
tool/profile.** This is a narrow positive-size result, not a full C/C++
regression suite. The Rust/Bool/native cases were not rerun in this Build;
the result explicitly labels them `BASELINE_RESULT_REFERENCE_ONLY` and grants
no automatic proof credit. The Cloud run exit 1 is the runner's deliberate
`supplemental raw review pending; no automatic proof credit` exception after
both successful stages, not a verifier or linker failure. The result and audit
remain unaccepted, and overall merged-profile readiness is outside this
review. No local proof or build execution was performed.
