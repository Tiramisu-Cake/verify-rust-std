# Frozen oracles

All actual native slots, main/fixed compilation, MIR observations and CI confirmation: **NOT_RUN**. The prepared `result.json` is a NOT_RUN artifact, not CI evidence. Source-level expectations carry no B1/B2 or independent proof credit.

| Slot | Exact feature / harness | Required observation | Invalid or missing observation |
| --- | --- | --- | --- |
| Setup | stock setup action | action outcome success | INCONCLUSIVE; action outcome recorded separately |
| Build | `cargo build-dev`, cwd stock | completed native exit 0, exact stock/compiler binding | INCONCLUSIVE; build exit/signal/diagnostics retained; proof slots stay NOT_RUN |
| PFC | provider / provider | complete SUCCESS export, one exact selected harness, successful `\|result\| *result == x + 1` property | INCONCLUSIVE |
| Verified control | verified / verified_control | complete SUCCESS export, exact target, successful `f(x)==x+1` assertion | INCONCLUSIVE |
| Ordinary | ordinary / ordinary_stub | exact missing `__kani_recursion_check_f` diagnostic for f, complete bounded diagnostics, nonzero exit, no verification inventory/export | DEFECT_PRESENT only with successful setup/build/controls |
| Ordinary | same | complete SUCCESS export and successful `f(x)==x+2` assertion | DEFECT_ABSENT for this fixture only, with successful controls |
| Ordinary | same | exact explicit unsupported-combination user diagnostic | separate EXPLICIT_UNSUPPORTED behavior; INCONCLUSIVE under frozen-main policy, whose docs do not declare this target restriction |
| Any | same | unrelated error, assertion failure, wrong source/tool/target/cfg/request, no RESULTS without expected diagnostic, timeout/RSS/output cap/spawn error, partial export, missing control or incomplete diagnostics | INCONCLUSIVE |

`provider` is always present so the verified harness's provider-existence check is satisfied; successful independent PFC is required as an additional control. The original function and postcondition are `x+1` under `x<8`. The ordinary replacement is `x+2`, deliberately outside that postcondition; it can witness full substitution and cannot pass by executing the original body. The symbolic input, assumption and assertion avoid arithmetic overflow and require the asserted property to be successful and reachable. Generic nonzero exit never establishes reproduction.

Features exclude the ordinary harness from PFC/control compilations; each command uses one `--exact --harness`, `--lib`, an explicit manifest/workspace, no dependencies/default features and a fresh target directory. A different codegen unit or absence of RESULTS cannot erase earlier invocations: the collector saves each slot independently and continues to the next slot after target errors. On a compiler build/setup failure there is no usable compiler and all proof slots remain NOT_RUN.

A future revision that documents a restriction can select a distinct supported oracle, reviewed with that revision. This frozen request never equates a user diagnostic with proof success. Native successful compilation followed by a failed postcondition would expose a different policy or defect and remains INCONCLUSIVE for the missing-closure hypothesis.
