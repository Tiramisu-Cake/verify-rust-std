> **Исторический справочник:** актуальная [инструкция v0.11](EVIDENCE-READER-GUIDE.md) отменяет прежние16-квоту, лексические WITHHELD и запрет targeted-пагинации. Ниже сохранён текст старой версии.

# v0.10.0: exact literal locators in verified archived files

Status: available for agent use, as confirmed by the owner on 2026-10-19.
Baseline before v0.10 was protected main
`4ad66625cacf98cfcda1fab03233c8f042f1acee` (v0.9.0).

## Outcome and boundary

An AST/MIR/source artifact may have a verified catalogue entry but no retained
Reader projection. v0.9 can extract only a caller-selected source range or
position, which leaves an agent unable to discover its coordinates. The new
selector returns **coordinates only** for a literal in one verified file. It
does not parse AST/MIR, identify an enclosing node, infer receiver types/regions,
link AST and MIR statements, establish parser input, or reproduce diagnostics.
Those conclusions still require explicit source observations and bindings.

The separate targeted service accepts the selector on its existing authenticated
POST route. Reader remains reports-only. No new route, IAM grant, raw object path,
regex, archive enumeration, proof Build, report rewrite or budget increase is
introduced. Existing selectors and their normalized request/cache keys are unchanged.

## API and CLI

```json
{"file_id":"<catalogue ID>","literal":"InferredTypeExpr","expected_sha256":"<member SHA>"}
```

```bash
smallsort-brief "$BUILD_ID" --refresh --file "$FILE_ID" \
  --locate 'InferredTypeExpr' --expect-sha256 "$EXPECTED_SHA256"
```

Literal matching is **case-sensitive**, exact, without normalization or regular
expressions. This differs from Reader `--search`, which is case-insensitive and
covers only retained sanitized observations. The literal must contain at least
3 printable Unicode codepoints and at most 160 UTF-8 bytes. Control characters,
newlines, unsafe command/credential/instruction-like literals and unknown or mixed
selectors are rejected. Metacharacters are ordinary text. Overlapping occurrences
are included, in source order.

At most 20 locators are returned. There is **no pagination** and no raw content or
hex in locator rows. With more matches, `truncated=true` and `complete=false`;
no total source match count is exposed. Use a more specific task-relevant literal,
not offset enumeration or repeated windows to reconstruct a file.

Each row contains:

- `unicode_start`, `unicode_end_exclusive`: zero-based Unicode codepoint offsets;
- `utf8_byte_start`, `utf8_byte_end_exclusive`: zero-based byte offsets in UTF-8;
- `line`, `column`: one-based LF source line and Unicode codepoint column;
- `end_line`, `end_column_exclusive`: exclusive endpoint in the same line system.

The envelope retains file/index/archive SHA, normalized request and request ID,
`SOURCE_OBSERVATIONS_NOT_PROOF`, `causal_status=UNKNOWN` and
`parser_input_binding=NOT_ESTABLISHED`. `exact=true` describes numeric coordinates,
not semantic AST identity or a proof claim. Source size is reported in bytes,
codepoints and LF lines. No-match is `NO_MATCH_IN_SEARCH_SCOPE`; it is not NOT_RUN,
semantic absence or evidence that a different file has no match.

### Locate near a previously established anchor

To find another marker near an exact position obtained from a prior locator,
use a fixed radius of 4096 explicitly named source units:

```bash
smallsort-brief "$BUILD_ID" --refresh --file "$FILE_ID" \
  --locate 'InferredTypeExpr' \
  --near-position "$ANCHOR_CODEPOINT" --unit unicode-codepoint \
  --expect-sha256 "$EXPECTED_SHA256"
```

`--near-position` is zero-based; `--unit` must be `unicode-codepoint` or
`utf8-byte`. `--unit` without a position is rejected. The byte scope expands to
UTF-8 boundaries and the returned `search_scope` states actual bounds in both
units. Matching is limited to complete literal occurrences within those bounds.
Out-of-range anchors return `POSITION_OUT_OF_RANGE`. Near search also has 20-row
cap/no pagination. Results remain in source order, not semantic proximity order.

