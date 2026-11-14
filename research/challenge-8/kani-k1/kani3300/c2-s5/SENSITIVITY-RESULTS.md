# Sensitivity results

NOT_RUN. Four independent CI-only/test-only patch files plus exact SHA manifest are outside export.
All `git apply --check` checks pass on exact base; no patch was applied to source.
No local compiler/verifier/build/native compiletest ran. Predicted outcomes are hypotheses.

The positive mutant currently passes the weak base verdict-only oracle: it becomes a sensitivity
experiment only after final S5 golden requires its own outside41 SUCCESS-block. The negative-extra
variant must retain the original user-write failure, add an independently reached root assertion,
and be rejected by exact N. Repair retains the read and lawful out-write. Golden-status inversion
is sanity only, never the sole nontriviality evidence. Final S5 source splits/formatting may require
rebasing patch context and repinning hashes; this package must not be dispatched as completed S5.
