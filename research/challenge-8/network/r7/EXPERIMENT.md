# R7 isolated swap-size transfer

`run-cloud.py` is the Cloud-only runner for the isolated generic theorem
`smallsort::has_efficient_in_place_swap`. It first validates the real Cloud
Build provider and the pinned R7 profile, then calls the unchanged
`extract-verifast-swap-size.py` in `PROOF_ROOT`. The source commit, Git blob,
and SHA-256 are pinned to `cd371e035c7e573760c43bf934d53e8118ee3e7d`,
`40939f922bcb6fdc7ee0d30427fa861827043827`, and
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`.

The source extractor is pinned by SHA-256
`ffa6fe5fa3f35533fafba3bc035e0da08d1624f093f2c47fceeb861a35a44140`.
Extraction must preserve the live generic function and add only the ghost
contract `req true; ens result == (std::mem::size_of::<T>() <= 8);`. The
runner checks exact ghost stripping, runs stock VeriFast 26.09 and the pinned
refinement checker with separate 180-second bounds, and runs refinement even
if verification exits nonzero. Evidence includes source variants, extraction
metadata, per-file tool hashes, compiler identity, command logs, original
exits/timeouts/exceptions, and evidence snapshots.

An accepted component requires the full source/tool/compiler/LP64 pins, an
unchanged source, zero verifier and refiner exits, exactly one named function
record, at least one body statement record on the extracted source lines, and
no verifier errors. The result is limited to this helper. `proof-audit.json`
always sets `accepted` and `proof_credit` to false; the shell may classify a
fully accepted component for its own evidence handling. This runner assigns
no caller or independent proof credit. `tool-inventory.json` records hashes
for the MIR exporter, refiner, all regular files below `bin/rust`, and the
available prelude files; its digest is also included in `results.json`.

`test_run_cloud.py` uses synthetic extraction and command fixtures only. It
does not access the Rust source or invoke Rust, VeriFast, or the refiner.
