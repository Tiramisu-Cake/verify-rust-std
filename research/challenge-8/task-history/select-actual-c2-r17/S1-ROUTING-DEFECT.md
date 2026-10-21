# R17 S1: strict routing and fresh phase

Defect: R16 resource controls embed the complete actual source but select an unrelated ghost lemma (`name` differs, `mir_target=sort4_stable`). They inherit `actual_hrtb_output=True` from the actual body. The strict HRTB route correctly refuses this helper target, interrupting all subsequent controls. S5 diagnostic-audit reports the RuntimeError and empty controls.

Applicability: only the two exact constructor-produced resource negative helper cases, with exact helper name, enclosing actual MIR target and matching actual-body/scoping/source metadata. Actual-body frontend controls retain HRTB opt-in; dedicated HRTB-off contrast removes both keys. Other helpers cannot inherit ambient opt-in.

Invariant: no relaxation of `run_case` route checks, no actual runtime/CFG/contract/kernel change, no new assumption. Strip only the two HRTB routing metadata keys from recognized unrelated helper targets before calling the same fail-closed runner. Preserve c1/scope checks for their enclosing source. The full historical R16 chain remains exact; a new final source overlay only changes its authorization literal to R17.

Controls: exact full target and frontend negatives retain opt-in; HRTB-off disables it; both fixed resource helper identities are routed without it; unknown/name mismatch/missing source/scope/mir-target fail closed. Existing service success/error/timeout/partial/missing/null/wrong-type/NOT_RUN and source-stage-target mismatch preserve original snapshots. Cloud required before any execution claim. S1 remains the full actual-body c1 baseline, not c2 success.
