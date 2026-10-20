# R7 candidate3 independent delta review — 2026-10-20

Decision GO: GPT-6 Luna HIGH, fork_turns=none, no nested delegation. Actual compiler/proof not run for review. Tool e87b7648aa34058f4599330d8f7007e892778294; translator reviewed SHA d7c23b094c6822c210335d587066750c0d7da473f759088df89d12399dcc9e02. Profile7f532d68,17patch/18base/source-pin closure staticPASS. Other candidate2 scope/resource semantics unchanged.

Build2 exposed uncaught Not_found in GhostCmd source dispatch before resource proof. Explicit original let_lft start Noop preserves old compiler source placeholder while real binding moves to source begin. The begin marker's old Noop is omitted so its binding start is unique. Source oldstart/begin/close/cut/recover candidates must each be unique; actual binding has exact begin/cut. Missing arbitrary source command fails located static error, never silently Noop. Decoded actual272/305 spans plus pinned preprocessor/translator establish mapping defect; the saved crash lacks first call_loc, so no stronger causal/parser-input claim is made. A small synthetic static coordinate reproducer distinguishes missing/duplicate/wrong-start mappings; it is not actual parser/proof evidence.

Additional static fix prevents ghost reads in ordinary If / gotos in pure context: non-addressable ordinary mutable Bool __vf_late_callback_unwind is initialized at function root only for enabled late plan, collision-checked against all translated MIR locals including arguments/_0, and assigned false/true in the original returning/unwinding arms. Post-scope ordinary selector jumps to original normal/Cleanup targets. Source ghost flag is admission metadata only. No source Rust/runtime/kernel/model/prelude change.

Wrong-value control now uses exact observed prelude_core264,72–74 equality failure, with source/stage identities plus target and last-pre-error execution. Earlier geometry failure260/wrong coordinates/target/message/missing data remain inconclusive. All4 service tests pass. Prior candidate2 late admission4 and wiring gates remain; no full re-review of unchanged components. Source/control claims have accepted=false/proof_credit=false; whole CURRENT/insert_tail/B2/qualification remain OPEN.

Exact final inputs:

- `GLUE-PROFILE.json`: `7f532d68f695ac5a47dd0996d0c4bc88d04b1d9a9db881b4a50ae2063e4b2815`
- `r7-late-callback.patch`: `66227b9be9ed948f76a588b765aea4b1226dcc99068fa8245ece6384c420a6ef`
- `R7-TOOL-OBJECTS-20261020.bundle`: `1b8372a1321d6f11b13a95b96663e13ebf06a65713bf14c6f22fe9efc9593060`
- `r7-placeholder-reproducer.py`: `f079ed0aef77ac75d001a5d66b618e25fb5b4b152d7a72235578ca9deabae415`
- `r7-source-preflight.py`: `72ca2d75d5714c8f8f8c2e5a7dbfa321bcac6109e48c6b9f0dcefa2ae0043e4a`
- `r7-array-controls.py`: `c700e77abfe84acd65ef20edf09877d406f4b440bb86c426d2cb130f81fbd021`
- `r7-array-controls-service-test.py`: `32a5059b268cbef1c99668cd5d65256f5f95fb15a717518d46811ab0814ff190`
- `R7-BUILD2-ARRAY-CONTROL-OBSERVATION-20261020.json`: `e9986206fc7604e76c4d5ed35e5fbe9b72d3317c45968651044d25f6e5f3d476`
