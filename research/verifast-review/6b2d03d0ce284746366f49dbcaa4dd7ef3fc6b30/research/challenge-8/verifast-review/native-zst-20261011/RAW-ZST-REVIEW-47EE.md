# Independent raw ZST evidence review — Build 47ee47d9

Reviewed read-only from `/tmp/verifast-native-h-47ee47d9-raw` for Build
`47ee47d9-274b-4b13-84e2-167ba88ff770`, proof/infra
`03c2f4e134473253045d716a9779cc1b8530d0bb`, tool candidate
`46181aff379a5d4231cc51814cfe3732bda21c03`, profile
`verifast-native-zst-c3-integration-20261011-h`. The observed effective
`src/verifast1.ml` SHA-256 is
`bfbfb518fb9783afeeba9384e1431b6cd280c7da7713b9fdbfd15a8395b00207`;
kernel `src/verifast.ml` is
`37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`;
effective `bin/rust/std/lib.rsspec` is
`d33b2a7a284557002b4f7afe3d5e63f813e51f818c588712d743b4b46f9bedaf`.
The raw native result records tool-profile digest
`6b73208f02f9b1c0d2e84b1b43bf53a70797c9d1953e818c6626ee4c99ee376d`.
I checked the case sources, case and stage JSON, verifier logs, and selected
source/log SHA-256 values against their recorded pins. The complete archive
integrity audit is the maintainer's separate check, not a claim of this review.

All **nine Rust model cases** have paired normal/readonly exporter and decoder
exits 0, refinement exit 0, and `paired_support_passed=true`. The generic
guard body verifies both without scratch and with an unused
`MaybeUninit<T>` scratch (59 statements each). The assertion `size_of::<T>()>0`
verifies after the actual nonzero branch in both versions (60 statements
each), while both pre-guard versions fail at that assertion: verified lines
3/4, columns 41–42, `Cannot prove 0 < sizeof(T_typeid)`. Thus merely adding
the scratch does not justify positivity. The concrete matrix verifies 73
statements covering unit and `MaybeUninit<()>`, empty default and `repr(C)`
structs, `u8` and `MaybeUninit<u8>`, zero-length and ZST arrays, and explicit
valid-layout and size/align lemmas. The matrix's original/verified source
hashes are `ac500d6cd097fef64b638d898d2bd6015fd31ba2b8bc882b992ecd237279be86`
and `aaf4c531c01bd1fe83c623acd613fbf2e3f43656efcc8aec896336a788915f7c`;
normal/readonly full-MIR hashes are
`e89b990d716627700a0351197730519af5aeb114a495f5fb7a8401772cf82a10`
and `a8bfa7dda65bcd62b4e20cd040950ef90c0209b1362298cca7ed68a173613f72`.
The layout and alignment assertions depend on those existing lemmas, so this
case does not independently establish their general validity.

The concrete ZST `assert false` fails at verified line 4, columns 16–21,
showing that the ZST path is reachable. The arbitrary raw-pointer
`*p |-> ?value` assertion fails at verified line 4, columns 19–22 with
`No matching heap chunks: points_to<std_tuple_0_>(p, _)`. A zero size therefore
does not supply that heap permission. These are intended VC failures after
successful paired source/MIR/refinement support, not exporter/setup failures.
This negative checks one points-to obligation, not every ownership route.

The **C and C++ controls remain inconclusive**. Their source hashes are
`0795cf5af0aca963af2f5656e42d5a899fa31c19866f1cfbbfcc05e1227dfb3a`
and `b9d0c398d00bb5b62277a1a5566a0d7bf53f8541bc6654e75d0dc108af93e361`.
Each log reports `0 errors found (1 statements verified)` and then exits 1
because the translation unit has no `main`; both logs have SHA-256
`93da5864432dc2b5f02fd2ee05c513ab06f7a68fe9743b00d4e09b44a69091ec`.
The pre-link assertion observation is useful diagnostic evidence but cannot
credit the required complete C/C++ preservation gate. The proposed runner
`-shared` fix must be checked by a fresh affected Cloud run on the exact
profile before that gate can pass.

Verdict: the nine Rust ZST cases support the intended narrow size, layout,
`MaybeUninit`, nonvacuity and no-extra-heap claims for this integrated tool.
They do not establish general Rust layout/ownership soundness, the actual
caller ZST guard, full sort4, or overall profile readiness. Build summary and
proof audit explicitly remain incomplete/unaccepted; the C/C++ gate is open.
No build, verifier, extraction, or proof execution was run in this review.
