# S1-05 — local preparation

Entry g0 `6521d03ed1b429354f9b8cb2d0119061bdbff17e`. Package is isolated under
`kani3300/ch8-s1/s1-05/`; historical S1-04 intake/acceptance and ledgers are unchanged.

Control `8860d38558651f7cf2e292d57b06b378c6ad3b94`, local worktree
`/root/kani-ch8-s1-05-w13`, branch `uninit-ci/ch8-s1-05-prep-w13`, exactly one
parent `40b5d9cf48900ff1e227e1fbba24cb5b2edbf8d5`. Author Tiramisu-Cake
<igkharin@gmail.com>. CI-REQUEST.json is byte-identical to the committed request.
Std remains `5be85699b8826e3286c0bf89efb9affefac0acb5`, stock tool
`0aac16ef62da9e9d5645782d458593e5d78143ba`; neither source was changed.

Relative to executed S1-04 control205b0e98c7:

- Regular output replaces terse; a streaming decoder retains every check/cover
  ID/class/description/file/line/status and reconciles the whole inventory with
  stock JSON from that same invocation. Multiline descriptions, relative source
  paths, short display IDs and UNKNOWN display mapping follow pinned source.
  Missing/ambiguous descriptions/sites or incomplete evidence fail closed.
- Runner returns RECORDED observations with exits, elapsed/VT and sampled group
  RSS; verdict/oracle/unreachable/unsupported admission is exclusively offline
  under ACCEPTANCE-POLICY-BATCH/w11. Per-root exit/RSS stay UNKNOWN where unavailable.
- Macro source binding includes declaration29 plus original anchors66/67/68.
  F1–F6 unchanged; F7/F8 prospective oracles freeze exact w11 proposals, mutant
  hashes/sites/descriptions, sole permitted failure and unmutated companions
  with reachable named post-return covers. Wrapper/role qualification remains
  required offline; no retroactive S1-04 detection claim.
- One compact structured artifact per group; raw stdout is not uploaded.
  Attempt1, single parent, exact paths/hashes, typed YAML, depth3, original proof
  checks,35 roots/14 groups, group order/max-parallel1 and proof time/RSS budgets
  are preserved. Stdout byte cap rises from1MiB to16MiB for full rich output;
  retained stdout capture is limited to64KiB of head/tail.
  YAML uses the equivalent C safe loader/dumper when available so exhaustive
  scalar regressions fit the existing one-minute preflight; fallback stays safe.

Artifacts: exactly14 `group-evidence.json.gz` payloads, each at most8,388,608 bytes
compressed and33,554,432 bytes uncompressed. Exact compressed reservation is
117,440,512 bytes (112MiB); uncompressed cap469,762,048 bytes (448MiB).
The precise future compressed length cannot be known before new properties and
receipts exist. ARTIFACT-SIZE.json records exact measured S1-04 JSON-projection
baseline60,570 compressed/355,044 uncompressed bytes; this excludes unavailable
rich metadata and terminal/setup/per-row duplication. Planning assumption for
9,986 rich records at1,536 bytes is15,338,496 uncompressed bytes total, explicitly
heuristic. Hard caps govern; overflow produces INCOMPLETE/UNKNOWN.

Timing: observed S1-04 grouped driver2082.381s (34m42.381s), excluding repeated
setup/upload/queue. New regular/packing overhead is unmeasured. Preserve the
full conservative71,540s (19h52m20s) serial matrix envelope excluding queue;
180min is the cap of each job. No budget/window/phase/reservation is opened.

Validation:46 Python synthetic/service/Git-fixture tests PASS (27.526s), including
exact real S1-04 rich objects, missing description/location for every fixture
property, full35/14 pack→collect, interruption/error/source/target cases, native
YAML mutations and actual shallow clones. Offline closure validates production
pins, all anchors/payload hashes, each mutant source hash/site in a temporary
patch tree, prospective companions and actual control preflight with synthetic
GitHub environment. See VALIDATION.json, FORMAT.md and independent-review.md.

No push, CI, publication, ledger modification, local cargo/rustc/Kani/CBMC or
full raw-log read. All S1-05 proof NOT_RUN; qualified acceptance PENDING; credit
NONE. Next stage needs separate authorization for publication/dispatch and the
existing coordinator controls. After that run, collect each downloaded structured
artifact directory with control collect.py --root DIR (repeat for14 roots), then
apply the offline w11 classifier/policy with same-run rich property/site/role,
PFC-wrapper, named required-check/cover and complete-union qualification. The
historical w11 replay script has fixed S1-04 paths/totals and is not itself a
ready S1-05 classifier command.
