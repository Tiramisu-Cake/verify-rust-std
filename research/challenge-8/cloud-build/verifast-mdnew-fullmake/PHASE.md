# VeriFast ManuallyDrop upstream PR full Linux test phase

Authorized by the direct user assignment at 2026-10-09T20:21:27Z. Main submit
cutoff 21:21:27Z; finish-only cutoff 21:51:27Z. Independent Cloud ceiling
3600 seconds; historical balances remain closed. Sole owner `verifast` and lane
`verifast-mdnew-fullmake`; own ledger `BUDGET.json` and state
`.verifast-fullmake-state`. The coordinator keeps two shared slots, one active
build per owner/ledger, unresolved reservations, global lock, 60-second queue
reserve, and no new submissions after the main cutoff.

The one planned 3000-second Build reserves 3060 seconds. It uses the selected
upstream base and source-delivered final PR branch. It installs only pinned
dependencies, removes stock copies of changed executables, then executes
`make test NUMCPU=4` once. The previous 650-second cap stopped during normal
test progress; this phase allows 2250 seconds for make within the 3000-second
Build. Source setup, diagnostics, and evidence upload occupy the remainder.
No Rust suite or selected fixture matrix runs before `make test`; a tiny
post-make dead-code diagnostic confirms the exact native negative control.
Timeout remains `INCOMPLETE_TIMEOUT`, and process/resources are recorded.

No upstream publication, consumer proof/pin, or three-slot migration is
authorized by this phase.
