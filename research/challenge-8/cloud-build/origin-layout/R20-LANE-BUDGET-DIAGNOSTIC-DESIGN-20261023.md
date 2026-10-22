# Read-only lane budget checkpoints

P4 Brief reports a lane entry budget of 176 seconds and compile-only NOT_RUN
because its budget was exhausted. Static merge.sh subtracts the existing
140-second guard and preflight elapsed time before admitting compile-only.
The setup stage responsible for the lost outer budget remains UNKNOWN.

Add a small TSV-formatted .txt evidence record at lane entry, compile gate and compile finish:
stage, one sampled elapsed value, remaining lane budget and existing guard140.
This measures the current runner; it changes no timeout, reserve, deadline,
command arguments, proof mode, compile admission condition, matrix/control,
source binding or acceptance. Do not suppress an original failure or turn a
missing milestone into a proof claim. The TSV is ordinary evidence metadata,
not a new reporting interface. Local validation is bash syntax plus independent
static diff review; actual runner execution stays Cloud-only.
