# N7 RefinedRust G1 — INCONCLUSIVE (cold setup failed)

2026-10-23 UTC. The online Artifact Registry route was implemented and exercised
through two authorized cold Builds. **No RefinedRust image digest was obtained;
G1 frontend admission and cleanup generation remain NOT_RUN.** Proof credit0,
independent proof credit0, readiness index unchanged. N6 is preserved separately
in [N6-RR-G1-RESULT.md](N6-RR-G1-RESULT.md).

## First causal failure

Stage: **cold-image / Docker client-daemon API negotiation**.
Operation/symbol: `docker build`, before executing the image Dockerfile.
Rust symbol/span: **not reached / unavailable**.

The exact archived diagnostic at `allprooflogs/cold-image.log:6` reports client
API **1.52** rejected because the daemon supports at most **1.41**. The archived
cold status binds the same Build, lane/stage and original exit **1**. The selected
script `cold-image.sh:59` is its first Docker build pipeline, followed by
`set -Eeuo pipefail`/EXIT handling that preserves this exit; receipt copy and
push occur later. This is the source-based attribution of the first setup
failure, not an RR/compiler rejection. Reader's generic causal/parser status
remains UNKNOWN and no AST/MIR/source proof binding is inferred.

Exact selectors, request IDs, file/index/archive SHA256s and scope limits are
recorded in [N7-COLD-FAILURE-EVIDENCE.json](N7-COLD-FAILURE-EVIDENCE.json) and the
immutable observation linked by [N7-RESULT-IDENTITIES.json](N7-RESULT-IDENTITIES.json).
Brief integrity `VERIFIED_ARCHIVE_AND_INVENTORY` confirms archive/inventory only.
The source audit is INCONCLUSIVE, accepted=false, diagnostic_complete=false,
proof_credit=false; it does not establish formal verification.

## Builds and accounting

| Build | Outcome | Accounted | Execution | Evidence |
| --- | --- | ---: | ---: | --- |
| `efd32c5f-83e5-4cae-8b4a-a83dc7bc072a` | EXPIRED before steps | 297s | 0s | normal client metadata; Brief HTTP404 |
| `3e604123-0d22-415d-b629-5ce2bf05aca7` | FAILURE, cold exit1 | 94s | 93s | exact Brief cold log/status/audit |

Total **391/5400s spent**, **5009s retired**, carry0. These are conservative
Cloud ledger seconds including queue, not active agent time. Both terminal
accounts and CHECKPOINT/STATUS were committed and pushed before further work.
The first queue expiry's mechanism is UNKNOWN; null step metadata does not
establish quota or capacity cause. The one reviewed repair reduced the request
from E2_HIGHCPU_8/jobs4 to allowed E2_STANDARD_2/jobs2, keeping timeout1740,
queue60 and report reserve240. It reached cold setup and then hit the API error.
The two cold Build admissions are now exhausted; warm cannot run without image
and binary freeze. No third attempt, shortened timeout or budget transfer occurs.

## Exact identities

- RR `332d945fafa14bf55c0c8390cb35ec4b0c012cff`, tree
  `b33bcccbbbd6168ac73e0c7238a1edddbe34057c`, unpatched; binary hash UNKNOWN.
- Compiler pin `nightly-2026-08-28` /
  `e457a7b0d326d67b4322ef0d11bd715cfaeda48f`; binary hash UNKNOWN, not executed.
- Std `cd371e035c7e573760c43bf934d53e8118ee3e7d`, SmallSort blob
  `40939f922bcb6fdc7ee0d30427fa861827043827`; seven exact annotation anchors and
  runtime bodies retained from N6.
- Package origin `68671873669cd8578796ad4cb74f0fc28e622f2f`; executed repair
  candidate `2df9908134a736965bcea6921cebcd16584b2a08`. Initial and delta review
  identities: [N7-INDEPENDENT-REVIEW](N7-INDEPENDENT-REVIEW.json),
  [N7-REPAIR-REVIEW](N7-REPAIR-REVIEW.json).
- Registry `us-central1-docker.pkg.dev/smallsort-ci/smallsort-tools/refinedrust-g1`;
  image digest and executable receipt **not established**.
- Repair Brief archive SHA256
  `f8a9df8200129445c71af60b911eb5cdc64a6ea9667d8fcd4424c67d365e94a2`;
  index SHA256 `aa617e137ac5575c1708dd0090cb7a2508b847ca7cb6587b89bedad10bd99eb4`.
  Causal file ID `7d1bbbfbf1c5e8ba88a9edf75e9649ec1794f4d5ec989a75f09ee303ed63fec1`,
  SHA256 `d91360715dbf58a2c89861341c002c6db81f4ca9056f2936d9766df1959cca56`, lines5–6.

Full profile/package/config/source-input identities are in N7-RESULT-IDENTITIES.
The legacy packager stock tool_profile is not an actual VF/compiler execution
identity for this lane; the explicit N7 cold/G1 records govern interpretation.
No raw archive/log/Cloud Logging fallback or download_verified claim was used.

## Exit and remaining obligations

Missing specifications: **UNKNOWN**. Actual `insert_tail`, `CopyOnDrop::drop`,
reached callees and cleanup/unwind output: **NOT_RUN**. Neither GO_G2 nor a
STOP_RR frontend/semantics conclusion is justified; no G2 estimate is fabricated.
RR work stops with INCONCLUSIVE after the allowed setup repair. A later task can
address the localized Docker API defect; [N7-NEXT-SETUP.md](N7-NEXT-SETUP.md)
records unverified options without treating them as checked fixes.

Final published Select recheck at `d6aca506e4344b6f6ef6ee0e6770c4b59652875e`
has no R24 P2 interface and retained R23 P2 is NOT_PUBLISHED. W7/R4 remains gated;
W8 needs published W3/W5/W7 resources. See [N7-SELECT-RECHECK](N7-SELECT-RECHECK.json).
Existing N9/N13/R7 bounded source-reported results are retained without new
credit or unrelated repeat Builds. Stock VeriFast profile, RR frontend,
coordination/IAM/shared transport, runtime std and other owners' ledgers are
unchanged. Independent review plus45 distinct synthetic controls/syntax/closure
validate only the prepared runner/client boundary, not a completed image or G1.