`complete=true` means that all literal matches in the stated search scope fit;
it does not mean the whole file was returned. `source_absence_established` is
always false. After obtaining coordinates, use ordinary v0.9 `--position --unit`
or `--start --end` to request a separately bounded fragment, subject to its own
content policy and shared quota.

## Privacy and bounds

The whole verified UTF-8 member is screened **before** matching, including for a
near search or an absent literal. Any credential/PEM/unsafe command, instruction,
email or encoded-value context causes `LOCATE_WITHHELD` with no locators or match
count. A near scope cannot bypass an unsafe region elsewhere in the file. No
per-private-region offsets or hidden match counts are exposed.

A locator can process a source line longer than 64 KiB **only because it exports
no source text**. All other existing lexical safety checks still apply across
the entire file. This does not loosen v0.9 line/text export limits: requesting a
fragment inside that same long line may still return `WINDOW_WITHHELD`. Locators
therefore do not guarantee that receiver type/region text is displayable.

Unchanged hard limits: one known catalogue file ID, member up to 4 MiB,
archive/expansion bounds, 2048-byte request body, 12000-byte response, and
**16 persistent reserved requests per Build shared with all v0.9 selectors**.
Completed identical requests reuse immutable cached results. Failed reserved
requests still spend slots; pending/quota states do not permit raw fallback.
No new supplement prefix or policy-key reset is used: existing
`supplements/targeted-v1/` cache and slot records stay intact.

## r3 workflow after rollout

The operator supplied the following artifact identities; these are task metadata,
not an assertion that the candidate has inspected their production bytes:

```bash
BUILD_ID='5f668cd9-fb34-4570-ad1c-4b97abbb36d0'
AST_FILE_ID='34ea04bf09c2f6022dac1c22a0444b4583420dfe82ec1865f5ac18b85f25039b'
AST_SHA='3193176be89d0f18982253759930c9bdac47f2c1c4b6bc83c2437a69603a1f0c'

smallsort-brief "$BUILD_ID" --refresh --file "$AST_FILE_ID" \
  --locate '214' --expect-sha256 "$AST_SHA"
```

`214` is a source-position token to investigate, not an AST grammar assumption or
a unique node ID. Interpret only returned observations. A more specific literal
must be taken from known source/serializer syntax or a displayed verified fragment,
not invented. Use a returned anchor to locate `InferredTypeExpr` nearby, then
request a safe fragment if available. Multiple candidates remain ambiguous.
A nearest textual occurrence is not necessarily the enclosing AST node.

For prefix `decode.out`, first use Reader catalogue to select its exact ID and
confirm supplied SHA
`70be7daa815fd80ad8f921b1da2984e3cc64d258a7a0c625d59958b82518723c`.
Use the same coordinate workflow for a task-relevant known literal. No path-based
raw endpoint or automatic AST-to-MIR mapping exists. Preserve ambiguity instead
of guessing receiver type, region, field linkage or a failing placeholder.

## Release, rollout and rollback

Release a reviewed protected-main commit through the existing approval-gated
image-only trigger as v0.10.0. Deploy only the existing private targeted service
from the released digest, preserving its distinct runtime identity, buckets,
OUTPUT_VERSION=v8, IAM Conditions, authentication, timeout and instance limits.
No IAM changes or historical backfill are needed. Install the updated standalone
client on the VPS separately; its existing targeted URL/auth remain usable.
Reader/Processor can stay on their current images.

Verify mode/version, no public invocation or /process, one approved narrow locator
request and repeat cache use, plus a known existing v0.9 selector. Do not use a
new proof Build for validation. Roll back targeted to its recorded v0.9 digest
and retain cache/quota/report objects; new locator keys are simply unusable until
v0.10 is restored. The old client can still make old requests against either
version; a new locator against v0.9 is rejected, never silently downgraded.

## Validation

Synthetic fixtures cover omitted .ml projection, very long AST lines, exact
Unicode/UTF-8/CRLF coordinates, overlapping literals, literal metacharacters,
fixed near scopes, row truncation/no pagination, whole-file withholding even on
no-match/near queries, unsafe requests, unchanged v0.9 exports and quota/cache
behavior. HTTP smoke includes real standalone CLI serialization and cached
locator reuse against fake storage. No production raw archive was read for this
implementation. Independent security review is required before merge/release.
