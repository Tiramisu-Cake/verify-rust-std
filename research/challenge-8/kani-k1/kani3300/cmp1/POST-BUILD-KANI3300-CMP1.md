# CMP1 — single native attempt, partial handoff

Exact coordinator GO on `66881e0c52d010af94403a9bcf6dd7775b1d7cfb`, request kani3300-cmp1-20261111-02. Submitted once; k1g watcher delivered terminal FAILURE. No repair/replay has been submitted.

Build `77e4765a-d82a-48c8-bf2e-cb6ae2fcdc07`: Cloud FAILURE, summary TOOL_ERROR, gate=false. Kani build PASS252s; compiletest build PASS16s. Native15PASS/3ERROR. Applied tree `4c0c56b2808adb542f6e58a59f4672fdc89b439c`, patch SHA256 `e216f41ca8887c85e19ba84ee56fc6581ee5b95f68ad982e111c5f1b0ca19183`, request SHA256 `49fb4a6df2268219dd96b29febb4c598b1490e5bc726773760e819949851b53e` match the authorized packet. check-tooling full KT2 base `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c` PASS, pool standard4. Summary SHA256 `a8b756fdd93c0fb3402ea7e7c4807d97fe161da32cf9ca060a10c5af08328628` is preserved in native-field pages.

|offset|selector|native|wall s|bounded interpretation|
|---:|---|---|---:|---|
|0|wrap-u3-intoiter|ERROR|12.104|own retained FAILURE property at IndexRange::len, uninit usize; complete own Failed Checks/root mapping unavailable|
|1|compound-cmp1-positive|ERROR|49.032|own Failed Checks uninit usize in IndexRange::len; individual roots/full list incomplete|
|2|compound-empty|PASS|3.727|2 named failure statuses bound by golden; file-level own FC usize; each cause UNKNOWN|
|3|compound-overwrite|PASS|7.791|3 named failure statuses; file-level own FC usize; each cause UNKNOWN|
|4|compound-call|PASS|24.949|8 named failure statuses; file-level own FC usize; each cause UNKNOWN|
|5|compound-projection|PASS|11.804|golden1SUCCESS/4named failures; own file FC usize; per-negative causes UNKNOWN|
|6|compound-padding|ERROR|15.468|required u8 diagnostic absent from own stdout/stderr; all5 root causes/terminals UNKNOWN|
|7|compound-layout|PASS|3.576|all5 named failures; file-level own compound Unsupported; separate causes UNKNOWN, including indirect guard|
|8|compound-no-MIR|PASS|1.319|one unique root, own FC bodyless shadow-argument Unsupported; full list UNKNOWN|
|9|wrap-u3-positive|PASS|5.633|7SUCCESS through require_success and exact source/golden; literal SUCCESS excerpts absent|
|10|wrap-u3-padding|PASS|0.867|one FAILURE bound by golden; own property Description u8; Failed Checks not retained|
|11|wrap-u3-source-read|PASS|1.269|one FAILURE bound by golden; own property Description u64; Failed Checks not retained|
|12|review-positive|PASS|9.546|7SUCCESS through require_success and exact source/golden; literal SUCCESS excerpts absent|
|13|review-overwrite-copy|PASS|1.770|one FAILURE bound by golden; own Description [u8;2]; Failed Checks not retained|
|14|frame-negative|PASS|147.136|one unique root, own FC *var_7 not assignable; exact golden binds user line22; full list UNKNOWN|
|15|flat no-MIR|PASS|1.671|one FAILURE bound by golden; own Description bodyless Unsupported; Failed Checks not retained|
|16|plain-negative|PASS|1.721|one FAILURE bound by golden; own Description u16; Failed Checks not retained|
|17|clause-PFC-negative|PASS|2.474|one FAILURE bound by golden; own Description u16; Failed Checks not retained|

Every intended negative root has its own row in RESULT-KANI3300-CMP1.md and its own record in POST-BUILD-OBSERVATIONS.json. There are35 roots:30 reported failure statuses bound by exact native golden matches,5 terminal statuses UNKNOWN in the errored padding file. Only2 unique-root own Failed Checks lines can be attributed individually (offset8 and14). The other33 own-FC root causes remain UNKNOWN. A named failure status/golden match does not supply the full property's cause or complete check/covers list.

## Retention boundary

The existing producer retains output_sources/output_excerpt only for native_status FAILED or expect=fail. Negative expected-mode native PASS rows have only their selected own-output diagnostic string; output_excerpt was not retained. Each targeted `native-field ... output_excerpt` query at offsets2,3,4,5,7,8,10,11,13,14,15,16,17 returned exit2 `unknown native field: output_excerpt`; receipts and validated native rows are preserved. This is not NOT_RUN. Native-field diagnostic pages were followed only through returned next_start, with identical summary/source identities.

For multi-root offsets2,3,4,5,7, a single own file-level FC cannot be assigned to every root. The five layout guards therefore each remain UNKNOWN as to their own FC, including the four mandatory arbitrary-union/storage-enum/nested-MU/nested-union controls. The indirect guard remains a fifth separate UNKNOWN.

Error excerpts also have omissions: offsets0/1/6 omit9/3/15 failed-check lines respectively. Offset0 retains an own `Check 1: ...IndexRange::len...`, Status FAILURE, Description uninit usize, but no own full Failed Checks line/location pair. Offset1 retains own uninit usize Failed Checks with IndexRange::len location; no individual group-root attribution is retained. All records are read as data; no source/AST/MIR causality is inferred from a coordinate alone.

At offset6, every retained record is compiletest_stdout. Its first u8 Failed Checks line is an echo of a missing golden, not own execution evidence: output_sources proves required_substring_found=false in kani_stdout and kani_stderr, true only in compiletest_stdout. Other echoed fragments mention Pad, C<Pad>, u32 and *const u8; none is promoted to an own Failed Checks result. Absence of the expected u8 diagnostic does not establish unexpected SUCCESS of either padding-read root. Those roots remain UNKNOWN, and the file is ERROR.

No raw logs, archives, Cloud Logging or downloaded raw copies were read. No fallback was used to bypass this retention boundary. Full Failed Checks lists, precise per-root additional failures, source contexts and reached-read covers are incomplete. Tooling was unchanged; reading the summary cannot repair omitted producer evidence.

## Handoff

The descriptor/compiler change compiled successfully; native acceptance did not pass. The independent review remains static and unchanged. No complete compound acceptance, general theorem, B1/B2 or core replay credit is claimed. Global `uninit checks off` summary text is the request-level harness setting; native tests retain their source `-Z uninit-checks` directives in the authorized tree, and observed instrumentation failures must not be relabeled as runs without uninit checks.

Next authorized work would need a new coordinator task/GO: investigate the IndexRange::len ordinary-byte shadow failures and padding/pointer-read diagnostic mismatch, and obtain sufficient per-root own evidence. This stage neither repairs production nor changes goldens/tooling/runner. U8/U9(+U1/U2,U6) remain NOT_RUN; core dispatch is not justified. The separately excluded U3B PFC+modifies+uninit OOM pair remains OPEN.

Budget for this CMP1 stage: one build, actual$0.1755, reserve$0, cap$0.60 (budget BUILD receipt). The former$0.540 reservation is released; unused headroom is not permission for a repair. Original stage/window/owner restrictions are preserved.
