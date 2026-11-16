# Full evidence at stock0aac

The tool remains stock0aac16ef62da9e9d5645782d458593e5d78143ba. Pinned source:
`cbmc_property_renderer.rs:274–347` emits every property's ordinal/name, status,
raw quoted description and optional displayed location under `RESULTS:` for
regular output; `call_cbmc.rs:585–603` sets show_checks for regular. Existing
`schema_utils.rs:485–587,753–773` retains rich failures/unsupported only, success
counts and other check/cover ID buckets. Stock JSON alone is insufficient.

`runner.py` uses `--output-format=regular --jobs=1` and NO_COLOR/TERM=dumb.
Pinned args/mod.rs:436–471,557–563,919–925 explicitly permits jobs1 with regular;
it builds a single-thread pool. No listing/codegen-only/additional proof run.

`rich_evidence.py` incrementally reads stdout without rereading full log files.
The stdout stream cap is16MiB; retained stdout head/tail capture is64KiB.
It isolates each exact `Checking harness …`/RESULTS/SUMMARY section, preserves
embedded quotes/newlines in descriptions, and rejects missing/ambiguous blocks,
ordinal gaps, duplicates, missing description/file/line and oversized records.
A record's ordinal is never used as an oracle/property identity. Class comes
from the explicit final class component of the pinned Property::property_name
format. `missing_definition`/`recursion` display IDs are converted by the pinned
PropertyId::to_cbmc_id rules; both display and canonical ID are retained.

SourceLocation display (cbmc_output_parser.rs:261–321) relativizes files to the
child cwd. Decoder records that exact displayed location and normalizes its
file against the std cwd; it never guesses a source line from an assertion ID.
Absent file/line, including `Unknown file`, fails collection. UNKNOWN displays
as UNDETERMINED (parser.rs:388–405): only exact membership in the same harness's
stock unknown bucket restores UNKNOWN; displayed status is retained.

Before a group can be COMPLETE, reconcile every rich check/cover class total,
SUCCESS count, all non-success status/ID buckets, n_properties/n_failed, and
rich failed/unsupported metadata against that same invocation's immutable
stock export. Unknown/error/unreachable/unsupported observations are retained
without admission/veto. Each row retains the stock harness record, group exit,
elapsed/VT, original source snapshots and group RSS. Per-row exit/RSS are UNKNOWN
where stock batch attribution is unavailable. A proof FAILURE is recordable;
a malformed/incomplete evidence stream produces UNKNOWN and nonzero runner exit.

`pack_evidence.py` saves JSON files as exact UTF-8 text with original SHA256/size
inside one deterministic gzip JSON container; it never opens .log files. Upload
selects only that filename. Bounded stdout/stderr previews remain inside receipts.
A cap or partial JSON yields an INCOMPLETE container, never reconstructed data.
`collect.py --root DIR` reads original directories or DIR/group-evidence.json.gz,
checks exact contained bytes and revalidates rich inventory. Collection still
returns PENDING offline acceptance and NONE credit. Original uncompressed bytes
are recoverable from files[path].text; no archive/raw-log reader is needed.

The S1-04 fixture consists of four exact retained rich objects (one attachment
failure plus three unsupported checks), pinned to its original export SHA.
Tests render that fragment using pinned format_result grammar. It is not a
recovered regular stdout fragment: S1-04 ran terse. No missing historical
SUCCESS/unreachable/cover metadata is fabricated. Missing description/location
is tested separately for each retained record. Existing synthetic service,
shallow-checkout and native YAML regressions remain.

Offline acceptance must still establish source-site roles, mandatory post/frame/
relation reachability, full PFC wrapper correlation, named successful assertions,
cover-message correlation and all union cases. Stock runtime-message placeholders
may require exact source-site/assertion-context review. Recording full metadata
does not itself admit any positive obligation or prove B1/B2/general correctness.
