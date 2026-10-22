# R22 fresh admission for the approved fractional candidate

Defect: the branch client, callee runner marker and the fractional fingerprint/proof entry admit only the closed R21 phase. Applicability: the fresh owner-authorized R22 account (Runtime: Claude Code) on the identical `o26-select-callee-r20` lane and the owner-approved fractional candidate `288fa7cd`.

Invariant: proof/patch/transform/fingerprint-pin inputs byte-identical to `288fa7cd` (fractional patch `e1f98deb…`; translator chain `0862e635…` → `606235c6…` → `50a77b8d…` rechecked statically by `git apply` on pinned tool objects `f76012fb`). R20/R21 historical constants and ledgers unchanged; exact separate R22 owner/lane/window/3600 ceiling/270..1200 timeout/240 reserve; coordinator v4 untouched; pinned-object transport (113 parts, 336556 bytes) under the 191 cap. The fractional helper and proof entry change only their exact phase constant (R21 → R22) and refusal text; the entry's helper SHA pin follows. `select-callee-r20.py` is unchanged (its phase gate is not on the fractional route), so its recorded `r20_helper_sha256` in the fingerprint input stays exact. No tool, model, runtime algorithm, spec, ghost transform, control target or proof-credit change.

Timeout: the R21 retry `fe704af2` used timeout 600 (work 360s, deadline 300s) and ended 124 before any stage result was retained; R22 submits only with 1200 (work 960s), never shortened.

Controls: synthetic R22 registration tests (exact account and refusals, both deadline gates, R21 account refused under R22, env/transport/config); existing callee/fractional service tests (missing/null/wrong-type/NOT_RUN, provider/phase/GitHub/ambient opt-in refusals). The historical R21 registration test now fails only its "installed ledger is AUTHORIZED" check because R21 is CLOSED (pre-existing, not a regression).

Preparation: `smallsort-session prepare` on candidate `5b6fbed9` (76 closure entries, PREPARED_NOT_REGISTERED); draft ledger differs from the registered one only in status/schema/authorization text.
