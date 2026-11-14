# Fresh isolation observations

| Dimension | Current status |
| --- | --- |
| Structural lifecycle | Implemented; static review in REVIEW.md |
| New baseline accumulation | NOT_RUN; old R4 additions are hypothesis only |
| Baseline 11 invocations / 18 comparisons | NOT_RUN |
| Candidate 11 invocations / 18 exact comparisons | NOT_RUN |
| Baseline-isolated vs candidate-isolated inventories | NOT_RUN |
| Actual unit/shared Instance binding | NOT_RUN |
| Observed producer/codegen order | NOT_ESTABLISHED |
| Rust native tests / build / clippy | NOT_RUN |
| JSON composition stale-binding debt | Retained; ordinary gate may FAIL until S5 |

Coordinator fills observations separately with exact capture/receipt/tool/source
identities and full retained delta rows. Do not substitute historical counts
3/6/9 for this baseline. Capture exit 2 is diagnostic, never PASS. Check print
ordinals are ignored; no status/description/class/location normalization beyond
the existing checkout/toolchain-prefix normalization is allowed.

Candidate must have all 18 accepted=true, exact_match=true, differences={} and
mixed_root_oracle=EXACT_MATCH. Every selected root must retain its isolated
full checks/failures/Unsupported/covers, verdict, failure kind and counts.
Baseline must have at least one reached shared root with actual additional
delayed checks/operations, mapping to the unchanged read; only the full recorded
delta and binding can establish that discrimination. Identical baseline
inventories are NONDISCRIMINATING. Missing/partial/timeout or early unrelated
guard is UNREPRODUCED, not evidence that S4 works.
