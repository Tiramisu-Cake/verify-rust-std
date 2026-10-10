# Independent physical frame review — annotation-only

Build c766f676 / proof29771d65 / tool df6b3fbf / profile0b8cf55b proves qualified guard extent and actual alignment, then refuses field access at separation80: No matching CopyOnDrop_src(gap_guard_addr, _). Alignment lemma returns initialized aggregate points_to, preserving its saved struct value and coefficient.

Independent review /root/review_bridge GO: existing src/verifast.ml:659–667 open_points_to consumes exactly that same pointer/type chunk and forwards coefficient and saved value to produce_c_object(Term value). src/verify_expr.ml:1840–1919 exposes src/dst/len fields and padding of that value with same coefficient. The annotation restores physical representation; it creates no own, payload, CURRENT, source permission or destination gap. No semantic rule/tool/contract/runtime change. Half-FBC subsequent transfer remains a fresh proof obligation.

Exact saved preparation replay fourfixtures/fourmutations PASS_PREPARATION_ONLY; fresh Rust ghost acceptance, separation and full normal return/leak still require Cloud. Negative overlap/zero must reach their shifted TARGET82, not the old field-access refusal. Same exact tool/profile; no new compiler-only campaign.
