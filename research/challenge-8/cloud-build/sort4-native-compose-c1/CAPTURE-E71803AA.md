# Fresh source/MIR capture, not composition proof

Build `e71803aa-11e1-4804-ae9c-8f901b106d5d`, token
`dispatch-9df94c605b8241409f273087473858d3`; proof=infra
`eb631c2222c9070948c15693d424c631488aa86f`. Cloud SUCCESS means completed
diagnostic collection. Create `2026-10-10T00:58:48.760074527Z`, finish
`2026-10-10T01:04:54.840009Z`; charge 367 seconds, session total 704/3600.
Archive SHA256 `98be3c4b3e819bc2c3d123264d8aa717ee38e984d5e0092279b5f02c2446d426`.
Archive hash checked locally; raw cases extracted outside Git. Full download
receipt/text inventory are tracked by the budget collector.

Normal and readonly exporter/decode and refinement all exit 0. Original source
`7638df96152b2bddb59b0f159e8277e69acf774e68a0c1eb88e933120578faeb`,
verified source `1ffbb2b5196df483c107971aa81515cd615fcaf5ee09e1a63b2f1b0da3e9aee5`.
Complete helper MIR normal
`0dc4d60b62343cb816326b4cf229581081f4e7ff906559cdc2448f14853be3b0`,
readonly `362db0d6d413be96c526407fb6781498cdde8ff8a68b8d064eb3ec4a1a0cc720`.
Native diagnostic MIR normal
`cc10c065842bb807aaa63b378cbf641c98711426ef12ef07869008670be96730`,
readonly `71d4f4835e6a9b4ffcf181aaf4d70fde638e02f3d4f48ac6fc5baeab6fe46d9c`.

Both AST diagnostic and full verifier exit 1 at
`verified/lib.rs(226,17-23): error: Parse error: Parse error.` The second
`assert` in a multiline ghost annotation is the first blocker. Neither target
entered verification; no normal/unwind/frame/posts/return/leak composition
verdict. Correction: separate source assertions into individual annotations;
new source requires fresh compiler/MIR/refinement evidence. No semantic overlay
or AST capture instrumentation was exercised here.

The raw normal helper graph has exactly one resolved FnMut and its
`unwindAction = (continue = void)`. The initial diagnostic's uppercase
`Continue` string count is not an edge certificate; it incorrectly displays
zero. Ordered operands and exact callback edge must be admitted independently
before a semantic overlay. Native diagnostic is an internal helper caller,
not actual caller CFG or caller→sort4. Existing separate native/C1 results and
mandatory unbound C2 refusal retain their previous status.
