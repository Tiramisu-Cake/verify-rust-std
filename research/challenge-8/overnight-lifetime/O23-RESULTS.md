# O23 strict-cut diagnostic result

Hosted [O23 run 37756681437](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37756681437),
proof SHA `94d055d5a0a531a3920acdc74e4cede5e9d0800b`, used the new
production overlay followed by the unchanged isolated CUT patch SHA-256
`d557082b0c17771acd7386ad6caca7bc139877cf1ca513d9570da210b1b542d8`.
The CUT binary hash was
`907979720155d2dcad008a793fa47ce47bcc840bea9179cf862d226d0a6917a6`.
Complete artifacts are at
`/tmp/overnight-o23-evidence/overnight-s6/strict-cut-isolated/`.
This remains `STRICT_CUT_DIAGNOSTIC_NOT_ACCEPTED`.

Of 17 planned CUT source cases, 13 were prepared and captured. Four local
positives (`positive_basic`, `ordinary_unmarked`, `positive_early_return`,
`positive_direct_unwind`) again had full VeriFast 0, paired NORMAL/readonly
MIR, refinement 0 and no leak. Eight source/grammar negatives reached their
intended first admission or post-cut type error: wrong, duplicate, outside,
unknown, nested and malformed markers, plus scoped type name and type argument
after the cut. Their individual exact error lines remain in the captured
`result.json` files; no setup error was counted as a negative.

The `positive_f_bound` fixture is **INCONCLUSIVE**: both exports/decodes and
refinement passed, the verifier entered `callback_positive`, then stopped at
`verified/lib.rs(84,9-38): Strict lifetime binding has unresolved inference
in entry outer type`. The decoded source body contains `'<erased>` regions
in reference input/local types, and the stock translator maps that region
to `InferredTypeExpr`. The blanket strict entry freeze is therefore a real
candidate compatibility blocker before the callback call. No CUT acceptance
or actual sort4 prefix proof follows; the rejection must be analyzed without
simply dropping the inference/escape check.

The 17-case process then exited at the *second* generic source-shape guard:
`negative_typed_chunk_survives_cut<T>()` was expected to have `(` immediately
after its name. This happened before that case's export. It and the following
three resource negatives (`negative_unclosed_fractional_access`,
`negative_reserved_half_after_lifetime_end`, `negative_end_lifetime_twice`)
are **NOT_RUN**. `capture.py` now accepts `<` for exactly this reviewed
generic case in addition to `positive_f_bound`; this is a runner-only edit
with source, verifier patch, contracts and classifiers unchanged.

The independent lawful test source in `overnight-lifetime-test/positive.rs`
passed NORMAL and readonly export/decode, refinement and full verifier exit
0 with 60 statements, no error/dead code and a final leak check. Its verbose
trace shows `close live::<T>()` producing the chunk before the cut and
`open live::<T>()` consuming it after the cut. That is a valid TEST control
baseline; no TEST-only metadata injection was installed or run.

The separate absent-opt-in control, all eight fresh S6 stages and all nine
no-cut callback controls/classifications also returned status 0 on this CUT
console. Mandatory source-file, CFG ingress/reentry, inference alias,
bound-only heap and outer-variable negatives are still outstanding.
