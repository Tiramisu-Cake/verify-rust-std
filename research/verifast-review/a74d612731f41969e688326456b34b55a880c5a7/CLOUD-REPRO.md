# Applying and reproducing

1. In an isolated VeriFast checkout with exact base f76012fb518703b1d98e243ac4f487f16877cfcb,
   verify the supplied bundle and fetch refs/heads/merge/incoming-span-lifetime-20261009
   from it into your own review ref. Alternatively git am the portable patch.
2. The tested proof tool additionally uses the historical wrapping/callback/copy/
   cleanup/usize/stack patches and tracked-md.patch. PROFILE.json pins the assembled
   sources and frozen exporter/refiner/prelude/z3. A stock-base-only assembly gives
   wrong final source hashes; first Buildaf5c4a35 correctly rejected that setup.
3. Reproduce using the exact proof/infra SHA recorded in the evidence receipt and
   merge recipe/selection. Compilation/extraction/proof are Cloud-only. A new run
   needs a separately authorized phase, budget and owner ledger; do not reuse the
   closed ledger. Coordinator protocol remains v2/max2, one active Build per owner.
4. build-profile.sh validates baseline input sources and frozen binaries before
   applying tracked MD and incoming lifecycle patches, builds the console, then
   validates every final source hash and records the console hash. It never disables
   an identity gate or overwrites a present mismatched exporter/refiner.
5. prove.py runs the six isolated controls first. Exact-target semantic failures,
   alias read execution, and retired decoded-MIR/proof-AST order are mandatory.
   Setup/frontend failure is INCONCLUSIVE. Actual one-cell cases run only after all
   mechanism controls match; false-after-recovery is credited only after recovery.
6. Retrieve the immutable archive/upload receipt/text index using control.py download.
   verify-evidence.py binds build/proof/infra/config/archive and inventories; saved-log
   replay is separate from fresh proof execution. External text chunks may be fetched
   independently and must be hash-checked against the immutable index.

Final status: NOT_FOR_INTEGRATION. In addition to the excluded generic extent
domain, spelling-based lifecycle CallExpr markers have an unresolved origin
gate (extern-prototype/diverging source call may forge an event). This is static
review evidence, not an executed exploit. Six mechanism controls match in
cae0f3cc-9ca4-4ceb-b570-ab5e26e6ce82; all five actual cases stop before FBC at
line69 and are INCONCLUSIVE for their intended downstream obligations.
