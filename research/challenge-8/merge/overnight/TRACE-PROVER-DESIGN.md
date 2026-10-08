# Existing bundled Z3 backend diagnostic, before hosted run

M3k's complete stock quartet representation entered the full G2 trace; M3l
then timed out after120s with360 main statements and13 checked helper bodies.
No pre-body failure is repeated. The next experiment selects the existing
`Z3v4.5` plugin already compiled into the same pinned console and bound to
VFdeps libz3 SHA1837668dc531d14b3a4fffc0b690b77929d29c41868f98a89686f5ff64da95ea.
The plugin name is the stock interface name, not a claim about the actual
library version. No kernel, translator, prelude, exporter, refiner or primitive
contract changes. The prover is an explicit new evidence configuration; old
Redux proof SHA/results remain separate and are not transferred.

Hypothesis: existing Z3 discharges repeated heap-address/tuple and arithmetic
queries within180s, preserving every original twelve-coordinate post and all
body/source/refinement/normal/unwind/leak/dead checks. The main source,
helper bodies and tuple representation stay byte-identical.

The hosted matrix must include Z3 normal/unwind positives, false-unwind and
known-dead controls, exact generic/u32 G2-domain unit positives and the false
assertion under that exact domain, and the full twelve-field quartet
constructor plus its reached-false control. This checks both domain and
result-allocation inhabitation. Existing accepted math/W1/M2/C1/cleanup/actual
regressions still run with the original default configuration. A new positive
Z3 trace is accepted only with every full per-body gate and these Z3 controls;
any backend setup/unsupported failure is inconclusive. No functional or
generic Challenge implication follows. The default runner backend is untouched;
commands record the chosen stock plugin and stage timeout.

Separately, actual len2 gets120s to finish observed normal-return/panic paths;
len2/3 repairs its exact optional third-slot predicate without changing runtime
bodies/posts. Default backend remains for both current actual diagnostics.
