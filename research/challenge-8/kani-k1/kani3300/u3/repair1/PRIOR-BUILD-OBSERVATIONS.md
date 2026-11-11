# Bounded KT2 reading of the previous U3 build

Build `14dd0792-1c06-47be-b931-94f6096a664a`, authorized head `2021b7cf3518fc72fee611e2a5d306e4bf5b619e`.
Summary SHA256 `d9a45dc19dfe3d1d4959864ab3c04c3af991a5782df7cee700b1f31b42b4083b`.
KT2 native-field now reads individual old-summary fields successfully; the previous page-size blocker is removed.
Three targeted fields read: offsets0,16,17, output_excerpt.records, start0/count8 then returned next_start8/count12.
The second pages are stored in evidence/previous-native-{0,16,17}-records-8.json, with build/head/request/summary/file identities.

Offset0 total20 records: first page0..7 followed by count12/next_startnull. Kani tail says Complete0 success/6 failures/6 total.
Offset16 overwrite total19: second page count11/next_startnull. Kani tail says overwrite_copy failed, Complete0/1/1.
Its stderr excerpt says foreign function(1), verification will fail if reachable; callee and actual failed check remain UNKNOWN.
Offset17 overlap total18: second page count10/next_startnull. Kani tail lists overlap_copy_left and right failed, Complete0/2/2.
It contains Description internal error: entered unreachable code at kani_stdout lines257 and538 (also compiletest_stdout271/552).
Description is not property FAILURE; no source cause/foreign reachability is inferred.

Across the three complete selected excerpt-record arrays, no actual Failed Checks line was returned. This is an omitted
portion of old diagnostic excerpts, NOT an empty failed-check list. KT2 cannot retrospectively regenerate excerpts from raw
output, and no raw output was read. Exact failed properties from the old build remain unresolved. No old verdict/ledger changes.
The new repair run will use KT2 failed-check-first selection and explicit omitted_failed_check_line_count. After that build,
read summary, verify check-tooling against3bb5445d2a, then native-field output_excerpt/records via returned next_start.
Write all available actual Failed Checks for overwrite16 and both overlap17 harnesses; report any omitted/clipped coverage,
foreign/unreachable failure separately. Do not infer absent properties or proof credit from a description or excerpt alone.
