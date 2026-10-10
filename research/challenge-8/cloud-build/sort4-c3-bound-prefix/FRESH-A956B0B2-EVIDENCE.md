# Fresh bounded C1→C2→C3 — a956b0b2

Fresh Cloud proof candidate, not replay or whole-sort4 summary. [Independent raw review](FRESH-A956B0B2-REVIEW.md) is PASS for this exact
bounded projection; global profile acceptance is a separate gate; original collector fields remain pending and profile
acceptance remains false.

Build `a956b0b2-4e05-4c19-90b4-408f381ba1fc`, proof=infra
`aa6e5a725f71506602903f95b1832a32fa849e50`, SUCCESS. Create
2026-10-10T11:13:15.452875305Z→finish11:20:55.811535Z:461 charged
seconds,460 execution. Config SHA256
`56d109267e82dd2717b94e27a4478b922ec1eab410d2b8a9cfa6b495f0cea33f`,
source input `687e733d1c0cd59453a0b3b40708288d1e3864113c8630dddd27b813a85163b5`,
archive `c62db4d3b66396e8d65930502d34f6b7776e01f2623ee723994bca012ba98d73`.
Archive/inventory/index verified; complete raw files read from archive; external
text chunks not separately fetched. Own account1323/3600, remaining2277.

Fresh exact source087123b1/preAST7dbc4ed8/normal MIR7582215b/readonly9622479f
match the complete hashes in [profile.json](profile.json). The original runtime
ghost-strip3602050e is unchanged. Full source still contains five comparisons,
eight selects and four copies. The projection reaches actual C3 `(c,a)` then
normal recovery/join, stopping before C4; all selects/copies remain NOT_RUN.

Positive VF0,335 statements, no errors/dead-code. Same-version recover_pair,
join_four_owned_cells and all three selected-four helpers verified before target.
Three distinct named callback scopes and compiler Output=bool registrations;
original full CURRENT raw source/F/thread/type/optional-dst posts, unit return
and leak checks retained. C1/C2 direct unwind skips C3; C3 direct unwind recovers
CURRENT selected pair and complementary frame in every c1/c2 case. Entry
source/F/thread/types/sizeT>0/destination remain supplied; native lemma separate,
native→C1/actual caller→sort4 NOT_RUN.

Eight controls all exit1 after target: missing normal/unwind debt at
recover_pair comparison_debt; omitted normal/unwind rejoin at original foreach
post; normal false post and C1/C2/C3 unwind false asserts fail at their own
paths. First-VC causality and allocations require the independent review.
Changed C3 operands produce source-hash refusal before target (exit2), an
admission control, not semantic negative. Default-off C2 VF0 and mandatory
unbound C2/C3 refusals preserved.

Tool HEAD `f76012fb518703b1d98e243ac4f487f16877cfcb`; nightly-2026-09-25.
Frozen kernel `37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`.
Bound translator `d2f132148d409eb9a9e27afd24603d992405ec1984849817da9e427ab070db6e`.
Profile SHA256 `001a4437ed3c8df72bb24ca703f1b415d45aa3220342ecbe30c0916bf29ce29a`.
Capture→bound delta d6165630...; full hashes in profile. Nontranslator critical
files/RSSpec/proof std and non-console binaries unchanged across bound build.
No compatible production-base strict-cut delta implemented this session.
