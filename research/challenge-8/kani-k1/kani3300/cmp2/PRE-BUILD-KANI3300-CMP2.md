# KANI3300 CMP2 — PRE-BUILD packet, dispatch CLOSED

Task: `research/challenge-8/kani-k1/TASK-KANI3300-CMP2.md`; Runtime Codex, owner k1-merge, stage kani3300-cmp2. One native attempt requires coordinator GO for the exact published research commit. No submit, active phase registration or budget reservation has been performed.

Full Kani candidate `b1f0105c0390fb55081e3d186fa286d23867b585`, tree `45511935c1ce911ea6c85eee5f6850095cbf966e`, in `/root/kani-fix-3300-cmp` branch fix/kani-3300-cmp, continuing immutable CMP1 `6ef9fd72066443f7f113440ba32f77f310520a93`. Canonical publication is the full and reduced patches in this research packet; the author clone's origin is another local author clone and was left untouched.
Derived build subset commit `a03dff43df015b3be020c6717f6b1bf3c0ec2dd7`, tree `e6870add67f2b1602f60ef3a623cf08139831265`; patch SHA256 `17db5a0db394c5c5db8f7182fb61866df656747b17e160ead4034e03a14dbc0a`. All production and selected fixture/dependency blobs equal the full candidate. Baseline pin files remain intact. Build diffstat is 3543 bytes (<4096).
Full patch SHA256 `f60071e6e0e81544ed537f572cdd02878df52582cabf81a322999066867d5e56`; excluded full-candidate tests remain NOT_RUN. Exact pin f046b70644e113be0df9c22c2e6ea44a65a57566, nightly-2026-10-23, unchanged KT2 3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c.
Request kani3300-cmp2-20261111-01 SHA256 `27cdfcdf089af8dc025a90ec98e3e189701758ba4fe64f1d77ccd1dfc42421c5`; root RUN-REQUEST equals snapshot. Manifest20selectors/77roots: all18 CMP1 selectors including all35 negatives retained, plus5 minimum positive repros and3 parameter negatives. All18 old goldens byte-equal CMP1; padding source only replaces two ptr::read calls by direct byte dereference without relaxing required diagnostics/root failures.

Production delta is one file (+42/-13); fresh ordinary formal parameter bytes are initialized at entry only when delayed analysis may check that exact place and a supported sized mask exists. Unions/storage-containing parameters are excluded; pointer value bytes do not initialize pointees. Caller reads and subsequent body writes/checks remain. Product R/S/P and ghost/buffer protocol unchanged. Actual failing-instance binding remains UNKNOWN pending native; do not substitute static diagnosis for measured causality.

Independent Luna HIGH review of exact candidate/spec: REVIEW-CMP2.md SHA256 `c678c133a6d2d65cf60c88a8d0f8f85a3cbd2a8af0188ef462618eb421dcfac4`; packet inventory d2aee8734223d455bc987fa00338f3522e69adefd6353f9dee9ba39a04e8f44e, spec beee1d51eaacd847d8a771f6cd07341c91ff4f4340877be3a189f743ea452fb8. Verdict static GO for coordinator consideration, no blocking finding. Empty-entry and nested-pointer aggregate branches lack direct dedicated fixtures; source review only. This is not build authorization or proof credit.

Existing exact-pin preflight apply/tree and request validate, identities/equality/control checks passed. No compiler/Kani/CBMC ran. Rustfmt binary/wrapper is unavailable in this runtime; not claimed checked. No tooling changed, so runner service regression tests are not required for this delta.

Native work cap10min, per-test timeout150s, total reservation envelope40min × $0.0135 = $0.540 ≤ cap$0.60. CMP2 spent$0/reserved$0; global coordinator ledger must still be checked by the existing dispatcher after GO. No repair/replay attempt is authorized by this packet. Core U8/U9(+U1/U2,U6) require native acceptance and separate GO/budget. Native acceptance, core and B1/B2 remain NOT_RUN/NONE; U3/PFC limitation remains OPEN.

After terminal build use bounded k1g summary/native/native-field only; require each negative's own intended failure and complete/omitted context. Any unexpected negative SUCCESS: stop and `Координатор, вопрос`. Missing bounded evidence remains UNKNOWN; no raw fallback.

REVIEW REQUEST b1f0105c0390fb55081e3d186fa286d23867b585
