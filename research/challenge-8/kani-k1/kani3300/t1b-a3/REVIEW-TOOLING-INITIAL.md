# KANI3300 T1b-A3 tooling review

**Result: NEEDS FIX.** Tooling candidate review only; no proof credit, run admission, or dispatch authorization.

- Baseline: `fb88f46b39467382ba73870091e8758a79116fdf` (tree `ba9d9cacbc25773233774fb8a2e93147300ff121`)
- Candidate: `e0697b05f0611e3d1f824a1fce3858c02b71f443` (tree `5e4b2160df2423191d3764b82dc432d82474a2ec`)
- Review packet inventory SHA256: `84c757dcc7bdd1e33d557dc2265313a9920ee7292d2d972d621e921ad63bd32c`
- Packet spec SHA256: `ef83c6721b2984ca8e8803f5c6a2de4cd921102ed26d70b3ada2735ded3776d4`
- Patch SHA256: `cd73974424586d074d3b785bcb0e019cb8c0e1e569989b7baaa6c7439c8ad52e`

## Finding

**P2 — a bounded deeply nested JSON row can abort collection after footer retention and prevent summary persistence.** In `diagnostic_trace.py:400-405`, per-row `json.loads(line)` runs inside the validator try block, but the handler at `:507` catches `ValueError`, `TypeError`, `AttributeError`, `UnicodeError`, and `JSONDecodeError`, not `RecursionError`. `_retain_footer` catches `RecursionError` for its own parse (`:49-52`), but that does not protect the subsequent full-sidecar parse. A <=2048-byte JSON row with nesting deep enough for Python's decoder recursion limit therefore escapes `collect_trace`; `kani_k1.py:summarize` also omits `RecursionError` from its outer handler (`:2159`), so the service can fail before it writes/uploads a summary containing the already-collected footer. Catch this parser failure as an INVALID row in the collector (and keep the captured footer); add a focused synthetic regression that passes a normal footer plus a deeply nested non-footer row. Author-reported suites do not cover this case.

## Reviewed controls

The collector otherwise records bounded footer observations before validator decisions, keeps only the named fields, marks them `UNVALIDATED`, and binds them to sidecar/line hashes. The validation page path exposes `footers` and validator `errors` under the existing identity envelope and 20-item/12,000-byte page limits; ordinary record paging still rejects `INVALID`. Tests cover early malformed/type/size/stage/context failures, payload non-disclosure, persisted summary paging, pagination, and identity mutations.

Reviewed A3 request and PRE-BUILD against producer `989f72351c2b5c5f3b5117315fc84f502e66d904` (clean). Literal substring filters target IndexRange::len, selected CMP3 functions, and the calibration pair while retaining the same nine roots and expectations. Budget arithmetic is consistent: `(9 + 30) × $0.0135 = $0.5265`, within `$0.5975`; PRE-BUILD is 27 lines (limit 30). Kani diagnostic delta and producer were not changed.

**Limitations:** author-reported Python test results and static checks were inspected but not rerun. No local Rust/Kani/CBMC execution, Cloud build, dispatch, or proof validation was performed; trace completeness and runtime failure reproduction remain unknown until an independently authorized run.
